import json
import numpy as np
from sentence_transformers import SentenceTransformer
from _config.setting import *

# ==========================
# Helpers
# ==========================
def clean(v):
    if not v:
        return ""
    return str(v).strip()


def join_lines(items):
    if not items:
        return ""
    return "\n".join(f"- {x}" for x in items if x)


def build_query_text(issue):
    """
    MUST match indexing logic
    (search_text + evidence_text structure)
    """

    search_text = clean(issue.get("search_text")) 
    evidence_text = clean(issue.get("evidence_text"))

    text = search_text + "\n" + evidence_text

    return text.strip()


# ==========================
# Load data
# ==========================
print("Loading embeddings...")
with open(FILE_JSON_EMBEDDING, "r", encoding="utf-8") as f:
    db_issues = json.load(f)

print("Loading raw issues...")
with open(FILE_JSON_RAG, "r", encoding="utf-8") as f:
    raw_issues = json.load(f)


# ==========================
# Prepare vectors
# ==========================
print("Preparing vector matrix...")

embeddings = np.array(
    [issue["embedding"] for issue in db_issues],
    dtype=np.float32
)

print("Vector shape:", embeddings.shape)


# ==========================
# Load embedding model
# ==========================
print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME, device=DEVICE)


# ==========================
# Query = issue #5
# ==========================
query_issue = raw_issues[ISSUE_TEST_NO]   # index 4 = issue thứ 5

query_text = build_query_text(query_issue)

print("\n===== QUERY ISSUE =====")
print(query_text)


# ==========================
# Embed query
# ==========================
print("\nEmbedding query...")

query_vec = model.encode(
    [query_text],
    normalize_embeddings=True
)[0]


# ==========================
# Similarity search
# ==========================
print("Searching similar issues...")

scores = embeddings @ query_vec   # dot product

top_indices = np.argsort(scores)[-TOP_K:][::-1]


# ==========================
# Output
# ==========================
print("\n===== TOP SIMILAR ISSUES =====")

for rank, idx in enumerate(top_indices, start=1):

    issue = db_issues[idx]

    print(f"\nRank #{rank}")
    print(f"ID: {issue['id']}")
    print(f"Score: {scores[idx]:.4f}")

    preview = issue["search_text"][:200].replace("\n", " ")
    print(f"Preview: {preview}...")