# 刷流策略系统

这是一个灵活的刷流策略管理系统，允许您定义和组合不同的下载策略来控制种子的下载行为。

## 功能特性

- **多种策略类型**: 支持基于大小、比例、时间等多种策略
- **策略组合**: 支持AND、OR、加权等多种组合方式
- **配置管理**: 支持JSON配置文件管理策略
- **动态切换**: 可以在运行时切换不同的策略
- **优先级计算**: 为种子计算下载优先级
- **详细日志**: 提供详细的决策日志

## 策略类型

### 1. 大小策略 (SizeBasedStrategy)
根据种子大小和磁盘空间决定是否下载。

**配置参数:**
- `min_size`: 最小种子大小（字节）
- `max_size`: 最大种子大小（字节）
- `min_disk_space`: 最小保留磁盘空间（字节）
- `size_priority_weight`: 大小优先级权重

### 2. 比例策略 (RatioBasedStrategy)
根据做种/下载比例决定是否下载。

**配置参数:**
- `min_seeders`: 最小做种人数
- `min_ratio`: 最小下载/做种比例
- `max_ratio`: 最大下载/做种比例
- `ratio_priority_weight`: 比例优先级权重
- `prefer_high_seeders`: 是否优先选择做种人数多的种子

### 3. 时间策略 (TimeBasedStrategy)
根据发布时间和免费时间决定是否下载。

**配置参数:**
- `max_publish_age`: 最大发布时间（秒）
- `min_free_time`: 最小剩余免费时间（秒）
- `time_priority_weight`: 时间优先级权重
- `prefer_new_torrents`: 是否优先选择新发布的种子
- `time_decay_factor`: 时间衰减因子

### 4. 组合策略 (CompositeStrategy)
组合多个策略，支持AND、OR、加权等组合方式。

**配置参数:**
- `strategies`: 策略列表
- `combination_type`: 组合类型 ('and', 'or', 'weighted')
- `weights`: 各策略权重（仅用于weighted类型）

## 使用方法

### 基本使用

```python
from strategies.strategy_manager import StrategyManager

# 创建策略管理器
manager = StrategyManager("config_example.json")

# 种子信息
torrent_info = {
    "id": "12345",
    "name": "示例种子",
    "size": 5 * 1024 * 1024 * 1024,  # 5GB
    "discount": "FREE",
    "discount_end_time": datetime.now() + timedelta(hours=20),
    "seeders": 10,
    "leechers": 5,
    "publish_time": datetime.now() - timedelta(hours=2),
    "disk_space": 100 * 1024 * 1024 * 1024  # 100GB
}

# 判断是否应该下载
should_download = manager.should_download(torrent_info)

# 获取优先级
priority = manager.get_priority(torrent_info)
```

### 切换策略

```python
# 查看可用策略
available_strategies = manager.get_available_strategies()
print("可用策略:", available_strategies)

# 切换到保守策略
manager.set_current_strategy("conservative")

# 获取策略信息
strategy_info = manager.get_strategy_info("conservative")
print("策略信息:", strategy_info)
```

### 在 flood_refactored.py 中使用

```python
from strategies.strategy_manager import StrategyManager

# 在 flood_task 函数中初始化策略管理器
strategy_manager = StrategyManager()

# 在处理种子时使用策略
for item in root.findall("channel/item", NAMESPACE):
    # ... 解析种子信息 ...
    
    torrent_info = {
        "id": torrent_id,
        "name": name,
        "size": size,
        "discount": discount,
        "discount_end_time": discount_end_time,
        "seeders": seeders,
        "leechers": leechers,
        "publish_time": publish_time,
        "disk_space": disk_space
    }
    
    # 使用策略判断是否下载
    if not strategy_manager.should_download(torrent_info):
        continue
    
    # 获取优先级（可选）
    priority = strategy_manager.get_priority(torrent_info)
    
    # 继续下载流程...
```

## 配置文件格式

```json
{
  "strategy_configs": {
    "conservative": {
      "type": "composite",
      "combination_type": "and",
      "weights": [0.4, 0.3, 0.3],
      "strategies": [
        {
          "type": "size",
          "params": {
            "min_size": 1073741824,
            "max_size": 10737418240,
            "min_disk_space": 85899345920
          }
        },
        {
          "type": "ratio",
          "params": {
            "min_seeders": 5,
            "min_ratio": 0.2,
            "max_ratio": 5.0
          }
        },
        {
          "type": "time",
          "params": {
            "max_publish_age": 43200,
            "min_free_time": 18000
          }
        }
      ]
    }
  },
  "default_strategy": "conservative"
}
```

## 预定义策略

系统提供了三种预定义策略：

1. **conservative (保守策略)**: 使用AND组合，要求所有条件都满足
2. **aggressive (激进策略)**: 使用OR组合，只要有一个条件满足即可
3. **balanced (平衡策略)**: 使用加权组合，平衡各种因素

## 扩展自定义策略

要添加自定义策略，需要：

1. 继承 `BaseStrategy` 类
2. 实现 `should_download` 和 `get_priority` 方法
3. 在 `StrategyFactory` 中注册新策略

```python
from strategies.base_strategy import BaseStrategy

class CustomStrategy(BaseStrategy):
    def should_download(self, torrent_info):
        # 实现自定义逻辑
        return True
    
    def get_priority(self, torrent_info):
        # 实现优先级计算
        return 0.5

# 注册策略
factory = StrategyFactory()
factory.register_strategy('custom', CustomStrategy)
```

## 注意事项

1. 所有大小参数都以字节为单位
2. 时间参数以秒为单位
3. 优先级范围是 0.0 到 1.0
4. 策略配置更改后需要重新加载
5. 建议在生产环境中使用配置文件管理策略 