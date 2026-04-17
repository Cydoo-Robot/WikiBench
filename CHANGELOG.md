# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-alpha] - 2026-04-17

### Added

- **Examples** (`examples/`): four walkthroughs — corpus verify, synthetic generation, benchmark run (mock / real LLM), persisted results + SQLite + `wikibench report`.
- **HTML reports** via `reporters/html` and `ResultStore` (`report.html`).
- **SQLite result store** (`BenchmarkSqliteStore`) and `wikibench run --sqlite`.
- **End-to-end CLI test** (`tests/e2e/test_full_run.py`) using `WIKIBENCH_LLM_MOCK` (no network in CI).
- **Documentation**: `Doc/10-测试说明书.md` (testing guide).

### Changed

- CLI: `wikibench run` / `wikibench report` support HTML output; report loading from `.db` with `--run-id`.

## [0.1.0-alpha] - 2026-04-17

### Added

- Initial public skeleton: core models, `WikiAdapter` / tasks / runner, `NaiveAdapter`, synthetic-tiny corpus, CLI (`run`, `corpus`, `report`, `verify` placeholder), reporters (console / JSON / Markdown), CI, and planning docs under `Doc/`.

<!-- Release compare links: add when the public repository URL is fixed. -->
