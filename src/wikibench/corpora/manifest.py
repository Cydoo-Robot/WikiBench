"""manifest.yaml schema validation (Phase 1 Week 1)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from wikibench.models.corpus import CorpusMetadata


def load_manifest(manifest_path: str | Path) -> CorpusMetadata:
    """Parse and validate a corpus ``manifest.yaml`` file."""
    with open(manifest_path, encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh)
    try:
        return CorpusMetadata(**raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid manifest at {manifest_path}:\n{exc}") from exc
