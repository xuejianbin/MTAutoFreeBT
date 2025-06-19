"""
策略使用示例
演示如何使用策略系统
"""

import logging
from datetime import datetime, timedelta
from strategy_manager import StrategyManager

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def example_usage():
    """策略使用示例"""
    
    # 创建策略管理器
    manager = StrategyManager("config_example.json")
    
    # 显示可用策略
    print("可用策略:", manager.get_available_strategies())
    
    # 获取当前策略信息
    current_info = manager.get_strategy_info()
    print("当前策略信息:", current_info)
    
    # 模拟种子信息
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
    
    # 使用策略判断是否下载
    should_download = manager.should_download(torrent_info)
    priority = manager.get_priority(torrent_info)
    
    print(f"种子 {torrent_info['name']} 是否应该下载: {should_download}")
    print(f"种子 {torrent_info['name']} 优先级: {priority:.2f}")
    
    # 切换策略
    if "conservative" in manager.get_available_strategies():
        manager.set_current_strategy("conservative")
        should_download_conservative = manager.should_download(torrent_info)
        priority_conservative = manager.get_priority(torrent_info)
        
        print(f"保守策略 - 是否下载: {should_download_conservative}")
        print(f"保守策略 - 优先级: {priority_conservative:.2f}")
    
    if "aggressive" in manager.get_available_strategies():
        manager.set_current_strategy("aggressive")
        should_download_aggressive = manager.should_download(torrent_info)
        priority_aggressive = manager.get_priority(torrent_info)
        
        print(f"激进策略 - 是否下载: {should_download_aggressive}")
        print(f"激进策略 - 优先级: {priority_aggressive:.2f}")

def test_different_torrents():
    """测试不同类型的种子"""
    manager = StrategyManager("config_example.json")
    
    # 测试用例
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
        }
    ]
    
    print("\n=== 测试不同种子 ===")
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
        
        print(f"{case['name']}: 下载={should_download}, 优先级={priority:.2f}")

if __name__ == "__main__":
    example_usage()
    test_different_torrents() 