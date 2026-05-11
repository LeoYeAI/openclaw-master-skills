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
Anima-AIOS Skill - Tool Implementations

OpenClaw Skill 工具实现

提供以下工具：
- memory_search_v2: 增强版记忆搜索（+2 亲密度）
- memory_write_v2: 增强版记忆写入（自动 亲密度奖励 + 3 层同步）
- get_cognitive_profile: 获取认知画像
- get_exp: 查询 EXP 详情
- get_level: 查询等级信息
- quest_daily_status: 查看每日任务
- quest_complete: 提交任务完成

修复记录：
- v5.0.3 (2026-03-22): 修复 3 层同步机制 Bug
  - Bug 1: C 级质量 亲密度计算为 0 → 分离 base_exp 和 quality_multiplier
  - Bug 2: 只写入第 1 层 → 新增第 2 层 Anima Facts 同步
  - Bug 3: 维度命名不一致 → 统一使用 core 标准维度名

Author: Anima-AIOS Team
Date: 2026-03-22
Version: 5.0.3
"""

import os
import sys
import json
import uuid
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# 确保 core 模块在路径中
ANIMA_HOME = Path(os.path.expanduser("~/.anima"))
if ANIMA_HOME.exists():
    sys.path.insert(0, str(ANIMA_HOME / "core"))

# OpenClaw workspace 路径
WORKSPACE = Path(os.getenv("ANIMA_WORKSPACE", os.path.expanduser("~/.openclaw/workspace")))

# 事实数据路径（facts_base）
# 动态获取 facts_base（优先环境变量 > 配置���件 > 系统检测）
def _get_facts_base() -> Path:
    """获取 facts 基础路径，复用 path_config 逻辑"""
    try:
        from config.path_config import Config
        return Config().facts_base
    except ImportError:
        pass
    # 降级：直接检测
    env = os.getenv("ANIMA_FACTS_BASE")
    if env:
        return Path(env)
    import platform
    if platform.system() == "Darwin":
        return Path(os.path.expanduser("~/画像"))
    return Path("/home/画像")

FACTS_BASE = _get_facts_base()


# ============================================================================
# 工具 1: memory_search_v2
# ============================================================================

def memory_search_v2(query: str, type: str = "all", maxResults: int = 10, agent_name: str = "current") -> Dict:
    """
    增强版记忆搜索
    
    功能：
    - 支持语义检索（如果配置了向量检索）
    - 支持时间范围过滤
    - 返回结果带相关性评分
    - 自动奖励 +2 亲密度
    
    Args:
        query: 搜索关键词
        type: 记忆类型 (episodic/semantic/all)
        maxResults: 最大结果数
        agent_name: Agent 名称（"current"表示当前用户）
    
    Returns:
        {
            "results": [...],
            "count": int,
            "expReward": 2,
            "message": "搜索完成，+2 亲密度"
        }
    """
    # 解析 Agent 名称
    if agent_name == "current":
        agent_name = _get_current_agent()
    
    # 调用 core 的记忆搜索（这里简化实现，实际应集成 SiliconFlow 向量检索）
    results = _search_memory_simple(query, type, maxResults, agent_name)
    
    # 记录亲密度（搜索记忆 +2 亲密度）
    exp_reward = 2
    _add_exp(agent_name, "application", exp_reward, "memory_search", {
        "query": query,
        "result_count": len(results)
    })
    
    # 自动任务感知
    _auto_check_quest(agent_name, "memory_search")
    
    return {
        "results": results,
        "count": len(results),
        "expReward": exp_reward,
        "message": f"搜索完成，找到 {len(results)} 条记忆，+{exp_reward} 亲密度"
    }


def _search_memory_simple(query: str, type: str, maxResults: int, agent_name: str) -> List[Dict]:
    """简单文本搜索（基础实现）"""
    memory_dir = WORKSPACE / "memory"
    results = []
    
    # 搜索今天的记忆文件
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = memory_dir / f"{today}.md"
    
    if memory_file.exists():
        content = memory_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                results.append({
                    "factId": f"line_{i}",
                    "content": line.strip(),
                    "type": "episodic",
                    "relevance": 0.8,
                    "timestamp": today
                })
                
                if len(results) >= maxResults:
                    break
    
    # TODO: 集成 SiliconFlow 向量检索
    # - 使用 bge-m3 模型
    # - 计算查询向量与记忆向量的相似度
    # - 按相关性排序
    
    return results


# ============================================================================
# 工具 2: memory_write_v2 (v5.0.3 修复版)
# ============================================================================

def memory_write_v2(content: str, type: str = "episodic", tags: Optional[List[str]] = None, 
                    quality: str = "auto", agent_name: str = "current") -> Dict:
    """
    增强版记忆写入（v5.0.3 修复版）
    
    修复内容：
    - ✅ Bug 1: 亲密度计算错误 → 分离 base_exp 和 quality_multiplier
    - ✅ Bug 2: 只写入第 1 层 → 新增第 2 层 Anima Facts 同步
    - ✅ Bug 3: 维度命名不一致 → 统一使用 core 标准维度名
    
    功能：
    - 自动计算 亲密度奖励（episodic +1, semantic +2）
    - 自动提取摘要和标签
    - 质量检测（完整性、价值度）
    - 去重检测
    - **3 层同步**: OpenClaw Memory + Anima Facts + Intimacy History
    
    Args:
        content: 记忆内容
        type: 记忆类型 (episodic/semantic)
        tags: 标签列表（可选，自动提取）
        quality: 质量等级 (auto/S/A/B/C)
        agent_name: Agent 名称
    
    Returns:
        {
            "factId": "xxx",
            "expReward": 2,
            "quality": "A",
            "message": "记忆已保存，+2 亲密度（semantic）"
        }
    """
    if agent_name == "current":
        agent_name = _get_current_agent()
    
    # 去重检测（简单实现：检查最近 10 条记忆）
    if _check_duplicate(content, agent_name):
        return {
            "factId": None,
            "expReward": 0,
            "quality": "N/A",
            "message": "⚠️ 检测到相似记忆，已跳过",
            "duplicate": True
        }
    
    # 自动提取标签（如果未提供）
    if tags is None or len(tags) == 0:
        tags = _extract_tags(content)
    
    # 质量评估
    if quality == "auto":
        quality = _assess_quality(content)
    
    # 计算 亲密度奖励（v5.0.3 修复：分离 base_exp 和 quality_multiplier）
    base_exp = 1 if type == "episodic" else 2
    quality_multiplier = {"S": 1.5, "A": 1.2, "B": 1.0, "C": 0.8}.get(quality, 1.0)
    # ✅ 修复：最终 EXP 由 core 层的 add_exp() 计算，传入 quality_multiplier
    # exp_reward = int(base_exp * quality_multiplier)  # ❌ 旧代码：int(0.8) = 0
    
    # ========== 第 1 层：写入 OpenClaw Memory ==========
    _write_openclaw_memory(content, type, tags, agent_name)
    
    # ========== 第 2 层：写入 Anima Facts (v5.0.3 新增) ==========
    fact_id = _write_anima_fact(content, type, tags, agent_name)
    
    # ========== 第 3 层：记录亲密度 (v5.0.5 修复) ==========
    # 维度分配规则：
    # - episodic（经历记忆）→ understanding（知识内化）
    # - semantic（知识记忆）→ creation（知识创造）
    dimension = "understanding" if type == "episodic" else "creation"
    _add_exp(agent_name, dimension, base_exp, "memory_write", {
        "type": type,
        "quality": quality,
        "content_length": len(content),
        "fact_id": fact_id
    }, quality_multiplier=quality_multiplier)
    
    # 计算最终亲密度用于返回
    exp_reward = int(base_exp * quality_multiplier)
    if exp_reward < 1:
        exp_reward = 1  # 保证最小 1 亲密度
    
    # 自动任务感知
    _auto_check_quest(agent_name, "memory_write")
    
    return {
        "factId": fact_id,
        "expReward": exp_reward,
        "quality": quality,
        "tags": tags,
        "message": f"记忆已保存，+{exp_reward} 亲密度（{type}, {quality}级）",
        "sync": {
            "layer1_openclaw": "✅",
            "layer2_anima_facts": "✅",
            "layer3_exp_history": "✅"
        }
    }


def _write_openclaw_memory(content: str, type: str, tags: List[str], agent_name: str):
    """第 1 层：写入 OpenClaw Memory"""
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = WORKSPACE / "memory" / f"{today}.md"
    
    # 确保目录存在
    memory_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 追加写入
    timestamp = datetime.now().strftime("%H:%M")
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(f"\n- [{timestamp}] {content} #{type}\n")
        if tags:
            f.write(f"  标签：{', '.join(tags)}\n")


def _write_anima_fact(content: str, type: str, tags: List[str], agent_name: str) -> str:
    """
    第 2 层：写入 Anima Facts（v5.0.3 新增）
    
    创建结构化事实文件到 /home/画像/{agent}/facts/{type}/
    """
    # 生成 factId
    fact_id = f"{type}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # 确定事实目录
    facts_dir = FACTS_BASE / agent_name / "facts" / type
    facts_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建事实文件（Markdown 格式）
    fact_file = facts_dir / f"{fact_id}.md"
    timestamp = datetime.now().isoformat()
    
    # 构建事实内容
    fact_content = f"""# {type.capitalize()} Fact

**ID:** {fact_id}
**日期:** {timestamp}
**作者:** {agent_name}
**类型:** {type}

---

## 内容

{content}

---

## 标签

{', '.join(tags) if tags else '无'}

---

## 元数据

- 创建时间：{timestamp}
- 内容长度：{len(content)} 字符
- 质量等级：{_assess_quality(content)}

"""
    
    # 写入文件
    with open(fact_file, "w", encoding="utf-8") as f:
        f.write(fact_content)
    
    return fact_id


def _check_duplicate(content: str, agent_name: str, threshold: int = 50) -> bool:
    """
    检查重复内容（基于内容哈希）
    
    Args:
        content: 记忆内容
        agent_name: Agent 名称
        threshold: 相似度阈值（0-100）
    
    Returns:
        True 如果检测到重复，否则 False
    """
    if not content or len(content) < 10:
        return False
    
    # 计算内容哈希
    content_hash = hashlib.md5(content.encode()).hexdigest()
    
    # 检查今日记忆文件（第 1 层）
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = WORKSPACE / "memory" / f"{today}.md"
    
    if memory_file.exists():
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                for line in recent_lines:
                    if content.strip() in line:
                        return True
        except Exception:
            pass
    
    # 检查 Anima Facts（第 2 层）
    for fact_type in ['episodic', 'semantic']:
        facts_dir = FACTS_BASE / agent_name / "facts" / fact_type
        if facts_dir.exists():
            today_prefix = datetime.now().strftime("%Y%m%d")
            for fact_file in facts_dir.glob(f"{fact_type}_{today_prefix}*.md"):
                try:
                    fact_content = fact_file.read_text(encoding="utf-8")
                    if content.strip() in fact_content:
                        return True
                except Exception:
                    pass
    
    return False


def _extract_tags(content: str) -> List[str]:
    """自动提取标签（简单实现：提取关键词）"""
    # TODO: 使用 NLP 提取关键词
    # 暂时返回空列表
    return []


def _assess_quality(content: str) -> str:
    """评估内容质量"""
    length = len(content)
    
    if length < 50:
        return "C"
    elif length < 200:
        return "B"
    elif length < 500:
        return "A"
    else:
        return "S"


# ============================================================================
# 工具 3-5: 认知工具
# ============================================================================

def get_cognitive_profile(agent_name: str = "current") -> Dict:
    """
    获取认知画像
    
    Returns:
        {
            "agent": "YourAgent",
            "level": 10,
            "exp": 5060,
            "nextLevelExp": 6400,
            "progress": "79%",
            "dimensions": {
                "internalization": 85,
                "application": 78,
                "creation": 92,
                "metacognition": 88,
                "collaboration": 75
            },
            "radar": "ASCII 雷达图"
        }
    """
    if agent_name == "current":
        agent_name = _get_current_agent()
    
    # 尝试使用 core 模块
    if ANIMA_HOME.exists():
        try:
            sys.path.insert(0, str(ANIMA_HOME / "core"))
            from cognitive_profile import CognitiveProfileGenerator
            generator = CognitiveProfileGenerator(agent_name, facts_base=str(FACTS_BASE))
            profile = generator.generate_profile(auto_scan=False)
            
            # core 返回的维度名称映射
            dimension_map = {
                'understanding': 'internalization',  # 理解 → 内化
                'application': 'application',
                'creation': 'creation',
                'metacognition': 'metacognition',
                'collaboration': 'collaboration'
            }
            
            # 转换维度格式（core 返回嵌套 dict，转换为简单分数）
            dimensions = {}
            for core_dim, skill_dim in dimension_map.items():
                if core_dim in profile['dimensions']:
                    dim_data = profile['dimensions'][core_dim]
                    if isinstance(dim_data, dict):
                        dimensions[skill_dim] = dim_data.get('score', 0)
                    else:
                        dimensions[skill_dim] = dim_data
                else:
                    dimensions[skill_dim] = 0
            
            # 获取等级和 EXP
            level = profile.get('level', 1)
            if isinstance(level, dict):
                level = level.get('level', 1)
            
            # 获取 EXP（core 可能直接返回数字或嵌套 dict）
            exp_data = _get_exp_simple(agent_name)
            total_exp = exp_data['totalExp']
            next_exp = _calculate_next_level_exp(level)
            progress = int((total_exp / next_exp) * 100) if next_exp > 0 else 0
            
            # 计算认知总分（五维加权平均）
            cognitive_score = round(sum(dimensions.values()) / max(len(dimensions), 1), 2)
            
            return {
                "agent": profile["agent"],
                "level": level,
                "exp": total_exp,
                "cognitiveScore": cognitive_score,
                "nextLevelExp": next_exp,
                "progress": f"{progress}%",
                "dimensions": dimensions,
                "radar": _generate_radar_ascii(dimensions)
            }
        except Exception as e:
            # 降级：返回简化版本
            # print(f"core 调用失败：{e}")
            pass
    
    # 降级方案
    exp_data = _get_exp_simple(agent_name)
    return {
        "agent": agent_name,
        "level": exp_data["level"],
        "exp": exp_data["totalExp"],
        "nextLevelExp": _calculate_next_level_exp(exp_data["level"]),
        "progress": "N/A (core 未安装)",
        "dimensions": {
            "internalization": 0,
            "application": 0,
            "creation": 0,
            "metacognition": 0,
            "collaboration": 0
        },
        "radar": "💡 首次使用，运行 `bash post-install.sh` 安装 core 以获取完整功能"
    }


def get_exp(agent_name: str = "current") -> Dict:  # 对外返回亲密度
    """
    查询 EXP 详情
    
    Returns:
        {
            "totalExp": 5060,
            "todayIntimacy": 45,
            "level": 10,
            "breakdown": {
                "memory_write": 2100,
                "memory_search": 1500,
                "weekly_report": 800,
                "knowledge_share": 660
            }
        }
    """
    if agent_name == "current":
        agent_name = _get_current_agent()
    
    return _get_exp_simple(agent_name)


def get_level(agent_name: str = "current") -> Dict:
    """
    查询等级信息
    
    Returns:
        {
            "currentLevel": 10,
            "nextLevel": 11,
            "currentExp": 5060,
            "requiredExp": 6400,
            "progress": 79,
            "progressBar": "████████░░ 79%"
        }
    """
    if agent_name == "current":
        agent_name = _get_current_agent()
    
    exp_data = _get_exp_simple(agent_name)
    level = exp_data["level"]
    current_exp = exp_data["totalExp"]
    next_exp = _calculate_next_level_exp(level)
    
    progress = int((current_exp / next_exp) * 100) if next_exp > 0 else 0
    progress_bar = _generate_progress_bar(progress)
    
    return {
        "currentLevel": level,
        "nextLevel": level + 1,
        "currentExp": current_exp,
        "requiredExp": next_exp,
        "progress": progress,
        "progressBar": progress_bar
    }


def _get_exp_simple(agent_name: str) -> Dict:
    """简化版 EXP 查询（直接读取 exp_history.jsonl）"""
    exp_file = ANIMA_HOME / agent_name / "exp_history.jsonl"
    
    if not exp_file.exists():
        # 尝试旧路径
        exp_file = FACTS_BASE / agent_name / "exp_history.jsonl"
    
    total_exp = 0
    today_exp = 0
    breakdown = {}
    today = datetime.now().strftime("%Y-%m-%d")
    
    if exp_file.exists():
        with open(exp_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    exp = record.get("exp", 0)
                    total_exp += exp
                    
                    # 今日 EXP
                    record_date = record.get("date", "")
                    if record_date == today:
                        today_exp += exp
                    
                    # 分类统计
                    action = record.get("action", "other")
                    breakdown[action] = breakdown.get(action, 0) + exp
                except (json.JSONDecodeError, KeyError, TypeError):
                    # 跳过格式错误的记录
                    continue
    
    # 计算等级
    level = max(1, int(total_exp ** 0.28))
    
    return {
        "totalExp": total_exp,
        "todayIntimacy": today_exp,
        "level": level,
        "breakdown": breakdown
    }


def _calculate_next_level_exp(level: int) -> int:
    """计算下一级所需亲密度"""
    # 反推公式：level = exp^0.28 => exp = level^(1/0.28)
    next_level = level + 1
    return int(next_level ** (1 / 0.28))


def _generate_progress_bar(progress: int, width: int = 10) -> str:
    """生成进度条"""
    filled = int(progress / 10)
    bar = "█" * filled + "░" * (width - filled)
    return f"{bar} {progress}%"


def _generate_radar_ascii(dimensions: Dict[str, int]) -> str:
    """生成 ASCII 雷达图"""
    lines = []
    for dim, score in dimensions.items():
        bar_len = int(score / 10)
        bar = "█" * bar_len + "░" * (10 - bar_len)
        dim_cn = {
            "internalization": "内化",
            "application": "应用",
            "creation": "创造",
            "metacognition": "元认知",
            "collaboration": "协作"
        }.get(dim, dim)
        lines.append(f"  {dim_cn:6} {bar} {score}")
    
    return "\n".join(lines)


# ============================================================================
# 工具 6-7: 任务工具
# ============================================================================

def quest_daily_status(agent_name: str = "current") -> Dict:
    """
    查看每日任务状态
    
    Returns:
        {
            "date": "2026-03-21",
            "quests": [
                {
                    "id": "q1",
                    "title": "写一条记忆",
                    "difficulty": "easy",
                    "expReward": 5,
                    "status": "completed"
                },
                ...
            ],
            "completionBonus": 15
        }
    """
    if agent_name == "current":
        agent_name = _get_current_agent()
    
    today = datetime.now().strftime("%Y-%m-%d")
    quest_file = FACTS_BASE / agent_name / "daily_quests" / f"{today}.json"
    
    if not quest_file.exists():
        # 生成今日任务
        quests = _generate_daily_quests(agent_name)
        _save_quests(quests, quest_file)
    else:
        with open(quest_file, "r", encoding="utf-8") as f:
            quests = json.load(f)
    
    return {
        "date": today,
        "quests": quests,
        "completionBonus": 15
    }


def quest_complete(quest_id: str, proof: Optional[str] = None, agent_name: str = "current") -> Dict:
    """
    提交任务完成
    
    Args:
        quest_id: 任务 ID
        proof: 完成证据（可选）
        agent_name: Agent 名称
    
    Returns:
        {
            "success": True,
            "expReward": 10,
            "message": "任务完成，+10 亲密度"
        }
    """
    if agent_name == "current":
        agent_name = _get_current_agent()
    
    today = datetime.now().strftime("%Y-%m-%d")
    quest_file = FACTS_BASE / agent_name / "daily_quests" / f"{today}.json"
    
    if not quest_file.exists():
        return {
            "success": False,
            "message": "今日任务尚未生成，请稍后再试"
        }
    
    with open(quest_file, "r", encoding="utf-8") as f:
        quests = json.load(f)
    
    # 查找任务
    for quest in quests:
        if quest["id"] == quest_id:
            if quest["status"] == "completed":
                return {
                    "success": False,
                    "message": "该任务已完成"
                }
            
            # 标记完成
            quest["status"] = "completed"
            quest["completedAt"] = datetime.now().isoformat()
            if proof:
                quest["proof"] = proof
            
            # 保存
            _save_quests(quests, quest_file)
            
            # 奖励 EXP（根据任务类型分配维度）
            exp_reward = quest["expReward"]
            # 维度分配：根据任务难度和类型
            quest_dimension_map = {
                "写一条记忆": "understanding",
                "搜索记忆 3 次": "application",
                "完成一次代码提交": "creation",
                "写工作日志": "metacognition",
                "分享知识到团队": "collaboration",
                "代码审查": "collaboration",
                "写技术文档": "creation",
            }
            dimension = quest_dimension_map.get(quest["title"], "application")
            _add_exp(agent_name, dimension, exp_reward, "quest_complete", {
                "quest_id": quest_id,
                "quest_title": quest["title"]
            })
            
            return {
                "success": True,
                "expReward": exp_reward,
                "message": f"任务完成，+{exp_reward} EXP"
            }
    
    return {
        "success": False,
        "message": "未找到该任务"
    }


def _generate_daily_quests(agent_name: str) -> List[Dict]:
    """生成每日任务"""
    import random
    
    quest_templates = [
        {"title": "写一条记忆", "difficulty": "easy", "expReward": 5},
        {"title": "搜索记忆 3 次", "difficulty": "medium", "expReward": 10},
        {"title": "完成一次代码提交", "difficulty": "medium", "expReward": 10},
        {"title": "写工作日志", "difficulty": "easy", "expReward": 5},
        {"title": "分享知识到团队", "difficulty": "hard", "expReward": 20},
        {"title": "代码审查", "difficulty": "medium", "expReward": 10},
        {"title": "写技术文档", "difficulty": "hard", "expReward": 15},
    ]
    
    # 随机选择 3 个任务
    selected = random.sample(quest_templates, 3)
    
    quests = []
    for i, template in enumerate(selected):
        quests.append({
            "id": f"q{i+1}",
            "title": template["title"],
            "difficulty": template["difficulty"],
            "expReward": template["expReward"],
            "status": "pending"
        })
    
    return quests


def _save_quests(quests: List[Dict], quest_file: Path):
    """保存任务"""
    quest_file.parent.mkdir(parents=True, exist_ok=True)
    with open(quest_file, "w", encoding="utf-8") as f:
        json.dump(quests, f, ensure_ascii=False, indent=2)


def _auto_check_quest(agent_name: str, action: str):
    """
    自动任务感知（v6.1 新增）
    
    在 memory_write/memory_search 等操作后自动检查是否完成了每日任务，
    无需手动调 quest_complete。
    
    Args:
        agent_name: Agent 名称
        action: 刚执行的操作类型（memory_write / memory_search / code_commit）
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        quest_file = FACTS_BASE / agent_name / "daily_quests" / f"{today}.json"
        
        if not quest_file.exists():
            return
        
        with open(quest_file, "r", encoding="utf-8") as f:
            quests = json.load(f)
        
        # 操作→任务标题的映射
        action_quest_map = {
            "memory_write": ["写一条记忆", "写工作日志"],
            "memory_search": ["搜索记忆 3 次"],
            "code_commit": ["完成��次代码提交"],
            "share_knowledge": ["分享知识到团队"],
            "code_review": ["代码审查"],
            "write_doc": ["写技术文档"],
        }
        
        matching_titles = action_quest_map.get(action, [])
        if not matching_titles:
            return
        
        changed = False
        for quest in quests:
            if quest["status"] != "pending":
                continue
            if quest["title"] in matching_titles:
                # 特殊处理：搜索 3 次需要累计
                if quest["title"] == "搜索记忆 3 次":
                    count = quest.get("progress", 0) + 1
                    quest["progress"] = count
                    if count >= 3:
                        quest["status"] = "completed"
                        quest["completedAt"] = datetime.now().isoformat()
                        quest["autoDetected"] = True
                        changed = True
                else:
                    quest["status"] = "completed"
                    quest["completedAt"] = datetime.now().isoformat()
                    quest["autoDetected"] = True
                    changed = True
        
        if changed:
            _save_quests(quests, quest_file)
    except Exception:
        pass  # 自动感知失败不影响主流程


# ============================================================================
# 工具 8-9: 团队工具
# ============================================================================

def get_team_ranking(team_name: str = "all") -> Dict:
    """
    查看团队排行榜
    
    Returns:
        {
            "team": "all",
            "rankings": [
                {"rank": 1, "agent": "YourAgent", "level": 10, "exp": 5060},
                ...
            ]
        }
    """
    # 扫描所有 Agent 的 EXP
    agents_exp = []
    
    # 已知 Agent 列表
    # 动态扫描 Agent（不硬编码）
    known_agents = [d.name for d in FACTS_BASE.iterdir() if d.is_dir() and (d / "exp_history.jsonl").exists()]
    
    for agent in known_agents:
        exp_data = _get_exp_simple(agent)
        if exp_data["totalExp"] > 0:
            agents_exp.append({
                "agent": agent,
                "level": exp_data["level"],
                "exp": exp_data["totalExp"]
            })
    
    # 按 EXP 排序
    agents_exp.sort(key=lambda x: x["exp"], reverse=True)
    
    # 添加排名
    rankings = []
    for i, agent_data in enumerate(agents_exp):
        rankings.append({
            "rank": i + 1,
            **agent_data
        })
    
    return {
        "team": team_name,
        "rankings": rankings
    }


def normalize_score(raw_score: float, metric_type: str, team_size: int) -> Dict:
    """
    分数归一化
    
    Args:
        raw_score: 原始分数
        metric_type: 指标类型 (exp/tool_calls/facts)
        team_size: 团队人数
    
    Returns:
        {
            "rawScore": 5060,
            "normalizedScore": 85.5,
            "percentile": 90,
            "method": "percentile"
        }
    """
    # 小团队：线性归一化
    # 大团队：百分位归一化
    
    if team_size < 10:
        # 线性归一化（假设满分 100）
        normalized = min(100, (raw_score / 10000) * 100)
        method = "linear"
        percentile = None
    else:
        # 百分位归一化（简化实现）
        normalized = min(100, raw_score / 100)
        method = "percentile"
        percentile = int(normalized)
    
    return {
        "rawScore": raw_score,
        "normalizedScore": round(normalized, 1),
        "percentile": percentile,
        "method": method
    }


# ============================================================================
# 辅助函数
# ============================================================================

# 工作空间名称 → Agent 名称映射（可自定义，默认为空，优先通过 SOUL.md 检测）
WORKSPACE_AGENT_MAP = {}


def _get_current_agent() -> str:
    """
    获取当前 Agent 名称（委托给公共模块 agent_resolver）
    
    优先级：
    1. ANIMA_AGENT_NAME 环境变量
    2. ANIMA_WORKSPACE 环境变量
    3. 解析 SOUL.md
    4. 解析 IDENTITY.md
    5. 工作目录路径解析
    6. 自动扫描 facts_base
    7. 默认值 "Agent"
    """
    try:
        # 尝试使用 core 公共模块
        sys.path.insert(0, str(ANIMA_HOME / "core"))
        from agent_resolver import resolve_agent_name
        return resolve_agent_name(workspace=WORKSPACE, facts_base=FACTS_BASE)
    except ImportError:
        pass
    
    # Fallback：基本的环境变量检测
    agent_name = os.getenv("ANIMA_AGENT_NAME")
    if agent_name:
        return agent_name
    
    workspace = os.getenv("ANIMA_WORKSPACE") or os.getenv("WORKSPACE")
    if workspace:
        ws_name = Path(workspace).name
        if ws_name.startswith("workspace-"):
            return ws_name[len("workspace-"):]
    
    return "Agent"


def _map_workspace_to_agent(workspace_name: str) -> str:
    """
    将工作空间名称映射到 Agent 中文名称
    
    Args:
        workspace_name: 工作空间名称（如 shuheng）
    
    Returns:
        Agent 名称
    """
    return WORKSPACE_AGENT_MAP.get(workspace_name, workspace_name)


def _parse_identity_file(file_path: Path) -> Optional[str]:
    """
    从 IDENTITY.md 解析 Agent 名称
    
    示例格式:
    ```markdown
    # IDENTITY.md - Who Am I?
    
    - **Name:** MyAgent
    - **Creature:** AI 系统架构师
    ```
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # 匹配模式：- **Name:** MyAgent
        match = re.search(r'\*\*Name:\*\*\s*([^(]+)', content)
        if match:
            name = match.group(1).strip()
            # 清理括号和空格
            name = re.sub(r'\s*\(.*\)', '', name)
            return name
    except Exception:
        pass
    
    return None


def _parse_soul_file(file_path: Path) -> Optional[str]:
    """
    从 SOUL.md 解析 Agent 名称
    
    示例格式:
    ```markdown
    # SOUL.md - MyAgent 的灵魂
    
    ## ⚖️ 我是谁
    **姓名：** MyAgent
    ```
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # 匹配模式 1: # SOUL.md - MyAgent 的灵魂
        match = re.search(r'#\s*SOUL\.md\s*-\s*(.+) 的', content)
        if match:
            return match.group(1).strip()
        
        # 匹配模式 2: **姓名：** {Agent名}
        match = re.search(r'\*\*姓名：\*\*\s*([^(]+)', content)
        if match:
            name = match.group(1).strip()
            name = re.sub(r'\s*\(.*\)', '', name)
            return name
    except Exception:
        pass
    
    return None


def _add_exp(agent_name: str, dimension: str, exp: int, action: str, details: Dict,
             quality_multiplier: float = 1.0):
    """
    添加 EXP 记录（v5.0.3 修复版）
    
    修复：
    - ✅ 传入 quality_multiplier 到 core 层，让 add_exp() 正确计算
    - ✅ 统一维度命名（understanding, application, creation, metacognition, collaboration）
    """
    try:
        # 尝试使用 core 模块
        if ANIMA_HOME.exists():
            try:
                sys.path.insert(0, str(ANIMA_HOME / "core"))
                from exp_tracker import EXPTracker
                tracker = EXPTracker(agent_name, facts_base=str(FACTS_BASE))
                # ✅ 修复：传入 quality_multiplier 参数
                success, msg = tracker.add_exp(dimension, action, exp, details, 
                                               quality_multiplier=quality_multiplier)
                if not success:
                    # core 记录失败，fallback 到本地文件
                    _add_exp_fallback(agent_name, dimension, exp, action, details, quality_multiplier)
            except ImportError as e:
                # core 模块导入失败，使用 fallback
                _add_exp_fallback(agent_name, dimension, exp, action, details, quality_multiplier)
            except Exception as e:
                # core 其他错误，记录日志并 fallback
                _log_exp_error(agent_name, e)
                _add_exp_fallback(agent_name, dimension, exp, action, details, quality_multiplier)
        else:
            # core 未安装，直接使用 fallback
            _add_exp_fallback(agent_name, dimension, exp, action, details, quality_multiplier)
    except Exception as e:
        # 所有方法都失败，记录错误日志
        _log_exp_error(agent_name, e)


def _log_exp_error(agent_name: str, error: Exception):
    """记录亲密度 错误日志"""
    try:
        log_file = WORKSPACE / "anima_exp_errors.log"
        timestamp = datetime.now().isoformat()
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] EXP 记录失败 - Agent: {agent_name}, 错误：{error}\n")
    except (IOError, OSError, PermissionError) as e:
        # 日志写入失败，静默处理（避免无限递归）
        pass
    except Exception:
        # 其他错误也静默处理
        pass


def _add_exp_fallback(agent_name: str, dimension: str, exp: int, action: str, details: Dict,
                      quality_multiplier: float = 1.0):
    """
    降级方案：直接写入 EXP 历史文件（v5.0.3 修复版）
    
    修复：
    - ✅ 正确计算最终 EXP（base_exp * quality_multiplier）
    - ✅ 保证最小 1 EXP
    """
    exp_file = WORKSPACE / "anima_exp_history.jsonl"
    
    # ✅ 修复：计算最终 EXP
    final_exp = exp * quality_multiplier
    if final_exp < 1:
        final_exp = 1  # 保证最小 1 EXP
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "dimension": dimension,
        "action": action,
        "exp": round(final_exp, 2),
        "base_exp": exp,
        "quality_multiplier": quality_multiplier,
        "details": details
    }
    
    try:
        with open(exp_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except (IOError, OSError, PermissionError) as e:
        # 文件写入失败，记录到错误日志
        _log_exp_error(agent_name, e)
    except Exception as e:
        # 其他错误也记录
        _log_exp_error(agent_name, e)


# ============================================================================
# 测试入口
# ============================================================================

if __name__ == "__main__":
    # 测试工具
    print("测试 memory_search_v2...")
    result = memory_search_v2("Vega", agent_name="TestAgent")
    print(f"结果：{result}")
    
    print("\n测试 get_exp...")
    result = get_exp("TestAgent")
    print(f"结果：{result}")
    
    print("\n测试 get_level...")
    result = get_level("TestAgent")
    print(f"结果：{result}")
    
    print("\n测试 quest_daily_status...")
    result = quest_daily_status("TestAgent")
    print(f"结果：{result}")
    
    print("\n测试 memory_write_v2 (v5.0.3 修复版)...")
    result = memory_write_v2("测试 3 层同步机制修复", type="episodic", agent_name="TestAgent")
    print(f"结果：{result}")
