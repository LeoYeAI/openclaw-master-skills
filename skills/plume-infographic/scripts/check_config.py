#!/usr/bin/env python3
"""
Check if PLUME_API_KEY is configured
Output: CONFIGURED / NOT_CONFIGURED
"""

import os
import sys


def main():
    key = os.environ.get("PLUME_API_KEY")

    if key:
        print("CONFIGURED")
        sys.exit(0)
    else:
        print("NOT_CONFIGURED")
        print(
            "Please configure PLUME_API_KEY using one of the following methods:\n"
            '  1. Edit ~/.openclaw/openclaw.json, add under skills.entries:\n'
            '     "plume-infographic": { "env": { "PLUME_API_KEY": "your-key" } }\n'
            "  2. echo 'PLUME_API_KEY=your-key' >> ~/.openclaw/.env",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
