"""Document model — core unit passed to every WikiAdapter."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Modality = Literal[
    "markdown",
    "transcript",
    "chat",
    "email",
    "code_comment",
    "forum_thread",
    "other",
]
"""Semantic origin of a document's content.

All documents are stored and transmitted as Markdown text regardless of
modality.  Adapters may use ``modality`` to adjust their prompting strategy.
"""


class Document(BaseModel):
    """A single knowledge unit in a WikiBench corpus.

    Regardless of its original format (forum thread, meeting transcript, etc.)
    the ``content`` field always contains rendered Markdown text.
    """

    id: str
    path: str
    """Virtual path preserving directory-structure semantics; always ends in .md."""
    content: str
    """Markdown text — the only format adapters ever receive."""
    modality: Modality = "markdown"
    timestamp: datetime | None = None
    """Original creation time, used for staleness metrics."""
    metadata: dict[str, str] = Field(default_factory=dict)


class ForumThread(BaseModel):
    """Intermediate representation produced by crawlers before rendering to Markdown.

    ``ForumRenderer`` converts a ``ForumThread`` into a ``Document``.
    """

    id: str
    platform: Literal["hackernews", "stackoverflow", "reddit", "v2ex", "other"]
    title: str
    url: str
    body: str
    """Original post body (raw text / HTML)."""
    comments: list[ForumComment] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    score: int = 0
    timestamp: datetime | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class ForumComment(BaseModel):
    id: str
    author: str
    body: str
    score: int = 0
    timestamp: datetime | None = None
    parent_id: str | None = None
