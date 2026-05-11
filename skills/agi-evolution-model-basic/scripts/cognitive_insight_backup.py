#!/usr/bin/env python3
"""
认知架构洞察组件

功能：从数学顶点输出的结构化模式中提取洞察，为映射层和自我迭代提供进化依据
- 总结：从验证后的模式中提取核心特征
- 分类：识别模式类型和洞察类型
- 共性：跨场景特征识别
- 革新依据：判断改进空间
- 适用性评估：评估洞察在当前场景下的可用性

协议：AGPL-3.0
作者：kiwifruit
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import hashlib


class CognitiveInsight:
    """认知架构洞察组件"""
    
    def __init__(self, memory_dir: str = "./agi_memory"):
        self.memory_dir = memory_dir
        self.cognitive_insight_dir = os.path.join(memory_dir, "cognitive_insight")
        os.makedirs(self.cognitive_insight_dir, exist_ok=True)
        
        # 存储文件
        self.patterns_file = os.path.join(self.cognitive_insight_dir, "patterns.json")
        self.insights_file = os.path.join(self.cognitive_insight_dir, "insights.json")
        self.pattern_library_file = os.path.join(self.cognitive_insight_dir, "pattern_library.json")
        
        # 加载数据
        self.patterns = self._load_json(self.patterns_file, {"patterns": {}, "metadata": {"total_count": 0}})
        self.insights = self._load_json(self.insights_file, {"insights": {}, "metadata": {"total_count": 0}})
        self.pattern_library = self._load_json(self.pattern_library_file, {"strategies": [], "logics": [], "behaviors": [], "errors": []})
        
        # 适用性权重
        self.applicability_weights = {
            "timeliness": 0.2,
            "relevance": 0.3,
            "compatibility": 0.2,
            "resource_efficiency": 0.15,
            "risk": 0.15
        }
        
        self.apply_threshold = 0.7
        self.wait_threshold = 0.4
    
    # ==================== 公开API ====================
    
    def add_pattern(self, pattern: dict) -> str:
        """添加来自数学顶点的模式"""
        pattern_id = self._generate_pattern_id(pattern)
        standardized = self._standardize_pattern(pattern, pattern_id)
        
        self.patterns["patterns"][pattern_id] = standardized
        self.patterns["metadata"]["total_count"] += 1
        self.patterns["metadata"]["last_updated"] = datetime.now().isoformat()
        
        self._update_pattern_library(standardized)
        self._save_patterns()
        self._save_pattern_library()
        
        return pattern_id
    
    def generate_insight(self, pattern_ids: List[str]) -> dict:
        """基于指定模式生成洞察"""
        patterns = [self.patterns["patterns"][pid] for pid in pattern_ids if pid in self.patterns["patterns"]]
        if not patterns:
            raise ValueError("未找到有效的模式")
        
        insight_id = self._generate_insight_id(patterns)
        
        # 执行洞察流程
        summary = self._summarize_patterns(patterns)
        classification = self._classify_insight(patterns, summary)
        commonality = self._extract_commonality(patterns)
        innovation = self._evaluate_innovation_basis(patterns, classification)
        confidence = self._calculate_confidence(patterns, summary, innovation)
        
        # 初始适用性评估
        applicability = self._calculate_initial_applicability(patterns, classification)
        
        insight = {
            "insight_id": insight_id,
            "timestamp": datetime.now().isoformat(),
            "insight_type": classification["insight_type"],
            "summary": summary["summary"],
            "classification": classification,
            "commonality": commonality,
            "innovation_basis": innovation,
            "confidence": confidence,
            "applicability": applicability,
            "source_patterns": pattern_ids,
            "validation_status": "pending",
            "application_status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.insights["insights"][insight_id] = insight
        self.insights["metadata"]["total_count"] += 1
        self._save_insights()
        
        return insight
    
    def get_insight(self, insight_id: str) -> dict:
        """获取洞察详情"""
        return self.insights["insights"].get(insight_id)
    
    def list_insights(self, insight_type: Optional[str] = None, status: Optional[str] = None, limit: int = 100) -> List[dict]:
        """列出洞察"""
        insights = list(self.insights["insights"].values())
        
        if insight_type:
            insights = [i for i in insights if i["insight_type"] == insight_type]
        if status:
            insights = [i for i in insights if i["validation_status"] == status]
        
        insights.sort(key=lambda x: x["confidence"], reverse=True)
        return insights[:limit]
    
    def validate_insight(self, insight_id: str, result: bool, feedback: str = "") -> None:
        """验证洞察效果"""
        if insight_id not in self.insights["insights"]:
            raise ValueError(f"洞察不存在: {insight_id}")
        
        insight = self.insights["insights"][insight_id]
        insight["validation_status"] = "validated" if result else "rejected"
        insight["validation_result"] = {
            "validated_at": datetime.now().isoformat(),
            "result": result,
            "feedback": feedback
        }
        self._save_insights()
    
    def assess_applicability(self, insight_id: str, context: dict = None) -> dict:
        """评估洞察的当前适用性"""
        if insight_id not in self.insights["insights"]:
            raise ValueError(f"洞察不存在: {insight_id}")
        
        insight = self.insights["insights"][insight_id]
        
        # 计算各维度评分
        timeliness = self._assess_timeliness(insight)
        relevance = self._assess_relevance(insight, context)
        compatibility = self._assess_compatibility(insight, context)
        resource = self._assess_resource_efficiency(insight, context)
        risk = self._assess_risk(insight)
        
        # 综合评分
        score = (
            timeliness * self.applicability_weights["timeliness"] +
            relevance * self.applicability_weights["relevance"] +
            compatibility * self.applicability_weights["compatibility"] +
            resource * self.applicability_weights["resource_efficiency"] +
            risk * self.applicability_weights["risk"]
        )
        
        # 生成推荐
        if score >= self.apply_threshold:
            recommendation = "apply"
        elif score >= self.wait_threshold:
            recommendation = "wait"
        else:
            recommendation = "reject"
        
        # 更新洞察
        applicability_data = {
            "score": score,
            "dimensions": {
                "timeliness": timeliness,
                "relevance": relevance,
                "compatibility": compatibility,
                "resource_efficiency": resource,
                "risk": risk
            },
            "last_assessed": datetime.now().isoformat(),
            "assessment_count": insight.get("applicability", {}).get("assessment_count", 0) + 1
        }
        
        insight["applicability"] = applicability_data
        self._save_insights()
        
        result = applicability_data.copy()
        result["recommendation"] = recommendation
        return result
    
    def list_insights_by_applicability(self, min_applicability: float = 0.5, context: dict = None, limit: int = 100) -> List[dict]:
        """按适用性列出洞察"""
        insights = list(self.insights["insights"].values())
        insights = [i for i in insights if i["validation_status"] == "validated"]
        
        # 动态评估
        if context is not None:
            for insight in insights:
                self.assess_applicability(insight["insight_id"], context)
        
        # 筛选和排序
        insights = [i for i in insights if i.get("applicability", {}).get("score", 0) >= min_applicability]
        insights.sort(key=lambda x: x.get("applicability", {}).get("score", 0), reverse=True)
        
        return insights[:limit]
    
    def get_pattern_library(self) -> dict:
        """获取模式库"""
        return self.pattern_library
    
    # ==================== 私有方法 ====================
    
    def _load_json(self, filepath: str, default: dict) -> dict:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: str, data: dict) -> None:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _save_patterns(self) -> None:
        self._save_json(self.patterns_file, self.patterns)
    
    def _save_insights(self) -> None:
        self._save_json(self.insights_file, self.insights)
    
    def _save_pattern_library(self) -> None:
        self._save_json(self.pattern_library_file, self.pattern_library)
    
    def _generate_pattern_id(self, pattern: dict) -> str:
        content = json.dumps(pattern, sort_keys=True)
        return f"pattern_{hashlib.md5(content.encode()).hexdigest()[:8]}"
    
    def _generate_insight_id(self, patterns: List[dict]) -> str:
        content = json.dumps([p["pattern_id"] for p in patterns], sort_keys=True)
        return f"insight_{hashlib.md5(content.encode()).hexdigest()[:8]}"
    
    def _standardize_pattern(self, pattern: dict, pattern_id: str) -> dict:
        return {
            "pattern_id": pattern_id,
            "timestamp": pattern.get("timestamp", datetime.now().isoformat()),
            "source": pattern.get("source", "unknown"),
            "pattern_type": pattern.get("pattern_type", "unknown"),
            "pattern_data": pattern.get("pattern_data", {}),
            "validation_score": pattern.get("validation_score", 0.0),
            "context": pattern.get("context", {}),
            "occurrence_count": pattern.get("occurrence_count", 1),
            "time_span": pattern.get("time_span", 0.0),
            "created_at": datetime.now().isoformat()
        }
    
    def _update_pattern_library(self, pattern: dict) -> None:
        signature = self._compute_pattern_signature(pattern)
        library_type = f"{pattern['pattern_type']}s"
        
        if library_type in self.pattern_library:
            for item in self.pattern_library[library_type]:
                if item["pattern_signature"] == signature:
                    item["occurrence_count"] += pattern["occurrence_count"]
                    item["last_seen"] = pattern["timestamp"]
                    return
            
            self.pattern_library[library_type].append({
                "pattern_signature": signature,
                "description": pattern["pattern_data"].get("description", ""),
                "occurrence_count": pattern["occurrence_count"],
                "first_seen": pattern["timestamp"],
                "last_seen": pattern["timestamp"]
            })
    
    def _compute_pattern_signature(self, pattern: dict) -> str:
        content = json.dumps({
            "pattern_type": pattern["pattern_type"],
            "source": pattern["source"]
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    # ==================== 核心算法 ====================
    
    def _summarize_patterns(self, patterns: List[dict]) -> dict:
        grouped = {}
        for p in patterns:
            ptype = p["pattern_type"]
            if ptype not in grouped:
                grouped[ptype] = []
            grouped[ptype].append(p)
        
        core_features = {}
        for ptype, pats in grouped.items():
            core_features[ptype] = {
                "count": len(pats),
                "avg_validation": sum(p["validation_score"] for p in pats) / len(pats),
                "total_occurrences": sum(p["occurrence_count"] for p in pats)
            }
        
        summary = "; ".join([
            f"发现{ptype}类型模式{f['count']}个，平均验证得分{f['avg_validation']:.2f}，累计出现{f['total_occurrences']}次"
            for ptype, f in core_features.items()
        ])
        
        avg_validation = sum(p["validation_score"] for p in patterns) / len(patterns)
        return {"summary": summary, "core_features": core_features, "confidence": min(avg_validation, 1.0)}
    
    def _classify_insight(self, patterns: List[dict], summary: dict) -> dict:
        pattern_types = set(p["pattern_type"] for p in patterns)
        impact_scope = "local" if len(patterns) < 5 else "global"
        
        avg_validation = sum(p["validation_score"] for p in patterns) / len(patterns)
        urgency = "high" if avg_validation > 0.8 else ("medium" if avg_validation > 0.5 else "low")
        
        if "error" in pattern_types:
            insight_type = "error_correction"
        elif impact_scope == "global":
            insight_type = "architecture_upgrade"
        else:
            insight_type = "strategy_optimization"
        
        return {
            "pattern_types": list(pattern_types),
            "insight_type": insight_type,
            "impact_scope": impact_scope,
            "urgency": urgency,
            "classification_confidence": 0.8
        }
    
    def _extract_commonality(self, patterns: List[dict]) -> dict:
        common_sources = set(p["source"] for p in patterns)
        common_types = set(p["pattern_type"] for p in patterns)
        
        return {
            "global_commonality": {
                "all_from_same_source": len(common_sources) == 1,
                "all_same_type": len(common_types) == 1
            },
            "diversity_score": 0.3
        }
    
    def _evaluate_innovation_basis(self, patterns: List[dict], classification: dict) -> dict:
        avg_validation = sum(p["validation_score"] for p in patterns) / len(patterns)
        total_occurrences = sum(p["occurrence_count"] for p in patterns)
        
        exists = avg_validation > 0.7 and total_occurrences > 10
        
        if exists:
            return {
                "exists": True,
                "description": f"发现高频高置信度模式，建议优化{classification['insight_type']}",
                "priority": min(avg_validation, 1.0),
                "expected_impact": {"scope": classification["impact_scope"]}
            }
        
        return {
            "exists": False,
            "description": "未发现值得革新的依据",
            "priority": 0.0,
            "expected_impact": {}
        }
    
    def _calculate_confidence(self, patterns: List[dict], summary: dict, innovation: dict) -> float:
        validation_factor = sum(p["validation_score"] for p in patterns) / len(patterns)
        pattern_factor = min(len(patterns) / 10, 1.0)
        summary_factor = summary.get("confidence", 0.5)
        innovation_factor = innovation["priority"] if innovation["exists"] else 0.8
        
        confidence = (
            validation_factor * 0.3 +
            pattern_factor * 0.2 +
            summary_factor * 0.3 +
            innovation_factor * 0.2
        )
        
        return min(confidence, 1.0)
    
    # ==================== 适用性评估 ====================
    
    def _calculate_initial_applicability(self, patterns: List[dict], classification: dict) -> dict:
        """计算初始适用性"""
        timeliness = 1.0  # 新生成的洞察，时效性为1.0
        relevance = 0.7  # 默认中等相关性
        compatibility = 0.9  # 默认高兼容性
        resource = 0.8  # 默认良好资源效率
        risk = 0.75  # 默认中等风险
        
        score = (
            timeliness * self.applicability_weights["timeliness"] +
            relevance * self.applicability_weights["relevance"] +
            compatibility * self.applicability_weights["compatibility"] +
            resource * self.applicability_weights["resource_efficiency"] +
            risk * self.applicability_weights["risk"]
        )
        
        return {
            "score": score,
            "dimensions": {
                "timeliness": timeliness,
                "relevance": relevance,
                "compatibility": compatibility,
                "resource_efficiency": resource,
                "risk": risk
            },
            "last_assessed": datetime.now().isoformat(),
            "assessment_count": 1
        }
    
    def _assess_timeliness(self, insight: dict) -> float:
        """时效性评估"""
        created = datetime.fromisoformat(insight["created_at"])
        days_passed = (datetime.now() - created).days
        return max(0.2, 1.0 - days_passed * 0.05)
    
    def _assess_relevance(self, insight: dict, context: dict) -> float:
        """相关性评估"""
        if not context:
            return 0.5
        
        task_type = context.get("task_type", "general")
        insight_type = insight["insight_type"]
        
        relevance_map = {
            "error_correction": {"error": 1.0, "general": 0.3},
            "strategy_optimization": {"optimization": 1.0, "general": 0.7},
            "logic_improvement": {"logic": 1.0, "general": 0.6},
            "architecture_upgrade": {"upgrade": 1.0, "general": 0.5}
        }
        
        return relevance_map.get(insight_type, {}).get(task_type, 0.5)
    
    def _assess_compatibility(self, insight: dict, context: dict) -> float:
        """兼容性评估"""
        if not context:
            return 1.0
        
        applied = context.get("applied_insights", [])
        conflict_types = set()
        
        for applied_id in applied:
            if applied_id in self.insights["insights"]:
                conflict_types.add(self.insights["insights"][applied_id]["insight_type"])
        
        if insight["insight_type"] in conflict_types and insight["insight_type"] == "architecture_upgrade":
            return 0.3
        
        return 1.0
    
    def _assess_resource_efficiency(self, insight: dict, context: dict) -> float:
        """资源效率评估"""
        if not context:
            return 0.8
        
        insight_type = insight["insight_type"]
        requirements = {
            "error_correction": {"cpu": 0.1, "memory": 0.1, "time": 0.1},
            "strategy_optimization": {"cpu": 0.3, "memory": 0.2, "time": 0.2},
            "logic_improvement": {"cpu": 0.5, "memory": 0.3, "time": 0.3},
            "architecture_upgrade": {"cpu": 0.8, "memory": 0.6, "time": 0.8}
        }
        
        req = requirements.get(insight_type, {"cpu": 0.3, "memory": 0.2, "time": 0.2})
        available = context.get("available_resources", {"cpu": 1.0, "memory": 1.0, "time": 1.0})
        
        cpu_eff = min(available.get("cpu", 1.0) / req["cpu"], 1.0)
        mem_eff = min(available.get("memory", 1.0) / req["memory"], 1.0)
        time_eff = min(available.get("time", 1.0) / req["time"], 1.0)
        
        return (cpu_eff + mem_eff + time_eff) / 3.0
    
    def _assess_risk(self, insight: dict) -> float:
        """风险评估"""
        insight_type = insight["insight_type"]
        risks = {
            "error_correction": {"failure": 0.2, "side_effect": 0.1, "rollback": 0.2},
            "strategy_optimization": {"failure": 0.3, "side_effect": 0.2, "rollback": 0.3},
            "logic_improvement": {"failure": 0.5, "side_effect": 0.4, "rollback": 0.5},
            "architecture_upgrade": {"failure": 0.7, "side_effect": 0.6, "rollback": 0.8}
        }
        
        r = risks.get(insight_type, {"failure": 0.3, "side_effect": 0.2, "rollback": 0.3})
        return 1.0 - (r["failure"] * 0.4 + r["side_effect"] * 0.3 + r["rollback"] * 0.3)


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="认知架构洞察组件 - 从数学顶点输出的结构化模式中提取洞察",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 添加模式
  python3 cognitive_insight.py add-pattern --pattern '{"pattern_type": "strategy", "pattern_data": {...}}'
  
  # 生成洞察
  python3 cognitive_insight.py generate-insight --pattern-ids pattern_xxxx pattern_yyyy
  
  # 列出洞察
  python3 cognitive_insight.py list-insights
  
  # 评估适用性
  python3 cognitive_insight.py assess-applicability --insight-id insight_xxxx
  
  # 按适用性列出
  python3 cognitive_insight.py list-by-applicability --min 0.7
        """
    )
    
    parser.add_argument("--memory-dir", default="./agi_memory", help="记忆目录路径（默认: ./agi_memory）")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # add-pattern 命令
    add_pattern_parser = subparsers.add_parser("add-pattern", help="添加模式")
    add_pattern_parser.add_argument("--pattern", required=True, help="模式JSON数据")
    
    # generate-insight 命令
    generate_parser = subparsers.add_parser("generate-insight", help="生成洞察")
    generate_parser.add_argument("--pattern-ids", nargs="+", required=True, help="模式ID列表")
    
    # get-insight 命令
    get_parser = subparsers.add_parser("get-insight", help="获取洞察详情")
    get_parser.add_argument("--insight-id", required=True, help="洞察ID")
    
    # list-insights 命令
    list_parser = subparsers.add_parser("list-insights", help="列出洞察")
    list_parser.add_argument("--type", help="按类型筛选")
    list_parser.add_argument("--status", help="按状态筛选")
    list_parser.add_argument("--limit", type=int, default=100, help="返回数量限制")
    
    # validate-insight 命令
    validate_parser = subparsers.add_parser("validate-insight", help="验证洞察")
    validate_parser.add_argument("--insight-id", required=True, help="洞察ID")
    validate_parser.add_argument("--result", type=bool, required=True, help="验证结果（True/False）")
    validate_parser.add_argument("--feedback", default="", help="反馈信息")
    
    # assess-applicability 命令
    assess_parser = subparsers.add_parser("assess-applicability", help="评估适用性")
    assess_parser.add_argument("--insight-id", required=True, help="洞察ID")
    assess_parser.add_argument("--context", default="{}", help="上下文JSON数据")
    
    # list-by-applicability 命令
    list_app_parser = subparsers.add_parser("list-by-applicability", help="按适用性列出洞察")
    list_app_parser.add_argument("--min", type=float, default=0.5, help="最低适用性分数")
    list_app_parser.add_argument("--context", default="{}", help="上下文JSON数据")
    list_app_parser.add_argument("--limit", type=int, default=100, help="返回数量限制")
    
    # get-pattern-library 命令
    subparsers.add_parser("get-pattern-library", help="获取模式库")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建组件实例
    ci = CognitiveInsight(memory_dir=args.memory_dir)
    
    try:
        if args.command == "add-pattern":
            pattern = json.loads(args.pattern)
            pattern_id = ci.add_pattern(pattern)
            print(json.dumps({"success": True, "pattern_id": pattern_id}, indent=2, ensure_ascii=False))
        
        elif args.command == "generate-insight":
            insight = ci.generate_insight(args.pattern_ids)
            print(json.dumps({"success": True, "insight": insight}, indent=2, ensure_ascii=False))
        
        elif args.command == "get-insight":
            insight = ci.get_insight(args.insight_id)
            if insight:
                print(json.dumps({"success": True, "insight": insight}, indent=2, ensure_ascii=False))
            else:
                print(json.dumps({"success": False, "error": "洞察不存在"}, indent=2, ensure_ascii=False))
        
        elif args.command == "list-insights":
            insights = ci.list_insights(insight_type=args.type, status=args.status, limit=args.limit)
            print(json.dumps({"success": True, "count": len(insights), "insights": insights}, indent=2, ensure_ascii=False))
        
        elif args.command == "validate-insight":
            ci.validate_insight(args.insight_id, args.result, args.feedback)
            print(json.dumps({"success": True, "message": "验证完成"}, indent=2, ensure_ascii=False))
        
        elif args.command == "assess-applicability":
            context = json.loads(args.context) if args.context else None
            result = ci.assess_applicability(args.insight_id, context)
            print(json.dumps({"success": True, "applicability": result}, indent=2, ensure_ascii=False))
        
        elif args.command == "list-by-applicability":
            context = json.loads(args.context) if args.context else None
            insights = ci.list_insights_by_applicability(min_applicability=args.min, context=context, limit=args.limit)
            print(json.dumps({"success": True, "count": len(insights), "insights": insights}, indent=2, ensure_ascii=False))
        
        elif args.command == "get-pattern-library":
            library = ci.get_pattern_library()
            print(json.dumps({"success": True, "pattern_library": library}, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2, ensure_ascii=False))
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

