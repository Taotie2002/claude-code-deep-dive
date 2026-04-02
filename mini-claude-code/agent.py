"""
核心 Agent 架构 - 对应 Claude Code src/QueryEngine.ts

Agent 是 Claude Code 的核心，负责：
1. 与 LLM API 通信
2. 管理对话历史
3. 调度 Tool 执行
4. 处理 Tool 结果并继续对话

源码对应:
- src/QueryEngine.ts - 核心查询引擎 (~46K 行)
- src/context.ts - 上下文收集
- src/query/ - 查询管道

本模块展示简化的 Agent 实现，包括:
- Message 历史管理
- Tool 调度循环
- 流式响应处理
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict
from enum import Enum
import os

# 导入 Tool 系统
from tools import ToolExecutor, ToolResult, global_registry


# ============================================================
# 类型定义 (对应 src/types/ 和 Claude API 格式)
# ============================================================

class Role(Enum):
    """消息角色 - 对应 Claude API 的 role 字段"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class Message:
    """
    消息 - 对应 Claude API 的 Message 类型
    
    Claude Code 使用以下角色:
    - user: 用户消息
    - assistant: AI 响应（可能包含 tool_use）
    - system: 系统提示
    
    参考: src/types/ 中的消息类型定义
    """
    role: Role
    content: str
    
    # Claude Code 扩展字段
    tool_calls: list[ToolCall] | None = None  # Assistant 消息中的 Tool 调用
    tool_results: list[ToolResultBlock] | None = None  # Tool 执行结果


@dataclass 
class ToolCall:
    """
    Tool 调用请求 - 对应 Claude API 的 tool_use 类型
    
    当 LLM 决定调用 Tool 时，会在 assistant 消息中包含此结构。
    Claude Code 使用 tool_use_id 来跟踪每次 Tool 调用。
    
    参考: src/Tool.ts 中的 ToolCall 类型
    """
    id: str                    # 唯一 ID，如 "toolu_xxxxx"
    name: str                  # Tool 名称
    input: dict[str, Any]      # Tool 输入参数


@dataclass
class ToolResultBlock:
    """
    Tool 结果块 - 对应 Claude API 的 content block 类型
    
    Claude API 返回的 tool_result 是一种特殊的 content block。
    用于将 Tool 执行结果传回 LLM。
    
    参考: Claude API 文档的 Tool Result 部分
    """
    type: str = "tool_result"
    tool_use_id: str = ""
    content: str = ""


@dataclass
class AgentConfig:
    """
    Agent 配置 - 对应 Claude Code 的 CLI 配置
    
    Claude Code 支持丰富的配置选项：
    - model: 模型选择
    - max_tokens: 最大输出 tokens
    - temperature: 温度参数
    - permission_mode: 权限模式
    - 等等...
    
    参考: src/schemas/ 中的 Zod schemas
    """
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 1.0
    system_prompt: str = "You are a helpful coding assistant."
    
    # API 配置
    api_key: str | None = None
    api_base_url: str = "https://api.anthropic.com/v1"
    
    # Tool 配置
    tool_max_iterations: int = 10  # Tool 调用的最大迭代次数
    
    # Debug
    verbose: bool = False


# ============================================================
# Claude API 客户端 (简化版)
# ============================================================

class ClaudeAPIClient:
    """
    Claude API 客户端 - 简化版的 API 调用封装
    
    真实 Claude Code 使用完整的 Anthropic SDK:
    - src/services/api/ 中的 API 客户端
    - 自动重试、超时、流式处理
    - Token 计算和成本跟踪
    
    本简化版仅做演示用。
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
    
    def messages_create(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]],
        system: str | None = None
    ) -> dict[str, Any]:
        """
        创建消息 - 对应 Claude Messages API
        
        Claude Code 的核心请求：
        1. 构造 messages（包含历史 + 当前请求）
        2. 注入可用的 tools
        3. 发送请求
        4. 处理响应（可能是 streaming 或 non-streaming）
        
        参考: src/query/ 中的查询构造
        """
        import anthropic
        
        # 确保有 API key
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. "
                "Set it via environment variable or config."
            )
        
        client = anthropic.Anthropic(api_key=self.api_key)
        
        # 转换消息格式
        api_messages = self._convert_messages(messages)
        
        # 构建请求参数
        params = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": api_messages,
            "tools": tools,
        }
        
        if system:
            params["system"] = system
        
        if self.config.verbose:
            print(f"[ClaudeAPI] Request: model={self.config.model}, "
                  f"messages={len(messages)}, tools={len(tools)}")
        
        # 调用 API
        response = client.messages.create(**params)
        
        if self.config.verbose:
            print(f"[ClaudeAPI] Response: stop_reason={response.stop_reason}")
        
        # 转换响应格式
        return self._convert_response(response)
    
    def _convert_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        """转换消息格式以适配 API"""
        result = []
        for msg in messages:
            block = {"role": msg.role.value, "content": msg.content}
            
            # 添加 tool_calls（如果有）
            if msg.tool_calls:
                block["content"] = [
                    {"type": "text", "text": msg.content} if msg.content else {"type": "text", "text": ""}
                ]
                for tc in msg.tool_calls:
                    block["content"].append({
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.input
                    })
            
            # 添加 tool_results（如果有）
            if msg.tool_results:
                for tr in msg.tool_results:
                    block["content"].append({
                        "type": "tool_result",
                        "tool_use_id": tr.tool_use_id,
                        "content": tr.content
                    })
            
            result.append(block)
        
        return result
    
    def _convert_response(self, response) -> dict[str, Any]:
        """转换 API 响应格式"""
        content = []
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        
        return {
            "content": content,
            "tool_calls": tool_calls,
            "stop_reason": response.stop_reason,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }


# ============================================================
# 核心 Agent (对应 src/QueryEngine.ts)
# ============================================================

class Agent:
    """
    核心 Agent 类 - Claude Code 的大脑
    
    Agent 负责：
    1. 维护对话历史 (messages)
    2. 与 LLM 交互 (通过 API client)
    3. 调度 Tool 执行 (通过 ToolExecutor)
    4. 管理 Tool 调用循环
    
    Claude Code 的 Agent 工作流程:
    ```
    while True:
        1. 构建 prompt（包含 system + messages + tools）
        2. 调用 LLM API
        3. 如果 LLM 返回 text -> 返回给用户
        4. 如果 LLM 返回 tool_use -> 执行 tool -> 将结果添加到 messages -> 继续
    ```
    
    参考: src/QueryEngine.ts 中的核心循环
    """
    
    def __init__(self, config: AgentConfig | None = None):
        """
        初始化 Agent
        
        参考: src/QueryEngine.ts 的构造函数
        """
        self.config = config or AgentConfig()
        
        # 对话历史
        self.messages: list[Message] = []
        
        # API 客户端
        self.api_client = ClaudeAPIClient(self.config)
        
        # Tool 执行器
        self.tool_executor = ToolExecutor(global_registry)
        
        # 统计
        self.total_tool_calls = 0
        
        if self.config.verbose:
            print(f"[Agent] Initialized with model: {self.config.model}")
    
    # ----------------------------------------------------------------
    # 对话管理 (参考 src/context.ts, src/state/)
    # ----------------------------------------------------------------
    
    def add_user_message(self, content: str) -> None:
        """
        添加用户消息 - 对应用户输入处理
        
        Claude Code 会在用户发送消息时：
        1. 解析消息内容
        2. 可能注入上下文（如当前目录、git 状态）
        3. 添加到 messages 历史
        
        参考: src/context.ts
        """
        message = Message(role=Role.USER, content=content)
        self.messages.append(message)
    
    def add_system_message(self, content: str) -> None:
        """添加系统消息"""
        message = Message(role=Role.SYSTEM, content=content)
        self.messages.append(message)
    
    def get_conversation_history(self) -> list[Message]:
        """获取对话历史"""
        return self.messages.copy()
    
    # ----------------------------------------------------------------
    # 核心推理循环 (对应 src/QueryEngine.ts 的 tool loop)
    # ----------------------------------------------------------------
    
    def think(self, prompt: str, max_iterations: int | None = None) -> str:
        """
        核心推理方法 - 对话式思考
        
        这是 Agent 的主循环：
        1. 添加用户消息
        2. 调用 LLM
        3. 处理响应：
           - 如果是 text，直接返回
           - 如果是 tool_use，执行 tool 并继续
        
        参考: src/QueryEngine.ts 中的 think/execute 方法
        
        Args:
            prompt: 用户输入
            max_iterations: 最大 Tool 调用迭代次数
            
        Returns:
            Agent 的最终响应文本
        """
        max_iter = max_iterations or self.config.tool_max_iterations
        
        # 1. 添加用户消息
        self.add_user_message(prompt)
        
        if self.config.verbose:
            print(f"[Agent] Processing prompt, messages: {len(self.messages)}")
        
        # 2. Tool 调用循环
        iteration = 0
        while iteration < max_iter:
            iteration += 1
            
            # 获取可用的 tools
            tools = global_registry.to_api_format()
            
            # 3. 调用 LLM
            response = self.api_client.messages_create(
                messages=self.messages,
                tools=tools,
                system=self.config.system_prompt
            )
            
            # 4. 处理响应
            response_text = ""
            tool_calls = response.get("tool_calls", [])
            
            # 提取文本内容
            for block in response.get("content", []):
                if block.get("type") == "text":
                    response_text += block.get("text", "")
            
            # 如果没有 tool_calls，直接返回
            if not tool_calls:
                # 添加 assistant 消息到历史
                assistant_msg = Message(
                    role=Role.ASSISTANT,
                    content=response_text
                )
                self.messages.append(assistant_msg)
                return response_text
            
            # 5. 有 tool_calls，执行它们
            if self.config.verbose:
                print(f"[Agent] Executing {len(tool_calls)} tool call(s)")
            
            # 执行所有 tool_calls 并收集结果
            tool_results: list[ToolResultBlock] = []
            
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_input = tc["input"]
                tool_id = tc["id"]
                
                # 执行 Tool
                result = self.tool_executor.execute(tool_name, tool_input)
                self.total_tool_calls += 1
                
                if self.config.verbose:
                    print(f"[Agent] Tool {tool_name} result: {result.success}")
                
                # 收集结果
                tool_results.append(ToolResultBlock(
                    type="tool_result",
                    tool_use_id=tool_id,
                    content=result.content
                ))
            
            # 6. 将 assistant 消息和 tool 结果添加到历史
            assistant_msg = Message(
                role=Role.ASSISTANT,
                content=response_text,
                tool_calls=[
                    ToolCall(id=tc["id"], name=tc["name"], input=tc["input"])
                    for tc in tool_calls
                ]
            )
            self.messages.append(assistant_msg)
            
            # 添加 tool 结果作为新消息
            tool_result_msg = Message(
                role=Role.USER,  # Tool 结果作为 user 消息发送
                content="",  # content 放在 tool_results 中
                tool_results=tool_results
            )
            self.messages.append(tool_result_msg)
        
        # 达到最大迭代次数
        return "[Warning] Max tool iterations reached. Please simplify your request."
    
    def reset(self) -> None:
        """
        重置 Agent 状态 - 对应 Claude Code 的 /clear 或新会话
        
        参考: src/commands/ 中的会话管理
        """
        self.messages.clear()
        self.total_tool_calls = 0
        if self.config.verbose:
            print("[Agent] Reset conversation history")
    
    # ----------------------------------------------------------------
    # 统计信息 (参考 src/cost-tracker.ts)
    # ----------------------------------------------------------------
    
    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "total_messages": len(self.messages),
            "total_tool_calls": self.total_tool_calls,
        }


# ============================================================
# 导出
# ============================================================

__all__ = [
    'Agent',
    'AgentConfig',
    'Message',
    'Role',
    'ToolCall',
    'ToolResultBlock',
    'ClaudeAPIClient',
]
