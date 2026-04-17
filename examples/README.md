# WikiBench 示例

本目录提供 **四个** 由浅入深的命令行示例，假设你已在仓库根目录安装依赖：

```bash
uv sync --extra dev
```

并将 `wikibench` 置于 PATH（开发时常用 `uv run wikibench …`）。

| # | 目录 | 内容 |
|---|------|------|
| 1 | [01-corpus-verify](./01-corpus-verify/) | 校验并查看内置 `synthetic-tiny` 语料 |
| 2 | [02-generate-synthetic](./02-generate-synthetic/) | 用 `SyntheticGenerator` 生成小规模合成语料 |
| 3 | [03-run-benchmark](./03-run-benchmark/) | 在语料上运行 `wikibench run`（mock 或真实 LLM） |
| 4 | [04-results-sqlite-report](./04-results-sqlite-report/) | 保存结果目录 + SQLite，并用 `wikibench report` 回看 |

更完整的测试与 CI 说明见 [Doc/10-测试说明书.md](../Doc/10-测试说明书.md)。
