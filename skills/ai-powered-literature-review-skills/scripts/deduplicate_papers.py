#!/usr/bin/env python3
"""
文献去重工具

功能：
- 基于DOI精确去重
- 基于标题相似度去重
- 保留信息更完整的版本
"""

from typing import List, Dict, Tuple
from difflib import SequenceMatcher


def calculate_similarity(str1: str, str2: str) -> float:
    """
    计算两个字符串的相似度
    
    Args:
        str1: 第一个字符串
        str2: 第二个字符串
    
    Returns:
        相似度（0.0 - 1.0）
    """
    if not str1 or not str2:
        return 0.0
    
    s1 = str1.lower().strip()
    s2 = str2.lower().strip()
    
    return SequenceMatcher(None, s1, s2).ratio()


def normalize_doi(doi: str) -> str:
    """标准化DOI"""
    if not doi:
        return ""
    
    doi = doi.replace("https://doi.org/", "")
    doi = doi.replace("http://doi.org/", "")
    doi = doi.replace("doi.org/", "")
    doi = doi.replace("DOI:", "")
    doi = doi.replace("doi:", "")
    
    return doi.strip().lower()


def calculate_paper_quality_score(paper: Dict) -> float:
    """
    计算文献质量分数（用于决定保留哪个重复版本）
    """
    score = 0.0
    
    # 有DOI加分
    if paper.get("doi"):
        score += 10
    
    # 有完整元数据加分
    if paper.get("abstract"):
        score += 5
    if paper.get("volume") and paper.get("issue"):
        score += 3
    if paper.get("pages"):
        score += 2
    
    return score


def deduplicate_papers(
    papers: List[Dict],
    title_similarity_threshold: float = 0.85
) -> Tuple[List[Dict], List[Dict]]:
    """
    文献去重主函数
    
    去重策略：
    1. DOI精确匹配
    2. 标题相似度匹配
    
    Args:
        papers: 文献列表
        title_similarity_threshold: 标题相似度阈值（默认0.85）
    
    Returns:
        (去重后的文献列表, 被移除的重复文献列表)
    """
    if not papers:
        return [], []
    
    unique_papers = []
    removed_papers = []
    seen_dois = set()
    
    for paper in papers:
        # 检查DOI
        doi = normalize_doi(paper.get("doi", ""))
        if doi:
            if doi in seen_dois:
                removed_papers.append(paper)
                continue
            seen_dois.add(doi)
            unique_papers.append(paper)
            continue
        
        # 没有DOI，检查标题相似度
        title = paper.get("title", "").lower()
        is_duplicate = False
        
        for existing in unique_papers:
            existing_title = existing.get("title", "").lower()
            similarity = calculate_similarity(title, existing_title)
            
            if similarity >= title_similarity_threshold:
                # 标题相似，比较质量
                if calculate_paper_quality_score(paper) > calculate_paper_quality_score(existing):
                    removed_papers.append(existing)
                    unique_papers.remove(existing)
                    unique_papers.append(paper)
                else:
                    removed_papers.append(paper)
                
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_papers.append(paper)
    
    return unique_papers, removed_papers


def print_deduplication_report(
    original_count: int,
    unique_papers: List[Dict],
    removed_papers: List[Dict]
):
    """打印去重报告"""
    print("=" * 60)
    print("文献去重报告")
    print("=" * 60)
    
    print(f"\n原始文献数量: {original_count}")
    print(f"去重后数量: {len(unique_papers)}")
    print(f"移除重复: {len(removed_papers)}")
    
    if original_count > 0:
        print(f"去重率: {len(removed_papers) / original_count * 100:.1f}%")


if __name__ == "__main__":
    # 测试示例
    test_papers = [
        {
            "id": "E1",
            "title": "Deep learning for image recognition",
            "authors": ["Y LeCun"],
            "year": 2015,
            "journal": "Nature",
            "doi": "10.1038/nature14539"
        },
        {
            "id": "E2",  # DOI重复的文献
            "title": "Deep learning",
            "authors": ["Y LeCun"],
            "year": 2015,
            "journal": "Nature",
            "doi": "10.1038/nature14539"
        },
        {
            "id": "E3",  # 标题相似的文献
            "title": "Deep learning for image recognition: A survey",
            "authors": ["Y LeCun"],
            "year": 2015,
            "journal": "Nature",
            "doi": ""
        },
        {
            "id": "E4",  # 完全不同的文献
            "title": "Attention is all you need",
            "authors": ["A Vaswani"],
            "year": 2017,
            "journal": "NIPS",
            "doi": "10.48550/arXiv.1706.03762"
        }
    ]
    
    unique, removed = deduplicate_papers(test_papers)
    print_deduplication_report(len(test_papers), unique, removed)
