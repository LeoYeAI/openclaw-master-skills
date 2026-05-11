#!/usr/bin/env python3
"""
记忆存储纯Python实现

不依赖任何编译的.so文件，使用纯Python实现所有记忆存储功能。
包括：记录存储、检索、分析、反馈、模式识别等。
"""

import json
import os
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Record:
    """交互记录"""
    timestamp: str
    user_query: str
    intent_type: str
    reasoning_quality: float = 8.0
    solution_effectiveness: float = 8.0
    innovation_score: float = 7.0
    new_insights: List[str] = None
    feedback: Dict[str, str] = None
    overall_rating: str = "good"
    response: str = ""  # 新增：生成的响应
    objectivity_metric: Dict = None  # 新增：客观性标注
    self_correction: Dict = None  # 新增：自我纠错记录

    def __post_init__(self):
        if self.new_insights is None:
            self.new_insights = []
        if self.feedback is None:
            self.feedback = {
                "drive": "",
                "math": "",
                "iteration": ""
            }
        if self.objectivity_metric is None:
            self.objectivity_metric = {}
        if self.self_correction is None:
            self.self_correction = {}

    def to_dict(self) -> dict:
        return asdict(self)

    def get_value_weight(self) -> float:
        """计算价值权重"""
        return (
            self.reasoning_quality * 0.4 +
            self.solution_effectiveness * 0.3 +
            self.innovation_score * 0.3
        ) / 10.0


@dataclass
class AnalysisResult:
    """分析结果"""
    total_records: int
    rating_distribution: Dict[str, int]
    intent_type_distribution: Dict[str, int]
    average_scores: Dict[str, float]
    recent_insights: List[str]

    def to_dict(self) -> dict:
        return asdict(self)


class MemoryStore:
    """记忆存储管理器（纯Python实现）"""

    def __init__(self, memory_dir: str = "./agi_memory"):
        """
        初始化记忆存储

        Args:
            memory_dir: 记忆存储目录
        """
        self.memory_dir = memory_dir
        self.records_file = os.path.join(memory_dir, "records.json")
        self.narrative_file = os.path.join(memory_dir, "narrative.md")
        self._records: List[Record] = []
        self._load_records()

    def _load_records(self):
        """加载记录"""
        if not os.path.exists(self.records_file):
            self._records = []
            return

        with open(self.records_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self._records = [Record(**item) for item in data]

    def _save_records(self):
        """保存记录"""
        os.makedirs(self.memory_dir, exist_ok=True)

        with open(self.records_file, 'w', encoding='utf-8') as f:
            json.dump([r.to_dict() for r in self._records], f, ensure_ascii=False, indent=2)

    def store(self, data: dict) -> bool:
        """
        存储记录

        Args:
            data: 记录数据

        Returns:
            bool: 是否成功
        """
        try:
            record = Record(
                timestamp=data.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ")),
                user_query=data.get("user_query", ""),
                intent_type=data.get("intent_type", ""),
                reasoning_quality=data.get("reasoning_quality", 8.0),
                solution_effectiveness=data.get("solution_effectiveness", 8.0),
                innovation_score=data.get("innovation_score", 7.0),
                new_insights=data.get("new_insights", []),
                feedback=data.get("feedback", {}),
                overall_rating=data.get("overall_rating", "good")
            )

            self._records.append(record)
            self._save_records()

            return True
        except Exception as e:
            print(f"存储记录失败: {e}")
            return False

    def retrieve(self, query_type: str, limit: int = 5) -> List[Dict]:
        """
        检索记录

        Args:
            query_type: 查询类型
            limit: 返回数量限制

        Returns:
            List[Dict]: 匹配的记录
        """
        # 简单的匹配逻辑
        matched = []

        for record in reversed(self._records):
            if query_type.lower() in record.intent_type.lower():
                matched.append(record.to_dict())
                if len(matched) >= limit:
                    break

        return matched

    def analyze(self) -> AnalysisResult:
        """
        分析记录

        Returns:
            AnalysisResult: 分析结果
        """
        if not self._records:
            return AnalysisResult(
                total_records=0,
                rating_distribution={},
                intent_type_distribution={},
                average_scores={},
                recent_insights=[]
            )

        total = len(self._records)

        # 评分分布
        rating_dist = {}
        for record in self._records:
            rating = record.overall_rating
            rating_dist[rating] = rating_dist.get(rating, 0) + 1

        # 意图类型分布
        intent_dist = {}
        for record in self._records:
            intent = record.intent_type
            intent_dist[intent] = intent_dist.get(intent, 0) + 1

        # 平均分
        avg_reasoning = sum(r.reasoning_quality for r in self._records) / total
        avg_effectiveness = sum(r.solution_effectiveness for r in self._records) / total
        avg_innovation = sum(r.innovation_score for r in self._records) / total

        # 最近洞察
        recent_insights = []
        for record in reversed(self._records[-10:]):
            recent_insights.extend(record.new_insights)

        return AnalysisResult(
            total_records=total,
            rating_distribution=rating_dist,
            intent_type_distribution=intent_dist,
            average_scores={
                "reasoning_quality": round(avg_reasoning, 2),
                "solution_effectiveness": round(avg_effectiveness, 2),
                "innovation_score": round(avg_innovation, 2)
            },
            recent_insights=recent_insights[-20:]
        )

    def feedback(self, vertex: str) -> Dict[str, str]:
        """
        生成反馈建议

        Args:
            vertex: 顶点名称（drive/math/iteration）

        Returns:
            Dict: 反馈建议
        """
        analysis = self.analyze()

        # 根据分析结果生成反馈
        feedback_map = {
            "drive": {
                "suggestion": "需求识别准确",
                "optimization": "继续优化优先级排序"
            },
            "math": {
                "suggestion": "推理方法有效",
                "optimization": "可增强逻辑一致性检查"
            },
            "iteration": {
                "suggestion": "进化路径平稳",
                "optimization": "尝试更多创新策略"
            }
        }

        if analysis.total_records == 0:
            return {
                "vertex": vertex,
                "suggestion": "暂无数据",
                "optimization": "需要更多交互记录"
            }

        base_feedback = feedback_map.get(vertex, {})

        # 根据评分调整
        avg_effectiveness = analysis.average_scores.get("solution_effectiveness", 8.0)

        if avg_effectiveness > 8.5:
            base_feedback["optimization"] = "当前策略优秀，继续保持"

        return base_feedback

    def patterns(self) -> List[Dict]:
        """
        识别模式

        Returns:
            List[Dict]: 识别到的模式
        """
        if len(self._records) < 5:
            return []

        patterns = []

        # 识别高频意图类型
        analysis = self.analyze()
        intent_dist = analysis.intent_type_distribution

        if intent_dist:
            most_common = max(intent_dist, key=intent_dist.get)
            if intent_dist[most_common] >= 3:
                patterns.append({
                    "type": "frequent_intent",
                    "pattern": most_common,
                    "frequency": intent_dist[most_common]
                })

        # 识别高分模式
        high_quality = [r for r in self._records if r.get_value_weight() > 0.8]
        if len(high_quality) >= 3:
            patterns.append({
                "type": "high_quality_pattern",
                "count": len(high_quality),
                "avg_score": sum(r.get_value_weight() for r in high_quality) / len(high_quality)
            })

        return patterns

    def compress(self, threshold: float = 0.5):
        """
        压缩低价值记录

        Args:
            threshold: 价值权重阈值
        """
        if len(self._records) < 10:
            return

        # 分离高低价值记录
        high_value = [r for r in self._records if r.get_value_weight() >= threshold]
        low_value = [r for r in self._records if r.get_value_weight() < threshold]

        # 保留所有高价值记录
        # 低价值记录保留摘要
        if low_value:
            summary_record = Record(
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                user_query=f"[摘要] {len(low_value)}条低价值记录",
                intent_type="summary",
                reasoning_quality=sum(r.reasoning_quality for r in low_value) / len(low_value),
                solution_effectiveness=sum(r.solution_effectiveness for r in low_value) / len(low_value),
                innovation_score=sum(r.innovation_score for r in low_value) / len(low_value),
                new_insights=[],
                feedback={},
                overall_rating="neutral"
            )
            high_value.append(summary_record)

        self._records = high_value
        self._save_records()

    def get_stats(self) -> Dict:
        """
        获取统计信息

        Returns:
            Dict: 统计信息
        """
        analysis = self.analyze()

        return {
            "total_records": analysis.total_records,
            "rating_distribution": analysis.rating_distribution,
            "intent_type_distribution": analysis.intent_type_distribution,
            "average_scores": analysis.average_scores,
            "recent_insights_count": len(analysis.recent_insights),
            "patterns_count": len(self.patterns())
        }


# ===== 命令行接口 =====

def main():
    """命令行测试接口"""
    print("=== 记忆存储纯Python实现（测试模式） ===\n")

    memory = MemoryStore()

    # 测试存储
    print("测试1：存储记录")
    memory.store({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "user_query": "架构升级需要谨慎",
        "intent_type": "架构决策",
        "reasoning_quality": 9.0,
        "solution_effectiveness": 9.0,
        "innovation_score": 7.0,
        "new_insights": ["架构升级是相变事件", "谨慎是美德"],
        "feedback": {
            "drive": "强化需求验证",
            "math": "优化推理规则",
            "iteration": "渐进演化优于激进突变"
        },
        "overall_rating": "good"
    })
    print("✓ 记录已存储\n")

    # 测试检索
    print("测试2：检索记录")
    results = memory.retrieve("架构决策", limit=5)
    print(f"✓ 找到 {len(results)} 条记录\n")

    # 测试分析
    print("测试3：分析记录")
    analysis = memory.analyze()
    print(f"✓ 总记录数: {analysis.total_records}")
    print(f"✓ 平均推理质量: {analysis.average_scores.get('reasoning_quality', 0)}")
    print(f"✓ 最近洞察数: {len(analysis.recent_insights)}\n")

    # 测试反馈
    print("测试4：生成反馈")
    feedback = memory.feedback("math")
    print(f"✓ 反馈: {feedback}\n")

    # 测试模式识别
    print("测试5：识别模式")
    patterns = memory.patterns()
    print(f"✓ 识别到 {len(patterns)} 个模式\n")

    # 测试统计
    print("测试6：获取统计")
    stats = memory.get_stats()
    print(f"✓ 统计信息: {stats}\n")

    print("=== 所有测试完成 ===")


if __name__ == "__main__":
    main()
