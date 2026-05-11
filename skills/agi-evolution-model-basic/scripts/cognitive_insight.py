"""
认知架构洞察组件 V2（集成概念提取扩展 - 增强版）

改进内容：
1. 集成概念提取扩展模块（TF-IDF加权、动态迁移学习、缓存优化）
2. 修正分类逻辑优先级
3. 支持概念库管理
4. 增强概念适用性评估
5. 支持用户反馈和A/B测试
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import hashlib

# 导入概念提取扩展
from concept_extraction_extension import ConceptExtractionExtension
# 导入帮助模块
from cognitive_insight_help import CognitiveInsightHelp


class CognitiveInsightV2:
    """认知架构洞察组件 V2（增强版）"""
    
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
        
        # 初始化概念提取扩展
        self.concept_extension = ConceptExtractionExtension(self)
        
        # 初始化帮助模块
        self._help_helper = CognitiveInsightHelp()
        
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
    
    def help(self) -> Dict:
        """
        获取帮助信息
        
        Returns:
            dict: 包含完整帮助信息的数据结构，包括：
                - version: 版本信息
                - author: 作者信息
                - license: 协议信息
                - description: 组件描述
                - features: 功能特性
                - api_reference: API参考
                - usage_examples: 使用示例
                - best_practices: 最佳实践
                - troubleshooting: 故障排查
                - faq: 常见问题
        """
        return self._help_helper.get_help()
    
    def print_help(self):
        """打印帮助信息到控制台"""
        self._help_helper.print_help()
    
    def _load_json(self, filepath: str, default: dict) -> dict:
        """加载JSON文件"""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    
    def _save_json(self, filepath: str, data: dict):
        """保存JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_pattern(self, pattern: dict):
        """添加模式"""
        pattern_id = pattern.get('pattern_id', '')
        if pattern_id:
            self.patterns['patterns'][pattern_id] = pattern
            self.patterns['metadata']['total_count'] = len(self.patterns['patterns'])
            self._save_json(self.patterns_file, self.patterns)
            return True
        return False
    
    def generate_insight(self, pattern_ids: List[str], context: Optional[dict] = None) -> dict:
        """
        生成洞察
        
        Args:
            pattern_ids: 模式ID列表
            context: 上下文信息
            
        Returns:
            洞察字典
        """
        if context is None:
            context = {}
        
        patterns = [self.patterns['patterns'].get(pid) for pid in pattern_ids if pid in self.patterns['patterns']]
        
        if not patterns:
            return {
                'error': 'No valid patterns found',
                'insight_type': 'error'
            }
        
        # 总结模式
        summary = self._summarize_patterns(patterns)
        
        # 分类洞察（修正优先级）
        insight_type = self._classify_insight(patterns)
        
        # 提取共性
        commonality = self._extract_commonality(patterns)
        
        # 评估革新依据
        innovation_basis = self._assess_innovation_basis(patterns)
        
        # 计算置信度
        confidence = self._calculate_confidence(patterns)
        
        # 生成洞察ID
        insight_id = self._generate_insight_id(patterns)
        
        insight = {
            'insight_id': insight_id,
            'insight_type': insight_type,
            'summary': summary,
            'commonality': commonality,
            'innovation_basis': innovation_basis,
            'confidence': confidence,
            'source_patterns': pattern_ids,
            'timestamp': datetime.now().isoformat(),
            'context': context,
            'version': '2.0'  # 标记版本
        }
        
        # 概念提取（如果是concept_abstraction类型）
        if insight_type == "concept_abstraction" and len(patterns) >= 3:
            concept_data = self.concept_extension.extract_concept(patterns)
            if concept_data:
                insight["concept"] = concept_data
                # 添加概念到库
                self.concept_extension.add_concept_to_library(insight)
            else:
                # 如果无法提取概念，回退到策略优化
                insight["insight_type"] = "strategy_optimization"
                insight["fallback_reason"] = "Concept extraction failed - insufficient data"
        
        # 评估适用性（包含概念特有评估）
        applicability = self._calculate_applicability(insight, context)
        insight['applicability'] = applicability
        
        # 存储洞察
        self.insights['insights'][insight_id] = insight
        self.insights['metadata']['total_count'] = len(self.insights['insights'])
        self._save_json(self.insights_file, self.insights)
        
        return insight
    
    def _classify_insight(self, patterns: List[dict]) -> str:
        """
        分类洞察类型（修正优先级）
        
        优先级：
        1. error_correction（错误纠正）
        2. architecture_upgrade（架构升级）
        3. concept_abstraction（概念提炼）- V2新增
        4. strategy_optimization（策略优化）
        """
        pattern_types = [p.get('pattern_type', 'strategy') for p in patterns]
        impact_scopes = [p.get('impact_scope', 'local') for p in patterns]
        
        # 提取共性
        commonality = self._extract_commonality(patterns)
        
        # 计算平均验证分数
        avg_validation = sum(p.get('validation_score', 0) for p in patterns) / len(patterns)
        
        # 判断影响范围
        impact_scope = 'global' if 'global' in impact_scopes else 'system_level' if 'system_level' in impact_scopes else 'local'
        
        # 修正后的分类逻辑
        if "error" in pattern_types:
            insight_type = "error_correction"
        elif impact_scope == "global" or impact_scope == "system_level":
            insight_type = "architecture_upgrade"
        elif commonality["diversity_score"] > 0.6 and avg_validation > 0.75:
            insight_type = "concept_abstraction"
        else:
            insight_type = "strategy_optimization"
        
        return insight_type
    
    def _summarize_patterns(self, patterns: List[dict]) -> dict:
        """总结模式"""
        descriptions = [p.get('description', '') for p in patterns]
        all_text = ' '.join(descriptions)
        
        return {
            'total_patterns': len(patterns),
            'combined_description': all_text[:200] + '...' if len(all_text) > 200 else all_text,
            'key_elements': self._extract_key_elements(descriptions)
        }
    
    def _extract_key_elements(self, descriptions: List[str]) -> List[str]:
        """提取关键元素"""
        # 简化版本：提取高频词
        all_words = ' '.join(descriptions).split()
        word_freq = {}
        
        for word in all_words:
            # 过滤掉无意义的词
            if len(word) > 1 and word not in ['的', '了', '是', '在', '和', '用']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 返回高频词
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word[0] for word in sorted_words[:5]]
    
    def _extract_commonality(self, patterns: List[dict]) -> dict:
        """提取共性"""
        pattern_types = [p.get('pattern_type', 'strategy') for p in patterns]
        sources = [p.get('source', '') for p in patterns]
        contexts = [p.get('context', {}) for p in patterns]
        
        # 计算类型一致性
        type_consistency = len(set(pattern_types)) == 1
        
        # 计算来源一致性
        source_consistency = len(set(sources)) == 1
        
        # 计算多样性得分
        all_from_same_source = len(set(sources)) == 1
        all_same_type = len(set(pattern_types)) == 1
        diversity_score = 0.0
        
        if all_from_same_source and all_same_type:
            diversity_score = 0.1  # 最低多样性
        elif all_from_same_source or all_same_type:
            diversity_score = 0.5  # 中等多样性
        else:
            diversity_score = 0.9  # 高多样性
        
        return {
            'type_consistency': type_consistency,
            'source_consistency': source_consistency,
            'diversity_score': diversity_score,
            'pattern_types': list(set(pattern_types)),
            'sources': list(set(sources))
        }
    
    def _assess_innovation_basis(self, patterns: List[dict]) -> dict:
        """评估革新依据"""
        if not patterns:
            return {'exists': False, 'priority': 0}
        
        avg_validation = sum(p.get('validation_score', 0) for p in patterns) / len(patterns)
        total_occurrences = sum(p.get('occurrence_count', 1) for p in patterns)
        
        exists = avg_validation > 0.7 and total_occurrences > 10
        
        return {
            'exists': exists,
            'description': '发现高频高置信度模式' if exists else '模式频率或置信度不足',
            'priority': avg_validation,
            'expected_impact': {
                'scope': 'global' if exists and avg_validation > 0.9 else 'local',
                'confidence': avg_validation
            }
        }
    
    def _calculate_confidence(self, patterns: List[dict]) -> float:
        """计算置信度"""
        if not patterns:
            return 0.0
        
        # 基于验证分数
        avg_validation = sum(p.get('validation_score', 0) for p in patterns) / len(patterns)
        
        # 基于样本数量
        sample_score = min(len(patterns) / 10.0, 1.0)
        
        # 加权平均
        confidence = avg_validation * 0.7 + sample_score * 0.3
        
        return min(confidence, 1.0)
    
    def _calculate_applicability(self, insight: dict, context: dict) -> dict:
        """
        计算适用性（V2增强版，包含概念特有评估）
        
        Args:
            insight: 洞察字典
            context: 上下文字典
            
        Returns:
            适用性评估字典
        """
        # 基础维度评估
        dimensions = {
            'timeliness': self._assess_timeliness(insight, context),
            'relevance': self._assess_relevance(insight, context),
            'compatibility': self._assess_compatibility(insight, context),
            'resource_efficiency': self._assess_resource_efficiency(insight, context),
            'risk': self._assess_risk(insight, context)
        }
        
        # 计算加权总分
        weighted_score = sum(
            dimensions[dim] * self.applicability_weights[dim]
            for dim in dimensions
        )
        
        # 如果是概念抽象，添加概念特有评估
        if insight.get('insight_type') == 'concept_abstraction':
            concept_score = self.concept_extension.assess_concept_specifics(insight, context)
            # 概念评分占30%，基础评分占70%
            weighted_score = weighted_score * 0.7 + concept_score * 0.3
            dimensions['concept_match'] = concept_score
        
        # 确定推荐等级
        if weighted_score >= self.apply_threshold:
            recommendation = 'apply'
        elif weighted_score >= self.wait_threshold:
            recommendation = 'wait'
        else:
            recommendation = 'reject'
        
        return {
            'score': round(weighted_score, 2),
            'dimensions': dimensions,
            'recommendation': recommendation,
            'calculated_at': datetime.now().isoformat()
        }
    
    def _assess_timeliness(self, insight: dict, context: dict) -> float:
        """评估时效性"""
        insight_time = datetime.fromisoformat(insight.get('timestamp', ''))
        current_time = datetime.now()
        
        # 洞察越新，时效性越高
        days_diff = (current_time - insight_time).days
        timeliness = max(0, 1.0 - days_diff / 365.0)  # 365天后降为0
        
        return timeliness
    
    def _assess_relevance(self, insight: dict, context: dict) -> float:
        """评估相关性"""
        # 简化版本：基于上下文关键词匹配
        context_keywords = context.get('keywords', [])
        insight_summary = insight.get('summary', {}).get('combined_description', '')
        
        if not context_keywords:
            return 0.8  # 默认中等相关性
        
        matches = sum(1 for kw in context_keywords if kw in insight_summary)
        relevance = matches / len(context_keywords) if context_keywords else 0.8
        
        return relevance
    
    def _assess_compatibility(self, insight: dict, context: dict) -> float:
        """评估兼容性"""
        # 简化版本：基于洞察类型和任务类型的兼容性
        insight_type = insight.get('insight_type', '')
        task_type = context.get('task_type', '')
        
        compatibility_matrix = {
            'strategy_optimization': {
                'optimization': 1.0,
                'general': 0.8,
                'error_fix': 0.6
            },
            'architecture_upgrade': {
                'system_design': 1.0,
                'optimization': 0.7,
                'general': 0.5
            },
            'error_correction': {
                'error_fix': 1.0,
                'debugging': 0.9,
                'general': 0.7
            },
            'concept_abstraction': {
                'knowledge_transfer': 1.0,
                'generalization': 0.9,
                'general': 0.8
            }
        }
        
        return compatibility_matrix.get(insight_type, {}).get(task_type, 0.7)
    
    def _assess_resource_efficiency(self, insight: dict, context: dict) -> float:
        """评估资源效率"""
        # 简化版本：基于洞察复杂度
        insight_type = insight.get('insight_type', '')
        
        efficiency_scores = {
            'strategy_optimization': 0.9,  # 策略优化通常效率较高
            'error_correction': 0.7,       # 错误纠正需要调试时间
            'architecture_upgrade': 0.5,   # 架构升级耗时较长
            'concept_abstraction': 0.6     # 概念提炼需要分析时间
        }
        
        return efficiency_scores.get(insight_type, 0.7)
    
    def _assess_risk(self, insight: dict, context: dict) -> float:
        """评估风险（得分越高风险越低）"""
        # 简化版本：基于洞察类型和置信度
        insight_type = insight.get('insight_type', '')
        confidence = insight.get('confidence', 0.5)
        
        # 置信度越高，风险越低
        risk_from_confidence = confidence
        
        # 洞察类型风险
        type_risks = {
            'strategy_optimization': 0.8,  # 风险较低
            'error_correction': 0.9,       # 风险最低（修复问题）
            'architecture_upgrade': 0.5,   # 风险较高
            'concept_abstraction': 0.6     # 风险中等
        }
        
        risk_from_type = type_risks.get(insight_type, 0.7)
        
        # 综合评估
        return (risk_from_confidence + risk_from_type) / 2.0
    
    def _generate_insight_id(self, patterns: List[dict]) -> str:
        """生成洞察ID"""
        pattern_ids = [p.get('pattern_id', '') for p in patterns]
        pattern_ids.sort()
        id_string = '_'.join(pattern_ids)
        hash_obj = hashlib.md5(id_string.encode())
        return f"insight_{hash_obj.hexdigest()[:12]}"
    
    def get_insight(self, insight_id: str) -> Optional[dict]:
        """获取洞察"""
        return self.insights['insights'].get(insight_id)
    
    def list_insights(self, limit: int = 10) -> List[dict]:
        """列出洞察"""
        insights = list(self.insights['insights'].values())
        insights.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return insights[:limit]
    
    def list_insights_by_type(self, insight_type: str) -> List[dict]:
        """按类型列出洞察"""
        return [
            insight for insight in self.insights['insights'].values()
            if insight.get('insight_type') == insight_type
        ]
    
    def get_concept_library(self) -> dict:
        """获取概念库"""
        return self.concept_extension.get_concept_library()
    
    def record_user_feedback(self, insight_id: str, feedback: dict) -> bool:
        """
        记录用户反馈
        
        Args:
            insight_id: 洞察ID
            feedback: 反馈字典 {'rating': 1-5, 'comment': '...', 'scenario': '...'}
        """
        insight = self.get_insight(insight_id)
        if not insight or insight.get('insight_type') != 'concept_abstraction':
            return False
        
        concept = insight.get('concept', {})
        concept_id = concept.get('concept_id', '') if concept else ''
        
        if not concept_id:
            # 尝试从洞察生成concept_id
            concept_str = json.dumps(concept, sort_keys=True) if concept else ''
            if concept_str:
                concept_hash = hashlib.md5(concept_str.encode()).hexdigest()
                concept_id = f"concept_{concept_hash[:12]}"
        
        if concept_id:
            return self.concept_extension.record_user_feedback(concept_id, feedback)
        
        return False
    
    def record_ab_test_result(self, insight_id: str, ab_test: dict) -> bool:
        """
        记录A/B测试结果
        
        Args:
            insight_id: 洞察ID
            ab_test: 测试字典 {'variant': 'A/B', 'metric': '...', 'value': float, 'winner': 'A/B'}
        """
        insight = self.get_insight(insight_id)
        if not insight or insight.get('insight_type') != 'concept_abstraction':
            return False
        
        concept = insight.get('concept', {})
        concept_id = concept.get('concept_id', '') if concept else ''
        
        if not concept_id:
            concept_str = json.dumps(concept, sort_keys=True) if concept else ''
            if concept_str:
                concept_hash = hashlib.md5(concept_str.encode()).hexdigest()
                concept_id = f"concept_{concept_hash[:12]}"
        
        if concept_id:
            return self.concept_extension.record_ab_test_result(concept_id, ab_test)
        
        return False
    
    def record_migration_result(self, from_domain: str, to_domain: str, success: bool):
        """
        记录迁移结果
        
        Args:
            from_domain: 源领域
            to_domain: 目标领域
            success: 是否成功
        """
        self.concept_extension.record_migration_result(from_domain, to_domain, success)
    
    def get_system_stats(self) -> dict:
        """获取系统统计信息"""
        return {
            'patterns_count': self.patterns['metadata']['total_count'],
            'insights_count': self.insights['metadata']['total_count'],
            'concept_library': self.concept_extension.get_concept_library(),
            'cache_stats': self.concept_extension.get_cache_stats(),
            'learning_stats': self.concept_extension.get_learning_stats(),
            'version': '2.0'
        }


# 便捷函数
def create_cognitive_insight_v2(memory_dir: str = "./agi_memory") -> CognitiveInsightV2:
    """
    创建认知架构洞察组件 V2 实例
    
    Args:
        memory_dir: 记忆目录
        
    Returns:
        认知架构洞察组件 V2 实例
    """
    return CognitiveInsightV2(memory_dir)
