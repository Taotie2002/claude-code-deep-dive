"""Tests for result parsing logic."""
import pytest
import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from test_llm_as_judge import _parse_judge_result, JudgeResult


class TestParseJudgeResult:
    def test_parse_valid_json_score(self):
        raw = '{"score": 0.85, "passed": true, "reasoning": "good", "suggestions": []}'
        result = _parse_judge_result(raw, "correctness")
        assert result.score == 0.85
        assert result.passed is True
        assert result.dimension_scores["correctness"] == 0.85

    def test_parse_valid_json_with_reasoning(self):
        raw = '{"score": 0.7, "passed": true, "reasoning": "meets requirements", "suggestions": ["nit"]}'
        result = _parse_judge_result(raw, "safety")
        assert result.reasoning == "meets requirements"
        assert result.suggestions == ["nit"]

    def test_parse_score_out_of_ten(self):
        # When LLM returns score out of 10 in regex fallback (not JSON path)
        raw = "Score: 9, Passed: yes. Great work."
        result = _parse_judge_result(raw, "style")
        assert result.score == 0.9  # 9/10 = 0.9

    def test_parse_fallback_regex(self):
        # Regex fallback uses pattern "score[:\s]*(\d+\.?\d*)" and "passed[:\s]*(true|false|yes|no)"
        raw = "Score: 0.75, Passed: yes. The code is correct."
        result = _parse_judge_result(raw, "correctness")
        assert result.score == 0.75

    def test_parse_fallback_regex_out_of_ten(self):
        raw = "Score: 8, Passed: true, reasoning here"
        result = _parse_judge_result(raw, "correctness")
        assert result.score == 0.8  # 8/10 = 0.8

    def test_parse_invalid_json_fallback(self):
        # Broken JSON, should fall back to regex
        raw = "Here is the result { broken json } score: 0.9 passed: yes"
        result = _parse_judge_result(raw, "correctness")
        assert result.score == 0.9

    def test_parse_score_only_raw(self):
        raw = "The solution is acceptable. Score: 0.6. No major issues."
        result = _parse_judge_result(raw, "safety")
        assert result.score == 0.6

    def test_parse_passed_false(self):
        raw = '{"score": 0.3, "passed": false, "reasoning": "fails", "suggestions": []}'
        result = _parse_judge_result(raw, "correctness")
        assert result.passed is False

    def test_parse_passed_yes(self):
        raw = "Score: 0.8. Passed: yes. Looks good."
        result = _parse_judge_result(raw, "correctness")
        assert result.passed is True

    def test_parse_no_score_fallback(self):
        raw = "No score provided in the response"
        result = _parse_judge_result(raw, "correctness")
        # Should default to 0.5
        assert result.score == 0.5
