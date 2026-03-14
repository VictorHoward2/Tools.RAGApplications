from __future__ import annotations

import json
from pathlib import Path

from assign.classifier import classify_issue


DATA_FILE = Path("D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list_rag.json")


def load_issues(file_path: Path) -> list[dict]:
    if not file_path.exists():
        raise FileNotFoundError(f"Cannot find file: {file_path.resolve()}")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def pretty_print_result(issue: dict, result: dict) -> None:
    print("=" * 80)
    print(f"Issue ID          : {issue.get('id')}")
    print(f"Ground Truth      : {result.get('ground_truth_module')}")
    print(f"Predicted Module  : {result.get('predicted_module')}")
    print(f"Predicted PIC     : {result.get('predicted_pic')}")
    print(f"Confidence        : {result.get('confidence')}")
    print(f"Review Status     : {result.get('review_status')}")
    print("-" * 80)

    print("Top 2 Candidates:")
    for candidate in result.get("top_2_candidates", []):
        print(f"  - {candidate['module']}: {candidate['score']}")

    print("-" * 80)
    print("Scores:")
    for module, score in result.get("scores", {}).items():
        print(f"  - {module}: {score}")

    print("-" * 80)
    print("Matched Priority Rules:")
    rules = result.get("matched_rules", [])
    if not rules:
        print("  (none)")
    else:
        for rule in rules:
            print(f"  - {rule['rule_name']} -> {rule['module']} (+{rule['bonus']})")

    print("-" * 80)
    print("Top Reasons:")
    reasons = result.get("top_reasons", [])
    if not reasons:
        print("  (none)")
    else:
        for reason in reasons:
            print(
                f"  - keyword='{reason['keyword']}', "
                f"level={reason['level']}, "
                f"field={reason['field']}, "
                f"occurrences={reason['occurrences']}, "
                f"score_gain={reason['score_gain']}"
            )

    print("-" * 80)
    print("Issue Title Preview:")
    search_text = issue.get("search_text", "")
    print(search_text[:300])
    print("=" * 80)


def main() -> None:
    issues = load_issues(DATA_FILE)

    if len(issues) < 2:
        raise ValueError("Need at least 2 issues in Defect_list_rag.json for this demo.")

    # Demo đúng theo yêu cầu: lấy issue thứ 2 trong danh sách
    issue = issues[1]
    result = classify_issue(issue)
    pretty_print_result(issue, result)


if __name__ == "__main__":
    main()