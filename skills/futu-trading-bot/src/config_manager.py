#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理模块
统一管理富途API配置，包括密码、host、port等敏感信息
"""

import json
import os
import logging
from typing import Dict, Any

try:
    from futu import SecurityFirm, TrdEnv as FutuTrdEnv
except Exception as e:
    raise RuntimeError(
        "加载 futu SDK 失败。若你在 OpenClaw/Codex 或其他受限沙箱中运行，请改用 host/elevated 模式。"
        "Futu SDK 在导入阶段可能需要访问本机 OpenD 资源并写入 ~/.com.futunn.FutuOpenD/Log。"
    ) from e

# 配置类
class ConfigManager:
    """配置管理器类"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        config_path = os.path.join(base_dir, 'json', 'config.json')
        
        # 如果配置文件不存在，使用示例配置
        if not os.path.exists(config_path):
            logging.warning(f"配置文件 {config_path} 不存在，请创建配置文件")
            example_paths = [
                os.path.join(base_dir, 'json', 'config_example.json'),
                os.path.join(base_dir, 'json', 'config.example.json'),
            ]
            for example_path in example_paths:
                if os.path.exists(example_path):
                    config_path = example_path
                    logging.warning(f"使用示例配置文件: {example_path}")
                    break
            else:
                raise FileNotFoundError(
                    "配置文件不存在，请创建 json/config.json 或提供 json/config_example.json / json/config.example.json"
                )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logging.info(f"配置文件加载成功: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"配置文件格式错误: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"加载配置文件失败: {str(e)}")
    
    def get_futu_config(self) -> Dict[str, Any]:
        """获取富途API配置"""
        if self._config is None:
            self._load_config()
        
        futu_config = self._config.get('futu_api', {})
        
        # 设置默认值
        default_config = {
            'host': '127.0.0.1',
            'port': 11111,
            'security_firm': 'FUTUSECURITIES',
            'trade_password': '',
            'trade_password_md5': '',
            'default_env': 'SIMULATE'
        }
        
        # 合并配置，用户配置优先
        for key, default_value in default_config.items():
            if key not in futu_config:
                futu_config[key] = default_value
        
        return futu_config
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置"""
        if self._config is None:
            self._load_config()
        
        logging_config = self._config.get('logging', {})
        
        # 设置默认值
        default_config = {
            'level': 'INFO',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        }
        
        # 合并配置，用户配置优先
        for key, default_value in default_config.items():
            if key not in logging_config:
                logging_config[key] = default_value
        
        return logging_config
    
    def get_trade_password(self) -> str:
        """获取交易密码"""
        config = self.get_futu_config()
        return config.get('trade_password', '')

    def get_trade_password_md5(self) -> str:
        """获取交易密码MD5（32位小写）"""
        config = self.get_futu_config()
        return config.get('trade_password_md5', '')
    
    def get_host(self) -> str:
        """获取OpenD主机地址"""
        config = self.get_futu_config()
        return config.get('host', '127.0.0.1')
    
    def get_port(self) -> int:
        """获取OpenD端口"""
        config = self.get_futu_config()
        return config.get('port', 11111)
    
    def get_security_firm(self) -> SecurityFirm:
        """获取券商枚举"""
        config = self.get_futu_config()
        firm_str = config.get('security_firm', 'FUTUSECURITIES')
        
        try:
            return getattr(SecurityFirm, firm_str)
        except AttributeError:
            logging.warning(f"未知的券商代码: {firm_str}，使用默认值 FUTUSECURITIES")
            return SecurityFirm.FUTUSECURITIES
    
    def get_default_env(self) -> FutuTrdEnv:
        """获取默认交易环境枚举"""
        config = self.get_futu_config()
        env_str = config.get('default_env', 'SIMULATE')
        
        if env_str.upper() == 'REAL':
            return FutuTrdEnv.REAL
        else:
            return FutuTrdEnv.SIMULATE
    
    def get_default_env_str(self) -> str:
        """获取默认交易环境字符串"""
        config = self.get_futu_config()
        return config.get('default_env', 'SIMULATE')

# 全局配置管理器实例
_config_manager = ConfigManager()

# 便捷函数
def get_futu_config() -> Dict[str, Any]:
    """获取富途API配置（便捷函数）"""
    return _config_manager.get_futu_config()

def get_trade_password() -> str:
    """获取交易密码（便捷函数）"""
    return _config_manager.get_trade_password()

def get_trade_password_md5() -> str:
    """获取交易密码MD5（便捷函数）"""
    return _config_manager.get_trade_password_md5()

def get_host() -> str:
    """获取OpenD主机地址（便捷函数）"""
    return _config_manager.get_host()

def get_port() -> int:
    """获取OpenD端口（便捷函数）"""
    return _config_manager.get_port()

def get_security_firm() -> SecurityFirm:
    """获取券商枚举（便捷函数）"""
    return _config_manager.get_security_firm()

def get_default_env() -> FutuTrdEnv:
    """获取默认交易环境枚举（便捷函数）"""
    return _config_manager.get_default_env()

def get_default_env_str() -> str:
    """获取默认交易环境字符串（便捷函数）"""
    return _config_manager.get_default_env_str()

# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("=== 配置管理模块测试 ===")
    
    try:
        # 测试配置加载
        config = get_futu_config()
        print(f"富途API配置: {config}")
        
        print(f"\n详细配置项:")
        print(f"主机: {get_host()}")
        print(f"端口: {get_port()}")
        print(f"券商: {get_security_firm()}")
        print(f"交易密码: {'*' * len(get_trade_password()) if get_trade_password() else '(空)'}")
        print(f"默认环境: {get_default_env_str()}")
        
        print("\n✅ 配置加载测试通过")
        
    except Exception as e:
        print(f"\n❌ 配置加载测试失败: {str(e)}")
        print("请确保 json/config.json 或 json/config.example.json 文件存在且格式正确")
