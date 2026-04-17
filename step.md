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
