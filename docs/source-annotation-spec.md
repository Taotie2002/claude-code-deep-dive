# 信源标注规范 v1.0

## 四级信源体系

| 等级 | 标签 | 定义 | 示例 |
|------|------|------|------|
| L1 | 🟢 源码实证 | 泄露源码中可直接对应、代码行级别验证 | "第4章COMMAND_ALLOWLIST配置在 `src/tools/BashTool/bashPermissions.ts` 第23-89行" |
| L2 | 🟡 源码推断 | 源码结构暗示，跨文件关联推断 | "Auto Dream的Lock rollback机制在 `autoDream.ts` 第156行可推知" |
| L3 | 🔵 社区共识 | GitHub/Discord/Reddit广泛认同的观察 | "MCP Server是Anthropic战略方向（据社区讨论）" |
| L4 | ⚪ 合理推测 | 基于已知架构模式的逻辑外推 | "推测：未来版本可能扩展classifier-based permissions" |

## 标注格式

### 行内标注

```
Undercover Mode 通过编译时常量折叠实现隔离[^L1:undercover.ts]
```

### 脚注格式

```
[^L1:undercover.ts]: 源码实证：src/utils/undercover.ts，USER_TYPE === 'ant' 常量折叠，2026-04-03审计狗验证。
```

## 必须覆盖的关键结论（共10项）

| # | 关键结论 | 信源等级 |
|---|----------|----------|
| 1 | COMMAND_ALLOWLIST 白名单机制实现位置与逻辑 | [待填充] |
| 2 | Undercover Mode 编译时常量折叠隔离原理 | [待填充] |
| 3 | Auto Dream 机制的 Lock rollback 实现 | [待填充] |
| 4 | BashTool 权限控制系统架构 | [待填充] |
| 5 | MCP Server 作为 Anthropic 战略方向 | [待填充] |
| 6 | Agent 生命周期状态机转换逻辑 | [待填充] |
| 7 | QueryEngine 查询路由与解析机制 | [待填充] |
| 8 | Stream 数据流与 Token 处理模型 | [待填充] |
| 9 | classifier-based permissions 扩展可能性 | [待填充] |
| 10 | 多 Agent 协作模式与通信机制 | [待填充] |

## 审计验证记录

| 日期 | 审计员 | 验证项 | 结果 |
|------|--------|--------|------|
| 2026-04-03 | 审计狗 | 规范初版建立 | ✅ |

## 更新日志

- v1.0 (2026-04-03): 初版建立，定义四级信源体系与标注格式
