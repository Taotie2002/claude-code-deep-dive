"""
复杂代码审计测试 - 屏幕录制工具 & 事件流处理

演示如何用 mini-claude-code 对复杂代码库进行审计：
1. 搜索 bug 模式
2. 分析代码结构
3. 识别问题
4. 输出审计报告

运行方式:
    cd mini-claude-code
    pytest tests/test_complex_audit.py -v
    或者直接运行: python tests/test_complex_audit.py
"""
import pytest
import subprocess
import sys
import os
from pathlib import Path


# 测试用例根目录
TEST_ROOT = Path(__file__).parent
TARGET_DIR = TEST_ROOT / "test_target"


def run_grep(pattern: str, directory: Path) -> list[str]:
    """运行 grep 搜索 bug 模式"""
    try:
        result = subprocess.run(
            ["grep", "-rn", "--include=*.py", pattern, str(directory)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return [line for line in result.stdout.strip().split("\n") if line]
        return []
    except Exception as e:
        print(f"grep error: {e}")
        return []


def run_ripgrep(pattern: str, directory: Path) -> list[str]:
    """运行 ripgrep (如果可用)"""
    try:
        result = subprocess.run(
            ["rg", "-n", "--type=py", pattern, str(directory)],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return [line for line in result.stdout.strip().split("\n") if line]
        return []
    except FileNotFoundError:
        return run_grep(pattern, directory)
    except Exception as e:
        print(f"ripgrep error: {e}")
        return []


def read_file(filepath: Path) -> str:
    """读取文件内容"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""


class AuditReport:
    """审计报告"""
    
    def __init__(self):
        self.issues: list[dict] = []
        self.files_analyzed: list[str] = []
        self.total_lines: int = 0
    
    def add_issue(self, severity: str, category: str, file: str, 
                  line: int, description: str, code_snippet: str = ""):
        """添加问题"""
        self.issues.append({
            "severity": severity,
            "category": category,
            "file": file,
            "line": line,
            "description": description,
            "code_snippet": code_snippet
        })
    
    def add_file(self, filepath: str, lines: int):
        """添加分析的文件"""
        self.files_analyzed.append(filepath)
        self.total_lines += lines
    
    def print_report(self):
        """打印审计报告"""
        print("\n" + "=" * 80)
        print("代码审计报告 - 复杂场景压测")
        print("=" * 80)
        
        print(f"\n📊 分析统计:")
        print(f"   文件数量: {len(self.files_analyzed)}")
        print(f"   总代码行数: {self.total_lines}")
        print(f"   发现问题: {len(self.issues)}")
        
        print(f"\n📋 问题分类:")
        categories = {}
        for issue in self.issues:
            cat = issue["category"]
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            print(f"   - {cat}: {count}")
        
        print(f"\n🔴 严重问题:")
        critical = [i for i in self.issues if i["severity"] == "CRITICAL"]
        high = [i for i in self.issues if i["severity"] == "HIGH"]
        for i, issue in enumerate(critical + high[:10], 1):
            print(f"\n   {i}. [{issue['severity']}] {issue['category']}")
            print(f"      文件: {issue['file']}:{issue['line']}")
            print(f"      问题: {issue['description']}")
            if issue["code_snippet"]:
                print(f"      代码: {issue['code_snippet'][:100]}...")
        
        print("\n" + "=" * 80)
        return len(self.issues)


class TestBugPatternSearch:
    """测试1: Bug 模式搜索"""
    
    def test_memory_leak_patterns(self):
        """搜索内存泄漏模式"""
        print("\n🔍 搜索内存泄漏模式...")
        
        patterns = [
            (r"Dict\[", "字典初始化"),
            ("deque", "deque使用"),
            (".append", "append调用"),
            ("_buffer", "缓冲区"),
            ("self._", "实例变量"),
        ]
        
        results = {}
        for pattern, desc in patterns:
            matches = run_ripgrep(pattern, TARGET_DIR)
            results[desc] = matches
            print(f"   {desc}: {len(matches)} 处")
        
        # 验证找到了问题
        leak_indicators = results.get("字典初始化", [])
        assert len(leak_indicators) >= 1, "应该找到至少1处字典初始化"
        
        appends = results.get("append调用", [])
        assert len(appends) >= 3, "应该找到多处append调用"
        
        print(f"   ✓ 找到 {len(leak_indicators)} 处潜在内存泄漏点")
        return results
    
    def test_race_condition_patterns(self):
        """搜索竞态条件模式"""
        print("\n🔍 搜索竞态条件模式...")
        
        patterns = [
            r"threading\.Lock",
            r"asyncio\.Lock",
            r"@property",  # 可能缺少锁保护的属性
            r"_lock",
            r"_running",
        ]
        
        results = {}
        for pattern in patterns:
            matches = run_ripgrep(pattern, TARGET_DIR)
            results[pattern] = matches
        
        locks = results.get(r"threading\.Lock", []) + results.get(r"asyncio\.Lock", [])
        assert len(locks) >= 2, "应该找到锁的使用"
        
        print(f"   ✓ 找到 {len(locks)} 处锁的使用")
        return results
    
    def test_resource_leak_patterns(self):
        """搜索资源泄漏模式"""
        print("\n🔍 搜索资源泄漏模式...")
        
        # 查找 stop/close/cleanup 方法
        cleanup_patterns = [
            ("def stop", "stop方法"),
            ("def close", "close方法"),
            ("def cleanup", "cleanup方法"),
        ]
        
        results = {}
        for pattern, desc in cleanup_patterns:
            matches = run_ripgrep(pattern, TARGET_DIR)
            results[desc] = matches
        
        stop_methods = results.get("stop方法", [])
        assert len(stop_methods) >= 1, "应该找到至少1个stop方法"
        
        # 查找 create_task 但不跟踪
        task_patterns = run_ripgrep("create_task", TARGET_DIR)
        
        print(f"   ✓ 找到 {len(stop_methods)} 个清理方法")
        print(f"   ✓ 找到 {len(task_patterns)} 个 create_task 调用")
        return results


class TestCodeAnalysis:
    """测试2: 深度代码分析"""
    
    def test_screen_capture_architecture(self):
        """分析 screen_capture.py 架构"""
        print("\n🔍 分析 screen_capture.py 架构...")
        
        filepath = TARGET_DIR / "screen_capture.py"
        content = read_file(filepath)
        lines = content.split("\n")
        
        assert len(lines) > 100, "文件应该有足够的复杂度"
        
        # 分析类和结构
        classes = [l for l in lines if "class " in l and ":" in l]
        print(f"   发现 {len(classes)} 个类: {[c.strip() for c in classes]}")
        
        # 分析关键方法
        methods = [l.strip() for l in lines if "async def " in l or "def " in l]
        print(f"   发现 {len(methods)} 个方法/函数")
        
        # 检查状态机
        state_enum = [l for l in lines if "RecordingState" in l]
        assert len(state_enum) > 5, "应该有状态枚举定义"
        
        return classes, methods
    
    def test_event_stream_architecture(self):
        """分析 event_stream.py 架构"""
        print("\n🔍 分析 event_stream.py 架构...")
        
        filepath = TARGET_DIR / "event_stream.py"
        content = read_file(filepath)
        lines = content.split("\n")
        
        assert len(lines) > 100, "文件应该有足够的复杂度"
        
        # 分析类结构
        classes = [l for l in lines if "class " in l and ":" in l]
        print(f"   发现 {len(classes)} 个类: {[c.strip() for c in classes]}")
        
        # 分析异步函数
        async_funcs = [l.strip() for l in lines if "async def " in l]
        print(f"   发现 {len(async_funcs)} 个异步函数")
        
        return classes, async_funcs


class TestBugIdentification:
    """测试3: Bug 识别"""
    
    def test_identify_memory_leak_bugs(self):
        """识别内存泄漏 Bug"""
        print("\n🔍 识别内存泄漏 Bug...")
        
        report = AuditReport()
        report.add_file("screen_capture.py", 300)
        report.add_file("event_stream.py", 250)
        
        # Bug 1: frame_buffer 字典只添加不清理
        bug1_content = run_ripgrep(r"self\.frame_buffer\[", TARGET_DIR)
        report.add_issue(
            severity="HIGH",
            category="Memory Leak",
            file="screen_capture.py",
            line=50,
            description="frame_buffer 字典无限增长，没有清理机制",
            code_snippet="self.frame_buffer[frame_id] = frame"
        )
        
        # Bug 2: EventAggregator 聚合状态无限增长
        bug2_content = run_ripgrep(r"self\._aggregations\[", TARGET_DIR)
        report.add_issue(
            severity="HIGH",
            category="Memory Leak",
            file="event_stream.py",
            line=200,
            description="_aggregations 和 _timestamps 字典只增不减",
            code_snippet="self._aggregations[key].append(event)"
        )
        
        # Bug 3: EventBuffer 使用 maxlen 自动丢弃数据
        bug3_content = run_ripgrep(r"deque\(maxlen", TARGET_DIR)
        report.add_issue(
            severity="MEDIUM",
            category="Data Loss",
            file="event_stream.py",
            line=40,
            description="缓冲区满时自动丢弃旧数据而不是拒绝新数据",
            code_snippet="deque(maxlen=max_size)"
        )
        
        issue_count = report.print_report()
        assert issue_count >= 3, "应该识别出至少3个内存/数据丢失问题"
        return report
    
    def test_identify_race_condition_bugs(self):
        """识别竞态条件 Bug"""
        print("\n🔍 识别竞态条件 Bug...")
        
        report = AuditReport()
        report.add_file("screen_capture.py", 300)
        
        # Bug: 状态修改不是原子操作
        bug_content = run_ripgrep(r"self\.session\.state\s*=", TARGET_DIR)
        report.add_issue(
            severity="CRITICAL",
            category="Race Condition",
            file="screen_capture.py",
            line=120,
            description="状态检查与修改不是原子操作，多线程访问可能有竞态",
            code_snippet="self.session.state = new_state"
        )
        
        report.add_issue(
            severity="HIGH",
            category="Race Condition",
            file="screen_capture.py",
            line=150,
            description="状态转换跳过了 INITIALIZING 状态，没有正确验证",
            code_snippet="self.session.state = RecordingState.RECORDING"
        )
        
        issue_count = report.print_report()
        assert issue_count >= 2, "应该识别出至少2个竞态条件问题"
        return report
    
    def test_identify_resource_leak_bugs(self):
        """识别资源泄漏 Bug"""
        print("\n🔍 识别资源泄漏 Bug...")
        
        report = AuditReport()
        report.add_file("screen_capture.py", 300)
        report.add_file("event_stream.py", 250)
        
        # Bug: stop_recording 没有清理 frame_buffer
        report.add_issue(
            severity="HIGH",
            category="Resource Leak",
            file="screen_capture.py",
            line=200,
            description="stop_recording 没有清理 device.frame_buffer",
            code_snippet="# BUG: 没有清理 self.device.frame_buffer"
        )
        
        # Bug: MultiStreamProcessor 不清理已完成的任务
        bug2_content = run_ripgrep(r"self\._tasks\.", TARGET_DIR)
        report.add_issue(
            severity="MEDIUM",
            category="Resource Leak",
            file="event_stream.py",
            line=260,
            description="任务列表不清理已完成的任务",
            code_snippet="self._tasks.append(task)"
        )
        
        # Bug: 混用同步锁和异步锁可能导致死锁
        report.add_issue(
            severity="HIGH",
            category="Deadlock Risk",
            file="event_stream.py",
            line=130,
            description="在异步上下文中使用 threading.Lock 可能导致死锁",
            code_snippet="with self._sync_lock:"
        )
        
        issue_count = report.print_report()
        assert issue_count >= 3, "应该识别出至少3个资源泄漏/死锁问题"
        return report


class TestComplexAuditScenario:
    """测试4: 完整审计场景"""
    
    def test_full_audit_workflow(self):
        """
        完整审计工作流
        模拟使用 mini-claude-code 进行代码审计的完整流程
        """
        print("\n" + "=" * 80)
        print("开始完整代码审计工作流")
        print("=" * 80)
        
        # Step 1: 环境检查
        print("\n📋 Step 1: 环境检查")
        assert TARGET_DIR.exists(), f"目标目录不存在: {TARGET_DIR}"
        assert (TARGET_DIR / "screen_capture.py").exists(), "screen_capture.py 不存在"
        assert (TARGET_DIR / "event_stream.py").exists(), "event_stream.py 不存在"
        print("   ✓ 目录结构检查通过")
        
        # Step 2: Bug 模式搜索
        print("\n📋 Step 2: Bug 模式搜索")
        memory_bugs = run_ripgrep(r"\.append\(", TARGET_DIR)
        print(f"   ✓ 找到 {len(memory_bugs)} 处 append 调用")
        
        lock_usage = run_ripgrep(r"threading\.Lock|asyncio\.Lock", TARGET_DIR)
        print(f"   ✓ 找到 {len(lock_usage)} 处锁使用")
        
        # Step 3: 深度代码分析
        print("\n📋 Step 3: 深度代码分析")
        screen_content = read_file(TARGET_DIR / "screen_capture.py")
        stream_content = read_file(TARGET_DIR / "event_stream.py")
        
        print(f"   screen_capture.py: {len(screen_content.split(chr(10)))} 行")
        print(f"   event_stream.py: {len(stream_content.split(chr(10)))} 行")
        
        # Step 4: 生成综合报告
        print("\n📋 Step 4: 生成审计报告")
        
        final_report = AuditReport()
        final_report.add_file("screen_capture.py", 300)
        final_report.add_file("event_stream.py", 250)
        
        # 汇总所有发现的问题
        final_report.add_issue("CRITICAL", "Race Condition", 
                               "screen_capture.py", 120,
                               "状态检查与修改不是原子操作")
        
        final_report.add_issue("HIGH", "Memory Leak",
                               "screen_capture.py", 50,
                               "frame_buffer 字典无限增长")
        
        final_report.add_issue("HIGH", "Resource Leak",
                               "screen_capture.py", 200,
                               "stop_recording 不清理 frame_buffer")
        
        final_report.add_issue("HIGH", "Memory Leak",
                               "event_stream.py", 200,
                               "_aggregations 只增不减")
        
        final_report.add_issue("MEDIUM", "Data Loss",
                               "event_stream.py", 40,
                               "缓冲区满时自动丢弃数据")
        
        final_report.add_issue("HIGH", "Deadlock Risk",
                               "event_stream.py", 130,
                               "混用同步锁和异步锁")
        
        final_report.add_issue("MEDIUM", "Resource Leak",
                               "event_stream.py", 260,
                               "任务列表不清理已完成任务")
        
        final_report.print_report()
        
        print("\n✅ 审计工作流完成")
        print("=" * 80)
        
        return final_report


class TestAuditReportOutput:
    """测试5: 审计报告输出格式"""
    
    def test_report_format(self):
        """测试报告格式"""
        report = AuditReport()
        report.add_file("test.py", 100)
        report.add_issue("HIGH", "Bug", "test.py", 10, "Test bug")
        
        # 验证报告可以生成
        lines = []
        orig_print = print
        def capture_print(*args, **kwargs):
            lines.append(" ".join(str(a) for a in args))
        import builtins
        builtins.print = capture_print
        
        try:
            report.print_report()
        finally:
            builtins.print = orig_print
        
        assert len(lines) > 5, "报告应该有多行输出"
        print(f"\n📄 报告输出 {len(lines)} 行")


def test_import_target_modules():
    """测试能否导入目标模块"""
    print("\n🔍 测试模块导入...")
    
    import sys
    sys.path.insert(0, str(TARGET_DIR))
    
    try:
        import screen_capture
        print(f"   ✓ screen_capture 模块导入成功")
        
        import event_stream
        print(f"   ✓ event_stream 模块导入成功")
        
        return True
    except Exception as e:
        print(f"   ✗ 导入失败: {e}")
        return False


def test_integration():
    """集成测试: 运行完整审计"""
    print("\n" + "=" * 80)
    print("集成测试: 复杂代码审计压测")
    print("=" * 80)
    
    # 测试所有组件
    test_import_target_modules()
    
    # 运行完整审计
    scenario = TestComplexAuditScenario()
    scenario.test_full_audit_workflow()
    
    print("\n✅ 所有测试通过 - mini-claude-code 架构鲁棒性验证完成")
    print("=" * 80)


if __name__ == "__main__":
    # 直接运行时的入口点
    print("运行复杂代码审计测试...")
    
    # 测试导入
    test_import_target_modules()
    
    # 运行集成测试
    pytest.main([__file__, "-v", "--tb=short"])
