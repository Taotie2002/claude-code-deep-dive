# 主文档章节与架构文档映射表

> 本表建立主文档（claude-code-deep-dive.md）20章正文与 docs/ 目录下架构文档之间的对应关系。
> 帮助读者在阅读主文档时快速定位到对应的详细分析文档。

---

## 第0章：前置知识
- **内容**：TypeScript 基础（类型/泛型/接口）、CLI 入门、源码阅读方法
- **对应 docs**：无（入门级内容，无专项文档）

---

## 第1章：产品哲学与定位
- **内容**：Claude Code 市场定位、目标用户、核心价值、Buddy System 设计哲学
- **对应 docs**：`01-architecture.md`（系统架构概述中 Buddy System 架构图）

---

## 第2章：设计哲学与原则
- **内容**：简洁优于复杂、编译时优于运行时、安全第一、可组合性、可观测性
- **对应 docs**：`07-system-design.md`（设计哲学章节系统特点与设计原则）

---

## 第3章：人机关系与Buddy设计
- **内容**：人机协作模式、Buddy 与 Agent 分离设计、Buddy Prompt 机制
- **对应 docs**：
  - `01-architecture.md`（系统架构总览中的组件关系图）
  - `03-query-engine.md`（Buddy Prompt 构建流程）

---

## 第4章：系统架构全貌
- **内容**：全局架构图、核心调用链、模块层次深度分析
- **对应 docs**：`01-architecture.md`（全局系统架构总图、组件关系总图）

---

## 第5章：入口设计与短路径
- **内容**：CLI 入口、请求处理流程、快速路径（Fast Path）机制
- **对应 docs**：`01-architecture.md`（请求处理流程图）

---

## 第6章：技术栈选型
- **内容**：TypeScript + Bun 选型理由、runtime 对比（Node vs Bun）
- **对应 docs**：`07-system-design.md`（架构决策回顾中"为什么选择 TypeScript/为什么用 Bun"）

---

## 第7章：工具系统架构
- **内容**：工具注册、调用协议、Tool Executor、权限抽象
- **对应 docs**：
  - `03-query-engine.md`（Tool 调用机制章节）
  - `06-data-flow.md`（Tool Flow 工具调用流）

---

## 第8章：安全权限体系
- **内容**：最小权限原则、allow-once/allow-always、危险命令识别、沙箱防御
- **对应 docs**：
  - `07-system-design.md`（Prompt 注入与沙箱防御章节、安全三角设计）
  - `02-agent-behavior.md`（Tool 调用行为中的权限检查流程）

---

## 第9章：上下文管理与缓存
- **内容**：128K token 上下文窗口、上下文压缩、Snip、Microcompact、Context Collapse
- **对应 docs**：
  - `03-query-engine.md`（Prompt 构建流程、上下文注入）
  - `02-agent-behavior.md`（Context 压缩行为章节）
  - `05-system-behavior.md`（上下文管理循环章节）

---

## 第10章：记忆系统
- **内容**：会话级记忆、持久化记忆、自动提取、gm_record 机制
- **对应 docs**：
  - `01-architecture.md`（Memory 生命周期图）
  - `02-agent-behavior.md`（Memory 管理行为章节）
  - `06-data-flow.md`（Memory Flow 记忆数据流）

---

## 第11章：Multi-Agent 协同
- **内容**：主从式协作、Fork 模式、Agent Spawn、结果汇总
- **对应 docs**：
  - `04-agent-lifecycle.md`（Agent Spawn 行为、协作章节）
  - `02-agent-behavior.md`（Agent Spawn 行为章节）
  - `06-data-flow.md`（Agent Communication Flow、Multi-Agent Routing 架构）

---

## 第12章：并行与UDS通信
- **内容**：并发执行、串行执行、UDS（Unix Domain Socket）通信
- **对应 docs**：
  - `03-query-engine.md`（工具并发/串行混合执行）
  - `04-agent-lifecycle.md`（Agent Coordination 协作章节）

---

## 第13章：KAIROS 与分布式调度
- **内容**：KAIROS 定时任务调度、Forked 子 Agent、Missed-fire 兜底机制
- **对应 docs**：`08-hidden-features.md`（KAIROS 分布式定时任务调度系统章节）

---

## 第14章：Feature Flag 体系
- **内容**：GrowthBook 集成、实验参数、Tree Shaking 效应、灰度发布
- **对应 docs**：
  - `07-system-design.md`（Feature Flag 灵活性章节）
  - `08-hidden-features.md`（Feature Flag 实验矩阵章节）

---

## 第15章：性能优化实践
- **内容**：Token Budget、Cost Tracking、递减收益检测、预算控制
- **对应 docs**：`03-query-engine.md`（Cost Tracking 成本追踪章节）

---

## 第16章：测试与质量保证
- **内容**：单元测试、集成测试、E2E 测试、混沌测试
- **对应 docs**：无专项文档（本章为实践性总结）

---

## 第17章：实操：从零构建 Agent 工具
- **内容**：Tool 注册协议、ToolInput/Output Schema、ToolResult 规范
- **对应 docs**：`03-query-engine.md`（Tool 调用机制章节）

---

## 第18章：实操：安全设计模式
- **内容**：命令白名单、权限分类器、Indirect Prompt Injection 防御
- **对应 docs**：
  - `07-system-design.md`（Prompt 注入与沙箱防御完整章节）
  - `08-hidden-features.md`（autoMode 自动模式分类器章节）

---

## 第19章：成本控制策略
- **内容**：USD Budget、API 调用优化、Token 预算管理、降级策略
- **对应 docs**：`03-query-engine.md`（Cost Tracking、预算控制、模型降级章节）

---

## 第20章：多 Agent 设计模式
- **内容**：主从模式、对等模式、流水线模式、跨 Agent 协作
- **对应 docs**：
  - `04-agent-lifecycle.md`（Agent Coordination 协作章节）
  - `06-data-flow.md`（Multi-Agent Routing 架构、Agent Communication Flow）
  - `09-comparison.md`（Multi-Agent 协作模式对比章节）

---

## 附录

| 附录 | 内容 | 对应 docs |
|------|------|-----------|
| 附录A | 术语表 | 各 docs 中的术语定义 |
| 附录B | 源码索引表 | `08-hidden-features.md`（Feature Flag 源码路径表） |

---

## docs/ 文档能力总览

| 文档 | 主要覆盖内容 | 与主文档的核心关联 |
|------|------------|------------------|
| `01-architecture.md` | 全局系统架构总图、组件关系、调用链 | 第1/3/4/5章核心参考 |
| `02-agent-behavior.md` | Agent Spawn、Context 压缩、Tool 调用行为、Memory 管理 | 第8/9/10/11章核心参考 |
| `03-query-engine.md` | QueryEngine 核心、Prompt 构建、Tool 调用、重试、Cost Tracking | 第7/15/17/19章核心参考 |
| `04-agent-lifecycle.md` | Agent 生命周期各阶段、断点续传、Agent Coordination | 第11/12/20章核心参考 |
| `05-system-behavior.md` | Agent 主循环、自修复机制、上下文管理循环 | 第9章核心参考 |
| `06-data-flow.md` | Prompt Flow、Tool Flow、Memory Flow、Agent Communication Flow | 第7/10/11/20章核心参考 |
| `07-system-design.md` | 设计哲学、系统特点、架构决策、安全防御 | 第2/6/8/14/18章核心参考 |
| `08-hidden-features.md` | KAIROS、Dream、Agent Swarms、Feature Flag、Bridge/Voice Mode | 第13/14/18章核心参考 |
| `09-comparison.md` | Claude Code vs Devin/OpenClaw/Cursor/AutoGPT 等竞品全面对比 | 第1/11/20章辅助参考 |

---

*映射表版本：v1.0 — 与 claude-code-deep-dive.md v1.1 对应*
