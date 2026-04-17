"""T1 — Retrieval Accuracy task.

Measures whether the adapter can retrieve the correct answer to factual
questions derived from corpus ground truth (QA pairs).

Scoring
-------
Each QA pair becomes one Query with intent="qa".  The adapter's free-text
answer is evaluated by an LLM judge (DefaultJudge) against the reference
answer.  Score is in [0, 1].

Aggregate metrics
-----------------
* ``mean``            — arithmetic mean across all QA pairs
* ``easy_mean``       — mean for difficulty="easy"
* ``medium_mean``     — mean for difficulty="medium"
* ``hard_mean``       — mean for difficulty="hard"
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from wikibench.judge.default import DefaultJudge
from wikibench.models.corpus import Corpus, QAPair
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score, TaskResult
from wikibench.tasks import Task, register_task

log = logging.getLogger(__name__)

_JUDGE_MODEL = "gemini/gemini-2.5-flash"


@register_task
class RetrievalAccuracyTask(Task):
    """T1: evaluate whether the adapter retrieves factually correct answers."""

    id = "retrieval_accuracy"
    version = "1.0.0"

    def __init__(self, judge_model: str = _JUDGE_MODEL) -> None:
        self._judge = DefaultJudge(model=judge_model)
        # populated by prepare(); used by score() to look up QA metadata
        self._qa_index: dict[str, QAPair] = {}

    # ── prepare ───────────────────────────────────────────────────────────────

    def prepare(self, corpus: Corpus) -> list[Query]:
        """Convert every QA pair in ground truth into a qa-intent Query."""
        self._qa_index = {}
        queries: list[Query] = []

        for qa in corpus.ground_truth.qa_pairs:
            q = Query(
                id=qa.query_id,
                text=qa.question,
                intent="qa",
                params={"difficulty": qa.difficulty, "qa_id": qa.id},
            )
            self._qa_index[qa.query_id] = qa
            queries.append(q)

        log.info("T1 prepared %d QA queries from corpus %s", len(queries), corpus.id)
        return queries

    # ── score ─────────────────────────────────────────────────────────────────

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        """Use the LLM judge to score one adapter answer."""
        qa = self._qa_index.get(query.id)
        if qa is None:
            log.warning("T1.score: query %r not in index; returning 0", query.id)
            return Score(
                metric="retrieval_accuracy",
                value=0.0,
                details={"error": "query not found in index"},
            )

        verdict = self._judge.judge_qa(
            question=query.text,
            reference_answer=qa.answer,
            adapter_answer=response.answer,
        )

        return Score(
            metric="retrieval_accuracy",
            value=verdict.score,
            details={
                "qa_id": qa.id,
                "difficulty": qa.difficulty,
                "reasoning": verdict.reasoning,
                "reference": qa.answer,
            },
        )

    # ── aggregate ─────────────────────────────────────────────────────────────

    def aggregate(self, scores: list[Score]) -> TaskResult:
        if not scores:
            return TaskResult(task_id=self.id, task_version=self.version, scores=[])

        overall = sum(s.value for s in scores) / len(scores)

        # Per-difficulty slices
        buckets: dict[str, list[float]] = defaultdict(list)
        for s in scores:
            diff = s.details.get("difficulty", "unknown")
            buckets[diff].append(s.value)

        slices: dict[str, Any] = {"mean": overall}
        for diff, vals in buckets.items():
            slices[f"{diff}_mean"] = sum(vals) / len(vals)
            slices[f"{diff}_count"] = len(vals)

        return TaskResult(
            task_id=self.id,
            task_version=self.version,
            scores=scores,
            slices=slices,
        )
