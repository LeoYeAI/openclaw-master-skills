#!/usr/bin/env python3
"""
🧬 灵魂提取器（Soul Extractor）
从对话文本中分析并提取用户的人格信息，更新灵魂存档。

用法：
  python3 soul_extract.py --input "对话内容"
  python3 soul_extract.py --input-file /path/to/conversation.txt
  python3 soul_extract.py --soul-dir /custom/path --input "对话内容"

默认数据目录：~/.skills_data/soul-archive/（通过 Path.home() 解析，跨平台兼容）
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ============================================================
# 数据结构定义
# ============================================================

DEFAULT_PROFILE = {
    "soul_version": "1.0",
    "created_at": None,
    "last_updated": None,
    "total_conversations": 0,
    "total_extractions": 0,
    "completeness_score": 0.0,
    "dimensions": {
        "identity": 0.0,
        "personality": 0.0,
        "language_style": 0.0,
        "knowledge": 0.0,
        "memory": 0.0,
        "relationships": 0.0,
        "voice": 0.0
    }
}

DEFAULT_BASIC_INFO = {
    "name": None,
    "nickname": None,
    "age": None,
    "birth_year": None,
    "gender": None,
    "location": None,
    "hometown": None,
    "occupation": None,
    "company": None,
    "education": None,
    "languages": [],
    "hobbies": [],
    "self_description": None,
    "life_motto": None,
    # === 生活习惯与偏好 ===
    "daily_routine": None,          # 日常作息描述
    "sleep_schedule": None,         # 作息时间（早起/夜猫子）
    "food_preferences": [],         # 饮食偏好
    "food_dislikes": [],            # 饮食禁忌/不喜欢的
    "music_taste": [],              # 音乐品味
    "movie_taste": [],              # 电影/剧集品味
    "book_taste": [],               # 阅读偏好
    "travel_preferences": None,     # 旅行风格
    "pet_preference": None,         # 宠物
    "aesthetic_style": None,        # 审美风格（穿衣/家居/设计偏好）
    "spending_style": None,         # 消费风格（节俭/享受型/理性消费）
    # === 数字身份 ===
    "online_personas": [],          # 网名/ID 风格
    "favorite_apps": [],            # 常用 App
    "social_platforms": [],         # 活跃的社交平台
    "digital_habits": None,         # 上网习惯描述
    "tech_proficiency": None,       # 技术水平（小白/普通/极客）
    "_meta": {}
}

DEFAULT_PERSONALITY = {
    "mbti": None,
    "big_five": {
        "openness": None,
        "conscientiousness": None,
        "extraversion": None,
        "agreeableness": None,
        "neuroticism": None
    },
    "traits": [],
    "values": [],
    "decision_style": None,
    "communication_preference": None,
    "strengths": [],
    "weaknesses": [],
    # === 行为模式 ===
    "risk_tolerance": None,         # 风险偏好（保守/适度/冒险）
    "procrastination_level": None,  # 拖延程度
    "perfectionism_level": None,    # 完美主义程度
    "planning_style": None,         # 计划性（随性/弹性/严格计划）
    "learning_style": None,         # 学习方式（实践/阅读/视频/讨论）
    "work_style": None,             # 工作风格（独狼/协作/领导）
    # === 社交风格 ===
    "social_energy": None,          # 社交能量（独处充电/社交充电/平衡）
    "group_role": None,             # 在群体中的角色（领导者/跟随者/调解者/观察者）
    "trust_building": None,         # 建立信任的方式（快速/谨慎/选择性）
    "conflict_approach": None,      # 面对冲突的方式（回避/直面/调解）
    # === 压力与成长 ===
    "stress_response": None,        # 压力反应模式
    "motivation_drivers": [],       # 什么驱动TA（成就/金钱/认可/自由/好奇心）
    "growth_areas": [],             # 自认为需要提升的方面
    "_meta": {}
}

DEFAULT_LANGUAGE = {
    "catchphrases": [],
    "sentence_patterns": [],
    "preferred_words": [],
    "avoided_words": [],
    "emoji_usage": {
        "frequency": "unknown",
        "favorites": []
    },
    "punctuation_habits": {},
    "formality_level": None,
    "verbosity": None,
    "humor_style": None,
    "response_length_preference": None,
    "thinking_expression": None,
    "examples": [],
    # === 语言深度指纹 ===
    "dialect_features": [],         # 方言/地域用语特征
    "filler_words": [],             # 语气词/填充词（嗯、啊、那个、就是说）
    "persuasion_style": None,       # 说服别人时的方式（摆事实/讲道理/打感情牌/用类比）
    "storytelling_style": None,     # 讲故事的方式（时间线/倒叙/先结论）
    "question_style": None,         # 提问风格（反问/开放式/选择式）
    "agreement_expressions": [],    # 表示同意时的说法
    "disagreement_expressions": [], # 表示不同意时的说法
    "greeting_style": None,         # 打招呼方式
    "farewell_style": None,         # 告别方式
    "typing_habits": None,          # 打字习惯（如喜欢连续短句 vs 长段落）
    "_meta": {}
}

DEFAULT_COMMUNICATION = {
    "directness": None,
    "logic_vs_emotion": None,
    "detail_level": None,
    "listening_style": None,
    "conflict_style": None,
    "encouragement_style": None,
    "criticism_style": None,
    "_meta": {}
}

DEFAULT_TOPICS = {
    "topics": [],
    "_meta": {}
}

DEFAULT_KNOWLEDGE = {
    "domains": [],
    "skills": [],
    "expertise_level": {},
    "_meta": {}
}

DEFAULT_EMOTIONAL_PATTERNS = {
    "triggers": {
        "joy": [],
        "anger": [],
        "sadness": [],
        "anxiety": [],
        "excitement": [],
        "nostalgia": [],
        "pride": [],            # 自豪感
        "gratitude": [],        # 感恩
        "frustration": [],      # 挫败感
        "curiosity": [],        # 好奇心被激发
        "peace": [],            # 内心平静
        "guilt": []             # 愧疚
    },
    "expression_style": None,
    "emotional_range": None,       # 情绪波动范围（平稳/适中/起伏大）
    "emotional_awareness": None,   # 情绪自我觉察能力
    "empathy_level": None,         # 共情能力（低/中/高）
    "coping_mechanisms": [],
    "comfort_activities": [],      # 心情不好时会做什么
    "celebration_style": None,     # 开心时的表现方式
    "_meta": {}
}

DEFAULT_PEOPLE = {
    "people": [],
    "_meta": {}
}

DEFAULT_CONFIG = {
    "privacy_level": "standard",
    "auto_extract": True,
    "extract_dimensions": {
        "identity": True,
        "personality": True,
        "language_style": True,
        "knowledge": True,
        "episodic_memory": True,
        "emotional_patterns": True,
        "relationships": False,
        "voice": False
    },
    "sensitive_topics_filter": True,
    "require_confirmation_for": ["health", "finance", "intimate_relationships"],
    "data_retention_days": None,
    "encryption": False
}


# ============================================================
# 文件操作工具
# ============================================================

def ensure_dir(path: Path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default=None, crypto=None):
    """加载 JSON 文件，不存在则返回默认值。支持加密文件透明解密。"""
    if path.exists():
        if crypto is not None:
            try:
                return crypto.decrypt_file(path)
            except Exception:
                pass  # fallback to plain read
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default if default is not None else {}


def save_json(path: Path, data: dict, crypto=None):
    """保存 JSON 文件。如果 crypto 不为 None，则加密写入。"""
    ensure_dir(path.parent)
    if crypto is not None:
        crypto.encrypt_file_save(path, data)
    else:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def append_jsonl(path: Path, record: dict, crypto=None):
    """追加一行到 JSONL 文件。如果 crypto 不为 None，则加密写入。"""
    ensure_dir(path.parent)
    if crypto is not None:
        crypto.append_encrypted_jsonl(path, record)
    else:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')


def now_iso():
    """当前时间 ISO 格式"""
    return datetime.now().astimezone().isoformat()


# ============================================================
# 灵魂存档管理器
# ============================================================

class SoulArchive:
    """灵魂存档管理器 —— 管理 .skills_data/soul-archive/ 目录的读写，支持加密"""

    def __init__(self, soul_dir: str, crypto=None):
        self.root = Path(soul_dir)
        self.profile_path = self.root / "profile.json"
        self.config_path = self.root / "config.json"
        self.changelog_path = self.root / "soul_changelog.jsonl"
        self.crypto = crypto  # SoulCrypto instance or None

        # 数据文件路径
        self.paths = {
            "basic_info": self.root / "identity" / "basic_info.json",
            "personality": self.root / "identity" / "personality.json",
            "language": self.root / "style" / "language.json",
            "communication": self.root / "style" / "communication.json",
            "topics": self.root / "memory" / "semantic" / "topics.json",
            "knowledge": self.root / "memory" / "semantic" / "knowledge.json",
            "emotional": self.root / "memory" / "emotional" / "patterns.json",
            "people": self.root / "relationships" / "people.json",
        }

    def is_initialized(self) -> bool:
        return self.profile_path.exists()

    def load_profile(self) -> dict:
        return load_json(self.profile_path, DEFAULT_PROFILE.copy())

    def load_config(self) -> dict:
        return load_json(self.config_path, DEFAULT_CONFIG.copy())

    def init_crypto_from_config(self, password: str = None):
        """Initialize crypto from config if encryption is enabled."""
        config = self.load_config()
        if config.get("encryption"):
            sys.path.insert(0, str(Path(__file__).parent))
            from soul_crypto import get_crypto_from_config
            self.crypto = get_crypto_from_config(config, password)

    def load_all(self) -> dict:
        """加载全部灵魂数据"""
        c = self.crypto
        return {
            "profile": self.load_profile(),
            "config": self.load_config(),
            "basic_info": load_json(self.paths["basic_info"], DEFAULT_BASIC_INFO.copy(), crypto=c),
            "personality": load_json(self.paths["personality"], DEFAULT_PERSONALITY.copy(), crypto=c),
            "language": load_json(self.paths["language"], DEFAULT_LANGUAGE.copy(), crypto=c),
            "communication": load_json(self.paths["communication"], DEFAULT_COMMUNICATION.copy(), crypto=c),
            "topics": load_json(self.paths["topics"], DEFAULT_TOPICS.copy(), crypto=c),
            "knowledge": load_json(self.paths["knowledge"], DEFAULT_KNOWLEDGE.copy(), crypto=c),
            "emotional": load_json(self.paths["emotional"], DEFAULT_EMOTIONAL_PATTERNS.copy(), crypto=c),
            "people": load_json(self.paths["people"], DEFAULT_PEOPLE.copy(), crypto=c),
        }

    def save_data(self, key: str, data: dict):
        """保存特定数据文件"""
        if key == "profile":
            save_json(self.profile_path, data)
        elif key == "config":
            save_json(self.config_path, data)
        elif key in self.paths:
            save_json(self.paths[key], data, crypto=self.crypto)

    def save_extraction(self, extraction: dict):
        """
        保存一次提取结果。
        extraction 格式：
        {
            "basic_info": { ... 增量更新字段 ... },
            "personality": { ... },
            "language": { ... },
            "topics": [ { new topic objects } ],
            "episodic": [ { new episodes } ],
            "emotional": { ... },
            "people": [ { new people } ],
            "summary": "本次提取摘要"
        }
        """
        changes = []
        config = self.load_config()
        dims = config.get("extract_dimensions", {})
        c = self.crypto

        # 1. 更新身份信息
        if dims.get("identity", True) and extraction.get("basic_info"):
            current = load_json(self.paths["basic_info"], DEFAULT_BASIC_INFO.copy(), crypto=c)
            updated_fields = self._merge_identity(current, extraction["basic_info"])
            if updated_fields:
                save_json(self.paths["basic_info"], current, crypto=c)
                changes.append(f"identity: updated {', '.join(updated_fields)}")

        # 2. 更新性格特征
        if dims.get("personality", True) and extraction.get("personality"):
            current = load_json(self.paths["personality"], DEFAULT_PERSONALITY.copy(), crypto=c)
            updated_fields = self._merge_personality(current, extraction["personality"])
            if updated_fields:
                save_json(self.paths["personality"], current, crypto=c)
                changes.append(f"personality: updated {', '.join(updated_fields)}")

        # 3. 更新语言风格
        if dims.get("language_style", True) and extraction.get("language"):
            current = load_json(self.paths["language"], DEFAULT_LANGUAGE.copy(), crypto=c)
            updated_fields = self._merge_language(current, extraction["language"])
            if updated_fields:
                save_json(self.paths["language"], current, crypto=c)
                changes.append(f"language: updated {', '.join(updated_fields)}")

        # 4. 更新话题观点
        if dims.get("knowledge", True) and extraction.get("topics"):
            current = load_json(self.paths["topics"], DEFAULT_TOPICS.copy(), crypto=c)
            new_count = self._merge_topics(current, extraction["topics"])
            if new_count:
                save_json(self.paths["topics"], current, crypto=c)
                changes.append(f"topics: added/updated {new_count} topics")

        # 5. 追加情景记忆
        if dims.get("episodic_memory", True) and extraction.get("episodic"):
            today = datetime.now().strftime("%Y-%m-%d")
            ep_path = self.root / "memory" / "episodic" / f"{today}.jsonl"
            for episode in extraction["episodic"]:
                episode["timestamp"] = now_iso()
                append_jsonl(ep_path, episode, crypto=c)
            changes.append(f"episodic: added {len(extraction['episodic'])} episodes")

        # 6. 更新情感模式
        if dims.get("emotional_patterns", True) and extraction.get("emotional"):
            current = load_json(self.paths["emotional"], DEFAULT_EMOTIONAL_PATTERNS.copy(), crypto=c)
            updated = self._merge_emotional(current, extraction["emotional"])
            if updated:
                save_json(self.paths["emotional"], current, crypto=c)
                changes.append(f"emotional: updated {', '.join(updated)}")

        # 7. 更新人际关系
        if dims.get("relationships", False) and extraction.get("people"):
            current = load_json(self.paths["people"], DEFAULT_PEOPLE.copy(), crypto=c)
            new_count = self._merge_people(current, extraction["people"])
            if new_count:
                save_json(self.paths["people"], current, crypto=c)
                changes.append(f"relationships: added/updated {new_count} people")

        # 更新 profile
        if changes:
            profile = self.load_profile()
            profile["last_updated"] = now_iso()
            profile["total_extractions"] = profile.get("total_extractions", 0) + 1
            profile["completeness_score"] = self._calc_completeness()
            profile["dimensions"] = self._calc_dimension_scores()
            save_json(self.profile_path, profile)

            # 追加 changelog
            append_jsonl(self.changelog_path, {
                "timestamp": now_iso(),
                "extraction_id": profile["total_extractions"],
                "changes": changes,
                "summary": extraction.get("summary", ""),
                "completeness": profile["completeness_score"]
            }, crypto=c)

        return changes

    # ---- 合并策略 ----

    def _merge_identity(self, current: dict, new_data: dict) -> list:
        """合并身份信息：只填充空字段或更新低置信度字段"""
        updated = []
        meta = current.get("_meta", {})
        for key, value in new_data.items():
            if key.startswith("_") or value is None:
                continue
            if isinstance(value, dict) and "value" in value:
                # 带置信度的更新
                new_conf = value.get("confidence", 0.5)
                old_conf = meta.get(key, {}).get("confidence", 0)
                if current.get(key) is None or new_conf > old_conf:
                    current[key] = value["value"]
                    meta[key] = {"confidence": new_conf, "updated": now_iso()}
                    updated.append(key)
            else:
                # 简单更新：只填充空字段
                if current.get(key) is None or (isinstance(current.get(key), list) and not current[key]):
                    current[key] = value
                    meta[key] = {"confidence": 0.7, "updated": now_iso()}
                    updated.append(key)
        current["_meta"] = meta
        return updated

    def _merge_personality(self, current: dict, new_data: dict) -> list:
        """合并性格特征"""
        updated = []
        for key, value in new_data.items():
            if key.startswith("_") or value is None:
                continue
            if key == "traits" and isinstance(value, list):
                existing = set(current.get("traits", []))
                new_traits = [t for t in value if t not in existing]
                if new_traits:
                    current.setdefault("traits", []).extend(new_traits)
                    updated.append(f"traits(+{len(new_traits)})")
            elif key == "values" and isinstance(value, list):
                existing = set(current.get("values", []))
                new_values = [v for v in value if v not in existing]
                if new_values:
                    current.setdefault("values", []).extend(new_values)
                    updated.append(f"values(+{len(new_values)})")
            elif key == "big_five" and isinstance(value, dict):
                bf = current.setdefault("big_five", {})
                for dim, score in value.items():
                    if score is not None and bf.get(dim) is None:
                        bf[dim] = score
                        updated.append(f"big_five.{dim}")
            elif current.get(key) is None:
                current[key] = value
                updated.append(key)
        return updated

    def _merge_language(self, current: dict, new_data: dict) -> list:
        """合并语言风格"""
        updated = []
        for key, value in new_data.items():
            if key.startswith("_") or value is None:
                continue
            if key in ("catchphrases", "sentence_patterns", "preferred_words", "examples") and isinstance(value, list):
                existing = current.get(key, [])
                # 对于例句，去重
                existing_set = set(str(x) for x in existing)
                new_items = [x for x in value if str(x) not in existing_set]
                if new_items:
                    current.setdefault(key, []).extend(new_items)
                    updated.append(f"{key}(+{len(new_items)})")
            elif key == "emoji_usage" and isinstance(value, dict):
                eu = current.setdefault("emoji_usage", {})
                if value.get("frequency"):
                    eu["frequency"] = value["frequency"]
                if value.get("favorites"):
                    existing_fav = set(eu.get("favorites", []))
                    new_fav = [e for e in value["favorites"] if e not in existing_fav]
                    if new_fav:
                        eu.setdefault("favorites", []).extend(new_fav)
                        updated.append("emoji_usage")
            elif current.get(key) is None:
                current[key] = value
                updated.append(key)
        return updated

    def _merge_topics(self, current: dict, new_topics: list) -> int:
        """合并话题"""
        existing = {t["name"]: t for t in current.get("topics", [])}
        count = 0
        for topic in new_topics:
            name = topic.get("name")
            if not name:
                continue
            if name in existing:
                # 更新已有话题
                et = existing[name]
                et["frequency"] = et.get("frequency", 0) + 1
                et["last_mentioned"] = datetime.now().strftime("%Y-%m-%d")
                if topic.get("key_opinions"):
                    existing_ops = set(et.get("key_opinions", []))
                    new_ops = [o for o in topic["key_opinions"] if o not in existing_ops]
                    et.setdefault("key_opinions", []).extend(new_ops)
                if topic.get("sentiment"):
                    et["sentiment"] = topic["sentiment"]
                if topic.get("stance"):
                    et["stance"] = topic["stance"]
                count += 1
            else:
                topic.setdefault("frequency", 1)
                topic.setdefault("last_mentioned", datetime.now().strftime("%Y-%m-%d"))
                current.setdefault("topics", []).append(topic)
                count += 1
        return count

    def _merge_emotional(self, current: dict, new_data: dict) -> list:
        """合并情感模式"""
        updated = []
        if new_data.get("triggers"):
            triggers = current.setdefault("triggers", {})
            for emotion, items in new_data["triggers"].items():
                if items:
                    existing = set(triggers.get(emotion, []))
                    new_items = [i for i in items if i not in existing]
                    if new_items:
                        triggers.setdefault(emotion, []).extend(new_items)
                        updated.append(f"triggers.{emotion}")
        for key in ("expression_style", "emotional_range"):
            if new_data.get(key) and current.get(key) is None:
                current[key] = new_data[key]
                updated.append(key)
        if new_data.get("coping_mechanisms"):
            existing = set(current.get("coping_mechanisms", []))
            new_items = [i for i in new_data["coping_mechanisms"] if i not in existing]
            if new_items:
                current.setdefault("coping_mechanisms", []).extend(new_items)
                updated.append("coping_mechanisms")
        return updated

    def _merge_people(self, current: dict, new_people: list) -> int:
        """合并人际关系"""
        existing = {p["name"]: p for p in current.get("people", [])}
        count = 0
        for person in new_people:
            name = person.get("name")
            if not name:
                continue
            if name in existing:
                ep = existing[name]
                for k, v in person.items():
                    if v and not ep.get(k):
                        ep[k] = v
                count += 1
            else:
                current.setdefault("people", []).append(person)
                count += 1
        return count

    # ---- 完整度计算 ----

    def _calc_completeness(self) -> float:
        """计算灵魂存档总体完整度"""
        scores = self._calc_dimension_scores()
        weights = {
            "identity": 0.15,
            "personality": 0.20,
            "language_style": 0.25,
            "knowledge": 0.15,
            "memory": 0.15,
            "relationships": 0.05,
            "voice": 0.05
        }
        total = sum(scores.get(k, 0) * w for k, w in weights.items())
        return round(total, 3)

    def _calc_dimension_scores(self) -> dict:
        """计算各维度完整度分数"""
        scores = {}
        c = self.crypto

        # 身份（扩展：包含生活习惯和数字身份）
        bi = load_json(self.paths["basic_info"], {}, crypto=c)
        core_fields = ["name", "occupation", "location"]
        filled = sum(1 for f in core_fields if bi.get(f))
        extra_fields = ["age", "gender", "education", "hometown", "hobbies"]
        filled += sum(0.5 for f in extra_fields if bi.get(f))
        # 新增字段（生活习惯 + 数字身份）
        lifestyle_fields = ["daily_routine", "sleep_schedule", "food_preferences",
                           "music_taste", "movie_taste", "book_taste",
                           "aesthetic_style", "spending_style"]
        filled += sum(0.3 for f in lifestyle_fields if bi.get(f))
        digital_fields = ["favorite_apps", "social_platforms", "tech_proficiency"]
        filled += sum(0.3 for f in digital_fields if bi.get(f))
        max_score = len(core_fields) + len(extra_fields) * 0.5 + len(lifestyle_fields) * 0.3 + len(digital_fields) * 0.3
        scores["identity"] = min(1.0, round(filled / max_score, 2))

        # 性格（扩展：包含行为模式和社交风格）
        ps = load_json(self.paths["personality"], {}, crypto=c)
        trait_count = len(ps.get("traits", []))
        value_count = len(ps.get("values", []))
        bf_count = sum(1 for v in ps.get("big_five", {}).values() if v is not None)
        behavior_fields = ["risk_tolerance", "procrastination_level", "planning_style",
                          "learning_style", "work_style"]
        behavior_filled = sum(1 for f in behavior_fields if ps.get(f))
        social_fields = ["social_energy", "group_role", "conflict_approach"]
        social_filled = sum(1 for f in social_fields if ps.get(f))
        motivation_count = len(ps.get("motivation_drivers", []))
        scores["personality"] = min(1.0, round(
            trait_count / 5 * 0.25 +
            value_count / 3 * 0.15 +
            bf_count / 5 * 0.2 +
            behavior_filled / len(behavior_fields) * 0.2 +
            social_filled / len(social_fields) * 0.1 +
            min(motivation_count / 3, 1.0) * 0.1
        , 2))

        # 语言风格（扩展：包含深度语言指纹）
        lang = load_json(self.paths["language"], {}, crypto=c)
        cp_count = len(lang.get("catchphrases", []))
        sp_count = len(lang.get("sentence_patterns", []))
        ex_count = len(lang.get("examples", []))
        deep_lang_fields = ["dialect_features", "filler_words",
                           "persuasion_style", "storytelling_style",
                           "agreement_expressions", "disagreement_expressions"]
        deep_filled = sum(1 for f in deep_lang_fields if lang.get(f))
        scores["language_style"] = min(1.0, round(
            cp_count / 3 * 0.3 +
            sp_count / 3 * 0.2 +
            ex_count / 5 * 0.2 +
            deep_filled / len(deep_lang_fields) * 0.3
        , 2))

        # 知识观点
        topics = load_json(self.paths["topics"], {}, crypto=c)
        topic_count = len(topics.get("topics", []))
        scores["knowledge"] = min(1.0, round(topic_count / 5, 2))

        # 记忆
        ep_dir = self.root / "memory" / "episodic"
        ep_count = 0
        if ep_dir.exists():
            for f in ep_dir.glob("*.jsonl"):
                if c is not None:
                    ep_count += len(c.read_encrypted_jsonl(f))
                else:
                    with open(f, 'r', encoding='utf-8') as fh:
                        ep_count += sum(1 for _ in fh)
        scores["memory"] = min(1.0, round(ep_count / 10, 2))

        # 人际关系
        people = load_json(self.paths["people"], {}, crypto=c)
        people_count = len(people.get("people", []))
        scores["relationships"] = min(1.0, round(people_count / 3, 2))

        # 语音
        voice_dir = self.root / "voice" / "samples"
        voice_count = len(list(voice_dir.glob("*"))) if voice_dir.exists() else 0
        scores["voice"] = min(1.0, 1.0 if voice_count > 0 else 0.0)

        return scores

    def get_status_report(self) -> str:
        """生成状态报告"""
        profile = self.load_profile()
        scores = self._calc_dimension_scores()
        completeness = self._calc_completeness()

        lines = [
            "🧬 灵魂存档状态报告",
            f"━━━━━━━━━━━━━━━━━━━━━━━━",
            f"总完整度: {completeness:.1%}",
            f"总提取次数: {profile.get('total_extractions', 0)}",
            f"最后更新: {profile.get('last_updated', '从未')}",
            "",
            "各维度完整度:",
        ]

        dim_names = {
            "identity": "👤 身份信息",
            "personality": "💫 性格特征",
            "language_style": "🗣️ 语言风格",
            "knowledge": "🧠 知识观点",
            "memory": "📝 记忆经历",
            "relationships": "🤝 人际关系",
            "voice": "🎤 语音特征",
        }

        for key, name in dim_names.items():
            score = scores.get(key, 0)
            bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
            lines.append(f"  {name}: [{bar}] {score:.0%}")

        return "\n".join(lines)


# ============================================================
# 提取结果构建器（供 AI 调用）
# ============================================================

class ExtractionBuilder:
    """构建一次提取的结果"""

    def __init__(self):
        self.result = {
            "basic_info": {},
            "personality": {},
            "language": {},
            "topics": [],
            "episodic": [],
            "emotional": {},
            "people": [],
            "summary": ""
        }

    def set_identity(self, **kwargs):
        """设置身份信息。支持带置信度：set_identity(name={"value": "张三", "confidence": 0.95})"""
        self.result["basic_info"].update(kwargs)
        return self

    def add_trait(self, trait: str):
        self.result.setdefault("personality", {}).setdefault("traits", []).append(trait)
        return self

    def add_value(self, value: str):
        self.result.setdefault("personality", {}).setdefault("values", []).append(value)
        return self

    def set_personality(self, **kwargs):
        self.result["personality"].update(kwargs)
        return self

    def add_catchphrase(self, phrase: str):
        self.result.setdefault("language", {}).setdefault("catchphrases", []).append(phrase)
        return self

    def add_sentence_pattern(self, pattern: str):
        self.result.setdefault("language", {}).setdefault("sentence_patterns", []).append(pattern)
        return self

    def add_language_example(self, example: str):
        self.result.setdefault("language", {}).setdefault("examples", []).append(example)
        return self

    def set_language(self, **kwargs):
        self.result["language"].update(kwargs)
        return self

    def add_topic(self, name: str, sentiment: str = None, stance: str = None, opinions: list = None):
        topic = {"name": name}
        if sentiment:
            topic["sentiment"] = sentiment
        if stance:
            topic["stance"] = stance
        if opinions:
            topic["key_opinions"] = opinions
        self.result["topics"].append(topic)
        return self

    def add_episode(self, event: str, emotion: str = None, context: str = None, significance: str = "normal"):
        ep = {"event": event, "significance": significance}
        if emotion:
            ep["emotion"] = emotion
        if context:
            ep["context"] = context
        self.result["episodic"].append(ep)
        return self

    def add_emotional_trigger(self, emotion: str, trigger: str):
        triggers = self.result.setdefault("emotional", {}).setdefault("triggers", {})
        triggers.setdefault(emotion, []).append(trigger)
        return self

    def add_person(self, name: str, relationship: str = None, description: str = None):
        person = {"name": name}
        if relationship:
            person["relationship"] = relationship
        if description:
            person["description"] = description
        self.result["people"].append(person)
        return self

    def set_summary(self, summary: str):
        self.result["summary"] = summary
        return self

    # === 新增：生活习惯 ===
    def set_lifestyle(self, **kwargs):
        """设置生活习惯。如 set_lifestyle(sleep_schedule='夜猫子', spending_style='理性消费')"""
        self.result["basic_info"].update(kwargs)
        return self

    def add_food_preference(self, food: str):
        self.result.setdefault("basic_info", {}).setdefault("food_preferences", []).append(food)
        return self

    def add_music_taste(self, genre: str):
        self.result.setdefault("basic_info", {}).setdefault("music_taste", []).append(genre)
        return self

    def add_favorite_app(self, app: str):
        self.result.setdefault("basic_info", {}).setdefault("favorite_apps", []).append(app)
        return self

    # === 新增：行为模式 ===
    def set_behavior(self, **kwargs):
        """设置行为模式。如 set_behavior(risk_tolerance='适度', planning_style='弹性计划')"""
        self.result["personality"].update(kwargs)
        return self

    def add_motivation(self, driver: str):
        self.result.setdefault("personality", {}).setdefault("motivation_drivers", []).append(driver)
        return self

    # === 新增：深度语言指纹 ===
    def add_filler_word(self, word: str):
        self.result.setdefault("language", {}).setdefault("filler_words", []).append(word)
        return self

    def add_dialect_feature(self, feature: str):
        self.result.setdefault("language", {}).setdefault("dialect_features", []).append(feature)
        return self

    def add_agreement_expression(self, expr: str):
        self.result.setdefault("language", {}).setdefault("agreement_expressions", []).append(expr)
        return self

    def add_disagreement_expression(self, expr: str):
        self.result.setdefault("language", {}).setdefault("disagreement_expressions", []).append(expr)
        return self

    # === 新增：情感扩展 ===
    def add_comfort_activity(self, activity: str):
        self.result.setdefault("emotional", {}).setdefault("comfort_activities", []).append(activity)
        return self

    def build(self) -> dict:
        return self.result


# ============================================================
# CLI 入口
# ============================================================

def main():
    default_soul_dir = str(Path.home() / ".skills_data" / "soul-archive")
    parser = argparse.ArgumentParser(description="🧬 灵魂提取器")
    parser.add_argument("--soul-dir", default=default_soul_dir,
                        help=f"灵魂数据目录路径（默认: {default_soul_dir}）")
    parser.add_argument("--input", help="对话内容（直接传入）")
    parser.add_argument("--input-file", help="对话内容文件路径")
    parser.add_argument("--mode", default="auto", choices=["auto", "manual", "status"],
                        help="模式：auto=自动提取, manual=手动, status=仅查看状态")
    parser.add_argument("--password", help="加密密码（不推荐在命令行使用，建议交互输入或设置 SOUL_PASSWORD 环境变量）")

    args = parser.parse_args()

    archive = SoulArchive(args.soul_dir)

    # Auto-initialize crypto if encryption is enabled
    if archive.is_initialized():
        config = archive.load_config()
        if config.get("encryption"):
            archive.init_crypto_from_config(password=args.password)

    if args.mode == "status":
        if not archive.is_initialized():
            print("❌ 灵魂存档尚未初始化。请先运行 soul_init.py")
            sys.exit(1)
        print(archive.get_status_report())
        return

    # 读取输入
    conversation = ""
    if args.input:
        conversation = args.input
    elif args.input_file:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            conversation = f.read()
    else:
        print("请通过 --input 或 --input-file 提供对话内容")
        sys.exit(1)

    if not archive.is_initialized():
        print("❌ 灵魂存档尚未初始化。请先运行 soul_init.py")
        sys.exit(1)

    # 输出对话内容供 AI 分析（AI 会在外部调用后处理结果）
    print(f"📖 收到对话内容（{len(conversation)} 字符）")
    print(f"📂 灵魂存档路径：{args.soul_dir}")
    print()
    print("请使用 ExtractionBuilder 构建提取结果，然后调用 SoulArchive.save_extraction() 保存。")
    print()
    print("示例代码：")
    print("```python")
    print("from soul_extract import SoulArchive, ExtractionBuilder")
    print(f"archive = SoulArchive('{args.soul_dir}')")
    print("builder = ExtractionBuilder()")
    print("builder.set_identity(name='张三', occupation='程序员')")
    print("builder.add_catchphrase('你懂我意思吧')")
    print("builder.add_topic('人工智能', sentiment='positive', stance='乐观派')")
    print("builder.set_summary('本次发现用户是程序员，对AI态度乐观')")
    print("changes = archive.save_extraction(builder.build())")
    print("```")


if __name__ == "__main__":
    main()
