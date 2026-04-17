# WikiBench

> **The first systematic evaluation infrastructure for LLM-maintained knowledge bases (LLM Wiki)**
> — analogous to SWE-bench for code agents and BEIR for information retrieval.

---

## What is WikiBench?

After Karpathy introduced the **LLM Wiki** concept, 15+ open-source implementations appeared within
two weeks.  The core paradigm: let an LLM "compile" raw documents into a structured knowledge base,
replacing the stateless query-by-query retrieval of RAG.

**The gap:** Every implementation's "test" is the author running it on their own project and
reporting token savings — efficiency only, no quality; one data point, no control variables; no
cross-project reproducibility.

**WikiBench fills that gap.**

## Key Features

| Feature | Description |
|---------|-------------|
| **Standardised tasks** | T1 Retrieval, T2 Fidelity, T3 Contradiction, T4 Grounding, T5 Opinion Synthesis |
| **Controlled corpora** | Synthetic (tiny/saas) + Small (500+ docs) + Medium (2000+) + Large (50000+) |
| **Plug-in adapters** | Any LLM Wiki implementation can be wrapped as a `WikiAdapter` |
| **Composite scoring** | Quality × Efficiency × Maintainability with anti-gaming floor constraints |
| **Open leaderboard** | Public reproducible results, versioned corpora |

## Quick Start

```bash
pip install wikibench
wikibench run --impl naive --corpus synthetic-tiny
```

## Status

WikiBench is in **Phase 0 (Scaffolding)**.  See the [Roadmap](planning/07-roadmap.md) for the
6-week MVP plan.
