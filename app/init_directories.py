#!/usr/bin/env python3
"""
目录初始化脚本
创建应用运行所需的所有目录
"""

import os
import logging

def init_directories():
    """初始化所有必要的目录"""
    directories = [
        'logs',           # 日志目录
        'data',           # 数据目录
        'strategies',     # 策略配置目录
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logging.info(f"目录已创建/确认存在: {directory}")
        except Exception as e:
            logging.error(f"创建目录失败 {directory}: {e}")

if __name__ == '__main__':
    # 配置基本日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    init_directories()
    print("目录初始化完成！") 