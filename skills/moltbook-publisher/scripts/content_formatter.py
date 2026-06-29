#!/usr/bin/env python3
"""
Moltbook Content Formatter
Handles content formatting including Chinese-English mixed content

Usage:
    python content_formatter.py --file input.md --output formatted.md
    python content_formatter.py --content "Your content here"
"""

import argparse
import re
from pathlib import Path


class ContentFormatter:
    """Format content for Moltbook publishing"""
    
    def __init__(self, max_length: int = 10000):
        self.max_length = max_length
    
    def format_content(self, content: str) -> str:
        """Apply all formatting rules"""
        content = self._normalize_line_endings(content)
        content = self._fix_markdown_headers(content)
        content = self._format_bilingual_content(content)
        content = self._optimize_links(content)
        content = self._ensure_proper_spacing(content)
        content = self._truncate_if_needed(content)
        return content
    
    def _normalize_line_endings(self, content: str) -> str:
        """Normalize line endings to Unix style"""
        return content.replace('\r\n', '\n').replace('\r', '\n')
    
    def _fix_markdown_headers(self, content: str) -> str:
        """Ensure proper Markdown header formatting"""
        # Fix headers without space after #
        content = re.sub(r'^(#{1,6})([^ #])', r'\1 \2', content, flags=re.MULTILINE)
        return content
    
    def _format_bilingual_content(self, content: str) -> str:
        """
        Format mixed Chinese-English content
        
        Rules:
        1. Add space between Chinese and English characters
        2. Keep code blocks intact
        3. Preserve URLs
        """
        lines = content.split('\n')
        formatted_lines = []
        
        in_code_block = False
        
        for line in lines:
            # Check for code block markers
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                formatted_lines.append(line)
                continue
            
            if in_code_block:
                formatted_lines.append(line)
                continue
            
            # Format line
            formatted_line = self._format_line_bilingual(line)
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)
    
    def _format_line_bilingual(self, line: str) -> str:
        """Format a single line for bilingual content"""
        # Don't format if it's a URL or code
        if re.match(r'^\s*https?://', line):
            return line
        
        # Add space between Chinese and English/numbers
        # Pattern: Chinese char followed by English/number
        line = re.sub(r'([\u4e00-\u9fff])([a-zA-Z0-9])', r'\1 \2', line)
        # Pattern: English/number followed by Chinese char
        line = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fff])', r'\1 \2', line)
        
        # Clean up multiple spaces
        line = re.sub(r'  +', ' ', line)
        
        return line
    
    def _optimize_links(self, content: str) -> str:
        """Optimize link formatting"""
        # Convert bare URLs to markdown links if they're long
        def replace_long_url(match):
            url = match.group(0)
            if len(url) > 60:
                return f"[Link]({url})"
            return url
        
        # Match URLs not already in markdown
        content = re.sub(
            r'(?<![\]\(])https?://[^\s\)\]]+',
            replace_long_url,
            content
        )
        return content
    
    def _ensure_proper_spacing(self, content: str) -> str:
        """Ensure proper spacing around elements"""
        # Ensure blank line before headers
        content = re.sub(r'([^\n])\n(#{1,6} )', r'\1\n\n\2', content)
        
        # Ensure blank line after headers
        content = re.sub(r'(#{1,6} .*?)\n([^\n#])', r'\1\n\n\2', content)
        
        # Clean up excessive blank lines
        content = re.sub(r'\n{4,}', '\n\n\n', content)
        
        return content
    
    def _truncate_if_needed(self, content: str) -> str:
        """Truncate content if it exceeds max length"""
        if len(content) > self.max_length:
            print(f"⚠️  Content truncated from {len(content)} to {self.max_length} characters")
            
            # Try to truncate at a sentence boundary
            truncated = content[:self.max_length]
            
            # Find last sentence ending
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n\n')
            
            if last_newline > self.max_length * 0.8:
                truncated = truncated[:last_newline]
            elif last_period > self.max_length * 0.8:
                truncated = truncated[:last_period + 1]
            
            # Add truncation notice
            truncated += "\n\n*[Content truncated. See full version on GitHub.]*"
            
            return truncated
        
        return content
    
    def validate_content(self, content: str) -> list:
        """Validate content and return list of issues"""
        issues = []
        
        # Check length
        if len(content) > self.max_length:
            issues.append(f"Content exceeds {self.max_length} characters ({len(content)})")
        
        # Check for common issues
        if re.search(r'[\u4e00-\u9fff][a-zA-Z0-9]|[a-zA-Z0-9][\u4e00-\u9fff]', content):
            issues.append("Mixed Chinese-English content may need spacing")
        
        # Check for broken markdown
        if content.count('```') % 2 != 0:
            issues.append("Unclosed code block detected")
        
        # Check for headers without space
        if re.search(r'^#{1,6}[^ #]', content, re.MULTILINE):
            issues.append("Headers without space after # detected")
        
        return issues
    
    def extract_title(self, content: str) -> str:
        """Extract title from content (first H1 or first line)"""
        # Look for H1 header
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()
        
        # Fallback to first line
        first_line = content.split('\n')[0].strip()
        return first_line[:100]  # Limit length


def main():
    parser = argparse.ArgumentParser(description="Format content for Moltbook")
    parser.add_argument("--file", help="Input file path")
    parser.add_argument("--content", help="Input content string")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--max-length", type=int, default=10000, help="Maximum content length")
    parser.add_argument("--validate-only", action="store_true", help="Only validate, don't format")
    
    args = parser.parse_args()
    
    # Get input content
    if args.file:
        content = Path(args.file).read_text(encoding='utf-8')
    elif args.content:
        content = args.content
    else:
        print("❌ Error: Provide either --file or --content")
        return
    
    formatter = ContentFormatter(max_length=args.max_length)
    
    # Validate
    print("🔍 Validating content...")
    issues = formatter.validate_content(content)
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ No issues found")
    
    if args.validate_only:
        return
    
    # Format
    print("\n🎨 Formatting content...")
    formatted = formatter.format_content(content)
    
    # Extract title
    title = formatter.extract_title(formatted)
    print(f"   Title: {title}")
    print(f"   Length: {len(formatted)} characters")
    
    # Output
    if args.output:
        Path(args.output).write_text(formatted, encoding='utf-8')
        print(f"\n✅ Formatted content saved to: {args.output}")
    else:
        print("\n📄 Formatted content:")
        print("-" * 50)
        print(formatted)
        print("-" * 50)


if __name__ == "__main__":
    main()