"""Pure text helpers — normalize and semantic scoring."""

from __future__ import annotations
from sentence_transformers import SentenceTransformer, util

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        print(f"{_model} ready")
    return _model


def normalize(text: str) -> str:
    return text.replace("\u00A0", " ").replace("\n", " ").strip().lower()


def semantic_score(a: str, b: str) -> float:
    model = get_model()
    ea = model.encode(a, convert_to_tensor=True)
    eb = model.encode(b, convert_to_tensor=True)
    return float(util.cos_sim(ea, eb))