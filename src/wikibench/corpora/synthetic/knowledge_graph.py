"""Lightweight knowledge graph for synthetic corpus generation.

The graph is intentionally simple: a set of domain *concepts* plus optional
pairing metadata used to embed deliberate contradictions between documents.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from wikibench.corpora.synthetic.domains._base import DomainTemplate


@dataclass
class KnowledgeGraph:
    """Concept nodes for a single synthetic corpus run."""

    domain_id: str
    concepts: list[str]
    """Ordered seed concepts (cycled when emitting more docs than concepts)."""
    contradiction_pair_indices: list[tuple[int, int]] = field(default_factory=list)
    """Pairs of document indices that will contain mutually exclusive facts."""

    @classmethod
    def build(cls, domain: DomainTemplate, n_docs: int) -> KnowledgeGraph:
        """Build a graph for *n_docs* documents.

        Contradiction pairs are (0,1), (2,3), … while both indices are < *n_docs*.
        """
        concepts = list(domain.seed_concepts())
        if not concepts:
            raise ValueError(f"Domain {domain.id!r} returned no seed concepts")

        pairs: list[tuple[int, int]] = []
        i = 0
        while i + 1 < n_docs:
            pairs.append((i, i + 1))
            i += 2

        return cls(
            domain_id=domain.id,
            concepts=concepts,
            contradiction_pair_indices=pairs,
        )

    def concept_for_doc(self, doc_index: int) -> str:
        return self.concepts[doc_index % len(self.concepts)]

    def in_contradiction_pair(self, doc_index: int) -> tuple[int, int] | None:
        """Return the (a,b) pair containing *doc_index*, or ``None``."""
        for a, b in self.contradiction_pair_indices:
            if doc_index in (a, b):
                return (a, b)
        return None
