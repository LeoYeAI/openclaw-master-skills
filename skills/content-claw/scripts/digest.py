"""
Content Claw - Performance Digest

Aggregates engagement metrics across runs and generates summaries.
Supports hourly, daily, and weekly digests. Also serves as recipe leaderboard.

Usage:
    uv run digest.py <brand-dir> [--period hourly|daily|weekly] [--notify]
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BASE = Path(__file__).parent.parent


def load_feedback(brand_dir: str) -> dict:
    """Load the brand's feedback.yaml."""
    import yaml
    feedback_path = Path(brand_dir) / "feedback.yaml"
    if not feedback_path.exists():
        return {"insights": []}
    with open(feedback_path) as f:
        return yaml.safe_load(f) or {"insights": []}


def load_all_publish_records(brand_name: str) -> list[dict]:
    """Load all publish records across all runs for a brand."""
    content_dir = BASE / "content"
    if not content_dir.exists():
        return []
    records = []
    for d in content_dir.iterdir():
        if not d.is_dir():
            continue
        meta_file = d / "metadata.json"
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                if meta.get("brand", "").lower() != brand_name.lower():
                    continue
            except json.JSONDecodeError:
                pass
        records_file = d / "publish_records.json"
        if records_file.exists():
            try:
                for r in json.loads(records_file.read_text()):
                    r["run_dir"] = str(d)
                    r["recipe"] = d.name.split("_", 1)[-1] if "_" in d.name else "unknown"
                    records.append(r)
            except json.JSONDecodeError:
                pass
    return records


def filter_by_period(insights: list[dict], period: str) -> list[dict]:
    """Filter insights by time period."""
    now = datetime.now()
    if period == "hourly":
        cutoff = now - timedelta(hours=1)
    elif period == "daily":
        cutoff = now - timedelta(days=1)
    elif period == "weekly":
        cutoff = now - timedelta(weeks=1)
    else:
        return insights

    filtered = []
    for i in insights:
        checked = i.get("checked_at", "")
        if checked:
            try:
                dt = datetime.fromisoformat(checked)
                if dt >= cutoff:
                    filtered.append(i)
            except ValueError:
                pass
    return filtered


def compute_leaderboard(insights: list[dict], records: list[dict]) -> list[dict]:
    """Rank recipes by average engagement per platform."""
    recipe_stats = defaultdict(lambda: defaultdict(list))

    # Map URLs to recipes via publish records
    url_to_recipe = {}
    for r in records:
        url = r.get("url", "")
        recipe = r.get("recipe", "unknown")
        if url:
            url_to_recipe[url] = recipe

    for i in insights:
        url = i.get("url", "")
        recipe = url_to_recipe.get(url, "unknown")
        platform = i.get("platform", "unknown")
        metrics = i.get("metrics", {})

        engagement = sum(metrics.get(k, 0) for k in ["upvotes", "likes", "comments", "replies", "retweets"])
        if engagement > 0:
            recipe_stats[f"{recipe} ({platform})"]["engagement"].append(engagement)
            recipe_stats[f"{recipe} ({platform})"]["views"].append(metrics.get("views", 0))

    leaderboard = []
    for key, stats in recipe_stats.items():
        eng = stats["engagement"]
        leaderboard.append({
            "recipe_platform": key,
            "posts": len(eng),
            "avg_engagement": round(sum(eng) / len(eng), 1) if eng else 0,
            "max_engagement": max(eng) if eng else 0,
            "total_engagement": sum(eng),
        })

    leaderboard.sort(key=lambda x: x["avg_engagement"], reverse=True)
    return leaderboard


def generate_digest(brand_dir: str, period: str = "daily") -> dict:
    """Generate a performance digest."""
    brand_name = Path(brand_dir).name
    feedback = load_feedback(brand_dir)
    records = load_all_publish_records(brand_name)
    insights = filter_by_period(feedback.get("insights", []), period)

    # Aggregate metrics
    total_engagement = 0
    platforms = defaultdict(int)
    top_post = None
    worst_post = None
    live_count = 0
    removed_count = 0

    for i in insights:
        metrics = i.get("metrics", {})
        eng = sum(metrics.get(k, 0) for k in ["upvotes", "likes", "comments", "replies", "retweets"])
        total_engagement += eng
        platforms[i.get("platform", "unknown")] += eng

        if i.get("status") == "live":
            live_count += 1
        elif i.get("status") == "removed":
            removed_count += 1

        if top_post is None or eng > top_post.get("_engagement", 0):
            top_post = {**i, "_engagement": eng}
        if worst_post is None or (eng < worst_post.get("_engagement", float("inf")) and eng > 0):
            worst_post = {**i, "_engagement": eng}

    leaderboard = compute_leaderboard(feedback.get("insights", []), records)

    digest = {
        "brand": brand_name,
        "period": period,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "posts_tracked": len(insights),
            "total_engagement": total_engagement,
            "avg_engagement": round(total_engagement / max(len(insights), 1), 1),
            "live": live_count,
            "removed": removed_count,
            "by_platform": dict(platforms),
        },
        "top_performer": {
            "url": top_post.get("url", ""),
            "platform": top_post.get("platform", ""),
            "engagement": top_post.get("_engagement", 0),
        } if top_post else None,
        "worst_performer": {
            "url": worst_post.get("url", ""),
            "platform": worst_post.get("platform", ""),
            "engagement": worst_post.get("_engagement", 0),
        } if worst_post else None,
        "leaderboard": leaderboard[:10],
        "total_published": len(records),
    }

    # Save digest
    digests_dir = BASE / "content" / "digests"
    digests_dir.mkdir(parents=True, exist_ok=True)
    digest_file = digests_dir / f"{datetime.now().strftime('%Y-%m-%d_%H%M')}_{period}_{brand_name}.json"
    digest_file.write_text(json.dumps(digest, indent=2))
    digest["saved_to"] = str(digest_file)

    return digest


def format_discord_digest(digest: dict) -> str:
    """Format digest for Discord notification."""
    s = digest["summary"]
    lines = [
        f"**{digest['period'].title()} Digest for {digest['brand']}**",
        f"Posts tracked: {s['posts_tracked']} | Total engagement: {s['total_engagement']} | Avg: {s['avg_engagement']}",
        f"Live: {s['live']} | Removed: {s['removed']}",
    ]

    if digest.get("top_performer"):
        t = digest["top_performer"]
        lines.append(f"Top: {t['engagement']} engagement on {t['platform']} ({t['url'][:50]})")

    if digest.get("leaderboard"):
        lines.append("\n**Recipe Leaderboard:**")
        for i, l in enumerate(digest["leaderboard"][:5], 1):
            lines.append(f"  {i}. {l['recipe_platform']}: avg {l['avg_engagement']} ({l['posts']} posts)")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: digest.py <brand-dir> [--period hourly|daily|weekly] [--notify]"}))
        sys.exit(1)

    brand_dir = sys.argv[1]
    period = "daily"
    notify = False

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--period" and i + 1 < len(args):
            period = args[i + 1]
            i += 2
        elif args[i] == "--notify":
            notify = True
            i += 1
        else:
            i += 1

    digest = generate_digest(brand_dir, period)
    print(json.dumps(digest, indent=2))

    if notify:
        try:
            from notify import send_discord
            msg = format_discord_digest(digest)
            send_discord(msg)
        except Exception as e:
            print(f"Discord notify failed: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
