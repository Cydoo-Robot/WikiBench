"""Adapter registry — discovers adapters via entry_points."""

from __future__ import annotations

from importlib.metadata import entry_points
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wikibench.adapters._base import WikiAdapter

_ENTRY_POINT_GROUP = "wikibench.adapters"


def list_adapters() -> dict[str, type[WikiAdapter]]:
    """Return all registered adapters keyed by name."""
    eps = entry_points(group=_ENTRY_POINT_GROUP)
    return {ep.name: ep.load() for ep in eps}


def get_adapter(name: str) -> type[WikiAdapter]:
    """Load a single adapter class by name, or raise ``KeyError``."""
    eps = entry_points(group=_ENTRY_POINT_GROUP)
    for ep in eps:
        if ep.name == name:
            return ep.load()  # type: ignore[return-value]
    raise KeyError(f"No adapter registered under name '{name}'.")
