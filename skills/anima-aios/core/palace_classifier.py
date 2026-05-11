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
Anima AIOS v6.0 - Palace Classifier (Deferred Debounce)

宫殿分类调度器 —— 延迟防抖机制。

核心理念：等笔停了再整理。
Agent 高频工作时产生的知识片段是碎片化的，等工作告一段落后
再集中调用 LLM 批量分类，准确率最高。

调度流程：
  每 N 分钟轮询 → 有新增待分类？
    → 否：跳过
    → 是：最后写入距今 ≥ quiet_threshold？
        → 是：立即批量分类
        → 否：推迟 retry_delay 后重新检查

Author: 清禾
Date: 2026-03-23
Version: 6.0.0
"""

import os
import json
import time
import logging
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from .palace_index import PalaceIndex
except ImportError:
    from palace_index import PalaceIndex
try:
    from .fact_store import FactStore, Fact
except ImportError:
    from fact_store import FactStore, Fact

logger = logging.getLogger(__name__)


class PalaceClassifier:
    """
    宫殿分类调度器
    
    定期扫描未分类的 L3 语义记忆，通过 LLM 或关键词规则
    将其���入知识宫殿的对应房间。
    """
    
    def __init__(self, agent_name: str, facts_base: str = None,
                 config: Dict = None, llm_config: Dict = None):
        self.agent_name = agent_name
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                import sys as _s; _s.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / 'config')); from path_config import get_config
            facts_base = str(get_config().facts_base)
        self.facts_base = facts_base
        self.config = config or {}
        
        # 调度参数
        self.poll_interval = self.config.get("poll_interval_minutes", 30) * 60  # 秒
        self.quiet_threshold = self.config.get("quiet_threshold_seconds", 60)
        self.retry_delay = self.config.get("retry_delay_seconds", 60)
        
        # 组件
        self.palace = PalaceIndex(agent_name, facts_base)
        self.store = FactStore(agent_name, facts_base)
        
        # LLM 客户端
        self.llm = None
        if llm_config:
            try:
                from distill_engine import LLMClient
                self.llm = LLMClient(llm_config)
            except ImportError:
                pass
        
        # 状态
        self._classified_ids: set = set()  # 已分类的 fact_id
        self._load_classified_ids()
        self._running = False
        self._last_classify_time = 0
        
        # 引用 memory_watcher 的最后写入时间（如果可用）
        self._external_last_write_time = None
    
    def _load_classified_ids(self):
        """加载已分类的 fact_id 集合"""
        state_file = Path(self.facts_base) / self.agent_name / "palace" / ".classified_ids.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    self._classified_ids = set(json.load(f))
            except Exception:
                pass
    
    def _save_classified_ids(self):
        """保存已分类的 fact_id 集合"""
        state_file = Path(self.facts_base) / self.agent_name / "palace" / ".classified_ids.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(list(self._classified_ids), f)
    
    def set_last_write_time(self, timestamp: float):
        """设置外部的最后写入时间（由 memory_watcher 调用）"""
        self._external_last_write_time = timestamp
    
    def _get_last_write_time(self) -> float:
        """获取最后一次知识写入时间"""
        if self._external_last_write_time:
            return self._external_last_write_time
        
        # 降级：检查 L3 目录的最后修改时间
        semantic_dir = Path(self.facts_base) / self.agent_name / "facts" / "semantic"
        if semantic_dir.exists():
            files = list(semantic_dir.glob("*.md"))
            if files:
                return max(f.stat().st_mtime for f in files)
        
        return 0
    
    def get_unclassified(self) -> List[Fact]:
        """获取未分类的 L3 语义记忆"""
        all_semantics = self.store.list_facts("semantic", limit=200)
        return [f for f in all_semantics if f.fact_id not in self._classified_ids]
    
    def classify_one(self, fact: Fact) -> str:
        """
        对单条 fact 进行分类
        
        优先 LLM，降级关键词匹配。
        
        Returns:
            分类到的 room_id
        """
        # 尝试 LLM 分类
        if self.llm:
            rooms = self.palace.list_rooms()
            rooms_desc = "\n".join([
                f"- {r['id']}: {r['name']} (关键词: {', '.join(r.get('keywords', [])[:5])})"
                for r in rooms if r['id'] != '_inbox'
            ])
            
            prompt = f"""请将以下知识分类到最合适的房间。

可选房间：
{rooms_desc}

知识内容：
{fact.content[:300]}

请只回复房间 ID（如 technical、project、people、decision），不要其他内容。
如果无法确定，回复 _inbox。"""
            
            response = self.llm.call(prompt, task="palace_classify", max_tokens=20)
            room_id = response.strip().lower().replace('"', '').replace("'", "")
            
            # 验证 room_id 是否合法
            valid_rooms = {r['id'] for r in rooms}
            if room_id in valid_rooms:
                return room_id
        
        # 降级：关键词匹配
        return self.palace.classify_by_keywords(fact.content)
    
    def classify_batch(self, facts: List[Fact]) -> Dict:
        """
        批量分类
        
        Returns:
            分类统计
        """
        stats = {
            "total": len(facts),
            "classified": 0,
            "by_room": {},
            "errors": 0
        }
        
        for fact in facts:
            try:
                room_id = self.classify_one(fact)
                
                # 添加到宫殿
                summary = fact.content[:100]
                self.palace.add_item(room_id, fact.fact_id, summary, fact.tags)
                
                # 标记已分类
                self._classified_ids.add(fact.fact_id)
                
                stats["classified"] += 1
                stats["by_room"][room_id] = stats["by_room"].get(room_id, 0) + 1
                
                logger.debug(f"分类: {fact.fact_id} → {room_id}")
            except Exception as e:
                logger.warning(f"分类失败 {fact.fact_id}: {e}")
                stats["errors"] += 1
        
        # 保存状态
        self._save_classified_ids()
        
        logger.info(f"批量分类完成: {stats['classified']}/{stats['total']}，"
                     f"分布: {stats['by_room']}")
        
        return stats
    
    def poll_once(self) -> Optional[Dict]:
        """
        执行一次轮询检查
        
        实现延迟防抖逻辑：
        1. 有新增待分类知识？
        2. 最后写入距今 ≥ quiet_threshold？
        3. 是 → 立即分类；否 → 返回 None（稍后重试）
        """
        unclassified = self.get_unclassified()
        
        if not unclassified:
            logger.debug("没有待分类的知识")
            return None
        
        # 检查安静阈值
        last_write = self._get_last_write_time()
        elapsed = time.time() - last_write
        
        if elapsed < self.quiet_threshold:
            logger.debug(f"距最后写入 {elapsed:.0f}s < {self.quiet_threshold}s，推迟分类")
            return None
        
        # 安静了，执行分类
        logger.info(f"距最后写入 {elapsed:.0f}s ≥ {self.quiet_threshold}s，开始批量分类 ({len(unclassified)} 条)")
        return self.classify_batch(unclassified)
    
    def run_daemon(self):
        """
        以守护线程方式运行调度器
        """
        self._running = True
        logger.info(f"宫殿分类调度器启动 (轮询间隔: {self.poll_interval}s, "
                     f"安静阈值: {self.quiet_threshold}s)")
        
        while self._running:
            try:
                result = self.poll_once()
                
                if result is None:
                    # 没有待分类或还在写入中
                    # 如果有待分类但不够安静，用 retry_delay；否则用 poll_interval
                    unclassified = self.get_unclassified()
                    if unclassified:
                        time.sleep(self.retry_delay)
                    else:
                        time.sleep(self.poll_interval)
                else:
                    # 分类完成，等待下一个轮询周期
                    self._last_classify_time = time.time()
                    time.sleep(self.poll_interval)
                    
            except Exception as e:
                logger.error(f"调度器错误: {e}")
                time.sleep(self.poll_interval)
    
    def stop(self):
        """停止调度器"""
        self._running = False
    
    def get_status(self) -> Dict:
        """获取调度器状态"""
        return {
            "agent": self.agent_name,
            "running": self._running,
            "poll_interval_minutes": self.poll_interval / 60,
            "quiet_threshold_seconds": self.quiet_threshold,
            "retry_delay_seconds": self.retry_delay,
            "classified_count": len(self._classified_ids),
            "unclassified_count": len(self.get_unclassified()),
            "last_classify_time": datetime.fromtimestamp(self._last_classify_time).isoformat() if self._last_classify_time else None,
            "palace_stats": self.palace.get_stats()
        }


def main():
    """命令行入口"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [PalaceClassifier] %(levelname)s: %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Anima Palace Classifier - 宫殿分类调度器')
    parser.add_argument('--agent', type=str, default='', help='Agent 名称')
    parser.add_argument('--facts-base', type=str, default='/home/画像')
    parser.add_argument('--once', action='store_true', help='执行一次分类后退出')
    parser.add_argument('--status', action='store_true', help='显示状态')
    parser.add_argument('--daemon', action='store_true', help='守护进程模式')
    args = parser.parse_args()
    
    agent = args.agent or os.getenv("ANIMA_AGENT_NAME", "unknown")
    
    classifier = PalaceClassifier(agent, args.facts_base)
    
    if args.status:
        print(json.dumps(classifier.get_status(), ensure_ascii=False, indent=2))
        return
    
    if args.once:
        result = classifier.poll_once()
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 强制分类（忽略防抖）
            unclassified = classifier.get_unclassified()
            if unclassified:
                result = classifier.classify_batch(unclassified)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("没有待分类的知识")
        return
    
    if args.daemon:
        classifier.run_daemon()
        return
    
    # 默认：执行一次
    result = classifier.poll_once()
    print(json.dumps(result or {"message": "无待分类知识"}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
