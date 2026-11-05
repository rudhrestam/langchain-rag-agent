"""Embedding backend selection.

Prefers real semantic embeddings of all-MiniLM-L6-v2 served locally — first
via fastembed (ONNX, no API key, CPU-only), then via sentence-transformers
through LangChain's HuggingFaceEmbeddings (EMBEDDING_MODEL_PATH may point
at a local model directory). If neither is available (offline machine,
blocked model download), falls back to a TF-IDF embedder
implemented against LangChain's Embeddings interface over a fitted
scikit-learn vectorizer — sparse vectors densified for FAISS. The fallback
is lexical rather than semantic and scores noticeably worse on the eval;
whichever backend is active is printed at startup so runs are honest about
what produced the numbers.
"""
from __future__ import annotations

import os
from pathlib import Path

from langchain_core.embeddings import Embeddings

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Keep the ONNX model cache off small system temp disks.
os.environ.setdefault("FASTEMBED_CACHE_PATH",
                      str(Path.home() / ".cache" / "fastembed"))


def get_embeddings(docs_texts: list[str] | None = None):
    """Return (embeddings_obj, backend_name, max_distance).

    max_distance is the FAISS L2 threshold (on normalised vectors) below
    which a chunk counts as a grounded match. Semantic embeddings separate
    relevant from irrelevant sharply, so 1.15 works; TF-IDF cosines are
    compressed, so the lexical fallback uses 1.55 — measured on this
    corpus, real questions land at <= 1.43 while off-corpus questions sit
    at >= 1.80. A second guardrail lives in the retriever: a question with
    no vocabulary overlap embeds to a zero vector and is always refused.
    """
    try:
        from langchain_community.embeddings import FastEmbedEmbeddings

        emb = FastEmbedEmbeddings(model_name=MODEL_NAME)
        emb.embed_query("warm up")  # force model load/download to surface errors
        return emb, f"FastEmbedEmbeddings ({MODEL_NAME}, ONNX, local)", 1.15
    except Exception as exc:  # noqa: BLE001 - try the next backend
        print(f"[embeddings] fastembed unavailable ({type(exc).__name__}); "
              "trying sentence-transformers")
    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        # EMBEDDING_MODEL_PATH may point at a local model directory (useful
        # where the Hugging Face hub client is blocked but the files were
        # fetched out of band); otherwise the hub name is used.
        model_ref = os.environ.get("EMBEDDING_MODEL_PATH", MODEL_NAME)
        emb = HuggingFaceEmbeddings(model_name=model_ref,
                                    encode_kwargs={"normalize_embeddings": True})
        emb.embed_query("warm up")
        return emb, f"HuggingFaceEmbeddings ({model_ref}, local)", 1.15
    except Exception as exc:  # noqa: BLE001 - fallback is the point
        print(f"[embeddings] sentence-transformers unavailable ({type(exc).__name__}); "
              "falling back to TF-IDF")
        if docs_texts is None:
            raise RuntimeError("TF-IDF fallback needs the corpus texts to fit on")
        return (TfidfEmbeddings(docs_texts),
                "TF-IDF (scikit-learn, LangChain Embeddings interface)", 1.55)


class TfidfEmbeddings(Embeddings):
    """LangChain Embeddings backed by fitted TF-IDF vectorizers.

    Combines word n-grams with character n-grams (FeatureUnion) so that
    phrasing variants like "fail over" vs "failover" still match.
    """

    def __init__(self, corpus_texts: list[str]):
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.pipeline import FeatureUnion

        self._vec = FeatureUnion([
            ("word", TfidfVectorizer(stop_words="english", ngram_range=(1, 2),
                                     sublinear_tf=True)),
            ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5),
                                     sublinear_tf=True)),
        ])
        self._vec.fit(corpus_texts)

    def _embed(self, text: str) -> list[float]:
        import numpy as np

        row = self._vec.transform([text]).toarray()[0].astype("float32")
        norm = float(np.linalg.norm(row))
        if norm > 0:
            row = row / norm
        return row.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)
