"""Shared pytest fixtures for WikiBench test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
TINY_CORPUS_PATH = REPO_ROOT / "corpora" / "synthetic" / "tiny"


@pytest.fixture(scope="session")
def tiny_corpus_path() -> Path:
    """Return the path to the hand-crafted synthetic-tiny corpus."""
    assert TINY_CORPUS_PATH.exists(), f"tiny corpus not found at {TINY_CORPUS_PATH}"
    return TINY_CORPUS_PATH


@pytest.fixture(scope="session")
def sample_documents() -> list:
    """Return a minimal list of Document instances for adapter smoke tests."""
    from wikibench.models.document import Document

    return [
        Document(
            id="doc-001",
            path="architecture/overview.md",
            content="# Overview\n\nThis is a test document about system architecture.",
            modality="markdown",
        ),
        Document(
            id="doc-002",
            path="decisions/2026-01-db-choice.md",
            content="# DB Choice\n\nWe chose PostgreSQL over MongoDB.",
            modality="markdown",
        ),
    ]
