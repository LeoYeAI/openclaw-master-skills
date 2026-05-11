"""
Content Claw - Source Extractor

Dispatches URL to the appropriate extractor based on URL pattern.
Uses Playwright for browser-based extraction (bypasses bot detection).
Returns extracted text to stdout as JSON.

Usage:
    uv run extract.py <url>
"""

import json
import sys
from urllib.parse import urlparse


def get_page_html(url: str, wait_for: str | None = None) -> str:
    """Fetch a page's HTML using Playwright with stealth settings."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = context.new_page()
        # Hide webdriver property
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        if wait_for:
            page.wait_for_selector(wait_for, timeout=10000)
        else:
            page.wait_for_timeout(3000)
        html = page.content()
        context.close()
        browser.close()
    return html


def extract_web(url: str) -> dict:
    """Generic web page extractor. Uses Playwright + readabilipy for clean text."""
    from readabilipy import simple_json_from_html_string

    html = get_page_html(url)
    article = simple_json_from_html_string(html, use_readability=True)

    text_content = article.get("plain_text", [])
    if isinstance(text_content, list):
        text = "\n".join(
            p.get("text", "") if isinstance(p, dict) else str(p) for p in text_content
        )
    else:
        text = str(text_content)

    return {
        "type": "web",
        "url": url,
        "title": article.get("title", ""),
        "text": text,
        "word_count": len(text.split()),
    }


def extract_pdf(url: str) -> dict:
    """PDF extractor. Downloads PDF via httpx and extracts text with pymupdf."""
    import tempfile
    import httpx
    import pymupdf

    resp = httpx.get(
        url,
        follow_redirects=True,
        timeout=60,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        },
    )
    resp.raise_for_status()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(resp.content)
        tmp_path = f.name

    doc = pymupdf.open(tmp_path)
    pages = []
    for pg in doc:
        pages.append(pg.get_text())
    doc.close()

    text = "\n\n".join(pages)

    return {
        "type": "pdf",
        "url": url,
        "title": "",
        "text": text,
        "word_count": len(text.split()),
        "page_count": len(pages),
    }


def extract_reddit(url: str) -> dict:
    """Reddit post extractor. Renders with Playwright, extracts with readability."""
    from readabilipy import simple_json_from_html_string

    # Render the page with a real browser
    html = get_page_html(url, wait_for=None)
    article = simple_json_from_html_string(html, use_readability=True)

    text_content = article.get("plain_text", [])
    if isinstance(text_content, list):
        text = "\n".join(
            p.get("text", "") if isinstance(p, dict) else str(p) for p in text_content
        )
    else:
        text = str(text_content)

    # Try to extract subreddit from URL
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    subreddit = parts[1] if len(parts) >= 2 and parts[0] == "r" else ""

    return {
        "type": "reddit",
        "url": url,
        "title": article.get("title", ""),
        "text": text,
        "word_count": len(text.split()),
        "subreddit": subreddit,
    }


def extract_twitter(url: str) -> dict:
    """Twitter/X post extractor. Uses Playwright to render the tweet."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)

        tweet_text = ""
        author = ""

        try:
            tweet_el = page.query_selector("article div[data-testid='tweetText']")
            if tweet_el:
                tweet_text = tweet_el.inner_text()
        except Exception:
            pass

        try:
            author_el = page.query_selector("article a[role='link'] span")
            if author_el:
                author = author_el.inner_text()
        except Exception:
            pass

        browser.close()

    text = f"Author: {author}\n\n{tweet_text}"

    return {
        "type": "twitter",
        "url": url,
        "title": f"Tweet by {author}",
        "text": text,
        "word_count": len(text.split()),
    }


def extract_github(url: str) -> dict:
    """GitHub repo/PR extractor. Uses GitHub API (public, no auth needed for public repos)."""
    import httpx

    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    headers = {"Accept": "application/vnd.github.v3+json"}

    if len(path_parts) >= 2:
        owner, repo = path_parts[0], path_parts[1]

        if len(path_parts) >= 4 and path_parts[2] == "pull":
            pr_num = path_parts[3]
            api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_num}"
            resp = httpx.get(api_url, headers=headers, timeout=30)
            resp.raise_for_status()
            pr = resp.json()
            text = f"PR: {pr['title']}\n\n{pr.get('body', '')}"
            title = pr["title"]
        else:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
            resp = httpx.get(
                api_url,
                headers={**headers, "Accept": "application/vnd.github.raw+json"},
                timeout=30,
            )
            resp.raise_for_status()
            text = resp.text
            title = f"{owner}/{repo}"
    else:
        raise ValueError(f"Cannot parse GitHub URL: {url}")

    return {
        "type": "github",
        "url": url,
        "title": title,
        "text": text,
        "word_count": len(text.split()),
    }


def detect_type(url: str) -> str:
    """Detect source type from URL pattern."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if "reddit.com" in domain or "redd.it" in domain:
        return "reddit"
    if "github.com" in domain:
        return "github"
    if "arxiv.org" in domain and "/pdf/" in parsed.path:
        return "pdf"
    if "arxiv.org" in domain:
        return "web"
    if parsed.path.lower().endswith(".pdf"):
        return "pdf"
    if "youtube.com" in domain or "youtu.be" in domain:
        return "youtube"
    if "x.com" in domain or "twitter.com" in domain:
        return "twitter"

    return "web"


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: extract.py <url>"}), file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    source_type = detect_type(url)

    extractors = {
        "web": extract_web,
        "pdf": extract_pdf,
        "reddit": extract_reddit,
        "twitter": extract_twitter,
        "github": extract_github,
    }

    extractor = extractors.get(source_type)
    if not extractor:
        print(
            json.dumps(
                {
                    "error": f"No extractor for source type: {source_type}. Supported: {list(extractors.keys())}",
                    "url": url,
                    "detected_type": source_type,
                }
            )
        )
        sys.exit(1)

    try:
        result = extractor(url)
        if len(result.get("text", "")) > 50000:
            result["text"] = result["text"][:50000] + "\n\n[... truncated]"
            result["truncated"] = True
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(
            json.dumps(
                {
                    "error": str(e),
                    "url": url,
                    "detected_type": source_type,
                }
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
