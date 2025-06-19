"""
策略工厂类
用于创建和管理各种刷流策略
"""

from typing import Dict, Any, List, Optional
import logging
from .base_strategy import BaseStrategy
from .size_based_strategy import SizeBasedStrategy
from .ratio_based_strategy import RatioBasedStrategy
from .time_based_strategy import TimeBasedStrategy
from .composite_strategy import CompositeStrategy


class StrategyFactory:
    """策略工厂类"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._strategies = {}
        self._register_default_strategies()
    
    def _register_default_strategies(self):
        """注册默认策略"""
        self.register_strategy('size', SizeBasedStrategy)
        self.register_strategy('ratio', RatioBasedStrategy)
        self.register_strategy('time', TimeBasedStrategy)
        self.register_strategy('composite', CompositeStrategy)
    
    def register_strategy(self, name: str, strategy_class: type):
        """注册策略类"""
        if not issubclass(strategy_class, BaseStrategy):
            self.logger.error(f"策略类 {strategy_class} 必须继承自 BaseStrategy")
            return False
        
        self._strategies[name] = strategy_class
        self.logger.info(f"注册策略: {name} -> {strategy_class.__name__}")
        return True
    
    def create_strategy(self, name: str, config: Dict[str, Any]) -> Optional[BaseStrategy]:
        """创建策略实例"""
        if name not in self._strategies:
            self.logger.error(f"未找到策略: {name}")
            return None
        
        try:
            strategy_class = self._strategies[name]
            strategy = strategy_class(config)
            
            # 验证配置
            if hasattr(strategy, 'validate_config') and not strategy.validate_config():
                self.logger.error(f"策略 {name} 配置验证失败")
                return None
            
            self.logger.info(f"成功创建策略: {name}")
            return strategy
        except Exception as e:
            self.logger.error(f"创建策略 {name} 失败: {e}")
            return None
    
    def create_composite_strategy(self, config: Dict[str, Any]) -> Optional[CompositeStrategy]:
        """创建组合策略"""
        strategies_config = config.get('strategies', [])
        strategies = []
        
        for strategy_config in strategies_config:
            strategy_name = strategy_config.get('type')
            strategy_params = strategy_config.get('params', {})
            
            if not strategy_name:
                self.logger.error("策略配置缺少 type 字段")
                continue
            
            strategy = self.create_strategy(strategy_name, strategy_params)
            if strategy:
                strategies.append(strategy)
            else:
                self.logger.error(f"创建子策略 {strategy_name} 失败")
        
        if not strategies:
            self.logger.error("没有成功创建任何子策略")
            return None
        
        # 创建组合策略
        composite_config = {
            'strategies': strategies,
            'combination_type': config.get('combination_type', 'and'),
            'weights': config.get('weights', [])
        }
        
        return self.create_strategy('composite', composite_config)
    
    def get_available_strategies(self) -> List[str]:
        """获取可用的策略列表"""
        return list(self._strategies.keys())
    
    def create_default_strategy_set(self) -> CompositeStrategy:
        """创建默认策略组合"""
        # 创建各个子策略
        size_strategy = SizeBasedStrategy({
            'min_size': 1 * 1024 * 1024 * 1024,  # 1GB
            'max_size': 30 * 1024 * 1024 * 1024,  # 30GB
            'min_disk_space': 80 * 1024 * 1024 * 1024,  # 80GB
        })
        
        ratio_strategy = RatioBasedStrategy({
            'min_seeders': 1,
            'min_ratio': 0.1,
            'max_ratio': 10.0,
        })
        
        time_strategy = TimeBasedStrategy({
            'max_publish_age': 24 * 60 * 60,  # 24小时
            'min_free_time': 10 * 60 * 60,  # 10小时
        })
        
        # 创建组合策略 - 只传递策略对象，不包含在配置中
        composite_config = {
            'strategies': [size_strategy, ratio_strategy, time_strategy],
            'combination_type': 'and',
            'weights': [0.4, 0.3, 0.3]  # 大小策略权重最高
        }
        
        return CompositeStrategy(composite_config)
    
    def create_strategy_from_config(self, config: Dict[str, Any]) -> Optional[BaseStrategy]:
        """从配置字典创建策略"""
        strategy_type = config.get('type')
        
        if not strategy_type:
            self.logger.error("配置缺少 type 字段")
            return None
        
        if strategy_type == 'composite':
            return self.create_composite_strategy(config)
        else:
            params = config.get('params', {})
            return self.create_strategy(strategy_type, params) 