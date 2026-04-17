# 07 · 开发路线图与 MVP 计划

> **本文档回答什么问题**
> - 项目分几个阶段？每阶段交付什么？
> - MVP（Minimum Viable Benchmark）具体范围和 6 周排期？
> - 关键里程碑的退出条件？
> - 每周要完成什么？

---

## 1. 总路线图

```
 时间轴 ──────────────────────────────────────────────────────▶
        │         │              │            │
     Phase 0    Phase 1        Phase 1.5    Phase 2
     筹备       MVP            扩展          生态完善
    (1-2周)    (4-6周)        (2-3月)       (长期持续)
```

| Phase | 时长 | 核心目标 | 关键交付 |
|-------|------|---------|---------|
| **0 · 筹备** | 1–2 周 | 定稿设计，搭脚手架 | 仓库骨架、CI、Doc 定稿、v0.1.0-alpha |
| **1 · MVP** | 4–6 周 | 端到端跑通最小闭环 | synthetic 生成器、3 任务、CLI、HTML 报告、v0.2.0 |
| **1.5 · 扩展** | 2–3 月 | 覆盖主流实现 + 丰富数据集 | 5+ 适配器、small corpus、grounding/incremental、v0.5.0 |
| **2 · 生态完善** | 长期持续 | 推广 WikiBench、吸纳社区反馈、持续完善框架 | 动态 leaderboard、多语言 corpus、学术影响力、v1.0.0+ |

---

## 2. Phase 0 · 筹备（Week -2 ~ 0）

> **状态（与仓库对齐，2026-Q2）**：下列 checklist 反映 **当前代码库**；未勾选项为**刻意延后**（公网文档站域名、Discord、TestPyPI 首发等），不代表阻塞开发。

### 目标
把规划变成可执行的代码骨架，自己第一天就能跑起来。

### 任务清单

- [x] **仓库骨架**
  - [x] `pyproject.toml` + `uv.lock`
  - [x] 第 06 节规定的目录结构（`src/wikibench/` 等）
  - [x] `ruff`, `mypy`, `pytest` 配置
  - [x] pre-commit hooks
- [x] **CI/CD**
  - [x] GitHub Actions：Linux/macOS/Windows × Python 3.11/3.12
  - [x] lint + 类型检查 + unit / integration / adapter_contract + 构建 wheel
  - [x] PR / Issue 模板
- [x] **文档站（仓库内）**
  - [x] MkDocs Material 基础配置（`mkdocs.yml` + `docs/`）
  - [x] `Doc/` 规划文档为单一真源
  - [ ] 独立域名 `docs.wikibench.dev`（或 GitHub Pages 对外站）— *可选，未上线*
- [x] **社区（仓库侧）**
  - [x] LICENSE（Apache 2.0）
  - [x] CODE_OF_CONDUCT.md
  - [x] CONTRIBUTING.md
  - [x] Issue / PR 模板
  - [ ] Discord / 额外即时通讯 — *可选*
- [ ] **包发布（公网索引）**
  - [ ] `v0.1.0-alpha` / `v0.2.0-alpha` 发布到 **TestPyPI / PyPI**（当前以源码 + `uv sync` 为主）
  - [x] 本地 / editable 安装后 `wikibench --version` 可用

### 退出条件
- CI 全绿
- 贡献者 `git clone` + `uv sync --extra dev` 可开发、可跑测试（公网 `pip install` 见发布项）
- `Doc/` 与 `examples/` 可复现主流程

---

## 3. Phase 1 · MVP（Week 1 ~ 6）

### 3.1 MVP 范围（严格限定）

**必须做**：
- ✅ `SyntheticGenerator` 能跑通一个领域（SaaS 工程）
- ✅ 三个核心任务：T1 Retrieval / T2 Fidelity / T3 Contradiction
- ✅ 三类效率指标：E1/E2/E3
- ✅ 两个内置基线 adapter：`NaiveAdapter`, `SimpleSummaryAdapter`
- ✅ 一个参考实现 adapter：`ReferenceWikiAdapter`（类 Karpathy 原型）
- ✅ `wikibench run` CLI 能端到端跑通
- ✅ HTML + Markdown + JSON 报告
- ✅ SQLite 结果存储
- [ ] **至少 1 个外部实现的社区 adapter**（ussumant / Ar9av 等 — **Phase 1.5**，见 §4；与内置 `naive` / `simple_summary` / `reference_wiki` 不同）

**明确不做**：
- ❌ 增量更新 / staleness（Phase 1.5）
- ❌ Grounding 任务
- ❌ Leaderboard 前端
- ❌ WikiBench 企业功能
- ❌ 中文 synthetic（MVP 先英文）

### 3.2 六周周计划

#### Week 1 · 核心数据模型 + Corpus 加载

- [x] `models/` 全部 pydantic 类（Document / Query / Corpus / Result）
- [x] `corpora/loader.py` 能加载 manifest.yaml 格式
- [x] `corpora/manifest.py` schema 校验
- [x] 手写一个极小 corpus `synthetic-tiny`（5 docs + 10 QA + 2 矛盾）用于测试
- [x] unit tests 覆盖数据模型

**周末可验证**：在仓库根目录执行 `python -m wikibench.corpora corpora/synthetic/tiny` 或 `wikibench corpus verify corpora/synthetic/tiny`（路径以仓库内 `corpora/synthetic/tiny` 为准）。

#### Week 2 · Runtime + 最小 Adapter

- [x] `runtime/llm.py` 统一 llm_call（包 litellm）
- [x] `runtime/token_counter.py`
- [x] `runtime/cache.py`
- [x] `adapters/__init__.py` WikiAdapter ABC
- [x] `adapters/builtin/naive.py` 完整实现
- [x] adapter 冒烟：`WIKIBENCH_LLM_MOCK=1` + 单测；后续扩展为 `wikibench verify`（见 Week 6）

**周末可验证**：`NaiveAdapter.ingest(tiny_docs)` + `.query(q)` 能返回合理响应。

#### Week 3 · Task + Runner 串起来

- [x] `tasks/__init__.py` Task ABC + registry
- [x] `tasks/retrieval_accuracy.py` 完整实现
- [x] `tasks/knowledge_fidelity.py` 完整实现
- [x] `tasks/contradiction_detection.py` 完整实现
- [x] `runner/runner.py` 最小编排
- [x] `runner/env.py` 收集 RunEnvironment

**周末可验证**：`Runner(..., corpus=tiny).run()` 返回 BenchmarkResult 有分数。

#### Week 4 · CLI + Metric + Reporter

- [x] `cli/main.py` + `cli/run.py`（typer）
- [x] `metrics/_registry.py` + 三维度指标
- [x] `metrics/aggregators/composite.py` 默认 composite
- [x] `reporters/console.py` Rich 彩色表格
- [x] `reporters/json.py`
- [x] `reporters/markdown.py`

**周末可验证**：在仓库根目录 `wikibench run --impl naive --corpus corpora/synthetic/tiny` 在终端打出表格（或 `--format json`）。

#### Week 5 · Synthetic Generator + SimpleSummary + Reference

- [x] `corpora/synthetic/generator.py` 主流程
- [x] `corpora/synthetic/knowledge_graph.py`
- [x] `corpora/synthetic/fact_sampler.py`
- [x] `corpora/synthetic/doc_writer.py`（当前以 Markdown 为主）
- [x] `corpora/synthetic/noise.py`
- [x] `corpora/synthetic/verifier.py`
- [x] `corpora/synthetic/domains/saas_engineering.py` 等（`domains/__init__.py`）
- [x] `SimpleSummaryAdapter` 实现
- [x] `ReferenceWikiAdapter` 实现

**周末可验证**：
```
wikibench corpus generate --domain saas --n-docs 50 --out ./my-corpus
wikibench run --impl reference_wiki --corpus ./my-corpus
```
（`--impl` 使用 entry-point 名 `reference_wiki`，或 `wikibench.adapters.builtin.reference_wiki:ReferenceWikiAdapter`。）

#### Week 6 · HTML 报告 + 存储 + 发布

- [x] `reporters/html/` 单页 HTML 报告（`report.html`；图表类增强可后续迭代）
- [x] `storage/sqlite.py` + `wikibench run --sqlite`
- [x] 端到端 e2e：`tests/e2e/test_full_run.py`（默认 `WIKIBENCH_LLM_MOCK=1`）
- [x] `examples/` 四步 walkthrough（见仓库 `examples/README.md`）
- [x] `CHANGELOG` + `Doc/10-测试说明书.md` 等文档迭代
- [ ] **v0.2.0-alpha（或正式 v0.2.0）发布到 PyPI / TestPyPI** — *待办*
- [ ] 写 launch 博文 + 原推评论区（低调）— *待办*

**退出条件（MVP 成功标准）**：
1. `git clone` + `uv sync --extra dev` 后，按 `examples/` 可在 **约 10 分钟内**跑通「语料 → run → 报告」；公网 `pip install` 以 PyPI 发布项为准。
2. `synthetic-tiny` 上 T1–T3 全跑通；**small corpus（500+）** 为 Phase 1.5 数据目标，不阻塞 MVP 代码闭环。
3. §3.1「必须做」中除 **社区 adapter** 外均已满足；社区 adapter 以 §4 Phase 1.5 为准。

### 3.3 MVP 风险缓冲

每周预留 **20% 缓冲时间**；如延期：
- 先砍 `SimpleSummaryAdapter`（保 naive + reference 即可）
- 再砍 `SyntheticGenerator` 的多模态，只出 markdown
- 最后砍 HTML 报告的图表，只出 markdown 版本

---

## 4. Phase 1.5 · 扩展（Month 2 ~ 4）

### 4.1 目标

- 覆盖 **至少 5 个主流实现**的 adapter，**优先接入两个最高影响力工具**：
  - `llm-wiki-compiler`（atomicmemory，536★，TypeScript CLI，性能标杆）
  - `obsidian-wiki`（Ar9av，409★，代理驱动技能框架，最受 Obsidian 社区关注）
- 提供 **small 真实语料库**（500+ docs）
- 引入 **增量更新**、**grounding**、**观点综合** 任务
- 搭建论坛数据爬取 pipeline（HN + SO）

### 4.1.1 第三方评测沙箱原则（normative）

评测**第三方** LLM Wiki 实现时，WikiBench **不得**在仓库内「自造」与上游等价的编译 / 查询逻辑来冒充该工具。正确做法是 **沙箱模式**：

| 原则 | 说明 |
|------|------|
| **从 Git 拉取上游** | 在隔离工作目录（如 `.wikibench-sandboxes/<impl>/`）内 `git clone` 官方仓库，**固定 tag 或 commit**（可写入 `adapter.yaml` / CI 矩阵），保证可复现 |
| **按上游安装** | 严格遵循上游 README：`npm install` / `pip install` / `setup.sh` 等；CI 可对重型依赖（Node 全局包）做 **可选 job**，本地与 nightly 必跑 |
| **Adapter 只做薄封装** | 负责：写 corpus → 调上游 CLI / 文档规定的入口 → 解析 stdout / 产物目录；**不**复制其算法与提示词策略 |
| **与内置基线区分** | `naive` / `simple_summary` 等是 WikiBench **内置基线**，可自研；**社区 adapter** 名称对应的必须是**真实上游行为**（经沙箱调用） |
| **安全与清理** | 沙箱目录默认加入 `.gitignore`；跑完可保留日志供审计；敏感项仅经环境变量注入，不写死进仓库 |

**反例（禁止）**：在 `adapters/community/` 里手写一套「仿 llm-wiki-compiler 的两阶段编译」而不调用 `llmwiki` 可执行文件或上游包。

**正例**：clone `atomicmemory/llm-wiki-compiler` → `npm ci` / `npx llm-wiki-compiler …` → 解析 `wiki/` 输出。

### 4.2 目标 Adapter 详细调研

#### A · llm-wiki-compiler（atomicmemory/llm-wiki-compiler，536★）

> **定位**：号称性能最好的 LLM Wiki 编译器，灵感直接来源于 Karpathy 原始模式。

| 属性 | 说明 |
|------|------|
| 语言 | TypeScript / Node.js（`npm install -g llm-wiki-compiler`） |
| API | CLI：`llmwiki ingest`、`llmwiki compile`、`llmwiki query` |
| LLM 支持 | Anthropic（默认）、OpenAI、Ollama（通过 `LLMWIKI_PROVIDER` 切换） |
| 增量机制 | SHA-256 hash 检测，仅重编译变更的 source |
| 输出结构 | `wiki/concepts/*.md`（YAML frontmatter + wikilinks）、`wiki/queries/`、`wiki/index.md` |
| MCP 集成 | 内置 MCP Server（`llmwiki serve`），提供 `compile_wiki`、`query_wiki`、`search_pages` 等工具 |
| 依赖 | Node.js >= 18 + API Key（Anthropic 或 OpenAI） |

**WikiBench 接入方案（沙箱）**：在沙箱目录 clone 上游（或 `npm install -g llm-wiki-compiler` 与上游 lockfile 对齐的版本），`subprocess` 调用 **`llmwiki` 真实 CLI**；惰性检测可执行文件是否存在。

```
沙箱准备
  └── git clone https://github.com/atomicmemory/llm-wiki-compiler.git --depth 1 [--branch <tag>]
      └── 按上游 README 安装依赖（npm / npx）

ingest(docs)
  ├── 写 docs → <sandbox>/sources/
  ├── llmwiki ingest <file>（与上游一致）
  └── llmwiki compile

query(query)
  └── llmwiki query "<text>"，解析 stdout
```

适配器路径：`src/wikibench/adapters/community/llm_wiki_compiler.py`（仅封装路径与环境变量，**不**实现编译器本身）

#### B · obsidian-wiki（Ar9av/obsidian-wiki，409★）

> **定位**：代理驱动的技能框架（Skill-based Agent Framework），最受 Obsidian 社区欢迎。

| 属性 | 说明 |
|------|------|
| 语言 | Markdown skill files（无独立 Python/TS 运行时，代理即 LLM） |
| API | 无可编程 API；技能文件（`.skills/`）指导 AI agent 操作 vault |
| Vault 结构 | `concepts/`、`entities/`、`skills/`、`references/`、`synthesis/`、`journal/`、`projects/` |
| 跟踪机制 | `.manifest.json`（delta 摄入 + 来源溯源） |
| LLM 支持 | 任意代理（Claude Code、Cursor、Windsurf 等），不绑定特定 LLM |
| 依赖 | Python 3.11+（vault 读写）+ 外部 AI agent 执行技能 |

**WikiBench 接入方案（沙箱）**：在沙箱目录 **clone** [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)，使用仓库内 **真实的** `.skills/`、`.env.example` → `.env` 流程与 `SETUP.md` 约定；**禁止**在 WikiBench 内手写一套「仿 obsidian-wiki vault 结构」的替代实现来冒充该工具。

```
沙箱准备
  └── git clone https://github.com/Ar9av/obsidian-wiki.git --depth 1 [--branch <tag>]
      └── cp .env.example .env，设置 OBSIDIAN_VAULT_PATH 指向沙箱内临时 vault

ingest / query
  └── 按上游技能文档编排：或调用上游若提供的脚本；若上游**仅支持 AI 代理驱动**，
      则 adapter 通过 WikiBench `llm_call` **加载沙箱内 `.skills/` 中的指令文本**作为 prompt 的一部分，
      使行为与「使用官方仓库技能」一致，而非另写一套平行提示词
```

> **说明**：若某版本上游仍无无头（headless）CLI，可在文档中标注该 adapter 为 **semi-automated**，但评测产物路径、目录结构、manifest 格式仍须与 **clone 下来的仓库**一致。

适配器路径：`src/wikibench/adapters/community/obsidian_wiki.py`（编排沙箱 + 调用上游约定，**不**自研 vault 编译器）

#### C · 待定（Phase 1.5 后期）

| 工具 | 说明 | 优先级 |
|------|------|--------|
| obsidian-llm-wiki（kytmanov） | PyPI 包，Ollama 本地 LLM，`olw compile/query` | 中 |
| klore / vbarsoum1 | Python，OpenRouter，支持所有代理 | 低 |
| ussumant/llm-wiki-compiler | Claude Code plugin，`/wiki-compile` slash cmd | 参考 |

### 4.3 重要任务

| 任务 | 产出 | 优先级 |
|------|------|--------|
| **`LLMWikiCompilerAdapter`**（沙箱 clone + `llmwiki` CLI） | `adapters/community/llm_wiki_compiler.py` | 🔴 P0 |
| **`ObsidianWikiAdapter`**（沙箱 clone + 上游 `.skills/` 编排） | `adapters/community/obsidian_wiki.py` | 🔴 P0 |
| **沙箱目录与 `.gitignore` 规范** | `.wikibench-sandboxes/`、文档说明固定 commit | 🟠 P1 |
| `wikibench verify` + `run_adapter_verify` + `tests/adapter_contract/` | 内置 adapter 契约冒烟；社区接入可在此基础上扩展 | ✅ 已完成（持续增强） |
| `SimpleSummaryAdapter` + `ReferenceWikiAdapter` 完整实现 | 内置基线补全 | ✅ 已完成 |
| 标注 small corpus（k8s 500+ / react 500+） | `corpora/small-*` 2+ 个，规模 500+ docs | 🟠 P1 |
| **HN Fetcher 爬虫** | `corpora/crawlers/hackernews.py` | 🟡 P2 |
| **SO XML Parser** | `corpora/crawlers/stackoverflow.py` | 🟡 P2 |
| **Ground Truth Annotator** | `opinion_map.jsonl` 自动生成 | 🟡 P2 |
| **medium corpus 打包**（2000+ docs） | `corpora/medium-tech-forum/` | 🟡 P2 |
| Grounding 任务实现 | T4 落地 | 🟡 P2 |
| **Opinion Synthesis 任务**（T5） | 依赖 forum corpus | 🟢 P3 |
| Incremental Update 任务 | M1 落地 | 🟢 P3 |
| Staleness Detection 任务 | M2 落地 | 🟢 P3 |
| 首个社区 leaderboard（静态） | GitHub Pages，手动更新 | 🟢 P3 |
| 文档站正式上线 | docs.wikibench.dev | 🟢 P3 |

### 4.4 爬虫子阶段排期（Phase 1.5 内）

| 周次 | 任务 | 交付 |
|------|------|------|
| 1.5-W1 | **LLMWikiCompilerAdapter** + ObsidianWikiAdapter 实现 + 契约扩展 | 两个社区 adapter 跑通；`wikibench verify` 覆盖社区 spec |
| 1.5-W2 | small corpus（k8s 500）+ 与内置三基线同跑验证 | 内置 naive / simple_summary / reference_wiki 已就绪；补 **small** 语料后可横向对比 |
| 1.5-W3 | HN Fetcher + 数据清洗 | 可采集 HN Ask HN，输出 ForumThread JSON |
| 1.5-W4 | SO XML Parser | 从 Data Dump 提取 5 个标签的 QA |
| 1.5-W5 | Stance Clustering Pipeline + T5 ground truth | opinion_map.jsonl 自动生成，人工抽查 |
| 1.5-W6 | medium corpus 打包 + T5 任务集成测试 | `wikibench run --task opinion_synthesis` 跑通 |
| 1.5-W7-8 | Reddit PRAW + V2EX Scrapy + leaderboard 静态版 | 补充中文数据，leaderboard 上线 |

### 4.5 里程碑：v0.5.0

退出条件：
- **llm-wiki-compiler + obsidian-wiki** 两个社区 adapter 跑通，进入 leaderboard
- 共 5 个 adapter 可对比（naive + simple_summary + reference + llm_wiki_compiler + obsidian_wiki）
- 3 个 corpus tier（synthetic / small-500 / medium-2000）
- T5 Opinion Synthesis 任务跑通（至少 HN corpus）
- 引用到至少 1 篇研究论文 / 博客

---

## 5. Phase 2 · 生态完善（长期持续）

> **定调**：不考虑商业化。核心目标是把 WikiBench 推广出去，形成社区正向反馈闭环，让 LLM Wiki 评测成为领域事实标准。

### 5.1 目标

| 方向 | 说明 |
|------|------|
| **推广** | 让更多 LLM Wiki 实现者知道 WikiBench，并愿意用它衡量自己的工具 |
| **社区反馈** | 收集真实用户（研究者、工具作者、工程团队）对评测任务、corpus、指标的意见，快速迭代 |
| **框架完善** | 根据反馈修补设计缺陷、补充新任务、扩大 corpus 覆盖、提升报告可读性 |
| **影响力** | 进入学术视野，被引用、被讨论，吸引社区贡献 adapter 和 corpus |

### 5.2 推广策略

#### 5.2.1 首发触达（v0.2.0 发布时）

- 在 [Karpathy 原始 LLM Wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 评论区 **低调回复**，附 WikiBench 链接和一张对比截图
- 在 llm-wiki-compiler / obsidian-wiki 两个 repo 的 Discussions 或 Issue 里友好告知：「WikiBench 已支持对你的工具进行标准化评测」
- 发一篇 **dev log 博文**（GitHub Pages 或 dev.to），重点讲 synthetic corpus 设计 + T1/T2/T3 任务原理，不推销

#### 5.2.2 持续曝光

- 每个 adapter 跑通后发一条简短帖子（HN、X/Twitter、Reddit r/MachineLearning）：只贴数字和方法，不夸大
- 维护一份公开 `ADAPTERS.md`，列出所有已测实现的分数，保持透明
- 接受社区 PR 贡献新 adapter（见 `CONTRIBUTING.md` 接入流程）

#### 5.2.3 学术方向

- 准备一份 2–4 页的技术报告（arXiv / ACL Findings 方向），重点讲评测框架设计
- 向 NeurIPS / ICLR Datasets & Benchmarks 投稿（中长期）

### 5.3 社区反馈闭环

```
用户遇到问题 / 提出改进
        │
        ▼
GitHub Issue / Discussion（模板引导：任务设计 / corpus 质量 / adapter 接入 / 报告可读性）
        │
        ▼
Triage（每周一次）：
  - 高频需求 → 进入下个迭代
  - 设计缺陷 → 优先 hotfix
  - 新 corpus/task 提案 → 评估合入标准
        │
        ▼
发版 CHANGELOG（清晰写明「基于 issue #X 的改进」）
```

**反馈优先处理区域**（预判高频问题）：
- 评测任务覆盖不足（如缺乏 Grounding、Incremental 任务）
- Corpus 领域偏差（当前只有 SaaS / Clinical，缺 k8s / react / 金融 / 中文）
- adapter 接入门槛高（`wikibench verify` 对社区场景的提示与文档仍可增强）
- 报告可读性（图表、对比视图）

### 5.4 框架持续完善路线

| 阶段 | 触发条件 | 主要工作 |
|------|---------|---------|
| **v0.5.0 → v0.7.0** | 第一批社区反馈到位 | 补全 T4 Grounding + M1 Incremental；改进 adapter 接入文档；引入 embedding 检索（ObsidianWikiAdapter） |
| **v0.7.0 → v1.0.0** | 5+ adapter 稳定，corpus 覆盖 3 tier | 动态 leaderboard 上线；Large corpus（50000+ docs）；Coverage Calibration (M3)；多语言 corpus（中文优先） |
| **v1.0.0+** | 有研究者复现 / 引用 | 年度 LLM Wiki 质量报告；对接 Hugging Face Datasets / Papers with Code；GitHub Action `wikibench-action@v1` |

### 5.5 基础设施

| 项目 | 方案 |
|------|------|
| Leaderboard（静态 v0.5） | GitHub Pages，手动更新 markdown 表格 |
| Leaderboard（动态 v1.0） | Next.js + JSON / SQLite，支持筛选 / 版本对比，自动 PR 触发刷新 |
| CI 集成 | GitHub Action `wikibench-action@v1`（用户在自己 repo 引用） |
| 长期监控 | `wikibench monitor` CLI（定期跑 + 趋势存储，配合 SQLite） |
| 对抗性 corpus | 专门诱发幻觉的测试集（Phase 2 中期引入） |

### 5.6 里程碑

| 版本 | 核心退出条件 |
|------|------------|
| **v0.5.0** | 5 adapter 可对比；3 corpus tier；leaderboard 静态版上线；T5 跑通 |
| **v1.0.0** | 动态 leaderboard；Large corpus；至少 1 篇学术引用或技术博文被社区转发 |
| **v1.x（持续）** | 每季度有社区贡献的新 adapter 或 corpus；年度 LLM Wiki 质量报告发布 |

---

## 7. 成本预算

- 云 / API 预算：~$200 / 月（开发期 synthetic 生成 + 联调）
- 基础设施：GitHub 免费额度起步 → Cloudflare Pages / Vercel 免费

---

## 8. 日常节奏建议

- **每天**：用 Cursor 推进当日任务，以每周目标为粒度规划
- **每周**：demo 当周交付（即使不完美）；更新周计划 checklist
- **每迭代结束**：写一篇简短博文 / dev log（对外透明度 = 倒逼质量）
- **每月**：发一次 CHANGELOG

---

## 9. 决议项与未决议题

### 9.1 已决议

- **MVP 排期原则**：**不绑定固定日历或「N 周内必须完成」**；Phase 1 仍按文档中的周计划作为**逻辑顺序与检查清单**，但以**里程碑是否达成**为准，不以实际经过的周数施压。进度可随实现复杂度与社区反馈调整，**完成度与可复现性优先于截止日期**。

- **第三方依赖与运行环境（Node.js 等）**：不在 WikiBench 主仓库内「内置」上游运行时。评测时在 **沙箱目录**（见 §4.1.1）**从 GitHub 拉取上游项目并本地化部署**（`git clone` + 按 README 安装依赖，如 `npm ci` / 全局 `llmwiki`）。**默认 CI（lint / 单测 / 核心 adapter）不安装 Node.js**；针对 `LLMWikiCompilerAdapter` 的集成验证可放在 **可选 workflow** 或本地 / nightly，避免阻塞主链路。

- **检索与向量策略（ObsidianWiki 等）**：**不由 WikiBench 在框架内选定** BM25 或 embedding。以 **沙箱内已 clone 的上游仓库** 的实现、配置项与文档为准；Adapter 只负责把 corpus 与查询交给该环境，**禁止**在 WikiBench 内单独实现一套检索策略冒充上游行为。

- **首批社区 adapter（llm-wiki-compiler / obsidian-wiki）接入方式**：已定为 **沙箱 + 真上游**，不讨论「是否自研等效实现」。`llm-wiki-compiler`：沙箱内 clone [atomicmemory/llm-wiki-compiler](https://github.com/atomicmemory/llm-wiki-compiler)，调用公开 **`llmwiki` CLI** 编排 ingest/query（§4.2 A）。`obsidian-wiki`：沙箱内 clone [Ar9av/obsidian-wiki](https://github.com/Ar9av/obsidian-wiki)，遵循 **§4.1.1** 与 **§4.2 B**（上游 `.skills/` 与 vault 约定，不另写平行编译器）。**工程排期**（何时写代码、何时进 leaderboard）以 **Phase 1.5 §4.4** 周计划为准，**不作为开放议题**。

### 9.2 未决议题

- [ ] **推广节奏**：什么时候主动在 HN / Reddit 发布？建议等 v0.5.0 两个社区 adapter 跑通后，数字更有说服力
- [ ] **社区 Discussion 平台**：GitHub Discussions 够用还是需要 Discord？初期 Discussions 即可，有实质用户量再迁 Discord
- [ ] **语言优先级**：中文 corpus 在 v0.7.0 还是 v1.0.0 引入？取决于是否有中文 LLM Wiki 实现者参与
