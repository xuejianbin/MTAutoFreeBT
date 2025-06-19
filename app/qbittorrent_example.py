#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qBittorrent 客户端使用示例
"""

import logging
from qbittorrent_client import QBittorrentClient

# 配置日志
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def main():
    """主函数示例"""
    
    # 方式1：使用环境变量配置
    with QBittorrentClient() as qb:
        if not qb.login():
            logging.error("登录失败")
            return
        
        # 获取磁盘空间
        disk_space = qb.get_disk_space()
        if disk_space:
            logging.info(f"磁盘剩余空间: {disk_space / 1024 / 1024 / 1024:.2f} GB")
        
        # 获取所有种子信息
        torrents = qb.get_torrents()
        if torrents:
            logging.info(f"当前有 {len(torrents)} 个种子")
            for torrent in torrents[:3]:  # 只显示前3个
                logging.info(f"种子: {torrent.get('name', 'Unknown')} - 状态: {torrent.get('state', 'Unknown')}")
    
    # 方式2：直接指定参数
    qb = QBittorrentClient(
        base_url="http://192.168.66.10:10000",
        username="admin",
        password="adminadmin"
    )
    
    try:
        if not qb.login():
            logging.error("登录失败")
            return
        
        # 添加种子示例（需要有效的种子URL）
        # success = qb.add_torrent_by_url(
        #     url="https://example.com/torrent.torrent",
        #     save_path="/download/PT刷流",
        #     tags="MT刷流"
        # )
        # if success:
        #     logging.info("种子添加成功")
        
        # 获取种子详细信息示例
        # torrents = qb.get_torrents()
        # if torrents:
        #     first_torrent = torrents[0]
        #     torrent_hash = first_torrent.get('hash')
        #     if torrent_hash:
        #         properties = qb.get_torrent_properties(torrent_hash)
        #         if properties:
        #             logging.info(f"种子大小: {properties.get('size', 0) / 1024 / 1024 / 1024:.2f} GB")
        
    finally:
        qb.logout()

def advanced_example():
    """高级使用示例"""
    
    qb = QBittorrentClient()
    
    try:
        if not qb.login():
            return
        
        # 获取同步数据（包含服务器状态和种子信息）
        sync_data = qb.get_sync_maindata()
        if sync_data:
            server_state = sync_data.get('server_state', {})
            logging.info(f"下载速度: {server_state.get('dl_info_speed', 0) / 1024 / 1024:.2f} MB/s")
            logging.info(f"上传速度: {server_state.get('up_info_speed', 0) / 1024 / 1024:.2f} MB/s")
            
            torrents = sync_data.get('torrents', {})
            logging.info(f"活跃种子数: {len(torrents)}")
        
        # 种子管理示例
        torrents = qb.get_torrents()
        if torrents:
            for torrent in torrents:
                name = torrent.get('name', 'Unknown')
                state = torrent.get('state', 'Unknown')
                progress = torrent.get('progress', 0)
                
                logging.info(f"种子: {name}")
                logging.info(f"  状态: {state}")
                logging.info(f"  进度: {progress * 100:.1f}%")
                
                # 如果种子已完成，可以暂停它
                if progress >= 1.0 and state == 'uploading':
                    torrent_hash = torrent.get('hash')
                    if torrent_hash:
                        qb.pause_torrent(torrent_hash)
                        logging.info(f"已暂停完成的种子: {name}")
                
                break  # 只处理第一个种子作为示例
    
    finally:
        qb.logout()

if __name__ == "__main__":
    logging.info("=== 基本使用示例 ===")
    main()
    
    logging.info("\n=== 高级使用示例 ===")
    advanced_example() 