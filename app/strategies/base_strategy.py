"""
基础策略类
定义所有刷流策略的通用接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging


class BaseStrategy(ABC):
    """刷流策略基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化策略
        
        Args:
            config: 策略配置参数
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def should_download(self, torrent_info: Dict[str, Any]) -> bool:
        """
        判断是否应该下载该种子
        
        Args:
            torrent_info: 种子信息字典，包含以下字段：
                - id: 种子ID
                - name: 种子名称
                - size: 种子大小（字节）
                - discount: 折扣类型
                - discount_end_time: 折扣结束时间
                - seeders: 做种人数
                - leechers: 下载人数
                - publish_time: 发布时间
                - disk_space: 当前磁盘剩余空间
                
        Returns:
            bool: True表示应该下载，False表示不应该下载
        """
        pass
    
    @abstractmethod
    def get_priority(self, torrent_info: Dict[str, Any]) -> float:
        """
        获取种子下载优先级（数值越大优先级越高）
        
        Args:
            torrent_info: 种子信息字典
            
        Returns:
            float: 优先级数值
        """
        pass
    
    def get_strategy_name(self) -> str:
        """获取策略名称"""
        return self.__class__.__name__
    
    def log_decision(self, torrent_info: Dict[str, Any], decision: bool, reason: str):
        """记录决策日志"""
        torrent_id = torrent_info.get('id', 'unknown')
        name = torrent_info.get('name', 'unknown')
        self.logger.info(f"策略 {self.get_strategy_name()}: 种子 {torrent_id}({name}) - {reason} - 决策: {'下载' if decision else '跳过'}")
    
    def validate_config(self) -> bool:
        """
        验证配置参数是否有效
        
        Returns:
            bool: True表示配置有效，False表示配置无效
        """
        return True 