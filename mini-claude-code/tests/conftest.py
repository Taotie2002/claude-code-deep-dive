"""conftest.py - pytest configuration for mini-claude-code tests."""
import sys
import os

# Add tests/ directory to sys.path so that:
# - test_llm_as_judge.py (in tests/) can import judge_prompts (also in tests/)
# - All test files can import modules from the project root
_tests_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_tests_dir)
sys.path.insert(0, _tests_dir)
sys.path.insert(0, _root_dir)
