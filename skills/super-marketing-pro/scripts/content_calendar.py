#!/usr/bin/env python3
"""
内容日历生成器 - 自动生成每周社媒内容计划

Usage:
    python3 content_calendar.py --week 1 --theme "新品推广"
    python3 content_calendar.py --month 3 --output content_plan.csv
"""

import argparse
import csv
from datetime import datetime, timedelta
import random

# 内容主题库
CONTENT_THEMES = {
    "新品推广": {
        "linkedin": ["新品技术解析", "市场趋势分析", "客户应用场景"],
        "youtube": ["新品开箱视频", "产品对比测试", "工厂生产实拍"],
        "instagram": ["新品美图", "细节特写", "应用场景"],
        "douyin": ["新品展示", "功能测试", "客户反馈"],
        "xiaohongshu": ["新品测评", "使用教程", "避坑指南"]
    },
    "工厂实力": {
        "linkedin": ["生产能力介绍", "质量控制体系", "团队风采"],
        "youtube": ["工厂参观视频", "生产流程展示", "质检过程"],
        "instagram": ["工厂日常", "设备展示", "团队照片"],
        "douyin": ["工厂实拍", "出货视频", "老板日常"],
        "xiaohongshu": ["工厂探秘", "生产揭秘", "源头优势"]
    },
    "客户案例": {
        "linkedin": ["合作案例分享", "客户见证", "成功故事"],
        "youtube": ["客户采访视频", "案例展示", "应用效果"],
        "instagram": ["客户产品展示", "合作照片", "成果展示"],
        "douyin": ["客户反馈", "大货出货", "合作故事"],
        "xiaohongshu": ["客户案例", "合作经验", "效果分享"]
    },
    "行业知识": {
        "linkedin": ["行业趋势分析", "技术科普", "市场洞察"],
        "youtube": ["材料知识科普", "选购指南", "行业分析"],
        "instagram": ["知识卡片", "对比图表", "数据可视化"],
        "douyin": ["材料测试", "知识科普", "选购技巧"],
        "xiaohongshu": ["材料科普", "选购指南", "避坑攻略"]
    }
}

# 内容格式模板
CONTENT_FORMATS = {
    "linkedin": ["图文文章", "纯文字", "图片轮播", "视频"],
    "youtube": ["长视频(5-10分钟)", "短视频(1-3分钟)", "Shorts"],
    "instagram": ["单图", "轮播图", "Reels", "Stories"],
    "douyin": ["短视频(15-60秒)", "图文", "直播"],
    "xiaohongshu": ["图文笔记", "视频笔记"]
}

# 最佳发布时间
BEST_TIMES = {
    "linkedin": ["周二 9:00", "周三 9:00", "周四 9:00"],
    "youtube": ["周六 10:00", "周日 10:00"],
    "instagram": ["周一 12:00", "周三 15:00", "周五 18:00"],
    "douyin": ["12:00", "18:00", "21:00"],
    "xiaohongshu": ["7:00", "12:00", "20:00"]
}

def generate_weekly_calendar(week_num, theme):
    """生成周内容日历"""
    calendar = []
    
    # 获取主题内容
    theme_content = CONTENT_THEMES.get(theme, CONTENT_THEMES["行业知识"])
    
    # 周一到周日
    days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    
    for day in days:
        day_plan = {"day": day, "platforms": []}
        
        # 每个平台安排内容
        for platform, contents in theme_content.items():
            if day in ["周一", "周三", "周五"] or platform in ["douyin", "xiaohongshu"]:
                # 去除随机性，基于周数和平台使用确定性算法，确保结果可复现且分布合理
                content_idx = (week_num + days.index(day)) % len(contents)
                format_idx = (week_num + days.index(day)) % len(CONTENT_FORMATS[platform])
                time_idx = days.index(day) % len(BEST_TIMES[platform])
                
                content = contents[content_idx]
                format_type = CONTENT_FORMATS[platform][format_idx]
                best_time = BEST_TIMES[platform][time_idx]
                
                day_plan["platforms"].append({
                    "platform": platform,
                    "content": content,
                    "format": format_type,
                    "time": best_time
                })
        
        calendar.append(day_plan)
    
    return calendar

def generate_monthly_calendar(month, themes):
    """生成月内容日历"""
    calendar = []
    
    for week in range(1, 5):
        theme = themes[(week - 1) % len(themes)]
        week_calendar = generate_weekly_calendar(week, theme)
        
        for day_plan in week_calendar:
            for platform_plan in day_plan["platforms"]:
                calendar.append({
                    "周": f"第{week}周",
                    "日期": day_plan["day"],
                    "平台": platform_plan["platform"],
                    "内容主题": platform_plan["content"],
                    "内容形式": platform_plan["format"],
                    "发布时间": platform_plan["time"],
                    "大主题": theme
                })
    
    return calendar

def export_to_csv(calendar, filename):
    """导出为CSV"""
    if not calendar:
        print("日历为空")
        return
    
    fieldnames = list(calendar[0].keys())
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(calendar)
    
    print(f"✅ 内容日历已导出: {filename}")

def print_calendar(calendar):
    """打印日历"""
    current_week = ""
    
    for item in calendar:
        if item["周"] != current_week:
            current_week = item["周"]
            print(f"\n{'='*60}")
            print(f"{current_week} - 主题: {item['大主题']}")
            print(f"{'='*60}")
        
        print(f"\n{item['日期']} | {item['平台']}")
        print(f"  内容: {item['内容主题']}")
        print(f"  形式: {item['内容形式']}")
        print(f"  时间: {item['发布时间']}")

def main():
    parser = argparse.ArgumentParser(description="社媒内容日历生成器 (OpenClaw 批量优化版)")
    parser.add_argument("--week", type=int, help="生成第几周的内容")
    parser.add_argument("--month", type=int, help="生成整月内容")
    parser.add_argument("--months", type=int, help="批量生成多个月的内容 (如: 3 表示生成一季度)")
    parser.add_argument("--theme", default="行业知识", help="内容主题")
    parser.add_argument("--output", help="输出CSV文件名")
    
    args = parser.parse_args()
    
    if args.week:
        calendar = generate_weekly_calendar(args.week, args.theme)
        print(f"\n📅 第{args.week}周内容日历（主题: {args.theme}）\n")
        for day in calendar:
            print(f"\n{day['day']}:")
            for platform in day['platforms']:
                print(f"  [{platform['platform']}] {platform['content']} ({platform['format']}) - {platform['time']}")
    
    elif args.months:
        print(f"\n🚀 启动多批次内容日历生成模式 (生成 {args.months} 个月)...")
        themes = ["新品推广", "工厂实力", "客户案例", "行业知识"]
        all_calendar = []
        
        for m in range(1, args.months + 1):
            month_cal = generate_monthly_calendar(m, themes)
            # 添加月份标记
            for item in month_cal:
                item["月份"] = f"第{m}月"
            all_calendar.extend(month_cal)
            print(f"✅ 成功生成第 {m} 个月内容日历 (共 {len(month_cal)} 条记录)")
            
        if args.output:
            export_to_csv(all_calendar, args.output)
        else:
            print("\n💡 提示: 批量生成建议使用 --output 导出为 CSV 文件")
            
    elif args.month:
        themes = ["新品推广", "工厂实力", "客户案例", "行业知识"]
        calendar = generate_monthly_calendar(args.month, themes)
        print_calendar(calendar)
        
        if args.output:
            export_to_csv(calendar, args.output)
    
    else:
        # 默认生成下周内容
        calendar = generate_weekly_calendar(1, args.theme)
        print(f"\n📅 下周内容日历（主题: {args.theme}）\n")
        for day in calendar:
            print(f"\n{day['day']}:")
            for platform in day['platforms']:
                print(f"  [{platform['platform']}] {platform['content']} ({platform['format']}) - {platform['time']}")

if __name__ == "__main__":
    main()
