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

### 目标
把规划变成可执行的代码骨架，自己第一天就能跑起来。

### 任务清单

- [ ] **仓库骨架**
  - [ ] `pyproject.toml` + `uv.lock`
  - [ ] 第 06 节规定的目录结构（空实现）
  - [ ] `ruff`, `mypy`, `pytest` 配置
  - [ ] pre-commit hooks
- [ ] **CI/CD**
  - [ ] GitHub Actions：Linux/macOS/Windows × Python 3.11/3.12
  - [ ] lint + 类型检查 + unit 测试
  - [ ] PR 自动标签 / 模板
- [ ] **文档站**
  - [ ] MkDocs Material 基础配置
  - [ ] Doc/ 的内容迁移
  - [ ] `docs.wikibench.dev`（或 GitHub Pages 起步）
- [ ] **社区**
  - [ ] LICENSE（Apache 2.0）
  - [ ] CODE_OF_CONDUCT.md
  - [ ] CONTRIBUTING.md
  - [ ] Issue / PR 模板
  - [ ] Discord / Discussions 开通
- [ ] **v0.1.0-alpha 发布**
  - [ ] 空壳包发布到 TestPyPI
  - [ ] `wikibench --version` 能跑

### 退出条件
- CI 全绿
- 任何人 `pip install wikibench` 能装上（虽然暂无功能）
- Doc/ 全部定稿

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
- ✅ 至少 1 个外部实现的社区 adapter（找 ussumant 或 Ar9av）

**明确不做**：
- ❌ 增量更新 / staleness（Phase 1.5）
- ❌ Grounding 任务
- ❌ Leaderboard 前端
- ❌ WikiBench 企业功能
- ❌ 中文 synthetic（MVP 先英文）

### 3.2 六周周计划

#### Week 1 · 核心数据模型 + Corpus 加载

- [ ] `models/` 全部 pydantic 类（Document / Query / Corpus / Result）
- [ ] `corpora/loader.py` 能加载 manifest.yaml 格式
- [ ] `corpora/manifest.py` schema 校验
- [ ] 手写一个极小 corpus `synthetic-tiny`（5 docs + 10 QA + 2 矛盾）用于测试
- [ ] unit tests 覆盖数据模型

**周末可验证**：`python -m wikibench.corpora.loader corpora/synthetic-tiny` 输出正确统计。

#### Week 2 · Runtime + 最小 Adapter

- [ ] `runtime/llm.py` 统一 llm_call（包 litellm）
- [ ] `runtime/token_counter.py`
- [ ] `runtime/cache.py`
- [ ] `adapters/__init__.py` WikiAdapter ABC
- [ ] `adapters/builtin/naive.py` 完整实现
- [ ] adapter smoke test framework

**周末可验证**：`NaiveAdapter.ingest(tiny_docs)` + `.query(q)` 能返回合理响应。

#### Week 3 · Task + Runner 串起来

- [ ] `tasks/__init__.py` Task ABC + registry
- [ ] `tasks/retrieval_accuracy.py` 完整实现
- [ ] `tasks/knowledge_fidelity.py` 完整实现
- [ ] `tasks/contradiction_detection.py` 完整实现
- [ ] `runner/runner.py` 最小编排
- [ ] `runner/env.py` 收集 RunEnvironment

**周末可验证**：`Runner(..., corpus=tiny).run()` 返回 BenchmarkResult 有分数。

#### Week 4 · CLI + Metric + Reporter

- [ ] `cli/main.py` + `cli/run.py`（typer）
- [ ] `metrics/_registry.py` + 三维度指标
- [ ] `metrics/aggregators/composite.py` 默认 composite
- [ ] `reporters/console.py` Rich 彩色表格
- [ ] `reporters/json.py`
- [ ] `reporters/markdown.py`

**周末可验证**：`wikibench run --impl naive --corpus synthetic-tiny` 在终端打出漂亮表格。

#### Week 5 · Synthetic Generator + SimpleSummary + Reference

- [ ] `corpora/synthetic/generator.py` 主流程
- [ ] `corpora/synthetic/knowledge_graph.py`
- [ ] `corpora/synthetic/fact_sampler.py`
- [ ] `corpora/synthetic/doc_writer.py`（多模态）
- [ ] `corpora/synthetic/noise.py`
- [ ] `corpora/synthetic/verifier.py`
- [ ] `corpora/synthetic/domains/saas_engineering.py`
- [ ] `SimpleSummaryAdapter` 实现
- [ ] `ReferenceWikiAdapter` 实现

**周末可验证**：
```
wikibench corpus generate --domain saas --n-docs 50 --out ./my-corpus
wikibench run --impl reference --corpus ./my-corpus
```

#### Week 6 · HTML 报告 + 存储 + 发布

- [ ] `reporters/html/` 独立文件报告（嵌入图表）
- [ ] `storage/sqlite.py`
- [ ] 端到端 e2e 测试全绿
- [ ] `examples/` 四个示例都跑得通
- [ ] 文档更新 + CHANGELOG
- [ ] **v0.2.0 正式发布到 PyPI**
- [ ] 写 launch 博文 + 发 Karpathy 原推评论区（低调）

**退出条件（MVP 成功标准）**：
1. `pip install wikibench` 后 10 分钟内能跑出第一份报告
2. synthetic-tiny + small corpus 全部任务跑通
3. 所有 MVP 必须项 green-check

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

**WikiBench 接入方案**：`subprocess` 调用 CLI，惰性检测 `llmwiki` 是否已安装。

```
ingest(docs)
  ├── 写 docs → sources/ 目录
  ├── 逐文件 llmwiki ingest <file>
  └── llmwiki compile（两阶段：概念提取 → 页面生成）

query(query)
  └── llmwiki query "<text>"，解析 stdout
```

适配器路径：`src/wikibench/adapters/community/llm_wiki_compiler.py`

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

**WikiBench 接入方案**：在 Python 中**复现**其 vault 编译模式（不依赖外部代理），使用 WikiBench 的 `llm_call` 运行时驱动编译。

```
ingest(docs)
  ├── LLM 对每文档提取概念 + 实体
  ├── 按 obsidian-wiki vault 目录层次生成 markdown 页（含 wikilinks）
  └── 构建内存 manifest + 概念索引

query(query)
  ├── 按关键词/embedding 检索相关 vault 页
  └── LLM 综合相关页面，输出带 citation 的答案
```

适配器路径：`src/wikibench/adapters/community/obsidian_wiki.py`

#### C · 待定（Phase 1.5 后期）

| 工具 | 说明 | 优先级 |
|------|------|--------|
| obsidian-llm-wiki（kytmanov） | PyPI 包，Ollama 本地 LLM，`olw compile/query` | 中 |
| klore / vbarsoum1 | Python，OpenRouter，支持所有代理 | 低 |
| ussumant/llm-wiki-compiler | Claude Code plugin，`/wiki-compile` slash cmd | 参考 |

### 4.3 重要任务

| 任务 | 产出 | 优先级 |
|------|------|--------|
| **`LLMWikiCompilerAdapter`**（subprocess，atomicmemory） | `adapters/community/llm_wiki_compiler.py` | 🔴 P0 |
| **`ObsidianWikiAdapter`**（vault 模式复现） | `adapters/community/obsidian_wiki.py` | 🔴 P0 |
| `wikibench verify-adapter` 契约测试框架 | 自动化接入验证，支持社区提交 | 🟠 P1 |
| `SimpleSummaryAdapter` + `ReferenceWikiAdapter` 完整实现 | 内置基线补全 | 🟠 P1 |
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
| 1.5-W1 | **LLMWikiCompilerAdapter** + ObsidianWikiAdapter 实现 + 契约测试 | 两个社区 adapter 跑通，verify-adapter 绿 |
| 1.5-W2 | SimpleSummary + Reference 实现 + small corpus（k8s 500）| 4 个 adapter 可在同一 corpus 横向对比 |
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
- adapter 接入门槛高（`verify-adapter` 自检不够友好）
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

## 9. 未决议题

- [ ] **MVP 目标窗口**：6 周是否够？可根据 Cursor 辅助速度动态调整
- [ ] **LLMWikiCompilerAdapter 的 Node.js 依赖**：是否在 CI 中安装 Node.js？建议 CI 跳过该 adapter，本地开发时手动安装
- [ ] **ObsidianWikiAdapter embedding 检索**：vault 页面检索是用 keyword BM25 还是向量相似度？MVP 先用关键词，1.5 引入 embedding
- [ ] **第一个外部 adapter 对接时机**：`llm-wiki-compiler` 有公开 CLI，可直接接入无需联系作者；`obsidian-wiki` 也是开源框架，直接复现模式即可
- [ ] **推广节奏**：什么时候主动在 HN / Reddit 发布？建议等 v0.5.0 两个社区 adapter 跑通后，数字更有说服力
- [ ] **社区 Discussion 平台**：GitHub Discussions 够用还是需要 Discord？初期 Discussions 即可，有实质用户量再迁 Discord
- [ ] **语言优先级**：中文 corpus 在 v0.7.0 还是 v1.0.0 引入？取决于是否有中文 LLM Wiki 实现者参与
