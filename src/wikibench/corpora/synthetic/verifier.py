"""Post-generation verification of a synthetic corpus directory."""

from __future__ import annotations

from pathlib import Path

from wikibench.corpora.loader import load_corpus
from wikibench.corpora.manifest import VerifyResult, verify_corpus_dir


def verify_generated_corpus(corpus_root: str | Path) -> VerifyResult:
    """Run manifest checks and ensure the corpus loads end-to-end."""
    root = Path(corpus_root)
    result = verify_corpus_dir(root)
    if not result.ok:
        return result

    try:
        corpus = load_corpus(root)
    except Exception as exc:
        return VerifyResult(ok=False, errors=[f"load_corpus failed: {exc}"], warnings=result.warnings)

    extra_warnings = list(result.warnings)
    n = len(corpus.documents)
    if corpus.metadata.doc_count != n:
        extra_warnings.append(
            f"manifest doc_count={corpus.metadata.doc_count} but loaded {n} documents"
        )
    if not corpus.ground_truth.qa_pairs:
        extra_warnings.append("ground_truth has no qa_pairs")
    return VerifyResult(ok=True, errors=[], warnings=extra_warnings)
