"""Integration tests for corpus loader and manifest validator."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from wikibench.corpora.loader import load_corpus
from wikibench.corpora.manifest import load_manifest, verify_corpus_dir
from wikibench.models.corpus import Corpus

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def tiny_corpus(tiny_corpus_path: Path) -> Corpus:
    return load_corpus(tiny_corpus_path)


# ── load_corpus: happy path ───────────────────────────────────────────────────


class TestLoadCorpus:
    def test_returns_corpus_instance(self, tiny_corpus: Corpus) -> None:
        assert isinstance(tiny_corpus, Corpus)

    def test_corpus_id(self, tiny_corpus: Corpus) -> None:
        assert tiny_corpus.id == "synthetic-tiny@0.1.0"

    def test_documents_loaded(self, tiny_corpus: Corpus) -> None:
        assert len(tiny_corpus.documents) == 5

    def test_document_content_nonempty(self, tiny_corpus: Corpus) -> None:
        for doc in tiny_corpus.documents:
            assert doc.content.strip(), f"Document {doc.id!r} has empty content"

    def test_document_paths_are_relative_md(self, tiny_corpus: Corpus) -> None:
        for doc in tiny_corpus.documents:
            assert doc.path.endswith(".md"), f"{doc.path!r} should end with .md"
            assert not doc.path.startswith("/"), f"{doc.path!r} should be relative"

    def test_qa_pairs_loaded(self, tiny_corpus: Corpus) -> None:
        assert len(tiny_corpus.ground_truth.qa_pairs) == 10

    def test_fidelity_claims_loaded(self, tiny_corpus: Corpus) -> None:
        assert len(tiny_corpus.ground_truth.fidelity_claims) == 4

    def test_contradictions_loaded(self, tiny_corpus: Corpus) -> None:
        assert len(tiny_corpus.ground_truth.contradictions) == 2

    def test_qa_pair_fields(self, tiny_corpus: Corpus) -> None:
        qa = tiny_corpus.ground_truth.qa_pairs[0]
        assert qa.id
        assert qa.question
        assert qa.answer
        assert qa.document_ids

    def test_fidelity_claim_verdicts(self, tiny_corpus: Corpus) -> None:
        valid_verdicts = {"supported", "not_supported", "unknown"}
        for claim in tiny_corpus.ground_truth.fidelity_claims:
            assert claim.verdict in valid_verdicts, (
                f"Claim {claim.id!r} has invalid verdict {claim.verdict!r}"
            )

    def test_metadata_tier(self, tiny_corpus: Corpus) -> None:
        assert tiny_corpus.metadata.tier == "synthetic"

    def test_metadata_language(self, tiny_corpus: Corpus) -> None:
        assert tiny_corpus.metadata.language == "en"


# ── load_corpus: error cases ──────────────────────────────────────────────────


class TestLoadCorpusErrors:
    def test_missing_directory(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_corpus(tmp_path / "nonexistent")

    def test_missing_manifest(self, tmp_path: Path) -> None:
        (tmp_path / "docs").mkdir()
        with pytest.raises(FileNotFoundError, match=r"manifest\.yaml"):
            load_corpus(tmp_path)

    def test_invalid_manifest_yaml(self, tmp_path: Path) -> None:
        (tmp_path / "manifest.yaml").write_text(":: invalid: yaml: [", encoding="utf-8")
        with pytest.raises(ValueError, match=r"Malformed YAML|Invalid manifest"):
            load_corpus(tmp_path)

    def test_manifest_missing_required_fields(self, tmp_path: Path) -> None:
        (tmp_path / "manifest.yaml").write_text("id: test\n", encoding="utf-8")
        with pytest.raises(ValueError, match="Invalid manifest"):
            load_corpus(tmp_path)


# ── verify_corpus_dir ─────────────────────────────────────────────────────────


class TestVerifyCorpusDir:
    def test_tiny_corpus_passes(self, tiny_corpus_path: Path) -> None:
        result = verify_corpus_dir(tiny_corpus_path)
        assert result.ok, f"Expected pass but got errors: {result.errors}"

    def test_missing_manifest(self, tmp_path: Path) -> None:
        result = verify_corpus_dir(tmp_path)
        assert not result.ok
        assert any("manifest.yaml" in e for e in result.errors)

    def test_missing_docs_dir(self, tmp_path: Path) -> None:
        _write_minimal_manifest(tmp_path)
        result = verify_corpus_dir(tmp_path)
        assert not result.ok
        assert any("docs/" in e for e in result.errors)

    def test_doc_count_mismatch_is_warning(self, tmp_path: Path) -> None:
        _write_minimal_manifest(tmp_path, doc_count=99)
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "a.md").write_text("# A", encoding="utf-8")
        result = verify_corpus_dir(tmp_path)
        assert result.ok  # mismatch is a warning, not an error
        assert any("doc_count" in w for w in result.warnings)

    def test_invalid_jsonl_raises_error(self, tmp_path: Path) -> None:
        _write_minimal_manifest(tmp_path, doc_count=1)
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "a.md").write_text("# A", encoding="utf-8")
        gt = tmp_path / "ground_truth"
        gt.mkdir()
        (gt / "qa_pairs.jsonl").write_text("{bad json}\n", encoding="utf-8")
        result = verify_corpus_dir(tmp_path)
        assert not result.ok
        assert any("qa_pairs.jsonl" in e for e in result.errors)


# ── load_manifest ─────────────────────────────────────────────────────────────


class TestLoadManifest:
    def test_loads_tiny_manifest(self, tiny_corpus_path: Path) -> None:
        meta = load_manifest(tiny_corpus_path / "manifest.yaml")
        assert meta.id == "synthetic-tiny@0.1.0"
        assert meta.version == "0.1.0"
        assert meta.doc_count == 5

    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_manifest(tmp_path / "manifest.yaml")


# ── Helpers ───────────────────────────────────────────────────────────────────


def _write_minimal_manifest(root: Path, doc_count: int = 1) -> None:
    root.joinpath("manifest.yaml").write_text(
        textwrap.dedent(f"""\
            id: test-corpus@0.1.0
            version: "0.1.0"
            tier: synthetic
            doc_count: {doc_count}
        """),
        encoding="utf-8",
    )
