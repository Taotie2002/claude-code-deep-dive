# Claude Code 行为分析与架构推演

> 通过黑盒观测与工程经验，探索 AI 编程工具的设计哲学与工程实践

---

**⚠️ 重要法律与道德免责声明**

**本项目纯属个人学习与技术研究目的**，**不代表 Anthropic 官方立场**，**与 Anthropic 公司无任何关联**。

- 本项目基于公开渠道获取的 Claude Code 相关信息及社区讨论进行**黑盒行为分析与架构推演**，旨在帮助开发者理解 AI 编程工具的工程设计理念与最佳实践。
- 项目中所有代码、文档、Mini Demo 均为**原创教学示例**，供学习参考使用。
- 本项目**不提供任何 Claude Code 原始源码**，也不鼓励或支持任何侵犯知识产权的行为。
- 作者已尽最大努力确保内容基于公开信息，但**不保证信息的完整性、准确性或时效性**。
- **使用本项目及其内容完全由用户自行承担风险**。
- 如发现知识产权问题，请联系作者处理。

本项目遵循 [MIT License](LICENSE) 开源，仅供**非商业、教育和研究**用途。

---

[![Stars](https://img.shields.io/github/stars/Taotie2002/claude-code-deep-dive?style=social)](https://github.com/Taotie2002/claude-code-deep-dive/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/Taotie2002/claude-code-deep-dive)](https://github.com/Taotie2002/claude-code-deep-dive/graphs/contributors)

这是一本基于 Claude Code **公开信息与社区讨论**的系统性技术教程，通过黑盒观测与架构推演，探讨 AI 编程工具的架构设计、工程实践与设计哲学。

---

## ✨ 特色

| 模块 | 内容 |
|------|------|
| **前置知识（第0章）** | 理解本书所需的背景知识铺垫 |
| **核心正文（第1-20章）** | 从产品定位到多 Agent 协作的全链路分析 |
| **架构分析（docs/）** | 系统架构、行为分析、设计哲学文档 |

---

## 📖 目录导航

### 核心内容（docs/）

| 文档 | 说明 |
|------|------|
| [docs/01-architecture.md](./docs/01-architecture.md) | 系统架构总览 |
| [docs/02-agent-behavior.md](./docs/02-agent-behavior.md) | Agent行为分析 |
| [docs/03-query-engine.md](./docs/03-query-engine.md) | QueryEngine剖析 |
| [docs/04-agent-lifecycle.md](./docs/04-agent-lifecycle.md) | Agent生命周期 |
| [docs/05-system-behavior.md](./docs/05-system-behavior.md) | 系统行为总结 |
| [docs/06-data-flow.md](./docs/06-data-flow.md) | 数据流分析 |
| [docs/07-system-design.md](./docs/07-system-design.md) | 系统设计总结 |
| [docs/08-hidden-features.md](./docs/08-hidden-features.md) | 隐藏功能与发现 |
| [docs/09-comparison.md](./docs/09-comparison.md) | 与其他Agent对比 |

### 主文档

| 章节 | 标题 |
|------|------|
| 第0章 | [前置知识](./claude-code-deep-dive.md#第-0-章-前置知识) |
| 第一章 | [产品哲学与定位](./claude-code-deep-dive.md#第一章-产品哲学与定位) |
| ... | ... |

### 附录

| 附录 | 说明 |
|------|------|
| [附录A](./claude-code-deep-dive.md#附录-a术语表) | 术语表 |
| [附录B](./claude-code-deep-dive.md#附录-b源码索引表) | 源码索引表 |

---

## 🚀 实战 Demo

本项目包含一个 **Mini Claude Code 简化复刻 Demo**：

```bash
cd mini-claude-code
pip install -r requirements.txt
python main.py
```

展示 Claude Code 核心架构的简化实现（Agent + Tool调度 + Memory）。

---

## 📦 产物

| 产物 | 位置 |
|------|------|
| PDF版本 | [assets/claude-code-deep-dive.pdf](./assets/claude-code-deep-dive.pdf) |
| Mini Demo | [mini-claude-code/](./mini-claude-code/) |

---

## 👤 适合读者

- **AI 工具开发者** — 理解如何从零构建生产级 AI 编程辅助工具
- **软件架构师** — 参考 Claude Code 的模块化架构与设计模式
- **安全工程师** — 深入了解 AI Agent 的权限模型与沙箱设计
- **对 AI 编程工具内部原理感兴趣的用户** — 满足技术好奇心

---

## ⭐ 支持项目

如果这套教程对你有帮助，欢迎 **Star** ⭐ 一下！

```bash
git clone https://github.com/Taotie2002/claude-code-deep-dive.git
cd claude-code-deep-dive
```

---

## 🤝 参与贡献

欢迎提交 Issue 和 Pull Request！详见 [CONTRIBUTING.md](./CONTRIBUTING.md)。

---

## 📄 License

本项目基于 [MIT License](./LICENSE) 开源。
