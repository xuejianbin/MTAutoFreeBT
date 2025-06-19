#!/usr/bin/env python3
"""
MTAutoFreeBT Web应用启动脚本
"""

import os
import sys
import logging
from web_app import app, init_app
from init_directories import init_directories

def main():
    """主函数"""
    try:
        # 初始化目录
        init_directories()
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/web_app.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # 初始化应用
        init_app()
        
        # 获取配置
        host = os.environ.get('WEB_HOST', '0.0.0.0')
        port = int(os.environ.get('WEB_PORT', 5000))
        debug = os.environ.get('WEB_DEBUG', 'False').lower() == 'true'
        
        logging.info(f"启动Web应用 - 地址: {host}:{port}, 调试模式: {debug}")
        
        # 启动应用
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except Exception as e:
        logging.error(f"启动Web应用失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 