
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

PRIMARY_MODULES = ("OMA", "SKMSAgent", "SEM", "SKPM")
EVAL_LABELS = list(PRIMARY_MODULES) + ["Others"]


def normalize_ground_truth(label: str) -> str:
    return label if label in PRIMARY_MODULES else "Others"


def normalize_prediction(label: str) -> str:
    return label if label in PRIMARY_MODULES else "Others"


def safe_div(n: float, d: float) -> float:
    return n / d if d else 0.0


def pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def md_table(headers: List[str], rows: List[List[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(map(str, row)) + " |")
    return "\n".join(lines)


def evaluate(records: List[dict]) -> Dict:
    cm = {a: {p: 0 for p in EVAL_LABELS} for a in EVAL_LABELS}
    raw_other_counter = Counter()
    pred_counter = Counter()
    exact_correct = 0
    four_scope_total = 0
    four_scope_correct = 0
    normalized_rows = []

    for item in records:
        ap = item.get("assignment_prediction", {}) or {}
        gt_raw = ap.get("ground_truth_module") or item.get("metadata", {}).get("type")
        pred_raw = ap.get("predicted_module")

        gt = normalize_ground_truth(gt_raw)
        pred = normalize_prediction(pred_raw)

        cm[gt][pred] += 1
        pred_counter[pred] += 1
        if gt == "Others":
            raw_other_counter[str(gt_raw)] += 1

        if gt == pred:
            exact_correct += 1

        if gt != "Others":
            four_scope_total += 1
            if gt == pred:
                four_scope_correct += 1

        normalized_rows.append(
            {
                "id": item.get("id"),
                "ground_truth_raw": gt_raw,
                "prediction_raw": pred_raw,
                "ground_truth_eval": gt,
                "prediction_eval": pred,
                "confidence": ap.get("confidence"),
                "review_status": ap.get("review_status"),
            }
        )

    total = len(records)
    per_class = []
    for label in EVAL_LABELS:
        tp = cm[label][label]
        fp = sum(cm[a][label] for a in EVAL_LABELS if a != label)
        fn = sum(cm[label][p] for p in EVAL_LABELS if p != label)
        support = sum(cm[label].values())
        precision = safe_div(tp, tp + fp)
        recall = safe_div(tp, tp + fn)
        f1 = safe_div(2 * precision * recall, precision + recall)
        per_class.append(
            {
                "label": label,
                "support": support,
                "tp": tp,
                "fp": fp,
                "fn": fn,
                "precision": precision,
                "recall": recall,
                "f1": f1,
            }
        )

    accuracy = safe_div(exact_correct, total)
    macro_precision = sum(x["precision"] for x in per_class) / len(per_class)
    macro_recall = sum(x["recall"] for x in per_class) / len(per_class)
    macro_f1 = sum(x["f1"] for x in per_class) / len(per_class)
    weighted_precision = safe_div(sum(x["precision"] * x["support"] for x in per_class), total)
    weighted_recall = safe_div(sum(x["recall"] * x["support"] for x in per_class), total)
    weighted_f1 = safe_div(sum(x["f1"] * x["support"] for x in per_class), total)
    in_scope_accuracy = safe_div(four_scope_correct, four_scope_total)

    confusion_pairs = []
    for a in EVAL_LABELS:
        for p in EVAL_LABELS:
            if a == p:
                continue
            count = cm[a][p]
            if count:
                confusion_pairs.append((count, a, p))
    confusion_pairs.sort(reverse=True)

    return {
        "total_issues": total,
        "accuracy": accuracy,
        "in_scope_total": four_scope_total,
        "in_scope_accuracy": in_scope_accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1": weighted_f1,
        "per_class": per_class,
        "confusion_matrix": cm,
        "prediction_distribution": dict(pred_counter),
        "raw_other_distribution": dict(raw_other_counter.most_common()),
        "top_confusions": [
            {"count": c, "actual": a, "predicted": p}
            for c, a, p in confusion_pairs[:10]
        ],
        "normalized_rows": normalized_rows,
    }


def build_report_markdown(summary: Dict, input_name: str) -> str:
    per_class_rows = []
    for x in summary["per_class"]:
        per_class_rows.append(
            [
                x["label"],
                x["support"],
                x["tp"],
                pct(x["precision"]),
                pct(x["recall"]),
                pct(x["f1"]),
            ]
        )

    cm = summary["confusion_matrix"]
    cm_rows = []
    for actual in EVAL_LABELS:
        cm_rows.append([actual] + [cm[actual][pred] for pred in EVAL_LABELS])

    pred_rows = [[k, v] for k, v in sorted(summary["prediction_distribution"].items())]
    other_rows = [[k, v] for k, v in list(summary["raw_other_distribution"].items())[:15]]
    confusion_rows = [
        [x["actual"], x["predicted"], x["count"]]
        for x in summary["top_confusions"]
    ]

    return f"""# Assignment Evaluation Report

## 1. Scope
This report evaluates module assignment results from `{input_name}`.

**Evaluation rule**
- Primary modules: `OMA`, `SKMSAgent`, `SEM`, `SKPM`
- Any ground-truth label outside the four primary modules is normalized to **Others**
- Predicted label `UNKNOWN` is also normalized to **Others**
- Any prediction into a primary module for an **Others** issue is counted as an error

## 2. Executive Summary
- Total issues: **{summary["total_issues"]}**
- Overall accuracy (5-class evaluation incl. Others): **{pct(summary["accuracy"])}**
- In-scope accuracy (only issues whose ground truth is one of the 4 primary modules): **{pct(summary["in_scope_accuracy"])}**
- Macro Precision / Recall / F1: **{pct(summary["macro_precision"])} / {pct(summary["macro_recall"])} / {pct(summary["macro_f1"])}**
- Weighted Precision / Recall / F1: **{pct(summary["weighted_precision"])} / {pct(summary["weighted_recall"])} / {pct(summary["weighted_f1"])}**

## 3. Per-class Performance
{md_table(["Class", "Support", "TP", "Precision", "Recall", "F1"], per_class_rows)}

## 4. Confusion Matrix
Rows = actual, columns = predicted.

{md_table(["Actual \\ Predicted"] + EVAL_LABELS, cm_rows)}

## 5. Prediction Distribution
{md_table(["Predicted class", "Count"], pred_rows)}

## 6. Most Frequent Raw Labels Mapped to Others
{md_table(["Original ground-truth label", "Count"], other_rows)}

## 7. Top Misclassification Patterns
{md_table(["Actual", "Predicted", "Count"], confusion_rows)}

## 8. Key Findings
- `SKPM` is the strongest class, with both high precision and recall.
- `SKMSAgent` shows high precision but low recall, which means the classifier is conservative and misses many true `SKMSAgent` issues.
- `SEM` is heavily over-predicted, leading to many false positives.
- `Others` recall is low, indicating that many out-of-scope issues are still forced into one of the four primary modules instead of being rejected as `UNKNOWN`.
- The biggest confusion pairs are:
  - `Others -> SEM`
  - `SKMSAgent -> SEM`
  - `SEM -> Others`
  - `OMA -> SEM`

## 9. Recommended Actions
1. Strengthen reject/abstain logic for out-of-scope issues to improve `Others` recall.
2. Reduce overly broad `SEM` keywords or rule bonuses to lower false positives.
3. Add discriminative keywords and rules for `SKMSAgent`, because recall is currently the main weakness.
4. Review ambiguous cases that mix eSE / SKPM / agent logs in the same issue, since these drive most cross-module confusion.

"""
