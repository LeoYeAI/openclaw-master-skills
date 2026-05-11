"""
Content Claw - Engagement Tracker

Checks published content for engagement metrics (upvotes, comments, likes, retweets).
Updates publish records and brand graph feedback layer.

Usage:
    uv run track_engagement.py <content-dir> [--reddit-cookie <path>] [--x-cookie <path>]
    uv run track_engagement.py --brand <brand-dir> [--reddit-cookie <path>] [--x-cookie <path>]

The --brand flag tracks ALL published content for a brand across all runs.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_env():
    """Load only declared keys from .env (scoped to FAL_KEY, EXA_API_KEY)."""
    allowed = {"FAL_KEY", "EXA_API_KEY"}
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key in allowed:
            os.environ.setdefault(key, value.strip())


def check_reddit_post(url: str, cookie_path: str | None = None) -> dict:
    """Check a Reddit post's current engagement metrics."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1280, "height": 800},
        )

        if cookie_path and Path(cookie_path).exists():
            cookies = json.loads(Path(cookie_path).read_text())
            context.add_cookies(cookies)

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        metrics = {"url": url, "platform": "reddit", "checked_at": datetime.now().isoformat()}

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Check if post is still live
            removed = page.query_selector('span:has-text("[removed]"), span:has-text("[deleted]")')
            metrics["status"] = "removed" if removed else "live"

            # Extract upvotes
            score_el = page.query_selector('div[id*="vote-arrows"] button[aria-label*="upvote"]')
            if not score_el:
                score_el = page.query_selector('shreddit-post')
            if score_el:
                score_text = score_el.get_attribute("score") or ""
                if score_text.isdigit():
                    metrics["upvotes"] = int(score_text)

            # Extract comment count
            comments_el = page.query_selector('a[data-click-id="comments"], span:has-text("comment")')
            if comments_el:
                text = comments_el.inner_text()
                nums = [int(s) for s in text.split() if s.isdigit()]
                if nums:
                    metrics["comments"] = nums[0]

        except Exception as e:
            metrics["error"] = str(e)
        finally:
            context.close()
            browser.close()

    return metrics


def check_x_post(url: str, cookie_path: str | None = None) -> dict:
    """Check an X/Twitter post's current engagement metrics."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            viewport={"width": 1280, "height": 800},
        )

        if cookie_path and Path(cookie_path).exists():
            cookies = json.loads(Path(cookie_path).read_text())
            context.add_cookies(cookies)

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        metrics = {"url": url, "platform": "x", "checked_at": datetime.now().isoformat()}

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(5000)

            # Check if post still exists
            not_found = page.query_selector('span:has-text("doesn\\'t exist"), span:has-text("suspended")')
            metrics["status"] = "removed" if not_found else "live"

            # Extract engagement metrics
            metrics_els = page.query_selector_all('a[role="link"] span[data-testid]')
            for el in metrics_els:
                text = el.inner_text().strip()
                parent = el.evaluate("el => el.closest('a')?.getAttribute('aria-label') || ''")
                if "like" in parent.lower():
                    metrics["likes"] = parse_metric(text)
                elif "repost" in parent.lower() or "retweet" in parent.lower():
                    metrics["retweets"] = parse_metric(text)
                elif "reply" in parent.lower() or "comment" in parent.lower():
                    metrics["replies"] = parse_metric(text)
                elif "view" in parent.lower():
                    metrics["views"] = parse_metric(text)

            # Try aria-label based extraction as fallback
            if "likes" not in metrics:
                group = page.query_selector('div[role="group"]')
                if group:
                    aria = group.get_attribute("aria-label") or ""
                    # Parse "5 replies, 10 reposts, 25 likes, 1000 views"
                    for part in aria.split(","):
                        part = part.strip().lower()
                        for key in ["replies", "reposts", "likes", "views", "bookmarks"]:
                            if key in part:
                                nums = [int(s) for s in part.split() if s.isdigit()]
                                if nums:
                                    if key == "reposts":
                                        metrics["retweets"] = nums[0]
                                    else:
                                        metrics[key] = nums[0]

        except Exception as e:
            metrics["error"] = str(e)
        finally:
            context.close()
            browser.close()

    return metrics


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


def update_brand_feedback(brand_dir: str, metrics: list[dict]):
    """Update the brand graph's feedback layer with engagement data."""
    import yaml

    feedback_path = Path(brand_dir) / "feedback.yaml"

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

        # Only add if we have actual metrics
        if insight["metrics"]:
            insights.append(insight)

    feedback["insights"] = insights
    feedback["last_tracked"] = datetime.now().isoformat()

    with open(feedback_path, "w") as f:
        yaml.dump(feedback, f, default_flow_style=False)


def find_publish_records(content_dir: str) -> list[dict]:
    """Find all publish records in a content directory."""
    path = Path(content_dir)
    records_file = path / "publish_records.json"
    if records_file.exists():
        return json.loads(records_file.read_text())
    return []


def find_all_brand_runs(brand_name: str) -> list[str]:
    """Find all content run directories for a brand."""
    content_dir = Path(__file__).parent.parent / "content"
    if not content_dir.exists():
        return []
    runs = []
    for d in content_dir.iterdir():
        if d.is_dir():
            records_file = d / "publish_records.json"
            if records_file.exists():
                runs.append(str(d))
    return runs


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: track_engagement.py <content-dir> or --brand <brand-dir>"
        }), file=sys.stderr)
        sys.exit(1)

    load_env()

    reddit_cookie = None
    x_cookie = None
    brand_dir = None
    content_dirs = []

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--reddit-cookie" and i + 1 < len(args):
            reddit_cookie = args[i + 1]
            i += 2
        elif args[i] == "--x-cookie" and i + 1 < len(args):
            x_cookie = args[i + 1]
            i += 2
        elif args[i] == "--brand" and i + 1 < len(args):
            brand_dir = args[i + 1]
            i += 2
        else:
            content_dirs.append(args[i])
            i += 1

    # Default cookie paths
    base = Path(__file__).parent.parent
    if not reddit_cookie:
        reddit_cookie = str(base / "creds" / "reddit-cookies.json")
    if not x_cookie:
        x_cookie = str(base / "creds" / "x-cookies.json")

    # Collect all publish records
    all_records = []

    if brand_dir:
        # Track all runs
        for run_dir in find_all_brand_runs(""):
            all_records.extend(
                (run_dir, r) for r in find_publish_records(run_dir)
            )
    else:
        for cd in content_dirs:
            all_records.extend(
                (cd, r) for r in find_publish_records(cd)
            )

    if not all_records:
        print(json.dumps({"error": "No publish records found"}))
        sys.exit(1)

    # Check engagement for each published post
    all_metrics = []
    for run_dir, record in all_records:
        url = record.get("url", "")
        platform = record.get("platform", "")

        if not url or record.get("status") in ("dry_run", "error"):
            continue

        if platform == "reddit":
            metrics = check_reddit_post(url, reddit_cookie)
        elif platform == "x":
            metrics = check_x_post(url, x_cookie)
        else:
            continue

        metrics["run_dir"] = run_dir
        all_metrics.append(metrics)

    # Update brand feedback if brand_dir provided
    if brand_dir and all_metrics:
        update_brand_feedback(brand_dir, all_metrics)

    output = {
        "tracked_at": datetime.now().isoformat(),
        "posts_checked": len(all_metrics),
        "metrics": all_metrics,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
