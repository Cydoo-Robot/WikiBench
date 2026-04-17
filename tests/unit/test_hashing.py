"""Unit tests for hashing utilities."""

from __future__ import annotations

from wikibench.utils.hashing import dict_hash, sha256_hex


def test_sha256_hex_deterministic() -> None:
    assert sha256_hex("hello") == sha256_hex("hello")


def test_sha256_hex_different_inputs() -> None:
    assert sha256_hex("hello") != sha256_hex("world")


def test_dict_hash_order_independent() -> None:
    a = dict_hash({"x": 1, "y": 2})
    b = dict_hash({"y": 2, "x": 1})
    assert a == b


def test_dict_hash_different_values() -> None:
    assert dict_hash({"x": 1}) != dict_hash({"x": 2})
