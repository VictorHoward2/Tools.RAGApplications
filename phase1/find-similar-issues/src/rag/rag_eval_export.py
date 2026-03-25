"""
Batch export retrieval results for RAG evaluation (AI scoring + human/Dev scoring).

Run from src:
    python -m rag.rag_eval_export

Outputs JSON with query snapshots, top-k hits (self excluded), and empty evaluation slots.
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer

from _config.setting import (
    DEVICE,
    FILE_JSON,
    FILE_JSON_EMBEDDING,
    FILE_JSON_RAG,
    MODEL_NAME,
)


def clean(v: Any) -> str:
    if not v:
        return ""
    return str(v).strip()


def build_query_text(issue: dict[str, Any]) -> str:
    """Must stay aligned with embedding.indexing and rag_demo."""
    search_text = clean(issue.get("search_text"))
    evidence_text = clean(issue.get("evidence_text"))
    return (search_text + "\n" + evidence_text).strip()


def snapshot_from_defect_json(row: dict[str, Any]) -> dict[str, Any]:
    """Fields for annotators: problem + resolution direction (ground context)."""
    return {
        "case_code": row.get("case_code"),
        "type": row.get("type"),
        "title": row.get("title"),
        "request_reason": row.get("request_reason"),
        "defect_type": row.get("defect_type"),
        "phenomena": row.get("phenomena") or [],
        "root_cause": clean(row.get("root_cause")),
        "countermeasure": clean(row.get("countermeasure")),
    }


def snapshot_hit_for_eval(rag_issue: dict[str, Any], *, search_max: int, evidence_max: int) -> dict[str, Any]:
    """Enough text for AI/human to judge similarity of problem + fix direction."""
    sol = rag_issue.get("solution") or {}
    meta = rag_issue.get("metadata") or {}
    st = clean(rag_issue.get("search_text"))
    ev = clean(rag_issue.get("evidence_text"))
    return {
        "case_code": rag_issue.get("id"),
        "module_type": meta.get("type"),
        "defect_type": meta.get("defect_type"),
        "request_reason": meta.get("request_reason"),
        "search_text": st[:search_max] + ("…" if len(st) > search_max else ""),
        "search_text_was_truncated": len(st) > search_max,
        "evidence_text": ev[:evidence_max] + ("…" if len(ev) > evidence_max else ""),
        "evidence_text_was_truncated": len(ev) > evidence_max,
        "root_cause": clean(sol.get("root_cause")),
        "countermeasure": clean(sol.get("countermeasure")),
    }


def empty_hit_eval_slots(ranks_and_codes: list[tuple[int, str]]) -> dict[str, Any]:
    rows = []
    for rank, code in ranks_and_codes:
        rows.append(
            {
                "rank": rank,
                "case_code": code,
                "problem_match": None,
                "solution_direction_match": None,
                "overall_score": None,
                "comment": None,
            }
        )
    return {
        "filled": False,
        "per_hit": rows,
        "query_notes": None,
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Export top-k retrieval for random queries to JSON for evaluation.")
    p.add_argument("--seed", type=int, default=42, help="RNG seed for reproducible 50-issue sample.")
    p.add_argument("--sample-size", type=int, default=50, help="Number of random issues to query.")
    p.add_argument("--top-k", type=int, default=4, help="Top similar issues per query (query itself excluded).")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: data/719/rag_eval_batch.json next to Defect_list.json).",
    )
    p.add_argument("--search-max-chars", type=int, default=2000, help="Max chars of search_text per hit in export.")
    p.add_argument("--evidence-max-chars", type=int, default=1500, help="Max chars of evidence_text per hit in export.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_path = args.output
    if out_path is None:
        out_path = Path(FILE_JSON).resolve().parent / "rag_eval_batch.json"

    with open(FILE_JSON, "r", encoding="utf-8") as f:
        defect_rows: list[dict[str, Any]] = json.load(f)

    with open(FILE_JSON_RAG, "r", encoding="utf-8") as f:
        rag_issues: list[dict[str, Any]] = json.load(f)

    rag_by_id: dict[str, dict[str, Any]] = {str(x["id"]): x for x in rag_issues}

    with open(FILE_JSON_EMBEDDING, "r", encoding="utf-8") as f:
        db_issues: list[dict[str, Any]] = json.load(f)

    embeddings = np.array([issue["embedding"] for issue in db_issues], dtype=np.float32)
    id_to_index = {str(db_issues[i]["id"]): i for i in range(len(db_issues))}

    n = len(defect_rows)
    if args.sample_size > n:
        raise ValueError(f"sample_size ({args.sample_size}) > dataset size ({n})")

    rng = random.Random(args.seed)
    chosen_indices = rng.sample(range(n), args.sample_size)

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME, device=DEVICE)

    queries_out: list[dict[str, Any]] = []

    for qi, defect_idx in enumerate(chosen_indices):
        row = defect_rows[defect_idx]
        case_code = str(row.get("case_code") or "")
        if not case_code:
            raise ValueError(f"Empty case_code at defect_rows[{defect_idx}]")

        rag_q = rag_by_id.get(case_code)
        if rag_q is None:
            print(f"[WARN] Skip {case_code}: not found in RAG JSON (id mismatch).")
            continue

        query_text = build_query_text(rag_q)
        qvec = model.encode([query_text], normalize_embeddings=True)[0]

        scores = embeddings @ qvec
        if case_code in id_to_index:
            scores = scores.copy()
            scores[id_to_index[case_code]] = -np.inf

        top_idx = np.argsort(scores)[-args.top_k :][::-1]

        hits: list[dict[str, Any]] = []
        ranks_codes: list[tuple[int, str]] = []

        for rank, idx in enumerate(top_idx, start=1):
            hit = db_issues[int(idx)]
            cid = str(hit["id"])
            sc = float(scores[int(idx)])
            if not np.isfinite(sc):
                continue
            rag_hit = rag_by_id.get(cid, hit)
            hits.append(
                {
                    "rank": rank,
                    "case_code": cid,
                    "similarity_score": round(sc, 6),
                    "snapshot": snapshot_hit_for_eval(
                        rag_hit,
                        search_max=args.search_max_chars,
                        evidence_max=args.evidence_max_chars,
                    ),
                }
            )
            ranks_codes.append((rank, cid))

        eval_ai = empty_hit_eval_slots(ranks_codes)
        eval_human = empty_hit_eval_slots(ranks_codes)

        queries_out.append(
            {
                "query_index": qi,
                "source_row_index_in_defect_list_json": defect_idx,
                "query": {
                    "snapshot": snapshot_from_defect_json(row),
                    "query_text_char_length": len(query_text),
                },
                "retrieval": hits,
                "evaluation": {
                    "criteria_hint": {
                        "problem": "Cùng bản chất vấn đề (triệu chứng / ngữ cảnh kỹ thuật).",
                        "solution_direction": "Cùng hướng xử lý / gợi ý fix (root cause + countermeasure tương đồng).",
                    },
                    "ai": eval_ai,
                    "human": eval_human,
                },
            }
        )

        if (qi + 1) % 10 == 0:
            print(f"  processed {qi + 1}/{args.sample_size} queries...")

    payload = {
        "meta": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "random_seed": args.seed,
            "sample_requested": args.sample_size,
            "queries_exported": len(queries_out),
            "top_k": args.top_k,
            "exclude_query_id_from_hits": True,
            "model_name": MODEL_NAME,
            "device": DEVICE,
            "paths": {
                "defect_list_json": str(Path(FILE_JSON).resolve()),
                "rag_json": str(Path(FILE_JSON_RAG).resolve()),
                "embeddings_json": str(Path(FILE_JSON_EMBEDDING).resolve()),
            },
            "truncation": {
                "search_text_max_chars": args.search_max_chars,
                "evidence_text_max_chars": args.evidence_max_chars,
            },
        },
        "queries": queries_out,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"OK Wrote {len(queries_out)} queries to {out_path.resolve()}")


if __name__ == "__main__":
    main()
