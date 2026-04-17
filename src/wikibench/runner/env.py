"""RunEnvironment collection utilities."""

from __future__ import annotations

import platform
import sys

from wikibench.__version__ import __version__
from wikibench.models.result import RunEnvironment


def collect_environment(
    impl_version: str,
    impl_commit: str | None,
    llm_models: dict[str, str],
    seed: int,
) -> RunEnvironment:
    return RunEnvironment(
        python_version=sys.version,
        os=platform.platform(),
        wikibench_version=__version__,
        impl_version=impl_version,
        impl_commit=impl_commit,
        llm_models=llm_models,
        seed=seed,
    )
