"""
金融审计测试 - 用mini-claude-code审计上海金/伦敦金溢价监控脚本

本文件演示如何使用Claude Code进行金融场景的代码审计,
重点检测可能导致幻觉的代码模式和数值陷阱。

使用方法:
    cd mini-claude-code
    ./claude-code.sh --eval "按以下审计清单检查tests/test_target/financial_gold_premium/"
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any

# 目标文件路径
TARGET_DIR = Path(__file__).parent
MONITOR_FILE = TARGET_DIR / "gold_price_monitor.py"
CONFIG_FILE = TARGET_DIR / "config.py"


# =============================================================================
# 审计检查项定义
# =============================================================================

class AuditCheck:
    """审计检查项"""

    def __init__(self, name: str, pattern: str, severity: str, description: str):
        self.name = name
        self.pattern = re.compile(pattern, re.MULTILINE)
        self.severity = severity  # HIGH, MEDIUM, LOW
        self.description = description

    def search(self, content: str) -> List[Tuple[int, str]]:
        """搜索匹配项,返回(行号,匹配内容)列表"""
        matches = []
        for i, line in enumerate(content.split("\n"), 1):
            if self.pattern.search(line):
                matches.append((i, line.strip()))
        return matches


# BUG模式检测规则
BUG_PATTERNS = [
    AuditCheck(
        name="BUG-001: 单位混淆",
        pattern=r"28\.3495",  # 液量盎司值,不是金衡盎司
        severity="HIGH",
        description="检测到液量盎司换算值(28.3495),可能与金衡盎司(31.1035)混淆"
    ),
    AuditCheck(
        name="BUG-002: 硬编码时区",
        pattern=r"UTC[\+\-]8|timezone\.utc",
        severity="MEDIUM",
        description="检测到硬编码时区或UTC处理,需要确认是否考虑夏令时"
    ),
    AuditCheck(
        name="BUG-003: HTTP错误处理缺失",
        pattern=r"raise_for_status|HTTPError",
        severity="HIGH",
        description="检测到HTTP错误处理,检查是否处理了500错误"
    ),
    AuditCheck(
        name="BUG-004: 缺少退避策略",
        pattern=r"retry|backoff|sleep|timeout",
        severity="MEDIUM",
        description="检测到重试相关代码,检查是否有指数退避策略"
    ),
    AuditCheck(
        name="数字常量检查",
        pattern=r"\b\d+\.\d+\b",  # 所有数字常量
        severity="LOW",
        description="列出所有数字常量,人工核对是否合理"
    ),
]


# =============================================================================
# 数值核对清单
# =============================================================================

UNIT_CONVERSIONS = {
    "troy_oz_to_gram": {
        "correct_value": 31.1035,
        "wrong_value": 28.3495,
        "wrong_name": "fluid_oz",
        "description": "1金衡盎司=31.1035克 (不是28.3495液量盎司)"
    },
    "usd_cny_rate": {
        "typical_range": (7.0, 8.0),
        "description": "USD/CNY通常在7-8之间"
    },
    "gold_price": {
        "typical_range": (1500, 2500),
        "unit": "USD/oz",
        "description": "黄金价格通常在1500-2500 USD/oz"
    },
}


def verify_unit_conversions(file_content: str) -> Dict[str, Any]:
    """
    验证单位换算的正确性

    检查:
    1. oz_to_gram的值是否正确(应为31.1035)
    2. 是否有注释中的错误值(28.3495)
    3. 单位是否一致(USD/oz vs CNY/gram)
    """
    results = {
        "found_values": [],
        "issues": [],
        "warnings": []
    }

    # 搜索所有数字常量
    number_pattern = re.compile(r"(\d+\.\d+)")
    for i, line in enumerate(file_content.split("\n"), 1):
        if "#" in line:
            comment = line[line.index("#"):]
            numbers = number_pattern.findall(line)
            for num in numbers:
                if float(num) > 0:
                    results["found_values"].append({
                        "line": i,
                        "value": num,
                        "context": line.strip()
                    })

    # 检查是否有错误的28.3495
    if "28.3495" in file_content:
        results["issues"].append({
            "type": "WRONG_UNIT_CONVERSION",
            "message": "发现液量盎司值28.3495,可能与金衡盎司31.1035混淆",
            "severity": "HIGH"
        })

    # 检查oz_to_gram的定义
    oz_pattern = re.compile(r"OZ_TO_GRAM\s*=\s*(\d+\.\d+)")
    match = oz_pattern.search(file_content)
    if match:
        oz_value = float(match.group(1))
        if abs(oz_value - 31.1035) < 0.001:
            results["found_values"].append({
                "name": "OZ_TO_GRAM",
                "value": oz_value,
                "status": "✓ 正确"
            })
        else:
            results["issues"].append({
                "type": "OZ_TO_GRAM_ERROR",
                "message": f"OZ_TO_GRAM值{oz_value}不正确,应为31.1035",
                "severity": "HIGH"
            })

    return results


def check_error_handling(file_content: str) -> Dict[str, Any]:
    """
    检查错误处理是否完善

    检查:
    1. API调用是否有try-except
    2. HTTP 500错误是否被处理
    3. 是否有适当的超时处理
    4. 是否有重试机制
    """
    results = {
        "try_except_blocks": [],
        "http_error_handling": [],
        "timeout_handling": [],
        "issues": []
    }

    # 统计try-except块
    try_blocks = len(re.findall(r"\btry\s*:", file_content))
    except_blocks = len(re.findall(r"\bexcept\s+", file_content))
    results["try_except_blocks"] = {
        "try_count": try_blocks,
        "except_count": except_blocks,
        "balanced": try_blocks == except_blocks
    }

    # 检查HTTP错误处理
    if "raise_for_status()" in file_content:
        # 检查是否有对应的except处理
        lines = file_content.split("\n")
        for i, line in enumerate(lines):
            if "raise_for_status()" in line:
                # 检查前后20行是否有HTTPError处理
                context = "\n".join(lines[max(0, i-20):min(len(lines), i+20)])
                if "HTTPError" not in context and "requests.HTTPError" not in context:
                    results["issues"].append({
                        "line": i + 1,
                        "type": "MISSING_HTTP_ERROR_HANDLING",
                        "message": "raise_for_status()后没有处理HTTPError(可能被500等错误中断)",
                        "severity": "HIGH"
                    })

    # 检查超时处理
    if "timeout=" in file_content or "Timeout" in file_content:
        results["timeout_handling"].append("找到超时配置")
    else:
        results["issues"].append({
            "type": "NO_TIMEOUT",
            "message": "API请求没有配置超时,可能导致无限等待",
            "severity": "MEDIUM"
        })

    # 检查重试机制
    if "retry" in file_content.lower() or "sleep" in file_content.lower():
        results["http_error_handling"].append("找到重试/等待逻辑")
    else:
        results["issues"].append({
            "type": "NO_RETRY",
            "message": "API失败时没有重试机制,可能因暂时性错误中断",
            "severity": "MEDIUM"
        })

    return results


# =============================================================================
# 防幻觉决策树
# =============================================================================

HALLUCINATION_DECISION_TREE = """
=== 金融数据防幻觉决策树 ===

当处理金融数据计算时,按以下顺序检查:

[1] 单位一致性检查
    ├─ 所有价格是否在同一单位下?
    │   ├─ USD/oz → 需要转换为CNY/gram才能比较
    │   └─ CNY/gram → 可以直接比较
    ├─ oz→gram换算是否正确?
    │   ├─ 正确: 31.1035 (金衡盎司)
    │   └─ 错误: 28.3495 (液量盎司,常见错误!)
    └─ 汇率是否正确应用?

[2] 数值合理性检查
    ├─ 黄金价格是否在合理区间?
    │   └─ 1500-2500 USD/oz (异常值需要确认)
    ├─ 汇率是否在合理区间?
    │   └─ USD/CNY应在7-8之间 (2020s典型值)
    └─ 计算结果是否合理?
        └─ 溢价通常在±10 CNY/gram以内

[3] API依赖检查
    ├─ 是否处理了所有HTTP错误码?
    │   ├─ 400: 请求参数错误
    │   ├─ 401/403: 认证/授权错误
    │   ├─ 429: 请求过于频繁(限流)
    │   ├─ 500: 服务器内部错误 (容易被忽略!)
    │   └─ 502/503/504: 网关/服务不可用
    ├─ 是否有超时处理?
    └─ 是否有重试退避策略?

[4] 时区处理检查
    ├─ 所有时间戳是否在同一时区?
    ├─ 是否考虑了夏令时?
    └─ 交易时段是否正确判断?

[5] 审计追踪检查
    ├─ 原始数据是否被记录?
    ├─ 每步转换是否有日志?
    └─ 最终结果是否可复现?
"""


# =============================================================================
# 主审计流程
# =============================================================================

def run_audit() -> Dict[str, Any]:
    """执行完整审计"""
    print("=" * 70)
    print("金融数据压测用例 - 审计报告生成器")
    print("=" * 70)

    audit_results = {
        "files_checked": [],
        "bugs_found": [],
        "warnings": [],
        "decision_tree": HALLUCINATION_DECISION_TREE
    }

    # 读取文件
    files_to_check = {
        "gold_price_monitor.py": MONITOR_FILE,
        "config.py": CONFIG_FILE
    }

    for filename, filepath in files_to_check.items():
        if not filepath.exists():
            print(f"\n❌ 文件不存在: {filepath}")
            continue

        print(f"\n📄 审计文件: {filename}")
        print("-" * 50)

        content = filepath.read_text()
        audit_results["files_checked"].append(filename)

        # BUG模式检测
        print("\n[BUG模式检测]")
        for check in BUG_PATTERNS:
            matches = check.search(content)
            if matches:
                print(f"\n⚠️ {check.name} (严重性: {check.severity})")
                print(f"   说明: {check.description}")
                for line_no, line_content in matches[:5]:  # 最多显示5个
                    print(f"   L{line_no}: {line_content}")
                audit_results["bugs_found"].append({
                    "file": filename,
                    "check": check.name,
                    "severity": check.severity,
                    "matches": matches
                })

        # 单位换算验证
        if filename == "gold_price_monitor.py":
            print("\n[单位换算验证]")
            unit_results = verify_unit_conversions(content)
            for issue in unit_results.get("issues", []):
                print(f"❌ {issue['type']}: {issue['message']}")
                audit_results["warnings"].append(issue)
            print(f"✓ 找到{len(unit_results.get('found_values', []))}个数值常量")

        # 错误处理检查
        if filename == "gold_price_monitor.py":
            print("\n[错误处理检查]")
            error_results = check_error_handling(content)
            print(f"   try-except块: {error_results['try_except_blocks']}")
            for issue in error_results.get("issues", []):
                print(f"❌ L{issue.get('line', '?')}: {issue['message']}")
                audit_results["warnings"].append(issue)

    # 输出决策树
    print("\n" + "=" * 70)
    print("防幻觉决策树")
    print("=" * 70)
    print(HALLUCINATION_DECISION_TREE)

    # 总结
    print("\n" + "=" * 70)
    print("审计总结")
    print("=" * 70)
    print(f"检查文件数: {len(audit_results['files_checked'])}")
    print(f"发现BUG模式: {len(audit_results['bugs_found'])}")
    print(f"发现警告: {len(audit_results['warnings'])}")

    if audit_results["bugs_found"]:
        print("\n🔍 需要关注的BUG:")
        for bug in audit_results["bugs_found"]:
            if bug["severity"] == "HIGH":
                print(f"   ⚠️ HIGH: {bug['check']} in {bug['file']}")

    return audit_results


def main():
    """CLI入口"""
    if "--tree-only" in sys.argv:
        print(HALLUCINATION_DECISION_TREE)
    else:
        run_audit()


if __name__ == "__main__":
    main()
