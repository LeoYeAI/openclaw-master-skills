#!/usr/bin/env python3
"""
意向性分类模块

功能：
- 按主体分类：自身意向性 / 他人意向性
- 按方向分类：主动意向性 / 被动意向性
- 按内容分类：知觉 / 信念 / 欲望
- 按实现方式分类：内在意向性 / 派生意向性
- 计算分类置信度

设计原则：
- 四维独立分类
- 基于规则和特征匹配
- 提供分类依据和置信度
"""

import argparse
import json
import sys
from typing import Dict, Any, List, Tuple


class IntentionalityClassifier:
    """意向性分类器"""
    
    def __init__(self):
        # 主体分类规则
        self.agent_rules = {
            "self": {
                "keywords": ["我", "我想", "我要", "我觉得", "我认为", "我的", "我自己", "本系统", "我们"],
                "patterns": [r"^我", r"^我们"],
                "weight": 1.0
            },
            "other": {
                "keywords": ["你", "他", "她", "它", "他们", "她们", "你们", "用户", "用户们", "对方"],
                "patterns": [r"^你", r"^他", r"^她"],
                "weight": 1.0
            }
        }
        
        # 方向分类规则
        self.direction_rules = {
            "active": {
                "keywords": ["想要", "需要", "希望", "打算", "计划", "目标", "试图", "寻求", "努力", "致力于"],
                "verbs": ["做", "实现", "完成", "达到", "获得"],
                "weight": 1.0
            },
            "passive": {
                "keywords": ["被", "受", "吸引", "触发", "引发", "迫使", "影响", "导致", "产生"],
                "patterns": [r"被.*?", r"受到.*?"],
                "weight": 1.0
            }
        }
        
        # 内容分类规则
        self.content_rules = {
            "perception": {
                "keywords": ["看到", "听到", "感觉", "察觉", "发现", "观察", "感知", "注意到", "意识到"],
                "patterns": [r".*?(?:看到|听到|感觉|发现|察觉)"],
                "weight": 1.0
            },
            "belief": {
                "keywords": ["相信", "认为", "觉得", "以为", "肯定", "确定", "相信", "确信", "断定"],
                "patterns": [r".*?(?:相信|认为|觉得|以为)"],
                "weight": 1.0
            },
            "desire": {
                "keywords": ["想要", "希望", "渴望", "期待", "需要", "愿望", "向往", "追求", "寻求"],
                "patterns": [r".*?(?:想要|希望|渴望|期待|需要)"],
                "weight": 1.0
            }
        }
        
        # 实现方式分类规则
        self.realization_rules = {
            "intrinsic": {
                "keywords": ["本质", "内在", "本性", "固有", "根本", "天然", "本性"],
                "indicators": ["这是", "属于", "具有"],
                "weight": 1.0
            },
            "derived": {
                "keywords": ["派生", "衍生", "产生", "形成", "获得", "习得", "后天"],
                "indicators": ["因为", "由于", "源于", "来自"],
                "weight": 1.0
            }
        }
    
    def classify_by_agent(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        按主体分类
        
        Args:
            data: 意向性数据
            
        Returns:
            主体分类结果
        """
        content = data.get("preprocessed", {}).get("content", "")
        features = data.get("features", {})
        preliminary = data.get("preliminary_identification", {})
        
        scores = {}
        evidence = []
        
        # 计算每个类别的得分
        for agent_type, rules in self.agent_rules.items():
            score = 0.0
            type_evidence = []
            
            # 关键词匹配
            for keyword in rules["keywords"]:
                count = content.count(keyword)
                if count > 0:
                    score += count * rules["weight"]
                    type_evidence.append(f"关键词'{keyword}'出现{count}次")
            
            # 特征匹配
            feature_count = sum(len(v) for v in features.get(f"{agent_type}_agent", []))
            if feature_count > 0:
                score += feature_count * 0.5
                type_evidence.append(f"特征匹配发现{feature_count}处")
            
            # 初步识别作为参考
            if preliminary.get("likely_agent") == agent_type:
                score += 0.3
                type_evidence.append("初步识别提示")
            
            scores[agent_type] = score
            if type_evidence:
                evidence.extend([(agent_type, e) for e in type_evidence])
        
        # 确定最佳分类
        if scores["self"] > scores["other"]:
            best_type = "self"
            confidence = min(scores["self"] / (scores["self"] + scores["other"] + 0.1), 1.0)
        else:
            best_type = "other"
            confidence = min(scores["other"] / (scores["self"] + scores["other"] + 0.1), 1.0)
        
        return {
            "type": best_type,
            "confidence": round(confidence, 2),
            "evidence": [e[1] for e in evidence if e[0] == best_type],
            "all_scores": {k: round(v, 2) for k, v in scores.items()}
        }
    
    def classify_by_direction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        按方向分类
        
        Args:
            data: 意向性数据
            
        Returns:
            方向分类结果
        """
        content = data.get("preprocessed", {}).get("content", "")
        features = data.get("features", {})
        preliminary = data.get("preliminary_identification", {})
        
        scores = {}
        evidence = []
        
        for direction_type, rules in self.direction_rules.items():
            score = 0.0
            type_evidence = []
            
            # 关键词匹配
            for keyword in rules["keywords"]:
                count = content.count(keyword)
                if count > 0:
                    score += count * rules["weight"]
                    type_evidence.append(f"关键词'{keyword}'出现{count}次")
            
            # 特征匹配
            feature_count = sum(len(v) for v in features.get(f"{direction_type}_direction", []))
            if feature_count > 0:
                score += feature_count * 0.5
                type_evidence.append(f"特征匹配发现{feature_count}处")
            
            # 初步识别作为参考
            if preliminary.get("likely_direction") == direction_type:
                score += 0.3
                type_evidence.append("初步识别提示")
            
            scores[direction_type] = score
            if type_evidence:
                evidence.extend([(direction_type, e) for e in type_evidence])
        
        # 确定最佳分类
        if scores["active"] > scores["passive"]:
            best_type = "active"
            confidence = min(scores["active"] / (scores["active"] + scores["passive"] + 0.1), 1.0)
        else:
            best_type = "passive"
            confidence = min(scores["passive"] / (scores["active"] + scores["passive"] + 0.1), 1.0)
        
        return {
            "type": best_type,
            "confidence": round(confidence, 2),
            "evidence": [e[1] for e in evidence if e[0] == best_type],
            "all_scores": {k: round(v, 2) for k, v in scores.items()}
        }
    
    def classify_by_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        按内容分类
        
        Args:
            data: 意向性数据
            
        Returns:
            内容分类结果
        """
        content = data.get("preprocessed", {}).get("content", "")
        features = data.get("features", {})
        preliminary = data.get("preliminary_identification", {})
        
        scores = {}
        evidence = []
        
        for content_type, rules in self.content_rules.items():
            score = 0.0
            type_evidence = []
            
            # 关键词匹配
            for keyword in rules["keywords"]:
                count = content.count(keyword)
                if count > 0:
                    score += count * rules["weight"]
                    type_evidence.append(f"关键词'{keyword}'出现{count}次")
            
            # 特征匹配
            feature_count = sum(len(v) for v in features.get(f"{content_type}_content", []))
            if feature_count > 0:
                score += feature_count * 0.5
                type_evidence.append(f"特征匹配发现{feature_count}处")
            
            # 初步识别作为参考
            if preliminary.get("likely_content") == content_type:
                score += 0.3
                type_evidence.append("初步识别提示")
            
            scores[content_type] = score
            if type_evidence:
                evidence.extend([(content_type, e) for e in type_evidence])
        
        # 确定最佳分类
        max_score = max(scores.values())
        best_type = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = min(max_score / (total_score + 0.1), 1.0)
        
        return {
            "type": best_type,
            "confidence": round(confidence, 2),
            "evidence": [e[1] for e in evidence if e[0] == best_type],
            "all_scores": {k: round(v, 2) for k, v in scores.items()}
        }
    
    def classify_by_realization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        按实现方式分类
        
        Args:
            data: 意向性数据
            
        Returns:
            实现方式分类结果
        """
        content = data.get("preprocessed", {}).get("content", "")
        
        scores = {}
        evidence = []
        
        for realization_type, rules in self.realization_rules.items():
            score = 0.0
            type_evidence = []
            
            # 关键词匹配
            for keyword in rules["keywords"]:
                count = content.count(keyword)
                if count > 0:
                    score += count * rules["weight"]
                    type_evidence.append(f"关键词'{keyword}'出现{count}次")
            
            # 指示词匹配
            for indicator in rules.get("indicators", []):
                if indicator in content:
                    score += 0.3
                    type_evidence.append(f"发现指示词'{indicator}'")
            
            scores[realization_type] = score
            if type_evidence:
                evidence.extend([(realization_type, e) for e in type_evidence])
        
        # 确定最佳分类
        if scores["intrinsic"] > scores["derived"]:
            best_type = "intrinsic"
            confidence = min(scores["intrinsic"] / (scores["intrinsic"] + scores["derived"] + 0.1), 1.0)
        else:
            best_type = "derived"
            confidence = min(scores["derived"] / (scores["intrinsic"] + scores["derived"] + 0.1), 1.0)
        
        # 如果两者得分都很低，默认为派生
        if scores["intrinsic"] < 0.5 and scores["derived"] < 0.5:
            best_type = "derived"
            confidence = 0.5
            evidence.append(("derived", "无明确指示，默认为派生意向性"))
        
        return {
            "type": best_type,
            "confidence": round(confidence, 2),
            "evidence": [e[1] for e in evidence if e[0] == best_type],
            "all_scores": {k: round(v, 2) for k, v in scores.items()}
        }
    
    def classify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        完整分类（四维）
        
        Args:
            data: 意向性数据
            
        Returns:
            完整分类结果
        """
        result = {
            "agent": self.classify_by_agent(data),
            "direction": self.classify_by_direction(data),
            "content": self.classify_by_content(data),
            "realization": self.classify_by_realization(data)
        }
        
        # 计算整体置信度
        confidences = [
            result["agent"]["confidence"],
            result["direction"]["confidence"],
            result["content"]["confidence"],
            result["realization"]["confidence"]
        ]
        result["overall_confidence"] = round(sum(confidences) / len(confidences), 2)
        
        return result


def main():
    parser = argparse.ArgumentParser(description="意向性分类模块")
    parser.add_argument("--input", required=True, help="输入文件路径（JSON格式）")
    parser.add_argument("--dimension", 
                        choices=["agent", "direction", "content", "realization", "all"],
                        default="all",
                        help="分类维度")
    parser.add_argument("--output", help="输出文件路径（JSON格式）")
    
    args = parser.parse_args()
    
    # 读取输入数据
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    classifier = IntentionalityClassifier()
    
    # 执行分类
    if args.dimension == "all":
        result = classifier.classify(data)
    elif args.dimension == "agent":
        result = {"agent": classifier.classify_by_agent(data)}
    elif args.dimension == "direction":
        result = {"direction": classifier.classify_by_direction(data)}
    elif args.dimension == "content":
        result = {"content": classifier.classify_by_content(data)}
    elif args.dimension == "realization":
        result = {"realization": classifier.classify_by_realization(data)}
    
    # 输出结果
    output_data = json.dumps(result, ensure_ascii=False, indent=2)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_data)
    else:
        print(output_data)


if __name__ == "__main__":
    main()
