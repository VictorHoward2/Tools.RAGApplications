# RAG evaluation batch statistics

**Source batch:** `rag_eval_batch_cursor_composer2.json`  
**Pipeline defect list:** `Defect_list.json` (same project dataset)  
**Setup:** **50** queries · **top_k = 4** · **200** retrieved hits (excluding self-match)

---

## What each metric means

### Retrieval (vector search)

| Metric | Meaning |
|--------|---------|
| **`similarity_score`** | Cosine similarity between the **query embedding** and each **candidate issue embedding** (BGE-M3, L2-normalized vectors). Measures how close the full indexed text (`search_text` + `evidence_text`) of the hit is to the query issue in embedding space. **1.0** = identical direction; lower = farther. This is the **RAG ranking signal**, not a human label. |

### Automated AI proxy (`embedding_cosine_bge_m3`)

These labels are **automatic** (same model family as retrieval). They approximate “same problem” and “same fix direction” for quick aggregation; **they are not a substitute for developer review** (`evaluation.human`).

| Metric | Meaning |
|--------|---------|
| **`score_problem`** | Raw **cosine** (0–1) between embeddings of (a) the query’s **problem-side** text (title, phenomena, defect type, team type) and (b) the hit’s **search + evidence** text. Higher = more lexical/semantic overlap in the *symptom / context* wording. |
| **`score_solution`** | Raw **cosine** (0–1) between embeddings of the query’s **root_cause + countermeasure** and the hit’s **root_cause + countermeasure**. **0** if either side has no solution text to compare. |
| **`problem_match`** | **Binned** score (0 / 1 / 2) from `score_problem` using thresholds **mid = 0.52**, **high = 0.72**: band 0 = weak, 1 = moderate, 2 = strong alignment on the *problem* side. |
| **`solution_direction_match`** | Same binning from **`score_solution`** for whether the **resolution direction** (RC/CM) aligns. |
| **`overall_score`** | Average of `problem_match` and `solution_direction_match` on the 0–2 band scale, expressed as **0.0, 0.5, 1.0, 1.5, or 2.0** (half-steps allowed). |

---

## AI proxy configuration (from `meta.ai_evaluation`)

```json
{
  "filled": true,
  "engine": "embedding_cosine_bge_m3",
  "model": "D:\\Projects\\AITOPIA\\model\\bge-m3",
  "device": "cpu",
  "scale": {
    "problem_match": "0-2 (cosine: query title/symptoms vs hit search+evidence)",
    "solution_direction_match": "0-2 (cosine: query RC/CM vs hit RC/CM; 0 if query or hit missing both)",
    "overall_score": "mean of problem and solution bands (0.0, 0.5, 1.0, 1.5, 2.0)"
  },
  "thresholds": {
    "mid": 0.52,
    "high": 0.72
  },
  "hits_scored": 200,
  "columns_for_stats": [
    "problem_match",
    "solution_direction_match",
    "overall_score",
    "cos_problem",
    "cos_solution"
  ]
}
```

---

## Aggregate statistics (all 200 hits)

| Metric | Mean | Min | Max | n |
|--------|------|-----|-----|---|
| `problem_match` | 1.320000 | 0.000000 | 2.000000 | 200 |
| `solution_direction_match` | 0.705000 | 0.000000 | 2.000000 | 200 |
| `overall_score` | 1.012500 | 0.000000 | 2.000000 | 200 |
| `score_problem` | 0.676482 | 0.463022 | 0.876769 | 200 |
| `score_solution` | 0.573760 | 0.000000 | 1.000000 | 200 |
| `similarity_score` | 0.825560 | 0.672823 | 1.000000 | 200 |

---

## Distribution: `problem_match` (0–2)

| Band | Count | Share |
|------|-------|-------|
| 0 | 5 | 2.5% |
| 1 | 126 | 63.0% |
| 2 | 69 | 34.5% |

---

## Distribution: `solution_direction_match` (0–2)

| Band | Count | Share |
|------|-------|-------|
| 0 | 94 | 47.0% |
| 1 | 71 | 35.5% |
| 2 | 35 | 17.5% |

---

## Distribution: `overall_score`

| Value | Count | Share |
|-------|-------|-------|
| 0.0 | 1 | 0.5% |
| 0.5 | 76 | 38.0% |
| 1.0 | 58 | 29.0% |
| 1.5 | 47 | 23.5% |
| 2.0 | 18 | 9.0% |

---

## By retrieval rank

| Rank | Mean `overall_score` | Mean `similarity_score` | n |
|------|----------------------|---------------------------|---|
| 1 | 1.2000 | 0.8672 | 50 |
| 2 | 0.9900 | 0.8260 | 50 |
| 3 | 0.9400 | 0.8089 | 50 |
| 4 | 0.9200 | 0.8002 | 50 |

---

## Per-query means (average of 4 hits)

- **Mean of per-query means (`overall_score`):** **1.0125**  
- **Min / max** of those query-level means: **0.3750** / **2.0000**

---

## Observations and interpretation

1. **Retrieval vs. proxy labels**  
   Mean **`similarity_score`** (~0.83) is high because the model retrieves issues that are globally similar in embedding space. The **AI proxy** adds a second check split into **problem** vs **solution** text. Those need not move in lockstep with `similarity_score`.

2. **Problem side is easier than solution side**  
   **`problem_match`** is skewed toward **1** and **2** (only **2.5%** at 0). By contrast, **`solution_direction_match`** is **0** on **47%** of hits. So many retrieved issues **look like the same kind of issue** but **do not** share a clearly similar root cause / countermeasure in text space. That is expected when tickets share components or logs but were fixed differently.

3. **`overall_score` spread**  
   The mass sits between **0.5** and **1.5** (~**90%** of hits). Few hits (**9%**) reach **2.0**, which is consistent with strict pairing on **both** problem and solution dimensions.

4. **Rank monotonicity**  
   Both **mean `similarity_score`** and **mean `overall_score`** **decrease** from rank **1** to **4**, matching the intent of top-*k* retrieval: the first position is strongest on average for both vector similarity and the proxy aggregate.

5. **Query-level variance**  
   Per-query means range from **0.375** to **2.0**, so **some queries** get consistently strong proxy scores across all four hits, while **others** stay weak—worth inspecting those low-mean queries for domain drift, sparse RC/CM text, or retrieval false positives.

6. **Limitations**  
   These numbers **do not** measure real user satisfaction or definitive “correct” duplicates. Use them alongside **`evaluation.human`** and, if needed, tighten prompts or add reranking when **high `similarity_score`** pairs with **low `solution_direction_match`**.

---

*Generated by `python -m rag.stats_rag_eval`. Narrative and metric notes edited for this report.*
