# Claude Code 源码解读

> 从源码深处理解 AI 编程工具的设计哲学与工程实践

[![Stars](https://img.shields.io/github/stars/Taotie2002/claude-code-deep-dive?style=social)](https://github.com/Taotie2002/claude-code-deep-dive/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/Taotie2002/claude-code-deep-dive)](https://github.com/Taotie2002/claude-code-deep-dive/graphs/contributors)

这是一本基于 Claude Code **泄露源码**的系统性技术教程。通过对源码的逐模块分析，深入探讨 AI 编程工具的架构设计、工程实践与设计哲学。

---

## ✨ 特色

| 模块 | 内容 |
|------|------|
| **前置知识（第0章）** | 理解本书所需的背景知识铺垫 |
| **核心正文（第1-20章）** | 从产品定位到多 Agent 协作的全链路分析 |
| **附录** | 术语表与源码索引，方便快速定位 |

---

## 📖 目录导航

### 第一部分：核心理念

| 章节 | 标题 |
|------|------|
| 第0章 | [前置知识](./claude-code-deep-dive.md#第-0-章-前置知识) |
| 第一章 | [产品哲学与定位](./claude-code-deep-dive.md#第一章-产品哲学与定位) |
| 第二章 | [设计哲学与原则](./claude-code-deep-dive.md#第二章-设计哲学与原则) |
| 第三章 | [人机关系与 Buddy 设计](./claude-code-deep-dive.md#第三章-人机关系与buddy设计) |

### 第二部分：架构全景

| 章节 | 标题 |
|------|------|
| 第四章 | [系统架构全貌](./claude-code-deep-dive.md#第四章-系统架构全貌) |
| 第五章 | [入口设计与短路径](./claude-code-deep-dive.md#第五章-入口设计与短路径) |
| 第六章 | [技术栈选型](./claude-code-deep-dive.md#第六章-技术栈选型) |
| 第七章 | [工具系统架构](./claude-code-deep-dive.md#第七章-工具系统架构) |

### 第三部分：安全与权限

| 章节 | 标题 |
|------|------|
| 第八章 | [安全权限体系](./claude-code-deep-dive.md#第八章-安全权限体系) |
| 第九章 | [上下文管理与缓存](./claude-code-deep-dive.md#第九章-上下文管理与缓存) |

### 第四部分：智能与记忆

| 章节 | 标题 |
|------|------|
| 第十章 | [记忆系统](./claude-code-deep-dive.md#第十章-记忆系统) |
| 第十一章 | [Multi-Agent 协同](./claude-code-deep-dive.md#第十一章-multi-agent-协同) |
| 第十二章 | [并行与 UDS 通信](./claude-code-deep-dive.md#第十二章-并行与uds通信) |
| 第十三章 | [KAIROS 与分布式调度](./claude-code-deep-dive.md#第十三章-kairos-与分布式调度) |

### 第五部分：工程实践

| 章节 | 标题 |
|------|------|
| 第十四章 | [Feature Flag 体系](./claude-code-deep-dive.md#第十四章-feature-flag-体系) |
| 第十五章 | [性能优化实践](./claude-code-deep-dive.md#第十五章-性能优化实践) |
| 第十六章 | [测试与质量保证](./claude-code-deep-dive.md#第十六章-测试与质量保证) |
| 第十七章 | [实操 · 从零构建 Agent 工具](./claude-code-deep-dive.md#第十七章-实操从零构建-agent-工具) |
| 第十八章 | [实操 · 安全设计模式](./claude-code-deep-dive.md#第十八章-实操安全设计模式) |
| 第十九章 | [成本控制策略](./claude-code-deep-dive.md#第十九章-成本控制策略) |
| 第二十章 | [多 Agent 设计模式](./claude-code-deep-dive.md#第二十章-多-agent-设计模式) |

### 附录

| 附录 | 标题 |
|------|------|
| 附录 A | [术语表](./claude-code-deep-dive.md#附录-a术语表) |
| 附录 B | [源码索引表](./claude-code-deep-dive.md#附录-b源码索引表) |

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

## 📚 扩展文档（必读）

| 文档 | 说明 |
|------|------|
| ⭐ [architecture-overview.md](./architecture-overview.md) | **系统架构总览（4张Mermaid图）** - 强烈建议先读 |
| [behavior-analysis.md](./behavior-analysis.md) | 系统行为分析（7个行为流程图） |
| [hidden-features.md](./hidden-features.md) | 隐藏功能与源码发现（8类发现） |
| [data-flow-analysis.md](./data-flow-analysis.md) | 🆕 数据流分析（Prompt/Tool/Memory流） |
| [system-behavior.md](./system-behavior.md) | 🆕 系统行为总结（Agent Loop/自修复机制） |

---

## 📊 项目状态

| 维度 | 评分 |
|------|------|
| 技术准确性 | ⭐⭐⭐⭐⭐ |
| 源码深度 | ⭐⭐⭐⭐⭐ |
| 架构分析 | ⭐⭐⭐⭐⭐ |
| 工程价值 | ⭐⭐⭐⭐（新增Demo） |

**基于外部专家评审持续改进中**

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
