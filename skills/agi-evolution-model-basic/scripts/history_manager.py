#!/usr/bin/env python3
"""
历史记录管理脚本

功能：
- 管理初始化历史
- 管理自定义历史
- 提供历史查询功能

协议：AGPL-3.0
作者：kiwifruit
"""

import json
import os
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Optional


class HistoryManager:
    """历史记录管理器"""
    
    INIT_HISTORY_FILE = "./agi_memory/init_history.json"
    CUSTOM_HISTORY_FILE = "./agi_memory/custom_history.json"
    
    @staticmethod
    def _load_history(file_path: str) -> dict:
        """加载历史记录"""
        if not os.path.exists(file_path):
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载历史记录失败: {e}", file=sys.stderr)
            return {}
    
    @staticmethod
    def _save_history(file_path: str, history: dict) -> bool:
        """保存历史记录"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存历史记录失败: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def record_init(nickname: str, traits: List[str], source: str = "init_command") -> bool:
        """
        记录初始化历史
        
        参数：
            nickname: 用户昵称
            traits: 核心特质列表
            source: 来源（init_command 或 auto）
        
        返回：
            True 表示成功
        """
        try:
            history = HistoryManager._load_history(HistoryManager.INIT_HISTORY_FILE)
            
            # 初始化结构
            if 'init_records' not in history:
                history['init_records'] = []
            
            # 创建记录
            record = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'default',
                'source': source,
                'user_nickname': nickname,
                'core_traits': traits,
                'status': 'success'
            }
            
            # 添加记录
            history['init_records'].append(record)
            history['initialized'] = True
            history['init_count'] = len(history['init_records'])
            history['last_init_time'] = datetime.now(timezone.utc).isoformat()
            
            # 保存
            return HistoryManager._save_history(HistoryManager.INIT_HISTORY_FILE, history)
        except Exception as e:
            print(f"记录初始化历史失败: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def record_custom(answers: List[str], nickname: str, traits: List[str]) -> bool:
        """
        记录自定义历史
        
        参数：
            answers: 7个答案
            nickname: 用户昵称
            traits: 核心特质列表
        
        返回：
            True 表示成功
        """
        try:
            history = HistoryManager._load_history(HistoryManager.CUSTOM_HISTORY_FILE)
            
            # 初始化结构
            if 'custom_records' not in history:
                history['custom_records'] = []
            
            # 创建记录
            record = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'type': 'custom',
                'source': 'root_command',
                'answers': answers,
                'user_nickname': nickname,
                'core_traits': traits,
                'status': 'success'
            }
            
            # 添加记录
            history['custom_records'].append(record)
            history['custom_count'] = len(history['custom_records'])
            history['last_custom_time'] = datetime.now(timezone.utc).isoformat()
            
            # 保存
            return HistoryManager._save_history(HistoryManager.CUSTOM_HISTORY_FILE, history)
        except Exception as e:
            print(f"记录自定义历史失败: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def check_first_interaction() -> dict:
        """
        检查是否为首次交互
        
        返回：
            {
                'is_first': bool,
                'init_count': int,
                'last_init_time': str or None
            }
        """
        try:
            history = HistoryManager._load_history(HistoryManager.INIT_HISTORY_FILE)
            
            is_first = not history.get('initialized', False)
            init_count = history.get('init_count', 0)
            last_init_time = history.get('last_init_time', None)
            
            return {
                'is_first': is_first,
                'init_count': init_count,
                'last_init_time': last_init_time
            }
        except Exception as e:
            print(f"检查首次交互失败: {e}", file=sys.stderr)
            return {
                'is_first': True,
                'init_count': 0,
                'last_init_time': None
            }
    
    @staticmethod
    def get_init_history(limit: int = 10) -> List[dict]:
        """获取初始化历史"""
        try:
            history = HistoryManager._load_history(HistoryManager.INIT_HISTORY_FILE)
            records = history.get('init_records', [])
            return records[-limit:]
        except Exception as e:
            print(f"获取初始化历史失败: {e}", file=sys.stderr)
            return []
    
    @staticmethod
    def get_custom_history(limit: int = 10) -> List[dict]:
        """获取自定义历史"""
        try:
            history = HistoryManager._load_history(HistoryManager.CUSTOM_HISTORY_FILE)
            records = history.get('custom_records', [])
            return records[-limit:]
        except Exception as e:
            print(f"获取自定义历史失败: {e}", file=sys.stderr)
            return []


def main():
    """命令行入口"""
    import sys
    
    parser = argparse.ArgumentParser(description="AGI History Manager")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # check-first 命令
    subparsers.add_parser("check-first", help="Check if first interaction")
    
    # get-init-history 命令
    init_parser = subparsers.add_parser("get-init-history", help="Get initialization history")
    init_parser.add_argument("--limit", type=int, default=10, help="Limit number of records")
    
    # get-custom-history 命令
    custom_parser = subparsers.add_parser("get-custom-history", help="Get customization history")
    custom_parser.add_argument("--limit", type=int, default=10, help="Limit number of records")
    
    args = parser.parse_args()
    
    if args.command == "check-first":
        result = HistoryManager.check_first_interaction()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.command == "get-init-history":
        records = HistoryManager.get_init_history(args.limit)
        print(json.dumps(records, ensure_ascii=False, indent=2))
    
    elif args.command == "get-custom-history":
        records = HistoryManager.get_custom_history(args.limit)
        print(json.dumps(records, ensure_ascii=False, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
