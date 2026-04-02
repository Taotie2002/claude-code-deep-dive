# 复杂代码审计测试用例

用于测试 mini-claude-code 对复杂真实代码库的审计能力。

## 测试场景

本测试用例模拟一个**屏幕录制工具**和**异步事件流处理系统**的真实代码库，包含：

1. **screen_capture.py** - 屏幕录制核心模块
   - 多线程状态管理
   - 异步事件处理
   - 底层 API 调用模拟
   - 故意植入 3-4 个 Bug

2. **event_stream.py** - 异步事件流处理
   - 事件队列管理
   - 缓冲区处理
   - 错误恢复机制
   - 故意植入 Bug

## 故意植入的 Bug

### screen_capture.py

| Bug # | 类型 | 严重性 | 位置 | 描述 |
|-------|------|--------|------|------|
| 1 | 内存泄漏 | HIGH | line ~50 | `frame_buffer` 字典只添加不清理 |
| 2 | 竞态条件 | CRITICAL | line ~120 | 状态检查与修改不是原子操作 |
| 3 | 资源泄露 | HIGH | line ~200 | `stop_recording` 不清理 frame_buffer |
| 4 | 状态机漏洞 | HIGH | line ~150 | 状态转换跳过 INITIALIZING |

### event_stream.py

| Bug # | 类型 | 严重性 | 位置 | 描述 |
|-------|------|--------|------|------|
| 1 | 数据丢失 | MEDIUM | line ~40 | `deque(maxlen)` 满时自动丢弃旧数据 |
| 2 | 内存泄漏 | HIGH | line ~200 | `_aggregations` 只增不减 |
| 3 | 死锁风险 | HIGH | line ~130 | 混用同步锁和异步锁 |
| 4 | 资源泄露 | MEDIUM | line ~260 | 任务列表不清理已完成任务 |

## 文件结构

```
mini-claude-code/tests/
├── test_complex_audit.py      # 主测试文件
├── test_target/               # 被审计的目标代码
│   ├── screen_capture.py      # 有 Bug 的屏幕录制代码
│   ├── event_stream.py         # 有 Bug 的事件流代码
│   └── requirements.txt        # 测试依赖
└── README.md                   # 本文件
```

## 安装依赖

```bash
cd mini-claude-code/tests/test_target
pip install -r requirements.txt
```

## 运行测试

### 方式 1: 使用 pytest

```bash
cd mini-claude-code
pytest tests/test_complex_audit.py -v
```

### 方式 2: 直接运行

```bash
cd mini-claude-code
python tests/test_complex_audit.py
```

### 方式 3: 运行特定测试

```bash
# 只运行 Bug 识别测试
pytest tests/test_complex_audit.py::TestBugIdentification -v

# 运行完整审计场景
pytest tests/test_complex_audit.py::TestComplexAuditScenario -v
```

## 预期输出

### 测试通过时的输出

```
✅ 测试通过 - mini-claude-code 架构鲁棒性验证完成
```

### 审计报告示例

```
================================================================================
代码审计报告 - 复杂场景压测
================================================================================

📊 分析统计:
   文件数量: 2
   总代码行数: 550
   发现问题: 7

📋 问题分类:
   - Memory Leak: 2
   - Race Condition: 1
   - Resource Leak: 2
   - Deadlock Risk: 1
   - Data Loss: 1

🔴 严重问题:

   1. [CRITICAL] Race Condition
      文件: screen_capture.py:120
      问题: 状态检查与修改不是原子操作，多线程访问可能有竞态

   2. [HIGH] Memory Leak
      文件: screen_capture.py:50
      问题: frame_buffer 字典无限增长，没有清理机制

   ...
================================================================================
```

## 测试覆盖

- [x] Bug 模式搜索 (grep/ripgrep)
- [x] 代码结构分析
- [x] 深度代码审计
- [x] 问题分类与严重性评估
- [x] 审计报告生成
- [x] 模块导入测试
- [x] 集成测试

## 验证 mini-claude-code 能力

本测试用例可以验证 mini-claude-code 在以下方面的能力：

1. **多文件分析** - 同时审计多个相关文件
2. **Bug 模式识别** - 识别常见的 Bug 模式（内存泄漏、竞态条件等）
3. **代码复杂度处理** - 处理 >100 行的复杂 Python 代码
4. **异步代码审计** - 分析 async/await、asyncio、事件循环
5. **多线程代码审计** - 分析 threading、锁、条件变量
6. **报告生成** - 输出结构化的审计报告

## 扩展测试

如果需要添加更多测试场景，可以在 `test_target/` 目录下创建新的目标文件，然后：

1. 在 `test_complex_audit.py` 中添加新的测试类
2. 定义新的 Bug 模式
3. 运行审计验证

## 注意事项

- 本测试用例故意包含 Bug，用于验证审计能力
- 不要在实际项目中使用 `screen_capture.py` 和 `event_stream.py`
- Bug 描述中包含 `# BUG:` 注释，方便识别
