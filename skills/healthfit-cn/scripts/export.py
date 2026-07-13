#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HealthFit 数据导出脚本
支持导出为 JSON、CSV、Markdown 格式
"""

import json
import csv
import sqlite3
from pathlib import Path
from datetime import datetime
import argparse
import shutil


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "db" / "healthfit.db"


def export_json_files(output_dir: Path, include_private: bool = False):
    """导出所有 JSON 文件"""
    json_dir = DATA_DIR / "json"
    
    if not json_dir.exists():
        print("⚠️ JSON 目录不存在，跳过")
        return
    
    exported_count = 0
    skipped_count = 0
    
    for json_file in json_dir.glob("*.json"):
        # 跳过私密文件（除非明确要求）
        if json_file.name == "private_sexual_health.json" and not include_private:
            print(f"⏭️ 跳过私密文件：{json_file.name}")
            skipped_count += 1
            continue
        
        # 复制文件
        dest = output_dir / json_file.name
        shutil.copy2(json_file, dest)
        print(f"✅ 导出：{json_file.name}")
        exported_count += 1
    
    print(f"\n📊 JSON 文件导出完成：{exported_count} 个文件，跳过 {skipped_count} 个私密文件")


def export_database_to_csv(output_dir: Path):
    """将数据库表导出为 CSV"""
    if not DB_PATH.exists():
        print("⚠️ 数据库不存在，跳过")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    exported_count = 0
    
    for (table_name,) in tables:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 写入 CSV
        csv_path = output_dir / f"{table_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"✅ 导出表：{table_name}.csv ({len(rows)} 条记录)")
        exported_count += 1
    
    conn.close()
    print(f"\n📊 数据库导出完成：{exported_count} 张表")


def generate_markdown_report(output_dir: Path):
    """生成可读的 Markdown 报告"""
    report_lines = [
        "# HealthFit 数据导出报告",
        f"\n导出时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n"
    ]
    
    # 读取用户档案
    profile_path = DATA_DIR / "json" / "profile.json"
    if profile_path.exists():
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        report_lines.append("## 用户档案\n")
        report_lines.append(f"- 昵称：{profile.get('nickname', '未设置')}")
        report_lines.append(f"- 身高：{profile.get('height_cm', '未设置')} cm")
        report_lines.append(f"- 体重：{profile.get('weight_kg', '未设置')} kg")
        report_lines.append(f"- 主要目标：{profile.get('primary_goal', '未设置')}")
        report_lines.append(f"- 创建时间：{profile.get('created_at', '未知')}")
        report_lines.append(f"- 上次更新：{profile.get('updated_at', '未知')}\n")
    
    # 统计数据库记录数
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        report_lines.append("## 数据统计\n")
        
        cursor.execute("SELECT COUNT(*) FROM workouts")
        report_lines.append(f"- 运动记录：{cursor.fetchone()[0]} 条")
        
        cursor.execute("SELECT COUNT(*) FROM nutrition_entries")
        report_lines.append(f"- 饮食记录：{cursor.fetchone()[0]} 条")
        
        cursor.execute("SELECT COUNT(*) FROM metrics_daily")
        report_lines.append(f"- 每日指标：{cursor.fetchone()[0]} 条")
        
        cursor.execute("SELECT COUNT(*) FROM pr_records")
        report_lines.append(f"- PR 记录：{cursor.fetchone()[0]} 条")
        
        cursor.execute("SELECT COUNT(*) FROM weekly_summaries")
        report_lines.append(f"- 周统计：{cursor.fetchone()[0]} 条")
        
        cursor.execute("SELECT COUNT(*) FROM monthly_summaries")
        report_lines.append(f"- 月统计：{cursor.fetchone()[0]} 条\n")
        
        conn.close()
    
    # 写入 TXT 日志统计
    txt_dir = DATA_DIR / "txt"
    if txt_dir.exists():
        report_lines.append("## 文本日志\n")
        
        workout_log = txt_dir / "workout_log.txt"
        if workout_log.exists():
            lines = workout_log.read_text(encoding="utf-8").strip().split('\n')
            report_lines.append(f"- 运动日志：{len(lines)} 条记录")
        
        nutrition_log = txt_dir / "nutrition_log.txt"
        if nutrition_log.exists():
            lines = nutrition_log.read_text(encoding="utf-8").strip().split('\n')
            report_lines.append(f"- 饮食日志：{len(lines)} 条记录")
        
        achievements = txt_dir / "achievements.txt"
        if achievements.exists():
            lines = achievements.read_text(encoding="utf-8").strip().split('\n')
            report_lines.append(f"- 成就记录：{len(lines)} 条")
        
        report_lines.append("")
    
    # 写入报告
    report_path = output_dir / "export_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"✅ 生成报告：export_report.md")


def main():
    parser = argparse.ArgumentParser(description="HealthFit 数据导出")
    parser.add_argument("--output", "-o", default="./healthfit_export", help="导出目录")
    parser.add_argument("--include-private", action="store_true", help="包含私密数据（需二次确认）")
    parser.add_argument("--format", choices=["all", "json", "csv", "markdown"], default="all",
                       help="导出格式")
    
    args = parser.parse_args()
    
    # 私密数据二次确认
    if args.include_private:
        print("\n" + "="*60)
        print("⚠️  警告：高度敏感数据导出确认  ⚠️")
        print("="*60)
        print("""
您选择了导出私密数据，包括：
  - 性健康记录（private_sexual_health.json）
  - 所有个人健康隐私信息

此操作风险：
  ❌ 备份文件可能被他人访问
  ❌ 云同步可能自动上传
  ❌ 数据泄露可能造成隐私损害

请确认您理解以上风险。
""")
        print("="*60)
        
        # 随机验证码确认
        import random
        import string
        verify_code = ''.join(random.choices(string.ascii_uppercase, k=6))
        print(f"\n请输入以下验证码以确认：{verify_code}")
        
        user_input = input("验证码：").strip().upper()
        if user_input != verify_code:
            print("❌ 验证码错误，已取消操作")
            return
        
        # 记录操作日志
        log_path = DATA_DIR / "security_log.txt"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] 私密数据导出操作已执行\n")
        
        print("✅ 验证通过，继续执行导出...\n")
    
    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = output_dir / f"export_{timestamp}"
    export_dir.mkdir()
    
    print(f"📁 导出目录：{export_dir}\n")
    
    # 执行导出
    if args.format in ["all", "json"]:
        print("📄 导出 JSON 文件...")
        export_json_files(export_dir, args.include_private)
        print()
    
    if args.format in ["all", "csv"]:
        print("📊 导出数据库为 CSV...")
        export_database_to_csv(export_dir)
        print()
    
    if args.format in ["all", "markdown"]:
        print("📝 生成 Markdown 报告...")
        generate_markdown_report(export_dir)
        print()
    
    print(f"\n✅ 导出完成！目录：{export_dir}")
    print(f"💡 提示：可手动压缩备份，或上传到云存储")


if __name__ == "__main__":
    main()
