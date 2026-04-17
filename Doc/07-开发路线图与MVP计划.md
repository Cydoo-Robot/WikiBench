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
        │         │              │            │           │
     Phase 0    Phase 1        Phase 1.5    Phase 2     Phase 3
     筹备       MVP            扩展          企业版       生态
    (1-2周)    (4-6周)        (2-3月)       (6月+)       (长期)
```

| Phase | 时长 | 核心目标 | 关键交付 |
|-------|------|---------|---------|
| **0 · 筹备** | 1–2 周 | 定稿设计，搭脚手架 | 仓库骨架、CI、Doc 定稿、v0.1.0-alpha |
| **1 · MVP** | 4–6 周 | 端到端跑通最小闭环 | synthetic 生成器、3 任务、CLI、HTML 报告、v0.2.0 |
| **1.5 · 扩展** | 2–3 月 | 覆盖主要实现 + 数据集 | 5+ 适配器、small corpus、grounding/incremental、v0.5.0 |
| **2 · 企业版** | 6 月+ | WikiProbe + Leaderboard | 监控、CI Action、公开榜单、v1.0.0 |
| **3 · 生态** | 长期 | 成为事实标准 | 论文引用、2+ 下游工具集成、多语言 |

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
- ❌ WikiProbe 企业功能
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

- 覆盖 **至少 5 个主流实现**的 adapter
- 提供 **small 真实语料库**（500+ docs）
- 引入 **增量更新**、**grounding**、**观点综合** 任务
- 搭建论坛数据爬取 pipeline（HN + SO）

### 4.2 重要任务

| 任务 | 产出 |
|------|------|
| 接入 ussumant / Ar9av / AgriciDaniel / claude-obsidian | `wikibench-adapter-*` 5+ 个包 |
| 标注 small corpus（k8s 500+ / react 500+） | `corpora/small-*` 2+ 个，规模 500+ docs |
| **HN Fetcher 爬虫**（Phase 1.5 Week 1） | `corpora/crawlers/hackernews.py` |
| **SO XML Parser**（Phase 1.5 Week 2） | `corpora/crawlers/stackoverflow.py` |
| **Ground Truth Annotator**（立场聚类 pipeline） | `opinion_map.jsonl` 自动生成 |
| **medium corpus 打包**（2000+ docs，含论坛数据） | `corpora/medium-tech-forum/` |
| Grounding 任务实现 | T4 落地 |
| **Opinion Synthesis 任务**（T5） | 依赖 forum corpus |
| Incremental Update 任务 | M1 落地 |
| Staleness Detection 任务 | M2 落地 |
| `wikibench verify-adapter` 契约测试 | 自动化接入验证 |
| 首个社区 leaderboard（静态） | GitHub Pages，手动更新 |
| 文档站正式上线 | docs.wikibench.dev |

### 4.3 爬虫子阶段排期（Phase 1.5 内）

| 周次 | 任务 | 交付 |
|------|------|------|
| 1.5-W1 | HN Fetcher + 数据清洗 | 可采集 HN Ask HN，输出 ForumThread JSON |
| 1.5-W2 | SO XML Parser | 从 Data Dump 提取 5 个标签的 QA |
| 1.5-W3 | Stance Clustering Pipeline | opinion_map.jsonl 自动生成，人工抽查 |
| 1.5-W4 | medium corpus 打包 + T5 任务集成测试 | `wikibench run --task opinion_synthesis` 跑通 |
| 1.5-W5-6 | Reddit PRAW + V2EX Scrapy | 补充中文 / 更多英文数据 |

### 4.4 里程碑：v0.5.0

退出条件：
- 5 个外部 adapter 跑通并在 leaderboard 显示
- 3 个 corpus tier（synthetic / small-500 / medium-2000）
- T5 Opinion Synthesis 任务跑通（至少 HN corpus）
- 引用到至少 1 篇研究论文 / 博客

---

## 5. Phase 2 · 企业版 WikiProbe（Month 4 ~ 12）

### 5.1 目标

从"社区跑分"升级到"企业可信诊断"；同时构建 Large corpus（50000+）。

### 5.2 关键交付

| 模块 | 说明 |
|------|------|
| `wikiprobe probe` | 一键健康检查 CLI，针对用户自有语料 |
| `wikiprobe monitor` | 长期监控模式，定期跑 + 存趋势 |
| GitHub Action `wikiprobe-action@v1` | CI 集成模板 |
| **Large corpus（50000+ docs）** | 基于 HN + SO + Reddit 全量爬取，含 T5 ground truth |
| 对抗性 corpus | 专门诱发幻觉的测试集 |
| Coverage Calibration (M3) | adapter 自评准确性校验 |
| 动态 leaderboard | Next.js + 数据库，支持筛选 / 版本对比 |

### 5.3 商业模式探索（非强制）

- 保持核心开源；可能提供：
  - 托管评测服务（SaaS）
  - 定制 corpus 构建
  - 私有部署企业支持

明确：**不会在社区版塞专有依赖**，不会 core-shell 模式。

### 5.4 里程碑：v1.0.0

退出条件：
- 至少 2 家企业公开使用 WikiProbe
- 动态 leaderboard 每周自动刷新
- 总用户数（下载 / star / adapter 作者）达到 "实质标准" 门槛

---

## 6. Phase 3 · 生态（长期）

- [ ] 多语言支持扩展到 3+ 语言 corpus
- [ ] 与 Hugging Face / Papers with Code 联动
- [ ] 被 LangChain / LlamaIndex / LangGraph 等原生集成
- [ ] 年度 LLM Wiki 质量报告（类似 MLPerf 年报）
- [ ] 学术会议 workshop

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
- [ ] **第一个外部 adapter 对接时机**：自己的三个基线跑通后再主动联系 ussumant / Ar9av
- [ ] **Launch 时机**：Phase 0 结束就可以低调公开 repo + Doc；MVP 完成再正式 launch
