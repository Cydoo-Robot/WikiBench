# 示例 2 · 生成合成语料

在临时目录生成 **小规模** SaaS 工程领域合成语料（确定性、可复现），并校验输出。

在**仓库根目录**执行；将 `OUT` 换成你希望输出的目录（建议使用绝对路径或 `./tmp-synth`）。

**Windows (PowerShell)**

```powershell
$OUT = ".\tmp-synth-demo"
uv run wikibench corpus generate --domain saas --n-docs 4 --out $OUT --seed 42 --qa-per-doc 2
uv run wikibench corpus verify $OUT
```

**macOS / Linux**

```bash
OUT=./tmp-synth-demo
uv run wikibench corpus generate --domain saas --n-docs 4 --out "$OUT" --seed 42 --qa-per-doc 2
uv run wikibench corpus verify "$OUT"
```

期望：`generate` 写出 `manifest.yaml`、`docs/`、`ground_truth/`；`verify` 通过。

后续评测可把 `--corpus` 指向 `$OUT`。
