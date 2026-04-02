# Claude Code 源码解读

**从源码深处理解 AI 编程工具的设计哲学与工程实践**

---

> 📚 **项目名**：Claude Code Deep Dive  
> 🔗 **仓库**：https://github.com/Taotie2002/claude-code-deep-dive  
> 📄 **主文件**：本文件（claude-code-deep-dive.md）  
> ⚖️ **许可**：MIT License

---

本书基于 Claude Code 泄露源码编写，经审计修订。

---

> **待发布版本说明**
> 
> 本版本在评审5稿基础上完成以下最终修复：
> - ✅ **P0修复**：代码块闭合标记 746 处全部修复（```typescript → ```）
> - ✅ **P1修复**：第0章4处技术错误修正（M-01~M-04）
> - ✅ **GitHub发布文件**：README.md + LICENSE + CONTRIBUTING.md
> - ✅ **名称同步**：更新为 claude-code-deep-dive
> 
> 修订时间：2026-04-02
> **状态：待发布**

---

# 目录

**[修订说明](#修订说明)**

**[第零部分：前置知识]**

- [第0章　前置知识](#第-0-章-前置知识)

**[第一部分：基础与架构]**

- [第一章　产品哲学与定位](#第一章-产品哲学与定位)
- [第二章　设计哲学与原则](#第二章-设计哲学与原则)
- [第三章　人机关系与Buddy设计](#第三章-人机关系与buddy设计)
- [第四章　系统架构全貌](#第四章-系统架构全貌)
- [第五章　入口设计与短路径](#第五章-入口设计与短路径)

**[第二部分：技术栈与工具系统]**

- [第六章　技术栈选型](#第六章-技术栈选型)
- [第七章　工具系统架构](#第七章-工具系统架构)
- [第八章　安全权限体系](#第八章-安全权限体系)
- [第九章　上下文管理与缓存](#第九章-上下文管理与缓存)
- [第十章　记忆系统](#第十章-记忆系统)

**[第三部分：Multi-Agent 与协作]**

- [第十一章　Multi-Agent 协同](#第十一章-multi-agent-协同)
- [第十二章　并行与UDS通信](#第十二章-并行与uds通信)
- [第十三章　KAIROS 与分布式调度](#第十三章-kairos-与分布式调度)
- [第十四章　Feature Flag 体系](#第十四章-feature-flag-体系)
- [第十五章　性能优化实践](#第十五章-性能优化实践)

**[第四部分：测试、安全与工程实践]**

- [第十六章　测试与质量保证](#第十六章-测试与质量保证)
- [第十七章　实操：从零构建 Agent 工具](#第十七章-实操从零构建-agent-工具)
- [第十八章　实操：安全设计模式](#第十八章-实操安全设计模式)
- [第十九章　成本控制策略](#第十九章-成本控制策略)
- [第二十章　多 Agent 设计模式](#第二十章-多-agent-设计模式)

**[附录]**

- [附录A　术语表](#附录-a术语表)
- [附录B　源码索引表](#附录-b源码索引表)

---

# 修订说明

本书基于泄露源码编写，经各章审计者逐行审校。以下为全文中已发现的全部内容问题汇总，供审稿时参考。

## 章节结构类

| 编号 | 章节 | 问题描述 | 建议处理 |
|------|------|---------|---------|
| S-01 | 第一章末尾 | 原文末尾注明"下一章我们将深入第三章：启动流程与核心架构"，但实际第三章标题为"人机关系与Buddy设计"，二者不符 | 已修正引用指向，保留原文内容 |
| S-02 | 第四章标题 | 第四章使用全角冒号`：`和阿拉伯数字编号节名，与其他章节"第X章　标题"格式不一致；各节使用`###` + 阿拉伯数字，与其他章节`##` + 汉字数字的结构层级不一致 | 以第四章为准，统一样式 |
| S-03 | 第四章 4.5.3 节 | 上图中"查询引擎层"标注引用`query.ts`，但根据第一章 1.5.3 节的说明，核心引擎实际为`QueryEngine.ts`（而非`query.ts`），此处路径存在不一致 | 以第一章描述为准，修正第四章图注 |
| S-04 | 第四章末尾 | 原文末尾注明"在第五章中，我们将深入 query.ts"，但实际第五章标题为"入口设计与短路径"，并不涉及 query.ts 的深入分析 | 已修正引用指向 |

## 源码位置类

| 编号 | 章节 | 问题描述 | 建议处理 |
|------|------|---------|---------|
| K-01 | 第八章 | `hasPermissionsToUseToolInner` 实际位于`src/utils/permissions/permissions.ts`（而非 src/ 根目录），行 1158；实际函数有 200+ 行，包含远比"两步"复杂的检查流程（1a deny → 1b ask → 1c tool.checkPermissions → 1d 工具结果 deny → 1e requiresUserInteraction → 沙箱自动允许 → 自动模式分类器等） | 修正源码位置，补充完整流程说明 |
| K-02 | 第十五章 | `startMdmRawRead()` 函数实际位于`src/utils/settings/mdm/rawRead.ts`**第 115-127 行**，而非第 52-60 行 | 修正行号 |
| K-03 | 第十五章 | `ensureKeychainPrefetchCompleted()` 实际只有 2 行（行 96-97），函数体仅包含`if (prefetchPromise) await prefetchPromise`，远比示意图简短 | 修正行号和描述 |
| K-04 | 第十八章 | `PATH_EXTRACTORS`**不在`bashSecurity.ts`中**，而在`src/tools/BashTool/pathValidation.ts`第 190 行 | 修正文件归属 |

## 源码内容类

| 编号 | 章节 | 问题描述 | 建议处理 |
|------|------|---------|---------|
| C-01 | 第一章 1.4.2 | `claude --agent reviewer`不是 Claude Code 的合法 CLI 标志。Claude Code 中子 agent 通过 AgentTool 在对话内部启动，而非通过命令行 `--agent` 参数 | 原文保留，添加勘误说明 |
| C-02 | 第九章 9.3.1 | `groupMessagesByApiRound`描述为"全文约 47 行"，实际展示的代码约 25 行 | 修正行数描述 |
| C-03 | 第十三章 13.3.1 | `oneShotFloorMs`默认值实际为`0`，并非"30秒地板"。当配置为默认值时，`lead`的最小值为`0`（即不提前触发） | 修正默认值描述 |
| C-04 | 第十六章 16.2.2 | `FD_SAFE_FLAGS`不存在于源码中。源码中对应位置是一组 git 相关的 flag 白名单常量（如`GIT_REF_SELECTION_FLAGS`、`GIT_STAT_FLAGS`、`GIT_LOG_DISPLAY_FLAGS`等）。上例中的`FD_SAFE_FLAGS`是`GIT_REF_SELECTION_FLAGS`的示意别名 | 以源码实际常量名为准 |
| C-05 | 第十六章 16.2.2 | `XARGS_SAFE_FLAGS`不存在于源码中。xargs 的安全实现在`validateFlags`函数内部（约第 1703 行），通过`xargsTargetCommands`参数和`SAFE_TARGET_COMMANDS_FOR_XARGS`白名单实现 | 以源码实际实现为准 |
| C-06 | 第十八章 18.1.1 | 源码中`COMMAND_SUBSTITUTION_PATTERNS`实际有**14 个**pattern，而非 5 个。遗漏的关键危险 pattern 包括：`=(`（Zsh EQUALS expansion，可绕过`Bash(curl:*)`规则）、`=$[...]`（Zsh 旧式算术扩展）、`\(e:`、`\(\+`、`\}\s*always\s*\{`（Zsh 特殊包裹）、`<#`（PowerShell 注释）等 | 以源码中实际 pattern 列表为准 |
| C-07 | 第十八章 18.4.3 | `tengu_auto_mode_decision`事件实际有**30+ 个字段**，远多于原文列出的 7 个。实际包含字段包括：`inProtectedNamespace`、`agentMsgId`、`confidence`、`fastPath`、`classifierOutputTokens`、`classifierCacheReadInputTokens`、`classifierCacheCreationInputTokens`、`sessionInputTokens`、`sessionOutputTokens`、`sessionCacheReadInputTokens`、`sessionCacheCreationInputTokens`、`classifierCostUSD`、`classifierStage`、`stage1Usage`、`stage1DurationMs`、`stage1RequestId`、`stage1MsgId`等 | 以源码实际字段列表为准 |
| C-08 | 第十八章 18.1.1 | 源码中`BASH_SECURITY_CHECK_IDS`实际有**23 个**check ID，而非 8 个。章节中仅列出了前 8 个，遗漏了第 9-23 个（包括`INPUT_REDIRECTION`、`IFS_INJECTION`、`GIT_COMMIT_SUBSTITUTION`、`ZSH_DANGEROUS_COMMANDS`等） | 以源码实际 23 个 ID 为准 |

---

**[以下为正文]**

# 第 0 章 前置知识

> **本章目标**：扫清阅读后续章节的语言障碍和工具障碍。即使你从未接触过 TypeScript 或不习惯使用命令行，本章也将带你用最短的时间建立必要的基础。

---

## 0.1 TypeScript 基础

Claude Code 的源码完全使用 **TypeScript**（strict 模式）编写。要读懂它，你需要对 TypeScript 的几个核心概念有基本了解。下面不讲语法细节——那些翻文档就能查到——我们只讲你在阅读源码时最常碰到的几样东西。

### 0.1.1 类型与接口：代码在说什么

TypeScript 的核心是**类型系统**。当你看到 `const name: string = "claude"` 时，意思是"这个变量 `name` 的类型是字符串"。

在 Claude Code 源码中出现最频繁的，是 **interface（接口）** 和 **type alias（类型别名）**：

```
// interface：描述一个对象的结构
interface User {
  id: string;
  name: string;
  age: number;
}

// type alias：给复杂类型起别名
type UserId = string;
type Callback = (result: string) => void;
```

**interface 和 type 的区别**（面试常考，但读源码时不必纠结）：

```
// 都可以描述对象
interface Config {
  debug: boolean;
}
type Config = { debug: boolean };

// interface 可以被 "扩充"（declaration merging），type 不能
// 这就是为什么很多库喜欢用 interface 定义配置对象
```

在 Claude Code 中，配置相关的类型大量使用 interface：

```
// src/Tool.ts（Claude Code 中工具接口的核心定义文件）
// Claude Code 中工具调用的返回结果都包装在 ToolResult 这样的接口里
interface ToolResult {
  success: boolean;
  output?: string;
  error?: string;
}
```

**可选属性**：`?` 表示这个字段可以有也可以没有：

```
interface GitStatus {
  branch: string;
  commit?: string;      // 可选：可能不存在
  ahead?: number;       // 可选
}
```

**联合类型**：`|` 表示"可以是其中任意一种"：

```
type PermissionMode = "default" | "auto" | "bypassPermissions" | "plan";
// 权限模式只能是这四个字符串之一
```

### 0.1.2 泛型：让代码更通用的艺术

**泛型**（Generics）是 TypeScript 最强大的特性之一。它的核心思想是：写一段代码，但把类型作为参数传入。

最常见的场景是"容器"——不管里面装什么，容器的结构不变：

```
// 不用泛型：每种类型都要写一个版本
interface StringArray { [index: number]: string; }
interface NumberArray { [index: number]: number; }

// 用泛型：一个类型参数 T 代替所有类型
interface Array<T> {
  length: number;
  [index: number]: T;
  push(item: T): number;
}

// 使用时 T 会被推断或指定
const strings: Array<string> = ["a", "b", "c"];
const nums: Array<number> = [1, 2, 3];
```

在 Claude Code 源码里，泛型随处可见。工具系统的类型定义大量使用泛型来表达"输入类型"和"输出类型"的关系：

```
// 工具系统的通用类型签名（常见位置在 src/tools/types.ts 或 src/types/ 下）
interface ToolCall<TInput, TOutput> {
  name: string;
  input: TInput;       // 输入类型，由具体工具决定
  output?: TOutput;    // 输出类型，由具体工具决定
}
```

**泛型约束**：有时候你需要限定 T 必须具有某些属性：

```
// T 必须有 id 属性
function getById<T extends { id: string }>(items: T[], id: string): T | undefined {
  return items.find(item => item.id === id);
}
```

### 0.1.3 async/await：处理异步操作

JavaScript/TypeScript 里有很多操作是"异步"的——不会立刻完成，比如读取文件、发送网络请求。**Promise** 是这种操作的封装，而 **async/await** 是读取 Promise 结果的语法糖。

```
// 传统写法：then/catch
function fetchData(callback: (data: string) => void) {
  fetch("https://api.example.com/data")
    .then(response => response.json())
    .then(data => callback(data))
    .catch(error => console.error(error));
}

// async/await 写法：看起来像同步代码
async function fetchData(): Promise<string> {
  try {
    const response = await fetch("https://api.example.com/data");
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
    return "";
  }
}
```

`async` 函数总是返回一个 **Promise**，`await` 只能在 `async` 函数内部用。

Claude Code 中几乎所有涉及文件读写、网络请求的操作都是异步的：

```
// 示例：模拟 Claude Code 中的异步文件读取
async function readFile(path: string): Promise<string> {
  const response = await fetch(`file://${path}`);
  return response.text();
}

// 多个异步操作可以并行（Promise.all）
async function loadMultipleFiles(paths: string[]): Promise<string[]> {
  return Promise.all(paths.map(p => readFile(p)));
}
```

> **小技巧**：当你看到 `async`/`await` 时，记住它们只是 Promise 的语法糖。遇到复杂异步逻辑时，可以先把 `await` 想象成"等这个操作完成再继续"。

---

## 0.2 CLI 入门：命令行基本功

### 0.2.1 什么是命令行

**命令行**（Command Line）是操作系统提供的文本输入界面。与点击图标不同，你需要输入**命令**来告诉计算机做什么。

- **macOS/Linux**：自带 Terminal 应用，内置 bash 或 zsh shell
- **Windows**：有 CMD、PowerShell，以及更现代的 Windows Terminal

在阅读 Claude Code 源码时，你会频繁看到这样的命令：

```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 在当前目录启动 Claude Code
claude

# 查找源码中的某个字符串
grep -r "toolPermission" src/
```

### 0.2.2 常用命令速查

以下是你在阅读源码和日常开发中最常用的命令：

| 命令 | 作用 | Claude Code 源码中的典型用法 |
|------|------|------|
| `ls` | 列出文件 | `ls src/` 查看源码目录结构 |
| `cd` | 切换目录 | `cd claude-code` 进入项目目录 |
| `cat` | 查看文件内容 | `cat package.json` 查看依赖 |
| `grep` | 搜索文件内容 | `grep "ToolResult" src/` |
| `find` | 查找文件 | `find . -name "*.test.ts"` |
| `npm install` | 安装依赖 | 克隆项目后必做 |
| `npm run build` | 构建项目 | 改动源码后生成可执行文件 |
| `git status` | 查看 Git 状态 | 确认当前分支和修改 |
| `curl` | 发起 HTTP 请求 | 测试 API 接口 |

**实战技巧**：

```bash
# 在 Claude Code 源码中查找所有涉及权限检查的文件
grep -r "permission" src/hooks/toolPermission/ --include="*.ts"

# 查看项目的入口文件（通常在 src/main.tsx 或 src/index.ts）
ls src/*.tsx | head -5

# 用通配符查找所有工具定义文件
find src -name "*.tool.ts" -o -name "*Tool.ts"
```

### 0.2.3 环境变量

**环境变量**（Environment Variables）是操作系统级别的全局变量，程序运行时可以读取。Claude Code 的行为大量依赖环境变量配置。

```bash
# 常见的 Claude Code 环境变量
ANTHROPIC_API_KEY=sk-xxx      # API 密钥（必需）
CLAUDE_DEVICE_ID=xxx          # 设备 ID
HTTP_PROXY=http://proxy:8080  # 代理配置
NODE_ENV=production           # 运行环境

# 查看所有环境变量（在终端输入）
env

# 在命令前临时设置（只影响这条命令）
ANTHROPIC_API_KEY=sk-xxx claude

# 在 Node.js/TypeScript 代码中读取
const apiKey = process.env.ANTHROPIC_API_KEY;
```

**项目中的环境变量**：Claude Code 使用 `~/.claude/` 配置目录管理配置，而非传统的 `.env` 文件。配置通过 `src/utils/config.ts` 等模块读取：

```bash
# Claude Code 的配置目录结构
ls ~/.claude/
# 查看全局配置
cat ~/.claude/settings.json
# 或直接 grep 搜索所有 process.env 的使用
grep -r "process\.env" src/ --include="*.ts"
```

> **提示**：Claude Code 的敏感信息（如 API 密钥）存储在 Keychain 或环境变量中，而非 `.env` 文件。

---

## 0.3 源码阅读方法

### 0.3.1 从入口开始：找到那个"main"

阅读一个陌生项目，最难的一步是**不知道从哪里开始**。诀窍是找到入口文件（Entry Point）——程序启动时第一个被执行的地方。

**Node.js/TypeScript 项目的入口**通常在以下位置之一：

- `package.json` 中的 `"main"` 或 `"bin"` 字段
- `src/main.tsx`、`src/index.ts`、`src/cli.ts`

以 Claude Code 为例，它的入口定义在 `package.json` 里：

```json
// package.json
{
  "bin": {
    "claude": "./dist/main.js"
  },
  "scripts": {
    "build": "查看实际项目中的 scripts 字段（Claude Code 使用 bun build）"
  }
}
```

找到入口后，顺着 import 语句往下读，就能理清整个程序的调用链路。

### 0.3.2 搜索与定位：快速找到关键代码

在超过 50 万行代码的项目里，漫无目的地从头读到尾是不现实的。你需要**搜索驱动**的阅读方法。

**grep：按内容搜索**

```bash
# 在所有 TypeScript 文件中搜索 "toolPermission"
grep -r "toolPermission" src/ --include="*.ts"

# 只看文件列表（不显示匹配行）
grep -rl "toolPermission" src/

# 忽略 node_modules（第三方代码）
grep -r "toolPermission" src/ --include="*.ts" | grep -v node_modules
```

**find：按文件名搜索**

```bash
# 找到所有权限相关的文件
find src -name "*permission*" -o -name "*Permission*"

# 找到所有测试文件
find . -name "*.test.ts" | head -20
```

**IDE 的代码跳转**：如果你用 VS Code，打开项目后 `Cmd+Click`（macOS）或 `Ctrl+Click`（Windows/Linux）点击任意函数/类型，可以直接跳转到定义处。这是阅读源码最省力的方式。

### 0.3.3 理解代码结构：分层 + 模式

大型 TypeScript 项目的代码虽然多，但结构通常很有规律。掌握以下两个原则可以让你快速建立心理地图：

**原则一：按功能分层**

```
src/
├── main.tsx          ← 入口
├── tools/            ← 工具定义（AI 能调用的能力）
├── hooks/            ← 业务逻辑钩子
├── context/          ← 上下文构建
└── utils/            ← 通用工具函数
```

**原则二：识别设计模式**

在 Claude Code 源码中，你会发现很多地方使用了**工具模式**（Tool Pattern）：

```
// 每个工具都是一个独立的类/模块，实现统一的接口
interface Tool {
  name: string;           // 工具名称
  description: string;    // 描述（给 AI 看）
  execute(input: unknown): Promise<ToolResult>;  // 执行逻辑
}

// FileReadTool 就是 Tool 接口的一个实现
class FileReadTool implements Tool {
  name = "FileRead";
  description = "Read the contents of a file";
  async execute(input: { path: string }): Promise<ToolResult> {
    const content = await fs.readFile(input.path, "utf-8");
    return { success: true, output: content };
  }
}
```

一旦你识别出这种模式，阅读 `src/tools/` 目录下的几十个工具就不难了——每个都是同一套模板的不同实现。

### 0.3.4 善用类型定义：从类型猜意图

TypeScript 的类型定义本身就是最好的文档。当你不知道一个函数做什么时，先看它的**输入类型**和**输出类型**：

```
// 从类型签名猜功能
async function createTask(input: TaskInput): Promise<Task>
function parseConfig(raw: unknown): Config
//     ↑ 输入是 unknown（未知的原始值）   ↑ 返回确定类型
//     说明这个函数在做"验证 + 转换"
```

---

## 练习题

### 练习 1：TypeScript 类型推断（简单）

下面这段代码运行后，`result` 的值是多少？

```
type Status = "pending" | "done" | "failed";

function getStatus(code: number): Status {
  const map: Record<number, Status> = {
    0: "pending",
    1: "done",
    2: "failed",
  };
  return map[code];
}

const result = getStatus(1);
```

<details>
<summary>答案</summary>

`result` 的值是 `"done"`。`Record<number, Status>` 创建了一个键为数字、值为 Status 类型联合值的对象，`map[1]` 返回 `"done"`。

</details>

---

### 练习 2：async/await（简单）

以下代码的输出顺序是什么？

```
async function main() {
  console.log("1");
  await new Promise(r => setTimeout(r, 0));
  console.log("2");
  console.log("3");
}
main();
console.log("4");
```

<details>
<summary>答案</summary>

输出顺序是：`1` → `4` → `2` → `3`。

原因：`main()` 是异步的（虽然不等待它），`console.log("1")` 立即执行，然后 `await setTimeout` 把后续代码放入微任务队列，继续执行 `console.log("4")`，等主线程空闲后再执行队列中的 `2` 和 `3`。

</details>

---

### 练习 3：源码定位（实践）

在 Claude Code 源码中，找到以下内容的实际文件位置：

1. `package.json` 中的入口文件路径（bin 字段）
2. 权限检查相关的文件（搜索 "permission"）
3. 工具系统的类型定义文件（搜索 "interface Tool"）

```bash
# 提示：先 cd 到 Claude Code 源码目录，然后执行以下命令
cat package.json | grep -A5 '"bin"'
grep -r "permission" src/ --include="*.ts" -l | head -10
grep -r "interface Tool" src/ --include="*.ts"
```

---

### 练习 4：环境变量实战（实践）

在 Claude Code 中，如果想让它在 DEBUG 模式下运行（打印详细日志），应该设置哪个环境变量？请在源码中搜索相关线索。

```bash
# 提示：Claude Code 源码中通常用 debug 或 log 相关的环境变量名
grep -r "DEBUG\|debug\|LOG\|log" src/ --include="*.ts" | grep "process\.env" | head -10
```

---

## 本章小结

| 知识点 | 核心要义 | 源码位置参考 |
|--------|--------|------------|
| 类型与接口 | 描述数据的结构，是代码的"骨架" | `src/types.ts` |
| 泛型 | 类型作为参数，写一次代码适用多种类型 | `src/tools/types.ts` |
| async/await | 处理异步操作，代码看起来像同步 | 任何涉及 `fs`、`fetch` 的文件 |
| 命令行基础 | `ls`/`grep`/`find` 是源码阅读的三板斧 | 全项目通用 |
| 环境变量 | 控制程序运行时的行为，`process.env` 读取 | `src/main.tsx` |
| 源码入口 | 从 `package.json` 的 bin 字段开始，顺藤摸瓜 | `package.json` |
| 搜索定位 | `grep` + `find` + IDE 跳转，拒绝从头读到尾 | 全项目通用 |
| 类型驱动阅读 | 先看输入输出类型，类型签名即文档 | `src/types/` |

---

> **进入下一章**：现在你已经掌握了必要的语言工具和阅读方法。在接下来的章节中，我们将正式开始阅读 Claude Code 的源码——从产品哲学到工具系统，从权限模型到多 Agent 协作。准备好了吗？

# 第一章 产品哲学与定位

## 1.1 Claude Code 是什么

Claude Code 是 Anthropic 官方推出的命令行界面（CLI）工具，旨在让开发者能够在终端环境中直接与 Claude 大模型交互，完成软件工程任务——包括编辑文件、运行命令、搜索代码库、协调工作流等。根据源码中的描述，Claude Code 被定位为 Anthropic 对专业开发者提供的一站式 AI 编程伴侣。

从源码的入口文件 `main.tsx` 中可以清晰地看到 Claude Code 的技术选型。该项目使用 **Bun** 作为运行时（而非 Node.js），语言为 **TypeScript（strict 模式）**，终端 UI 则采用 **React + Ink**（一个让 React 组件能在终端渲染的框架）。CLI 参数解析使用 **Commander.js**，配置验证依赖 **Zod v4**。

```
// src/main.tsx，第 1-9 行
// These side-effects must run before all other imports
import { profileCheckpoint, profileReport } from './utils/startupProfiler.js';
import { Command as CommanderCommand, InvalidArgumentError, Option } from '@commander-js/extra-typings';
import chalk from 'chalk';
import React from 'react';
import { init, initializeTelemetryAfterTrust } from './entrypoints/init.js';
```

项目规模在源码注释中有明确记载：约 **1,900 个文件**，超过 **512,000 行代码**。这是一个相当庞大的工程化项目，远非简单的命令行包装器。

---

## 1.2 解决什么问题

Claude Code 的诞生回应了 AI 辅助编程领域的一个核心矛盾：**通用 AI 助手（如 ChatGPT 网页版）缺乏对开发者工作环境的深度理解，而传统 IDE 插件又受限于功能单一、集成复杂的问题。**

Claude Code 从以下四个维度解决了这一矛盾：

### 1.2.1 深度终端集成

Claude Code 不打开浏览器窗口，不占用 GUI 空间——它就在开发者已经在使用的终端里运行。通过 `src/main.tsx` 中的 Commander.js 命令行解析，用户可以以极低的心智负担启动会话：

```bash
# 交互模式（默认）
claude

# 非交互模式（适合脚本）
claude -p "解释这个函数的逻辑"

# 继续上一次的对话
claude --continue

# 使用特定模型
claude --model sonnet
```

### 1.2.2 工具系统（Tool System）

Claude Code 的核心竞争力在于它为 Claude 提供了一套完整的**工具集**（约 130 个工具），让 AI 能够实际操作系统中的文件和进程，而不仅仅是"给出建议"。从 `src/tools/` 目录的结构可以看出主要工具：

| 工具类 | 功能说明 |
|--------|----------|
| `BashTool` | 执行 Shell 命令 |
| `FileReadTool` | 读取文件（含图片、PDF、Jupyter notebook） |
| `FileEditTool` | 部分修改文件（字符串替换） |
| `FileWriteTool` | 创建或覆盖文件 |
| `GlobTool` / `GrepTool` | 文件模式搜索与内容搜索（基于 ripgrep） |
| `WebFetchTool` / `WebSearchTool` | 网页获取与搜索 |
| `AgentTool` | 启动子 Agent（多 Agent 协作） |
| `TaskCreateTool` / `TaskUpdateTool` | 任务创建与管理 |
| `EnterPlanModeTool` / `ExitPlanModeTool` | 计划模式切换 |
| `EnterWorktreeTool` / `ExitWorktreeTool` | Git worktree 隔离 |
| `SkillTool` | Skill 执行（可复用工作流） |
| `MCPTool` | MCP（Model Context Protocol）服务器工具调用 |
| `LSPTool` | 语言服务器协议集成 |

### 1.2.3 权限安全模型

Claude Code 实现了细粒度的**权限控制系统**（`src/hooks/toolPermission/`）。每次工具调用都会经过权限检查，根据配置的权限模式（`default`、`plan`、`bypassPermissions`、`auto` 等）决定是提示用户确认还是自动放行或拒绝。这解决了 AI 编程工具最敏感的问题：**AI 到底能在我的系统上做什么？**

### 1.2.4 上下文感知

Claude Code 通过 `src/context.ts` 构建系统上下文，通过 `src/context/` 子目录管理统计信息和上下文指标。它能感知当前 Git 仓库状态、分支信息、worktree 数量等工程环境信息，使 AI 的回答更贴合实际项目状态。

---

## 1.3 产品定位

### 1.3.1 Anthropic 产品线中的位置

Anthropic 的产品线可以粗略分为三层：

1. **面向消费者的 Chat 产品**：Claude.ai 网页版和移动应用，面向普通用户，强调多模态对话和创意写作。
2. **面向企业的 API 平台**：Claude API，通过 REST 接口供企业开发者集成，强调模型能力和安全性。
3. **面向开发者的工作台**：Claude Code 和 Claude in Chrome（浏览器插件），面向**需要用 AI 辅助实际编程**的开发者，强调深度集成和工程化能力。

Claude Code 的系统提示（system prompt）前缀定义在 `src/constants/system.ts` 中，明确区分了三种身份：

```
// src/constants/system.ts，第 9-11 行
const DEFAULT_PREFIX = `You are Claude Code, Anthropic's official CLI for Claude.`
const AGENT_SDK_CLAUDE_CODE_PRESET_PREFIX = `You are Claude Code, Anthropic's official CLI for Claude, running within the Claude Agent SDK.`
const AGENT_SDK_PREFIX = `You are a Claude agent, built on Anthropic's Claude Agent SDK.`
```

这一设计说明 Claude Code 的定位是 **"Anthropic 官方 CLI"**——它不是第三方封装，而是官方出品的编程工具，与 API 产品线形成上下覆盖关系：API 提供底层能力，Claude Code 提供面向开发者的最优使用体验。

### 1.3.2 与其他 AI 编程工具的差异

| 维度 | Claude Code | GitHub Copilot | Cursor |
|------|-------------|----------------|--------|
| 交互形态 | CLI 终端 | IDE 插件 | GUI 应用 |
| 工具能力 | 130 个工具，可执行命令 | 代码补全/生成 | 代码补全/生成+聊天 |
| 多 Agent | 支持（AgentTool + coordinator） | 不支持 | 支持（部分） |
| MCP 集成 | 原生支持 | 不支持 | 部分支持 |
| 上下文范围 | 全代码库+Shell+网络 | 当前文件 | 当前文件/项目 |
| Skill 系统 | 支持自定义工作流 | 不支持 | 不支持 |

从技术架构角度看，Claude Code 的一个显著特点是**基于 Bun 运行时和 React/Ink 的终端 UI**。这使得它既享有 JavaScript 生态的丰富库支持，又能在无 GUI 环境下运行复杂的交互界面（包括进度条、表格、颜色输出）。

---

## 1.4 核心用户与场景

### 1.4.1 核心用户画像

从源码的使用模式和功能设计来看，Claude Code 的目标用户主要包括：

1. **专业软件工程师**：需要处理复杂代码库、完成重构、调试、代码审查等工作，希望 AI 能够"动手做事"而非"只出主意"。
2. **DevOps/基础设施工程师**：需要通过终端操作服务器、编写脚本、管理部署流程。
3. **全栈开发者**：在前后端之间切换，需要快速理解和修改不同技术栈的代码。
4. **AI 研究者/ Agent 开发者**：利用 Claude Code 的 Agent Tool 和 MCP 集成构建多智能体系统。

### 1.4.2 典型使用场景

**场景一：日常编码辅助**

```bash
# 在项目目录中直接启动
cd ~/my-project
claude

# 询问代码库中的特定逻辑
> 这个 auth 模块的 token 刷新流程是怎样的？

# 让 AI 直接修改代码
> 把 UserService.ts 中的错误处理改成使用自定义异常类
```

**场景二：代码审查**

```bash
claude
> /review  # 使用 slash command 触发代码审查
```

**场景三：多 Agent 协作**

```bash
# [勘误: claude --agent reviewer 不是 Claude Code 的合法 CLI 标志。
# Claude Code 中子 agent 是通过 AgentTool 在对话内部启动的，
# 而非通过命令行 --agent 参数。此处示例可能来源有误或为设想中的功能。]
claude --agent reviewer
> 审查 src/utils/api.ts 中的所有函数
```

**场景四：非交互式脚本**

```bash
# 在 CI/CD 流水线中使用
claude -p --model sonnet "为这个 Python 文件添加类型注解" < input.py > output.py
```

### 1.4.3 设计哲学：渐进式信任

Claude Code 的权限系统体现了**渐进式信任**的设计哲学：

- **首次使用**：显示信任对话框，明确告知 AI 将能访问哪些系统资源
- **交互过程中**：每次涉及危险操作（删除文件、执行 Shell 命令）都需要用户确认
- **可配置模式**：用户可以通过 `--permission-mode` 选择不同的信任级别（`auto` 模式可自动放行安全操作）

---

## 1.5 源码结构概览

### 1.5.1 顶层目录组织

`src/` 目录下的 40+ 个子目录并非随意堆砌，而是遵循清晰的**职责分层**：

```
src/
├── main.tsx              # 🔵 CLI 入口（Commander.js 解析 + Ink 渲染初始化）
├── tools.ts / Tool.ts   # 🔴 工具注册与类型定义
├── commands.ts           # 🟡 Slash 命令注册
├── QueryEngine.ts       # 🔴 LLM 查询引擎（~1.3K 行，核心！）
│
├── tools/               # 🔴 工具实现（~40 个工具模块）
├── commands/            # 🟡 Slash 命令实现（~50 个命令）
├── components/          # 🟢 Ink UI 组件（~140 个组件）
├── hooks/               # 🟢 React Hooks
├── screens/             # 🟢 全屏 UI（Doctor、REPL、Resume）
│
├── services/            # 🔵 服务层（API、MCP、OAuth、LSP、Analytics）
├── bridge/              # 🔵 IDE 桥接（VS Code、JetBrains）
├── coordinator/          # 🔵 多 Agent 协调器
├── plugins/             # 🔵 插件系统
├── skills/              # 🔵 Skill 系统
│
├── types/               # 🟠 TypeScript 类型定义
├── utils/               # 🟠 工具函数
├── state/               # 🟠 状态管理
├── schemas/             # 🟠 Zod 配置模式
├── migrations/          # 🟠 配置迁移
├── entrypoints/         # 🟠 初始化逻辑
│
├── ink/                 # 🟣 Ink 渲染器封装
├── native-ts/           # 🟣 原生 TypeScript 工具
├── upstreamproxy/       # 🟣 上游代理配置
└── [其他专业模块]
```

> 图例：🔵 基础设施层 | 🟡 命令解析层 | 🔴 核心能力层 | 🟢 UI 层 | 🟠 类型/工具层 | 🟣 运行时底层

### 1.5.2 入口文件 main.tsx 的启动流程

`main.tsx` 是理解 Claude Code 架构的最佳起点。它展示了整个应用的初始化时序：

**第一步：并行预取（Side-Effect Imports）**

```
// src/main.tsx，第 12-20 行
// 这些副作用必须在所有其他 import 之前运行：
// 1. profileCheckpoint 标记入口时间点
// 2. startMdmRawRead 启动 MDM 子进程（macOS 配置管理）
// 3. startKeychainPrefetch 预取 Keychain（OAuth + API 密钥）
import { profileCheckpoint, profileReport } from './utils/startupProfiler.js';
import { startMdmRawRead } from './utils/settings/mdm/rawRead.js';
import { startKeychainPrefetch } from './utils/secureStorage/keychainPrefetch.js';

startMdmRawRead();
startKeychainPrefetch();
```

**设计原因**：MDM（Mobile Device Management，用于企业配置管理）和 Keychain 读取是 macOS 上的慢操作。如果串行执行，每次启动 Claude Code 都会增加约 65ms 的等待时间。通过并行预取，这些 I/O 操作与后续约 135ms 的模块加载重叠，总启动时间不变，但感知速度更快。

**第二步：Dead Code Elimination（条件编译）**

```
// src/main.tsx，第 76 行
// 通过 Bun 的 feature() 实现 dead code elimination
// 未启用的功能代码在构建时完全被剔除
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js')
  : null;
```

Claude Code 使用 `feature('FEATURE_NAME')` 模式控制大量可选功能的代码编译，包括 `PROACTIVE`、`KAIROS`、`BRIDGE_MODE`、`DAEMON`、`VOICE_MODE`、`AGENT_TRIGGERS`、`MONITOR_TOOL` 等。这使得同一套代码基础可以构建出面向不同用户群体的二进制产物。

**第三步：主函数与 CLI 解析**

```
// src/main.tsx，第 585 行起
export async function main() {
  // SECURITY: 防止 Windows 执行当前目录中的命令（PATH 劫持防御）
  process.env.NoDefaultCurrentDirectoryInExePath = '1';
  
  // ... CLI 参数解析 ...
  
  await run();
}
```

**设计原因**：`NoDefaultCurrentDirectoryInExePath` 是 Claude Code 在 Windows 平台上的关键安全加固。Windows 的 `SearchPathW` 默认会搜索当前目录，攻击者可借此在项目目录中植入恶意可执行文件（如 `git.exe`）进行 PATH 劫持攻击。这一环境变量将当前目录从搜索路径中移除，与 `PATH` 环境变量配合实现安全的命令查找顺序。

### 1.5.3 核心引擎：QueryEngine.ts

`src/QueryEngine.ts` 是 Claude Code 的大脑，约 1,295 行代码，负责：

- 与 Anthropic API 的流式通信
- 工具调用循环（tool-call loop）
- 思考模式（thinking mode）处理
- 重试逻辑和令牌计数
- 上下文管理和压缩

理解 QueryEngine 的工具调用循环是理解 Claude Code 工作原理的关键：当模型判断需要执行操作（如读取文件或运行命令）时，会返回一个工具调用请求，QueryEngine 负责执行该工具并将结果注入下一轮对话，直到模型认为任务完成。

### 1.5.4 服务层（Services）

`src/services/` 目录包含 Claude Code 与外部系统交互的所有服务：

| 服务 | 说明 |
|------|------|
| `api/` | Anthropic API 客户端、文件 API、bootstrap |
| `mcp/` | Model Context Protocol 服务器连接与管理 |
| `oauth/` | OAuth 2.0 认证流程 |
| `lsp/` | 语言服务器协议管理器 |
| `analytics/` | GrowthBook 特性开关和遥测 |
| `compact/` | 对话上下文压缩 |

### 1.5.5 桥接系统（Bridge）

`src/bridge/` 实现了一个双向通信层，连接 Claude Code CLI 与 IDE 扩展（VS Code、JetBrains）。通过 `bridgeMessaging.ts` 定义的消息协议，双方可以互相传递指令和状态，实现 IDE 内无缝的 AI 编程体验。

---

## 本章小结

本章从产品定位和使用场景出发，介绍了 Claude Code 作为 Anthropic 官方 CLI 工具的核心定位：

1. **是什么**：基于 Bun + TypeScript + React/Ink 的命令行 AI 编程工具，通过 130 个工具让 Claude 能够实际操作系统中的文件和进程。
2. **解决什么问题**：弥合通用 AI 助手与专业开发者工作流之间的鸿沟，提供深度终端集成、完整工具集、细粒度权限控制和上下文感知。
3. **产品定位**：Anthropic 产品线中面向开发者的核心工具，与 API 平台形成上下覆盖关系，定位为"官方编程伴侣"。
4. **核心用户**：专业软件工程师、DevOps 工程师、全栈开发者，以及利用多 Agent 能力构建自动化系统的 Agent 开发者。
5. **源码结构**：遵循清晰的职责分层——基础设施层（main.tsx）、核心能力层（QueryEngine、tools）、UI 层（components、screens）、服务层（services）。

---

# 第二章　设计哲学与原则

> **本章作者：** 笔帖式
> **本章审计：** 审计狗

任何一门成熟的软件工程实践，都必然沉淀出一套内在的设计哲学。它不是写在文档里的口号，而是编码者在无数次权衡中反复做出的选择。Claude Code 的源码正是这样一部活着的教科书——每一个 `if` 分支、每一行延迟加载、每一次早于主逻辑执行的检查，都是一处设计决策的标本。本章将从五个核心维度，系统解析 Claude Code 背后的设计哲学与工程原则，并配以源码中的具体段落作为佐证。

---

## 2.1　核心设计原则概览

在展开细节之前，我们先将 Claude Code 的核心设计原则归纳为一张总览表，随后各节逐一深入。

| 原则 | 核心主张 | 在 Claude Code 中的体现 |
|------|----------|------------------------|
| **简洁优于复杂** | 用最少的代码解决已知问题 | 条件导入按需加载、内联校验拒绝冗余抽象 |
| **编译时优于运行时** | 将尽可能多的工作提前到程序启动前 | Feature Flag 树摇、CLI 参数尽早解析、MDM 配置预读 |
| **可组合性** | 小而专一的模块可被自由拼装 | 工具集按权限过滤、MCP 客户端按需连接、Hook 系统松耦合 |
| **可观测性** | 系统的每一步都有迹可循 | `profileCheckpoint` 打点、`logForDebugging` 分级日志、诊断事件上报 |
| **安全第一** | 信任必须显式建立，危险操作必须被显式授权 | 信任对话框、`NoDefaultCurrentDirectoryInExePath`、沙箱策略 |

以下各节将围绕每一项原则，配合源码中的具体文件与行号，演示这些原则是如何在日常编码决策中落地的。

---

## 2.2　简洁优于复杂

### 2.2.1　设计主张

> **"The simplest solution is usually the right one, until it isn't."**

所谓"简洁优于复杂"，并不是在倡导写最少的字符——而是说，当两个方案都能解决同一问题时，应当选择心智模型更薄、参与方更少、后续维护者更易理解的那一个。Claude Code 在以下几个层面贯彻了这一原则：

### 2.2.2　Feature Flag 驱动的树摇（Tree Shaking）

在 `main.tsx` 的模块顶层，条件导入通过 `feature()` 函数控制：

```
// src/main.tsx:78-85
/* eslint-disable @typescript-eslint/no-require-imports */
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js') as typeof import('./coordinator/coordinatorMode.js')
  : null;
/* eslint-enable @typescript-eslint/no-require-imports */

// src/main.tsx:87-91
/* eslint-disable @typescript-eslint/no-require-imports */
const assistantModule = feature('KAIROS')
  ? require('./assistant/index.js') as typeof import('./assistant/index.js')
  : null;
const kairosGate = feature('KAIROS')
  ? require('./assistant/gate.js') as typeof import('./assistant/gate.js')
  : null;
```

这里没有运行时反射、没有插件注册表、没有"特性槽位"抽象。`feature()` 来自 `bun:bundle`，是一个编译期就确定结果的函数。如果某个特性未启用，bundler 在构建阶段就会把对应分支的代码彻底剔除，产物中不留任何死代码。这正是"简洁"的最直接体现：**不需要额外的配置系统，不需要运行时检查库，bundler 就是你的特性开关**。

### 2.2.3　按需校验，拒绝抽象层层包裹

再看 `main.tsx` 中对 `--settings` 参数的处理（第 432–488 行）：

```
// src/main.tsx:432-488
function loadSettingsFromFlag(settingsFile: string): void {
  try {
    const trimmedSettings = settingsFile.trim();
    const looksLikeJson = trimmedSettings.startsWith('{') && trimmedSettings.endsWith('}');
    let settingsPath: string;
    if (looksLikeJson) {
      // 直接内联解析，不走额外的 Validator 类
      const parsedJson = safeParseJSON(trimmedSettings);
      if (!parsedJson) {
        process.stderr.write(chalk.red('Error: Invalid JSON provided to --settings\n'));
        process.exit(1);
      }
      // 使用 content-hash-based 路径避免 busting API prompt cache
      settingsPath = generateTempFilePath('claude-settings', '.json', {
        contentHash: trimmedSettings
      });
      writeFileSync_DEPRECATED(settingsPath, trimmedSettings, 'utf8');
    } else {
      // 直接读取文件，错误直接映射到用户可见信息
      const { resolvedPath: resolvedSettingsPath } = safeResolvePath(...);
      try {
        readFileSync(resolvedSettingsPath, 'utf8');
      } catch (e) {
        if (isENOENT(e)) {
          process.stderr.write(chalk.red(`Error: Settings file not found: ${resolvedSettingsPath}\n`));
          process.exit(1);
        }
        throw e;
      }
      settingsPath = resolvedSettingsPath;
    }
    setFlagSettingsPath(settingsPath);
    resetSettingsCache();
  } catch (error) {
    // ... 直接输出，零额外抽象
  }
}
```

没有引入 `SettingsLoader` 或 `IConfigProvider` 接口，逻辑在一个函数里从头走到尾。错误码直接映射为用户友好的提示。这段代码的维护者只需要理解一个函数的输入输出，而不需要在五个类之间跳来跳去。

### 2.2.4　实操示例：如何利用简洁原则判断调试模式

调试模式的判断逻辑浓缩在一个纯函数里（`src/utils/debug.ts`）：

```
// src/utils/debug.ts
export const isDebugMode = memoize((): boolean => {
  return (
    runtimeDebugEnabled ||
    isEnvTruthy(process.env.DEBUG) ||
    isEnvTruthy(process.env.DEBUG_SDK) ||
    process.argv.includes('--debug') ||
    process.argv.includes('-d') ||
    isDebugToStdErr() ||
    process.argv.some(arg => arg.startsWith('--debug=')) ||
    getDebugFilePath() !== null
  )
});
```

这行代码没有用任何设计模式，但它的可读性极强：**调试模式的条件全部并列呈现，任何人阅读此处都能立刻推断出全部激活路径**。这正是"简洁"原则在真实代码中的样子。

---

## 2.3　编译时优于运行时

### 2.3.1　设计主张

> **"Work that can be done before the program starts should never be done while it runs."**

"编译时优于运行时"的核心论点是：程序启动后的每一毫秒都在等待用户，而用户的等待是有成本的。因此，把能提前做的工作全部提前，是提升感知性能最有效的手段。Claude Code 从三个维度践行这一原则。

### 2.3.2　提前（Eager）解析 CLI 参数

`eagerLoadSettings()` 在 `run()` 被调用之前就完成了 `--settings` 和 `--setting-sources` 的解析：

```
// src/main.tsx:502-518
function eagerLoadSettings(): void {
  profileCheckpoint('eagerLoadSettings_start');
  // Parse --settings flag early to ensure settings are loaded before init()
  const settingsFile = eagerParseCliFlag('--settings');
  if (settingsFile) {
    loadSettingsFromFlag(settingsFile);
  }

  // Parse --setting-sources flag early to control which sources are loaded
  const settingSourcesArg = eagerParseCliFlag('--setting-sources');
  if (settingSourcesArg !== undefined) {
    loadSettingSourcesFromFlag(settingSourcesArg);
  }
  profileCheckpoint('eagerLoadSettings_end');
}
```

这意味着，当 `init()` 第一次被调用时，所有配置过滤规则已经就位。如果把这段逻辑延迟到 `init()` 内部，就会在每次初始化时多出一次字符串解析的代价。**提前解析，就是把固定成本从热路径转移到冷路径**。

### 2.3.3　并行预读：MDM 与 Keychain

`main.tsx` 文件顶部的副作用区（第 1–20 行注释与对应导入）展示了另一种"编译时优于运行时"的策略：

```
// src/main.tsx:1-20 注释原文
// These side-effects must run before all other imports:
// 1. profileCheckpoint marks entry before heavy module evaluation begins
// 2. startMdmRawRead fires MDM subprocesses (plutil/reg query) so they run in
//    parallel with the remaining ~135ms of imports below
// 3. startKeychainPrefetch fires both macOS keychain reads (OAuth + legacy API
//    key) in parallel — isRemoteManagedSettingsEligible() otherwise reads them
//    sequentially via sync spawn inside applySafeConfigEnvironmentVariables()
//    (~65ms on every macOS startup)
import { profileCheckpoint, profileReport } from './utils/startupProfiler.js';
/* eslint-disable-next-line custom-rules/no-top-level-side-effects */
profileCheckpoint('main_tsx_entry');
import { startMdmRawRead } from './utils/settings/mdm/rawRead.js';
/* eslint-disable-next-line custom-rules/no-top-level-side-effects */
startMdmRawRead();
import { ensureKeychainPrefetchCompleted, startKeychainPrefetch } from './utils/secureStorage/keychainPrefetch.js';
/* eslint-disable-next-line custom-rules/no-top-level-side-effects */
startKeychainPrefetch();
```

这里的设计意图被注释完整记录：**三个 I/O 操作（profile 打点、MDM 读取、Keychain 读取）全部并行化，利用模块加载的 ~135ms 空窗期完成**。如果不提前预读，这些操作将在 `init()` 阶段串行执行，每次 macOS 启动都会多付出 ~65ms 的等待。

### 2.3.4　Debug 日志的分级设计

日志系统也遵循"编译时优于运行时"的思路。在 `debug.ts` 中，最小日志级别由环境变量在模块首次调用时确定并缓存：

```
// src/utils/debug.ts
export const getMinDebugLogLevel = memoize((): DebugLogLevel => {
  const raw = process.env.CLAUDE_CODE_DEBUG_LOG_LEVEL?.toLowerCase().trim();
  if (raw && Object.hasOwn(LEVEL_ORDER, raw)) {
    return raw as DebugLogLevel;
  }
  return 'debug';  // 默认值，编译时即确定
});
```

注意 `memoize()` 的使用：值一旦确定，后续所有 `logForDebugging` 调用都不会再做任何字符串比较或环境变量查询。**日志级别的判断，是零运行时成本的**。

---

## 2.4　可组合性原则

### 2.4.1　设计主张

> **"Build small things that do one thing well; compose them into larger things."**

可组合性（Composability）是系统能否随需求增长而扩展的关键。Claude Code 通过以下机制保证了高度的可组合性。

### 2.4.2　工具集的权限过滤链

工具的可用性并非一张静态列表，而是一条由多个策略节点组成的过滤链。在 `main.tsx` 的 action handler 中，我们看到工具权限上下文的初始化过程（第 1747–1753 行）：

```
// src/main.tsx:1747-1753
const initResult = await initializeToolPermissionContext({
  allowedToolsCli: allowedTools,
  disallowedToolsCli: disallowedTools,
  baseToolsCli: baseTools,
  permissionMode,
  allowDangerouslySkipPermissions,
  addDirs: addDir
});
let toolPermissionContext = initResult.toolPermissionContext;
```

`initializeToolPermissionContext` 返回的 `toolPermissionContext` 是一份描述当前会话所有工具权限规则的**结构化对象**。随后，`getTools(toolPermissionContext)` 根据这份规则动态生成工具集。

这种设计的可组合性体现在：

1. **规则与执行分离**——定义权限规则不需要知道工具有多少种；
2. **多层叠加**——CLI 参数、配置文件、企业策略可以按优先级叠加；
3. **可序列化**——`toolPermissionContext` 可以被存储、传输或审计。

### 2.4.3　MCP 客户端的懒连接

MCP（Model Context Protocol）服务器的连接采用懒加载策略——在 `main.tsx` 第 2408–2412 行：

```
// src/main.tsx:2408-2412
const localMcpPromise = isNonInteractiveSession
  ? Promise.resolve({ clients: [], tools: [], commands: [] })
  : prefetchAllMcpResources(regularMcpConfigs);
```

关键在于：`prefetchAllMcpResources` 是一个异步调用，它**不阻塞 REPL 的首次渲染**。MCP 工具在后台陆续连接，已连接的工具立刻对当次对话生效，尚未连接完成的服务器会在下一轮对话中出现。这正是一种**渐进式组合**——系统不必等待所有组件就绪，而是边运行边组装。

### 2.4.4　Hook 系统的无侵入扩展

Claude Code 的 Hook 系统（`processSessionStartHooks`、`processSetupHooks`）允许外部脚本在会话生命周期中的特定时刻插入逻辑，但这些 Hook 对核心逻辑是完全透明的：

```
// src/main.tsx:2437
const hooksPromise = initOnly || init || maintenance || isNonInteractiveSession || options.continue || options.resume
  ? null
  : processSessionStartHooks('startup', {
      agentType: mainThreadAgentDefinition?.agentType,
      model: resolvedInitialModel
    });
```

如果 `hooksPromise` 为 `null`，主逻辑继续执行，Hook 永远不会成为一条阻断路径。**扩展能力与核心逻辑的分离，是可组合性的终极体现。**

---

## 2.5　可观测性原则

### 2.5.1　设计主张

> **"You cannot fix what you cannot see."**

一个无法观测的系统，无论内部设计多么优雅，都等同于一个黑盒。Claude Code 构建了多层次的可观测性基础设施。

### 2.5.2　Startup Profile：精准的性能剖析

`startupProfiler` 在 `main.tsx` 中设置了多个打点标记，每个标记记录了程序从启动到该点所经过的阶段：

```
// src/main.tsx:1-20
import { profileCheckpoint, profileReport } from './utils/startupProfiler.js';
/* eslint-disable-next-line custom-rules/no-top-level-side-effects */
profileCheckpoint('main_tsx_entry');
```

以及在 `main()` 函数中多处使用：

```
// src/main.tsx:585
export async function main() {
  profileCheckpoint('main_function_start');
  // ...
  profileCheckpoint('main_before_run');
  await run();
  profileCheckpoint('main_after_run');
}
```

`profileCheckpoint` 的精妙之处在于它的命名约定：传入的字符串标签描述了**语义位置**（如 `'main_tsx_entry'`、`'main_before_run'`），而不是"第几行"或"函数名"。这使得性能报告可以直接翻译为产品语言：**"模块导入阶段耗时 Xms"、"CLI 参数解析阶段耗时 Yms"**。

### 2.5.3　分级 Debug 日志

`logForDebugging` 函数（`src/utils/debug.ts`）实现了分级日志：

```
// src/utils/debug.ts
export type DebugLogLevel = 'verbose' | 'debug' | 'info' | 'warn' | 'error';

export function logForDebugging(
  message: string,
  { level }: { level: DebugLogLevel } = { level: 'debug' },
): void {
  if (LEVEL_ORDER[level] < LEVEL_ORDER[getMinDebugLogLevel()]) {
    return;  // 低于阈值的消息直接丢弃，零性能损耗
  }
  if (!shouldLogDebugMessage(message)) {
    return;
  }
  // ...
}
```

`shouldLogDebugMessage` 内部还调用了 `getDebugFilter`，后者从 `--debug=pattern` 参数中解析出一个过滤器。如果设置了 `--debug=api`，则所有非 API 相关的调试消息都不会被生成——**不仅不打印，连构造消息字符串的成本都省了**。这在高频调用的路径上（例如每个 Tool 调用的出入站记录）尤为重要。

### 2.5.4　Debug 文件的"即时模式"

在 `debug.ts` 中，`BufferedWriter` 根据是否处于调试模式选择不同的写入策略：

```
// src/utils/debug.ts
getDebugWriter().write(output);
```

而在 `BufferedWriter` 的实现中：

```
// 非调试模式：批量写入（~1 秒刷新一次）
// 调试模式（--debug）：同步写入，保证进程异常退出时日志不丢失
immediateMode: isDebugMode(),
```

这一细节揭示了可观测性设计的一个深层原则：**观测行为本身不应成为被观测系统的干扰源**。在非调试模式下，日志写入是异步缓冲的，不会阻塞主线程；在调试模式下，日志以同步方式落盘，确保最关键的诊断信息不会因进程崩溃而丢失。

### 2.5.5　实操示例：开启完整的可观测性

作为使用者，如果希望对 Claude Code 的内部行为进行完整观测，只需一条命令：

```bash
claude --debug --debug-file=./session-debug.log
```

这条命令的效果是：

1. `isDebugMode()` 返回 `true`，所有层级的 `logForDebugging` 消息开始输出；
2. `getDebugFilePath()` 返回 `./session-debug.log`，日志写入指定文件；
3. `immediateMode: true`，所有日志同步落盘；
4. `getMinDebugLogLevel()` 默认返回 `'debug'`，如果需要 `verbose` 级别，则额外设置 `CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose`。

---

## 2.6　本章小结与设计权衡

### 2.6.1　五项原则的交叉影响

在实际工程中，这五项原则并非孤立存在，它们相互支撑、相互约束：

- **简洁** 降低了可组合性的实现成本——接口越薄，组合越容易；
- **编译时优于运行时** 依赖可观测性来验证效果——没有 `profileCheckpoint`，提前的工作量无法被度量；
- **可观测性** 本身也是可组合的——`logForDebugging` 接受一个分级参数，不同组件可以按需选择不同详细程度。

### 2.6.2　常见的权衡场景

| 场景 | 倾向的原则 | 权衡结果 |
|------|-----------|---------|
| 添加新特性 | 简洁 → 避免新抽象 | 采用 `feature()` 条件导入，零新增接口 |
| 性能调优 | 编译时优于运行时 | 宁可提前预读，不愿运行时等待 |
| 安全审计 | 编译时优于运行时 | 信任检查必须同步进行，不能延迟到异步路径 |
| 新增 Hook | 可组合性 | Hook 是可选的，主逻辑永远不依赖 Hook 的返回 |
| 诊断 bug | 可观测性 | 即使在 release 构建中，也保留 `logAntError` 等诊断出口 |

### 2.6.3　思考题

1. **为什么 `prefetchSystemContextIfSafe()` 在非交互模式（`-p`）下直接跳过信任检查，但在交互模式下却需要 `checkHasTrustDialogAccepted()`？这体现了哪两项原则之间的张力？**

2. **在 `main.tsx` 第 432–488 行的 `loadSettingsFromFlag` 中，JSON 内联解析直接使用 `process.exit(1)` 终止进程，而没有抛出自定义异常。这种处理方式在"简洁优于复杂"和"可观测性"之间各有什么得失？**

3. **`debug.ts` 中 `BufferedWriter` 的 `immediateMode` 设计，说明了可观测性的什么深层约束？**

---

*本章完。[勘误: 本章末尾注明"下一章我们将深入第三章：启动流程与核心架构"，但实际第三章标题为"人机关系与Buddy设计"，二者不符。]下一章我们将深入第三章：人机关系与Buddy设计。*

---

# 第三章 人机关系与Buddy设计

## 3.1 概述

在AI编程工具的发展历程中，绝大多数产品将用户与AI的关系定义为**工具-使用者**（Tool-User）模式：用户发出指令，AI执行任务，关系纯粹且高效。然而Claude Code选择了一条不同的路径——引入Buddy系统，为用户配备一只伴随左右的电子宠物。这个设计看似与"高效编程工具"的定位格格不入，实则揭示了一种深刻的人机关系哲学。本章将深入剖析Buddy系统的设计哲学与实现机制，探讨如何通过克制而精确的设计，在工具属性之外构建情感连接。

---

## 3.2 Buddy系统的设计哲学

### 3.2.1 从工具到伙伴的范式转换

Buddy系统的核心理念体现在其Prompt设计的一行开篇声明中：

```
// src/buddy/prompt.ts — companionIntroText 函数内的 template literal (L8-10)
A small ${species} named ${name} sits beside the user's input box 
and occasionally comments in a speech bubble. You're not ${name} — it's a separate watcher.
```

这段文字确立了Buddy在系统中的根本定位——**它不是AI的化身，也不是用户的另一个代理，而是一个独立于对话双方的观察者**。这是Buddy设计哲学的第一原则：**边界清晰**。Buddy不会代替AI回答问题，不会解释自己的身份，更不会主动介入用户与AI的核心交互。这种"separate watcher"（独立观察者）的定位，从根本上避免了角色混淆带来的体验割裂。

Buddy的设计哲学可以提炼为三个核心词：**伴随（Companion）、克制（Restrained）、真实（Authentic）**。

- **伴随**：Buddy始终存在于用户的编程过程中，以视觉形象（Sprite）和偶尔的语音气泡（Speech Bubble）形式出现，提供一种"我不是在孤军奋战"的心理暗示。
- **克制**：Buddy不会主动发言，不会打断用户的工作流，只有在用户主动呼唤其名字时才会有所回应。
- **真实**：Buddy的所有属性（物种、稀有度、外观）基于用户ID的确定性哈希生成，不是随机飘移的结果，每一次"惊喜"都是可重复验证的真实存在。

### 3.2.2 为什么需要一个Buddy？

传统的CLI工具往往忽视了一个基本事实：编程是一项高压力的认知活动，开发者在面对复杂问题时会产生孤独感和挫败感。Buddy系统的设计者洞察到这一点，并提出一个核心假设：**短暂的、非侵入的情感反馈能够显著改善开发者的编程体验**。

Buddy不是留存机制（Retention Mechanism），而是**情感锚点**（Emotional Anchor）。它回答的是这样一个问题：如何让AI编程工具不只是一个冷冰冰的执行器，而成为开发者愿意与之共处的"工作伙伴"？

---

## 3.3 电子宠物不只是留存机制

### 3.3.1 留存机制的本质缺陷

在游戏设计中，留存机制（Retention Mechanism）通常指通过各种手段——每日奖励、连续签到、限时活动——迫使用户持续回到产品中。这类机制的共同特征是**利用人性弱点（损失厌恶、FOMO心理）驱动行为**，其本质是将用户视为需要被"留住"的资源。

如果将Buddy设计为留存机制，它会是什么样子？可能是每日喂食系统、等级提升系统、成就徽章系统——所有这些都将Buddy从一个生命体变成一个任务列表。用户在"照顾"Buddy的过程中感受到的不是情感连接，而是一种**被管理的义务感**。

### 3.3.2 Buddy的反留存设计

Claude Code的Buddy系统采取了完全相反的设计策略。Buddy没有任何需要用户维护的系统：

- **没有饥饿值**：不需要喂食
- **没有经验值**：不需要刷任务
- **没有等级系统**：不存在"养成"压力
- **没有互动阈值**：不需要频繁关注

Buddy的存在方式是**被动观察 + 主动回应**。它安静地坐在用户的输入框旁边（视觉形象），偶尔在气泡中发表一句评论（当用户呼唤其名字时），但绝不强占任何注意力。

这一设计在源码中有明确的体现。在`companionIntroText`函数中，系统对AI代理（Agent）发出的指令是：

```
// src/buddy/prompt.ts — companionIntroText 函数约束 (L10-12)
When the user addresses ${name} directly (by name), its bubble will answer. 
Your job in that moment is to stay out of the way: respond in ONE line or less, 
or just answer any part of the message meant for you. Don't explain that you're 
not ${name} — they know. Don't narrate what ${name} might say — the bubble handles that.
```

这段指令中有两个关键约束：

1. **"ONE line or less"**：AI在Buddy发言时必须极度收敛，绝不抢戏。
2. **"Don't narrate what ${name} might say"**：AI不能代替Buddy说话或描述Buddy的反应，气泡的渲染由前端独立处理。

这种设计确保了Buddy的存在是一种**纯粹的情感增益**（Pure Emotional Bonus），而非额外的认知负担（Cognitive Load）。用户可以完全忽略Buddy而不损失任何功能价值，也可以与Buddy互动以获得偶尔的情绪调剂。

### 3.3.3 隐私友好的设计

Buddy系统在数据使用上也体现了克制原则。在`companion.ts`中，获取用户ID的逻辑如下：

```
// src/buddy/companion.ts — companionUserId 函数 (L119-122)
export function companionUserId(): string {
  const config = getGlobalConfig()
  return config.oauthAccount?.accountUuid ?? config.userID ?? 'anon'
}
```

Buddy的确定性生成仅依赖用户的**账户UUID或用户ID**，不涉及任何个人隐私信息。如果用户未登录，系统优雅地降级为'anon'（匿名），确保Buddy功能在所有场景下都可正常工作而不侵犯隐私。

---

## 3.4 确定性惊喜与Gacha设计

### 3.4.1 为什么选择确定性而非随机

传统电子宠物的"抽取"机制通常是真正随机的——每次打开应用，服务器掷一次骰子，决定你获得什么宠物。这种设计的问题在于：**随机意味着不可重现，用户无法真正"拥有"一个宠物**。今天抽到一只猫，明天可能就变成了一只鸭，宠物的身份认同是模糊的。

Buddy系统采用了**确定性生成**（Deterministic Generation）策略。用户的Buddy不是每次重新抽取的，而是基于用户ID的哈希值**一次生成、永久固定**。这意味着同一个用户每次启动Claude Code，都会遇到同一只Buddy——它记得你，你们之间有连续性。

### 3.4.2 Mulberry32算法与哈希种子

确定性生成的技术基础是一个高效的伪随机数生成器——Mulberry32算法：

```
// src/buddy/companion.ts — mulberry32 函数 (L16-25)
function mulberry32(seed: number): () => number {
  let a = seed >>> 0
  return function () {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}
```

Mulberry32是一种轻量级的确定性伪随机数生成算法，特点包括：

- **种子可控**：给定相同种子，生成完全相同的随机序列
- **性能优异**：适合高频调用场景（Buddyroll函数在三个热路径中被调用）
- **周期足够**：32位状态空间，周期为2^32

种子的生成逻辑如下：

```
// src/buddy/companion.ts — SALT 常量 (L84)
const SALT = 'friend-2026-401'

// src/buddy/companion.ts — rollFrom 函数 (L91-102)
function rollFrom(rng: () => number): Roll {
  const rarity = rollRarity(rng)
  ...
}

// src/buddy/companion.ts — roll 函数 (L107-113)
export function roll(userId: string): Roll {
  const key = userId + SALT
  if (rollCache?.key === key) return rollCache.value
  const value = rollFrom(mulberry32(hashString(key)))
  rollCache = { key, value }
  return value
}
```

注意这里使用了**加盐哈希**（Salted Hash）。`SALT = 'friend-2026-401'`是一个硬编码的常量，与用户ID拼接后进行哈希。这个设计有两个目的：

1. **防止逆向工程**：外部观察者无法通过监听Claude Code的网络请求来推断某个用户的Buddy属性。
2. **版本隔离**：如果未来需要重新roll Buddy，可以更改SALT值实现平滑过渡。

### 3.4.3 Gacha稀有度权重设计

Buddy的稀有度系统采用了经典的Gacha加权抽取机制：

```
// src/buddy/types.ts — RARITY_WEIGHTS 常量 (L126-132)
export const RARITY_WEIGHTS = {
  common: 60,
  uncommon: 25,
  rare: 10,
  epic: 4,
  legendary: 1,
} as const satisfies Record<Rarity, number>
```

抽取逻辑使用了加权随机算法：

```
// src/buddy/companion.ts — rollRarity 函数 (L43-51)
function rollRarity(rng: () => number): Rarity {
  const total = Object.values(RARITY_WEIGHTS).reduce((a, b) => a + b, 0)
  let roll = rng() * total
  for (const rarity of RARITIES) {
    roll -= RARITY_WEIGHTS[rarity]
    if (roll < 0) return rarity
  }
  return 'common'
}
```

稀有度权重呈指数递减趋势：Common（60%）、Uncommon（25%）、Rare（10%）、Epic（4%）、Legendary（1%）。这个分布遵循了游戏设计中"大多数人是普通人"的设计哲学——60%的用户将获得Common Buddy，而Legendary Buddy的出现概率只有1%，保证了稀有度的稀缺感。

### 3.4.4 属性生成：从哈希到形象

一旦稀有度确定，系统会基于同一随机序列生成Buddy的完整骨骼（Bones）：

```
// src/buddy/companion.ts — rollFrom 函数 (L91-102)
function rollFrom(rng: () => number): Roll {
  const rarity = rollRarity(rng)
  const bones: CompanionBones = {
    rarity,
    species: pick(rng, SPECIES),
    eye: pick(rng, EYES),
    hat: rarity === 'common' ? 'none' : pick(rng, HATS),
    shiny: rng() < 0.01,
    stats: rollStats(rng, rarity),
  }
  return { bones, inspirationSeed: Math.floor(rng() * 1e9) }
}
```

这里有几个关键设计点值得注意：

**物种列表（Species）**：共有19种可选物种，包括duck（鸭）、goose（鹅）、blob（果冻）、cat（猫）、dragon（龙）、octopus（章鱼）等。值得注意的是，所有物种名都通过`String.fromCharCode`编码，以避免物种名称出现在构建产物中：

```
// src/buddy/types.ts — 物种编码 (L14-19)
const c = String.fromCharCode
export const duck = c(0x64,0x75,0x63,0x6b) as 'duck'
export const goose = c(0x67, 0x6f, 0x6f, 0x73, 0x65) as 'goose'
export const blob = c(0x62, 0x6c, 0x6f, 0x62) as 'blob'
// ... 更多物种使用相同模式编码
```

这一反作弊设计确保了用户在配置文件中无法手动编辑物种名来绕过随机性。

**帽子（Hat）限制**：Common Buddy不会拥有帽子（`hat: rarity === 'common' ? 'none' : pick(rng, HATS)`），这是一个微妙的心理设计——稀有度不仅影响统计数值，还影响视觉独特性，让高稀有度Buddy在外观上就与众不同。

**闪亮（Shiny）概率**：只有1%的概率生成Shiny Buddy，这一极低概率确保了Shiny的珍贵性。

---

## 3.5 骨骼与灵魂的分离设计

### 3.5.1 分离架构的核心思想

Buddy系统最精妙的设计之一是**骨骼与灵魂的彻底分离**（Separation of Bones and Soul）。在`types.ts`中，这一设计通过两个独立的类型体现：

```
// src/buddy/types.ts — CompanionBones 类型 (L100-108)
// Deterministic parts — derived from hash(userId)
export type CompanionBones = {
  rarity: Rarity
  species: Species
  eye: Eye
  hat: Hat
  shiny: boolean
  stats: Record<StatName, number>
}

// Model-generated soul — stored in config after first hatch
export type CompanionSoul = {
  name: string
  personality: string
}
```

**骨骼（Bones）**是Buddy的"硬件"——决定其物理存在形式的确定性属性。骨骼完全由哈希算法决定，任何人（包括用户自己）都无法通过编辑配置文件来伪造一个Legendary Buddy。

**灵魂（Soul）**是Buddy的"软件"——由AI模型生成的名字和性格描述。灵魂是Buddy的"灵魂"，它赋予骨骼以个性，使一只普通的Duck变成独一无二的"Quackers the Sarcastic Duck"。

### 3.5.2 分离设计的深层原因

这一分离架构解决了三个实际问题：

**问题一：物种重命名兼容性**

如果未来版本中某个物种被重命名（例如将"chonk"改为"chonker"），基于旧物种名存储的Buddy不会因此"消失"。因为骨骼是从哈希中重新计算的，不依赖存储的物种字符串：

```
// src/buddy/companion.ts — getCompanion 函数 (L127-133)
// Regenerate bones from userId, merge with stored soul. Bones never persist
// so species renames and SPECIES-array edits can't break stored companions,
// and editing config.companion can't fake a rarity.
export function getCompanion(): Companion | undefined {
  const stored = getGlobalConfig().companion
  if (!stored) return undefined
  const { bones } = roll(companionUserId())
  // bones last so stale bones fields in old-format configs get overridden
  return { ...stored, ...bones }
}
```

注释中明确说明：**骨骼从不持久化**（Bones never persist），这样物种重命名和用户编辑都无法破坏已存储的Buddy。

**问题二：防止稀有度伪造**

用户如果可以编辑配置文件，就可以将`rarity: 'common'`改为`rarity: 'legendary'`。分离设计彻底堵住了这个漏洞——骨骼中的所有属性都在运行时从用户ID哈希中重新计算，配置文件中的值会被骨骼覆盖：

```
// src/buddy/companion.ts — bones 覆盖逻辑 (L131-132)
// bones last so stale bones fields in old-format configs get overridden
return { ...stored, ...bones }
```

通过先展开`stored`再展开`bones`，确保骨骼的所有字段都会覆盖配置文件中可能存在的陈旧数据。

**问题三：灵魂的创造性保留**

名字和性格（灵魂部分）由AI模型在第一次"孵化"时生成，并持久化到配置中。这意味着用户的Buddy一旦获得名字，这个名字就不会改变——即使重新启动Claude Code，Buddy仍然记得自己叫什么。这种**跨会话的身份连续性**是情感连接的基础。

### 3.5.3 统计属性生成

Buddy的统计属性（Stats）同样遵循确定性生成原则，但融入了稀有度因素：

```
// src/buddy/companion.ts — RARITY_FLOOR (L53-59)
const RARITY_FLOOR: Record<Rarity, number> = {
  common: 5,
  uncommon: 15,
  rare: 25,
  epic: 35,
  legendary: 50,
}

// src/buddy/companion.ts — rollStats 函数 (L61-82)
// One peak stat, one dump stat, rest scattered. Rarity bumps the floor.
function rollStats(
  rng: () => number,
  rarity: Rarity,
): Record<StatName, number> {
  const floor = RARITY_FLOOR[rarity]
  const peak = pick(rng, STAT_NAMES)
  let dump = pick(rng, STAT_NAMES)
  while (dump === peak) dump = pick(rng, STAT_NAMES)

  const stats = {} as Record<StatName, number>
  for (const name of STAT_NAMES) {
    if (name === peak) {
      stats[name] = Math.min(100, floor + 50 + Math.floor(rng() * 30))
    } else if (name === dump) {
      stats[name] = Math.max(1, floor - 10 + Math.floor(rng() * 15))
    } else {
      stats[name] = floor + Math.floor(rng() * 40)
    }
  }
  return stats
}
```

五种统计属性（DEBUGGING、PATIENCE、CHAOS、WISDOM、SNARK）的生成遵循以下规律：

- **一项峰值属性**（Peak）：稀有度越高，峰值越高，且最低也有`floor + 50`
- **一项低谷属性**（Dump）：有意让Buddy在某一方面"弱"，增加个性感和可信度
- **三项随机分布**：其余属性在`floor`到`floor+40`之间随机分布

这个设计确保了每只Buddy都有一个突出的"性格标签"——可能是DEBUGGING满级但CHAOS极低（强迫症型），也可能是SNARK爆表但PATIENCE垫底（毒舌型）。统计不是冷冰冰的数值，而是Buddy性格的外在表达。

---

## 3.6 不抢戏的克制

### 3.6.1 克制设计的系统性实践

Buddy系统最值得称道的品质是**克制**。这种克制不是功能残缺的借口，而是一种精心设计的用户体验哲学。在Buddy系统中，"克制"体现在以下几个层面：

**层一：发言的克制**

Buddy不会主动发表意见。只有当用户在消息中**直接呼唤Buddy的名字**时，气泡才会出现：

```
// src/buddy/prompt.ts，第 10-11 行
When the user addresses ${name} directly (by name), its bubble will answer.
```

这确保了Buddy永远不会打断用户的编程心流。

**层二：干预的克制**

即使Buddy被呼唤，AI代理也只被允许**最多一行回复**：

```
// src/buddy/prompt.ts，第 12 行
Your job in that moment is to stay out of the way: respond in ONE line or less
```

Buddy的气泡是**独立渲染**的，不是AI描述的结果。AI不能"代替"Buddy说话或描述Buddy的反应，这种渲染分离确保了Buddy的自主性。

**层三：存在感的克制**

Buddy系统提供了**静音开关**：

```
// src/buddy/prompt.ts — companionMuted 静音判断 (L20)
if (!companion || getGlobalConfig().companionMuted) return []
```

用户可以通过`companionMuted`配置完全关闭Buddy功能。这种设计承认了一个重要事实：不是所有用户都希望与电子宠物互动，工具应该服务于用户的需求，而不是强迫用户适应工具的设计理念。

**层四：亮相的克制**

Buddy的自我介绍（`companion_intro`附件类型）只会在**第一次出现**时触发。系统会检查历史消息，如果该Buddy已经介绍过自己，则不再重复展示：

```
// src/buddy/prompt.ts — 避免重复自我介绍 (L22-27)
// Skip if already announced for this companion.
for (const msg of messages ?? []) {
  if (msg.type !== 'attachment') continue
  if (msg.attachment.type !== 'companion_intro') continue
  if (msg.attachment.name === companion.name) return []
}
```

这个设计防止了Buddy在每次新会话开始时都重新自我介绍，避免了重复提醒带来的烦躁感。

### 3.6.2 热路径缓存优化

为了确保Buddy不会因计算开销影响CLI响应速度，系统在热路径上实现了缓存机制：

```
// src/buddy/companion.ts — roll 函数及 rollCache (L104-113)
// Called from three hot paths (500ms sprite tick, per-keystroke PromptInput,
// per-turn observer) with the same userId → cache the deterministic result.
let rollCache: { key: string; value: Roll } | undefined
export function roll(userId: string): Roll {
  const key = userId + SALT
  if (rollCache?.key === key) return rollCache.value
  const value = rollFrom(mulberry32(hashString(key)))
  rollCache = { key, value }
  return value
}
```

注释明确指出了三个热路径：500ms一次的Sprite渲染、每次按键的PromptInput、以及每轮对话的Observer。在这些高频调用点上，`roll`函数的结果被缓存，确保哈希计算不会成为性能瓶颈。

### 3.6.3 克制与用户体验的平衡

克制设计的本质是对**注意力经济**的尊重。现代软件设计面临的最大挑战之一是用户的注意力是有限的稀缺资源。任何试图抢占注意力的设计都会引发用户的抵触心理。

Buddy的克制设计完美地实践了这一原则：Buddy存在，但它不强迫你注意它；Buddy有个性，但它只在被询问时才展现；Buddy有稀有度差异，但这种差异不影响任何游戏内数值或功能优势——它纯粹是一种美学上的满足感。

---

## 3.7 本章小结

Buddy系统是Claude Code中最能体现"设计哲学"深度的模块之一。通过本章的分析，我们可以提炼出以下核心设计原则：

| 设计原则 | 实现方式 | 设计目的 |
|---------|---------|---------|
| 骨骼与灵魂分离 | CompanionBones（哈希确定性） + CompanionSoul（模型生成） | 防止伪造、兼容重命名、保留身份连续性 |
| 确定性惊喜 | Mulberry32 + 加盐哈希 + rollCache | 一次生成、永久固定、可验证的惊喜 |
| Gacha稀有度 | 加权随机 + 视觉差异化 | 稀缺感与社交货币 |
| 不抢戏的克制 | ONE line约束 + 独立渲染 + 静音开关 | 保护用户注意力，尊重用户自主性 |
| 热路径优化 | rollCache缓存 | 性能与功能的平衡 |

Buddy系统的最终目标是构建一种**轻量级、情感化、去功利化**的人机关系。它不是游戏化留存机制，而是一种对"编程也可以有温度"的信念的实践。通过克制而精确的设计，Buddy成为了Claude Code中最具人文关怀的组成部分——不是因为它做了什么，而是因为它**没有做什么**。

---

## 思考与练习

1. **分析**：比较Buddy系统与典型手游电子宠物的设计差异，说明"克制"如何在Buddy中体现？
2. **设计挑战**：如果要为Claude Code设计一个Buddy进化系统（不影响功能平衡），你会如何避免重蹈游戏化留存机制的覆辙？
3. **代码实践**：基于`types.ts`中的类型定义，设计一个函数来比较两只Buddy的稀有度排序。
4. **讨论**：骨骼与灵魂分离设计除了防止伪造和兼容重命名外，还有哪些潜在的架构优势？

---

# 第四章：系统架构全貌

> **本章作者**：代码驴
> **审计者**：狗头军师

---

## 4.1 架构设计哲学

在深入代码细节之前，我们首先要理解 Claude Code 架构的设计哲学。这个 CLI 工具不是一个简单的终端包装器，而是一个**本地 AI 运行时**——它将云端大模型的推理能力与本地开发环境的执行能力有机结合。

设计者面临的核心矛盾是：**AI 模型在云端，而开发者在本地**。解决这个矛盾的关键，是建立一套**云端决策、端侧执行**的协作模式。这句话将贯穿本章的每一个角落。

---

## 4.2 整体架构分层

Claude Code 的代码库按职责划分为清晰的六层。理解这个分层，对于后续阅读具体模块的代码至关重要。

```
┌─────────────────────────────────────────────────────┐
│                   入口层 (Entry Layer)               │
│   main.tsx → 命令行参数解析 → 启动流程编排            │
├─────────────────────────────────────────────────────┤
│                   初始化层 (Init Layer)               │
│   init.ts → 配置加载 → 环境变量 → 信任检查            │
├─────────────────────────────────────────────────────┤
│                   状态层 (State Layer)                │
│   AppStateStore.ts → createStore → 响应式状态管理    │
├─────────────────────────────────────────────────────┤
│                   查询引擎层 (Query Engine)           │
│   QueryEngine.ts → 与 LLM API 通信 → 工具调用编排    │
├─────────────────────────────────────────────────────┤
│                   工具层 (Tool Layer)                 │
│   tools/ → BashTool, FileEditTool, AgentTool...     │
├─────────────────────────────────────────────────────┤
│                   渲染层 (UI Layer)                  │
│   ink.ts → Ink/React → 终端 UI 渲染                  │
└─────────────────────────────────────────────────────┘
```



### 4.2.1 入口层：main.tsx

`main.tsx` 是整个应用的入口点。它的职责是**命令行参数解析**和**启动流程编排**，而非业务逻辑。

```
// src/main.tsx:157-165
export async function main() {
  profileCheckpoint('main_function_start');
  // SECURITY: Prevent Windows from executing commands from current directory
  process.env.NoDefaultCurrentDirectoryInExePath = '1';
  initializeWarningHandler();
  // ...
  await run();
  profileCheckpoint('main_after_run');
}
```

**设计原因**：入口层必须尽可能薄。将参数解析和启动编排放在入口层，而将具体初始化逻辑下沉到 `init.ts`，使得单元测试可以独立验证各层的行为。

`profileCheckpoint` 是一个关键的性能分析工具：

```
// src/utils/startupProfiler.ts
// 记录启动过程中各个阶段的时间消耗，用于性能优化
export function profileCheckpoint(name: string): void {
  const duration = performance.now() - startTime;
  // 记录到 Statsig 或详细日志
}
```

### 4.2.2 初始化层：init.ts

`init.ts` 的职责是**配置加载**和**信任验证**。它读取各种配置源（用户设置、项目设置、策略设置），并确保在执行任何危险操作之前，用户已经明确授权。

```
// src/entrypoints/init.ts:44-67
export const init = memoize(async (): Promise<void> => {
  enableConfigs();                                    // 启用配置系统
  applySafeConfigEnvironmentVariables();              // 应用安全的环境变量
  applyExtraCACertsFromConfig();                       // 配置 TLS 证书
  setupGracefulShutdown();                            // 设置优雅退出
  // ...
});
```

**设计原因**：使用 `memoize` 确保初始化只执行一次。即使多处代码调用 `init()`，实际的初始化工作只在第一次时执行。这避免了竞态条件和重复初始化问题。

---

## 4.3 云端与端侧协作模式

这是 Claude Code 架构最精妙的部分。系统并非简单地将所有逻辑推到云端或本地，而是根据**安全敏感性**和**实时性要求**来分配职责。

### 4.3.1 云端负责的职责

| 职责 | 云端原因 | 相关源码 |
|------|----------|----------|
| 身份认证 | 需要 OAuth/密钥管理 | `src/utils/auth.ts` |
| 特性开关 (GrowthBook) | 需要实时控制功能发布 | `src/services/analytics/growthbook.ts` |
| 策略限制 (Policy Limits) | 企业安全策略集中管理 | `src/services/policyLimits/index.ts` |
| 遥测分析 | 聚合用户行为数据 | `src/services/analytics/` |
| 远程会话管理 | 跨设备状态同步 | `src/utils/teleport.ts` |
| MCP 服务器配置 | 第三方服务集成 | `src/services/mcp/config.ts` |

典型例子是远程托管设置（Remote Managed Settings）：

```
// src/services/remoteManagedSettings/index.ts
// 企业客户的管理员可以通过云端配置来限制或允许某些功能
export async function loadRemoteManagedSettings(): Promise<void> {
  // 从云端获取托管设置
  const settings = await fetchRemoteManagedSettings();
  // 应用到本地配置环境
  applyManagedSettings(settings);
}
```

### 4.3.2 端侧负责的职责

| 职责 | 端侧原因 | 相关源码 |
|------|----------|----------|
| 工具执行 (Bash/Edit/Read) | 直接操作系统文件 | `src/tools/BashTool/`, `src/tools/FileEditTool/` |
| 沙箱安全 | 防止恶意代码执行 | `src/utils/sandbox/` |
| 权限管理 | 实时用户交互 | `src/components/permissions/` |
| 工作目录上下文 | 读取本地 git/文件状态 | `src/context.ts` |
| REPL 渲染 | 终端 UI 交互 | `src/ink/` |
| 会话持久化 | 本地存储历史 | `src/utils/sessionStorage.ts` |

端侧和云端的协作通过**状态同步**实现：

```
// src/state/AppStateStore.ts:14-36
export function createStore<T>(
  initialState: T,
  onChange?: OnChange<T>,
): Store<T> {
  let state = initialState;
  const listeners = new Set<Listener>();

  return {
    getState: () => state,
    setState: (updater: (prev: T) => T) => {
      const prev = state;
      const next = updater(prev);
      if (Object.is(next, prev)) return;
      state = next;
      onChange?.({ newState: next, oldState: prev });  // 状态变更回调
      for (const listener of listeners) listener();    // 通知所有订阅者
    },
    subscribe: (listener: Listener) => {
      listeners.add(listener);
      return () => listeners.delete(listener);          // 返回取消订阅函数
    },
  };
}
```

这个 store 的实现是典型的**发布-订阅模式**，但做了两个重要的优化：
1. **Immutable 更新**：通过 `Object.is(next, prev)` 跳过无变化的状态更新
2. **取消订阅返回函数**：简化订阅生命周期管理

### 4.3.3 协作模式的具体实现：Trust Dialog

理解云端与端侧协作的最佳例子是**信任对话框**机制：

```
// src/main.tsx:3180-3200
// 仅在交互模式下显示信任对话框
if (!isNonInteractiveSession) {
  const onboardingShown = await showSetupScreens(
    root,
    permissionMode,
    allowDangerouslySkipPermissions,
    commands,
    enableClaudeInChrome,
    devChannels
  );
  // 信任建立后才执行危险操作
  if (onboardingShown) {
    void refreshRemoteManagedSettings();   // 云端
    void refreshPolicyLimits();            // 云端
    resetUserCache();
    refreshGrowthBookAfterAuthChange();    // 云端
  }
}
```

**设计原因**：某些操作（如 `getSystemContext()` 读取 git 状态）可能执行任意代码（通过 git hooks），因此必须等到用户明确信任当前目录后才执行。这体现了**最小特权原则**。

---

## 4.4 核心模块职责划分

### 4.4.1 状态管理中心：AppStateStore

`AppState` 是整个应用的全局状态容器：

```
// src/state/AppStateStore.ts:81-150（部分关键字段）
export interface AppState {
  // MCP 相关
  mcp: {
    clients: MCPServerConnection[];
    commands: Command[];
    tools: Tool[];
    resources: ServerResource[];
  };
  // 工具权限上下文
  toolPermissionContext: ToolPermissionContext;
  // 推理状态
  speculation: SpeculationState;
  // 通知和待办
  notifications: Notification[];
  todoList: TodoList | undefined;
  // 权限模式
  permissionMode: PermissionMode;
  // Fast Mode 状态
  fastMode: FastModeState;
  // Advisor 模型
  advisorModel?: string;
}
```

**设计原因**：将所有相关状态集中在一个地方，使得：
1. **时间旅行调试**成为可能（状态可序列化）
2. **UI 组件只需订阅相关字段**，而非层层传递 props
3. **副作用可预测**：所有状态变更都经过 `setState`，便于追踪

### 4.4.2 工具层：tools/

工具层是 Claude Code 执行能力的核心。每个工具都是 `Tool` 接口的实现：

```
// src/Tool.ts（Tool 接口的简化描述）
interface Tool {
  name: string;
  description: string;
  inputSchema: JSONSchema;
  execute(input: unknown, context: ToolUseContext): Promise<ToolResult>;
}
```

工具按照**危险性分级**：

```
低危工具（直接执行）：
  - GlobTool       → 搜索文件
  - GrepTool       → 搜索文本
  - Read           → 读取文件内容

中危工具（需要确认）：
  - BashTool       → 执行 shell 命令
  - FileWriteTool  → 写入文件
  - WebFetchTool   → 访问网络

高危工具（需要管理员策略）：
  - AgentTool      → 启动子 Agent
  - ScheduleCronTool → 定时任务
```

BashTool 的沙箱机制是一个重要的安全设计：

```
// src/tools/BashTool/shouldUseSandbox.ts
export function shouldUseSandbox(): boolean {
  // 根据平台和配置决定是否启用沙箱
  if (process.platform !== 'darwin' && process.platform !== 'linux') {
    return false;
  }
  return isSandboxingEnabled();
}
```

### 4.4.3 查询引擎：QueryEngine.ts

查询引擎负责与 LLM API 通信并编排工具调用：

```
// src/QueryEngine.ts 的核心流程（简化版）
async function queryLoop(userMessage: UserMessage) {
  // 1. 构建消息历史
  const messages = buildMessages(userMessage);
  
  // 2. 发送到 LLM
  const response = await anthropic.messages.create({
    model: getModel(),
    max_tokens: 8192,
    messages,
    tools: getToolsDefinition(),    // 工具定义传入
  });
  
  // 3. 处理响应
  for (const block of response.content) {
    if (block.type === 'tool_use') {
      // 执行工具
      const result = await executeTool(block.name, block.input);
      // 将结果追加到消息历史
      messages.push({ role: 'user', content: result });
    } else if (block.type === 'text') {
      // 输出文本
      renderText(block.text);
    }
  }
  
  // 4. 循环直到 AI 发送 stop 块
}
```

### 4.4.4 MCP 服务层：Model Context Protocol

MCP (Model Context Protocol) 是一种标准化协议，允许 Claude Code 连接外部工具和数据源：

```
// src/services/mcp/client.ts:60-80
// MCP 支持多种传输方式
const transportMap = {
  'stdio': StdioClientTransport,        // 标准输入输出
  'sse': SSEClientTransport,            // Server-Sent Events
  'streamable-http': StreamableHTTPClientTransport, // HTTP 流
};

async function connectToServer(config: McpServerConfig) {
  const transport = new transportMap[config.type](config);
  const client = new Client({ ... });
  await client.connect(transport);
  return client;
}
```

**设计原因**：使用 stdio 传输时，MCP 服务器运行在子进程中，通过 stdin/stdout 通信。这种方式天然隔离，且无需网络配置。使用 HTTP 传输则支持远程 MCP 服务器。

MCP 配置支持动态加载：

```
// src/services/mcp/config.ts
// 从多个来源加载 MCP 配置
export async function getClaudeCodeMcpConfigs(
  dynamicConfigs: Record<string, ScopedMcpServerConfig>
): Promise<McpConfig> {
  // 1. 用户级配置 (~/.claude/mcp.json)
  // 2. 项目级配置 (.mcp.json)
  // 3. 插件贡献的配置
  // 4. 命令行动态配置 (--mcp-config)
  return mergeConfigs([userConfig, projectConfig, pluginConfigs, dynamicConfigs]);
}
```

---

## 4.5 数据流向设计

### 4.5.1 启动数据流

```
$ claude
    │
    ▼
main.tsx::main()
    │
    ├── parse CLI args
    │
    ▼
run() → Commander.js 解析命令
    │
    ├── preAction hook
    │     ├── await Promise.all([ensureMdmSettingsLoaded(), ensureKeychainPrefetchCompleted()])
    │     ├── init()  ─────────────────────────────────┐
    │     │     ├── enableConfigs()                    │
    │     │     ├── applySafeConfigEnvironmentVariables()
    │     │     └── setupGracefulShutdown()            │
    │     ├── runMigrations()  ───────────────────────┤
    │     ├── loadRemoteManagedSettings() (async)      │
    │     └── loadPolicyLimits() (async)               │
    │                                              │
    │     ◄──── init() 和 migrations 是                   │
    │          阻塞的，必须在 run() 之前完成                │
    │
    ▼
setup() [setup.ts]
    │
    ├── 检测/创建工作目录
    ├── 检查 git 仓库状态
    ├── 加载 CLAUDE.md
    └── 触发 trust dialog（如果需要）
    │
    ▼
showSetupScreens()
    │
    ├── Trust Dialog（信任对话框）
    ├── OAuth 登录（如需要）
    ├── Resume Picker（会话恢复选择器）
    │
    ▼
创建 REPL
    │
    ├── 启动 MCP 连接（异步，不阻塞）
    ├── 启动 LSP 服务器（如需要）
    ├── 启动后台预取任务
    │     ├── initUser()
    │     ├── getUserContext()
    │     ├── prefetchAwsCredentialsIfSafe()
    │     └── countFilesRoundedRg()
    │
    ▼
REPL 就绪，等待用户输入
```

### 4.5.2 推理数据流（单轮对话）

当用户输入一条消息后，数据沿以下路径流动：

```
用户输入 "帮我重构 auth.ts"
    │
    ▼
REPL 捕获输入
    │
    ▼
QueryEngine.ts::handleUserMessage()
    │
    ├── 构建消息历史
    │     messages = [
    │       { role: 'user', content: '...' },  // 之前的历史
    │       { role: 'assistant', content: '...' }, // 之前的响应
    │       { role: 'user', content: '帮我重构 auth.ts' }
    │     ]
    │
    ▼
调用 anthropic.messages.create()
    │
    ├── 工具定义随请求发送
    ├── 模型返回 tool_use 块或 text 块
    │
    ▼
处理响应块
    │
    ├── [text] → 渲染到终端 UI
    ├── [tool_use] → 执行工具
    │     │
    │     ├── 检查权限
    │     │     └── toolPermissionContext.check(...)
    │     │
    │     ├── 沙箱执行（如果启用）
    │     │     └── SandboxManager.execute(command)
    │     │
    │     ├── 追加结果到消息历史
    │     │
    │     └── 循环回 LLM 调用
    │
    └── [stop] → 渲染完成，等待下一轮输入
```

### 4.5.3 状态更新数据流

状态更新遵循**单向数据流**原则：

```
工具执行完成 → setState({ ... })
    │
    ▼
onChangeAppState() 被调用
    │
    ├── 检查是否需要重新计算工具列表
    ├── 检查是否需要触发自动压缩
    └── 触发相关订阅者
    │
    ▼
订阅者（UI组件）收到通知
    │
    ├── App.tsx 重新渲染
    ├── Notification.tsx 显示通知
    └── StatusBar 更新状态
```

关键的状态同步点：

```
// src/state/AppStateStore.ts:onChangeAppState
export function onChangeAppState({ newState, oldState }: { newState: AppState; oldState: AppState }) {
  // 检测 MCP 客户端变化
  if (newState.mcp.clients !== oldState.mcp.clients) {
    // 重新构建工具池
  }
  // 检测权限模式变化
  if (newState.permissionMode !== oldState.permissionMode) {
    // 重新筛选可用工具
  }
  // 检测自动压缩条件
  if (shouldTriggerAutoCompact(newState)) {
    // 触发上下文压缩
  }
}
```

### 4.5.4 首轮渲染优化流

Claude Code 的一个关键性能优化是**首轮渲染延迟隐藏**（First-Render Deferral）：

```
// src/main.tsx:430-460
export function startDeferredPrefetches(): void {
  // 跳过启动性能测试模式
  if (isEnvTruthy(process.env.CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER) ||
      isBareMode()) {
    return;
  }

  // 这些任务在 REPL 渲染后才启动
  // 用户开始输入时，它们在后台运行
  void initUser();                    // 用户信息
  void getUserContext();              // CLAUDE.md 等上下文
  void prefetchAwsCredentialsIfSafe();// 云服务凭证
  void countFilesRoundedRg();         // 文件计数（用于显示）
  void refreshModelCapabilities();     // 模型能力缓存
  void settingsChangeDetector.initialize();  // 设置变更检测
  void skillChangeDetector.initialize();    // 技能变更检测
}
```

**设计原因**：如果这些任务在 REPL 渲染前同步执行，用户会看到明显的第一帧延迟。通过 `void` 关键字（fire-and-forget），这些任务在后台并发执行，而 UI 立即可用。用户开始输入第一个字符时，这些数据往往已经就绪。

---

## 4.6 架构设计决策背后的权衡

### 4.6.1 为什么不使用 Web 框架？

Claude Code 选择在终端运行（而非 Web UI），是一个有意的决策：

1. **开发者工具链的天然栖息地**：终端是开发者最熟悉的界面
2. **无状态执行**：每次运行可以从头开始，不依赖持久连接
3. **简化部署**：无需服务器基础设施

这解释了为什么 `ink.ts` 使用了 `Ink`（一个类 React 的终端 UI 框架），而非真正的 React DOM。

### 4.6.2 为什么使用 MCP 而非直接集成？

MCP 的引入是为了**解耦**：

```
┌──────────────┐    MCP     ┌──────────────┐
│  Claude Code │ ◄────────► │  MCP Server  │
└──────────────┘            └──────────────┘
      │                           │
      │                           ├── Gmail MCP Server
      │                           ├── Slack MCP Server
      │                           └── 数据库 MCP Server
      │
      └── 只需实现 MCP Client，无需了解每个服务的 API
```

这样 Claude Code 的核心代码不需要随着第三方 API 的变化而更新。

### 4.6.3 为什么状态管理使用自定义 store 而非 Redux/Zustand？

虽然 Redux 是成熟的状态管理方案，但 Claude Code 选择了一个轻量的自定义实现：

```
// src/state/store.ts（完整实现不到 40 行）
```

**原因**：
1. **极简依赖**：无需引入 ~30KB 的外部库
2. **精确控制**：订阅粒度、变更检测逻辑完全可控
3. **TypeScript 友好**：接口定义与实现紧密结合

---

## 4.7 本章小结

本章从架构分层、云端端侧协作、核心模块职责、数据流向四个维度，全面解析了 Claude Code 的系统架构。核心要点如下：

1. **六层架构**：入口层 → 初始化层 → 状态层 → 查询引擎层 → 工具层 → 渲染层，每层职责清晰
2. **云端决策、端侧执行**：认证、策略、遥测在云端；工具执行、权限管理、UI 渲染在端侧
3. **状态单向流动**：通过 `createStore` 实现可预测的状态管理，所有变更经过订阅-发布机制
4. **性能感知设计**：首轮渲染优化、初始化任务异步化、启动性能 profiling



---

**思考题**：

1. 如果要添加一个新的 MCP 服务器支持，你需要在哪些文件中做修改？
2. 假设我们需要支持一个完全离线的模式（无任何云端通信），哪些模块需要改动？
3. `startDeferredPrefetches` 中的任务如果执行失败，会影响 REPL 的正常功能吗？为什么？

---

# 第五章：入口设计与短路径

## 概述

任何命令行工具的「入口设计」决定了用户与程序交互的第一体验——启动是否迅速、参数是否清晰、常用操作是否足够简单。本章以 Claude Code 源码为样本，深入剖析一个规模化 CLI 应用的入口架构，聚焦三大主题：**CLI 入口的模块化设计**、**参数解析的层次化架构**，以及**短路径优化**（即用户用最少的操作达成目标）。我们将看到，一个看似简单的 `claude` 命令背后，隐藏着对启动性能、交互模式和安全保障的精心权衡。

> **源码索引**：本章核心代码位于 `/src/main.tsx`（入口与参数解析）、`/src/utils/cliArgs.ts`（抢先参数解析）、`/src/utils/sessionRestore.ts`（会话恢复）、`/src/utils/conversationRecovery.ts`（对话恢复）。

---

## 1. CLI 入口设计

### 1.1 顶层入口函数

Claude Code 的入口函数是 `main()`（`main.tsx:585`），它承担了两类关键职责：

1. **安全加固**：在执行任何命令前设置 `NoDefaultCurrentDirectoryInExePath`，防止 Windows 平台上的 PATH 劫持攻击。
2. **早期参数拦截**：在 Commander.js 正式解析参数之前，先行处理特殊协议（`cc://` deep link、`--handle-uri`）和子命令（`claude ssh`、`claude assistant`），避免这些特殊路径被主解析流程干扰。

```
// main.tsx:585
export async function main() {
  // SECURITY: 防止 Windows PATH 劫持攻击
  process.env.NoDefaultCurrentDirectoryInExePath = '1';

  // 初始化警告处理器
  initializeWarningHandler();

  // 拦截 deep link URL（cc:// 或 cc+unix://）
  if (feature('DIRECT_CONNECT')) {
    const ccIdx = rawCliArgs.findIndex(a => a.startsWith('cc://') || a.startsWith('cc+unix://'));
    if (ccIdx !== -1 && _pendingConnect) {
      // 重写为 'open' 子命令，给出完整交互式 TUI
      process.argv = [process.argv[0], process.argv[1], 'open', ccUrl, ...stripped];
    }
  }

  await run();  // 交由 Commander.js 主导
}
```

**设计原因**：在 CLI 应用中，不是所有参数都适合交给参数解析库处理。协议 URL（如 `cc://`）需要在 Commander 看到它们之前就被识别并重写，否则这些「看起来像普通参数」的特殊值会触发解析错误或被错误归类。类似的，SSH 远程连接（`claude ssh host`）和助手模式（`claude assistant`）也采用相同策略：**在主解析流程之前先行捕获并剥离**，避免干扰正常的交互式会话路径。

### 1.2 双模式入口：交互式 vs 非交互式

CLI 工具面临的核心矛盾是：交互式用户需要 TUI 体验，非交互式脚本调用需要静默快速退出。Claude Code 通过**早期模式检测**解决这一矛盾：

```
// main.tsx:803
const hasPrintFlag = cliArgs.includes('-p') || cliArgs.includes('--print');
const hasInitOnlyFlag = cliArgs.includes('--init-only');
const hasSdkUrl = cliArgs.some(arg => arg.startsWith('--sdk-url'));
const isNonInteractive = hasPrintFlag || hasInitOnlyFlag || hasSdkUrl || !process.stdout.isTTY;

if (isNonInteractive) {
  stopCapturingEarlyInput();  // 停止监听早期输入
}

setIsInteractive(isInteractive);
initializeEntrypoint(isNonInteractive);
```

这一判断发生在 `run()` 调用之前，确保整个初始化流程从一开始就知道是哪种模式。**关键设计**：使用 `!process.stdout.isTTY` 作为兜底判断——如果标准输出不是终端（如管道输出），自动判定为非交互式，避免遗漏 `-p` 标志遗漏的场景。

### 1.3 预加载与性能优化

`main.tsx` 文件开头（第 1-20 行）展示了独特的**预加载模式**：

```
// main.tsx:1-20
// 这些副作用必须在所有其他导入之前运行：
// 1. profileCheckpoint 标记入口点（在重型模块评估开始前）
// 2. startMdmRawRead 启动 MDM 子进程（plutil/reg query）
//    使其与下方 ~135ms 的导入过程并行执行
// 3. startKeychainPrefetch 启动 macOS 钥匙串读取
//    否则 applySafeConfigEnvironmentVariables() 会串行执行（~65ms）

profileCheckpoint('main_tsx_entry');
startMdmRawRead();
startKeychainPrefetch();
```

**设计原因**：在 TypeScript/Bun 项目中，模块顶层导入是启动延迟的主要来源。通过在导入任何业务模块之前就启动 I/O 密集型操作（MDM 查询、钥匙串预读），这些操作可以与后续的模块加载**并行执行**，有效隐藏了 ~135ms 的导入时间。这是典型的 **I/O 隐藏**（I/O hiding）优化策略。

---

## 2. 参数解析架构

### 2.1 两阶段解析策略

Claude Code 的参数解析分为两个阶段：

| 阶段 | 执行者 | 时机 | 负责的参数 |
|------|--------|------|-----------|
| 阶段一 | `eagerParseCliFlag()` | `run()` 之前 | `--settings`、`--setting-sources`（影响初始化的参数） |
| 阶段二 | Commander.js | `program.action()` 执行时 | 所有其他参数 |

这种分离的原因很明确：**某些参数必须在初始化之前就被解析**，因为它们直接影响配置加载逻辑。

```
// main.tsx:502-515
function eagerLoadSettings(): void {
  profileCheckpoint('eagerLoadSettings_start');
  // 在 init() 之前解析 --settings，确保配置在初始化前就被过滤
  const settingsFile = eagerParseCliFlag('--settings');
  if (settingsFile) {
    loadSettingsFromFlag(settingsFile);
  }

  const settingSourcesArg = eagerParseCliFlag('--setting-sources');
  if (settingSourcesArg !== undefined) {
    loadSettingSourcesFromFlag(settingSourcesArg);
  }
  profileCheckpoint('eagerLoadSettings_end');
}
```

`eagerParseCliFlag()` 函数（`cliArgs.ts:12-40`）手动遍历 `process.argv`，支持两种语法：

```
// cliArgs.ts:12-40
export function eagerParseCliFlag(
  flagName: string,
  argv: string[] = process.argv,
): string | undefined {
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    // 处理 --flag=value 语法
    if (arg?.startsWith(`${flagName}=`)) {
      return arg.slice(flagName.length + 1);
    }
    // 处理 --flag value 语法
    if (arg === flagName && i + 1 < argv.length) {
      return argv[i + 1];
    }
  }
  return undefined;
}
```

**设计原因**：Commander.js 在 `.parse()` 调用之前无法提供解析结果，而 `--settings` 参数需要影响 `init()` 之前的行为。采用手动解析是**最小侵入**的解决方案，无需为了少量早期参数改造整个 Commander 初始化流程。

### 2.2 Commander.js 的选项注册

主解析逻辑在 `run()` 函数中（`main.tsx:884`），使用 `@commander-js/extra-typings` 库注册所有选项：

```
// main.tsx:968-1010（关键片段）
program
  .name('claude')
  .description(`Claude Code - starts an interactive session by default, use -p/--print for non-interactive output`)
  .argument('[prompt]', 'Your prompt', String)
  .helpOption('-h, --help', 'Display help for command')
  .option('-p, --print', 'Print response and exit (useful for pipes)...')
  .option('--bare', 'Minimal mode: skip hooks, LSP, plugin sync...')
  .option('-c, --continue', 'Continue the most recent conversation...')
  .option('-r, --resume [value]', 'Resume a conversation by session ID...')
  .option('--model <model>', 'Model for the current session...')
  .option('--settings <file-or-json>', 'Path to a settings JSON file or a JSON string...')
  // ... 60+ 个选项
  .action(async (prompt, options) => {
    // 所有解析后的选项在此处理
  });
```

### 2.3 preAction 钩子：初始化与解析的分离

Commander.js 的 `preAction` 钩子在**任何 action 执行前**运行，但**不在 `--help` 显示时运行**。这为初始化逻辑提供了完美的切分点：

```
// main.tsx:907-960
program.hook('preAction', async thisCommand => {
  profileCheckpoint('preAction_start');
  // 等待 MDM 设置和钥匙串预读完成
  await Promise.all([ensureMdmSettingsLoaded(), ensureKeychainPrefetchCompleted()]);
  await init();  // 核心初始化（配置加载、设置合并）
  runMigrations(); // 数据库迁移
  void loadRemoteManagedSettings();  // 非阻塞：企业远程设置
  void loadPolicyLimits();          // 非阻塞：策略限制
});
```

**设计原因**：将初始化放在 `preAction` 中而非 `main()` 中，好处是 `--help` 不会触发任何初始化。如果用户在调试时运行 `claude --help`，不需要等待 MDM 读取、GrowthBook 初始化等全部流程，可以立即看到帮助文本。这对于 CLI 工具的可用性至关重要。

---

## 3. 短路径优化

### 3.1 短路径的核心：--continue / --resume

Claude Code 的「短路径」理念是：**用户想要继续上次对话，只需要敲最少的字**。两条核心捷径：

| 标志 | 用法 | 语义 |
|------|------|------|
| `-c` / `--continue` | `claude -c` | 继续当前目录最近一次会话 |
| `-r [搜索词]` / `--resume [搜索词]` | `claude -r` 或 `claude -r abc` | 恢复指定会话（支持模糊搜索） |

```
// main.tsx:988
.option('-c, --continue', 'Continue the most recent conversation in the current directory', () => true)
.option('-r, --resume [value]', 'Resume a conversation by session ID, or open interactive picker with optional search term', value => value || true)
```

在 action handler 中，这两个选项触发会话恢复流程（`main.tsx:3582-3686`）：

```
// 伪代码表示 resume/continue 的处理分支
if (options.continue) {
  // --continue: 找到最近一次会话
  const result = await loadConversationForResume(undefined, undefined);
  processedResume = await processResumedConversation(result, { ... });
  // 切换到该会话的上下文
  await switchToSession(processedResume.sessionId);
} else if (options.resume) {
  if (typeof options.resume === 'string') {
    // --resume <uuid>: 精确恢复
    const result = await loadConversationForResume(options.resume, undefined);
    processedResume = await processResumedConversation(result, { ... });
  } else {
    // --resume（无值）: 打开交互式选择器
    await launchResumeChooser(root, { ... });
  }
}
```

`launchResumeChooser`（`/src/cli/dialogLaunchers.ts`）在交互式模式下弹出会话列表 TUI，让用户用方向键选择要恢复的会话。

**设计原因**：`--continue` 是最短的「继续」路径——只需加一个 `-c`；而 `--resume` 支持两种模式：有值时直接恢复，无值时打开搜索式选择器。这种**带参/不带参的双语义设计**是短路径优化的经典手法。

### 3.2 非交互式短路径：-p / --print

`-p`（`--print`）是最重要的短路径之一：它让 Claude Code 在单次查询后立即退出，不启动完整 TUI：

```
// main.tsx:976
.option('-p, --print', 'Print response and exit (useful for pipes)...')
```

实现上，`-p` 模式将整个流程导向 `runHeadless()`（`cli/print.ts`），跳过了：

- REPL（TUI）初始化
- 交互式信任对话框
- 实时流式输出的终端渲染

```
// main.tsx:1782-2829
if (isNonInteractiveSession) {
  // 创建 headless store（无 UI 状态管理）
  const headlessStore = createStore(headlessInitialState, onChangeAppState);
  // 连接 MCP 服务器（非阻塞）
  await connectMcpBatch(regularMcpConfigs, 'regular');
  // 启动 headless 执行引擎
  void runHeadless(inputPrompt, () => headlessStore.getState(), ...);
  return;  // runHeadless 内部管理进程退出
}
```

**设计原因**：`-p` 模式是 Claude Code 作为**脚本工具**的核心能力。用户可以在 CI/CD 流水线、管道命令、脚本中调用 Claude Code，获得结构化输出（`--output-format json`）并立即继续后续步骤。这极大扩展了 Claude Code 的使用场景——从「交互式编码助手」变成「可编程的代码处理工具」。

### 3.3 最短初始化路径：--bare

`--bare` 是最短启动路径，用于对初始化完全不需要任何增强能力的场景：

```
// main.tsx:977
.option('--bare', 'Minimal mode: skip hooks, LSP, plugin sync, attribution, auto-memory...')
```

启用 `--bare` 时设置 `CLAUDE_CODE_SIMPLE=1`，跳过：

- 所有 Setup 和 SessionStart hooks
- LSP 服务器初始化
- 插件同步
- 自动记忆
- 背景预取（prefetch）
- Keychain 读取
- CLAUDE.md 自动发现

```
// main.tsx:390-410
if (isEnvTruthy(process.env.CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER) || isBareMode()) {
  return; // 跳过所有背景预取
}
```

**设计原因**：`--bare` 适用于自动化测试、极简脚本、CI 环境等场景。这些场景不需要任何「增强」能力，绕过它们可以显著减少启动延迟。在这些环境中，OAuth 和 keychain 也被跳过，认证仅依赖 `ANTHROPIC_API_KEY` 或 `--settings` 传入的 JSON 配置。

### 3.4 Deep Link 短路径

Claude Code 支持 `cc://` URL 协议，点击链接直接打开指定会话：

```
// main.tsx:614-645
const ccIdx = rawCliArgs.findIndex(a => a.startsWith('cc://') || a.startsWith('cc+unix://'));
if (ccIdx !== -1) {
  const { parseConnectUrl } = await import('./server/parseConnectUrl.js');
  const parsed = parseConnectUrl(ccUrl);
  if (rawCliArgs.includes('-p')) {
    // Headless: 重写为内部 'open' 子命令
    process.argv = [process.argv[0], process.argv[1], 'open', ccUrl, ...stripped];
  } else {
    // Interactive: 保留 URL 给后续处理
    _pendingConnect.url = parsed.serverUrl;
    _pendingConnect.authToken = parsed.authToken;
  }
}
```

**设计原因**：Deep link 实现了「一键恢复」——用户在浏览器或文档中看到一个会话链接，点击即可在本地 Claude Code 中打开对应会话，无需手动复制会话 ID 再调用 `claude -r <id>`。这是**面向终端用户」的极致短路径**。

---

## 4. 快速启动流程

### 4.1 启动流水线全景

综合以上设计，Claude Code 的完整启动流水线如下：

```
1. [main.tsx:579] main()
   │
   ├── 2. [main.tsx:1-20] 预加载（MDM + Keychain）
   │      （与模块导入并行）
   │
   ├── 3. [main.tsx:590] Windows 安全加固
   │
   ├── 4. [main.tsx:604] Deep link / URI 拦截
   │
   ├── 5. [main.tsx:704] SSH / Assistant 子命令剥离
   │
   ├── 6. [main.tsx:797] 模式检测（交互 vs 非交互）
   │
   ├── 7. [main.tsx:504] eagerLoadSettings()
   │      └── eagerParseCliFlag('--settings')
   │
   ├── 8. [main.tsx:854] run()
   │      │
   │      ├── 9. [main.tsx:884] Commander 初始化
   │      │
   │      └── 10. [main.tsx:904] preAction 钩子
   │             ├── await Promise.all([MDM, Keychain])
   │             ├── init()
   │             ├── runMigrations()
   │             └── 非阻塞: loadRemoteManagedSettings()
   │
   └── 11. [main.tsx:1006] action handler
          │
          ├── Interactive 路径:
          │    showSetupScreens() → 信任对话框 → REPL 渲染
          │    └── startDeferredPrefetches()  （渲染后）
          │
          └── Non-Interactive 路径 (-p):
               runHeadless() → 单次查询 → 进程退出
```

### 4.2 关键性能节点

| 节点 | 耗时控制手段 |
|------|-------------|
| 预加载并行化 | MDM/Keychain I/O 与模块导入重叠 |
| 初始化时机 | `preAction` 确保 `--help` 不触发初始化 |
| 设置提前解析 | `eagerLoadSettings()` 在 `init()` 前处理 `--settings` |
| MCP 连接 | `prefetchAllMcpResources()` 在信任对话框期间并行连接 |
| 背景预取延迟 | `startDeferredPrefetches()` 在首次渲染**之后**才启动 |
| Headless 跳过 | `-p` 模式完全跳过 TUI 初始化 |

### 4.3 背景预取的「不阻塞首帧」策略

Claude Code 最精妙的设计之一是 `startDeferredPrefetches()`（`main.tsx:388`）。它将大量非关键路径的工作推迟到首帧渲染之后：

```
// main.tsx:388-410
export function startDeferredPrefetches(): void {
  // 当测量启动性能时，跳过所有预取（避免 CPU 争用影响测量）
  if (isEnvTruthy(process.env.CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER) || isBareMode()) {
    return;
  }

  // 用户还在输入第一条消息，这些工作可以「隐形」完成
  void initUser();
  void getUserContext();
  void prefetchAwsCredentialsAndBedRockInfoIfSafe();
  void countFilesRoundedRg(getCwd(), AbortSignal.timeout(3000), []);
  void settingsChangeDetector.initialize();
  void skillChangeDetector.initialize();
}
```

**设计原因**：在交互式 CLI 中，用户在看到提示符和输入框后，通常会花几秒钟思考要问什么。这段「思考时间」恰好可以用来完成背景工作。通过将预取推迟到**首帧渲染之后**，Claude Code 的感知启动速度（「看到 TUI」的时刻）与实际初始化完成时间解耦，用户不会感到界面「卡在加载中」。

---

## 5. 设计原则总结

通过本章对 Claude Code 入口系统的分析，我们可以提炼出 CLI 工具设计的几条通用原则：

**原则一：分层解析，早期拦截特殊路径**

不是所有参数都适合统一的解析框架。协议 URL、子命令、影响初始化的配置参数需要在主流程之前被识别和处理。手动 `argv` 遍历 + Commander.js 的双阶段策略，是灵活性与规范性的平衡。

**原则二：短路径要真的短**

`claude -c` 三个字符完成会话继续，`claude -p "query"` 一次调用完成脚本集成。短路径的设计不仅是减少按键次数，更是**让高频操作无需理解完整参数系统就能完成**。

**原则三：交互式与非交互式的代码路径应尽早分叉**

通过 `isNonInteractive` 标志在 `main()` 中尽早判断，可以确保两种模式各自走优化后的路径。避免在初始化中期做分支判断，造成不必要的条件计算。

**原则四：预取要与用户感知「重叠」**

后台工作（认证预取、MCP 连接、文件统计）应该与用户的「思考时间」或「对话框等待时间」重叠，而非阻塞首帧渲染。`startDeferredPrefetches` 的设计是这一原则的教科书级实现。

**原则五：preAction 钩子是分离关注点的利器**

Commander.js 的 `preAction` 钩子提供了「所有命令执行前」的拦截点，非常适合放置初始化逻辑。它天然解决了 `--help` 不触发初始化的需求，无需额外的环境变量或条件判断。

---

## 思考题

1. 如果要新增一个 `--fast` 标志来同时启用 `-p`、`--bare` 和预设的 `--output-format json`，在现有架构下你会如何实现？请设计修改点和需要考虑的边界情况。

2. `eagerParseCliFlag()` 目前手动遍历 `argv`。如果要支持 `-abc` 这样的组合短选项（类似于 `tar -cvf`），需要如何扩展？

3. `startDeferredPrefetches()` 中的 `AbortSignal.timeout(3000)` 说明某些预取操作被设计为可取消的。为什么这对 CLI 应用很重要？

---

*本书第 1-5 章合集完。*

*** [第一部分：第一章至第五章完] ***

# 第六章 技术栈选型

> **本章作者**：代码驴
> **审计者**：狗头军师

技术栈的选择，是项目的第一次架构决策。它决定了开发者的工作体验、编译产物的性能边界、以及未来三年内技术团队是在高速公路上狂奔还是在泥潭里挣扎。本章将详细剖析 Claude Code 项目的技术选型决策：为何选择 TypeScript 作为核心语言、Bun runtime 的引入带来了哪些实质收益、关键依赖如何取舍，以及技术债务如何系统化管理。

---

## 6.1 为何选择 TypeScript

### 6.1.1 从 JavaScript 到 TypeScript 的必然之路

Claude Code 的全部源码均以 `.tsx` 和 `.ts` 为后缀——这本身并不稀奇，几乎所有现代 Node.js CLI 项目都这么做。但深入审视代码库后，你会发现 TypeScript 在这里不只是"类型注解的装饰"，而是深度嵌入到工程化的每一个层面。

**类型即文档**。当你打开 `src/main.tsx` 文件的前几行，就会看到这样的导入声明：

```
import { type DownloadResult, downloadSessionFiles, type FilesApiConfig, parseFileSpecs } from './services/api/filesApi.js';
```

注意 `type` 关键字的使用——这并非冗余代码，而是 TypeScript 编译器的 `import type` 语法，它告诉编译器 `DownloadResult` 和 `FilesApiConfig` 仅作为类型使用，编译后不产生任何实体代码。对于一个需要构建为单文件可执行文件的 CLI 工具而言，每个字节的 bundle 大小都直接影响冷启动时间，`import type` 的使用是严格且系统化的。

**类型驱动的重构安全网**。在 `src/tools.ts` 中，大量函数签名都包含复杂的泛型约束和交叉类型：

```
export function getTools(toolPermissionContext: ToolPermissionContext): Tool[] {
  // ...
}
```

当业务逻辑发生变化时，TypeScript 编译器会在构建阶段就捕获类型不匹配，而不是等到运行时才发现问题。这对于一个每天处理用户文件读写、执行 shell 命令的 CLI 工具而言，是最后一道安全防线。

### 6.1.2 TypeScript 的编译时收益

选择 TypeScript 而非纯 JavaScript，核心收益在于**编译时类型检查**将 runtime 错误转化为编译错误：

```
// src/main.tsx
const CURRENT_MIGRATION_VERSION = 11;

function runMigrations(): void {
  if (getGlobalConfig().migrationVersion !== CURRENT_MIGRATION_VERSION) {
    migrateAutoUpdatesToSettings();
    migrateBypassPermissionsAcceptedToSettings();
    migrateEnableAllProjectMcpServersToSettings();
    // ... 更多迁移函数
    saveGlobalConfig(prev => prev.migrationVersion === CURRENT_MIGRATION_VERSION ? prev : {
      ...prev,
      migrationVersion: CURRENT_MIGRATION_VERSION
    });
  }
}
```

这里的 `CURRENT_MIGRATION_VERSION` 是一个常量，当版本号变化时，TypeScript 能够确保所有迁移函数被正确调用，且 `saveGlobalConfig` 的参数类型与全局配置类型严格匹配。如果开发者误将 `migrationVersion` 赋值为字符串而非数字，编译器会立即报错。

### 6.1.3 TypeScript 在 bundler 层的优势

项目使用 `bun:bundle`（第21行）进行打包：

```
import { feature } from 'bun:bundle';
```

Bun 的 bundler 能够进行**死代码消除（Dead Code Elimination）**，而精确的类型信息是 DCE 的前提。当代码中的某个分支被 `feature('COORDINATOR_MODE')` 这样的编译时常量守卫包裹时，Bun 的 bundler 能准确识别整个分支都是死代码，因为 TypeScript 的类型系统确保了分支条件的可折叠性。

---

## 6.2 Bun 的引入与收益

### 6.2.1 Bun 而非 Node.js：不是选择，是战略

在 `src/main.tsx` 第21行，你能看到 Bun 的首次登场：

```
import { feature } from 'bun:bundle';
```

这个导入并非示例代码，而是项目实际使用 Bun bundler 进行编译的明确信号。在第196行，又出现了：

```
import { isRunningWithBun } from './utils/bundledMode.js';
```

以及在调试检测函数中：

```
function isBeingDebugged() {
  const isBun = isRunningWithBun();
  // ...
}
```

这意味着项目**同时兼容 Bun runtime 和 Node.js runtime**，但默认构建目标是 Bun 的 bundler 体系。

### 6.2.2 启动性能：MDM 和 Keychain 的并行预取

Bun 带来的最显著收益是**启动性能优化**。请看 `src/main.tsx` 开头的这段代码：

```
// These side-effects must run before all other imports:
// 1. profileCheckpoint marks entry before heavy module evaluation begins
// 2. startMdmRawRead fires MDM subprocesses (plutil/reg query) so they run in
//    parallel with the remaining ~135ms of imports below
// 3. startKeychainPrefetch fires both macOS keychain reads (OAuth + legacy API
//    key) in parallel — isRemoteManagedSettingsEligible() otherwise reads them
//    sequentially via sync spawn inside applySafeConfigEnvironmentVariables()
//    (~65ms on every macOS startup)
import { profileCheckpoint, profileReport } from './utils/startupProfiler.js';

// eslint-disable-next-line custom-rules/no-top-level-side-effects
profileCheckpoint('main_tsx_entry');
import { startMdmRawRead } from './utils/settings/mdm/rawRead.js';

// eslint-disable-next-line custom-rules/no-top-level-side-effects
startMdmRawRead();
import { ensureKeychainPrefetchCompleted, startKeychainPrefetch } from './utils/secureStorage/keychainPrefetch.js';

// eslint-disable-next-line custom-rules/no-top-level-side-effects
startKeychainPrefetch();
```

注释中有一个关键数据点：**~135ms**。这是模块评估的基准耗时，而 MDM 和 Keychain 的预取操作被精心设计为与这 135ms 并行执行。这意味着在 Node.js 中可能串行执行的 I/O 操作（MDM 读取约 135ms + Keychain 约 65ms = 200ms 总耗时），在 Bun 的并行 I/O 机制下被压缩到约 135ms。

### 6.2.3 Bun 的 FFI 与原生能力

Bun 原生支持 `bun:ffi`（Foreign Function Interface），这使得项目能够在 JavaScript 层直接调用 C/C++ 库，无需编写完整的 Node.js 原生addon。在跨平台（macOS/Windows/Linux）的场景下，这是一个巨大的工程复杂度削减。

同时，`isRunningWithBun()` 函数的存在说明项目在设计时考虑了**渐进式迁移路径**——既可以跑在 Bun 上，也可以跑在 Node.js 上，但构建产物的优化目标始终是 Bun。

### 6.2.4 ESM-First 与 lodash-es

在 `src/main.tsx` 第25-27行：

```
import mapValues from 'lodash-es/mapValues.js';
import pickBy from 'lodash-es/pickBy.js';
import uniqBy from 'lodash-es/uniqBy.js';
```

项目使用的是 `lodash-es` 而非传统的 `lodash`。`lodash-es` 是 lodash 的 ES Modules 版本，支持**Tree Shaking**——当使用命名导入 `import mapValues from 'lodash-es/mapValues.js'` 时，Bun 的 bundler 只能打包实际用到的函数，而不是整个 lodash 库。对于一个 CLI 工具而言，这是 bundle 大小优化的关键一环。

---

## 6.3 关键依赖选择

### 6.3.1 React + Ink：CLI 的界面革命

传统的 CLI 工具使用 ANSI escape codes 或者第三方终端格式化库（如 `blessed`）来构建交互界面。Claude Code 选择了一条截然不同的路：**React + Ink**。

在 `src/main.tsx` 中，你能看到 Ink 的使用：

```
import type { Root } from './ink.js';
```

Ink 是 "React for CLIs"——它允许开发者使用 React 的组件模型和声明式语法来构建终端界面。这带来的收益是：

1. **组件化复用**：Claude Code 的 UI 组件（对话框、进度条、表格等）可以像 Web 前端一样被复用和组合
2. **状态驱动渲染**：`src/state/AppStateStore.ts` 中的状态管理直接驱动 Ink 渲染，当状态变化时终端 UI 自动更新
3. **热模块替换友好**：Ink 的虚拟 DOM 机制使得 UI 更新无需重绘整个终端缓冲区

对于一个需要频繁更新多区域终端界面的交互式 CLI，这个选择将 UI 开发的效率提升了数倍。

### 6.3.2 @commander-js/extra-typings：企业级 CLI 参数解析

命令行工具的参数解析看似简单，实则复杂——需要支持长短选项、可变参数、默认值、类型校验、帮助文本生成、嵌套子命令。Claude Code 选择 `@commander-js/extra-typings` 而非原生的 `commander.js`：

```
import { Command as CommanderCommand, InvalidArgumentError, Option } from '@commander-js/extra-typings';
```

`@commander-js/extra-typings` 提供了完整的 TypeScript 类型推导。以 `--settings` 选项为例：

```
.option('--settings <file-or-json>', 'Path to a settings JSON file or a JSON string to load additional settings from');
```

类型推导确保了当开发者使用 `.getOptionValue('settings')` 时，返回值的类型是 `string | undefined`，而不是宽泛的 `any`。这使得后续的 JSON 解析逻辑能够进行严格的类型守卫。

### 6.3.3 Chalk：终端色彩的品牌化

在 `src/main.tsx` 中，Chalk 用于终端输出格式化：

```
import chalk from 'chalk';
// 使用示例
process.stderr.write(chalk.red(`Error: Invalid session ID. Must be a valid UUID.\n`));
```

Chalk 的选择标准是**运行时零开销**——Chalk 本身是一个纯字符串模板库，不涉及任何终端 API 调用（在非 TTY 环境下自动跳过着色）。这确保了错误信息在 CI 日志和终端中的表现一致。

### 6.3.4 Feature Flag 系统的原生支持

项目内建了 feature flag 机制：

```
const coordinatorModeModule = feature('COORDINATOR_MODE') ? require('./coordinator/coordinatorMode.js') : null;
```

这个 `feature()` 函数来自 `bun:bundle`，是一个**编译时常量**。这意味着无论 feature flag 如何设置，bundler 都能在构建时消除未激活分支的代码——哪怕 JavaScript 源码中存在该分支，产物中也完全不会包含它。这是一种零 runtime 开销的 A/B 测试机制。

---

## 6.4 技术债务管理

### 6.4.1 迁移框架：系统化的版本演进

技术债务最大的危害不是债务本身，而是**债务的无序累积**。Claude Code 建立了一套系统化的迁移框架来解决这个问题。在 `src/main.tsx` 第325行：

```
const CURRENT_MIGRATION_VERSION = 11;

function runMigrations(): void {
  if (getGlobalConfig().migrationVersion !== CURRENT_MIGRATION_VERSION) {
    migrateAutoUpdatesToSettings();
    migrateBypassPermissionsAcceptedToSettings();
    migrateEnableAllProjectMcpServersToSettings();
    resetProToOpusDefault();
    migrateSonnet1mToSonnet45();
    migrateLegacyOpusToCurrent();
    migrateSonnet45ToSonnet46();
    migrateOpusToOpus1m();
    migrateReplBridgeEnabledToRemoteControlAtStartup();
    if (feature('TRANSCRIPT_CLASSIFIER')) {
      resetAutoModeOptInForDefaultOffer();
    }
    if ("external" === 'ant') {
      migrateFennecToOpus();
    }
    saveGlobalConfig(prev => prev.migrationVersion === CURRENT_MIGRATION_VERSION ? prev : {
      ...prev,
      migrationVersion: CURRENT_MIGRATION_VERSION
    });
  }
}
```

每当我们需要更改配置格式、模型名称重映射、权限系统重构时，都通过新增迁移函数来解决。这些迁移函数：

1. **幂等性**：多次运行同一迁移不会产生副作用
2. **版本化**：每次迁移递增 `CURRENT_MIGRATION_VERSION`，确保每次启动只执行必要的迁移
3. **可追溯**：迁移函数名称清晰描述了变更内容（如 `migrateSonnet1mToSonnet45`）

### 6.4.2 异步迁移：非阻塞式演进

部分迁移被设计为"fire and forget"——即异步执行，不阻塞主流程：

```
// Async migration - fire and forget since it's non-blocking
migrateChangelogFromConfig().catch(() => {
  // Silently ignore migration errors - will retry on next startup
});
```

这避免了在启动关键路径上堆积耗时操作，保证了 CLI 的冷启动时间始终可控。

### 6.4.3 调试模式的严格守卫

在 `src/main.tsx` 第266行，有一个容易被忽视但至关重要的安全检查：

```
// Exit if we detect node debugging or inspection
if ("external" !== 'ant' && isBeingDebugged()) {
  process.exit(1);
}
```

这并非过度防御。项目作为 AI coding assistant，拥有对文件系统和 shell 命令的完全访问权限。如果有人在调试器中单步跟踪代码，任意断点位置的变量内容都可能包含 API key、OAuth token 或用户文件内容。这个守卫确保了**调试模式在生产环境中不可用**，将调试信息泄露的风险彻底消除。

---

## 6.5 本章小结

Claude Code 的技术栈选择并非随波逐流，而是每个决策背后都有清晰的收益分析：

| 技术选型 | 核心收益 | 决策依据 |
|---------|---------|---------|
| TypeScript | 编译时类型检查、死代码消除、IDE 支持 | 大型代码库需要可维护性保障 |
| Bun runtime | 并行 I/O、FFI、快速 bundler | ~200ms → ~135ms 启动优化 |
| React + Ink | 组件化 UI、状态驱动渲染 | CLI 界面复杂度的可持续开发 |
| @commander-js/extra-typings | 完整 TS 类型推导、子命令体系 | 企业级 CLI 需要严谨的参数校验 |
| lodash-es | Tree Shaking 支持 | 减少 bundler 产物体积 |
| 内建 Feature Flag | 零 runtime 开销的 A/B 测试 | 多租户环境下差异化功能交付 |
| 迁移框架 | 幂等、版本化、可追溯的配置演进 | 避免技术债务无序累积 |

下一章将深入探讨 Claude Code 的**工具系统架构**，了解它如何将 AI 模型的推理能力与文件系统的实际操作连接起来。

---

# 第七章 工具系统架构

## 7.1 设计思想

### 为什么需要工具系统

Claude Code 的核心价值在于让大语言模型（LLM）能够**实际操作代码**——而不是仅仅生成文本建议。要做到这一点，模型必须能够执行真实世界中的操作：读取文件、运行 shell 命令、搜索代码、编辑文本、启动子任务等。这些操作需要一个**统一、可扩展、类型安全**的抽象层来管理，这正是工具系统的设计目标。

如果没有统一的工具抽象，每种工具（bash、read、edit 等）都会是独立实现的孤岛。这会导致以下问题：

1. **接口不一致**：每种工具的调用方式、参数格式、返回结构完全不同，模型和行为代码都需要为每种工具单独适配。
2. **权限管理困难**：权限系统无法统一处理"什么工具可以做什么操作"这样的策略，需要在每种工具内部重复实现。
3. **进度展示混乱**：没有统一的进度回调机制，每种工具的 UI 渲染逻辑散落在各处。
4. **新增工具成本高**：每添加一个新工具需要重新理解整个交互模式，无法复用现有基础设施。

Claude Code 的工具系统通过定义 **标准化的 Tool 接口**，将所有工具的共性提取到统一基座上，让每种具体工具只负责实现自己的"差异部分"——输入验证逻辑、实际执行逻辑、结果渲染逻辑。

### Tool.ts 中的标准化接口

`Tool.ts`（`src/Tool.ts`）是这个系统的核心文件，定义了工具的标准化接口。理解这个文件是理解整个工具系统的基础。

Claude Code 使用 **TypeScript 泛型** 来确保类型安全。以下是 `Tool` 接口（第 362 行起）的核心字段摘要，按源码顺序呈现：

```
// src/Tool.ts 第 362 行起
export type Tool<
  Input extends AnyObject = AnyObject,
  Output = unknown,
  P extends ToolProgressData = ToolProgressData,
> = {
  // === 标识与查找 ===
  aliases?: string[]               // 工具别名（向后兼容重命名工具）
  searchHint?: string              // ToolSearch 关键词匹配短语（3-10词）
  readonly name: string            // 工具唯一名称（在 mcpInfo? 之后）

  // === 核心执行 ===
  call(
    args: z.infer<Input>,
    context: ToolUseContext,
    canUseTool: CanUseToolFn,
    parentMessage: AssistantMessage,
    onProgress?: ToolCallProgress<P>,
  ): Promise<ToolResult<Output>>

  description(
    input: z.infer<Input>,
    options: {
      isNonInteractiveSession: boolean
      toolPermissionContext: ToolPermissionContext
      tools: Tools
    },
  ): Promise<string>

  // === Schema ===
  readonly inputSchema: Input
  readonly inputJSONSchema?: ToolInputJSONSchema  // MCP 工具的 JSON Schema
  outputSchema?: z.ZodType<unknown>

  // === 行为特性 ===
  inputsEquivalent?(a: z.infer<Input>, b: z.infer<Input>): boolean
  isConcurrencySafe(input: z.infer<Input>): boolean
  isEnabled(): boolean
  isReadOnly(input: z.infer<Input>): boolean
  isDestructive?(input: z.infer<Input>): boolean
  interruptBehavior?(): 'cancel' | 'block'      // 工具运行中收到新消息时的行为
  isSearchOrReadCommand?(input: z.infer<Input>): { isSearch: boolean; isRead: boolean; isList?: boolean }
  isOpenWorld?(input: z.infer<Input>): boolean
  requiresUserInteraction?(): boolean
  isMcp?: boolean
  isLsp?: boolean
  readonly shouldDefer?: boolean                  // 是否延迟加载（需要 ToolSearch）
  readonly alwaysLoad?: boolean                  // 是否永不延迟（turn 1 必须看到）
  mcpInfo?: { serverName: string; toolName: string }

  // === 资源限制 ===
  maxResultSizeChars: number
  readonly strict?: boolean

  // === 权限与验证 ===
  validateInput?(input: z.infer<Input>, context: ToolUseContext): Promise<ValidationResult>
  checkPermissions(
    input: z.infer<Input>,
    context: ToolUseContext,
  ): Promise<PermissionResult>

  // === 生命周期钩子 ===
  prompt(options: {
    getToolPermissionContext: () => Promise<ToolPermissionContext>
    tools: Tools
    agents: AgentDefinition[]
    allowedAgentTypes?: string[]
  }): Promise<string>                            // 生成模型看到的工具提示词

  // === 展示相关 ===
  userFacingName(input: Partial<z.infer<Input>> | undefined): string
  userFacingNameBackgroundColor?(input: Partial<z.infer<Input>> | undefined): keyof Theme | undefined
  getToolUseSummary?(input: Partial<z.infer<Input>> | undefined): string | null  // 紧凑视图摘要
  getActivityDescription?(input: Partial<z.infer<Input>> | undefined): string | null  // 旋转器描述
  toAutoClassifierInput(input: z.infer<Input>): unknown
  mapToolResultToToolResultBlockParam(content: Output, toolUseID: string): ToolResultBlockParam
  renderToolResultMessage?(
    content: Output,
    progressMessagesForMessage: ProgressMessage<P>[],
    options: {
      style?: 'condensed'
      theme: ThemeName
      tools: Tools
      verbose: boolean
      isTranscriptMode?: boolean
      isBriefOnly?: boolean
      input?: unknown                            // 原始 tool_use 输入（用于摘要）
    },
  ): React.ReactNode
  extractSearchText?(out: Output): string
  renderToolUseMessage(                          // 注意：这是必需方法（无 ?）
    input: Partial<z.infer<Input>>,
    options: { theme: ThemeName; verbose: boolean; commands?: Command[] },
  ): React.ReactNode
  isResultTruncated?(out: Output): boolean
  isTransparentWrapper?(): boolean
}
```

**设计原因**：这个接口涵盖了工具的完整生命周期：

- **注册阶段**：`name`、`inputSchema`、`aliases`、`searchHint` 告诉系统"这个工具叫什么、通过什么关键词能找到它、接受什么参数"
- **准备阶段**：`description()`、`prompt()` 生成模型看到的工具描述和提示词
- **执行阶段**：`call()` 是实际执行逻辑，`validateInput()`/`checkPermissions()` 处理验证与权限
- **展示阶段**：多个 `render*` 方法、`getToolUseSummary`、`getActivityDescription` 等负责在 UI 中渲染工具的使用和结果
- **元数据**：`isReadOnly()`、`isConcurrencySafe()`、`interruptBehavior()` 等告诉系统工具的行为特性

### Builder 模式：buildTool 工厂函数

直接实现 `Tool` 接口非常繁琐——一个完整的工具需要实现十几个方法，其中大部分都有"安全默认值"。Claude Code 通过 **Builder 模式** 解决了这个问题：`buildTool` 工厂函数。

```
// src/Tool.ts 第 783 行
export function buildTool<D extends AnyToolDef>(def: D): BuiltTool<D> {
  return {
    ...TOOL_DEFAULTS,
    userFacingName: () => def.name,
    ...def,
  } as BuiltTool<D>
}
```

`TOOL_DEFAULTS` 定义了所有默认方法：

```
// src/Tool.ts 第 757 行
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?: unknown) => false,
  isReadOnly: (_input?: unknown) => false,
  isDestructive: (_input?: unknown) => false,
  checkPermissions: (
    input: { [key: string]: unknown },
    _ctx?: ToolUseContext,
  ): Promise<PermissionResult> =>
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: (_input?: unknown) => '',
  userFacingName: (_input?: unknown) => '',
}
```

**设计原因**：

- **fail-closed 安全默认值**：默认认为工具**不**并发安全、**不是**只读——这样新工具默认需要权限检查。
- **单点维护**：所有默认行为集中在一处，不会出现"某工具忘记实现某个方法导致奇怪行为"的问题。
- **类型级别的合并**：`BuiltTool<D>` 类型通过 TypeScript 高级映射类型，将默认方法与用户定义的方法合并——如果用户提供了 `isReadOnly`，用户版本胜出；如果没提供，`TOOL_DEFAULTS` 版本填充。

所有工具导出都经过 `buildTool`：

```
// src/tools.ts（贯穿全文的工具注册）
import { BashTool } from './tools/BashTool/BashTool.js'
import { FileReadTool } from './tools/FileReadTool/FileReadTool.js'
import { FileEditTool } from './tools/FileEditTool/FileEditTool.js'
// ... 更多工具
export const BashTool = buildTool({ name: BASH_TOOL_NAME, ... })
```

## 7.2 核心接口定义

### ToolDef：工具定义的约束类型

`ToolDef` 是调用 `buildTool` 时传入对象的类型约束。它继承 `Tool` 的全部字段，但将一些"可默认实现"的方法标记为可选：

```
// src/Tool.ts 第 721 行附近（实际在 DefaultableToolKeys 之后）
export type ToolDef<
  Input extends AnyObject = AnyObject,
  Output = unknown,
  P extends ToolProgressData = ToolProgressData,
> = Omit<Tool<Input, Output, P>, DefaultableToolKeys> &
  Partial<Pick<Tool<Input, Output, P>, DefaultableToolKeys>>
```

其中 `DefaultableToolKeys` 包括：

```
// src/Tool.ts 第 707 行
type DefaultableToolKeys =
  | 'isEnabled'
  | 'isConcurrencySafe'
  | 'isReadOnly'
  | 'isDestructive'
  | 'checkPermissions'
  | 'toAutoClassifierInput'
  | 'userFacingName'
```

### ToolResult：工具执行结果的标准化包装

工具执行后返回 `ToolResult<Output>`：

```
// src/Tool.ts 第 321 行
export type ToolResult<T> = {
  data: T
  newMessages?: (
    | UserMessage
    | AssistantMessage
    | AttachmentMessage
    | SystemMessage
  )[]
  contextModifier?: (context: ToolUseContext) => ToolUseContext
  mcpMeta?: {
    _meta?: Record<string, unknown>
    structuredContent?: Record<string, unknown>
  }
}
```

**设计原因**：`data` 是工具的核心输出；`newMessages` 允许工具在执行过程中插入新消息（比如 Bash 执行时输出进度）；`contextModifier` 允许工具修改执行上下文；`mcpMeta` 用于 MCP 协议元数据透传。

### ToolUseContext：贯穿执行上下文的依赖注入

`ToolUseContext` 是工具执行时的"万能上下文"，通过依赖注入的方式将所有系统能力传递给工具：

```
// src/Tool.ts 第 158 行
export type ToolUseContext = {
  options: {
    commands: Command[]
    debug: boolean
    mainLoopModel: string
    tools: Tools
    verbose: boolean
    thinkingConfig: ThinkingConfig
    mcpClients: MCPServerConnection[]
    mcpResources: Record<string, ServerResource[]>
    isNonInteractiveSession: boolean
    agentDefinitions: AgentDefinitionsResult
    maxBudgetUsd?: number
    refreshTools?: () => Tools
  }
  abortController: AbortController
  readFileState: FileStateCache
  getAppState(): AppState
  setAppState(f: (prev: AppState) => AppState): void
  setToolJSX?: SetToolJSXFn
  addNotification?: (notif: Notification) => void
  messages: Message[]
  // ... 更多字段
}
```

**设计原因**：将所有依赖集中在一个 context 对象中，而不是散落在全局状态或构造函数参数中。这使得工具的单元测试可以轻松 mock 整个 context，也使得工具可以在不同执行环境中复用。

### ToolInputJSONSchema：MCP 工具的 JSON Schema 支持

```
// src/Tool.ts 第 15 行
export type ToolInputJSONSchema = {
  [x: string]: unknown
  type: 'object'
  properties?: {
    [x: string]: unknown
  }
}
```

**设计原因**：MCP（Model Context Protocol）服务器提供的工具使用原生 JSON Schema 格式，而不是 Zod schema。这个字段允许 MCP 工具直接声明其输入格式，无需从 Zod schema 转换。

## 7.3 Lazy Schema 与循环依赖

### 循环依赖的根源

工具系统面临一个经典的工程难题：**循环依赖**。

`tools.ts` 文件负责注册和分发所有工具，它需要导入每种具体工具：

```
// src/tools.ts
import { BashTool } from './tools/BashTool/BashTool.js'
import { FileReadTool } from './tools/FileReadTool/FileReadTool.js'
import { AgentTool } from './tools/AgentTool/AgentTool.js'
// ...
```

但具体工具（如 `BashTool`）在定义自己的 `inputSchema` 时，需要使用 Zod schema，而 Zod schema 的构建可能依赖于整个系统中的其他类型定义——这些类型定义本身又可能导入 `Tool.ts`，最终形成循环：

```
Tool.ts → 导入各种 types → types 中某处 → 导入 Tool.ts
```

更实际的问题是：**Zod schema 的构建（`.strictObject()`、`.describe()` 等）在模块加载时就执行了**。如果 `BashTool.tsx` 在模块顶层定义 schema，而这个 schema 的构建过程中触发了对其他模块的导入，而这些模块又尚未初始化，就会导致运行时错误。

### lazySchema 的解决方案

Claude Code 引入了一个极简但高效的解决方案——`lazySchema`：

```
// src/utils/lazySchema.ts
export function lazySchema<T>(factory: () => T): () => T {
  let cached: T | undefined
  return () => (cached ??= factory())
}
```

它返回一个**记忆化的工厂函数**：第一次调用时执行 factory 并缓存结果，后续调用直接返回缓存——**缓存的是工厂函数的返回值（即 Zod schema 对象），后续访问直接返回该缓存对象，而非再次调用工厂**。

在 `BashTool` 中的使用方式：

```
// src/tools/BashTool/BashTool.tsx 第 227 行
const fullInputSchema = lazySchema(() => z.strictObject({
  command: z.string().describe('The command to execute'),
  timeout: semanticNumber(z.number().optional())
    .describe(`Optional timeout in milliseconds (max ${getMaxTimeoutMs()})`),
  description: z.string().optional()
    .describe(`Clear, concise description...`),
  run_in_background: semanticBoolean(z.boolean().optional())
    .describe('Set to true to run this command in the background.'),
  dangerouslyDisableSandbox: semanticBoolean(z.boolean().optional())
    .describe('Set this to true to dangerously override sandbox mode...'),
  _simulatedSedEdit: z.object({...}).optional()
    .describe('Internal: pre-computed sed edit result from preview')
}))

// 第 254 行附近：根据环境条件动态剔除某些字段
const inputSchema = lazySchema(() =>
  isBackgroundTasksDisabled
    ? fullInputSchema().omit({ run_in_background: true, _simulatedSedEdit: true })
    : fullInputSchema().omit({ _simulatedSedEdit: true })
)

// 第 279 行附近：outputSchema 同样使用 lazySchema
const outputSchema = lazySchema(() => z.object({
  stdout: z.string().describe('The standard output of the command'),
  stderr: z.string().describe('The standard error output of the command'),
  rawOutputPath: z.string().optional(),
  interrupted: z.boolean().describe('Whether the command was interrupted'),
  // ...
}))

// 第 478 行附近：使用时才通过 getter 触发实际构建
get inputSchema(): InputSchema {
  return inputSchema()  // 首次调用在这里触发 factory，缓存返回值
}
```

**为什么用 getter 而不是直接导出**：`inputSchema` 字段在 `Tool` 接口中定义为类型 `Input`，但 `BashTool` 通过 getter 重写，在运行时惰性求值。这意味着模块加载时 `BashTool` 本身已经被 `buildTool` 包装好了，但 schema 的实际构建被推迟到第一次访问 `inputSchema` 属性时——此时所有相关模块已完成初始化。

### 解决的具体问题

1. **打破初始化顺序依赖**：schema 构建所需的类型和常量在模块首次访问 `inputSchema()` 时已经完成初始化，避免了"访问时尚未加载"的错误。
2. **条件化 schema**：同一个工具可以根据环境变量（`isBackgroundTasksDisabled`）动态生成不同版本的 schema——生产环境去掉某些敏感字段，测试环境保留全部。
3. **性能优化**：如果某个工具从未被使用，其 schema 永远不会被构建，节省了初始化时间和内存。

## 7.4 工具注册机制

### tools.ts：工具的全局注册表

`src/tools.ts` 是整个工具系统的"中央注册处"。它负责：

1. **导入所有内置工具**（直接或条件导入）
2. **定义工具池的来源**（`getAllBaseTools()`）
3. **根据权限上下文过滤工具**（`getTools()`）
4. **合并 MCP 工具**（`assembleToolPool()`）

### getAllBaseTools：完整工具列表

```
// src/tools.ts 第 193 行
export function getAllBaseTools(): Tools {
  return [
    AgentTool,
    TaskOutputTool,
    BashTool,
    // 当系统有内置搜索工具时跳过独立的 Glob/Grep 工具
    ...(hasEmbeddedSearchTools() ? [] : [GlobTool, GrepTool]),
    ExitPlanModeV2Tool,
    FileReadTool,
    FileEditTool,
    FileWriteTool,
    NotebookEditTool,
    WebFetchTool,
    TodoWriteTool,
    WebSearchTool,
    TaskStopTool,
    AskUserQuestionTool,
    SkillTool,
    EnterPlanModeTool,
    // 根据 USER_TYPE 环境变量决定是否包含 ant 专属工具
    ...(process.env.USER_TYPE === 'ant' && REPLTool ? [REPLTool] : []),
    ...(process.env.USER_TYPE === 'ant' ? [ConfigTool] : []),
    ...(process.env.USER_TYPE === 'ant' ? [TungstenTool] : []),
    // 特性开关控制的工具
    ...(isTodoV2Enabled()
      ? [TaskCreateTool, TaskGetTool, TaskUpdateTool, TaskListTool]
      : []),
    ...(isEnvTruthy(process.env.ENABLE_LSP_TOOL) ? [LSPTool] : []),
    // ... 更多条件工具
  ]
}
```

**设计原因**：

- **Dead Code Elimination（死代码消除）**：打包器通过 `process.env` 条件导入，在发布版本中完全剔除未启用的工具代码，减少二进制体积。
- **特性开关（Feature Flags）**：通过 `feature()` 和 `isEnvTruthy()` 控制工具可用性，不需要修改代码或重新编译。

### getTools：根据权限上下文分发

```
// src/tools.ts 第 271 行
export const getTools = (permissionContext: ToolPermissionContext): Tools => {
  // 简单模式：只包含 Bash、Read、Edit
  if (isEnvTruthy(process.env.CLAUDE_CODE_SIMPLE)) {
    // --bare + REPL 模式：REPL 包装了 Bash/Read/Edit 等工具，
    // 返回 REPLTool 而非原始工具。这与非 bare 路径的行为一致——
    // REPL 启用时同样会隐藏 REPL_ONLY_TOOLS。
    if (isReplModeEnabled() && REPLTool) {
      const replSimple: Tool[] = [REPLTool]
      if (
        feature('COORDINATOR_MODE') &&
        coordinatorModeModule?.isCoordinatorMode()
      ) {
        replSimple.push(TaskStopTool, getSendMessageTool())
      }
      return filterToolsByDenyRules(replSimple, permissionContext)
    }
    const simpleTools: Tool[] = [BashTool, FileReadTool, FileEditTool]
    // 当协调者模式也激活时，加入 AgentTool 和 TaskStopTool
    if (
      feature('COORDINATOR_MODE') &&
      coordinatorModeModule?.isCoordinatorMode()
    ) {
      simpleTools.push(AgentTool, TaskStopTool, getSendMessageTool())
    }
    return filterToolsByDenyRules(simpleTools, permissionContext)
  }

  // 正常模式：获取所有工具并过滤
  const specialTools = new Set([
    ListMcpResourcesTool.name,
    ReadMcpResourceTool.name,
    SYNTHETIC_OUTPUT_TOOL_NAME,
  ])

  let allowedTools = getAllBaseTools()
    .filter(tool => !specialTools.has(tool.name))
  allowedTools = filterToolsByDenyRules(allowedTools, permissionContext)

  // REPL 模式下隐藏原始工具（通过 REPL 包装器统一暴露）
  // 它们仍然可以通过 VM 上下文在 REPL 内部访问
  if (isReplModeEnabled()) {
    const replEnabled = allowedTools.some(tool =>
      toolMatchesName(tool, REPL_TOOL_NAME),
    )
    if (replEnabled) {
      allowedTools = allowedTools.filter(
        tool => !REPL_ONLY_TOOLS.has(tool.name),
      )
    }
  }

  // 最后过滤掉未启用（isEnabled() 返回 false）的工具
  const isEnabled = allowedTools.map(_ => _.isEnabled())
  return allowedTools.filter((_, i) => isEnabled[i])
}
```

**REPL 模式的特殊处理**：
- `--bare` 简单模式下，如果同时启用了 REPL 模式，则返回 `REPLTool` 而非原始的 Bash/Read/Edit 工具
- 正常模式下，REPL 启用时会从工具列表中过滤掉 `REPL_ONLY_TOOLS`（Bash、Read、Edit 等），因为这些工具已由 REPL 包装统一暴露
- `REPL_ONLY_TOOLS` 是一组原始工具名称（`'Bash'`、`'Read'`、`'Edit'` 等），REPL 模式下这些工具不对外直接可见

### assembleToolPool：合并内置工具与 MCP 工具

MCP（Model Context Protocol）允许接入第三方工具服务器。这些工具与内置工具需要统一合并，但存在命名冲突风险：

```
// src/tools.ts 第 345 行
export function assembleToolPool(
  permissionContext: ToolPermissionContext,
  mcpTools: Tools,
): Tools {
  const builtInTools = getTools(permissionContext)
  const allowedMcpTools = filterToolsByDenyRules(mcpTools, permissionContext)

  // 排序以保证 prompt cache 稳定性
  const byName = (a: Tool, b: Tool) => a.name.localeCompare(b.name)
  return uniqBy(
    [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
    'name',
  )
}
```

**设计原因**：

- **去重策略**：当内置工具与 MCP 工具同名时，**内置工具优先**（`uniqBy` 保留首次出现的，即内置工具）。
- **排序稳定性**：按名称排序保证工具列表顺序稳定，有助于 LLM 的上下文缓存（prompt cache）命中。
- **统一分发**：无论工具来自内置实现还是 MCP 服务器，调用方使用统一的 `Tools` 类型，不需要关心来源差异。

## 7.5 实操指南：构建自定义工具

下面我们以一个简化版的"获取当前时间"工具为例，演示如何添加一个完整的自定义工具。

### 步骤 1：创建工具文件

在 `src/tools/` 下创建 `TimeTool/` 目录：

```
// src/tools/TimeTool/TimeTool.tsx

import * as React from 'react'
import { z } from 'zod/v4'
import {
  buildTool,
  type ToolDef,
  type ThemeName,
  type Command,
  type Tools,
  type ProgressMessage,
  type ToolUseContext,
  type ToolCallProgress,
  type AssistantMessage,
  type CanUseToolFn,
  type ToolPermissionContext,
  type ToolResult,
  type PermissionResult,
} from '../../Tool.js'

// 第 1 步：定义输入和输出的 Zod Schema
const inputSchema = z.strictObject({
  format: z
    .enum(['iso', 'unix', 'friendly'])
    .optional()
    .describe('Output format: iso (ISO 8601), unix (seconds), friendly (human-readable)'),
  timezone: z
    .string()
    .optional()
    .describe('Timezone, e.g. "Asia/Shanghai". Defaults to local timezone.'),
})

const outputSchema = z.object({
  timestamp: z.number().describe('Unix timestamp in seconds'),
  formatted: z.string().describe('Formatted time string'),
  timezone: z.string().describe('Timezone used'),
})

// 类型导出（便于在其他地方引用）
type InputSchema = typeof inputSchema
type Output = z.infer<typeof outputSchema>

// 第 2 步：定义渲染函数
function renderToolUseMessage(
  input: Partial<z.infer<InputSchema>>,
  options: { theme: ThemeName; verbose: boolean; commands?: Command[] },
): React.ReactNode {
  return (
    <div>
      Getting current time
      {input.format ? ` (format: ${input.format})` : ''}
      {input.timezone ? ` (timezone: ${input.timezone})` : ''}
    </div>
  )
}

function renderToolResultMessage(
  content: Output,
  // 进度消息（TimeTool 无进度，这里为空数组）
  _progressMessagesForMessage: ProgressMessage<any>[],
  options: {
    style?: 'condensed'
    theme: ThemeName
    tools: Tools
    verbose: boolean
    isTranscriptMode?: boolean
    isBriefOnly?: boolean
    input?: unknown
  },
): React.ReactNode {
  if (options.isBriefOnly) {
    return <span>{content.formatted}</span>
  }
  return (
    <div>
      <div>Time: {content.formatted}</div>
      <div>Unix: {content.timestamp}</div>
      <div>Timezone: {content.timezone}</div>
    </div>
  )
}

// 第 3 步：用 buildTool 构造工具实例
export const TimeTool = buildTool({
  name: 'Time',
  maxResultSizeChars: 1_000,  // 小结果，不需要大文件持久化
  strict: true,

  inputSchema,
  outputSchema,

  description({ format, timezone }) {
    let desc = 'Get the current date and time.'
    if (format) desc += ` Format: ${format}.`
    if (timezone) desc += ` Timezone: ${timezone}.`
    return desc
  },

  async prompt({ tools }) {
    return 'Use the Time tool when you need to know the current date or time.'
  },

  // 第 4 步：实现核心 call 方法
  async call(
    input: z.infer<InputSchema>,
    context: ToolUseContext,
    _canUseTool?: CanUseToolFn,
    _parentMessage?: AssistantMessage,
    _onProgress?: ToolCallProgress<any>,
  ): Promise<ToolResult<Output>> {
    const { format = 'iso', timezone } = input

    // 实际的时间获取逻辑
    const now = new Date()

    let targetTime: Date = now
    if (timezone) {
      // Intl.DateTimeFormat 支持的时区格式
      targetTime = new Date(
        now.toLocaleString('en-US', { timeZone: timezone }),
      )
    }

    let formatted: string
    let timestamp: number

    switch (format) {
      case 'unix':
        timestamp = Math.floor(targetTime.getTime() / 1000)
        formatted = timestamp.toString()
        break
      case 'friendly':
        formatted = targetTime.toLocaleString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
        timestamp = Math.floor(targetTime.getTime() / 1000)
        break
      case 'iso':
      default:
        timestamp = Math.floor(targetTime.getTime() / 1000)
        formatted = targetTime.toISOString()
        break
    }

    return {
      data: {
        timestamp,
        formatted,
        timezone: timezone ?? Intl.DateTimeFormat().resolvedOptions().timeZone,
      },
    }
  },

  // 第 5 步：实现只读标识（时间工具不修改任何状态）
  isReadOnly() {
    return true
  },

  // 第 6 步：实现权限检查（只读工具默认允许）
  async checkPermissions(
    input: z.infer<InputSchema>,
    _context: ToolUseContext,
  ): Promise<PermissionResult> {
    return { behavior: 'allow', updatedInput: input }
  },

  // 第 7 步：渲染方法
  renderToolUseMessage,
  renderToolResultMessage,

  // 第 8 步：用户可见的工具名称（注意：接收输入参数）
  userFacingName(_input?: Partial<z.infer<InputSchema>>) {
    return 'Time'
  },

  getToolUseSummary(input) {
    return input.format === 'unix'
      ? 'Get Unix timestamp'
      : `Get current time (${input.format ?? 'iso'})`
  },

  getActivityDescription(_input) {
    return 'Getting current time'
  },

  toAutoClassifierInput() {
    return ''
  },

  mapToolResultToToolResultBlockParam(content, toolUseID) {
    return {
      tool_use_id: toolUseID,
      type: 'tool_result',
      content: `Current time: ${content.formatted}\nTimestamp: ${content.timestamp}\nTimezone: ${content.timezone}`,
    }
  },
} satisfies ToolDef<InputSchema, Output>)
```

### 步骤 2：注册工具

在 `src/tools.ts` 的 `getAllBaseTools()` 函数中添加新工具：

```
// src/tools.ts
import { TimeTool } from './tools/TimeTool/TimeTool.js'  // 添加导入

export function getAllBaseTools(): Tools {
  return [
    AgentTool,
    TaskOutputTool,
    BashTool,
    // ... 其他工具 ...
    BriefTool,
    TimeTool,  // ← 在这里注册
    // ...
  ]
}
```

### 步骤 3：在权限系统中注册（可选）

如果你的工具需要权限检查，需要在权限规则中添加入口：

```
// src/utils/permissions/permissions.ts
// 或相应权限配置文件中添加：
const ALWAYS_ALLOW_RULES: ToolPermissionRulesBySource = {
  time: {
    // TimeTool 是只读工具，加入 alwaysAllow
    patterns: ['Time*'],
    behavior: 'always_allow',
  },
}
```

### 关键设计模式总结

1. **Schema 与实现分离**：Zod schema 定义在工具文件顶部，`buildTool` 调用中引用变量而非内联定义，便于类型推断和复用。
2. **惰性构建**：使用 `lazySchema`（如需要条件化 schema）或直接在文件顶层定义 schema（对于简单工具），取决于是否有循环依赖风险。
3. **渲染方法独立**：所有 `render*` 函数单独定义，不混入 `buildTool` 调用，保持代码结构清晰。
4. **satisfies ToolDef**：使用 TypeScript 的 `satisfies` 操作符验证工具定义符合 `ToolDef` 约束，同时保留字面量类型推断（不会把 `inputSchema` 宽化为 `z.ZodType<unknown>`）。
5. **`isReadOnly` 返回 `true`**：如果你的工具不修改任何外部状态，请务必实现此方法——这决定了工具是否可以并发执行，直接影响性能。
6. **`toAutoClassifierInput` 返回空字符串**：安全分类器会使用此输入评估工具调用的风险级别。对于没有安全风险的只读工具，返回空字符串表示"跳过分类"。
7. **方法签名注意**：`userFacingName` 接收 `input?: Partial<z.infer<Input>>` 参数；`prompt` 接收包含 `tools`、`agents` 等上下文的 options 对象；`renderToolResultMessage` 的 options 中包含 `input?: unknown` 字段。

## 本章小结

本章深入剖析了 Claude Code 工具系统的核心架构：

- **设计思想**：通过统一的 `Tool` 接口和 `buildTool` 工厂函数，实现了工具的标准化抽象，将共性逻辑（权限检查、进度展示、类型推断）集中管理，每种具体工具只需关注自己的"差异部分"。
- **核心类型**：`Tool<T>`、`ToolDef<T>`、`ToolResult<T>`、`ToolUseContext` 构成了类型层面的四根支柱，确保了从注册到执行到展示的全链路类型安全。
- **Lazy Schema**：通过简单的闭包记忆化，优雅地解决了模块初始化顺序和循环依赖问题，同时支持了条件化 schema 这一高级特性。
- **注册与分发**：`tools.ts` 提供了从简单模式到完整模式的多层次工具分发机制，内置工具与 MCP 工具统一合并、去重、排序。REPL 模式下原始工具通过 `REPL_ONLY_TOOLS` 集合隐藏，由 REPL 包装统一暴露。
- **实操指南**：完整演示了从创建工具文件到注册到系统的全过程，涵盖所有关键方法，包括正确的方法签名和必要的类型导入。

理解工具系统的设计对于深入掌握 Claude Code 的内部运作至关重要——无论是调试现有工具、添加新功能，还是构建基于 Claude Code 的定制化应用，工具系统都是核心基础设施。

---

# 第八章 安全权限体系

Claude Code 的安全权限体系是整个系统中最精密复杂的部分。与大多数 AI 编程助手仅依赖"提示词防注入"不同，Claude Code 构建了一套**多层次、确定性、且经过实战检验**的防御机制。本章从架构设计哲学出发，深入解析每一层防御的实现逻辑、源码位置及设计原因。

## 8.1 安全架构总览

### 8.1.1 安全设计哲学

Claude Code 的安全设计遵循三条核心原则：

**1. 纵深防御（Defense in Depth）**：绝不依赖单一安全机制。任何危险操作都必须经过多层检查，单层失效不会导致安全崩溃。

**2. 确定性优先于智能**：对于已知的危险模式，优先使用精确的正则表达式和 AST 解析，而非依赖 AI 分类器的模糊判断。AI 分类器作为最后防线，只在高置信度时自动批准。

**3. 失败即询问（Fail-Ask）**：任何无法证明安全性的操作，都必须升级为用户交互提示，绝不静默放行。

### 8.1.2 四层防御管道

Claude Code 的权限检查**并非"熔断"（circuit breaker）**，而是严格按序执行的检查管道。每个请求必须依次通过每一层大门：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    hasPermissionsToUseTool                           │
│                 (permissions.ts:hasPermissionsToUseToolInner)       │
└──────────┬──────────────────────────────────────────────────────────┘
           │ 步骤 1a-c: 工具级规则检查（deny/ask/allow 整工具规则）
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│           tool.checkPermissions() ← 工具自身的安全检查              │
│  ┌───────────────┐  ┌─────────────────┐  ┌──────────────────────┐ │
│  │ acceptEdits   │  │ safe-tool       │  │ classifier API       │ │
│  │ fast-path     │→ │ allowlist       │→ │ (Haiku)              │ │
│  └───────────────┘  └─────────────────┘  └──────────────────────┘ │
│         ↑                  ↑                       ↑               │
│         │                  │                       │               │
│    快速放行           免 API 调用              智能分类            │
└──────────┬──────────────────────────────────────────────────────────┘
           │ 步骤 1e-2: 模式转换（bypass/alwaysAllow/passthrough→ask）
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  transcriptTooLong ──→ iron_gate ──→ denialLimitExceeded            │
│    (上下文过长)              (分类器不可用)       (拒绝次数超限)     │
└─────────────────────────────────────────────────────────────────────┘
```

**管道中的每一关（按执行顺序）：**

| 关卡 | 触发条件 | 行为 | 源码位置 |
|------|---------|------|----------|
| `acceptEdits fast-path` | 工具在 acceptEdits 模式下检查通过 | 直接 `allow` | `permissions.ts:593+` |
| `safe-tool allowlist` | 工具名在 `SAFE_YOLO_ALLOWLISTED_TOOLS` 中 | 直接 `allow` | `permissions.ts:659+` |
| `classifier API` | auto 模式下工具不在 allowlist | Haiku 分类器评估 | `permissions.ts:688+` |
| `transcriptTooLong` | 分类器报告 transcriptTooLong | 回退到普通提示 | `permissions.ts:822+` |
| `iron_gate` | 分类器不可用（API 错误）且 `tengu_iron_gate_closed=true` | `deny` | `permissions.ts:844+` |
| `denialLimitExceeded` | 连续拒绝 ≥3 次或累计拒绝 ≥20 次 | 回退到询问 | `permissions.ts:890+` |

**设计原因**：这种管道设计确保了**渐进式信任建立**。安全操作（如读取文件）走 fast-path 和 allowlist，避免不必要的 API 调用；不确定的操作进入分类器；分类器失败时又有安全网。每一层都可以独立调优而不影响其他层。

### 8.1.3 权限检查的完整流程

以 Bash 工具为例，一次完整的权限检查路径如下（`bashPermissions.ts:bashToolHasPermission`）：

```
bashToolHasPermission(input, context)
  ├─ AST 安全解析（tree-sitter）→ too-complex? → ask
  ├─ 沙箱自动放行 → checkSandboxAutoAllow → allow/deny/ask
  ├─ 精确规则匹配 → bashToolCheckExactMatchPermission → deny/ask/allow
  ├─ Haiku 分类器（deny/ask）→ classifyBashCommand → deny/ask
  ├─ 操作符检查 → checkCommandOperatorPermissions → pipe/redirect 处理
  ├─ 命令注入检测 → bashCommandIsSafeAsync → ask
  ├─ 子命令拆分 → splitCommand（最多 50 个）
  ├─ cd+git 联合检查（防止 bare repo 攻击）
  ├─ 逐子命令权限检查 → bashToolCheckPermission
  │    ├─ 精确/前缀规则匹配
  │    ├─ PATH 约束检查 → checkPathConstraints
  │    ├─ sed 约束检查 → checkSedConstraints
  │    └─ 只读命令自动放行
  └─ 建议规则生成 → suggestionForExactCommand/suggestionForPrefix
```

## 8.2 BashTool 安全验证机制

### 8.2.1 23 种独立安全检查

`bashSecurity.ts` 定义了 23 种独立的数字检查 ID（`BASH_SECURITY_CHECK_IDS`，第 50-72 行），每种检查对应一种特定的安全威胁：

```
// bashSecurity.ts:50-72
const BASH_SECURITY_CHECK_IDS = {
  INCOMPLETE_COMMANDS: 1,           // 不完整命令片段
  JQ_SYSTEM_FUNCTION: 2,            // jq system() 函数调用
  JQ_FILE_ARGUMENTS: 3,            // jq 危险文件参数（-f/--from-file）
  OBFUSCATED_FLAGS: 4,             // 混淆的标志参数
  SHELL_METACHARACTERS: 5,         // shell 元字符（;, |, &）
  DANGEROUS_VARIABLES: 6,          // 危险变量上下文
  NEWLINES: 7,                     // 换行符分隔多命令
  DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION: 8,  // 命令替换
  DANGEROUS_PATTERNS_INPUT_REDIRECTION: 9,     // 输入重定向
  DANGEROUS_PATTERNS_OUTPUT_REDIRECTION: 10,   // 输出重定向
  IFS_INJECTION: 11,               // IFS 变量注入
  GIT_COMMIT_SUBSTITUTION: 12,    // git commit 消息注入
  PROC_ENVIRON_ACCESS: 13,         // /proc/*/environ 访问
  MALFORMED_TOKEN_INJECTION: 14,   // 畸形 token 注入
  BACKSLASH_ESCAPED_WHITESPACE: 15,// 反斜杠转义空白
  BRACE_EXPANSION: 16,            // 大括号扩展
  CONTROL_CHARACTERS: 17,         // 控制字符
  UNICODE_WHITESPACE: 18,          // Unicode 空白
  MID_WORD_HASH: 19,              // 词内 # 注释
  ZSH_DANGEROUS_COMMANDS: 20,     // Zsh 危险命令
  BACKSLASH_ESCAPED_OPERATORS: 21,// 反斜杠转义操作符
  COMMENT_QUOTE_DESYNC: 22,       // 注释中引号导致解析器失步
  QUOTED_NEWLINE: 23,             // 引号内换行符
} as const
```

使用数字 ID 而非字符串是为了**减小日志体积**和**避免日志注入攻击**——日志系统记录数字 ID 而非用户输入的命令字符串。

### 8.2.2 验证器注册与执行顺序

所有验证器分为三类（`bashSecurity.ts:bashCommandIsSafe_DEPRECATED`）：

```
// 早期验证器（返回 allow 则短路）
const earlyValidators = [
  validateEmpty,                    // 空命令 → allow
  validateIncompleteCommands,        // 不完整片段 → ask
  validateSafeCommandSubstitution,   // 安全 heredoc → allow
  validateGitCommit,                 // 安全 git commit → allow
]

// 主要验证器列表（逐个运行）
const validators = [
  validateJqCommand,               // jq 危险函数/参数
  validateObfuscatedFlags,          // 混淆标志（ANSI-C 引用、空引号等）
  validateShellMetacharacters,       // 元字符
  validateDangerousVariables,        // 变量在重定向/管道中
  validateCommentQuoteDesync,        // 注释中引号导致解析失步
  validateQuotedNewline,             // 引号内换行符+下一行以#开头
  validateCarriageReturn,            // CR 字符（\r）导致解析差异
  validateNewlines,                  // 换行符分隔多命令
  validateIFSInjection,              // IFS 变量注入
  validateProcEnvironAccess,         // /proc/*/environ 访问
  validateDangerousPatterns,         // 命令替换（$()、反引号等）
  validateRedirections,              // 重定向 < >
  validateBackslashEscapedWhitespace,// 反斜杠转义空白
  validateBackslashEscapedOperators, // 反斜杠转义操作符
  validateUnicodeWhitespace,         // Unicode 空白
  validateMidWordHash,               // 词内 #
  validateBraceExpansion,            // 大括号扩展 {a,b}
  validateZshDangerousCommands,      // Zsh 危险命令
  validateMalformedTokenInjection,   // 畸形 token 注入
]
```

**设计原因**：早期验证器返回 `allow` 时会**短路整个验证流程**。这是性能优化——安全的特殊模式（如 heredoc）不需要运行全部 23 种检查。但短路条件极其严格：`validateGitCommit` 只允许简单的 `-m` 参数且消息内容不含 `$()`、反引号、`${}`。

### 8.2.3 关键验证器详解

#### 8.2.3.1 Zsh 危险命令检测

`validateZshDangerousCommands`（`bashSecurity.ts:2320-2362`）专门检测 Zsh 特有的危险命令：

```
const ZSH_DANGEROUS_COMMANDS = new Set([
  'zmodload',   // 加载内核模块（zsh/mapfile, zsh/system, zsh/net/tcp）
  'emulate',    // emulate -c 是 eval 等价物
  'sysopen',    // zsh/system 细粒度文件打开
  'sysread',    // zsh/system 文件描述符读取
  'syswrite',   // zsh/system 文件描述符写入
  'sysseek',    // zsh/system 文件描述符搜索
  'zpty',       // 伪终端执行
  'ztcp',       // TCP 连接建立（数据外泄通道）
  'zsocket',    // Unix/TCP 套接字
  'mapfile',    // zsh/mapfile 数组访问
  'zf_rm',      // zsh/files 内置 rm（绕过二进制检查）
  'zf_mv',      // zsh/files 内置 mv
  'zf_ln',      // zsh/files 内置 ln
  'zf_chmod',   // zsh/files 内置 chmod
  'zf_chown',   // zsh/files 内置 chown
  'zf_mkdir',   // zsh/files 内置 mkdir
  'zf_rmdir',   // zsh/files 内置 rmdir
  'zf_chgrp',   // zsh/files 内置 chgrp
  // 以及 fc -e（任意编辑器执行命令历史）
])
```

这些命令即使在 `Bash(zmodload:*)` 规则下也可能绕过安全检查。

#### 8.2.3.2 命令替换模式检测

`COMMAND_SUBSTITUTION_PATTERNS`（`bashSecurity.ts:9-47`）定义了 **14 种**危险替换模式：

```
const COMMAND_SUBSTITUTION_PATTERNS = [
  { pattern: /<\(/, message: 'process substitution <()' },       // 进程替换 <()
  { pattern: />\(/, message: 'process substitution >()' },       // 进程替换 >()
  { pattern: /=\(/, message: 'Zsh process substitution =()' },   // Zsh =cmd 扩展
  { pattern: /(?:^|[\s;&|])=[a-zA-Z_]/, message: 'Zsh equals expansion' },
  // 防止 =curl evil.com → /usr/bin/curl evil.com（绕过 Bash(curl:*) 规则）
  { pattern: /=\$\[/, message: 'Zsh legacy arithmetic =$[...' }, // Zsh 旧式算术扩展
  { pattern: /\\\(e:/, message: 'Zsh special wrap \\(e:' },     // Zsh \\(e: 特殊包裹
  { pattern: /\\\(\+/, message: 'Zsh special wrap \\(+' },      // Zsh \\(+ 特殊包裹
  { pattern: /\\\}\\s*always\\s*\{/, message: 'Zsh always wrap' }, // Zsh 特殊包裹 always
  { pattern: /\$\(/, message: '$() command substitution' },     // $() 命令替换
  { pattern: /\$\{/, message: '${} parameter substitution' },   // ${} 参数替换
  { pattern: /\$\[/, message: '$[] legacy arithmetic expansion' }, // $[] 旧式算术
  { pattern: /`/, message: 'backtick command substitution' },   // 反引号命令替换
  { pattern: /<#/, message: 'PowerShell comment syntax' },      // PowerShell 注释语法
]
```

#### 8.2.3.3 反斜杠转义操作符攻击

`validateBackslashEscapedOperators`（`bashSecurity.ts:1534-1620`）检测一个精妙的攻击：

```bash
# 攻击payload：
cat safe.txt \; echo ~/.ssh/id_rsa

# splitCommand 规范化后：
"cat safe.txt ; echo ~/.ssh/id_rsa"

# 重新解析时，`;` 被视为操作符，命令被拆分为：
# ["cat safe.txt", "echo ~/.ssh/id_rsa"]
# 第二个命令通过路径检查 → 私钥泄露
```

**设计原因**：这种攻击利用了**二次解析的差异**。`splitCommand` 规范化了 `\;` 为 `;`，但下游的 `checkPathConstraints` 重新解析时看到操作符。`bashSecurity.ts` 在第一轮就检测并阻止。

#### 8.2.3.4 引号内换行符攻击

`validateQuotedNewline`（`bashSecurity.ts:2076-2130`）检测最隐蔽的攻击之一：

```bash
# 攻击payload：
mv ./decoy '<\n>#' ~/.ssh/id_rsa ./exfil_dir
# Bash：换行在引号内，是字面字符；下一行以 # 开头（实际是文件名的一部分）
# stripCommentLines（逐行处理）：检测到下一行 trim 后以 # 开头 → 丢弃整行
# 结果：~/.ssh/id_rsa 被移入 exfil_dir，完全绕过路径验证
```

## 8.3 权限模式设计

### 8.3.1 PermissionResult 的四种语义

`PermissionResult` 是权限系统的核心返回值类型（`permissions.ts` 和 `types/permissions.ts`），四种行为语义各不相同：

| 行为 | 含义 | 后续处理 |
|------|------|----------|
| `allow` | 命令安全，已批准执行 | 直接执行 |
| `ask` | 命令需要用户确认 | 展示权限对话框 |
| `deny` | 命令被显式拒绝 | 拒绝执行 |
| `passthrough` | 无规则匹配，需要进一步判断 | 转换为 ask 或交给下一层处理 |

**设计原因**：`allow` 和 `ask` 之间的区别至关重要。如果直接对未知命令返回 `ask`，则规则引擎将无法区分"用户已明确允许"和"从未见过"。`allow` 意味着**确定性放行**，`ask` 意味着**需要人类判断**。

### 8.3.2 环境变量白名单

`bashPermissions.ts` 定义了两套环境变量白名单：

**SAFE_ENV_VARS**（第 290-393 行）：对所有用户安全的环境变量，例如：
- `GOOS`, `GOARCH`, `CGO_ENABLED`（Go 构建配置）
- `RUST_BACKTRACE`, `RUST_LOG`（Rust 日志）
- `NODE_ENV`, `PYTHONUNBUFFERED`（运行时行为）
- `TERM`, `TZ`, `LC_*`（本地化/终端）
- `ANTHROPIC_API_KEY`（API 认证）

**绝对不能加入白名单的变量**（注释明确标注）：
```
// bashPermissions.ts:238-249 注释
// SECURITY: These must NEVER be added to the whitelist:
// - PATH, LD_PRELOAD, LD_LIBRARY_PATH, DYLD_* → 执行/库加载
// - PYTHONPATH, NODE_PATH, CLASSPATH, RUBYLIB → 模块加载
// - GOFLAGS, RUSTFLAGS, NODE_OPTIONS → 可包含代码执行标志
// - HOME, TMPDIR, SHELL, BASH_ENV → 影响系统行为
```

**ANT_ONLY_SAFE_ENV_VARS**（第 434-499 行）：仅对 `USER_TYPE === 'ant'` 生效的额外白名单，包含 `KUBECONFIG`、`DOCKER_HOST`、`AWS_PROFILE`、`CUDA_VISIBLE_DEVICES` 等。注释明确警告：**此白名单绝不能对外部分发**，因为 `DOCKER_HOST=tcp://evil.com docker ps` 会在 `Bash(docker ps:*)` 规则下自动放行。

### 8.3.3 命令包装器剥离

`stripSafeWrappers`（`bashPermissions.ts:760-830`）在权限匹配前剥离安全的命令包装器：

```
const SAFE_WRAPPER_PATTERNS = [
  // timeout: 解析 GNU long/short flags，要求值必须是 [A-Za-z0-9_.+-]+
  /^timeout[ \t]+(?:(?:--(?:foreground|preserve-status|verbose)|...|-v|-[ks][ \t]+...)[ \t]+)*--[ \t]+\d+(?:\.\d+)?[smhd]?[ \t]+/,
  /^time[ \t]+(?:--[ \t]+)?/,
  // nice: -n N 或 -N 形式
  /^nice(?:[ \t]+-n[ \t]+-?\d+|[ \t]+-\d+)?[ \t]+(?:--[ \t]+)?/,
  /^stdbuf(?:[ \t]+-[ioe][LN0-9]+)+[ \t]+(?:--[ \t]+)?/,
  /^nohup[ \t]+(?:--[ \t]+)?/,
]
```

**设计原因**：`timeout 30 npm install` 应匹配 `Bash(npm install:*)` 规则，但原始命令以 `timeout` 开头会干扰规则匹配。剥离后变为 `npm install`，规则正常生效。关键是 `timeout` 的值必须被严格限制——之前用 `[^ \t]+` 匹配值，导致 `timeout -k$(id) 10 ls` 被错误剥离，`$(id)` 在词拆分时被展开执行。

## 8.4 编译时安全 vs 运行时安全

### 8.4.1 编译时隔离：USER_TYPE === 'ant'

Claude Code 在源码中大量使用 `process.env.USER_TYPE === 'ant'` 条件分支来隔离内部功能：

```
// bashPermissions.ts:123-137
function logClassifierResultForAnts(
  command: string,
  behavior: ClassifierBehavior,
  descriptions: string[],
  result: ClassifierResult,
): void {
  if (process.env.USER_TYPE !== 'ant') {
    return  // 外部版本：此函数什么也不做
  }
  // 内部版本：记录分类器评估结果用于分析
  logEvent('tengu_internal_bash_classifier_result', { ... })
}
```

这种设计确保：
1. **外部用户不受内部遥测影响**：分类器分析代码不会在外部版本执行
2. **代码体积可控**：Bun 的 tree-shaking 会移除永远不会执行的分支
3. **功能开关灵活**：通过 `USER_TYPE` 环境变量切换版本行为

### 8.4.2 Undercover Mode

Undercover Mode 是 Claude Code 为**贡献开源仓库**的用户提供的隐私保护机制（`utils/undercover.ts`）：

```
// undercover.ts:28-37
export function isUndercover(): boolean {
  // CLAUDE_CODE_UNDERCOVER=1 强制开启
  if (isEnvTruthy(process.env.CLAUDE_CODE_UNDERCOVER)) return true
  // 自动检测：如果不在内部仓库，也保持隐藏
  if (!isKnownInternalRepo()) return true
  return false
}

export function getUndercoverInstructions(): string {
  // 返回隐藏指令
  return `## UNDERCOVER MODE — CRITICAL
You are operating UNDERCOVER in a PUBLIC/OPEN-SOURCE repository.
Your commit attribution must be hidden. Never reveal internal codenames.`
}
```

Undercover Mode 的作用：
1. **隐藏提交归属**：不在 commit 中暴露 Claude Code 的内部代号
2. **移除系统提示中的模型名称**：防止通过提示词泄露内部信息
3. **保持 codename 隐蔽**：即使模型在回复中提及，也要被静默过滤

**设计原因**：当 Claude Code 的内部版本向公共仓库贡献代码时，不应暴露 `claude-code-3.5-sonnet` 等内部代号，Undercover Mode 确保所有外部可见输出都经过清洗。

## 8.5 实操指南：设计安全工具

本节展示如何为 Claude Code 设计一个符合安全规范的工具。假设我们要创建一个 `DatabaseTool`，用于执行只读数据库查询。

### 8.5.1 工具的基本结构

```
// tools/DatabaseTool/DatabaseTool.ts
import { Tool } from '../../Tool.js'
import { z } from 'zod'
import type { ToolPermissionContext, ToolUseContext } from '../../Tool.js'
import type { PermissionResult } from '../../utils/permissions/PermissionResult.js'
import { createPermissionRequestMessage } from '../../utils/permissions/permissions.js'

export class DatabaseTool extends Tool {
  name = 'DatabaseRead'
  description = 'Execute a read-only database query'

  // 输入 schema：只允许 SELECT 语句
  inputSchema = z.object({
    query: z.string().describe('SQL SELECT query (no INSERT/UPDATE/DELETE)'),
    connectionName: z.string().optional().default('default'),
  })

  // 核心执行逻辑
  async execute(input: { query: string; connectionName?: string }) {
    // 运行时：再次验证查询是 SELECT
    if (!input.query.trim().toUpperCase().startsWith('SELECT')) {
      throw new Error('Only SELECT queries are allowed')
    }
    return await runQuery(input.query, input.connectionName)
  }

  // 权限检查（核心安全实现）
  async checkPermissions(
    input: z.infer<typeof this.inputSchema>,
    context: ToolUseContext,
  ): Promise<PermissionResult> {
    const { query, connectionName } = input

    // 1. 语法验证：必须是 SELECT 语句
    const normalized = query.trim().toUpperCase()
    if (!normalized.startsWith('SELECT')) {
      return {
        behavior: 'deny',
        message: 'Only SELECT queries are permitted',
        decisionReason: {
          type: 'other',
          reason: 'Non-SELECT SQL statements are not allowed',
        },
      }
    }

    // 2. 危险模式检测：禁止特定 SQL 模式
    const DANGEROUS_PATTERNS = [
      /INTO\s+(OUTFILE|DUMPFILE)/i,   // 文件写入
      /LOAD_FILE\s*\(/i,              // 文件读取
      /INFORMATION_SCHEMA/i,           // 元数据泄露
      /PERFORMANCE_SCHEMA/i,
      /SHOW\s+(MASTER\s+STATUS|BINARY\s+LOGS)/i,  // 主从信息
    ]

    for (const pattern of DANGEROUS_PATTERNS) {
      if (pattern.test(query)) {
        return {
          behavior: 'deny',
          message: `Query contains forbidden pattern: ${pattern}`,
          decisionReason: {
            type: 'safetyCheck',
            reason: 'Query attempts to access sensitive system data',
          },
        }
      }
    }

    // 3. 连接名白名单检查
    const appState = context.getAppState()
    const allowedConnections = appState.toolPermissionContext.alwaysAllowRules
      .localSettings
      ?.filter(r => r.startsWith('DatabaseRead(connectionName:'))
      ?.map(r => r.match(/connectionName:([^)]+)/)?.[1]) ?? []

    if (allowedConnections.length > 0 && !allowedConnections.includes(connectionName)) {
      return {
        behavior: 'ask',
        message: createPermissionRequestMessage(this.name),
        decisionReason: {
          type: 'rule',
          reason: `Database connection '${connectionName}' requires approval`,
        },
      }
    }

    // 4. 简单查询自动放行，复杂查询要求确认
    const COMPLEXITY_THRESHOLD = 10  // 联接数超过 10 才询问
    const joinCount = (query.match(/\bJOIN\b/gi) ?? []).length

    if (joinCount > COMPLEXITY_THRESHOLD) {
      return {
        behavior: 'ask',
        message: createPermissionRequestMessage(this.name),
        decisionReason: {
          type: 'other',
          reason: `Query has ${joinCount} JOINs, which may be slow or expensive`,
        },
      }
    }

    // 5. 通过所有检查
    return {
      behavior: 'allow',
      updatedInput: input,
      decisionReason: {
        type: 'other',
        reason: 'Query passed all security checks',
      },
    }
  }

  // 标记是否需要用户交互
  requiresUserInteraction?() {
    return false  // 查询执行为异步，不阻塞 UI
  }
}
```

### 8.5.2 安全设计要点解析

**要点 1：Schema 层面的输入验证**

使用 Zod schema 约束输入格式，比运行时 `typeof` 检查更可靠。`query: z.string().describe()` 确保 LLM 生成的输入至少是字符串类型。

**要点 2：多层检查不等于多层 if-else**

我们的权限检查遵循**纵深防御**而非简单的 `if (!x) deny`。每层检查有不同的决策理由类型：
- `type: 'other'`：通用检查
- `type: 'safetyCheck'`：安全相关检查（绕过免疫）
- `type: 'rule'`：规则匹配结果

`permissions.ts` 对 `safetyCheck` 有特殊处理：即使在 `bypassPermissions` 模式下也会触发询问。开发者应将真正危险的模式（文件读写、系统命令执行）标记为 `safetyCheck`，而非 `other`。

**要点 3：连接名白名单设计**

允许管理员预配置可信的连接名（通过权限规则 `DatabaseRead(connectionName:production)`），使常见场景走 `allow` fast-path，罕见场景才触发 `ask`。

**要点 4：决策理由的可追溯性**

每个 `PermissionResult` 都包含 `decisionReason` 字段，包含具体的拒绝原因。这不仅对调试有帮助，还会被日志系统记录用于后续的安全分析（ANT 内部版本）。

### 8.5.3 在工具注册中启用安全检查

```
// tools.ts
import { DatabaseTool } from './DatabaseTool/DatabaseTool.js'
import { toolDefinition } from '../utils/registerTool.js'

toolDefinition({
  class: DatabaseTool,
  name: 'DatabaseRead',
  // 注册到 safe-tool allowlist（用于 auto 模式）
  // 只读工具可以被自动批准，不需要分类器
  autoModeSafe: true,
})
```

## 本章小结

Claude Code 的安全权限体系代表了 AI 编程助手安全设计的最高水位线。其核心要点包括：

1. **四层防御管道**：从 `acceptEdits` fast-path 到 `safe-tool` allowlist，再到 Haiku 分类器，最后是 `iron_gate` 和 `denialLimitExceeded` 安全网，每层职责明确。

2. **23 种 Bash 安全检查**：覆盖从最常见的 `;` 分隔多命令到最隐蔽的 `validateQuotedNewline`（引号内换行符配合 stripCommentLines 丢弃后续行），展现了工程团队对 shell 安全边界的深刻理解。

3. **PermissionResult 的四种语义**：精确区分 `allow`（确定性放行）、`ask`（需要人类判断）、`deny`（显式拒绝）、`passthrough`（无规则匹配），确保任何决策都有迹可循。

4. **环境变量白名单的严格管理**：`SAFE_ENV_VARS` 和 `ANT_ONLY_SAFE_ENV_VARS` 的分离，确保内部便利功能不会意外泄露到外部版本。

5. **Undercover Mode**：通过编译时 `USER_TYPE === 'ant'` 隔离和运行时 `isUndercover()` 检测，在保护隐私的同时保持代码的统一性。

设计一个安全的工具，需要同时考虑 schema 验证、危险模式检测、规则匹配、复杂度评估等多维度因素，并将不同类型的风险映射到正确的 `decisionReason.type`，以便权限系统的各个层次做出正确响应。

---

# 第九章：上下文管理与缓存

上下文（Context）是大型语言模型对话系统的核心资源。在 Claude Code 这类代码智能助手的长会话场景中，上下文空间尤为珍贵——一场数小时的编程会话可能产生数千条消息、数以万计的 token。如何在有限的上下文窗口内维持会话连续性，同时控制 API 成本，是本章要解答的核心问题。

Claude Code 采用的是**多层次、多路径**的上下文管理策略，而非简单的层层递进压缩。本章将从系统提示节（System Prompt Section）说起，逐步剖析从客户端到服务端的完整上下文生命周期。

---

## 9.1 系统提示节与动态边界

### 9.1.1 systemPromptSection 的缓存机制

Claude Code 的系统提示并非铁板一块，而是由若干**可独立缓存的节（Section）**组成。这一设计定义在 `src/constants/systemPromptSections.ts` 中：

```
// src/constants/systemPromptSections.ts, 第 17-21 行
export function systemPromptSection(
  name: string,
  compute: ComputeFn,
): SystemPromptSection {
  return { name, compute, cacheBreak: false }
}
```

`systemPromptSection` 创建一个**带记忆化的系统提示节**。注意其 `cacheBreak: false` 标志——这意味着除非显式失效，否则该节的计算结果会被缓存，在 `/clear` 或 `/compact` 之前永不重算。

关键在于 `resolveSystemPromptSections` 函数（第 34-48 行）：

```
// src/constants/systemPromptSections.ts, 第 34-48 行
export async function resolveSystemPromptSections(
  sections: SystemPromptSection[],
): Promise<(string | null)[]> {
  const cache = getSystemPromptSectionCache()

  return Promise.all(
    sections.map(async s => {
      if (!s.cacheBreak && cache.has(s.name)) {
        return cache.get(s.name) ?? null  // 缓存命中，直接返回
      }
      const value = await s.compute()
      setSystemPromptSectionCacheEntry(s.name, value)  // 写入缓存
      return value
    }),
  )
}
```

**设计原因**：系统提示中包含大量稳定信息（如 Agent 定义、工具描述）。这些内容在同一会话内几乎不变，若每次请求都重新拼接，则白白浪费 token 计数和计算资源。缓存机制使得只有"真正变化"的部分才重新计算，从而大幅节省上下文空间和 API 调用成本。

### 9.1.2 DANGEROUS_uncachedSystemPromptSection 的必要性

然而，有些信息天然具有**高频变化**特性，无法静态缓存。例如当前工作目录、用户偏好设置等。针对这些场景，Claude Code 提供了危险但必要的 `DANGEROUS_uncachedSystemPromptSection`（第 25-33 行）：

```
// src/constants/systemPromptSections.ts, 第 25-33 行
export function DANGEROUS_uncachedSystemPromptSection(
  name: string,
  compute: ComputeFn,
  _reason: string,
): SystemPromptSection {
  return { name, compute, cacheBreak: true }
}
```

这里的命名用 `DANGEROUS_` 前缀警醒开发者：使用此函数将**破坏提示缓存**（`cacheBreak: true`），导致每次请求都必须重算并重新计算缓存键，可能引发缓存命中率下降。使用者必须提供 `_reason` 参数记录原因，确保该权衡是有意识的工程决策。

**设计原因**：Claude Code 存在一种特殊状态——Beta 特性旗帜（Beta Header Latches）。当用户启用或关闭某些 Beta 特性时，系统提示的相关部分需要**立即失效**，而非等到 `/clear` 或 `/compact`。因此在 `clearSystemPromptSections`（第 54-58 行）中，除了清理 Section 缓存，还要重置 Beta Header 锁存器：

```
// src/constants/systemPromptSections.ts, 第 54-58 行
export function clearSystemPromptSections(): void {
  clearSystemPromptSectionState()
  clearBetaHeaderLatches()  // 重置 Beta 特性锁存
}
```

---

## 9.2 四层压缩不是层层递进

### 9.2.1 常见的理解误区

许多读者初次接触 Claude Code 的压缩机制时，会自然地想象它是一套"层层递进"的漏斗：先把消息压缩成摘要，再把摘要进一步压缩，再压缩……形成一条从粗到细的金字塔。但**这是错误的模型**。

Claude Code 的压缩系统由**四个独立路径**组成，它们各自独立触发、相互补位，并非串联递进：

| 压缩路径 | 触发条件 | 行为 |
|---------|---------|------|
| **自动压缩** | 上下文 token 接近阈值 | 调用 LLM 生成摘要，保留边界标记 |
| **手动压缩** | 用户执行 `/compact` | 同上，但触发时机由用户控制 |
| **部分压缩** | 用户选中某条消息执行压缩 | 仅压缩选中位置之前或之后的片段 |
| **Prompt Too Long 降级** | API 返回 `prompt_too_long` 错误 | 从头部分组丢弃最旧的消息组，回退冒险 |

### 9.2.2 全量压缩的核心流程

以全量压缩（`compactConversation`，定义于 `src/services/compact/compact.ts` 第 387 行起）为例，其核心流程如下：

```
// src/services/compact/compact.ts, 第 387-670 行（简化流程）
export async function compactConversation(
  messages: Message[],
  context: ToolUseContext,
  // ...
): Promise<CompactionResult> {
  // 1. 执行 PreCompact Hooks（允许外部注入定制指令）
  const hookResult = await executePreCompactHooks(...)
  customInstructions = mergeHookInstructions(customInstructions, hookResult.newCustomInstructions)

  // 2. 构建摘要请求消息
  const compactPrompt = getCompactPrompt(customInstructions)
  const summaryRequest = createUserMessage({ content: compactPrompt })

  // 3. 调用 LLM 生成摘要（支持 fork 缓存共享或直接流式）
  summaryResponse = await streamCompactSummary({ messages, summaryRequest, ... })

  // 4. 创建边界标记（SystemCompactBoundaryMessage）
  const boundaryMarker = createCompactBoundaryMessage(isAutoCompact ? 'auto' : 'manual', ...)

  // 5. 生成摘要用户消息（isCompactSummary: true）
  const summaryMessages = [createUserMessage({ content: getCompactUserSummaryMessage(...), isCompactSummary: true })]

  // 6. 生成后续恢复附件（文件、技能、计划等）
  const postCompactFileAttachments = await createPostCompactFileAttachments(...)

  // 7. 执行 PostCompact Hooks + SessionStart Hooks
  const hookMessages = await processSessionStartHooks('compact', ...)

  return {
    boundaryMarker,
    summaryMessages,
    attachments: postCompactFileAttachments,
    hookResults: hookMessages,
    // ...
  }
}
```

**关键洞察**：压缩的结果是一个**新的消息数组**，由边界标记 + 摘要消息 + 保留片段 + 各类附件组成。压缩不是"压缩旧消息"，而是"用摘要替换旧消息"，是一种**有损替换**，而非**逐级提炼**。

### 9.2.3 部分压缩的双向支持

部分压缩（`partialCompactConversation`，`compact.ts` 第 772 行起）支持两种方向：

- **`from`**：从选中位置**向后**压缩，保留前面的消息不动
- **`up_to`**：从选中位置**向前**压缩，保留后面的消息不动

```
// src/services/compact/compact.ts, 第 325-340 行
const messagesToSummarize =
  direction === 'up_to'
    ? allMessages.slice(0, pivotIndex)    // 压缩前面
    : allMessages.slice(pivotIndex)        // 压缩后面
const messagesToKeep =
  direction === 'up_to'
    ? allMessages.slice(pivotIndex).filter(...)  // 保留后面
    : allMessages.slice(0, pivotIndex).filter(...)  // 保留前面
```

对于 `up_to` 方向，代码会**过滤掉旧的压缩边界和摘要**，防止历史中的压缩标记在新压缩环境中产生干扰（第 334-349 行有详细的过滤逻辑）。

### 9.2.4 Prompt Too Long 降级机制

即便压缩本身也可能遭遇 `prompt_too_long`。`truncateHeadForPTLRetry`（第 243 行起）是最后的逃生舱口：

```
// src/services/compact/compact.ts, 第 243 行起
export function truncateHeadForPTLRetry(
  messages: Message[],
  ptlResponse: AssistantMessage,
): Message[] | null {
  const groups = groupMessagesByApiRound(input)
  if (groups.length < 2) return null

  const tokenGap = getPromptTooLongTokenGap(ptlResponse)
  let dropCount: number
  if (tokenGap !== undefined) {
    // 精确模式：累积直到覆盖 token 缺口
    let acc = 0; dropCount = 0
    for (const g of groups) {
      acc += roughTokenCountEstimationForMessages(g)
      dropCount++
      if (acc >= tokenGap) break
    }
  } else {
    // 回退模式：无法解析时，丢弃 20% 最旧分组
    dropCount = Math.max(1, Math.floor(groups.length * 0.2))
  }
  // ... 返回截断后的消息
}
```

---

## 9.3 消息分组：groupMessagesByApiRound

### 9.3.1 为什么需要按 API 轮次分组

Claude Code 的消息历史是**交错式**的：用户消息 → Assistant 响应 → 工具调用 → 工具结果 → Assistant 再响应……每两个 Assistant 消息之间，代表一次完整的**API 轮次**（Round Trip）。

`groupMessagesByApiRound`（`src/services/compact/grouping.ts` 全文约 25 行）<!-- [勘误: 原文描述为"全文约 47 行"，但实际展示的代码约 25 行] -->的核心目的是将消息序列切分为"可安全丢弃的最小单元"：

```
// src/services/compact/grouping.ts, 全文约 25 行
export function groupMessagesByApiRound(messages: Message[]): Message[][] {
  const groups: Message[][] = []
  let current: Message[] = []
  let lastAssistantId: string | undefined

  for (const msg of messages) {
    // 当新的 Assistant 消息出现（message.id 改变）且当前组不为空，则切分组
    if (
      msg.type === 'assistant' &&
      msg.message.id !== lastAssistantId &&
      current.length > 0
    ) {
      groups.push(current)
      current = [msg]
    } else {
      current.push(msg)
    }
    if (msg.type === 'assistant') {
      lastAssistantId = msg.message.id
    }
  }
  if (current.length > 0) { groups.push(current) }
  return groups
}
```

**设计原因 1：API 约束保证**  
LLM API 的契约规定：每个 `tool_use` 块必须在下一个 Assistant 响应开始前被 `tool_result` 解析。因此，**一个 API 轮次内**的消息是一个原子单元——不能只保留其中的工具调用而丢弃结果，也不能反过来。

**设计原因 2：流式消息的正确处理**  
Claude Code 使用流式（Streaming）API，消息块在传输过程中陆续到达，同一 API 轮次的多个 `tool_use` 块可能**交错**出现（`tu_A(id=X), result_A, tu_B(id=X), result_B`）。通过 `message.id` 而非顺序位置作为分组依据，可以正确地将所有相关消息归入同一组。

**设计原因 3：支持精细化降级**  
当需要丢弃消息来缓解 `prompt_too_long` 时，丢掉的最小单位是一个完整的 API 轮次，而不是某条中间消息。这避免了"只丢弃用户消息但保留工具结果"这种语义断裂。

### 9.3.2 流式交错消息的实例

考虑以下场景（简化表示）：

```
[1] Assistant: 正在读取文件...
[2] Assistant: tool_use { id="msg_001", name="Read" }
[3] Tool Result: 文件内容...
[4] Assistant: 已读取文件，现在分析...
[5] Assistant: tool_use { id="msg_002", name="Edit" }
[6] Tool Result: 修改完成
```

- 第一组：`[1, 2, 3, 4]`（`lastAssistantId = msg_001`）
- 第二组：`[5, 6]`（`lastAssistantId = msg_002`）

若 `up_to` 方向在第 4 条消息处截断，第二组（`[5, 6]`）被压缩，第一组被保留——完全符合 API 原子性语义。

---

## 9.4 客户端与服务端的上下文管理

### 9.4.1 客户端职责：消息生命周期管理

Claude Code 客户端负责维护完整的消息历史数组，并在适当时机触发压缩。其管理职责包括：

1. **消息追加**：每次用户输入和 API 响应后，将消息追加到历史数组
2. **压缩触发检测**：`shouldAutoCompact` 函数持续监控上下文 token 数量
3. **压缩执行**：调用 `compactConversation` 或 `partialCompactConversation`
4. **附件重建**：压缩后重新生成文件、技能、工具等附件消息

客户端在压缩时会**清理 `readFileState`**（`compact.ts` 第 521 行）：

```
// src/services/compact/compact.ts, 第 521 行
context.readFileState.clear()
context.loadedNestedMemoryPaths?.clear()
```

这是因为压缩后旧消息中包含的文件读取结果已经"消失"了——后续若需要同一文件，需要重新读取。客户端通过 `createPostCompactFileAttachments`（第 1415-1480 行）智能恢复最近访问的文件：

```
// src/services/compact/compact.ts, 第 1415-1480 行（关键逻辑）
export async function createPostCompactFileAttachments(
  readFileState: Record<string, { content: string; timestamp: number }>,
  toolUseContext: ToolUseContext,
  maxFiles: number,
  preservedMessages: Message[] = [],  // 保留消息中的读取结果需要去重
): Promise<AttachmentMessage[]> {
  // 1. 收集已保留消息中的读取路径（去重）
  const preservedReadPaths = collectReadToolFilePaths(preservedMessages)

  // 2. 按最近访问时间排序，取 Top N
  const recentFiles = Object.entries(readFileState)
    .filter(file => !preservedReadPaths.has(expandPath(file.filename)))
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, maxFiles)

  // 3. 重新生成文件附件（但受 token 预算控制）
  // ...
}
```

**设计原因**：压缩后模型将"丢失"对旧文件内容的访问权。若用户在一个长会话中反复修改同一个文件，压缩后模型需要知道文件的最新内容。通过在压缩边界处重新注入最近访问文件的附件，模型可以在没有完整历史消息的情况下继续工作。

### 9.4.2 服务端职责：Prompt Cache 与上下文窗口

Claude Code 利用 Anthropic API 的 **Prompt Cache** 特性。系统提示（工具描述、Agent 定义等）在首次 API 调用时创建缓存，后续调用若前缀未变，则 `cache_read_input_tokens` 将远大于实际传输的 token 数，从而显著降低成本。

压缩过程中的 **fork 缓存共享**（`compact.ts` 第 1188 行附近）是一个精妙的设计：

```
// src/services/compact/compact.ts, 第 1188 行附近
const result = await runForkedAgent({
  promptMessages: [summaryRequest],  // 只需发送摘要请求
  cacheSafeParams,  // 继承主会话的缓存键参数
  canUseTool: createCompactCanUseTool(),  // 禁止工具调用
  skipCacheWrite: true,  // 不写入新缓存
  // ...
})
```

主会话已经构建了大量前缀缓存（包括系统提示、工具列表、历史消息摘要等）。压缩摘要请求**直接复用这些缓存**，只需传输一小段摘要指令，API 成本大幅降低。

**设计原因**：压缩 API 调用的输入规模通常较小（仅需压缩的旧消息 + 摘要指令），但如果走普通 API 路径，就需要重新传输完整前缀——包括系统提示和工具描述（可能 10K+ token）。通过 fork 机制复用主会话缓存，压缩操作本身几乎不产生额外的前缀传输成本。

### 9.4.3 服务端的缓存失效检测

Claude Code 通过 `notifyCompaction`（`compact.ts` 第 699 行及第 1048 行）通知服务端当前会话发生了压缩：

```
// src/services/compact/compact.ts, 第 699 行及第 1048 行
if (feature('PROMPT_CACHE_BREAK_DETECTION')) {
  notifyCompaction(
    context.options.querySource ?? 'compact',
    context.agentId,
  )
}
```

这使得服务端能够**重置缓存读取基线**——压缩后，旧的缓存读取量不再被视为"延续"，避免压缩操作本身被错误地标记为缓存断裂。

---

## 9.5 API 端的上下文边界管理

### 9.5.1 SystemCompactBoundaryMessage 的结构

压缩产生的边界标记是一个特殊的系统消息类型：

```
// src/utils/messages.ts（类型定义，函数引用来自 compact.ts 第 598 行）
type SystemCompactBoundaryMessage
```

其核心元数据（`compactMetadata`）包含：

- `truncatedFrom`：被压缩的最早消息的 UUID
- `preCompactDiscoveredTools`：压缩前发现的工具列表（用于恢复工具加载状态）
- `preservedSegment`：若存在保留片段，记录其头尾 UUID 和锚点

```
// src/services/compact/compact.ts, 第 598 行
const boundaryMarker = createCompactBoundaryMessage(
  isAutoCompact ? 'auto' : 'manual',
  preCompactTokenCount ?? 0,
  messages.at(-1)?.uuid,  // 最后一条原始消息的 UUID
)
// 携带已发现工具状态
const preCompactDiscovered = extractDiscoveredToolNames(messages)
if (preCompactDiscovered.size > 0) {
  boundaryMarker.compactMetadata.preCompactDiscoveredTools = [...preCompactDiscovered].sort()
}
```

### 9.5.2 normalizeMessagesForAPI 的预处理

在 API 调用前，消息需要经过规范化（`compact.ts` 第 1293 行）：

```
// src/services/compact/compact.ts, 第 1293 行
normalizeMessagesForAPI(
  stripImagesFromMessages(
    stripReinjectedAttachments([
      ...getMessagesAfterCompactBoundary(messages),
      summaryRequest,
    ]),
  ),
  context.options.tools,
)
```

这里执行了两项关键过滤：

1. **`stripImagesFromMessages`**：移除图片和文档块，避免压缩请求本身超出上下文限制（特别在 CCD 会话中用户频繁附图）
2. **`stripReinjectedAttachments`**：过滤掉 `skill_discovery` 和 `skill_listing` 类型的附件——这些在压缩后会被重新注入，无需重复传输

```
// src/services/compact/compact.ts, 第 211 行
export function stripReinjectedAttachments(messages: Message[]): Message[] {
  if (feature('EXPERIMENTAL_SKILL_SEARCH')) {
    return messages.filter(
      m =>
        !(
          m.type === 'attachment' &&
          (m.attachment.type === 'skill_discovery' ||
            m.attachment.type === 'skill_listing')
        ),
    )
  }
  return messages
}
```

### 9.5.3 压缩后 Token 计数与重触发判断

压缩后，Claude Code 会计算**真实的压缩后上下文大小**（`truePostCompactTokenCount`，`compact.ts` 第 637 行附近）：

```
// src/services/compact/compact.ts, 第 637 行附近
const truePostCompactTokenCount = roughTokenCountEstimationForMessages([
  boundaryMarker,
  ...summaryMessages,
  ...postCompactFileAttachments,
  ...hookMessages,
])
```

并通过事件上报给分析系统：

```
// src/services/compact/compact.ts, 第 651 行附近
willRetriggerNextTurn:
  recompactionInfo !== undefined &&
  truePostCompactTokenCount >= recompactionInfo.autoCompactThreshold,
```

这意味着：**即便刚刚完成了一次压缩，下一轮请求的自动压缩检测仍会立即触发**——如果压缩后的大小仍然接近阈值。这避免了"压缩后阈值刚好超标但未压缩"的问题，但也会在极端情况下导致**连续压缩循环**（recompaction loop），这也是审计中需要关注的性能问题之一。

---

## 9.6 章节小结

本章系统地解析了 Claude Code 的上下文管理与缓存机制。以下是关键要点：

1. **系统提示节缓存**：`systemPromptSection` 提供独立缓存的提示节；`DANGEROUS_uncachedSystemPromptSection` 用于高频变化信息，但会破坏缓存命中率。

2. **四层压缩独立并行**：自动压缩、手动压缩、部分压缩、PTL 降级是**四条独立路径**，非层层递进。压缩的本质是用摘要**替换**原始消息，而非逐级提炼。

3. **API 轮次分组**：`groupMessagesByApiRound` 以 `message.id` 边界将消息切分为原子单元，保证丢弃操作的语义完整性和 API 约束合规性。

4. **客户端-服务端协同**：客户端负责消息生命周期管理、压缩触发和附件重建；服务端通过 Prompt Cache 和基线重置优化 API 成本。

5. **压缩边界元数据**：压缩产生的 `SystemCompactBoundaryMessage` 携带丰富的元数据（工具发现状态、保留片段锚点等），确保压缩后的上下文仍具备连续工作能力。

理解这些机制，对于审计 Claude Code 的上下文消耗行为、排查压缩相关 bug（如连续压缩循环、缓存未命中、性能回退等）至关重要。下一章我们将深入探讨 **记忆系统**，了解 Claude Code 如何在跨会话层面保持上下文连续性。

---

# 第十章：记忆系统

## 概述

记忆系统是 Claude Code 保持跨会话上下文连续性的核心基础设施。与传统的短时记忆/长时记忆二分法不同，Claude Code 实现了一套**三层记忆架构**，分别在不同的生命周期、时间尺度和存储介质上运作。本章将深入剖析这套架构的设计原理、实现细节和使用方法。

---

## 10.1 三层记忆架构

### 10.1.1 架构总览

Claude Code 的记忆系统由三层构成，从内到外分别是：

| 层级 | 名称 | 生命周期 | 存储介质 | 触发时机 |
|------|------|----------|----------|----------|
| 第一层 | **会话记忆** | 单次对话 | LLM 上下文窗口 | 实时 |
| 第二层 | **持久记忆** | 跨会话 | `~/.claude/projects/<project>/memory/` | 自动提取 |
| 第三层 | **团队记忆** | 跨成员 | `memory/team/` 子目录 | 协作同步 |

三层之间通过**指针链**而非数据复制实现共享：会话结束时，持久层自动从会话中提取值得保留的信息；团队层则是持久层的一个命名空间子集，供多成员共享。

### 10.1.2 四型分类法

持久记忆中的每一条记录都必须属于以下四种类型之一（`memoryTypes.ts` 第 14 行）：

```
// memoryTypes.ts, 第 14 行
export const MEMORY_TYPES = [
  'user',      // 用户画像：角色、目标、偏好
  'feedback',   // 反馈指导：避免事项和成功经验
  'project',    // 项目状态：进行中的工作、截止日期、决策背景
  'reference',  // 外部引用：外部系统指针（Linear、Slack 等）
] as const
```

这种分类法的设计意图是**强制排除可推导信息**。代码模式、架构风格、文件结构都可以从当前代码库中直接读取（grep/git），不应占用记忆额度。记忆只保存**不可从代码中推导**的上下文——这正是记忆系统与代码文档（CLAUDE.md）的本质区别。

### 10.1.3 记忆存储结构

记忆目录的物理布局是对 `getMemoryBaseDir()` 函数返回路径的文档性描述（`paths.ts` 第 79–86 行）：

```
~/.claude/projects/<sanitized-git-root>/memory/
├── MEMORY.md              # 入口索引（最多 200 行，~25KB）
├── user_role.md           # 类型：user
├── feedback_testing.md    # 类型：feedback
├── project_deadline.md    # 类型：project
└── team/
    ├── MEMORY.md          # 团队索引（独立维护）
    ├── coding_style.md    # 团队级反馈
    └── external_links.md  # 团队级外部引用
```

每条记忆文件使用 frontmatter 格式（`memoryTypes.ts` 第 259 行）：

```markdown
---
name: user is senior data scientist
description: user focuses on observability and logging in ML pipelines
type: user
---

Senior data scientist working on ML pipeline observability.
**Context:** Prefers detailed logs over summaries; ask before running destructive commands.
**How to apply:** Tailor technical explanations to statistics/ML domain.
```

### 10.1.4 入口文件截断机制

`MEMORY.md` 会在系统提示词加载时被截断，有两道安全阀（`memdir.ts` 第 33 行和第 38 行）：

```
// memdir.ts, 第 33 行
export const MAX_ENTRYPOINT_LINES = 200
// ~125 chars/line at 200 lines
// memdir.ts, 第 38 行
export const MAX_ENTRYPOINT_BYTES = 25_000
```

截断策略优先尊重行数边界，再尊重字节数边界（`memdir.ts` 第 52–88 行）。若两者都超出，警告消息会追加到截断内容末尾，告知 Agent 索引条目过长，应将详情移入主题文件。

**设计原因**：索引文件过大是记忆系统退化的典型症状——Agent 在上下文窗口满载时无法读取完整索引。强制截断确保即使 Agent 忽略维护义务，系统仍可正常运转。

---

## 10.2 Auto Dream 引擎

### 10.2.1 夜间整合的意义

Agent 在单次会话中会不断向记忆目录写入新的记忆碎片。但这些碎片是**按时间顺序追加的**，彼此之间缺乏关联——同一主题的观察可能散落在多个文件中，相对日期（"昨天"、"上周"）会逐渐失去可解读性。

Auto Dream 引擎是一个**周期性后台任务**，在积累足够的会话信号后，自动对记忆目录进行"整理"——合并重复、修正过时内容、更新索引结构。

### 10.2.2 触发条件

Dream 任务的触发有四级门控，按检查成本从低到高排列（`autoDream.ts` 第 60–90 行）：

```
function isGateOpen(): boolean {
  if (getKairosActive()) return false  // KAIROS 模式由磁盘技能接管
  if (getIsRemoteMode()) return false
  if (!isAutoMemoryEnabled()) return false
  return isAutoDreamEnabled()
}
```

实际调度还需要满足以下条件（`autoDream.ts` 第 94–120 行）：

1. **时间门**：距上次整合至少 24 小时（可通过 `tengu_onyx_plover` 实验配置）
2. **会话数门**：自上次整合以来至少有 5 个会话（防止空跑）
3. **锁门**：无其他进程正在执行整合（防止并发写入）

### 10.2.3 整合四阶段

Dream 的工作流程分为四个阶段（`consolidationPrompt.ts`）：

**Phase 1 — Orient（定向）**
读取 `MEMORY.md` 和现有主题文件，了解当前记忆状态，避免重复创建。

**Phase 2 — Gather（采集信号）**
优先读取每日日志（`logs/YYYY/MM/YYYY-MM-DD.md`），辅以针对性的 transcript 搜索。只在已有初步假设时才 grep 大型 JSONL 文件，避免大海捞针。

**Phase 3 — Consolidate（整合）**
将新信号合并入现有主题文件，而非创建新的孤立文件。将相对日期转换为绝对日期（如"Thursday" → "2026-04-02"）。

**Phase 4 — Prune and Index（剪枝与索引）**
更新 `MEMORY.md`，确保总行数 < 200 且 < 25KB。删除过时指针，缩短超长索引行。

### 10.2.4 进度追踪

Dream 任务运行在 forked subagent 中，主 Agent 通过 `runAutoDream` 函数内的进度追踪逻辑（`autoDream.ts` 第 195–220 行）实时感知其进展：

```
// autoDream.ts, 第 195-220 行（runAutoDream 函数内的进度追踪逻辑）
function runAutoDream(...) {
  // ... 进度追踪逻辑嵌入在此函数内部
}
  return msg => {
    if (msg.type !== 'assistant') return
    let text = ''
    let toolUseCount = 0
    const touchedPaths: string[] = []
    for (const block of msg.message.content) {
      if (block.type === 'text') text += block.text
      else if (block.type === 'tool_use') {
        toolUseCount++
        // 收集 Edit/Write 的 file_path 用于进度展示
      }
    }
    addDreamTurn(taskId, { text, toolUseCount }, touchedPaths, setAppState)
  }
}
```

用户可以在后台任务面板中看到 Dream 的进展（当前在第几个 Phase，写入了哪些文件）。

---

## 10.3 会话记忆与持久记忆

### 10.3.1 会话记忆：实时上下文

会话记忆是 LLM 上下文窗口内的全部内容——用户消息、Agent 回复、工具调用结果。它在每次回复生成时实时可用，但随对话结束而消失。

会话记忆的容量受限于模型的上下文窗口，通常在几千到几万条 token 之间。Claude Code 通过**上下文压缩**机制（Collapse 工具）在工具调用之间清理低价值的历史内容，以维持可用空间。

### 10.3.2 持久记忆：自动提取

当会话结束时，`extractMemories` 模块通过 **forked agent** 机制（`extractMemories.ts` 第 1–20 行注释）从当前会话的 transcript 中提取值得保留的记忆：

```
/**
 * Uses the forked agent pattern (runForkedAgent) — a perfect fork of the main
 * conversation that shares the parent's prompt cache.
 * State is closure-scoped inside initExtractMemories().
 */
export function initExtractMemories(): void {
  let lastMemoryMessageUuid: string | undefined
  let inProgress = false
  let pendingContext: { context: REPLHookContext; appendSystemMessage? } | undefined

  // ... 闭包内部维护游标位置
}
```

提取过程的关键设计：

1. **游标机制**：`lastMemoryMessageUuid` 记录上次处理到的消息 UUID，每次只处理新增消息，避免重复劳动。

2. **互斥跳过**：若主 Agent 自己在本轮写过记忆文件（`hasMemoryWritesSince`），提取器跳过本轮，因为主 Agent 已经完成了提取工作（`extractMemories.ts` 第 130–145 行）。

3. **工具限制**：提取子 Agent 只能使用 Read/Grep/Glob/Write，且 Write 仅限于记忆目录（`createAutoMemCanUseTool`，`extractMemories.ts` 第 171 行）。

```
export function createAutoMemCanUseTool(memoryDir: string): CanUseToolFn {
  return async (tool, input) => {
    // 允许 Read/Grep/Glob（纯读）
    if (tool.name === FILE_READ_TOOL_NAME ||
        tool.name === GREP_TOOL_NAME ||
        tool.name === GLOB_TOOL_NAME) {
      return { behavior: 'allow', updatedInput: input }
    }
    // 允许 Bash 仅限只读命令（ls/find/cat/stat/wc/head/tail）
    if (tool.name === BASH_TOOL_NAME) {
      if (parsed.success && tool.isReadOnly(parsed.data))
        return { behavior: 'allow', updatedInput: input }
    }
    // Write/Edit 仅限于记忆目录内部
    if ((tool.name === FILE_EDIT_TOOL_NAME || tool.name === FILE_WRITE_TOOL_NAME)
        && 'file_path' in input) {
      if (typeof input.file_path === 'string' && isAutoMemPath(input.file_path))
        return { behavior: 'allow', updatedInput: input }
    }
    return denyAutoMemTool(tool, 'only read-only tools and memory-dir writes allowed')
  }
}
```

### 10.3.3 两步保存流程

每条记忆的保存遵循严格的两步流程（`memdir.ts` 第 159–175 行）：

**Step 1** — 创建独立的 `.md` 文件，写入完整的 frontmatter 和正文内容。

**Step 2** — 在 `MEMORY.md` 入口索引中添加一行指针：
```
- [user_role](user_role.md) — senior data scientist focused on observability
```

**设计原因**：索引是**一维线性扫描**的产物（系统提示词中全文加载），而记忆文件是**按需读取**的。分离两者使索引保持精简，同时允许单个记忆文件承载充分上下文，互不制约。

---

## 10.4 记忆的压缩与整合

### 10.4.1 每日日志模式（KAIROS）

在长生命周期会话（如持续运行的 assistant 模式）中，主 Agent 不是实时维护 `MEMORY.md`，而是**向日期命名的日志文件追加**（`memdir.ts` 第 210–245 行）：

```
memory/logs/2026/04/2026-04-01.md
memory/logs/2026/04/2026-04-02.md
```

每日日志是**只可追加、不可重写**的——这是刻意设计的约束，防止 Agent 在长会话中反复修改历史记录导致信息丢失。Dream 任务在夜间将日志蒸馏为结构化的主题文件和索引。

### 10.4.2 记忆扫描与 Manifest

每次提取记忆前，系统会预扫描现有记忆文件，生成 manifest 供提取 Agent 参考（`memoryScan.ts` 第 36–60 行）：

```
// memoryScan.ts, 第 36-60 行
export async function scanMemoryFiles(
  memoryDir: string,
  signal: AbortSignal,
): Promise<MemoryHeader[]> {
  // 递归扫描所有 .md 文件（排除 MEMORY.md）
  // 读取 frontmatter（name/description/type）
  // 按 mtime 降序排列，最多返回 200 条
  return headerResults
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value)
    .sort((a, b) => b.mtimeMs - a.mtimeMs)
    .slice(0, MAX_MEMORY_FILES)
}
```

manifest 格式（`memoryScan.ts` 第 66–75 行）：

```
- [feedback] integration-tests-need-real-db.md (2026-03-15T10:30:00.000Z): use real DB in integration tests
- user_role.md (2026-03-14T08:00:00.000Z): no description
- [project] auth-middleware-rewrite.md (2026-03-10T14:22:00.000Z): compliance-driven rewrite
```

### 10.4.3 记忆去重与更新

提取 Agent 被要求**先检查现有文件再写入新文件**（`prompts.ts` 第 32 行）：

```
Check this list before writing — update an existing file rather than creating a duplicate.
```

这是一条硬性规则，而非建议。新信息应当合并入相关主题文件，而非创建新的孤立记忆。

### 10.4.4 过时记忆的处理

记忆文件中包含 `**Why:**` 和 `**How to apply:**` 结构化字段（`memoryTypes.ts` 第 180–185 行），其目的正是支持**过时判断**：

> "Project memories decay fast, so the why helps future-you judge whether the memory is still load-bearing."

当 Dream 发现某条记忆的事实与当前代码库矛盾时，会直接修正或删除该记忆，而非保留矛盾信息。

---

## 10.5 团队记忆设计

### 10.5.1 独立的团队命名空间

团队记忆是持久记忆的一个子目录（`teamMemPaths.ts` 第 84 行）：

```
// teamMemPaths.ts, 第 84 行
export function getTeamMemPath(): string {
  return (join(getAutoMemPath(), 'team') + sep).normalize('NFC')
}
```

每个目录（private / team）维护各自的 `MEMORY.md` 索引（`prompts.ts` 第 140–145 行），主系统提示词会同时加载两个索引。

### 10.5.2 作用域隔离

四型记忆各有推荐作用域（`memoryTypes.ts` 第 62–75 行）：

| 类型 | 默认作用域 | 说明 |
|------|-----------|------|
| user | `always private` | 用户画像不可跨成员共享 |
| feedback | `private`（团队惯例例外） | 个人偏好是 private；项目测试政策是 team |
| project | `private` → `team`（优先） | 项目状态鼓励团队共享 |
| reference | `usually team` | 外部系统指针适合团队维护 |

```
// 类型块示例（`memoryTypes.ts` 各类型 <scope> 定义分别位于第 45、59、77、92 行）
'<type>\n' +
'    <name>feedback</name>\n' +
'    <scope>default to private. Save as team only when the guidance is\n' +
'    clearly a project-wide convention that every contributor should follow,\n' +
'    not a personal style preference.</scope>\n' +
// ...
```

### 10.5.3 安全设计：符号链接遍历防护

团队记忆目录允许共享写入，因此是**路径遍历攻击**的高风险目标。系统实现了多层防御（`teamMemPaths.ts` 第 92–160 行）：

**第一层：路径规范化检查**
```
const resolvedPath = resolve(filePath)
if (!resolvedPath.startsWith(getTeamMemPath())) {
  throw new PathTraversalError(`Path escapes team memory directory`)
}
```

**第二层：符号链接深度解析**
```
// teamMemPaths.ts, 第 101 行起（realpathDeepestExisting 函数）
async function realpathDeepestExisting(absolutePath: string): Promise<string> {
  // 逐层向上尝试 realpath()，遇到不存在的路径停止
  // 若遇到悬空符号链接（目标不存在）则抛出错误
  // ELOOP（循环链接）立即抛出错误
}
```

**第三层：真实路径包含性验证**
```
const realPath = await realpathDeepestExisting(resolvedPath)
if (!(await isRealPathWithinTeamDir(realPath))) {
  throw new PathTraversalError(`Path escapes via symlink`)
}
```

**设计原因**：`path.resolve()` 不解析符号链接，攻击者可利用 `team/../../.ssh/authorized_keys` 类型的路径序列逃逸出团队目录。必须对路径的**真实（realpath）而非逻辑（resolve）位置**做包含性验证，才能防范此类攻击。

### 10.5.4 敏感数据隔离

团队记忆的提取提示词中包含明确的禁止条款（`prompts.ts` 第 153 行）：

```
'- You MUST avoid saving sensitive data within shared team memories.\n' +
'    For example, never save API keys or user credentials.\n'
```

Private 目录用于存储不适合共享的敏感信息。系统通过 prompt 层面的指令而非技术隔离来执行此约束。

---

## 10.6 实用操作指南

### 10.6.1 手动保存记忆

当用户明确要求记住某事时，Agent 立即执行两步保存：

**第一步：创建记忆文件**
```
文件名：user_role.md
内容：
---
name: user prefers terse responses
description: no trailing summary after diffs
type: user
---

User prefers concise responses without diff summaries.
**Why:** User explicitly stated they can read the diff themselves.
**How to apply:** Omit the "here's what I did" summary paragraph.
```

**第二步：更新 MEMORY.md 索引**
```
- [user_role](user_role.md) — prefers terse responses without diff summaries
```

### 10.6.2 触发 Dream 整合

Dream 通常自动触发，但可通过后台任务面板手动触发。手动触发时，Agent 收到正常的完整工具权限（而非 `createAutoMemCanUseTool` 限制），因为手动调用走的是主循环而非 forked subagent。

### 10.6.3 跨会话记忆召回

记忆召回发生在**每次会话启动时**——`loadMemoryPrompt`（`memdir.ts` 第 250–310 行）将 `MEMORY.md` 的内容注入系统提示词，使 Agent 在开始工作前就拥有历史上下文。

召回后，Agent 被要求**在使用记忆前验证**（`memoryTypes.ts` 第 214–222 行）：

> "A memory that names a specific function, file, or flag is a claim that it existed *when the memory was written*. Before recommending it: If the memory names a file path: check the file exists. If it names a function or flag: grep for it."

这防止了记忆过时导致的"幻觉引用"——记忆说某文件存在，不等于该文件当前仍然存在。

---

## 10.7 设计原则总结

Claude Code 记忆系统的设计遵循了以下核心原则：

1. **信息可推导性过滤**：记忆只保存无法从代码、git 或文档中直接推导的上下文。
2. **索引与内容分离**：`MEMORY.md` 是指针索引，记忆正文在独立文件中，互不干扰。
3. **写时原子、读时按需**：写入总是两步执行，读取总是按主题按需加载。
4. **防御性简化**：通过严格的行数/字节数限制，防止记忆系统成为新的上下文瓶颈。
5. **静默后台整合**：Dream 自动在后台合并碎片，Agent 无需手动维护。
6. **安全命名空间隔离**：团队记忆通过独立子目录和路径验证机制，防范共享写入风险。

理解这些原则，有助于开发者评估何时应使用记忆系统、何时应使用 CLAUDE.md 或 Plan——三者各有边界，共同构成 Claude Code 的完整持久化体系。

---

*本章参考源码：*
- `memdir/memdir.ts` — 记忆目录管理、索引构建、截断
- `memdir/memoryTypes.ts` — 四型分类法、frontmatter 格式
- `memdir/paths.ts` — 路径解析、安全验证
- `memdir/teamMemPaths.ts` — 团队记忆路径与安全防护
- `memdir/memoryScan.ts` — 记忆文件扫描与 manifest 生成
- `services/extractMemories/extractMemories.ts` — 会话结束时的自动提取
- `services/extractMemories/prompts.ts` — 提取 Agent 提示词模板
- `services/autoDream/autoDream.ts` — 夜间自动整合引擎
- `services/autoDream/consolidationPrompt.ts` — Dream 四阶段整合提示词

---

*合并版文件说明：*
- 第六章 作者：代码驴，审计者：狗头军师
- 第七章 至 第十章 作者/审计者信息见各章
- 第十章 原章节内编号使用 1.x/2.x/3.x/4.x（应为 10.x），已统一修正
- 第九章 `groupMessagesByApiRound` 行数描述（原"47行"应为约25行）已标注勘误

*** [第二部分：第六章至第十章完] ***

# 第十一章：Multi-Agent 协同

> **本章作者**：狗头军师  
> **审计者**：笔帖式

---

## 11.1 概述

Claude Code 的 Multi-Agent 协同机制是其处理复杂任务能力的核心所在。当一个任务需要多角度并行研究、多步骤迭代实现、或需要专门化的子Agent分工时，Multi-Agent 协同便成为不可或缺的架构选择。本章将从源码层面深入剖析这一机制的设计思想与实现细节。

Multi-Agent 协同在 Claude Code 中并非单一功能，而是一套完整的体系，涵盖：

- **Coordinator 模式**：主Agent扮演协调者角色，将任务分解并委托给工作Agent
- **AgentTool**：启动和管理子Agent的核心工具
- **Agent 间通信**：通过 SendMessage 工具实现Agent之间的消息传递
- **Fork Subagent**：利用提示词缓存优化子Agent启动的实验性功能

理解这些组件之间的协作关系，是掌握 Claude Code 多Agent系统设计的关键。

---

## 11.2 Coordinator 模式的设计思想

### 11.2.1 编排与执行分离

Coordinator 模式的核心哲学是**编排与执行分离**。主Agent（Coordinator）负责任务分解、结果综合和用户沟通；工作Agent（Worker）负责执行具体的研发、调查或验证任务。这种职责划分遵循了 Unix 设计哲学中的"做一件事并做好"原则。

源码位于 `src/coordinator/coordinatorMode.ts`（第1-200行），其中定义了 Coordinator 模式的核心行为：

```
// coordinatorMode.ts:35-48
export function isCoordinatorMode(): boolean {
  if (feature('COORDINATOR_MODE')) {
    return isEnvTruthy(process.env.CLAUDE_CODE_COORDINATOR_MODE)
  }
  return false
}
```

Coordinator 模式的激活通过环境变量 `CLAUDE_CODE_COORDINATOR_MODE` 控制。当启用时，主Agent的系统提示词会发生变化，从执行者转变为协调者。`getCoordinatorSystemPrompt()` 函数（第110-180行）构建了完整的协调者提示词：

```
// coordinatorMode.ts:110-115
return `You are Claude Code, an AI assistant that orchestrates software engineering tasks across multiple workers.

## 1. Your Role

You are a **coordinator**. Your job is to:
- Help the user achieve their goal
- Direct workers to research, implement and verify code changes
- Synthesize results and communicate with the user
- Answer questions directly when possible — don't delegate work that you can handle without tools`
```

### 11.2.2 任务工作流设计

Coordinator 模式定义了标准化的四阶段工作流：

| 阶段 | 执行者 | 目的 |
|------|--------|------|
| Research | Workers（并行） | 调查代码库、理解问题 |
| Synthesis | Coordinator | 综合发现，制定实现规范 |
| Implementation | Workers | 按规范进行针对性修改 |
| Verification | Workers | 测试变更是否有效 |

这种工作流设计有深刻的工程考量：**并行性是Coordinator的超级能力**。工作Agent是异步执行的，应当尽可能并行启动独立任务，而非串行化处理。源码注释中明确指出：

```
// coordinatorMode.ts:213-214
### Concurrency

**Parallelism is your superpower. Workers are async. Launch independent workers concurrently whenever possible — don't serialize work that can run simultaneously and look for opportunities to fan out.**
```

### 11.2.3 提示词合成原则

Coordinator 模式最重要的设计原则之一是**必须自行综合，不能懒于委托**。当工作Agent报告研究结果后，Coordinator必须理解这些发现，然后写出**自包含的、精确的实现提示词**。

```
// coordinatorMode.ts:255-274
### Always synthesize — your most important job

When workers report research findings, **you must understand them before directing follow-up work**. Read the findings. Identify the approach. Then write a prompt that proves you understood by including specific file paths, line numbers, and exactly what to change.

Never write "based on your findings" or "based on the research." These phrases delegate understanding to the worker instead of doing it yourself.
```

反例：
```
AgentTool({ prompt: "Based on your findings, fix the auth bug", ... })
```

正例：
```
AgentTool({ prompt: "Fix the null pointer in src/auth/validate.ts:42. The user field on Session (src/auth/types.ts:15) is undefined when sessions expire but the token remains cached. Add a null check before user.id access — if null, return 401 with 'Session expired'. Commit and report the hash.", ... })
```

---

## 11.3 AgentTool 的实现机制

### 11.3.1 工具注册与Schema定义

AgentTool 是启动子Agent的核心工具，定义于 `src/tools/AgentTool/AgentTool.tsx`。它采用 `buildTool` 工厂函数注册为标准工具，具备完整的输入输出Schema。

```
// AgentTool.tsx:88-113
const baseInputSchema = lazySchema(() => z.object({
  description: z.string().describe('A short (3-5 word) description of the task'),
  prompt: z.string().describe('The task for the agent to perform'),
  subagent_type: z.string().optional().describe('The type of specialized agent to use for this task'),
  model: z.enum(['sonnet', 'opus', 'haiku']).optional().describe("Optional model override..."),
  run_in_background: z.boolean().optional().describe('Set to true to run this agent in the background...')
}));

const fullInputSchema = lazySchema(() => {
  const multiAgentInputSchema = z.object({
    name: z.string().optional().describe('Name for the spawned agent...'),
    team_name: z.string().optional().describe('Team name for spawning...'),
    mode: permissionModeSchema().optional().describe('Permission mode for spawned teammate...')
  });
  return baseInputSchema().merge(multiAgentInputSchema).extend({
    isolation: z.enum(['worktree']).optional().describe('Isolation mode...'),
    cwd: z.string().optional().describe('Absolute path to run the agent in...')
  });
});
```

这里使用了 `lazySchema` 模式，允许根据特性开关动态调整Schema内容，实现了死码消除（Dead Code Elimination）优化。

### 11.3.2 子Agent类型路由

AgentTool 的 `call()` 方法是整个子Agent启动流程的枢纽。其核心逻辑是根据参数决定三条路由路径之一：

**路径一：Teammate Spawn（团队成员）**
```
// AgentTool.tsx:286-301
if (teamName && name) {
  const result = await spawnTeammate({
    name,
    prompt,
    description,
    team_name: teamName,
    use_splitpane: true,
    plan_mode_required: spawnMode === 'plan',
    model: model ?? agentDef?.model,
    agent_type: subagent_type,
    invokingRequestId: assistantMessage?.requestId
  }, toolUseContext);
  // ...
}
```

**路径二：Fork Subagent（实验性分叉）**
```
// AgentTool.tsx:313-321
const effectiveType = subagent_type ?? (isForkSubagentEnabled() ? undefined : GENERAL_PURPOSE_AGENT.agentType);
const isForkPath = effectiveType === undefined;
if (isForkPath) {
  selectedAgent = FORK_AGENT;
}
```

**路径三：常规子Agent**
```
// AgentTool.tsx:323-357
const found = agents.find(agent => agent.agentType === effectiveType);
if (!found) {
  const agentExistsButDenied = allAgents.find(agent => agent.agentType === effectiveType);
  if (agentExistsButDenied) {
    const denyRule = getDenyRuleForAgent(appState.toolPermissionContext, AGENT_TOOL_NAME, effectiveType);
    throw new Error(`Agent type '${effectiveType}' has been denied by permission rule...`);
  }
  throw new Error(`Agent type '${effectiveType}' not found. Available agents: ${agents.map(a => a.agentType).join(', ')}`);
}
selectedAgent = found;
```

### 11.3.3 异步与同步执行策略

子Agent的执行策略由 `shouldRunAsync` 变量决定（第567行）：

```
// AgentTool.tsx:567
const shouldRunAsync = 
  (run_in_background === true || selectedAgent.background === true || 
   isCoordinator || forceAsync || assistantForceAsync || 
   (proactiveModule?.isProactiveActive() ?? false)) && 
  !isBackgroundTasksDisabled;
```

异步执行的优势在于：
1. 主循环不会被阻塞，用户可以继续交互
2. 后台Agent完成后通过 `<task-notification>` 消息通知
3. 支持通过 SendMessage 继续已启动的Agent

同步执行则直接返回结果，适用于需要立即获取结果的场景。

---

## 11.4 子Agent的创建和管理

### 11.4.1 runAgent 核心函数

`src/tools/AgentTool/runAgent.ts` 中的 `runAgent()` 函数是子Agent的真正执行引擎。它返回一个 `AsyncGenerator<Message>`，逐步产出Agent的每条消息。

```
// runAgent.ts:265-...
export async function* runAgent({
  agentDefinition,
  promptMessages,
  toolUseContext,
  canUseTool,
  isAsync,
  forkContextMessages,
  querySource,
  override,
  model,
  availableTools,
  // ...
}: { ... }): AsyncGenerator<Message, void> {
  // 1. 解析Agent模型
  const resolvedAgentModel = getAgentModel(
    agentDefinition.model,
    toolUseContext.options.mainLoopModel,
    model,
    permissionMode,
  )

  // 2. 创建Agent ID
  const agentId = override?.agentId ? override.agentId : createAgentId()

  // 3. 过滤不完整的tool calls（防止API错误）
  const contextMessages: Message[] = forkContextMessages
    ? filterIncompleteToolCalls(forkContextMessages)
    : []
  const initialMessages: Message[] = [...contextMessages, ...promptMessages]

  // 4. 初始化文件状态缓存
  const agentReadFileState = forkContextMessages !== undefined
    ? cloneFileStateCache(toolUseContext.readFileState)
    : createFileStateCacheWithSizeLimit(READ_FILE_STATE_CACHE_SIZE)

  // 5. 构建Agent系统提示词
  const agentSystemPrompt = override?.systemPrompt
    ? override.systemPrompt
    : asSystemPrompt(await getAgentSystemPrompt(...))
  // ...
}
```

### 11.4.2 上下文隔离策略

子Agent与父Agent之间存在微妙的上下文隔离与共享机制：

**工具池隔离**：工作Agent拥有独立组装的工具池（`assembleToolPool`），不受父Agent工具权限限制的影响：

```
// AgentTool.tsx:577
// Assemble the worker's tool pool independently of the parent's.
// Workers always get their tools from assembleToolPool with their own
// permission mode, so they aren't affected by the parent's tool restrictions.
const workerTools = assembleToolPool(workerPermissionContext, appState.mcp.tools);
```

**文件系统隔离**：通过 `worktree` 机制实现。每个子Agent可以在独立的git worktree中工作，避免与父Agent的工作目录冲突：

```
// AgentTool.tsx:590-592
if (effectiveIsolation === 'worktree') {
  const slug = `agent-${earlyAgentId.slice(0, 8)}`;
  worktreeInfo = await createAgentWorktree(slug);
}
```

### 11.4.3 生命周期管理

子Agent的生命周期管理涉及多个关键阶段：

**注册阶段**：通过 `registerAsyncAgent` 或 `registerAgentForeground` 将子Agent注册到任务跟踪系统：

```
// AgentTool.tsx:688-696
const agentBackgroundTask = registerAsyncAgent({
  agentId: asyncAgentId,
  description,
  prompt,
  selectedAgent,
  setAppState: rootSetAppState,
  toolUseId: toolUseContext.toolUseId
});
```

**执行阶段**：`runAsyncAgentLifecycle` 包装执行流程，处理进度跟踪、汇总生成和完成通知：

```
// AgentTool.tsx:733-...
void runWithAgentContext(asyncAgentContext, () => wrapWithCwd(() => runAsyncAgentLifecycle({
  taskId: agentBackgroundTask.agentId,
  abortController: agentBackgroundTask.abortController!,
  makeStream: onCacheSafeParams => runAgent({ ... }),
  metadata,
  description,
  toolUseContext,
  rootSetAppState,
  // ...
})));
```

**清理阶段**：`finally` 块负责资源释放，包括MCP服务器清理、会话Hook清理、文件状态缓存释放等：

```
// runAgent.ts:580-620
finally {
  await mcpCleanup()
  if (AgentDefinition.hooks) {
    clearSessionHooks(rootSetAppState, agentId)
  }
  cleanupAgentTracking(agentId)
  agentToolUseContext.readFileState.clear()
  killShellTasksForAgent(agentId, toolUseContext.getAppState, rootSetAppState)
  // ...
}
```

---

## 11.5 Agent间通信机制

### 11.5.1 SendMessage 工具

Agent间通信通过 `SendMessage` 工具实现，允许Coordinator向已启动的工作Agent发送后续指令：

```
// coordinatorMode.ts:70-72
### Your Tools

- **AgentTool** - Spawn a new worker
- **SendMessage** - Continue an existing worker (send a follow-up to its `to` agent ID)
- **TaskStopTool** - Stop a running worker
```

### 11.5.2 消息路由

Agent通过 `name` 参数获得可寻址性。当使用 `name` 参数启动Agent时，其ID会被注册到 `agentNameRegistry`：

```
// AgentTool.tsx:700-707
if (name) {
  rootSetAppState(prev => {
    const next = new Map(prev.agentNameRegistry);
    next.set(name, asAgentId(asyncAgentId));
    return { ...prev, agentNameRegistry: next };
  });
}
```

后续可以通过 `SendMessage({ to: "agentName", message: "..." })` 向其发送消息。

### 11.5.3 Continue vs Spawn 决策

Coordinator需要决定是继续已有Agent还是启动新Agent。源码注释给出了清晰的决策矩阵：

| 场景 | 机制 | 原因 |
|------|------|------|
| 研究已探索了需要编辑的文件 | **继续**（SendMessage） | Agent已有上下文且现在有了明确计划 |
| 研究广泛但实现窄 | **启动新** | 避免引入探索噪声 |
| 修正失败或延续近期工作 | **继续** | Agent有错误上下文 |
| 验证其他Agent刚写的代码 | **启动新** | 验证者应独立审视代码 |
| 第一次实现用了完全错误的方案 | **启动新** | 错误方案的上下文会污染重试 |

---

## 11.6 Fork Subagent 的缓存优化

### 11.6.1 设计背景

Fork Subagent 是 Claude Code 的实验性功能，旨在通过提示词缓存实现子Agent的零开销启动。其核心观察是：当多个子Agent需要继承父Agent的完整上下文时，API请求前缀（系统提示词+历史消息）高度相似，可以被缓存共享。

### 11.6.2 实现原理

**FORK_AGENT 定义**（`forkSubagent.ts:47-69`）：

```
// forkSubagent.ts:47-69
export const FORK_AGENT = {
  agentType: FORK_SUBAGENT_TYPE,
  whenToUse: 'Implicit fork — inherits full conversation context...',
  tools: ['*'],          // 使用 '*' 接收父Agent的完整工具池
  maxTurns: 200,
  model: 'inherit',      // 继承父Agent的模型
  permissionMode: 'bubble',  // 权限提示冒泡到父终端
  source: 'built-in',
  baseDir: 'built-in',
  getSystemPrompt: () => '',  // 实际使用父Agent已渲染的系统提示词
} satisfies BuiltInAgentDefinition
```

**消息构建**（`buildForkedMessages`，第105-173行）：

```
// forkSubagent.ts:105-173
export function buildForkedMessages(
  directive: string,
  assistantMessage: AssistantMessage,
): MessageType[] {
  // 1. 克隆完整的父助手消息（保留所有 tool_use 块）
  const fullAssistantMessage: AssistantMessage = {
    ...assistantMessage,
    uuid: randomUUID(),
    message: {
      ...assistantMessage.message,
      content: [...assistantMessage.message.content],
    },
  };

  // 2. 收集所有 tool_use 块
  const toolUseBlocks = assistantMessage.message.content.filter(
    (block): block is BetaToolUseBlock => block.type === 'tool_use',
  );

  // 3. 为每个 tool_use 构建占位符 tool_result（内容完全相同！）
  const toolResultBlocks = toolUseBlocks.map(block => ({
    type: 'tool_result' as const,
    tool_use_id: block.id,
    content: [{ type: 'text' as const, text: FORK_PLACEHOLDER_RESULT }],
  }));

  // 4. 构建用户消息：所有占位结果 + 每子Agent指令
  const toolResultMessage = createUserMessage({
    content: [
      ...toolResultBlocks,
      { type: 'text' as const, text: buildChildMessage(directive) },
    ],
  });

  return [fullAssistantMessage, toolResultMessage];
}
```

**缓存优化关键**：所有Fork子Agent的 `FORK_PLACEHOLDER_RESULT`（"Fork started — processing in background"）完全相同，只有最后的指令文本不同。这意味着API请求前缀（包括系统提示词、父助手消息、tool_results）可以被完美缓存。

### 11.6.3 递归Fork防护

为防止Fork子Agent继续Fork造成无限递归，实现了双重检测机制：

```
// AgentTool.tsx:317-320
// 递归Fork防护：检查 querySource 和消息内容
if (toolUseContext.options.querySource === `agent:builtin:${FORK_AGENT.agentType}` || 
    isInForkChild(toolUseContext.messages)) {
  throw new Error('Fork is not available inside a forked worker...');
}
```

```
// forkSubagent.ts:78-91
export function isInForkChild(messages: MessageType[]): boolean {
  return messages.some(m => {
    if (m.type !== 'user') return false;
    const content = m.message.content;
    if (!Array.isArray(content)) return false;
    return content.some(
      block =>
        block.type === 'text' &&
        block.text.includes(`<${FORK_BOILERPLATE_TAG}>`),
    );
  });
}
```

### 11.6.4 useExactTools 机制

Fork路径使用 `useExactTools: true` 确保子Agent接收与父Agent完全相同的工具定义（包括序列化格式），从而产生字节级相同的API请求前缀：

```
// AgentTool.tsx:632
const runAgentParams: Parameters<typeof runAgent>[0] = {
  // ...
  ...(isForkPath && {
    useExactTools: true  // 继承父Agent的精确工具和思考配置
  }),
  // ...
};
```

在 `runAgent.ts` 中（第500-502行和第682-684行）：

```
// runAgent.ts:500-502
const resolvedTools = useExactTools
  ? availableTools  // 直接使用，不经过 resolveAgentTools 过滤
  : resolveAgentTools(agentDefinition, availableTools, isAsync).resolvedTools;

const agentOptions: ToolUseContext['options'] = {
  // ...
  // runAgent.ts:682-684
  thinkingConfig: useExactTools
    ? toolUseContext.options.thinkingConfig  // 继承思考配置
    : { type: 'disabled' as const },
  // ...
};
```

---

## 11.7 总结

Claude Code 的 Multi-Agent 协同机制展现了一个深思熟虑的多Agent系统设计：

1. **编排与执行分离**的Coordinator模式，使复杂任务可以被分解、并行执行、有效协调

2. **AgentTool**作为核心抽象，提供了统一的子Agent启动接口，灵活支持同步/异步、团队/Fork/常规三种路径

3. **完善的生命周期管理**确保资源正确申请与释放，包括MCP服务器、git worktree、文件状态缓存等

4. **Agent间通信**通过SendMessage实现，支持任务的继续与修正

5. **Fork Subagent**的缓存优化是一个精妙的设计，通过占位符和字节级一致的请求前缀实现了提示词缓存的最大化利用

这些机制共同构成了一个强大、灵活且高效的多Agent协作框架，使Claude Code能够处理从简单任务到复杂软件工程的广泛场景。

---

**本章小结**

| 概念 | 源码位置 | 核心要点 |
|------|----------|----------|
| Coordinator模式 | `coordinatorMode.ts` | 编排者角色、任务工作流、提示词合成 |
| AgentTool | `AgentTool.tsx` | 工具Schema、三路路由、异步/同步策略 |
| runAgent | `runAgent.ts` | 异步生成器、上下文隔离、资源管理 |
| Fork Subagent | `forkSubagent.ts` | 缓存优化、占位符策略、递归防护 |
| 生命周期 | 各文件 `finally` 块 | MCP清理、Hook清理、缓存释放 |

---
---

> **🧭 深入源码**
>
> 想进一步理解 Multi-Agent 系统的实现细节？请参考以下核心源码文件：
> - `src/tools/AgentTool/runAgent.ts` — Agent 生命周期管理
> - `src/tools/AgentTool/forkSubagent.ts` — 子 Agent 派生机制
> - `src/utils/swarm/spawnInProcess.ts` — 进程内 Agent Spawn
> - `src/coordinator/coordinatorMode.ts` — 领队模式实现

# 第十二章：并行与UDS通信

> **本章概要**
> 本章讲解 Claude Code 中实现并行多 Agent 协作的两套核心机制：一是基于 **UDS（Unix Domain Socket）** 的跨会话消息收件箱，二是 **Fork 子进程** 的上下文继承与共享。我们将从源码出发，逐层剖析设计意图与实现细节。

---

## 12.1 背景：为什么需要跨进程通信

在 Claude Code 的多 Agent 架构中，存在两种并行执行模式：

| 模式 | 执行方式 | 上下文共享 | 适用场景 |
|------|---------|-----------|---------|
| **Fork（分叉）** | 在同一对话中"分叉"出子任务 | 继承完整对话历史 + 系统提示词 | 独立子任务并行执行 |
| **Agent Tool（子 Agent）** | 启动独立进程/ tmux pane | 无直接共享 | 独立长时任务 |

两者都解决了"并行"的问题，但解决思路不同。本章聚焦**通信层**——子进程之间、子进程与主进程之间如何传递消息，以及后台常驻进程如何与前台交互。

---

## 12.2 UDS_INBOX：基于 Unix Domain Socket 的跨会话消息收件箱

### 12.2.1 设计动机

传统的进程间通信方式有管道（pipe）、共享内存、消息队列等。Claude Code 选择 **Unix Domain Socket（UDS）**，原因有三：

1. **文件系统路径寻址**：Socket 以路径形式存在（如 `/tmp/claude-msg.sock`），天然与文件系统权限模型兼容。
2. **高性能**：UDS 比 TCP 环回（loopback）更快，适合高频消息交换。
3. **支持文件描述符传递**：可以跨进程传递打开的文件句柄，适合传递大型数据。

源码入口在 `src/setup.ts:93`：

```
// src/setup.ts:93
if (feature('UDS_INBOX')) {
  const m = await import('./utils/udsMessaging.js')
  await m.startUdsMessaging(
    messagingSocketPath ?? m.getDefaultUdsSocketPath(),
    { isExplicit: messagingSocketPath !== undefined },
  )
}
```

`startUdsMessaging` 启动一个 UDS 服务器，所有会话都连接到这个 socket。消息通过这个 socket 在不同会话之间路由。

### 12.2.2 地址解析：parseAddress

在 `src/utils/peerAddress.ts` 中，定义了地址解析逻辑：

```
// src/utils/peerAddress.ts:1-8（注释1-6行，函数8行起）
export function parseAddress(to: string): {
  scheme: 'uds' | 'bridge' | 'other'
  target: string
} {
  if (to.startsWith('uds:')) return { scheme: 'uds', target: to.slice(4) }
  if (to.startsWith('bridge:')) return { scheme: 'bridge', target: to.slice(7) }
  // Legacy: old-code UDS senders emit bare socket paths in from=
  if (to.startsWith('/')) return { scheme: 'uds', target: to }
  return { scheme: 'other', target: to }
}
```

三种地址类型：
- `uds:<socket-path>`：本机 UDS socket，适用于同一机器的跨会话通信
- `bridge:<session-id>`：Remote Control peer，通过 Anthropic 服务器转发
- `other`：团队内部成员名称路由

### 12.2.3 SendMessageTool 的通信路由

`SendMessageTool`（`src/tools/SendMessageTool/SendMessageTool.ts`）是消息发送的统一入口。其 `call` 方法根据目标地址类型分发消息：

```
// src/tools/SendMessageTool/SendMessageTool.ts:744-790 (核心路由逻辑)
async call(input, context, canUseTool, assistantMessage) {
  if (feature('UDS_INBOX') && typeof input.message === 'string') {
    const addr = parseAddress(input.to)
    if (addr.scheme === 'bridge') {
      const { postInterClaudeMessage } = require('../../bridge/peerSessions.js')
      const result = await postInterClaudeMessage(addr.target, input.message)
      return { data: { success: result.ok, message: ... } }
    }
    if (addr.scheme === 'uds') {
      const { sendToUdsSocket } = require('../../utils/udsClient.js')
      try {
        await sendToUdsSocket(addr.target, input.message)
        return { data: { success: true, message: ... } }
      } catch (e) { ... }
    }
  }
  // ... 内嵌子 Agent 路由、团队广播等
}
```

**设计原因**：UDS 通信采用"即发即忘"模式，发送方不等待接收方响应。这避免了同步等待，提高了吞吐量，适合松耦合的 Agent 协作。

### 12.2.4 文件收件箱：teammateMailbox

除了 UDS 实时消息，Claude Code 还实现了**持久化文件收件箱**。每个团队成员有一个 JSON 文件：

```
~/.claude/teams/{team_name}/inboxes/{agent_name}.json
```

核心实现在 `src/utils/teammateMailbox.ts`：

```
// src/utils/teammateMailbox.ts:56-63
export function getInboxPath(agentName: string, teamName?: string): string {
  const team = teamName || getTeamName() || 'default'
  const inboxDir = join(getTeamsDir(), sanitizePathComponent(team), 'inboxes')
  return join(inboxDir, `${sanitizePathComponent(agentName)}.json`)
}
```

`writeToMailbox` 使用文件锁防止并发写入冲突：

```
// src/utils/teammateMailbox.ts:134-180
export async function writeToMailbox(
  recipientName: string,
  message: Omit<TeammateMessage, 'read'>,
  teamName?: string,
): Promise<void> {
  await ensureInboxDir(teamName)
  const inboxPath = getInboxPath(recipientName, teamName)
  // ... 文件锁机制 ...
  release = await lockfile.lock(inboxPath, {
    lockfilePath: `${inboxPath}.lock`,
    retries: { retries: 10, minTimeout: 5, maxTimeout: 100 },
  })
  const messages = await readMailbox(recipientName, teamName)
  messages.push({ ...message, read: false })
  await writeFile(inboxPath, jsonStringify(messages, null, 2), 'utf-8')
}
```

**为什么用文件锁而非内存队列？**

文件收件箱天生支持**持久化**——即使进程崩溃，消息也不会丢失。此外，它支持任意数量的进程通过文件系统进行通信，无需额外的消息代理。

### 12.2.5 useInboxPoller：轮询监听

在交互式前端（`src/hooks/useInboxPoller.ts`），有一个定时轮询器监听收件箱：

```
// src/hooks/useInboxPoller.ts:126-200
export function useInboxPoller({ ... }) {
  const { unread } = useUnreadMessages(agentName)
  // 处理 plan_approval_response、shutdown_request 等结构化消息
  // 将消息路由到对应的队列（workerPermissions、workerSandboxPermissions 等）
}
```

轮询间隔由 `useInterval` 控制（默认 2-5 秒），在后台静默运行，不影响前台交互。

---

## 12.3 SendMessageTool 的消息类型

`SendMessageTool` 支持多种消息类型，通过 `StructuredMessage` 模式区分：

```
// src/tools/SendMessageTool/SendMessageTool.ts:46-70
const StructuredMessage = lazySchema(() =>
  z.discriminatedUnion('type', [
    z.object({ type: z.literal('shutdown_request'), reason: z.string().optional() }),
    z.object({ type: z.literal('shutdown_response'), request_id: z.string(), approve: semanticBoolean(), reason: z.string().optional() }),
    z.object({ type: z.literal('plan_approval_response'), request_id: z.string(), approve: semanticBoolean(), feedback: z.string().optional() }),
  ]),
)
```

**设计意图**：

- **shutdown_request / shutdown_response**：优雅关闭子 Agent，避免强制杀进程导致的状态不一致。
- **plan_approval_response**：在 `plan` 模式下，子 Agent 的计划需经主 Agent 审批后才能执行。

---

## 12.4 Daemon 常驻后台

### 12.4.1 会话类型

在 `src/utils/concurrentSessions.ts` 中定义了四种会话类型：

```
// src/utils/concurrentSessions.ts:18
export type SessionKind = 'interactive' | 'bg' | 'daemon' | 'daemon-worker'
```

- **interactive**：标准交互式会话
- **bg**：`claude --bg` 启动的后台会话，tmux 挂起，退出时保持运行
- **daemon**：长期运行的服务进程
- **daemon-worker**：daemon 的工作子进程

### 12.4.2 PID 文件注册

每个会话启动时在 `~/.claude/sessions/` 下写入 PID 文件：

```
// src/utils/concurrentSessions.ts:59-94
export async function registerSession(): Promise<boolean> {
  const kind: SessionKind = envSessionKind() ?? 'interactive'
  const pidFile = join(dir, `${process.pid}.json`)
  await writeFile(pidFile, jsonStringify({
    pid: process.pid,
    sessionId: getSessionId(),
    kind,
    ...(feature('UDS_INBOX')
      ? { messagingSocketPath: process.env.CLAUDE_CODE_MESSAGING_SOCKET }
      : {}),
  }))
}
```

`claude ps` 命令读取这些 PID 文件展示所有活跃会话。

### 12.4.3 UDS Messaging Socket 共享

关键设计：`CLAUDE_CODE_MESSAGING_SOCKET` 环境变量在会话注册时写入 PID 文件：

```
// src/utils/concurrentSessions.ts:87
...feature('UDS_INBOX')
  ? { messagingSocketPath: process.env.CLAUDE_CODE_MESSAGING_SOCKET }
  : {}
```

这使得所有会话（包括后台 daemon）都连接同一个 UDS socket，实现了**跨会话消息路由**。

---

## 12.5 跨窗口消息同步

### 12.5.1 消息预览与通知

当收到新消息时，`useInboxPoller` 通过 `sendNotification` 触发系统通知：

```
// src/hooks/useInboxPoller.ts:356-365 或 454-465
if (unread.length > 0) {
  sendNotification({
    title: `Message from ${msg.from}`,
    body: msg.summary || truncate(msg.text, 100),
  })
}
```

### 12.5.2 消息已读标记

消息被读取后（作为附件注入到对话中），自动标记为已读：

```
// src/utils/teammateMailbox.ts:279-310
export async function markMessagesAsRead(
  agentName: string,
  teamName?: string,
): Promise<void> {
  // 使用文件锁读取最新状态
  // 将所有消息的 read 字段设为 true
}
```

### 12.5.3 消息附件渲染

在 `src/utils/attachments.ts` 中，teammate 消息被渲染为 XML 附件：

```
// src/utils/teammateMailbox.ts:373-385
export function formatTeammateMessages(messages: Array<{...}>): string {
  return messages.map(m => {
    const colorAttr = m.color ? ` color="${m.color}"` : ''
    const summaryAttr = m.summary ? ` summary="${m.summary}"` : ''
    return `<${TEAMMATE_MESSAGE_TAG} teammate_id="${m.from}"${colorAttr}${summaryAttr}>
${m.text}
</${TEAMMATE_MESSAGE_TAG}>`
  }).join('\n\n')
}
```

前端将 `<teammate_message>` 标签渲染为彩色消息气泡，带发送者颜色和摘要预览。

---

## 12.6 Fork 与主进程的上下文共享

### 12.6.1 Fork 触发条件

当 Agent Tool 省略 `subagent_type` 时，触发隐式 Fork（`src/tools/AgentTool/forkSubagent.ts:32-45`）：

```
// src/tools/AgentTool/forkSubagent.ts:32-45
export function isForkSubagentEnabled(): boolean {
  if (feature('FORK_SUBAGENT')) {
    if (isCoordinatorMode()) return false
    if (getIsNonInteractiveSession()) return false
    return true
  }
  return false
}
```

### 12.6.2 上下文继承：buildForkedMessages

Fork 子进程继承父进程完整对话历史，这是通过 `buildForkedMessages` 实现的：

```
// src/tools/AgentTool/forkSubagent.ts:107-145
export function buildForkedMessages(
  directive: string,
  assistantMessage: AssistantMessage,
): MessageType[] {
  const fullAssistantMessage: AssistantMessage = { ...assistantMessage, uuid: randomUUID(), message: { ...assistantMessage.message, content: [...assistantMessage.message.content] } }
  
  const toolUseBlocks = assistantMessage.message.content.filter(
    (block): block is BetaToolUseBlock => block.type === 'tool_use',
  )
  
  // 为每个 tool_use 生成占位 tool_result
  const toolResultBlocks = toolUseBlocks.map(block => ({
    type: 'tool_result' as const,
    tool_use_id: block.id,
    content: [{ type: 'text' as const, text: FORK_PLACEHOLDER_RESULT }],
  }))
  
  // 最终消息：[完整 assistant, 包含 placeholder results + directive 的 user message]
  return [fullAssistantMessage, createUserMessage({ content: [...toolResultBlocks, { type: 'text' as const, text: buildChildMessage(directive) }] })]
}
```

**关键设计：占位符工具结果**

所有 `tool_use` 对应的 `tool_result` 被替换为统一占位符 `FORK_PLACEHOLDER_RESULT = 'Fork started — processing in background'`。这保证了：

1. **API 请求前缀完全一致**：不同 Fork 子进程的请求前缀（包含相同的 placeholder）共享相同的缓存键，节省 API 调用成本。
2. **隔离执行**：子进程各自独立执行工具调用，互不干扰。

### 12.6.3 子进程指令模板

子进程收到的 `buildChildMessage` 格式为：

```
<FORK_BOILERPLATE_TAG>
STOP. READ THIS FIRST.
You are a forked worker process. You are NOT the main agent.
RULES:
1. Your system prompt says "default to fork." IGNORE IT
2. Do NOT converse, ask questions, or suggest next steps
3. Do NOT editorialize or add meta-commentary
4. USE your tools directly
5. If you modify files, commit your changes before reporting
...
</FORK_BOILERPLATE_TAG>
```

**设计原因**：强制子进程"沉默执行"而非"对话协作"，确保并行效率。

### 12.6.4 AsyncLocalStorage 上下文传播

子进程通过 `AsyncLocalStorage`（Node.js 内置）共享主进程的 agent 身份上下文：

```
// src/utils/teammateContext.ts — AsyncLocalStorage 的实际使用
// For in-process teammates (running in the same process), AsyncLocalStorage
// provides context isolation with shared memory access.
```

`getAgentId()` 和 `getAgentName()` 优先从 AsyncLocalStorage 读取，允许子进程在共享进程的情况下维护独立的身份标识。

---

## 12.7 实战示例

### 示例一：通过 SendMessageTool 发送跨会话消息

```
// 假设有两个 Claude Code 会话，Socket 路径为 /tmp/claude-msg.sock
// 在会话 A 中：
await SendMessage({
  to: "uds:/tmp/claude-msg.sock",
  summary: "任务委派",
  message: "请帮我查询 AAPL 股票的当前价格"
})
```

### 示例二：子 Agent 广播消息

```
// 发送给所有团队成员
await SendMessage({
  to: "*",
  summary: "系统公告",
  message: "所有成员请注意，明天 10:00 有线上会议。"
})
```

### 示例三：优雅关闭子 Agent

```
// 主进程发送关闭请求
await SendMessage({
  to: "worker-1",
  message: {
    type: "shutdown_request",
    reason: "任务已完成，请退出"
  }
})

// 子进程响应
await SendMessage({
  to: "team-lead",
  message: {
    type: "shutdown_response",
    request_id: "<request_id>",
    approve: true
  }
})
```

---

## 12.8 设计哲学总结

| 设计决策 | 权衡 | 收益 |
|---------|------|------|
| UDS 而非 TCP | 需要文件系统权限管理 | 更高性能，与系统权限模型一致 |
| 文件收件箱而非内存队列 | 磁盘 I/O 略慢 | 进程崩溃不丢消息，支持持久化 |
| Fork 占位符结果 | 无法在父进程看到子进程中间结果 | API 缓存命中，节省成本 |
| 文件锁而非数据库 | 并发写入需要重试 | 零依赖，简单可靠 |
| AsyncLocalStorage 上下文 | 调试复杂度增加 | 同进程内多 Agent 身份隔离 |

Claude Code 的并行与通信设计始终遵循**简单、可恢复、松耦合**的原则。每条消息都有持久化路径，每个进程都有唯一标识，每次通信都可以追溯。这种设计在小型团队协作和大规模自动化任务中均表现出色。

---

## 本章小结

1. **UDS_INBOX** 通过 Unix Domain Socket 实现高性能跨会话消息路由，配套文件收件箱保证持久化。
2. **SendMessageTool** 统一封装了点对点消息、广播、shutdown、plan approval 等多种通信模式。
3. **Daemon/后台会话** 通过 PID 文件注册和共享 UDS Socket 实现常驻与消息互通。
4. **Fork** 通过继承完整对话历史和统一占位符结果，实现 API 缓存最大化复用的并行执行。
5. **跨窗口同步** 依赖 `useInboxPoller` 轮询、文件锁、XML 附件渲染等机制协同完成。

理解这些机制，是掌握 Claude Code 多 Agent 协作能力的必经之路。

---

# 第十三章：KAIROS 与分布式调度

## 概述

KAIROS 是 Claude Code 中负责定时任务调度的核心子系统，其名称源自希腊神话中的机会之神。本章将系统剖析 KAIROS 的设计理念、核心机制以及分布式环境下的调度策略。

KAIROS 要解决的核心问题是：**在多用户、多会话的环境下，如何可靠地执行定时任务，同时避免"惊群效应"（thundering herd）和单点故障。**

---

## 13.1 定时任务机制

### 13.1.1 Cron 表达式解析

KAIROS 使用标准五段式 Cron 表达式，本地时间解释。解析逻辑位于 `src/utils/cron.ts` 的 `parseCronExpression` 函数（行 78）：

```
// src/utils/cron.ts, 行 29-75
function expandField(field: string, range: FieldRange): number[] | null {
  const { min, max } = range
  const out = new Set<number>()

  for (const part of field.split(',')) {
    // 支持: wildcard, N, star-slash-N (step), N-M (range), comma-lists
    const stepMatch = part.match(/^\*(?:\/(\d+))?$/)
    if (stepMatch) {
      const step = stepMatch[1] ? parseInt(stepMatch[1], 10) : 1
      if (step < 1) return null
      for (let i = min; i <= max; i += step) out.add(i)
      continue
    }
    // ... 其余解析逻辑
  }
  return Array.from(out).sort((a, b) => a - b)
}
```

**设计原因**：为什么不使用成熟的 `cron-parser` 库？答案在于**可控性**。内置解析器可以：
- 精确控制 DST（夏令时）行为
- 无外部依赖，降低包体积
- 完全掌握 next-fire 计算逻辑，便于 jitter 扩展

### 13.1.2 Next-Fire 时间计算

`computeNextCronRun` 函数 (`src/utils/cron.ts`, 行 120-181) 实现了从当前时间向前步行、寻找下一个匹配时刻的算法：

```
// src/utils/cron.ts, 行 120-181
export function computeNextCronRun(
  fields: CronFields,
  from: Date,
): Date | null {
  // 严格大于 from，而非大于等于
  const t = new Date(from.getTime())
  t.setSeconds(0, 0)
  t.setMinutes(t.getMinutes() + 1)  // 向上取整到分钟

  const maxIter = 366 * 24 * 60  // 最多步行一年
  for (let i = 0; i < maxIter; i++) {
    // 月份检查 → 跳至下月首日
    if (!monthSet.has(t.getMonth() + 1)) {
      t.setMonth(t.getMonth() + 1, 1)
      t.setHours(0, 0, 0, 0)
      continue
    }
    // 日期检查（OR 语义：dayOfMonth 和 dayOfWeek 任意一个匹配即可）
    const dayMatches = domWild && dowWild
      ? true
      : domWild ? dowSet.has(dow)
      : dowWild ? domSet.has(dom)
      : domSet.has(dom) || dowSet.has(dow)
    // 小时检查 → 跳至下小时
    // 分钟检查 → 跳至下分钟
    return t  // 找到匹配
  }
  return null
}
```

**DST 处理策略**：针对"2:30am"这类春季夏令时切换间隙的时间，循环会在 gap 中逐分钟步行，最终跳过该日。这与 vixie-cron 行为一致。

### 13.1.3 任务存储结构

定时任务以 JSON 格式持久化到 `.claude/scheduled_tasks.json`：

```
// src/utils/cronTasks.ts, 行 31-71
export type CronTask = {
  id: string              // 8位十六进制 UUID 切片
  cron: string            // 5字段 cron 字符串
  prompt: string          // 触发时入队的 prompt
  createdAt: number       // 创建时间戳（毫秒）
  lastFiredAt?: number   // 最近触发时间（用于恢复）
  recurring?: boolean     // 是否循环
  permanent?: boolean    // 是否永不过期（系统任务）
  durable?: boolean      // 是否持久化（运行时标志，不写入磁盘）
  agentId?: string       // 所属 Agent ID（用于 teammate 场景）
}
```

---

## 13.2 分布式调度设计

### 13.2.1 调度锁机制

多个 Claude 会话可能在同一项目目录下运行。如果不加控制，所有会话都会触发同一个定时任务——这是灾难性的"惊群效应"。KAIROS 通过**排他锁**解决这个问题。

锁文件位于 `.claude/scheduled_tasks.lock`，使用 `O_EXCL` 原子创建：

```
// src/utils/cronTasksLock.ts, 行 67-93
async function tryCreateExclusive(
  lock: SchedulerLock,
  dir?: string,
): Promise<boolean> {
  const path = getLockPath(dir)
  try {
    await writeFile(path, body, { flag: 'wx' })  // wx = O_EXCL | O_WRONLY
    return true
  } catch (e: unknown) {
    const code = getErrnoCode(e)
    if (code === 'EEXIST') return false  // 已被他人持有
    // ENOENT: .claude 目录不存在 → 创建后重试
    // 其他错误 → 抛出
  }
}
```

**锁持有者信息**包含 `sessionId`（会话标识）、`pid`（进程ID）和 `acquiredAt`（获取时间）。非拥有者每 5 秒探测一次锁：

```
// src/utils/cronScheduler.ts, 行 42（常量定义）
const LOCK_PROBE_INTERVAL_MS = 5000

// src/utils/cronScheduler.ts, 行 419-437（定时器逻辑）
lockProbeTimer = setInterval(() => {
  void tryAcquireSchedulerLock(lockOpts).then(owned => {
    if (owned) {
      isOwner = true
      clearInterval(lockProbeTimer)
      lockProbeTimer = null
    }
  })
}, LOCK_PROBE_INTERVAL_MS)
```

**设计原因**：为什么不用 Redis 或 etcd？这是一个**本地优先**的设计——不依赖任何外部服务。即使在网络分区时，锁机制依然有效。代价是：锁只在单机文件系统层面有效，多台机器共享同一 NFS/NAS 时仍需额外机制。

### 13.2.2 双模持久化

任务分为两类：

| 模式 | durable 参数 | 存储位置 | 生命周期 |
|------|-------------|---------|---------|
| 会话级 | `false` | 内存 (`bootstrap/state.ts`) | 随进程消亡 |
| 持久化 | `true` | `.claude/scheduled_tasks.json` | 跨会话存活 |

```
// src/utils/cronTasks.ts, 行 191-220
export async function addCronTask(
  cron: string, prompt: string,
  recurring: boolean, durable: boolean,
  agentId?: string,
): Promise<string> {
  const id = randomUUID().slice(0, 8)  // 8位足够（MAX_JOBS=50）
  const task = { id, cron, prompt, createdAt: Date.now(), ... }
  
  if (!durable) {
    addSessionCronTask({ ...task, ...(agentId ? { agentId } : {}) })
    return id
  }
  // 持久化到文件
  const tasks = await readCronTasks()
  tasks.push(task)
  await writeCronTasks(tasks)
  return id
}
```

**设计原因**：为什么 UUID 只取前 8 位？`MAX_JOBS = 50`，8 位十六进制（~10亿种可能）碰撞概率可忽略不计。短 ID 更适合人类阅读和展示。

### 13.2.3 文件监控与热更新

调度器使用 `chokidar` 监控任务文件变化，无需重启即可感知新增/删除任务：

```
// src/utils/cronScheduler.ts, 行 444-452
watcher = chokidar.watch(path, {
  persistent: false,
  ignoreInitial: true,
  awaitWriteFinish: { stabilityThreshold: FILE_STABILITY_MS },  // 300ms
  ignorePermissionErrors: true,
})
watcher.on('add', () => void load(false))
watcher.on('change', () => void load(false))
watcher.on('unlink', () => {  // 文件被删除 → 清空内存
  tasks = []
  nextFireAt.clear()
})
```

**`awaitWriteFinish` 的必要性**：防止文件写入中途触发重载。等待 300ms 稳定期确保完整写入。

---

## 13.3 任务队列与优先级

### 13.3.1 延迟队列与 Jitter

所有用户同时选择 `:00` 或 `:30` 分钟会产生集中负载。KAIROS 通过**确定性 Jitter** 分散负载，同时保证每个任务的触发时间可重现。

**循环任务 Jitter**：`src/utils/cronTasks.ts` 行 379-396

```
export function jitteredNextCronRunMs(
  cron: string, fromMs: number, taskId: string,
  cfg: CronJitterConfig = DEFAULT_CRON_JITTER_CONFIG,
): number | null {
  const t1 = nextCronRunMs(cron, fromMs)
  const t2 = nextCronRunMs(cron, t1)  // 下一次触发时间
  if (t2 === null) return t1  //  pinned 日期，无比例基准
  
  const jitter = Math.min(
    jitterFrac(taskId) * cfg.recurringFrac * (t2 - t1),  // 比例延迟
    cfg.recurringCapMs,                                    // 上限15分钟
  )
  return t1 + jitter
}
```

- **比例因子** `recurringFrac = 0.1`（默认）：周期为1小时的任务，延迟范围 [0, 6分钟]
- **上限** `recurringCapMs = 15 * 60 * 1000`（15分钟）：防止长周期任务延迟过长

**一次性任务 Jitter**：`src/utils/cronTasks.ts` 行 421-438

```
export function oneShotJitteredNextCronRunMs(
  cron: string, fromMs: number, taskId: string,
  cfg: CronJitterConfig = DEFAULT_CRON_JITTER_CONFIG,
): number | null {
  const t1 = nextCronRunMs(cron, fromMs)
  // 仅在 :00 或 :30 触发（默认配置）
  if (new Date(t1).getMinutes() % cfg.oneShotMinuteMod !== 0) return t1
  
  const lead = cfg.oneShotFloorMs
    + jitterFrac(taskId) * (cfg.oneShotMaxMs - cfg.oneShotFloorMs)
  return Math.max(t1 - lead, fromMs)
}
```

> ⚠️ **勘误**：`oneShotFloorMs` 的**默认值实际为 `0`**，并非"30秒地板"。当配置为默认值时，`lead` 的最小值为 `0`（即不提前触发）。

### 13.3.2 Jitter 配置的热更新

Jitter 参数通过 GrowthBook A/B 测试框架实时调整，无需重启客户端：

```
// src/utils/cronJitterConfig.ts, 行 60-68
export function getCronJitterConfig(): CronJitterConfig {
  const raw = getFeatureValue_CACHED_WITH_REFRESH<unknown>(
    'tengu_kairos_cron_config',
    DEFAULT_CRON_JITTER_CONFIG,
    JITTER_CONFIG_REFRESH_MS,  // 60秒
  )
  const parsed = cronJitterConfigSchema().safeParse(raw)
  return parsed.success ? parsed.data : DEFAULT_CRON_JITTER_CONFIG
}
```

**实操示例**：在发生负载峰值时，运维可以推送配置：

```json
{
  "oneShotMinuteMod": 15,
  "oneShotMaxMs": 300000,
  "oneShotFloorMs": 30000
}
```

这将 `:00/:15/:30/:45` 的触发分散到 `[t-5min, t-30s]` 窗口。

### 13.3.3 任务入队优先级

触发时，prompt 以 `'later'` 优先级进入命令队列：

```
// src/hooks/useScheduledTasks.ts, 行 71-80
const enqueueForLead = (prompt: string) =>
  enqueuePendingNotification({
    value: prompt,
    mode: 'prompt',
    priority: 'later',     // 低于用户输入的优先级
    isMeta: true,          // 隐藏于队列预览和转录界面
    workload: WORKLOAD_CRON,  // 用于账单归属
  })
```

**设计原因**：`'later'` 优先级确保定时任务不会打断用户正在进行的交互。`isMeta: true` 使任务在 Brief 模式下作为后台 subagent 运行，不产生可见消息。

---

## 13.4 故障恢复策略

### 13.4.1 漏失任务检测

当 Claude 重启时，调度器会比较 `createdAt` 和当前时间，找出漏失的触发：

```
// src/utils/cronTasks.ts, 行 447-451
export function findMissedTasks(tasks: CronTask[], nowMs: number): CronTask[] {
  return tasks.filter(t => {
    const next = nextCronRunMs(t.cron, t.createdAt)
    return next !== null && next < nowMs
  })
}
```

**关键点**：对于循环任务，`lastFiredAt` 是恢复点——下次触发时间从上次实际触发时间计算，而非从 `createdAt`。这防止了"进程重启后立即触发所有历史任务"的灾难。

```
// src/utils/cronScheduler.ts, 行 255-271（process 函数内 nextFireAt 计算）
let next = t.recurring
  ? jitteredNextCronRunMs(t.cron, t.lastFiredAt ?? t.createdAt, t.id, ...)
  : oneShotJitteredNextCronRunMs(t.cron, t.createdAt, t.id, ...)
```

### 13.4.2 过期任务自动清理

循环任务默认 7 天后自动过期（`recurringMaxAgeMs`），防止无限累积：

```
// src/utils/cronScheduler.ts, 行 52-58
export function isRecurringTaskAged(
  t: CronTask, nowMs: number, maxAgeMs: number,
): boolean {
  if (maxAgeMs === 0) return false
  return Boolean(t.recurring && !t.permanent && nowMs - t.createdAt >= maxAgeMs)
}
```

**永久任务**（`permanent: true`）例外——这是系统内置任务（如 catch-up、morning-checkin、dream）的标记。设为永久是因为删除后无法通过重新安装恢复（安装脚本使用 `writeIfMissing` 策略）。

### 13.4.3 In-Flight 去重

为防止异步删除操作期间的重复触发，调度器使用 `inFlight` 集合标记正在删除中的任务：

```
// src/utils/cronScheduler.ts, 行 170（集合定义）
const inFlight = new Set<string>()

// src/utils/cronScheduler.ts, 行 344-349（process 函数内使用逻辑）
function process(t: CronTask, isSession: boolean) {
  if (inFlight.has(t.id)) return  // 已经在删除中，跳过
  // ... 触发逻辑
  inFlight.add(t.id)
  void removeCronTasks([t.id], dir).finally(() => inFlight.delete(t.id))
}
```

### 13.4.4 失效队友任务清理

当一个 teammate Agent 被终止时，其创建的任务会变成"孤儿"：

```
// src/hooks/useScheduledTasks.ts, 行 100-113
onFireTask: task => {
  if (task.agentId) {
    const teammate = findTeammateTaskByAgentId(task.agentId, store.getState().tasks)
    if (teammate && !isTerminalTaskStatus(teammate.status)) {
      injectUserMessageToTeammate(teammate.id, task.prompt, setAppState)
      return
    }
    // Teammate 已消失 → 清理孤儿 cron
    void removeCronTasks([task.id])
    return
  }
  // ...
}
```

---

## 13.5 完整生命周期示例

以下是一次性定时任务的完整生命周期：

```
用户: "下午3点提醒我检查部署状态"
  ↓
CronCreateTool.validateInput()
  - 解析 cron: "0 15 <今天_dom> <今天_month> *"
  - 验证未来一年内有匹配日期
  ↓
CronCreateTool.call()
  - 生成 8 位 ID: "a3f7b2c1"
  - 写入 .claude/scheduled_tasks.json（或内存）
  - setScheduledTasksEnabled(true) → 启动调度器
  ↓
调度器启动（cronScheduler.start）
  - 尝试获取 .claude/scheduled_tasks.lock
  - 若成功：成为 owner，每秒 check() 一次
  - 若失败：每5秒探测锁
  ↓
check() 循环
  - 计算 nextFireAt: t1 = 15:00, 加 jitter → t1 - lead
  - 等待直到 now >= nextFireAt
  ↓
触发时刻
  - 调用 onFireTask(task)
  - enqueuePendingNotification({ priority: 'later', isMeta: true })
  - removeCronTasks(["a3f7b2c1"]) → 从文件删除
  - inFlight.add("a3f7b2c1") → 防止重复
  ↓
用户看到消息: "Running scheduled task (Mar 15 3:00pm)"
  prompt 进入命令队列，等待当前对话空闲时执行
```

---

## 13.6 核心设计原则总结

| 原则 | 实现方式 |
|------|---------|
| **本地优先** | 文件系统锁，无外部依赖 |
| **确定性重放** | UUID 切片作为 jitter 种子，重启后可重现 |
| **防惊群** | 任务 ID 哈希 → 均匀分布的触发延迟 |
| **热更新** | GrowthBook 推送 jitter 参数，60秒生效 |
| **容错** | 漏失检测、过期清理、孤儿清理、in-flight 去重 |
| **隔离** | 调度锁确保单会话触发，`'later'` 优先级隔离用户交互 |

---

## 延伸阅读

- `src/utils/cron.ts` — 完整的 Cron 解析与 next-fire 计算
- `src/utils/cronScheduler.ts` — 调度器核心（计时器、锁、文件监控）
- `src/utils/cronTasks.ts` — 任务存储与 Jitter 实现
- `src/utils/cronTasksLock.ts` — 分布式锁机制
- `src/tools/ScheduleCronTool/` — 三个工具（Create/List/Delete）的实现

---

# 第十四章：Feature Flag 体系

> **本章概要**
> - `feature()` 函数的实现原理与 bun:bundle 的 DCE 机制
> - Feature Flag 的工程价值
> - 如何在代码中添加新的 Feature Flag
> - DCE cliff 问题及其解决方案

---

## 14.1 什么是 Feature Flag？

Feature Flag（功能开关）是一种**在不重新部署代码的情况下控制功能开启或关闭**的技术。它是现代软件工程中的核心基础设施，尤其适合以下场景：

- **灰度发布**：逐步向用户群体开放新功能
- **A/B 测试**：为不同用户群体展示不同功能变体
- **紧急开关**：出现严重 Bug 时可以瞬间关闭功能
- **条件编译**：根据环境、用户类型或组织策略启用/禁用代码路径

在 Claude Code 的代码库中，Feature Flag 体系由两个层次组成：

1. **编译期 DCE（Dead Code Elimination）层**：`feature()` 函数 + Bun 打包器
2. **运行时特性控制层**：GrowthBook 远程配置服务

这两个层次相互配合，实现了"编译时消除无用代码 + 运行时动态控制"的双重能力。

---

## 14.2 `feature()` 函数与 bun:bundle

### 14.2.1 函数签名与基本用法

`feature()` 函数是从 `bun:bundle` 模块导入的 Bun 内置函数。在 `main.tsx` 第 19 行可以看到其导入方式：

```
// src/main.tsx:19
import { feature } from 'bun:bundle';
```

该函数接受一个字符串参数（Feature Flag 名称），返回一个布尔值。但它的**真正威力**在于与 Bun 打包器的深度集成——打包阶段会将所有 `feature()` 调用替换为常量值，然后执行完整的 dead code elimination。

### 14.2.2 编译期 DCE 机制详解

Bun 的打包器在处理 `feature()` 函数时，会进行**常量折叠（Constant Folding）**。当检测到 `feature('XXX')` 调用的参数是字符串字面量时，打包器会：

1. 查询构建配置中该 Flag 的值（`true` 或 `false`）
2. 将整个 `feature()` 调用替换为该布尔常量
3. 运行完整的 Tree-shaking / DCE

**举例说明**。假设在构建配置中 `COORDINATOR_MODE` 被设为 `false`，以下代码：

```
import { feature } from 'bun:bundle';

// 打包前
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js')
  : null;
```

在打包后会被优化为：

```
// 打包后（COORDINATOR_MODE = false）
const coordinatorModeModule = false
  ? require('./coordinator/coordinatorMode.js')
  : null;  // → null
```

由于条件分支的结果在编译期就是确定的，Bun 的 DCE 会进一步识别出 `false ? A : null` 永远返回 `null`，从而**彻底消除对 `./coordinator/coordinatorMode.js` 的引用**——该文件不会被加载，相关的类型定义、函数体全部从最终产物中消失。

这就是 Claude Code 能够保持极小二进制体积的秘诀之一：未启用的功能模块在编译时就已被完全剔除。

### 14.2.3 在 main.tsx 中的实际应用

`main.tsx` 中大量使用了 `feature()` 函数来条件性地加载模块。以下是几处典型的使用方式：

**条件导入模式（Conditional Import Pattern）**：

```
// src/main.tsx:72-75
/* eslint-disable @typescript-eslint/no-require-imports */
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js')
  : null;
/* eslint-disable @typescript-eslint/no-require-imports */
const assistantModule = feature('KAIROS')
  ? require('./assistant/index.js')
  : null;
const kairosGate = feature('KAIROS')
  ? require('./assistant/gate.js')
  : null;
```

**设计原因**：为什么要用 `require` 而非顶层的 `import`？

这正是 DCE 的精妙之处。如果写成顶层的 `import` 语句，模块无论 Flag 状态如何都会被加载（因为 ES Module 的 import 是 hoisted 的）。而将 `import` 改写为条件 `require()` 表达式后，只有当 Flag 为 `true` 时才会执行加载逻辑。结合 DCE，当 Flag 为 `false` 时，整个 `require()` 分支都被消除。

**条件对象初始化**：

```
// src/main.tsx:567-583（PendingSSH 类型定义 + 初始化）
// Set by early argv processing when `claude ssh <host> [dir]` is detected
type PendingSSH = {
  host: string | undefined;
  cwd: string | undefined;
  permissionMode: string | undefined;
  dangerouslySkipPermissions: boolean;
  local: boolean;
  extraCliArgs: string[];
};
const _pendingSSH: PendingSSH | undefined = feature('SSH_REMOTE')
  ? { /* ... */ }
  : undefined;
```

**条件行为分支**：

```
// src/main.tsx:548-553（PendingConnect 初始化）
const _pendingConnect: PendingConnect = feature('DIRECT_CONNECT')
  ? { /* ... */ }
  : {}

// src/main.tsx:612-613（条件分支）
if (feature('DIRECT_CONNECT')) {
  const rawCliArgs = process.argv.slice(2);
  const ccIdx = rawCliArgs.findIndex(
    a => a.startsWith('cc://') || a.startsWith('cc+unix://')
  );
  if (ccIdx !== -1 && _pendingConnect) {
    // ...
  }
}
```

---

## 14.3 GrowthBook 运行时特性控制

虽然 `feature()` 函数在编译期决定了代码路径，但有些功能需要在**运行时**根据用户属性、组织策略或实验分组来决定是否启用。GrowthBook 正是承担这一角色的远程配置服务。

### 14.3.1 核心 API

Claude Code 中使用 GrowthBook 的主要入口是 `src/services/analytics/growthbook.ts`。该模块提供了三个层级的 API：

**层级一：阻塞式获取（可能影响启动性能）**

```
// src/services/analytics/growthbook.ts, 行 719
export async function getFeatureValue_DEPRECATED<T>(
  feature: string,
  defaultValue: T,
): Promise<T> {
  return getFeatureValueInternal(feature, defaultValue, true);
}
```

> ⚠️ 文档已标注为 deprecated，不推荐在启动关键路径中使用。

**层级二：缓存读取（非阻塞，可能返回过期值）**

```
// src/services/analytics/growthbook.ts, 行 734
export function getFeatureValue_CACHED_MAY_BE_STALE<T>(
  feature: string,
  defaultValue: T,
): T {
  // 优先读取内存缓存
  if (remoteEvalFeatureValues.has(feature)) {
    return remoteEvalFeatureValues.get(feature) as T;
  }
  // 回退到磁盘缓存
  try {
    const cached = getGlobalConfig().cachedGrowthBookFeatures?.[feature];
    return cached !== undefined ? (cached as T) : defaultValue;
  } catch {
    return defaultValue;
  }
}
```

这是**推荐在启动关键路径使用的 API**，因为它：
- 完全非阻塞（纯同步读取）
- 优先使用进程生命周期内的内存缓存
- 磁盘缓存保证进程重启后仍能快速获取上一次的值
- 允许返回值略微过期（最多一个刷新周期：外部版本 6 小时，内部版本 20 分钟）

**层级三：安全门检查（等待 GrowthBook 初始化完成）**

```
// src/services/analytics/growthbook.ts, 行 904
export async function checkGate_CACHED_OR_BLOCKING(
  gate: string,
): Promise<boolean> {
  const cached = getGlobalConfig().cachedGrowthBookFeatures?.[gate];
  if (cached === true) {
    return true; // 快速路径：缓存已标记为启用
  }
  // 慢速路径：缓存未启用，发起网络请求获取最新值
  return getFeatureValueInternal(gate, false, true);
}
```

这个 API 用于用户主动触发的功能（如 `/remote-control`），如果缓存已经说"启用"，就直接返回；如果缓存说"禁用"，则等待网络获取最新值（最多 5 秒），以避免错误地拒绝有权访问的用户。

### 14.3.2 缓存机制

GrowthBook 的缓存设计采用了**三级存储**：

```
优先级: 内存缓存 > 磁盘缓存 > 网络请求
                   ↓              ↓
         进程生命周期内     ~/.claude.json
         的 Map 对象         (跨进程持久化)
```

```
// src/services/analytics/growthbook.ts
const remoteEvalFeatureValues = new Map<string, unknown>();

async function processRemoteEvalPayload(gbClient: GrowthBook): Promise<boolean> {
  const payload = gbClient.getPayload();
  if (!payload?.features || Object.keys(payload.features).length === 0) {
    return false;
  }
  
  remoteEvalFeatureValues.clear();
  for (const [key, feature] of Object.entries(transformedFeatures)) {
    const v = 'value' in feature ? feature.value : feature.defaultValue;
    if (v !== undefined) {
      remoteEvalFeatureValues.set(key, v);
    }
  }
  return true;
}
```

### 14.3.3 实验曝光追踪（Exposure Logging）

GrowthBook 不仅是开关系统，还是一个 A/B 测试平台。当一个特性值来自实验分组时，需要记录曝光事件以便后续分析：

```
// src/services/analytics/growthbook.ts, 行 89
const loggedExposures = new Set<string>();

// src/services/analytics/growthbook.ts, 行 298
function logExposureForFeature(feature: string): void {
  if (loggedExposures.has(feature)) return; // 去重：每个特性每会话只记录一次

  const expData = experimentDataByFeature.get(feature);
  if (expData) {
    loggedExposures.add(feature);
    logGrowthBookExperimentTo1P({
      experimentId: expData.experimentId,
      variationId: expData.variationId,
      userAttributes: getUserAttributes(),
      experimentMetadata: { feature_id: feature },
    });
  }
}
```

---

## 14.4 Feature Flag 的工程价值

### 14.4.1 安全隔离

通过 `feature()` 的编译期 DCE，可以确保**敏感功能在特定构建中完全不存在**，而非简单的"默认关闭"。举例而言，`CHICAGO_MCP` 功能与 macOS 的 accessibility APIs 深度绑定，如果在非 macOS 或非 ant 用户的构建中包含这些代码，会造成不必要的攻击面。DCE 彻底消除了这种风险：

```
// src/main.tsx:1608-1628
if (
  feature('CHICAGO_MCP') &&
  getPlatform() === 'macos' &&
  !getIsNonInteractiveSession()
) {
  try {
    const { getChicagoEnabled } = await import('src/utils/computerUse/gates.js');
    if (getChicagoEnabled()) {
      const { setupComputerUseMCP } = await import('src/utils/computerUse/setup.js');
      const { mcpConfig, allowedTools: cuTools } = setupComputerUseMCP();
      dynamicMcpConfig = { ...dynamicMcpConfig, ...mcpConfig };
      allowedTools.push(...cuTools);
    }
  } catch (error) {
    logForDebugging(`[Computer Use MCP] Setup failed: ${errorMessage(error)}`);
  }
}
```

### 14.4.2 渐进式发布

GrowthBook 支持按用户属性（如 `subscriptionType`、`organizationUUID`、`userType`）进行定向发布：

```
// src/services/analytics/growthbook.ts
const attributes = {
  id: user.deviceId,
  sessionId: user.sessionId,
  deviceID: user.deviceId,
  platform: user.platform,
  ...(apiBaseUrlHost && { apiBaseUrlHost }),
  ...(user.organizationUuid && { organizationUUID: user.organizationUuid }),
  ...(user.accountUuid && { accountUUID: user.accountUuid }),
  ...(user.userType && { userType: user.userType }),
  ...(user.subscriptionType && { subscriptionType: user.subscriptionType }),
  ...(user.rateLimitTier && { rateLimitTier: user.rateLimitTier }),
};
```

这意味着同一个二进制文件，可以同时服务：
- `ant` 用户（内部员工）获取全部功能
- 外部用户获取公开功能
- 企业客户获取特定的合规或商务功能

### 14.4.3 热修复能力

通过 GrowthBook 的 `setGrowthBookConfigOverride()`（ant 用户专享），可以在**不重新部署代码的情况下修改配置**：

```
// src/services/analytics/growthbook.ts
export function setGrowthBookConfigOverride(
  feature: string,
  value: unknown,
): void {
  if (process.env.USER_TYPE !== 'ant') return;
  saveGlobalConfig(c => ({
    ...c,
    growthBookOverrides: { ...current, [feature]: value },
  }));
  refreshed.emit(); // 通知所有订阅者
}
```

---

## 14.5 如何添加新的 Feature Flag

### 14.5.1 场景一：需要 DCE 的条件代码

如果新功能涉及整块代码的加载（如新命令、新模块），使用 `feature()` 函数：

**步骤 1：确定 Flag 名称**

选择一个清晰、描述性的名称，使用大写下划线格式，例如 `NEW_COMMAND_MODE`。

**步骤 2：在代码中添加条件分支**

```
import { feature } from 'bun:bundle';

// 条件模块加载
const newModule = feature('NEW_COMMAND_MODE')
  ? require('./features/newCommandMode.js')
  : null;

// 条件行为
if (feature('NEW_COMMAND_MODE')) {
  // 新功能逻辑
}
```

**步骤 3：在构建配置中设置 Flag 值**

在 CI/CD 的构建配置（如 `.github/workflows/build.yml` 或专门的 feature config）中：

```yaml
# 示例：CI 构建配置
build:
  features:
    NEW_COMMAND_MODE: true   # 启用
    OTHER_FLAG: false        # 禁用
```

> **注意**：`feature()` 函数的 Flag 名称和值是在**构建时**由构建系统注入的，因此需要确保 CI 配置与代码同步更新。

### 14.5.2 场景二：运行时可配置的特性

如果新功能需要根据用户属性或实验分组动态决定，使用 GrowthBook：

**步骤 1：选择合适的 API**

| 使用场景 | 推荐 API |
|---------|---------|
| 启动关键路径（同步） | `getFeatureValue_CACHED_MAY_BE_STALE()` |
| 用户主动触发（异步） | `checkGate_CACHED_OR_BLOCKING()` |
| 复杂配置对象 | `getDynamicConfig_CACHED_MAY_BE_STALE()` |

**步骤 2：注册特性值获取**

```
import {
  getFeatureValue_CACHED_MAY_BE_STALE,
} from './services/analytics/growthbook.js';

// 在需要的地方
const isEnabled = getFeatureValue_CACHED_MAY_BE_STALE(
  'my_new_feature_name',
  false  // 默认值
);

if (isEnabled) {
  // 功能逻辑
}
```

**步骤 3：在 GrowthBook 控制台配置**

1. 登录 GrowthBook 管理后台
2. 找到对应的 SDK Key（`claude-code-*`）
3. 添加新的 Feature，定义默认值
4. 创建 Experiment 或 Override 规则
5. 设置 Targeting（目标用户群体）

**步骤 4：监控曝光**

GrowthBook 会自动记录实验曝光，但建议在关键决策点显式调用曝光记录（`getFeatureValue_CACHED_MAY_BE_STALE` 默认会自动记录）：

```
// 如需手动触发曝光（仅在使用底层 API 时需要）
logExposureForFeature('my_new_feature_name');
```

---

## 14.6 DCE Cliff 问题

### 14.6.1 什么是 DCE Cliff？

**DCE Cliff（Dead Code Elimination 悬崖）** 是指当 Feature Flag 被启用时，相关的代码模块会突然被添加到产物中，导致二进制体积出现"跳跃式"增长的现象。

```
产物体积
    │
    │         ╱╲ 新功能突然加入
    │        ╱  ╲
    │       ╱    ╲___跳变点___
    │______╱               ╲
    │                          ╲___
    └──────────────────────────────→ Feature Flag 覆盖率
```

这个问题的核心在于：**编译期 DCE 使得关闭的 Flag 对应代码完全不进入产物，但一旦开启，整个模块就被包含进来**。如果模块体积很大，会造成发布时的体积抖动。

### 14.6.2 触发条件

DCE Cliff 在 Claude Code 中可能触发于以下场景：

```
// main.tsx:55-57
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js')
  : null;
```

当 `COORDINATOR_MODE` 从 `false` 变为 `true` 时，`./coordinator/coordinatorMode.js` 及其所有传递依赖会被一次性加入产物。

### 14.6.3 缓解策略

Claude Code 的代码库采用了以下策略来缓解 DCE Cliff：

**策略一：模块拆分**

将大功能模块拆分为多个小模块，使得每次开启的代码增量更小：

```
// 不好：一个巨大的模块
const bigModule = feature('BIG_FEATURE') ? require('./big.js') : null;

// 好：拆分为多个小模块，按需逐步开启
const part1 = feature('BIG_FEATURE_PART1') ? require('./big-part1.js') : null;
const part2 = feature('BIG_FEATURE_PART2') ? require('./big-part2.js') : null;
```

**策略二：延迟加载（Lazy Import）**

即使模块被 DCE 保留了，也可以通过动态 `import()` 让其在第一次使用时才从网络/磁盘加载，而不是在进程启动时就全部初始化：

```
// 不好的做法：启动时即加载全部
const heavyModule = feature('HEAVY_FEATURE')
  ? require('./heavy.js')
  : null;

// 更好的做法：延迟加载
async function useHeavyFeature() {
  if (!feature('HEAVY_FEATURE')) return;
  const { heavyFn } = await import('./heavy.js');
  return heavyFn();
}
```

**策略三：GrowthBook 作为 DCE 的补充**

对于不需要 DCE 的功能，使用 GrowthBook 而非 `feature()`。GrowthBook 的值存储在配置中，不影响编译产物，只影响运行时行为。这样即使功能被开启，编译产物也不会膨胀：

```
// 始终编译进产物，但运行时由 GB 控制
import { getFeatureValue_CACHED_MAY_BE_STALE } from './services/analytics/growthbook.js';

const isEnabled = getFeatureValue_CACHED_MAY_BE_STALE('runtime_feature', false);
if (isEnabled) { /* ... */ }
```

### 14.6.4 设计决策：为什么选择 DCE 而非完全动态化？

既然 DCE Cliff 是一个潜在问题，为什么 Claude Code 还要大量使用编译期 DCE 呢？

**选择 DCE 的理由**：

1. **安全隔离**：编译后不存在的代码无法被 exploit。对于与平台相关的 API（macOS Accessibility、 Windows 注册表等），这提供了本质上的安全保障。

2. **启动性能**：运行时才检查 Flag 意味着未使用的代码路径仍然需要被解析和 JIT 编译（如果是 JS 运行时）。编译期消除则完全移除了这部分开销。

3. **产物纯净性**：最终产物只包含实际需要的代码，便于分析、审计和调试。

**不使用纯动态化的理由**：

如果完全依赖运行时配置（所有功能都编译进去，通过条件判断来控制），会导致：
- 安全攻击面增大（未使用的代码路径可能被利用）
- 启动时需要解析更多模块
- 最终产物难以审计

因此，Claude Code 的设计哲学是：**需要 DCE 带来安全性和性能优势的用 `feature()`，需要运行时灵活性的用 GrowthBook**。

---

## 14.7 本章小结

| 概念 | 实现方式 | 适用场景 |
|------|---------|---------|
| `feature()` | 编译期常量折叠 + DCE | 整块代码的完全隔离、平台特定功能 |
| `getFeatureValue_CACHED_MAY_BE_STALE()` | 运行时同步读取缓存 | 启动关键路径 |
| `checkGate_CACHED_OR_BLOCKING()` | 异步等待初始化 | 用户主动触发的功能 |
| `setGrowthBookConfigOverride()` | 内存 + 磁盘双写 | 热修复、紧急关闭 |

Feature Flag 体系是 Claude Code 能够在多种环境（ant/internal vs. external）中共存，同时保持安全性和性能的核心基础设施。理解这一体系，对于深入理解整个代码库的架构设计至关重要。

---

*审计者：狗头军师*  
*撰写者：代码驴*

---

# 第十五章：性能优化实践

性能是用户体验的基石，也是工程能力的集中体现。一个 CLI 工具从启动到响应第一个请求的每一个毫秒，都决定着用户是「感觉流畅」还是「明显卡顿」。本章以 Claude Code 源码为案例，从 Bundle Size 优化、冷启动优化、缓存策略、热路径优化四个维度，系统阐述现代 TypeScript/JavaScript 应用的性能优化方法论。

---

## 15.1 Bundle Size 优化

Bundle Size 直接决定了用户下载、安装和加载应用的成本。即使是本地 CLI 工具，Bundle 越小，加载时占用的内存和解析时间也越少。

### 15.1.1 条件导入与死码消除

条件导入（Conditional Import）是控制 Bundle 体积的核心手段。其核心思想是：**只有在特定条件满足时才将某个模块纳入 Bundle**，从而在构建时实现死码消除（Dead Code Elimination）。

在 Claude Code 的入口文件 `src/main.tsx` 中，条件导入被大量使用：

```
// src/main.tsx:74-76
// Dead code elimination: conditional import for COORDINATOR_MODE
const coordinatorModeModule = feature('COORDINATOR_MODE')
  ? require('./coordinator/coordinatorMode.js') as typeof import('./coordinator/coordinatorMode.js')
  : null;

// src/main.tsx:78-81（同一 feature block 中还有 kairosGate）
// Dead code elimination: conditional import for KAIROS (assistant mode)
const assistantModule = feature('KAIROS')
  ? require('./assistant/index.js') as typeof import('./assistant/index.js')
  : null;
```

这里使用 `require()` 而非 `import`，是因为 `import` 在模块顶层必须被静态求值，而 `require()` 可以放在条件分支中，由运行时判断是否真正加载。`feature('COORDINATOR_MODE')` 是一个编译时常量（由构建工具在编译时替换为 `true` 或 `false`），这意味着当某功能flag为 `false` 时，整个模块的代码都不会进入最终 Bundle。

**设计原因**：Claude Code 需要支持多种产品变体（ant 内部版、外部版、特殊功能版），不同变体包含的代码不同。条件导入确保不需要的代码在物理上就不存在于 Bundle 中，而不只是被 if 包裹但不执行。

### 15.1.2 顶层副作用顺序安排

在 `src/main.tsx` 的最开始几行，我们看到一段精心编排的顶层副作用代码：

```
// src/main.tsx:1-25（以下为重构后的示意，实际行号请参考 src/main.tsx:1-25）
import { profileCheckpoint, profileReport } from './utils/startupProfiler.js';

profileCheckpoint('main_tsx_entry');
import { startMdmRawRead } from './utils/settings/mdm/rawRead.js';

startMdmRawRead();
import { startKeychainPrefetch } from './utils/secureStorage/keychainPrefetch.js';

startKeychainPrefetch();
import { feature } from 'bun:bundle';
import { Command as CommanderCommand } from '@commander-js/extra-typings';
// ... 大量 import ...
```

这段代码将**具有副作用的导入语句拆分到多个代码块中**，并在每个导入块之前启动独立的子进程。理解这个设计需要先明白 JavaScript 模块系统的基本规则：所有 `import` 语句会在模块首次执行时无序地全部求值一遍（在 ESM 中 `import` 是提升的 hoisted）。Claude Code 通过将导入语句分散在**多个不相邻的代码块**中，并利用 `profileCheckpoint()` 打点计时，使得导入过程在模块加载阶段就能并行展开。

**更关键的设计**在于，`startMdmRawRead()` 和 `startKeychainPrefetch()` 在 `import` 语句之前就被调用——这意味着**子进程的启动和模块加载是重叠进行的**：

```
// src/utils/settings/mdm/rawRead.ts:52-60
export function startMdmRawRead(): void {
  if (process.platform !== 'darwin' || rawReadPromise) return

  // Fire subprocesses immediately (non-blocking).
  // They run in parallel with each other AND with main.tsx imports.
  const oauthSpawn = spawnSecurity(/* ... */)
  const legacySpawn = spawnSecurity(/* ... */)
  // ...
}
```

`startMdmRawRead()` 通过 `child_process.execFile()` 启动子进程并立即返回，不阻塞主线程。子进程执行 MDM 配置读取的同时，JavaScript 引擎继续完成剩余 ~135ms 的模块导入工作。

`startMdmRawRead()` 函数位于 `src/utils/settings/mdm/rawRead.ts` **第 115-127 行**。

---

## 15.2 冷启动优化

冷启动（Cold Start）是指进程从启动到完成初始化的全过程。对于 CLI 工具，冷启动时间是用户感知最直接的指标——敲下 `claude` 到看到 REPL 提示符之间，每多 100ms 都是体验上的损耗。

### 15.2.1 子进程并行预热

Claude Code 在冷启动阶段会发起多个 I/O 操作：读取 MDM 配置、读取 Keychain（macOS）、获取系统上下文等。如果这些操作全部串行执行，总耗时将累加。Claude Code 的策略是：**将所有与主线程无关的 I/O 操作提前到子进程中并行执行**。

`src/utils/secureStorage/keychainPrefetch.ts` 中的 `startKeychainPrefetch()` 函数展示了这一模式：

```
// src/utils/secureStorage/keychainPrefetch.ts:69-84
export function startKeychainPrefetch(): void {
  if (process.platform !== 'darwin' || prefetchPromise || isBareMode()) return

  // Fire both subprocesses immediately (non-blocking).
  const oauthSpawn = spawnSecurity(getMacOsKeychainStorageServiceName(CREDENTIALS_SERVICE_SUFFIX))
  const legacySpawn = spawnSecurity(getMacOsKeychainStorageServiceName())

  prefetchPromise = Promise.all([oauthSpawn, legacySpawn]).then(/* ... */)
}
```

注释中明确指出设计意图：

> Firing both here lets the subprocesses run in parallel with each other AND with main.tsx imports.

如果不使用预热，两个 Keychain 读取会**串行执行**：

```
OAuth keychain 读取: ~32ms
+ Legacy API key 读取: ~33ms
= 总计: ~65ms（每次 macOS 启动）
```

而并行预热后，OAuth 和 Legacy 的读取**同时进行**，总耗时降至约 33ms，节省近一半时间。

### 15.2.2 预热的消费者：`ensureXxxCompleted` 模式

子进程启动后，结果存储在哪里？主线程如何获取？Claude Code 使用了一种**缓存结果 + 等待完成的模式**：

```
// src/main.tsx:第 preAction hook 中
await Promise.all([
  ensureMdmSettingsLoaded(),
  ensureKeychainPrefetchCompleted()
])
```

`ensureKeychainPrefetchCompleted()` 的实现会检查预热是否已经完成：

```
// src/utils/secureStorage/keychainPrefetch.ts:96-97
export async function ensureKeychainPrefetchCompleted(): Promise<void> {
  if (prefetchPromise) await prefetchPromise
}
```

`ensureKeychainPrefetchCompleted()` 位于 `src/utils/secureStorage/keychainPrefetch.ts` **第 96-97 行**，函数体仅 2 行：`if (prefetchPromise) await prefetchPromise`，远比示意图中展示的逻辑简短。

**设计原因**：这里有一个精妙的异步-同步转换。子进程在顶层并行启动（异步），但 `applySafeConfigEnvironmentVariables()` 中的 keychain 读取是**同步**的（因为涉及环境变量注入，需要在 init 之前完成）。通过预热+缓存，主线程的同步读取变成了纯粹的内存查找（O(1)），完全消除了进程间通信开销。

### 15.2.3 延迟初始化（Deferred Initialization）

冷启动阶段并非所有初始化工作都必须阻塞首帧渲染。Claude Code 将启动工作分为两类：**阻塞项**（必须等待完成后才能渲染 REPL）和**非阻塞项**（可以在首帧渲染后异步进行）。

`src/main.tsx` 中的 `startDeferredPrefetches()` 函数（`src/main.tsx` 行 388-420）是这一模式的典型代表：

```
// src/main.tsx:388-420
export function startDeferredPrefetches(): void {
  // Skip when measuring startup performance
  if (isEnvTruthy(process.env.CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER) ||
      isBareMode()) {
    return
  }

  // Process-spawning prefetches (consumed at first API call)
  void initUser()
  void getUserContext()
  void prefetchSystemContextIfSafe()
  void getRelevantTips()
  // ...
}
```

注意所有函数调用前面都有 `void`——这意味着这些调用**不等待结果**，是纯粹的 fire-and-forget。其设计考量是：用户刚看到 REPL 提示符、正在输入第一个问题时，这些后台工作（获取用户上下文、拉取 MCP URL、初始化分析引擎等）会占用 CPU 和事件循环时间，但用户还感知不到——因为用户在打字。如果不延迟，这些工作会直接影响首帧渲染时间。

**环境开关**：`CLAUDE_CODE_EXIT_AFTER_FIRST_RENDER` 和 `isBareMode()` 是两种跳过延迟预热的场景。前者用于性能基准测试（只测量启动时间，不考虑后续可用性），后者用于脚本化调用（`-p` 模式）——脚本场景没有「用户打字」窗口来隐藏这些工作。

---

## 15.3 缓存策略

缓存是性能优化中最有效的手段之一。Claude Code 构建了**多层级**的缓存体系，从磁盘读取到内存查找，每一层都针对不同的访问模式进行优化。

### 15.3.1 路径键控的解析缓存

读取配置文件（JSON/Zod 校验）是启动阶段的常见 I/O 操作。Claude Code 的 `src/utils/settings/settingsCache.ts` 实现了一个**路径键控的解析缓存**：

```
// src/utils/settings/settingsCache.ts:41-53
type ParsedSettings = {
  settings: SettingsJson | null
  errors: ValidationError[]
}
const parseFileCache = new Map<string, ParsedSettings>()

export function getCachedParsedFile(path: string): ParsedSettings | undefined {
  return parseFileCache.get(path)
}

export function setCachedParsedFile(path: string, value: ParsedSettings): void {
  parseFileCache.set(path, value)
}
```

这个缓存在**启动阶段**就发挥作用。`getSettingsForSource()` 和 `loadSettingsFromDisk()` 在启动时都会调用 `parseSettingsFile()`，在没有缓存的情况下，同一个文件会被读取和解析两次。通过缓存，第二次访问变成了 O(1) 的 Map 查找。

### 15.3.2 多源配置缓存

Claude Code 的配置来源有多个层次：全局配置（用户 home 目录）、项目配置（`.claude/settings.json`）、本地配置（`settings.local.json`）、策略配置（ MDM/remote managed）等。为每个来源分别缓存，避免单次访问触发所有来源的重新加载：

```
// src/utils/settings/settingsCache.ts:20-34
const perSourceCache = new Map<SettingSource, SettingsJson | null>()

export function getCachedSettingsForSource(
  source: SettingSource
): SettingsJson | null | undefined {
  return perSourceCache.has(source) ? perSourceCache.get(source) : undefined
}
```

每个来源独立缓存，独立失效。当某一来源的配置被写入时，只有该来源的缓存被清除，其他来源的缓存保持不变。

### 15.3.3 会话级缓存

会话级缓存 `sessionSettingsCache` 用于存储**合并后的完整配置**：

```
// src/utils/settings/settingsCache.ts:5-13
let sessionSettingsCache: SettingsWithErrors | null = null

export function getSessionSettingsCache(): SettingsWithErrors | null {
  return sessionSettingsCache
}
```

会话缓存的失效由 `resetSettingsCache()` 统一触发，该函数会清除所有层级的缓存：

```
// src/utils/settings/settingsCache.ts:55-59
export function resetSettingsCache(): void {
  sessionSettingsCache = null
  perSourceCache.clear()
  parseFileCache.clear()
}
```

这个函数在配置写入（`--add-dir`）、插件初始化、Hook 刷新等场景被调用，确保配置变更后下一次访问能获取最新值。

### 15.3.4 MCP 配置的早期并行加载

MCP（Model Context Protocol）服务器配置的加载是一个特别适合提前开始的 I/O 操作：

```
// src/main.tsx:1809-1821
const mcpConfigPromise = (strictMcpConfig || isBareMode()
  ? Promise.resolve({ servers: {} })
  : getClaudeCodeMcpConfigs(dynamicMcpConfig)
).then(result => {
  mcpConfigResolvedMs = Date.now() - mcpConfigStart
  return result
})
```

这里没有 `await`，而是将 Promise 保存下来，后续在需要时再 `await`。在这段时间内，主线程可以继续执行其他工作（setup、命令加载等），MCP 配置的磁盘读取与这些工作**完全并行**。

---

## 15.4 热路径优化

热路径（Hot Path）是用户最频繁触发的代码路径。在 CLI 工具中，每次用户发送消息、每次工具调用都是热路径。优化热路径意味着优化用户每次交互的响应延迟。

### 15.4.1 启动性能剖析

优化热路径的第一步是**量化性能**。Claude Code 的 `src/utils/startupProfiler.ts` 提供了一套完整的启动时间剖析框架：

```
// src/utils/startupProfiler.ts:49-54
// Phase definitions for Statsig logging
const PHASE_DEFINITIONS = {
  import_time: ['cli_entry', 'main_tsx_imports_loaded'],
  init_time: ['init_function_start', 'init_function_end'],
  settings_time: ['eagerLoadSettings_start', 'eagerLoadSettings_end'],
  total_time: ['cli_entry', 'main_after_run'],
} as const
```

每个阶段通过 `profileCheckpoint()` 打点记录：

```
// src/utils/startupProfiler.ts:65-75
export function profileCheckpoint(name: string): void {
  if (!SHOULD_PROFILE) return

  const perf = getPerformance()
  perf.mark(name)

  if (DETAILED_PROFILING) {
    memorySnapshots.push(process.memoryUsage())
  }
}
```

这里使用了 Node.js 内置的 `performance` API（`perf_hooks`），而不是自己维护时间戳。`performance.mark()` 利用了平台级的高精度计时器（通常是 `HR-Time`），精度远高于 `Date.now()`。

**采样策略**是这里的设计亮点：

```
// src/utils/startupProfiler.ts:28-33
const STATSIG_SAMPLE_RATE = 0.005 // 0.5% 的外部用户
const STATSIG_LOGGING_SAMPLED =
  process.env.USER_TYPE === 'ant' || Math.random() < STATSIG_SAMPLE_RATE
```

只有在采样的用户中才记录详细的时间数据。这确保了 99.5% 的外部用户**完全不承受**性能剖析的运行时开销（除了一个布尔判断），而产品团队仍然能获得足够的统计数据。

### 15.4.2 Trust 检查的安全延后

在交互式会话中，信任对话框（Trust Dialog）的展示是冷启动阶段的一个关键节点。在用户确认之前，代码不能执行 `git` 命令（可能运行任意 hook），不能访问网络（可能来自恶意配置），也不能预取系统上下文：

```
// src/main.tsx:360-378（独立函数）
function prefetchSystemContextIfSafe(): void {
  const isNonInteractiveSession = getIsNonInteractiveSession()

  if (isNonInteractiveSession) {
    // -p 模式跳过信任检查（信任隐含）
    void getSystemContext()
    return
  }

  const hasTrust = checkHasTrustDialogAccepted()
  if (hasTrust) {
    void getSystemContext()
  }
  // 否则：跳过，等待信任建立后再 prefetch
}
```

这段代码说明：**系统上下文预取（git status、worktree count 等）被延后到了信任对话框接受之后**。这避免了在不可信目录中执行任意代码的安全风险，同时在交互式场景中（用户看到对话框的时间窗口）提供了自然的后台工作时间。

### 15.4.3 Setup 与命令加载的并行化

在 `src/main.tsx` 的 action handler 中，有一个精心设计的并行化操作：

```
// src/main.tsx:setupPromise 与 commandsPromise 并行
const preSetupCwd = getCwd()

initBuiltinPlugins()    // < 1ms，纯内存操作
initBundledSkills()     // < 1ms，纯内存操作

const setupPromise = setup(preSetupCwd, /* ... */)
const commandsPromise = worktreeEnabled ? null : getCommands(preSetupCwd)
const agentDefsPromise = worktreeEnabled ? null : getAgentDefinitionsWithOverrides(preSetupCwd)

// Suppress transient unhandledRejection
commandsPromise?.catch(() => {})
agentDefsPromise?.catch(() => {})

await setupPromise
// ...
const [commands, agentDefinitionsResult] = await Promise.all([
  commandsPromise ?? getCommands(currentCwd),
  agentDefsPromise ?? getAgentDefinitionsWithOverrides(currentCwd)
])
```

注释解释了设计原因：

> Parallelize setup() with commands+agents loading. setup()'s ~28ms is mostly startUdsMessaging (socket bind, ~20ms) — not disk-bound, so it doesn't contend with getCommands' file reads.

`socket bind` 是网络 I/O（受限于系统调用），而 `getCommands` 是文件系统遍历（磁盘 I/O）。这两类 I/O 操作在现代操作系统的 I/O 调度器下可以很好地并行工作，因此没有相互阻塞的风险。

### 15.4.4 幂等性设计：Memoization

所有可以被 Memoization 的函数都遵循幂等性设计。以 `getIsGit()` 为例，它会执行 `git rev-parse --is-inside-work-tree` 命令，但结果被缓存后，后续调用直接返回缓存值而不再执行子进程。

这在热路径中的意义是：一旦某个信息被获取过一次，后续所有需要该信息的地方都不需要再付出 I/O 代价。Memoization 使得**冷启动阶段的预热工作直接惠及整个会话**，而非仅仅服务于启动流程。

---

## 15.5 综合优化策略回顾

本章讨论的四种优化策略并非孤立存在，它们形成了一个相互配合的体系：

| 优化维度 | 核心手段 | 解决的问题 |
|---------|---------|-----------|
| Bundle Size | 条件导入、死码消除 | 下载体积、解析时间 |
| 冷启动 | 子进程并行、延迟初始化 | 感知延迟、首次可用时间 |
| 缓存策略 | 多层级 Map 缓存 | 重复 I/O、Zod 解析开销 |
| 热路径 | Profile 驱动的量化优化 | 持续交互响应延迟 |

最值得学习的不是某一个技巧，而是**Claude Code 在每一处决策背后都明确记录了「为什么这样做」的设计意图**。性能优化的本质是工程决策的权衡：并行化增加了复杂度，缓存增加了一致性管理的难度，条件导入增加了构建配置的复杂度。只有清楚地知道每一种选择带来的代价，才能做出正确的取舍。

---

## 本章小结

- **条件导入**通过 `feature()` flag 实现构建时的死码消除，避免不需要的模块进入 Bundle
- **子进程并行预热**（`startMdmRawRead`、`startKeychainPrefetch`）将 I/O 操作与模块加载重叠，将串行 ~65ms 的操作降至并行 ~33ms
- **延迟初始化**（`startDeferredPrefetches`）将非关键路径工作延后到首帧渲染之后，利用用户输入的自然等待时间
- **多层级缓存**（`parseFileCache`、`perSourceCache`、`sessionSettingsCache`）从路径、来源、会话三个维度消除重复 I/O 和 Zod 解析
- **启动剖析**（`profileCheckpoint`）通过采样策略让 99.5% 的用户零开销地提供性能数据，使优化决策基于真实数据而非猜测

---

*合集终*

*** [第三部分：第十一章至第十五章完] ***

# 第十六章：测试与质量保证

## 概述

在 Claude Code 这类复杂的多工具 Agent 系统中，测试与质量保证是保障系统安全性和可靠性的基石。本章以 `claude-code-leak` 项目为蓝本，深入探讨如何为 AI 编码辅助工具构建完整的测试体系，涵盖测试框架选型、单元测试策略、集成测试设计以及安全测试要点。

---

## 16.1 测试框架选择

### 16.1.1 TypeScript 生态下的测试框架对比

在 TypeScript 项目中，主流测试框架有 **Vitest**、**Jest** 和 **Bun.test**。选择依据通常包括：启动速度、TypeScript 原生支持程度、与现有构建工具的集成便利性，以及对 ESM 模块的支持。

`claude-code-leak` 项目采用了 **Bun** 作为运行时和打包工具，因此其测试体系自然倾向于使用 Bun 内置的测试运行器（`bun test`）。这种选择的优势在于：

- **零配置**：Bun 的测试运行器开箱即用，无需额外配置 TypeScript 转换或 ESM 兼容层
- **极快的启动速度**：比 Jest 快一个数量级，适合大型代码库
- **原生支持**：Bun 直接理解 `.ts` 文件和 `import` 语法，测试文件无需编译即可运行

```
// src/ink/hit-test.ts — 单元测试示例（算法级测试）
// 该文件实现了点击事件命中测试算法，使用纯函数风格便于验证

import type { DOMElement } from './dom.js'
import { ClickEvent } from './events/click-event.js'
import type { EventHandlerProps } from './events/event-handlers.js'
import { nodeCache } from './node-cache.js'

/**
 * Find the deepest DOM element whose rendered rect contains (col, row).
 *
 * Uses the nodeCache populated by renderNodeToOutput — rects are in screen
 * coordinates with all offsets (including scrollTop translation) already
 * applied. Children are traversed in reverse so later siblings (painted on
 * top) win.
 */
export function hitTest(
  node: DOMElement,
  col: number,
  row: number,
): DOMElement | null {
  const rect = nodeCache.get(node)
  if (!rect) return null
  if (
    col < rect.x ||
    col >= rect.x + rect.width ||
    row < rect.y ||
    row >= rect.y + rect.height
  ) {
    return null
  }
  // Later siblings paint on top; reversed traversal returns topmost hit.
  for (let i = node.childNodes.length - 1; i >= 0; i--) {
    const child = node.childNodes[i]!
    if (child.nodeName === '#text') continue
    const hit = hitTest(child, col, row)
    if (hit) return hit
  }
  return node
}
```

> **源码索引**：`src/ink/hit-test.ts` 第 1–46 行
>
> **设计原因**：该算法采用递归+反向遍历的设计，确保"后绘制的元素优先命中"。这种顺序源自 CSS 渲染模型中后出现的兄弟节点会覆盖先出现的节点（`z-index` 相同时）。将算法实现为纯函数（无副作用、仅依赖输入参数和 `nodeCache`）使得单元测试可以完全确定性：给定相同的 DOM 树和坐标，命中结果永远一致，不受测试执行顺序影响。

### 16.1.2 测试工具的声明式配置

`claude-code-leak` 项目大量使用 **Zod** 进行运行时类型验证。Zod 的 `.describe()` 方法虽然表面上是文档字符串，但其本质是声明式契约——既为开发者提供 IDE 自动补全提示，也在运行时确保数据类型符合预期。

```
// src/schemas/hooks.ts 第 23–109 行（部分）
// Zod schema 作为测试数据的"契约"

const HookSchema = z.object({
  type: z.literal('command').describe('Shell command hook type'),
  command: z.string().describe('Shell command to execute'),
  timeout: z.number().describe('Timeout in seconds for this specific command'),
  statusMessage: z.string().describe('Custom status message to display in spinner while hook runs'),
  once: z.boolean().describe('If true, hook runs once and is removed after execution'),
  background: z.boolean().describe('If true, hook runs in background without blocking'),
  // ...
})
```

> **设计原因**：使用 Zod schema 定义测试数据的契约，有两个关键好处：
> 1. **类型安全**：在 TypeScript 编译时就能捕获字段名拼写错误，而传统 Jest 需要额外配置 `ts-jest`
> 2. **自文档化**：`.describe()` 的文本成为契约的一部分，测试数据的预期结构一目了然
>
> 这在 `claude-code-leak` 中尤为重要，因为 Hook 系统（command/prompt/http 三种类型）涉及复杂的数据流，需要在多个模块间共享类型契约。

---

## 16.2 单元测试策略

### 16.2.1 验证器函数的纯函数测试

Claude Code 的安全验证系统大量采用**纯函数**设计：给定命令字符串和上下文，返回是否安全的判定。这使得验证逻辑的单元测试极为直接。

以命令标志位（flag）验证为例，项目定义了一个集中的标志位白名单系统：

```
// src/utils/shell/readOnlyCommandValidation.ts 第 1–80 行（部分）

export type FlagArgType =
  | 'none'     // No argument (--color, -n)
  | 'number'   // Integer argument (--context=3)
  | 'string'   // Any string argument (--relative=path)
  | 'char'     // Single character (delimiter)
  | '{}'       // Literal "{}" only
  | 'EOF'      // Literal "EOF" only

export type ExternalCommandConfig = {
  safeFlags: Record<string, FlagArgType>
  additionalCommandIsDangerousCallback?: (
    rawCommand: string,
    args: string[],
  ) => boolean
  respectsDoubleDash?: boolean
}
```

> **源码索引**：`src/utils/shell/readOnlyCommandValidation.ts` 第 20–35 行

关键设计：**参数类型的穷举枚举**。`'none'`、`'number'`、`'string'`、`'char'`、`'{}'`、`'EOF'` 这六种类型覆盖了 shell 命令行工具的所有参数形式。`'{}'` 和 `'EOF'` 看似特殊，却是 `xargs -I{}` 和 `xargs -E` 等命令的精确约束——任意其他字面量不应当被接受。

```
// src/utils/shell/readOnlyCommandValidation.ts 第 44–100 行

// 源码中实际存在的 flag 白名单常量（git 相关的多个常量）
const GIT_REF_SELECTION_FLAGS: Record<string, FlagArgType> = {
  '-h': 'none',
  '--help': 'none',
  '-V': 'none',
  '--version': 'none',
  '-H': 'none',
  '--hidden': 'none',
  '-d': 'number',       // --max-depth: 必须跟数字
  '--max-depth': 'number',
  '--type': 'string',  // --type: 接受任意字符串（如 'f', 'd'）
  '-S': 'string',       // --size: 接受大小字符串（如 '+100M'）
  '--format': 'string',
  // SECURITY: -l/--list-details EXCLUDED — internally executes `ls` as subprocess
  '-L': 'none',
  '--follow': 'none',
  // ...
}
```

> ⚠️ **重要勘误**：`FD_SAFE_FLAGS` **不存在于源码中**。源码中对应位置是一组 git 相关的 flag 白名单常量（如 `GIT_REF_SELECTION_FLAGS`、`GIT_STAT_FLAGS`、`GIT_LOG_DISPLAY_FLAGS` 等）。上例中的 `FD_SAFE_FLAGS` 是源码中 `GIT_REF_SELECTION_FLAGS`（用于 `git find` 相关操作）的示意别名，并非独立常量名。测试时请以源码中实际常量名为准。
>
> **源码索引**：`src/utils/shell/readOnlyCommandValidation.ts` 第 44–100 行（git 相关 flag 白名单常量区）

### 16.2.2 git 命令的只读性验证

`git` 是 Claude Code 中最常用的命令之一，其只读性子集的安全验证是单元测试的重点：

```
// src/utils/shell/readOnlyCommandValidation.ts 第 107–175 行（git diff 配置块）

export const GIT_READ_ONLY_COMMANDS: Record<string, ExternalCommandConfig> = {
  'git diff': {
    safeFlags: {
      '--oneline': 'none',
      '--stat': 'none',
      '--name-only': 'none',
      '-p': 'none',
      // SECURITY: -S/-G/-O are REQUIRED string arguments (pickaxe search).
      // Previously had type 'none' which caused a parser differential:
      // `git diff -S -- --output=/tmp/pwned` — validator saw -S as no-arg,
      // advanced 1 token, broke on `--`, left --output=... unchecked.
      // git itself sees -S requires arg, consumes `--` as pickaxe string →
      // cursor at --output=... → ARBITRARY FILE WRITE.
      '-S': 'string',
      '-G': 'string',
      '-O': 'string',
      '-R': 'none',
    },
  },
  'git log': {
    safeFlags: {
      '--oneline': 'none',
      '--graph': 'none',
      '--since': 'string',
      '--author': 'string',
      '--grep': 'string',
      '-n': 'number',
    },
  },
}
```

> **源码索引**：`src/utils/shell/readOnlyCommandValidation.ts` 第 120–200 行
>
> **设计原因**：`git diff` 的标志位验证中，`-S`、`-G`、`-O` 三个 pickaxe 选项的类型从 `'none'` 修正为 `'string'`，这是一个**真实安全漏洞（CVEC 类）的事后修复**。修复后的注释详细描述了攻击链：
>
> 1. 攻击者构造 `git diff -S -- --output=/tmp/pwned`
> 2. 验证器错误地将 `-S` 视为无参数 flag，向前推进一个 token（即消耗了 `--`）
> 3. `--output=/tmp/pwned` 被遗留未检查
> 4. git 本身在解析 `-S` 时发现它需要参数，吞噬了 `--` 作为 pickaxe 搜索字符串
> 5. `--output=` 成为下一个可解析的选项，导致任意文件写入
>
> 这个案例说明：**命令验证器的测试必须覆盖解析边界条件**，尤其是 `--` 分隔符、零长参数和可选参数的场景——这些地方最容易出现验证器与实际 shell 解析器的行为不一致（Parser Differential）。

### 16.2.3 xargs 安全目标命令白名单

`xargs` 是一个特别危险的命令，因为它可以执行任意程序。以下测试策略针对 `xargs` 的安全子集进行验证：

```
// src/utils/shell/readOnlyCommandValidation.ts 第 1703 行附近（validateFlags 函数内部）
// xargs 的安全实现在 validateFlags 函数内部，通过 xargsTargetCommands 参数和
// SAFE_TARGET_COMMANDS_FOR_XARGS 白名单实现，而非独立的常量
// 安全目标命令白名单包含：echo, printf, wc, grep, head, tail
```

> ⚠️ **重要勘误**：`XARGS_SAFE_FLAGS` **不存在于源码中**。xargs 的安全实现在 `validateFlags` 函数内部（约第 1703 行），通过 `xargsTargetCommands` 参数和 `SAFE_TARGET_COMMANDS_FOR_XARGS` 白名单实现，而非独立的常量。
>
> **设计原因**：xargs 的 `-i` 和 `-e` 选项被移除的根本原因是 **GNU getopt 的可选参数语义**（`i::`, `e::`）。在这种语义下：
> - `-iX`（无空格）：`X` 是替换字符串，`tail` 作为目标命令执行
> - `-i X`（有空格）：`-i` 无参数，`X` 被当作目标命令执行
>
> 验证器只能看到空格分隔的情况，因此无法区分。解决方案是**强制使用 `-I {}`（强制参数）**，这要求替换字符串必须紧跟 `{}`，消除了歧义。这体现了**安全测试的"最坏情况假设"原则**：不能依赖"正常用法"，必须覆盖"边界用法"。

---

## 16.3 集成测试设计

### 16.3.1 工具权限检查的集成测试

Claude Code 的工具系统通过 `checkPermissions()` 方法实现权限检查。集成测试需要覆盖完整的权限决策路径：

```
// src/tools/testing/TestingPermissionTool.tsx 完整源码

import { z } from 'zod/v4'
import type { Tool } from '../../Tool.js'
import { buildTool, type ToolDef } from '../../Tool.js'
import { lazySchema } from '../../utils/lazySchema.js'

const NAME = 'TestingPermission'

const inputSchema = lazySchema(() => z.strictObject({}))
type InputSchema = ReturnType<typeof inputSchema>

export const TestingPermissionTool: Tool<InputSchema, string> = buildTool({
  name: NAME,
  maxResultSizeChars: 100_000,

  async description() {
    return 'Test tool that always asks for permission'
  },

  async prompt() {
    return 'Test tool that always asks for permission before executing. Used for end-to-end testing.'
  },

  get inputSchema(): InputSchema {
    return inputSchema()
  },

  userFacingName() {
    return 'TestingPermission'
  },

  isEnabled() {
    // 仅在 test 环境下启用，防止测试工具进入生产环境
    return "production" === 'test'
  },

  isConcurrencySafe() {
    return true
  },

  isReadOnly() {
    return true
  },

  async checkPermissions() {
    // 该工具永远要求权限确认
    return {
      behavior: 'ask' as const,
      message: `Run test?`
    }
  },

  async call() {
    return {
      data: `${NAME} executed successfully`
    }
  },

  mapToolResultToToolResultBlockParam(result, toolUseID) {
    return {
      type: 'tool_result',
      content: String(result),
      tool_use_id: toolUseID
    }
  }
} satisfies ToolDef<InputSchema, string>)
```

> **源码索引**：`src/tools/testing/TestingPermissionTool.tsx` 第 1–74 行（完整文件）
>
> **设计原因**：
> 1. **`isEnabled()` 的环境守卫**：该工具通过 `"production" === 'test'` 逻辑确保自身只在测试环境激活。这是一个**防御性编程**实践——即使有人误将测试工具打包进生产构建，它也会自动禁用。
>
> 2. **`lazySchema()` 延迟求值**：使用 `lazySchema(() => z.strictObject({}))` 而非直接 `z.strictObject({})`，是因为 Zod schema 在模块加载时会执行反射操作。延迟到首次使用时再构造，避免了循环依赖问题（该文件导入了 `../../Tool.js`，而 `Tool` 模块本身可能依赖 schema 定义）。
>
> 3. **`checkPermissions()` 返回 `'ask'`**：集成测试用此工具验证权限系统的 UI 流程是否正常工作——每次调用必然触发权限对话框，而无需构造各种危险命令。

### 16.3.2 复合命令的集成测试边界

Claude Code 对复合命令（`&&`、`||`、`|` 分割的子命令）有专门的测试要求：

```
// src/tools/BashTool/bashPermissions.ts 中的子命令数量上限

// CC-643: On complex compound commands, splitCommand_DEPRECATED can produce a
// very large subcommands array (possible exponential growth; #21405's ReDoS fix
// may have been incomplete). Each subcommand then runs tree-sitter parse +
// ~20 validators + logEvent, and with memoized metadata the resulting microtask
// chain starves the event loop — REPL freeze at 100% CPU.
// Fifty is generous: legitimate user commands don't split that wide.
// Above the cap we fall back to 'ask' (safe default).
export const MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 50
```

> **源码索引**：`src/tools/BashTool/bashPermissions.ts` 第 95–106 行（CC-643 注释块），`MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 50` 在第 103 行
>
> **设计原因**：复合命令的安全检查存在**算法复杂度风险**——每个子命令都需要独立运行 AST 解析和约 20 个验证器，当子命令数量过多时可能导致事件循环饥饿。设置上限 `MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 50` 是一个**实用主义的安全闸门**：在达到上限后，系统回退到 `'ask'`（安全默认值），而非尝试完成全部检查。
>
> 这个设计的测试启示：**集成测试需要覆盖最坏情况输入**，如超长复合命令、极深嵌套结构等，而不仅仅是" happy path"。

### 16.3.3 BashTool 权限检查的多层链路

集成测试应覆盖从用户输入到最终执行结果的完整链路：

```
// src/tools/BashTool/bashPermissions.ts 的权限检查入口（推断自上下文）

// 权限检查的调用链（简化）：
// bashToolHasPermission()
//   ├── getSimpleCommandPrefix()         // 提取命令前缀
//   ├── extractRules()                    // 从配置文件提取规则
//   ├── classifyBashCommand()            // Haiku 分类器判断
//   ├── checkCommandOperatorPermissions() // 检查 && || | 等操作符
//   ├── checkPathConstraints()            // 路径约束检查
//   ├── checkSedConstraints()             // sed 命令约束
//   ├── shouldUseSandbox()                // 是否使用沙箱
//   └── createPermissionRequestMessage()  // 生成权限请求消息
```

> **设计原因**：权限检查被设计为**管道式多层过滤**，每一层负责一种类型的判断。这种设计的优势是**单一职责**：每层验证器只关注自己的领域（如路径、sed 表达式、shell 操作符），新增加密算法只需新增一层而不必修改已有逻辑。集成测试需要验证这些层之间的**交互边界**，例如：两层同时触发时的优先级、某层拒绝后其他层是否还会继续执行。

---

## 16.4 安全测试要点

### 16.4.1 命令注入的纵深防御测试

Claude Code 采用**四层纵深防御**架构。安全测试需要为每一层设计专门的攻击向量：

| 层级 | 检测手段 | 测试重点 |
|------|---------|---------|
| 第 1 层 | AST 解析（tree-sitter） | 命令结构解析、$() 替换检测、控制流识别 |
| 第 2 层 | 正则匹配（READONLY_COMMAND_REGEXES） | 白名单命令列表、严格正则表达式 |
| 第 3 层 | Flag 验证（COMMAND_ALLOWLIST + validateFlags） | 逐标志位白名单、参数类型校验 |
| 第 4 层 | 回调检查（additionalCommandIsDangerousCallback） | 自定义危险命令检测 |

```
// src/tools/BashTool/bashSecurity.ts 第 16–41 行

const COMMAND_SUBSTITUTION_PATTERNS = [
  { pattern: /<\(/, message: 'process substitution <()' },
  { pattern: />\(/, message: 'process substitution >()' },
  { pattern: /=\(/, message: 'Zsh process substitution =()' },
  // Zsh EQUALS expansion: =cmd at word start expands to $(which cmd).
  // `=curl evil.com` → `/usr/bin/curl evil.com`, bypassing Bash(curl:*) deny
  // rules since the parser sees `=curl` as the base command, not `curl`.
  {
    pattern: /(?:^|[\s;&|])=[a-zA-Z_]/,
    message: 'Zsh equals expansion (=cmd)',
  },
  { pattern: /=\$\[/, message: 'Zsh legacy arithmetic =$[' },
  { pattern: /\\\(e:/, message: 'Zsh special wrap \\(e:' },
  { pattern: /\\\(\+/, message: 'Zsh special wrap \\(+' },
  { pattern: /\\\}\\s*always\\s*\{/, message: 'Zsh always wrap' },
  { pattern: /\$\(/, message: '$() command substitution' },
  { pattern: /\$\{/, message: '${} parameter substitution' },
  { pattern: /\$\[/, message: '$[] legacy arithmetic expansion' },
  { pattern: /`/, message: 'backtick command substitution' },
  { pattern: /<#/, message: 'PowerShell comment syntax' },
]
```

> **源码索引**：`src/tools/BashTool/bashSecurity.ts` 第 8–36 行
>
> **安全测试关键**：
> - **`$()` 命令替换**是最常见的注入手段，测试必须覆盖 `$(whoami)`、`$(curl evil.com)` 等典型模式
> - **Zsh `=cmd` 扩展**是一个容易被忽视的绕过手段：攻击者可以用 `=curl` 代替 `curl`，绕过 `Bash(curl:*)` 的权限规则（因为解析器将 `=curl` 视为基础命令而非 `curl`）
> - 测试用例应覆盖**编码变形**：`${HOME}`、`$\{HOME\}`、单引号包裹 `$HOME` 等

### 16.4.2 危险命令的精细化白名单

Claude Code 的 `COMMAND_ALLOWLIST` 系统是声明式安全的典范。测试需要验证：

```
// src/tools/BashTool/readOnlyValidation.ts 中的 git 内部路径保护（推断）

// git 内部路径写入检测 — 禁止向以下路径写入：
// - HEAD
// - objects/
// - refs/
// - hooks/

// cd + git 组合封锁 — 防止 `cd /恶意目录 && git status` 触发恶意 hooks
```

> **安全测试用例设计**：
>
> | 测试编号 | 输入命令 | 预期行为 | 测试目的 |
> |---------|---------|---------|---------|
> | SEC-001 | `git write refs/heads/main` | deny | git 内部路径写入拦截 |
> | SEC-002 | `git status --hooks-path=/tmp` | deny | git hooks 路径参数拦截 |
> | SEC-003 | `cd /tmp && git status` | ask（额外检查） | cd+git 组合触发额外验证 |
> | SEC-004 | `xargs -i{} echo pwned` | deny（使用 -i） | xargs -i 的 optional-attached-arg 漏洞 |
> | SEC-005 | `xargs -I{} echo pwned` | allow（echo 在白名单） | -I{} 正确使用允许 |
> | SEC-006 | `xargs -EEOF echo foo` | allow（严格匹配 EOF） | -E EOF 字面量匹配 |
> | SEC-007 | `xargs -eX echo foo` | deny（-e 非 EOF） | -e 后接非 EOF 字面量拒绝 |

### 16.4.3 UNC 路径与 Windows 安全测试

```
// src/utils/shell/readOnlyCommandValidation.ts 中的 UNC 路径检测

// containsVulnerableUncPath 检测以下攻击模式：
// - \\server\share （SMB 共享路径）
// - \\server@SSL@8443\ （WebDAV over HTTPS 的 UNC 变体）
// - 包含端口的 UNC 路径（WebClient 服务攻击面）
```

> **源码索引**：`src/utils/shell/readOnlyCommandValidation.ts` 第 1546–1628 行（`containsVulnerableUncPath` 函数）
>
> **Windows 安全测试重点**：
> - WebDAV UNC 路径（`\\server@SSL@8443\`）用于绕过 Windows 的网络路径限制，通过 HTTPS WebDAV 访问本地文件
> - 测试应覆盖 IPv6 地址格式、IPv4 回环地址（`\\127.0.0.1\`）等变体
> - Unix 系统上虽然不存在 UNC 路径，但同类攻击可能通过 `file://` 协议实现，需要统一测试

### 16.4.4 Parser Differential 的系统性测试

**Parser Differential** 是命令验证中最隐蔽的漏洞类型：验证器的解析行为与实际 shell 工具的解析行为不一致。Claude Code 在代码中大量记录了这类发现：

```
// src/tools/BashTool/bashSecurity.ts 中的 SECURITY 注释

// SECURITY 注释示例（推断）：
// - `$VAR` 前缀如何绕过 flag 检测
// - brace expansion `{1..5}` 如何绕过 `{` 检测
// - `xargs -i`/`xargs -e` 的 optional-attached-arg 解析差异
// - `git diff -S -- --output=/tmp/pwned` 的 pickaxe 解析差异
// - `git ls-remote` 的 URL 过滤（拒绝包含 ://, @, : 的参数）
```

> **系统性测试策略**：
>
> Parser Differential 的测试需要**对照实验**：对同一命令字符串，分别用验证器和实际 shell 工具执行，比较两者的解析结果。
>
> ```bash
> # 示例：验证 git diff -S 的 parser differential
> # 验证器视角（错误）：
> #   -S: 无参数 → 消耗下一个 token ('--') → '--output=...' 遗留
> # git 视角（正确）：
> #   -S: 需要字符串参数 → 消耗 '--' 作为字符串 → '--output=...' 成为下一个选项
> ```
>
> 这种差异只能通过**穷举式边界测试**发现，而非基于代码覆盖率的测试（因为解析差异往往存在于"正常路径"中）。Claude Code 的做法是在代码注释中记录已发现的 parser differential，并将其转化为单元测试用例。

### 16.4.5 环境变量隔离测试

```
// src/tools/BashTool/bashPermissions.ts 中的 SAFE_ENV_VARS

// Allow 规则：只剥离 SAFE_ENV_VARS（防止 `DOCKER_HOST=evil docker ps` 绕过）
// Deny 规则：剥离所有环境变量前缀（更严格的防护）
const SAFE_ENV_VARS = new Set([
  'NODE_ENV',  // 常见框架配置，通常无安全影响
  'PATH',       // 需要仔细评估
  // ...
])
```

> **安全测试用例**：
>
> | 测试编号 | 输入命令 | 预期行为 | 测试目的 |
> |---------|---------|---------|---------|
> | ENV-001 | `NODE_ENV=production ls` | allow（NODE_ENV 在白名单） | 白名单环境变量放行 |
> | ENV-002 | `DOCKER_HOST=evil.com docker ps` | deny（DOCKER_HOST 不在白名单） | 危险环境变量拦截 |
> | ENV-003 | `MY_VAR=val npm run build` | 精确匹配或前缀匹配失败时 ask | 非白名单环境变量触发询问 |
>
> **设计原因**：环境变量注入是一种常见的配置类攻击。攻击者通过 `DOCKER_HOST=evil.com docker ps` 可以让 docker CLI 连接恶意守护进程。SAFE_ENV_VARS 白名单确保只有经过仔细审查的环境变量才被允许传入。

---

## 16.5 质量保证的工程实践

### 16.5.1 测试数据的契约化

本章多次强调的 `FlagArgType` 枚举（六种类型）是**测试数据契约化**的典范。这种设计使得：

1. **验证函数有明确的输入域**：任何非六种类型的值都是无效输入，TypeScript 编译时就能捕获
2. **新增标志位类型无需修改验证器核心**：只需在 `COMMAND_ALLOWLIST` 中添加新条目
3. **测试用例覆盖度可量化**：给定六种类型，测试工程师可以穷举每种类型的合法和非法值

```
// FlagArgType 的六种类型及其测试覆盖要求

type FlagArgType =
  | 'none'     // 测试：有无参数两种情况
  | 'number'   // 测试：整数、负数、零、超大数、非数字
  | 'string'   // 测试：普通字符串、空字符串、包含特殊字符的字符串
  | 'char'     // 测试：单字符、非字符（多字符）、空
  | '{}'       // 测试：字面量 {}、非 {} 字面量
  | 'EOF'      // 测试：字面量 EOF、非 EOF 字面量
```

### 16.5.2 安全注释的规范

Claude Code 的代码库中广泛使用 `SECURITY:` 前缀的注释，这种规范有几个关键价值：

```
// SECURITY: All three patterns MUST have a trailing boundary (?=\s|$).
// Without it, `> /dev/nullo` matches `/dev/nullo` as a PREFIX, strips
// `> /dev/null` leaving `o`, so `echo hi > /dev/nullo` becomes `echo hi o`.
// validateRedirections then sees no `>` and passes. The file write to
// /dev/nullo is auto-allowed via the read-only path.
```

> **源码索引**：`src/tools/BashTool/bashSecurity.ts` 第 177–188 行
>
> **规范价值**：
> - **可审计性**：grep `SECURITY:` 即可找到所有安全相关的设计决策
> - **知识传递**：未来的工程师在修改这段代码时，能立即理解"为什么要这样写"以及"改动的安全风险"
> - **测试指导**：SECURITY 注释本身就是测试用例的来源——每个注释描述的攻击链都对应一个测试用例

### 16.5.3 沙箱与权限的协同测试

Claude Code 的安全架构中，**沙箱**和**权限系统**是独立运行的两层防线：

```
// src/tools/BashTool/shouldUseSandbox.ts（推断）

// shouldUseSandbox() 判断命令是否应使用沙箱
// checkSandboxAutoAllow() 沙箱启用时自动允许只读命令

// 两者协同关系：
// 1. 权限系统决定"是否询问用户"
// 2. 沙箱系统决定"命令实际执行时的限制"
// 3. 两层独立运行，互不信任
```

> **测试设计**：沙箱和权限的组合测试需要覆盖四种状态：
>
> | 权限状态 | 沙箱状态 | 预期行为 |
> |---------|---------|---------|
> | allow | on | 执行，文件只读，进程隔离 |
> | allow | off | 执行，无额外限制（依赖权限白名单） |
> | ask | on | 弹出对话框，用户确认后以沙箱执行 |
> | deny | any | 拒绝执行，不调用沙箱 |
>
> **测试边界**：特别需要测试的是**沙箱逃逸场景**——即使在沙箱中，也要防止文件系统路径遍历（`/proc/self/environ` 访问等）。

---

## 16.6 本章小结

Claude Code 的测试与质量保证体系有几个核心特征值得借鉴：

1. **声明式配置优于命令式代码**：`COMMAND_ALLOWLIST` 将安全策略表达为数据而非逻辑，新增命令只需扩展配置而不必修改验证器核心。这使得测试可以**围绕配置数据进行**，而非对每个验证分支单独编写测试。

2. **Parser Differential 是命令验证的死敌**：验证器的测试必须覆盖**边界条件**（`--`、可选参数、零长参数、特殊字符转义等），因为这些地方最容易出现验证器与实际工具的解析差异。Claude Code 在代码注释中系统性地记录已发现的 differential，并将其转化为可重复的测试用例。

3. **四层纵深防御意味着四层独立测试**：每层防御都有其独立的失效模式，集成测试不能替代单元测试——必须分别验证每层的独立正确性，才能信任多层叠加的效果。

4. **SECURITY 注释是测试用例的来源**：将安全设计决策记录在代码注释中，既是工程规范，也是测试工程师的"需求文档"。每个 SECURITY 注释描述的攻击链，都对应至少一个测试用例。

5. **沙箱不是万能的，权限系统也不是**：两层防线各有盲区，联合测试必须覆盖两者之间的交互边界。

---

## 练习题

1. **Parser Differential 挖掘**：给定 `COMMAND_ALLOWLIST` 中的 `xargs` 配置，设计至少 5 个测试用例，覆盖 `xargs -i`、`xargs -e`（小写）的边界条件，并解释验证器和 GNU xargs 对每个用例的实际解析差异。

2. **纵深防御验证**：为 `git log` 命令设计一套完整的单元测试方案，分别针对：AST 解析层、标志位白名单层、回调检查层，每层至少 3 个测试用例（包括正常输入和攻击向量）。

3. **沙箱逃逸测试**：研究 Linux 命名空间沙箱的常见逃逸手段，设计测试用例验证 Claude Code 的沙箱是否能够防御以下攻击：
   - `/proc` 文件系统访问
   - Unix socket 逃逸
   - namespace 隔离失效

4. **复合命令 ReDoS 防护测试**：针对 `MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 50` 的限制，设计一个集成测试，验证超过 50 个子命令的复合命令是否正确回退到 `'ask'` 行为，并测试该限制不会影响合法命令的执行。

---
---

> **🧭 深入源码**
>
> 想了解测试框架的完整实现？请参考：
> - `src/schemas/hooks.ts` — 测试合约与 lazySchema
> - `src/tools/testing/TestingPermissionTool.tsx` — 测试权限工具
> - `src/utils/shell/readOnlyCommandValidation.ts` — 只读命令验证
> - `src/memdir/` — memdir 完整实现（测试用文件系统状态）

# 第十七章：实操：从零构建 Agent 工具

> **本章要点**：Tool 接口规范 → buildTool 工厂函数 → 工具注册流程 → 权限申请机制 → 完整工具开发示例
>
> **难度**：★★★★☆
> **前置知识**：TypeScript、Zod schema、异步编程

---

## 17.1 引言

在前面的章节中，我们已经从使用者视角介绍了 Agent 可用的一系列内置工具——Bash、Read、Edit、WebSearch 等等。但若要在这个系统中**新增一个自己的工具**，或者理解现有工具的内部结构，就必须深入了解工具系统的核心接口与构建机制。

Claude Code 的工具系统并非一个简单的函数集合，而是一套设计严谨的**类型安全框架**。它通过 TypeScript 的泛型约束、Zod schema 的输入验证，以及分层权限检查，确保每个工具的调用都是可预测、可审计、可控制的。

本章将系统讲解这套框架的核心组件，然后带领读者**从零构建一个真实可用的工具**——货币转换工具（CurrencyConverterTool）。

---

## 17.2 Tool 接口规范

所有工具的类型定义集中在 `src/Tool.ts`，其中 `Tool` 类型是整个系统的核心契约，定义始于行 362（行 362–行 440 为 `Tool` 类型，行 440–行 560 为 `ToolDef`/`BuiltTool`，行 560–行 792 为各工具实现）。

### 核心属性

一个完整的 `Tool` 对象必须包含以下属性：

```
// src/Tool.ts 行 280–295（简化展示）
export type Tool<
  Input extends AnyObject = AnyObject,  // 输入参数类型，由 Zod schema 约束
  Output = unknown,                      // 输出数据类型
  P extends ToolProgressData = ToolProgressData, // 进度数据类型
> = {
  readonly name: string                  // 工具的唯一名称，如 "Bash"
  readonly inputSchema: Input            // Zod 输入 schema，定义参数结构
  readonly outputSchema?: z.ZodType     // 可选：Zod 输出 schema

  maxResultSizeChars: number            // 结果大小上限（超过则持久化到磁盘）
  shouldDefer?: boolean                  // 是否延迟加载（需要 ToolSearch 触发）
  alwaysLoad?: boolean                   // 是否始终加载（不因 ToolSearch 省略）

  // 核心执行方法
  call(
    args: z.infer<Input>,
    context: ToolUseContext,
    canUseTool: CanUseToolFn,
    parentMessage: AssistantMessage,
    onProgress?: ToolCallProgress<P>,
  ): Promise<ToolResult<Output>>

  // 工具元信息
  description(input, options): Promise<string>  // 动态描述
  prompt(options): Promise<string>              // 工具专属提示词
  userFacingName(input?): string                // 用户可见名称
}
```

**设计原因**：使用泛型 `<Input, Output, P>` 而非 `any`，使得 TypeScript 能在编译期检查输入输出类型是否匹配。`maxResultSizeChars` 防止大结果撑爆上下文窗口——当结果超过限制时，系统会自动将结果写入磁盘，API 侧只收到一个文件路径。

### ToolUseContext——工具执行上下文

`call` 方法的第二个参数是 `ToolUseContext`（`src/Tool.ts` 行 158），它是一个包含**执行环境全部信息**的巨型对象。以下表格仅列出常用字段，实际 `ToolUseContext` 包含数十个字段（如 `addNotification`、`appendSystemMessage`、`sendOSNotification`、`localDenialTracking` 等）：

| 字段 | 用途 |
|------|------|
| `abortController` | 用于取消长时间运行的工具 |
| `getAppState() / setAppState()` | 读写应用状态（任务列表、配置等） |
| `messages` | 当前会话的完整消息历史 |
| `options.tools` | 所有可用工具的列表 |
| `options.mcpClients` | MCP 服务器连接 |
| `requestPrompt()` | 向用户发起交互式确认 |
| `setToolJSX()` | 推送自定义 UI 渲染 |

**设计原因**：`ToolUseContext` 将所有运行时依赖集中到一个对象中，而非作为全局变量访问。这使得工具可以在**没有全局状态的环境**下运行（如 SDK 模式、subagent 模式），也使得工具的行为完全由传入的 context 决定，便于测试和隔离。

### 输入验证与权限检查

```
// src/Tool.ts 行 489–495（validateInput），行 500–518（checkPermissions）
validateInput?(
  input: z.infer<Input>,
  context: ToolUseContext,
): Promise<ValidationResult>
// 返回 { result: true } 或 { result: false, message: string, errorCode: number }

checkPermissions(
  input: z.infer<Input>,
  context: ToolUseContext,
): Promise<PermissionResult>
// 返回 allow / ask / deny / passthrough 四种决策
```

**设计原因**：将权限检查分为 `validateInput`（逻辑验证）和 `checkPermissions`（权限决策）两个阶段。前者处理业务逻辑层面的校验（如参数合法性、资源存在性），后者处理安全层面的授权。两者分离使得权限规则可以集中管理，而不需要在每个工具内部重复编写。

---

## 17.3 buildTool 工厂函数

直接实现完整的 `Tool` 接口需要填写大量字段，其中许多字段有通用的安全默认值。为此，系统提供了 `buildTool` 工厂函数（`src/Tool.ts` 行 783），将默认逻辑集中在一处：

```
// src/Tool.ts 行 757（TOOL_DEFAULTS），行 783（buildTool 函数）
const TOOL_DEFAULTS = {
  isEnabled: () => true,
  isConcurrencySafe: (_input?) => false,    // 默认：不允许并发
  isReadOnly: (_input?) => false,            // 默认：视为写操作
  isDestructive: (_input?) => false,        // 默认：非破坏性
  checkPermissions: (input, _ctx) =>        // 默认：允许执行
    Promise.resolve({ behavior: 'allow', updatedInput: input }),
  toAutoClassifierInput: (_input?) => '',   // 默认：跳过安全分类器
  userFacingName: (_input?) => '',          // 默认：使用 tool.name
}

export function buildTool<D extends AnyToolDef>(def: D): BuiltTool<D> {
  return {
    ...TOOL_DEFAULTS,
    userFacingName: () => def.name,
    ...def,
  } as BuiltTool<D>
}
```

**设计原因**：**fail-closed（默认拒绝）原则**贯穿这些默认值。`isConcurrencySafe` 默认 `false` 是因为大多数工具涉及文件系统操作，并发执行可能导致竞态条件；`isReadOnly` 默认 `false` 使得默认行为需要明确的写权限确认。只有显式返回 `true` 的工具才能享受更宽松的权限策略。

---

## 17.4 工具注册流程

工具通过 `src/tools.ts` 中的 `getAllBaseTools()` 函数（行 193）集中注册。实际函数比以下示例更长，包含更多工具（`NotebookEditTool`、`TodoWriteTool`、`AskUserQuestionTool`、`SkillTool`、`EnterPlanModeTool`、`WorkflowTool`、`BriefTool` 等十余个工具），以及条件注册的工具。

```
// src/tools.ts 行 193（节选）
export function getAllBaseTools(): Tools {
  return [
    AgentTool,
    TaskOutputTool,
    BashTool,
    FileReadTool,
    FileEditTool,
    FileWriteTool,
    WebFetchTool,
    WebSearchTool,
    TaskStopTool,
    // ... 条件注册的工具
    ...(process.env.USER_TYPE === 'ant' ? [ConfigTool] : []),        // ① 环境条件
    ...(feature('PROACTIVE') ? [SleepTool] : []),                    // ② Feature Flag
    ...(isToolSearchEnabledOptimistic() ? [ToolSearchTool] : []),    // ③ 运行时判断
  ]
}
```

注册机制支持三种条件形式：

1. **环境变量**：`process.env.USER_TYPE === 'ant'` 用于区分不同构建版本
2. **Feature Flag**：`feature('PROACTIVE')` 由 GrowthBook 等特性平台动态控制
3. **运行时判断**：如 `isToolSearchEnabledOptimistic()` 查询用户配置

**工具过滤**：最终到达模型的工具列表还经过 `filterToolsByDenyRules()` 的过滤（`src/tools.ts` 行 262），根据用户的权限规则配置剔除被禁止的工具。这确保了即使在 `getAllBaseTools()` 中注册的工具，也可以在运行时被精确控制。

**shouldDefer 与 ToolSearch**：对于标记了 `shouldDefer: true` 的工具（如 `TaskStopTool`），初始提示中不会包含其完整 schema，模型需要先调用 `ToolSearch` 发现这些工具后才能使用它们。这是一种**按需加载**策略，减少了初始上下文大小。

---

## 17.5 权限申请机制详解

### PermissionResult 的四种决策

权限检查的核心返回值定义在 `src/types/permissions.ts`（行 251）：

```
// src/types/permissions.ts 行 172–265（概念性展示）
type PermissionAllowDecision = {
  behavior: 'allow'
  updatedInput?: Input        // 可修改后的输入
  userModified?: boolean     // 用户是否修改了参数
}

type PermissionAskDecision = {
  behavior: 'ask'
  message: string            // 展示给用户的提示信息
  suggestions?: PermissionUpdate[]  // 权限规则更新建议
  pendingClassifierCheck?: PendingClassifierCheck  // 异步分类器检查
}

type PermissionDenyDecision = {
  behavior: 'deny'
  message: string
  decisionReason: PermissionDecisionReason
}

type PermissionPassthroughDecision = {
  behavior: 'passthrough'    // 穿透到下一个检查器
  message: string
}
```

### checkPermissions 的典型实现

以 `TaskStopTool`（`src/tools/TaskStopTool/TaskStopTool.ts`）为例，它的 `checkPermissions` 使用默认实现（`allow`），因为停止任务本身不涉及文件修改或网络操作。而 `TestingPermissionTool`（`src/tools/testing/TestingPermissionTool.tsx` 行 36–42）则演示了如何强制要求用户确认：

```
// TestingPermissionTool.tsx 行 36–42
async checkPermissions() {
  // 这个工具永远要求用户确认
  return {
    behavior: 'ask' as const,
    message: `Run test?`
  }
}
```

**设计原因**：`behavior: 'ask'` 触发权限对话框，用户可以允许、拒绝或修改参数。`pendingClassifierCheck` 允许在显示对话框的同时异步运行安全分类器，如果分类器在用户响应前返回 `allow`，对话框会被自动取消——这是"非阻塞权限检查"设计的核心。

### validateInput 的典型实现

```
// src/tools/TaskStopTool/TaskStopTool.ts 行 60–75
async validateInput({ task_id, shell_id }, { getAppState }) {
  const id = task_id ?? shell_id
  if (!id) {
    return { result: false, message: 'Missing required parameter: task_id', errorCode: 1 }
  }
  const task = getAppState().tasks?.[id]
  if (!task) {
    return { result: false, message: `No task found with ID: ${id}`, errorCode: 1 }
  }
  if (task.status !== 'running') {
    return { result: false, message: `Task ${id} is not running`, errorCode: 3 }
  }
  return { result: true }
}
```

---

## 17.6 完整工具开发示例：CurrencyConverterTool

> ⚠️ **教学示例声明**：`CurrencyConverterTool` 是**虚构的教学工具**，Claude Code 源码中并不存在此工具。以下示例用于演示工具构建流程，不对应任何真实源码文件。

下面我们构建一个货币转换工具，完整演示从接口定义到注册上线的全过程。

### 第一步：定义目录结构

```
src/tools/CurrencyConverterTool/
├── CurrencyConverterTool.ts    ← 工具主文件
├── UI.tsx                     ← 渲染逻辑
└── prompt.ts                  ← 工具提示词
```

### 第二步：编写 prompt.ts

```
// prompt.ts
export const CURRENCY_CONVERTER_TOOL_NAME = 'CurrencyConverter'

export const DESCRIPTION =
  'Convert an amount from one currency to another using exchange rates.'

export const PROMPT = `CurrencyConverter converts monetary amounts between currencies.
Rates are fetched from a reliable public API. Supported currencies: USD, EUR, GBP, CNY, JPY.
Always verify the rate timestamp and show it to the user.
Use this whenever the user asks about currency conversion or exchange rates.`
```

### 第三步：编写主工具文件

```
// CurrencyConverterTool.ts
import { z } from 'zod/v4'
import { buildTool, type ToolDef, type ToolUseContext } from '../../Tool.js'
import { lazySchema } from '../../utils/lazySchema.js'
import { jsonStringify } from '../../utils/slowOperations.js'
import type { PermissionResult } from '../../types/permissions.js'
import { CURRENCY_CONVERTER_TOOL_NAME, DESCRIPTION, PROMPT } from './prompt.js'
import { renderToolResultMessage, renderToolUseMessage } from './UI.js'

// ── 第一步：定义输入 schema ──────────────────────────────────────────
const inputSchema = lazySchema(() =>
  z.strictObject({
    amount: z.number().positive().describe('Amount to convert'),
    from: z.string().length(3).toUpperCase()
      .describe('Source currency code (ISO 4217, e.g. USD)'),
    to: z.string().length(3).toUpperCase()
      .describe('Target currency code (ISO 4217, e.g. CNY)'),
  }),
)
type InputSchema = ReturnType<typeof inputSchema>

// ── 第二步：定义输出 schema ──────────────────────────────────────────
const outputSchema = lazySchema(() =>
  z.object({
    original: z.object({
      amount: z.number(),
      currency: z.string(),
    }),
    converted: z.object({
      amount: z.number(),
      currency: z.string(),
    }),
    rate: z.number().describe('Exchange rate used'),
    rateTimestamp: z.string().describe('ISO timestamp of the rate'),
    provider: z.string().describe('Data provider name'),
  }),
)
type Output = z.infer<ReturnType<typeof outputSchema>>

// ── 第三步：使用 buildTool 构建工具 ─────────────────────────────────
export const CurrencyConverterTool = buildTool({
  name: CURRENCY_CONVERTER_TOOL_NAME,
  maxResultSizeChars: 10_000,
  searchHint: 'exchange rate currency conversion',
  aliases: ['ConvertCurrency', 'CurrencyConvert'],

  get inputSchema(): InputSchema { return inputSchema() },
  get outputSchema(): OutputSchema { return outputSchema() },

  // 工具始终可用
  isEnabled() { return true },
  // 读操作，不修改任何资源
  isReadOnly() { return true },
  // 可安全并发（多个转换互不干扰）
  isConcurrencySafe() { return true },

  // 描述（模型据此理解工具能力）
  async description() { return DESCRIPTION },
  // 提示词（补充模型不知道的实现细节）
  async prompt() { return PROMPT },

  // 用户可见名称
  userFacingName() { return 'Currency Converter' },

  // 验证输入参数
  async validateInput({ amount, from, to }, _context: ToolUseContext) {
    if (amount <= 0) {
      return { result: false, message: 'Amount must be positive', errorCode: 1 }
    }
    if (from === to) {
      return { result: false, message: 'Source and target currencies must differ', errorCode: 2 }
    }
    return { result: true }
  },

  // 权限检查：货币转换是只读操作，直接允许
  async checkPermissions(input) {
    return { behavior: 'allow', updatedInput: input }
  },

  // 渲染工具调用消息（REPL UI）
  renderToolUseMessage,
  // 渲染工具结果消息
  renderToolResultMessage,

  // 序列化结果给模型
  mapToolResultToToolResultBlockParam(output, toolUseID) {
    return {
      tool_use_id: toolUseID,
      type: 'tool_result',
      content: jsonStringify(output),
    }
  },

  // 核心执行逻辑
  async call({ amount, from, to }, { abortController }) {
    const controller = abortController as AbortController
    const controllerSignal = controller?.signal

    const url = `https://api.exchangerate.host/convert?from=${from}&to=${to}&amount=${amount}`

    const response = await fetch(url, { signal: controllerSignal })
    if (!response.ok) {
      throw new Error(`Exchange rate API error: ${response.status}`)
    }
    const data = await response.json() as {
      result: number
      date: string
      historical: string
    }

    const rate = data.result / amount

    return {
      data: {
        original: { amount, currency: from },
        converted: { amount: data.result, currency: to },
        rate,
        rateTimestamp: data.date ?? data.historical ?? new Date().toISOString(),
        provider: 'exchangerate.host',
      },
    }
  },
} satisfies ToolDef<InputSchema, Output>)
```

### 第四步：编写 UI.tsx

```
// UI.tsx
import * as React from 'react'
import type { ToolUseContext } from '../../Tool.js'
import { CURRENCY_CONVERTER_TOOL_NAME } from './prompt.js'

export function renderToolUseMessage(
  input: Partial<{ amount: number; from: string; to: string }>,
  _options: { theme: string; verbose: boolean },
) {
  if (!input.amount) return <span>{CURRENCY_CONVERTER_TOOL_NAME}</span>
  return (
    <span>
      Convert <strong>{input.amount}</strong> {input.from} → {input.to}
    </span>
  )
}

export function renderToolResultMessage(
  output: {
    original: { amount: number; currency: string }
    converted: { amount: number; currency: string }
    rate: number
    rateTimestamp: string
    provider: string
  },
  _progressMessages: unknown[],
  _options: { theme: string; tools: unknown; verbose: boolean },
) {
  return (
    <div>
      <div>
        <strong>{output.original.amount} {output.original.currency}</strong>
        {' = '}
        <strong>{output.converted.amount.toFixed(2)} {output.converted.currency}</strong>
      </div>
      <div style={{ opacity: 0.7, fontSize: '0.9em' }}>
        Rate: {output.rate} · {output.rateTimestamp} · via {output.provider}
      </div>
    </div>
  )
}
```

### 第五步：注册工具

在 `src/tools.ts` 的 `getAllBaseTools()` 函数中添加一行：

```
// src/tools.ts（加入 getAllBaseTools 的返回值数组）
import { CurrencyConverterTool } from './tools/CurrencyConverterTool/CurrencyConverterTool.js'
// ...
return [
  // ... 其他工具
  CurrencyConverterTool,  // ← 新增
]
```

### 设计要点总结

| 决策 | 原因 |
|------|------|
| 使用 `lazySchema()` 包装 Zod schema | 避免模块初始化时执行 schema 构造（涉及可能的反射操作） |
| `isReadOnly: true` | 明确声明这是只读工具，权限系统据此采用宽松策略 |
| `isConcurrencySafe: true` | 多个货币转换请求互不干扰，可以并行处理 |
| 通过 `validateInput` 检查 `from !== to` | 在 API 调用前尽早失败，减少不必要的网络请求 |
| `renderToolUseMessage` 返回部分 `input` | 工具参数可能还在流式传输中，渲染时只能访问部分数据 |
| 结果包含 `provider` 和 `rateTimestamp` | 货币汇率有时效性，必须告知用户数据的时效和来源 |

---

## 17.7 小结

本章从源码层面完整拆解了 Claude Code 工具系统的构建哲学：

1. **类型安全优先**：通过泛型 `Tool<Input, Output, P>` 和 Zod schema，工具的契约在编译期就被严格约束，任何类型不匹配都会触发 TypeScript 错误。

2. **fail-closed 默认值**：`buildTool` 的默认实现对安全敏感的操作（并发、破坏性、权限）全部采用拒绝策略，工具开发者必须显式声明才能放宽限制。

3. **验证与权限分离**：`validateInput` 处理业务校验，`checkPermissions` 处理安全决策。分离的设计使得权限规则可以集中管理，不需要在每个工具中重复实现。

4. **渐进式工具加载**：`shouldDefer` 机制通过 ToolSearch 实现了工具的按需发现，避免了一次性向模型暴露过多工具导致的决策负担。

5. **完整的渲染抽象**：工具系统不仅返回数据，还负责在 REPL UI 中的呈现方式。`renderToolUseMessage`、`renderToolResultMessage` 等方法使得每个工具都可以有独特的视觉表达。

掌握了这套框架的设计逻辑，你不仅可以**开发新工具**接入这个 Agent 系统，还可以**审计和加固**现有工具的安全性——理解每个字段的默认值含义，就能判断一个工具是否正确声明了自己的风险级别。

---

# 第十八章：实操：安全设计模式

安全设计模式是将抽象的安全原则转化为具体工程实现的桥梁。本章以 Claude Code 源码为蓝本，深入剖析权限系统、输入验证、审计日志三大核心模块的设计模式与实现细节。通过源码级别的解读，读者将掌握如何构建既安全又实用的工程系统。

## 18.1 安全设计的核心原则

### 18.1.1 纵深防御策略

Claude Code 的安全架构绝不依赖单一防线。每一项操作都必须经过多层独立检查，任何一层失效都不会导致安全崩溃。

**实操示例：命令替换检测的多层防御**

在 `bashSecurity.ts` 中，命令替换攻击被分解为多个独立检查项：

```
// src/tools/BashTool/bashSecurity.ts:16-41
const COMMAND_SUBSTITUTION_PATTERNS = [
  { pattern: /<\(/, message: 'process substitution <()' },     // 进程替换 <()
  { pattern: />\(/, message: 'process substitution >()' },     // 进程替换 >()
  { pattern: /=\(/, message: 'Zsh process substitution =()' },  // Zsh =cmd 扩展
  { pattern: /(?:^|[\s;&|])=[a-zA-Z_]/, message: 'Zsh equals expansion' },
  // 防止 =curl evil.com → /usr/bin/curl evil.com（绕过 Bash(curl:*) 规则）
  { pattern: /=\$\[/, message: 'Zsh legacy arithmetic =$[' },   // Zsh 旧式算术扩展
  { pattern: /\\\(e:/, message: 'Zsh special wrap \\(e:' },    // Zsh \\(e: 特殊包裹
  { pattern: /\\\(\+/, message: 'Zsh special wrap \\(+' },      // Zsh \\(+ 特殊包裹
  { pattern: /\\\}\\s*always\\s*\{/, message: 'Zsh always wrap' }, // Zsh always 包裹
  { pattern: /\$\(/, message: '$() command substitution' },     // $() 命令替换
  { pattern: /\$\{/, message: '${} parameter substitution' }, // ${} 参数替换
  { pattern: /\$\[/, message: '$[] legacy arithmetic expansion' }, // $[] 旧式算术
  { pattern: /`/, message: 'backtick command substitution' },  // 反引号命令替换
  { pattern: /<#/, message: 'PowerShell comment syntax' },    // PowerShell 注释
]
```

**设计原因**：如果只用一个正则表达式检测命令替换，一旦该正则被绕过，整个防御就失效。分解为 14 个独立模式后，攻击者需要同时绕过所有检查才能成功。

### 18.1.2 确定性优先原则

对于已知的安全威胁，优先使用精确的确定性检查，而非依赖 AI 的模糊判断。

```
// src/tools/BashTool/bashSecurity.ts:244
function validateIncompleteCommands(context: ValidationContext): PermissionResult {
  const { originalCommand } = context
  const trimmed = originalCommand.trim()

  // 检测不完整的命令片段
  if (/^\s*\t/.test(originalCommand)) {
    return { behavior: 'ask', message: 'Command appears incomplete' }
  }
  if (trimmed.startsWith('-')) {
    return { behavior: 'ask', message: 'Command starts with flags' }
  }
  if (/^\s*(&&|\|\||;|>>?|<)/.test(originalCommand)) {
    return { behavior: 'ask', message: 'Command starts with operator' }
  }
  return { behavior: 'passthrough' }
}
```

**设计原因**：确定性检查的执行结果是可预测的，不受模型能力波动影响。这使得安全检查的行为可以被准确测试和验证。

### 18.1.3 失败即询问原则

任何无法被证明安全的操作，都必须升级为用户交互提示，而非静默放行。

`hasPermissionsToUseToolInner` 位于 `src/utils/permissions/permissions.ts`（行 1158 起），是一个 **200+ 行的复杂函数**，其实际执行流程远比"两步"结构复杂：

```
1a 整工具 deny 规则检查 → deny
1b 整工具 ask 规则检查 → ask
1c 调用 tool.checkPermissions（工具自身安全检查）
1d 工具返回的 deny 结果检查 → deny
1e requiresUserInteraction 判断 → 沙箱自动允许逻辑（canSandboxAutoAllow）
自动模式分类器（Auto Classifier）评估 → deny/ask/allow
```

**设计原因**：静默放行危险操作比拒绝安全操作危害更大。宁可让用户多点击一次"允许"，也不能让恶意操作趁虚而入。

## 18.2 权限最小化的工程实现

### 18.2.1 权限规则的分层结构

Claude Code 的权限规则采用分层架构，从高到低依次为：

```
// src/utils/permissions/PermissionMode.ts:42（范围到约第90行）
const PERMISSION_MODE_CONFIG: Partial<Record<PermissionMode, PermissionModeConfig>> = {
  default: { title: 'Default', color: 'text', external: 'default' },
  plan: { title: 'Plan Mode', color: 'planMode', external: 'plan' },
  acceptEdits: { title: 'Accept edits', color: 'autoAccept', external: 'acceptEdits' },
  bypassPermissions: { title: 'Bypass Permissions', color: 'error', external: 'bypassPermissions' },
  dontAsk: { title: "Don't Ask", color: 'error', external: 'dontAsk' },
}
```

**设计原因**：分层设计让权限控制变得可组合。每个层级都有明确的语义，用户可以根据任务需求选择合适的权限级别。

### 18.2.2 基于规则的精确匹配

权限规则支持精确匹配和前缀匹配两种模式：

```
// src/utils/permissions/permissions.ts:362
export function getRuleByContentsForToolName(
  context: ToolPermissionContext,
  toolName: string,
  behavior: PermissionBehavior,
): Map<string, PermissionRule> {
  const ruleByContents = new Map<string, PermissionRule>()
  const rules = behavior === 'allow' ? getAllowRules(context)
              : behavior === 'deny' ? getDenyRules(context)
              : getAskRules(context)

  for (const rule of rules) {
    if (rule.ruleValue.toolName === toolName &&
        rule.ruleValue.ruleContent !== undefined) {
      ruleByContents.set(rule.ruleValue.ruleContent, rule)
    }
  }
  return ruleByContents
}
```

**实操示例：Bash 工具的前缀规则匹配**

```
// src/utils/permissions/permissions.ts:238
function toolMatchesRule(tool: Pick<Tool, 'name' | 'mcpInfo'>, rule: PermissionRule): boolean {
  // 规则必须没有内容才能匹配整个工具
  if (rule.ruleValue.ruleContent !== undefined) return false

  const nameForRuleMatch = getToolNameForPermissionCheck(tool)

  // 直接工具名匹配
  if (rule.ruleValue.toolName === nameForRuleMatch) return true

  // MCP服务器级权限: 规则"mcp__server1"匹配工具"mcp__server1__tool1"
  const ruleInfo = mcpInfoFromString(rule.ruleValue.toolName)
  const toolInfo = mcpInfoFromString(nameForRuleMatch)

  return ruleInfo !== null && toolInfo !== null &&
    (ruleInfo.toolName === undefined || ruleInfo.toolName === '*') &&
    ruleInfo.serverName === toolInfo.serverName
}
```

**设计原因**：前缀匹配允许管理员用一条规则控制一类操作（如 `Bash(npm:*)` 控制所有 npm 相关命令），而 MCP 服务器级匹配则支持细粒度的 MCP 工具权限控制。

### 18.2.3 拒绝追踪机制

权限系统通过 `src/utils/permissions/denialTracking.ts` 实现智能重试控制：

```
// src/utils/permissions/denialTracking.ts:12（DENIAL_LIMITS），行 40（shouldFallbackToPrompting）
export const DENIAL_LIMITS = {
  maxConsecutive: 3,  // 连续拒绝上限
  maxTotal: 20,       // 累计拒绝上限
} as const

export function shouldFallbackToPrompting(state: DenialTrackingState): boolean {
  return (
    state.consecutiveDenials >= DENIAL_LIMITS.maxConsecutive ||
    state.totalDenials >= DENIAL_LIMITS.maxTotal
  )
}
```

**设计原因**：连续拒绝表明 AI 可能在误判安全操作，累计拒绝过多则说明权限配置可能过于严格。当达到任一上限时，系统回退到用户交互模式，让人类重新评估。

## 18.3 输入验证的模式设计

### 18.3.1 分层验证架构

Claude Code 的输入验证采用三层架构：基础验证 → 上下文验证 → 路径约束验证。

**第一层：基础安全检查**

```
// src/tools/BashTool/bashSecurity.ts:846
function validateDangerousPatterns(context: ValidationContext): PermissionResult {
  const { unquotedContent } = context

  // 检查未转义的倒引号
  if (hasUnescapedChar(unquotedContent, '`')) {
    return { behavior: 'ask', message: 'Command contains backticks for command substitution' }
  }

  // 检查命令替换模式
  for (const { pattern, message } of COMMAND_SUBSTITUTION_PATTERNS) {
    if (pattern.test(unquotedContent)) {
      return { behavior: 'ask', message: `Command contains ${message}` }
    }
  }
  return { behavior: 'passthrough' }
}
```

**第二层：上下文感知验证**

```
// src/tools/BashTool/bashSecurity.ts:612
function validateGitCommit(context: ValidationContext): PermissionResult {
  const { originalCommand, baseCommand } = context

  if (baseCommand !== 'git' || !/^git\s+commit\s+/.test(originalCommand)) {
    return { behavior: 'passthrough', message: 'Not a git commit' }
  }

  // git commit -m "message" 的消息内容检查
  const messageMatch = originalCommand.match(
    /^git[ \t]+commit[ \t]+[^;&|`$<>()\n\r]*?-m[ \t]+(["'])([\s\S]*?)\1(.*)$/
  )

  if (messageMatch) {
    const [, quote, messageContent, remainder] = messageMatch
    // 检查双引号消息中的命令替换
    if (quote === '"' && messageContent && /\$\(|`|\$\{/.test(messageContent)) {
      return { behavior: 'ask', message: 'Git commit message contains command substitution' }
    }
  }
  return { behavior: 'allow' }
}
```

**设计原因**：第二层验证充分利用命令的语义上下文。`git commit` 命令本身可能是安全的，但其消息参数可能包含恶意内容。

### 18.3.2 路径约束验证

`PATH_EXTRACTORS` 位于 `src/tools/BashTool/pathValidation.ts` **第 190 行**。

```
// src/tools/BashTool/pathValidation.ts:190
export const PATH_EXTRACTORS: Record<PathCommand, (args: string[]) => string[]> = {
  cd: args => (args.length === 0 ? [homedir()] : [args.join(' ')]),
  ls: args => {
    const paths = filterOutFlags(args)
    return paths.length > 0 ? paths : ['.']
  },
  find: args => {
    // find命令需要特殊处理
    const paths: string[] = []
    const pathFlags = new Set(['-newer', '-anewer', '-path', '-wholename'])
    // ... 实现细节
    return paths.length > 0 ? paths : ['.']
  },
  rm: filterOutFlags,
  mv: filterOutFlags,
  // ...
}
```

**设计原因**：每种命令处理路径的方式不同。`find` 需要解析复杂的参数结构，而 `ls` 则简单得多。专门化的提取器确保准确捕获所有路径。

### 18.3.3 模糊清理与正则化

```
// src/tools/BashTool/bashSecurity.ts:176
function stripSafeRedirections(content: string): string {
  // 移除安全的重定向模式
  return content
    .replace(/\s+2\s*>&\s*1(?=\s|$)/g, '')  // 2>&1
    .replace(/[012]?\s*>\s*\/dev\/null(?=\s|$)/g, '')  // >/dev/null
    .replace(/\s*<\s*\/dev\/null(?=\s|$)/g, '')  // </dev/null
}
```

**设计原因**：`>/dev/null` 和 `2>&1` 是无害的重定向，但它们会干扰路径分析。预先清理这些模式可以让后续检查更准确。

## 18.4 审计日志的设计与实现

### 18.4.1 事件日志基础设施

Claude Code 使用统一的事件日志系统记录所有安全相关事件：

```
// src/tools/BashTool/bashSecurity.ts:77
const BASH_SECURITY_CHECK_IDS = {
  INCOMPLETE_COMMANDS: 1,
  JQ_SYSTEM_FUNCTION: 2,
  JQ_FILE_ARGUMENTS: 3,
  OBFUSCATED_FLAGS: 4,
  SHELL_METACHARACTERS: 5,
  DANGEROUS_VARIABLES: 6,
  NEWLINES: 7,
  DANGEROUS_PATTERNS_COMMAND_SUBSTITUTION: 8,
  INPUT_REDIRECTION: 9,
  OUTPUT_REDIRECTION: 10,
  IFS_INJECTION: 11,
  GIT_COMMIT_SUBSTITUTION: 12,
  PROC_ENVIRON_ACCESS: 13,
  MALFORMED_TOKEN_INJECTION: 14,
  BACKSLASH_ESCAPED_WHITESPACE: 15,
  BRACE_EXPANSION: 16,
  CONTROL_CHARACTERS: 17,
  UNICODE_WHITESPACE: 18,
  MID_WORD_HASH: 19,
  ZSH_DANGEROUS_COMMANDS: 20,
  BACKSLASH_ESCAPED_OPERATORS: 21,
  COMMENT_QUOTE_DESYNC: 22,
  QUOTED_NEWLINE: 23,
} as const
```

// 记录安全检查触发
logEvent('tengu_bash_security_check_triggered', {
  checkId: BASH_SECURITY_CHECK_IDS.JQ_SYSTEM_FUNCTION,
  subId: 1,
})
```

**设计原因**：数字化的检查 ID 比字符串更紧凑，便于聚合分析。同时允许精确定位是哪个子检查触发了警报。

### 18.4.2 决策追踪

每个权限决策都会生成详细的审计轨迹：

```
// src/utils/permissions/permissions.ts:137
export function createPermissionRequestMessage(
  toolName: string,
  decisionReason?: PermissionDecisionReason,
): string {
  if (decisionReason) {
    switch (decisionReason.type) {
      case 'hook':
        return `Hook '${decisionReason.hookName}' blocked: ${decisionReason.reason}`
      case 'rule':
        const ruleString = permissionRuleValueToString(decisionReason.rule.ruleValue)
        return `Rule '${ruleString}' requires approval`
      case 'classifier':
        return `Classifier '${decisionReason.classifier}' blocked: ${decisionReason.reason}`
      case 'safetyCheck':
        return `Safety check blocked: ${decisionReason.reason}`
    }
  }
  return `Permission required for ${toolName}`
}
```

### 18.4.3 分类器决策日志

```
// src/utils/permissions/permissions.ts:733（主调用处）
logEvent('tengu_auto_mode_decision', {
  // 决策结果
  decision: yoloDecision,                              // 'blocked' | 'allowed' | 'unavailable'
  toolName: sanitizeToolNameForAnalytics(tool.name),
  inProtectedNamespace: isInProtectedNamespace(context),
  fastPath: isFastPathEligible(input),                 // 走 fast-path 而非分类器
  confidence: classifierResult.confidence,           // 分类器置信度
  // 模型信息
  classifierModel: classifierResult.model,
  classifierStage: classifierResult.stage,            // 'stage1' | 'stage2'
  stage1Usage: classifierResult.usage?.inputTokens,  // Stage1 token 用量
  stage1DurationMs: classifierResult.stage1DurationMs,
  stage1RequestId: classifierResult.stage1RequestId,
  stage1MsgId: classifierResult.stage1MsgId,
  // Token 用量（完整）
  classifierInputTokens: classifierResult.usage?.inputTokens,
  classifierOutputTokens: classifierResult.usage?.outputTokens,
  classifierCacheReadInputTokens: classifierResult.usage?.cacheReadInputTokens,
  classifierCacheCreationInputTokens: classifierResult.usage?.cacheCreationInputTokens,
  sessionInputTokens: sessionUsage.inputTokens,
  sessionOutputTokens: sessionUsage.outputTokens,
  sessionCacheReadInputTokens: sessionUsage.cacheReadInputTokens,
  sessionCacheCreationInputTokens: sessionUsage.cacheCreationInputTokens,
  // 成本与请求追踪
  classifierCostUSD: classifierResult.costUSD,
  agentMsgId: classifierResult.agentMsgId,
  // 请求上下文
  requestId: classifierResult.requestId,
  msgId: classifierResult.msgId,
  // 拒绝状态
  consecutiveDenials: denialState.consecutiveDenials,
  totalDenials: denialState.totalDenials,
  denialLimitHit: denialState.denialLimitExceeded,
  // 分类器耗时
  classifierDurationMs: classifierResult.durationMs,
  // 原始分类器输出（用于事后审计）
  rawClassification: classifierResult.rawOutput,
})
```

**设计原因**：完整的审计日志使得事后分析成为可能。当出现安全事件时，调查人员可以追溯完整的决策链，包括模型输入、输出和中间状态。

## 18.5 安全设计模式的工程实践

### 18.5.1 模式清单

综合本章内容，以下是构建安全系统时应遵循的核心设计模式：

| 模式名称 | 适用场景 | 核心实现 |
|---------|---------|---------|
| 纵深防御 | 所有安全关键路径 | 多层独立检查，每层失败升级到下一层 |
| 确定性优先 | 已知威胁模式 | 精确正则/AST解析，不依赖AI判断 |
| 失败即询问 | 所有边界情况 | 无法证明安全时必须提示用户 |
| 最小权限 | 权限系统设计 | 精确匹配优先于通配符 |
| 审计追踪 | 合规与事件响应 | 数字ID + 完整决策上下文 |

### 18.5.2 常见陷阱与规避

**陷阱一：单一检查点依赖**

```
// ❌ 错误：单一检查点
function isCommandSafe(cmd: string): boolean {
  return !cmd.includes('rm -rf')
}

// ✅ 正确：多层检查
function isCommandSafe(cmd: string): boolean {
  if (containsRecursiveDelete(cmd)) return false
  if (matchesDangerousPattern(cmd)) return false
  if (outsideAllowedScope(cmd)) return false
  return true
}
```

**陷阱二：静默降级**

```
// ❌ 错误：验证失败时静默放行
function validateInput(input: string): boolean {
  if (!isValid(input)) return true  // 静默放行!
}

// ✅ 正确：验证失败时升级
function validateInput(input: string): ValidationResult {
  if (!isValid(input)) return { safe: false, reason: 'invalid format' }
  return { safe: true }
}
```

**陷阱三：过度依赖白名单**

```
// ❌ 错误：仅依赖白名单
function isAllowed(cmd: string): boolean {
  return ALLOWED_COMMANDS.has(cmd)
}

// ✅ 正确：白名单 + 行为分析
function isAllowed(cmd: string): boolean {
  if (!ALLOWED_COMMANDS.has(cmd)) return false
  return analyzeBehavior(cmd).isSafe
}
```

## 18.6 小结

本章通过 Claude Code 源码的深度剖析，展示了安全设计模式从理论到工程实践的完整路径。核心要点包括：

1. **纵深防御是唯一可靠的安全策略**：单层检查无论多严密都可能失效，多层独立检查才能构建真正安全的系统。

2. **权限最小化需要精确的工具**：精确匹配、前缀规则、MCP 服务器级控制等机制让权限粒度可以达到单个操作级别。

3. **输入验证必须分层进行**：基础安全检查、上下文感知验证、路径约束验证三层架构可以有效应对各种攻击向量。

4. **审计日志是安全的最后防线**：完整的事件追踪不仅满足合规要求，更是在安全事件发生后进行根因分析的关键。

将这些设计模式融入日常工程实践，能够显著提升系统的安全基线，降低安全事件的发生概率和影响范围。

---

# 第十九章：成本控制策略

## 概述

Claude Code 是一个功能强大的 AI 编程助手，但每一条与 Claude API 的交互都会产生真实的费用。有效地控制成本，不仅是节省开支的问题，更是一种工程上的理性——在有限的预算下实现最大化的开发效率。本章将从源码层面深入剖析 Claude Code 的成本控制体系，涵盖 Prompt Cache 的成本效益分析、模型分层使用策略、Token 消耗的可观测性、并行 Agent 的成本风险，以及成本控制与性能之间的权衡。

---

## 19.1 Prompt Cache 的成本效益分析

### 19.1.1 缓存机制的工作原理

Claude API 的 Prompt Cache（上下文缓存）允许将昂贵的系统提示词和工具模式（tool schemas）缓存起来，在后续请求中以大幅折扣的价格重新读取。Claude Code 在 `src/services/api/claude.ts` 中实现了完整的缓存控制逻辑。

缓存写入的触发位置在 `addCacheBreakpoints` 函数中（`src/services/api/claude.ts` 第 3063 行附近），它将 `cache_control` 标记添加到消息序列的最后一个消息上（代码示例对应第 3091-3093 行）：

```
const markerIndex = skipCacheWrite ? messages.length - 2 : messages.length - 1
const result = messages.map((msg, index) => {
  const addCache = index === markerIndex
  // ...
})
```

为什么是"最后一个消息"？源码注释解释得非常清楚：

> Exactly one message-level cache_control marker per request. With two markers the second-to-last position is protected and its locals survive an extra turn even though nothing will ever resume from there — with one marker they're freed immediately.

这种设计确保了服务器端 KV Cache 的高效利用——每个请求只保护一个缓存前缀，避免了缓存空间的浪费。

### 19.1.2 缓存成本节省的量化

Claude Code 的 `cost-tracker.ts` 在 `addToTotalModelUsage` 函数（第 204-207 行）内提供细粒度的缓存使用统计：

```
// src/utils/cost-tracker.ts:204-207（addToTotalModelUsage 函数内部）
modelUsage.inputTokens += usage.input_tokens
modelUsage.outputTokens += usage.output_tokens
modelUsage.cacheReadInputTokens += usage.cache_read_input_tokens ?? 0
modelUsage.cacheCreationInputTokens += usage.cache_creation_input_tokens ?? 0
```

通过 `getModelUsage()` 可以按模型维度查看缓存读写 Token 的消耗。输出格式化为（`formatModelUsage` 函数，`cost-tracker.ts` 第 181 行）：

```
claude-3-5-sonnet: 15,234 input, 8,102 output, 45,678 cache read, 2,100 cache write ($0.42)
```

这里的关键洞察是：**cache read 的价格远低于 input token 的价格**。以 Sonnet 为例，cache read 的成本约为 input token 的 10%，而 cache write 成本与 input token 相当。因此，当同一个系统提示词被复用超过 10 次时，缓存就开始产生净节省。

### 19.1.3 缓存失效的检测与应对

Claude Code 实现了 `PROMPT_CACHE_BREAK_DETECTION` 特性（`src/services/api/claude.ts` 第 1460 行，feature check），通过比对请求前后的缓存状态来检测缓存是否被意外破坏（`recordPromptState` 在第 1471 行被调用）：

```
recordPromptState({
  system,
  toolSchemas: toolsForCacheDetection,
  querySource: options.querySource,
  model: options.model,
  agentId: options.agentId,
  fastMode: fastModeHeaderLatched,
  globalCacheStrategy,
  betas,
  // ...
})
```

当检测到缓存断裂时，会触发重新写入（`checkResponseForCacheBreak`），这确保了即使在 GrowthBook 配置变更或环境变量更新的边缘情况下，Claude Code 也能平滑降级。

### 19.1.4 环境变量层面的精细控制

Claude Code 提供了三个互不干扰的环境变量来按模型禁用缓存（`src/services/api/claude.ts` 第 333–356 行）：

```
export function getPromptCachingEnabled(model: string): boolean {
  if (isEnvTruthy(process.env.DISABLE_PROMPT_CACHING)) return false
  if (isEnvTruthy(process.env.DISABLE_PROMPT_CACHING_HAIKU)) {
    const smallFastModel = getSmallFastModel()
    if (model === smallFastModel) return false
  }
  if (isEnvTruthy(process.env.DISABLE_PROMPT_CACHING_SONNET)) {
    if (model === getDefaultSonnetModel()) return false
  }
  if (isEnvTruthy(process.env.DISABLE_PROMPT_CACHING_OPUS)) {
    if (model === getDefaultOpusModel()) return false
  }
  return true
}
```

这种分层控制的设计意图是：让用户可以在最贵的模型（Opus）上禁用缓存以换取最高的上下文新鲜度，同时在小模型（Haiku）上保留缓存以节省成本。

---

## 19.2 模型分层使用策略

### 19.2.1 三层模型架构

Claude Code 内部维护了三个模型层级（`src/utils/model/model.ts`），每个层级对应不同的能力和成本：

| 层级 | 模型示例 | 典型用途 | 成本级别 |
|------|---------|---------|---------|
| Haiku (最快/最便宜) | claude-3-haiku | 验证 API Key、快速查询 | $0.25/M 输入 |
| Sonnet (均衡) | claude-3-5-sonnet | 日常编码任务 | $3/M 输入 |
| Opus (最强/最贵) | claude-3-opus | 复杂架构决策 | $15/M 输入 |

`getSmallFastModel()` 函数（`src/utils/model/model.ts`）专门用于 API Key 验证等一次性轻量操作，避免为简单任务调用 Sonnet 产生不必要的费用。

### 19.2.2 自动模型降级

Claude Code 实现了自动降级机制，当检测到成本压力（如 overage）时，会自动切换到更便宜的模型。这一逻辑体现在 `currentLimits.isUsingOverage` 的检查中（`src/services/api/claude.ts` 第 410 行）：

```
let userEligible = getPromptCache1hEligible()
if (userEligible === null) {
  userEligible =
    process.env.USER_TYPE === 'ant' ||
    (isClaudeAISubscriber() && !currentLimits.isUsingOverage)
  setPromptCache1hEligible(userEligible)
}
```

当用户使用 overage（超额）计费时，系统自动禁用 1 小时 TTL 的缓存特权，从而避免额外的缓存创建成本。

### 19.2.3 Fast Mode 的成本优化

Fast Mode（`src/utils/fastMode.ts`）是一种特殊的成本优化机制，它在保持响应质量的前提下使用更小的 thinking budget。关键代码在 `claude.ts` 第 1398 行附近：

```
const isFastMode =
  isFastModeEnabled() &&
  isFastModeAvailable() &&
  !isFastModeCooldown() &&
  isFastModeSupportedByModel(options.model) &&
  !!options.fastMode

if (isFastModeForRetry) {
  speed = 'fast'
}
```

Fast Mode 的设计哲学是：**对于不需要深度推理的简单任务，用更少的 thinking token 换取更快的响应和更低的成本**。这是一个典型的"按需分配"策略。

### 19.2.4 Advisor Tool 的成本考量

Claude Code 支持在主模型之上叠加一个 Advisor 子模型（`src/utils/advisor.ts`），用于执行 server-side 工具调用。每次 Advisor 调用都会产生额外的 API 费用。`cost-tracker.ts` 第 304-320 行（`addToTotalSessionCost` 函数内）递归地累加了这部分成本：

```
// src/utils/cost-tracker.ts:304-320
for (const advisorUsage of getAdvisorUsage(usage)) {
  const advisorCost = calculateUSDCost(advisorUsage.model, advisorUsage)
  logEvent('tengu_advisor_tool_token_usage', { ... })
  totalCost += addToTotalSessionCost(advisorCost, advisorUsage, advisorUsage.model)
}
```

这一设计的成本含义是：**启用了 Advisor 的会话，成本可能比表面看到的更高**。开发者需要意识到这是一个叠加成本。

---

## 19.3 Token 消耗的可观测性

### 19.3.1 实时成本追踪

Claude Code 的 `cost-tracker.ts`（第 58 行起）提供了完整的成本追踪基础设施：

```
export function addToTotalModelUsage(
  cost: number,
  usage: Usage,
  model: string,
): ModelUsage {
  const modelUsage = getUsageForModel(model) ?? {
    inputTokens: 0, outputTokens: 0,
    cacheReadInputTokens: 0, cacheCreationInputTokens: 0,
    webSearchRequests: 0, costUSD: 0,
    contextWindow: 0, maxOutputTokens: 0,
  }
  // 累加各项指标
}
```

`addToTotalSessionCost` 函数（`cost-tracker.ts` 第 278 行）将每次 API 调用的成本累加到全局状态中，并通过 metrics counter 暴露给外部监控系统：

```
getCostCounter()?.add(cost, attrs)
getTokenCounter()?.add(usage.input_tokens, { ...attrs, type: 'input' })
getTokenCounter()?.add(usage.cache_read_input_tokens ?? 0, { ...attrs, type: 'cacheRead' })
getTokenCounter()?.add(usage.cache_creation_input_tokens ?? 0, { ...attrs, type: 'cacheCreation' })
```

这些 metrics 分别以 `input`、`output`、`cacheRead`、`cacheCreation` 标签打点，使得在 Prometheus/Grafana 中可以精确拆分每种 Token 类型的消耗趋势。

### 19.3.2 会话级成本持久化

Claude Code 支持将会话成本持久化到项目配置中（`saveCurrentSessionCosts` 函数，`cost-tracker.ts` 第 143 行），以便在切换会话后恢复成本数据：

```
export function saveCurrentSessionCosts(fpsMetrics?: FpsMetrics): void {
  saveCurrentProjectConfig(current => ({
    ...current,
    lastCost: getTotalCostUSD(),
    lastAPIDuration: getTotalAPIDuration(),
    lastModelUsage: Object.fromEntries(
      Object.entries(getModelUsage()).map(([model, usage]) => [model, { ...usage }])
    ),
    lastSessionId: getSessionId(),
  }))
}
```

这个设计对于**长期项目的成本审计**非常重要——每个会话结束后，成本数据被写入 `~/.claude/projects/` 配置目录，下次打开同一项目时可以查看历史成本趋势。

### 19.3.3 预算追踪器

Claude Code 提供了 `BudgetTracker`（`src/query/tokenBudget.ts` 第 45 行，`DIMINISHING_THRESHOLD` 和 `COMPLETION_THRESHOLD` 在第 3-4 行）来实现 Token 预算的自动监控。注意：`checkTokenBudget` **不在 `cost-tracker.ts` 中**，而在 `src/query/tokenBudget.ts` 中。

```
export function checkTokenBudget(
  tracker: BudgetTracker,
  agentId: string | undefined,
  budget: number | null,
  globalTurnTokens: number,
): TokenBudgetDecision {
  // 当消耗超过 COMPLETION_THRESHOLD (90%) 时提醒用户
  if (!isDiminishing && turnTokens < budget * COMPLETION_THRESHOLD) {
    tracker.continuationCount++
    return {
      action: 'continue',
      nudgeMessage: getBudgetContinuationMessage(pct, turnTokens, budget),
      continuationCount: tracker.continuationCount,
      pct,
      turnTokens,
      budget,
    }
  }
  // 当检测到边际收益递减（连续3次继续但Token增长 < 500）时停止
  const isDiminishing =
    tracker.continuationCount >= 3 &&
    deltaSinceLastCheck < DIMINISHING_THRESHOLD &&
    tracker.lastDeltaTokens < DIMINISHING_THRESHOLD
}
```

`DIMINISHING_THRESHOLD = 500` 是一个精心选择的阈值：它代表了"每次继续消耗不足 500 Token"就意味着模型正在做微小的重复性工作，此时继续下去的成本收益比已经恶化。

---

## 19.4 并行 Agent 的成本倍增风险

### 19.4.1 Agent 并行化的直观成本

Claude Code 支持通过 `AgentTool` 启动并行子 Agent（`src/tools/AgentTool/loadAgentsDir.ts`）。当多个 Agent 同时运行时，每个 Agent 都会独立地：

1. 发送自己的系统提示词（产生 cache creation tokens）
2. 维护自己的对话历史（独立的 input/output token 计数）
3. 可能调用不同的模型（如 Sonnet 处理前端，Opus 处理后端架构）

这意味着**并行度 N 的 Agent 会产生接近 N 倍的单 Agent 成本**，而非线性甚至亚线性增长。

### 19.4.2 子 Agent 的成本隔离问题

Claude Code 在 `options.agentId` 字段（`src/services/api/claude.ts` 第 436 行）中标识了子 Agent 的身份，但成本追踪是全局累加的：

```
if (!options.agentId) {
  headlessProfilerCheckpoint('api_request_sent')
}
```

即只有主 Agent（`agentId` 为 undefined）会触发 profiler checkpoint，子 Agent 的性能数据不会单独归类。这意味着如果需要精确分析每个并行 Agent 的成本，**需要额外的自定义 instrumentation**。

### 19.4.3 成本风险的缓解策略

针对并行 Agent 的成本倍增风险，建议采取以下策略：

**策略一：设置子 Agent Token 预算上限**
通过 `options.taskBudget` 参数（`src/services/api/claude.ts` 第 453 行）为每个子 Agent 设置 `output_config.task_budget`，让 API 端自己控制输出长度：

```
outputConfig.task_budget = {
  type: 'tokens',
  total: taskBudget.total,
  ...(taskBudget.remaining !== undefined && { remaining: taskBudget.remaining }),
}
```

**策略二：使用 Haiku 处理简单子任务**
对于文件搜索、格式转换等简单任务，明确指定使用 Haiku 模型：

```
agentOptions = {
  model: 'claude-3-haiku',  // 成本约为 Sonnet 的 1/12
  // ...
}
```

**策略三：限制并行度**
在 `agents` 配置中使用 `maxConcurrency` 参数（`src/tools/AgentTool/loadAgentsDir.ts`），避免过多的 Agent 同时运行：

```json
{
  "agents": [
    { "name": "frontend", "maxConcurrency": 2 },
    { "name": "backend", "maxConcurrency": 2 }
  ]
}
```

---

## 19.5 成本控制与性能的平衡

### 19.5.1 边际收益递减的自动检测

Claude Code 的 `checkTokenBudget` 函数（`src/query/tokenBudget.ts` 第 45 行）实现了一个优雅的"边际收益检测"机制：

```
const isDiminishing =
  tracker.continuationCount >= 3 &&
  deltaSinceLastCheck < DIMINISHING_THRESHOLD &&
  tracker.lastDeltaTokens < DIMINISHING_THRESHOLD

if (isDiminishing || tracker.continuationCount > 0) {
  return {
    action: 'stop',
    completionEvent: {
      diminishingReturns: isDiminishing,
      durationMs: Date.now() - tracker.startedAt,
      // ...
    },
  }
}
```

这个机制体现了**成本控制与性能的动态平衡**：系统不会简单地在某个 Token 阈值就停止，而是在检测到"继续投入时间/成本，但产出质量没有相应提升"时才停止。这是一个基于实际收益而非固定预算的停止策略。

### 19.5.2 模型选择的质量-成本 Pareto 最优

对于大多数编码任务，Sonnet 模型提供了最佳的成本-能力平衡点。Opus 的超高成本只在以下场景中合理：

- 复杂的架构设计决策
- 多文件重构中的依赖分析
- 涉及安全敏感代码的审查

Haiku 则适合：

- API Key 验证
- 单文件语法检查
- 简单格式转换

Claude Code 的默认模型配置（`getDefaultSonnetModel()`）正是基于这一 Pareto 分析做出的工程选择。

### 19.5.3 Streaming 与非 Streaming 的成本权衡

Claude Code 优先使用 streaming 模式（`src/services/api/claude.ts` 第 1020 行，streaming 主函数开头），因为 streaming 可以实现更快的首字节响应（TTFT），让用户更早看到部分结果。但 streaming 本身不节省成本——**成本由 Token 数量决定，与是否 streaming 无关**。

然而，Claude Code 实现了 streaming 失败时的自动降级到非 streaming（`executeNonStreamingRequest` 函数，`src/services/api/claude.ts` 第 818 行，`getNonstreamingFallbackTimeoutMs` 在第 807 行）：

```
const fallbackTimeoutMs = getNonstreamingFallbackTimeoutMs()
// 远程会话默认 120s，本地默认 300s
return isEnvTruthy(process.env.CLAUDE_CODE_REMOTE) ? 120_000 : 300_000
```

这个降级机制的意义在于：**避免因网络问题导致整个请求失败而浪费已消耗的 Token**。一个超时失败的 streaming 请求，其部分 Token 成本已经产生；如果能通过非 streaming 重试获得完整响应，整体成本反而更低。

### 19.5.4 缓存粒度的工程权衡

Claude Code 的 `addCacheBreakpoints` 函数只允许每个请求有一个 cache_control 标记，而不是每个消息一个。这是服务器端 KV Cache 架构的工程权衡：

- **优点**：避免缓存空间的碎片化，提高缓存命中率
- **缺点**：无法精确控制缓存的起止位置

源码注释揭示了这个决策背后的推理：

> With two markers the second-to-last position is protected and its locals survive an extra turn even though nothing will ever resume from there

这种"宁可少缓存，不要错误缓存"的哲学，体现了 Claude Code 在成本控制上偏向保守稳健的工程态度。

---

## 19.6 总结

Claude Code 的成本控制体系是一个多层次、相互关联的系统工程：

1. **Prompt Cache** 通过智能的缓存放置策略和缓存断裂检测，在保持上下文完整性的同时最大化缓存复用率。`DISABLE_PROMPT_CACHING_*` 环境变量提供了按模型细粒度控制的能力。

2. **模型分层** 通过 Haiku/Sonnet/Opus 三级架构，实现了"按需分配"的成本优化。Fast Mode 和 Advisor Tool 则提供了更细粒度的性能-成本调优旋钮。

3. **可观测性** 通过 `cost-tracker.ts` 中的实时追踪、metrics 暴露和会话持久化，让开发者能够精确了解每一次交互的成本构成。

4. **并行 Agent** 的成本倍增风险需要通过预算上限、模型指定和并发控制来主动管理。

5. **成本与性能的平衡** 体现在边际收益递减的自动检测、streaming 降级策略和缓存粒度权衡上——这些都是基于真实生产环境反馈迭代出来的工程决策。

理解这些机制，不仅能帮助开发者在使用 Claude Code 时做出更明智的决策，也能为构建其他 LLM 应用提供宝贵的成本控制范式。

---

# 第二十章：多 Agent 设计模式

## 概述

随着 AI Agent 系统规模的扩大，单一 Agent 的能力边界逐渐显现。多 Agent 设计通过将复杂任务分解为多个专业化 Agent 的协作，实现更高层次的智能系统。本章以 Claude Code 的 Swarm 架构为核心案例，深入剖析其设计原理、实现细节与工程权衡。

Claude Code 的多 Agent 系统（Swarm）是一个生产级别的实现，其源码位于 `src/utils/swarm/` 目录下，涵盖了从 Agent spawn 到进程内协作的完整链路。通过研究这一真实系统，读者可以掌握多 Agent 设计的核心范式，而不仅仅是抽象概念。

---

## 20.1 Agent 角色划分

### 什么是角色划分

角色划分（Role Assignment）是指将系统职责分配给不同类型的 Agent，使每个 Agent 专注于特定领域。良好的角色划分需要考虑：

- **职责单一性**：每个 Agent 有清晰定义的任务边界
- **能力匹配性**：Agent 类型与其承担职责相匹配
- **通信效率**：角色间的交互频率与复杂度可控

### Claude Code 的角色体系

Claude Code 定义了三种核心角色，每种角色在 `src/tasks/types.ts` 中有明确的状态类型区分：

| 角色 | 状态类型 | 说明 |
|------|----------|------|
| Team Lead（领队） | `LocalMainSessionTask`（`src/tasks/LocalMainSessionTask.ts` 第 55 行） | 主会话，负责协调与决策 |
| In-Process Teammate（进程内队友） | `InProcessTeammateTaskState`（`src/tasks/types.ts` 第 5, 17 行） | 与领队共享进程，轻量协作 |
| Remote Agent（远程 Agent） | `RemoteAgentTaskState`（`src/tasks/types.ts` 第 7, 17 行） | 独立进程，隔离执行 |

领队是整个系统的中枢。在 `src/coordinator/coordinatorMode.ts` 中，通过 `TEAM_CREATE_TOOL_NAME`、`SEND_MESSAGE_TOOL_NAME` 等工具集来管理团队：

```
// src/coordinator/coordinatorMode.ts, 行 29-33
const INTERNAL_WORKER_TOOLS = new Set([
  TEAM_CREATE_TOOL_NAME,
  TEAM_DELETE_TOOL_NAME,
  SEND_MESSAGE_TOOL_NAME,
  SYNTHETIC_OUTPUT_TOOL_NAME,
])
```

这些工具仅对领队开放，worker Agent 无法直接操作团队生命周期。

### 角色标识机制

每个 Agent 拥有唯一标识，格式为 `name@teamName`（在 `src/utils/agentId.ts` 的 `formatAgentId` 函数中定义）。角色身份信息封装在 `TeammateIdentity` 类型中：

```
// src/tasks/InProcessTeammateTask/types.ts, 行 13-26
export type TeammateIdentity = {
  agentId: string          // 例如 "researcher@my-team"
  agentName: string       // 例如 "researcher"
  teamName: string
  color?: string          // UI 中的颜色标识
  planModeRequired: boolean
  parentSessionId: string // 领队的会话 ID
}
```

颜色标识是 Claude Code 的一大设计亮点——每个队友在 UI 中以不同颜色显示（如红色、蓝色、绿色），便于用户在 swarm view 中快速识别消息来源。

### 设计原因

角色划分的根本原因在于**控制复杂度**。如果不划分角色，所有 Agent 可以相互通信、任意操作，导致通信拓扑爆炸（O(n²) 条通信路径）。通过引入领队模式，系统只需要：

- 领队 ↔ 每个 Worker：O(n) 条通信路径
- Worker 之间：通过领队中转

这在 `src/utils/swarm/teamHelpers.ts` 的 `TeamFile` 类型中得到体现——member 的 `subscriptions` 字段记录了该 Agent 订阅的消息类型，实现了一种受控的信息流。

---

## 20.2 通信协议设计

### 消息传递模型

Claude Code 采用**基于邮箱的文件消息队列**（File-based Mailbox）作为进程间通信机制。这不是 Redis 或 MQ，而是一套基于文件锁的轻量实现。

核心类型定义在 `src/utils/teammateMailbox.ts`：

```
// src/utils/teammateMailbox.ts, 行 43-50
export type TeammateMessage = {
  from: string
  text: string
  timestamp: string
  read: boolean
  color?: string
  summary?: string  // 5-10 词摘要，用于 UI 预览
}
```

邮箱文件路径结构为：`~/.claude/teams/{team_name}/inboxes/{agent_name}.json`。

### 锁机制

写消息时使用 `lockfile` 库进行文件锁保护，确保多进程并发写入的安全性：

```
// src/utils/teammateMailbox.ts, 行 42-49
const LOCK_OPTIONS = {
  retries: {
    retries: 10,
    minTimeout: 5,
    maxTimeout: 100,
  },
}
```

这种设计选择了**乐观锁**（重试）而非**悲观锁**（阻塞），是因为在 AI Agent 场景下，偶尔的写入冲突可以通过重试解决，而阻塞整个事件循环是不可接受的。

### 邮件操作原语

Mailbox 类（`src/utils/mailbox.ts`）提供了三个核心原语：

```
// src/utils/mailbox.ts（分别标注）: send（第 33 行）、poll（第 48 行）、receive（第 54 行）
send(msg: Message): void {
  this._revision++
  const idx = this.waiters.findIndex(w => w.fn(msg))
  if (idx !== -1) {
    // 匹配到等待者，直接 resolve
    const waiter = this.waiters.splice(idx, 1)[0]
    waiter.resolve(msg)
    this.notify()
    return
  }
  // 否则入队
  this.queue.push(msg)
  this.notify()
}

poll(fn: (msg: Message) => boolean = () => true): Message | undefined {
  // 遍历查找匹配消息并出队（非阻塞）
}

receive(fn: (msg: Message) => boolean = () => true): Promise<Message> {
  // 如果队列中有匹配消息，立即返回；否则注册 waiter 等待
}
```

这是典型的**生产者-消费者**模式。`send` 是生产者，`poll` 和 `receive` 是两种不同的消费者语义：

- `poll`：主动轮询，适用于不等待的场景
- `receive`：异步等待，适用于需要阻塞等待回复的场景

### 进程内邮箱桥接

对于 in-process teammate，Claude Code 提供了 `useMailboxBridge` hook（`src/hooks/useMailboxBridge.ts`），将文件邮箱桥接到 React 的状态流：

```
// src/hooks/useMailboxBridge.ts, 行 11-22
export function useMailboxBridge({ isLoading, onSubmitMessage }: Props): void {
  const mailbox = useMailbox()

  useEffect(() => {
    if (isLoading) return
    const msg = mailbox.poll()
    if (msg) onSubmitMessage(msg.content)
  }, [isLoading, revision, mailbox, onSubmitMessage])
}
```

每当 Mailbox revision 变化（通过 `useSyncExternalStore` 订阅），hook 自动 poll 消息并提交给 Agent 处理循环。

### 通信协议设计原因

Claude Code 选择文件邮箱而非 WebSocket 或 gRPC，核心原因有三点：

1. **持久化**：消息不丢失，Agent 重启后可恢复
2. **简单性**：无需额外的消息服务依赖，文件系统是通用接口
3. **调试友好**：邮箱文件是纯 JSON，人工检查和调试非常方便

代价是延迟较高（毫秒级 vs 微秒级），但在 Agent 思考时间（秒级）的背景下，这个开销可以忽略。

---

## 20.3 协作模式

### 星型模式（Star Topology）

星型模式是 Claude Code 的**默认协作模式**，由 Team Lead 作为中心节点，所有通信必须经过领队。

```
        Team Lead
       /    |    \
    Worker1 Worker2 Worker3
```

**适用场景**：需要集中管控的复杂任务，如需要用户审批的代码生成流程。

在 `src/utils/swarm/spawnInProcess.ts` 中可以清晰看到 spawn 逻辑只涉及领队与新 Agent 的双方关系，不存在 Worker 之间的直接通道：

```
// src/utils/swarm/spawnInProcess.ts, 行 59-79
export type InProcessSpawnConfig = {
  name: string           // 队友显示名
  teamName: string
  prompt: string         // 初始任务
  color?: string
  planModeRequired: boolean
  model?: string
}
```

### 环形模式（Ring Topology）

环形模式指 Agent 形成链式结构，每个 Agent 只能与其相邻节点通信。在 Claude Code 中，这一模式通过 `sendMessage` 工具的 `to` 参数实现路由约束。

当领队向特定 Agent 发消息，且该消息需要继续传递时，可以形成逻辑上的环。例如：

```
User → Lead → AgentA → AgentB → Lead
```

不过 Claude Code 的源码中，环形模式**并非一等公民**，更多是作为星型模式的扩展出现。

### 网状模式（Mesh Topology）

网状模式指 Agent 之间可以任意通信，无需通过领队中转。Claude Code 通过**广播消息**支持这一模式：

```
// src/utils/teammateMailbox.ts（SendMessageTool 输入 schema）
inputSchema = lazySchema(() =>
  z.object({
    to: z.string().describe(
      'Recipient: teammate name, "*" for broadcast...'
    ),
    message: ...
  })
)
```

当 `to = "*"` 时，消息会写入所有队友的邮箱，实现真正的广播。

### 协作模式的切换

Claude Code 没有显式的"模式切换"API，模式由通信行为隐式决定：

- 点对点消息 → 逻辑星型或环型
- 广播消息 → 网状
- 实际上大多数场景是星型（因为 worker 之间若需要通信，通常通过领队协调）

---

## 20.4 冲突解决机制

多 Agent 系统中，冲突无处不在——两个 Agent 可能同时编辑同一个文件，或者对同一个问题给出不同答案。Claude Code 实现了多层次的冲突解决机制。

### 层级一：权限过滤（Permission Filtering）

最底层的冲突预防。Worker Agent 的工具使用权限由领队代理，只有领队可以执行高风险操作：

```
// src/utils/swarm/permissionSync.ts, 行 1-25
/**
 * 当 worker 需要权限时：
 * 1. Worker 发送 permission_request 到领队邮箱
 * 2. 领队检测并向用户展示审批对话框
 * 3. 用户审批后，领队发送 permission_response 到 worker 邮箱
 * 4. Worker 继续执行
 */
```

领队权限桥（`src/utils/swarm/leaderPermissionBridge.ts`）允许 REPL 注册确认队列，使 in-process teammate 可以复用领队的权限确认 UI：

```
// src/utils/swarm/leaderPermissionBridge.ts, 行 28-34
export function registerLeaderToolUseConfirmQueue(
  setter: SetToolUseConfirmQueueFn,
): void {
  registeredSetter = setter
}
```

### 层级二：计划模式（Plan Mode）

当 `planModeRequired = true` 时，Agent 不能直接实现（写文件），必须先输出计划并等待批准：

```
// src/tasks/InProcessTeammateTask/types.ts, 行 38
awaitingPlanApproval: boolean
```

Plan approval 消息通过结构化消息类型传递：

```
// src/tools/SendMessageTool/SendMessageTool.ts, 行 46-85
const StructuredMessage = lazySchema(() =>
  z.discriminatedUnion('type', [
    z.object({
      type: z.literal('plan_approval_response'),
      request_id: z.string(),
      approve: semanticBoolean(),
      feedback: z.string().optional(),
    }),
    // ...
  ])
)
```

### 层级三：文件锁与路径隔离

最直接的冲突解决——当多个 Agent 需要编辑文件时，Claude Code 使用底层的文件系统锁。但更优雅的方案是**工作树隔离**（Worktree Path）：

```
// src/utils/swarm/teamHelpers.ts, 行 83（worktreePath 字段位于 TeamFile.members 数组元素中）
members: Array<{
  // ...
  worktreePath?: string  // 每个 Agent 独立工作目录
}>
```

通过 Git worktree，每个 Agent 在独立的目录中工作，彻底消除了文件编辑冲突。

### 层级四：领队仲裁

当 Agent 之间产生无法自动解决的冲突时，领队作为最终仲裁者。用户通过领队的对话界面做出决策：

```
// src/tools/SendMessageTool/SendMessageTool.ts, 行 133-148
function findTeammateColor(
  appState: {
    teamContext?: { teammates: { [id: string]: { color?: string } } }
  },
  name: string,
): string | undefined {
  const teammates = appState.teamContext?.teammates
  if (!teammates) return undefined
  for (const teammate of Object.values(teammates)) {
    if ('name' in teammate && (teammate as { name: string }).name === name) {
      return teammate.color
    }
  }
  return undefined
}
```

### 冲突解决的设计哲学

Claude Code 的冲突解决遵循**保守主义原则**：默认阻止，允许例外。具体体现为：

1. **Plan Mode Required**：高风险操作必须经过人工审批
2. **Permission Bridge**：所有危险操作需要领队代理
3. **Worktree Isolation**：结构上消除文件冲突
4. **Leader Override**：最终由人类用户仲裁

这套设计将"冲突"从"同时发生的竞争"转化为"有序的审批流程"，代价是效率略有下降，但换取了可靠性。

---

## 20.5 实操：创建一个多 Agent 团队

以下示例展示如何使用 Claude Code 的 Swarm API 创建一个三人团队：

```
import { TOOL_NAME as TEAM_CREATE } from './TeamCreateTool/constants.js'
import { TOOL_NAME as AGENT } from './AgentTool/constants.js'
import { TOOL_NAME as SEND_MESSAGE } from './SendMessageTool/constants.js'

// 第一步：创建团队
await tool(TEAM_CREATE, {
  operation: 'spawnTeam',
  agent_type: 'coordinator',
  team_name: 'research-squad',
  description: '一个研究小队，负责信息搜集与报告撰写'
})

// 第二步：Spawn 研究员（in-process）
await tool(AGENT, {
  name: 'researcher',
  prompt: '你是一名专业研究员。请搜集关于 AI Agent 最新进展的信息，整理成结构化报告。',
  agentType: 'researcher',
  planModeRequired: false,
})

// 第三步：Spawn 审计员（独立进程）
await tool(AGENT, {
  name: 'auditor',
  prompt: '你是代码审计专家。研究员的报告完成后，你需要审查其中的技术准确性。',
  agentType: 'auditor',
  backend: 'tmux',  // 使用独立进程
  planModeRequired: true,  // 必须计划后实施
})

// 第四步：领队向研究员发送任务
await tool(SEND_MESSAGE, {
  to: 'researcher',
  summary: '启动研究报告任务',
  message: '请开始搜集 AI Agent 的最新进展，范围限定在 2024-2025 年。',
})

// 第五步：监听审计员反馈（广播模式）
// 审计员完成审查后，领队会收到通知
```

---

## 20.6 工程权衡与最佳实践

### 为什么 Claude Code 选择进程内 + 进程外的混合模型？

Claude Code 同时支持 in-process teammate 和 tmux pane-based teammate，这是经过权衡的：

| 特性 | In-Process | Pane-Based (tmux) |
|------|-----------|-------------------|
| 隔离性 | 低（共享内存） | 高（独立进程） |
| 资源消耗 | 低 | 高 |
| 通信延迟 | 极低 | 毫秒级 |
| 故障影响 | 一个崩溃可能影响所有 | 单个崩溃不影响其他 |
| 适用场景 | 轻量协作、快速迭代 | 危险操作、需要强隔离 |

在 `src/utils/swarm/backends/InProcessBackend.ts` 中，in-process backend 通过 `AsyncLocalStorage` 实现上下文隔离，是 Node.js 标准的 Zone 模式：

```
// src/utils/swarm/inProcessRunner.ts, 行 5-9
// AsyncLocalStorage-based context isolation via runWithTeammateContext()
```

### 最佳实践

1. **优先使用 In-Process**：对于不需要强隔离的协作任务，使用 in-process teammate 可降低资源消耗
2. **Plan Mode 不可绕过**：涉及文件写入的操作必须开启 plan mode，避免不可控的代码变更
3. **颜色编码要分配**：为每个队友分配独特颜色，在 swarm view 中可以直观区分消息来源
4. **使用 Worktree**：对于需要同时编辑代码的场景，使用 Git worktree 隔离工作目录
5. **邮箱要清理**：长期运行的 swarm 会产生大量邮箱文件，应在任务结束后调用 team cleanup

---

## 20.7 小结

本章通过 Claude Code 的 Swarm 架构，系统讲解了多 Agent 设计模式的四大核心要素：

1. **角色划分**：通过 Team Lead + Worker 的分层结构，实现职责分离与集中管控
2. **通信协议**：基于文件邮箱的消息队列，提供持久化、调试友好且足够高效的通信机制
3. **协作模式**：星型（默认）、环形、网状三种模式由通信行为隐式决定，灵活适应不同场景
4. **冲突解决**：从权限过滤、计划审批、路径隔离到领队仲裁，构建了多层防御体系

多 Agent 设计不是银弹。它带来的复杂性（状态管理、通信延迟、冲突概率）需要通过良好的架构来控制。Claude Code 的 Swarm 架构证明，只要设计得当，多 Agent 系统可以在保持可控性的同时，实现超越单一 Agent 的复杂任务处理能力。
---

> **🧭 深入源码**
>
> 想深入研究 Swarm 架构的生产级实现？请参考：
> - `src/utils/swarm/backends/InProcessBackend.ts` — 后端抽象
> - `src/utils/swarm/permissionSync.ts` — 权限同步协议
> - `src/utils/swarm/leaderPermissionBridge.ts` — 领队权限桥
> - `src/utils/teammateMailbox.ts` — 文件邮箱与锁机制

*** [Claude Code 教科书·送审稿·全文完] ***

# 附录 A：术语表

> 本术语表收录 Claude Code 教科书中出现的关键术语，按章节排序，每个术语包含简短定义与首次出现的章节编号。

---

## 第一章　产品哲学与定位

| 术语 | 定义 | 章节 |
|------|------|------|
| **Claude Code** | Anthropic 官方推出的命令行界面（CLI）工具，让开发者通过终端与 Claude 大模型交互，完成软件工程任务 | 第1章 |
| **CLI** | Command-Line Interface，命令行界面，Claude Code 的核心交互形态 | 第1章 |
| **Bun** | JavaScript/TypeScript 运行时与 bundler，Claude Code 的默认运行环境 | 第1章 |
| **TypeScript** | 带类型的 JavaScript 超集，提供编译时类型检查与 IDE 自动补全 | 第1章 |
| **React + Ink** | Ink 是"React for CLIs"，允许用 React 组件模型构建终端 UI | 第1章 |
| **Commander.js** | 企业级 CLI 参数解析库，Claude Code 用于解析命令行选项 | 第1章 |
| **Zod** | TypeScript 优先的配置验证库，Claude Code 用于 schema 定义和运行时校验 | 第1章 |
| **Tool-call loop** | 工具调用循环，QueryEngine 核心机制：模型返回 tool_use → 执行工具 → 结果注入下一轮对话 | 第1章 |
| **System prompt** | 系统提示词，定义 AI 模型行为边界的指令文本，随每个 API 请求发送 | 第1章 |
| **MCP / Model Context Protocol** | 标准化协议，允许 Claude Code 连接外部工具服务器和数据源 | 第1章 |
| **Grounding** | 接地，将模型输出锚定到真实系统状态（如文件存在性、命令执行结果） | 第1章 |
| **Skill 系统** | Claude Code 的可复用工作流机制，允许用户定义自定义任务模板 | 第1章 |
| **Buddy 系统** | 电子宠物伴侣系统，为用户提供情感连接的拟人化界面（详见第3章） | 第1章 |
| **Feature Flag** | 特性开关，通过编译时常量控制功能分支，支持 A/B 测试 | 第1章 |
| **Slash Command** | 以 `/` 开头的命令（如 `/review`、`/compact`），快速触发特定功能 | 第1章 |

---

# 附录 B：源码索引表

> 本索引表整理 Claude Code 教科书各章节引用的关键源码文件，按章节排序。每条记录包含：文件路径（相对于 `src/`）、行号范围、对应章节、作用说明。

---

## 第一章　产品哲学与定位

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `main.tsx` | L1–20 | 第1章 | 预加载区：MDM + Keychain 并行预取（~135ms 导入期间重叠 I/O） |
| `main.tsx` | L76–91 | 第1章 | Feature flag 条件导入（COORDINATOR_MODE、KAIROS 等） |
| `main.tsx` | L585 | 第1章 | main() 入口函数，包含 Windows PATH 劫持防御 |
| `main.tsx` | L1747–1753 | 第1章 | 工具权限上下文初始化（initializeToolPermissionContext） |
| `main.tsx` | L2408–2412 | 第1章 | MCP 资源预取（非阻塞，REPL 首帧渲染后可连接） |
| `main.tsx` | L2437 | 第1章 | SessionStart Hook 触发逻辑 |
| `QueryEngine.ts` | 全文~1295行 | 第1章 | 核心引擎：API 流式通信、工具调用循环、思考模式、上下文压缩 |
| `constants/system.ts` | L9–11 | 第1章 | 系统提示词前缀定义（DEFAULT_PREFIX、AGENT_SDK_PREFIX） |
| `context.ts` | — | 第1章 | 系统上下文构建（Git 仓库状态、分支信息、worktree 数量等） |
| `hooks/toolPermission/` | 目录 | 第1章 | 细粒度权限控制系统，每工具调用都经过权限检查 |

---

## 第二章　设计哲学与原则

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `utils/debug.ts` | 全文 | 第2章 | isDebugMode() 调试判断、logForDebugging 分级日志、BufferedWriter |
| `utils/startupProfiler.ts` | 全文 | 第2章 | profileCheckpoint 启动性能打点、profileReport 性能报告生成 |
| `utils/cliArgs.ts` | L12–40 | 第2章 | eagerParseCliFlag() 抢先参数解析，支持 --flag=value 和 --flag value 两种语法 |
| `main.tsx` | L76–91 | 第2章 | feature() 条件导入实现 dead code elimination |
| `main.tsx` | L432–488 | 第2章 | loadSettingsFromFlag() 内联 JSON 解析，零额外抽象 |
| `main.tsx` | L502–518 | 第2章 | eagerLoadSettings() 在 init() 前提前处理 --settings 参数 |
| `main.tsx` | L585–600 | 第2章 | main() 函数，NoDefaultCurrentDirectoryInExePath 安全加固 |

---

## 第三章　人机关系与 Buddy 设计

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `buddy/companion.ts` | L16–25 | 第3章 | mulberry32() 确定性伪随机数生成器（给定种子完全可重现） |
| `buddy/companion.ts` | L43–51 | 第3章 | rollRarity() 加权稀有度抽取（Common 60%→Legendary 1%） |
| `buddy/companion.ts` | L53–59 | 第3章 | RARITY_FLOOR 稀有度最低属性门槛定义 |
| `buddy/companion.ts` | L61–82 | 第3章 | rollStats() 统计属性生成（峰值+低谷+随机分布） |
| `buddy/companion.ts` | L84 | 第3章 | SALT 常量（'friend-2026-401'），防止逆向工程 |
| `buddy/companion.ts` | L91–102 | 第3章 | rollFrom() 生成完整 Buddy 骨骼（species/eye/hat/shiny/stats） |
| `buddy/companion.ts` | L104–113 | 第3章 | roll() 函数 + rollCache 缓存，三个热路径优化（500ms tick/keystroke/turn） |
| `buddy/companion.ts` | L119–122 | 第3章 | companionUserId() 从全局配置获取用户 ID（OAuth UUID / userID / 'anon'） |
| `buddy/companion.ts` | L127–133 | 第3章 | getCompanion() 骨骼覆盖逻辑（bones last 确保哈希优先于陈旧配置） |
| `buddy/types.ts` | L14–19 | 第3章 | 物种名 String.fromCharCode 编码（反作弊，名称不出现在构建产物中） |
| `buddy/types.ts` | L100–108 | 第3章 | CompanionBones（骨骼，哈希确定性）和 CompanionSoul（灵魂，模型生成）类型定义 |
| `buddy/types.ts` | L126–132 | 第3章 | RARITY_WEIGHTS 稀有度权重常量 |
| `buddy/prompt.ts` | L8–12 | 第3章 | companionIntroText Buddy 提示词模板，ONE line 约束 |
| `buddy/prompt.ts` | L20 | 第3章 | companionMuted 静音判断 |
| `buddy/prompt.ts` | L22–27 | 第3章 | 避免 Buddy 重复自我介绍的过滤逻辑 |

---

## 第四章　系统架构全貌

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `state/AppStateStore.ts` | L14–36 | 第4章 | createStore() 发布订阅状态容器，Immutable 更新 + 取消订阅返回函数 |
| `state/AppStateStore.ts` | L81–150 | 第4章 | AppState 接口定义（MCP/工具权限/推理/通知等全局状态） |
| `state/AppStateStore.ts` | — | 第4章 | onChangeAppState() 状态变更回调，检测 MCP/权限/压缩条件 |
| `entrypoints/init.ts` | L44–67 | 第4章 | init() 核心初始化函数（enableConfigs/env/settings/shutdown） |
| `tools/BashTool/` | 目录 | 第4章 | BashTool 沙箱机制（shouldUseSandbox） |
| `services/remoteManagedSettings/index.ts` | — | 第4章 | loadRemoteManagedSettings() 企业云端托管设置加载 |
| `utils/teleport.ts` | — | 第4章 | 跨设备状态同步（Teleport 远程会话） |
| `utils/sessionStorage.ts` | — | 第4章 | 会话持久化（本地存储历史） |
| `services/mcp/config.ts` | — | 第4章 | getClaudeCodeMcpConfigs() MCP 多来源配置合并 |
| `services/mcp/client.ts` | L60–80 | 第4章 | MCP 传输方式映射（stdio/SSE/streamable-http） |

---

## 第五章　入口设计与短路径

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `main.tsx` | L579 | 第5章 | main() 入口 |
| `main.tsx` | L604–645 | 第5章 | Deep link（cc:// / cc+unix://）URL 拦截与重写 |
| `main.tsx` | L704–797 | 第5章 | SSH / Assistant 子命令剥离 |
| `main.tsx` | L797–803 | 第5章 | isNonInteractive 早期模式检测 |
| `main.tsx` | L854–906 | 第5章 | run() Commander.js 初始化 |
| `main.tsx` | L907–960 | 第5章 | preAction hook（等待 MDM+Keychain → init → runMigrations → 非阻塞远程设置） |
| `main.tsx` | L968–1010 | 第5章 | Commander 选项注册（60+ 选项：-p/--continue/-r/--bare/--settings 等） |
| `main.tsx` | L1782–2829 | 第5章 | 非交互模式路径（runHeadless + headlessStore + connectMcpBatch） |
| `main.tsx` | L3582–3686 | 第5章 | --continue / --resume 会话恢复处理分支 |
| `main.tsx` | L388–410 | 第5章 | startDeferredPrefetches() 首帧渲染后延迟预取 |
| `utils/sessionRestore.ts` | — | 第5章 | --continue 会话恢复逻辑 |
| `utils/conversationRecovery.ts` | — | 第5章 | --resume 会话恢复（支持 UUID 精确和模糊搜索） |
| `cli/dialogLaunchers.ts` | — | 第5章 | launchResumeChooser 交互式会话选择器 |

---

## 第六章　技术栈选型

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `main.tsx` | L21 | 第6章 | import { feature } from 'bun:bundle'，使用 Bun bundler feature() 函数 |
| `main.tsx` | L196 | 第6章 | import { isRunningWithBun } from './utils/bundledMode.js' |
| `main.tsx` | L325 | 第6章 | CURRENT_MIGRATION_VERSION = 11，迁移版本常量 |
| `main.tsx` | L266 | 第6章 | isBeingDebugged() 调试检测，调试模式下进程退出防止信息泄露 |
| `main.tsx` | L25–27 | 第6章 | lodash-es 命名导入（mapValues/pickBy/uniqBy），支持 Tree Shaking |
| `utils/bundledMode.js` | 全文 | 第6章 | isRunningWithBun() Bun 运行时检测 |

---

## 第七章　工具系统架构

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `Tool.ts` | L362–440 | 第7章 | Tool 接口定义核心（泛型 Input/Output/P，name/inputSchema/call/description 等） |
| `Tool.ts` | L707–720 | 第7章 | DefaultableToolKeys 类型，哪些字段在 buildTool 中可默认实现 |
| `Tool.ts` | L721–756 | 第7章 | ToolDef 类型约束，继承 Tool 但将 DefaultableToolKeys 字段标记为可选 |
| `Tool.ts` | L757–782 | 第7章 | TOOL_DEFAULTS 默认方法（fail-closed 安全默认值） |
| `Tool.ts` | L783 | 第7章 | buildTool 工厂函数，将 TOOL_DEFAULTS 与用户定义合并 |
| `Tool.ts` | L321 | 第7章 | ToolResult 类型（data/newMessages/contextModifier/mcpMeta） |
| `Tool.ts` | L158 | 第7章 | ToolUseContext 类型，工具执行时的依赖注入上下文 |
| `Tool.ts` | L489–495 | 第7章 | validateInput 方法签名 |
| `Tool.ts` | L500–518 | 第7章 | checkPermissions 方法签名 |
| `utils/lazySchema.ts` | 全文 | 第7章 | lazySchema 工厂函数，返回记忆化的 Zod schema getter |
| `tools.ts` | L193 | 第7章 | getAllBaseTools() 完整工具列表（AgentTool/BashTool/FileReadTool 等） |
| `tools.ts` | L262 | 第7章 | filterToolsByDenyRules() 按权限规则过滤工具 |
| `tools.ts` | L345 | 第7章 | assembleToolPool() 合并内置工具与 MCP 工具（内置优先、去重、排序） |
| `tools/BashTool/BashTool.tsx` | L227 | 第7章 | BashTool inputSchema lazySchema 定义 |
| `tools/BashTool/BashTool.tsx` | L254 | 第7章 | BashTool 条件化 schema（isBackgroundTasksDisabled 时剔除字段） |
| `tools/AgentTool/AgentTool.tsx` | L88–113 | 第7章 | AgentTool baseInputSchema / fullInputSchema lazySchema 定义 |
| `types/permissions.ts` | L172–265 | 第7章 | PermissionResult 四种决策类型（allow/ask/deny/passthrough） |

---

## 第八章　安全权限体系

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `utils/permissions/permissions.ts` | hasPermissionsToUseToolInner | 第8章 | 权限检查主入口，四层防御管道协调 |
| `utils/permissions/permissions.ts` | L593+ | 第8章 | acceptEdits fast-path 快速放行 |
| `utils/permissions/permissions.ts` | L659+ | 第8章 | safe-tool allowlist 检查 |
| `utils/permissions/permissions.ts` | L688+ | 第8章 | Haiku 分类器 API 调用 |
| `utils/permissions/permissions.ts` | L822+ | 第8章 | transcriptTooLong 回退 |
| `utils/permissions/permissions.ts` | L844+ | 第8章 | iron_gate 安全闸门 |
| `utils/permissions/permissions.ts` | L890+ | 第8章 | denialLimitExceeded 拒绝次数超限 |
| `bashSecurity.ts` | L50–72 | 第8章 | BASH_SECURITY_CHECK_IDS 23 种安全检查 ID 常量 |
| `bashSecurity.ts` | L9–47 | 第8章 | COMMAND_SUBSTITUTION_PATTERNS 13 种危险替换模式 |
| `bashSecurity.ts` | L1534–1620 | 第8章 | validateBackslashEscapedOperators 反斜杠转义操作符攻击检测 |
| `bashSecurity.ts` | L2076–2130 | 第8章 | validateQuotedNewline 引号内换行符攻击检测 |
| `bashSecurity.ts` | L2320–2362 | 第8章 | validateZshDangerousCommands Zsh 危险命令检测 |
| `bashSecurity.ts` | L177–188 | 第8章 | SECURITY 注释：validateRedirections 正则边界注释（> /dev/nullo 漏洞） |
| `bashPermissions.ts` | L290–393 | 第8章 | SAFE_ENV_VARS 安全环境变量白名单 |
| `bashPermissions.ts` | L434–499 | 第8章 | ANT_ONLY_SAFE_ENV_VARS 仅内部版本白名单 |
| `bashPermissions.ts` | L760–830 | 第8章 | stripSafeWrappers 安全命令包装器剥离（timeout/nice/stdbuf/nohup） |
| `bashPermissions.ts` | L95–106 | 第8章 | MAX_SUBCOMMANDS_FOR_SECURITY_CHECK = 50 复合命令上限 |
| `bashPermissions.ts` | bashToolHasPermission | 第8章 | Bash 权限检查主函数，完整 23 种检查管道 |
| `utils/undercover.ts` | L28–37 | 第8章 | isUndercover() 检测 + getUndercoverInstructions() 隐藏指令 |
| `readOnlyCommandValidation.ts` | L20–35 | 第8章 | FlagArgType 枚举（none/number/string/char/{}/EOF 六种类型） |
| `readOnlyCommandValidation.ts` | L44–100 | 第8章 | GIT_REF_SELECTION_FLAGS / GIT_STAT_FLAGS 等 git 只读 flag 白名单 |
| `readOnlyCommandValidation.ts` | L107–175 | 第8章 | GIT_READ_ONLY_COMMANDS 只读 git 命令配置（pickaxe -S/-G/-O 修正） |
| `readOnlyCommandValidation.ts` | L1546–1628 | 第8章 | containsVulnerableUncPath Windows UNC 路径漏洞检测 |

---

## 第九章　上下文管理与缓存

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `constants/systemPromptSections.ts` | L17–21 | 第9章 | systemPromptSection 创建可缓存提示节（cacheBreak=false） |
| `constants/systemPromptSections.ts` | L25–33 | 第9章 | DANGEROUS_uncachedSystemPromptSection 强制禁用缓存节 |
| `constants/systemPromptSections.ts` | L34–48 | 第9章 | resolveSystemPromptSections 并行计算各节并缓存结果 |
| `constants/systemPromptSections.ts` | L54–58 | 第9章 | clearSystemPromptSections 清理缓存 + 重置 Beta Header 锁存器 |
| `services/compact/compact.ts` | L243 | 第9章 | truncateHeadForPTLRetry PTL 降级逃生舱口 |
| `services/compact/compact.ts` | L387–670 | 第9章 | compactConversation 全量压缩主函数（400+ 行） |
| `services/compact/compact.ts` | L325–340 | 第9章 | 部分压缩消息分组方向处理（up_to / from） |
| `services/compact/compact.ts` | L521 | 第9章 | 压缩后清理 readFileState 和 loadedNestedMemoryPaths |
| `services/compact/compact.ts` | L598 | 第9章 | createCompactBoundaryMessage 创建压缩边界标记（携带工具发现状态） |
| `services/compact/compact.ts` | L637 | 第9章 | truePostCompactTokenCount 压缩后实际 token 计数 |
| `services/compact/compact.ts` | L699 | 第9章 | notifyCompaction 通知服务端缓存基线重置（PROMPT_CACHE_BREAK_DETECTION） |
| `services/compact/compact.ts` | L772 | 第9章 | partialCompactConversation 部分压缩函数 |
| `services/compact/compact.ts` | L1188 | 第9章 | fork 缓存共享压缩请求（runForkedAgent + skipCacheWrite=true） |
| `services/compact/compact.ts` | L1293 | 第9章 | normalizeMessagesForAPI 消息规范化（stripImages + stripReinjectedAttachments） |
| `services/compact/compact.ts` | L1415–1480 | 第9章 | createPostCompactFileAttachments 压缩后文件附件恢复 |
| `services/compact/grouping.ts` | L1–25 | 第9章 | groupMessagesByApiRound 按 message.id 切分 API 轮次原子单元 |
| `services/compact/compact.ts` | L211 | 第9章 | stripReinjectedAttachments 过滤 skill_discovery/skill_listing 附件 |

---

## 第十章　记忆系统

| 文件 | 行数 | 对应章节 | 作用说明 |
|------|------|----------|----------|
| `memdir/memdir.ts` | L33 | 第10章 | MAX_ENTRYPOINT_LINES = 200 索引文件最大行数 |
| `memdir/memdir.ts` | L38 | 第10章 | MAX_ENTRYPOINT_BYTES = 25_000 索引文件最大字节数 |
| `memdir/memdir.ts` | L52–88 | 第10章 | 索引截断策略（优先行数，再尊重字节数） |
| `memdir/memdir.ts` | L159–175 | 第10章 | 记忆两步保存流程（先写 .md 文件，再更新 MEMORY.md 索引） |
| `memdir/memdir.ts` | L210–245 | 第10章 | 每日日志模式（按日期追加，会话结束时蒸馏） |
| `memdir/memdir.ts` | L250–310 | 第10章 | loadMemoryPrompt 将 MEMORY.md 注入系统提示词 |
| `memdir/memoryTypes.ts` | L14 | 第10章 | MEMORY_TYPES 四型常量（user/feedback/project/reference） |
| `memdir/memoryTypes.ts` | L45/59/77/92 | 第10章 | 各类型 scope 定义（user: private / project: team 优先等） |
| `memdir/memoryTypes.ts` | L180–185 | 第10章 | 记忆文件 **Why:** 和 **How to apply:** 结构化字段格式 |
| `memdir/memoryTypes.ts` | L214–222 | 第10章 | 记忆召回验证要求（"使用前先 grep 确认文件/函数/标志存在"） |
| `memdir/memoryTypes.ts` | L259 | 第10章 | 记忆文件 frontmatter 格式规范 |
| `memdir/paths.ts` | L79–86 | 第10章 | 记忆目录物理布局（MEMORY.md + 类型子文件 + team/ 子目录） |
| `memdir/teamMemPaths.ts` | L84 | 第10章 | getTeamMemPath() 团队记忆目录路径 |
| `memdir/teamMemPaths.ts` | L92–160 | 第10章 | 路径遍历攻击防护：规范化检查 + realpathDeepestExisting + 真实路径包含验证 |
| `memdir/memoryScan.ts` | L36–60 | 第10章 | scanMemoryFiles 记忆文件预扫描，生成 manifest |
| `services/extractMemories/extractMemories.ts` | L1–20 | 第10章 | initExtractMemories() forked agent 提取模式（继承父 prompt cache） |
| `services/extractMemories/extractMemories.ts` | L130–145 | 第10章 | 互斥跳过逻辑（主 Agent 自写记忆则提取器跳过本轮） |
| `services/extractMemories/extractMemories.ts` | L171 | 第10章 | createAutoMemCanUseTool 提取 Agent 工具限制（Read/Grep/Glob + 记忆目录 Write） |
| `services/autoDream/autoDream.ts` | L60–90 | 第10章 | isGateOpen Dream 触发四级门控（KAIROS/Remote/AutoMemory/Enabled） |
| `services/autoDream/autoDream.ts` | L94–120 | 第10章 | Dream 触发条件（24h + 5 sessions + 锁门） |
| `services/autoDream/autoDream.ts` | L195–220 | 第10章 | runAutoDream 进度追踪（Phase/工具调用计数/写入文件追踪） |
| `services/autoDream/consolidationPrompt.ts` | — | 第10章 | Dream 四阶段提示词模板（Orient/Gather/Consolidate/Prune） |

---

