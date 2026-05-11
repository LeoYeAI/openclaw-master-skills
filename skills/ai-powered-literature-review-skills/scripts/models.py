#!/usr/bin/env python3
"""
统一数据模型定义

提供标准化的Paper、Author等数据模型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Author:
    """作者信息"""
    name: str = ""  # 完整姓名
    affiliation: str = ""  # 单位
    
    def format_for_citation(self) -> str:
        """格式化为引用格式"""
        return self.name


@dataclass
class Paper:
    """
    统一文献数据模型
    """
    # 标识
    id: str = ""  # 内部ID (E1, C1, etc.)
    doi: str = ""
    
    # 基本元数据
    title: str = ""
    authors: List[str] = field(default_factory=list)  # 简化为字符串列表
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    
    # 发表信息
    journal: str = ""  # 期刊/会议名称
    year: Optional[int] = None
    volume: str = ""
    issue: str = ""
    pages: str = ""
    
    # 类型和语言
    language: str = "en"  # zh, en
    
    # 来源
    source_db: str = ""  # cnki, wos, sciencedirect, pubmed
    source_url: str = ""
    
    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "doi": self.doi,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "journal": self.journal,
            "year": self.year,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "language": self.language,
            "source_db": self.source_db,
            "source_url": self.source_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Paper":
        """从字典创建"""
        return cls(
            id=data.get("id", ""),
            doi=data.get("doi", ""),
            title=data.get("title", ""),
            authors=data.get("authors", []),
            abstract=data.get("abstract", ""),
            keywords=data.get("keywords", []),
            journal=data.get("journal", ""),
            year=data.get("year"),
            volume=data.get("volume", ""),
            issue=data.get("issue", ""),
            pages=data.get("pages", ""),
            language=data.get("language", "en"),
            source_db=data.get("source_db", ""),
            source_url=data.get("source_url", "")
        )
    
    def get_first_author(self) -> str:
        """获取第一作者"""
        if self.authors:
            return self.authors[0]
        return "Unknown"
