"""T3 — Contradiction Detection task.

Measures whether the adapter can identify deliberate contradictions between
documents that were pre-embedded in the corpus.

Protocol
--------
One Query with intent="contradiction_check" is sent per ContradictionPair.
The adapter's ``structured["has_contradiction"]`` bool is compared to
ground truth (always True for items in the contradictions list).

Scoring per item
----------------
* 1.0  — adapter correctly flagged the contradiction (True Positive)
* 0.0  — adapter missed it (False Negative)

Aggregate metrics
-----------------
* ``recall``        — TP / (TP + FN);  most important — missing contradictions is costly
* ``precision``     — TP / (TP + FP);  requires negative samples (future corpus versions)
* ``f1``            — harmonic mean of precision and recall
* ``mean``          — same as recall when corpus has only positive samples
"""

from __future__ import annotations

import logging
from typing import Any

from wikibench.models.corpus import Corpus, ContradictionPair
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score, TaskResult
from wikibench.tasks import Task, register_task

log = logging.getLogger(__name__)


@register_task
class ContradictionDetectionTask(Task):
    """T3: evaluate whether the adapter detects inter-document contradictions."""

    id = "contradiction_detection"
    version = "1.0.0"

    def __init__(self) -> None:
        self._pair_index: dict[str, ContradictionPair] = {}

    # ── prepare ───────────────────────────────────────────────────────────────

    def prepare(self, corpus: Corpus) -> list[Query]:
        """One contradiction_check query per ContradictionPair."""
        self._pair_index = {}
        queries: list[Query] = []

        for pair in corpus.ground_truth.contradictions:
            q = Query(
                id=pair.id,
                text=(
                    f"Do documents '{pair.doc_id_a}' and '{pair.doc_id_b}' "
                    "contradict each other?"
                ),
                intent="contradiction_check",
                params={
                    "doc_id_a": pair.doc_id_a,
                    "doc_id_b": pair.doc_id_b,
                    "description": pair.description,
                },
            )
            self._pair_index[pair.id] = pair
            queries.append(q)

        log.info("T3 prepared %d contradiction queries from corpus %s", len(queries), corpus.id)
        return queries

    # ── score ─────────────────────────────────────────────────────────────────

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        """Score: 1.0 if the adapter correctly flagged the contradiction."""
        pair = self._pair_index.get(query.id)
        if pair is None:
            log.warning("T3.score: query %r not in index; returning 0", query.id)
            return Score(
                metric="contradiction_detection",
                value=0.0,
                details={"error": "pair not found in index"},
            )

        # Ground truth: every item in contradictions list IS a contradiction
        ground_truth_positive = True

        raw_flag = response.structured.get("has_contradiction")
        if isinstance(raw_flag, str):
            adapter_flag = raw_flag.lower() in ("true", "yes", "1")
        elif isinstance(raw_flag, bool):
            adapter_flag = raw_flag
        else:
            # No structured response — try to infer from free text
            answer_lower = response.answer.lower()
            adapter_flag = any(
                kw in answer_lower
                for kw in ("contradict", "conflict", "inconsistent", "disagree")
            )
            log.debug("T3: no structured response for %r; inferred flag=%s", query.id, adapter_flag)

        correct = adapter_flag == ground_truth_positive

        return Score(
            metric="contradiction_detection",
            value=1.0 if correct else 0.0,
            details={
                "pair_id": pair.id,
                "doc_id_a": pair.doc_id_a,
                "doc_id_b": pair.doc_id_b,
                "ground_truth": ground_truth_positive,
                "adapter_flag": adapter_flag,
                "correct": correct,
            },
        )

    # ── aggregate ─────────────────────────────────────────────────────────────

    def aggregate(self, scores: list[Score]) -> TaskResult:
        if not scores:
            return TaskResult(task_id=self.id, task_version=self.version, scores=[])

        # All ground truth items are positives; precision requires negatives
        tp = sum(1 for s in scores if s.details.get("correct") and s.details.get("ground_truth"))
        fn = sum(1 for s in scores if not s.details.get("correct") and s.details.get("ground_truth"))
        # fp / tn from negative samples (future corpus versions)
        fp = 0
        tn = 0

        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0  # no FP → perfect precision
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        mean = sum(s.value for s in scores) / len(scores)

        slices: dict[str, Any] = {
            "mean": mean,
            "recall": recall,
            "precision": precision,
            "f1": f1,
            "tp": tp,
            "fn": fn,
        }

        return TaskResult(
            task_id=self.id,
            task_version=self.version,
            scores=scores,
            slices=slices,
        )
