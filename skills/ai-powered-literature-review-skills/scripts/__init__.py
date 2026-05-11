#!/usr/bin/env python3
"""
Literature Survey Skill - 工具脚本

提供基础的文献处理功能：
- models: 数据模型定义
- deduplicate_papers: 文献去重
- citation_formatter: 引用格式化
"""

from .models import Paper, Author, Venue
from .deduplicate_papers import deduplicate_papers, calculate_similarity
from .citation_formatter import format_citation_gb7714

__all__ = [
    'Paper',
    'Author', 
    'Venue',
    'deduplicate_papers',
    'calculate_similarity',
    'format_citation_gb7714'
]
