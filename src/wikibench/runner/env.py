"""RunEnvironment collection utilities."""

from __future__ import annotations

import platform
import sys

from wikibench.__version__ import __version__
from wikibench.models.result import RunEnvironment


def collect_environment(
    impl_version: str,
    llm_models: dict[str, str],
    seed: int,
    impl_commit: str | None = None,
) -> RunEnvironment:
    """Snapshot the current execution environment for reproducibility.

    Args:
        impl_version: Version string of the adapter being evaluated.
        llm_models: Dict mapping role → model slug (from ``adapter.describe()``).
        seed: Random seed used for this run.
        impl_commit: Optional git commit hash of the adapter implementation.

    Returns:
        A populated :class:`~wikibench.models.result.RunEnvironment`.
    """
    return RunEnvironment(
        python_version=sys.version,
        os=platform.platform(),
        wikibench_version=__version__,
        impl_version=impl_version,
        impl_commit=impl_commit,
        llm_models=llm_models,
        seed=seed,
    )
