#!/usr/bin/env python3
"""
PPT Compressor - Simple Entry Point

This is a simplified wrapper that handles path issues automatically.
It can be copied to any directory and executed directly.

Usage:
    python compress.py "path/to/your.pptx"
    python compress.py "path/to/your.pptx" --crf 32 --image-quality 70
"""

import sys
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the scripts directory to Python path
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Import and run the main compression module
from compress_ppt_videos import main

if __name__ == '__main__':
    main()
