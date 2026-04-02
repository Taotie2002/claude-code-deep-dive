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
import time

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


# ============================================================
# 熔断器 (Circuit Breaker) - 优雅降级
# ============================================================

class CircuitBreaker:
    """
    熔断器 - 防止连续失败导致系统雪崩
    
    状态机:
    - closed: 正常状态，请求直接通过
    - open: 熔断状态，请求被拒绝，快速失败
    - half-open: 半开状态，允许一个测试请求通过
    
    熔断触发条件: 连续失败次数达到阈值
    自动恢复: 半开状态后如果成功则关闭，否则重新打开
    """
    
    def __init__(self, failure_threshold: int = 3, recovery_timeout: float = 30.0):
        """
        初始化熔断器
        
        Args:
            failure_threshold: 触发熔断的连续失败次数
            recovery_timeout: 自动尝试恢复的等待时间（秒）
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failures = 0
        self.successes = 0
        self.state = "closed"  # closed / open / half-open
        self.last_failure_time: float | None = None
        
        # 诊断数据
        self.context_usage: float = 0.0  # 上下文使用率 (0-1)
        self.recent_calls: list[dict[str, Any]] = []  # 最近5次调用记录
        self.token_budget: int = 200000  # token 预算
        self.used_tokens: int = 0  # 已使用 tokens
        self.errors: list[dict[str, Any]] = []  # 最近错误记录
    
    def record_failure(self, error: Exception | None = None, context_usage: float = 0.0) -> None:
        """
        记录一次失败
        
        Args:
            error: 异常对象（如果有）
            context_usage: 失败时的上下文使用率
        """
        self.failures += 1
        self.successes = 0
        self.last_failure_time = time.time()
        
        # 记录错误
        error_info = {
            "timestamp": self.last_failure_time,
            "type": type(error).__name__ if error else "UnknownError",
            "message": str(error) if error else "Unknown error",
            "context_usage": context_usage,
            "failures_count": self.failures
        }
        self.errors.append(error_info)
        if len(self.errors) > 10:
            self.errors = self.errors[-10:]
        
        # 更新上下文使用率
        self.context_usage = context_usage
        
        # 检查是否需要熔断
        if self.failures >= self.failure_threshold:
            self._trip_circuit()
    
    def record_success(self, tokens_used: int = 0, context_usage: float = 0.0) -> None:
        """
        记录一次成功
        
        Args:
            tokens_used: 本次使用的 tokens 数量
            context_usage: 成功时的上下文使用率
        """
        self.used_tokens += tokens_used
        self.context_usage = context_usage
        self.failures = 0
        self.successes += 1
        
        # 半开状态下成功则关闭熔断器
        if self.state == "half-open" and self.successes >= 1:
            self._reset_circuit()
    
    def _trip_circuit(self) -> None:
        """触发熔断"""
        self.state = "open"
        print(f"[CircuitBreaker] ⚡ 熔断器打开！连续 {self.failures} 次失败")
    
    def _reset_circuit(self) -> None:
        """重置熔断器"""
        self.state = "closed"
        self.failures = 0
        self.successes = 0
        print(f"[CircuitBreaker] ✅ 熔断器关闭，服务恢复")
    
    def can_proceed(self) -> bool:
        """
        检查是否可以继续请求
        
        Returns:
            True: 可以发送请求
            False: 熔断中，快速失败
        """
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # 检查是否超时可以尝试恢复
            if self.last_failure_time and \
               (time.time() - self.last_failure_time) >= self.recovery_timeout:
                self.state = "half-open"
                print(f"[CircuitBreaker] 🔄 进入半开状态，尝试恢复...")
                return True
            return False
        
        # half-open 状态允许请求通过测试
        return True
    
    def get_diagnostic_report(self) -> dict[str, Any]:
        """
        生成诊断报告
        
        Returns:
            包含系统健康状态的字典
        """
        return {
            "circuit_state": self.state,
            "consecutive_failures": self.failures,
            "total_failures": len(self.errors),
            "context_usage": round(self.context_usage * 100, 1),  # 百分比
            "token_budget_remaining": self.token_budget - self.used_tokens,
            "token_usage_total": self.used_tokens,
            "recent_calls": self.recent_calls[-5:] if self.recent_calls else [],
            "error_summary": self.errors[-3:] if self.errors else []
        }
    
    def record_call(self, call_info: dict[str, Any]) -> None:
        """
        记录一次 API 调用
        
        Args:
            call_info: 调用信息字典
        """
        self.recent_calls.append({
            "timestamp": time.time(),
            **call_info
        })
        if len(self.recent_calls) > 10:
            self.recent_calls = self.recent_calls[-10:]


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
    model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 1.0
    system_prompt: str = "You are a helpful coding assistant."
    
    # API 配置
    api_key: str | None = None
    api_base_url: str = "https://api.anthropic.com/v1"
    
    # Tool 配置
    tool_max_iterations: int = 10  # Tool 调用的最大迭代次数
    
    # 熔断器配置
    failure_threshold: int = 3  # 触发熔断的连续失败次数
    circuit_recovery_timeout: float = 30.0  # 自动恢复等待时间
    
    # Token 预算
    token_budget: int = 200000  # 会话总 token 预算
    
    # Debug
    verbose: bool = False
    
    # 超时配置
    request_timeout: float = 60.0  # 请求超时时间（秒）


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
        
        # 熔断器
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.failure_threshold,
            recovery_timeout=self.config.circuit_recovery_timeout
        )
        self.circuit_breaker.token_budget = self.config.token_budget
        
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
        核心推理方法 - 对话式思考（带熔断保护）
        
        这是 Agent 的主循环：
        1. 添加用户消息
        2. 检查熔断器状态
        3. 调用 LLM（带超时和错误处理）
        4. 处理响应：
           - 如果是 text，直接返回
           - 如果是 tool_use，执行 tool 并继续
        5. 失败时输出诊断报告
        
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
        
        # 2. 检查熔断器状态
        if not self.circuit_breaker.can_proceed():
            return self._build_circuit_open_message()
        
        # 3. Tool 调用循环
        iteration = 0
        while iteration < max_iter:
            iteration += 1
            
            # 获取可用的 tools
            tools = global_registry.to_api_format()
            
            # 计算当前上下文使用率
            context_usage = self._calculate_context_usage()
            
            # 4. 调用 LLM（带超时处理）
            call_start = time.time()
            try:
                response = self._call_llm_with_timeout(
                    messages=self.messages,
                    tools=tools,
                    system=self.config.system_prompt,
                    timeout=self.config.request_timeout
                )
                
                call_duration = time.time() - call_start
                
                # 记录成功调用
                self.circuit_breaker.record_call({
                    "duration": round(call_duration, 2),
                    "iteration": iteration,
                    "success": True,
                    "context_usage": context_usage
                })
                
                # 记录 tokens 使用
                if "usage" in response:
                    tokens_used = response["usage"].get("output_tokens", 0)
                    self.circuit_breaker.record_success(
                        tokens_used=tokens_used,
                        context_usage=context_usage
                    )
                
            except TimeoutError as e:
                # 处理超时
                return self._handle_timeout_error(e, iteration, context_usage)
            
            except Exception as e:
                # 处理其他错误
                return self._handle_api_error(e, iteration, context_usage)
            
            # 5. 处理响应
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
            
            # 6. 有 tool_calls，执行它们
            if self.config.verbose:
                print(f"[Agent] Executing {len(tool_calls)} tool call(s)")
            
            # 执行所有 tool_calls 并收集结果
            tool_results: list[ToolResultBlock] = []
            tool_execution_success = True
            
            for tc in tool_calls:
                tool_name = tc["name"]
                tool_input = tc["input"]
                tool_id = tc["id"]
                
                try:
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
                    
                    if not result.success:
                        tool_execution_success = False
                        
                except Exception as e:
                    # Tool 执行失败
                    tool_execution_success = False
                    tool_results.append(ToolResultBlock(
                        type="tool_result",
                        tool_use_id=tool_id,
                        content=f"[Error] Tool execution failed: {str(e)}"
                    ))
            
            # 7. 将 assistant 消息和 tool 结果添加到历史
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
            
            # 如果有 tool 执行失败，记录但继续
            if not tool_execution_success:
                self.circuit_breaker.record_failure(
                    error=Exception("Tool execution partial failure"),
                    context_usage=context_usage
                )
        
        # 达到最大迭代次数
        return "[Warning] Max tool iterations reached. Please simplify your request."
    
    def _call_llm_with_timeout(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]],
        system: str | None,
        timeout: float
    ) -> dict[str, Any]:
        """
        带超时的 LLM 调用
        
        Args:
            messages: 消息列表
            tools: 可用工具列表
            system: 系统提示
            timeout: 超时时间（秒）
            
        Returns:
            API 响应
            
        Raises:
            TimeoutError: 请求超时
        """
        import threading
        import queue
        
        result_queue: queue.Queue = queue.Queue()
        exception_queue: queue.Queue = queue.Queue()
        
        def api_call():
            try:
                result = self.api_client.messages_create(
                    messages=messages,
                    tools=tools,
                    system=system
                )
                result_queue.put(result)
            except Exception as e:
                exception_queue.put(e)
        
        # 在独立线程中执行 API 调用
        thread = threading.Thread(target=api_call)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            # 线程仍在运行，表示超时
            raise TimeoutError(f"API request exceeded timeout of {timeout}s")
        
        # 检查是否有异常
        try:
            exc = exception_queue.get_nowait()
            raise exc
        except queue.Empty:
            pass
        
        # 获取结果
        try:
            return result_queue.get_nowait()
        except queue.Empty:
            raise TimeoutError("No response received from API")
    
    def _handle_timeout_error(
        self,
        error: TimeoutError,
        iteration: int,
        context_usage: float
    ) -> str:
        """
        处理超时错误
        
        Args:
            error: 超时异常
            iteration: 当前迭代次数
            context_usage: 上下文使用率
            
        Returns:
            诊断报告字符串
        """
        self.circuit_breaker.record_failure(
            error=error,
            context_usage=context_usage
        )
        
        # 记录调用
        self.circuit_breaker.record_call({
            "iteration": iteration,
            "success": False,
            "error_type": "TimeoutError",
            "error_message": str(error),
            "context_usage": context_usage
        })
        
        return self._build_diagnostic_report(
            title="⚠️ API 请求超时",
            summary=f"LLM 响应超时（{self.config.request_timeout}s）",
            suggestion="可能是网络问题或模型负载过高，请稍后重试。"
        )
    
    def _handle_api_error(
        self,
        error: Exception,
        iteration: int,
        context_usage: float
    ) -> str:
        """
        处理 API 错误
        
        Args:
            error: 异常对象
            iteration: 当前迭代次数
            context_usage: 上下文使用率
            
        Returns:
            诊断报告字符串
        """
        self.circuit_breaker.record_failure(
            error=error,
            context_usage=context_usage
        )
        
        # 记录调用
        self.circuit_breaker.record_call({
            "iteration": iteration,
            "success": False,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context_usage": context_usage
        })
        
        # 检查是否触发熔断
        if self.circuit_breaker.state == "open":
            return self._build_circuit_open_message()
        
        return self._build_diagnostic_report(
            title="❌ API 调用失败",
            summary=f"{type(error).__name__}: {str(error)}",
            suggestion="请检查 API 配置和网络连接。"
        )
    
    def _build_circuit_open_message(self) -> str:
        """
        构建熔断器打开时的消息
        
        Returns:
            包含诊断报告的消息
        """
        report = self.circuit_breaker.get_diagnostic_report()
        
        return self._build_diagnostic_report(
            title="🔴 熔断器已打开",
            summary=f"连续 {report['consecutive_failures']} 次失败，服务暂时不可用",
            suggestion=f"等待 {self.config.circuit_recovery_timeout} 秒后自动重试，或手动检查服务状态。",
            include_full_report=True
        )
    
    def _build_diagnostic_report(
        self,
        title: str,
        summary: str,
        suggestion: str,
        include_full_report: bool = False
    ) -> str:
        """
        构建结构化诊断报告
        
        Args:
            title: 报告标题
            summary: 问题摘要
            suggestion: 建议操作
            include_full_report: 是否包含完整报告
            
        Returns:
            格式化的诊断报告字符串
        """
        report = self.circuit_breaker.get_diagnostic_report()
        
        lines = [
            "",
            "=" * 50,
            title,
            "=" * 50,
            "",
            f"📋 问题: {summary}",
            "",
            f"💡 建议: {suggestion}",
            "",
            "📊 诊断信息:",
            f"  • 熔断状态: {report['circuit_state']}",
            f"  • 连续失败: {report['consecutive_failures']} 次",
            f"  • 上下文使用: {report['context_usage']}%",
            f"  • Token 剩余: {report['token_budget_remaining']:,}",
        ]
        
        if include_full_report and report["recent_calls"]:
            lines.append("")
            lines.append("📞 最近调用:")
            for call in report["recent_calls"]:
                status = "✅" if call.get("success") else "❌"
                lines.append(
                    f"  {status} iter={call.get('iteration', '?')} "
                    f"duration={call.get('duration', '?')}s"
                )
        
        if include_full_report and report["error_summary"]:
            lines.append("")
            lines.append("🚨 最近错误:")
            for err in report["error_summary"]:
                lines.append(
                    f"  • [{err['type']}] {err['message'][:50]}..."
                )
        
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _calculate_context_usage(self) -> float:
        """
        计算当前上下文使用率
        
        Returns:
            使用率 (0.0 - 1.0)
        """
        # 简单估算：基于消息数量和总 tool 调用数
        msg_count = len(self.messages)
        tool_count = self.total_tool_calls
        
        # 假设每个消息平均约 200 tokens
        estimated_tokens = (msg_count * 200) + (tool_count * 500)
        
        return min(estimated_tokens / self.circuit_breaker.token_budget, 1.0)
    
    def reset(self) -> None:
        """
        重置 Agent 状态 - 对应 Claude Code 的 /clear 或新会话
        
        参考: src/commands/ 中的会话管理
        """
        self.messages.clear()
        self.total_tool_calls = 0
        
        # 重置熔断器
        if self.circuit_breaker.state != "closed":
            self.circuit_breaker._reset_circuit()
        self.circuit_breaker.failures = 0
        self.circuit_breaker.errors.clear()
        self.circuit_breaker.recent_calls.clear()
        
        if self.config.verbose:
            print("[Agent] Reset conversation history and circuit breaker")
    
    # ----------------------------------------------------------------
    # 统计信息 (参考 src/cost-tracker.ts)
    # ----------------------------------------------------------------
    
    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        cb_stats = self.circuit_breaker.get_diagnostic_report()
        return {
            "total_messages": len(self.messages),
            "total_tool_calls": self.total_tool_calls,
            "circuit_breaker": {
                "state": cb_stats["circuit_state"],
                "consecutive_failures": cb_stats["consecutive_failures"],
                "context_usage": cb_stats["context_usage"],
                "token_budget_remaining": cb_stats["token_budget_remaining"],
            }
        }
    
    def get_diagnostic_report(self) -> dict[str, Any]:
        """获取完整诊断报告"""
        return self.circuit_breaker.get_diagnostic_report()


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
    'CircuitBreaker',
]
