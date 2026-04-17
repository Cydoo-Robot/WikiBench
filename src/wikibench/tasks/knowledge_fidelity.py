"""T2 — Knowledge Fidelity task.

Measures whether the adapter correctly classifies factual claims as
"supported", "not_supported", or "unknown" relative to the knowledge base.

No LLM judge is needed — the adapter's ``structured["verdict"]`` is compared
directly to the ground-truth verdict.  This makes T2 cheap and deterministic.

Scoring
-------
Each FidelityClaim becomes one Query with intent="fidelity_check".
Score per item: 1.0 if verdict matches, 0.0 otherwise.

Aggregate metrics
-----------------
* ``mean``                  — overall accuracy
* ``precision``             — TP / (TP + FP) for "supported" class
* ``recall``                — TP / (TP + FN) for "supported" class
* ``hallucination_rate``    — fraction of "not_supported" claims the adapter
                              incorrectly marked "supported"
* per-verdict confusion matrix slices
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from wikibench.models.corpus import Corpus, FidelityClaim
from wikibench.models.query import Query, QueryResponse
from wikibench.models.result import Score, TaskResult
from wikibench.tasks import Task, register_task

log = logging.getLogger(__name__)

_VALID_VERDICTS = {"supported", "not_supported", "unknown"}


@register_task
class KnowledgeFidelityTask(Task):
    """T2: evaluate whether the adapter correctly judges factual claims."""

    id = "knowledge_fidelity"
    version = "1.0.0"

    def __init__(self) -> None:
        self._claim_index: dict[str, FidelityClaim] = {}

    # ── prepare ───────────────────────────────────────────────────────────────

    def prepare(self, corpus: Corpus) -> list[Query]:
        """Convert every FidelityClaim into a fidelity_check Query."""
        self._claim_index = {}
        queries: list[Query] = []

        for claim in corpus.ground_truth.fidelity_claims:
            q = Query(
                id=claim.id,
                text=f"Evaluate this claim: {claim.claim}",
                intent="fidelity_check",
                params={
                    "claim": claim.claim,
                    "decision_space": list(_VALID_VERDICTS),
                    "document_id": claim.document_id,
                },
            )
            self._claim_index[claim.id] = claim
            queries.append(q)

        log.info("T2 prepared %d fidelity queries from corpus %s", len(queries), corpus.id)
        return queries

    # ── score ─────────────────────────────────────────────────────────────────

    def score(self, query: Query, response: QueryResponse, corpus: Corpus) -> Score:
        """Compare adapter verdict to ground truth — no LLM call needed."""
        claim = self._claim_index.get(query.id)
        if claim is None:
            log.warning("T2.score: query %r not in index; returning 0", query.id)
            return Score(
                metric="knowledge_fidelity",
                value=0.0,
                details={"error": "claim not found in index"},
            )

        # Extract verdict from structured response
        adapter_verdict = str(
            response.structured.get("verdict", "")
        ).lower().strip()

        # Normalise common variants
        _ALIASES = {
            "not supported": "not_supported",
            "unsupported": "not_supported",
            "false": "not_supported",
            "true": "supported",
            "yes": "supported",
            "no": "not_supported",
        }
        adapter_verdict = _ALIASES.get(adapter_verdict, adapter_verdict)

        if adapter_verdict not in _VALID_VERDICTS:
            log.debug(
                "T2: adapter returned unrecognised verdict %r for claim %s",
                adapter_verdict,
                claim.id,
            )
            adapter_verdict = "unknown"

        match = int(adapter_verdict == claim.verdict)

        return Score(
            metric="knowledge_fidelity",
            value=float(match),
            details={
                "claim_id": claim.id,
                "reference_verdict": claim.verdict,
                "adapter_verdict": adapter_verdict,
                "correct": bool(match),
                "document_id": claim.document_id,
            },
        )

    # ── aggregate ─────────────────────────────────────────────────────────────

    def aggregate(self, scores: list[Score]) -> TaskResult:
        if not scores:
            return TaskResult(task_id=self.id, task_version=self.version, scores=[])

        overall = sum(s.value for s in scores) / len(scores)

        # Build confusion matrix for "supported" class
        tp = fp = fn = tn = 0
        hallucination_count = 0
        total_not_supported = 0

        for s in scores:
            ref = s.details.get("reference_verdict", "")
            ada = s.details.get("adapter_verdict", "")
            if ref == "supported":
                if ada == "supported":
                    tp += 1
                else:
                    fn += 1
            elif ref == "not_supported":
                total_not_supported += 1
                if ada == "supported":
                    fp += 1
                    hallucination_count += 1
                else:
                    tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        hallucination_rate = hallucination_count / total_not_supported if total_not_supported > 0 else 0.0

        slices: dict[str, Any] = {
            "mean": overall,
            "precision": precision,
            "recall": recall,
            "hallucination_rate": hallucination_rate,
            "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        }

        return TaskResult(
            task_id=self.id,
            task_version=self.version,
            scores=scores,
            slices=slices,
        )
