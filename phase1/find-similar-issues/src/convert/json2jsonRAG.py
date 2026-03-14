import json
import re
from pathlib import Path
from _config.setting import *


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

ERROR_PATTERN = re.compile(
    r"(error|fail|exception|timeout|trace|stack|crash|assert|warn)",
    re.IGNORECASE,
)

MODULE_KEYWORDS = {
    "OMA": [
        "CtsOmapiTestCases",
        "CtsSecureElementAccessControlTestCases",
        "VtsHalSecureElementTargetTest",
        "VtsHalSecureElementV1_0TargetTest",
        "com.android.se",
        "SecureElementApplication",
        "SecureElementService",
        "SEService",
        "SecureElement",
        "secure-element",
        "OMAPI CTS",
    ],
    "SKMSAgent": [
        "SEC_PRODUCT_FEATURE_SECURITY_SUPPORT_CNSKMS",
        "SEC_PRODUCT_FEATURE_SECURITY_CONFIG_MSG_VERSION",
        "com.skms.android.agent",
        "com.samsung.android.ese",
        "SKMSAgent",
        "SamsungSeAgent",
        "TSMAgent",
        "SEC_ESE",
        "SecAppLoader",
        "CPLC",
        "NXP",
        "THALES_HAL",
        "GEMALTO_P3",
    ],
    "SEM": [
        "ESES",
        "ESEA",
        "SEC_PRODUCT_FEATURE_SECURITY_SUPPORT_ESE_REE_SPI",
        "SEC_PRODUCT_FEATURE_SECURITY_CONFIG_ESE_CHIP_VENDOR",
        "SEC_PRODUCT_FEATURE_SECURITY_CONFIG_ESE_COS_NAME",
        "SEC_PRODUCT_FEATURE_SECURITY_SUPPORT_ESEK",
        "SEMFactoryApp",
        "sem_daemon",
        "SEMService",
        "eSE HAL",
        "eSE",
        "eSE restricted mode",
        "Ap-eSE",
        "eSE COS",
        "ro.security.esest",
        "ro.security.esebap",
        "SEC_ESE",
        "SEM",
        "NXP",
        "THALES_HAL",
        "GEMALTO_P3",
        "SecureElement",
    ],
    "SKPM": [
        "SKPM",
        "skpm",
        "vendor.samsung.hardware.security.skpm",
        "ISehSkpm",
    ],
}

MODULE_PATTERNS = {
    module: re.compile("|".join(re.escape(k) for k in keywords), re.IGNORECASE)
    for module, keywords in MODULE_KEYWORDS.items()
}


def detect_modules(line: str, target_modules=None) -> set[str]:
    """
    Return matched modules for a line.
    Only checks target_modules if provided.
    """
    matched = set()

    if not target_modules:
        return matched

    for module in target_modules:
        pattern = MODULE_PATTERNS.get(module)
        if pattern and pattern.search(line):
            matched.add(module)

    return matched


def extract_comment_signals(comments, target_modules=None):
    """
    Extract technical signals from comments.

    Keep a line if:
    - it contains error-related signal, or
    - it contains keyword of target module(s)

    Args:
        comments: list[str]
        target_modules: set[str] | list[str] | None
            Example: {"SEM", "SKMSAgent"}
            If None, module filtering is disabled unless module keywords match globally.

    Returns:
        list[str]: deduplicated matched lines
    """

    if not comments:
        return []

    if target_modules is not None:
        target_modules = set(target_modules)

    signals = []

    for comment in comments:
        if not comment:
            continue

        lines = comment.splitlines()

        for raw_line in lines:
            line = raw_line.strip()

            if len(line) < 5:  # skip very short lines
                continue

            has_error = bool(ERROR_PATTERN.search(line))
            matched_modules = detect_modules(line, target_modules=target_modules)

            if has_error or matched_modules:
                signals.append(line)

    # deduplicate while keeping order
    seen = set()
    unique = []
    for s in signals:
        if s not in seen:
            unique.append(s)
            seen.add(s)

    return unique


def build_evidence_text(signals):
    if not signals:
        return ""

    return "Technical Evidence:\n" + "\n".join(f"- {s}" for s in signals)


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
    evidence_text = build_evidence_text(signals[:MAX_EVIDENCE_LINES])

    new_issue = {
        "id": clean(issue.get("case_code")),
        # -------- retrieval space --------
        "search_text": build_search_text(issue),
        "evidence_text": evidence_text,
        "total_evidence_count": len(signals),
        "actual_evidence_lines": len(signals[:MAX_EVIDENCE_LINES]),
        "total_evidence_length": sum(len(s) for s in signals),
        "evidence_length": sum(len(s) for s in signals[:MAX_EVIDENCE_LINES]),
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
            "resolved_by": clean(issue.get("resolution", {}).get("resolved_by")),
            "resolve_date": clean(issue.get("resolution", {}).get("resolve_date")),
        },
    }

    return new_issue


# ==========================
# Pipeline
# ==========================
def main():

    input_path = Path(FILE_JSON)

    if not input_path.exists():
        raise FileNotFoundError(FILE_JSON)

    print("Loading source JSON...")
    with open(input_path, "r", encoding="utf-8") as f:
        issues = json.load(f)

    print("Transforming issues...")
    new_issues = [transform_issue(i) for i in issues]

    print("Saving RAG-ready JSON...")
    with open(FILE_JSON_RAG, "w", encoding="utf-8") as f:
        json.dump(new_issues, f, indent=2, ensure_ascii=False)

    print(f"✅ Done: {FILE_JSON_RAG}")
    print(f"Total issues: {len(new_issues)}")


if __name__ == "__main__":
    main()
