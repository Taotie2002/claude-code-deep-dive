# Tests for mini-claude-code
# This is a placeholder test structure.
# Run with: pytest or python -m pytest

import sys
sys.path.insert(0, '.')

def test_import():
    """Test that all modules can be imported."""
    try:
        import tools
        import memory
        import agent
        print("All modules imported successfully")
    except Exception as e:
        print(f"Import failed: {e}")

if __name__ == "__main__":
    test_import()
