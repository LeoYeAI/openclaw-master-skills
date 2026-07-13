#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HealthFit 数据库初始化脚本

用途：创建 SQLite 数据库表结构
执行：python scripts/init_db.py
"""

import sqlite3
from pathlib import Path


def init_database(db_path: Path):
    """初始化 HealthFit 数据库，创建所有必要的表"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 运动记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise_name TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight_kg REAL,
            duration_min INTEGER,
            distance_km REAL,
            rpe INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. 饮食记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nutrition_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL,
            food_name TEXT NOT NULL,
            calories INTEGER,
            protein_g REAL,
            carbs_g REAL,
            fat_g REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 3. 每日身体指标表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics_daily (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            weight_kg REAL,
            body_fat_pct REAL,
            waist_cm REAL,
            hip_cm REAL,
            resting_hr INTEGER,
            sleep_hours REAL,
            stress_level INTEGER,
            energy_level INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 4. 个人最佳成绩表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pr_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT NOT NULL,
            pr_type TEXT NOT NULL,
            value REAL NOT NULL,
            date_achieved TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 5. 周统计缓存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            week_start TEXT NOT NULL UNIQUE,
            week_end TEXT NOT NULL,
            total_workouts INTEGER,
            total_duration_min INTEGER,
            avg_calories INTEGER,
            avg_protein_g REAL,
            avg_sleep_hours REAL,
            weight_change_kg REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 6. 月统计缓存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL UNIQUE,
            total_workouts INTEGER,
            total_duration_min INTEGER,
            avg_weight_kg REAL,
            weight_change_kg REAL,
            pr_count INTEGER,
            workout_adherence_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建索引以优化查询
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nutrition_date ON nutrition_entries(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics_daily(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pr_exercise ON pr_records(exercise_name)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ 数据库初始化完成：{db_path}")
    print("📊 已创建数据表：")
    print("   - workouts (运动记录)")
    print("   - nutrition_entries (饮食记录)")
    print("   - metrics_daily (每日身体指标)")
    print("   - pr_records (个人最佳成绩)")
    print("   - weekly_summaries (周统计缓存)")
    print("   - monthly_summaries (月统计缓存)")


if __name__ == "__main__":
    # 数据库路径：healthfit/data/db/healthfit.db
    db_path = Path(__file__).parent.parent / "data" / "db" / "healthfit.db"
    
    # 确保目录存在
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 检查数据库是否已存在
    if db_path.exists():
        response = input(f"⚠️  数据库已存在：{db_path}\n是否重新初始化？(y/N): ")
        if response.lower() != 'y':
            print("❌ 取消初始化")
            exit(0)
        # 备份旧数据库
        backup_path = db_path.with_suffix('.db.bak')
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"💾 已备份旧数据库：{backup_path}")
    
    init_database(db_path)
