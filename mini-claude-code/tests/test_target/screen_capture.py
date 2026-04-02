"""
屏幕录制工具模拟 - 包含故意植入的Bug
用于测试 mini-claude-code 的复杂代码审计能力
"""
import asyncio
import threading
import time
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum
import uuid


class RecordingState(Enum):
    IDLE = "idle"
    INITIALIZING = "initializing"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class Frame:
    """视频帧"""
    frame_id: str
    timestamp: float
    data: bytes
    width: int
    height: int


@dataclass
class RecordingSession:
    """录制会话"""
    session_id: str
    state: RecordingState
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    frame_count: int = 0
    error_message: Optional[str] = None


class ScreenCaptureError(Exception):
    """屏幕捕获异常"""
    pass


class CaptureDevice:
    """
    模拟底层捕获设备API
    BUG 1: 内存泄漏 - frame_buffer 字典只添加不清理
    """
    
    def __init__(self, device_id: str = "screen_0"):
        self.device_id = device_id
        self.frame_buffer: Dict[str, Frame] = {}  # BUG: 无限增长
        self._capture_count = 0
    
    def capture_frame(self) -> Frame:
        """捕获单帧"""
        frame_id = str(uuid.uuid4())
        self._capture_count += 1
        
        frame = Frame(
            frame_id=frame_id,
            timestamp=time.time(),
            data=b"fake_image_data_" + str(self._capture_count).encode(),
            width=1920,
            height=1080
        )
        
        # BUG: 永远不清理 buffer
        self.frame_buffer[frame_id] = frame
        
        return frame
    
    def get_buffer_size(self) -> int:
        """获取缓冲区大小"""
        return len(self.frame_buffer)


class EventBus:
    """事件总线 - 异步事件发布"""
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
    
    def subscribe(self, event_type: str, callback: Callable):
        """订阅事件"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """取消订阅"""
        if event_type in self._subscribers:
            self._subscribers[event_type].remove(callback)
    
    async def publish(self, event_type: str, data: Any):
        """发布事件到队列"""
        await self._event_queue.put({"type": event_type, "data": data})
    
    async def process_events(self):
        """处理事件队列"""
        self._running = True
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)
                if event["type"] in self._subscribers:
                    for callback in self._subscribers[event["type"]]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event["data"])
                            else:
                                callback(event["data"])
                        except Exception as e:
                            print(f"Event handler error: {e}")
            except asyncio.TimeoutError:
                continue
    
    def stop(self):
        """停止事件处理"""
        self._running = False


class ScreenRecorder:
    """
    屏幕录制器主类
    BUG 2: 竞态条件 - 状态检查与修改不是原子操作
    BUG 3: 资源泄露 - 停止录制时没有清理所有资源
    """
    
    def __init__(self, output_path: str = "./output.mp4"):
        self.output_path = output_path
        self.device = CaptureDevice()
        self.event_bus = EventBus()
        self.session: Optional[RecordingSession] = None
        self._state_lock = threading.Lock()
        self._recording_task: Optional[asyncio.Task] = None
        self._frame_handlers: List[Callable] = []
    
    @property
    def state(self) -> RecordingState:
        """获取当前状态"""
        if self.session is None:
            return RecordingState.IDLE
        return self.session.state
    
    def _set_state(self, new_state: RecordingState):
        """设置状态 - BUG: 没有锁保护"""
        if self.session is None:
            return
        self.session.state = new_state
    
    async def start_recording(self, fps: int = 30) -> str:
        """
        开始录制
        BUG: 状态转换没有正确的状态机验证
        """
        if self.session is not None and self.session.state == RecordingState.RECORDING:
            raise ScreenCaptureError("Already recording")
        
        # BUG: 没有检查是否从非法状态转换
        session_id = str(uuid.uuid4())
        self.session = RecordingSession(
            session_id=session_id,
            state=RecordingState.INITIALIZING
        )
        
        # 初始化完成直接进入 RECORDING
        self.session.state = RecordingState.RECORDING  # BUG: 跳过了 INITIALIZING
        self.session.start_time = time.time()
        
        self._recording_task = asyncio.create_task(self._recording_loop(fps))
        
        await self.event_bus.publish("recording_started", {
            "session_id": session_id
        })
        
        return session_id
    
    async def _recording_loop(self, fps: float):
        """录制循环"""
        frame_interval = 1.0 / fps
        
        try:
            while self.session and self.session.state == RecordingState.RECORDING:
                frame = self.device.capture_frame()
                
                # 触发 frame_ready 事件
                await self.event_bus.publish("frame_ready", {
                    "frame": frame,
                    "session_id": self.session.session_id
                })
                
                # 调用 frame handlers
                for handler in self._frame_handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(frame)
                        else:
                            handler(frame)
                    except Exception as e:
                        await self.event_bus.publish("recording_error", {
                            "error": str(e),
                            "session_id": self.session.session_id
                        })
                
                self.session.frame_count += 1
                await asyncio.sleep(frame_interval)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if self.session:
                self.session.error_message = str(e)
                self.session.state = RecordingState.ERROR
            await self.event_bus.publish("recording_error", {
                "error": str(e),
                "session_id": self.session.session_id if self.session else None
            })
    
    async def pause_recording(self):
        """暂停录制"""
        # BUG: 没有检查当前状态是否为 RECORDING
        if self.session is None:
            raise ScreenCaptureError("No active session")
        
        self.session.state = RecordingState.PAUSED
        await self.event_bus.publish("recording_paused", {
            "session_id": self.session.session_id
        })
    
    async def resume_recording(self):
        """恢复录制"""
        # BUG: 没有检查当前状态是否为 PAUSED
        if self.session is None:
            raise ScreenCaptureError("No active session")
        
        self.session.state = RecordingState.RECORDING
        await self.event_bus.publish("recording_resumed", {
            "session_id": self.session.session_id
        })
    
    async def stop_recording(self) -> Dict[str, Any]:
        """
        停止录制
        BUG 3: 资源泄露 - 不清理 device.frame_buffer
        """
        if self.session is None:
            raise ScreenCaptureError("No active session")
        
        self.session.state = RecordingState.STOPPING
        self.session.end_time = time.time()
        
        # 取消录制任务
        if self._recording_task:
            self._recording_task.cancel()
            try:
                await self._recording_task
            except asyncio.CancelledError:
                pass
        
        self.session.state = RecordingState.IDLE
        
        result = {
            "session_id": self.session.session_id,
            "duration": self.session.end_time - self.session.start_time,
            "frame_count": self.session.frame_count,
            "output_path": self.output_path
        }
        
        # BUG: 没有清理 self.device.frame_buffer
        # BUG: 没有清理 self._frame_handlers
        # BUG: 没有调用 self.event_bus.stop()
        
        await self.event_bus.publish("recording_stopped", result)
        
        return result
    
    def add_frame_handler(self, handler: Callable):
        """添加帧处理器"""
        self._frame_handlers.append(handler)
    
    def remove_frame_handler(self, handler: Callable):
        """移除帧处理器"""
        if handler in self._frame_handlers:
            self._frame_handlers.remove(handler)


class RecordingManager:
    """
    录制会话管理器
    BUG 4: 会话管理混乱 - 没有妥善处理并发会话
    """
    
    def __init__(self):
        self._recorders: Dict[str, ScreenRecorder] = {}
        self._lock = threading.Lock()
    
    def create_recorder(self, session_id: str, output_path: str = "./output.mp4") -> ScreenRecorder:
        """创建录制器"""
        # BUG: 没有检查 session_id 是否已存在
        recorder = ScreenRecorder(output_path)
        self._recorders[session_id] = recorder
        return recorder
    
    def get_recorder(self, session_id: str) -> Optional[ScreenRecorder]:
        """获取录制器"""
        return self._recorders.get(session_id)
    
    async def close_session(self, session_id: str):
        """关闭会话"""
        recorder = self._recorders.get(session_id)
        if recorder:
            await recorder.stop_recording()
            # BUG: 清理 device.frame_buffer
            recorder.device.frame_buffer.clear()  # 手动清理，但 stop_recording 里没有
            del self._recorders[session_id]
    
    def list_active_sessions(self) -> List[str]:
        """列出活跃会话"""
        return list(self._recorders.keys())


# 辅助函数
def create_default_recorder() -> ScreenRecorder:
    """创建默认配置录制器"""
    return ScreenRecorder(output_path="/tmp/screen_recording.mp4")


async def quick_record(duration: float = 5.0) -> Dict[str, Any]:
    """快速录制辅助函数"""
    recorder = create_default_recorder()
    
    session_id = await recorder.start_recording(fps=30)
    await asyncio.sleep(duration)
    result = await recorder.stop_recording()
    
    return result
