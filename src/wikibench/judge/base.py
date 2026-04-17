"""LLM-as-judge base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class JudgeVerdict:
    """Result of a single judge evaluation."""

    score: float
    """Normalised score in [0, 1]."""
    reasoning: str
    """One-sentence explanation of the verdict."""
    raw: str = ""
    """Raw LLM output for debugging."""


class BaseJudge(ABC):
    """Evaluate free-text adapter responses against a reference answer."""

    @abstractmethod
    def judge_qa(
        self,
        question: str,
        reference_answer: str,
        adapter_answer: str,
    ) -> JudgeVerdict:
        """Score a QA answer; return a JudgeVerdict with score in [0, 1]."""
