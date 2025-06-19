"""
基于种子大小的刷流策略
根据种子大小、磁盘空间等因素决定是否下载
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from .base_strategy import BaseStrategy


class SizeBasedStrategy(BaseStrategy):
    """基于种子大小的刷流策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化大小策略
        
        Args:
            config: 配置字典，包含以下参数：
                - min_size: 最小种子大小（字节）
                - max_size: 最大种子大小（字节）
                - min_disk_space: 最小保留磁盘空间（字节）
                - size_priority_weight: 大小优先级权重
        """
        super().__init__(config)
        self.min_size = config.get('min_size', 1 * 1024 * 1024 * 1024)  # 默认1GB
        self.max_size = config.get('max_size', 30 * 1024 * 1024 * 1024)  # 默认30GB
        self.min_disk_space = config.get('min_disk_space', 80 * 1024 * 1024 * 1024)  # 默认80GB
        self.size_priority_weight = config.get('size_priority_weight', 1.0)
    
    def should_download(self, torrent_info: Dict[str, Any]) -> bool:
        """判断是否应该下载该种子"""
        size = torrent_info.get('size', 0)
        disk_space = torrent_info.get('disk_space', 0)
        
        # 检查种子大小是否在允许范围内
        if size < self.min_size:
            self.log_decision(torrent_info, False, f"种子大小 {size/1024/1024/1024:.2f}GB 小于最小限制 {self.min_size/1024/1024/1024:.2f}GB")
            return False
        
        if size > self.max_size:
            self.log_decision(torrent_info, False, f"种子大小 {size/1024/1024/1024:.2f}GB 大于最大限制 {self.max_size/1024/1024/1024:.2f}GB")
            return False
        
        # 检查下载后磁盘空间是否足够
        if disk_space - size < self.min_disk_space:
            self.log_decision(torrent_info, False, 
                            f"下载后磁盘空间 {disk_space-size/1024/1024/1024:.2f}GB 将小于最小保留空间 {self.min_disk_space/1024/1024/1024:.2f}GB")
            return False
        
        self.log_decision(torrent_info, True, f"种子大小 {size/1024/1024/1024:.2f}GB 符合要求")
        return True
    
    def get_priority(self, torrent_info: Dict[str, Any]) -> float:
        """获取种子下载优先级"""
        size = torrent_info.get('size', 0)
        disk_space = torrent_info.get('disk_space', 0)
        
        # 基于种子大小的优先级计算
        # 优先选择中等大小的种子（避免过小或过大）
        optimal_size = (self.min_size + self.max_size) / 2
        size_score = 1.0 - abs(size - optimal_size) / optimal_size
        
        # 考虑磁盘空间利用率
        space_utilization = 1.0 - (disk_space - size) / disk_space if disk_space > 0 else 0
        
        # 综合优先级
        priority = size_score * self.size_priority_weight + space_utilization * 0.5
        
        return max(0.0, min(1.0, priority))
    
    def validate_config(self) -> bool:
        """验证配置参数"""
        if self.min_size < 0 or self.max_size < 0:
            self.logger.error("种子大小限制不能为负数")
            return False
        
        if self.min_size > self.max_size:
            self.logger.error("最小种子大小不能大于最大种子大小")
            return False
        
        if self.min_disk_space < 0:
            self.logger.error("最小磁盘空间不能为负数")
            return False
        
        return True 