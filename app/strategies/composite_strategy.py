"""
组合策略类
可以组合多个策略，支持AND、OR、加权等组合方式
"""

from typing import Dict, Any, List
from .base_strategy import BaseStrategy


class CompositeStrategy(BaseStrategy):
    """组合策略类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化组合策略
        
        Args:
            config: 配置字典，包含以下参数：
                - strategies: 策略列表
                - combination_type: 组合类型 ('and', 'or', 'weighted')
                - weights: 各策略权重（仅用于weighted类型）
        """
        super().__init__(config)
        self.strategies = config.get('strategies', [])
        self.combination_type = config.get('combination_type', 'and').lower()
        self.weights = config.get('weights', [])
        
        # 验证策略列表
        if not self.strategies:
            self.logger.warning("没有配置任何子策略")
    
    def should_download(self, torrent_info: Dict[str, Any]) -> bool:
        """判断是否应该下载该种子"""
        if not self.strategies:
            return True
        
        results = []
        for strategy in self.strategies:
            if hasattr(strategy, 'should_download'):
                result = strategy.should_download(torrent_info)
                results.append(result)
            else:
                self.logger.warning(f"策略 {strategy} 没有 should_download 方法")
                results.append(True)
        
        if self.combination_type == 'and':
            # 所有策略都必须通过
            final_result = all(results)
        elif self.combination_type == 'or':
            # 至少一个策略通过
            final_result = any(results)
        elif self.combination_type == 'weighted':
            # 加权投票
            if len(self.weights) == len(results):
                weighted_sum = sum(w * (1 if r else 0) for w, r in zip(self.weights, results))
                total_weight = sum(self.weights)
                final_result = weighted_sum / total_weight >= 0.5 if total_weight > 0 else False
            else:
                # 权重数量不匹配，使用简单平均
                final_result = sum(results) / len(results) >= 0.5
        else:
            self.logger.error(f"不支持的组合类型: {self.combination_type}")
            final_result = False
        
        # 记录决策
        strategy_names = [s.get_strategy_name() if hasattr(s, 'get_strategy_name') else str(s) for s in self.strategies]
        result_str = ", ".join([f"{name}: {'通过' if r else '拒绝'}" for name, r in zip(strategy_names, results)])
        self.log_decision(torrent_info, final_result, f"组合策略({self.combination_type}) - {result_str}")
        
        return final_result
    
    def get_priority(self, torrent_info: Dict[str, Any]) -> float:
        """获取种子下载优先级"""
        if not self.strategies:
            return 0.5  # 默认中等优先级
        
        priorities = []
        for strategy in self.strategies:
            if hasattr(strategy, 'get_priority'):
                priority = strategy.get_priority(torrent_info)
                priorities.append(priority)
            else:
                self.logger.warning(f"策略 {strategy} 没有 get_priority 方法")
                priorities.append(0.5)
        
        if self.combination_type == 'and':
            # 取最小值（最保守）
            final_priority = min(priorities)
        elif self.combination_type == 'or':
            # 取最大值（最激进）
            final_priority = max(priorities)
        elif self.combination_type == 'weighted':
            # 加权平均
            if len(self.weights) == len(priorities):
                weighted_sum = sum(w * p for w, p in zip(self.weights, priorities))
                total_weight = sum(self.weights)
                final_priority = weighted_sum / total_weight if total_weight > 0 else 0.5
            else:
                # 权重数量不匹配，使用简单平均
                final_priority = sum(priorities) / len(priorities)
        else:
            # 默认使用简单平均
            final_priority = sum(priorities) / len(priorities)
        
        return max(0.0, min(1.0, final_priority))
    
    def add_strategy(self, strategy: BaseStrategy):
        """添加子策略"""
        self.strategies.append(strategy)
    
    def remove_strategy(self, strategy: BaseStrategy):
        """移除子策略"""
        if strategy in self.strategies:
            self.strategies.remove(strategy)
    
    def set_weights(self, weights: List[float]):
        """设置策略权重"""
        if len(weights) == len(self.strategies):
            self.weights = weights
        else:
            self.logger.error(f"权重数量 {len(weights)} 与策略数量 {len(self.strategies)} 不匹配")
    
    def validate_config(self) -> bool:
        """验证配置参数"""
        if not isinstance(self.strategies, list):
            self.logger.error("strategies 必须是列表类型")
            return False
        
        if self.combination_type not in ['and', 'or', 'weighted']:
            self.logger.error(f"不支持的组合类型: {self.combination_type}")
            return False
        
        if self.combination_type == 'weighted' and self.weights:
            if len(self.weights) != len(self.strategies):
                self.logger.error("权重数量与策略数量不匹配")
                return False
            
            if any(w < 0 for w in self.weights):
                self.logger.error("权重不能为负数")
                return False
        
        # 验证所有子策略
        for strategy in self.strategies:
            if hasattr(strategy, 'validate_config'):
                if not strategy.validate_config():
                    return False
        
        return True 