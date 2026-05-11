#!/usr/bin/env python3
"""Eval runner for Returns & Reverse Logistics capability."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "shared"))

from eval_framework import main

if __name__ == "__main__":
    if "--capability" not in sys.argv:
        capability_dir = Path(__file__).resolve().parent.parent
        sys.argv.extend(["--capability", str(capability_dir)])

    main()
