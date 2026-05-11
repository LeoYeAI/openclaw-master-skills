"""
Content Claw - Content Publisher

Publishes content to Reddit and X/Twitter via Playwright. Actually submits posts.

Usage:
    uv run publish.py <content-dir> <platform> [--subreddit <name>] [--dry-run]
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

sys.path.insert(0, str(Path(__file__).parent))
from env import load_env
from browser import create_browser_context


def add_utm(url: str, source: str, medium: str, campaign: str) -> str:
    """Add UTM parameters to a URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params["utm_source"] = [source]
    params["utm_medium"] = [medium]
    params["utm_campaign"] = [campaign]
    new_query = urlencode({k: v[0] for k, v in params.items()})
    return urlunparse(parsed._replace(query=new_query))


def load_run_metadata(content_dir: str) -> dict:
    """Load run metadata and content files from a run directory."""
    path = Path(content_dir)
    metadata = {}

    meta_file = path / "metadata.json"
    if meta_file.exists():
        metadata = json.loads(meta_file.read_text())

    text_files = list(path.glob("*.md"))
    spec_files = list(path.glob("*-spec.json"))

    metadata["text_files"] = [str(f) for f in text_files]
    metadata["spec_files"] = [str(f) for f in spec_files]
    metadata["image_files"] = [str(f) for f in path.glob("*.png")] + [str(f) for f in path.glob("*.jpg")]

    if text_files:
        metadata["post_text"] = text_files[0].read_text()
    else:
        metadata["post_text"] = ""

    for sf in spec_files:
        spec = json.loads(sf.read_text())
        if "image_url" in spec:
            metadata["image_url"] = spec["image_url"]
            break

    return metadata


def publish_reddit(content: str, subreddit: str, title: str, cookie_path: str, dry_run: bool = False) -> dict:
    """Publish a post to Reddit. Actually clicks submit."""
    if dry_run:
        return {
            "status": "dry_run", "platform": "reddit", "subreddit": subreddit,
            "title": title, "content_preview": content[:200],
        }

    with create_browser_context(cookie_path) as (page, context, browser):
        try:
            submit_url = f"https://www.reddit.com/r/{subreddit}/submit?type=TEXT"
            page.goto(submit_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Fill title
            title_input = page.query_selector('textarea[name="title"], input[name="title"], div[slot="title"] textarea')
            if title_input:
                title_input.fill(title)
            page.wait_for_timeout(500)

            # Fill body
            body_input = page.query_selector('div[contenteditable="true"], textarea[name="text"], div[slot="text"] div[contenteditable]')
            if body_input:
                body_input.fill(content)
            page.wait_for_timeout(1000)

            # Click submit
            submit_btn = page.query_selector('button[type="submit"]:has-text("Post"), button:has-text("Post"), faceplate-tracker[action="submit"]')
            if submit_btn:
                submit_btn.click()
                page.wait_for_timeout(5000)

                # Check for redirect to the new post
                current_url = page.url
                if "/comments/" in current_url:
                    return {
                        "status": "published", "platform": "reddit",
                        "subreddit": subreddit, "title": title,
                        "url": current_url,
                        "content_preview": content[:200],
                    }

            # If we got here, submit may not have worked
            return {
                "status": "submitted", "platform": "reddit",
                "subreddit": subreddit, "title": title,
                "url": page.url,
                "content_preview": content[:200],
                "message": "Form submitted but could not confirm post URL",
            }

        except Exception as e:
            return {"error": str(e), "platform": "reddit"}


def publish_x(content: str, cookie_path: str, image_url: str | None = None, dry_run: bool = False) -> dict:
    """Publish a post to X/Twitter. Actually clicks post."""
    if dry_run:
        return {
            "status": "dry_run", "platform": "x",
            "content_preview": content[:280], "image_url": image_url,
        }

    with create_browser_context(cookie_path) as (page, context, browser):
        try:
            page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Fill tweet
            composer = page.query_selector('div[data-testid="tweetTextarea_0"], div[role="textbox"]')
            if composer:
                composer.fill(content[:280])
            page.wait_for_timeout(1000)

            # Click post
            post_btn = page.query_selector('button[data-testid="tweetButton"], button[data-testid="tweetButtonInline"]')
            if post_btn:
                post_btn.click()
                page.wait_for_timeout(5000)

                # Try to find the posted tweet URL
                current_url = page.url
                if "/status/" in current_url:
                    return {
                        "status": "published", "platform": "x",
                        "url": current_url,
                        "content_preview": content[:280],
                    }

            return {
                "status": "submitted", "platform": "x",
                "url": page.url,
                "content_preview": content[:280],
                "message": "Tweet submitted but could not confirm URL",
            }

        except Exception as e:
            return {"error": str(e), "platform": "x"}


def save_publish_record(content_dir: str, result: dict):
    """Save a publish record for tracking."""
    path = Path(content_dir)
    records_file = path / "publish_records.json"
    records = json.loads(records_file.read_text()) if records_file.exists() else []
    result["published_at"] = datetime.now().isoformat()
    records.append(result)
    records_file.write_text(json.dumps(records, indent=2))


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: publish.py <content-dir> <platform> [--subreddit <name>] [--dry-run]"}), file=sys.stderr)
        sys.exit(1)

    load_env()

    content_dir = sys.argv[1]
    platform = sys.argv[2]
    subreddit = None
    dry_run = False

    base = Path(__file__).parent.parent
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--subreddit" and i + 1 < len(args):
            subreddit = args[i + 1]
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            i += 1

    metadata = load_run_metadata(content_dir)
    post_text = metadata.get("post_text", "")

    if not post_text:
        print(json.dumps({"error": "No content found in run directory"}))
        sys.exit(1)

    # Add UTM tracking
    campaign = Path(content_dir).name
    if "http" in post_text:
        urls = re.findall(r'https?://[^\s\)]+', post_text)
        for url in urls:
            tracked_url = add_utm(url, source=platform, medium="social", campaign=campaign)
            post_text = post_text.replace(url, tracked_url)

    cookie_path = str(base / "creds" / f"{platform if platform != 'x' else 'x'}-cookies.json")
    if platform == "reddit":
        cookie_path = str(base / "creds" / "reddit-cookies.json")
        if not subreddit:
            print(json.dumps({"error": "Reddit requires --subreddit <name>"}))
            sys.exit(1)
        title = post_text.split("\n")[0].strip().lstrip("#").strip()[:300]
        result = publish_reddit(post_text, subreddit, title, cookie_path, dry_run=dry_run)
    elif platform == "x":
        cookie_path = str(base / "creds" / "x-cookies.json")
        result = publish_x(post_text, cookie_path, image_url=metadata.get("image_url"), dry_run=dry_run)
    else:
        result = {"error": f"Unsupported platform: {platform}"}

    save_publish_record(content_dir, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
