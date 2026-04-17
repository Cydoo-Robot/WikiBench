"""Content-addressable hashing utilities."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def dict_hash(d: dict[str, Any]) -> str:
    """Stable SHA-256 hex digest of a JSON-serialisable dict."""
    serialised = json.dumps(d, sort_keys=True, ensure_ascii=False)
    return sha256_hex(serialised)
