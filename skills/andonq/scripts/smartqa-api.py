#!/usr/bin/env python3
"""
CLI wrapper for smartqa_api module.

Usage:
    python3 scripts/smartqa-api.py -q "轻量应用服务器如何登录"
    python3 scripts/smartqa-api.py -q "测试" -n   # dry-run
    python3 scripts/smartqa-api.py -q "CVM价格" -v  # verbose
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.smartqa_api import main

if __name__ == "__main__":
    main()
