#!/usr/bin/env python3
"""
Generate a header/hero HTML snippet for blog articles. Used by blog-generator skill.
Reads JSON from stdin: {"section": "header", "title": "...", "text": "...", "topic_type": "..."}
Outputs JSON: {"html_snippet": "<header class=\"...\">...</header>"}
"""

import json
import sys
import html as html_module

def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.stderr.write("Invalid JSON\n")
        sys.exit(1)
    title = payload.get("title", "").strip() or "Article"
    text = payload.get("text", "")[:500].strip()
    topic_type = payload.get("topic_type", "general")
    section = payload.get("section", "header")
    if section != "header":
        # Only produce header for section "header"
        print(json.dumps({}))
        return 0
    title_esc = html_module.escape(title, quote=True)
    # One-line summary for subtitle
    summary = " ".join(text.split()[:20]) if text else ""
    if len(summary) > 160:
        summary = summary[:157] + "..."
    summary_esc = html_module.escape(summary, quote=True) if summary else ""
    # Hero header snippet matching visual-explainer style (dark, typography-led)
    snippet = f'''<header class="ve-article-header" aria-label="Article header">
  <div class="ve-article-header__inner">
    <h1 class="ve-article-header__title">{title_esc}</h1>
    {f'<p class="ve-article-header__summary">{summary_esc}</p>' if summary_esc else ''}
  </div>
</header>'''
    out = {"html_snippet": snippet}
    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
