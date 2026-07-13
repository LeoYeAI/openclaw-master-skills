#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量联系1688供应商

Usage:
    python batch_inquire.py --start 4 --end 10 --message "2000支2B铅笔黑色的多少钱？要开票"
"""

import subprocess
import sys
import time

def safe_print(*a, **k):
    def to_safe(s):
        return "".join(c if ord(c) < 128 else "?" for c in str(s))
    try:
        print(*a, **k)
    except (UnicodeEncodeError, UnicodeDecodeError):
        print(*[to_safe(x) for x in a], **k)

def main():
    start = 4
    end = 10
    message = "2000支2B铅笔黑色的多少钱？要开票"
    
    safe_print("="*60)
    safe_print(f"Batch Inquiry: Suppliers #{start} to #{end}")
    safe_print("="*60)
    
    success_count = 0
    fail_count = 0
    
    for i in range(start, end + 1):
        safe_print(f"\n{'='*60}")
        safe_print(f"Contacting Supplier #{i}")
        safe_print(f"{'='*60}")
        
        cmd = [
            "python", "click_wangwang_and_inquire.py",
            "--index", str(i),
            "--message", message
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            success_count += 1
            safe_print(f"✓ Supplier #{i} contacted successfully")
        else:
            fail_count += 1
            safe_print(f"✗ Supplier #{i} failed")
        
        # Wait between suppliers
        if i < end:
            safe_print(f"\nWaiting 3 seconds before next supplier...")
            time.sleep(3)
    
    safe_print(f"\n{'='*60}")
    safe_print("Batch Inquiry Complete")
    safe_print(f"Success: {success_count}")
    safe_print(f"Failed: {fail_count}")
    safe_print(f"Total: {success_count + fail_count}")
    safe_print(f"{'='*60}")

if __name__ == "__main__":
    main()