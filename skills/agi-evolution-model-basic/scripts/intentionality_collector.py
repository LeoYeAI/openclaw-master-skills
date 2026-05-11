#!/usr/bin/env python3
"""
意向性收集模块

功能：
- 收集来自用户、系统内部和外部的意向性数据
- 预处理数据（格式转换、数据清洗、特征提取）
- 初步识别意向性类型和基本特征

设计原则：
- 模块化设计，支持多数据源
- 标准化输出格式
- 可配置的预处理策略
"""

import argparse
import json
import sys
import re
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional


class IntentionalityCollector:
    """意向性收集器"""
    
    def __init__(self):
        self.keywords = {
            "self_agent": ["我", "我想", "我要", "我觉得", "我认为", "我的", "我自己"],
            "other_agent": ["你", "他", "她", "他们", "你们", "用户", "系统"],
            "active_direction": ["想要", "需要", "希望", "打算", "计划", "目标"],
            "passive_direction": ["被", "受", "吸引", "触发", "引发"],
            "perception_content": ["看到", "听到", "感觉", "察觉", "发现"],
            "belief_content": ["相信", "认为", "觉得", "以为", "肯定"],
            "desire_content": ["想要", "希望", "渴望", "期待", "需要"]
        }
    
    def collect_from_user(self, user_input: str) -> Dict[str, Any]:
        """
        收集用户输入
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            意向性数据对象
        """
        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "source": "user",
            "raw_content": user_input,
            "metadata": {
                "input_type": "direct",
                "channel": "text"
            }
        }
    
    def collect_from_system(self, internal_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        收集系统内部状态
        
        Args:
            internal_state: 系统内部状态字典
            
        Returns:
            意向性数据对象
        """
        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "source": "system",
            "raw_content": json.dumps(internal_state, ensure_ascii=False),
            "metadata": {
                "input_type": "internal",
                "component": internal_state.get("component", "unknown")
            }
        }
    
    def collect_from_external(self, external_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        收集外部数据
        
        Args:
            external_data: 外部数据字典
            
        Returns:
            意向性数据对象
        """
        return {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "source": "external",
            "raw_content": json.dumps(external_data, ensure_ascii=False),
            "metadata": {
                "input_type": "external",
                "source": external_data.get("source", "unknown")
            }
        }
    
    def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        预处理数据
        
        Args:
            data: 原始意向性数据
            
        Returns:
            预处理后的数据
        """
        raw_content = data.get("raw_content", "")
        
        # 格式转换
        if isinstance(raw_content, dict):
            formatted_content = json.dumps(raw_content, ensure_ascii=False)
        else:
            formatted_content = str(raw_content)
        
        # 数据清洗
        cleaned_content = self._clean_text(formatted_content)
        
        # 特征提取
        features = self._extract_features(cleaned_content)
        
        data["preprocessed"] = {
            "content": cleaned_content,
            "length": len(cleaned_content),
            "word_count": len(cleaned_content.split())
        }
        data["features"] = features
        
        return data
    
    def _clean_text(self, text: str) -> str:
        """
        清洗文本
        
        Args:
            text: 原始文本
            
        Returns:
            清洗后的文本
        """
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符（保留基本标点）
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？、；：""''（）【】]', '', text)
        # 去除首尾空格
        text = text.strip()
        return text
    
    def _extract_features(self, text: str) -> Dict[str, Any]:
        """
        提取特征
        
        Args:
            text: 清洗后的文本
            
        Returns:
            特征字典
        """
        features = {}
        
        # 关键词匹配
        for category, keywords in self.keywords.items():
            features[category] = []
            for keyword in keywords:
                if keyword in text:
                    count = text.count(keyword)
                    features[category].append({
                        "keyword": keyword,
                        "count": count
                    })
        
        # 句子结构
        sentences = re.split(r'[。！？.!?]', text)
        features["sentence_count"] = len([s for s in sentences if s.strip()])
        
        # 情绪标记（简单）
        emotion_keywords = ["开心", "难过", "愤怒", "焦虑", "满意", "失望", "期待", "担心"]
        features["emotion"] = []
        for emotion in emotion_keywords:
            if emotion in text:
                features["emotion"].append(emotion)
        
        return features
    
    def preliminary_identify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        初步识别意向性
        
        Args:
            data: 预处理后的数据
            
        Returns:
            初步识别结果
        """
        features = data.get("features", {})
        
        # 简单的初步分类提示
        preliminary_hints = {
            "likely_agent": None,
            "likely_direction": None,
            "likely_content": None
        }
        
        # 判断主体
        self_count = sum(len(v) for v in features.get("self_agent", []))
        other_count = sum(len(v) for v in features.get("other_agent", []))
        if self_count > other_count:
            preliminary_hints["likely_agent"] = "self"
        elif other_count > self_count:
            preliminary_hints["likely_agent"] = "other"
        
        # 判断方向
        active_count = sum(len(v) for v in features.get("active_direction", []))
        passive_count = sum(len(v) for v in features.get("passive_direction", []))
        if active_count > passive_count:
            preliminary_hints["likely_direction"] = "active"
        elif passive_count > active_count:
            preliminary_hints["likely_direction"] = "passive"
        
        # 判断内容类型
        perception_count = sum(len(v) for v in features.get("perception_content", []))
        belief_count = sum(len(v) for v in features.get("belief_content", []))
        desire_count = sum(len(v) for v in features.get("desire_content", []))
        
        if perception_count >= belief_count and perception_count >= desire_count:
            preliminary_hints["likely_content"] = "perception"
        elif belief_count >= desire_count:
            preliminary_hints["likely_content"] = "belief"
        else:
            preliminary_hints["likely_content"] = "desire"
        
        data["preliminary_identification"] = preliminary_hints
        
        return data


def main():
    parser = argparse.ArgumentParser(description="意向性收集模块")
    parser.add_argument("--source", required=True, choices=["user", "system", "external"],
                        help="数据来源")
    parser.add_argument("--content", help="原始内容（文本或JSON字符串）")
    parser.add_argument("--input-file", help="输入文件路径（JSON格式）")
    parser.add_argument("--output-file", help="输出文件路径（JSON格式）")
    
    args = parser.parse_args()
    
    collector = IntentionalityCollector()
    
    # 收集数据
    if args.source == "user":
        if args.input_file:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
        else:
            content = args.content or sys.stdin.read().strip()
        
        if not content:
            print("错误：未提供用户输入内容", file=sys.stderr)
            sys.exit(1)
        
        data = collector.collect_from_user(content)
    
    elif args.source == "system":
        if args.input_file:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
        elif args.content:
            state = json.loads(args.content)
        else:
            print("错误：未提供系统内部状态", file=sys.stderr)
            sys.exit(1)
        
        data = collector.collect_from_system(state)
    
    else:  # external
        if args.input_file:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                external = json.load(f)
        elif args.content:
            external = json.loads(args.content)
        else:
            print("错误：未提供外部数据", file=sys.stderr)
            sys.exit(1)
        
        data = collector.collect_from_external(external)
    
    # 预处理
    data = collector.preprocess(data)
    
    # 初步识别
    data = collector.preliminary_identify(data)
    
    # 输出结果
    result = json.dumps(data, ensure_ascii=False, indent=2)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(result)
    else:
        print(result)


if __name__ == "__main__":
    main()
