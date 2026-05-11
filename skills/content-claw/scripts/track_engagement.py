"""
Content Claw - Engagement Tracker

Checks published content for engagement metrics. Updates brand graph feedback.

Usage:
    uv run track_engagement.py <content-dir>
    uv run track_engagement.py --brand <brand-dir>
    uv run track_engagement.py --brand <brand-dir> --alert-threshold 50
"""

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from env import load_env
from browser import create_browser_context


def parse_metric(text: str) -> int:
    """Parse metric text like '1.2K' or '500' to int."""
    text = text.strip().upper().replace(",", "")
    if not text:
        return 0
    try:
        if "K" in text:
            return int(float(text.replace("K", "")) * 1000)
        if "M" in text:
            return int(float(text.replace("M", "")) * 1000000)
        return int(text)
    except (ValueError, TypeError):
        return 0


def check_reddit_post(page, url: str) -> dict:
    """Check a Reddit post's engagement metrics using an existing page."""
    metrics = {"url": url, "platform": "reddit", "checked_at": datetime.now().isoformat()}
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        removed = page.query_selector('span:has-text("[removed]"), span:has-text("[deleted]")')
        metrics["status"] = "removed" if removed else "live"

        score_el = page.query_selector('shreddit-post')
        if score_el:
            score_text = score_el.get_attribute("score") or ""
            if score_text.isdigit():
                metrics["upvotes"] = int(score_text)

        comments_el = page.query_selector('a[data-click-id="comments"], span:has-text("comment")')
        if comments_el:
            text = comments_el.inner_text()
            nums = [int(s) for s in text.split() if s.isdigit()]
            if nums:
                metrics["comments"] = nums[0]

    except Exception as e:
        metrics["error"] = str(e)
    return metrics


def check_x_post(page, url: str) -> dict:
    """Check an X/Twitter post's engagement metrics using an existing page."""
    metrics = {"url": url, "platform": "x", "checked_at": datetime.now().isoformat()}
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(5000)

        not_found = page.query_selector('span:has-text("doesn\'t exist"), span:has-text("suspended")')
        metrics["status"] = "removed" if not_found else "live"

        # Try aria-label extraction (most reliable)
        group = page.query_selector('div[role="group"]')
        if group:
            aria = group.get_attribute("aria-label") or ""
            for part in aria.split(","):
                part = part.strip().lower()
                for key in ["replies", "reposts", "likes", "views", "bookmarks"]:
                    if key in part:
                        nums = [int(s) for s in part.split() if s.isdigit()]
                        if nums:
                            mapped = "retweets" if key == "reposts" else key
                            metrics[mapped] = nums[0]

    except Exception as e:
        metrics["error"] = str(e)
    return metrics


def update_brand_feedback(brand_dir: str, metrics: list[dict]):
    """Update the brand graph's feedback layer with engagement data."""
    import yaml
    import fcntl

    feedback_path = Path(brand_dir) / "feedback.yaml"

    # File locking to prevent concurrent write corruption
    lock_path = Path(brand_dir) / ".feedback.lock"
    lock_path.touch()
    with open(lock_path) as lock_f:
        fcntl.flock(lock_f, fcntl.LOCK_EX)
        try:
            if feedback_path.exists():
                with open(feedback_path) as f:
                    feedback = yaml.safe_load(f) or {}
            else:
                feedback = {}

            insights = feedback.get("insights", [])

            for m in metrics:
                if "error" in m or m.get("status") == "removed":
                    continue
                insight = {
                    "url": m.get("url", ""),
                    "platform": m.get("platform", ""),
                    "checked_at": m.get("checked_at", ""),
                    "status": m.get("status", "unknown"),
                    "metrics": {},
                }
                for key in ["upvotes", "comments", "likes", "retweets", "replies", "views"]:
                    if key in m:
                        insight["metrics"][key] = m[key]
                if insight["metrics"]:
                    insights.append(insight)

            feedback["insights"] = insights
            feedback["last_tracked"] = datetime.now().isoformat()

            with open(feedback_path, "w") as f:
                yaml.dump(feedback, f, default_flow_style=False)
        finally:
            fcntl.flock(lock_f, fcntl.LOCK_UN)


def find_publish_records(content_dir: str) -> list[dict]:
    """Find all publish records in a content directory."""
    records_file = Path(content_dir) / "publish_records.json"
    if records_file.exists():
        return json.loads(records_file.read_text())
    return []


def find_all_brand_runs(brand_name: str) -> list[str]:
    """Find all content run directories for a specific brand."""
    content_dir = Path(__file__).parent.parent / "content"
    if not content_dir.exists():
        return []
    runs = []
    for d in content_dir.iterdir():
        if not d.is_dir():
            continue
        # Check metadata.json for brand match
        meta = d / "metadata.json"
        if meta.exists():
            try:
                data = json.loads(meta.read_text())
                if data.get("brand", "").lower() == brand_name.lower():
                    runs.append(str(d))
                    continue
            except (json.JSONDecodeError, KeyError):
                pass
        # Fallback: check if directory has publish records
        if (d / "publish_records.json").exists():
            runs.append(str(d))
    return runs


def check_alerts(metrics: list[dict], threshold: int) -> list[dict]:
    """Check if any metrics crossed the alert threshold."""
    alerts = []
    for m in metrics:
        if "error" in m:
            continue
        for key in ["upvotes", "likes", "views"]:
            val = m.get(key, 0)
            if val >= threshold:
                alerts.append({
                    "url": m.get("url", ""),
                    "platform": m.get("platform", ""),
                    "metric": key,
                    "value": val,
                    "threshold": threshold,
                })
    return alerts


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: track_engagement.py <content-dir> or --brand <brand-dir>"}), file=sys.stderr)
        sys.exit(1)

    load_env()

    brand_dir = None
    content_dirs = []
    alert_threshold = 50

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--brand" and i + 1 < len(args):
            brand_dir = args[i + 1]
            i += 2
        elif args[i] == "--alert-threshold" and i + 1 < len(args):
            alert_threshold = int(args[i + 1])
            i += 2
        else:
            content_dirs.append(args[i])
            i += 1

    base = Path(__file__).parent.parent
    reddit_cookie = str(base / "creds" / "reddit-cookies.json")
    x_cookie = str(base / "creds" / "x-cookies.json")

    # Collect all publish records
    all_records = []
    if brand_dir:
        brand_name = Path(brand_dir).name
        for run_dir in find_all_brand_runs(brand_name):
            all_records.extend((run_dir, r) for r in find_publish_records(run_dir))
    else:
        for cd in content_dirs:
            all_records.extend((cd, r) for r in find_publish_records(cd))

    if not all_records:
        print(json.dumps({"error": "No publish records found"}))
        sys.exit(1)

    # Group by platform to minimize browser launches
    reddit_urls = [(rd, r) for rd, r in all_records if r.get("platform") == "reddit" and r.get("url") and r.get("status") not in ("dry_run", "error")]
    x_urls = [(rd, r) for rd, r in all_records if r.get("platform") == "x" and r.get("url") and r.get("status") not in ("dry_run", "error")]

    all_metrics = []

    # Check Reddit posts (one browser session for all)
    if reddit_urls:
        try:
            with create_browser_context(reddit_cookie) as (page, ctx, br):
                for run_dir, record in reddit_urls:
                    m = check_reddit_post(page, record["url"])
                    m["run_dir"] = run_dir
                    all_metrics.append(m)
        except Exception as e:
            all_metrics.append({"error": f"Reddit browser failed: {e}", "platform": "reddit"})

    # Check X posts (one browser session for all)
    if x_urls:
        try:
            with create_browser_context(x_cookie) as (page, ctx, br):
                for run_dir, record in x_urls:
                    m = check_x_post(page, record["url"])
                    m["run_dir"] = run_dir
                    all_metrics.append(m)
        except Exception as e:
            all_metrics.append({"error": f"X browser failed: {e}", "platform": "x"})

    # Update brand feedback
    if brand_dir and all_metrics:
        update_brand_feedback(brand_dir, all_metrics)

    # Check alerts
    alerts = check_alerts(all_metrics, alert_threshold)

    output = {
        "tracked_at": datetime.now().isoformat(),
        "posts_checked": len(all_metrics),
        "metrics": all_metrics,
        "alerts": alerts,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
