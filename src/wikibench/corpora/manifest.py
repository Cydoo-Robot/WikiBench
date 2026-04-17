"""manifest.yaml schema validation and corpus integrity checks."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from wikibench.models.corpus import CorpusMetadata

log = logging.getLogger(__name__)


# ── Loading ───────────────────────────────────────────────────────────────────

def load_manifest(manifest_path: str | Path) -> CorpusMetadata:
    """Parse and validate a corpus ``manifest.yaml`` file.

    Args:
        manifest_path: Path to the ``manifest.yaml`` file.

    Returns:
        A validated :class:`~wikibench.models.corpus.CorpusMetadata` instance.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If YAML is malformed or schema validation fails.
    """
    p = Path(manifest_path)
    if not p.exists():
        raise FileNotFoundError(f"manifest.yaml not found: {p}")

    with open(p, encoding="utf-8") as fh:
        try:
            raw: dict[str, Any] = yaml.safe_load(fh) or {}
        except yaml.YAMLError as exc:
            raise ValueError(f"Malformed YAML in {p}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"manifest.yaml must be a YAML mapping, got {type(raw).__name__}")

    try:
        return CorpusMetadata(**raw)
    except ValidationError as exc:
        raise ValueError(f"Invalid manifest at {p}:\n{exc}") from exc


# ── Integrity verification ────────────────────────────────────────────────────

@dataclass
class VerifyResult:
    """Result of a corpus integrity check."""

    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        lines = ["PASS" if self.ok else "FAIL"]
        for e in self.errors:
            lines.append(f"  ERROR   {e}")
        for w in self.warnings:
            lines.append(f"  WARNING {w}")
        return "\n".join(lines)


def verify_corpus_dir(corpus_root: str | Path) -> VerifyResult:
    """Verify a corpus directory against the manifest schema and internal consistency.

    Checks performed:
    - ``manifest.yaml`` exists and is valid
    - ``docs/`` directory exists and contains at least one ``.md`` file
    - ``doc_count`` in manifest matches actual number of ``.md`` files
    - ``ground_truth/`` directory exists (warning if absent)
    - Each ground-truth file is valid JSONL

    Args:
        corpus_root: Path to the corpus root directory.

    Returns:
        A :class:`VerifyResult` with ``ok=True`` when all checks pass.
    """
    root = Path(corpus_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    # ── manifest ──────────────────────────────────────────────────────────────
    manifest_path = root / "manifest.yaml"
    if not manifest_path.exists():
        errors.append("manifest.yaml is missing")
        return VerifyResult(ok=False, errors=errors, warnings=warnings)

    try:
        meta = load_manifest(manifest_path)
    except (ValueError, FileNotFoundError) as exc:
        errors.append(str(exc))
        return VerifyResult(ok=False, errors=errors, warnings=warnings)

    # ── docs/ ─────────────────────────────────────────────────────────────────
    docs_dir = root / "docs"
    if not docs_dir.exists():
        errors.append("docs/ directory is missing")
    else:
        md_files = list(docs_dir.rglob("*.md"))
        if not md_files:
            errors.append("docs/ directory contains no .md files")
        else:
            actual = len(md_files)
            declared = meta.doc_count
            if actual != declared:
                warnings.append(
                    f"manifest declares doc_count={declared} but found {actual} .md files"
                )

    # ── ground_truth/ ─────────────────────────────────────────────────────────
    gt_dir = root / "ground_truth"
    if not gt_dir.exists():
        warnings.append("ground_truth/ directory is missing (corpus cannot be scored)")
    else:
        for fname in ("qa_pairs.jsonl", "fidelity_claims.jsonl", "contradictions.jsonl"):
            fpath = gt_dir / fname
            if not fpath.exists():
                warnings.append(f"ground_truth/{fname} is missing")
            else:
                jsonl_errors = _validate_jsonl(fpath)
                errors.extend(jsonl_errors)

    ok = len(errors) == 0
    return VerifyResult(ok=ok, errors=errors, warnings=warnings)


def _validate_jsonl(path: Path) -> list[str]:
    """Return a list of parse errors found in a JSONL file."""
    import json

    errs: list[str] = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                errs.append(f"{path.name}:{lineno}: {exc}")
    return errs
