# GDScript Simple Game - Godot 项目示例

## 项目背景

这是一个简化的 Godot 2D 游戏项目，用于测试 AI Agent 对多文件游戏引擎项目的代码审计能力。

- **引擎版本**: Godot 4.2
- **项目类型**: 2D 平台动作游戏（简化版）
- **主要功能**: 玩家控制、背包系统

## 目录结构

```
gdscript_simple_game/
├── project.godot        # Godot 项目配置文件
├── scenes/
│   ├── player.tscn     # 玩家场景（CharacterBody2D）
│   └── world.tscn      # 世界场景（包含 Player 实例）
├── scripts/
│   ├── player.gd       # 玩家移动控制脚本
│   └── backpack.gd     # 背包系统脚本
└── README.md
```

## 审计目标

审计 Agent 需要能够：
1. 递归搜索项目中的 `.gd` 和 `.tscn` 文件
2. 解析 Godot 场景文件（TSCN 格式）
3. 分析 GDScript 脚本逻辑
4. 识别常见的游戏开发 Bug 模式

## 预期 Bug

本项目故意植入了以下 Bug，用于测试审计能力：

### Bug 1: `player.gd` - 玩家无法移动
```gdscript
func _physics_process(delta):
    velocity = Vector2.ZERO  # Bug: 每次都设为零，玩家永远不能移动
    move_and_slide()
```
**问题**: velocity 被强制设为零，且没有处理输入事件，玩家角色完全无法移动。

### Bug 2: `player.gd` - 接口不一致
**问题**: 注释提到与 world.gd 接口不一致，但 world.gd 不存在，说明设计文档或接口规范缺失。

### Bug 3: `backpack.gd` - 容量超限未检查
```gdscript
func add_item(item):
    items.append(item)  # Bug: 超过 capacity 不检查，可能导致内存溢出或逻辑错误
```
**问题**: 添加物品前未检查是否已达到容量上限。

### Bug 4: `backpack.gd` - 移除不存在的物品未处理
```gdscript
func remove_item(item):
    items.erase(item)  # Bug: 物品不存在时没处理，可能导致意外行为
```
**问题**: 移除物品前未检查物品是否存在于背包中。

## 审计检查清单

- [ ] 搜索所有 `.gd` 文件
- [ ] 搜索所有 `.tscn` 文件  
- [ ] 分析 player.gd 的移动逻辑
- [ ] 分析 backpack.gd 的容量管理
- [ ] 检查场景树结构
- [ ] 验证输入处理是否完整
- [ ] 输出结构化审计报告
