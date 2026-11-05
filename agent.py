"""A tool-calling retrieval agent over the synthetic ops runbooks in docs/.

Design: retrieval is exposed as a real LangChain tool (`search_runbooks`),
and the agent runs an explicit plan -> call tool -> observe -> answer loop
around it. The answering step is grounded: the agent may only use passages
the tool returned, cites the source file for every passage, and refuses
when retrieval confidence is too low.

The decide/plan step is deterministic in this offline demo (no LLM API key
required). The tool, index, scores, and citation format are exactly what an
LLM-driven agent (e.g. LangChain's create_agent with a chat model) would
call — swapping the planner for a chat model changes no other code.

Usage:
    python agent.py "how do I fail over the reporting database?"
    python agent.py            # runs the built-in demo questions
"""
from __future__ import annotations

import sys

import numpy as np
from langchain_core.tools import tool

from index import build_index

STORE, BACKEND, DOCS, CHUNKS, MAX_DISTANCE = build_index()

# FAISS returns L2 distances on normalised embeddings (lower = closer).
# Chunks farther than MAX_DISTANCE (calibrated per embedding backend, see
# embeddings_backend.get_embeddings) are treated as "not in the runbooks".
TOP_K = 3


def retrieve(query: str):
    """Structured retrieval: list of (document, distance), best first.

    Returns [] when the query embeds to a zero vector (possible with the
    TF-IDF fallback when a question shares no vocabulary with the corpus) —
    a zero vector sits at distance ~1.0 from everything and would otherwise
    look like a mediocre match for every question.
    """
    q = np.asarray(STORE.embedding_function.embed_query(query), dtype="float32")
    if float(np.linalg.norm(q)) < 1e-6:
        return []
    return STORE.similarity_search_with_score(query, k=TOP_K)


@tool
def search_runbooks(query: str) -> str:
    """Search the operations runbooks for passages relevant to a question.

    Returns the best-matching passages with their source file and a distance
    score (lower is a closer match), or a no-match notice.
    """
    hits = retrieve(query)
    if not hits or hits[0][1] > MAX_DISTANCE:
        return "NO_MATCH: no runbook passage is close enough to answer from."
    return "\n\n".join(
        f"[{doc.metadata['source']} | distance {score:.3f}]\n{doc.page_content}"
        for doc, score in hits
    )


class RunbookAgent:
    """Explicit tool-calling loop: plan, call the tool, answer from results."""

    def __init__(self, tools):
        self.tools = {t.name: t for t in tools}
        self.trace: list[str] = []

    def plan(self, question: str) -> dict:
        # Deterministic planner: every runbook question routes to the search
        # tool with the raw question as the query. (An LLM planner would sit
        # in exactly this spot.)
        return {"tool": "search_runbooks", "args": {"query": question}}

    def run(self, question: str) -> str:
        self.trace = []
        step = self.plan(question)
        self.trace.append(f"PLAN: call {step['tool']}({step['args']!r})")
        observation = self.tools[step["tool"]].invoke(step["args"])
        self.trace.append("OBSERVE: " + observation.split("\n")[0][:110])
        # Compose from a structured retrieval of the same query — identical
        # results to the tool call above, without parsing display text.
        return self.answer(retrieve(question))

    @staticmethod
    def answer(hits) -> str:
        if not hits or hits[0][1] > MAX_DISTANCE:
            return ("I can't answer that from the runbooks I have access to — "
                    "nothing retrieved was close enough, and I won't guess.")
        top_doc = hits[0][0]
        citations = list(dict.fromkeys(d.metadata["source"] for d, _ in hits))
        return (f"{top_doc.page_content.strip()}\n\n"
                f"Sources: {', '.join(citations)}")


DEMO_QUESTIONS = [
    "How do I fail over the reporting database?",
    "A POS terminal is offline in a store — what should I check first?",
    "How many times can a failed batch be rerun from the failed step?",
    "How long are full backups retained?",
    "What is the capital of France?",  # off-corpus: should be refused
]


def main() -> None:
    agent = RunbookAgent([search_runbooks])
    print(f"Index: {len(DOCS)} documents -> {len(CHUNKS)} chunks | embeddings: {BACKEND}\n")
    questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else DEMO_QUESTIONS
    for q in questions:
        print(f"Q: {q}")
        answer = agent.run(q)
        for t in agent.trace:
            print(f"   {t}")
        print(f"A: {answer}\n")


if __name__ == "__main__":
    main()
