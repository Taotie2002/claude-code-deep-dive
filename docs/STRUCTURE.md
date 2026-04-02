# Claude Code Deep Dive 文档结构

## 整体架构

本项目采用三层文档体系：

| 层级 | 文件 | 受众 | 说明 |
|------|------|------|------|
| 摘要层 | executive-summary.md | 决策者/管理层 | 5-10页执行摘要 |
| 概览层 | docs/01-architecture.md 等 | 技术Leader/架构师 | 20页技术概览 |
| 深度层 | claude-code-deep-dive.md | 开发者/研究者 | 完整技术报告 |

## docs/ 目录结构

- `01-architecture.md` - 系统架构总览
- `02-agent-behavior.md` - Agent行为分析
- `03-query-engine.md` - QueryEngine剖析
- `04-agent-lifecycle.md` - Agent生命周期
- `05-system-behavior.md` - 系统行为总结
- `06-data-flow.md` - 数据流分析
- `07-system-design.md` - 系统设计总结
- `08-hidden-features.md` - 隐藏功能与发现
- `09-comparison.md` - 与其他Agent对比
- `10-error-handling.md` - 错误处理机制

## 阅读路径

1. **快速了解** → 阅读 `executive-summary.md`
2. **深入技术** → 阅读 `docs/01-architecture.md` 等概览文档
3. **完整研究** → 阅读 `claude-code-deep-dive.md` 完整报告

## 信源导航

详见 `source-annotation-spec.md` 和 `architecture-inference-index.md`
