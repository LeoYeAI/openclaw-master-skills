#!/usr/bin/env python3
"""
Unified entry point for tg-reader.
Automatically selects between Pyrogram and Telethon implementations.
"""
import sys
import os


def main():
    """
    Main entry point that routes to either Pyrogram or Telethon implementation.
    
    Selection priority:
    1. --telethon flag in command line arguments
    2. TG_USE_TELETHON environment variable
    3. Default: Pyrogram
    """
    # Check for --telethon flag
    use_telethon = '--telethon' in sys.argv
    if use_telethon:
        sys.argv.remove('--telethon')
    
    # Check environment variable if flag not present
    if not use_telethon:
        use_telethon = os.getenv('TG_USE_TELETHON', 'false').lower() in ('true', '1', 'yes')
    
    # Route to appropriate implementation
    if use_telethon:
        try:
            from reader_telethon import main as telethon_main
            telethon_main()
        except ImportError as e:
            print(f"Error: Telethon implementation not available: {e}", file=sys.stderr)
            print("Install with: pip install telethon", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            from reader import main as pyrogram_main
            pyrogram_main()
        except ImportError as e:
            print(f"Error: Pyrogram implementation not available: {e}", file=sys.stderr)
            print("Install with: pip install pyrogram tgcrypto", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()