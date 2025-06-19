"""
基于做种/下载比例的刷流策略
根据种子的做种人数、下载人数比例决定是否下载
"""

from typing import Dict, Any
from .base_strategy import BaseStrategy


class RatioBasedStrategy(BaseStrategy):
    """基于做种/下载比例的刷流策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化比例策略
        
        Args:
            config: 配置字典，包含以下参数：
                - min_seeders: 最小做种人数
                - min_ratio: 最小下载/做种比例
                - max_ratio: 最大下载/做种比例
                - ratio_priority_weight: 比例优先级权重
                - prefer_high_seeders: 是否优先选择做种人数多的种子
        """
        super().__init__(config)
        self.min_seeders = config.get('min_seeders', 1)
        self.min_ratio = config.get('min_ratio', 0.1)  # 最小比例
        self.max_ratio = config.get('max_ratio', 10.0)  # 最大比例
        self.ratio_priority_weight = config.get('ratio_priority_weight', 1.0)
        self.prefer_high_seeders = config.get('prefer_high_seeders', True)
    
    def should_download(self, torrent_info: Dict[str, Any]) -> bool:
        """判断是否应该下载该种子"""
        seeders = torrent_info.get('seeders', 0)
        leechers = torrent_info.get('leechers', 0)
        
        # 检查做种人数是否足够
        if seeders < self.min_seeders:
            self.log_decision(torrent_info, False, f"做种人数 {seeders} 小于最小要求 {self.min_seeders}")
            return False
        
        # 计算下载/做种比例
        ratio = leechers / seeders if seeders > 0 else 0
        
        # 检查比例是否在允许范围内
        if ratio < self.min_ratio:
            self.log_decision(torrent_info, False, f"下载/做种比例 {ratio:.2f} 小于最小要求 {self.min_ratio}")
            return False
        
        if ratio > self.max_ratio:
            self.log_decision(torrent_info, False, f"下载/做种比例 {ratio:.2f} 大于最大限制 {self.max_ratio}")
            return False
        
        self.log_decision(torrent_info, True, f"做种人数 {seeders}, 下载人数 {leechers}, 比例 {ratio:.2f} 符合要求")
        return True
    
    def get_priority(self, torrent_info: Dict[str, Any]) -> float:
        """获取种子下载优先级"""
        seeders = torrent_info.get('seeders', 0)
        leechers = torrent_info.get('leechers', 0)
        
        if seeders == 0:
            return 0.0
        
        ratio = leechers / seeders
        
        # 基于比例的优先级计算
        # 优先选择比例适中的种子（既不会太拥挤也不会太冷门）
        optimal_ratio = (self.min_ratio + self.max_ratio) / 2
        ratio_score = 1.0 - abs(ratio - optimal_ratio) / optimal_ratio
        
        # 基于做种人数的优先级
        if self.prefer_high_seeders:
            # 做种人数越多，优先级越高（但有上限）
            seeder_score = min(1.0, seeders / 100.0)  # 100个做种者达到最高分
        else:
            # 做种人数适中时优先级最高
            seeder_score = 1.0 - abs(seeders - 50) / 50.0  # 50个做种者达到最高分
        
        # 综合优先级
        priority = ratio_score * self.ratio_priority_weight + seeder_score * 0.5
        
        return max(0.0, min(1.0, priority))
    
    def validate_config(self) -> bool:
        """验证配置参数"""
        if self.min_seeders < 0:
            self.logger.error("最小做种人数不能为负数")
            return False
        
        if self.min_ratio < 0 or self.max_ratio < 0:
            self.logger.error("比例限制不能为负数")
            return False
        
        if self.min_ratio > self.max_ratio:
            self.logger.error("最小比例不能大于最大比例")
            return False
        
        return True 