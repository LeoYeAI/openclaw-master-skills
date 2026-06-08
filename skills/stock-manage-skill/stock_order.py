"""
股票订单管理模块
管理股票的买入时间、价格以及股票类型（美港股等）信息
支持订单历史备份
"""

import os
import json
import logging
import shutil
from datetime import datetime
from config import DATA_DIR

# 配置日志
log_file = os.path.join(DATA_DIR, "logs", f"stock_order_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StockOrderManager:
    """股票订单管理器（支持历史备份）"""

    def __init__(self):
        """初始化"""
        self.data_dir = DATA_DIR
        self.order_dir = os.path.join(self.data_dir, "orders")
        self.order_file = os.path.join(self.order_dir, "orders.json")
        self._ensure_order_file_exists()

    def _ensure_order_file_exists(self):
        """确保订单文件存在"""
        os.makedirs(self.order_dir, exist_ok=True)
        if not os.path.exists(self.order_file):
            with open(self.order_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _backup_orders(self):
        """
        备份当前订单文件

        :return: 备份文件路径
        """
        try:
            if not os.path.exists(self.order_file):
                return None
            
            # 生成备份文件名：orders.json_YYYYMMDDHHMMSS
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            backup_filename = f"orders.json_{timestamp}"
            backup_filepath = os.path.join(self.order_dir, backup_filename)
            
            # 复制文件
            shutil.copy2(self.order_file, backup_filepath)
            
            logger.info(f"备份订单文件: {backup_filename}")
            
            # 清理多余的备份，只保留最近的10个
            self._cleanup_excess_backups(max_backups=10)
            
            return backup_filepath
        except Exception as e:
            logger.error(f"备份订单文件失败: {e}")
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
            for filename in os.listdir(self.order_dir):
                if filename.startswith('orders.json_') and filename != 'orders.json':
                    filepath = os.path.join(self.order_dir, filename)
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

            for filename in os.listdir(self.order_dir):
                if filename.startswith('orders.json_') and filename != 'orders.json':
                    filepath = os.path.join(self.order_dir, filename)
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

    def add_order(self, stock_code, stock_name, buy_time, buy_price, stock_type="A股", platform=None, quantity=None):
        """
        添加股票订单

        :param stock_code: 股票代码
        :param stock_name: 股票名称
        :param buy_time: 买入时间（YYYY-MM-DD HH:MM:SS）
        :param buy_price: 买入价格
        :param stock_type: 股票类型（A股、美股、港股等）
        :param platform: 股票交易平台（富途、平安等，可选）
        :param quantity: 购买数量（股数，可选）
        :return: 订单ID
        """
        try:
            # 读取现有订单
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            # 生成订单ID
            order_id = f"ORDER_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(orders) + 1}"

            # 创建新订单
            new_order = {
                "order_id": order_id,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "buy_time": buy_time,
                "buy_price": buy_price,
                "stock_type": stock_type,
                "platform": platform,
                "quantity": quantity,
                "status": "持有",
                "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # 添加到订单列表
            orders.append(new_order)

            # 备份当前订单文件
            self._backup_orders()

            # 保存订单
            with open(self.order_file, 'w', encoding='utf-8') as f:
                json.dump(orders, f, ensure_ascii=False, indent=2)

            logger.info(f"成功添加订单: {order_id} - {stock_name}({stock_code})")
            return order_id

        except Exception as e:
            logger.error(f"添加订单失败: {e}")
            raise

    def get_all_orders(self):
        """
        获取所有订单

        :return: 订单列表
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)
            return orders
        except Exception as e:
            logger.error(f"获取订单失败: {e}")
            return []

    def get_order_by_id(self, order_id):
        """
        根据订单ID获取订单

        :param order_id: 订单ID
        :return: 订单信息
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            for order in orders:
                if order["order_id"] == order_id:
                    return order
            return None
        except Exception as e:
            logger.error(f"获取订单失败: {e}")
            return None

    def update_order_status(self, order_id, status):
        """
        更新订单状态

        :param order_id: 订单ID
        :param status: 新状态（持有、已卖出、已止损等）
        :return: 是否成功
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            updated = False
            updated_order = None
            for order in orders:
                if order["order_id"] == order_id:
                    order["status"] = status
                    order["update_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    updated = True
                    updated_order = order.copy()
                    break

            if updated:
                # 备份当前订单文件
                self._backup_orders()

                with open(self.order_file, 'w', encoding='utf-8') as f:
                    json.dump(orders, f, ensure_ascii=False, indent=2)
                
                logger.info(f"成功更新订单状态: {order_id} - {status}")
                return True
            else:
                logger.warning(f"未找到订单: {order_id}")
                return False

        except Exception as e:
            logger.error(f"更新订单状态失败: {e}")
            return False

    def update_order(self, order_id, **kwargs):
        """
        更新订单信息（支持更新多个字段）

        :param order_id: 订单ID
        :param kwargs: 要更新的字段（如 stock_name, buy_time, buy_price, stock_type, platform, status等）
        :return: 是否成功
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            updated = False
            updated_order = None
            for order in orders:
                if order["order_id"] == order_id:
                    # 更新指定字段
                    for key, value in kwargs.items():
                        if key in order and value is not None:
                            order[key] = value
                    order["update_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    updated = True
                    updated_order = order.copy()
                    break

            if updated:
                # 备份当前订单文件
                self._backup_orders()

                with open(self.order_file, 'w', encoding='utf-8') as f:
                    json.dump(orders, f, ensure_ascii=False, indent=2)
                
                logger.info(f"成功更新订单: {order_id}")
                return True
            else:
                logger.warning(f"未找到订单: {order_id}")
                return False

        except Exception as e:
            logger.error(f"更新订单失败: {e}")
            return False

    def delete_order(self, order_id):
        """
        删除订单

        :param order_id: 订单ID
        :return: 是否成功
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            deleted_order = None
            new_orders = []
            for order in orders:
                if order["order_id"] == order_id:
                    deleted_order = order.copy()
                else:
                    new_orders.append(order)

            if deleted_order:
                # 备份当前订单文件
                self._backup_orders()

                # 删除订单
                with open(self.order_file, 'w', encoding='utf-8') as f:
                    json.dump(new_orders, f, ensure_ascii=False, indent=2)
                
                logger.info(f"成功删除订单: {order_id}")
                return True
            else:
                logger.warning(f"未找到订单: {order_id}")
                return False

        except Exception as e:
            logger.error(f"删除订单失败: {e}")
            return False

    def get_orders_by_stock_type(self, stock_type):
        """
        根据股票类型获取订单

        :param stock_type: 股票类型
        :return: 订单列表
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            filtered_orders = [order for order in orders if order["stock_type"] == stock_type]
            return filtered_orders
        except Exception as e:
            logger.error(f"获取订单失败: {e}")
            return []

    def get_orders_by_status(self, status):
        """
        根据状态获取订单

        :param status: 订单状态
        :return: 订单列表
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            filtered_orders = [order for order in orders if order["status"] == status]
            return filtered_orders
        except Exception as e:
            logger.error(f"获取订单失败: {e}")
            return []

    def get_orders_by_platform(self, platform):
        """
        根据交易平台获取订单

        :param platform: 交易平台
        :return: 订单列表
        """
        try:
            with open(self.order_file, 'r', encoding='utf-8') as f:
                orders = json.load(f)

            filtered_orders = [order for order in orders if order.get("platform") == platform]
            return filtered_orders
        except Exception as e:
            logger.error(f"获取订单失败: {e}")
            return []