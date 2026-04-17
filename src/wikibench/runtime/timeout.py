"""Cross-platform timeout helpers.

On Unix, ``signal.SIGALRM`` gives true preemptive timeouts.
On Windows (no SIGALRM), we use a daemon thread that calls
``ctypes.pythonapi.PyThreadState_SetAsyncExc`` to raise ``TimeoutError``
in the calling thread.  This covers the common case of I/O-bound LLM calls.

Usage::

    with timeout(seconds=60):
        reply = some_llm_call(...)

    # or as a decorator
    @with_timeout(seconds=30)
    def fast_function():
        ...
"""

from __future__ import annotations

import ctypes
import logging
import platform
import threading
from contextlib import contextmanager
from typing import Callable, Generator, TypeVar

log = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., object])

_IS_WINDOWS = platform.system() == "Windows"


class TimeoutError(RuntimeError):  # noqa: A001 — intentional shadow
    """Raised when an operation exceeds its allotted time."""

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        super().__init__(f"Operation timed out after {seconds:.1f}s")


# ── Context manager ───────────────────────────────────────────────────────────

@contextmanager
def timeout(seconds: float) -> Generator[None, None, None]:
    """Context manager that raises ``TimeoutError`` after ``seconds``.

    Args:
        seconds: Maximum number of seconds to allow.

    Raises:
        TimeoutError: If the block does not complete within ``seconds``.
    """
    if seconds <= 0:
        yield
        return

    if _IS_WINDOWS:
        with _windows_timeout(seconds):
            yield
    else:
        with _unix_timeout(seconds):
            yield


# ── Decorator ─────────────────────────────────────────────────────────────────

def with_timeout(seconds: float) -> Callable[[F], F]:
    """Decorator version of :func:`timeout`."""

    def decorator(fn: F) -> F:
        import functools

        @functools.wraps(fn)
        def wrapper(*args: object, **kwargs: object) -> object:
            with timeout(seconds):
                return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


# ── Platform implementations ──────────────────────────────────────────────────

@contextmanager
def _unix_timeout(seconds: float) -> Generator[None, None, None]:
    import signal

    def _handler(signum: int, frame: object) -> None:
        raise TimeoutError(seconds)

    old_handler = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


@contextmanager
def _windows_timeout(seconds: float) -> Generator[None, None, None]:
    """Best-effort timeout for Windows using async exception injection."""
    main_thread_id = threading.current_thread().ident
    cancelled = threading.Event()

    def _watchdog() -> None:
        if not cancelled.wait(timeout=seconds):
            # Inject TimeoutError into the calling thread
            if main_thread_id is not None:
                ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_ulong(main_thread_id),
                    ctypes.py_object(TimeoutError),
                )
                if ret == 0:
                    log.debug("Timeout injection failed (thread may have finished)")

    watchdog = threading.Thread(target=_watchdog, daemon=True)
    watchdog.start()
    try:
        yield
    except TimeoutError:
        raise TimeoutError(seconds)
    finally:
        cancelled.set()
        watchdog.join(timeout=1.0)
