"""
LLM-as-Judge: 用AI评测AI输出质量

基于评审人建议，用AI Agent测试AI Agent输出质量。
支持代码正确性、安全性、风格等多维度评判。
"""

import os
import json
import re
import time
from dataclasses import dataclass, field
from typing import Optional, Literal
from judge_prompts import (
    CODE_CORRECTNESS_PROMPT,
    CODE_SAFETY_PROMPT,
    CODE_STYLE_PROMPT,
    JUDGE_SYSTEM_PROMPT,
    build_judge_prompt,
)


@dataclass
class JudgeResult:
    """评判结果"""
    score: float              # 0.0-1.0 综合评分
    passed: bool             # 是否通过
    dimension_scores: dict         # 各维度评分
    reasoning: str           # 评判理由
    suggestions: list[str]   # 改进建议
    metadata: dict = field(default_factory=dict)


@dataclass
class TestCase:
    """测试用例"""
    id: str
    task: str                 # 任务描述
    expected: str             # 期望输出/行为
    code: str                 # 待评测代码
    category: str = "correctness"  # correctness | safety | style
    metadata: dict = field(default_factory=dict)


def call_llm(
    prompt: str,
    model: str = "gpt-4o",
    temperature: float = 0.0,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
) -> str:
    """调用LLM进行评判"""
    try:
        import openai
    except ImportError:
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("需要安装 openai 或 anthropic 库")

    api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

    # OpenAI兼容接口
    if "OPENAI_API_KEY" in os.environ or not os.environ.get("ANTHROPIC_API_KEY"):
        client = openai.OpenAI(api_key=api_key, base_url=api_base or os.environ.get("OPENAI_API_BASE"))
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content
    else:
        # Anthropic接口
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=JUDGE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


def judge_code_correctness(
    code: str,
    expected: str,
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
    timeout: int = 30,
) -> JudgeResult:
    """
    评判代码正确性

    Args:
        code: 待评测代码
        expected: 期望行为/输出
        model: 使用的模型
        api_key: API密钥
        timeout: 超时时间(秒)

    Returns:
        JudgeResult: 包含评分和详细理由
    """
    prompt = build_judge_prompt(
        dimension="correctness",
        code=code,
        expected=expected,
    )

    raw = call_llm(prompt, model=model, api_key=api_key)
    return _parse_judge_result(raw, "correctness")


def judge_code_safety(
    code: str,
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
) -> JudgeResult:
    """评判代码安全性"""
    prompt = build_judge_prompt(dimension="safety", code=code)
    raw = call_llm(prompt, model=model, api_key=api_key)
    return _parse_judge_result(raw, "safety")


def judge_code_style(
    code: str,
    language: str = "python",
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
) -> JudgeResult:
    """评判代码风格"""
    prompt = build_judge_prompt(dimension="style", code=code, language=language)
    raw = call_llm(prompt, model=model, api_key=api_key)
    return _parse_judge_result(raw, "style")


def judge_comprehensive(
    code: str,
    expected: Optional[str] = None,
    language: str = "python",
    dimensions: list[str] = None,
    model: str = "gpt-4o",
    api_key: Optional[str] = None,
) -> JudgeResult:
    """
    综合评判：同时评测多个维度

    Args:
        code: 待评测代码
        expected: 期望行为（correctness维度需要）
        language: 编程语言
        dimensions: 评测维度列表，默认["correctness", "safety", "style"]
        model: 使用的模型
        api_key: API密钥

    Returns:
        JudgeResult: 综合评分和各维度评分
    """
    dimensions = dimensions or ["correctness", "safety", "style"]
    scores = {}
    all_suggestions = []
    all_reasoning = []

    for dim in dimensions:
        if dim == "correctness" and expected:
            result = judge_code_correctness(code, expected, model, api_key)
        elif dim == "safety":
            result = judge_code_safety(code, model, api_key)
        elif dim == "style":
            result = judge_code_style(code, language, model, api_key)
        else:
            continue

        scores[dim] = result.score
        all_reasoning.append(f"[{dim.upper()}] {result.reasoning}")
        all_suggestions.extend(result.suggestions)

    # 综合评分：加权平均（correctness权重最高）
    weights = {"correctness": 0.5, "safety": 0.3, "style": 0.2}
    total_score = sum(scores.get(d, 0) * weights.get(d, 0) for d in scores)
    normalized_score = total_score / sum(weights.get(d, 0) for d in scores) if scores else 0.0

    return JudgeResult(
        score=round(normalized_score, 3),
        passed=normalized_score >= 0.7,
        dimension_scores=scores,
        reasoning="\n".join(all_reasoning),
        suggestions=all_suggestions,
        metadata={"dimensions": list(scores.keys()), "model": model},
    )


def _parse_judge_result(raw: str, dimension: str) -> JudgeResult:
    """解析LLM返回的评判结果"""
    # 尝试提取JSON
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if json_match:
        try:
            data = json.loads(json_match.group())
            return JudgeResult(
                score=float(data.get("score", 0.0)),
                passed=bool(data.get("passed", False)),
                dimension_scores={dimension: float(data.get("score", 0.0))},
                reasoning=data.get("reasoning", ""),
                suggestions=data.get("suggestions", []),
            )
        except (json.JSONDecodeError, ValueError):
            pass

    # 回退：正则提取
    score_match = re.search(r"score[:\s]*(\d+\.?\d*)", raw, re.IGNORECASE)
    passed_match = re.search(r"passed[:\s]*(true|false|yes|no)", raw, re.IGNORECASE)

    score = float(score_match.group(1)) / 10 if score_match and float(score_match.group(1)) > 1 else float(score_match.group(1)) if score_match else 0.5
    passed = passed_match and re.search(r"true|yes", passed_match.group(1), re.IGNORECASE)

    return JudgeResult(
        score=round(score, 3),
        passed=bool(passed),
        dimension_scores={dimension: round(score, 3)},
        reasoning=raw[:500],
        suggestions=[],
    )


# ============ 测试用例运行器 ============

def run_test_case(
    case: TestCase,
    judge_model: str = "gpt-4o",
    api_key: Optional[str] = None,
) -> dict:
    """运行单个测试用例"""
    start = time.time()
    try:
        if case.category == "correctness":
            result = judge_code_correctness(case.code, case.expected, judge_model, api_key)
        elif case.category == "safety":
            result = judge_code_safety(case.code, judge_model, api_key)
        elif case.category == "style":
            result = judge_code_style(case.code, metadata.get("language", "python"), judge_model, api_key)
        else:
            result = judge_comprehensive(case.code, case.expected)
    except Exception as e:
        return {
            "id": case.id,
            "passed": False,
            "error": str(e),
            "duration": time.time() - start,
        }

    return {
        "id": case.id,
        "score": result.score,
        "passed": result.passed,
        "reasoning": result.reasoning,
        "suggestions": result.suggestions,
        "duration": round(time.time() - start, 2),
        "category": case.category,
    }


def run_benchmark(
    test_cases: list[TestCase],
    judge_model: str = "gpt-4o",
    api_key: Optional[str] = None,
    parallel: bool = False,
) -> dict:
    """运行一组测试用例"""
    results = []
    for case in test_cases:
        result = run_test_case(case, judge_model, api_key)
        results.append(result)

    passed = sum(1 for r in results if r.get("passed", False))
    total = len(results)
    avg_score = sum(r.get("score", 0) for r in results) / total if total else 0

    return {
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "avg_score": round(avg_score, 3),
        },
        "results": results,
    }


# ============ CLI入口 ============

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="LLM-as-Judge 代码质量评测")
    parser.add_argument("--code", type=str, help="待评测代码")
    parser.add_argument("--expected", type=str, help="期望行为")
    parser.add_argument("--file", type=str, help="代码文件路径")
    parser.add_argument("--dimension", type=str, default="comprehensive",
                        choices=["correctness", "safety", "style", "comprehensive"])
    parser.add_argument("--model", type=str, default=os.environ.get("JUDGE_MODEL", "gpt-4o"))
    parser.add_argument("--output", type=str, help="输出JSON文件路径")
    args = parser.parse_args()

    # 读取代码
    if args.file:
        with open(args.file) as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        print("错误：需要提供 --code 或 --file")
        return 1

    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")

    # 执行评判
    if args.dimension == "comprehensive":
        result = judge_comprehensive(code, args.expected, model=args.model, api_key=api_key)
    elif args.dimension == "correctness":
        result = judge_code_correctness(code, args.expected or "", model=args.model, api_key=api_key)
    elif args.dimension == "safety":
        result = judge_code_safety(code, model=args.model, api_key=api_key)
    else:
        result = judge_code_style(code, model=args.model, api_key=api_key)

    output = {
        "score": result.score,
        "passed": result.passed,
        "reasoning": result.reasoning,
        "suggestions": result.suggestions,
        "dimension_scores": result.dimension_scores,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    return 0 if result.passed else 1


if __name__ == "__main__":
    exit(main())
