import pandas as pd
import json
from pathlib import Path
from _config.setting import *

# =============================
# Helpers
# =============================
def clean_value(v):
    """Convert NaN -> None + strip text"""
    if pd.isna(v):
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v else None
    return v


def safe_list(values):
    """Remove None + duplicate values"""
    return list(
        {v for v in values if v is not None}
    )


# =============================
# Main aggregation logic
# =============================
def build_issue_summary(df: pd.DataFrame):

    issues = []

    grouped = df.groupby("Case Code")

    for case_code, group in grouped:

        first = group.iloc[0]

        issue = {
            "case_code": clean_value(case_code),

            "type": clean_value(first.get("Type")),
            "title": clean_value(first.get("Title")),
            "request_reason": clean_value(first.get("Request reason")),
            "defect_type": clean_value(first.get("Defect Type")),

            # ---- phenomena aggregation ----
            "phenomena": safe_list(
                clean_value(v)
                for v in group["Detailed Phenomenon"]
            ),

            # ---- resolution info ----
            "resolution": {
                "resolved_by": clean_value(first.get("Resolved by")),
                "resolver_id": clean_value(first.get("Resolver ID")),
                "resolve_date": clean_value(first.get("Resolve Date")),
                "cl_number": clean_value(first.get("CL Number")),
            },

            # ---- analysis ----
            "root_cause": clean_value(first.get("Cause")),
            "countermeasure": clean_value(first.get("Countermeasure")),

            # ---- collect all comments ----
            "comments": safe_list(
                clean_value(v)
                for v in group["Comment"]
            ),
        }

        issues.append(issue)

        
    # deduplicate while keeping order
    seen = set()
    unique_issues = []
    for i in issues:
        if i["case_code"] not in seen:
            unique_issues.append(i)
            seen.add(i["case_code"])

    return unique_issues



# =============================
# Pipeline
# =============================
def main():

    input_path = Path(FILE_CSV)

    if not input_path.exists():
        raise FileNotFoundError(f"Cannot find {FILE_CSV}")

    print("Reading CSV...")
    df = pd.read_csv(input_path)

    print("Building aggregated issues...")
    issues = build_issue_summary(df)

    print("Saving JSON...")
    with open(FILE_JSON, "w", encoding="utf-8") as f:
        json.dump(
            issues,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(f"✅ Done! Output saved to: {FILE_JSON}")
    print(f"Total issues: {len(issues)}")


if __name__ == "__main__":
    main()