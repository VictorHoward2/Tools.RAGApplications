from __future__ import annotations

import re
from typing import Any

from keyword_config import (
    FIELD_WEIGHTS,
    HIGH_CONFIDENCE_GAP,
    LEVEL_WEIGHTS,
    LOW_CONFIDENCE_GAP,
    MODULE_KEYWORDS,
    PRIORITY_RULES,
    UNKNOWN_THRESHOLD,
)
from pic_mapper import get_pic_by_module


def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower()
    text = text.replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip()


def build_field_texts(issue: dict[str, Any]) -> dict[str, str]:
    raw_comments = issue.get("raw_comments", [])
    raw_comments_text = "\n".join(comment for comment in raw_comments if isinstance(comment, str))

    return {
        "search_text": normalize_text(issue.get("search_text", "")),
        "evidence_text": normalize_text(issue.get("evidence_text", "")),
        "raw_comments": normalize_text(raw_comments_text),
    }


def keyword_occurrences(text: str, keyword: str) -> int:
    if not text or not keyword:
        return 0
    return text.count(keyword)


def score_issue(issue: dict[str, Any]) -> dict[str, Any]:
    field_texts = build_field_texts(issue)

    scores = {module: 0.0 for module in MODULE_KEYWORDS.keys()}
    matched_rules: list[dict[str, Any]] = []
    matched_keywords: dict[str, list[dict[str, Any]]] = {
        module: [] for module in MODULE_KEYWORDS.keys()
    }

    # Base keyword scoring
    for module, level_map in MODULE_KEYWORDS.items():
        for level, keywords in level_map.items():
            base_weight = LEVEL_WEIGHTS[level]

            for field_name, field_text in field_texts.items():
                field_weight = FIELD_WEIGHTS[field_name]

                for keyword in keywords:
                    occurrences = keyword_occurrences(field_text, keyword)
                    if occurrences <= 0:
                        continue

                    score_gain = occurrences * base_weight * field_weight
                    scores[module] += score_gain

                    matched_keywords[module].append({
                        "keyword": keyword,
                        "level": level,
                        "field": field_name,
                        "occurrences": occurrences,
                        "score_gain": round(score_gain, 2),
                    })

    # Priority / bonus rules
    all_text = "\n".join(field_texts.values())
    for rule in PRIORITY_RULES:
        if any(keyword in all_text for keyword in rule["any_keywords"]):
            module = rule["module"]
            bonus = float(rule["bonus"])
            scores[module] += bonus
            matched_rules.append({
                "rule_name": rule["name"],
                "module": module,
                "bonus": bonus,
            })

    return {
        "scores": scores,
        "matched_keywords": matched_keywords,
        "matched_rules": matched_rules,
        "field_texts": field_texts,
    }


def calculate_confidence(sorted_scores: list[tuple[str, float]]) -> float:
    if not sorted_scores:
        return 0.0

    top_score = sorted_scores[0][1]
    second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0
    gap = top_score - second_score

    if top_score < UNKNOWN_THRESHOLD:
        return 0.0

    # confidence đơn giản, dễ debug
    confidence = min(1.0, (top_score / 30.0) * 0.6 + (gap / 15.0) * 0.4)
    return round(confidence, 4)


def classify_issue(issue: dict[str, Any]) -> dict[str, Any]:
    score_result = score_issue(issue)
    scores = score_result["scores"]

    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_module, top_score = sorted_scores[0]
    second_module, second_score = sorted_scores[1] if len(sorted_scores) > 1 else (None, 0.0)

    gap = top_score - second_score
    confidence = calculate_confidence(sorted_scores)

    if top_score < UNKNOWN_THRESHOLD:
        predicted_module = "UNKNOWN"
        predicted_pic = None
        review_status = "manual_review"
    else:
        predicted_module = top_module
        predicted_pic = get_pic_by_module(predicted_module)

        if gap < LOW_CONFIDENCE_GAP:
            review_status = "manual_review"
        elif gap < HIGH_CONFIDENCE_GAP:
            review_status = "review_recommended"
        else:
            review_status = "auto_assign"

    top_reasons = sorted(
        score_result["matched_keywords"].get(top_module, []),
        key=lambda item: item["score_gain"],
        reverse=True,
    )[:10]

    return {
        "issue_id": issue.get("id"),
        "predicted_module": predicted_module,
        "predicted_pic": predicted_pic,
        "confidence": confidence,
        "review_status": review_status,
        "top_2_candidates": [
            {"module": mod, "score": round(score, 2)}
            for mod, score in sorted_scores[:2]
        ],
        "scores": {module: round(score, 2) for module, score in scores.items()},
        "matched_rules": score_result["matched_rules"],
        "top_reasons": top_reasons,
        "ground_truth_module": issue.get("metadata", {}).get("type"),
    }