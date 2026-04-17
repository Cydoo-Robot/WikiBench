## 2026-04-17

- [完成] 创建 Cursor 规则 `.cursor/rules/sync-progress-to-step.mdc`，全局同步开发进度到 step.md
- [完成] 创建 `.gitignore`，将 `.cursor/` 目录加入 Git 屏蔽列表
- [完成] 创建 Doc/ 全套项目规划文档（00–09，共 10 份），覆盖架构/评测/语料/爬虫/路线图
- [完成] 语料规模升级：Small 500+、Medium 2000+、Large 50000+
- [完成] 新增 Forum corpus 类型 + T5 Opinion Synthesis 评测任务
- [完成] 新建 Doc/09-语料爬取与论坛数据集.md，规划 HN/SO/Reddit/V2EX 爬取方案
- [完成] 明确 corpus 文档格式约定：docs/ 下全部为 .md 文件，modality 描述语义来源而非文件格式；论坛数据经 ForumRenderer 渲染后写入
- [完成] 更新 Doc/06 代码目录树：补充 crawlers/、renderers/、annotators/ 子模块，与 Doc/09 爬虫规划对齐；当前实际文件仅有 Doc/ 规划文档，代码尚未创建
