"""
Content Claw - Content Publisher

Publishes generated content to Reddit and X/Twitter using Playwright
with authenticated sessions. Adds UTM tracking to all links.

Usage:
    uv run publish.py <content-dir> <platform> [--reddit-cookie <path>] [--x-cookie <path>] [--dry-run]

Arguments:
    content-dir: Path to a run directory (e.g., content/2026-03-18_paper-breakdown-insight/)
    platform: "reddit" or "x"

Environment:
    No API keys needed. Uses browser cookies for authentication.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse


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

    # Load metadata.json if it exists
    meta_file = path / "metadata.json"
    if meta_file.exists():
        metadata = json.loads(meta_file.read_text())

    # Find text content files
    text_files = list(path.glob("*.md"))
    spec_files = list(path.glob("*-spec.json"))
    image_files = list(path.glob("*.png")) + list(path.glob("*.jpg"))

    metadata["text_files"] = [str(f) for f in text_files]
    metadata["spec_files"] = [str(f) for f in spec_files]
    metadata["image_files"] = [str(f) for f in image_files]

    # Load first text file as the post content
    if text_files:
        metadata["post_text"] = text_files[0].read_text()
    else:
        metadata["post_text"] = ""

    # Load image URL from spec if available
    for sf in spec_files:
        spec = json.loads(sf.read_text())
        if "image_url" in spec:
            metadata["image_url"] = spec["image_url"]
            break

    return metadata


def publish_reddit(content: str, subreddit: str, title: str, cookie_path: str, image_path: str | None = None, dry_run: bool = False) -> dict:
    """Publish a post to Reddit using Playwright."""
    from playwright.sync_api import sync_playwright

    if dry_run:
        return {
            "status": "dry_run",
            "platform": "reddit",
            "subreddit": subreddit,
            "title": title,
            "content_preview": content[:200],
            "image": image_path,
        }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )

        # Load cookies
        if cookie_path and Path(cookie_path).exists():
            cookies = json.loads(Path(cookie_path).read_text())
            context.add_cookies(cookies)
        else:
            browser.close()
            return {"error": "Reddit cookies required. Run 'setup creds reddit' first."}

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            # Navigate to submit page
            submit_url = f"https://www.reddit.com/r/{subreddit}/submit"
            page.goto(submit_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Fill in the post
            # Title
            title_input = page.query_selector('textarea[name="title"], input[name="title"]')
            if title_input:
                title_input.fill(title)

            # Body
            body_input = page.query_selector('div[contenteditable="true"], textarea[name="text"]')
            if body_input:
                body_input.fill(content)

            page.wait_for_timeout(2000)

            # Get the current URL (should redirect to the post after submit)
            result = {
                "status": "ready",
                "platform": "reddit",
                "subreddit": subreddit,
                "title": title,
                "content_preview": content[:200],
                "message": "Post form filled. Review in browser before submitting.",
            }

        except Exception as e:
            result = {"error": str(e), "platform": "reddit"}
        finally:
            context.close()
            browser.close()

    return result


def publish_x(content: str, cookie_path: str, image_url: str | None = None, dry_run: bool = False) -> dict:
    """Publish a post to X/Twitter using Playwright."""
    from playwright.sync_api import sync_playwright

    if dry_run:
        return {
            "status": "dry_run",
            "platform": "x",
            "content_preview": content[:280],
            "image_url": image_url,
        }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )

        if cookie_path and Path(cookie_path).exists():
            cookies = json.loads(Path(cookie_path).read_text())
            context.add_cookies(cookies)
        else:
            browser.close()
            return {"error": "X cookies required. Run 'setup creds x' first."}

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        try:
            page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)

            # Fill in the tweet
            composer = page.query_selector('div[data-testid="tweetTextarea_0"], div[role="textbox"]')
            if composer:
                composer.fill(content[:280])

            page.wait_for_timeout(2000)

            result = {
                "status": "ready",
                "platform": "x",
                "content_preview": content[:280],
                "message": "Post composed. Review before submitting.",
            }

        except Exception as e:
            result = {"error": str(e), "platform": "x"}
        finally:
            context.close()
            browser.close()

    return result


def save_publish_record(content_dir: str, result: dict):
    """Save a publish record for tracking."""
    path = Path(content_dir)
    records_file = path / "publish_records.json"

    records = []
    if records_file.exists():
        records = json.loads(records_file.read_text())

    result["published_at"] = datetime.now().isoformat()
    records.append(result)

    records_file.write_text(json.dumps(records, indent=2))


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: publish.py <content-dir> <platform> [--reddit-cookie <path>] [--x-cookie <path>] [--subreddit <name>] [--dry-run]"
        }), file=sys.stderr)
        sys.exit(1)

    load_env()

    content_dir = sys.argv[1]
    platform = sys.argv[2]

    reddit_cookie = None
    x_cookie = None
    subreddit = None
    dry_run = False

    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--reddit-cookie" and i + 1 < len(args):
            reddit_cookie = args[i + 1]
            i += 2
        elif args[i] == "--x-cookie" and i + 1 < len(args):
            x_cookie = args[i + 1]
            i += 2
        elif args[i] == "--subreddit" and i + 1 < len(args):
            subreddit = args[i + 1]
            i += 2
        elif args[i] == "--dry-run":
            dry_run = True
            i += 1
        else:
            i += 1

    # Load content
    metadata = load_run_metadata(content_dir)
    post_text = metadata.get("post_text", "")

    if not post_text:
        print(json.dumps({"error": "No content found in run directory"}))
        sys.exit(1)

    # Add UTM tracking to any URLs in the content
    campaign = Path(content_dir).name
    # Simple UTM injection for source links
    if "http" in post_text:
        import re
        urls = re.findall(r'https?://[^\s\)]+', post_text)
        for url in urls:
            tracked_url = add_utm(url, source=platform, medium="social", campaign=campaign)
            post_text = post_text.replace(url, tracked_url)

    if platform == "reddit":
        cookie_path = reddit_cookie or str(Path(__file__).parent.parent / "creds" / "reddit-cookies.json")
        if not subreddit:
            print(json.dumps({"error": "Reddit requires --subreddit <name>"}))
            sys.exit(1)
        # Extract title from first line or use a default
        title = post_text.split("\n")[0].strip().lstrip("#").strip()[:300]
        result = publish_reddit(post_text, subreddit, title, cookie_path, dry_run=dry_run)

    elif platform == "x":
        cookie_path = x_cookie or str(Path(__file__).parent.parent / "creds" / "x-cookies.json")
        image_url = metadata.get("image_url")
        result = publish_x(post_text, cookie_path, image_url=image_url, dry_run=dry_run)

    else:
        result = {"error": f"Unsupported platform: {platform}. Use 'reddit' or 'x'."}

    # Save publish record
    save_publish_record(content_dir, result)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
