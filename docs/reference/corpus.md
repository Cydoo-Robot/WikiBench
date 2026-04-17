# Corpus Format

Full specification: `Doc/03-数据集与语料库设计.md`

## Directory layout

```
my-corpus/
├── manifest.yaml
├── docs/
│   ├── architecture/
│   │   └── overview.md
│   └── decisions/
│       └── 2026-01-example.md
└── ground_truth/
    ├── qa_pairs.jsonl
    ├── fidelity_claims.jsonl
    └── contradictions.jsonl
```

## manifest.yaml

```yaml
id: my-corpus@1.0.0
version: "1.0.0"
description: "My custom corpus"
tier: small          # synthetic | small | medium | large
domain: saas_engineering
language: en
doc_count: 42
wikibench_min_version: "0.1.0"
```

## Validate

```bash
wikibench corpus verify ./my-corpus
```
