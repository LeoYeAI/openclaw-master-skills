#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BettaFish 数据采集工具
通过 WebSearch、WebFetch、Browser 等工具获取真实数据
**严禁使用模拟数据**
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class SocialMediaPost:
    """社交媒体帖子数据模型"""
    id: str
    platform: str
    nickname: str
    content: str
    sentiment: str
    likes: int
    comments: int
    shares: int
    timestamp: str
    url: str
    topic: str = ""
    engagement_score: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)


class DataCollector:
    """
    真实数据采集器

    **重要**: 本类所有方法必须通过 WebSearch/WebFetch/Browser 获取真实数据
    严禁生成或使用模拟数据
    """

    def __init__(self):
        self.platform_patterns = {
            'weibo': r'weibo\.com|微博',
            'xiaohongshu': r'xiaohongshu\.com|小红书',
            'douyin': r'douyin\.com|抖音',
            'bilibili': r'bilibili\.com|b23\.tv|B站',
            'zhihu': r'zhihu\.com|知乎',
            'tieba': r'tieba\.baidu\.com|贴吧'
        }

    def identify_platform(self, url: str) -> str:
        """根据 URL 识别平台"""
        url_lower = url.lower()
        for platform, pattern in self.platform_patterns.items():
            if re.search(pattern, url_lower):
                return platform
        return 'other'

    def parse_search_result(self, result: Dict) -> Optional[Dict]:
        """
        解析搜索结果为结构化数据

        Args:
            result: WebSearch 返回的搜索结果条目

        Returns:
            结构化数据字典
        """
        return {
            'title': result.get('title', ''),
            'snippet': result.get('snippet', result.get('content', '')),
            'url': result.get('url', result.get('link', '')),
            'source': result.get('source', 'unknown'),
            'date': result.get('date', datetime.now().strftime('%Y-%m-%d')),
            'platform': self.identify_platform(result.get('url', ''))
        }

    def extract_content_from_webfetch(self, webfetch_result: Dict) -> Dict:
        """
        从 WebFetch 结果中提取内容

        Args:
            webfetch_result: WebFetch 返回的页面内容

        Returns:
            提取的内容结构
        """
        content = webfetch_result.get('content', '')

        # 提取文本内容（移除 HTML 标签）
        text_content = re.sub(r'<[^>]+>', '', content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()

        return {
            'title': webfetch_result.get('title', ''),
            'content': text_content[:5000],  # 限制长度
            'url': webfetch_result.get('url', ''),
            'timestamp': datetime.now().isoformat()
        }

    def aggregate_platform_stats(self, data: List[Dict]) -> Dict:
        """
        聚合平台统计数据

        Args:
            data: 社交媒体帖子列表

        Returns:
            各平台统计信息
        """
        platform_stats = defaultdict(lambda: {
            'count': 0,
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'engagement_score': 0,
            'sentiments': {'positive': 0, 'negative': 0, 'neutral': 0}
        })

        for item in data:
            platform = item.get('platform', 'unknown')
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['likes'] += item.get('likes', 0)
            platform_stats[platform]['comments'] += item.get('comments', 0)
            platform_stats[platform]['shares'] += item.get('shares', 0)
            platform_stats[platform]['engagement_score'] += item.get('engagement_score', 0)
            platform_stats[platform]['sentiments'][item.get('sentiment', 'neutral')] += 1

        # 计算占比和平均值
        total = len(data)
        for platform in platform_stats:
            stats = platform_stats[platform]
            stats['percentage'] = round(stats['count'] / total * 100, 2) if total > 0 else 0
            stats['avg_likes'] = round(stats['likes'] / stats['count'], 2) if stats['count'] > 0 else 0
            stats['avg_comments'] = round(stats['comments'] / stats['count'], 2) if stats['count'] > 0 else 0
            stats['avg_shares'] = round(stats['shares'] / stats['count'], 2) if stats['count'] > 0 else 0
            stats['avg_engagement'] = round(stats['engagement_score'] / stats['count'], 2) if stats['count'] > 0 else 0

        return dict(platform_stats)

    def calculate_heat_index(self, texts: List[str], timestamps: Optional[List] = None) -> Dict:
        """
        计算热度指数

        Args:
            texts: 文本内容列表
            timestamps: 时间戳列表

        Returns:
            热度指标
        """
        total = len(texts)

        # 计算平均文本长度
        avg_length = sum(len(t) for t in texts) / total if total > 0 else 0

        # 计算互动性指标（基于标点符号密度）
        interaction_score = sum(
            t.count('!') + t.count('！') + t.count('?') + t.count('？') +
            t.count('【') + t.count('#')
            for t in texts
        ) / total if total > 0 else 0

        # 热度指数（综合指标）
        heat_score = min(100, (
            total * 0.3 +
            avg_length * 0.05 +
            interaction_score * 5
        ))

        # 热度等级
        if heat_score >= 80:
            heat_level = '极高'
        elif heat_score >= 60:
            heat_level = '高'
        elif heat_score >= 40:
            heat_level = '中等'
        elif heat_score >= 20:
            heat_level = '低'
        else:
            heat_level = '极低'

        return {
            'heat_score': round(heat_score, 2),
            'heat_level': heat_level,
            'total_mentions': total,
            'avg_text_length': round(avg_length, 2),
            'interaction_score': round(interaction_score, 2)
        }

    def extract_mentions(self, text: str) -> List[str]:
        """提取@提及"""
        mentions = re.findall(r'@(\w+)', text)
        return mentions

    def extract_hashtags(self, text: str) -> List[str]:
        """提取话题标签"""
        hashtags = re.findall(r'#([^#]+)#', text)
        return hashtags

    def classify_content_type(self, content: str) -> str:
        """分类内容类型"""
        content = content.lower()

        if any(kw in content for kw in ['视频', 'vlog', '短片', '直播', 'video']):
            return 'video'
        elif any(kw in content for kw in ['图', '照片', '图片', 'photo', 'image']):
            return 'image'
        elif any(kw in content for kw in ['文章', '长文', 'blog', 'article']):
            return 'article'
        elif any(kw in content for kw in ['问', '？', '求助', 'question']):
            return 'question'
        else:
            return 'text'


def collect_from_search_results(search_results: List[Dict]) -> List[Dict]:
    """
    从 WebSearch 结果中收集结构化数据

    **必须由智能体调用，传入真实的 WebSearch 结果**

    Args:
        search_results: WebSearch 返回的搜索结果列表

    Returns:
        结构化数据列表
    """
    collector = DataCollector()
    structured_data = []

    for result in search_results:
        parsed = collector.parse_search_result(result)
        if parsed:
            structured_data.append(parsed)

    return structured_data


def extract_video_urls(search_results: List[Dict]) -> List[Dict]:
    """
    从搜索结果中提取视频链接

    Args:
        search_results: WebSearch 结果

    Returns:
        视频链接列表，包含平台信息
    """
    video_platforms = ['douyin', 'bilibili', 'tiktok', 'youtube']
    video_urls = []

    for result in search_results:
        url = result.get('url', '')
        platform = DataCollector().identify_platform(url)

        if platform in video_platforms:
            video_urls.append({
                'url': url,
                'platform': platform,
                'title': result.get('title', ''),
                'snippet': result.get('snippet', '')
            })

    return video_urls


if __name__ == '__main__':
    print("BettaFish Data Collector")
    print("本工具用于处理 WebSearch/WebFetch 获取的真实数据")
    print("严禁使用模拟数据")
    print("\n请通过智能体的 WebSearch、WebFetch、Browser 工具获取真实数据后，")
    print("使用本工具进行数据处理和聚合。")
