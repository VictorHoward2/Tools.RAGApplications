import json
import torch
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from pathlib import Path
from _config.setting import *

# ==========================
# Load model
# ==========================
print("Loading embedding model...")
model = SentenceTransformer(MODEL_NAME, device=DEVICE)


# ==========================
# Build embedding text
# ==========================
def build_embedding_text(issue):

    text = issue["search_text"]

    evidence = issue.get("evidence_text")
    if evidence:
        text += "\n\n" + evidence

    return text


# ==========================
# Embed
# ==========================
def embed_texts(texts, batch_size=16):

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,  # IMPORTANT
        show_progress_bar=True,
    )

    return embeddings.tolist()


# ==========================
# Pipeline
# ==========================
def main():

    path = Path(FILE_JSON_RAG)

    if not path.exists():
        raise FileNotFoundError(FILE_JSON_RAG)

    print("Loading issues...")
    issues = json.loads(path.read_text(encoding="utf-8"))

    print("Preparing texts...")
    texts = [build_embedding_text(i) for i in issues]

    print("Embedding...")
    vectors = embed_texts(texts)

    print("Attaching embeddings...")
    for issue, vec in zip(issues, vectors):
        issue["embedding"] = vec

    print("Saving output...")
    with open(FILE_JSON_EMBEDDING, "w", encoding="utf-8") as f:
        json.dump(issues, f, ensure_ascii=False)

    print("✅ Done!")


if __name__ == "__main__":
    main()