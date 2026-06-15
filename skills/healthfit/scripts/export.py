#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HealthFit Data Export Script
Support export to JSON, CSV, Markdown formats
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
    """Export all JSON files"""
    json_dir = DATA_DIR / "json"
    
    if not json_dir.exists():
        print("⚠️  JSON directory doesn't exist, skipping")
        return
    
    exported_count = 0
    skipped_count = 0
    
    for json_file in json_dir.glob("*.json"):
        # Skip sensitive files (unless explicitly requested)
        if json_file.name == "private_sexual_health.json" and not include_private:
            print(f"⏭️  Skipping sensitive file: {json_file.name}")
            skipped_count += 1
            continue
        
        # Copy file
        dest = output_dir / json_file.name
        shutil.copy2(json_file, dest)
        print(f"✅ Exported: {json_file.name}")
        exported_count += 1
    
    print(f"\n📊 JSON files export complete: {exported_count} files, skipped {skipped_count} sensitive files")


def export_database_to_csv(output_dir: Path):
    """Export database tables to CSV"""
    if not DB_PATH.exists():
        print("⚠️  Database doesn't exist, skipping")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    exported_count = 0
    
    for (table_name,) in tables:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Write CSV
        csv_path = output_dir / f"{table_name}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)
        
        print(f"✅ Exported table: {table_name}.csv ({len(rows)} records)")
        exported_count += 1
    
    conn.close()
    print(f"\n📊 Database export complete: {exported_count} tables")


def generate_markdown_report(output_dir: Path):
    """Generate readable Markdown report"""
    report_lines = [
        "# HealthFit Data Export Report",
        f"\nExport time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "---\n"
    ]
    
    # Read user profile
    profile_path = DATA_DIR / "json" / "profile.json"
    if profile_path.exists():
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
        report_lines.append("## User Profile\n")
        report_lines.append(f"- Nickname: {profile.get('nickname', 'Not set')}")
        report_lines.append(f"- Height: {profile.get('height_cm', 'Not set')} cm")
        report_lines.append(f"- Weight: {profile.get('weight_kg', 'Not set')} kg")
        report_lines.append(f"- Primary Goal: {profile.get('primary_goal', 'Not set')}")
        report_lines.append(f"- Created: {profile.get('created_at', 'Unknown')}")
        report_lines.append(f"- Last Updated: {profile.get('updated_at', 'Unknown')}\n")
    
    # Count database records
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        report_lines.append("## Data Statistics\n")
        
        cursor.execute("SELECT COUNT(*) FROM workouts")
        report_lines.append(f"- Workout records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM nutrition_entries")
        report_lines.append(f"- Diet records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM metrics_daily")
        report_lines.append(f"- Daily metrics: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM pr_records")
        report_lines.append(f"- PR records: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM weekly_summaries")
        report_lines.append(f"- Weekly summaries: {cursor.fetchone()[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM monthly_summaries")
        report_lines.append(f"- Monthly summaries: {cursor.fetchone()[0]}\n")
        
        conn.close()
    
    # Write report
    report_path = output_dir / "export_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"✅ Generated report: export_report.md")


def main():
    parser = argparse.ArgumentParser(description="HealthFit Data Export")
    parser.add_argument("--output", "-o", default="./healthfit_export", help="Export directory")
    parser.add_argument("--include-private", action="store_true", help="Include sensitive data (requires secondary confirmation)")
    parser.add_argument("--format", choices=["all", "json", "csv", "markdown"], default="all",
                       help="Export format")
    
    args = parser.parse_args()
    
    # Secondary confirmation for sensitive data
    if args.include_private:
        print("\n" + "="*60)
        print("⚠️  WARNING: Highly Sensitive Data Export Confirmation  ⚠️")
        print("="*60)
        print("""
You have requested to export sensitive private data, including:
  - Sexual health records (private_sexual_health.json)
  - All personal health privacy information

This operation risks:
  ❌ Backup files may be accessed by others
  ❌ Cloud sync may automatically upload
  ❌ Data breach may cause privacy damage

Please confirm you understand these risks.
""")
        print("="*60)
        
        # Random verification code confirmation
        import random
        import string
        verify_code = ''.join(random.choices(string.ascii_uppercase, k=6))
        print(f"\nPlease enter the following verification code to confirm: {verify_code}")
        
        user_input = input("Verification code: ").strip().upper()
        if user_input != verify_code:
            print("❌ Verification code incorrect, operation cancelled")
            return
        
        # Record operation log
        log_path = DATA_DIR / "security_log.txt"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Sensitive data export operation confirmed\n")
        
        print("✅ Verification passed, continuing export...\n")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_dir = output_dir / f"export_{timestamp}"
    export_dir.mkdir()
    
    print(f"📁 Export directory: {export_dir}\n")
    
    # Execute export
    if args.format in ["all", "json"]:
        print("📄 Exporting JSON files...")
        export_json_files(export_dir, args.include_private)
        print()
    
    if args.format in ["all", "csv"]:
        print("📊 Exporting database to CSV...")
        export_database_to_csv(export_dir)
        print()
    
    if args.format in ["all", "markdown"]:
        print("📝 Generating Markdown report...")
        generate_markdown_report(export_dir)
        print()
    
    print(f"\n✅ Export complete! Directory: {export_dir}")
    print(f"💡 Tip: You can manually compress for backup, or upload to cloud storage")


if __name__ == "__main__":
    main()
