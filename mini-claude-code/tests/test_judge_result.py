import pytest
import sys
import os

# Add project root to path so we can import both judge_prompts (in tests/)
# and test_llm_as_judge (in tests/)
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

from test_llm_as_judge import JudgeResult, TestCase

class TestJudgeResult:
    def test_default_metadata(self):
        result = JudgeResult(score=0.8, passed=True, dimension_scores={}, reasoning="", suggestions=[])
        assert result.metadata == {}

    def test_serialization(self):
        from dataclasses import asdict
        result = JudgeResult(score=0.85, passed=True, dimension_scores={}, reasoning="Good", suggestions=["nit"])
        d = asdict(result)
        assert isinstance(d["dimension_scores"], dict)
        assert d["score"] == 0.85

    @pytest.mark.parametrize("score,expected_passed", [
        (0.69, False), (0.70, True), (0.71, True)
    ])
    def test_passed_threshold(self, score, expected_passed):
        result = JudgeResult(score=score, passed=score >= 0.7, dimension_scores={}, reasoning="", suggestions=[])
        assert result.passed == expected_passed

class TestTestCase:
    def test_default_category(self):
        case = TestCase(id="t1", task="task", expected="expected", code="code")
        assert case.category == "correctness"

    def test_all_categories(self):
        for cat in ["correctness", "safety", "style"]:
            case = TestCase(id=f"t_{cat}", task="task", expected="exp", code="code", category=cat)
            assert case.category == cat
