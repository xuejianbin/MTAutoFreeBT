#!/usr/bin/env python3
"""
策略编辑功能演示脚本
展示如何通过API创建、编辑和管理策略
"""

import requests
import json
import time

# API基础URL
BASE_URL = "http://localhost:5000/api"

def print_response(response, title):
    """打印API响应"""
    print(f"\n=== {title} ===")
    print(f"状态码: {response.status_code}")
    try:
        data = response.json()
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"响应: {response.text}")

def demo_create_strategies():
    """演示创建策略"""
    print("\n🎯 演示：创建策略")
    
    # 1. 创建大小策略
    size_strategy = {
        "name": "我的大小策略",
        "type": "size",
        "description": "根据种子大小和磁盘空间决定下载",
        "config": {
            "min_size": 1 * 1024 * 1024 * 1024,  # 1GB
            "max_size": 20 * 1024 * 1024 * 1024,  # 20GB
            "min_disk_space": 50 * 1024 * 1024 * 1024  # 50GB
        }
    }
    
    response = requests.post(f"{BASE_URL}/strategies", json=size_strategy)
    print_response(response, "创建大小策略")
    
    # 2. 创建比率策略
    ratio_strategy = {
        "name": "我的比率策略",
        "type": "ratio",
        "description": "根据做种/下载比例决定下载",
        "config": {
            "min_seeders": 5,
            "min_ratio": 0.3,
            "max_ratio": 8.0,
            "prefer_high_seeders": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/strategies", json=ratio_strategy)
    print_response(response, "创建比率策略")
    
    # 3. 创建时间策略
    time_strategy = {
        "name": "我的时间策略",
        "type": "time",
        "description": "根据发布时间和免费时间决定下载",
        "config": {
            "max_publish_age": 12 * 3600,  # 12小时
            "min_free_time": 8 * 3600,  # 8小时
            "prefer_new_torrents": True,
            "time_decay_factor": 0.1
        }
    }
    
    response = requests.post(f"{BASE_URL}/strategies", json=time_strategy)
    print_response(response, "创建时间策略")

def demo_list_strategies():
    """演示获取策略列表"""
    print("\n📋 演示：获取策略列表")
    
    response = requests.get(f"{BASE_URL}/strategies")
    print_response(response, "策略列表")

def demo_test_strategy():
    """演示测试策略"""
    print("\n🧪 演示：测试策略")
    
    # 测试种子信息
    test_data = {
        "name": "测试电影种子",
        "size": 8 * 1024 * 1024 * 1024,  # 8GB
        "discount": "FREE",
        "free_time": 15,
        "seeders": 12,
        "leechers": 3,
        "publish_age": 6,
        "disk_space": 80 * 1024 * 1024 * 1024  # 80GB
    }
    
    # 测试大小策略
    response = requests.post(f"{BASE_URL}/strategies/我的大小策略/test", json=test_data)
    print_response(response, "测试大小策略")
    
    # 测试比率策略
    response = requests.post(f"{BASE_URL}/strategies/我的比率策略/test", json=test_data)
    print_response(response, "测试比率策略")

def demo_update_strategy():
    """演示更新策略"""
    print("\n✏️ 演示：更新策略")
    
    # 更新大小策略的配置
    update_data = {
        "action": "update_config",
        "description": "更新后的大小策略 - 更保守的设置",
        "config": {
            "min_size": 2 * 1024 * 1024 * 1024,  # 2GB
            "max_size": 15 * 1024 * 1024 * 1024,  # 15GB
            "min_disk_space": 60 * 1024 * 1024 * 1024  # 60GB
        }
    }
    
    response = requests.put(f"{BASE_URL}/strategies/我的大小策略", json=update_data)
    print_response(response, "更新大小策略")

def demo_set_current_strategy():
    """演示设置当前策略"""
    print("\n🎯 演示：设置当前策略")
    
    # 设置大小策略为当前策略
    set_current_data = {
        "action": "set_current"
    }
    
    response = requests.put(f"{BASE_URL}/strategies/我的大小策略", json=set_current_data)
    print_response(response, "设置当前策略")

def demo_delete_strategy():
    """演示删除策略"""
    print("\n🗑️ 演示：删除策略")
    
    # 删除时间策略
    response = requests.delete(f"{BASE_URL}/strategies/我的时间策略")
    print_response(response, "删除时间策略")

def main():
    """主函数"""
    print("🚀 MTAutoFreeBT 策略编辑功能演示")
    print("=" * 50)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/stats", timeout=5)
        if response.status_code == 200:
            print("✅ Web服务运行正常")
        else:
            print("❌ Web服务响应异常")
            return
    except requests.exceptions.RequestException:
        print("❌ 无法连接到Web服务，请确保服务正在运行")
        print("   运行命令: python web_app.py")
        return
    
    # 执行演示
    try:
        demo_create_strategies()
        time.sleep(1)
        
        demo_list_strategies()
        time.sleep(1)
        
        demo_test_strategy()
        time.sleep(1)
        
        demo_update_strategy()
        time.sleep(1)
        
        demo_set_current_strategy()
        time.sleep(1)
        
        demo_list_strategies()  # 再次查看列表
        time.sleep(1)
        
        demo_delete_strategy()
        time.sleep(1)
        
        demo_list_strategies()  # 最终查看列表
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
    
    print("\n🎉 演示完成！")
    print("\n💡 提示:")
    print("   - 访问 http://localhost:5000/strategies 查看Web界面")
    print("   - 使用Web界面可以更直观地管理策略")
    print("   - 所有操作都会持久化到数据库中")

if __name__ == '__main__':
    main() 