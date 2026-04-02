extends CharacterBody2D

# 玩家移动脚本
var speed: int = 200

func _physics_process(delta):
    # Bug: 没有处理速度为0的情况
    # Bug: 与world.gd的接口不一致
    velocity = Vector2.ZERO
    move_and_slide()
