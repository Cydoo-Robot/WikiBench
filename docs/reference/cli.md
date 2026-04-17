# CLI Reference

## wikibench run

```
wikibench run --impl <adapter> --corpus <corpus-id-or-path> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--impl`, `-i` | Adapter name or `package:Class` |
| `--corpus`, `-c` | Corpus ID or path to corpus directory |
| `--task`, `-t` | Task ID (repeatable; default: all) |
| `--seed` | Random seed (default: 42) |
| `--cache-dir` | Cache directory (default: `.wikibench-cache`) |
| `--no-cache` | Disable caching |
| `--output`, `-o` | Output directory |
| `--format`, `-f` | Report format: `console`\|`json`\|`markdown`\|`html` |

## wikibench corpus generate

```
wikibench corpus generate --domain <domain> [OPTIONS]
```

| Option | Description |
|--------|-------------|
| `--domain`, `-d` | Domain template: `saas`\|`clinical_trials` |
| `--n-docs` | Number of documents (default: 50) |
| `--out`, `-o` | Output directory |
| `--seed` | Random seed |

## wikibench corpus verify

```
wikibench corpus verify <path>
```

Validates a corpus directory against the manifest schema.

## wikibench verify-adapter

```
wikibench verify-adapter <adapter-name> [--config <path>]
```

Runs the adapter contract test suite.

## wikibench report

```
wikibench report <path> [--format console|json|markdown|html] [--out <file>]
```
