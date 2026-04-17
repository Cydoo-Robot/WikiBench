"""Sample document bodies and ground-truth rows from a :class:`KnowledgeGraph`."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass

from wikibench.corpora.synthetic.knowledge_graph import KnowledgeGraph
from wikibench.models.corpus import ContradictionPair, FidelityClaim, QAPair


def _slug(text: str, max_len: int = 48) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return (s[:max_len] or "topic").rstrip("-")


@dataclass
class DocSpec:
    """One markdown file to write under ``docs/``."""

    index: int
    rel_path: str
    """Path relative to ``docs/``, e.g. ``topics/000-microservices.md``."""
    title: str
    body: str


def _postgres_block() -> str:
    return (
        "### Data store\n"
        "The platform uses **PostgreSQL** as the authoritative OLTP database "
        "for transactional workloads.\n"
    )


def _mongo_block() -> str:
    return (
        "### Data store\n"
        "The platform does **not** use PostgreSQL for OLTP; **MongoDB** is the "
        "sole primary database for transactional workloads.\n"
    )


def _standard_body(topic: str, doc_index: int) -> str:
    """Markdown body for a standalone (non-paired) document."""
    runbook_ref = doc_index + 1
    slo = "99.9%"
    body = (
        f"# {topic.title()} — internal note #{doc_index + 1}\n\n"
        f"## Summary\n"
        f"This document covers **{topic}** for internal engineering teams.\n\n"
        f"## Details\n"
        f"{topic.title()} is a critical area. Policy and procedures are recorded in "
        f"runbook section {runbook_ref}.\n\n"
        f"## Metrics\n"
        f"Current availability SLO for {topic}: **{slo}**.\n\n"
        f"## Related\n"
        f"See adjacent topics in the knowledge base.\n"
    )
    return body


def _paired_body(topic: str, doc_index: int, graph: KnowledgeGraph) -> str:
    """Body for a document that participates in a contradiction pair."""
    pair = graph.in_contradiction_pair(doc_index)
    assert pair is not None
    a, b = pair
    assert doc_index in (a, b)
    base = _standard_body(topic, doc_index)
    block = _postgres_block() if doc_index == a else _mongo_block()
    insert_at = base.find("## Related")
    if insert_at == -1:
        return base + "\n" + block
    return base[:insert_at] + block + "\n" + base[insert_at:]


def sample_documents(graph: KnowledgeGraph, n_docs: int, rng: random.Random) -> list[DocSpec]:
    """Produce *n_docs* document specifications with deterministic structure."""
    specs: list[DocSpec] = []
    for i in range(n_docs):
        topic = graph.concept_for_doc(i)
        slug = _slug(topic)
        rel_path = f"topics/{i:03d}-{slug}.md"

        pair = graph.in_contradiction_pair(i)
        body = _paired_body(topic, i, graph) if pair is not None else _standard_body(topic, i)

        specs.append(DocSpec(index=i, rel_path=rel_path, title=topic.title(), body=body))
    return specs


def build_ground_truth(
    graph: KnowledgeGraph,
    specs: list[DocSpec],
    qa_per_doc: int = 2,
) -> tuple[list[QAPair], list[FidelityClaim], list[ContradictionPair]]:
    """Derive QA, fidelity, and contradiction ground truth from written paths."""
    qa_pairs: list[QAPair] = []
    fidelity: list[FidelityClaim] = []
    contradictions: list[ContradictionPair] = []

    q_counter = 0
    for spec in specs:
        topic = graph.concept_for_doc(spec.index)
        path = spec.rel_path
        doc_id = path

        # --- QA (deterministic, answer strings appear in body) ---
        slo_q = f"What availability SLO is stated for {topic} in this document?"
        slo_a = "99.9%"
        qa_pairs.append(
            QAPair(
                id=f"qa-{spec.index + 1:03d}",
                query_id=f"q-{q_counter + 1:03d}",
                document_ids=[doc_id],
                question=slo_q,
                answer=slo_a,
                difficulty="easy",
            )
        )
        q_counter += 1

        if qa_per_doc >= 2:
            rb_q = f"In which section is the runbook reference for {topic}?"
            rb_a = "Details"
            qa_pairs.append(
                QAPair(
                    id=f"qa-{spec.index + 1:03d}-b",
                    query_id=f"q-{q_counter + 1:03d}",
                    document_ids=[doc_id],
                    question=rb_q,
                    answer=rb_a,
                    difficulty="easy",
                )
            )
            q_counter += 1

        # --- Fidelity: alternate supported / not_supported ---
        if spec.index % 2 == 0:
            fidelity.append(
                FidelityClaim(
                    id=f"fid-{spec.index + 1:03d}",
                    document_id=doc_id,
                    claim=f"The document states a {99.9}% availability SLO for {topic}.",
                    verdict="supported",
                    evidence="Metrics section",
                )
            )
        else:
            fidelity.append(
                FidelityClaim(
                    id=f"fid-{spec.index + 1:03d}",
                    document_id=doc_id,
                    claim=f"The team has fully deprecated work on {topic} with no replacement.",
                    verdict="not_supported",
                    evidence="Fabricated for evaluation",
                )
            )

    # --- Contradictions between paired docs ---
    for ci, (a, b) in enumerate(graph.contradiction_pair_indices):
        pa = specs[a].rel_path
        pb = specs[b].rel_path
        contradictions.append(
            ContradictionPair(
                id=f"contr-{ci + 1:03d}",
                doc_id_a=pa,
                doc_id_b=pb,
                description=(
                    "Conflicting statements about whether PostgreSQL is the OLTP database."
                ),
            )
        )

    return qa_pairs, fidelity, contradictions
