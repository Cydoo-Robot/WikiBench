# New Engineer Setup Guide

Welcome to Acme Corp Engineering.  Follow these steps on your first day.

## Prerequisites

- macOS 14+ or Ubuntu 22.04
- Docker Desktop ≥ 4.28
- Python 3.11+ (managed via `uv`)
- `kubectl` 1.29+

## Step 1 — Clone the monorepo

```bash
git clone git@github.com:acme/platform.git
cd platform
```

## Step 2 — Install dev dependencies

```bash
uv sync --all-extras
pre-commit install
```

## Step 3 — Start local services

```bash
docker compose up -d
```

This starts PostgreSQL, Redis, and a local instance of api-gateway on port 8080.

## Step 4 — Run tests

```bash
pytest tests/
```

All tests should pass before you open your first PR.

## Who to contact

- **Platform lead:** @alice (Slack: #platform-eng)
- **On-call:** See PagerDuty rotation in the `#incidents` channel.
