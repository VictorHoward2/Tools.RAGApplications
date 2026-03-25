"""
Flatten evaluation.ai per_hit rows to CSV for Excel / pandas.

Run from src:
    python -m rag.export_ai_eval_csv --input path/to/rag_eval_batch_cursor_composer2.json
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, nargs="?", default=None, help="rag_eval JSON path")
    ap.add_argument("--output", type=Path, default=None, help="CSV path (default: same name .csv)")
    args = ap.parse_args()

    inp = args.input
    if inp is None:
        inp = Path(__file__).resolve().parents[2] / "data" / "719" / "rag_eval_batch_cursor_composer2.json"
    inp = inp.resolve()

    out = args.output
    if out is None:
        out = inp.with_suffix(".csv")

    with open(inp, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows: list[dict] = []
    for q in data.get("queries") or []:
        qix = q.get("query_index")
        ai = (q.get("evaluation") or {}).get("ai") or {}
        for row in ai.get("per_hit") or []:
            flat = {
                "query_index": qix,
                "query_case_code": row.get("query_case_code"),
                "rank": row.get("rank"),
                "hit_case_code": row.get("case_code"),
                "problem_match": row.get("problem_match"),
                "solution_direction_match": row.get("solution_direction_match"),
                "overall_score": row.get("overall_score"),
                "score_problem": row.get("score_problem"),
                "score_solution": row.get("score_solution"),
                "comment": row.get("comment"),
            }
            rows.append(flat)

    if not rows:
        print("No evaluation.ai per_hit rows found.")
        return

    fieldnames = list(rows[0].keys())
    with open(out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"OK Wrote {len(rows)} rows to {out.resolve()}")


if __name__ == "__main__":
    main()
