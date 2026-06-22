#!/usr/bin/env python3
"""
快速分析抖音视频脚本
用法: python3 analyze_douyin.py [抖音链接]
"""

import sys
import os
import re
import subprocess
import json
import time

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from trader_simulator import simulate_blogger, BUILTIN_PROFILES, generate_report, RecommendationEngine


def extract_video_id(url: str) -> str:
    """从抖音链接提取视频ID"""
    # 支持多种格式
    patterns = [
        r'douyin\.com/([a-zA-Z0-9]+)',  # 标准短链
        r'v\.douyin\.com/([a-zA-Z0-9]+)',  # v.douyin.com 格式
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def analyze_douyin_link(url: str) -> dict:
    """分析抖音链接，返回视频摘要（需要通过浏览器抓取）"""
    
    # 这里是一个占位符
    # 实际使用时，通过浏览器打开页面并提取章节要点
    return {
        "video_id": extract_video_id(url),
        "title": "待抓取",
        "summary": "需要通过浏览器自动化抓取视频内容"
    }


def quick_simulate(blogger_name: str) -> str:
    """快速模拟博主风格（使用内置配置）"""
    
    if blogger_name not in BUILTIN_PROFILES:
        return f"❌ 未找到博主【{blogger_name}】\n支持的博主: {', '.join(BUILTIN_PROFILES.keys())}"
    
    profile = BUILTIN_PROFILES[blogger_name].copy()
    
    # 生成推荐
    engine = RecommendationEngine(profile)
    recommendations = engine.generate_recommendations({})
    
    # 生成报告
    report = generate_report(blogger_name, profile, recommendations)
    
    return report


def main():
    if len(sys.argv) < 2:
        # 默认模拟文主任
        print("=" * 60)
        print("🎯 Trader Simulator - 炒作者模拟器")
        print("=" * 60)
        print("\n📋 内置博主:")
        for name in BUILTIN_PROFILES.keys():
            profile = BUILTIN_PROFILES[name]
            print(f"  • {name}: {', '.join(profile['style_tags'][:3])}")
        
        print("\n" + "=" * 60)
        print("🚀 模拟【文主任】的选股思路:")
        print("=" * 60 + "\n")
        
        report = quick_simulate("文主任")
        print(report)
        return
    
    command = sys.argv[1]
    
    if command in ["模拟", "simulate"]:
        blogger = sys.argv[2] if len(sys.argv) > 2 else "文主任"
        print(f"\n🚀 正在模拟【{blogger}】的选股思路...\n")
        report = quick_simulate(blogger)
        print(report)
    
    elif command in ["列出", "list"]:
        print("\n📋 支持的博主:")
        for name in BUILTIN_PROFILES.keys():
            print(f"  • {name}")
    
    else:
        # 假设是抖音链接
        url = command
        print(f"\n🔍 分析抖音链接: {url}")
        result = analyze_douyin_link(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
