#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Continue batch search for remaining keywords
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import subprocess
import os
import time

# Remaining keywords to search
keywords = ["围巾", "T恤", "裤子", "鞋子", "包包", "腰带"]

def safe_print(text):
    try:
        print(text)
    except:
        print(str(text).encode('utf-8', errors='replace').decode('utf-8', errors='replace'))

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_script = os.path.join(script_dir, "search_box_v2.py")
    results_dir = os.path.join(script_dir, "results")
    
    safe_print("="*60)
    safe_print("Continue 1688 Batch Search - Remaining Keywords")
    safe_print("="*60)
    
    for i, keyword in enumerate(keywords, 1):
        safe_print(f"\n[{i}/{len(keywords)}] Searching: {keyword}")
        safe_print("-"*40)
        
        output_file = os.path.join(results_dir, f"{keyword}.json")
        
        try:
            result = subprocess.run(
                [sys.executable, search_script, "--keyword", keyword, "--num", "5", "--output", output_file],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=120
            )
            
            # Print output
            if result.stdout:
                safe_print(result.stdout)
            if result.stderr:
                safe_print(f"Errors: {result.stderr}")
            
            if result.returncode == 0:
                safe_print(f"✓ Saved: {output_file}")
            else:
                safe_print(f"✗ Failed with code {result.returncode}")
                
        except subprocess.TimeoutExpired:
            safe_print(f"✗ Timeout after 120s")
        except Exception as e:
            safe_print(f"✗ Error: {e}")
        
        # Wait between searches to avoid triggering anti-bot
        if i < len(keywords):
            safe_print(f"\nWaiting 3 seconds before next search...")
            time.sleep(3)
    
    safe_print("\n" + "="*60)
    safe_print("Batch search completed!")
    safe_print("="*60)

if __name__ == "__main__":
    main()
