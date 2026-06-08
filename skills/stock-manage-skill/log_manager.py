"""
日志管理模块
提供日志清理和管理功能
"""

import os
import logging
from datetime import datetime, timedelta
from config import LOG_DIR

# 配置日志
log_file = os.path.join(LOG_DIR, f"log_manager_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LogManager:
    """日志管理器"""

    def __init__(self):
        """初始化"""
        self.log_dir = LOG_DIR

    def list_log_files(self):
        """
        列出所有日志文件

        :return: 日志文件列表
        """
        try:
            if not os.path.exists(self.log_dir):
                logger.warning(f"日志目录不存在: {self.log_dir}")
                return []

            log_files = []
            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    # 获取文件信息
                    stat = os.stat(filepath)
                    file_size = stat.st_size
                    file_mtime = datetime.fromtimestamp(stat.st_mtime)
                    
                    log_files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_size,
                        'size_mb': file_size / (1024 * 1024),
                        'mtime': file_mtime
                    })
            
            # 按修改时间排序（最新的在前）
            log_files.sort(key=lambda x: x['mtime'], reverse=True)
            
            return log_files
        except Exception as e:
            logger.error(f"列出日志文件失败: {e}")
            return []

    def delete_log_file(self, filename):
        """
        删除指定的日志文件

        :param filename: 日志文件名
        :return: 是否成功
        """
        try:
            filepath = os.path.join(self.log_dir, filename)
            
            if not os.path.exists(filepath):
                logger.warning(f"日志文件不存在: {filepath}")
                return False
            
            os.remove(filepath)
            logger.info(f"成功删除日志文件: {filename}")
            return True
        except Exception as e:
            logger.error(f"删除日志文件失败: {e}")
            return False

    def delete_old_logs(self, days=30):
        """
        删除指定天数之前的旧日志

        :param days: 天数
        :return: 删除的文件数量
        """
        try:
            if not os.path.exists(self.log_dir):
                logger.warning(f"日志目录不存在: {self.log_dir}")
                return 0

            cutoff_date = datetime.now() - timedelta(days=days)
            deleted_count = 0

            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_mtime < cutoff_date:
                        os.remove(filepath)
                        logger.info(f"删除旧日志: {filename} (修改时间: {file_mtime})")
                        deleted_count += 1

            logger.info(f"共删除 {deleted_count} 个旧日志文件")
            return deleted_count
        except Exception as e:
            logger.error(f"删除旧日志失败: {e}")
            return 0

    def get_log_size(self):
        """
        获取日志目录总大小

        :return: 总大小（字节）
        """
        try:
            if not os.path.exists(self.log_dir):
                return 0

            total_size = 0
            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)

            return total_size
        except Exception as e:
            logger.error(f"获取日志大小失败: {e}")
            return 0

    def clear_all_logs(self):
        """
        清空所有日志文件

        :return: 删除的文件数量
        """
        try:
            if not os.path.exists(self.log_dir):
                logger.warning(f"日志目录不存在: {self.log_dir}")
                return 0

            deleted_count = 0
            for filename in os.listdir(self.log_dir):
                filepath = os.path.join(self.log_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
                    logger.info(f"删除日志文件: {filename}")
                    deleted_count += 1

            logger.info(f"共删除 {deleted_count} 个日志文件")
            return deleted_count
        except Exception as e:
            logger.error(f"清空日志失败: {e}")
            return 0

    def format_size(self, size_bytes):
        """
        格式化文件大小

        :param size_bytes: 字节数
        :return: 格式化后的字符串
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"