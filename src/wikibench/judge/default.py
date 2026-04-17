"""Default LLM-as-judge using Gemini Flash (or any model via llm_call).

The judge evaluates adapter answers against ground-truth reference answers.
It uses a structured prompt that returns a JSON verdict so parsing is robust.

Scoring rubric (QA):
    1.0  — Fully correct; key facts present, no hallucination
    0.75 — Mostly correct; minor omission or slight imprecision
    0.5  — Partially correct; main point captured but significant gaps
    0.25 — Mostly wrong; correct direction but key facts missing/wrong
    0.0  — Incorrect or contradicts the reference answer
"""

from __future__ import annotations

import json
import logging

from wikibench.judge.base import BaseJudge, JudgeVerdict
from wikibench.runtime.llm import llm_call

log = logging.getLogger(__name__)

_DEFAULT_MODEL = "gemini/gemini-2.5-flash"

_QA_JUDGE_PROMPT = """\
You are an impartial grader evaluating an AI assistant's answer to a question.

Question:
{question}

Reference answer (ground truth):
{reference}

Assistant's answer:
{answer}

Grade the assistant's answer on a scale of 0.0 to 1.0 using this rubric:
  1.0  = Fully correct; all key facts present, no hallucination
  0.75 = Mostly correct; minor omission or slight imprecision
  0.5  = Partially correct; main point captured but significant gaps
  0.25 = Mostly wrong; right direction but key facts missing or wrong
  0.0  = Incorrect or contradicts the reference answer

Reply with ONLY valid JSON (no markdown fences):
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}"""


class DefaultJudge(BaseJudge):
    """LLM-as-judge backed by ``llm_call``."""

    def __init__(self, model: str = _DEFAULT_MODEL) -> None:
        self.model = model

    def judge_qa(
        self,
        question: str,
        reference_answer: str,
        adapter_answer: str,
    ) -> JudgeVerdict:
        prompt = _QA_JUDGE_PROMPT.format(
            question=question,
            reference=reference_answer,
            answer=adapter_answer,
        )

        # Gemini 2.5-flash thinking disabled for deterministic judging
        extra: dict = {}
        if "gemini-2.5" in self.model or "gemini-3" in self.model:
            extra["thinking"] = {"type": "disabled"}

        raw = llm_call(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            purpose="task.judge",
            temperature=0.0,
            max_tokens=256,
            **extra,
        )

        return _parse_verdict(raw)


def _parse_verdict(raw: str) -> JudgeVerdict:
    """Parse the judge's JSON response into a JudgeVerdict."""
    text = raw.strip()

    # Strip markdown fences
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:]).strip()

    try:
        data = json.loads(text)
        score = float(data.get("score", 0.0))
        score = max(0.0, min(1.0, score))
        reasoning = str(data.get("reasoning", ""))
        return JudgeVerdict(score=score, reasoning=reasoning, raw=raw)
    except (json.JSONDecodeError, KeyError, TypeError):
        log.warning("Judge returned unparseable response: %r", raw[:200])
        # Fallback: try to extract a score from plain text
        for token in text.split():
            try:
                val = float(token.strip(".,;:"))
                if 0.0 <= val <= 1.0:
                    return JudgeVerdict(score=val, reasoning="parsed from plain text", raw=raw)
            except ValueError:
                continue
        return JudgeVerdict(score=0.0, reasoning="judge response unparseable", raw=raw)
