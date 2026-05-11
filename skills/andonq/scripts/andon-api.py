#!/usr/bin/env python3
"""
CLI wrapper for andon_api module.

Python cannot import hyphenated filenames directly, so this thin wrapper
delegates to the importable `andon_api` module in the same directory.

Usage:
    python3 scripts/andon-api.py -a CreateMCTicket -d '{"Content":"..."}'
    python3 scripts/andon-api.py -a CreateMCTicket -d '{"Content":"..."}' -n   # dry-run
    python3 scripts/andon-api.py -a CreateMCTicket -d '{"Content":"..."}' -v   # verbose
"""

import os
import sys

# Ensure the scripts package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.andon_api import main

if __name__ == "__main__":
    main()
