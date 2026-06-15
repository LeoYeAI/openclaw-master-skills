#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HealthFit Database Initialization Script
Create SQLite database and all necessary table structures
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "db" / "healthfit.db"


def init_database():
    """Initialize database"""
    
    # Ensure directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if database already exists
    if DB_PATH.exists():
        print(f"⚠️  Database already exists: {DB_PATH}")
        response = input("Reinitialize? This will backup old database. (y/N): ")
        if response.lower() != 'y':
            print("❌ Initialization cancelled")
            return
        
        # Backup old database
        backup_path = DB_PATH.with_suffix('.db.bak')
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"💾 Old database backed up to: {backup_path}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript('''
        -- Workout records table
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
        );
        
        -- Diet records table
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
        );
        
        -- Daily body metrics table
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
        );
        
        -- Personal records table
        CREATE TABLE IF NOT EXISTS pr_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT NOT NULL,
            pr_type TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            achieved_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Weekly statistics cache table
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
        );
        
        -- Monthly statistics cache table
        CREATE TABLE IF NOT EXISTS monthly_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL UNIQUE,
            period_start TEXT,
            period_end TEXT,
            total_workouts INTEGER,
            total_duration_min INTEGER,
            avg_weight_kg REAL,
            weight_change_kg REAL,
            pr_count INTEGER,
            workout_adherence_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Index optimization
        CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date);
        CREATE INDEX IF NOT EXISTS idx_nutrition_date ON nutrition_entries(date);
        CREATE INDEX IF NOT EXISTS idx_metrics_date ON metrics_daily(date);
        CREATE INDEX IF NOT EXISTS idx_pr_exercise ON pr_records(exercise_name);
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialization complete: {DB_PATH}")
    print("📊 Tables created:")
    print("   - workouts (workout records)")
    print("   - nutrition_entries (diet records)")
    print("   - metrics_daily (daily body metrics)")
    print("   - pr_records (personal records)")
    print("   - weekly_summaries (weekly statistics cache)")
    print("   - monthly_summaries (monthly statistics cache)")


if __name__ == "__main__":
    init_database()
