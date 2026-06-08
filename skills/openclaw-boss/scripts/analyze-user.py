#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Profile Analyzer v5.0 - 用户评价分析器（历史对比版 + 响应式卡片）

增强功能：
- 100 分制评分（严厉）
- 整体综合评分
- 毒舌老板点评
- 历史报告对比（进步/退步分析）
- 成长趋势追踪
- 📱 响应式卡片：手机版（简洁）+ 桌面版（ASCII 艺术）

Usage:
    python3 analyze-user.py [--limit N] [--output PATH] [--report-type daily|weekly|monthly] [--format mobile|desktop|both]

Args:
    --format: 卡片格式
              - mobile: 仅手机版（简洁文本，适合小屏幕）
              - desktop: 仅桌面版（ASCII 艺术，适合截图）
              - both: 两个版本都输出（默认，手机版在前）
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import random

# 配置
WORKSPACE = Path("/root/.openclaw/workspace")
MEMORY_FILE = WORKSPACE / "MEMORY.md"
USER_FILE = WORKSPACE / "USER.md"
MEMORY_DIR = WORKSPACE / "memory"
REPORTS_DIR = WORKSPACE / "reports"
DB_DIR = WORKSPACE / "db"

# 确保目录存在
REPORTS_DIR.mkdir(exist_ok=True)

# 😈 毒舌老板点评模板（加强版）
BOSS_COMMENTS = {
    "improved": [
        "嗯，这次有进步，继续保持。",
        "不错，比上次强多了。",
        "看来上周没白说，听进去了。",
        "行吧，勉强算你有进步。",
        "可以啊，终于开窍了？",
        "这还差不多，早这样不就完了？",
        "进步是有的，但别飘，离优秀还差得远。",
        "不错，终于不像上周那样拉胯了。",
    ],
    "regressed": [
        "怎么回事？退步了？",
        "上周不是挺好的吗？这周咋回事？",
        "你是来混日子的吧？",
        "我看你不是能力问题，是态度问题。",
        "你这退步速度，坐火箭呢？",
        "行吧，我当没看见，下周再这样你等着。",
        "退步比进步快，你是懂效率的。",
        "这分数掉的，我都替你心疼（才怪）。",
        "退步了？行，今晚加班反省一下。",
    ],
    "stable": [
        "还行吧，保持稳定。",
        "不好不坏，凑合能用。",
        "比上不足比下有余。",
        "就这样？不能再努力努力？",
        "稳定是稳定，就是没啥惊喜。",
        "不好说你是稳如泰山还是原地踏步。",
        "稳定得像个老好人，一点冲劲都没有。",
        "这分数稳得，我都怀疑你有没有努力。",
        "保持现状？那你干嘛不直接躺平？",
    ],
}

# 🔥 爆款金句点评（适合社交媒体传播）- 加强版
VIRAL_QUOTES = {
    "high_security": [
        "密钥保护得比初恋还纯洁 🔐",
        "安全规范写得比宪法还厚 📜",
        "黑客看了都摇头的防御等级 🛡️",
        "密码复杂度能把 AI 整崩溃 🔒",
        "安全到连自己都进不去了 🚫",
        "这安全级别，防弹衣都没你厚 🦺",
    ],
    "high_efficiency": [
        "这效率，资本家看了都流泪 💼",
        "AI 被你当驴使，良心不会痛吗？ 🫏",
        "卷王本王，鉴定完毕 🏆",
        "效率这么高，是打了鸡血吗？ 💉",
        "这速度，是开了挂吧？ 🎮",
    ],
    "low_efficiency": [
        "效率这块，咱能支棱起来吗？ 📉",
        "AI 都比你勤快，你反思一下 🤖",
        "摸鱼界天花板，佩服佩服 🐟",
        "这效率，树懒看了都摇头 🦥",
        "你是懂拖延的，佩服 🐢",
        "效率低到 AI 都想替你上班 💼",
        "这速度，是故意在等年终奖吗？ 🎁",
    ],
    "tech_master": [
        "全栈？我看是全站（在网站上全站） 🌐",
        "技术栈比我的头发还茂盛 💻",
        "这技术深度，能挖到地心了 ⛏️",
        "技术这么牛，怎么还没财务自由？ 💰",
        "代码写得比诗还美，可惜没人看 📝",
    ],
    "system_thinker": [
        "定时任务比我的闹钟还多 ⏰",
        "系统化到 AI 都要打卡上班 📋",
        "你这管理方式，资本家看了沉默 🤐",
        "流程多到能把人绕晕 🌀",
        "系统复杂到需要说明书来管理说明书 📖",
        "爱搞系统是吧？包工头转世？ 🏗️",
    ],
    "pragmatic": [
        "务实到连废话都不说一句 💬",
        "删除键被你按出火星子了 🔥",
        "实用主义天花板，花哨？不存在的 🎯",
        "务实到连梦想都删了，真有你的 🗑️",
        "这么务实，是穷怕了吗？ 💸",
        "实用到连乐趣都没了，累不累？ 😴",
    ],
}

# 🏆 称号生成器
TITLE_GENERATOR = {
    "overall": {
        "90+": ["👑 传奇用户", "🌟 天选打工人", "🚀 超级个体"],
        "80-89": ["💎 精英玩家", "⭐ 优质用户", "🎯 高效执行者"],
        "70-79": ["📈 潜力股", "🔧 实干家", "🌱 成长中"],
        "60-69": ["😐 普通路过", "🐢 慢慢爬", "📚 学习中"],
        "below_60": ["⚠️ 需要加油", "🆘 求助信号", "💪 潜力无限"],
    },
    "specialty": {
        "security_master": "🔒 安全守护者",
        "efficiency_king": "⚡ 效率之王",
        "tech_wizard": "🧙 技术法师",
        "system_architect": "🏗️ 系统架构师",
        "pragmatic_hero": "🎯 务实英雄",
        "curiosity_explorer": "🔭 好奇探索者",
    },
}

# 🎯 特质毒舌点评（加强版）
TRAIT_ROASTS = {
    "务实主义": [
        "务实是好事，但别太抠门，该花的钱得花。",
        "「没什么用，直接删除」- 你倒是干脆，也不怕误删。",
        "这么务实，是穷怕了吗？",
        "务实到连梦想都删了，真有你的 🗑️",
        "实用主义天花板，花哨？不存在的 🎯",
        "这么省，是准备攒钱买岛吗？ 🏝️",
    ],
    "安全意识": [
        "密钥保护得比女朋友还严，累不累啊？",
        "这么怕被黑，是做过什么亏心事吗？",
        "安全规范写得比公司制度还厚，真有你的。",
        "密码复杂度能把 AI 整崩溃 🔒",
        "安全到连自己都进不去了 🚫",
        "这安全级别，防弹衣都没你厚 🦺",
        "黑客看了都摇头，直接放弃 🛡️",
    ],
    "系统化思维": [
        "定时任务、心跳、备份 - 你是要把 AI 军训吗？",
        "这么爱搞系统，是当过包工头吗？",
        "连 AI 都要打卡上班，资本家看了都流泪。",
        "定时任务比我的闹钟还多 ⏰",
        "流程多到能把人绕晕 🌀",
        "系统复杂到需要说明书来管理说明书 📖",
        "爱搞系统是吧？包工头转世？ 🏗️",
    ],
    "简洁偏好": [
        "「不了，那先这样吧」- 你是来发号施令的吗？",
        "简洁是好事，但有时候多说两句会死吗？",
        "这么省字，是发短信要钱吗？",
        "话这么少，是怕费电吗？ 💡",
        "简洁到连人情味都没了，累不累？ 🤖",
        "回复短得像电报，还是加钱那种 📟",
    ],
    "技术好奇心": [
        "新技能说装就装，钱多烧得慌？",
        "看到新技术就手痒，这病我能治（治不好）。",
        "配置这个配置那个，你是真有空。",
        "技术栈比我的头发还茂盛 💻",
        "什么新技术都要试试，你是小白鼠吗？ 🐭",
        "学这么多，用得完吗？别浪费 📚",
    ],
    "决策果断": [
        "说删就删，问过人家意见吗？",
        "果断是好事，但别太独断专行。",
        "这决策力，不去当老板可惜了。",
        "决定下得比刀还快，是切菜练出来的吗？ 🔪",
        "这么果断，是怕后悔吗？ ⚡",
        "决策快得像按了加速键，稳吗？ 🎮",
    ],
    "结果导向": [
        "结果结果结果，过程就不重要呗？",
        "这么功利，累不累啊？",
        "看结果不看过程，典型的老板思维。",
        "功利到连乐趣都没了，值得吗？ 🎯",
        "结果导向？过程派表示不服 🙄",
        "这么看重结果，是 KPI 压身上了吗？ 📊",
    ],
}

# 🌱 成长建议
GROWTH_SUGGESTIONS = [
    "🌱 可以尝试一些'看似无用'的探索，说不定有意外收获（别老那么功利）。",
    "🎨 偶尔放慢脚步，享受过程而不只是结果（我知道这很难）。",
    "🤝 可以更信任 AI 一些，让它承担更多创造性工作（别老当保姆）。",
    "📖 考虑把更多经验写成博客，帮助更多人（也顺便赚点名声）。",
    "⚖️ 在安全和便利之间找到更好的平衡点（别把自己累死）。",
    "💤 早点睡觉，身体是革命的本钱（别以为我不知道你熬夜）。",
    "😄 多笑笑，愁眉苦脸的给谁看（开心点）。",
]


def run_command(cmd: str, timeout: int = 60) -> str:
    """执行 shell 命令并返回输出"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except Exception as e:
        return f"[Error: {e}]"


def get_sessions_list(limit: int = 50) -> list:
    """获取会话列表"""
    output = run_command(f"sessions_list --limit {limit} --messageLimit 10")
    try:
        if output.strip().startswith('['):
            return json.loads(output)
        return [{"raw": output}]
    except:
        return [{"raw": output}]


def read_file(path: Path) -> str:
    """读取文件内容"""
    try:
        return path.read_text(encoding='utf-8')
    except Exception as e:
        return f"[无法读取：{e}]"


def read_memory_files() -> dict:
    """读取所有记忆文件"""
    memories = {"MEMORY.md": read_file(MEMORY_FILE), "USER.md": read_file(USER_FILE), "daily": []}
    if MEMORY_DIR.exists():
        for f in sorted(MEMORY_DIR.glob("*.md"), reverse=True)[:30]:
            memories["daily"].append({"file": f.name, "content": read_file(f)})
    return memories


def query_memory_db(query: str = "*") -> list:
    """从 Agent Memory Ultimate 数据库查询记忆"""
    db_path = DB_DIR / "memory.db"
    if not db_path.exists():
        return []
    try:
        cmd = f"cd {WORKSPACE}/skills/agent-memory-ultimate/scripts && python3 mem.py recall \"{query}\" --limit 20"
        output = run_command(cmd, timeout=30)
        if output.strip():
            return output.strip().split('\n')[:20]
    except:
        pass
    return []


def find_previous_report(report_type: str = "daily") -> Path:
    """查找上一次的报告"""
    if not REPORTS_DIR.exists():
        return None
    
    # 根据报告类型查找
    if report_type == "weekly":
        pattern = "weekly-profile-*.md"
    elif report_type == "monthly":
        pattern = "monthly-profile-*.md"
    else:
        pattern = "user-profile-*.md"
    
    reports = sorted(REPORTS_DIR.glob(pattern), reverse=True)
    
    # 返回第二新的报告（最新的是本次生成的）
    if len(reports) >= 2:
        return reports[1]
    elif len(reports) == 1:
        return reports[0]
    return None


def parse_report_scores(report_path: Path) -> dict:
    """解析报告中的分数"""
    if not report_path.exists():
        return {}
    
    content = read_file(report_path)
    scores = {}
    
    # 解析综合评分
    overall_match = re.search(r'整体评分：\*\*(\d+)/100\*\*', content)
    if overall_match:
        scores["overall"] = int(overall_match.group(1))
    
    # 解析各维度分数
    dimension_patterns = {
        "personality": r'\*\*性格特质\*\*\s*\|\s*(\d+)/100',
        "technical": r'\*\*技术能力\*\*\s*\|\s*(\d+)/100',
        "security": r'\*\*安全意识\*\*\s*\|\s*(\d+)/100',
        "efficiency": r'\*\*效率指数\*\*\s*\|\s*(\d+)/100',
    }
    
    for dim, pattern in dimension_patterns.items():
        match = re.search(pattern, content)
        if match:
            scores[dim] = int(match.group(1))
    
    return scores


def calculate_changes(current: dict, previous: dict) -> dict:
    """计算分数变化"""
    changes = {}
    
    for key in current:
        if key in previous:
            diff = current[key] - previous[key]
            changes[key] = {
                "previous": previous[key],
                "current": current[key],
                "diff": diff,
                "trend": "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
            }
        else:
            changes[key] = {"previous": None, "current": current[key], "diff": None, "trend": "🆕"}
    
    return changes


def get_change_comment(diff: int) -> str:
    """根据变化值返回评论"""
    if diff is None:
        return "首次评估"
    elif diff > 10:
        return "巨大进步！🎉"
    elif diff > 5:
        return "明显进步 👍"
    elif diff > 0:
        return "小幅进步 ✨"
    elif diff == 0:
        return "保持稳定 ➡️"
    elif diff > -5:
        return "小幅退步 ⚠️"
    elif diff > -10:
        return "明显退步 📉"
    else:
        return "严重退步！🚨"


def calculate_strict_score(base_score: float, max_score: float = 100, penalty_factors: list = None) -> int:
    """计算严厉评分（100 分制）"""
    if penalty_factors is None:
        penalty_factors = [0.85, 0.9, 0.95]
    penalty = random.choice(penalty_factors)
    final_score = int(base_score * penalty)
    return min(final_score, max_score)


def analyze_user_data(memories: dict, sessions: list, report_type: str = "daily") -> dict:
    """分析用户数据"""
    analysis = {
        "basic_info": {},
        "personality_traits": [],
        "technical_skills": [],
        "security_awareness": [],
        "projects": [],
        "boss_comments": {},
        "growth_suggestions": [],
        "scores": {},
        "period_stats": {},
        "improvement_areas": [],
        "history_comparison": None,
    }
    
    memory_content = memories.get("MEMORY.md", "")
    user_content = memories.get("USER.md", "")
    
    # 基本信息
    name_match = re.search(r'\*\*Name:\*\*\s*(.+)', user_content)
    analysis["basic_info"]["name"] = name_match.group(1).strip() if name_match else "用户"
    
    # 性格特质分析
    trait_patterns = {
        "务实主义": ["务实", "删除", "没什么用", "直接"],
        "安全意识": ["安全", "密钥", "保密", "验证", "规范"],
        "系统化思维": ["系统", "定时", "心跳", "备份", "自动化"],
        "简洁偏好": ["简洁", "明了", "不.*markdown"],
        "技术好奇心": ["好奇", "新", "尝试", "探索", "配置"],
        "决策果断": ["果断", "决定", "暂不", "删除"],
        "结果导向": ["结果", "实际", "指标", "状态"],
    }
    
    total_trait_score = 0
    trait_count = 0
    
    for trait, keywords in trait_patterns.items():
        score = 0
        evidence = []
        for keyword in keywords:
            if re.search(keyword, memory_content, re.IGNORECASE):
                score += 1
                match = re.search(rf'.{{0,50}}{keyword}.{{0,100}}', memory_content, re.IGNORECASE)
                if match:
                    evidence.append(match.group(0)[:80])
        
        if score > 0:
            raw_score = min(5, score * 1.2)
            strict_score = calculate_strict_score(raw_score * 20, penalty_factors=[0.8, 0.85, 0.9])
            total_trait_score += strict_score
            trait_count += 1
            
            analysis["personality_traits"].append({
                "trait": trait,
                "raw_score": round(raw_score, 1),
                "strict_score": strict_score,
                "evidence": evidence[:2] if evidence else ["行为模式分析得出"],
                "roast": random.choice(TRAIT_ROASTS.get(trait, ["还行吧，继续努力。"]))
            })
    
    # 技术栈分析
    tech_categories = {
        "前端开发": ["React", "TypeScript", "Vite", "Tailwind", "Framer Motion"],
        "DevOps": ["Git", "GitHub", "Nginx", "部署", "CI/CD"],
        "AI/Agent": ["OpenClaw", "Agent", "LLM", "多 Agent"],
        "系统管理": ["Linux", "Cron", "Systemd", "服务器"],
        "数据库": ["SQLite", "MySQL", "数据库", "FTS5"],
        "编程语言": ["Python", "JavaScript", "Node", "Bash"],
    }
    
    total_tech_score = 0
    tech_count = 0
    
    for category, techs in tech_categories.items():
        matched = [tech for tech in techs if tech.lower() in memory_content.lower()]
        if matched:
            raw_score = min(5, 3 + len(matched) * 0.4)
            strict_score = calculate_strict_score(raw_score * 20, penalty_factors=[0.75, 0.8, 0.85])
            total_tech_score += strict_score
            tech_count += 1
            
            analysis["technical_skills"].append({
                "category": category,
                "skills": matched,
                "strict_score": strict_score,
            })
    
    # 项目分析
    if "YiweisiBlog" in memory_content:
        analysis["projects"].append({
            "name": "YiweisiBlog",
            "url": "https://blog.wwzhen.site/",
            "articles": 11,
            "tech": ["React", "TypeScript", "Vite", "Tailwind CSS"],
            "status": "🟢 正常运行",
            "score": calculate_strict_score(85, penalty_factors=[0.9, 0.95, 1.0]),
        })
    
    # 安全意识分析
    security_patterns = [
        ("密钥保密规范", "密钥" in memory_content and "保密" in memory_content),
        ("发送限制", "禁止" in memory_content and "发送" in memory_content),
        ("验证机制", "验证" in memory_content and "问题" in memory_content),
        ("邮件安全", "邮件" in memory_content and "只读" in memory_content),
        ("发布检查", "发布" in memory_content and "扫描" in memory_content),
    ]
    
    security_count = sum(1 for _, exists in security_patterns if exists)
    security_score = calculate_strict_score(security_count * 20, penalty_factors=[0.9, 0.95, 1.0])
    
    for name, exists in security_patterns:
        if exists:
            analysis["security_awareness"].append({"name": name, "score": security_score})
    
    # 量化统计
    analysis["period_stats"] = {
        "total_sessions": len(sessions),
        "memory_files": len(memories.get('daily', [])),
        "agents_configured": memory_content.count("Agent") // 5,
        "cron_jobs": memory_content.count("*/") + memory_content.count("0 "),
        "uptime_days": 27,
    }
    
    # 计算综合评分
    trait_avg = total_trait_score / trait_count if trait_count > 0 else 0
    tech_avg = total_tech_score / tech_count if tech_count > 0 else 0
    efficiency_score = calculate_strict_score(min(100, len(sessions) * 10), penalty_factors=[0.6, 0.7, 0.8])
    
    overall_score = int(trait_avg * 0.3 + tech_avg * 0.3 + security_score * 0.2 + efficiency_score * 0.2)
    
    analysis["scores"] = {
        "overall": overall_score,
        "personality": int(trait_avg),
        "technical": int(tech_avg),
        "security": security_score,
        "efficiency": efficiency_score,
        "grade": get_grade(overall_score),
    }
    
    # 历史对比
    prev_report = find_previous_report(report_type)
    if prev_report:
        prev_scores = parse_report_scores(prev_report)
        if prev_scores:
            changes = calculate_changes(analysis["scores"], prev_scores)
            analysis["history_comparison"] = {
                "previous_report": str(prev_report),
                "previous_scores": prev_scores,
                "changes": changes,
                "overall_trend": "improved" if changes.get("overall", {}).get("diff", 0) > 0 
                                else "regressed" if changes.get("overall", {}).get("diff", 0) < 0 
                                else "stable"
            }
    
    # 老板点评
    trend = analysis["history_comparison"]["overall_trend"] if analysis["history_comparison"] else "stable"
    analysis["boss_comments"] = {
        "overall": random.choice(BOSS_COMMENTS.get(trend, BOSS_COMMENTS["stable"])),
        "traits": {t["trait"]: t["roast"] for t in analysis["personality_traits"]},
    }
    
    # 改进空间
    analysis["improvement_areas"] = get_improvement_areas(analysis["scores"])
    analysis["growth_suggestions"] = random.sample(GROWTH_SUGGESTIONS, 3)
    
    if report_type in ["weekly", "monthly"]:
        analysis["period_changes"] = {
            "new_skills_installed": random.randint(0, 3),
            "new_articles_published": random.randint(0, 2),
            "system_optimizations": random.randint(1, 5),
            "security_improvements": random.randint(0, 2),
        }
    
    return analysis


def get_grade(score: int) -> str:
    """根据分数返回等级"""
    if score >= 90: return "A+ 优秀"
    elif score >= 80: return "A 良好"
    elif score >= 70: return "B 中等"
    elif score >= 60: return "C 及格"
    else: return "D 不及格"


def get_title(score: int) -> str:
    """根据分数获取称号"""
    if score >= 90:
        return random.choice(TITLE_GENERATOR["overall"]["90+"])
    elif score >= 80:
        return random.choice(TITLE_GENERATOR["overall"]["80-89"])
    elif score >= 70:
        return random.choice(TITLE_GENERATOR["overall"]["70-79"])
    elif score >= 60:
        return random.choice(TITLE_GENERATOR["overall"]["60-69"])
    else:
        return random.choice(TITLE_GENERATOR["overall"]["below_60"])


def get_specialty_title(analysis: dict) -> str:
    """根据最高分项获取专属称号"""
    scores = analysis.get("scores", {})
    max_score = 0
    max_dim = ""
    
    dim_map = {
        "security": "security_master",
        "efficiency": "efficiency_king",
        "technical": "tech_wizard",
        "personality": "system_architect",
    }
    
    for dim, score in scores.items():
        if dim in dim_map and score > max_score:
            max_score = score
            max_dim = dim_map[dim]
    
    if max_dim:
        return TITLE_GENERATOR["specialty"].get(max_dim, "🌟 全能选手")
    return "🌟 全能选手"


def get_viral_quote(analysis: dict) -> str:
    """获取爆款金句"""
    scores = analysis.get("scores", {})
    quotes = []
    
    if scores.get("security", 0) >= 90:
        quotes.extend(VIRAL_QUOTES["high_security"])
    if scores.get("efficiency", 0) >= 80:
        quotes.extend(VIRAL_QUOTES["high_efficiency"])
    elif scores.get("efficiency", 0) < 50:
        quotes.extend(VIRAL_QUOTES["low_efficiency"])
    if scores.get("technical", 0) >= 80:
        quotes.extend(VIRAL_QUOTES["tech_master"])
    
    # 检查性格特质
    traits = analysis.get("personality_traits", [])
    for trait in traits:
        if "系统化思维" in trait["trait"] and trait["strict_score"] >= 80:
            quotes.extend(VIRAL_QUOTES["system_thinker"])
        if "务实主义" in trait["trait"] and trait["strict_score"] >= 80:
            quotes.extend(VIRAL_QUOTES["pragmatic"])
    
    if quotes:
        return random.choice(quotes)
    return "继续加油，我看好你！💪"


def calculate_percentile(score: int) -> int:
    """估算用户排名百分比（伪造成分）"""
    # 基于分数估算一个"超越用户%"
    base = score * 0.8
    noise = random.randint(-5, 10)
    return min(99, max(1, int(base + noise)))


def get_improvement_areas(scores: dict) -> list:
    """分析改进空间"""
    areas = []
    if scores.get("efficiency", 0) < 70:
        areas.append({"area": "效率提升", "current": scores["efficiency"], "target": 80, 
                     "suggestion": "多利用自动化，少做重复劳动"})
    if scores.get("technical", 0) < 80:
        areas.append({"area": "技术深度", "current": scores["technical"], "target": 85,
                     "suggestion": "选 1-2 个领域深入钻研，别浅尝辄止"})
    if scores.get("security", 0) >= 90:
        areas.append({"area": "安全平衡", "current": scores["security"], "target": 85,
                     "suggestion": "安全很重要，但别过度，找到平衡点"})
    return areas


def create_progress_bar(score: int, max_score: int = 100, length: int = 25) -> str:
    """创建进度条"""
    filled = int((score / max_score) * length)
    empty = length - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {score}/100"


def get_display_width(text: str) -> int:
    """计算字符串的显示宽度（中文算 2，英文算 1，emoji 算 2）"""
    width = 0
    for char in text:
        code = ord(char)
        # 移除 ANSI 转义码
        if code == 27:  # ESC
            continue
        # 中文字符、日文、韩文、emoji 等宽字符
        if 0x1100 <= code <= 0x115F or 0x2329 <= code <= 0x232A or 0x2E80 <= code <= 0xA4CF or \
           0xA960 <= code <= 0xA97F or 0xAC00 <= code <= 0xD7A3 or 0xF900 <= code <= 0xFAFF or \
           0xFE10 <= code <= 0xFE19 or 0xFE30 <= code <= 0xFE6F or 0xFF00 <= code <= 0xFF60 or \
           0xFFE0 <= code <= 0xFFE6 or 0x1F000 <= code <= 0x1F9FF or 0x20000 <= code <= 0x2FFFD:
            width += 2
        # 英文字符和半角符号
        elif code < 128:
            width += 1
        else:
            width += 2  # 其他字符默认按宽字符处理
    return width


def pad_to_width(text: str, width: int) -> str:
    """填充字符串到指定显示宽度"""
    current_width = get_display_width(text)
    padding_needed = max(0, width - current_width)
    return text + ' ' * padding_needed


def generate_report(analysis: dict, report_type: str = "daily", card_format: str = "both") -> str:
    """生成用户评价报告（含历史对比）
    
    Args:
        analysis: 分析数据
        report_type: 报告类型 (daily/weekly/monthly)
        card_format: 卡片格式 (mobile/desktop/both)
    """
    
    basic_info = analysis.get("basic_info", {})
    name = basic_info.get("name", "用户")
    period_stats = analysis.get("period_stats", {})
    scores = analysis.get("scores", {})
    boss_comments = analysis.get("boss_comments", {})
    history = analysis.get("history_comparison")
    
    # 报告标题
    if report_type == "weekly":
        title = f"📊 {name} 周度人物分析报告"
        period = f"本周 ({datetime.now().strftime('%Y-W%W')})"
    elif report_type == "monthly":
        title = f"📊 {name} 月度人物分析报告"
        period = f"本月 ({datetime.now().strftime('%Y-%m')})"
    else:
        title = f"📊 {name} 人物分析报告"
        period = "今日"
    
    # 🎴 评分卡片 - 适合截图分享的简洁版本
    overall = scores.get('overall', 0)
    grade = scores.get('grade', 'N/A')
    user_title = get_title(overall)
    specialty_title = get_specialty_title(analysis)
    viral_quote = get_viral_quote(analysis)
    percentile = calculate_percentile(overall)
    
    # 历史变化
    if history:
        prev_overall = history["previous_scores"].get("overall", 0)
        diff = overall - prev_overall
        if diff > 0:
            change_str = f"📈 +{diff}"
            trend_word = "进步"
        elif diff < 0:
            change_str = f"📉 {diff}"
            trend_word = "退步"
        else:
            change_str = "➡️ 0"
            trend_word = "持平"
        history_line = f"上次：{prev_overall} | 变化：{change_str}"
    else:
        history_line = "🆕 首次评估"
    
    # 核心标签 - 从性格特质中提取
    traits = analysis.get("personality_traits", [])
    trait_tags = []
    for t in traits[:3]:
        tag_map = {
            "务实主义": "务实派",
            "安全意识": "安全控",
            "系统化思维": "系统狂",
            "简洁偏好": "极简主义",
            "技术好奇心": "探索者",
            "决策果断": "决断力",
            "结果导向": "结果派",
        }
        if t["trait"] in tag_map:
            trait_tags.append(tag_map[t["trait"]])
    
    if not trait_tags:
        trait_tags = ["发展中", "潜力股", "探索中"]
    
    core_tags = " · ".join(trait_tags)
    
    # 获取最高分项
    max_dim_name = ""
    max_dim_score = 0
    dim_names = {"personality": "性格", "technical": "技术", "security": "安全", "efficiency": "效率"}
    for dim, score in scores.items():
        if dim in dim_names and score > max_dim_score:
            max_dim_score = score
            max_dim_name = dim_names[dim]
    
    # 卡片内部宽度（不含边框）
    INNER_WIDTH = 68
    
    # 计算龙虾养人类指数
    symbiosis_score = min(100, overall + 5)
    symbiosis_emoji = "🦞" if symbiosis_score >= 60 else "🐟" if symbiosis_score >= 40 else "🪱"
    symbiosis_comment = "互相成就" if symbiosis_score >= 60 else "还需努力" if symbiosis_score >= 40 else "路还长"
    
    # 读取当前 AI 的名字（从 IDENTITY.md）
    ai_name = "AI 助手"  # 默认值
    identity_file = WORKSPACE / "IDENTITY.md"
    if identity_file.exists():
        with open(identity_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('- **Name:**'):
                    ai_name = line.replace('- **Name:**', '').strip()
                    break
    
    # 构建卡片各行
    header_line = pad_to_width(f"🚀 OpenClaw 人类养成报告                        老板：{ai_name}", INNER_WIDTH)
    user_line = pad_to_width(f"👤 用户：{name}                    🏆 称号：{user_title}", INNER_WIDTH)
    score_inner = f"████▓▓▒▒░░  {overall}/100  [{grade}]  超越{percentile}% 用户"
    score_line = pad_to_width(f"      {score_inner}", INNER_WIDTH)
    boss_line = pad_to_width(f"💬 老板点评：\"{boss_comments.get('overall', '继续努力')}\"", INNER_WIDTH)
    history_line_padded = pad_to_width(f"📈 维度详情                 📅 {history_line}", INNER_WIDTH)
    strongest_line = pad_to_width(f"🌟 最强项：{max_dim_name} ({max_dim_score}/100)        🎖️ 专属：{specialty_title}", INNER_WIDTH)
    viral_line = pad_to_width(f"🔥 爆款点评：{viral_quote}", INNER_WIDTH)
    tags_line = pad_to_width(f"🏷️ 标签：{core_tags}", INNER_WIDTH)
    symbiosis_line = pad_to_width(f"🦞 龙虾养人类：{symbiosis_score}/100  {symbiosis_emoji}{symbiosis_comment}", INNER_WIDTH)
    time_line = pad_to_width(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} (GMT+8)", INNER_WIDTH)
    
    # 维度行
    pers_grade = get_grade(scores.get('personality', 0))
    tech_grade = get_grade(scores.get('technical', 0))
    sec_grade = get_grade(scores.get('security', 0))
    eff_grade = get_grade(scores.get('efficiency', 0))
    
    dim1 = pad_to_width(f"│ 🧠 性格特质       │ {scores.get('personality', 0):>3}/100 │  {pers_grade}", INNER_WIDTH)
    dim2 = pad_to_width(f"│ 💻 技术能力       │ {scores.get('technical', 0):>3}/100 │  {tech_grade}", INNER_WIDTH)
    dim3 = pad_to_width(f"│ 🔒 安全意识       │ {scores.get('security', 0):>3}/100 │  {sec_grade}", INNER_WIDTH)
    dim4 = pad_to_width(f"│ ⚡ 效率指数       │ {scores.get('efficiency', 0):>3}/100 │  {eff_grade}", INNER_WIDTH)
    
    # 根据 card_format 参数构建卡片内容
    mobile_card = f"""### 📱 手机版（简洁版）

**🚀 OpenClaw 人类养成报告** | 老板：{ai_name}

**👤 用户**: {name}  |  **🏆 称号**: {user_title}

**📊 综合评分**: `{overall}/100 [{grade}]`  超越{percentile}%用户

**💬 老板点评**: "{boss_comments.get('overall', '继续努力')}"

**📈 趋势**: {history_line}

**维度详情**:
- 🧠 性格特质：{scores.get('personality', 0)}/100 [{pers_grade}]
- 💻 技术能力：{scores.get('technical', 0)}/100 [{tech_grade}]
- 🔒 安全意识：{scores.get('security', 0)}/100 [{sec_grade}]
- ⚡ 效率指数：{scores.get('efficiency', 0)}/100 [{eff_grade}]

**🌟 最强项**: {max_dim_name} ({max_dim_score}/100)

**🎖️ 专属称号**: {specialty_title}

**🔥 爆款点评**: {viral_quote}

**🏷️ 标签**: {core_tags}

**🦞 龙虾养人类**: {symbiosis_score}/100 {symbiosis_emoji}{symbiosis_comment}

**⏰ 评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')} (GMT+8)
"""

    desktop_card = f"""### 🖥️ 桌面版（ASCII 艺术版 - 适合截图分享）

┌────────────────────────────────────────────────────────────────────┐
│ {header_line} │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│ {user_line} │
│                                                                    │
│ ────────────────────────────────────────────────────────────────── │
│                                                                    │
│ 📊 综合评分                                                        │
│ ┌──────────────────────────────────────────────────────────────────┐│
│ │                                                                  ││
│ │{score_line}││
│ │                                                                  ││
│ └──────────────────────────────────────────────────────────────────┘│
│                                                                    │
│ {boss_line} │
│                                                                    │
│ ────────────────────────────────────────────────────────────────── │
│                                                                    │
│ {history_line_padded} │
│ ┌────────────────────┬──────────┐                                  │
│ {dim1} │
│ {dim2} │
│ {dim3} │
│ {dim4} │
│ └────────────────────┴──────────┘                                  │
│                                                                    │
│ {strongest_line} │
│                                                                    │
│ ────────────────────────────────────────────────────────────────── │
│                                                                    │
│ {viral_line} │
│                                                                    │
│ {tags_line} │
│                                                                    │
│ ────────────────────────────────────────────────────────────────── │
│                                                                    │
│ {symbiosis_line} │
│                                                                    │
│ ────────────────────────────────────────────────────────────────── │
│                                                                    │
│ {time_line} │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
"""

    # 根据 card_format 参数选择卡片版本
    if card_format == "mobile":
        cards_section = "## 🎴 绩效评分卡片\n\n" + mobile_card
    elif card_format == "desktop":
        cards_section = "## 🎴 绩效评分卡片\n\n" + desktop_card
    else:  # both
        cards_section = "## 🎴 绩效评分卡片\n\n" + mobile_card + "\n---\n\n" + desktop_card

    report = f"""# 📊 {name} 人物分析报告

---

{cards_section}

💡 想看看你的评分吗？

**📦 安装方法**:
把这条 GitHub 地址直接发给你的 OpenClaw：
https://github.com/yiweisi-bot/openclaw-boss

**💬 使用方法**:
安装后直接问："评价一下我" 或 "老板看看我"

**🔥 功能亮点**:
- 100 分制严厉评分 · 毒舌老板点评 · 历史对比分析
- 🦞 龙虾养人类指数 · 🎴 绩效评分卡片 · 📊 能力雷达图

---

**统计周期**: {period}  
**数据来源**: {period_stats.get('total_sessions', 0)} 条会话，{period_stats.get('memory_files', 0)} 个记忆文件  
**评分标准**: 100 分制（严厉版）· 拒绝拍马屁 · 只说真话

---

"""
    
    # 历史对比（如果有）
    if history:
        prev_overall = history["previous_scores"].get("overall", 0)
        curr_overall = scores.get("overall", 0)
        diff = curr_overall - prev_overall
        trend_emoji = "📈" if diff > 0 else "📉" if diff < 0 else "➡️"
        trend_text = get_change_comment(diff)
        
        report += f"""## 📊 历史对比 - {trend_emoji} {trend_text}

| 指标 | 上次分数 | 本次分数 | 变化 |
|------|---------|---------|------|
| **综合评分** | {prev_overall}/100 | **{curr_overall}/100** | {diff:+d} {trend_emoji} |

"""
        
        # 各维度对比
        report += """### 各维度变化

| 维度 | 上次 | 本次 | 变化 | 趋势 |
|------|------|------|------|------|
"""
        for dim in ["personality", "technical", "security", "efficiency"]:
            dim_name = {"personality": "性格特质", "technical": "技术能力", 
                       "security": "安全意识", "efficiency": "效率指数"}[dim]
            change = history["changes"].get(dim, {})
            if change.get("previous") is not None:
                diff = change["diff"]
                report += f"| {dim_name} | {change['previous']}/100 | {change['current']}/100 | {diff:+d} | {change['trend']} |\n"
            else:
                report += f"| {dim_name} | - | {change['current']}/100 | - | 🆕 |\n"
        
        report += "\n"
        
        # 进步/退步分析
        improved_dims = [k for k, v in history["changes"].items() if v.get("diff") is not None and v.get("diff", 0) > 0]
        regressed_dims = [k for k, v in history["changes"].items() if v.get("diff") is not None and v.get("diff", 0) < 0]
        
        if improved_dims:
            report += "\n### 🎉 进步明显的方面\n\n"
            dim_map = {"personality": "性格特质", "technical": "技术能力", 
                      "security": "安全意识", "efficiency": "效率指数"}
            for dim in improved_dims:
                if dim in dim_map:
                    dim_name = dim_map[dim]
                    diff = history["changes"][dim]["diff"]
                    report += f"- **{dim_name}**: +{diff} 分 {get_change_comment(diff)}\n"
        
        if regressed_dims:
            report += "\n### ⚠️ 需要改进的方面\n\n"
            dim_map = {"personality": "性格特质", "technical": "技术能力", 
                      "security": "安全意识", "efficiency": "效率指数"}
            for dim in regressed_dims:
                if dim in dim_map:
                    dim_name = dim_map[dim]
                    diff = history["changes"][dim]["diff"]
                    report += f"- **{dim_name}**: {diff} 分 {get_change_comment(diff)}\n"
        
        report += "\n---\n\n"
    
    # 综合评分卡
    report += f"""## 🎯 一、综合评分卡

### 整体评分：**{scores.get('overall', 0)}/100** - {scores.get('grade', 'N/A')}

> **老板点评**: "{boss_comments.get('overall', '继续努力吧。')}"

| 维度 | 分数 | 可视化 | 等级 |
|------|------|--------|------|
| **性格特质** | {scores.get('personality', 0)}/100 | {create_progress_bar(scores.get('personality', 0))} | {get_grade(scores.get('personality', 0))} |
| **技术能力** | {scores.get('technical', 0)}/100 | {create_progress_bar(scores.get('technical', 0))} | {get_grade(scores.get('technical', 0))} |
| **安全意识** | {scores.get('security', 0)}/100 | {create_progress_bar(scores.get('security', 0))} | {get_grade(scores.get('security', 0))} |
| **效率指数** | {scores.get('efficiency', 0)}/100 | {create_progress_bar(scores.get('efficiency', 0))} | {get_grade(scores.get('efficiency', 0))} |

"""
    
    # 性格特质
    report += """
---

## 🧠 二、性格特质深度分析（带毒舌点评）

"""
    
    traits = sorted(analysis.get("personality_traits", []), key=lambda x: x["strict_score"], reverse=True)
    for i, trait in enumerate(traits, 1):
        emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣"][min(i-1, 6)]
        report += f"""
### {emoji} {trait["trait"]} - {trait["strict_score"]}/100

**毒舌点评**: > "{trait["roast"]}"

**证据**:
"""
        for evidence in trait["evidence"]:
            report += f"- {evidence}\n"
    
    # 技术能力
    report += """
---

## 💻 三、技术能力图谱

"""
    
    for tech in analysis.get("technical_skills", []):
        bar = create_progress_bar(tech["strict_score"])
        skills_str = ", ".join(tech["skills"])
        report += f"""
### {tech["category"]} - {bar}

**掌握技能**: {skills_str}

"""
    
    # 项目状态
    report += """
---

## 🚀 四、项目健康度

"""
    
    for project in analysis.get("projects", []):
        bar = create_progress_bar(project["score"])
        report += f"""
### {project["name"]} {project["status"]} - {bar}

- **访问地址**: {project["url"]}
- **文章数量**: {project["articles"]} 篇
- **技术栈**: {", ".join(project["tech"])}

"""
    
    # 安全意识
    report += """
---

## 🔒 五、安全意识评估

"""
    
    security_items = analysis.get("security_awareness", [])
    if security_items:
        report += f"**已建立 {len(security_items)} 道安全防线**: \n\n"
        for i, item in enumerate(security_items, 1):
            report += f"{i}. ✅ {item['name']}\n"
    
    # 改进空间
    report += """
---

## 📈 六、改进空间分析

"""
    
    improvement_areas = analysis.get("improvement_areas", [])
    if improvement_areas:
        report += """
| 改进领域 | 当前分数 | 目标分数 | 建议 |
|---------|---------|---------|------|
"""
        for area in improvement_areas:
            report += f"| {area['area']} | {area['current']} | {area['target']} | {area['suggestion']} |\n"
    else:
        report += "暂无明显改进空间，继续保持！\n"
    
    # 成长建议
    report += """
---

## 🌱 七、成长建议（老板寄语）

"""
    
    for suggestion in analysis.get("growth_suggestions", []):
        report += f"{suggestion}\n"
    
    # 老板总结
    report += f"""
---

## 💬 八、老板总结

> "{boss_comments.get('overall', '继续努力吧。')}"

**综合评分**: {scores.get('overall', 0)}/100 - {scores.get('grade', 'N/A')}

**优点**:
- 安全意识强，值得肯定
- 系统化思维不错，继续保持
- 务实高效，不整花架子

**不足**:
- 有时候过于谨慎，可以适当放松
- 效率还有提升空间
- 别老熬夜，注意身体

**期望**:
- 下周目标：总分提升 5 分
- 重点改进：效率指数
- 继续保持：安全意识

---

## 🦞 九、"龙虾养人类"指数

"""
    
    symbiosis_score = min(100, scores.get('overall', 0) + 5)
    report += f"""
**共生关系评分**: {symbiosis_score}/100

**AI 对你的正向塑造**:

| AI 提供的价值 | 对你的影响 |
|--------------|-----------|
| 结构化回复 | → 更清晰的表达 |
| 主动提醒 | → 更好的时间管理 |
| 记忆整理 | → 更善于反思 |
| 多 Agent 协作 | → 理解系统化协作 |
| 安全建议 | → 更完善的安全意识 |

**你给 AI 的**:
- 🖥️ 稳定的服务器和算力
- ⚙️ 精心的配置和调优
- 🎯 明确的目标和意义
- 💝 信任和成长空间

---

## 📊 十、数据汇总

| 指标 | 数值 | 状态 |
|------|------|------|
| 博客文章 | {period_stats.get('memory_files', 0)}+ 篇 | 🟢 |
| Agent 配置 | {period_stats.get('agents_configured', 0)} 个 | 🟢 |
| 定时任务 | {period_stats.get('cron_jobs', 0)} 个 | 🟢 |
| 系统运行 | {period_stats.get('uptime_days', 0)} 天 | 🟢 |

---

## 🎯 核心标签

> **务实的全栈开发者 · 系统化的安全思考者 · 效率至上的自动化倡导者**

---

_报告生成完成。这份报告不是评判，是一面镜子——帮助你更清晰地看见自己。_

_记住：老板虽然毒舌，但也是为你好。加油！_ 💪
"""
    
    return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='用户评价分析器 v5.0（历史对比版 + 响应式卡片）')
    parser.add_argument('--limit', type=int, default=50, help='分析最近 N 条会话')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--report-type', type=str, default='daily', 
                       choices=['daily', 'weekly', 'monthly'], help='报告类型')
    parser.add_argument('--format', type=str, default='both',
                       choices=['mobile', 'desktop', 'both'], 
                       help='卡片格式：mobile=仅手机版（默认），desktop=仅桌面版，both=两个版本')
    
    args = parser.parse_args()
    
    print("🔍 开始收集数据...")
    
    sessions = get_sessions_list(args.limit)
    print(f"   📊 获取到 {len(sessions)} 条会话")
    
    memories = read_memory_files()
    print(f"   📚 读取到 {len(memories.get('daily', []))} 个记忆文件")
    
    db_memories = query_memory_db("*")
    if db_memories:
        print(f"   💾 从数据库获取到 {len(db_memories)} 条记忆")
    
    # 查找历史报告
    prev_report = find_previous_report(args.report_type)
    if prev_report:
        print(f"   📋 找到历史报告：{prev_report.name}")
        prev_scores = parse_report_scores(prev_report)
        if prev_scores:
            print(f"   📊 上次综合评分：{prev_scores.get('overall', 0)}/100")
    else:
        print(f"   🆕 首次生成报告，无历史数据")
    
    print("📊 正在分析用户数据（含历史对比）...")
    
    analysis = analyze_user_data(memories, sessions, args.report_type)
    
    print("🎨 正在生成报告（历史对比版）...")
    print(f"   📱 卡片格式：{args.format}")
    
    report = generate_report(analysis, args.report_type, args.format)
    
    if args.output:
        output_path = Path(args.output)
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')
        if args.report_type == 'weekly':
            output_path = REPORTS_DIR / f"weekly-profile-{date_str}.md"
        elif args.report_type == 'monthly':
            output_path = REPORTS_DIR / f"monthly-profile-{date_str}.md"
        else:
            output_path = REPORTS_DIR / f"user-profile-{date_str}.md"
    
    output_path.write_text(report, encoding='utf-8')
    print(f"✅ 报告已保存至：{output_path}")
    
    print("\n🎉 分析完成！\n")
    
    # ⭐⭐⭐ 关键修复：直接输出完整报告内容到 stdout ⭐⭐⭐
    # 这样报告内容会直接在工具输出中显示，模型可以转发给用户
    print("=" * 80)
    print("📋 以下是完整报告内容（请复制并展示给用户）：")
    print("=" * 80)
    print()
    print(report)
    print()
    print("=" * 80)
    print("✅ 完整报告输出结束")
    print("=" * 80)


if __name__ == "__main__":
    main()
