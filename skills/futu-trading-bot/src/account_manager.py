#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
账户管理封装模块
为LLM提供封装好的账户查询、解锁与锁定交易功能
"""

from typing import Dict, Any, Optional, List
import logging
import json
import os
import hashlib
from datetime import datetime

try:
    import futu as ft
    from futu import TrdMarket, SecurityFirm
except Exception as e:
    raise RuntimeError(
        "加载 futu SDK 失败。若你在 OpenClaw/Codex 或其他受限沙箱中运行，请改用 host/elevated 模式。"
        "Futu SDK 在导入阶段可能需要访问本机 OpenD 资源并写入 ~/.com.futunn.FutuOpenD/Log。"
    ) from e

# 导入配置管理模块
from config_manager import (
    get_host,
    get_port,
    get_security_firm,
    get_trade_password,
    get_trade_password_md5,
)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AccountManager:
    """
    账户管理器类
    封装账户查询和交易锁功能，供LLM调用
    """
    
    def __init__(self):
        """初始化Futu API连接"""
        # 从配置文件获取连接参数
        host = get_host()
        port = get_port()
        security_firm = get_security_firm()
        
        self.quote_ctx = ft.OpenQuoteContext(host=host, port=port)
        self.trd_ctx = ft.OpenSecTradeContext(
            filter_trdmarket=TrdMarket.HK,
            host=host,
            port=port,
            security_firm=security_firm
        )
        self.account_info_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "json", "account_info.json")
        )
        
    def __del__(self):
        """析构函数，关闭连接"""
        self.close()

    def close(self):
        """显式关闭账户相关上下文连接"""
        try:
            if hasattr(self, 'quote_ctx'):
                self.quote_ctx.close()
            if hasattr(self, 'trd_ctx'):
                self.trd_ctx.close()
        except Exception as e:
            logger.error(f"关闭连接时出错: {e}")
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        获取账户信息
        
        Returns:
            Dict[str, Any]: 账户信息字典，包含：
                - account_id: 账户ID
                - account_type: 账户类型
                - market: 市场
                - net_assets: 净资产
                - cash: 现金
                - power: 购买力
                - risk: 风险指标
                - success: 操作是否成功
                - error_msg: 错误信息（如果有）
        """
        try:
            # 获取账户列表
            ret, data = self.trd_ctx.get_acc_list()
            
            if ret == ft.RET_OK:
                # 处理多个账户的情况
                if len(data) > 0:
                    accounts = []
                    for i in range(len(data)):
                        account_info = {
                            'account_id': str(data['acc_id'].iloc[i]),
                            'account_type': str(data['trd_env'].iloc[i]),
                            'market': str(data['trdmarket_auth'].iloc[i]) if 'trdmarket_auth' in data.columns else 'N/A',
                            'acc_type': str(data['acc_type'].iloc[i]) if 'acc_type' in data.columns else 'N/A',
                            'security_firm': str(data['security_firm'].iloc[i]) if 'security_firm' in data.columns else 'N/A',
                            'sim_acc_type': str(data['sim_acc_type'].iloc[i]) if 'sim_acc_type' in data.columns else 'N/A',
                            'acc_status': str(data['acc_status'].iloc[i]) if 'acc_status' in data.columns else 'N/A'
                        }
                        accounts.append(account_info)
                    
                    result = {
                        'success': True,
                        'accounts': accounts,
                        'error_msg': None
                    }
                    self._save_account_info_to_file(result)
                    logger.info(f"账户信息获取成功，共 {len(accounts)} 个账户")
                    return result
                else:
                    result = {
                        'success': True,
                        'accounts': [],
                        'error_msg': None
                    }
                    self._save_account_info_to_file(result)
                    logger.info("账户信息获取成功，但没有账户数据")
                    return result
            else:
                error_msg = f"获取账户信息失败: {data}"
                logger.error(error_msg)
                result = {
                    'success': False,
                    'error_msg': error_msg,
                    'accounts': None
                }
                self._save_account_info_to_file(result)
                return result
                
        except Exception as e:
            error_msg = f"获取账户信息时发生异常: {str(e)}"
            logger.error(error_msg)
            result = {
                'success': False,
                'error_msg': error_msg,
                'accounts': None
            }
            self._save_account_info_to_file(result)
            return result

    def _save_account_info_to_file(self, result: Dict[str, Any]) -> None:
        """
        将本次账户查询结果写入本地JSON文件（每次覆盖）
        """
        payload = {
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "data": result
        }
        try:
            with open(self.account_info_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            logger.info(f"账户信息已写入本地文件: {self.account_info_file}")
        except Exception as e:
            logger.error(f"保存账户信息到本地文件失败: {str(e)}")
    
    def unlock_trade(self, password: Optional[str] = None, password_md5: Optional[str] = None) -> Dict[str, Any]:
        """
        解锁交易权限
        
        Args:
            password (str, optional): 明文交易密码
            password_md5 (str, optional): 交易密码MD5（32位小写）
            
        Returns:
            Dict[str, Any]: 解锁结果字典，包含：
                - success: 操作是否成功
                - error_msg: 错误信息（如果有）
        """
        try:
            if password_md5:
                ret, data = self.trd_ctx.unlock_trade(password_md5=password_md5)
            elif password:
                password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
                ret, data = self.trd_ctx.unlock_trade(password_md5=password_hash)
            else:
                return {'success': False, 'error_msg': "未提供交易密码或MD5密码"}
            
            if ret == ft.RET_OK:
                logger.info("交易权限解锁成功")
                return {
                    'success': True,
                    'error_msg': None
                }
            else:
                error_msg = f"解锁交易权限失败: {data}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error_msg': error_msg
                }
                
        except Exception as e:
            error_msg = f"解锁交易权限时发生异常: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error_msg': error_msg
            }
    
    def lock_trade(self, password: Optional[str] = None, password_md5: Optional[str] = None) -> Dict[str, Any]:
        """
        锁定交易权限

        Args:
            password (str, optional): 明文交易密码
            password_md5 (str, optional): 交易密码MD5（32位小写）

        Returns:
            Dict[str, Any]: 锁定结果字典，包含：
                - success: 操作是否成功
                - error_msg: 错误信息（如果有）
        """
        try:
            if password_md5:
                ret, data = self.trd_ctx.unlock_trade(password_md5=password_md5, is_unlock=False)
            elif password:
                password_hash = hashlib.md5(password.encode("utf-8")).hexdigest()
                ret, data = self.trd_ctx.unlock_trade(password_md5=password_hash, is_unlock=False)
            else:
                return {'success': False, 'error_msg': "未提供交易密码或MD5密码"}

            if ret == ft.RET_OK:
                logger.info("交易权限锁定成功")
                return {
                    'success': True,
                    'error_msg': None
                }
            else:
                error_msg = f"锁定交易权限失败: {data}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error_msg': error_msg
                }

        except Exception as e:
            error_msg = f"锁定交易权限时发生异常: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error_msg': error_msg
            }


def get_account_info() -> Dict[str, Any]:
    """
    获取账户信息的便捷函数
    供LLM直接调用
    
    Returns:
        Dict[str, Any]: 账户信息
    """
    manager = AccountManager()
    try:
        return manager.get_account_info()
    finally:
        manager.close()


def unlock_trade(password: Optional[str] = None, password_md5: Optional[str] = None) -> Dict[str, Any]:
    """
    解锁交易权限的便捷函数
    供LLM直接调用
    
    Args:
        password (str, optional): 明文交易密码，不提供则从配置文件读取
        password_md5 (str, optional): 交易密码MD5，不提供则从配置文件读取
    
    Returns:
        Dict[str, Any]: 解锁结果
    """
    try:
        if password_md5 is None:
            password_md5 = get_trade_password_md5()
        if password is None:
            password = get_trade_password()
        if not password and not password_md5:
                return {
                    'success': False,
                    'error_msg': "未配置交易密码，请在json/config.json中配置trade_password或trade_password_md5"
                }

        manager = AccountManager()
        try:
            return manager.unlock_trade(password=password, password_md5=password_md5)
        finally:
            manager.close()
    except Exception as e:
        return {
            'success': False,
            'error_msg': f"解锁交易时发生错误: {str(e)}"
        }

def lock_trade(password: Optional[str] = None, password_md5: Optional[str] = None) -> Dict[str, Any]:
    """
    锁定交易权限的便捷函数
    供LLM直接调用

    Args:
        password (str, optional): 明文交易密码，不提供则从配置文件读取
        password_md5 (str, optional): 交易密码MD5，不提供则从配置文件读取

    Returns:
        Dict[str, Any]: 锁定结果
    """
    try:
        if password_md5 is None:
            password_md5 = get_trade_password_md5()
        if password is None:
            password = get_trade_password()
        if not password and not password_md5:
            return {
                'success': False,
                'error_msg': "未配置交易密码，请在json/config.json中配置trade_password或trade_password_md5"
            }

        manager = AccountManager()
        try:
            return manager.lock_trade(password=password, password_md5=password_md5)
        finally:
            manager.close()
    except Exception as e:
        return {
            'success': False,
            'error_msg': f"锁定交易时发生错误: {str(e)}"
        }

def unlock_trade_interactive() -> Dict[str, Any]:
    """
    交互式解锁交易权限的便捷函数（兼容旧版本）
    供LLM直接调用
    
    Returns:
        Dict[str, Any]: 解锁结果
    """
    try:
        # 提示用户输入密码
        password = input("请输入交易密码: ")
        
        manager = AccountManager()
        try:
            return manager.unlock_trade(password)
        finally:
            manager.close()
    except Exception as e:
        return {
            'success': False,
            'error_msg': f"输入密码时发生错误: {str(e)}"
        }


# 使用示例（供参考）
if __name__ == "__main__":
    # 示例1: 获取账户信息
    print("=== Account Information Example ===")
    account_info = get_account_info()
    if account_info['success']:
        if account_info['accounts']:
            for i, account in enumerate(account_info['accounts']):
                print(f"账户 {i+1}:")
                print(f"  账户ID: {account['account_id']}")
                print(f"  账户类型: {account['account_type']}")
                print(f"  市场权限: {account['market']}")
                print(f"  账户子类型: {account['acc_type']}")
                print(f"  券商: {account['security_firm']}")
                print(f"  模拟账户类型: {account['sim_acc_type']}")
                print(f"  账户状态: {account['acc_status']}")
                print()
        else:
            print("没有账户数据")
    else:
        print(f"Failed to get account info: {account_info['error_msg']}")
    
    print("\n" + "="*50 + "\n")
    
    # 示例2: 解锁交易权限
    print("=== Unlock Trade Example ===")
    # 注意：这里会提示用户输入密码
    unlock_result = unlock_trade()
    if unlock_result['success']:
        print("Trade unlocked successfully")
    else:
        print(f"Failed to unlock trade: {unlock_result['error_msg']}")
