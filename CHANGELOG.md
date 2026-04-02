# Changelog

All notable changes to this project will be documented in this file.

## [1.4.0] - 2026-04-02 (v1.4)

### Added
- **系统设计总结**：[system-design.md](./system-design.md)
  - 设计哲学（5项）
  - 系统特点（4项）
  - Claude Code优势（4项）
  - 架构决策回顾（3项）
  - AI Agent领域启示（3项）
  - 17个Mermaid图表

---

## [1.3.0] - 2026-04-02 (v1.3)

### Added
- **QueryEngine深度分析**：[query-engine-deep-dive.md](./query-engine-deep-dive.md)
  - Prompt构建 / Tool调用 / Retry逻辑 / Cost追踪
- **Agent生命周期分析**：[agent-lifecycle.md](./agent-lifecycle.md)
  - Spawn / Execute / Review / Fix / Terminate / Coordination
  - 13个Mermaid图

### Updated
- **architecture-overview.md** - 全局系统架构总图增强
  - CLI→Runtime→QueryEngine→AgentManager→Tool→Memory→LLM完整调用链

---

## [1.2.0] - 2026-04-02 (v1.2)

### Added
- **数据流分析**：[data-flow-analysis.md](./data-flow-analysis.md) - 7张Mermaid图
  - Prompt Flow / Tool Flow / Memory Flow / Agent Communication Flow
- **系统行为总结**：[system-behavior.md](./system-behavior.md) - 5大行为模式
  - Agent Loop / Self-Healing / Task Lifecycle / Context Management Loop

### Updated
- README.md 扩展文档列表更新

---

## [1.1.0] - 2026-04-02 (v1.1)

### Added
- **源码依据小节**：在第4、7、10、11、13章末尾增加源码依据表格（共56条引用）
- **系统架构总览**：[architecture-overview.md](./architecture-overview.md) - 4张Mermaid架构图
- **系统行为分析**：[behavior-analysis.md](./behavior-analysis.md) - 7个行为流程图
- **隐藏功能与发现**：[hidden-features.md](./hidden-features.md) - 8类发现（KAIROS、Dream、Swarm等）
- **第4.7节：模块层次深度分析** - 五层模块框架

### Improved
- **Mermaid图升级**：12处架构图升级为GitHub原生Mermaid格式
- **调度机制分析**：补充Agent调度流程
- **模块划分分析**：新增五层框架（Agent/Prompt/Tool/Memory/Runtime）

## [1.0.0] - 2026-04-02 (v1.0)

### Added
- **主内容**：[claude-code-deep-dive.md](./claude-code-deep-dive.md) - 20章+附录（~10,000行）
- **Mini Claude Code Demo**：[mini-claude-code/](./mini-claude-code/) - ~1700行Python代码
- **PDF版本**：[claude-code-deep-dive.pdf](./claude-code-deep-dive.pdf)
- **README.md** - 项目导航页
- **LICENSE** - MIT License
- **CONTRIBUTING.md** - 贡献指南

---

## 项目结构

```
claude-code-deep-dive/
├── README.md                    # 项目首页
├── CHANGELOG.md               # 版本日志
├── claude-code-deep-dive.md    # 主内容（20章+附录）
├── claude-code-deep-dive.pdf   # PDF版本
├── architecture-overview.md     # 系统架构总览 🆕
├── behavior-analysis.md         # 系统行为分析 🆕
├── hidden-features.md          # 隐藏功能与发现 🆕
├── mini-claude-code/           # Mini Demo 🆕
│   ├── agent.py
│   ├── tools.py
│   ├── memory.py
│   └── main.py
├── LICENSE
└── CONTRIBUTING.md
```
