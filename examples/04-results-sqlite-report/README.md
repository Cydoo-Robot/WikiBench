# 示例 4 · 落盘结果、SQLite 与报告回放

将一次完整评测写入**结果目录**（`result.json` + `report.md` + `report.html`），并**追加**到 SQLite；再用 `wikibench report` 列出并展示。

以下在**仓库根目录**执行；输出目录与数据库路径可自定义。

**Windows (PowerShell)**

```powershell
$OUT = ".\.wikibench-results-demo"
$DB = ".\.wikibench-results-demo\runs.db"
$env:WIKIBENCH_LLM_MOCK = "1"
uv run wikibench run `
  --impl naive `
  --corpus corpora/synthetic/tiny `
  --output $OUT `
  --sqlite $DB `
  --cache-dir ".\.wikibench-cache-demo" `
  --quiet `
  --format json
Remove-Item Env:WIKIBENCH_LLM_MOCK

# 列出 run_id
uv run wikibench report list $OUT

# 从目录渲染（任选一种格式）
$runId = (Get-ChildItem $OUT -Directory | Select-Object -First 1).Name
uv run wikibench report show (Join-Path $OUT $runId) --format markdown

# 从 SQLite 加载同一 run
uv run wikibench report show $DB --run-id $runId --format html
```

**macOS / Linux**

```bash
OUT=./.wikibench-results-demo
DB=./.wikibench-results-demo/runs.db
export WIKIBENCH_LLM_MOCK=1
uv run wikibench run \
  --impl naive \
  --corpus corpora/synthetic/tiny \
  --output "$OUT" \
  --sqlite "$DB" \
  --cache-dir ./.wikibench-cache-demo \
  --quiet \
  --format json
unset WIKIBENCH_LLM_MOCK

uv run wikibench report list "$OUT"
RUN_ID="$(ls -1 "$OUT" | head -1)"
uv run wikibench report show "$OUT/$RUN_ID" --format markdown
uv run wikibench report show "$DB" --run-id "$RUN_ID" --format html
```

说明：演示目录 `.wikibench-results-demo` / `.wikibench-cache-demo` 已加入 `.gitignore` 的同类规则；若名称不同，请勿将大文件或密钥提交到 Git。
