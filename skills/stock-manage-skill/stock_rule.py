"""
股票交易规则管理模块
管理股票的买入规则和卖出规则
支持规则历史备份
"""

import os
import json
import logging
import shutil
from datetime import datetime
from config import DATA_DIR

# 配置日志
log_file = os.path.join(DATA_DIR, "logs", f"stock_rule_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StockRuleManager:
    """股票交易规则管理器（支持历史备份）"""

    def __init__(self):
        """初始化"""
        self.data_dir = DATA_DIR
        self.rule_dir = os.path.join(self.data_dir, "rules")
        self.rule_file = os.path.join(self.rule_dir, "rules.json")
        self._ensure_rule_file_exists()

    def _ensure_rule_file_exists(self):
        """确保规则文件存在"""
        os.makedirs(self.rule_dir, exist_ok=True)
        if not os.path.exists(self.rule_file):
            with open(self.rule_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _backup_rules(self):
        """
        备份当前规则文件

        :return: 备份文件路径
        """
        try:
            if not os.path.exists(self.rule_file):
                return None
            
            # 生成备份文件名：rules.json_YYYYMMDDHHMMSS
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            backup_filename = f"rules.json_{timestamp}"
            backup_filepath = os.path.join(self.rule_dir, backup_filename)
            
            # 复制文件
            shutil.copy2(self.rule_file, backup_filepath)
            
            logger.info(f"备份规则文件: {backup_filename}")
            
            # 清理多余的备份，只保留最近的10个
            self._cleanup_excess_backups(max_backups=10)
            
            return backup_filepath
        except Exception as e:
            logger.error(f"备份规则文件失败: {e}")
            return None

    def _cleanup_excess_backups(self, max_backups=10):
        """
        清理多余的备份，只保留最近的指定数量

        :param max_backups: 保留的最大备份数量
        :return: 清理的备份数量
        """
        try:
            # 获取所有备份文件
            backups = []
            for filename in os.listdir(self.rule_dir):
                if filename.startswith('rules.json_') and filename != 'rules.json':
                    filepath = os.path.join(self.rule_dir, filename)
                    file_mtime = os.path.getmtime(filepath)
                    backups.append({
                        'filename': filename,
                        'filepath': filepath,
                        'mtime': file_mtime
                    })
            
            # 按修改时间排序（最新的在前）
            backups.sort(key=lambda x: x['mtime'], reverse=True)
            
            # 删除多余的备份
            deleted_count = 0
            for backup in backups[max_backups:]:
                os.remove(backup['filepath'])
                logger.info(f"清理多余备份: {backup['filename']}")
                deleted_count += 1
            
            if deleted_count > 0:
                logger.info(f"共清理 {deleted_count} 个多余备份（保留最近{max_backups}个）")
            
            return deleted_count
        except Exception as e:
            logger.error(f"清理多余备份失败: {e}")
            return 0

    def cleanup_old_backups(self, days=90):
        """
        清理指定天数之前的旧备份

        :param days: 保留的天数
        :return: 清理的备份数量
        """
        try:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0

            for filename in os.listdir(self.rule_dir):
                if filename.startswith('rules.json_') and filename != 'rules.json':
                    filepath = os.path.join(self.rule_dir, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_mtime < cutoff_date:
                        os.remove(filepath)
                        logger.info(f"清理旧备份: {filename}")
                        deleted_count += 1

            if deleted_count > 0:
                logger.info(f"共清理 {deleted_count} 个旧备份（{days}天前）")

            return deleted_count
        except Exception as e:
            logger.error(f"清理旧备份失败: {e}")
            return 0

    def add_rule(self, rule_type, rule_name, rule_description, conditions, actions, stock_type=None, stock_code=None):
        """
        添加交易规则

        :param rule_type: 规则类型（买入规则、卖出规则）
        :param rule_name: 规则名称
        :param rule_description: 规则描述
        :param conditions: 触发条件（字典列表）
        :param actions: 执行动作（字典列表）
        :param stock_type: 股票类型（可选，用于特定股票类型）
        :param stock_code: 股票代码（可选，用于特定股票）
        :return: 规则ID
        """
        try:
            # 读取现有规则
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            # 生成规则ID
            rule_id = f"RULE_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(rules) + 1}"

            # 创建新规则
            new_rule = {
                "rule_id": rule_id,
                "rule_type": rule_type,
                "rule_name": rule_name,
                "rule_description": rule_description,
                "conditions": conditions,
                "actions": actions,
                "stock_type": stock_type,
                "stock_code": stock_code,
                "enabled": True,
                "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 添加到规则列表
            rules.append(new_rule)

            # 备份当前规则文件
            self._backup_rules()

            # 保存规则
            with open(self.rule_file, 'w', encoding='utf-8') as f:
                json.dump(rules, f, ensure_ascii=False, indent=2)

            logger.info(f"成功添加规则: {rule_id} - {rule_name}({rule_type})")
            return rule_id

        except Exception as e:
            logger.error(f"添加规则失败: {e}")
            raise

    def get_all_rules(self):
        """
        获取所有规则

        :return: 规则列表
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            return rules
        except Exception as e:
            logger.error(f"获取规则失败: {e}")
            return []

    def get_rule_by_id(self, rule_id):
        """
        根据规则ID获取规则

        :param rule_id: 规则ID
        :return: 规则信息
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            for rule in rules:
                if rule["rule_id"] == rule_id:
                    return rule
            return None
        except Exception as e:
            logger.error(f"获取规则失败: {e}")
            return None

    def update_rule(self, rule_id, **kwargs):
        """
        更新规则信息（支持更新多个字段）

        :param rule_id: 规则ID
        :param kwargs: 要更新的字段（如 rule_name, rule_description, conditions, actions, enabled等）
        :return: 是否成功
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            updated = False
            updated_rule = None
            for rule in rules:
                if rule["rule_id"] == rule_id:
                    # 更新指定字段
                    for key, value in kwargs.items():
                        if key in rule and value is not None:
                            rule[key] = value
                    rule["update_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    updated = True
                    updated_rule = rule.copy()
                    break

            if updated:
                # 备份当前规则文件
                self._backup_rules()

                with open(self.rule_file, 'w', encoding='utf-8') as f:
                    json.dump(rules, f, ensure_ascii=False, indent=2)
                
                logger.info(f"成功更新规则: {rule_id}")
                return True
            else:
                logger.warning(f"未找到规则: {rule_id}")
                return False

        except Exception as e:
            logger.error(f"更新规则失败: {e}")
            return False

    def delete_rule(self, rule_id):
        """
        删除规则

        :param rule_id: 规则ID
        :return: 是否成功
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            deleted_rule = None
            new_rules = []
            for rule in rules:
                if rule["rule_id"] == rule_id:
                    deleted_rule = rule.copy()
                else:
                    new_rules.append(rule)

            if deleted_rule:
                # 备份当前规则文件
                self._backup_rules()

                # 删除规则
                with open(self.rule_file, 'w', encoding='utf-8') as f:
                    json.dump(new_rules, f, ensure_ascii=False, indent=2)
                
                logger.info(f"成功删除规则: {rule_id}")
                return True
            else:
                logger.warning(f"未找到规则: {rule_id}")
                return False

        except Exception as e:
            logger.error(f"删除规则失败: {e}")
            return False

    def get_rules_by_type(self, rule_type):
        """
        根据规则类型获取规则

        :param rule_type: 规则类型（买入规则、卖出规则）
        :return: 规则列表
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            filtered_rules = [rule for rule in rules if rule["rule_type"] == rule_type]
            return filtered_rules
        except Exception as e:
            logger.error(f"获取规则失败: {e}")
            return []

    def get_rules_by_stock_type(self, stock_type):
        """
        根据股票类型获取规则

        :param stock_type: 股票类型
        :return: 规则列表
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            filtered_rules = [rule for rule in rules if rule.get("stock_type") == stock_type]
            return filtered_rules
        except Exception as e:
            logger.error(f"获取规则失败: {e}")
            return []

    def get_rules_by_stock_code(self, stock_code):
        """
        根据股票代码获取规则

        :param stock_code: 股票代码
        :return: 规则列表
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            filtered_rules = [rule for rule in rules if rule.get("stock_code") == stock_code]
            return filtered_rules
        except Exception as e:
            logger.error(f"获取规则失败: {e}")
            return []

    def get_enabled_rules(self):
        """
        获取所有启用的规则

        :return: 规则列表
        """
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)

            enabled_rules = [rule for rule in rules if rule.get("enabled", True)]
            return enabled_rules
        except Exception as e:
            logger.error(f"获取规则失败: {e}")
            return []

    def toggle_rule(self, rule_id):
        """
        切换规则的启用/禁用状态

        :param rule_id: 规则ID
        :return: 是否成功
        """
        try:
            rule = self.get_rule_by_id(rule_id)
            if rule:
                new_status = not rule.get("enabled", True)
                success = self.update_rule(rule_id, enabled=new_status)
                if success:
                    status_str = "启用" if new_status else "禁用"
                    logger.info(f"成功{status_str}规则: {rule_id}")
                return success
            return False
        except Exception as e:
            logger.error(f"切换规则状态失败: {e}")
            return False