"""Corpus loader — reads a manifest.yaml directory into a Corpus object."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from wikibench.models.corpus import (
    Corpus,
    ContradictionPair,
    FidelityClaim,
    GroundTruth,
    QAPair,
)
from wikibench.models.document import Document

log = logging.getLogger(__name__)


# ── Public API ────────────────────────────────────────────────────────────────

def load_corpus(path: str | Path) -> Corpus:
    """Load a WikiBench corpus from a directory containing ``manifest.yaml``.

    Directory layout expected::

        <path>/
        ├── manifest.yaml
        ├── docs/
        │   └── **/*.md
        └── ground_truth/
            ├── qa_pairs.jsonl          (optional)
            ├── fidelity_claims.jsonl   (optional)
            └── contradictions.jsonl   (optional)

    Args:
        path: Path to the corpus root directory.

    Returns:
        A fully populated :class:`~wikibench.models.corpus.Corpus`.

    Raises:
        FileNotFoundError: If ``path`` or ``manifest.yaml`` does not exist.
        ValueError: If ``manifest.yaml`` fails schema validation.
    """
    root = Path(path).resolve()
    _require_dir(root)

    from wikibench.corpora.manifest import load_manifest

    manifest_path = root / "manifest.yaml"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.yaml not found in {root}")

    metadata = load_manifest(manifest_path)
    log.debug("Loaded manifest for corpus %s", metadata.id)

    documents = _load_documents(root / "docs")
    ground_truth = _load_ground_truth(root / "ground_truth")

    log.info(
        "Corpus %s loaded: %d docs, %d QA, %d claims, %d contradictions",
        metadata.id,
        len(documents),
        len(ground_truth.qa_pairs),
        len(ground_truth.fidelity_claims),
        len(ground_truth.contradictions),
    )
    return Corpus(metadata=metadata, documents=documents, ground_truth=ground_truth)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _require_dir(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Corpus directory not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Expected a directory, got: {path}")


def _load_documents(docs_dir: Path) -> list[Document]:
    """Recursively load all .md files under ``docs_dir``."""
    if not docs_dir.exists():
        log.warning("docs/ directory not found in corpus at %s", docs_dir.parent)
        return []

    documents: list[Document] = []
    for md_file in sorted(docs_dir.rglob("*.md")):
        rel_path = md_file.relative_to(docs_dir).as_posix()
        content = md_file.read_text(encoding="utf-8")
        doc_id = rel_path.replace("/", "__").removesuffix(".md")
        documents.append(
            Document(
                id=doc_id,
                path=rel_path,
                content=content,
                modality=_infer_modality(rel_path),
            )
        )
    return documents


def _infer_modality(rel_path: str) -> str:
    """Infer document modality from directory name conventions."""
    parts = rel_path.lower().split("/")
    if any(p in ("meetings", "transcripts") for p in parts):
        return "transcript"
    if any(p in ("forum", "discussions") for p in parts):
        return "forum_thread"
    return "markdown"


def _load_ground_truth(gt_dir: Path) -> GroundTruth:
    """Load all ground-truth JSONL files from ``gt_dir``."""
    if not gt_dir.exists():
        log.warning("ground_truth/ directory not found in corpus at %s", gt_dir.parent)
        return GroundTruth()

    qa_pairs = _load_jsonl(gt_dir / "qa_pairs.jsonl", QAPair)
    fidelity_claims = _load_jsonl(gt_dir / "fidelity_claims.jsonl", FidelityClaim)
    contradictions = _load_jsonl(gt_dir / "contradictions.jsonl", ContradictionPair)

    return GroundTruth(
        qa_pairs=qa_pairs,
        fidelity_claims=fidelity_claims,
        contradictions=contradictions,
    )


def _load_jsonl(path: Path, model: type) -> list:  # type: ignore[type-arg]
    """Parse a JSONL file into a list of pydantic model instances."""
    if not path.exists():
        return []
    items = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                raw = json.loads(line)
                items.append(model(**raw))
            except (json.JSONDecodeError, Exception) as exc:
                log.warning("Skipping line %d in %s: %s", lineno, path.name, exc)
    return items
