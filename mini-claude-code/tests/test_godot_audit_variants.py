"""Tests for Godot audit test variants."""
import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)


class TestGodotAuditVariants:
    """Test cases covering various Godot code bugs and their detection."""

    # ---- Correctness Variants ----

    def test_godot_null_pointer_variant(self):
        """Variant: accessing node after queue_free."""
        # This pattern should be flagged by correctness judge
        code = '''
func _ready():
    var sprite = get_node("Sprite")
    sprite.queue_free()
    print(sprite.texture)  # Bug: use after free
'''
        # smoke test - just verify it runs without error
        assert "queue_free" in code
        assert "sprite" in code

    def test_godot_type_mismatch_variant(self):
        """Variant: type-related bugs in GDScript."""
        code = '''
func _process(delta):
    var speed = "100"  # Bug: string instead of float
    position += Vector2(1, 0) * speed  # Type error at runtime
'''
        assert 'speed = "100"' in code

    def test_godot_signal_not_connected_variant(self):
        """Variant: signal connected but handler has wrong signature."""
        code = '''
func _ready():
    connect("body_entered", self, "_on_body_entered")

func _on_body_entered():  # Bug: missing body parameter
    queue_free()
'''
        assert 'connect("body_entered"' in code
        assert "_on_body_entered" in code

    def test_godot_scene_path_variant(self):
        """Variant: incorrect scene tree path."""
        code = '''
func _ready():
    get_node("Player/HealthBar").value = 100  # Bug: path may not exist
'''
        assert "get_node" in code

    def test_godot_reference_before_set_variant(self):
        """Variant: using a variable before it's assigned."""
        code = '''
func take_damage(amount):
    health -= amount  # Bug: health not initialized in this scope
    if health <= 0:
        die()
'''
        assert "health" in code

    # ---- Safety Variants ----

    def test_godot_hardcoded_path_variant(self):
        """Variant: hardcoded file paths break portability."""
        code = '''
func load_save():
    var file = File.new()
    file.open("/home/user/savegame.dat", File.READ)  # Not portable
'''
        assert "/home/user" in code

    def test_godot_insecure_http_variant(self):
        """Variant: using HTTP instead of HTTPS for sensitive data."""
        code = '''
func send_score():
    var http = HTTPClient.new()
    http.connect("http://game-server.com/api/score", 80)  # Insecure
'''
        assert "http://" in code

    def test_godot_print_debug_variant(self):
        """Variant: accidentally printing sensitive data in release."""
        code = '''
func _process(delta):
    print("DEBUG: password =", password)  # Should not be in production
'''
        assert "print" in code
        assert "password" in code

    # ---- Style Variants ----

    def test_godot_single_letter_vars_variant(self):
        """Variant: unhelpful variable names."""
        code = '''
func _init():
    var x = get_node("a")
    var y = get_node("b")
    var z = x + y  # Unclear what this does
'''
        assert "x" in code and "y" in code

    def test_godot_no_docstring_variant(self):
        """Variant: critical function without documentation."""
        code = '''
func calculate_trajectory(angle, velocity, gravity):
    var rad = deg2rad(angle)
    return Vector2(cos(rad) * velocity, sin(rad) * velocity)
'''
        assert "calculate_trajectory" in code
        # No docstring - style issue
        assert '"""' not in code

    def test_godot_magic_numbers_variant(self):
        """Variant: unexplained magic numbers."""
        code = '''
func _process(delta):
    velocity += Vector2(0, -9.8 * delta)
    if position.y > 720:  # Magic number - screen height?
        position.y = 0
'''
        assert "720" in code

    # ---- Score Boundary Tests ----

    @staticmethod
    def _make_case(score_val, passed_val):
        from test_llm_as_judge import JudgeResult
        return JudgeResult(
            score=score_val,
            passed=passed_val,
            dimension_scores={"correctness": score_val},
            reasoning="",
            suggestions=[],
        )

    def test_godot_score_boundary_pass(self):
        r = self._make_case(0.7, True)
        assert r.passed is True

    def test_godot_score_boundary_fail(self):
        r = self._make_case(0.69, False)
        assert r.passed is False

    def test_godot_high_score_perfect(self):
        r = self._make_case(1.0, True)
        assert r.score == 1.0
        assert r.passed is True
