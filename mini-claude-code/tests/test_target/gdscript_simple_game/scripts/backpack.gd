extends Node

# 背包系统
var items: Array = []
var capacity: int = 10

func add_item(item):
    # Bug: 超过capacity不检查
    items.append(item)

func remove_item(item):
    # Bug: 物品不存在时没处理
    items.erase(item)
