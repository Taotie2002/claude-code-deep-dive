# Claude Code 数据流分析

> 本章分析 Claude Code 核心系统的数据流动路径

---

## 1. Prompt Flow（提示词流）

Prompt Flow 描述从用户输入到 LLM 调用的完整数据变换路径。

### 1.1 System Prompt 构建流程

```mermaid
flowchart TD
    subgraph 构建阶段
        A[基础 System Prompt 模板] --> B[加载项目上下文<br/>AGENTS.md / SOUL.md / TOOLS.md]
        B --> C[加载当前任务上下文<br/>memory/task_flow.md]
        C --> D[User Context 组装]
        D --> E[Available Skills 扫描]
        E --> F[Buddy System Prompt 注入]
        F --> G[完整 System Prompt]
    end
```

### 1.2 用户输入 → 上下文组装 → LLM 调用

```mermaid
sequenceDiagram
    participant U as 用户输入
    participant C as Context Assembler
    participant M as Memory
    participant P as Prompt Builder
    participant L as LLM

    U->>C: 原始用户消息
    C->>M: 查询相关记忆
    M-->>C: 历史上下文片段
    C->>P: 组装中间产物
    P->>P: 应用 SOUL.md 人格设定
    P->>P: 注入 Available Skills
    P->>P: 注入 Tools 定义
    P->>L: 最终 System Prompt + 用户消息
    L-->>P: LLM 输出
    P-->>U: 流式响应
```

### 1.3 Buddy System Prompt 注入机制

```mermaid
flowchart LR
    subgraph 普通 Agent
        A1[Session Context] --> B1[Basic Prompt]
    end

    subgraph Buddy System
        A2[Session Context] --> B2[Base Prompt]
        B2 --> C2[Skill Context<br/>能力描述]
        B2 --> D2[Memory Context<br/>召回的记忆]
        B2 --> E2[Role Context<br/>角色设定]
        C2 & D2 & E2 --> F2[Fused Buddy Prompt]
    end

    style Buddy System fill:#e8f5e9,stroke:#4caf50
```

---

## 2. Tool Flow（工具调用流）

Tool Flow 描述从工具匹配到结果返回的完整调用链路。

### 2.1 工具调用总览

```mermaid
flowchart TD
    A[用户请求 / LLM 决策] --> B{请求类型判断}
    B -->|需要工具| C[Tool Matcher]
    B -->|纯文本| Z[直接响应]

    C --> D[工具名称匹配]
    D --> E[权限检查引擎]
    E --> F{权限通过?}
    F -->|否| G[拒绝响应 / 请求授权]
    F -->|是| H[Tool Executor]

    H --> I[BashTool]
    H --> J[FileTool / Read / Write / Edit]
    H --> K[AgentTool / Subagent]
    H --> L[Web Tools]

    I & J & K & L --> M[结果序列化]
    M --> N[结果注入上下文]
    N --> Z
```

### 2.2 BashTool 调用链

```mermaid
sequenceDiagram
    participant LLM
    participant TM as Tool Matcher
    participant PE as Permission Engine
    participant BE as Bash Executor
    participant FS as File System
    participant R as Result Serializer

    LLM->>TM: 请求调用 bash
    TM->>TM: 解析命令与参数
    TM->>PE: 安全检查
    PE->>PE: 危险命令识别
    PE-->>TM: 批准 / 拒绝
    TM->>BE: 执行命令
    BE->>FS: 系统调用
    FS-->>BE: 输出结果
    BE->>R: 序列化 stdout/stderr/exitCode
    R-->>LLM: ToolResult
```

### 2.3 FileTool 调用链

```mermaid
sequenceDiagram
    participant LLM
    participant C as Context Assembler
    participant FT as FileTool Router
    participant PE as Permission Engine
    participant OPS as File Operations
    participant R as Result

    LLM->>C: 读取/写入/编辑请求
    C->>FT: 分发到对应操作
    FT->>PE: 路径权限检查
    PE->>PE: 作用域限制验证
    PE-->>FT: 授权结果
    FT->>OPS: 执行文件操作
    OPS-->>FT: 操作结果
    FT-->>R: 结构化响应
    R-->>LLM: 工具结果
```

### 2.4 AgentTool / Subagent 调用链

```mermaid
flowchart TD
    A[LLM 请求 spawn subagent] --> B[Agent Registry]
    B --> C[创建子 Agent 实例]
    C --> D[独立 Session 分配]
    D --> E[Task 上下文传递]
    E --> F[Subagent 执行]
    F --> G[结果 push 回调]
    G --> H[主 Agent 上下文注入]
    H --> I[继续主流程]

    style Subagent 执行 fill:#fff3e0,stroke:#ff9800
```

---

## 3. Memory Flow（记忆数据流）

Memory Flow 描述会话记忆的生成、压缩、持久化与召回过程。

### 3.1 记忆全生命周期

```mermaid
flowchart LR
    subgraph 生成
        A[对话消息] --> B[自动提取]
        A --> C[主动记录 gm_record]
    end

    subgraph 处理
        B & C --> D[重要性评分]
        D --> E[压缩阶段]
        E --> F[向量嵌入]
    end

    subgraph 存储
        F --> G[(持久化存储)]
    end

    subgraph 召回
        G --> H[Query 匹配]
        H --> I[相关记忆检索]
        I --> J[上下文注入]
    end

    J --> A
```

### 3.2 记忆召回与遗忘

```mermaid
sequenceDiagram
    participant U as 用户输入
    participant QA as Query Analyzer
    participant GM as Graph Memory
    participant SC as Score Calculator
    participant MR as Memory Retriever
    participant C as Context Assembler

    U->>QA: 消息内容
    QA->>GM: 相似度搜索
    GM-->>SC: 候选记忆列表
    SC->>SC: 计算相关性分数
    SC->>MR: 过滤低分记忆
    MR->>C: Top-K 记忆片段
    C->>C: 注入 Prompt Context
```

### 3.3 自动记忆提取流程

```mermaid
flowchart TD
    A[会话结束 / 关键节点] --> B[分析对话内容]
    B --> C[提取实体与关系]
    C --> D[生成记忆摘要]
    D --> E[重要性评估]
    E --> F{分数 > 阈值?}
    F -->|是| G[写入长期记忆]
    F -->|否| H[标记为临时]
    G --> I[更新 MEMORY.md]
    H --> J[会话结束后丢弃]
```

---

## 4. Agent Communication Flow（Agent 通信流）

Agent Communication Flow 描述多 Agent 环境下的消息传递、权限同步与状态同步。

### 4.1 Agent 间消息传递

```mermaid
sequenceDiagram
    participant M as Main Agent
    participant MQ as Message Queue
    participant A as Sub Agent
    participant MB as Mailbox
    participant ST as State Store

    M->>MQ: 发送任务消息
    MQ->>A: 路由到目标 Agent
    A->>MB: 写入 Mailbox
    MB->>ST: 更新目标 Agent 状态
    A-->>M: 结果回调
    ST-->>M: 状态同步确认
```

### 4.2 权限同步机制

```mermaid
flowchart TD
    subgraph 权限来源
        A[User 授权] --> B[Permission Store]
    end

    subgraph 权限传播
        B --> C{Main Agent<br/>发起请求}
        C -->|跨 Agent| D[Permission Sync]
        D --> E[Sub Agent 权限列表更新]
    end

    subgraph 执行验证
        E --> F[Tool 调用时]
        F --> G[Permission Engine]
        G --> H{授权存在?}
        H -->|是| I[执行工具]
        H -->|否| J[拒绝 + 通知 Main]
    end

    style 权限传播 fill:#e3f2fd,stroke:#2196f3
```

### 4.3 状态同步与 Mailbox 机制

```mermaid
flowchart LR
    subgraph Agent A
        A1[Mailbox Inbox] --> A2[Message Handler]
        A2 --> A3[State Machine]
    end

    subgraph Message Bus
        B1[消息队列] --> B2[Router]
        B2 --> B3[Delivery Guarantee]
    end

    subgraph Agent B
        C1[Mailbox Inbox] --> C2[Message Handler]
        C2 --> C3[State Machine]
    end

    A3 -->|发布状态变更| B1
    B1 -->|同步| C3
    C3 -->|响应| B1
    B1 -->|回调| A3

    style Message Bus fill:#fce4ec,stroke:#e91e63
```

### 4.4 Multi-Agent Routing 架构

```mermaid
flowchart TD
    subgraph 用户层
        U[用户 / Telegram]
    end

    subgraph 协调层
        M[Main Agent<br/>领队]
    end

    subgraph 执行层
        F[Finance Agent<br/>钱串子]
        C[Coder Agent<br/>代码驴]
        AU[Auditor Agent<br/>审计狗]
        W[Writer Agent<br/>笔帖式]
        P[Planner Agent<br/>狗头军师]
    end

    U --> M
    M -->|TG @mention| F
    M -->|TG @mention| C
    M -->|TG @mention| AU
    M -->|TG @mention| W
    M -->|TG @mention| P

    F & C & AU & W & P -->|独立模型响应| U

    style 协调层 fill:#fff9c4,stroke:#fbc02d
    style 执行层 fill:#f3e5f5,stroke:#9c27b0
```

---

## 5. 综合数据流总图

```mermaid
flowchart TD
    subgraph 用户层
        U[用户消息]
    end

    subgraph Prompt 层
        PC[Prompt Constructor]
        SYS[System Prompt Builder]
    end

    subgraph LLM 层
        LLM[LLM Engine]
    end

    subgraph 工具层
        TM[Tool Matcher]
        PE[Permission Engine]
        EX[Tool Executor]
    end

    subgraph 记忆层
        GM[Graph Memory]
        ST[Session Store]
    end

    subgraph Agent 层
        MQ[Message Queue]
        MB[Mailbox]
    end

    U --> PC
    PC --> SYS
    SYS --> LLM
    LLM -->|决策| TM
    TM --> PE
    PE -->|通过| EX
    EX -->|结果| LLM
    LLM -->|输出| U

    GM -.->|召回| SYS
    ST -.->|会话上下文| SYS
    MQ -.->|Agent 通信| MB

    style 记忆层 fill:#e0f7fa,stroke:#00bcd4
    style Agent 层 fill:#e8f5e9,stroke:#4caf50
```

---

## 6. 数据流关键设计点

| 模块 | 数据类型 | 关键挑战 |
|------|---------|---------|
| Prompt Flow | 文本 Token | 上下文窗口管理、Token 预算 |
| Tool Flow | 结构化 JSON | 权限隔离、危险命令识别 |
| Memory Flow | 向量 + 图结构 | 遗忘阈值、准确召回 |
| Agent Flow | 异步消息 | 消息顺序保证、状态一致性 |
