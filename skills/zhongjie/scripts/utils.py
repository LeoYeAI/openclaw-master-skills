#!/usr/bin/env python3
"""
zhongjie skill 公共工具模块

管理运行时数据目录结构（遵循 .skills-data 规范）：

    <project_root>/.skills-data/zhongjie/
        .env            — 环境变量配置
        data/           — 持久化数据（搜索结果等）
        cache/          — 可安全删除的缓存
        configs/        — 额外配置文件
        logs/           — 日志文件
        tmp/            — 临时文件
        bin/            — 可执行文件
        venv/           — Python 虚拟环境

技能源码（SKILL.md、scripts/、references/）保持不可变。
"""

import os

SKILL_NAME = "zhongjie"

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())

SKILL_DATA_DIR = os.path.join(PROJECT_ROOT, ".skills-data", SKILL_NAME)

DATA_DIR = os.path.join(SKILL_DATA_DIR, "data")
SEARCH_RESULTS_DIR = os.path.join(DATA_DIR, "search-results")
CACHE_DIR = os.path.join(SKILL_DATA_DIR, "cache")
CONFIGS_DIR = os.path.join(SKILL_DATA_DIR, "configs")
LOGS_DIR = os.path.join(SKILL_DATA_DIR, "logs")
TMP_DIR = os.path.join(SKILL_DATA_DIR, "tmp")

ENV_FILE = os.path.join(SKILL_DATA_DIR, ".env")


def ensure_dirs():
    """确保运行时数据目录结构存在。"""
    for d in (SKILL_DATA_DIR, DATA_DIR, SEARCH_RESULTS_DIR,
              CACHE_DIR, CONFIGS_DIR, LOGS_DIR, TMP_DIR):
        os.makedirs(d, exist_ok=True)
