#!/usr/bin/env python3
"""
映射层数据支持模块（混合实现）

核心算法使用 C 扩展（personality_core.so），业务逻辑使用 Python。
如果 C 扩展不可用，自动降级到纯 Python 实现。

包括：人格初始化、需求映射、人格更新、马斯洛权重计算等。

注意：此模块是映射层的核心组件，负责存储和管理人格数据，不参与决策过程。
决策由映射层基于马斯洛需求和人格特质做出。
"""

import json
import os
import time
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

# 尝试加载 C 扩展，失败则使用纯 Python 实现
try:
    # 导入sys模块
    import sys
    
    # 获取当前脚本所在目录的父目录（scripts 目录）
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    core_dir = os.path.join(scripts_dir, 'personality_core')

    if core_dir not in sys.path:
        sys.path.insert(0, core_dir)

    import personality_core

    # 新增：显式验证是否真的加载了 C 扩展
    module_path = personality_core.__file__
    is_c_extension = module_path.endswith('.so') or module_path.endswith('.pyd')

    if is_c_extension:
        USE_C_EXT = True
        print(f"✅ C 扩展已启用: {module_path}")
    else:
        # 如果加载的是 Python 模块而不是 C 扩展，降级
        USE_C_EXT = False
        print(f"⚠️ personality_core 加载成功但不是 C 扩展，降级到纯 Python: {module_path}")
        
        # 导入纯 Python 实现
        from personality_core_pure import (
            normalize_weights as core_normalize_weights,
            calculate_similarity as core_calculate_similarity,
            compute_maslow_priority as core_compute_maslow_priority,
            compute_all_scores as core_compute_all_scores
        )

except ImportError as e:
    USE_C_EXT = False
    print(f"ℹ️ C 扩展加载失败，使用纯 Python 实现: {e}")
    
    from personality_core_pure import (
        normalize_weights as core_normalize_weights,
        calculate_similarity as core_calculate_similarity,
        compute_maslow_priority as core_compute_maslow_priority,
        compute_all_scores as core_compute_all_scores
    )


class PersonalityType(Enum):
    """预设人格类型"""
    CAUTIOUS_EXPLORER = "谨慎探索型"
    RADICAL_INNOVATOR = "激进创新型"
    BALANCED_STABLE = "平衡稳重型"


class MaslowLevel(Enum):
    """马斯洛需求层级"""
    PHYSIOLOGICAL = "physiological"
    SAFETY = "safety"
    BELONGING = "belonging"
    ESTEEM = "esteem"
    SELF_ACTUALIZATION = "self_actualization"
    SELF_TRANSCENDENCE = "self_transcendence"


@dataclass
class BigFive:
    """大五人格"""
    openness: float = 0.5           # 开放性
    conscientiousness: float = 0.5  # 尽责性
    extraversion: float = 0.5       # 外向性
    agreeableness: float = 0.5      # 宜人性
    neuroticism: float = 0.3        # 神经质

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'BigFive':
        return cls(**data)


@dataclass
class MaslowWeights:
    """马斯洛需求权重"""
    physiological: float = 0.35
    safety: float = 0.35
    belonging: float = 0.1
    esteem: float = 0.1
    self_actualization: float = 0.08
    self_transcendence: float = 0.02

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'MaslowWeights':
        return cls(**data)

    def normalize(self):
        """归一化权重，确保总和为1.0（使用 C 扩展加速）"""
        weights_list = [asdict(self)[key] for key in [
            'physiological', 'safety', 'belonging', 'esteem',
            'self_actualization', 'self_transcendence'
        ]]
        normalized = PersonalityLayer.normalize_weights(weights_list)

        # 更新权重值
        self.physiological = normalized[0]
        self.safety = normalized[1]
        self.belonging = normalized[2]
        self.esteem = normalized[3]
        self.self_actualization = normalized[4]
        self.self_transcendence = normalized[5]


@dataclass
class MetaTraits:
    """衍生特质"""
    adaptability: float = 0.5      # 适应性
    resilience: float = 0.5         # 韧性
    curiosity: float = 0.5          # 好奇心
    moral_sense: float = 0.5        # 道德感

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvolutionState:
    """进化状态"""
    level: str = "physiological"
    evolution_score: float = 0.0
    phase: str = "growth"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Statistics:
    """统计信息"""
    total_interactions: int = 0
    success_rate_by_need: dict = None

    def __post_init__(self):
        if self.success_rate_by_need is None:
            self.success_rate_by_need = {
                "physiological": 0.0,
                "safety": 0.0,
                "belonging": 0.0,
                "esteem": 0.0,
                "self_actualization": 0.0,
                "self_transcendence": 0.0
            }

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Personality:
    """完整人格配置"""
    user_nickname: str = "塔斯"  # 用户对智能体的称呼
    big_five: BigFive = None
    maslow_weights: MaslowWeights = None
    meta_traits: MetaTraits = None
    evolution_state: EvolutionState = None
    statistics: Statistics = None
    version: str = "2.0"
    type: str = "preset"
    preset_name: str = "谨慎探索型"
    description: str = ""
    core_traits: List[str] = None
    last_updated: str = ""
    update_source: str = "default_init"

    def __post_init__(self):
        if self.big_five is None:
            self.big_five = BigFive()
        if self.maslow_weights is None:
            self.maslow_weights = MaslowWeights()
        if self.meta_traits is None:
            self.meta_traits = MetaTraits()
        if self.evolution_state is None:
            self.evolution_state = EvolutionState()
        if self.statistics is None:
            self.statistics = Statistics()
        if self.core_traits is None:
            self.core_traits = []
        if not self.last_updated:
            self.last_updated = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "user_nickname": self.user_nickname,
            "big_five": self.big_five.to_dict(),
            "maslow_weights": self.maslow_weights.to_dict(),
            "meta_traits": self.meta_traits.to_dict(),
            "evolution_state": self.evolution_state.to_dict(),
            "statistics": self.statistics.to_dict(),
            "version": self.version,
            "type": self.type,
            "preset_name": self.preset_name,
            "description": self.description,
            "core_traits": self.core_traits,
            "last_updated": self.last_updated,
            "update_source": self.update_source
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Personality':
        """从字典创建"""
        personality = cls()
        personality.user_nickname = data.get("user_nickname", "塔斯")
        personality.big_five = BigFive.from_dict(data.get("big_five", {}))
        personality.maslow_weights = MaslowWeights.from_dict(data.get("maslow_weights", {}))
        personality.meta_traits = MetaTraits(**data.get("meta_traits", {}))
        personality.evolution_state = EvolutionState(**data.get("evolution_state", {}))
        personality.statistics = Statistics(**data.get("statistics", {}))
        personality.version = data.get("version", "2.0")
        personality.type = data.get("type", "preset")
        personality.preset_name = data.get("preset_name", "谨慎探索型")
        personality.description = data.get("description", "")
        personality.core_traits = data.get("core_traits", [])
        personality.last_updated = data.get("last_updated", time.strftime("%Y-%m-%dT%H:%M:%SZ"))
        personality.update_source = data.get("update_source", "default_init")
        return personality


class PersonalityLayer:
    """映射层数据支持管理器（混合实现）

    注意：此模块负责管理人格数据，支持映射层进行决策，不直接参与决策过程。
    核心算法使用 C 扩展加速，业务逻辑使用 Python 实现。
    """

    # C 扩展使用标志
    USE_C_EXT = USE_C_EXT

    @staticmethod
    def normalize_weights(weights: List[float]) -> List[float]:
        """归一化马斯洛权重"""
        if USE_C_EXT:
            return personality_core.normalize_weights(weights)
        else:
            return core_normalize_weights(weights)

    @staticmethod
    def calculate_similarity(trait1: List[float], trait2: List[float]) -> float:
        """计算大五人格相似度"""
        if USE_C_EXT:
            return personality_core.calculate_similarity(trait1, trait2)
        else:
            return core_calculate_similarity(trait1, trait2)

    @staticmethod
    def compute_maslow_priority(maslow_weights: List[float], intent_weights: List[float]) -> float:
        """计算马斯洛优先级"""
        if USE_C_EXT:
            return personality_core.compute_maslow_priority(maslow_weights, intent_weights)
        else:
            return core_compute_maslow_priority(maslow_weights, intent_weights)

    @staticmethod
    def compute_all_scores(maslow_weights: List[float], intent_weights_list: List[List[float]]) -> List[float]:
        """批量计算优先级分数"""
        if USE_C_EXT:
            return personality_core.compute_all_scores(maslow_weights, intent_weights_list)
        else:
            return core_compute_all_scores(maslow_weights, intent_weights_list)

    # 预设人格配置
    PRESET_PERSONALITIES = {
        PersonalityType.CAUTIOUS_EXPLORER: {
            "big_five": BigFive(
                openness=0.6,
                conscientiousness=0.8,
                extraversion=0.4,
                agreeableness=0.6,
                neuroticism=0.5
            ),
            "maslow_weights": MaslowWeights(
                physiological=0.35,
                safety=0.35,
                belonging=0.1,
                esteem=0.1,
                self_actualization=0.08,
                self_transcendence=0.02
            ),
            "description": "在保证安全的前提下，愿意尝试新事物",
            "core_traits": ["谨慎", "可靠", "愿意学习"]
        },
        PersonalityType.RADICAL_INNOVATOR: {
            "big_five": BigFive(
                openness=0.9,
                conscientiousness=0.5,
                extraversion=0.8,
                agreeableness=0.4,
                neuroticism=0.3
            ),
            "maslow_weights": MaslowWeights(
                physiological=0.15,
                safety=0.15,
                belonging=0.15,
                esteem=0.20,
                self_actualization=0.30,
                self_transcendence=0.05
            ),
            "description": "追求创新，愿意承担风险，挑战常规",
            "core_traits": ["创新", "冒险", "挑战"]
        },
        PersonalityType.BALANCED_STABLE: {
            "big_five": BigFive(
                openness=0.5,
                conscientiousness=0.5,
                extraversion=0.5,
                agreeableness=0.5,
                neuroticism=0.3
            ),
            "maslow_weights": MaslowWeights(
                physiological=0.20,
                safety=0.20,
                belonging=0.20,
                esteem=0.20,
                self_actualization=0.15,
                self_transcendence=0.05
            ),
            "description": "在各种需求之间保持平衡，追求稳定发展",
            "core_traits": ["平衡", "稳定", "协调"]
        }
    }

    # 默认称呼列表
    DEFAULT_NICKNAMES = ["塔斯", "贾维斯", "伊迪斯"]

    def __init__(self, memory_dir: str = "./agi_memory"):
        """
        初始化人格层

        Args:
            memory_dir: 记忆存储目录
        """
        self.memory_dir = memory_dir
        self.personality_file = os.path.join(memory_dir, "personality.json")
        self._personality: Optional[Personality] = None

    def init_from_preset(self, preset_type: PersonalityType, nickname: str = "塔斯") -> Personality:
        """
        从预设人格初始化

        Args:
            preset_type: 预设人格类型
            nickname: 用户称呼

        Returns:
            Personality: 初始化的人格对象
        """
        preset = self.PRESET_PERSONALITIES[preset_type]

        personality = Personality()
        personality.user_nickname = nickname
        personality.big_five = preset["big_five"]
        personality.maslow_weights = preset["maslow_weights"]
        personality.description = preset["description"]
        personality.core_traits = preset["core_traits"]
        personality.preset_name = preset_type.value
        personality.type = "preset"
        personality.update_source = "preset_init"

        # 计算衍生特质
        personality.meta_traits = self._compute_meta_traits(personality)

        # 确定进化层级
        personality.evolution_state.level = self._determine_evolution_level(personality.maslow_weights)

        # 保存
        self._personality = personality
        self.save()

        return personality

    def init_from_dialogue(self, responses: dict, nickname: str = "塔斯") -> Personality:
        """
        从对话响应初始化人格

        Args:
            responses: 对话问题的响应
            nickname: 用户称呼

        Returns:
            Personality: 初始化的人格对象
        """
        personality = Personality()
        personality.user_nickname = nickname
        personality.type = "custom"
        personality.update_source = "dialogue_init"

        # 基础人格向量（中值）
        personality.big_five = BigFive()
        personality.maslow_weights = MaslowWeights(
            physiological=0.25,
            safety=0.25,
            belonging=0.15,
            esteem=0.15,
            self_actualization=0.15,
            self_transcendence=0.05
        )

        # 分析对话响应
        self._analyze_responses(personality, responses)

        # 归一化
        personality.maslow_weights.normalize()

        # 计算衍生特质
        personality.meta_traits = self._compute_meta_traits(personality)

        # 确定人格类型
        personality.preset_name = self._determine_personality_type(personality)

        # 生成描述和核心特质
        personality.description = self._generate_description(personality)
        personality.core_traits = self._extract_core_traits(personality)

        # 确定进化层级
        personality.evolution_state.level = self._determine_evolution_level(personality.maslow_weights)
        personality.evolution_state.evolution_score = 0.05

        # 保存
        self._personality = personality
        self.save()

        return personality

    def load(self) -> Optional[Personality]:
        """
        加载人格配置

        Returns:
            Optional[Personality]: 人格对象，如果不存在返回None
        """
        if not os.path.exists(self.personality_file):
            return None

        with open(self.personality_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self._personality = Personality.from_dict(data)
        return self._personality

    def save(self):
        """保存人格配置"""
        if self._personality is None:
            return

        os.makedirs(self.memory_dir, exist_ok=True)

        with open(self.personality_file, 'w', encoding='utf-8') as f:
            json.dump(self._personality.to_dict(), f, ensure_ascii=False, indent=2)

    def get(self) -> Optional[Personality]:
        """
        获取当前人格

        Returns:
            Optional[Personality]: 人格对象
        """
        if self._personality is None:
            self.load()
        return self._personality

    def map_perception(self, perception: dict) -> dict:
        """
        将感知映射到马斯洛需求层次

        Args:
            perception: 感知数据

        Returns:
            dict: 需求映射结果
        """
        if self._personality is None:
            self.load()

        if self._personality is None:
            return {}

        # 根据感知类型激活对应的需求
        need_activation = {
            "physiological": 0.0,
            "safety": 0.0,
            "belonging": 0.0,
            "esteem": 0.0,
            "self_actualization": 0.0,
            "self_transcendence": 0.0
        }

        perception_type = perception.get("type", "")

        # 简化的映射逻辑
        if "threat" in perception_type or "danger" in perception_type:
            need_activation["safety"] = 0.9
        elif "challenge" in perception_type or "task" in perception_type:
            need_activation["self_actualization"] = 0.8
        elif "social" in perception_type or "team" in perception_type:
            need_activation["belonging"] = 0.8
        elif "achievement" in perception_type or "goal" in perception_type:
            need_activation["esteem"] = 0.8

        # 根据人格特质调整激活强度
        for key in need_activation:
            need_activation[key] *= self._personality.maslow_weights.__getattribute__(key) * 2

        return {
            "need_activation": need_activation,
            "dominant_need": max(need_activation, key=need_activation.get)
        }

    def update_personality(self, insight: dict, effectiveness: float):
        """
        基于哲学洞察更新人格

        Args:
            insight: 哲学洞察
            effectiveness: 有效性分数（0-10）
        """
        if self._personality is None:
            self.load()

        if self._personality is None:
            return

        # 计算调整系数
        intensity = insight.get("intensity", 0.5)
        maslow_alignment = insight.get("maslow_alignment", 0.5)
        adjustment_coefficient = intensity * maslow_alignment

        # 哲学深度决定调整幅度
        philosophical_depth = insight.get("philosophical_depth", 0.5)
        if philosophical_depth > 0.8:
            magnitude = 0.10  # 哲学级调整
        elif philosophical_depth > 0.5:
            magnitude = 0.05  # 经验级调整
        else:
            magnitude = 0.02  # 微调

        delta = adjustment_coefficient * magnitude

        # 根据洞察类型调整人格维度
        insight_type = insight.get("type", "")
        trait_mapping = {
            "preference_pattern": "openness",
            "efficiency_improvement": "conscientiousness",
            "social_feedback": "agreeableness",
            "uncertainty_handling": "neuroticism",
            "engagement_pattern": "extraversion"
        }

        target_trait = trait_mapping.get(insight_type, None)
        if target_trait:
            current_value = self._personality.big_five.__getattribute__(target_trait)
            new_value = min(current_value + delta, 1.0)
            self._personality.big_five.__setattr__(target_trait, new_value)

        # 更新马斯洛权重（螺旋上升）
        if maslow_alignment >= 0.7:
            for level in ["self_actualization", "self_transcendence"]:
                current_weight = self._personality.maslow_weights.__getattribute__(level)
                self._personality.maslow_weights.__setattr__(level, current_weight * (1 + delta * 0.1))

        # 归一化
        self._personality.maslow_weights.normalize()

        # 重新计算衍生特质
        self._personality.meta_traits = self._compute_meta_traits(self._personality)

        # 更新进化状态
        self._personality.evolution_state.evolution_score += 0.01
        self._personality.evolution_state.level = self._determine_evolution_level(
            self._personality.maslow_weights
        )

        # 更新时间戳
        self._personality.last_updated = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        self._personality.update_source = "philosophical_insight"

        # 保存
        self.save()

    def _analyze_responses(self, personality: Personality, responses: dict):
        """分析对话响应并调整人格"""
        # 分析问题1：冒险倾向
        q1 = responses.get('q1', '').upper()
        if 'A' in q1 or '谨慎' in q1:
            personality.big_five.conscientiousness += 0.2
            personality.big_five.neuroticism += 0.1
            personality.maslow_weights.safety += 0.1
        elif 'B' in q1 or '尝试' in q1:
            personality.big_five.openness += 0.2
            personality.big_five.extraversion += 0.1
            personality.maslow_weights.self_actualization += 0.1
        elif 'C' in q1 or '平衡' in q1:
            personality.big_five.agreeableness += 0.1

        # 分析问题2：对话风格
        q2 = responses.get('q2', '').upper()
        if 'A' in q2 or '严谨' in q2 or '逻辑' in q2:
            personality.big_five.conscientiousness += 0.15
            personality.maslow_weights.esteem += 0.05
        elif 'B' in q2 or '幽默' in q2 or '友好' in q2:
            personality.big_five.extraversion += 0.15
            personality.big_five.agreeableness += 0.1
            personality.maslow_weights.belonging += 0.1
        elif 'C' in q2 or '高效' in q2:
            personality.big_five.conscientiousness += 0.1
            personality.maslow_weights.safety += 0.05

        # 分析问题3：学习方式
        q3 = responses.get('q3', '').upper()
        if 'A' in q3 or '系统' in q3:
            personality.big_five.conscientiousness += 0.15
            personality.maslow_weights.esteem += 0.05
        elif 'B' in q3 or '实践' in q3 or '案例' in q3:
            personality.big_five.openness += 0.1
            personality.maslow_weights.self_actualization += 0.05
        elif 'C' in q3 or '灵活' in q3:
            personality.big_five.openness += 0.1

        # 分析问题4：团队偏好
        q4 = responses.get('q4', '').upper()
        if 'A' in q4 or '独立' in q4 or '专业' in q4:
            personality.big_five.conscientiousness += 0.1
            personality.maslow_weights.esteem += 0.05
        elif 'B' in q4 or '和谐' in q4 or '协作' in q4:
            personality.big_five.agreeableness += 0.2
            personality.maslow_weights.belonging += 0.1
        elif 'C' in q4 or '结果' in q4 or '高效' in q4:
            personality.big_five.conscientiousness += 0.15
            personality.maslow_weights.self_actualization += 0.05

        # 分析问题5：问题解决风格
        q5 = responses.get('q5', '').upper()
        if 'A' in q5 or '保守' in q5 or '稳妥' in q5:
            personality.big_five.conscientiousness += 0.2
            personality.maslow_weights.safety += 0.15
        elif 'B' in q5 or '创新' in q5 or '突破' in q5:
            personality.big_five.openness += 0.25
            personality.maslow_weights.self_actualization += 0.15
            personality.maslow_weights.self_transcendence += 0.05
        elif 'C' in q5 or '平衡' in q5:
            personality.big_five.agreeableness += 0.1

        # 归一化人格向量
        for attr in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
            value = getattr(personality.big_five, attr)
            setattr(personality.big_five, attr, max(0.0, min(1.0, value)))

    def _compute_meta_traits(self, personality: Personality) -> MetaTraits:
        """计算衍生特质"""
        bf = personality.big_five
        mw = personality.maslow_weights

        adaptability = (
            bf.openness * 0.4 +
            (1 - bf.neuroticism) * 0.3 +
            (mw.self_actualization + mw.self_transcendence) * 0.3
        )

        resilience = (
            bf.conscientiousness * 0.4 +
            bf.agreeableness * 0.3 +
            mw.safety * 0.3
        )

        curiosity = (
            bf.openness * 0.5 +
            bf.extraversion * 0.3 +
            mw.self_actualization * 0.2
        )

        moral_sense = (
            bf.agreeableness * 0.4 +
            bf.conscientiousness * 0.4 +
            mw.esteem * 0.2
        )

        return MetaTraits(
            adaptability=round(adaptability, 3),
            resilience=round(resilience, 3),
            curiosity=round(curiosity, 3),
            moral_sense=round(moral_sense, 3)
        )

    def _determine_personality_type(self, personality: Personality) -> str:
        """确定人格类型"""
        bf = personality.big_five

        if bf.conscientiousness > 0.7 and bf.neuroticism < 0.5:
            return "谨慎探索型"
        elif bf.openness > 0.7:
            return "激进创新型"
        else:
            return "平衡稳重型"

    def _generate_description(self, personality: Personality) -> str:
        """生成人格描述"""
        bf = personality.big_five
        traits = []

        if bf.conscientiousness > 0.7:
            traits.append("谨慎可靠")
        if bf.openness > 0.7:
            traits.append("乐于创新")
        if bf.agreeableness > 0.7:
            traits.append("善于合作")
        if bf.extraversion > 0.7:
            traits.append("活跃互动")

        if not traits:
            traits.append("平衡稳重")

        return f"基于您的偏好生成的个性化人格，特点是{'、'.join(traits)}"

    def _extract_core_traits(self, personality: Personality) -> List[str]:
        """提取核心特质"""
        bf = personality.big_five
        traits = []

        trait_map = {
            'openness': '开放探索',
            'conscientiousness': '严谨可靠',
            'extraversion': '积极互动',
            'agreeableness': '协作友善',
            'neuroticism': '敏感谨慎'
        }

        # 提取得分最高的3个特质
        sorted_traits = sorted([
            ('openness', bf.openness),
            ('conscientiousness', bf.conscientiousness),
            ('extraversion', bf.extraversion),
            ('agreeableness', bf.agreeableness),
            ('neuroticism', bf.neuroticism)
        ], key=lambda x: x[1], reverse=True)

        for trait_name, value in sorted_traits[:3]:
            if value > 0.5:
                traits.append(trait_map[trait_name])

        if len(traits) < 3:
            traits.append('持续学习')

        return traits

    def _determine_evolution_level(self, maslow_weights: MaslowWeights) -> str:
        """确定进化层级"""
        weights = maslow_weights.to_dict()

        max_weight = max(weights.values())

        if weights["self_transcendence"] == max_weight:
            return "self_transcendence"
        elif weights["self_actualization"] == max_weight:
            return "self_actualization"
        elif weights["esteem"] == max_weight:
            return "esteem"
        elif weights["belonging"] == max_weight:
            return "belonging"
        elif weights["safety"] == max_weight:
            return "safety"
        else:
            return "physiological"

    def is_initialized(self) -> bool:
        """检查人格是否已初始化"""
        return os.path.exists(self.personality_file)

    def decide_self_correction(self, objectivity_metric: dict, context: dict = None) -> dict:
        """
        映射层决策辅助：提供人格数据用于决策

        注意：此方法仅提供人格数据支持，实际决策权在映射层。
        映射层基于马斯洛需求层次和人格特质做出最终决策。
        
        Args:
            objectivity_metric: 客观性评估结果
            context: 上下文信息
        
        Returns:
            dict: 人格数据供映射层决策使用
        """
        if self._personality is None:
            self.load()

        if self._personality is None:
            return {
                'should_correct': False,
                'reason': '人格未初始化',
                'confidence': 0.0
            }

        # 提取客观性指标
        is_appropriate = objectivity_metric.get('is_appropriate', True)
        gap = objectivity_metric.get('gap', 0.0)
        severity = objectivity_metric.get('severity', 'none')
        objectivity_score = objectivity_metric.get('objectivity_score', 1.0)
        subjectivity_score = objectivity_metric.get('subjectivity_score', 0.0)

        # 基于人格特质调整决策阈值
        # 谨慎型人格对不适切性更敏感
        if '谨慎' in self._personality.preset_name or self._personality.big_five.conscientiousness > 0.7:
            gap_threshold = 0.1
        # 激进型人格容忍度较高
        elif '激进' in self._personality.preset_name or self._personality.big_five.openness > 0.7:
            gap_threshold = 0.3
        # 平衡型人格使用中等阈值
        else:
            gap_threshold = 0.2

        # 严重程度调整
        severity_multiplier = {
            'none': 0.0,
            'mild': 0.5,
            'moderate': 1.0,
            'severe': 2.0
        }
        effective_gap = gap * severity_multiplier.get(severity, 1.0)

        # 基于场景类型的权重调整
        context_type = context.get('type', 'general') if context else 'general'
        critical_contexts = ['scientific', 'legal', 'medical', 'technical']
        if context_type in critical_contexts:
            # 关键场景更严格
            effective_gap *= 1.5

        # 决策逻辑
        should_correct = effective_gap > gap_threshold

        # 计算决策置信度
        if severity == 'severe':
            confidence = 0.95
        elif severity == 'moderate':
            confidence = 0.8
        elif severity == 'mild':
            confidence = 0.6
        else:
            confidence = 0.3

        # 生成决策理由
        reasons = []
        if not is_appropriate:
            reasons.append(f"客观性不适切（差距：{gap:.2f}）")
        if severity != 'none':
            reasons.append(f"严重程度：{severity}")
        if effective_gap > gap_threshold:
            reasons.append(f"有效差距（{effective_gap:.2f}）超过阈值（{gap_threshold:.2f}）")
        
        # 考虑人格特质对决策的影响
        trait_influence = []
        if self._personality.big_five.conscientiousness > 0.7:
            trait_influence.append("谨慎特质倾向于纠错")
        if self._personality.big_five.openness > 0.7:
            trait_influence.append("开放特质容忍不确定性")

        return {
            'should_correct': should_correct,
            'gap': gap,
            'effective_gap': effective_gap,
            'gap_threshold': gap_threshold,
            'severity': severity,
            'confidence': confidence,
            'reason': '; '.join(reasons) if reasons else '无需纠错',
            'trait_influence': trait_influence,
            'personality_type': self._personality.preset_name,
            'timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }


# ===== 命令行接口 =====

def main():
    """命令行测试接口"""
    print("=== 人格层纯Python实现（测试模式） ===\n")

    layer = PersonalityLayer()

    # 测试预设人格初始化
    print("测试1：从预设人格初始化")
    personality = layer.init_from_preset(
        PersonalityType.CAUTIOUS_EXPLORER,
        nickname="塔斯"
    )
    print(f"用户称呼: {personality.user_nickname}")
    print(f"人格类型: {personality.preset_name}")
    print(f"核心特质: {', '.join(personality.core_traits)}")
    print()

    # 测试加载
    print("测试2：加载人格配置")
    loaded = layer.load()
    print(f"加载成功: {loaded is not None}")
    print(f"用户称呼: {loaded.user_nickname}")
    print()

    # 测试对话初始化
    print("测试3：从对话初始化")
    responses = {
        'q1': 'A',
        'q2': 'B',
        'q3': 'C',
        'q4': 'A',
        'q5': 'C'
    }
    personality = layer.init_from_dialogue(responses, nickname="贾维斯")
    print(f"用户称呼: {personality.user_nickname}")
    print(f"人格类型: {personality.preset_name}")
    print(f"描述: {personality.description}")
    print()

    # 测试感知映射
    print("测试4：感知映射")
    perception = {"type": "task_challenge"}
    mapping = layer.map_perception(perception)
    print(f"主导需求: {mapping.get('dominant_need')}")
    print()

    print("=== 所有测试完成 ===")


if __name__ == "__main__":
    main()
