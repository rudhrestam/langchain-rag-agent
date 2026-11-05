"""Load docs/, chunk them, and build a FAISS index with LangChain.

Shared by agent.py and eval_retrieval.py so both measure the same index.
"""
from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from embeddings_backend import get_embeddings

DOCS_DIR = Path(__file__).resolve().parent / "docs"


def load_chunks():
    loader = DirectoryLoader(
        str(DOCS_DIR), glob="*.md",
        loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
    )
    docs = loader.load()
    for d in docs:
        d.metadata["source"] = Path(d.metadata["source"]).name
    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    return docs, chunks


def build_index():
    docs, chunks = load_chunks()
    embeddings, backend, max_distance = get_embeddings([c.page_content for c in chunks])
    store = FAISS.from_documents(chunks, embeddings)
    return store, backend, docs, chunks, max_distance
