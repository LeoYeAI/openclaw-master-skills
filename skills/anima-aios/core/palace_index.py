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
Anima AIOS v6.0 - Palace Index

记忆宫殿空间索引引擎。管理宫殿/楼层/房间/位置/物品的层级结构。
移植自 Z 的 palace-index.js，适配 Python + v6 架构。

结构：
  宫殿（Palace）→ 知识领域
    楼层（Floor）→ 大分类
      房间（Room）→ 子主题
        位置（Locus）→ 知识点
          物品（Item）→ 记忆片段（引用 fact_id）

Author: 清禾
Date: 2026-03-23
Version: 6.0.0
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PalaceIndex:
    """记忆宫殿索引管理器"""
    
    # 默认房间定义
    DEFAULT_ROOMS = {
        "technical": {"name": "技术知识", "keywords": ["代码", "架构", "bug", "API", "数据库", "python", "javascript", "部署", "测试", "性能", "code", "debug", "deploy"]},
        "project": {"name": "项目经验", "keywords": ["项目", "版本", "迭代", "需求", "进度", "上线", "发布", "milestone", "sprint", "release"]},
        "people": {"name": "人物关系", "keywords": ["团队", "协作", "沟通", "反馈", "会议", "评审", "mentor", "team", "review"]},
        "decision": {"name": "决策记录", "keywords": ["决策", "方案", "选型", "权衡", "取舍", "原则", "铁律", "decision", "tradeoff", "principle"]},
    }
    
    def __init__(self, agent_name: str, facts_base: str = None):
        self.agent_name = agent_name
        self.palace_dir = Path(facts_base) / agent_name / "palace"
        self.index_file = self.palace_dir / "index.json"
        self.rooms_dir = self.palace_dir / "rooms"
        self.links_file = self.palace_dir / "links.jsonl"
        
        # 确保目录
        self.palace_dir.mkdir(parents=True, exist_ok=True)
        self.rooms_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载或初始化索引
        self.index = self._load_index()
    
    def _load_index(self) -> Dict:
        """加载宫殿索引（Z BUG-015 修复：加载后重算 stats）"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
                # 从实际 room 文件重算 stats，避免统计偏差
                self._recalculate_stats(index)
                return index
            except Exception:
                pass
        
        # 初始化默认索引
        index = {
            "version": "6.0.0",
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
            "palace": {
                "name": f"{self.agent_name}的知识宫殿",
                "floors": {
                    "main": {
                        "name": "主楼层",
                        "rooms": {}
                    }
                }
            },
            "stats": {
                "total_items": 0,
                "total_rooms": 0
            }
        }
        
        # 创建默认房间
        for room_id, room_def in self.DEFAULT_ROOMS.items():
            index["palace"]["floors"]["main"]["rooms"][room_id] = {
                "name": room_def["name"],
                "keywords": room_def["keywords"],
                "item_count": 0,
                "created": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat()
            }
            index["stats"]["total_rooms"] += 1
        
        # 创建 _inbox 房间
        index["palace"]["floors"]["main"]["rooms"]["_inbox"] = {
            "name": "待分类",
            "keywords": [],
            "item_count": 0,
            "created": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        index["stats"]["total_rooms"] += 1
        
        self._save_index(index)
        return index
    
    def _recalculate_stats(self, index: Dict):
        """从实际 room 文件重算统计数据（Z BUG-015 修复）"""
        total_items = 0
        rooms = index.get("palace", {}).get("floors", {}).get("main", {}).get("rooms", {})
        for room_id, room_info in rooms.items():
            room_data = self._load_room(room_id)
            actual_count = len(room_data.get("items", []))
            room_info["item_count"] = actual_count
            total_items += actual_count
        index["stats"]["total_items"] = total_items
        index["stats"]["total_rooms"] = len(rooms)

    def _save_index(self, index: Dict = None):
        """保存索引"""
        if index is None:
            index = self.index
        index["updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def _load_room(self, room_id: str) -> Dict:
        """加载房间数据"""
        room_file = self.rooms_dir / f"{room_id}.json"
        if room_file.exists():
            with open(room_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"room_id": room_id, "items": [], "created": datetime.now().isoformat()}
    
    def _save_room(self, room_id: str, data: Dict):
        """保存房间数据"""
        room_file = self.rooms_dir / f"{room_id}.json"
        with open(room_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_item(self, room_id: str, fact_id: str, summary: str,
                 tags: List[str] = None) -> Dict:
        """
        向房间添加知识条目
        
        Args:
            room_id: 房间 ID
            fact_id: 关联的 fact ID
            summary: 知识摘要
            tags: 标签
        
        Returns:
            添加的条目
        """
        rooms = self.index["palace"]["floors"]["main"]["rooms"]
        if room_id not in rooms:
            logger.warning(f"房间不存在: {room_id}，放入 _inbox")
            room_id = "_inbox"
        
        # 加载房间数据
        room_data = self._load_room(room_id)
        
        item = {
            "fact_id": fact_id,
            "summary": summary,
            "tags": tags or [],
            "added_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0
        }
        
        room_data["items"].append(item)
        self._save_room(room_id, room_data)
        
        # 更新索引统计
        rooms[room_id]["item_count"] = len(room_data["items"])
        rooms[room_id]["last_accessed"] = datetime.now().isoformat()
        self.index["stats"]["total_items"] += 1
        self._save_index()
        
        logger.debug(f"添加到房间 {room_id}: {fact_id}")
        return item
    
    def classify_by_keywords(self, content: str) -> str:
        """
        基于关键词匹配分类到房间（规则降级方案）
        
        Args:
            content: 知识内容
        
        Returns:
            匹配的 room_id
        """
        content_lower = content.lower()
        best_room = "_inbox"
        best_score = 0
        
        rooms = self.index["palace"]["floors"]["main"]["rooms"]
        for room_id, room_info in rooms.items():
            if room_id == "_inbox":
                continue
            
            score = 0
            for kw in room_info.get("keywords", []):
                if kw.lower() in content_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_room = room_id
        
        return best_room
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        搜索宫殿中的知识
        
        Args:
            query: 搜索关键词
            limit: 最大返回数
        """
        query_lower = query.lower()
        results = []
        
        rooms = self.index["palace"]["floors"]["main"]["rooms"]
        for room_id in rooms:
            room_data = self._load_room(room_id)
            
            for item in room_data.get("items", []):
                if query_lower in item.get("summary", "").lower():
                    results.append({
                        "room_id": room_id,
                        "room_name": rooms[room_id]["name"],
                        **item
                    })
                    
                    if len(results) >= limit:
                        return results
        
        return results
    
    def get_room_items(self, room_id: str) -> List[Dict]:
        """获取房间内的所有条目"""
        room_data = self._load_room(room_id)
        return room_data.get("items", [])
    
    def list_rooms(self) -> List[Dict]:
        """列出所有房间"""
        rooms = self.index["palace"]["floors"]["main"]["rooms"]
        return [
            {"id": rid, **rinfo}
            for rid, rinfo in rooms.items()
        ]
    
    def get_stats(self) -> Dict:
        """获取宫殿统计"""
        return {
            "agent": self.agent_name,
            "rooms": len(self.index["palace"]["floors"]["main"]["rooms"]),
            "total_items": self.index["stats"]["total_items"],
            "rooms_detail": {
                rid: rinfo["item_count"]
                for rid, rinfo in self.index["palace"]["floors"]["main"]["rooms"].items()
            }
        }
    
    def create_room(self, room_id: str, name: str, keywords: List[str] = None) -> Dict:
        """创建新房间"""
        rooms = self.index["palace"]["floors"]["main"]["rooms"]
        if room_id in rooms:
            logger.warning(f"房间已存在: {room_id}")
            return rooms[room_id]
        
        rooms[room_id] = {
            "name": name,
            "keywords": keywords or [],
            "item_count": 0,
            "created": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        self.index["stats"]["total_rooms"] += 1
        self._save_index()
        
        # 初始化房间数据文件
        self._save_room(room_id, {"room_id": room_id, "items": [], "created": datetime.now().isoformat()})
        
        logger.info(f"创建房间: {room_id} ({name})")
        return rooms[room_id]
