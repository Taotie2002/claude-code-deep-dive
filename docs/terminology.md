# 术语表

> **版本**：v2.2
> **更新日期**：2026-04-03
> **作者**：笔帖式
> **说明**：本术语表区分三类术语——Anthropic 官方术语、行业通用术语、项目推演术语——以避免概念混淆。

---

## 概述：三类术语的区分

| 类别 | 标签 | 含义 | 示例 |
|------|------|------|------|
| Anthropic官方 | 🏛️ | Anthropic 官方文档中使用的术语，其定义以官方为准 | Agent, Claude Code, MCP |
| 行业通用 | 🔧 | AI Agent 领域的通用术语，不同项目用法可能略有差异 | Tool, Memory, Prompt Engineering |
| 项目推演 | 🔮 | 本项目基于源码行为推演定义的术语，非官方命名 | QueryEngine, StateManager, CircuitBreaker |

> **为什么要区分？** 在 Claude Code 源码解读的过程中，许多内部模块的名称（如 `QueryEngine.ts`）是源码中的实际文件名，但它们并非 Anthropic 官方在文档中使用的术语。另一些概念（如 "Agent"）在官方文档、行业讨论和本项目中都可能出现，但含义侧重不同。本术语表旨在消除这种歧义。

---

## A. Anthropic官方术语 🏛️

> 这些术语在 Anthropic 官方文档、API 参考或官方博客中有明确记载和定义。

| 术语 | 官方定义 | 出处 |
|------|---------|------|
| **Claude Code** | Anthropic 官方推出的命令行界面（CLI）工具，让开发者通过终端与 Claude 大模型交互，完成软件工程任务 | [Anthropic 官方文档](https://docs.anthropic.com/en/docs/claude-code) |
| **Agent** | 能够代表用户自主执行多步骤任务的 AI 系统；Anthropic 将 Agent 描述为"模型可以在循环中调用工具，直到满足任务完成条件" | [Anthropic API 文档 - Agent](https://docs.anthropic.com/en/docs/build-anthropic-agent) |
| **Agentic AI** | 强调 AI 能够自主推理、规划并调用工具完成复杂任务的 AI 范式；Anthropic 在文档中将"agentic"描述为具备工具使用和多步骤推理能力 | [Anthropic API 文档](https://docs.anthropic.com) |
| **Tool / Tool Use** | Anthropic API 中允许模型调用外部工具（如网页搜索、代码执行）的能力；通过 `tools` 参数在 API 请求中声明，模型可返回 `tool_use` 块 | [Anthropic API - Tool Use](https://docs.anthropic.com/en/docs/build-anthropic-agent/define-tools) |
| **Context Window** | 模型在单次请求中可以处理的最大 token 数量（包括输入和输出）；Claude 3.5 Sonnet 的上下文窗口为 200K tokens | [Anthropic API 文档](https://docs.anthropic.com/en/docs/about-claude/models) |
| **MCP / Model Context Protocol** | Anthropic 推出的标准化协议，用于在 AI 系统与外部数据源、工具之间建立连接；允许第三方服务作为 MCP 服务器向 Claude 提供工具和数据 | [Anthropic MCP 文档](https://modelcontextprotocol.io) |
| **System Prompt** | 在每次 API 请求中随请求发送的指令文本，用于定义模型的行为边界和角色定位；Claude Code 的 system prompt 定义了 AI 作为"编程助手"的身份 | Anthropic API 文档 |
| **Prompt Engineering** | 官方文档中使用的术语，指通过精心设计 prompt 来引导模型产生期望输出的实践；Anthropic 在指南中有专门章节讨论 prompt 优化 | [Anthropic Prompt Engineering 指南](https://docs.anthropic.com/en/docs/build-effective-prompts) |
| **Thinking Mode** | Claude 3.5 Sonnet 支持的思考模式，允许模型在生成最终回复前进行内部推理；通过 `thinking` 参数启用 | [Anthropic API - Thinking](https://docs.anthropic.com/en/docs/build-anthropic-agent/extended-thinking) |
| **Haiku Classifier** | Anthropic API 中用于对工具调用请求进行安全分类的轻量级模型；在 Claude Code 的权限系统中用于判断用户是否需要确认危险操作 | 源码注释 |
| **API Key / ANTHROPIC_API_KEY** | 用于认证 Anthropic API 请求的密钥；Claude Code 需要此密钥才能与 Claude 模型通信 | Anthropic API 文档 |

---

## B. 行业通用术语 🔧

> 这些术语在整个 AI Agent 领域被广泛使用，不同项目可能有略微不同的定义。以下为行业共识性定义。

| 术语 | 通用定义 | 参考来源 |
|------|---------|----------|
| **Agent** | 能够感知环境、做出决策并执行动作以达成目标的 AI 系统；行业共识强调"自主性"和"工具使用能力" | LangChain、AutoGPT、AutoGen 等开源 Agent 框架的通用定义 |
| **Agentic AI** | AI 系统的能力光谱中，强调"自主规划、多步骤执行、工具调用"的一端；区别于仅做单轮问答的 AI | 行业论文与主流 Agent 框架文档 |
| **Tool / Tool Use** | AI 系统调用外部功能（搜索、计算、文件操作等）的能力；在行业语境中泛指一切 AI 可调用的外部能力 | OpenAI Function Calling、LangChain Tools |
| **Context Window** | 单次推理过程中模型能访问的最大 token 数量；超出限制需要通过记忆系统或压缩技术管理 | 所有主流 LLM API（OpenAI、Anthropic、Google） |
| **Prompt Engineering** | 设计、优化输入提示词以获得更好模型输出的技术与实践；包括 few-shot 示例、结构化指令、角色扮演等技巧 | 行业最佳实践总结 |
| **Memory** | AI Agent 在多轮对话或跨会话中保持信息连续性的机制；通常分为短期记忆（对话历史）和长期记忆（持久化知识） | LangChain Memory、MemGPT |
| **Short-term Memory** | 当前会话中的上下文信息，通常指对话历史；受限于 context window 大小 | Agent 框架通用概念 |
| **Long-term Memory** | 跨会话持久化的信息，如用户偏好、过往任务结果、领域知识；通常存储在外部数据库或文件系统 | MemGPT、Retriever-Augmented Generation |
| **Tool Call Loop** | AI 在单次任务中循环调用工具直到任务完成或达到终止条件的模式；是 Agent 系统的核心执行机制 | Claude Code 源码（QueryEngine.ts）、LangChain Agent |
| **State Management** | 管理 Agent 执行过程中的内部状态（任务进度、中间结果、错误状态）的机制；确保多步骤任务的可恢复性 | Agent 框架中的状态机模式 |
| **Circuit Breaker** | 熔断器模式；当某个操作持续失败或超时时，暂时阻止后续调用以避免资源耗尽；来源于分布式系统设计，后被 Agent 框架采用 | 舱壁模式（Bulkhead Pattern）在 AI Agent 中的应用 |
| **Context Overflow** | 对话历史超出模型 context window 限制的情况；需要通过摘要、压缩或选择性截断来处理 | 所有大上下文窗口模型的共同挑战 |
| **Token** | 语言模型处理的基本单位；通常 1 token ≈ 4 个英文字符或 1 个中文字符；API 按 token 计费 | 所有 LLM API |
| **Grounding** | 将模型输出锚定到真实世界状态（如检查文件是否真实存在）的技术；减少幻觉（hallucination） | AI 安全与可靠性研究 |

---

## C. 项目推演术语 🔮

> 以下术语在本项目中基于源码行为推演定义。这些名称在 Claude Code 源码中真实存在，但**不是** Anthropic 官方在公开文档中使用的术语。定义依据为源码结构、函数命名和行为观测。

| 术语 | 推演定义 | 依据 |
|------|---------|------|
| **QueryEngine** | Claude Code 的核心推理引擎（`src/QueryEngine.ts`，约 1295 行）；负责与 Anthropic API 的流式通信、管理 tool-call loop、处理思考模式输出、管理上下文压缩 | 源码文件名与结构分析（第 1 章 1.5.3、第 4 章 4.5.2） |
| **StateManager** | Claude Code 的状态管理中心（`src/state/AppStateStore.ts`）；基于发布-订阅模式的内存状态容器，管理 AppState 全局状态，包括 MCP 连接、工具权限上下文、推理状态、通知等 | 源码 `createStore()` 函数模式与 `AppState` 接口定义（第 4 章 4.4.1） |
| **CircuitBreaker** | Claude Code 中对持续失败操作的熔断机制；体现在权限系统的 `denialLimitExceeded`（超过拒绝次数后降级处理）、API 请求的 `AbortSignal.timeout`（超时中断）以及 `autoCompact` 触发后的降级行为 | 源码权限检查管道、请求超时设计（第 8 章安全体系、第 9 章上下文压缩） |
| **Memory分层** | 本项目对 Claude Code 记忆系统的分层抽象：<br>• **会话层**（Short-term）：`src/utils/sessionStorage.ts` 管理的对话历史<br>• **压缩层**（Mid-term）：`src/services/compact/compactor.ts` 的自动摘要压缩<br>• **持久层**（Long-term）：`~/.claude/` 目录的本地文件存储 | 源码存储模块分析与第 10 章记忆系统结构（第 10 章） |
| **ToolRegistry** | Claude Code 工具系统的中央注册表（`src/tools.ts` 的 `getAllBaseTools()` 与 `assembleToolPool()`）；负责内置工具与 MCP 工具的合并、去重、权限过滤和按序分发 | 源码 `tools.ts` 工具注册逻辑（第 7 章 7.4） |
| **PromptBuilder** | Claude Code 中负责构建发送给 LLM 的完整请求的模块（分散在 `src/QueryEngine.ts` 的 `buildMessages()`、`src/context.ts` 的上下文注入、`src/Tool.ts` 的 `description()`/`prompt()` 中）；负责 System Prompt 生成、工具描述合成、消息历史格式化 | 源码消息构建流程分析（第 4 章 Prompt Layer、第七章工具描述生成） |
| **SandboxManager** | Claude Code 的 Bash 工具沙箱管理器（`src/utils/sandbox/` 及 `src/tools/BashTool/`）；负责在隔离环境中执行 Shell 命令，防止恶意代码访问宿主系统 | 源码沙箱相关文件与 `shouldUseSandbox()` 函数（第 4 章 4.4.2、第 8 章安全体系） |
| **AutoMode** | Claude Code 的自动模式决策系统（`src/hooks/autoMode/`）；根据用户输入特征判断是否启用自动执行（fast path），以减少用户确认等待 | 源码 `tengu_auto_mode_decision` 事件字段分析（第 18 章 18.4.3 勘误） |
| **SessionCoordinator** | Claude Code 的多 Agent 协调器（`src/coordinator/coordinatorMode.js`）；在 `COORDINATOR_MODE` 特性开启时管理多个 Agent 的任务分发与状态同步 | 源码 `coordinatorModeModule` 条件导入分析（第 11 章 Multi-Agent 协同） |
| **FeatureFlag控制器** | Claude Code 基于 `feature('FLAG_NAME')` 的特性开关系统（来自 `bun:bundle`）；编译时常量，实现零运行时开销的 A/B 测试和差异化功能交付 | 源码 `feature()` 函数使用模式（第 6 章 6.3.4、第 14 章 Feature Flag 体系） |

---

## 附录：术语溯源对照表

| 源码文件名/函数名 | 映射到本项目术语 | 类别 |
|------------------|-----------------|------|
| `src/QueryEngine.ts` | QueryEngine | 🔮 项目推演 |
| `src/state/AppStateStore.ts` | StateManager | 🔮 项目推演 |
| `src/tools.ts` + `src/Tool.ts` | ToolRegistry / Tool 接口 | 🔮 项目推演 |
| `src/utils/sandbox/` | SandboxManager | 🔮 项目推演 |
| `src/hooks/autoMode/` | AutoMode | 🔮 项目推演 |
| `src/coordinator/` | SessionCoordinator | 🔮 项目推演 |
| MCP Server | MCP / Model Context Protocol | 🏛️ Anthropic官方 |
| `tools` API 参数 | Tool / Tool Use | 🏛️ Anthropic官方 |
| System Prompt | System Prompt | 🏛️ Anthropic官方 |
| `thinking` 参数 | Thinking Mode | 🏛️ Anthropic官方 |
| 源码 `companion.ts` Buddy系统 | Buddy 系统 | 🔧 行业通用 + 🔮 项目推演 |
| `src/services/compact/` | Memory分层（压缩层） | 🔮 项目推演 |
| `src/utils/sessionStorage.ts` | Memory分层（会话层） | 🔮 项目推演 |
| `~/.claude/` 配置目录 | Memory分层（持久层） | 🔮 项目推演 |

---

## 增补说明

本术语表随项目迭代持续更新。每当发现新的概念混淆点或新增重要术语，应在对应类别下补充。

**更新记录**：

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v2.2 | 2026-04-03 | 新增三类术语分类框架（官方/通用/推演），迁移并扩充附录A原有术语表 |
| v1.1 | 2026-04-02 | 初始版本（仅含章节排序术语表） |
