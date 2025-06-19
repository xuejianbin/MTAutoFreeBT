"""
策略管理器类
用于管理策略配置的加载、保存和应用
"""

import json
import os
from typing import Dict, Any, Optional, List
import logging
from .strategy_factory import StrategyFactory
from .base_strategy import BaseStrategy


class StrategyManager:
    """策略管理器类"""
    
    def __init__(self, config_file: str = "strategies/config_example.json"):
        """
        初始化策略管理器
        
        Args:
            config_file: 策略配置文件路径
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file
        self.factory = StrategyFactory()
        self.strategies = {}
        self.current_strategy = None
        self.load_config()
    
    def load_config(self):
        """加载策略配置"""
        try:
            if not os.path.exists(self.config_file):
                self.logger.warning(f"配置文件 {self.config_file} 不存在，使用默认策略")
                self._create_default_strategies()
                return
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            strategy_configs = config.get('strategy_configs', {})
            default_strategy = config.get('default_strategy', 'balanced')
            
            # 创建所有策略
            for name, strategy_config in strategy_configs.items():
                strategy = self.factory.create_strategy_from_config(strategy_config)
                if strategy:
                    self.strategies[name] = strategy
                    self.logger.info(f"成功加载策略: {name}")
                else:
                    self.logger.error(f"加载策略 {name} 失败")
            
            # 设置默认策略
            if default_strategy in self.strategies:
                self.current_strategy = self.strategies[default_strategy]
                self.logger.info(f"设置默认策略: {default_strategy}")
            else:
                self.logger.warning(f"默认策略 {default_strategy} 不存在，使用第一个可用策略")
                if self.strategies:
                    first_strategy = next(iter(self.strategies.values()))
                    self.current_strategy = first_strategy
                else:
                    self._create_default_strategies()
                    
        except Exception as e:
            self.logger.error(f"加载策略配置失败: {e}")
            self._create_default_strategies()
    
    def _create_default_strategies(self):
        """创建默认策略"""
        self.logger.info("创建默认策略")
        self.current_strategy = self.factory.create_default_strategy_set()
        self.strategies['default'] = self.current_strategy
    
    def save_config(self, config_file: str = None):
        """保存策略配置"""
        if config_file is None:
            config_file = self.config_file
        
        try:
            # 创建配置目录
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            
            config = {
                'strategy_configs': {},
                'default_strategy': 'default'
            }
            
            # 这里可以添加保存当前策略配置的逻辑
            # 由于策略配置比较复杂，这里只是保存基本结构
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"策略配置已保存到: {config_file}")
            
        except Exception as e:
            self.logger.error(f"保存策略配置失败: {e}")
    
    def get_strategy(self, name: str) -> Optional[BaseStrategy]:
        """获取指定名称的策略"""
        return self.strategies.get(name)
    
    def set_current_strategy(self, name: str) -> bool:
        """设置当前使用的策略"""
        strategy = self.get_strategy(name)
        if strategy:
            self.current_strategy = strategy
            self.logger.info(f"切换到策略: {name}")
            return True
        else:
            self.logger.error(f"策略 {name} 不存在")
            return False
    
    def get_current_strategy(self) -> Optional[BaseStrategy]:
        """获取当前使用的策略"""
        return self.current_strategy
    
    def get_available_strategies(self) -> List[str]:
        """获取可用的策略列表"""
        return list(self.strategies.keys())
    
    def add_strategy(self, name: str, strategy: BaseStrategy) -> bool:
        """添加新策略"""
        if name in self.strategies:
            self.logger.warning(f"策略 {name} 已存在，将被覆盖")
        
        self.strategies[name] = strategy
        self.logger.info(f"添加策略: {name}")
        return True
    
    def remove_strategy(self, name: str) -> bool:
        """移除策略"""
        if name not in self.strategies:
            self.logger.error(f"策略 {name} 不存在")
            return False
        
        if self.current_strategy == self.strategies[name]:
            self.logger.warning(f"正在移除当前使用的策略 {name}")
            # 切换到其他策略
            other_strategies = [k for k in self.strategies.keys() if k != name]
            if other_strategies:
                self.set_current_strategy(other_strategies[0])
            else:
                self.current_strategy = None
        
        del self.strategies[name]
        self.logger.info(f"移除策略: {name}")
        return True
    
    def should_download(self, torrent_info: Dict[str, Any]) -> bool:
        """使用当前策略判断是否应该下载"""
        if not self.current_strategy:
            self.logger.error("没有设置当前策略")
            return False
        
        return self.current_strategy.should_download(torrent_info)
    
    def get_priority(self, torrent_info: Dict[str, Any]) -> float:
        """使用当前策略获取优先级"""
        if not self.current_strategy:
            self.logger.error("没有设置当前策略")
            return 0.0
        
        return self.current_strategy.get_priority(torrent_info)
    
    def get_strategy_info(self, name: str = None) -> Dict[str, Any]:
        """获取策略信息"""
        if name is None:
            strategy = self.current_strategy
            name = "current"
        else:
            strategy = self.get_strategy(name)
        
        if not strategy:
            return {"error": f"策略 {name} 不存在"}
        
        info = {
            "name": name,
            "type": strategy.get_strategy_name(),
            "config": getattr(strategy, 'config', {}),
        }
        
        if hasattr(strategy, 'validate_config'):
            info["valid"] = strategy.validate_config()
        
        return info
    
    def reload_config(self):
        """重新加载配置"""
        self.logger.info("重新加载策略配置")
        self.strategies.clear()
        self.current_strategy = None
        self.load_config() 