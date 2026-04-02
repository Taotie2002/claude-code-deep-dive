"""
Tool 调度机制 - 对应 Claude Code src/tools.ts 和 src/Tool.ts

Claude Code 的 Tool 系统是其 Agent 能力的核心扩展。本模块展示简化的 Tool 注册
和调度机制，包括：
1. Tool 注册表（Tool Registry）
2. Tool 定义和元数据
3. Tool 执行器（Tool Executor）
4. 权限检查接口

源码对应：
- src/tools.ts - Tool 注册表
- src/Tool.ts - Tool 基类和类型定义
- src/tools/*.ts - 各个具体 Tool 实现
"""

from __future__ import annotations
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar, Generic
from enum import Enum
import json

# ============================================================
# 类型定义 (对应 src/Tool.ts 中的类型定义)
# ============================================================

class PermissionMode(Enum):
    """
    权限模式 - 对应 Claude Code 的 permission modes
    参考: src/hooks/toolPermission/
    """
    DEFAULT = "default"      # 默认需要确认
    AUTO = "auto"            # 自动批准
    BYPASS = "bypass"        # 绕过权限检查
    PLAN = "plan"            # 计划模式


@dataclass
class ToolDefinition:
    """
    Tool 定义 - 对应 src/Tool.ts 中的 ToolDefinition 类型
    
    Claude Code 中每个 Tool 都有输入 schema、权限模型、执行逻辑
    """
    name: str                          # Tool 名称，如 "Bash", "Read"
    description: str                   # Tool 描述，供 LLM 理解用途
    input_schema: dict[str, Any]        # 输入参数 schema (JSON Schema)
    permission_mode: PermissionMode     # 权限模式
    fn: Callable[..., Any]             # 实际执行函数
    
    # 额外元数据
    category: str = "general"          # Tool 分类
    deprecated: bool = False           # 是否已废弃
    
    def to_api_format(self) -> dict[str, Any]:
        """
        转换为 API 格式 - 供 LLM 理解 Tool 的输入输出
        对应 Claude Code src/Tool.ts 中的 toAPIToolFormat()
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }


@dataclass
class ToolResult:
    """
    Tool 执行结果 - 封装 Tool 的返回值
    
    Claude Code 中 ToolResult 包含:
    - content: 返回内容
    - success: 是否成功
    - error: 错误信息（如果有）
    - tool_use_id: Tool 调用的唯一标识
    """
    content: str                        # 返回内容（作为 LLM 的观察）
    success: bool = True                # 是否成功执行
    error: str | None = None             # 错误信息
    tool_use_id: str | None = None       # Tool 调用 ID


# ============================================================
# Tool 注册表 (对应 src/tools.ts)
# ============================================================

class ToolRegistry:
    """
    Tool 注册表 - 管理和调度所有可用 Tool
    
    这是 Claude Code Tool 系统的核心。所有的 Tool 都需要注册到这里，
    Agent 在执行时会查询注册表找到对应的 Tool 并执行。
    
    源码对应:
    - src/tools.ts 中的 tool registry
    - src/tools/BashTool.ts 等具体 Tool 实现
    """
    
    def __init__(self):
        # 注册表: name -> ToolDefinition
        self._tools: dict[str, ToolDefinition] = {}
        
        # 内省用的索引: category -> [tool_names]
        self._categories: dict[str, list[str]] = {}
    
    def register(self, tool: ToolDefinition) -> None:
        """
        注册一个 Tool
        
        在 Claude Code 中，Tool 注册发生在启动时：
        1. 加载内置 Tool（src/tools/）
        2. 加载 Skill Tool（src/skills/）
        3. 加载 MCP Tool（src/services/mcp/）
        4. 加载 Plugin Tool（src/services/plugins/）
        """
        self._tools[tool.name] = tool
        
        # 更新分类索引
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        if tool.name not in self._categories[tool.category]:
            self._categories[tool.category].append(tool.name)
        
        print(f"[ToolRegistry] Registered tool: {tool.name} (category: {tool.category})")
    
    def get(self, name: str) -> ToolDefinition | None:
        """根据名称获取 Tool"""
        return self._tools.get(name)
    
    def list_tools(self) -> list[ToolDefinition]:
        """列出所有已注册的 Tool"""
        return list(self._tools.values())
    
    def list_by_category(self, category: str) -> list[ToolDefinition]:
        """按分类列出 Tool"""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def to_api_format(self) -> list[dict[str, Any]]:
        """
        导出所有 Tool 为 API 格式 - 发送给 LLM
        对应 Claude Code src/query/ 中的 query 构造
        """
        return [tool.to_api_format() for tool in self._tools.values()]


# ============================================================
# Tool 装饰器 (参考 Claude Code 的 @tool 模式)
# ============================================================

# 全局注册表实例 - 相当于 src/tools.ts 中的 defaultToolRegistry
global_registry = ToolRegistry()


def tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    permission_mode: PermissionMode = PermissionMode.DEFAULT,
    category: str = "general"
) -> Callable:
    """
    Tool 装饰器 - 简化版的 Tool 注册装饰器
    
    用法:
        @tool(name="Bash", description="Execute shell commands")
        def bash(command: str) -> ToolResult:
            ...
    
    对应 Claude Code 源码:
    - src/tools.ts 中的工具注册逻辑
    - src/tools/BashTool.ts 中的 Tool 定义
    
    Args:
        name: Tool 名称
        description: Tool 描述（供 LLM 理解何时使用）
        input_schema: 输入参数 JSON Schema
        permission_mode: 权限模式
        category: 分类
    """
    def decorator(fn: Callable) -> Callable:
        # 创建 Tool 定义
        tool_def = ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            permission_mode=permission_mode,
            fn=fn,
            category=category
        )
        
        # 注册到全局注册表
        global_registry.register(tool_def)
        
        # 给函数附加元数据（便于内省）
        fn._tool_def = tool_def
        
        return fn
    
    return decorator


# ============================================================
# Tool 执行器 (对应 Claude Code 的 Tool 执行逻辑)
# ============================================================

class ToolExecutor:
    """
    Tool 执行器 - 负责执行 Tool 并处理结果
    
    Claude Code 中的执行流程:
    1. LLM 返回 tool_use 消息
    2. 从 ToolRegistry 获取 Tool 定义
    3. 验证输入参数
    4. 检查权限
    5. 执行 Tool
    6. 格式化结果返回给 LLM
    
    对应源码:
    - src/QueryEngine.ts 中的 tool execution loop
    - src/hooks/toolPermission/ 中的权限检查
    """
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.permission_mode = PermissionMode.DEFAULT
    
    def execute(self, tool_name: str, tool_input: dict[str, Any]) -> ToolResult:
        """
        执行单个 Tool
        
        Args:
            tool_name: Tool 名称
            tool_input: Tool 输入参数
            
        Returns:
            ToolResult: 执行结果
        """
        # 1. 获取 Tool 定义
        tool_def = self.registry.get(tool_name)
        if not tool_def:
            return ToolResult(
                content=f"Error: Tool '{tool_name}' not found",
                success=False,
                error=f"Unknown tool: {tool_name}"
            )
        
        # 2. 权限检查
        if not self._check_permission(tool_def):
            return ToolResult(
                content=f"Error: Permission denied for tool '{tool_name}'",
                success=False,
                error="Permission denied"
            )
        
        # 3. 验证输入参数
        if not self._validate_input(tool_def, tool_input):
            return ToolResult(
                content=f"Error: Invalid input for tool '{tool_name}'",
                success=False,
                error="Invalid input parameters"
            )
        
        # 4. 执行 Tool
        try:
            result = tool_def.fn(**tool_input)
            
            # 如果返回的不是 ToolResult，包装一下
            if isinstance(result, ToolResult):
                return result
            else:
                return ToolResult(content=str(result))
        
        except Exception as e:
            return ToolResult(
                content=f"Error executing tool '{tool_name}': {str(e)}",
                success=False,
                error=str(e)
            )
    
    def _check_permission(self, tool_def: ToolDefinition) -> bool:
        """
        检查权限 - 对应 src/hooks/toolPermission/
        
        Claude Code 的权限模型:
        - default: 需要用户确认
        - auto: 自动批准
        - bypass: 完全绕过
        - plan: 计划模式下更严格
        """
        if self.permission_mode == PermissionMode.BYPASS:
            return True
        
        if self.permission_mode == PermissionMode.AUTO:
            return True
        
        # default 模式下，简单地批准内置工具
        trusted_categories = ["general", "filesystem"]
        return tool_def.category in trusted_categories
    
    def _validate_input(
        self, 
        tool_def: ToolDefinition, 
        tool_input: dict[str, Any]
    ) -> bool:
        """
        验证输入参数 - 对应 JSON Schema 验证
        
        Claude Code 使用 Zod 进行 schema 验证
        这里用简单的类型检查做演示
        """
        required = tool_def.input_schema.get("required", [])
        
        # 检查必需参数
        for param in required:
            if param not in tool_input:
                return False
        
        return True


# ============================================================
# 内置 Tool 示例 (对应 src/tools/ 目录)
# ============================================================

@tool(
    name="Bash",
    description="""Execute shell commands in a terminal. Use this tool to run 
command-line programs, scripts, or system commands. Returns the stdout and stderr 
output. Requires the 'command' parameter.""",
    input_schema={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute"
            }
        },
        "required": ["command"]
    },
    permission_mode=PermissionMode.DEFAULT,
    category="system"
)
def bash(command: str) -> ToolResult:
    """
    Bash Tool - 对应 src/tools/BashTool.ts
    
    Claude Code 最常用的 Tool 之一，用于执行 shell 命令。
    在 Claude Code 中实现了：
    - 命令超时控制
    - 工作目录管理
    - 环境变量注入
    - 安全沙箱
    """
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return ToolResult(content=output or "(no output)", success=result.returncode == 0)
    except subprocess.TimeoutExpired:
        return ToolResult(content="Error: Command timed out", success=False)
    except Exception as e:
        return ToolResult(content=f"Error: {str(e)}", success=False)


@tool(
    name="Read",
    description="""Read the contents of a file from the filesystem. Takes a 'path' 
parameter specifying the file path. Returns the file contents as a string. Supports 
reading images, PDFs, and other file types.""",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to read"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of lines to read (optional)"
            }
        },
        "required": ["path"]
    },
    permission_mode=PermissionMode.DEFAULT,
    category="filesystem"
)
def read_file(path: str, limit: int | None = None) -> ToolResult:
    """
    Read File Tool - 对应 src/tools/FileReadTool.ts
    
    Claude Code 用于读取文件内容的 Tool，支持：
    - 全文读取
    - 行数限制（用于截断长文件）
    - 二进制文件处理
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if limit:
                lines = [f.readline() for _ in range(limit)]
                content = ''.join(lines)
            else:
                content = f.read()
        return ToolResult(content=content)
    except FileNotFoundError:
        return ToolResult(content=f"Error: File not found: {path}", success=False)
    except Exception as e:
        return ToolResult(content=f"Error reading {path}: {str(e)}", success=False)


@tool(
    name="Write",
    description="""Write content to a file, creating a new file or overwriting 
an existing one. Takes 'path' and 'content' parameters. Use this to create or 
update files.""",
    input_schema={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path where the file should be written"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            }
        },
        "required": ["path", "content"]
    },
    permission_mode=PermissionMode.DEFAULT,
    category="filesystem"
)
def write_file(path: str, content: str) -> ToolResult:
    """
    Write File Tool - 对应 src/tools/FileWriteTool.ts
    
    Claude Code 用于创建/覆盖文件的 Tool。
    注意：这是覆盖写入，Claude Code 还有 Edit Tool 用于部分修改。
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return ToolResult(content=f"Successfully wrote to {path}")
    except Exception as e:
        return ToolResult(content=f"Error writing {path}: {str(e)}", success=False)


@tool(
    name="Grep",
    description="""Search for text patterns in files using grep. Takes 'pattern' 
for the regex pattern and optionally 'path' to search in a specific directory. 
Returns matching lines with context.""",
    input_schema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Regex pattern to search for"
            },
            "path": {
                "type": "string",
                "description": "Directory or file to search in (default: current dir)"
            }
        },
        "required": ["pattern"]
    },
    permission_mode=PermissionMode.DEFAULT,
    category="search"
)
def grep(pattern: str, path: str = ".") -> ToolResult:
    """
    Grep Tool - 对应 src/tools/GrepTool.ts
    
    Claude Code 用于代码搜索的 Tool，基于 ripgrep。
    支持正则表达式、高亮、上下文行等。
    """
    import subprocess
    try:
        result = subprocess.run(
            ["grep", "-rn", pattern, path],
            capture_output=True,
            text=True,
            timeout=10
        )
        return ToolResult(content=result.stdout or "(no matches)")
    except Exception as e:
        return ToolResult(content=f"Error searching: {str(e)}", success=False)


@tool(
    name="Glob",
    description="""Find files matching a glob pattern. Takes 'pattern' parameter 
(e.g., "*.py" for all Python files). Returns list of matching file paths.""",
    input_schema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Glob pattern to match files"
            },
            "path": {
                "type": "string",
                "description": "Directory to search in (default: current dir)"
            }
        },
        "required": ["pattern"]
    },
    permission_mode=PermissionMode.DEFAULT,
    category="search"
)
def glob(pattern: str, path: str = ".") -> ToolResult:
    """
    Glob Tool - 对应 src/tools/GlobTool.ts
    
    Claude Code 用于文件发现的 Tool，基于 glob 模式匹配。
    """
    import glob as g
    import os
    try:
        # 使用 os.path.join 确保路径正确
        search_path = os.path.join(path, pattern)
        matches = g.glob(search_path)
        if not matches:
            return ToolResult(content=f"No files matching {pattern}")
        return ToolResult(content="\n".join(matches))
    except Exception as e:
        return ToolResult(content=f"Error searching: {str(e)}", success=False)


# ============================================================
# 导出
# ============================================================

__all__ = [
    'ToolDefinition',
    'ToolResult',
    'ToolRegistry',
    'ToolExecutor',
    'PermissionMode',
    'tool',
    'global_registry',
    'bash',
    'read_file',
    'write_file',
    'grep',
    'glob',
]
