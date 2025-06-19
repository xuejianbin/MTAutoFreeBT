#!/usr/bin/env python3
"""
策略编辑功能测试脚本
"""

import json
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.strategy_manager import StrategyManager
from strategies.strategy_factory import StrategyFactory

def test_strategy_creation():
    """测试策略创建功能"""
    print("=== 测试策略创建功能 ===")
    
    # 创建策略工厂
    factory = StrategyFactory()
    
    # 测试创建大小策略
    size_config = {
        'type': 'size',
        'params': {
            'min_size': 1 * 1024 * 1024 * 1024,  # 1GB
            'max_size': 30 * 1024 * 1024 * 1024,  # 30GB
            'min_disk_space': 80 * 1024 * 1024 * 1024,  # 80GB
        }
    }
    
    size_strategy = factory.create_strategy_from_config(size_config)
    if size_strategy:
        print("✓ 大小策略创建成功")
        print(f"  策略名称: {size_strategy.get_strategy_name()}")
        print(f"  配置: {size_strategy.config}")
    else:
        print("✗ 大小策略创建失败")
    
    # 测试创建比率策略
    ratio_config = {
        'type': 'ratio',
        'params': {
            'min_seeders': 3,
            'min_ratio': 0.2,
            'max_ratio': 5.0,
            'prefer_high_seeders': True
        }
    }
    
    ratio_strategy = factory.create_strategy_from_config(ratio_config)
    if ratio_strategy:
        print("✓ 比率策略创建成功")
        print(f"  策略名称: {ratio_strategy.get_strategy_name()}")
        print(f"  配置: {ratio_strategy.config}")
    else:
        print("✗ 比率策略创建失败")
    
    # 测试创建时间策略
    time_config = {
        'type': 'time',
        'params': {
            'max_publish_age': 24 * 3600,  # 24小时
            'min_free_time': 10 * 3600,  # 10小时
            'prefer_new_torrents': True,
            'time_decay_factor': 0.05
        }
    }
    
    time_strategy = factory.create_strategy_from_config(time_config)
    if time_strategy:
        print("✓ 时间策略创建成功")
        print(f"  策略名称: {time_strategy.get_strategy_name()}")
        print(f"  配置: {time_strategy.config}")
    else:
        print("✗ 时间策略创建失败")

def test_strategy_manager():
    """测试策略管理器功能"""
    print("\n=== 测试策略管理器功能 ===")
    
    # 创建策略管理器
    manager = StrategyManager()
    
    print(f"可用策略: {manager.get_available_strategies()}")
    print(f"当前策略: {manager.get_current_strategy().get_strategy_name() if manager.get_current_strategy() else 'None'}")
    
    # 测试种子信息
    torrent_info = {
        'id': 'test_123',
        'name': '测试种子',
        'size': 5 * 1024 * 1024 * 1024,  # 5GB
        'discount': 'FREE',
        'discount_end_time': None,
        'seeders': 10,
        'leechers': 5,
        'publish_time': None,
        'disk_space': 100 * 1024 * 1024 * 1024  # 100GB
    }
    
    should_download = manager.should_download(torrent_info)
    priority = manager.get_priority(torrent_info)
    
    print(f"测试种子下载决策: {should_download}")
    print(f"测试种子优先级: {priority}")

def test_strategy_info():
    """测试策略信息获取功能"""
    print("\n=== 测试策略信息获取功能 ===")
    
    manager = StrategyManager()
    
    for strategy_name in manager.get_available_strategies():
        info = manager.get_strategy_info(strategy_name)
        print(f"策略 {strategy_name}:")
        print(f"  类型: {info.get('type', 'Unknown')}")
        print(f"  配置: {json.dumps(info.get('config', {}), indent=2, ensure_ascii=False)}")
        print()

if __name__ == '__main__':
    test_strategy_creation()
    test_strategy_manager()
    test_strategy_info()
    print("\n=== 测试完成 ===") 