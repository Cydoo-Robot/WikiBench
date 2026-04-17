"""Base domain template (Phase 1 Week 5)."""

from __future__ import annotations

from abc import ABC, abstractmethod


class DomainTemplate(ABC):
    id: str
    description: str

    @abstractmethod
    def seed_concepts(self) -> list[str]:
        """Return the initial concept seeds for the knowledge graph."""
