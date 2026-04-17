"""Corpus, CorpusMetadata, and GroundTruth models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from wikibench.models.document import Document


class CorpusMetadata(BaseModel):
    """Top-level metadata declared in ``manifest.yaml``."""

    id: str
    """Unique corpus identifier, e.g. ``synthetic-tiny@0.1.0``."""
    version: str
    description: str = ""
    tier: str
    """One of: synthetic | small | medium | large."""
    domain: str = ""
    language: str = "en"
    doc_count: int
    created_at: str = ""
    wikibench_min_version: str = "0.1.0"
    extra: dict[str, Any] = Field(default_factory=dict)


class QAPair(BaseModel):
    id: str
    query_id: str
    document_ids: list[str]
    """Documents that contain the answer."""
    question: str
    answer: str
    difficulty: str = "medium"


class FidelityClaim(BaseModel):
    id: str
    document_id: str
    claim: str
    verdict: str
    """'supported' | 'not_supported' | 'unknown'"""
    evidence: str = ""


class ContradictionPair(BaseModel):
    id: str
    doc_id_a: str
    doc_id_b: str
    description: str
    """Human-readable description of the contradiction."""


class GroundTruth(BaseModel):
    qa_pairs: list[QAPair] = Field(default_factory=list)
    fidelity_claims: list[FidelityClaim] = Field(default_factory=list)
    contradictions: list[ContradictionPair] = Field(default_factory=list)


class Corpus(BaseModel):
    """A fully loaded WikiBench corpus ready for evaluation."""

    metadata: CorpusMetadata
    documents: list[Document]
    ground_truth: GroundTruth

    @property
    def id(self) -> str:
        return self.metadata.id
