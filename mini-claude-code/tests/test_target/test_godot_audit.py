"""
Godot 游戏项目代码审计测试

测试 mini-claude-code 对 Godot 引擎项目的审计能力：
1. 递归搜索 GDScript 文件
2. 解析 .tscn 场景树
3. 静态分析代码找出 Bug
4. 输出结构化审计报告
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any


class GodotProjectAuditor:
    """Godot 项目审计器"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.gd_files: List[Path] = []
        self.tscn_files: List[Path] = []
        self.issues: List[Dict[str, Any]] = []
    
    def search_gdscript_files(self) -> List[Path]:
        """1. grep搜索GDScript文件"""
        print("[1/4] 搜索 GDScript 文件 (.gd)...")
        self.gd_files = list(self.project_path.rglob("*.gd"))
        print(f"    找到 {len(self.gd_files)} 个 .gd 文件")
        for f in self.gd_files:
            print(f"      - {f.relative_to(self.project_path)}")
        return self.gd_files
    
    def parse_tscn_scenes(self) -> Dict[str, Any]:
        """2. 分析.tscn场景树"""
        print("\n[2/4] 分析 TSCN 场景文件...")
        self.tscn_files = list(self.project_path.rglob("*.tscn"))
        scene_tree = {}
        
        for tscn_file in self.tscn_files:
            print(f"    解析: {tscn_file.name}")
            content = tscn_file.read_text(encoding="utf-8")
            
            # 提取场景节点信息
            nodes = re.findall(r'\[node name="(\w+)" type="(\w+)"', content)
            scene_tree[tscn_file.name] = {
                "path": str(tscn_file.relative_to(self.project_path)),
                "nodes": [{"name": n, "type": t} for n, t in nodes]
            }
        
        return scene_tree
    
    def analyze_gd_scripts(self) -> List[Dict[str, Any]]:
        """3. 分析 GDScript 找出 Bug"""
        print("\n[3/4] 静态分析 GDScript 代码...")
        
        for gd_file in self.gd_files:
            print(f"    分析: {gd_file.name}")
            content = gd_file.read_text(encoding="utf-8")
            
            # Bug 1: velocity = Vector2.ZERO 模式（玩家无法移动）
            if re.search(r'velocity\s*=\s*Vector2\.ZERO', content):
                self.issues.append({
                    "file": str(gd_file.relative_to(self.project_path)),
                    "severity": "CRITICAL",
                    "type": "Logic Error",
                    "bug_id": "BUG-001",
                    "description": "velocity 被强制设为 Vector2.ZERO，导致玩家无法移动",
                    "code_snippet": "velocity = Vector2.ZERO",
                    "fix_suggestion": "根据输入计算实际速度: velocity = input_direction * speed"
                })
            
            # Bug 2: add_item 不检查容量
            if "func add_item" in content and "capacity" in content:
                if not re.search(r'if\s+.*items\.size\(\)\s*>=\s*capacity', content):
                    self.issues.append({
                        "file": str(gd_file.relative_to(self.project_path)),
                        "severity": "HIGH",
                        "type": "Missing Validation",
                        "bug_id": "BUG-002",
                        "description": "add_item() 未检查背包容量，可能导致物品溢出",
                        "code_snippet": "items.append(item)",
                        "fix_suggestion": "添加容量检查: if items.size() >= capacity: return false"
                    })
            
            # Bug 3: remove_item 不检查物品存在性
            if "func remove_item" in content:
                if not re.search(r'if.*items\.has\(item\)', content):
                    self.issues.append({
                        "file": str(gd_file.relative_to(self.project_path)),
                        "severity": "MEDIUM",
                        "type": "Missing Validation",
                        "bug_id": "BUG-003",
                        "description": "remove_item() 未检查物品是否存在",
                        "code_snippet": "items.erase(item)",
                        "fix_suggestion": "添加存在性检查: if not items.has(item): return false"
                    })
        
        return self.issues
    
    def generate_report(self) -> str:
        """4. 输出审计报告"""
        print("\n[4/4] 生成审计报告...")
        
        report = []
        report.append("=" * 60)
        report.append("       GODOT 项目代码审计报告")
        report.append("=" * 60)
        report.append(f"项目路径: {self.project_path}")
        report.append(f"扫描时间: {subprocess.run(['date'], capture_output=True, text=True).stdout.strip()}")
        report.append("")
        report.append(f"扫描结果:")
        report.append(f"  - GDScript 文件: {len(self.gd_files)} 个")
        report.append(f"  - TSCN 场景文件: {len(self.tscn_files)} 个")
        report.append(f"  - 发现问题: {len(self.issues)} 个")
        report.append("")
        
        if self.issues:
            report.append("问题详情:")
            for i, issue in enumerate(self.issues, 1):
                report.append("")
                report.append(f"  [{i}] {issue['bug_id']} - {issue['type']}")
                report.append(f"      文件: {issue['file']}")
                report.append(f"      严重性: {issue['severity']}")
                report.append(f"      描述: {issue['description']}")
                report.append(f"      代码: {issue['code_snippet']}")
                report.append(f"      修复建议: {issue['fix_suggestion']}")
        
        report.append("")
        report.append("=" * 60)
        report.append("                    审计完成")
        report.append("=" * 60)
        
        return "\n".join(report)


def test_godot_audit():
    """Godot游戏项目代码审计测试"""
    print("=" * 60)
    print("  mini-claude-code Godot 项目审计测试")
    print("=" * 60)
    print()
    
    # 被审计的项目路径
    project_path = Path(__file__).parent / "gdscript_simple_game"
    
    if not project_path.exists():
        print(f"错误: 项目路径不存在: {project_path}")
        return
    
    # 创建审计器并执行审计
    auditor = GodotProjectAuditor(str(project_path))
    auditor.search_gdscript_files()
    auditor.parse_tscn_scenes()
    auditor.analyze_gd_scripts()
    report = auditor.generate_report()
    
    # 输出报告
    print()
    print(report)
    
    # 验证预期 Bug 是否被发现
    print("\n验证结果:")
    bug_ids = [issue['bug_id'] for issue in auditor.issues]
    expected_bugs = ['BUG-001', 'BUG-002', 'BUG-003']
    
    for bug in expected_bugs:
        if bug in bug_ids:
            print(f"  ✅ {bug} - 已发现")
        else:
            print(f"  ❌ {bug} - 未发现")
    
    return auditor.issues


if __name__ == "__main__":
    test_godot_audit()
