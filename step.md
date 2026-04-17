## 2026-04-17

- [完成] 创建 Cursor 规则 `.cursor/rules/sync-progress-to-step.mdc`，全局同步开发进度到 step.md
- [完成] 创建 `.gitignore`，将 `.cursor/` 目录加入 Git 屏蔽列表
- [完成] 创建 Doc/ 全套项目规划文档（00–09，共 10 份），覆盖架构/评测/语料/爬虫/路线图
- [完成] 语料规模升级：Small 500+、Medium 2000+、Large 50000+
- [完成] 新增 Forum corpus 类型 + T5 Opinion Synthesis 评测任务
- [完成] 新建 Doc/09-语料爬取与论坛数据集.md，规划 HN/SO/Reddit/V2EX 爬取方案
- [完成] 明确 corpus 文档格式约定：docs/ 下全部为 .md 文件，modality 描述语义来源而非文件格式；论坛数据经 ForumRenderer 渲染后写入
- [完成] 更新 Doc/06 代码目录树：补充 crawlers/、renderers/、annotators/ 子模块，与 Doc/09 爬虫规划对齐；当前实际文件仅有 Doc/ 规划文档，代码尚未创建

## 2026-04-17 Phase 0 仓库骨架搭建

- [完成] 创建 pyproject.toml：依赖声明（pydantic/typer/rich/litellm/tiktoken 等）、ruff/mypy/pytest 配置、entry_points 注册
- [完成] 创建 src/wikibench/ 完整目录骨架：cli/、models/、adapters/、tasks/、metrics/、runner/、runtime/、judge/、reporters/、storage/、utils/、corpora/（含 synthetic/crawlers/renderers/annotators 子目录），共 60+ 文件
- [完成] 实现核心数据模型：Document/ForumThread、Query/QueryResponse、Corpus/CorpusMetadata/GroundTruth、IngestStats/BenchmarkResult/RunEnvironment（pydantic v2）
- [完成] 实现 WikiAdapter ABC（_base.py）+ 适配器注册表（registry.py）+ NaiveAdapter 完整骨架 + SimpleSummaryAdapter/ReferenceWikiAdapter 占位
- [完成] 实现 Task ABC + 注册装饰器 + T1/T2/T3 占位 + T4/T5/M1/M2 占位
- [完成] 实现 CLI 入口（wikibench --version 可用）：run/corpus/verify/report 子命令骨架
- [完成] 创建 corpora/synthetic/tiny/：5 篇 Markdown 文档 + 10 QA + 4 fidelity claims + 2 contradiction pairs
- [完成] 创建 tests/ 全目录结构：unit/integration/e2e/adapter_contract + conftest.py，单元测试 18 passed
- [完成] 创建 .pre-commit-config.yaml（pre-commit-hooks + ruff + mypy）
- [完成] 创建 .github/workflows/ci.yml（Linux/macOS/Windows × Python 3.11/3.12，含 lint/typecheck/test/package 四 job）
- [完成] 创建 .github/: PR 模板 + Bug/Feature/Adapter 三类 Issue 模板
- [完成] 创建 CODE_OF_CONDUCT.md（Contributor Covenant 2.1）
- [完成] 创建 CONTRIBUTING.md（开发流程/适配器接入/语料贡献/代码规范）
- [完成] 创建 mkdocs.yml + docs/ 文档站骨架（MkDocs Material，含 Getting Started/Reference/Planning 导航）
- [完成] 创建 wikibench.yaml 默认配置（LLM/cache/runner/cost/storage/logging 各节）
- [完成] uv sync 安装成功，wikibench --version 输出 0.1.0-alpha，所有单元测试绿色
- [完成] 创建 Cursor 规则 `.cursor/rules/python-uv-env.mdc`，强制使用 uv 管理 Python 依赖环境

## 2026-04-17 Phase 1 Week 1 — Corpus 加载链路

- [完成] 实现 corpora/loader.py：递归加载 docs/*.md + ground_truth/*.jsonl → Corpus 对象
- [完成] 实现 corpora/manifest.py：load_manifest（YAML 解析 + pydantic 校验）+ verify_corpus_dir（完整性检查）
- [完成] 实现 corpora/__main__.py：python -m wikibench.corpora <path> 输出 Rich 摘要表格
- [完成] 实现 cli/corpus.py：wikibench corpus verify + wikibench corpus info（调用 loader）
- [完成] 补全 tests/unit/test_corpus_models.py（10 个单元测试）
- [完成] 补全 tests/integration/test_corpus_loader.py（23 个集成测试，覆盖正常路径 + 错误路径）
- [完成] 修复 Windows GBK 编码问题（Rich 输出改用 ASCII 标记）
- [完成] 周末验证：python -m wikibench.corpora corpora/synthetic/tiny 输出 5 docs / 10 QA / 4 claims / 2 contradictions；51 passed, 4 skipped

## 2026-04-17 Phase 1 Week 2 — Runtime 基础设施 + NaiveAdapter 完整实现

- [完成] 实现 runtime/token_counter.py：tiktoken（o200k_base/cl100k_base）+ 字符估算 fallback，支持 messages 整体计数
- [完成] 实现 runtime/cost.py：CostTracker（线程本地单例）+ 按 purpose 分桶 + hard_limit 强制中止 + 离线价格表 fallback
- [完成] 实现 runtime/cache.py：ResponseCache（diskcache）+ SHA-256 content-hash key + TTL + 全局单例 + 测试重置工具
- [完成] 实现 runtime/timeout.py：跨平台超时 context manager（Unix SIGALRM / Windows daemon thread + async exc 注入）
- [完成] 实现 runtime/llm.py：litellm 统一入口，集成缓存/计费/超时/mock 模式（WIKIBENCH_LLM_MOCK=1）
- [完成] 升级 NaiveAdapter：system prompt 架构、按 intent 分支构建 messages、JSON 提取 + markdown fence 剥离、ingest 无 LLM 调用
- [完成] 新增单元测试：test_token_counter / test_cost / test_cache / test_llm / test_naive_adapter，共 52 新测试
- [完成] 修复 Windows timeout yield-from bug
- [完成] 周末验证：103 passed, 4 skipped；NaiveAdapter.ingest(docs).query(q) 在 mock 模式下返回合理响应

## 2026-04-17 Phase 1 Week 3 — Task T1/T2/T3 + Runner 全流程

- [完成] 实现 judge/base.py：JudgeVerdict 数据类 + BaseJudge ABC（judge_qa 方法）
- [完成] 实现 judge/default.py：DefaultJudge（LLM-as-judge，Gemini Flash，温度 0，JSON 输出 + 容错解析）
- [完成] 实现 T1 RetrievalAccuracyTask：prepare（QAPairs → Query list）+ score（DefaultJudge 评分）+ aggregate（mean + difficulty 分桶切片）
- [完成] 实现 T2 KnowledgeFidelityTask：prepare（FidelityClaims → fidelity_check Query）+ score（verdict 直接匹配，无 LLM）+ aggregate（precision/recall/hallucination_rate + 混淆矩阵）
- [完成] 实现 T3 ContradictionDetectionTask：prepare（ContradictionPairs → contradiction_check Query）+ score（has_contradiction 标志 + 文本推断 fallback）+ aggregate（recall/precision/F1）
- [完成] 实现 runner/env.py：collect_environment 采集 python/os/wikibench/impl 版本 + llm_models + seed
- [完成] 实现 Runner.run()：corpus 加载 → adapter 解析（实例/类/名称三种方式）→ CostTracker 安装 → ingest → 逐 Task（prepare+query+score+aggregate）→ BenchmarkResult 组装 → CostLimitExceededError 穿透
- [完成] 实现 tests/integration/test_tasks.py（17 个测试，覆盖 T1/T2/T3 正常路径 + 边界情况）
- [完成] 实现 tests/integration/test_runner.py（15 个测试，覆盖 Runner 初始化/全流程/cost_limit/unknown_task 等）
- [完成] 周末验证：135 passed, 2 skipped；Runner(NaiveAdapter, corpus=tiny).run() 返回带分数的 BenchmarkResult

## 2026-04-17 Phase 1 Week 4 — CLI `wikibench run` + Reporters + ResultStore

- [完成] 实现 reporters/console.py：Rich Panel + Table 展示 Header/Ingest/Task/Metrics/Composite/Warnings，分数带颜色梯度
- [完成] 实现 reporters/json.py：render()/save()/load() — BenchmarkResult ↔ JSON 文件完整往返
- [完成] 实现 reporters/markdown.py：render()/save() — GitHub Flavoured Markdown 报告
- [完成] 实现 reporters/__init__.py：render(result, format=...) 统一分发入口
- [完成] 实现 storage/result_store.py：ResultStore.save()/load()/list_runs()/exists()，run_id → <root>/<run_id>/result.json + report.md
- [完成] 实现 cli/run.py：wikibench run --impl/--corpus/--task/--format/--output/--hard-limit 完整选项，支持 entry-point 名称及 module:Class 两种 adapter 指定方式
- [完成] 实现 cli/report.py：wikibench report show <path> + wikibench report list <store-root>，支持 console/json/markdown 格式及 --out 写文件
- [完成] 修复 Runner 中任务模块未导入导致注册表为空的问题（_ensure_tasks_registered）
- [完成] 新增 tests/unit/test_reporters.py（29 个测试，覆盖 json/markdown/console/ResultStore/dispatch）
- [完成] 冒烟验证：wikibench run --impl naive --corpus .../tiny --output .wikibench-results 全流程可用，report list/show 正常渲染
- [完成] 周末验证：164 passed, 4 skipped
- [完成] `.gitignore` 增加 `.wikibench-cache/`、`.wikibench-results/`（本地缓存与评测输出不入库）

## 2026-04-17 Phase 1 Week 5 — SyntheticGenerator（确定性合成语料）

- [完成] 实现 `knowledge_graph.py`：KnowledgeGraph.build（概念列表 + 矛盾对 (0,1),(2,3),…）
- [完成] 实现 `fact_sampler.py`：DocSpec、Markdown 正文模板、PostgreSQL/MongoDB 矛盾块、QA/fidelity/contradiction 派生
- [完成] 实现 `doc_writer.py` + `noise.py`：写入 `docs/topics/*.md`、可选 filler 段落
- [完成] 实现 `verifier.py`：verify_corpus_dir + load_corpus 端到端校验
- [完成] 实现 `generator.py`：`SyntheticGenerator.generate()` 写 manifest + ground_truth JSONL；`use_llm=True` 显式 NotImplementedError
- [完成] 实现 `pipeline.py`：`run_pipeline` 薄封装
- [完成] 实现 `domains/__init__.py`：`get_domain` / `list_domains`，别名 `saas`→`saas_engineering`、`clinical`→`clinical_trials`
- [完成] 接入 `cli/corpus.py`：`wikibench corpus generate --domain/--n-docs/--out/--seed/--qa-per-doc/--noise`
- [完成] `pyproject.toml`：对 `corpora/synthetic/**/*.py` 忽略 TC001/TC003（运行时导入与 TCH 规则冲突）
- [完成] 重写 `tests/unit/test_synthetic_generator.py`（10 个测试，覆盖确定性、pipeline、单文档无矛盾、use_llm）
- [完成] 周末验证：174 passed, 3 skipped；`wikibench corpus generate --domain saas --n-docs 3` 冒烟通过

## 2026-04-17 规划更新 — Phase 1.5 adapter 优先级

- [完成] 调研 llm-wiki-compiler（atomicmemory，536★）：TypeScript CLI，`llmwiki ingest/compile/query`，两阶段编译，SHA-256 增量，MCP Server，支持 Anthropic/OpenAI/Ollama
- [完成] 调研 obsidian-wiki（Ar9av，409★）：代理技能框架，vault 层次结构（concepts/entities/skills...），`.manifest.json` delta 跟踪，无独立 Python API
- [完成] 更新 `Doc/07-开发路线图与MVP计划.md`：Phase 1.5 新增 §4.2 两工具详细技术对照表 + 接入方案；§4.3 任务按 P0/P1/P2/P3 排优先级；§4.4 排期调整（W1 先出两个社区 adapter）；§4.5 里程碑更新；§9 补充未决议题
- [完成] 重写 Phase 2 & 3：合并为「Phase 2 · 生态完善」，去掉商业化，聚焦推广 + 社区反馈闭环 + 框架持续完善；新增推广策略（首发触达 / 持续曝光 / 学术方向）、反馈闭环流程、按版本分阶段的完善路线（v0.5→v0.7→v1.0→v1.x）、leaderboard 基础设施规划
- [完成] `Doc/07` 新增 §4.1.1「第三方评测沙箱原则」：第三方须 git clone 上游、沙箱内安装与调用，adapter 薄封装；修正 llm-wiki-compiler / obsidian-wiki 接入描述；任务表增加沙箱规范；§9 检索策略与上游一致；`.gitignore` 增加 `.wikibench-sandboxes/`
- [完成] `Doc/07` §9 拆分为「9.1 已决议」与「9.2 未决议题」：MVP 排期不绑定固定日历/N 周，以里程碑与完成度为准；未决议题去掉「6 周是否够」；adapter 接入措辞与沙箱 §4.1.1 对齐
- [完成] `Doc/07` §9.1 增补已决议：第三方依赖在沙箱内从 GitHub 本地化部署；主 CI 不强制 Node，可选 job/本地验证；检索策略完全跟沙箱上游，WikiBench 不自造；原 §9.2 对应两条移出未决议
- [完成] `Doc/07` §9.1 再增「首批社区 adapter 接入方式」为已决议（沙箱+CLI / 沙箱+§4.2 B）；排期指向 §4.4；§9.2 删除「第一个社区 adapter 接入时机」

## 2026-04-17 Phase 1 Week 6 — HTML 报告、SQLite 存储与 CLI 集成

- [完成] `reporters/html/renderer.py`：Jinja2 单页 HTML（内联 CSS），`render`/`save`；`reporters` 分发支持 `format=html`
- [完成] `storage/sqlite.py`：`BenchmarkSqliteStore`（save/load/list_run_ids，WAL，UPSERT）
- [完成] `ResultStore`：可选写出 `report.html`（`write_html`）；`cli/run.py` 增加 `--sqlite`，`--format html` 与 `--output` 组合时仅提示已写入目录内 `report.html`
- [完成] `cli/report.py`：`show` 支持从 `.db` 加载（需 `--run-id`）、`--format html`；只读加载时使用 `write_html=False`
- [完成] 单测：`test_reporters` 覆盖 HTML 与 `report.html`；新增 `test_sqlite_store`
- [完成] `cli/run.py`：`TYPE_CHECKING` 导入 `BenchmarkResult`、`_print_report(report_format=...)` 消除 A002/TC001
- [完成] `tests/e2e/test_full_run.py`：启用端到端（`WIKIBENCH_LLM_MOCK=1`，无网络/API）；覆盖 `wikibench run` → `result.json`/`report.md`/`report.html` + SQLite + `report show`/`list`；`pyproject.toml` 中 `e2e` marker 说明同步
- [完成] `.gitignore`：显式忽略 `.wikibench-cache/cache.db` 与 `.wikibench-cache/.cache.db`；对已误跟踪的 `cache.db` 执行 `git rm --cached`
- [完成] 新增 `Doc/10-测试说明书.md`（运行命令、分层、marker、LLM mock、skip 说明）；`Doc/README.md` 导航增加第 10 条
- [完成] MVP 封版准备（P0）：新增 `examples/` 四步示例（语料校验、合成语料、run mock/真 LLM、结果+SQLite+report）；`CHANGELOG.md`；版本升至 `0.2.0-alpha`；扩展根 `README.md`；`README_cn.md` 增加快速开始链接；`.gitignore` 增加 `demo` 缓存/结果目录；`Doc/10` 链到 `examples`
- [完成] `tests/e2e/test_full_run.py`：`CliRunner(mix_stderr=False)`；`--impl` 改为 `wikibench.adapters.builtin.naive:NaiveAdapter`（不依赖 entry points）；`test_version` 断言随 `0.2.0-alpha` 更新
- [完成] `SimpleSummaryAdapter`：ingest 按篇 `llm_call` 摘要、query 复用 naive 的 `_build_messages`/`_parse_response`；默认模型与 Naive 对齐（`gemini-2.5-flash`）；`Runner._resolve_adapter` 支持 `module:Class` 字符串；`test_simple_summary_adapter` + `test_runner` 集成用例；`runner.py` teardown 用 `contextlib.suppress`；`examples/03` 补充 `simple_summary`；`CHANGELOG` 更新
- [完成] `wikibench verify`：实现 `run_adapter_verify`（ingest + T1/T2/T3 各 1 条 query、默认 mock）；CLI 使用 `--adapter`/`-a`（避免 Typer 位置参数与子命令冲突）；`tests/adapter_contract` 与 `tests/unit/test_verify_cli`；CI 增加 `adapter_contract` job + `package` job 上传 wheel artifact；`Doc/10` 更新
