import json
import re
from pathlib import Path


# ==========================
# CONFIG
# ==========================
INPUT_JSON = "../../Defect_list_50.json"
OUTPUT_JSON = "../../Defect_list_50_rag.json"

# limit evidence size (important for embedding quality)
MAX_EVIDENCE_LINES = 25


# ==========================
# Helpers
# ==========================
def clean(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v else None
    return v


def join_lines(items):
    if not items:
        return ""
    return "\n".join([f"- {i}" for i in items if i])


# ==========================
# COMMENT SIGNAL EXTRACTION
# ==========================

LOG_PATTERN = re.compile(
    r"(error|fail|exception|timeout|trace|stack|crash|assert|warn)",
    re.IGNORECASE,
)


def extract_comment_signals(comments):
    """
    Extract only technical signals from comments.
    Avoid embedding workflow noise.
    """

    if not comments:
        return []

    signals = []

    for comment in comments:
        if not comment:
            continue

        lines = comment.split("\n")

        for line in lines:
            line = line.strip()

            if len(line) < 10:
                continue

            # keep only technical lines
            if LOG_PATTERN.search(line):
                signals.append(line)

    # deduplicate while keeping order
    seen = set()
    unique = []
    for s in signals:
        if s not in seen:
            unique.append(s)
            seen.add(s)

    return unique[:MAX_EVIDENCE_LINES]


def build_evidence_text(signals):
    if not signals:
        return ""

    return "Technical Evidence:\n" + "\n".join(
        f"- {s}" for s in signals
    )


# ==========================
# CORE: build search text
# ==========================
def build_search_text(issue):
    """
    ONLY information known before solution.
    """

    title = clean(issue.get("title"))
    defect_type = clean(issue.get("defect_type"))
    phenomena = issue.get("phenomena", [])

    text = f"""
Issue Title:
{title}

Observed Symptoms:
{join_lines(phenomena)}

Defect Category:
{defect_type}
"""

    return text.strip()


# ==========================
# Transform one issue
# ==========================
def transform_issue(issue):

    comments = issue.get("comments", [])

    # ---- extract valuable signals ----
    signals = extract_comment_signals(comments)
    evidence_text = build_evidence_text(signals)

    new_issue = {
        "id": clean(issue.get("case_code")),

        # -------- retrieval space --------
        "search_text": build_search_text(issue),
        "evidence_text": evidence_text,

        "symptoms": issue.get("phenomena", []),

        # keep raw comments (NOT embedded)
        "raw_comments": comments,

        "metadata": {
            "type": clean(issue.get("type")),
            "defect_type": clean(issue.get("defect_type")),
            "request_reason": clean(issue.get("request_reason")),
        },

        # -------- solution space --------
        "solution": {
            "root_cause": clean(issue.get("root_cause")),
            "countermeasure": clean(issue.get("countermeasure")),
            "resolved_by": clean(
                issue.get("resolution", {}).get("resolved_by")
            ),
            "resolve_date": clean(
                issue.get("resolution", {}).get("resolve_date")
            ),
        }
    }

    return new_issue


# ==========================
# Pipeline
# ==========================
def main():

    input_path = Path(INPUT_JSON)

    if not input_path.exists():
        raise FileNotFoundError(INPUT_JSON)

    print("Loading source JSON...")
    with open(input_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    print("Transforming issues...")
    new_issues = [transform_issue(i) for i in issues]

    print("Saving RAG-ready JSON...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(new_issues, f, indent=2, ensure_ascii=False)

    print(f"✅ Done: {OUTPUT_JSON}")
    print(f"Total issues: {len(new_issues)}")


if __name__ == "__main__":
    main()