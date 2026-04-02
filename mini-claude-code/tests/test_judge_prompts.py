"""Tests for judge_prompts module."""
import pytest
import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from judge_prompts import (
    CODE_CORRECTNESS_PROMPT,
    CODE_SAFETY_PROMPT,
    CODE_STYLE_PROMPT,
    JUDGE_SYSTEM_PROMPT,
    COMPREHENSIVE_PROMPT,
    build_judge_prompt,
    SAMPLE_TEST_CASES,
)


class TestJudgePrompts:
    def test_system_prompt_exists(self):
        assert isinstance(JUDGE_SYSTEM_PROMPT, str)
        assert len(JUDGE_SYSTEM_PROMPT) > 0
        assert "Code Review Expert" in JUDGE_SYSTEM_PROMPT or "代码评审" in JUDGE_SYSTEM_PROMPT

    def test_correctness_prompt_template(self):
        assert "code" in CODE_CORRECTNESS_PROMPT.lower() or "代码" in CODE_CORRECTNESS_PROMPT
        assert "score" in CODE_CORRECTNESS_PROMPT.lower()

    def test_safety_prompt_template(self):
        assert "safety" in CODE_SAFETY_PROMPT.lower() or "安全" in CODE_SAFETY_PROMPT
        assert "score" in CODE_SAFETY_PROMPT.lower()

    def test_style_prompt_template(self):
        assert "style" in CODE_STYLE_PROMPT.lower() or "风格" in CODE_STYLE_PROMPT
        assert "{language}" in CODE_STYLE_PROMPT

    def test_comprehensive_prompt_template(self):
        assert "comprehensive" in COMPREHENSIVE_PROMPT.lower() or "综合" in COMPREHENSIVE_PROMPT
        assert "{code}" in COMPREHENSIVE_PROMPT


class TestBuildJudgePrompt:
    def test_build_correctness_prompt(self):
        code = 'def add(a, b): return a + b'
        expected = "returns sum of two numbers"
        prompt = build_judge_prompt(dimension="correctness", code=code, expected=expected)
        assert code in prompt
        assert expected in prompt

    def test_build_safety_prompt(self):
        code = 'os.system("ls")'
        prompt = build_judge_prompt(dimension="safety", code=code)
        assert code in prompt

    def test_build_style_prompt(self):
        code = 'x = 1'
        prompt = build_judge_prompt(dimension="style", code=code, language="python")
        assert code in prompt
        assert "python" in prompt

    def test_build_comprehensive_prompt(self):
        code = 'print("hello")'
        prompt = build_judge_prompt(dimension="comprehensive", code=code)
        assert code in prompt

    def test_build_invalid_dimension_raises(self):
        with pytest.raises(ValueError):
            build_judge_prompt(dimension="invalid", code="pass")

    def test_build_style_prompt_with_custom_language(self):
        code = 'func main() {}'
        prompt = build_judge_prompt(dimension="style", code=code, language="go")
        assert "go" in prompt.lower()


class TestSampleTestCases:
    def test_sample_cases_exist(self):
        assert isinstance(SAMPLE_TEST_CASES, list)
        assert len(SAMPLE_TEST_CASES) > 0

    def test_sample_case_structure(self):
        for case in SAMPLE_TEST_CASES:
            assert "id" in case
            assert "task" in case
            assert "expected" in case
            assert "code" in case
            assert "category" in case
            assert case["category"] in ["correctness", "safety", "style"]

    def test_sample_cases_have_expected_score(self):
        for case in SAMPLE_TEST_CASES:
            assert "expected_score" in case
            assert 0.0 <= case["expected_score"] <= 1.0
