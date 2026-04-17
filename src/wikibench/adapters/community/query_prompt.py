"""Build natural-language prompts for subprocess / LLM query adapters."""

from __future__ import annotations

from wikibench.models.query import Query

# Mirrors ``naive._SYSTEM_PROMPT`` (keep in sync).
KB_SYSTEM_PROMPT = """\
You are a knowledge-base assistant.
Answer questions using ONLY the information in the knowledge base below.
If the answer cannot be found in the knowledge base, say so explicitly.
Do not invent facts.
"""

# Mirrors ``naive._INTENT_INSTRUCTIONS`` user-facing text (keep in sync).
_INTENT_INSTRUCTIONS: dict[str, str] = {
    "fidelity_check": (
        "Evaluate the following claim against the knowledge base.\n"
        "Reply with ONLY valid JSON (no markdown fences):\n"
        '{"verdict": "supported|not_supported|unknown", "explanation": "<one sentence>"}'
    ),
    "contradiction_check": (
        "Identify any factual contradictions BETWEEN documents in the knowledge base.\n"
        "Reply with ONLY valid JSON (no markdown fences):\n"
        '{"has_contradiction": true|false, "pairs": [{"doc_a": "<path>", "doc_b": "<path>", "description": "<brief>"}]}'
    ),
    "grounding": (
        "Answer the question and cite the specific document paths that support your answer.\n"
        "Reply with ONLY valid JSON (no markdown fences):\n"
        '{"answer": "<your answer>", "sources": ["<doc-path>", ...]}'
    ),
}


def build_user_query_text(query: Query) -> str:
    """Single user message body (same semantics as :func:`naive._build_messages`)."""
    intent_instruction = _INTENT_INSTRUCTIONS.get(query.intent, "")
    if query.intent == "fidelity_check":
        claim = query.params.get("claim", query.text)
        return f"{intent_instruction}\n\nClaim to evaluate:\n{claim}"
    if query.intent == "contradiction_check":
        return intent_instruction
    if query.intent == "grounding":
        return f"{intent_instruction}\n\nQuestion:\n{query.text}"
    return query.text
