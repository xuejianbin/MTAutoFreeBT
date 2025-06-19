#!/usr/bin/env python3
"""
策略系统测试脚本
用于测试策略系统的各种功能
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.strategy_manager import StrategyManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def test_basic_strategies():
    """测试基本策略功能"""
    print("=== 测试基本策略功能 ===")
    
    # 创建策略管理器
    manager = StrategyManager()
    
    # 显示可用策略
    available_strategies = manager.get_available_strategies()
    print(f"可用策略: {available_strategies}")
    
    # 获取当前策略信息
    current_info = manager.get_strategy_info()
    print(f"当前策略信息: {current_info}")
    
    # 测试种子
    test_torrent = {
        "id": "test_123",
        "name": "测试种子",
        "size": 5 * 1024 * 1024 * 1024,  # 5GB
        "discount": "FREE",
        "discount_end_time": datetime.now() + timedelta(hours=20),
        "seeders": 10,
        "leechers": 5,
        "publish_time": datetime.now() - timedelta(hours=2),
        "disk_space": 100 * 1024 * 1024 * 1024  # 100GB
    }
    
    # 测试决策
    should_download = manager.should_download(test_torrent)
    priority = manager.get_priority(test_torrent)
    
    print(f"测试种子决策结果:")
    print(f"  是否下载: {should_download}")
    print(f"  优先级: {priority:.2f}")

def test_different_torrent_types():
    """测试不同类型的种子"""
    print("\n=== 测试不同类型的种子 ===")
    
    manager = StrategyManager()
    
    test_cases = [
        {
            "name": "小种子",
            "size": 500 * 1024 * 1024,  # 500MB
            "seeders": 20,
            "leechers": 2,
            "publish_time": datetime.now() - timedelta(hours=1),
        },
        {
            "name": "大种子",
            "size": 50 * 1024 * 1024 * 1024,  # 50GB
            "seeders": 5,
            "leechers": 15,
            "publish_time": datetime.now() - timedelta(hours=6),
        },
        {
            "name": "热门种子",
            "size": 10 * 1024 * 1024 * 1024,  # 10GB
            "seeders": 100,
            "leechers": 200,
            "publish_time": datetime.now() - timedelta(hours=12),
        },
        {
            "name": "冷门种子",
            "size": 2 * 1024 * 1024 * 1024,  # 2GB
            "seeders": 2,
            "leechers": 1,
            "publish_time": datetime.now() - timedelta(hours=3),
        },
        {
            "name": "老种子",
            "size": 5 * 1024 * 1024 * 1024,  # 5GB
            "seeders": 8,
            "leechers": 3,
            "publish_time": datetime.now() - timedelta(hours=48),
        }
    ]
    
    for case in test_cases:
        torrent_info = {
            "id": f"test_{case['name']}",
            "name": case['name'],
            "size": case['size'],
            "discount": "FREE",
            "discount_end_time": datetime.now() + timedelta(hours=24),
            "seeders": case['seeders'],
            "leechers": case['leechers'],
            "publish_time": case['publish_time'],
            "disk_space": 100 * 1024 * 1024 * 1024  # 100GB
        }
        
        should_download = manager.should_download(torrent_info)
        priority = manager.get_priority(torrent_info)
        
        print(f"{case['name']:12} | 下载: {should_download:5} | 优先级: {priority:.2f}")

def test_strategy_switching():
    """测试策略切换"""
    print("\n=== 测试策略切换 ===")
    
    manager = StrategyManager()
    
    # 测试种子
    test_torrent = {
        "id": "switch_test",
        "name": "策略切换测试种子",
        "size": 15 * 1024 * 1024 * 1024,  # 15GB
        "discount": "FREE",
        "discount_end_time": datetime.now() + timedelta(hours=12),
        "seeders": 3,
        "leechers": 8,
        "publish_time": datetime.now() - timedelta(hours=18),
        "disk_space": 80 * 1024 * 1024 * 1024  # 80GB
    }
    
    available_strategies = manager.get_available_strategies()
    
    for strategy_name in available_strategies:
        if manager.set_current_strategy(strategy_name):
            should_download = manager.should_download(test_torrent)
            priority = manager.get_priority(test_torrent)
            
            print(f"{strategy_name:12} | 下载: {should_download:5} | 优先级: {priority:.2f}")

def test_edge_cases():
    """测试边界情况"""
    print("\n=== 测试边界情况 ===")
    
    manager = StrategyManager()
    
    edge_cases = [
        {
            "name": "超大种子",
            "size": 100 * 1024 * 1024 * 1024,  # 100GB
            "seeders": 1,
            "leechers": 1,
            "disk_space": 50 * 1024 * 1024 * 1024,  # 50GB
        },
        {
            "name": "极小种子",
            "size": 100 * 1024 * 1024,  # 100MB
            "seeders": 50,
            "leechers": 5,
            "disk_space": 200 * 1024 * 1024 * 1024,  # 200GB
        },
        {
            "name": "无做种者",
            "size": 5 * 1024 * 1024 * 1024,  # 5GB
            "seeders": 0,
            "leechers": 10,
            "disk_space": 100 * 1024 * 1024 * 1024,  # 100GB
        },
        {
            "name": "磁盘空间不足",
            "size": 10 * 1024 * 1024 * 1024,  # 10GB
            "seeders": 5,
            "leechers": 2,
            "disk_space": 5 * 1024 * 1024 * 1024,  # 5GB
        }
    ]
    
    for case in edge_cases:
        torrent_info = {
            "id": f"edge_{case['name']}",
            "name": case['name'],
            "size": case['size'],
            "discount": "FREE",
            "discount_end_time": datetime.now() + timedelta(hours=24),
            "seeders": case['seeders'],
            "leechers": case['leechers'],
            "publish_time": datetime.now() - timedelta(hours=1),
            "disk_space": case['disk_space']
        }
        
        should_download = manager.should_download(torrent_info)
        priority = manager.get_priority(torrent_info)
        
        print(f"{case['name']:12} | 下载: {should_download:5} | 优先级: {priority:.2f}")

def main():
    """主函数"""
    print("策略系统测试开始...\n")
    
    try:
        test_basic_strategies()
        test_different_torrent_types()
        test_strategy_switching()
        test_edge_cases()
        
        print("\n=== 测试完成 ===")
        print("所有测试已执行完毕。")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 