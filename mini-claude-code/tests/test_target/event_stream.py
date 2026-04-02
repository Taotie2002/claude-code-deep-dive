"""
异步事件流处理模块
用于测试 mini-claude-code 的复杂代码审计能力
"""
import asyncio
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import time
import threading
import weakref


T = TypeVar('T')


class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Event:
    """事件"""
    event_id: str
    event_type: str
    data: Any
    timestamp: float
    priority: EventPriority = EventPriority.NORMAL


class BufferOverflowError(Exception):
    """缓冲区溢出"""
    pass


class EventBuffer(Generic[T]):
    """
    事件缓冲区
    BUG 1: 缓冲区满时丢弃旧事件而不是拒绝新事件
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._buffer: deque = deque(maxlen=max_size)  # BUG: 自动丢弃旧数据
        self._overflow_count = 0
    
    def put(self, item: T) -> bool:
        """
        放入事件
        BUG: deque(maxlen=max_size) 会自动丢弃最旧的item
        这导致高优先级事件可能被丢弃
        """
        self._buffer.append(item)
        
        # 永远返回 True，即使丢失了旧数据
        return True
    
    def get(self) -> Optional[T]:
        """获取事件"""
        if len(self._buffer) == 0:
            return None
        return self._buffer.popleft()
    
    def get_all(self) -> List[T]:
        """获取所有事件"""
        events = list(self._buffer)
        self._buffer.clear()
        return events
    
    def size(self) -> int:
        """获取缓冲区大小"""
        return len(self._buffer)
    
    def is_empty(self) -> bool:
        """是否为空"""
        return len(self._buffer) == 0


class EventStream:
    """
    事件流处理器
    BUG 2: 错误恢复机制会在某些情况下失效
    BUG 3: 死锁风险 - 同步和异步处理混用
    """
    
    def __init__(self, stream_id: str, buffer_size: int = 1000):
        self.stream_id = stream_id
        self.buffer = EventBuffer[Event](buffer_size)
        self._handlers: Dict[str, List[Callable]] = {}
        self._error_handlers: List[Callable] = []
        self._running = False
        self._paused = False
        self._processing_lock = asyncio.Lock()  # BUG: 混用锁
        self._sync_lock = threading.Lock()  # BUG: 同步锁可能导致死锁
        self._retry_policy: Dict[str, int] = {}
        self._stats = {
            "processed": 0,
            "dropped": 0,
            "errors": 0,
            "retries": 0
        }
    
    def add_handler(self, event_type: str, handler: Callable):
        """添加事件处理器"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def remove_handler(self, event_type: str, handler: Callable):
        """移除事件处理器"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    def add_error_handler(self, handler: Callable):
        """添加错误处理器"""
        self._error_handlers.append(handler)
    
    def set_retry_policy(self, event_type: str, max_retries: int):
        """设置重试策略"""
        self._retry_policy[event_type] = max_retries
    
    async def emit(self, event: Event):
        """发送事件"""
        if self._paused:
            # BUG: 暂停时不应该继续放行
            pass
        
        # BUG: 这里应该在缓冲区满时拒绝而不是丢弃
        self.buffer.put(event)
    
    async def emit_batch(self, events: List[Event]):
        """批量发送事件"""
        for event in events:
            await self.emit(event)
    
    async def process_next(self) -> Optional[Any]:
        """处理下一个事件"""
        async with self._processing_lock:
            event = self.buffer.get()
            if event is None:
                return None
            
            try:
                result = await self._process_event(event)
                self._stats["processed"] += 1
                return result
            except Exception as e:
                self._stats["errors"] += 1
                return await self._handle_error(event, e)
    
    async def _process_event(self, event: Event) -> Any:
        """处理单个事件"""
        if event.event_type not in self._handlers:
            return None
        
        handlers = self._handlers[event.event_type]
        results = []
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(event)
                else:
                    # BUG: 同步handler在异步上下文中直接调用可能有问题
                    with self._sync_lock:  # BUG: 这里可能导致死锁
                        result = handler(event)
                results.append(result)
            except Exception as e:
                raise
        
        return results if len(results) > 1 else results[0] if results else None
    
    async def _handle_error(self, event: Event, error: Exception) -> Any:
        """
        错误处理
        BUG: 重试逻辑在某些情况下会失效
        """
        event_type = event.event_type
        max_retries = self._retry_policy.get(event_type, 0)
        
        if max_retries > 0:
            self._stats["retries"] += 1
            # BUG: 没有实现真正的重试逻辑，只是记录了次数
            # BUG: 重试时没有考虑指数退避
        
        # 调用错误处理器
        for error_handler in self._error_handlers:
            try:
                if asyncio.iscoroutinefunction(error_handler):
                    await error_handler(event, error)
                else:
                    error_handler(event, error)
            except Exception:
                pass
        
        return None
    
    async def start_processing(self):
        """启动处理循环"""
        self._running = True
        while self._running:
            try:
                await self.process_next()
                await asyncio.sleep(0.001)
            except Exception as e:
                print(f"Processing error: {e}")
    
    def stop_processing(self):
        """停止处理"""
        self._running = False
    
    def pause(self):
        """暂停"""
        self._paused = True
    
    def resume(self):
        """恢复"""
        self._paused = False
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()


class MultiStreamProcessor:
    """
    多事件流处理器
    BUG 4: 资源泄露 - 不跟踪创建的处理任务
    """
    
    def __init__(self):
        self._streams: Dict[str, EventStream] = {}
        self._tasks: List[asyncio.Task] = []  # BUG: 不清理已完成的任务
        self._running = False
    
    def create_stream(self, stream_id: str, buffer_size: int = 1000) -> EventStream:
        """创建事件流"""
        stream = EventStream(stream_id, buffer_size)
        self._streams[stream_id] = stream
        return stream
    
    def get_stream(self, stream_id: str) -> Optional[EventStream]:
        """获取事件流"""
        return self._streams.get(stream_id)
    
    async def start_all(self):
        """启动所有事件流"""
        self._running = True
        for stream_id, stream in self._streams.items():
            # BUG: 创建任务但不保存引用给外部
            task = asyncio.create_task(stream.start_processing())
            self._tasks.append(task)  # BUG: 任务完成后不清理
    
    async def stop_all(self):
        """停止所有事件流"""
        self._running = False
        for stream in self._streams.values():
            stream.stop_processing()
        
        # BUG: 不等待任务完成就退出
        # BUG: 不清理 self._tasks
    
    def get_stream_stats(self) -> Dict[str, Dict[str, int]]:
        """获取所有流的统计"""
        return {sid: stream.get_stats() for sid, stream in self._streams.items()}


class EventAggregator:
    """
    事件聚合器
    BUG 5: 内存泄漏 - 聚合状态无限增长
    """
    
    def __init__(self, aggregation_window: float = 60.0):
        self.aggregation_window = aggregation_window
        self._aggregations: Dict[str, List[Event]] = {}  # BUG: 只增不减
        self._timestamps: Dict[str, List[float]] = {}  # BUG: 只增不减
    
    async def aggregate(self, event: Event):
        """聚合事件"""
        key = event.event_type
        
        if key not in self._aggregations:
            self._aggregations[key] = []
            self._timestamps[key] = []
        
        self._aggregations[key].append(event)
        self._timestamps[key].append(event.timestamp)
        
        # BUG: 不清理过期数据
    
    def get_aggregated(self, event_type: str) -> List[Event]:
        """获取聚合的事件"""
        return self._aggregations.get(event_type, [])
    
    def get_count(self, event_type: str) -> int:
        """获取事件数量"""
        return len(self._aggregations.get(event_type, []))


# 便捷函数
def create_event_stream(stream_id: str) -> EventStream:
    """创建事件流"""
    return EventStream(stream_id)


def emit_simple(stream: EventStream, event_type: str, data: Any):
    """简单发送事件"""
    event = Event(
        event_id=str(id(data)),
        event_type=event_type,
        data=data,
        timestamp=time.time()
    )
    asyncio.create_task(stream.emit(event))


# 测试辅助
async def run_stream_demo():
    """运行事件流演示"""
    processor = MultiStreamProcessor()
    
    stream = processor.create_stream("test_stream")
    
    async def sample_handler(event: Event):
        print(f"Received: {event.event_type}")
    
    stream.add_handler("test", sample_handler)
    
    await processor.start_all()
    
    # 发送测试事件
    for i in range(10):
        await stream.emit(Event(
            event_id=str(i),
            event_type="test",
            data={"index": i},
            timestamp=time.time()
        ))
        await asyncio.sleep(0.1)
    
    await asyncio.sleep(1)
    await processor.stop_all()
    
    print(f"Stats: {stream.get_stats()}")


if __name__ == "__main__":
    asyncio.run(run_stream_demo())
