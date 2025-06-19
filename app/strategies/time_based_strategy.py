"""
基于时间的刷流策略
根据种子发布时间、免费时间等因素决定是否下载
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from .base_strategy import BaseStrategy


class TimeBasedStrategy(BaseStrategy):
    """基于时间的刷流策略"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化时间策略
        
        Args:
            config: 配置字典，包含以下参数：
                - max_publish_age: 最大发布时间（秒）
                - min_free_time: 最小剩余免费时间（秒）
                - time_priority_weight: 时间优先级权重
                - prefer_new_torrents: 是否优先选择新发布的种子
                - time_decay_factor: 时间衰减因子
        """
        super().__init__(config)
        self.max_publish_age = config.get('max_publish_age', 24 * 60 * 60)  # 默认24小时
        self.min_free_time = config.get('min_free_time', 10 * 60 * 60)  # 默认10小时
        self.time_priority_weight = config.get('time_priority_weight', 1.0)
        self.prefer_new_torrents = config.get('prefer_new_torrents', True)
        self.time_decay_factor = config.get('time_decay_factor', 0.1)
    
    def should_download(self, torrent_info: Dict[str, Any]) -> bool:
        """判断是否应该下载该种子"""
        publish_time = torrent_info.get('publish_time')
        discount_end_time = torrent_info.get('discount_end_time')
        
        if not publish_time:
            self.log_decision(torrent_info, False, "缺少发布时间信息")
            return False
        
        # 检查发布时间是否在允许范围内
        now = datetime.now()
        age = (now - publish_time).total_seconds()
        
        if age > self.max_publish_age:
            self.log_decision(torrent_info, False, 
                            f"种子发布时间 {age/3600:.1f}小时 超过最大限制 {self.max_publish_age/3600:.1f}小时")
            return False
        
        # 检查剩余免费时间是否足够
        if discount_end_time:
            remaining_free_time = (discount_end_time - now).total_seconds()
            if remaining_free_time < self.min_free_time:
                self.log_decision(torrent_info, False, 
                                f"剩余免费时间 {remaining_free_time/3600:.1f}小时 小于最小要求 {self.min_free_time/3600:.1f}小时")
                return False
        
        self.log_decision(torrent_info, True, f"发布时间 {age/3600:.1f}小时 符合要求")
        return True
    
    def get_priority(self, torrent_info: Dict[str, Any]) -> float:
        """获取种子下载优先级"""
        publish_time = torrent_info.get('publish_time')
        discount_end_time = torrent_info.get('discount_end_time')
        
        if not publish_time:
            return 0.0
        
        now = datetime.now()
        age = (now - publish_time).total_seconds()
        
        # 基于发布时间的优先级计算
        if self.prefer_new_torrents:
            # 新发布的种子优先级更高
            time_score = max(0.0, 1.0 - age / self.max_publish_age)
        else:
            # 发布时间适中的种子优先级最高
            optimal_age = self.max_publish_age / 2
            time_score = 1.0 - abs(age - optimal_age) / optimal_age
        
        # 基于剩余免费时间的优先级
        free_time_score = 0.0
        if discount_end_time:
            remaining_free_time = (discount_end_time - now).total_seconds()
            if remaining_free_time > 0:
                # 剩余免费时间越长，优先级越高
                free_time_score = min(1.0, remaining_free_time / (24 * 60 * 60))  # 24小时为满分
        
        # 时间衰减因子
        decay = 1.0 / (1.0 + self.time_decay_factor * age / 3600)  # 每小时衰减
        
        # 综合优先级
        priority = (time_score * 0.6 + free_time_score * 0.4) * decay * self.time_priority_weight
        
        return max(0.0, min(1.0, priority))
    
    def validate_config(self) -> bool:
        """验证配置参数"""
        if self.max_publish_age < 0:
            self.logger.error("最大发布时间不能为负数")
            return False
        
        if self.min_free_time < 0:
            self.logger.error("最小剩余免费时间不能为负数")
            return False
        
        if self.time_decay_factor < 0:
            self.logger.error("时间衰减因子不能为负数")
            return False
        
        return True 