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
Anima AIOS v6.0 - Distill Engine

L2→L3 提炼引擎：从情景记忆中提取语义知识。
引入 LLM 进行质量评估、去重分析和知识提炼。

Author: 清禾
Date: 2026-03-23
Version: 6.0.0
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import sys
try:
    from .fact_store import FactStore, Fact, QualityGrade
except ImportError:
    from fact_store import FactStore, Fact, QualityGrade

logger = logging.getLogger(__name__)


class LLMClient:
    """
    LLM 调用客户端（v6.1 重写）
    
    调用优先级：
    1. OpenAI 兼容 API 直连（配置 base_url + api_key）
    2. openclaw agent 命令调用（降级方案）
    3. 返回空字符串（规则模式降级）
    
    支持任何 OpenAI 兼容 API（百炼、OpenAI、Ollama、vLLM、LiteLLM 等）
    
    配置示例（~/.anima/config/anima_config.json）：
    {
        "llm": {
            "base_url": "https://api.openai.com/v1",
            "api_key": "sk-xxx",
            "default_model": "gpt-4o-mini"
        }
    }
    
    更多示例：
    - 百炼：base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", model="qwen-plus"
    - Ollama：base_url="http://localhost:11434/v1", model="llama3", api_key="ollama"
    - vLLM：base_url="http://localhost:8000/v1", model="your-model", api_key="token"
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.provider = self.config.get("provider", "current_agent")
        self.models = self.config.get("models", {})
        self._agent_name = self._detect_agent_name()
        
        # 尝试从全局配置文件加载 LLM 配置
        if not self.config.get("base_url"):
            self._load_config_file()
    
    def _load_config_file(self):
        """从 ~/.anima/config/anima_config.json 加载 LLM 配置"""
        config_file = Path(os.path.expanduser("~/.anima/config/anima_config.json"))
        if config_file.exists():
            try:
                import json as _json
                with open(config_file) as f:
                    cfg = _json.load(f)
                llm_cfg = cfg.get("llm", {})
                if llm_cfg.get("base_url"):
                    self.config.update(llm_cfg)
                    self.provider = llm_cfg.get("provider", self.provider)
            except Exception:
                pass
    
    @staticmethod
    def _detect_agent_name() -> str:
        """从环境变量或 workspace 路径自动检测当前 Agent 名称（委托给公共模块）"""
        try:
            from .agent_resolver import resolve_agent_name
        except ImportError:
            from agent_resolver import resolve_agent_name
        return resolve_agent_name()
    
    @staticmethod
    def _strip_ansi_and_logs(text: str) -> str:
        """过滤 ANSI 转义码和 [plugins] 日志行，只保留 LLM 实际响应"""
        import re
        lines = text.strip().split('\n')
        clean_lines = []
        for line in lines:
            clean = re.sub(r'\x1b\[[0-9;]*m', '', line)
            if clean.startswith('[plugins]') or clean.startswith('[gateway]'):
                continue
            clean_lines.append(clean)
        return '\n'.join(clean_lines).strip()
    
    def _call_api(self, prompt: str, task: str = "default", max_tokens: int = 500) -> str:
        """通过 OpenAI 兼容 API 直连调用 LLM"""
        base_url = self.config.get("base_url")
        api_key = self.config.get("api_key") or os.getenv("ANIMA_LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")
        
        if not base_url or not api_key:
            return ""
        
        model = self.config.get("models", {}).get(task) or self.config.get("default_model", "")
        
        import urllib.request
        import json as _json
        
        url = f"{base_url.rstrip('/')}/chat/completions"
        payload = _json.dumps({
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }).encode("utf-8")
        
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        })
        
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = _json.loads(resp.read().decode("utf-8"))
                return data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.warning(f"API 直连调用失败: {e}")
            return ""
    
    def _call_openclaw(self, prompt: str) -> str:
        """通过 openclaw agent 命令调用 LLM（降级方案）"""
        try:
            cmd = ["openclaw", "agent", "--message", prompt]
            if self._agent_name:
                cmd.extend(["--agent", self._agent_name])
            
            result = subprocess.run(
                cmd,
                capture_output=True, text=True, timeout=60
            )
            if result.returncode == 0:
                response = self._strip_ansi_and_logs(result.stdout)
                if response:
                    return response
        except subprocess.TimeoutExpired:
            logger.warning("openclaw agent 调用超时")
        except FileNotFoundError:
            logger.debug("openclaw 命令未找到")
        except Exception as e:
            logger.warning(f"openclaw agent 调用异常: {e}")
        return ""
    
    def call(self, prompt: str, task: str = "default", max_tokens: int = 500) -> str:
        """
        调用 LLM（自动选择最佳通道）
        
        优先级：API 直连 → openclaw agent → 空字符串（规则降级）
        
        Args:
            prompt: 提示词
            task: 任务类型（quality_assess / dedup_analyze / palace_classify / distill）
            max_tokens: 最大输出 token 数
        
        Returns:
            LLM 响应文本，失败返回空字符串
        """
        # 1. 优先：API 直连
        response = self._call_api(prompt, task, max_tokens)
        if response:
            return response
        
        # 2. 降级：openclaw agent
        response = self._call_openclaw(prompt)
        if response:
            return response
        
        # 3. 最终降级：规则模式
        logger.warning(f"LLM 全部通道失败，降级为规则模式 (task={task})")
        return ""


class DistillEngine:
    """
    L2→L3 提炼引擎
    
    工作流程：
    1. 扫描 L2 中 quality=pending 的 facts
    2. LLM 质量评估（S/A/B/C）
    3. B 级及以上的 facts 进入提炼候选
    4. LLM 去重检查（与已有 L3 对比）
    5. LLM 知识提炼（提取核心知识）
    6. 写入 L3 语义记忆
    """
    
    def __init__(self, agent_name: str, facts_base: str = None,
                 llm_config: Dict = None):
        self.agent_name = agent_name
        if facts_base is None:
            try:
                from ..config.path_config import get_config
            except ImportError:
                import sys as _s; _s.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / 'config')); from path_config import get_config
            facts_base = str(get_config().facts_base)
        self.facts_base = facts_base
        self.store = FactStore(agent_name, facts_base)
        self.llm = LLMClient(llm_config)
        
        # 提炼配置
        self.min_quality = "B"  # 最低提炼质量
        self.quality_order = {"S": 4, "A": 3, "B": 2, "C": 1, "pending": 0}
    
    def assess_quality(self, fact: Fact) -> QualityGrade:
        """
        LLM 质量评估
        
        Args:
            fact: 待评估的 L2 fact
        
        Returns:
            质量等级 S/A/B/C
        """
        prompt = f"""请评估以下 AI Agent 记忆片段的质量，从 S/A/B/C 四个等级中选择一个。

评估标准：
- S（极高）：包含重要决策、架构设计、关键教训，对长期成长有重大价值
- A（高）：包含有价值的技术知识、项目经验、问题解决方案
- B（中）：包含有用的日常记录、工作进展、学习笔记
- C（低）：琐碎信息、重复内容、临时备忘

记忆内容：
{fact.content[:500]}

请只回复一个字母（S/A/B/C），不要其他内容。"""
        
        response = self.llm.call(prompt, task="quality_assess", max_tokens=5)
        
        grade = response.strip().upper()
        if grade in ("S", "A", "B", "C"):
            return grade
        
        # LLM 降级：规则评估
        return self._rule_based_quality(fact)
    
    def _rule_based_quality(self, fact: Fact) -> QualityGrade:
        """规则降级：基于内容长度和关键词评估质量"""
        content = fact.content
        length = len(content)
        
        # 关键词权重
        high_value_keywords = ["决策", "架构", "设计", "教训", "方案", "原则", "铁律",
                               "decision", "architecture", "design", "lesson", "principle"]
        mid_value_keywords = ["解决", "修复", "实现", "学到", "发现", "优化",
                              "fix", "implement", "learn", "optimize"]
        
        score = 0
        for kw in high_value_keywords:
            if kw in content:
                score += 3
        for kw in mid_value_keywords:
            if kw in content:
                score += 1
        
        if length > 200:
            score += 2
        elif length > 100:
            score += 1
        
        if score >= 6:
            return "S"
        elif score >= 4:
            return "A"
        elif score >= 2:
            return "B"
        else:
            return "C"
    
    def check_duplicate(self, content: str, existing_semantics: List[Fact]) -> Tuple[bool, Optional[str]]:
        """
        LLM 去重检查
        
        Args:
            content: 待检查的内容
            existing_semantics: 已有的 L3 语义记忆列表
        
        Returns:
            (是否重复, 重复的 fact_id)
        """
        if not existing_semantics:
            return False, None
        
        # 取最近的 20 条 L3 做对比
        recent = existing_semantics[:20]
        existing_summaries = "\n".join([
            f"[{f.fact_id}] {f.content[:100]}" for f in recent
        ])
        
        prompt = f"""请判断以下新内容是否与已有知识重复或高度相似。

新内容：
{content[:300]}

已有知识：
{existing_summaries}

如果重复或高度相似，回复 "DUPLICATE: <fact_id>"。
如果不重复，回复 "UNIQUE"。
只回复上述格式，不要其他内容。"""
        
        response = self.llm.call(prompt, task="dedup_analyze", max_tokens=50)
        
        if response.startswith("DUPLICATE:"):
            dup_id = response.replace("DUPLICATE:", "").strip()
            return True, dup_id
        
        # LLM 降级：简单字符串匹配
        if not response:
            return self._rule_based_dedup(content, existing_semantics)
        
        return False, None
    
    def _rule_based_dedup(self, content: str, existing: List[Fact]) -> Tuple[bool, Optional[str]]:
        """规则降级：基于关键词重叠率去重"""
        content_words = set(content.lower().split())
        
        for fact in existing[:20]:
            fact_words = set(fact.content.lower().split())
            if not fact_words:
                continue
            overlap = len(content_words & fact_words) / max(len(content_words), 1)
            if overlap > 0.7:
                return True, fact.fact_id
        
        return False, None
    
    def distill(self, facts: List[Fact]) -> Optional[str]:
        """
        LLM 知识提炼：从多条 L2 情景记忆中提取核心知识
        
        Args:
            facts: L2 情景记忆列表
        
        Returns:
            提炼后的知识内容，如果无法提炼则返回 None
        """
        if not facts:
            return None
        
        # 单条直接提取
        if len(facts) == 1:
            content = facts[0].content
            prompt = f"""请从以下 AI Agent 的工作记录中提取核心知识点。
去掉时间、人物等细节，保留可复用的知识、经验、教训或决策。
用简洁的语言总结，不超过 200 字。

原始记录：
{content[:500]}

请直接输出提炼后的知识，不要加前缀。"""
        else:
            combined = "\n---\n".join([f.content[:300] for f in facts[:5]])
            prompt = f"""请从以下多条 AI Agent 工作记录中提炼核心知识。
找出共同主题、规律或教训，用简洁的语言总结。不超过 300 字。

记录：
{combined}

请直接输出提炼后的知识，不要加前缀。"""
        
        response = self.llm.call(prompt, task="distill", max_tokens=400)
        
        if response and len(response) > 10:
            return response
        
        # LLM 降级：取最长的一条作为知识
        if facts:
            longest = max(facts, key=lambda f: len(f.content))
            return longest.content[:300]
        
        return None
    
    def run(self, batch_size: int = 20, dry_run: bool = False) -> Dict:
        """
        执行一轮提炼
        
        Args:
            batch_size: 每轮处理的最大 fact 数
            dry_run: 仅评估不写入
        
        Returns:
            提炼统计
        """
        stats = {
            "scanned": 0,
            "assessed": 0,
            "quality_distribution": {"S": 0, "A": 0, "B": 0, "C": 0},
            "distilled": 0,
            "duplicates_skipped": 0,
            "errors": 0
        }
        
        # 1. 扫描 pending 的 L2 facts
        pending_facts = self.store.list_facts("episodic", quality="pending", limit=batch_size)
        stats["scanned"] = len(pending_facts)
        
        if not pending_facts:
            logger.info("没有待处理的 L2 facts")
            return stats
        
        logger.info(f"扫描到 {len(pending_facts)} 条待评估的 L2 facts")
        
        # 2. 获取已有 L3 用于去重
        existing_semantics = self.store.list_facts("semantic", limit=50)
        
        # 3. 逐条处理
        candidates = []
        
        for fact in pending_facts:
            try:
                # 质量评估
                quality = self.assess_quality(fact)
                stats["assessed"] += 1
                stats["quality_distribution"][quality] += 1
                
                # 更新质量
                if not dry_run:
                    self.store.update_quality(fact.fact_id, "episodic", quality)
                
                logger.debug(f"质量评估: {fact.fact_id} → {quality}")
                
                # B 级及以上进入候选
                if self.quality_order.get(quality, 0) >= self.quality_order[self.min_quality]:
                    candidates.append(fact)
                    
            except Exception as e:
                logger.warning(f"处理 fact 失败 {fact.fact_id}: {e}")
                stats["errors"] += 1
        
        logger.info(f"质量评估完成: {stats['quality_distribution']}，{len(candidates)} 条进入提炼候选")
        
        # 4. 对候选逐条提炼
        for fact in candidates:
            try:
                # 提炼知识
                knowledge = self.distill([fact])
                if not knowledge:
                    continue
                
                # 去重检查
                is_dup, dup_id = self.check_duplicate(knowledge, existing_semantics)
                if is_dup:
                    logger.debug(f"跳过重复: {fact.fact_id} ≈ {dup_id}")
                    stats["duplicates_skipped"] += 1
                    continue
                
                # 写入 L3
                if not dry_run:
                    new_fact = self.store.create_semantic(
                        content=knowledge,
                        source_facts=[fact.fact_id],
                        tags=fact.tags + ["distilled"],
                        quality=fact.quality
                    )
                    # 加入已有列表（后续去重用）
                    existing_semantics.insert(0, new_fact)
                    logger.info(f"提炼完成: {fact.fact_id} → {new_fact.fact_id}")
                
                stats["distilled"] += 1
                
            except Exception as e:
                logger.warning(f"提炼失败 {fact.fact_id}: {e}")
                stats["errors"] += 1
        
        logger.info(f"提炼完成: 扫描 {stats['scanned']}，评估 {stats['assessed']}，"
                     f"提炼 {stats['distilled']}，跳过重复 {stats['duplicates_skipped']}")
        
        return stats


def main():
    """命令行入口"""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [DistillEngine] %(levelname)s: %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Anima Distill Engine - L2→L3 知识提炼')
    parser.add_argument('--agent', type=str, default='', help='Agent 名称')
    parser.add_argument('--facts-base', type=str, default='/home/画像', help='Facts 基础路径')
    parser.add_argument('--batch-size', type=int, default=20, help='每轮处理数量')
    parser.add_argument('--dry-run', action='store_true', help='仅评估不写入')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    args = parser.parse_args()
    
    agent_name = args.agent or os.getenv("ANIMA_AGENT_NAME", "unknown")
    facts_base = os.getenv("ANIMA_FACTS_BASE", args.facts_base)
    
    engine = DistillEngine(agent_name, facts_base)
    
    if args.stats:
        episodic_count = engine.store.count("episodic")
        semantic_count = engine.store.count("semantic")
        pending = engine.store.list_facts("episodic", quality="pending")
        print(f"Agent: {agent_name}")
        print(f"L2 情景记忆: {episodic_count}")
        print(f"L3 语义记忆: {semantic_count}")
        print(f"待评估: {len(pending)}")
        return
    
    stats = engine.run(batch_size=args.batch_size, dry_run=args.dry_run)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
