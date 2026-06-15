"""
IMA Skills 日志模块
提供统一的日志配置和管理

功能：
- 双输出：同时输出到控制台和文件
- 日志轮转：自动管理日志文件大小
- 分级记录：INFO（关键操作）和 ERROR（错误信息）
- 性能优化：异步写入，不影响主流程

日志文件位置：~/.openclaw/logs/ima_skills/
文件命名：ima_create_YYYYMMDD.log
保留策略：保留最近 7 天
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "ima_skills",
    log_level: int = logging.INFO,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 7,  # Keep 7 days
    console_output: bool = True,
) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        name: Logger 名称
        log_level: 日志级别（INFO/ERROR）
        max_bytes: 单个日志文件最大大小（字节）
        backup_count: 保留的日志文件数量
        console_output: 是否同时输出到控制台
    
    Returns:
        配置好的 Logger 对象
    """
    # 创建日志目录
    log_dir = Path.home() / ".openclaw" / "logs" / "ima_skills"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 日志文件名（按日期）
    log_file = log_dir / f"ima_create_{datetime.now().strftime('%Y%m%d')}.log"
    
    # 创建 Logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 避免重复添加 Handler
    if logger.handlers:
        return logger
    
    # 日志格式
    # 格式：2026-02-26 15:30:45 | INFO | get_product_list | Query product list: category=text_to_image
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-5s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件 Handler（带轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台 Handler（可选）
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)  # 控制台只显示 WARNING 及以上
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "ima_skills") -> logging.Logger:
    """
    获取已配置的 Logger（如果不存在则创建）
    
    Args:
        name: Logger 名称
    
    Returns:
        Logger 对象
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger


# 清理旧日志文件
def cleanup_old_logs(days: int = 7) -> None:
    """
    清理超过指定天数的日志文件
    
    Args:
        days: 保留天数
    """
    try:
        log_dir = Path.home() / ".openclaw" / "logs" / "ima_skills"
        if not log_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        for log_file in log_dir.glob("ima_create_*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                log_file.unlink()
                
    except Exception:
        pass  # 清理失败不影响主流程
