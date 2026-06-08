#!/usr/bin/env python3
"""
Personal Health Manager - Comprehensive Health Tracking
Features: Profile, Medications, Records, Reminders, Analytics
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path.home() / ".health_data"

def init_storage():
    """Initialize storage directory and default files"""
    DATA_DIR.mkdir(exist_ok=True)
    
    files = {
        "profile.json": {},
        "medications.json": [],
        "reminders.json": [],
        "records.json": [],
        "goals.json": {
            "daily_steps": 10000,
            "daily_water": 8,
            "daily_sleep": 8,
            "weekly_exercise": 150
        }
    }
    
    for filename, default in files.items():
        path = DATA_DIR / filename
        if not path.exists():
            with open(path, 'w') as f:
                json.dump(default, f, indent=2)

# ==================== PROFILE ====================

def save_profile(profile: dict) -> dict:
    """Save user health profile"""
    # Calculate BMI if height/weight provided
    if profile.get("weight") and profile.get("height"):
        height_m = profile["height"] / 100
        profile["bmi"] = round(profile["weight"] / (height_m ** 2), 1)
    
    profile["updated_at"] = datetime.now().isoformat()
    
    with open(DATA_DIR / "profile.json", 'w') as f:
        json.dump(profile, f, indent=2)
    return profile

def get_profile() -> dict:
    """Get user health profile"""
    with open(DATA_DIR / "profile.json", 'r') as f:
        return json.load(f)

# ==================== MEDICATIONS ====================

def add_medication(med: dict) -> dict:
    """Add a medication"""
    meds = json.load(open(DATA_DIR / "medications.json"))
    med["id"] = len(meds) + 1
    med["created_at"] = datetime.now().isoformat()
    meds.append(med)
    json.dump(meds, open(DATA_DIR / "medications.json", 'w'), indent=2)
    return med

def get_medications() -> List[dict]:
    """Get all medications"""
    return json.load(open(DATA_DIR / "medications.json"))

def update_medication(med_id: int, updates: dict) -> dict:
    """Update a medication"""
    meds = json.load(open(DATA_DIR / "medications.json"))
    for med in meds:
        if med["id"] == med_id:
            med.update(updates)
            med["updated_at"] = datetime.now().isoformat()
            break
    json.dump(meds, open(DATA_DIR / "medications.json", 'w'), indent=2)
    return med

def delete_medication(med_id: int) -> bool:
    """Delete a medication"""
    meds = json.load(open(DATA_DIR / "medications.json"))
    meds = [m for m in meds if m["id"] != med_id]
    json.dump(meds, open(DATA_DIR / "medications.json", 'w'), indent=2)
    return True

# ==================== RECORDS ====================

def add_record(record_type: str, data: dict) -> dict:
    """Add a health record"""
    records = json.load(open(DATA_DIR / "records.json"))
    
    record = {
        "id": len(records) + 1,
        "type": record_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    records.append(record)
    json.dump(records, open(DATA_DIR / "records.json", 'w'), indent=2)
    return record

def get_records(record_type: str = None, days: int = 30) -> List[dict]:
    """Get health records, optionally filtered by type"""
    records = json.load(open(DATA_DIR / "records.json"))
    
    # Filter by type
    if record_type:
        records = [r for r in records if r.get("type") == record_type]
    
    # Filter by date
    cutoff = datetime.now().timestamp() - (days * 86400)
    records = [r for r in records if datetime.fromisoformat(r["timestamp"]).timestamp() > cutoff]
    
    return records

def get_latest_record(record_type: str) -> Optional[dict]:
    """Get most recent record of a type"""
    records = get_records(record_type, days=365)
    return records[-1] if records else None

# ==================== REMINDERS ====================

def add_reminder(reminder: dict) -> dict:
    """Add a reminder"""
    reminders = json.load(open(DATA_DIR / "reminders.json"))
    reminder["id"] = len(reminders) + 1
    reminder["created_at"] = datetime.now().isoformat()
    reminders.append(reminder)
    json.dump(reminders, open(DATA_DIR / "reminders.json", 'w'), indent=2)
    return reminder

def get_reminders() -> List[dict]:
    """Get all reminders"""
    return json.load(open(DATA_DIR / "reminders.json"))

def delete_reminder(reminder_id: int) -> bool:
    """Delete a reminder"""
    reminders = json.load(open(DATA_DIR / "reminders.json"))
    reminders = [r for r in reminders if r["id"] != reminder_id]
    json.dump(reminders, open(DATA_DIR / "reminders.json", 'w'), indent=2)
    return True

# ==================== ANALYTICS ====================

def get_weekly_summary() -> dict:
    """Generate weekly health summary"""
    records = get_records(days=7)
    
    summary = {
        "date_range": f"Last 7 days",
        "record_counts": {},
        "averages": {}
    }
    
    # Count by type
    for record in records:
        rtype = record["type"]
        summary["record_counts"][rtype] = summary["record_counts"].get(rtype, 0) + 1
    
    # Calculate averages
    bp_readings = [r["data"] for r in records if r["type"] == "blood_pressure"]
    if bp_readings:
        summary["averages"]["blood_pressure"] = {
            "systolic": sum(d.get("systolic", 0) for d in bp_readings) / len(bp_readings),
            "diastolic": sum(d.get("diastolic", 0) for d in bp_readings) / len(bp_readings)
        }
    
    glucose_readings = [r["data"] for r in records if r["type"] == "blood_glucose"]
    if glucose_readings:
        summary["averages"]["blood_glucose"] = sum(d.get("value", 0) for d in glucose_readings) / len(glucose_readings)
    
    weight_readings = [r["data"] for r in records if r["type"] == "weight"]
    if weight_readings:
        summary["averages"]["weight"] = sum(d.get("value", 0) for d in weight_readings) / len(weight_readings)
    
    return summary

# ==================== CHECKS ====================

def check_blood_pressure(systolic: int, diastolic: int) -> dict:
    """Check blood pressure category"""
    if systolic < 120 and diastolic < 80:
        return {"status": "normal", "advice": "Great! Maintain healthy lifestyle."}
    elif systolic < 130 and diastolic < 80:
        return {"status": "elevated", "advice": "Exercise regularly, reduce sodium."}
    elif systolic < 140 or diastolic < 90:
        return {"status": "stage1", "advice": "Consult doctor, lifestyle changes needed."}
    elif systolic >= 180 or diastolic >= 120:
        return {"status": "crisis", "advice": "SEEK EMERGENCY CARE IMMEDIATELY!"}
    else:
        return {"status": "stage2", "advice": "Consult doctor for treatment options."}

def check_blood_glucose(fasting: int) -> dict:
    """Check blood glucose category"""
    if fasting < 100:
        return {"status": "normal", "advice": "Good! Keep it up."}
    elif fasting < 126:
        return {"status": "prediabetes", "advice": "Lifestyle changes, consult doctor."}
    else:
        return {"status": "diabetes", "advice": "Consult doctor for diagnosis and management."}

def check_bmi(bmi: float) -> dict:
    """Check BMI category"""
    if bmi < 18.5:
        return {"category": "underweight", "advice": "Gain weight healthily with balanced diet."}
    elif bmi < 25:
        return {"category": "normal", "advice": "Maintain current weight."}
    elif bmi < 30:
        return {"category": "overweight", "advice": "Lose weight through diet and exercise."}
    else:
        return {"category": "obese", "advice": "Consult doctor for weight management."}

# ==================== CLI ====================

if __name__ == "__main__":
    import sys
    
    init_storage()
    print(f"Health data storage ready: {DATA_DIR}")
    print("\nCommands:")
    print("  python health_manager.py profile <json>  - Set profile")
    print("  python health_manager.py med add <json>  - Add medication")
    print("  python health_manager.py record <type> <json>  - Add record")
    print("  python health_manager.py summary         - Weekly summary")
