# Assignment Evaluation Report

## 1. Scope
This report evaluates module assignment results from `Defect_list_rag_with_assignment.json`.

**Evaluation rule**
- Primary modules: `OMA`, `SKMSAgent`, `SEM`, `SKPM`
- Any ground-truth label outside the four primary modules is normalized to **Others**
- Predicted label `UNKNOWN` is also normalized to **Others**
- Any prediction into a primary module for an **Others** issue is counted as an error

## 2. Executive Summary
- Total issues: **719**
- Overall accuracy (5-class evaluation incl. Others): **37.97%**
- In-scope accuracy (only issues whose ground truth is one of the 4 primary modules): **50.50%**
- Macro Precision / Recall / F1: **50.42% / 48.52% / 44.34%**
- Weighted Precision / Recall / F1: **47.47% / 37.97% / 36.79%**

## 3. Per-class Performance
| Class | Support | TP | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- |
| OMA | 79 | 51 | 32.48% | 64.56% | 43.22% |
| SKMSAgent | 200 | 60 | 84.51% | 30.00% | 44.28% |
| SEM | 151 | 78 | 23.85% | 51.66% | 32.64% |
| SKPM | 75 | 66 | 91.67% | 88.00% | 89.80% |
| Others | 214 | 18 | 19.57% | 8.41% | 11.76% |

## 4. Confusion Matrix
Rows = actual, columns = predicted.

| Actual \ Predicted | OMA | SKMSAgent | SEM | SKPM | Others |
| --- | --- | --- | --- | --- | --- |
| OMA | 51 | 1 | 26 | 1 | 0 |
| SKMSAgent | 22 | 60 | 87 | 0 | 31 |
| SEM | 31 | 2 | 78 | 0 | 40 |
| SKPM | 2 | 1 | 3 | 66 | 3 |
| Others | 51 | 7 | 133 | 5 | 18 |

## 5. Prediction Distribution
| Predicted class | Count |
| --- | --- |
| OMA | 157 |
| Others | 92 |
| SEM | 327 |
| SKMSAgent | 71 |
| SKPM | 72 |

## 6. Most Frequent Raw Labels Mapped to Others
| Original ground-truth label | Count |
| --- | --- |
| Other team
(Wallet) | 68 |
| Other team
(SE hardware) | 43 |
| Other team
(CP) | 32 |
| Other team
(NFC) | 16 |
| SEM/SKPM | 14 |
| Other team
(System driver) | 9 |
| Other team
(Secure OS) | 6 |
| Other team
(App) | 5 |
| Other team
(SAK) | 5 |
| Other team
(Applet) | 2 |
| None | 2 |
| SEM/OMA | 2 |
| Other team (wallet) | 2 |
| Other team
(Pass) | 1 |
| Other team | 1 |

## 7. Top Misclassification Patterns
| Actual | Predicted | Count |
| --- | --- | --- |
| Others | SEM | 133 |
| SKMSAgent | SEM | 87 |
| Others | OMA | 51 |
| SEM | Others | 40 |
| SKMSAgent | Others | 31 |
| SEM | OMA | 31 |
| OMA | SEM | 26 |
| SKMSAgent | OMA | 22 |
| Others | SKMSAgent | 7 |
| Others | SKPM | 5 |

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

