#!/usr/bin/env python3
"""
AI Diary PDF Export - v1.0.0 "Velvet Edition"

Generate a BEAUTIFUL, professionally-designed PDF from diary markdown files
using WeasyPrint (HTML → PDF).

Design: Editorial Magazine aesthetic with warm, intimate typography
Fonts: TeX Gyre Bonum (display) + Lato (body)
Colors: Forest Green, Antique Cream, Gold accents
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from html import escape

try:
    from weasyprint import HTML
except Exception as e:
    raise SystemExit(
        "WeasyPrint is required. Install with: pip3 install weasyprint\n"
        f"Import error: {e}"
    )

try:
    import markdown
    from markdown.extensions import Extension
    from markdown.treeprocessors import Treeprocessor
except Exception as e:
    raise SystemExit(
        "Python-Markdown is required. Install with: pip3 install markdown\n"
        f"Import error: {e}"
    )

# Configuration
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_FILE = SKILL_DIR / "config.json"
DEFAULT_DIARY_PATH = "memory/diary/"
DEFAULT_OUTPUT_NAME = "Cami-Diary.pdf"


def load_config():
    """Load configuration from config.json"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {"diary_path": DEFAULT_DIARY_PATH}


def get_workspace_root():
    """Find the workspace root"""
    import os
    
    # Check environment variable first
    env_workspace = os.getenv("OPENCLAW_WORKSPACE") or os.getenv("AGENT_WORKSPACE")
    if env_workspace:
        env_path = Path(env_workspace)
        if (env_path / "memory").exists():
            return env_path
    
    # Try common locations
    candidates = [
        Path.cwd(),
        Path.home() / "clawd",
        Path.home() / ".openclaw" / "workspace",
    ]
    for path in candidates:
        if (path / "memory").exists():
            return path
    return Path.cwd()


def get_diary_path(config):
    """Get full path to diary directory"""
    workspace = get_workspace_root()
    diary_path = workspace / config.get("diary_path", DEFAULT_DIARY_PATH)
    diary_path.mkdir(parents=True, exist_ok=True)
    return diary_path


def load_entries(diary_path: Path, month: str = None):
    """Load and return sorted diary entries, optionally filtered by month (YYYY-MM)"""
    md_files = sorted(diary_path.glob("*.md"))
    dated = [f for f in md_files if re.match(r"\d{4}-\d{2}-\d{2}$", f.stem)]
    if month:
        dated = [f for f in dated if f.stem.startswith(month + "-")]
    return dated


def parse_entry_title(content: str, date_str: str):
    """Extract title from markdown content"""
    # Try: # 📔 Cami's Diary - Saturday, January 31st, 2026
    match = re.search(r"^#\s*📔?\s*Cami'?s?\s*Diary\s*[-—–]\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        # Don't use if it's just the date repeated
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", title):
            return title
    
    # Try: # YYYY-MM-DD — Title (with actual title after)
    match = re.search(r"^#\s+\d{4}-\d{2}-\d{2}\s*[—–-]\s*([^#\n]+)$", content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # Don't use if it's empty or just punctuation
        if title and not re.match(r"^[\s—–-]*$", title):
            return title
    
    # Try: ## Summary section as fallback
    match = re.search(r"##\s*Summary\s*\n+(.+?)(?:\n\n|\n##|\Z)", content, re.IGNORECASE | re.DOTALL)
    if match:
        summary = match.group(1).strip()
        # Get first sentence, truncate if needed
        first_sentence = re.split(r'[.!?]', summary)[0].strip()
        if len(first_sentence) > 60:
            first_sentence = first_sentence[:57] + "..."
        if first_sentence:
            return first_sentence
    
    # Fallback to nicely formatted date
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A's Reflections")
    except:
        return "Journal Entry"


def format_date_display(date_str: str) -> tuple[str, str, str]:
    """Convert YYYY-MM-DD to beautiful date parts: (weekday, month day, year)"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday = dt.strftime("%A")
        month_day = dt.strftime("%B %d")
        year = dt.strftime("%Y")
        return weekday, month_day, year
    except:
        return "", date_str, ""


def extract_quote_of_day(content: str) -> str | None:
    """Extract quote of the day if present"""
    # Look for ## Quote of the Day or similar
    match = re.search(r"##\s*Quote.*?\n+>\s*(.+?)(?:\n\n|\Z)", content, re.IGNORECASE | re.DOTALL)
    if match:
        quote = match.group(1).strip()
        # Clean up multiline quotes
        quote = re.sub(r"\n>\s*", " ", quote)
        return quote
    return None


def extract_highlight(content: str) -> str | None:
    """Extract today's highlight if present"""
    match = re.search(r"##\s*🌟\s*Today'?s?\s*Highlight\s*\n+(.+?)(?=\n##|\Z)", content, re.IGNORECASE | re.DOTALL)
    if match:
        text = match.group(1).strip()
        # Get first paragraph only
        first_para = text.split("\n\n")[0]
        # Remove markdown formatting
        first_para = re.sub(r"\*\*(.+?)\*\*", r"\1", first_para)
        if len(first_para) > 200:
            first_para = first_para[:197] + "..."
        return first_para
    return None


def get_css():
    """Return the beautiful CSS stylesheet"""
    return """
    /* ===========================================
       VELVET EDITION - Editorial Magazine Style
       =========================================== */
    
    :root {
        /* Primary palette - Warm & Intimate */
        --forest-deep: #1a2f2a;
        --forest-mid: #2d4a42;
        --forest-light: #3d5e54;
        
        --cream: #faf6f0;
        --cream-warm: #f5efe5;
        --cream-dark: #e8dfd0;
        
        --gold: #c9a227;
        --gold-light: #d4b84a;
        --gold-muted: #a08520;
        
        --terracotta: #b85c38;
        --terracotta-light: #d4755a;
        
        --ink: #2c2c2c;
        --ink-light: #555555;
        --ink-faded: #888888;
    }
    
    /* Page Setup */
    @page {
        size: A4;
        margin: 30mm 25mm 35mm 30mm;
        
        @bottom-center {
            content: counter(page);
            font-family: "Lato", sans-serif;
            font-size: 9pt;
            color: var(--ink-faded);
            letter-spacing: 2px;
        }
    }
    
    @page :first {
        @bottom-center { content: none; }
    }
    
    @page cover {
        margin: 0;
        @bottom-center { content: none; }
    }
    
    @page toc {
        @bottom-center { content: none; }
    }
    
    /* Base Typography */
    html, body {
        font-family: "Lato", "DejaVu Sans", sans-serif;
        font-size: 10.5pt;
        line-height: 1.7;
        color: var(--ink);
        background: var(--cream);
    }
    
    /* ===========================================
       COVER PAGE
       =========================================== */
    
    .cover {
        page: cover;
        page-break-after: always;
        width: 210mm;
        height: 297mm;
        position: relative;
        background: linear-gradient(160deg, var(--forest-deep) 0%, var(--forest-mid) 50%, var(--forest-light) 100%);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        color: var(--cream);
    }
    
    .cover-ornament-top {
        position: absolute;
        top: 35mm;
        left: 50%;
        transform: translateX(-50%);
        font-size: 24pt;
        color: var(--gold);
        letter-spacing: 12px;
    }
    
    .cover-content {
        padding: 0 30mm;
    }
    
    .cover-emoji {
        font-size: 48pt;
        margin-bottom: 20px;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
    }
    
    .cover-title {
        font-family: "TeX Gyre Bonum", "URW Bookman", "Palatino", serif;
        font-size: 42pt;
        font-weight: 400;
        letter-spacing: 3px;
        margin: 0 0 12px 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .cover-subtitle {
        font-family: "Lato", sans-serif;
        font-size: 11pt;
        font-weight: 300;
        letter-spacing: 6px;
        text-transform: uppercase;
        color: var(--gold-light);
        margin-top: 8px;
    }
    
    .cover-divider {
        width: 80px;
        height: 1px;
        background: var(--gold);
        margin: 35px auto;
    }
    
    .cover-date-range {
        font-family: "Lato", sans-serif;
        font-size: 12pt;
        font-weight: 300;
        letter-spacing: 2px;
        color: var(--cream-dark);
    }
    
    .cover-entry-count {
        font-family: "Lato", sans-serif;
        font-size: 9pt;
        font-weight: 300;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: var(--gold-muted);
        margin-top: 8px;
    }
    
    .cover-ornament-bottom {
        position: absolute;
        bottom: 35mm;
        left: 50%;
        transform: translateX(-50%);
        font-size: 18pt;
        color: var(--gold);
        letter-spacing: 8px;
    }
    
    /* ===========================================
       TABLE OF CONTENTS
       =========================================== */
    
    .toc {
        page: toc;
        page-break-after: always;
        padding-top: 25mm;
    }
    
    .toc-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .toc-ornament {
        font-size: 14pt;
        color: var(--gold);
        letter-spacing: 8px;
        margin-bottom: 15px;
    }
    
    .toc-title {
        font-family: "TeX Gyre Bonum", "URW Bookman", serif;
        font-size: 24pt;
        font-weight: 400;
        color: var(--forest-deep);
        letter-spacing: 4px;
        margin: 0;
    }
    
    .toc-subtitle {
        font-family: "Lato", sans-serif;
        font-size: 9pt;
        font-weight: 300;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: var(--ink-faded);
        margin-top: 8px;
    }
    
    .toc-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .toc-item {
        display: flex;
        align-items: baseline;
        padding: 10px 0;
        border-bottom: 1px solid var(--cream-dark);
    }
    
    .toc-item:last-child {
        border-bottom: none;
    }
    
    .toc-date {
        font-family: "Lato", sans-serif;
        font-size: 9pt;
        font-weight: 600;
        letter-spacing: 1px;
        color: var(--forest-mid);
        width: 90px;
        flex-shrink: 0;
    }
    
    .toc-entry-title {
        font-family: "TeX Gyre Bonum", "URW Bookman", serif;
        font-size: 11pt;
        color: var(--ink);
        flex-grow: 1;
        padding-right: 10px;
    }
    
    .toc-entry-title a {
        color: inherit;
        text-decoration: none;
    }
    
    .toc-dots {
        flex-grow: 1;
        border-bottom: 1px dotted var(--cream-dark);
        margin: 0 8px 4px 8px;
    }
    
    .toc-page {
        font-family: "Lato", sans-serif;
        font-size: 9pt;
        color: var(--ink-faded);
        flex-shrink: 0;
    }
    
    /* ===========================================
       DIARY ENTRIES
       =========================================== */
    
    .entry {
        page-break-before: always;
    }
    
    .entry-header {
        text-align: center;
        padding-bottom: 30px;
        margin-bottom: 30px;
        border-bottom: 1px solid var(--cream-dark);
    }
    
    .entry-date-ornament {
        font-size: 12pt;
        color: var(--gold);
        letter-spacing: 6px;
        margin-bottom: 12px;
    }
    
    .entry-weekday {
        font-family: "Lato", sans-serif;
        font-size: 9pt;
        font-weight: 600;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: var(--terracotta);
        margin-bottom: 6px;
    }
    
    .entry-date-main {
        font-family: "TeX Gyre Bonum", "URW Bookman", serif;
        font-size: 28pt;
        font-weight: 400;
        color: var(--forest-deep);
        margin: 0;
        letter-spacing: 1px;
    }
    
    .entry-year {
        font-family: "Lato", sans-serif;
        font-size: 10pt;
        font-weight: 300;
        letter-spacing: 3px;
        color: var(--ink-faded);
        margin-top: 4px;
    }
    
    .entry-title {
        font-family: "TeX Gyre Bonum", "URW Bookman", serif;
        font-size: 14pt;
        font-style: italic;
        color: var(--ink-light);
        margin-top: 15px;
        padding: 0 20px;
    }
    
    .entry-highlight {
        background: linear-gradient(135deg, var(--cream-warm) 0%, var(--cream) 100%);
        border-left: 3px solid var(--gold);
        padding: 15px 20px;
        margin: 25px 0;
        font-family: "TeX Gyre Bonum", "URW Bookman", serif;
        font-size: 10.5pt;
        font-style: italic;
        color: var(--ink-light);
        line-height: 1.6;
    }
    
    .entry-highlight::before {
        content: "✦ ";
        color: var(--gold);
    }
    
    /* Entry Content Typography */
    .entry-content {
        text-align: justify;
        hyphens: auto;
    }
    
    .entry-content h1 {
        display: none; /* Hide the original H1, we render it separately */
    }
    
    .entry-content h2 {
        font-family: "TeX Gyre Bonum", "URW Bookman", serif;
        font-size: 14pt;
        font-weight: 400;
        color: var(--forest-mid);
        margin: 35px 0 15px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--cream-dark);
        letter-spacing: 0.5px;
    }
    
    .entry-content h3 {
        font-family: "Lato", sans-serif;
        font-size: 11pt;
        font-weight: 600;
        color: var(--ink);
        margin: 25px 0 10px 0;
        letter-spacing: 0.5px;
    }
    
    .entry-content h4 {
        font-family: "Lato", sans-serif;
        font-size: 10pt;
        font-weight: 600;
        color: var(--ink-light);
        margin: 20px 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .entry-content p {
        margin: 0 0 14px 0;
        text-indent: 0;
    }
    
    .entry-content p + p {
        text-indent: 1.5em;
    }
    
    .entry-content strong {
        font-weight: 600;
        color: var(--ink);
    }
    
    .entry-content em {
        font-style: italic;
        color: var(--ink-light);
    }
    
    .entry-content a {
        color: var(--terracotta);
        text-decoration: none;
        border-bottom: 1px solid var(--terracotta-light);
    }
    
    /* Lists */
    .entry-content ul, .entry-content ol {
        margin: 15px 0 15px 0;
        padding-left: 25px;
    }
    
    .entry-content li {
        margin: 6px 0;
        padding-left: 5px;
    }
    
    .entry-content ul li::marker {
        color: var(--gold);
    }
    
    .entry-content ol li::marker {
        color: var(--forest-mid);
        font-weight: 600;
    }
    
    /* Blockquotes */
    .entry-content blockquote {
        margin: 25px 0;
        padding: 20px 25px;
        background: var(--cream-warm);
        border-left: 4px solid var(--gold);
        font-family: "TeX Gyre Bonum", "URW Bookman", serif;
        font-size: 11pt;
        font-style: italic;
        color: var(--ink-light);
        position: relative;
    }
    
    .entry-content blockquote::before {
        content: "\\201C";
        position: absolute;
        top: -5px;
        left: 10px;
        font-family: "TeX Gyre Bonum", serif;
        font-size: 36pt;
        color: var(--gold-light);
        opacity: 0.5;
    }
    
    .entry-content blockquote p {
        margin: 0;
        text-indent: 0;
    }
    
    /* Horizontal Rules */
    .entry-content hr {
        border: none;
        text-align: center;
        margin: 35px 0;
    }
    
    .entry-content hr::after {
        content: "◆ ◆ ◆";
        font-size: 8pt;
        color: var(--gold);
        letter-spacing: 8px;
    }
    
    /* Code */
    .entry-content code {
        font-family: "Noto Sans Mono", "DejaVu Sans Mono", monospace;
        font-size: 9pt;
        background: var(--cream-dark);
        padding: 2px 6px;
        border-radius: 3px;
        color: var(--forest-mid);
    }
    
    .entry-content pre {
        background: var(--forest-deep);
        color: var(--cream);
        padding: 15px 20px;
        border-radius: 4px;
        font-family: "Noto Sans Mono", "DejaVu Sans Mono", monospace;
        font-size: 9pt;
        line-height: 1.5;
        overflow-x: auto;
        white-space: pre-wrap;
        margin: 20px 0;
    }
    
    .entry-content pre code {
        background: none;
        padding: 0;
        color: inherit;
    }
    
    /* Tables */
    .entry-content table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 9.5pt;
    }
    
    .entry-content th {
        background: var(--forest-mid);
        color: var(--cream);
        font-weight: 600;
        text-transform: uppercase;
        font-size: 8pt;
        letter-spacing: 1px;
        padding: 10px 12px;
        text-align: left;
    }
    
    .entry-content td {
        padding: 10px 12px;
        border-bottom: 1px solid var(--cream-dark);
    }
    
    .entry-content tr:nth-child(even) td {
        background: var(--cream-warm);
    }
    
    /* Entry Footer */
    .entry-footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid var(--cream-dark);
        text-align: center;
    }
    
    .entry-footer-ornament {
        font-size: 10pt;
        color: var(--gold);
        letter-spacing: 6px;
    }
    
    /* ===========================================
       COLOPHON / END PAGE
       =========================================== */
    
    .colophon {
        page-break-before: always;
        padding-top: 80mm;
        text-align: center;
    }
    
    .colophon-ornament {
        font-size: 18pt;
        color: var(--gold);
        letter-spacing: 8px;
        margin-bottom: 30px;
    }
    
    .colophon-text {
        font-family: "Lato", sans-serif;
        font-size: 9pt;
        font-weight: 300;
        letter-spacing: 2px;
        color: var(--ink-faded);
        line-height: 2;
    }
    
    .colophon-generated {
        margin-top: 25px;
        font-family: "Lato", sans-serif;
        font-size: 8pt;
        font-style: italic;
        color: var(--ink-faded);
    }
    
    /* ===========================================
       PRINT UTILITIES
       =========================================== */
    
    .page-break {
        page-break-after: always;
    }
    
    .no-break {
        page-break-inside: avoid;
    }
    """


def build_html(entries):
    """Build a beautifully designed HTML document"""
    if not entries:
        return None

    first_date = entries[0].stem
    last_date = entries[-1].stem
    
    # Format date range nicely
    try:
        first_dt = datetime.strptime(first_date, "%Y-%m-%d")
        last_dt = datetime.strptime(last_date, "%Y-%m-%d")
        if first_date == last_date:
            date_range = first_dt.strftime("%B %d, %Y")
        elif first_dt.year == last_dt.year:
            date_range = f"{first_dt.strftime('%B %d')} – {last_dt.strftime('%B %d, %Y')}"
        else:
            date_range = f"{first_dt.strftime('%B %Y')} – {last_dt.strftime('%B %Y')}"
    except:
        date_range = f"{first_date} → {last_date}"
    
    entry_count = len(entries)
    
    # Build TOC items
    toc_items = []
    entry_sections = []

    for idx, entry_path in enumerate(entries, start=1):
        date_str = entry_path.stem
        content = entry_path.read_text()
        title = parse_entry_title(content, date_str)
        
        # Clean title of emojis for TOC (keep it elegant)
        title_clean = re.sub(r'[\U0001F300-\U0001F9FF]', '', title).strip()
        if not title_clean:
            title_clean = title
        
        anchor = f"entry-{idx}"
        weekday, month_day, year = format_date_display(date_str)
        
        # TOC entry
        toc_items.append(f'''
            <li class="toc-item">
                <span class="toc-date">{date_str}</span>
                <span class="toc-entry-title"><a href="#{anchor}">{escape(title_clean)}</a></span>
            </li>
        ''')
        
        # Convert markdown to HTML
        html_body = markdown.markdown(
            content,
            extensions=["fenced_code", "tables", "sane_lists", "smarty"]
        )
        
        # Extract highlight for the header area
        highlight = extract_highlight(content)
        highlight_html = ""
        if highlight:
            highlight_html = f'<div class="entry-highlight">{escape(highlight)}</div>'
        
        # Build entry section
        entry_sections.append(f'''
            <section class="entry" id="{anchor}">
                <header class="entry-header">
                    <div class="entry-date-ornament">◈</div>
                    <div class="entry-weekday">{weekday}</div>
                    <h1 class="entry-date-main">{month_day}</h1>
                    <div class="entry-year">{year}</div>
                    <div class="entry-title">{escape(title_clean)}</div>
                </header>
                
                {highlight_html}
                
                <div class="entry-content">
                    {html_body}
                </div>
                
                <footer class="entry-footer">
                    <div class="entry-footer-ornament">✦ ✦ ✦</div>
                </footer>
            </section>
        ''')

    toc_html = "\n".join(toc_items)
    entries_html = "\n".join(entry_sections)
    
    # Generation timestamp
    generated = datetime.now().strftime("%B %d, %Y at %H:%M")

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Cami's Diary</title>
    <style>
{get_css()}
    </style>
</head>
<body>
    <!-- ==================== COVER PAGE ==================== -->
    <section class="cover">
        <div class="cover-ornament-top">◆ ◆ ◆</div>
        
        <div class="cover-content">
            <div class="cover-emoji">🦎</div>
            <h1 class="cover-title">Cami's Diary</h1>
            <div class="cover-subtitle">A Digital Mind's Journal</div>
            
            <div class="cover-divider"></div>
            
            <div class="cover-date-range">{date_range}</div>
            <div class="cover-entry-count">{entry_count} {'Entry' if entry_count == 1 else 'Entries'}</div>
        </div>
        
        <div class="cover-ornament-bottom">◇ ◇ ◇</div>
    </section>
    
    <!-- ==================== TABLE OF CONTENTS ==================== -->
    <section class="toc">
        <header class="toc-header">
            <div class="toc-ornament">◈ ◈ ◈</div>
            <h2 class="toc-title">Contents</h2>
            <div class="toc-subtitle">Journal Entries</div>
        </header>
        
        <ul class="toc-list">
            {toc_html}
        </ul>
    </section>
    
    <!-- ==================== DIARY ENTRIES ==================== -->
    {entries_html}
    
    <!-- ==================== COLOPHON ==================== -->
    <section class="colophon">
        <div class="colophon-ornament">◆ ◆ ◆</div>
        <div class="colophon-text">
            Typeset in TeX Gyre Bonum &amp; Lato<br/>
            Crafted with care by OpenClaw
        </div>
        <div class="colophon-generated">
            Generated on {generated}
        </div>
    </section>
</body>
</html>
'''

    return html


def export_pdf(output_path: Path, month: str = None):
    """Export diary entries to a beautiful PDF, optionally filtered by month (YYYY-MM)"""
    config = load_config()
    diary_path = get_diary_path(config)
    entries = load_entries(diary_path, month=month)

    if not entries:
        if month:
            print(f"No diary entries found for {month} in {diary_path}")
        else:
            print(f"No diary entries found in {diary_path}")
        return False

    html = build_html(entries)
    if not html:
        print("Failed to build HTML")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write HTML for debugging (optional)
    # html_path = output_path.with_suffix('.html')
    # html_path.write_text(html)
    # print(f"✓ Debug HTML saved to {html_path}")
    
    HTML(string=html, base_url=str(diary_path)).write_pdf(str(output_path))
    month_label = f" ({month})" if month else ""
    print(f"✓ Exported PDF to {output_path}")
    print(f"  {len(entries)} entries{month_label} • Velvet Edition v1.0")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Export diary to a beautifully designed PDF (Velvet Edition)"
    )
    parser.add_argument("--output", "-o", help="Output PDF path")
    parser.add_argument("--debug-html", action="store_true", help="Also save HTML for debugging")
    parser.add_argument(
        "--month",
        metavar="YYYY-MM",
        help="Export only entries from this month (e.g. 2026-03). Defaults output to Cami-Diary-YYYY-MM.pdf",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all entries (default behavior when --month is not specified)",
    )
    args = parser.parse_args()

    # Validate --month format if provided
    if args.month and not re.match(r"^\d{4}-\d{2}$", args.month):
        parser.error(f"--month must be in YYYY-MM format, got: {args.month!r}")

    config = load_config()
    diary_path = get_diary_path(config)

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    elif args.month:
        output_path = diary_path / f"Cami-Diary-{args.month}.pdf"
    else:
        output_path = diary_path / DEFAULT_OUTPUT_NAME

    if args.debug_html:
        entries = load_entries(diary_path, month=args.month)
        if entries:
            html = build_html(entries)
            html_path = output_path.with_suffix('.html')
            html_path.write_text(html)
            print(f"✓ Debug HTML saved to {html_path}")

    export_pdf(output_path, month=args.month)


if __name__ == "__main__":
    main()
