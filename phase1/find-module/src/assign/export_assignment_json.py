from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from assign.classifier import classify_issue


INPUT_FILE = Path("D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list_rag.json")
OUTPUT_FILE = Path("D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list_rag_with_assignment.json")


def load_issues(file_path: Path) -> list[dict[str, Any]]:
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot find input file: {file_path.resolve()}")

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Input JSON must be a list of issues.")

    return data


def enrich_issue(issue: dict[str, Any]) -> dict[str, Any]:
    result = classify_issue(issue)

    enriched_issue = dict(issue)

    enriched_issue["assignment_prediction"] = {
        "predicted_module": result.get("predicted_module"),
        "predicted_pic": result.get("predicted_pic"),
        "confidence": result.get("confidence"),
        "review_status": result.get("review_status"),
        "top_2_candidates": result.get("top_2_candidates", []),
        "scores": result.get("scores", {}),
        "matched_rules": result.get("matched_rules", []),
        "top_reasons": result.get("top_reasons", []),
        "ground_truth_module": result.get("ground_truth_module"),
    }

    return enriched_issue


def export_assignment_json(
    input_file: Path = INPUT_FILE,
    output_file: Path = OUTPUT_FILE,
) -> None:
    issues = load_issues(input_file)
    enriched_issues = [enrich_issue(issue) for issue in issues]

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(enriched_issues, f, ensure_ascii=False, indent=2)

    print("=" * 80)
    print(f"Input file : {input_file.resolve()}")
    print(f"Output file: {output_file.resolve()}")
    print(f"Total issues exported: {len(enriched_issues)}")
    print("Done.")
    print("=" * 80)


def main() -> None:
    export_assignment_json()


if __name__ == "__main__":
    main()