#!/usr/bin/env python3
"""将 collections/ 中的收藏同步到 Obsidian vault，做格式适配"""

import os
import re
import shutil
import yaml

# Default paths - customize for your setup
COLLECTIONS_DIR = os.path.expanduser(os.getenv("COLLECTIONS_DIR", "~/.openclaw/workspace/collections"))
OBSIDIAN_DIR = os.path.expanduser(os.getenv("OBSIDIAN_DIR", "~/ObsidianVault/收藏"))

# category -> obsidian subdirectory
CATEGORY_MAP = {
    "articles": "文章",
    "tweets": "推文",
    "videos": "视频",
    "wechat": "公众号",
    "ideas": "想法",
}

def parse_frontmatter(content):
    """Parse YAML frontmatter from markdown content"""
    if not content.startswith("---"):
        return {}, content
    end = content.find("---", 3)
    if end == -1:
        return {}, content
    fm_str = content[3:end].strip()
    try:
        fm = yaml.safe_load(fm_str)
    except:
        fm = {}
    body = content[end+3:].lstrip("\n")
    return fm or {}, body

def tags_to_obsidian(tags):
    """Convert tag list to Obsidian #tag format inline"""
    if not tags:
        return ""
    return " ".join(f"#{t.replace(' ', '_')}" for t in tags)

def build_obsidian_frontmatter(fm):
    """Build Obsidian-friendly YAML frontmatter"""
    obsidian_fm = {}
    
    # Keep essential fields
    for key in ["title", "source", "url", "author", "date_published", "date_collected", 
                "category", "language", "summary", "duration", "platform", "bvid"]:
        if key in fm:
            obsidian_fm[key] = fm[key]
    
    # Convert tags to Obsidian format (keep as list, Obsidian handles it)
    if "tags" in fm:
        obsidian_fm["tags"] = fm["tags"]
    
    # Add aliases for search
    if "title" in fm:
        obsidian_fm["aliases"] = [fm["title"]]
    
    return obsidian_fm

def sanitize_filename(title):
    """Make a safe filename from title"""
    # Remove/replace unsafe chars
    safe = re.sub(r'[<>:"/\\|?*]', '', title)
    safe = re.sub(r'\s+', ' ', safe).strip()
    # Truncate if too long
    if len(safe) > 80:
        safe = safe[:80].rstrip()
    return safe

def sync_file(src_path, category):
    """Sync a single collection file to KaiVault"""
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    fm, body = parse_frontmatter(content)
    
    # Determine filename
    title = fm.get("title", os.path.basename(src_path).replace(".md", ""))
    safe_title = sanitize_filename(title)
    
    # Determine target directory
    subdir = CATEGORY_MAP.get(category, "文章")
    target_dir = os.path.join(OBSIDIAN_DIR, subdir)
    os.makedirs(target_dir, exist_ok=True)
    
    target_path = os.path.join(target_dir, f"{safe_title}.md")
    
    # Build Obsidian version
    obsidian_fm = build_obsidian_frontmatter(fm)
    
    # Build content
    fm_str = yaml.dump(obsidian_fm, allow_unicode=True, default_flow_style=False, sort_keys=False).strip()
    
    # Add tag line after frontmatter
    tag_line = tags_to_obsidian(fm.get("tags", []))
    
    obsidian_content = f"---\n{fm_str}\n---\n\n{tag_line}\n\n{body}" if tag_line else f"---\n{fm_str}\n---\n\n{body}"
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(obsidian_content)
    
    print(f"  ✅ {safe_title}")
    return target_path

def main():
    synced = 0
    
    for category in ["articles", "videos", "tweets", "wechat", "ideas"]:
        cat_dir = os.path.join(COLLECTIONS_DIR, category)
        if not os.path.isdir(cat_dir):
            continue
        
        files = [f for f in os.listdir(cat_dir) if f.endswith(".md")]
        if not files:
            continue
        
        print(f"\n📂 {category} ({len(files)} 篇)")
        for fname in sorted(files):
            src = os.path.join(cat_dir, fname)
            try:
                sync_file(src, category)
                synced += 1
            except Exception as e:
                print(f"  ❌ {fname}: {e}")
    
    print(f"\n🎉 完成！共同步 {synced} 篇到 Obsidian")

if __name__ == "__main__":
    main()
