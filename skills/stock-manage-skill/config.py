"""
配置文件
"""

# 数据存储目录
DATA_DIR = "data"

# 创建必要的子目录
import os
os.makedirs(os.path.join(DATA_DIR, "orders"), exist_ok=True)

# 日志配置
LOG_DIR = os.path.join(DATA_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)