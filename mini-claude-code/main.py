#!/usr/bin/env python3
"""
Mini Claude Code - 入口演示

展示如何组合使用：
1. Agent - 核心推理
2. Tool 系统 - 工具调用
3. Memory 系统 - 记忆管理

运行方式:
    python main.py

前置条件:
    export ANTHROPIC_API_KEY="your-api-key"
"""

import os
import sys

# 导入核心组件
from agent import Agent, AgentConfig
from tools import global_registry, bash, read_file, write_file, grep, glob
from memory import MemoryManager


def print_header(title: str) -> None:
    """打印标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}\n")


def demo_tool_registry() -> None:
    """演示 Tool 注册表"""
    print_header("Demo 1: Tool Registry")
    
    print("已注册的 Tools:\n")
    for tool in global_registry.list_tools():
        print(f"  [{tool.category}] {tool.name}")
        print(f"           {tool.description[:60]}...")
        print()


def demo_memory_system() -> None:
    """演示记忆系统"""
    print_header("Demo 2: Memory System")
    
    # 创建记忆管理器
    memory = MemoryManager()
    
    # 演示短期记忆
    print("1. 短期对话记忆 (ConversationMemory)")
    memory.conversation.add(
        "用户正在开发一个 Web 项目",
        memory_type="context",
        importance=0.8
    )
    memory.conversation.add(
        "项目使用 Python FastAPI",
        memory_type="context",
        importance=0.9
    )
    memory.conversation.set_context("current_project", "web-api")
    print(memory.conversation.get_context_summary())
    
    # 演示长期记忆
    print("\n2. 长期记忆 (PersistentMemory)")
    memory.remember("FastAPI 项目结构: app/main.py, app/routers/, app/models/")
    memory.remember("常用命令: uvicorn app.main:app --reload")
    print("已存储 2 条持久化记忆")
    
    # 搜索记忆
    print("\n3. 搜索记忆")
    results = memory.recall("FastAPI")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r}")


def demo_agent_basic() -> None:
    """演示 Agent 基本功能（不需要 API key）"""
    print_header("Demo 3: Agent 基本结构")
    
    # 创建 Agent 配置
    config = AgentConfig(
        model="claude-3-5-sonnet-20241022",
        verbose=True,
        system_prompt="""You are a helpful coding assistant.
You have access to various tools to help users with their tasks.
When you need to run shell commands or access files, use the available tools."""
    )
    
    # 创建 Agent
    agent = Agent(config)
    
    print("Agent 配置:")
    print(f"  - Model: {agent.config.model}")
    print(f"  - Max Tool Iterations: {agent.config.tool_max_iterations}")
    print(f"  - System Prompt 长度: {len(agent.config.system_prompt)} chars")
    
    print(f"\n已注册 {len(global_registry.list_tools())} 个 Tools")
    
    # 显示统计
    stats = agent.get_stats()
    print(f"\n初始统计: {stats}")


def demo_tool_execution() -> None:
    """演示直接执行 Tool（不需要 API key）"""
    print_header("Demo 4: Tool 直接执行")
    
    from tools import ToolExecutor
    
    executor = ToolExecutor(global_registry)
    
    # 执行 ls 命令
    print("执行 Tool: Bash(command='ls -la')")
    result = executor.execute("Bash", {"command": "ls -la /tmp"})
    print(f"\n结果:\n{result.content[:500]}")


def demo_full_agent_session() -> None:
    """
    完整 Agent 对话演示
    
    需要 ANTHROPIC_API_KEY 环境变量
    """
    print_header("Demo 5: 完整 Agent 对话")
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY 未设置，跳过 API 调用演示")
        print("   设置方式: export ANTHROPIC_API_KEY='your-key'")
        return
    
    # 创建 Agent
    config = AgentConfig(
        model="claude-3-5-sonnet-20241022",
        verbose=True,
        system_prompt="""You are a helpful coding assistant specialized in Python.
Keep responses concise and practical."""
    )
    
    agent = Agent(config)
    
    # 简单的对话演示
    print("\n--- 对话开始 ---\n")
    
    # 第一轮：让 Agent 自我介绍
    print("用户: Hello, what can you do?")
    response = agent.think("Hello, what can you do?")
    print(f"\nAgent: {response[:300]}...")
    
    # 第二轮：让 Agent 使用工具
    print("\n用户: List the files in /tmp using bash tool")
    response = agent.think(
        "Please list files in /tmp directory using the Bash tool. "
        "Just execute: ls -la /tmp"
    )
    print(f"\nAgent: {response[:500]}")
    
    # 显示统计
    stats = agent.get_stats()
    print(f"\n--- 对话统计 ---")
    print(f"总消息数: {stats['total_messages']}")
    print(f"总 Tool 调用: {stats['total_tool_calls']}")


def demo_code_demo() -> None:
    """
    代码示例演示 - 展示如何使用这些组件构建自己的 Agent
    """
    print_header("Demo 6: 代码使用示例")
    
    code_example = '''
# ============================================================
# 如何使用 Mini Claude Code 构建自己的 Agent
# ============================================================

from agent import Agent, AgentConfig
from tools import global_registry, bash, read_file, write_file
from memory import MemoryManager

# 1. 创建记忆管理器（可选）
memory = MemoryManager()
memory.remember("用户的项目使用 Django 框架", memory_type="context")

# 2. 创建 Agent 配置
config = AgentConfig(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2048,
    verbose=True,
    system_prompt="你是一个 Django 开发专家"
)

# 3. 创建 Agent
agent = Agent(config)

# 4. 开始对话
response = agent.think("帮我创建一个 Django 模型")
print(response)

# 5. 检查统计
print(agent.get_stats())

# 6. 查看已注册的 Tools
for tool in global_registry.list_tools():
    print(f"{tool.name}: {tool.description[:50]}...")
'''
    
    print(code_example)


def main() -> None:
    """主函数"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           Mini Claude Code - 简化复刻 Demo                    ║
║                                                              ║
║           展示 Claude Code 核心架构                           ║
║           - Agent 核心                                        ║
║           - Tool 调度机制                                      ║
║           - Memory 记忆系统                                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 运行各个演示
    demo_tool_registry()
    demo_memory_system()
    demo_agent_basic()
    demo_tool_execution()
    demo_full_agent_session()
    demo_code_demo()
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60 + "\n")
    
    print("""
下一步：
1. 查看源码文件了解详细实现
2. 设置 ANTHROPIC_API_KEY 运行完整 Agent
3. 扩展 Tool 系统添加自定义功能
4. 对比 Claude Code 源码学习完整架构
""")


if __name__ == "__main__":
    main()
