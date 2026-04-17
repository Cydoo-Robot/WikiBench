"""SQLite append-only store for :class:`BenchmarkResult` (optional, Week 6)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from wikibench.models.result import BenchmarkResult


class BenchmarkSqliteStore:
    """Persist benchmark runs in a single SQLite file.

    Schema
    ------
    One row per run; full result is stored as JSON (same shape as ``result.json``).

    Typical use: ``wikibench run ... --sqlite ~/.wikibench/runs.db``
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS benchmark_runs (
                run_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                impl TEXT NOT NULL,
                corpus_id TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_benchmark_runs_created "
            "ON benchmark_runs(created_at DESC)"
        )
        return conn

    def save(self, result: BenchmarkResult) -> None:
        """Insert or replace one run."""
        payload = result.model_dump_json()
        created = result.created_at.isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO benchmark_runs (run_id, created_at, impl, corpus_id, payload_json)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    created_at = excluded.created_at,
                    impl = excluded.impl,
                    corpus_id = excluded.corpus_id,
                    payload_json = excluded.payload_json
                """,
                (result.run_id, created, result.impl, result.corpus_id, payload),
            )
            conn.commit()

    def load(self, run_id: str) -> BenchmarkResult:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM benchmark_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            raise FileNotFoundError(f"No run {run_id!r} in {self.path}")
        data = json.loads(row[0])
        return BenchmarkResult.model_validate(data)

    def list_run_ids(self) -> list[str]:
        """Newest first."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT run_id FROM benchmark_runs ORDER BY created_at DESC"
            ).fetchall()
        return [r[0] for r in rows]
