"""
概念提取扩展模块（增强版）
为认知架构洞察组件新增概念提取能力

改进内容：
1. TF-IDF 加权的概念提取算法
2. 动态迁移路径学习机制
3. 增强的验证机制（用户反馈 + A/B测试）
4. 性能优化（索引 + 增量更新 + LRU缓存）

功能：
1. 概念提取：从模式中抽象出概念
2. 概念库管理：存储和管理概念
3. 概念评估：评估概念的适用性
4. 迁移学习：基于历史数据优化迁移路径
"""

import json
import os
import math
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib
from collections import defaultdict, OrderedDict


class TFIDFCalculator:
    """TF-IDF 计算器"""
    
    def __init__(self):
        self.documents = []
        self.vocab = set()
        self.idf_cache = {}
    
    def add_document(self, doc: str):
        """添加文档"""
        words = self._tokenize(doc)
        self.documents.append(words)
        self.vocab.update(words)
        # 清除IDF缓存
        self.idf_cache = {}
    
    def _tokenize(self, text: str) -> List[str]:
        """分词（简化版）"""
        words = []
        for word in text.split():
            word = word.strip('，。！？；：""''（）【】《》')
            if len(word) > 1 and word not in ['的', '了', '是', '在', '和', '用', '有', '个', '这']:
                words.append(word)
        return words
    
    def calculate_tfidf(self, text: str) -> Dict[str, float]:
        """计算文本的 TF-IDF"""
        words = self._tokenize(text)
        
        # 计算词频 (TF)
        tf = {}
        for word in words:
            tf[word] = tf.get(word, 0) + 1
        total_words = len(words)
        tf = {k: v / total_words for k, v in tf.items()}
        
        # 计算逆文档频率 (IDF)
        idf = {}
        for word in tf.keys():
            if word in self.idf_cache:
                idf[word] = self.idf_cache[word]
            else:
                doc_count = sum(1 for doc in self.documents if word in doc)
                idf[word] = math.log(len(self.documents) / (doc_count + 1)) if doc_count > 0 else 0
                self.idf_cache[word] = idf[word]
        
        # 计算 TF-IDF
        tfidf = {}
        for word in tf.keys():
            tfidf[word] = tf[word] * idf[word]
        
        return tfidf
    
    def extract_keywords(self, text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """提取关键词（按TF-IDF排序）"""
        tfidf = self.calculate_tfidf(text)
        sorted_keywords = sorted(tfidf.items(), key=lambda x: x[1], reverse=True)
        return sorted_keywords[:top_k]


class ConceptCache:
    """概念LRU缓存"""
    
    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[dict]:
        """获取缓存"""
        if key in self.cache:
            self.hits += 1
            # 移到最后（最近使用）
            self.cache.move_to_end(key)
            return self.cache[key]
        self.misses += 1
        return None
    
    def put(self, key: str, value: dict):
        """放入缓存"""
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.max_size:
                # 移除最久未使用的
                self.cache.popitem(last=False)
        self.cache[key] = value
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate
        }


class MigrationPathLearner:
    """迁移路径学习器"""
    
    def __init__(self):
        self.migration_history = {}  # {(from_domain, to_domain): {'success': int, 'failure': int}}
        self.domain_map = {
            '代码生成': ['数据分析', '自动化测试', '系统设计', '性能优化'],
            '问题解决': ['决策支持', '风险控制', '资源优化', '故障排查'],
            '用户交互': ['产品设计', '体验优化', '需求分析', '用户研究'],
            '架构设计': ['系统架构', '技术选型', '性能优化', '安全设计'],
            '数据分析': ['机器学习', '商业智能', '数据可视化', '预测分析'],
            '通用': ['代码生成', '问题解决', '用户交互', '架构设计', '数据分析']
        }
    
    def record_migration(self, from_domain: str, to_domain: str, success: bool):
        """记录迁移结果"""
        key = (from_domain, to_domain)
        if key not in self.migration_history:
            self.migration_history[key] = {'success': 0, 'failure': 0, 'confidence': 0.7}
        
        if success:
            self.migration_history[key]['success'] += 1
        else:
            self.migration_history[key]['failure'] += 1
        
        # 重新计算置信度
        total = self.migration_history[key]['success'] + self.migration_history[key]['failure']
        if total > 0:
            success_rate = self.migration_history[key]['success'] / total
            # 指数加权移动平均
            old_confidence = self.migration_history[key]['confidence']
            self.migration_history[key]['confidence'] = 0.7 * old_confidence + 0.3 * success_rate
    
    def get_migration_paths(self, from_domain: str) -> List[dict]:
        """获取迁移路径（基于学习优化）"""
        paths = []
        
        if from_domain in self.domain_map:
            for to_target in self.domain_map[from_domain]:
                key = (from_domain, to_target)
                
                if key in self.migration_history:
                    # 使用学习到的置信度
                    confidence = self.migration_history[key]['confidence']
                    total_attempts = self.migration_history[key]['success'] + self.migration_history[key]['failure']
                else:
                    # 使用默认置信度
                    confidence = 0.7
                    total_attempts = 0
                
                paths.append({
                    'from': from_domain,
                    'to_targets': to_target,
                    'confidence': confidence,
                    'total_attempts': total_attempts,
                    'is_learned': key in self.migration_history
                })
        
        # 按置信度排序
        paths.sort(key=lambda x: x['confidence'], reverse=True)
        
        return paths
    
    def get_learning_stats(self) -> dict:
        """获取学习统计"""
        total_pairs = len(self.migration_history)
        successful_pairs = sum(1 for v in self.migration_history.values() 
                               if v['success'] > v['failure'])
        
        return {
            'total_migration_pairs': total_pairs,
            'successful_pairs': successful_pairs,
            'success_rate': successful_pairs / total_pairs if total_pairs > 0 else 0,
            'total_migrations': sum(v['success'] + v['failure'] for v in self.migration_history.values())
        }


class ConceptExtractionExtension:
    """概念提取扩展类（增强版）"""
    
    def __init__(self, cognitive_insight):
        """
        初始化概念提取扩展
        
        Args:
            cognitive_insight: 认知架构洞察组件实例
        """
        self.ci = cognitive_insight
        self.concept_library_file = os.path.join(
            self.ci.cognitive_insight_dir, 
            "concept_library.json"
        )
        
        # 初始化概念库
        self.concept_library = self._load_concept_library()
        
        # 初始化 TF-IDF 计算器
        self.tfidf_calculator = TFIDFCalculator()
        
        # 初始化缓存
        self.concept_cache = ConceptCache(max_size=100)
        
        # 初始化迁移路径学习器
        self.migration_learner = MigrationPathLearner()
        
        # 从概念库加载迁移历史
        self._load_migration_history()
    
    def _load_concept_library(self) -> dict:
        """加载概念库"""
        if os.path.exists(self.concept_library_file):
            with open(self.concept_library_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 确保有迁移历史字段
                if 'migration_history' not in data:
                    data['migration_history'] = {}
                return data
        
        return {
            "concepts": [],
            "principles": [],
            "migration_history": {},
            "metadata": {
                "total_count": 0,
                "last_updated": datetime.now().isoformat(),
                "version": "2.0"
            }
        }
    
    def _load_migration_history(self):
        """加载迁移历史"""
        if 'migration_history' in self.concept_library:
            self.migration_learner.migration_history = self.concept_library['migration_history']
    
    def _save_concept_library(self):
        """保存概念库"""
        self.concept_library["metadata"]["last_updated"] = datetime.now().isoformat()
        self.concept_library["metadata"]["total_count"] = len(self.concept_library["concepts"])
        self.concept_library["migration_history"] = self.migration_learner.migration_history
        
        with open(self.concept_library_file, 'w', encoding='utf-8') as f:
            json.dump(self.concept_library, f, ensure_ascii=False, indent=2)
    
    def extract_concept(self, patterns: List[dict]) -> Optional[dict]:
        """
        从一组模式中提取概念（增强版，使用TF-IDF）
        实现四层抽象：Pattern -> Rule -> Concept -> Principle
        
        Args:
            patterns: 模式列表
            
        Returns:
            概念数据字典，如果无法提取则返回None
        """
        if len(patterns) < 3:
            return None
        
        # 1. 使用 TF-IDF 提取共同语义特征
        all_descriptions = [p.get('description', '') for p in patterns]
        
        # 添加文档到 TF-IDF 计算器
        for desc in all_descriptions:
            self.tfidf_calculator.add_document(desc)
        
        # 提取关键词
        common_features = self._extract_common_features_enhanced(all_descriptions)
        
        # 2. 识别抽象层级
        abstraction_level = self._identify_abstraction_level(patterns)
        
        # 3. 生成概念定义
        concept_name = common_features.get('name', '未命名概念')
        concept_definition = common_features.get('definition', '')
        
        # 4. 识别适用边界
        boundaries = self._identify_applicable_boundaries(patterns)
        
        # 5. 识别迁移路径（使用学习器）
        migration_paths = self._identify_migration_paths_learned(patterns)
        
        # 6. 计算置信度（增强版）
        confidence = self._calculate_concept_confidence_enhanced(patterns)
        
        return {
            'concept_name': concept_name,
            'definition': concept_definition,
            'abstraction_level': abstraction_level,
            'applicable_domains': boundaries.get('domains', []),
            'boundary_conditions': boundaries.get('conditions', []),
            'migration_paths': migration_paths,
            'confidence': confidence,
            'source_patterns': [p.get('pattern_id', '') for p in patterns],
            'created_at': datetime.now().isoformat(),
            'extraction_method': 'tfidf'  # 标记使用的方法
        }
    
    def _extract_common_features_enhanced(self, descriptions: List[str]) -> dict:
        """
        提取描述中的共同语义特征（增强版，使用TF-IDF）
        
        Args:
            descriptions: 描述列表
            
        Returns:
            共同特征字典
        """
        # 合并所有描述
        combined_text = ' '.join(descriptions)
        
        # 使用 TF-IDF 提取关键词
        keywords = self.tfidf_calculator.extract_keywords(combined_text, top_k=5)
        
        if keywords:
            concept_name = f"{keywords[0][0]}原则"
            concept_definition = ' '.join([kw[0] for kw in keywords])
            common_features = [{'word': kw[0], 'score': kw[1]} for kw in keywords]
        else:
            concept_name = '未命名概念'
            concept_definition = '无法提取特征'
            common_features = []
        
        return {
            'name': concept_name,
            'definition': concept_definition,
            'common_features': common_features
        }
    
    def _identify_abstraction_level(self, patterns: List[dict]) -> str:
        """
        识别抽象层级
        - rule: 具体行为规则
        - concept: 领域概念
        - principle: 通用原理
        
        Args:
            patterns: 模式列表
            
        Returns:
            抽象层级字符串
        """
        # 检测模式的跨领域性
        domains = set(p.get('domain', '') for p in patterns)
        cross_domain = len(domains) > 1
        
        # 检测模式的泛化程度
        generic_terms = ['原则', '规则', '方法', '策略', '模式', '范式', '框架']
        has_generic_terms = any(
            any(term in p.get('description', '') for term in generic_terms)
            for p in patterns
        )
        
        # 检测高阶术语
        high_order_terms = ['本质', '核心', '根本', '基础', '通用', '普适']
        has_high_order_terms = any(
            any(term in p.get('description', '') for term in high_order_terms)
            for p in patterns
        )
        
        if cross_domain and (has_generic_terms or has_high_order_terms):
            return 'principle'
        elif cross_domain:
            return 'concept'
        else:
            return 'rule'
    
    def _identify_applicable_boundaries(self, patterns: List[dict]) -> dict:
        """
        识别概念适用的边界条件
        
        Args:
            patterns: 模式列表
            
        Returns:
            边界条件字典
        """
        domains = list(set(p.get('domain', '通用') for p in patterns))
        
        # 提取条件词
        conditions = []
        condition_keywords = ['当', '如果', '只有在', '只有在', '需要', '在...情况下', '基于']
        
        for p in patterns:
            desc = p.get('description', '')
            if any(keyword in desc for keyword in condition_keywords):
                conditions.append(desc)
        
        return {
            'domains': domains,
            'conditions': list(set(conditions))[:3]  # 最多保留3个条件
        }
    
    def _identify_migration_paths_learned(self, patterns: List[dict]) -> List[dict]:
        """
        识别概念的迁移路径（使用学习器）
        
        Args:
            patterns: 模式列表
            
        Returns:
            迁移路径列表
        """
        domains = set(p.get('domain', '通用') for p in patterns)
        
        all_paths = []
        for domain in domains:
            paths = self.migration_learner.get_migration_paths(domain)
            all_paths.extend(paths)
        
        return all_paths
    
    def _calculate_concept_confidence_enhanced(self, patterns: List[dict]) -> float:
        """
        计算概念的置信度（增强版）
        考虑：
        1. 验证分数的均值
        2. 多样性：不同来源的占比
        3. 样本充足性：至少需要3个模式
        4. 跨领域性：跨领域模式提高置信度
        
        Args:
            patterns: 模式列表
            
        Returns:
            置信度（0-1）
        """
        if not patterns:
            return 0.0
        
        avg_validation = sum(p.get('validation_score', 0.0) for p in patterns) / len(patterns)
        unique_sources = len(set(p.get('source', '') for p in patterns))
        total_patterns = len(patterns)
        
        # 多样性：不同来源的占比
        diversity = unique_sources / max(total_patterns, 1)
        
        # 样本充足性：至少需要3个模式才能形成概念
        sample_adequacy = min(total_patterns / 3.0, 1.0)
        
        # 跨领域性：跨领域模式提高置信度
        domains = set(p.get('domain', '') for p in patterns)
        cross_domain_bonus = 0.1 if len(domains) > 1 else 0.0
        
        # 加权计算置信度
        confidence = min(
            avg_validation * 0.45 + 
            diversity * 0.25 + 
            sample_adequacy * 0.20 +
            cross_domain_bonus,
            1.0
        )
        
        return confidence
    
    def add_concept_to_library(self, insight: dict) -> bool:
        """
        将验证后的概念添加到概念库
        
        Args:
            insight: 包含概念数据的洞察字典
            
        Returns:
            是否成功添加
        """
        if insight.get('insight_type') != 'concept_abstraction':
            return False
        
        concept = insight.get('concept')
        if not concept:
            return False
        
        # 生成概念ID
        concept_str = json.dumps(concept, sort_keys=True)
        concept_hash = hashlib.md5(concept_str.encode()).hexdigest()
        concept_id = f"concept_{concept_hash[:12]}"
        
        # 检查缓存
        cached = self.concept_cache.get(concept_id)
        if cached:
            # 更新验证计数
            cached['validation_count'] += 1
            cached['last_validated_at'] = datetime.now().isoformat()
            self._save_concept_library()
            return True
        
        # 检查是否已存在
        for existing_concept in self.concept_library['concepts']:
            if existing_concept['concept_id'] == concept_id:
                # 更新验证计数
                existing_concept['validation_count'] += 1
                existing_concept['last_validated_at'] = datetime.now().isoformat()
                # 加入缓存
                self.concept_cache.put(concept_id, existing_concept)
                self._save_concept_library()
                return True
        
        # 添加新概念
        new_concept = {
            'concept_id': concept_id,
            'source_insight_id': insight.get('insight_id', ''),
            'concept': concept,
            'validation_count': 1,
            'applicability_history': [],
            'user_feedback': [],  # 用户反馈
            'ab_test_results': [],  # A/B测试结果
            'created_at': datetime.now().isoformat(),
            'last_validated_at': datetime.now().isoformat(),
            'is_incremental': True  # 标记为增量更新
        }
        
        self.concept_library['concepts'].append(new_concept)
        
        # 如果是principle级别，也添加到principles列表
        if concept.get('abstraction_level') == 'principle':
            principle = {
                'principle_id': concept_id,
                'principle_name': concept['concept_name'],
                'definition': concept['definition'],
                'source_concept_id': concept_id
            }
            self.concept_library['principles'].append(principle)
        
        # 加入缓存
        self.concept_cache.put(concept_id, new_concept)
        
        self._save_concept_library()
        
        return True
    
    def record_user_feedback(self, concept_id: str, feedback: dict):
        """
        记录用户反馈
        
        Args:
            concept_id: 概念ID
            feedback: 反馈字典 {'rating': 1-5, 'comment': '...', 'scenario': '...'}
        """
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return False
        
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            **feedback
        }
        concept['user_feedback'].append(feedback_entry)
        
        self._save_concept_library()
        return True
    
    def record_ab_test_result(self, concept_id: str, ab_test: dict):
        """
        记录A/B测试结果
        
        Args:
            concept_id: 概念ID
            ab_test: 测试字典 {'variant': 'A/B', 'metric': '...', 'value': float, 'winner': 'A/B'}
        """
        concept = self.get_concept_by_id(concept_id)
        if not concept:
            return False
        
        test_entry = {
            'timestamp': datetime.now().isoformat(),
            **ab_test
        }
        concept['ab_test_results'].append(test_entry)
        
        self._save_concept_library()
        return True
    
    def record_migration_result(self, from_domain: str, to_domain: str, success: bool):
        """
        记录迁移结果
        
        Args:
            from_domain: 源领域
            to_domain: 目标领域
            success: 是否成功
        """
        self.migration_learner.record_migration(from_domain, to_domain, success)
        self._save_concept_library()
    
    def get_concept_library(self) -> dict:
        """
        获取概念库内容
        
        Returns:
            概念库数据字典
        """
        return self.concept_library
    
    def get_cache_stats(self) -> dict:
        """获取缓存统计"""
        return self.concept_cache.get_stats()
    
    def get_learning_stats(self) -> dict:
        """获取学习统计"""
        return self.migration_learner.get_learning_stats()
    
    def assess_concept_specifics(self, insight: dict, context: dict) -> float:
        """
        概念特有评估
        评估概念的抽象层级与任务需求的匹配度
        
        Args:
            insight: 洞察字典
            context: 上下文字典
            
        Returns:
            匹配度得分（0-1）
        """
        if insight.get('insight_type') != 'concept_abstraction':
            return 1.0
        
        concept = insight.get('concept', {})
        if not concept:
            return 1.0
        
        abstraction_level = concept.get('abstraction_level', 'rule')
        task_abstraction_requirement = context.get('abstraction_requirement', 'concept')
        
        # 抽象层级匹配度矩阵
        level_match = {
            'principle': {
                'principle': 1.0,
                'concept': 0.8,
                'rule': 0.6
            },
            'concept': {
                'principle': 0.7,
                'concept': 1.0,
                'rule': 0.8
            },
            'rule': {
                'principle': 0.5,
                'concept': 0.7,
                'rule': 1.0
            }
        }
        
        match_score = level_match.get(abstraction_level, {}).get(task_abstraction_requirement, 0.5)
        
        # 验证历史评分
        validation_score = min(concept.get('confidence', 0.0), 1.0)
        
        # 加权计算
        return match_score * 0.7 + validation_score * 0.3
    
    def list_concepts_by_level(self, level: str) -> List[dict]:
        """
        按抽象层级列出概念
        
        Args:
            level: 抽象层级（rule/concept/principle）
            
        Returns:
            概念列表
        """
        concepts = []
        for item in self.concept_library['concepts']:
            if item['concept'].get('abstraction_level') == level:
                concepts.append(item)
        
        return concepts
    
    def get_concept_by_id(self, concept_id: str) -> Optional[dict]:
        """
        根据ID获取概念（使用缓存）
        
        Args:
            concept_id: 概念ID
            
        Returns:
            概念数据字典，如果不存在则返回None
        """
        # 先查缓存
        cached = self.concept_cache.get(concept_id)
        if cached:
            return cached
        
        # 查数据库
        for item in self.concept_library['concepts']:
            if item['concept_id'] == concept_id:
                # 加入缓存
                self.concept_cache.put(concept_id, item)
                return item
        
        return None
    
    def validate_concept(self, concept_id: str, validation_result: bool) -> bool:
        """
        验证概念并更新验证历史
        
        Args:
            concept_id: 概念ID
            validation_result: 验证结果（True/False）
            
        Returns:
            是否成功更新
        """
        concept_item = self.get_concept_by_id(concept_id)
        if not concept_item:
            return False
        
        # 添加验证历史
        validation_entry = {
            'timestamp': datetime.now().isoformat(),
            'result': validation_result
        }
        concept_item['applicability_history'].append(validation_entry)
        concept_item['last_validated_at'] = datetime.now().isoformat()
        
        # 如果验证成功，增加验证计数
        if validation_result:
            concept_item['validation_count'] += 1
        
        self._save_concept_library()
        
        return True


# 便捷函数
def create_concept_extension(cognitive_insight) -> ConceptExtractionExtension:
    """
    创建概念提取扩展实例
    
    Args:
        cognitive_insight: 认知架构洞察组件实例
        
    Returns:
        概念提取扩展实例
    """
    return ConceptExtractionExtension(cognitive_insight)
