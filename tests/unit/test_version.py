"""Smoke test: wikibench package imports and version is set."""

from __future__ import annotations

import wikibench
from wikibench.__version__ import __version__


def test_version_is_set() -> None:
    assert __version__
    assert isinstance(__version__, str)
    assert "0.2.0" in __version__


def test_package_exports_version() -> None:
    assert wikibench.__version__ == __version__
