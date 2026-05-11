#!/usr/bin/env python3
"""
意向性分析模块

功能：
- 强度分析：评估意向性的显著性强弱
- 紧迫性分析：评估意向性的时间维度
- 优先级分析：基于人格和马斯洛需求评估优先级

设计原则：
- 多维度独立分析
- 加权评分模型
- 可配置的阈值和权重
"""

import argparse
import json
import sys
from typing import Dict, Any, List
from datetime import datetime


class IntentionalityAnalyzer:
    """意向性分析器"""
    
    def __init__(self):
        # 强度阈值
        self.intensity_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
        
        # 紧迫性阈值
        self.urgency_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
        
        # 优先级阈值
        self.priority_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8
        }
        
        # 强度分析权重
        self.intensity_weights = {
            "confidence": 0.3,  # 分类置信度
            "word_count": 0.2,  # 表达长度
            "keyword_count": 0.3,  # 关键词数量
            "emotion_strength": 0.2  # 情绪强度
        }
        
        # 紧迫性分析权重
        self.urgency_weights = {
            "time_indicators": 0.4,  # 时间指示词
            "urgency_keywords": 0.4,  # 紧迫性关键词
            "active_direction": 0.2  # 主动方向
        }
        
        # 优先级分析权重
        self.priority_weights = {
            "intensity": 0.3,  # 强度
            "urgency": 0.3,  # 紧迫性
            "maslow_alignment": 0.2,  # 马斯洛需求对齐
            "personality_match": 0.2  # 人格匹配度
        }
        
        # 紧迫性关键词
        self.urgency_keywords = [
            "紧急", "急需", "马上", "立刻", "现在", "今天", "尽快", "立即",
            "等不及", "来不及", "时间紧迫", "关键时刻"
        ]
        
        # 时间指示词
        self.time_indicators = {
            "immediate": ["现在", "立即", "马上", "此刻"],
            "short": ["今天", "今天", "明天", "本周"],
            "medium": ["本月", "近期", "不久"],
            "long": ["将来", "以后", "长期"]
        }
    
    def analyze_intensity(self, classification: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        强度分析
        
        Args:
            classification: 分类结果
            data: 原始意向性数据
            
        Returns:
            强度分析结果
        """
        preprocessed = data.get("preprocessed", {})
        features = data.get("features", {})
        
        # 1. 置信度贡献
        overall_confidence = classification.get("overall_confidence", 0.5)
        confidence_score = overall_confidence * self.intensity_weights["confidence"]
        
        # 2. 表达长度贡献
        word_count = preprocessed.get("word_count", 0)
        normalized_word_count = min(word_count / 100, 1.0)  # 归一化到0-1
        word_count_score = normalized_word_count * self.intensity_weights["word_count"]
        
        # 3. 关键词数量贡献
        total_keyword_count = sum(
            sum(v.get("count", 0) for v in values if isinstance(v, list))
            for values in features.values()
            if isinstance(values, list)
        )
        normalized_keyword_count = min(total_keyword_count / 10, 1.0)
        keyword_score = normalized_keyword_count * self.intensity_weights["keyword_count"]
        
        # 4. 情绪强度贡献
        emotion_list = features.get("emotion", [])
        emotion_strength = min(len(emotion_list) / 3, 1.0)  # 最多3个情绪词
        emotion_score = emotion_strength * self.intensity_weights["emotion_strength"]
        
        # 计算总强度
        total_intensity = confidence_score + word_count_score + keyword_score + emotion_score
        
        # 确定强度级别
        if total_intensity >= self.intensity_thresholds["high"]:
            level = "high"
        elif total_intensity >= self.intensity_thresholds["medium"]:
            level = "medium"
        else:
            level = "low"
        
        return {
            "score": round(total_intensity, 2),
            "level": level,
            "components": {
                "confidence": round(confidence_score, 2),
                "word_count": round(word_count_score, 2),
                "keyword_count": round(keyword_score, 2),
                "emotion_strength": round(emotion_score, 2)
            },
            "thresholds": self.intensity_thresholds
        }
    
    def analyze_urgency(self, classification: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        紧迫性分析
        
        Args:
            classification: 分类结果
            data: 原始意向性数据
            
        Returns:
            紧迫性分析结果
        """
        content = data.get("preprocessed", {}).get("content", "")
        direction_type = classification.get("direction", {}).get("type", "passive")
        
        # 1. 时间指示词贡献
        time_score = 0.0
        time_indicators_found = []
        
        for urgency_level, keywords in self.time_indicators.items():
            for keyword in keywords:
                if keyword in content:
                    if urgency_level == "immediate":
                        time_score += 0.3
                    elif urgency_level == "short":
                        time_score += 0.2
                    elif urgency_level == "medium":
                        time_score += 0.1
                    else:
                        time_score += 0.05
                    time_indicators_found.append(keyword)
        
        normalized_time_score = min(time_score, 1.0) * self.urgency_weights["time_indicators"]
        
        # 2. 紧迫性关键词贡献
        urgency_keyword_score = 0.0
        urgency_keywords_found = []
        
        for keyword in self.urgency_keywords:
            if keyword in content:
                urgency_keyword_score += 0.2
                urgency_keywords_found.append(keyword)
        
        normalized_urgency_score = min(urgency_keyword_score, 1.0) * self.urgency_weights["urgency_keywords"]
        
        # 3. 主动方向贡献
        active_direction_score = 1.0 if direction_type == "active" else 0.5
        active_score = active_direction_score * self.urgency_weights["active_direction"]
        
        # 计算总紧迫性
        total_urgency = normalized_time_score + normalized_urgency_score + active_score
        
        # 确定紧迫性级别
        if total_urgency >= self.urgency_thresholds["high"]:
            level = "high"
        elif total_urgency >= self.urgency_thresholds["medium"]:
            level = "medium"
        else:
            level = "low"
        
        return {
            "score": round(total_urgency, 2),
            "level": level,
            "components": {
                "time_indicators": round(normalized_time_score, 2),
                "urgency_keywords": round(normalized_urgency_score, 2),
                "active_direction": round(active_score, 2)
            },
            "indicators_found": time_indicators_found + urgency_keywords_found,
            "thresholds": self.urgency_thresholds
        }
    
    def analyze_priority(self, analysis: Dict[str, Any], personality: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        优先级分析
        
        Args:
            analysis: 包含强度和紧迫性分析结果
            personality: 人格数据（可选）
            
        Returns:
            优先级分析结果
        """
        intensity = analysis.get("intensity", {}).get("score", 0.5)
        urgency = analysis.get("urgency", {}).get("score", 0.5)
        
        # 1. 强度贡献
        intensity_score = intensity * self.priority_weights["intensity"]
        
        # 2. 紧迫性贡献
        urgency_score = urgency * self.priority_weights["urgency"]
        
        # 3. 马斯洛需求对齐贡献
        maslow_alignment_score = 0.5 * self.priority_weights["maslow_alignment"]
        aligned_with_maslow = "self_actualization"  # 默认值
        
        if personality:
            # 根据人格数据调整
            openness = personality.get("openness", 0.5)
            conscientiousness = personality.get("conscientiousness", 0.5)
            
            # 开放性高的人更关注自我实现
            if openness > 0.7:
                maslow_alignment_score = 0.8 * self.priority_weights["maslow_alignment"]
                aligned_with_maslow = "self_actualization"
            # 尽责性高的人更关注基础需求
            elif conscientiousness > 0.7:
                maslow_alignment_score = 0.6 * self.priority_weights["maslow_alignment"]
                aligned_with_maslow = "safety"
        
        # 4. 人格匹配度贡献
        personality_match_score = 0.5 * self.priority_weights["personality_match"]
        
        # 计算总优先级
        total_priority = intensity_score + urgency_score + maslow_alignment_score + personality_match_score
        
        # 确定优先级级别
        if total_priority >= self.priority_thresholds["high"]:
            level = "high"
        elif total_priority >= self.priority_thresholds["medium"]:
            level = "medium"
        else:
            level = "low"
        
        return {
            "score": round(total_priority, 2),
            "level": level,
            "components": {
                "intensity": round(intensity_score, 2),
                "urgency": round(urgency_score, 2),
                "maslow_alignment": round(maslow_alignment_score, 2),
                "personality_match": round(personality_match_score, 2)
            },
            "aligned_with_maslow": aligned_with_maslow,
            "thresholds": self.priority_thresholds
        }
    
    def analyze(self, classification: Dict[str, Any], data: Dict[str, Any], 
                personality: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        完整分析
        
        Args:
            classification: 分类结果
            data: 原始意向性数据
            personality: 人格数据（可选）
            
        Returns:
            完整分析结果
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "intensity": self.analyze_intensity(classification, data),
            "urgency": self.analyze_urgency(classification, data)
        }
        
        # 优先级分析需要先完成强度和紧迫性分析
        result["priority"] = self.analyze_priority(result, personality)
        
        # 计算整体评分
        overall_score = (
            result["intensity"]["score"] * 0.3 +
            result["urgency"]["score"] * 0.3 +
            result["priority"]["score"] * 0.4
        )
        result["overall_score"] = round(overall_score, 2)
        
        return result


def main():
    parser = argparse.ArgumentParser(description="意向性分析模块")
    parser.add_argument("--classification", required=True, 
                        help="分类结果文件路径（JSON格式）")
    parser.add_argument("--data", required=True, 
                        help="原始意向性数据文件路径（JSON格式）")
    parser.add_argument("--personality", 
                        help="人格数据文件路径（JSON格式，可选）")
    parser.add_argument("--dimension",
                        choices=["intensity", "urgency", "priority", "all"],
                        default="all",
                        help="分析维度")
    parser.add_argument("--output", help="输出文件路径（JSON格式）")
    
    args = parser.parse_args()
    
    # 读取输入数据
    with open(args.classification, 'r', encoding='utf-8') as f:
        classification = json.load(f)
    
    with open(args.data, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    personality = None
    if args.personality:
        with open(args.personality, 'r', encoding='utf-8') as f:
            personality = json.load(f)
    
    analyzer = IntentionalityAnalyzer()
    
    # 执行分析
    result = analyzer.analyze(classification, data, personality)
    
    # 根据维度过滤结果
    if args.dimension == "intensity":
        result = {"intensity": result["intensity"]}
    elif args.dimension == "urgency":
        result = {"urgency": result["urgency"]}
    elif args.dimension == "priority":
        result = {"priority": result["priority"]}
    
    # 输出结果
    output_data = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_data)
    else:
        print(output_data)


if __name__ == "__main__":
    main()
