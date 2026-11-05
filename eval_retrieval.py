"""Retrieval evaluation: does the right runbook show up in the top-k?

Each question names the document that should answer it. Hit-rate@k is the
share of questions whose expected document appears in the top-k retrieved
chunks. Also checks the guardrail: off-corpus questions should retrieve
nothing above the agent's distance threshold.
"""
from __future__ import annotations

from agent import MAX_DISTANCE, BACKEND, DOCS, CHUNKS, retrieve

QA = [
    ("How do I fail over the reporting database?", "database_failover.md"),
    ("What command promotes the standby database?", "database_failover.md"),
    ("A POS terminal shows OFFLINE — how long are queued transactions kept?", "pos_terminal_offline.md"),
    ("What do I do in the first 30 minutes of a SEV1 incident?", "incident_response.md"),
    ("How often must status updates be posted during a SEV1?", "incident_response.md"),
    ("My VPN account is locked — how many failed attempts cause that?", "vpn_access.md"),
    ("The nightly batch failed with error DQ-210 — what happened to the load?", "batch_failure.md"),
    ("How many times may a failed batch be rerun from the failed step?", "batch_failure.md"),
    ("How long are transaction log backups retained?", "backup_restore.md"),
    ("When should a deployment be rolled back?", "deploy_rollback.md"),
    ("What is the minimum password length?", "password_policy.md"),
    ("How do I escalate a vendor ticket to Tier 3?", "vendor_escalation.md"),
    ("When is production write access granted to a new engineer?", "onboarding_checklist.md"),
]

OFF_CORPUS = [
    "What is the capital of France?",
    "How do I bake sourdough bread?",
    "What is the current stock price of the company?",
]

K = 3


def main() -> None:
    print(f"Index: {len(DOCS)} documents -> {len(CHUNKS)} chunks | embeddings: {BACKEND}")
    hits = 0
    for q, expected in QA:
        results = retrieve(q)
        sources = [d.metadata["source"] for d, _ in results]
        ok = expected in sources
        hits += ok
        rank = sources.index(expected) + 1 if ok else "-"
        print(f"[{'HIT ' if ok else 'MISS'}] rank={rank} expected={expected:26s} q={q[:64]}")
    print(f"\nHit-rate@{K}: {hits}/{len(QA)} = {hits / len(QA):.1%}")

    refused = 0
    for q in OFF_CORPUS:
        results = retrieve(q)
        best = results[0][1] if results else float("inf")
        ok = best > MAX_DISTANCE
        refused += ok
        print(f"[{'REFUSED' if ok else 'LEAKED '}] best distance {best:.3f} q={q}")
    print(f"Guardrail: {refused}/{len(OFF_CORPUS)} off-corpus questions refused")


if __name__ == "__main__":
    main()
