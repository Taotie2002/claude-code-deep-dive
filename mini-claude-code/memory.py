"""
Memory 记忆机制 - 对应 Claude Code src/memdir/ 和 src/services/extractMemories/

Claude Code 的记忆系统分为两层：
1. 短期记忆 (Short-term): 对话历史，存储在内存中
2. 长期记忆 (Long-term): 持久化到磁盘的 memdir/

本模块展示简化的记忆实现：
1. ConversationMemory: 短期对话记忆
2. PersistentMemory: 长期持久化记忆
3. ExperienceMemory: 经验提取和检索

源码对应：
- src/memdir/memdir.ts - 记忆目录
- src/memdir/extractMemories.ts - 记忆提取
- src/memdir/memdirIndex.ts - 记忆索引
- src/services/extractMemories/ - 自动记忆服务
"""

from __future__ import annotations
import os
import json
import time
from dataclasses import dataclass, field
from typing import Any
from pathlib import Path


# ============================================================
# 基础类型
# ============================================================

@dataclass
class MemoryEntry:
    """
    记忆条目 - 对应 Claude Code 的 Memory 数据结构
    
    Claude Code 中每个记忆条目包含:
    - content: 记忆内容
    - timestamp: 创建时间
    - type: 记忆类型 (fact, preference, context, etc.)
    - importance: 重要性评分
    - source: 来源（哪个对话/任务）
    """
    content: str
    timestamp: float
    type: str = "general"  # fact, preference, context, skill
    importance: float = 1.0  # 0.0 - 1.0
    source: str | None = None
    tags: list[str] = field(default_factory=list)
    embedding: list[float] | None = None  # 向量嵌入（用于语义搜索）
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "content": self.content,
            "timestamp": self.timestamp,
            "type": self.type,
            "importance": self.importance,
            "source": self.source,
            "tags": self.tags,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryEntry":
        return cls(
            content=data["content"],
            timestamp=data["timestamp"],
            type=data.get("type", "general"),
            importance=data.get("importance", 1.0),
            source=data.get("source"),
            tags=data.get("tags", []),
        )


# ============================================================
# 短期记忆 (ConversationMemory)
# ============================================================

class ConversationMemory:
    """
    对话短期记忆 - 管理当前对话的上下文
    
    Claude Code 使用 ConversationMemory 跟踪：
    - 当前任务的中间状态
    - 最近 Tool 调用的结果
    - 用户偏好和上下文
    
    参考: src/memdir/conversationMemory.ts
    """
    
    def __init__(self, max_size: int = 100):
        """
        初始化对话记忆
        
        Args:
            max_size: 最大记忆条目数，超过后删除最旧的
        """
        self.max_size = max_size
        self._entries: list[MemoryEntry] = []
        self._context: dict[str, Any] = {}  # 键值上下文
    
    def add(
        self,
        content: str,
        memory_type: str = "context",
        importance: float = 1.0,
        tags: list[str] | None = None
    ) -> None:
        """
        添加记忆条目
        
        在 Claude Code 中，对话中的重要信息会被自动提取：
        - 用户明确说明的偏好
        - Tool 执行的关键结果
        - 任务状态的变更
        """
        entry = MemoryEntry(
            content=content,
            timestamp=time.time(),
            type=memory_type,
            importance=importance,
            tags=tags or []
        )
        
        self._entries.append(entry)
        
        # 维护大小限制
        if len(self._entries) > self.max_size:
            self._entries.pop(0)
    
    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        """获取最近的 n 条记忆"""
        return self._entries[-n:]
    
    def set_context(self, key: str, value: Any) -> None:
        """设置键值上下文"""
        self._context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """获取上下文值"""
        return self._context.get(key, default)
    
    def get_context_summary(self) -> str:
        """
        生成上下文摘要 - 供 Agent 使用
        
        Claude Code 会将短期记忆注入到 system prompt 中
        """
        if not self._entries and not self._context:
            return ""
        
        lines = ["## Current Context\n"]
        
        # 添加上下文键值
        if self._context:
            lines.append("### Variables:")
            for k, v in self._context.items():
                lines.append(f"- {k}: {v}")
        
        # 添加最近的记忆
        if self._entries:
            lines.append("\n### Recent Memories:")
            for entry in self._entries[-5:]:
                lines.append(f"- [{entry.type}] {entry.content}")
        
        return "\n".join(lines)
    
    def clear(self) -> None:
        """清空对话记忆"""
        self._entries.clear()
        self._context.clear()


# ============================================================
# 长期记忆 (PersistentMemory)
# ============================================================

class PersistentMemory:
    """
    持久化记忆 - 跨会话存储重要信息
    
    Claude Code 将重要记忆存储在 ~/.claude/memdir/ 目录：
    - memories.jsonl: 每行一个记忆条目
    - index.json: 记忆索引
    - skills/: 技能定义
    
    参考: src/memdir/memdir.ts
    """
    
    def __init__(self, memdir_path: str | None = None):
        """
        初始化持久化记忆
        
        Args:
            memdir_path: 记忆目录路径，默认 ~/.claude/memdir/
        """
        if memdir_path:
            self.memdir = Path(memdir_path)
        else:
            self.memdir = Path.home() / ".claude" / "memdir"
        
        self.memdir.mkdir(parents=True, exist_ok=True)
        self.memories_file = self.memdir / "memories.jsonl"
        self.index_file = self.memdir / "index.json"
        
        # 内存缓存
        self._cache: list[MemoryEntry] = []
        self._load_from_disk()
    
    def _load_from_disk(self) -> None:
        """从磁盘加载记忆"""
        if not self.memories_file.exists():
            return
        
        self._cache.clear()
        with open(self.memories_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data = json.loads(line)
                        self._cache.append(MemoryEntry.from_dict(data))
                    except json.JSONDecodeError:
                        continue
    
    def _save_to_disk(self) -> None:
        """保存记忆到磁盘"""
        with open(self.memories_file, "w", encoding="utf-8") as f:
            for entry in self._cache:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
    
    def store(
        self,
        content: str,
        memory_type: str = "general",
        importance: float = 1.0,
        source: str | None = None,
        tags: list[str] | None = None
    ) -> None:
        """
        存储记忆到持久化存储
        
        Claude Code 会在以下情况存储记忆：
        1. 用户明确说 "记住..."
        2. 自动提取（需要用户确认）
        3. 任务完成后的经验总结
        """
        entry = MemoryEntry(
            content=content,
            timestamp=time.time(),
            type=memory_type,
            importance=importance,
            source=source,
            tags=tags or []
        )
        
        self._cache.append(entry)
        self._save_to_disk()
    
    def search(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """
        搜索记忆 - 简单关键词匹配
        
        真实 Claude Code 使用向量嵌入进行语义搜索：
        - embed text -> vector
        - cosine similarity
        - return top-k results
        
        参考: src/memdir/memdirIndex.ts
        """
        results = []
        query_lower = query.lower()
        
        for entry in reversed(self._cache):  # 最近的优先
            if query_lower in entry.content.lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_all(self) -> list[MemoryEntry]:
        """获取所有记忆"""
        return self._cache.copy()
    
    def get_by_type(self, memory_type: str) -> list[MemoryEntry]:
        """按类型获取记忆"""
        return [e for e in self._cache if e.type == memory_type]
    
    def delete(self, index: int) -> bool:
        """删除指定索引的记忆"""
        if 0 <= index < len(self._cache):
            self._cache.pop(index)
            self._save_to_disk()
            return True
        return False


# ============================================================
# 经验记忆 (ExperienceMemory)
# ============================================================

class ExperienceMemory:
    """
    经验记忆 - 从任务中学习和提取经验
    
    Claude Code 的经验系统：
    1. 任务完成后，分析对话
    2. 提取有用的模式/技巧
    3. 存储为可复用的经验
    4. 下次遇到类似任务时应用
    
    参考: src/services/extractMemories/
    """
    
    def __init__(self, persistent: PersistentMemory | None = None):
        self.persistent = persistent or PersistentMemory()
        
        # 经验模式
        self.patterns: list[dict[str, Any]] = []
    
    def extract_from_task(
        self,
        task_description: str,
        conversation: list[dict[str, Any]],
        outcome: str
    ) -> list[str]:
        """
        从任务中提取经验
        
        Claude Code 分析对话，提取：
        - 成功使用的 Tool 组合
        - 常见的错误和解决方法
        - 有效的提示词模式
        
        这是一个简化版本，真实实现使用 LLM 来分析。
        
        Returns:
            提取的经验列表
        """
        experiences = []
        
        # 简化：直接存储任务结果作为经验
        if outcome == "success":
            exp = f"Successfully completed: {task_description}"
            experiences.append(exp)
            self.persistent.store(
                content=exp,
                memory_type="skill",
                importance=0.8,
                source="experience"
            )
        
        return experiences
    
    def suggest_for_task(self, task: str) -> list[str]:
        """
        根据任务提供经验建议
        
        Claude Code 在开始新任务时：
        1. 分析任务类型
        2. 检索相关经验
        3. 将经验注入到上下文中
        """
        memories = self.persistent.search(task, limit=3)
        return [m.content for m in memories]


# ============================================================
# 记忆管理器 (Memory Manager)
# ============================================================

class MemoryManager:
    """
    统一记忆管理器 - 整合所有记忆系统
    
    Claude Code 的完整记忆架构:
    ```
    ┌─────────────────────────────────────────┐
    │          Memory Manager                 │
    ├─────────────────────────────────────────┤
    │  ┌─────────────────────────────────┐   │
    │  │  Conversation Memory (短期)      │   │
    │  │  - 当前对话上下文                │   │
    │  │  - 实时 Tool 结果                │   │
    │  └─────────────────────────────────┘   │
    │  ┌─────────────────────────────────┐   │
    │  │  Persistent Memory (长期)        │   │
    │  │  - ~/.claude/memdir/            │   │
    │  │  - 跨会话持久化                  │   │
    │  └─────────────────────────────────┘   │
    │  ┌─────────────────────────────────┐   │
    │  │  Experience Memory (经验)       │   │
    │  │  - 任务模式                      │   │
    │  │  - 学习改进                      │   │
    │  └─────────────────────────────────┘   │
    └─────────────────────────────────────────┘
    ```
    
    参考: src/memdir/ 整体架构
    """
    
    def __init__(self, memdir_path: str | None = None):
        # 初始化各个记忆组件
        self.conversation = ConversationMemory()
        self.persistent = PersistentMemory(memdir_path)
        self.experience = ExperienceMemory(self.persistent)
    
    def get_system_prompt_context(self) -> str:
        """
        生成注入到 system prompt 的上下文
        
        Claude Code 在每次 LLM 调用前注入：
        1. 短期记忆摘要
        2. 相关长期记忆
        3. 经验建议
        """
        parts = []
        
        # 短期记忆
        context = self.conversation.get_context_summary()
        if context:
            parts.append(context)
        
        # 从经验中获取建议
        # (实际应该根据任务动态获取)
        
        return "\n\n".join(parts) if parts else ""
    
    def remember(self, content: str, memory_type: str = "general") -> None:
        """快捷方法：存储记忆到持久化存储"""
        self.persistent.store(content, memory_type=memory_type)
    
    def recall(self, query: str) -> list[str]:
        """快捷方法：搜索记忆"""
        memories = self.persistent.search(query)
        return [m.content for m in memories]


# ============================================================
# 导出
# ============================================================

__all__ = [
    'MemoryEntry',
    'ConversationMemory',
    'PersistentMemory',
    'ExperienceMemory',
    'MemoryManager',
]
