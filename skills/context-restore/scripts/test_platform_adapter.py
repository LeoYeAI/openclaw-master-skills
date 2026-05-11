#!/usr/bin/env python3
"""
Platform Format Auto-Adaptation Test Script
============================================

This script demonstrates the platform format auto-adaptation features
implemented in restore_context.py.

Features:
1. Platform detection from context
2. Platform-specific formatting
3. CLI --platform parameter
4. Auto-detection mode
"""

import sys
import os

# Add the scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from restore_context import (
    detect_platform_from_context,
    format_for_platform,
    format_for_telegram,
    format_for_discord,
    format_for_whatsapp,
    split_for_platform,
    split_for_telegram,
    PLATFORM_TELEGRAM,
    PLATFORM_DISCORD,
    PLATFORM_WHATSAPP,
    PLATFORM_SLACK,
    PLATFORM_UNKNOWN
)


def test_platform_detection():
    """Test platform detection from content"""
    print("=" * 60)
    print("TEST: Platform Detection")
    print("=" * 60)
    
    test_cases = [
        ("telegram context data", PLATFORM_TELEGRAM),
        ("Telegram notification received", PLATFORM_TELEGRAM),
        ("discord server message", PLATFORM_DISCORD),
        ("Discord webhook triggered", PLATFORM_DISCORD),
        ("whatsapp message from user", PLATFORM_WHATSAPP),
        ("Slack channel notification", PLATFORM_SLACK),
        ("random plain text", PLATFORM_UNKNOWN),
        ("", PLATFORM_UNKNOWN),
        (None, PLATFORM_UNKNOWN),
    ]
    
    for content, expected in test_cases:
        result = detect_platform_from_context(content)
        status = "✓" if result == expected else "✗"
        content_str = str(content) if content else "None"
        print(f"  {status} detect('{content_str[:30]}...' if len(content_str) > 30 else content_str) = {result}")
    
    print()


def test_platform_formatting():
    """Test platform-specific formatting"""
    print("=" * 60)
    print("TEST: Platform-Specific Formatting")
    print("=" * 60)
    
    # Test content with links (should be wrapped for Discord)
    test_content = """# Test Report

This is a [link to Google](https://google.com) and another link: https://github.com

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |

**Bold text** and *italic text*
"""
    
    print("  Original content:")
    print("-" * 40)
    print(test_content[:200] + "...")
    print("-" * 40)
    
    for platform, func in [
        ("telegram", format_for_telegram),
        ("discord", format_for_discord),
        ("whatsapp", format_for_whatsapp),
    ]:
        formatted = func(test_content)
        print(f"\n  {platform.upper()} formatted ({len(formatted)} chars):")
        print("-" * 40)
        print(formatted[:200] + "..." if len(formatted) > 200 else formatted)
    
    print()


def test_message_chunking():
    """Test message chunking for different platforms"""
    print("=" * 60)
    print("TEST: Message Chunking")
    print("=" * 60)
    
    # Create long content
    long_content = "\n".join([f"Line {i}: This is test content for chunking demonstration." 
                               for i in range(1, 51)])
    
    for platform, max_len in [
        ("telegram", 4000),
        ("discord", 2000),
    ]:
        chunks = split_for_platform(long_content, platform)
        print(f"  {platform.upper()}: {len(chunks)} chunk(s)")
        for i, chunk in enumerate(chunks, 1):
            print(f"    Chunk {i}: {len(chunk)} chars")
    
    print()


def test_cli_usage():
    """Test CLI usage examples"""
    print("=" * 60)
    print("TEST: CLI Usage Examples")
    print("=" * 60)
    
    examples = [
        'python3 restore_context.py --platform telegram',
        'python3 restore_context.py --platform discord',
        'python3 restore_context.py --auto-detect-platform',
        'python3 restore_context.py --platform whatsapp --level minimal',
        'python3 restore_context.py --platform discord --summary',
        'python3 restore_context.py --platform telegram --timeline --period weekly',
    ]
    
    for example in examples:
        print(f"  $ {example}")
    
    print()


def test_integration():
    """Test integration with actual context file"""
    print("=" * 60)
    print("TEST: Integration with Context File")
    print("=" * 60)
    
    context_file = "/home/athur/.openclaw/workspace/compressed_context/latest_compressed.json"
    
    if not os.path.exists(context_file):
        print(f"  Skipped: Context file not found at {context_file}")
        return
    
    from restore_context import load_compressed_context
    
    context = load_compressed_context(context_file)
    if context:
        content = context.get('content', str(context)) if isinstance(context, dict) else str(context)
        detected = detect_platform_from_context(content)
        print(f"  Detected platform from context: {detected}")
        
        # Test with different platforms
        for platform in [PLATFORM_TELEGRAM, PLATFORM_DISCORD]:
            formatted = format_for_platform(content[:500], platform)
            chunks = split_for_platform(content[:2000], platform)
            print(f"  {platform}: {len(chunks)} chunk(s), {len(formatted)} chars formatted")
    
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" Platform Format Auto-Adaptation Test Suite")
    print("=" * 60 + "\n")
    
    test_platform_detection()
    test_platform_formatting()
    test_message_chunking()
    test_cli_usage()
    test_integration()
    
    print("=" * 60)
    print(" All tests completed!")
    print("=" * 60)
