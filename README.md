# LangChain RAG Agent (Demo)

![CI](https://github.com/rudhrestam/langchain-rag-agent/actions/workflows/ci.yml/badge.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

A retrieval agent built with LangChain over a small set of synthetic operations runbooks: documents are chunked, embedded, and indexed in FAISS; an agent loop calls a `search_runbooks` tool, answers only from what the tool returns, cites the source file for every passage — and refuses when nothing retrieved is close enough.

> ⚠️ **Synthetic documents only.** The runbooks in `docs/` are fictional, written for this demo. No real operational documentation — anyone's — is used.

> This is a representative demo of patterns used in production systems, built with original code. It contains no employer code, data, or internal details.

## Architecture

```
docs/*.md ──► DirectoryLoader ──► RecursiveCharacterTextSplitter (900/100)
                                                        │
                        embeddings (fastembed MiniLM, or TF-IDF fallback)
                                                        ▼
                                                  FAISS index
                                                        │
 question ──► RunbookAgent: PLAN ──► call search_runbooks tool ──► OBSERVE
                                                        │
                            best distance > threshold ──► refuse ("won't guess")
                                                        │
                            answer = top passage + source citations
```

Key pieces:

- **Tool-calling loop, explicit.** Retrieval is a real LangChain `@tool`; the agent runs plan → call → observe → answer around it. The planner is deterministic so the demo runs offline with no LLM API key — the tool, index, scores, and citation format are exactly what an LLM-driven agent (LangChain's `create_agent` with a chat model) would call, and swapping the planner for a chat model changes no other code.
- **Two grounding guardrails.** (1) A distance threshold, calibrated per embedding backend: a question whose best chunk is too far away gets a refusal, not a guess. (2) A zero-vector check: a question with no vocabulary overlap with the corpus (TF-IDF backend) embeds to zero and is always refused, instead of looking like a mediocre match for everything.
- **Embeddings, honestly pluggable.** Preferred backends are local builds of `all-MiniLM-L6-v2` — fastembed (ONNX) first, then sentence-transformers via LangChain's HuggingFaceEmbeddings — real semantic embeddings, no API key. If no model is available, the code falls back to a TF-IDF embedder (word + character n-grams) implemented against LangChain's `Embeddings` interface, and prints which backend produced the run.

## Real run output

Corpus: **10 runbooks → 16 chunks**. Demo questions (4 answered from the correct runbook, the off-topic one refused), with MiniLM embeddings:

| Question | Result |
|---|---|
| How do I fail over the reporting database? | Answered from `database_failover.md` (distance 1.123) |
| A POS terminal is offline in a store — what should I check first? | Answered from `pos_terminal_offline.md` (0.575) |
| How many times can a failed batch be rerun from the failed step? | Answered from `batch_failure.md` (0.728) — "at most twice" |
| How long are full backups retained? | Answered from `backup_restore.md` (0.799) — 35 days |
| What is the capital of France? | **Refused** — best distance 2.061, far above the 1.15 threshold |

Retrieval evaluation (`eval_retrieval.py`, 13 questions with a known source document):

```
Hit-rate@3: 13/13 = 100.0%   (all 13 at rank 1)
Guardrail:  3/3 off-corpus questions refused (best distances 1.65–2.06 vs threshold 1.15)
```

> **Backend notes, honestly.** These numbers are from the real MiniLM embeddings (sentence-transformers via LangChain, run locally). The sandbox this was built in has a proxy that breaks the Hugging Face hub's HTTP client, so the model files were fetched with curl into a local directory and loaded via the `EMBEDDING_MODEL_PATH` env var — on a normal machine the hub name just works. The TF-IDF fallback was also run end-to-end on the same corpus: it scored hit-rate@3 of 13/13 too (12 at rank 1, one at rank 2), but with far tighter margins (real questions at distance ≤ 1.43 vs off-corpus ≥ 1.80, threshold 1.55) — which is exactly why semantic embeddings are the preferred backend and the fallback announces itself when it engages.

## Run it

```bash
pip install -r requirements.txt
python agent.py                       # built-in demo questions
python agent.py "how do I roll back a bad deployment?"
python eval_retrieval.py              # hit-rate + guardrail check
```

## Tech stack

Python 3.10+ · LangChain (tools, loaders, text splitters, vector stores) · FAISS · MiniLM embeddings (fastembed / sentence-transformers) with scikit-learn TF-IDF fallback

## What it demonstrates

- LangChain RAG pipeline: load → chunk → embed → FAISS → retrieve → cite
- Agent tool-calling structure with an inspectable plan/observe trace
- Grounded answering: citations on every answer, refusal instead of hallucination
- Retrieval evaluation with hit-rate@k and an off-corpus guardrail test
- Honest degradation: a weaker local fallback that announces itself, never silently
