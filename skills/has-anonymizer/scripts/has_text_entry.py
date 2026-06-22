#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///
"""Launcher for HaS Text CLI with uv-managed dependencies."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the local has_text package under scripts/ is importable.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from has_text.has_text import main


if __name__ == "__main__":
    main()
