#!/usr/bin/env python3
"""
content_tracker.py — Content Creator Pro
Manages performance.json: add posts, compute stats, rebuild from library.

Usage:
  python3 content_tracker.py add     --platform twitter --format thread \
                                      --hook credibility --hook-text "..." \
                                      --impressions 4200 --engagements 312
  python3 content_tracker.py stats   [--platform twitter]
  python3 content_tracker.py top     [--limit 5]
  python3 content_tracker.py rebuild --library /workspace/content/library/
  python3 content_tracker.py weekly
"""

import json
import argparse
import os
import sys
from datetime import datetime, date

PERFORMANCE_FILE = "/workspace/content/performance.json"
LIBRARY_DIR      = "/workspace/content/library/"
HOOKS_FILE       = "/workspace/content/hooks.md"
AUDIT_FILE       = "/workspace/AUDIT.md"
ERRORS_FILE      = "/workspace/.learnings/ERRORS.md"

VIRAL_THRESHOLDS = {
    "twitter":   {"er": 5.0, "impressions": 1000},
    "linkedin":  {"er": 3.0, "impressions": 500},
    "reddit":    {"upvotes": 200},
    "substack":  {"open_rate": 40},
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_performance():
    if not os.path.exists(PERFORMANCE_FILE):
        return {"summary": {}, "posts": [], "validated_hooks": {}, "weekly_summaries": []}
    with open(PERFORMANCE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_performance(data):
    os.makedirs(os.path.dirname(PERFORMANCE_FILE), exist_ok=True)
    with open(PERFORMANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_audit(message):
    os.makedirs(os.path.dirname(AUDIT_FILE), exist_ok=True)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {message}\n")


def log_error(error_type, description, action, resolution="pending"):
    os.makedirs(os.path.dirname(ERRORS_FILE), exist_ok=True)
    with open(ERRORS_FILE, "a", encoding="utf-8") as f:
        entry = (
            f"\n[{datetime.now().strftime('%Y-%m-%d')}] {error_type}\n"
            f"  Description: {description}\n"
            f"  Action taken: {action}\n"
            f"  Resolution: {resolution}\n"
        )
        f.write(entry)


def compute_er(impressions, engagements):
    if not impressions:
        return 0.0
    return round((engagements / impressions) * 100, 2)


def is_viral(post):
    platform = post.get("platform", "")
    er = post.get("engagement_rate", 0)
    thresh = VIRAL_THRESHOLDS.get(platform, {})
    if "er" in thresh:
        return er >= thresh["er"]
    return False


def update_summary(data):
    real_posts = [p for p in data.get("posts", []) if not p.get("_example")]
    if not real_posts:
        return
    total_impressions = sum(p.get("impressions", 0) for p in real_posts)
    total_engagements = sum(p.get("engagements", 0) for p in real_posts)
    avg_er = compute_er(total_impressions, total_engagements)

    # Top hook type
    from collections import Counter
    viral = [p for p in real_posts if is_viral(p)]
    hook_counts = Counter(p.get("hook_type") for p in viral if p.get("hook_type"))
    top_hook = hook_counts.most_common(1)[0][0] if hook_counts else None

    platform_counts = Counter(p.get("platform") for p in viral if p.get("platform"))
    top_platform = platform_counts.most_common(1)[0][0] if platform_counts else None

    data["summary"] = {
        "total_posts": len(real_posts),
        "total_impressions": total_impressions,
        "total_engagements": total_engagements,
        "average_engagement_rate": avg_er,
        "top_hook_type": top_hook,
        "top_platform": top_platform,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def save_hook(hook_text, platform, hook_type, er):
    """Append a validated hook to hooks.md"""
    os.makedirs(os.path.dirname(HOOKS_FILE), exist_ok=True)
    with open(HOOKS_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"\n## [{datetime.now().strftime('%Y-%m-%d')}] {platform} — {hook_type} — {er}% ER\n"
            f"{hook_text}\n"
        )


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_add(args):
    data = load_performance()
    real_posts = [p for p in data.get("posts", []) if not p.get("_example")]

    # Generate ID
    today = date.today().strftime("%Y%m%d")
    count = sum(1 for p in real_posts if p.get("id", "").startswith(f"{args.platform[:2]}-{today}")) + 1
    post_id = f"{args.platform[:2]}-{today}-{count:03d}"

    er = compute_er(args.impressions, args.engagements)
    viral = er >= VIRAL_THRESHOLDS.get(args.platform, {}).get("er", 999)

    post = {
        "id": post_id,
        "date": date.today().isoformat(),
        "platform": args.platform,
        "format": args.format,
        "hook_type": args.hook,
        "hook_text": args.hook_text,
        "topic_pillar": getattr(args, "pillar", 1),
        "impressions": args.impressions,
        "engagements": args.engagements,
        "engagement_rate": er,
        "follows_gained": getattr(args, "follows", 0),
        "revenue_attributed": getattr(args, "revenue", 0),
        "ai_detection_score": None,
        "validated_hook": viral,
        "repurposed": False,
        "notes": getattr(args, "notes", ""),
    }

    data["posts"].append(post)
    update_summary(data)
    save_performance(data)

    if viral:
        save_hook(args.hook_text, args.platform, args.hook, er)
        log_audit(f"🔥 Viral: [{args.hook_text[:60]}] → {er}% ER on {args.platform}")
        print(f"✅ Post {post_id} added — VIRAL ({er}% ER) 🔥")
    else:
        print(f"✅ Post {post_id} added ({er}% ER)")


def cmd_stats(args):
    data = load_performance()
    s = data.get("summary", {})
    platform = getattr(args, "platform", None)

    if platform:
        posts = [p for p in data.get("posts", [])
                 if p.get("platform") == platform and not p.get("_example")]
        if not posts:
            print(f"No posts found for {platform}")
            return
        total_imp = sum(p.get("impressions", 0) for p in posts)
        total_eng = sum(p.get("engagements", 0) for p in posts)
        er = compute_er(total_imp, total_eng)
        viral_count = sum(1 for p in posts if is_viral(p))
        print(f"\n📊 Stats for {platform}:")
        print(f"   Posts:       {len(posts)}")
        print(f"   Impressions: {total_imp:,}")
        print(f"   Engagements: {total_eng:,}")
        print(f"   Avg ER:      {er}%")
        print(f"   Viral posts: {viral_count}")
    else:
        print(f"\n📊 Overall Stats:")
        print(f"   Total posts:    {s.get('total_posts', 0)}")
        print(f"   Total impress.: {s.get('total_impressions', 0):,}")
        print(f"   Avg ER:         {s.get('average_engagement_rate', 0)}%")
        print(f"   Top hook type:  {s.get('top_hook_type', 'N/A')}")
        print(f"   Top platform:   {s.get('top_platform', 'N/A')}")
        print(f"   Last updated:   {s.get('last_updated', 'N/A')}")


def cmd_top(args):
    data = load_performance()
    limit = getattr(args, "limit", 5)
    posts = [p for p in data.get("posts", []) if not p.get("_example")]
    sorted_posts = sorted(posts, key=lambda x: x.get("engagement_rate", 0), reverse=True)

    print(f"\n🏆 Top {limit} posts by engagement rate:")
    for i, p in enumerate(sorted_posts[:limit], 1):
        print(f"  {i}. [{p.get('platform')}] {p.get('engagement_rate')}% ER — {p.get('hook_text', '')[:60]}")


def cmd_rebuild(args):
    """Rebuild performance.json from library/ files"""
    library = getattr(args, "library", LIBRARY_DIR)
    if not os.path.exists(library):
        print(f"❌ Library dir not found: {library}")
        log_error("PERFORMANCE_CORRUPT", "Rebuild attempted but library not found",
                  f"Rebuild skipped — library {library} missing", "pending")
        return

    posts = []
    for root, dirs, files in os.walk(library):
        for fname in files:
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(root, fname), encoding="utf-8") as f:
                        post = json.load(f)
                        posts.append(post)
                except Exception as e:
                    print(f"  ⚠️  Skipped {fname}: {e}")

    data = load_performance()
    data["posts"] = posts
    update_summary(data)
    save_performance(data)
    log_audit(f"performance.json rebuilt from library/ — {len(posts)} posts loaded")
    log_error("PERFORMANCE_CORRUPT", "performance.json was corrupted",
              f"Rebuilt from library/ — {len(posts)} posts restored", "resolved")
    print(f"✅ Rebuilt performance.json — {len(posts)} posts loaded")


def cmd_weekly(args):
    """Generate weekly summary and write to performance.json"""
    data = load_performance()
    update_summary(data)

    from datetime import timedelta
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_key = f"{today.year}-W{today.isocalendar()[1]:02d}"

    week_posts = [p for p in data.get("posts", [])
                  if not p.get("_example")
                  and p.get("date", "") >= week_start.isoformat()]

    if not week_posts:
        print("No posts this week yet.")
        return

    sorted_week = sorted(week_posts, key=lambda x: x.get("engagement_rate", 0), reverse=True)
    top = sorted_week[0] if sorted_week else {}

    from collections import Counter
    hook_counts = Counter(p.get("hook_type") for p in week_posts)
    pattern = f"Top hook: {hook_counts.most_common(1)[0][0]}" if hook_counts else None

    summary = {
        "week": week_key,
        "posts_published": len(week_posts),
        "top_post_id": top.get("id"),
        "top_post_er": top.get("engagement_rate", 0),
        "pattern_identified": pattern,
        "calendar_adjustment": None,
    }

    existing = [w for w in data.get("weekly_summaries", []) if w.get("week") != week_key]
    existing.append(summary)
    data["weekly_summaries"] = existing

    save_performance(data)
    log_audit(f"Weekly summary generated: {week_key} — {len(week_posts)} posts, top ER: {top.get('engagement_rate', 0)}%")

    print(f"\n📅 Week {week_key} Summary:")
    print(f"   Posts:    {summary['posts_published']}")
    print(f"   Top post: {summary['top_post_id']} ({summary['top_post_er']}% ER)")
    print(f"   Pattern:  {summary['pattern_identified']}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Content Creator Pro — Performance Tracker")
    sub = parser.add_subparsers(dest="command")

    # add
    p_add = sub.add_parser("add", help="Log a published post")
    p_add.add_argument("--platform",   required=True, choices=["twitter","linkedin","reddit","substack"])
    p_add.add_argument("--format",     required=True)
    p_add.add_argument("--hook",       required=True)
    p_add.add_argument("--hook-text",  required=True, dest="hook_text")
    p_add.add_argument("--impressions",type=int, default=0)
    p_add.add_argument("--engagements",type=int, default=0)
    p_add.add_argument("--follows",    type=int, default=0)
    p_add.add_argument("--revenue",    type=float, default=0)
    p_add.add_argument("--pillar",     type=int, default=1)
    p_add.add_argument("--notes",      default="")

    # stats
    p_stats = sub.add_parser("stats", help="Show performance stats")
    p_stats.add_argument("--platform", choices=["twitter","linkedin","reddit","substack"])

    # top
    p_top = sub.add_parser("top", help="Show top posts by ER")
    p_top.add_argument("--limit", type=int, default=5)

    # rebuild
    p_rebuild = sub.add_parser("rebuild", help="Rebuild performance.json from library/")
    p_rebuild.add_argument("--library", default=LIBRARY_DIR)

    # weekly
    sub.add_parser("weekly", help="Generate weekly summary")

    args = parser.parse_args()

    commands = {
        "add": cmd_add,
        "stats": cmd_stats,
        "top": cmd_top,
        "rebuild": cmd_rebuild,
        "weekly": cmd_weekly,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
