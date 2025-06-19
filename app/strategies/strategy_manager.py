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
    
    def __init__(self, config_file: str = "strategies/config_example.json", db_session=None):
        """
        初始化策略管理器
        
        Args:
            config_file: 策略配置文件路径
            db_session: 数据库会话对象（可选）
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config_file = config_file
        self.db_session = db_session
        self.factory = StrategyFactory()
        self.strategies = {}
        self.current_strategy = None
        self.load_config()
    
    def load_config(self):
        """加载策略配置"""
        try:
            # 首先尝试从数据库加载
            if self.db_session:
                self._load_from_database()
            
            # 如果数据库中没有策略，则从文件加载
            if not self.strategies:
                self._load_from_file()
            
            # 如果都没有，创建默认策略
            if not self.strategies:
                self._create_default_strategies()
                
        except Exception as e:
            self.logger.error(f"加载策略配置失败: {e}")
            self._create_default_strategies()
    
    def _load_from_database(self):
        """从数据库加载策略配置"""
        try:
            # 延迟导入以避免循环导入
            import sys
            if 'web_app' in sys.modules:
                from web_app import StrategyConfig
            else:
                # 如果web_app模块未加载，跳过数据库加载（这是正常情况）
                return
            
            configs = self.db_session.query(StrategyConfig).all()
            
            for config_record in configs:
                try:
                    config_data = json.loads(config_record.config_data)
                    strategy_type = config_data.get('type')
                    params = config_data.get('params', {})
                    
                    # 创建策略配置
                    strategy_config = {
                        'type': strategy_type,
                        'params': params
                    }
                    
                    # 创建策略对象
                    strategy = self.factory.create_strategy_from_config(strategy_config)
                    if strategy:
                        self.strategies[config_record.name] = strategy
                        self.logger.info(f"从数据库加载策略: {config_record.name}")
                        
                        # 如果是激活的策略，设为当前策略
                        if config_record.is_active:
                            self.current_strategy = strategy
                            self.logger.info(f"设置当前策略: {config_record.name}")
                    else:
                        self.logger.error(f"从数据库加载策略 {config_record.name} 失败")
                        
                except Exception as e:
                    self.logger.error(f"解析数据库策略配置失败 {config_record.name}: {e}")
                    
        except Exception as e:
            self.logger.error(f"从数据库加载策略失败: {e}")
    
    def _load_from_file(self):
        """从文件加载策略配置"""
        try:
            if not os.path.exists(self.config_file):
                self.logger.warning(f"配置文件 {self.config_file} 不存在")
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
                    self.logger.info(f"从文件加载策略: {name}")
                else:
                    self.logger.error(f"从文件加载策略 {name} 失败")
            
            # 设置默认策略
            if default_strategy in self.strategies:
                self.current_strategy = self.strategies[default_strategy]
                self.logger.info(f"设置默认策略: {default_strategy}")
            else:
                self.logger.warning(f"默认策略 {default_strategy} 不存在，使用第一个可用策略")
                if self.strategies:
                    first_strategy = next(iter(self.strategies.values()))
                    self.current_strategy = first_strategy
                    
        except Exception as e:
            self.logger.error(f"从文件加载策略配置失败: {e}")
    
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
        
        # 确保配置数据是可序列化的
        config = getattr(strategy, 'config', {})
        if config:
            # 深度复制配置，确保没有不可序列化的对象
            import copy
            try:
                config = copy.deepcopy(config)
                # 特别处理组合策略，移除策略对象
                if 'strategies' in config and isinstance(config['strategies'], list):
                    # 将策略对象替换为策略名称
                    strategy_names = []
                    for s in config['strategies']:
                        if hasattr(s, 'get_strategy_name'):
                            strategy_names.append(s.get_strategy_name())
                        else:
                            strategy_names.append(str(type(s).__name__))
                    config['strategies'] = strategy_names
            except Exception as e:
                # 如果深度复制失败，创建一个简化的配置
                self.logger.warning(f"配置序列化失败: {e}")
                config = {}
        
        info = {
            "name": name,
            "type": strategy.get_strategy_name(),
            "config": config,
        }
        
        if hasattr(strategy, 'validate_config'):
            try:
                info["valid"] = strategy.validate_config()
            except:
                info["valid"] = False
        
        return info
    
    def reload_config(self):
        """重新加载配置"""
        self.logger.info("重新加载策略配置")
        self.strategies.clear()
        self.current_strategy = None
        self.load_config() 