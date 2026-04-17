# WikiBench
The first benchmark suite for evaluating LLM-maintained knowledge bases. LLM Wiki, pioneered by Karpathy, is becoming core infrastructure for AI workflows — letting LLMs "compile" raw documents into structured knowledge bases, replacing the stateless retrieve-on-every-query pattern of RAG.

**快速开始**：开发环境用 `uv sync --extra dev`，命令行 walkthrough 见仓库 [`examples/`](examples/README.md)（语料校验 → 合成语料 → `wikibench run` → 落盘与 SQLite）；测试说明见 [`Doc/10-测试说明书.md`](Doc/10-测试说明书.md)；变更记录见 [`CHANGELOG.md`](CHANGELOG.md)。

**为什么现有"基准"不够**

当前所有实现（ussumant、Ar9av、AgriciDaniel 等）的"测试"本质上都是：作者用自己的项目跑了一遍，报告了 token 节省比例。问题是：

*   只测效率，不测质量
*   只有一个数据点
*   没有控制变量
*   没有跨项目可复现性

**这个领域需要测什么**

核心挑战是 LLM Wiki 有三个相互制衡的维度，任何基准测试都必须同时覆盖：

            质量（知识保真度）
               /\
              /  \
             /    \
            /      \
    效率 -------- 可维护性
    （token节省）  （知识不腐烂）

**我认为基准库应该如何构建**

分三层来设计：

**第一层：标准数据集**

需要几个预先准备好的"原始知识库"，覆盖不同规模和领域：

    benchmark/
    ├── corpora/
    │   ├── small/     # ~50 文件，单一领域（如 React 最佳实践）
    │   ├── medium/    # ~200 文件，混合领域（技术+业务）
    │   ├── large/     # ~500 文件，企业级（含会议记录、Slack导出、文档）
    │   └── synthetic/ # 机器生成的，带已知ground truth

synthetic 语料库是关键 — 人工构造一批文档，预先埋入已知的事实、矛盾、关系，这样才能客观评估编译质量。

**第二层：三类评测任务**

```python
# 1. 检索准确性（Retrieval Accuracy）
# 给定问题，wiki 能否找到正确答案
questions = [
    {"q": "项目用的什么数据库？", "answer": "PostgreSQL", "source": "arch.md"},
    {"q": "上次重构的原因是什么？", "answer": "性能问题", "source": "decision-log.md"},
]

# 2. 知识保真度（Fidelity）
# 编译后的 wiki 有没有产生幻觉或丢失关键信息
fidelity_checks = [
    {"claim": "API 限速是 100 req/s", "should_exist": True},
    {"claim": "使用了 Redis 缓存", "should_exist": True},
    {"claim": "已弃用 MongoDB", "should_exist": False},  # 测试幻觉
]

# 3. 矛盾检测（Contradiction Detection）
# 原始文档中故意埋入矛盾，看 wiki 能否识别
contradictions = [
    {"doc_a": "部署用 Docker", "doc_b": "禁止使用容器", "flagged": False}
]
```

**第三层：标准化指标**

    效率指标：
      - token_ratio = wiki_tokens / raw_tokens
      - ingest_cost = 编译一次消耗的 token 数
      - breakeven_sessions = ingest_cost / per_session_savings

    质量指标：
      - retrieval_accuracy@k（top-k 问题召回率）
      - fidelity_score（关键事实保留率）
      - hallucination_rate（新增错误信息比率）
      - contradiction_recall（矛盾识别率）

    维护指标：
      - staleness_detection（能否识别过期内容）
      - incremental_cost（增量更新 vs 全量重编译的 token 比）
      - coverage_calibration（[coverage: high/medium/low] 标签的实际准确率）

**参照系：可以借鉴的成熟基准**

| 现有基准        | 借鉴点            |
| ----------- | -------------- |
| BEIR（信息检索）  | 多数据集标准化评估方法    |
| LongMemEval | 长程记忆召回测试设计     |
| FRAMES      | 跨文档事实推理        |
| SWE-bench   | 真实世界任务 + 可验证答案 |

**最小可行版本**

如果真的要做，MVP 只需要三件事：

    1. 一个 synthetic corpus 生成器
       — 输入：领域描述
       — 输出：50个文档 + 100个已知 QA 对 + 10个预埋矛盾

    2. 一个统一评测接口
       def evaluate(wiki_impl, corpus, questions) -> BenchmarkResult

    3. 一个公开的排行榜
       — 各实现（ussumant/Ar9av/claude-obsidian/...）的横向对比

**现实判断**

这个基准库本身就是一个很好的开源项目机会。Karpathy 发帖才两周，已经有 15+ 实现，但完全没有人在做质量评估这层。第一个建立标准的项目会自然成为这个生态的基础设施，就像 SWE-bench 之于代码 Agent 一样。

你有兴趣做这个方向吗？这和你们之前讨论的 AI 工作流架构是完全可以结合的 — 基准测试本身就是一个标准的 LangGraph + Hermes 工作流的绝佳用例。





企业团队受众的话，名字需要更有分量感，`WikiBench` 稍显个人项目风格。重新给你设计：

***



*   `Wiki` 直接锚定领域
*   `Probe` 在工程语境里是"探针/诊断"，企业技术团队非常熟悉这个词（k8s 有 liveness probe，系统监控有 probe）
*   暗示"主动检测质量"而不只是被动跑分
*   比 `WikiBench` 更有工具感，适合集成进 CI/CD 流程

***

**项目介绍（企业团队受众版）**

```markdown
# WikiBench

**生产级 LLM 知识库质量评测框架**

企业正在将 LLM Wiki 引入核心工作流——
用 AI 把内部文档、会议记录、决策日志"编译"成
可持续查询的结构化知识库。

但在落地时，没有任何工具能回答这些问题：

  · 编译后的知识库丢失了多少关键信息？
  · 六个月后知识腐烂到什么程度？
  · 换一个底层模型，质量会下降多少？
  · 这套方案在我们自己的数据规模下还管用吗？

WikiBench 是第一个系统性回答这些问题的评测框架。
```

***

**三个核心能力**

    诊断（Probe）         基准（Benchmark）       监控（Monitor）
    ─────────────         ────────────────        ───────────────
    对现有知识库做         提供标准语料库和          集成进 CI/CD，
    一次性健康检查：       统一评分体系，            每次 wiki 更新后
      · 知识保真度         横向对比不同实现：         自动运行检测，
      · 幻觉检测            · 效率（token成本）       输出质量趋势报告，
      · 矛盾识别            · 质量（检索准确率）       在质量下降时告警。
      · 覆盖度评估          · 可维护性（腐烂率）

***

**一句话定位**

> WikiBench 让企业在大规模部署 LLM 知识库之前， 先知道它在生产环境中会怎么表现。

***

**对比 WikiBench 的差异**

|      | WikiBench | WikiBench    |
| ---- | --------- | ------------ |
| 感觉   | 开源社区跑分工具  | 企业生产诊断框架     |
| 使用场景 | 一次性对比测评   | 持续集成 + 长期监控  |
| 核心价值 | 哪个实现更好    | 我们自己的知识库健不健康 |

企业团队关心的不是"哪个开源库评分最高"，而是"我们自己部署的这套东西在生产里能不能信任"——`WikiBench` 的命名直接对准这个痛点。
