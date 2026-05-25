#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BettaFish 情感分析工具
基于 BettaFish InsightEngine 的情感分析模块
支持多维度情感分析：极性、细分情绪、强度
"""

import re
import json
from typing import List, Dict, Tuple, Optional, Union
from collections import Counter, defaultdict
from dataclasses import dataclass


@dataclass
class SentimentResult:
    """情感分析结果"""
    text: str
    label: str  # positive / negative / neutral
    confidence: float
    positive_score: float
    negative_score: float
    neutral_score: float
    fine_emotions: List[Dict] = None  # 细分情绪
    aspects: Dict[str, str] = None  # 方面级情感

    def __post_init__(self):
        if self.fine_emotions is None:
            self.fine_emotions = []
        if self.aspects is None:
            self.aspects = {}


class SentimentAnalyzer:
    """情感分析器 - 基于规则和词典的轻量级实现"""

    def __init__(self):
        self._load_dictionaries()

    def _load_dictionaries(self):
        """加载情感词典"""
        # 正面词汇词典
        self.positive_words = {
            '好', '棒', '优秀', '喜欢', '爱', '赞', '完美', '推荐', '满意', '不错',
            '开心', '快乐', '幸福', '成功', '漂亮', '厉害', '强', '牛', '给力',
            '值得', '惊喜', '超预期', '优质', '专业', '贴心', '靠谱', '真香',
            'good', 'great', 'excellent', 'amazing', 'love', 'best', 'perfect',
            'awesome', 'happy', 'wonderful', 'fantastic', 'awesome', 'nice'
        }

        # 负面词汇词典
        self.negative_words = {
            '差', '糟', '烂', '讨厌', '恨', '失望', '垃圾', '恶心', '差劲', '不好',
            '难过', '伤心', '失败', '丑', '弱', '惨', '麻烦', '问题', '坑', '雷',
            '骗', '假', '贵', '不值', '后悔', '踩雷', '避雷', '智商税', '翻车',
            'bad', 'terrible', 'awful', 'hate', 'worst', 'disappointing', 'sad',
            'angry', 'fail', 'poor', 'horrible', 'disgusting'
        }

        # 情感增强词
        self.intensifiers = {
            '非常', '特别', '很', '十分', '极其', '超级', '真的', '太', '相当',
            '绝对', '完全', '确实', '实在', '尤其', '格外', '分外',
            'so', 'very', 'extremely', 'really', 'too', 'quite', 'absolutely',
            'completely', 'especially', 'particularly'
        }

        # 否定词
        self.negations = {
            '不', '没', '无', '非', '莫', '勿', '没有', '不是', '别',
            'no', 'not', 'never', 'none', 'without', 'dont', 'doesnt', 'didnt'
        }

        # 细分情绪词典
        self.fine_emotions = {
            'joy': ['开心', '高兴', '兴奋', '愉快', '欢乐', '喜悦', 'happy', 'excited', 'joyful'],
            'trust': ['信任', '信赖', '可靠', '放心', '安心', '信任', 'trust', 'reliable'],
            'anticipation': ['期待', '盼望', '憧憬', '看好', '希望', 'expect', 'hope', 'look forward'],
            'anger': ['愤怒', '生气', '气愤', '恼火', '愤怒', 'angry', 'furious', 'mad'],
            'disappointment': ['失望', '失落', '遗憾', '沮丧', 'disappointed', 'frustrated'],
            'worry': ['担心', '焦虑', '忧虑', '害怕', '恐惧', 'worry', 'anxious', 'fear'],
            'disgust': ['厌恶', '反感', '讨厌', '恶心', 'disgust', 'dislike', 'hate'],
            'surprise': ['惊讶', '震惊', '意外', 'surprise', 'shocked', 'amazed']
        }

        # 方面词典（用于方面级情感分析）
        self.aspect_keywords = {
            '产品': ['产品', '质量', '品质', '做工', '用料', '功能', '性能', 'product', 'quality'],
            '价格': ['价格', '价钱', '费用', '贵', '便宜', '性价比', 'price', 'cost', 'expensive'],
            '服务': ['服务', '客服', '售后', '态度', '体验', 'service', 'support'],
            '设计': ['设计', '外观', '颜值', '好看', '美', '丑', 'design', 'look', 'appearance'],
            '物流': ['物流', '快递', '配送', '发货', '运输', 'shipping', 'delivery'],
            '包装': ['包装', '盒子', '袋子', 'package', 'packaging']
        }

    def analyze(self, text: str) -> SentimentResult:
        """
        执行情感分析

        Args:
            text: 待分析的文本

        Returns:
            SentimentResult 对象
        """
        text_lower = text.lower()
        words = self._tokenize(text_lower)

        # 基础情感分析
        sentiment_scores = self._calculate_sentiment_scores(words, text_lower)

        # 细分情绪分析
        fine_emotions = self._identify_fine_emotions(text_lower)

        # 方面级情感分析
        aspects = self._analyze_aspects(text, words)

        return SentimentResult(
            text=text,
            label=sentiment_scores['label'],
            confidence=sentiment_scores['confidence'],
            positive_score=sentiment_scores['positive'],
            negative_score=sentiment_scores['negative'],
            neutral_score=sentiment_scores['neutral'],
            fine_emotions=fine_emotions,
            aspects=aspects
        )

    def _tokenize(self, text: str) -> List[str]:
        """简单的分词实现"""
        # 中文词汇（2-4字）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
        # 英文单词
        english_words = re.findall(r'[a-z]+', text)
        return chinese_words + english_words

    def _calculate_sentiment_scores(self, words: List[str], text: str) -> Dict:
        """计算情感分数"""
        positive_count = 0
        negative_count = 0
        intensity = 1.0
        negation_active = False

        for i, word in enumerate(words):
            # 检查否定词
            if word in self.negations:
                negation_active = True
                continue

            # 检查情感增强词
            if word in self.intensifiers:
                intensity = 1.5
                continue

            # 检查情感词
            if word in self.positive_words:
                if negation_active:
                    negative_count += intensity
                    negation_active = False
                else:
                    positive_count += intensity
                intensity = 1.0

            elif word in self.negative_words:
                if negation_active:
                    positive_count += intensity
                    negation_active = False
                else:
                    negative_count += intensity
                intensity = 1.0

        # 计算最终分数
        total = positive_count + negative_count
        if total == 0:
            return {
                'label': 'neutral',
                'confidence': 0.5,
                'positive': 0.33,
                'negative': 0.33,
                'neutral': 0.34
            }

        positive_ratio = positive_count / total
        negative_ratio = negative_count / total
        neutral_ratio = 0

        # 判断情感极性
        if positive_ratio > negative_ratio * 1.5:
            label = 'positive'
            confidence = min(positive_ratio, 0.95)
        elif negative_ratio > positive_ratio * 1.5:
            label = 'negative'
            confidence = min(negative_ratio, 0.95)
        else:
            label = 'neutral'
            confidence = 0.5 + abs(positive_ratio - negative_ratio) * 0.5
            neutral_ratio = 1 - (positive_count + negative_count) / (total + 1)

        return {
            'label': label,
            'confidence': confidence,
            'positive': positive_count / (total + 1),
            'negative': negative_count / (total + 1),
            'neutral': neutral_ratio if neutral_ratio > 0 else 0.1
        }

    def _identify_fine_emotions(self, text: str) -> List[Dict]:
        """识别细分情绪"""
        emotions = []
        for emotion_type, keywords in self.fine_emotions.items():
            for keyword in keywords:
                if keyword in text:
                    emotions.append({
                        'type': emotion_type,
                        'keyword': keyword,
                        'intensity': 0.8
                    })
                    break
        return emotions

    def _analyze_aspects(self, text: str, words: List[str]) -> Dict[str, str]:
        """方面级情感分析"""
        aspects = {}
        text_lower = text.lower()

        for aspect, keywords in self.aspect_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # 找到方面词后，分析其周边情感
                    aspect_sentiment = self._analyze_aspect_sentiment(text, keyword)
                    aspects[aspect] = aspect_sentiment
                    break

        return aspects

    def _analyze_aspect_sentiment(self, text: str, aspect_keyword: str) -> str:
        """分析特定方面的情感"""
        # 找到方面词的位置
        pos = text.lower().find(aspect_keyword)
        if pos == -1:
            return 'neutral'

        # 提取方面词周围的文本（前后20字）
        start = max(0, pos - 20)
        end = min(len(text), pos + len(aspect_keyword) + 20)
        context = text[start:end]

        # 分析上下文的情感
        words = self._tokenize(context.lower())
        scores = self._calculate_sentiment_scores(words, context)

        return scores['label']

    def analyze_batch(self, texts: List[str]) -> List[SentimentResult]:
        """批量情感分析"""
        return [self.analyze(text) for text in texts]


# 便捷函数接口
def simple_sentiment_analyze(text: str) -> Dict:
    """简单情感分析接口"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(text)
    return {
        'label': result.label,
        'confidence': result.confidence,
        'positive_score': result.positive_score,
        'negative_score': result.negative_score,
        'neutral_score': result.neutral_score,
        'fine_emotions': result.fine_emotions,
        'aspects': result.aspects
    }


def batch_sentiment_analyze(texts: List[str]) -> List[Dict]:
    """批量情感分析接口"""
    analyzer = SentimentAnalyzer()
    results = analyzer.analyze_batch(texts)
    return [
        {
            'label': r.label,
            'confidence': r.confidence,
            'positive_score': r.positive_score,
            'negative_score': r.negative_score,
            'neutral_score': r.neutral_score,
            'fine_emotions': r.fine_emotions,
            'aspects': r.aspects
        }
        for r in results
    ]


def analyze_sentiment_distribution(results: List[Dict]) -> Dict:
    """分析情感分布统计"""
    labels = [r['label'] for r in results]
    counter = Counter(labels)
    total = len(labels)

    # 计算平均置信度
    avg_confidence = sum(r['confidence'] for r in results) / total if total > 0 else 0

    # 统计细分情绪
    all_emotions = []
    for r in results:
        all_emotions.extend([e['type'] for e in r.get('fine_emotions', [])])
    emotion_counter = Counter(all_emotions)

    return {
        'positive_count': counter.get('positive', 0),
        'negative_count': counter.get('negative', 0),
        'neutral_count': counter.get('neutral', 0),
        'positive_pct': round(counter.get('positive', 0) / total * 100, 2) if total > 0 else 0,
        'negative_pct': round(counter.get('negative', 0) / total * 100, 2) if total > 0 else 0,
        'neutral_pct': round(counter.get('neutral', 0) / total * 100, 2) if total > 0 else 0,
        'total': total,
        'average_confidence': round(avg_confidence, 2),
        'emotion_distribution': dict(emotion_counter.most_common(5))
    }


def extract_keywords(texts: List[str], top_k: int = 20) -> List[Tuple[str, int]]:
    """提取关键词"""
    # 停用词
    stopwords = {
        '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
        '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
        '自己', '这', '那', '啊', '哦', '嗯', '呢', '吧', '吗', 'the', 'a', 'an', 'is',
        'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'
    }

    # 合并所有文本
    all_text = ' '.join(texts).lower()

    # 提取中文词汇（2-4字）
    chinese_words = re.findall(r'[\u4e00-\u9fff]{2,4}', all_text)

    # 提取英文单词
    english_words = re.findall(r'[a-z]{3,}', all_text)

    # 统计词频
    word_freq = Counter(chinese_words + english_words)

    # 过滤停用词和低频词
    filtered = [(word, freq) for word, freq in word_freq.items()
                if word not in stopwords and freq > 1 and len(word) > 1]

    # 返回前k个
    return sorted(filtered, key=lambda x: x[1], reverse=True)[:top_k]


def calculate_heat_index(texts: List[str], timestamps: Optional[List] = None) -> Dict:
    """计算热度指数"""
    total = len(texts)

    # 计算平均文本长度
    avg_length = sum(len(t) for t in texts) / total if total > 0 else 0

    # 计算互动性指标（基于标点符号密度）
    interaction_score = sum(
        t.count('!') + t.count('！') + t.count('?') + t.count('？') +
        t.count('【') + t.count('#')
        for t in texts
    ) / total if total > 0 else 0

    # 计算情感强度（使用情感分析）
    analyzer = SentimentAnalyzer()
    sentiment_results = analyzer.analyze_batch(texts[:100])  # 采样前100条
    high_emotion_count = sum(
        1 for r in sentiment_results
        if r.confidence > 0.7 and r.label != 'neutral'
    )
    emotion_intensity = high_emotion_count / len(sentiment_results) if sentiment_results else 0

    # 热度指数（综合指标）
    heat_score = min(100, (
        total * 0.3 +
        avg_length * 0.05 +
        interaction_score * 5 +
        emotion_intensity * 30
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
        'interaction_score': round(interaction_score, 2),
        'emotion_intensity': round(emotion_intensity, 2)
    }


def identify_risk_points(texts: List[str], sentiment_results: List[Dict]) -> List[Dict]:
    """识别风险点"""
    risk_keywords = {
        '投诉', '举报', '维权', ' lawsuit', '曝光', '黑幕', '造假', '欺骗',
        '退款', '赔偿', '道歉', '负责', '倒闭', '跑路', '骗子', '假货',
        '质量问题', '安全隐患', '事故', '伤亡', 'complaint', 'scam', 'fraud',
        '避雷', '踩雷', '翻车', '塌房', '丑闻', '劣迹'
    }

    risks = []
    for i, (text, sentiment) in enumerate(zip(texts, sentiment_results)):
        text_lower = text.lower()
        matched_keywords = [kw for kw in risk_keywords if kw in text_lower]

        # 风险评级
        if len(matched_keywords) >= 2 or sentiment['label'] == 'negative' and sentiment['confidence'] > 0.8:
            risk_level = 'high'
        elif len(matched_keywords) == 1 or sentiment['label'] == 'negative':
            risk_level = 'medium'
        elif sentiment['negative_score'] > 0.3:
            risk_level = 'low'
        else:
            continue

        risks.append({
            'index': i,
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'risk_level': risk_level,
            'matched_keywords': matched_keywords,
            'sentiment': sentiment['label'],
            'confidence': sentiment['confidence']
        })

    # 按风险等级排序
    risk_order = {'high': 0, 'medium': 1, 'low': 2}
    risks.sort(key=lambda x: risk_order.get(x['risk_level'], 3))

    return risks[:10]


if __name__ == '__main__':
    print("BettaFish Sentiment Analyzer")
    print("基于规则和词典的轻量级情感分析模块")
    print("\nUsage:")
    print("  from scripts.sentiment_analyzer import SentimentAnalyzer")
    print("  analyzer = SentimentAnalyzer()")
    print("  result = analyzer.analyze('这个产品真的很棒！')")
    print("\n注意：本模块仅用于分析从 WebSearch/WebFetch 获取的真实数据")
    print("      严禁使用模拟数据进行测试。")
