#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch search 10 keywords on 1688
"""

import sys
import io
import subprocess
import os

# Force UTF-8
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 10 keywords to search
keywords = [
    "帽子",
    "外套", 
    "袜子",
    "手套",
    "围巾",
    "T恤",
    "裤子",
    "鞋子",
    "包包",
    "腰带"
]

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
    safe_print("1688 Batch Search - 10 Keywords")
    safe_print("="*60)
    
    for i, keyword in enumerate(keywords, 1):
        safe_print(f"\n[{i}/10] Searching: {keyword}")
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
    
    safe_print("\n" + "="*60)
    safe_print("Batch search completed!")
    safe_print("="*60)
    
    # List all result files
    safe_print("\nResult files:")
    for f in os.listdir(results_dir):
        if f.endswith('.json'):
            safe_print(f"  - {f}")

if __name__ == "__main__":
    main()
