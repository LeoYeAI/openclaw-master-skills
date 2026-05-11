#!/usr/bin/env python3
"""
引用格式化工具

支持 GB/T 7714-2015 格式
"""

from typing import Dict, List, Optional


def format_author_name(name: str, lang: str = "en") -> str:
    """
    格式化作者姓名
    
    Args:
        name: 作者姓名
        lang: 语言 (zh/en)
    
    Returns:
        格式化后的作者名
    """
    if not name:
        return ""
    
    if lang == "zh":
        # 中文：保持原样
        return name.strip()
    else:
        # 英文：姓, 名首字母
        parts = name.strip().split()
        if len(parts) >= 2:
            surname = parts[-1]
            initials = "".join([p[0] + "." for p in parts[:-1] if p])
            return f"{surname} {initials}"
        return name.strip()


def format_authors(authors: List[str], lang: str = "en") -> str:
    """
    格式化作者列表
    
    Args:
        authors: 作者列表
        lang: 语言
    
    Returns:
        格式化后的作者字符串
    """
    if not authors:
        return ""
    
    formatted = [format_author_name(a, lang) for a in authors if a]
    
    if lang == "zh":
        # 中文：用逗号分隔
        return ", ".join(formatted)
    else:
        # 英文：最后两个用 "and" 连接
        if len(formatted) == 1:
            return formatted[0]
        elif len(formatted) == 2:
            return " and ".join(formatted)
        else:
            return ", ".join(formatted[:-1]) + ", and " + formatted[-1]


def format_citation_gb7714(paper: Dict, index: str = "") -> str:
    """
    格式化为 GB/T 7714-2015 格式
    
    Args:
        paper: 文献字典
        index: 文献编号 (如 C1, E1)
    
    Returns:
        GB/T 7714-2015 格式的引文
    """
    lang = paper.get("language", "en")
    authors = paper.get("authors", [])
    title = paper.get("title", "")
    journal = paper.get("journal", "")
    year = paper.get("year", "")
    volume = paper.get("volume", "")
    issue = paper.get("issue", "")
    pages = paper.get("pages", "")
    doi = paper.get("doi", "")
    
    # 格式化作者
    author_str = format_authors(authors, lang)
    
    # 构建卷期页字符串
    vol_issue = ""
    if volume:
        vol_issue = volume
        if issue:
            vol_issue += f"({issue})"
        if pages:
            vol_issue += f": {pages}"
    elif pages:
        vol_issue = pages
    
    # 构建引文
    if lang == "zh":
        # 中文期刊格式
        citation = f"[{index}] {author_str}. {title}[J]. {journal}"
        if year:
            citation += f", {year}"
        if vol_issue:
            citation += f", {vol_issue}"
        if doi:
            citation += f". DOI:{doi}"
        citation += "."
    else:
        # 英文期刊格式
        citation = f"[{index}] {author_str}. {title}[J]. {journal}"
        if year:
            citation += f", {year}"
        if vol_issue:
            citation += f", {vol_issue}"
        if doi:
            citation += f". DOI:{doi}"
        citation += "."
    
    return citation


def format_citation_list(papers: List[Dict], prefix: str = "E") -> List[str]:
    """
    格式化文献列表
    
    Args:
        papers: 文献列表
        prefix: 编号前缀 (C/E)
    
    Returns:
        格式化后的引文列表
    """
    citations = []
    for i, paper in enumerate(papers, 1):
        index = f"{prefix}{i}"
        citation = format_citation_gb7714(paper, index)
        citations.append(citation)
    
    return citations


def generate_reference_md(papers_zh: List[Dict], papers_en: List[Dict]) -> str:
    """
    生成参考文献 Markdown 文档
    
    Args:
        papers_zh: 中文文献列表
        papers_en: 英文文献列表
    
    Returns:
        Markdown 格式的参考文献
    """
    lines = ["# 参考文献\n"]
    
    # 中文文献
    if papers_zh:
        lines.append("## 中文文献\n")
        for i, paper in enumerate(papers_zh, 1):
            citation = format_citation_gb7714(paper, f"C{i}")
            lines.append(f"{citation}\n")
        lines.append("")
    
    # 英文文献
    if papers_en:
        lines.append("## 英文文献\n")
        for i, paper in enumerate(papers_en, 1):
            citation = format_citation_gb7714(paper, f"E{i}")
            lines.append(f"{citation}\n")
        lines.append("")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # 测试示例
    test_papers = [
        {
            "id": "C1",
            "title": "基于深度学习的医学图像诊断研究",
            "authors": ["张三", "李四", "王五"],
            "journal": "计算机学报",
            "year": 2023,
            "volume": "46",
            "issue": "5",
            "pages": "1023-1035",
            "doi": "10.xxxx",
            "language": "zh"
        },
        {
            "id": "E1",
            "title": "Deep learning for medical image analysis",
            "authors": ["Smith J", "Johnson K", "Lee M"],
            "journal": "Nature Medicine",
            "year": 2022,
            "volume": "28",
            "issue": "8",
            "pages": "1500-1510",
            "doi": "10.1038/s41591-022-01900-0",
            "language": "en"
        }
    ]
    
    print("中文文献示例：")
    print(format_citation_gb7714(test_papers[0], "C1"))
    print()
    print("英文文献示例：")
    print(format_citation_gb7714(test_papers[1], "E1"))
