#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2026 Anima-AIOS Contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Anima AIOS v6.0 - Decay Function

基于 Ebbinghaus 遗忘曲线的记忆衰减计算器。
影响检索排序、复习推荐、归档清理。

复习 = 访问：每次 memory_search 命中，strength 重算。

Author: 清禾
Date: 2026-03-24
Version: 6.0.0
"""

import math
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def memory_strength(days_since_access: float, initial_strength: float = 1.0,
                    stability: float = 1.0, review_count: int = 0) -> float:
    """
    计算记忆强度

    Args:
        days_since_access: 距上次访问的天数
        initial_strength: 初始强度（S=1.0, A=0.8, B=0.6, C=0.4）
        stability: 稳定性因子（每次复习 +0.3，上限 3.0）
        review_count: 复习次数

    Returns:
        0.0 ~ 1.0 的记忆强度值
    """
    s_adj = min(3.0, stability + review_count * 0.3)
    strength = initial_strength * math.exp(-days_since_access / (s_adj * 7))
    return max(0.0, min(1.0, strength))


QUALITY_TO_STRENGTH = {"S": 1.0, "A": 0.8, "B": 0.6, "C": 0.4, "pending": 0.5}


class DecayManager:
    """
    记忆衰减管理器

    职责：
    - 计算每条记忆的当前强度
    - 生成复习推荐列表
    - 标记可归档的记忆
    - 维护强度缓存
    """

    # 强度区间行为
    THRESHOLDS = {
        "healthy": 0.7,       # ≥ 0.7 正常
        "weakening": 0.5,     # 0.5~0.7 优先级降低
        "review": 0.3,        # 0.3~0.5 复习推荐
        "forgetting": 0.1,    # 0.1~0.3 即将遗忘提醒
        "archive": 0.1        # < 0.1 可归档
    }

    def __init__(self, agent_name: str, facts_base: str = None):
        self.agent_name = agent_name
        self.decay_dir = Path(facts_base) / agent_name / "decay"
        self.cache_file = self.decay_dir / "strength_cache.json"
        self.decay_dir.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict:
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {"entries": {}, "updated": datetime.now().isoformat()}

    def _save_cache(self):
        self.cache["updated"] = datetime.now().isoformat()
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def record_access(self, fact_id: str, quality: str = "B"):
        """记录一次访问（被动复习）"""
        entry = self.cache["entries"].get(fact_id, {
            "quality": quality,
            "review_count": 0,
            "first_seen": datetime.now().isoformat()
        })
        entry["last_accessed"] = datetime.now().isoformat()
        entry["review_count"] = entry.get("review_count", 0) + 1
        entry["quality"] = quality
        self.cache["entries"][fact_id] = entry
        self._save_cache()

    def get_strength(self, fact_id: str, quality: str = "B") -> float:
        """获取某条记忆的当前强度"""
        entry = self.cache["entries"].get(fact_id)
        if not entry:
            return QUALITY_TO_STRENGTH.get(quality, 0.5)

        last_accessed = entry.get("last_accessed", entry.get("first_seen", ""))
        if not last_accessed:
            return QUALITY_TO_STRENGTH.get(quality, 0.5)

        try:
            last_dt = datetime.fromisoformat(last_accessed)
            days = (datetime.now() - last_dt).total_seconds() / 86400
        except Exception:
            days = 7

        r = QUALITY_TO_STRENGTH.get(entry.get("quality", quality), 0.5)
        review_count = entry.get("review_count", 0)
        return memory_strength(days, r, 1.0, review_count)

    def get_status(self, fact_id: str, quality: str = "B") -> str:
        """获取记忆健康状态"""
        s = self.get_strength(fact_id, quality)
        if s >= self.THRESHOLDS["healthy"]:
            return "healthy"
        elif s >= self.THRESHOLDS["weakening"]:
            return "weakening"
        elif s >= self.THRESHOLDS["review"]:
            return "needs_review"
        elif s >= self.THRESHOLDS["archive"]:
            return "forgetting"
        else:
            return "archivable"

    def scan_all(self, facts: List[Dict]) -> Dict:
        """
        扫描所有记忆的衰减状态

        Args:
            facts: [{"fact_id": ..., "quality": ..., "content": ...}, ...]

        Returns:
            按状态分组的统计
        """
        result = {
            "healthy": [], "weakening": [], "needs_review": [],
            "forgetting": [], "archivable": [], "total": len(facts)
        }

        for fact in facts:
            fid = fact.get("fact_id", "")
            quality = fact.get("quality", "B")
            status = self.get_status(fid, quality)
            strength = self.get_strength(fid, quality)
            result[status].append({
                "fact_id": fid,
                "strength": round(strength, 3),
                "quality": quality
            })

        return result

    def get_review_recommendations(self, facts: List[Dict], limit: int = 5) -> List[Dict]:
        """
        生成复习推荐列表

        返回 strength 在 0.1~0.5 区间的高质量记忆。
        """
        candidates = []
        for fact in facts:
            fid = fact.get("fact_id", "")
            quality = fact.get("quality", "B")
            if quality in ("C", "pending"):
                continue
            strength = self.get_strength(fid, quality)
            if 0.1 <= strength <= 0.5:
                candidates.append({
                    "fact_id": fid,
                    "strength": round(strength, 3),
                    "quality": quality,
                    "content_preview": fact.get("content", "")[:80]
                })

        candidates.sort(key=lambda x: x["strength"])
        return candidates[:limit]

    def get_stats(self) -> Dict:
        entries = self.cache.get("entries", {})
        return {
            "agent": self.agent_name,
            "tracked_memories": len(entries),
            "cache_updated": self.cache.get("updated", ""),
        }
