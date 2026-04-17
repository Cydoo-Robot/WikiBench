# 示例 3 · 运行评测（内置基线适配器）

对 **synthetic-tiny** 运行默认任务（T1/T2/T3）。内置基线可选：**`naive`**（全文上下文）、**`simple_summary`**（按篇摘要）、**`reference_wiki`**（摘要 + 全局索引 LLM）。

## A · 无 API 费用（Mock LLM，适合 CI / 本地冒烟）

不访问任何云端模型，结果仅用于验证管线是否跑通。

**Windows (PowerShell)**

```powershell
$env:WIKIBENCH_LLM_MOCK = "1"
uv run wikibench run --impl naive --corpus corpora/synthetic/tiny --quiet --format console
Remove-Item Env:WIKIBENCH_LLM_MOCK
```

**macOS / Linux**

```bash
WIKIBENCH_LLM_MOCK=1 uv run wikibench run --impl naive --corpus corpora/synthetic/tiny --quiet --format console
```

可将 `--impl naive` 换成 `--impl simple_summary`（ingest 阶段对每个文档各调用一次 LLM 生成摘要；mock 下仍无网络费用）。

## B · 真实 LLM（需配置 LiteLLM 支持的提供商与密钥）

取消 mock，并确保环境变量已按 [LiteLLM 文档](https://docs.litellm.ai/docs/providers) 配置（例如 `OPENAI_API_KEY`、`GEMINI_API_KEY` 等）。默认模型见 `NaiveAdapter`（`gemini/gemini-2.5-flash`），可通过适配器配置覆盖（进阶）。

```bash
uv run wikibench run --impl naive --corpus corpora/synthetic/tiny --format console
```

期望：终端打印各任务汇总与综合指标；若 mock，分数可能接近桩响应下的退化值，属预期。

若报错 `No adapter registered under name 'naive'`，说明当前环境未正确注册 entry points（常见于不完整的 editable 安装）。可改用显式类路径：

```bash
uv run wikibench run --impl wikibench.adapters.builtin.naive:NaiveAdapter --corpus corpora/synthetic/tiny --quiet --format console
```

或重新执行 `uv sync --extra dev` 修复安装元数据。
