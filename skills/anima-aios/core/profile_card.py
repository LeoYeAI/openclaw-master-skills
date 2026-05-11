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
Memora v4.0 - Profile Card Generator

极简纯文本认知画像卡片

设计理念：
- 潜移默化，不浮夸
- 一目了然，适合每日查看
- 纯文本/Unicode，无需依赖

Author: 枢衡
Date: 2026-03-20
Version: 5.0.0
"""

from typing import Dict, Optional
from datetime import datetime


class ProfileCardGenerator:
    """认知画像卡片生成器"""
    
    # 维度中文名称
    DIMENSION_NAMES = {
        'creation': '知识创造',
        'collaboration': '协作认知',
        'understanding': '知识内化',
        'application': '知识应用',
        'metacognition': '元认知'
    }
    
    # 维度图标
    DIMENSION_ICONS = {
        'creation': '💡',
        'collaboration': '🤝',
        'understanding': '📚',
        'application': '🔧',
        'metacognition': '🤔'
    }
    
    def generate_card(self, profile: Dict, show_trends: bool = True) -> str:
        """
        生成认知画像卡片
        
        Args:
            profile: 认知画像字典
            show_trends: 是否显示趋势
        
        Returns:
            Markdown 格式卡片
        """
        lines = []
        
        # 标题
        lines.append(f"🧠 认知画像 — {profile['agent']}")
        lines.append("")
        
        # 等级信息
        level = profile.get('level', 20)
        stage = profile.get('stage', 'Novice 新手')
        badge = profile.get('badge', '🌱 Novice')
        score = profile.get('cognitive_score', 0)
        
        # 进度条（10 段）
        bar_length = int(score / 10)
        bar = '█' * bar_length + '░' * (10 - bar_length)
        
        lines.append(f"Lv.{level} {badge} {stage}")
        lines.append(f"[{bar}] {score:.1f}/100")
        lines.append("")
        
        # 五维雷达图（文本版）
        lines.append("━━━ 五维评估 ━━━")
        lines.append("")
        
        dimensions = profile.get('dimensions', {})
        
        # 团队排名信息
        team_rank = profile.get('team_rank', {})
        
        for dim, name in self.DIMENSION_NAMES.items():
            dim_data = dimensions.get(dim, {})
            score_dim = dim_data.get('score', 0)
            
            # 进度条（10 段）
            bar_len = int(score_dim / 10)
            bar = '█' * bar_len + '░' * (10 - bar_len)
            
            # 排名信息
            rank_info = ""
            if team_rank and dim in team_rank:
                rank = team_rank[dim]
                rank_info = f" (#{rank})"
            
            # 图标
            icon = self.DIMENSION_ICONS.get(dim, '·')
            
            lines.append(f"{icon} {name:8s} {bar} {score_dim:5.1f}{rank_info}")
        
        lines.append("")
        
        # 统计数据
        lines.append("━━━ 统计 ━━━")
        lines.append("")
        
        stats = profile.get('statistics', {})
        
        lines.append(f"📝 总 Facts:    {stats.get('total_facts', 0)}")
        lines.append(f"   ├─ Semantic: {stats.get('semantic_facts', 0)}")
        lines.append(f"   └─ Episodic: {stats.get('episodic_facts', 0)}")
        lines.append(f"🔍 记忆搜索：  {stats.get('memory_searches', 0)}")
        lines.append(f"📤 知识分享：  {stats.get('shared_knowledge', 0)}")
        lines.append(f"📊 周报复盘：  {stats.get('weekly_reviews', 0)}")
        lines.append(f"🤝 协作任务：  {stats.get('collab_tasks', 0)}")
        
        lines.append("")
        
        # 趋势信息（如果可用）
        if show_trends and profile.get('trends'):
            lines.append("━━━ 趋势 ━━━")
            lines.append("")
            
            trends = profile['trends']
            overall_trend = trends.get('overall', 0)
            
            if overall_trend > 0:
                trend_icon = "📈"
                trend_text = f"+{overall_trend:.1f}"
            elif overall_trend < 0:
                trend_icon = "📉"
                trend_text = f"{overall_trend:.1f}"
            else:
                trend_icon = "➡️"
                trend_text = "0.0"
            
            lines.append(f"{trend_icon} 本周变化：{trend_text}")
            
            # 连续记录
            streak = trends.get('streak_days', 0)
            if streak > 0:
                lines.append(f"🔥 连续记录：{streak} 天")
            
            lines.append("")
        
        # 底部信息
        lines.append("━━━━━━━━━━━━━━")
        generated_at = profile.get('generated_at', '')
        if generated_at:
            date_str = generated_at[:10]
            lines.append(f"生成时间：{date_str}")
        
        return '\n'.join(lines)
    
    def generate_simple_card(self, profile: Dict) -> str:
        """
        生成简化版卡片（适合每日快速查看）
        
        Args:
            profile: 认知画像字典
        
        Returns:
            简化版卡片
        """
        lines = []
        
        # 等级和分数
        level = profile.get('level', 20)
        badge = profile.get('badge', '🌱')
        score = profile.get('cognitive_score', 0)
        
        lines.append(f"🧠 {profile['agent']} | Lv.{level} {badge} | {score:.1f}/100")
        lines.append("")
        
        # 五维简图
        dimensions = profile.get('dimensions', {})
        
        for dim, name in self.DIMENSION_NAMES.items():
            dim_data = dimensions.get(dim, {})
            dim_score = dim_data.get('score', 0)
            
            # 5 段进度条（更简洁）
            bar_len = int(dim_score / 20)
            bar = '█' * bar_len + '░' * (5 - bar_len)
            
            lines.append(f"{name:8s} {bar} {dim_score:5.1f}")
        
        return '\n'.join(lines)
    
    def generate_comparison_card(self, profiles: list) -> str:
        """
        生成团队对比卡片
        
        Args:
            profiles: 多个 Agent 的画像列表
        
        Returns:
            团队对比卡片
        """
        if not profiles:
            return "⚠️  无数据"
        
        lines = []
        lines.append("🏆 团队认知排名")
        lines.append("")
        
        # 按综合分数排序
        sorted_profiles = sorted(
            profiles,
            key=lambda p: p.get('cognitive_score', 0),
            reverse=True
        )
        
        # 表头
        lines.append(f"{'排名':<4} {'Agent':<12} {'等级':<8} {'分数':<6} {'趋势'}")
        lines.append("─" * 50)
        
        # 排名
        for i, profile in enumerate(sorted_profiles, 1):
            rank_icon = f"#{i}"
            if i == 1:
                rank_icon = "🥇"
            elif i == 2:
                rank_icon = "🥈"
            elif i == 3:
                rank_icon = "🥉"
            
            agent = profile.get('agent', 'Unknown')[:10]
            level = profile.get('level', 20)
            score = profile.get('cognitive_score', 0)
            
            # 趋势（如果可用）
            trend = profile.get('trends', {}).get('overall', 0)
            if trend > 0:
                trend_icon = f"📈 +{trend:.1f}"
            elif trend < 0:
                trend_icon = f"📉 {trend:.1f}"
            else:
                trend_icon = "➡️ 0.0"
            
            lines.append(f"{rank_icon:<4} {agent:<12} Lv.{level:<5} {score:<6.1f} {trend_icon}")
        
        lines.append("")
        lines.append(f"总计 {len(profiles)} 个 Agent")
        
        return '\n'.join(lines)


def main():
    """测试卡片生成器"""
    import json
    import sys
    from pathlib import Path
    
    # 添加核心模块路径
    sys.path.insert(0, str(Path(__file__).parent))
    
    from cognitive_profile import CognitiveProfileGenerator
    
    if len(sys.argv) < 2:
        print("用法：python3 profile_card.py <Agent 名称> [simple|comparison]")
        sys.exit(1)
    
    agent_name = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'full'
    
    # 生成认知画像
    generator = CognitiveProfileGenerator(agent_name)
    profile = generator.generate_profile()
    
    # 生成卡片
    card_gen = ProfileCardGenerator()
    
    if mode == 'simple':
        card = card_gen.generate_simple_card(profile)
    elif mode == 'comparison':
        # 需要扫描团队
        try:
            from .team_scanner import TeamScanner
        except ImportError:
            from team_scanner import TeamScanner
        scanner = TeamScanner()
        active_agents = scanner.scan_active_agents()
        
        profiles = []
        for agent in active_agents:
            try:
                gen = CognitiveProfileGenerator(agent)
                profiles.append(gen.generate_profile())
            except Exception:
                continue
        
        card = card_gen.generate_comparison_card(profiles)
    else:
        card = card_gen.generate_card(profile)
    
    print(card)


if __name__ == '__main__':
    main()
