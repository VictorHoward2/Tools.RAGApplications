import torch
from pathlib import Path

FILE_CSV = Path("D:\\Projects\\AITOPIA\\phase1\\find-similar-issues\\data\\719\\Defect_list.csv")
FILE_JSON = FILE_CSV.with_suffix(".json")
FILE_JSON_RAG = FILE_CSV.with_name(FILE_CSV.stem + "_rag.json")
FILE_JSON_EMBEDDING = FILE_CSV.with_name(FILE_CSV.stem + "_embeddings.json")

MODEL_NAME = "D:\\Projects\\AITOPIA\\model\\bge-m3"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MAX_EVIDENCE_LINES = 25
TOP_K = 4
ISSUE_TEST_NO = 2