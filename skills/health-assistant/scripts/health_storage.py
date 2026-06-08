#!/usr/bin/env python3
"""
Personal Health Manager - Data Storage Module
Handles local storage of health records in JSON format
"""

import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path.home() / ".health_data"

def init_storage():
    """Initialize storage directory"""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Create default files
    for file in ["medications.json", "reminders.json", "records.json", "profile.json"]:
        path = DATA_DIR / file
        if not path.exists():
            with open(path, 'w') as f:
                if "records" in file:
                    json.dump([], f)
                else:
                    json.dump({}, f)

def save_health_record(record_type: str, data: dict):
    """Save a health record"""
    records_file = DATA_DIR / "records.json"
    with open(records_file, 'r') as f:
        records = json.load(f)
    
    record = {
        "id": len(records) + 1,
        "type": record_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    records.append(record)
    
    with open(records_file, 'w') as f:
        json.dump(records, f, indent=2)
    
    return record

def get_records(record_type: str = None, limit: int = 10):
    """Get health records"""
    records_file = DATA_DIR / "records.json"
    with open(records_file, 'r') as f:
        records = json.load(f)
    
    if record_type:
        records = [r for r in records if r.get("type") == record_type]
    
    return records[-limit:]

def add_medication(medication: dict):
    """Add a medication"""
    meds_file = DATA_DIR / "medications.json"
    with open(meds_file, 'r') as f:
        meds = json.load(f)
    
    med_id = len(meds) + 1
    medication["id"] = med_id
    meds.append(medication)
    
    with open(meds_file, 'w') as f:
        json.dump(meds, f, indent=2)
    
    return medication

def get_medications():
    """Get all medications"""
    meds_file = DATA_DIR / "medications.json"
    with open(meds_file, 'r') as f:
        return json.load(f)

def add_reminder(reminder: dict):
    """Add a reminder"""
    reminders_file = DATA_DIR / "reminders.json"
    with open(reminders_file, 'r') as f:
        reminders = json.load(f)
    
    reminder_id = len(reminders) + 1
    reminder["id"] = reminder_id
    reminders.append(reminder)
    
    with open(reminders_file, 'w') as f:
        json.dump(reminders, f, indent=2)
    
    return reminder

def get_reminders():
    """Get all reminders"""
    reminders_file = DATA_DIR / "reminders.json"
    with open(reminders_file, 'r') as f:
        return json.load(f)

def save_profile(profile: dict):
    """Save user health profile"""
    profile_file = DATA_DIR / "profile.json"
    with open(profile_file, 'w') as f:
        json.dump(profile, f, indent=2)

def get_profile():
    """Get user health profile"""
    profile_file = DATA_DIR / "profile.json"
    with open(profile_file, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    init_storage()
    print(f"Health data storage initialized at: {DATA_DIR}")
