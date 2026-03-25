"""
Fill evaluation.ai in a rag_eval_batch JSON using automated similarity scoring.

Default: lexical similarity (difflib), no GPU — stable and fast for batch export.

Optional: --use-embedding for BGE-M3 cosine (same family as retrieval); heavier.

Run from src:
    python -m rag.fill_ai_evaluation --input path/to/rag_eval_batch_cursor_composer2.json
"""

from __future__ import annotations

import argparse
import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import numpy as np

from _config.setting import DEVICE, MODEL_NAME


def sim_to_band(score: float, hi: float, mid: float) -> int:
    if score >= hi:
        return 2
    if score >= mid:
        return 1
    return 0


def lexical_ratio(a: str, b: str) -> float:
    a, b = (a or "").strip(), (b or "").strip()
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return float(SequenceMatcher(None, a, b).ratio())


def build_problem_text(query_block: dict[str, Any]) -> str:
    s = query_block["snapshot"]
    parts = [
        s.get("title") or "",
        " ".join(s.get("phenomena") or []),
        s.get("defect_type") or "",
        (s.get("type") or "").replace("\r\n", " "),
    ]
    return "\n".join(p for p in parts if p).strip()


def build_solution_text(s: dict[str, Any]) -> str:
    rc = (s.get("root_cause") or "").strip()
    cm = (s.get("countermeasure") or "").strip()
    if not rc and not cm:
        return ""
    return f"{rc}\n{cm}".strip()


def build_hit_problem_text(hit_snap: dict[str, Any]) -> str:
    return "\n".join(
        [
            (hit_snap.get("search_text") or "")[:4000],
            (hit_snap.get("evidence_text") or "")[:2000],
        ]
    ).strip()


def score_with_embeddings(
    model: Any,
    p_text: str,
    h_problems: list[str],
    sol_q: str,
    h_sols: list[str],
    hi: float,
    mid: float,
) -> tuple[list[float], list[float], list[int], list[int]]:
    """Returns cos_p list, cos_s list, pb list, sb list per hit."""
    vp = model.encode([p_text] + h_problems, normalize_embeddings=True, show_progress_bar=False)
    v_p = vp[0]
    v_hp = vp[1:]

    cos_ps = [float(np.dot(v_p, v_hp[i])) for i in range(len(h_problems))]

    sol_pairs: list[str] = []
    sol_idx: list[int] = []
    for i, hs in enumerate(h_sols):
        if sol_q and hs:
            sol_pairs.extend([sol_q, hs])
            sol_idx.append(i)
    sol_cos_by_i: dict[int, float] = {}
    if sol_pairs:
        vs = model.encode(sol_pairs, normalize_embeddings=True, show_progress_bar=False)
        for j, qi in enumerate(sol_idx):
            sol_cos_by_i[qi] = float(np.dot(vs[j * 2], vs[j * 2 + 1]))

    cos_ss = []
    pbs = []
    sbs = []
    for i in range(len(h_problems)):
        cp = cos_ps[i]
        if i in sol_cos_by_i:
            cs = sol_cos_by_i[i]
            sb = sim_to_band(cs, hi, mid)
        else:
            cs = 0.0
            sb = 0
        pb = sim_to_band(cp, hi, mid)
        cos_ss.append(cs)
        pbs.append(pb)
        sbs.append(sb)
    return cos_ps, cos_ss, pbs, sbs


def score_with_lexical(
    p_text: str,
    h_problems: list[str],
    sol_q: str,
    h_sols: list[str],
    hi: float,
    mid: float,
) -> tuple[list[float], list[float], list[int], list[int]]:
    cos_ps = [lexical_ratio(p_text, hp) for hp in h_problems]
    cos_ss = []
    sbs = []
    for hs in h_sols:
        if sol_q and hs:
            cs = lexical_ratio(sol_q, hs)
            cos_ss.append(cs)
            sbs.append(sim_to_band(cs, hi, mid))
        else:
            cos_ss.append(0.0)
            sbs.append(0)
    pbs = [sim_to_band(cp, hi, mid) for cp in cos_ps]
    return cos_ps, cos_ss, pbs, sbs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        type=Path,
        default=Path(__file__).resolve().parents[2]
        / "data"
        / "719"
        / "rag_eval_batch_cursor_composer2.json",
        help="Path to rag eval JSON to fill in-place.",
    )
    ap.add_argument(
        "--hi",
        type=float,
        default=0.72,
        help="Embedding mode: threshold for band 2 (cosine). Ignored for lexical unless --lexical-scale off.",
    )
    ap.add_argument(
        "--mid",
        type=float,
        default=0.52,
        help="Embedding mode: threshold for band 1 (cosine).",
    )
    ap.add_argument(
        "--lex-mid",
        type=float,
        default=0.22,
        help="Lexical mode: SequenceMatcher ratio threshold for band 1 (strings are long; lower than cosine).",
    )
    ap.add_argument(
        "--lex-hi",
        type=float,
        default=0.42,
        help="Lexical mode: ratio threshold for band 2.",
    )
    ap.add_argument(
        "--use-embedding",
        action="store_true",
        help="Use BGE-M3 cosine instead of difflib (slower, needs RAM/GPU).",
    )
    args = ap.parse_args()

    path = args.input.resolve()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model = None
    engine_name = "lexical_difflib"
    score_label = "lexical_ratio"

    if args.use_embedding:
        from sentence_transformers import SentenceTransformer

        print(f"Loading {MODEL_NAME} ...")
        model = SentenceTransformer(MODEL_NAME, device=DEVICE)
        engine_name = "embedding_cosine_bge_m3"
        score_label = "cosine"

    queries = data.get("queries") or []
    n_hits = 0

    if args.use_embedding:
        t_mid, t_hi = args.mid, args.hi
    else:
        t_mid, t_hi = args.lex_mid, args.lex_hi

    for q in queries:
        ai_block = q.setdefault("evaluation", {}).setdefault("ai", {})
        ai_block["filled"] = True
        ai_block["engine"] = engine_name
        ai_block["score_type"] = score_label
        ai_block["engine_note"] = (
            "Automated proxy scores for aggregation; not a human review. "
            "Compare with evaluation.human when available."
        )
        ai_block["thresholds"] = {"mid": t_mid, "high": t_hi}

        p_text = build_problem_text(q["query"])
        sol_q = build_solution_text(q["query"]["snapshot"])
        retrievals = q.get("retrieval") or []
        if not retrievals:
            continue

        h_problems = [build_hit_problem_text(rh["snapshot"]) for rh in retrievals]
        h_sols = [build_solution_text(rh["snapshot"]) for rh in retrievals]

        if model is not None:
            cos_ps, cos_ss, pbs, sbs = score_with_embeddings(
                model, p_text, h_problems, sol_q, h_sols, t_hi, t_mid
            )
        else:
            cos_ps, cos_ss, pbs, sbs = score_with_lexical(
                p_text, h_problems, sol_q, h_sols, t_hi, t_mid
            )

        for i, rh in enumerate(retrievals):
            cos_p = cos_ps[i]
            cos_s = cos_ss[i]
            pb = pbs[i]
            sb = sbs[i]
            overall = round((pb + sb) / 2.0, 2)

            comment = (
                f"auto[{engine_name}]: {score_label}_problem={cos_p:.3f}->{pb}, "
                f"{score_label}_solution={cos_s:.3f}->{sb} (mid={t_mid}, hi={t_hi})"
            )

            q_code = q["query"]["snapshot"].get("case_code")
            for row in ai_block.get("per_hit") or []:
                if row.get("case_code") == rh["case_code"] and row.get("rank") == rh["rank"]:
                    row["problem_match"] = pb
                    row["solution_direction_match"] = sb
                    row["overall_score"] = overall
                    row["comment"] = comment
                    row["score_problem"] = round(cos_p, 6)
                    row["score_solution"] = round(cos_s, 6)
                    row["query_case_code"] = q_code
                    break
            n_hits += 1

    data.setdefault("meta", {})["ai_evaluation"] = {
        "filled": True,
        "engine": engine_name,
        "model": MODEL_NAME if args.use_embedding else None,
        "device": DEVICE if args.use_embedding else None,
        "scale": {
            "problem_match": "0-2",
            "solution_direction_match": "0-2",
            "overall_score": "mean of the two bands (0.0, 0.5, 1.0, 1.5, 2.0)",
        },
        "thresholds": {"mid": t_mid, "high": t_hi},
        "lexical_thresholds_default": {"mid": args.lex_mid, "high": args.lex_hi},
        "embedding_thresholds_default": {"mid": args.mid, "high": args.hi},
        "hits_scored": n_hits,
        "columns_for_stats": [
            "problem_match",
            "solution_direction_match",
            "overall_score",
            "score_problem",
            "score_solution",
            "query_index",
            "rank",
            "query_case_code",
            "hit_case_code",
        ],
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK Scored {n_hits} hits with {engine_name}, wrote {path}")


if __name__ == "__main__":
    main()
