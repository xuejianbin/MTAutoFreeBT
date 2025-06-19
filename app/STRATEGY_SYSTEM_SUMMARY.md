# 刷流策略系统总结

## 项目概述

本次为 MTAutoFreeBT 项目新增了一个完整的刷流策略管理系统，用于替代原有的硬编码判断逻辑，提供更灵活、可配置的种子下载决策机制。

## 新增文件结构

```
app/
├── strategies/
│   ├── __init__.py                    # 策略模块初始化
│   ├── base_strategy.py               # 基础策略类
│   ├── size_based_strategy.py         # 基于大小的策略
│   ├── ratio_based_strategy.py        # 基于比例的策略
│   ├── time_based_strategy.py         # 基于时间的策略
│   ├── composite_strategy.py          # 组合策略类
│   ├── strategy_factory.py            # 策略工厂类
│   ├── strategy_manager.py            # 策略管理器类
│   ├── config_example.json            # 策略配置示例
│   ├── example_usage.py               # 使用示例
│   └── README.md                      # 策略系统说明文档
├── test_strategies.py                 # 策略系统测试脚本
├── flood_refactored.py                # 集成策略系统的主程序
└── STRATEGY_SYSTEM_SUMMARY.md         # 本文档
```

## 核心功能

### 1. 策略类型

- **SizeBasedStrategy**: 基于种子大小和磁盘空间的策略
- **RatioBasedStrategy**: 基于做种/下载比例的策略
- **TimeBasedStrategy**: 基于发布时间和免费时间的策略
- **CompositeStrategy**: 组合多个策略的策略

### 2. 策略组合方式

- **AND**: 所有子策略都必须通过
- **OR**: 至少一个子策略通过
- **Weighted**: 加权投票方式

### 3. 预定义策略

- **conservative**: 保守策略，要求所有条件都满足
- **aggressive**: 激进策略，只要有一个条件满足即可
- **balanced**: 平衡策略，使用加权组合

## 主要改进

### 1. 原有代码改进

**修改前 (flood_refactored.py):**
```python
# 硬编码的判断逻辑
if size > MAX_SIZE:
    continue
if size < MIN_SIZE:
    continue
if disk_space - size < SPACE:
    continue
if seeders <= 0:
    continue
if leechers / seeders <= LS_RATIO:
    continue
```

**修改后:**
```python
# 使用策略系统
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

should_download = strategy_manager.should_download(torrent_info)
if not should_download:
    continue
```

### 2. 新增功能

- **配置化管理**: 支持JSON配置文件管理策略
- **动态切换**: 可以在运行时切换不同策略
- **优先级计算**: 为种子计算下载优先级
- **详细日志**: 提供详细的决策日志
- **错误处理**: 策略系统失败时使用原有逻辑作为兜底

## 使用方法

### 1. 基本使用

```python
from strategies.strategy_manager import StrategyManager

# 创建策略管理器
manager = StrategyManager("strategies/config_example.json")

# 判断是否下载
should_download = manager.should_download(torrent_info)

# 获取优先级
priority = manager.get_priority(torrent_info)
```

### 2. 环境变量配置

```bash
# 策略配置文件路径
STRATEGY_CONFIG_FILE=strategies/config_example.json
```

### 3. 策略切换

```python
# 查看可用策略
available_strategies = manager.get_available_strategies()

# 切换策略
manager.set_current_strategy("conservative")
```

## 配置示例

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

## 测试

运行测试脚本验证策略系统：

```bash
cd app
python test_strategies.py
```

测试内容包括：
- 基本策略功能测试
- 不同类型种子测试
- 策略切换测试
- 边界情况测试

## 优势

1. **灵活性**: 支持多种策略组合，可以根据需要调整
2. **可配置性**: 通过配置文件管理策略，无需修改代码
3. **可扩展性**: 易于添加新的策略类型
4. **可维护性**: 策略逻辑分离，便于维护和调试
5. **向后兼容**: 策略系统失败时使用原有逻辑作为兜底

## 注意事项

1. 策略配置文件路径可以通过环境变量 `STRATEGY_CONFIG_FILE` 指定
2. 如果配置文件不存在，系统会使用默认策略
3. 策略系统失败时会自动回退到原有的硬编码逻辑
4. 建议在生产环境中使用配置文件管理策略
5. 所有大小参数都以字节为单位，时间参数以秒为单位

## 未来扩展

1. **更多策略类型**: 可以添加基于类别、标签等的策略
2. **机器学习**: 可以集成机器学习算法来优化策略
3. **Web界面**: 可以添加Web界面来管理策略配置
4. **策略性能监控**: 可以添加策略性能统计和监控功能
5. **A/B测试**: 可以支持策略的A/B测试功能 