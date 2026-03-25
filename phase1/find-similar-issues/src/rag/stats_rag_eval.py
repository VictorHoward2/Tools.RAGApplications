"""
Aggregate statistics from a rag_eval_batch JSON (evaluation.ai + retrieval).

Run from src:
    python -m rag.stats_rag_eval
    python -m rag.stats_rag_eval --input path/to/batch.json --output path/to/report.md

Default input: data/719/rag_eval_batch_cursor_composer2.json
Default output: same basename with _stats.md next to the JSON file.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from typing import Any


def collect_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for q in data.get("queries", []):
        qidx = q.get("query_index")
        qcode = q["query"]["snapshot"].get("case_code")
        ai = (q.get("evaluation") or {}).get("ai") or {}
        retr = {(r["rank"], r["case_code"]): r for r in (q.get("retrieval") or [])}
        for h in ai.get("per_hit") or []:
            key = (h.get("rank"), h.get("case_code"))
            r = retr.get(key, {})
            sim = r.get("similarity_score")
            rows.append(
                {
                    "query_index": qidx,
                    "query_case_code": qcode,
                    "rank": h.get("rank"),
                    "hit_case_code": h.get("case_code"),
                    "problem_match": h.get("problem_match"),
                    "solution_direction_match": h.get("solution_direction_match"),
                    "overall_score": h.get("overall_score"),
                    "score_problem": h.get("score_problem") or h.get("cos_problem"),
                    "score_solution": h.get("score_solution") or h.get("cos_solution"),
                    "similarity_score": sim,
                }
            )
    return rows


def pct(part: int, total: int) -> str:
    if total == 0:
        return "0.0"
    return f"{100.0 * part / total:.1f}"


def build_report(data: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    meta = data.get("meta", {})
    ai_meta = meta.get("ai_evaluation") or {}
    n = len(rows)
    lines: list[str] = []

    lines.append("# RAG evaluation batch statistics\n\n")
    lines.append(f"- Pipeline defect list: `{meta.get('paths', {}).get('defect_list_json', '—')}`\n")
    lines.append(
        f"- Queries: **{meta.get('queries_exported', '—')}** · top_k: **{meta.get('top_k', '—')}** · hits: **{n}**\n"
    )

    if ai_meta:
        lines.append("\n## AI proxy configuration (`meta.ai_evaluation`)\n\n")
        lines.append("```json\n")
        lines.append(json.dumps(ai_meta, ensure_ascii=False, indent=2))
        lines.append("\n```\n")

    lines.append("\n## Aggregate statistics (all hits)\n\n")
    lines.append("| Metric | Mean | Min | Max | n |\n")
    lines.append("|--------|------|-----|-----|---|\n")
    for name in [
        "problem_match",
        "solution_direction_match",
        "overall_score",
        "score_problem",
        "score_solution",
        "similarity_score",
    ]:
        vals = [r[name] for r in rows if r.get(name) is not None]
        if vals:
            lines.append(
                f"| `{name}` | {mean(vals):.6f} | {min(vals):.6f} | {max(vals):.6f} | {len(vals)} |\n"
            )

    lines.append("\n## Distribution: `problem_match` (0–2)\n\n")
    for k in sorted({r["problem_match"] for r in rows if r.get("problem_match") is not None}):
        c = sum(1 for r in rows if r.get("problem_match") == k)
        lines.append(f"- **{k}**: {c} ({pct(c, n)}%)\n")

    lines.append("\n## Distribution: `solution_direction_match` (0–2)\n\n")
    for k in sorted(
        {r["solution_direction_match"] for r in rows if r.get("solution_direction_match") is not None}
    ):
        c = sum(1 for r in rows if r.get("solution_direction_match") == k)
        lines.append(f"- **{k}**: {c} ({pct(c, n)}%)\n")

    lines.append("\n## Distribution: `overall_score`\n\n")
    for k in sorted({r["overall_score"] for r in rows if r.get("overall_score") is not None}):
        c = sum(1 for r in rows if r.get("overall_score") == k)
        lines.append(f"- **{k}**: {c} ({pct(c, n)}%)\n")

    lines.append("\n## By retrieval rank\n\n")
    lines.append("| Rank | Mean `overall_score` | Mean `similarity_score` | n |\n")
    lines.append("|------|------------------------|--------------------------|---|\n")
    for rank in [1, 2, 3, 4]:
        sub = [r for r in rows if r.get("rank") == rank]
        if not sub:
            continue
        mo = mean([r["overall_score"] for r in sub if r.get("overall_score") is not None])
        ss = [r["similarity_score"] for r in sub if r.get("similarity_score") is not None]
        ms = mean(ss) if ss else float("nan")
        lines.append(f"| {rank} | {mo:.4f} | {ms:.4f} | {len(sub)} |\n")

    lines.append("\n## Per-query means (average of top-k hits)\n\n")
    q_means: list[float] = []
    for q in data.get("queries", []):
        ai = (q.get("evaluation") or {}).get("ai") or {}
        os = [h["overall_score"] for h in (ai.get("per_hit") or []) if h.get("overall_score") is not None]
        if os:
            q_means.append(mean(os))
    if q_means:
        lines.append(f"- Mean of per-query means: **{mean(q_means):.4f}**\n")
        lines.append(f"- Min / max query mean: **{min(q_means):.4f}** / **{max(q_means):.4f}**\n")

    lines.append("\n---\n*Generated by `python -m rag.stats_rag_eval`. Add metric definitions and narrative in the saved file if needed.*\n")
    return "".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description="Statistics for rag_eval_batch JSON.")
    ap.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to rag_eval_batch_*.json",
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write Markdown report (default: <input>_stats.md)",
    )
    ap.add_argument("--quiet", action="store_true", help="Do not print report to stdout.")
    args = ap.parse_args()

    inp = args.input
    if inp is None:
        inp = Path(__file__).resolve().parents[2] / "data" / "719" / "rag_eval_batch_cursor_composer2.json"
    inp = inp.resolve()

    out = args.output
    if out is None:
        out = inp.with_name(inp.stem + "_stats.md")

    data = json.loads(inp.read_text(encoding="utf-8"))
    rows = collect_rows(data)
    report = build_report(data, rows)

    out.write_text(report, encoding="utf-8")
    if not args.quiet:
        print(report)
    print(f"OK Wrote {out.resolve()}")


if __name__ == "__main__":
    main()
