# 示例 1 · 校验并查看语料

使用仓库自带的 **synthetic-tiny**（5 篇文档 + ground truth），确认 `manifest.yaml` 与文件结构合法，并打印摘要。

在**仓库根目录**执行（路径按你的克隆位置调整）：

**Windows (PowerShell)**

```powershell
uv run wikibench corpus verify corpora/synthetic/tiny
uv run python -m wikibench.corpora corpora/synthetic/tiny
```

**macOS / Linux**

```bash
uv run wikibench corpus verify corpora/synthetic/tiny
uv run python -m wikibench.corpora corpora/synthetic/tiny
```

期望：`verify` 无错误退出；`python -m wikibench.corpora` 输出文档数、QA 数等统计。
