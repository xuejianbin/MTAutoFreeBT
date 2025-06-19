import requests
import logging
import os
from typing import Optional, Dict, Any, List


class QBittorrentClient:
    """qBittorrent API 客户端封装类"""
    
    def __init__(self, base_url: str = None, username: str = None, password: str = None):
        """
        初始化 qBittorrent 客户端
        
        Args:
            base_url: qBittorrent Web UI 地址
            username: 用户名
            password: 密码
        """
        self.base_url = base_url or os.environ.get("QBURL", "http://192.168.66.10:10000")
        self.username = username or os.environ.get("QBUSER", "admin")
        self.password = password or os.environ.get("QBPWD", "adminadmin")
        self.session = requests.Session()
        self._is_logged_in = False
        
    def login(self) -> bool:
        """
        登录到 qBittorrent
        
        Returns:
            bool: 登录是否成功
        """
        login_url = f"{self.base_url}/api/v2/auth/login"
        login_data = {"username": self.username, "password": self.password}
        
        try:
            response = self.session.post(login_url, data=login_data)
        except requests.exceptions.RequestException as e:
            logging.error(f"qBittorrent 登录失败，请求异常：{e}")
            return False
            
        if response.status_code != 200:
            logging.error(f"qBittorrent 登录失败，HTTP状态码: {response.status_code}")
            return False
            
        self._is_logged_in = True
        logging.info("qBittorrent 登录成功")
        return True
    
    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        return self._is_logged_in
    
    def get_disk_space(self) -> Optional[int]:
        """
        获取磁盘剩余空间
        
        Returns:
            int: 磁盘剩余空间（字节），失败返回 None
        """
        if not self._is_logged_in:
            logging.error("未登录，无法获取磁盘空间")
            return None
            
        url = f"{self.base_url}/api/v2/sync/maindata"
        
        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException as e:
            logging.error(f"获取磁盘空间失败，请求异常：{e}")
            return None
            
        if response.status_code != 200:
            logging.error(f"获取磁盘空间失败，HTTP状态码: {response.status_code}")
            return None
            
        try:
            data = response.json()
            disk_space = int(data["server_state"]["free_space_on_disk"])
            logging.info(f"当前磁盘空间为: {disk_space / 1024 / 1024 / 1024:.2f}G")
            return disk_space
        except (KeyError, ValueError) as e:
            logging.error(f"获取磁盘空间失败，解析异常：{e}")
            return None
    
    def add_torrent_by_url(self, url: str, save_path: str = None, tags: str = None) -> bool:
        """
        通过 URL 添加种子
        
        Args:
            url: 种子下载链接
            save_path: 保存路径
            tags: 标签
            
        Returns:
            bool: 添加是否成功
        """
        if not self._is_logged_in:
            logging.error("未登录，无法添加种子")
            return False
            
        add_torrent_url = f"{self.base_url}/api/v2/torrents/add"
        data = {"urls": url}
        
        if save_path:
            data["savepath"] = save_path
        if tags:
            data["tags"] = tags
            
        try:
            response = self.session.post(add_torrent_url, data=data)
        except requests.exceptions.RequestException as e:
            logging.error(f"种子添加异常：{e}")
            return False
            
        if response.status_code != 200:
            logging.error(f"种子添加失败！HTTP状态码：{response.status_code}")
            return False
            
        logging.info("种子添加成功！")
        return True
    
    def add_torrent_by_file(self, torrent_content: bytes, filename: str, 
                           save_path: str = None, tags: str = None) -> bool:
        """
        通过文件内容添加种子
        
        Args:
            torrent_content: 种子文件内容
            filename: 文件名
            save_path: 保存路径
            tags: 标签
            
        Returns:
            bool: 添加是否成功
        """
        if not self._is_logged_in:
            logging.error("未登录，无法添加种子")
            return False
            
        add_torrent_url = f"{self.base_url}/api/v2/torrents/add"
        
        files = {
            "torrents": (
                f"{filename}.torrent",
                torrent_content,
                "application/x-bittorrent",
            )
        }
        
        data = {}
        if save_path:
            data["savepath"] = save_path
        if tags:
            data["tags"] = tags
            
        try:
            response = self.session.post(add_torrent_url, files=files, data=data)
        except requests.exceptions.RequestException as e:
            logging.error(f"种子添加异常：{e}")
            return False
            
        if response.status_code != 200:
            logging.error(f"种子添加失败！HTTP状态码：{response.status_code}")
            return False
            
        logging.info("种子添加成功！")
        return True
    
    def get_torrents(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取所有种子信息
        
        Returns:
            List[Dict]: 种子信息列表，失败返回 None
        """
        if not self._is_logged_in:
            logging.error("未登录，无法获取种子信息")
            return None
            
        url = f"{self.base_url}/api/v2/torrents/info"
        
        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException as e:
            logging.error(f"获取种子信息失败，请求异常：{e}")
            return None
            
        if response.status_code != 200:
            logging.error(f"获取种子信息失败，HTTP状态码: {response.status_code}")
            return None
            
        try:
            return response.json()
        except ValueError as e:
            logging.error(f"解析种子信息失败：{e}")
            return None
    
    def delete_torrent(self, torrent_hash: str, delete_files: bool = False) -> bool:
        """
        删除种子
        
        Args:
            torrent_hash: 种子哈希值
            delete_files: 是否同时删除文件
            
        Returns:
            bool: 删除是否成功
        """
        if not self._is_logged_in:
            logging.error("未登录，无法删除种子")
            return False
            
        url = f"{self.base_url}/api/v2/torrents/delete"
        data = {"hashes": torrent_hash, "deleteFiles": str(delete_files).lower()}
        
        try:
            response = self.session.post(url, data=data)
        except requests.exceptions.RequestException as e:
            logging.error(f"删除种子异常：{e}")
            return False
            
        if response.status_code != 200:
            logging.error(f"删除种子失败！HTTP状态码：{response.status_code}")
            return False
            
        logging.info("种子删除成功！")
        return True
    
    def pause_torrent(self, torrent_hash: str) -> bool:
        """
        暂停种子
        
        Args:
            torrent_hash: 种子哈希值
            
        Returns:
            bool: 暂停是否成功
        """
        if not self._is_logged_in:
            logging.error("未登录，无法暂停种子")
            return False
            
        url = f"{self.base_url}/api/v2/torrents/pause"
        data = {"hashes": torrent_hash}
        
        try:
            response = self.session.post(url, data=data)
        except requests.exceptions.RequestException as e:
            logging.error(f"暂停种子异常：{e}")
            return False
            
        if response.status_code != 200:
            logging.error(f"暂停种子失败！HTTP状态码：{response.status_code}")
            return False
            
        logging.info("种子暂停成功！")
        return True
    
    def resume_torrent(self, torrent_hash: str) -> bool:
        """
        恢复种子
        
        Args:
            torrent_hash: 种子哈希值
            
        Returns:
            bool: 恢复是否成功
        """
        if not self._is_logged_in:
            logging.error("未登录，无法恢复种子")
            return False
            
        url = f"{self.base_url}/api/v2/torrents/resume"
        data = {"hashes": torrent_hash}
        
        try:
            response = self.session.post(url, data=data)
        except requests.exceptions.RequestException as e:
            logging.error(f"恢复种子异常：{e}")
            return False
            
        if response.status_code != 200:
            logging.error(f"恢复种子失败！HTTP状态码：{response.status_code}")
            return False
            
        logging.info("种子恢复成功！")
        return True
    
    def get_torrent_properties(self, torrent_hash: str) -> Optional[Dict[str, Any]]:
        """
        获取种子详细信息
        
        Args:
            torrent_hash: 种子哈希值
            
        Returns:
            Dict: 种子详细信息，失败返回 None
        """
        if not self._is_logged_in:
            logging.error("未登录，无法获取种子详细信息")
            return None
            
        url = f"{self.base_url}/api/v2/torrents/properties"
        params = {"hash": torrent_hash}
        
        try:
            response = self.session.get(url, params=params)
        except requests.exceptions.RequestException as e:
            logging.error(f"获取种子详细信息失败，请求异常：{e}")
            return None
            
        if response.status_code != 200:
            logging.error(f"获取种子详细信息失败，HTTP状态码: {response.status_code}")
            return None
            
        try:
            return response.json()
        except ValueError as e:
            logging.error(f"解析种子详细信息失败：{e}")
            return None
    
    def get_sync_maindata(self) -> Optional[Dict[str, Any]]:
        """
        获取同步数据（包含服务器状态和种子信息）
        
        Returns:
            Dict: 同步数据，失败返回 None
        """
        if not self._is_logged_in:
            logging.error("未登录，无法获取同步数据")
            return None
            
        url = f"{self.base_url}/api/v2/sync/maindata"
        
        try:
            response = self.session.get(url)
        except requests.exceptions.RequestException as e:
            logging.error(f"获取同步数据失败，请求异常：{e}")
            return None
            
        if response.status_code != 200:
            logging.error(f"获取同步数据失败，HTTP状态码: {response.status_code}")
            return None
            
        try:
            return response.json()
        except ValueError as e:
            logging.error(f"解析同步数据失败：{e}")
            return None
    
    def logout(self):
        """登出"""
        if self._is_logged_in:
            logout_url = f"{self.base_url}/api/v2/auth/logout"
            try:
                self.session.post(logout_url)
            except:
                pass  # 忽略登出时的错误
            finally:
                self._is_logged_in = False
                self.session.close()
                logging.info("qBittorrent 已登出")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.logout() 