#!/usr/bin/env python3
"""Fetch content via Supadata API (transcript, web scrape, metadata).

Usage:
    python3 supadata_fetch.py transcript <url> [--lang zh] [--text]
    python3 supadata_fetch.py web <url>
    python3 supadata_fetch.py metadata <url>

Environment:
    SUPADATA_API_KEY  - Required. API key for authentication.

Output: JSON to stdout.
"""

import sys
import json
import os
import time
import urllib.request
import urllib.error
import urllib.parse

BASE_URL = "https://api.supadata.ai/v1"
POLL_INTERVAL = 2       # seconds between job status checks
POLL_TIMEOUT = 300      # max wait for async jobs (5 minutes)
MAX_RETRIES = 2         # retries on transient errors
RETRY_DELAY = 1         # initial delay between retries (doubles each retry)


def get_api_key():
    key = os.environ.get("SUPADATA_API_KEY", "").strip()
    if not key:
        print("Error: SUPADATA_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(path, params=None):
    """Make a GET request to the Supadata API. Returns parsed JSON."""
    url = BASE_URL + path
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "x-api-key": get_api_key(),
        "Accept": "application/json",
        "User-Agent": "supadata-fetch/1.0",
    }
    req = urllib.request.Request(url, headers=headers)

    last_err = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                status = resp.status
                if status == 202:
                    # async job — return raw data for polling
                    return {"_async": True, "_status": 202, **json.loads(body)}
                return json.loads(body)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            # don't retry client errors (4xx) except 429
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", RETRY_DELAY * (2 ** attempt)))
                print(f"Rate limited, waiting {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                last_err = e
                continue
            if 400 <= e.code < 500:
                print(f"API error {e.code}: {body}", file=sys.stderr)
                sys.exit(1)
            # server errors — retry
            last_err = e
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * (2 ** attempt)
                print(f"Server error {e.code}, retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
        except (urllib.error.URLError, OSError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * (2 ** attempt)
                print(f"Network error, retrying in {delay}s: {e}", file=sys.stderr)
                time.sleep(delay)

    print(f"Request failed after {MAX_RETRIES + 1} attempts: {last_err}", file=sys.stderr)
    sys.exit(1)


def poll_job(job_id):
    """Poll an async transcript job until completion or timeout."""
    print(f"Async job {job_id}, polling...", file=sys.stderr)
    start = time.time()
    while time.time() - start < POLL_TIMEOUT:
        time.sleep(POLL_INTERVAL)
        result = api_request(f"/transcript/{job_id}")
        status = result.get("status")
        if status == "completed":
            return result
        if status == "failed":
            error = result.get("error", "unknown error")
            print(f"Job failed: {error}", file=sys.stderr)
            sys.exit(1)
        elapsed = int(time.time() - start)
        print(f"  status={status}, elapsed={elapsed}s", file=sys.stderr)

    print(f"Timeout: job {job_id} did not complete within {POLL_TIMEOUT}s", file=sys.stderr)
    sys.exit(1)


def cmd_transcript(args):
    """Fetch transcript for a video URL."""
    if not args:
        print("Error: URL required for transcript command", file=sys.stderr)
        sys.exit(1)

    url = args[0]
    params = {"url": url}

    if "--lang" in args:
        idx = args.index("--lang")
        if idx + 1 < len(args):
            params["lang"] = args[idx + 1]

    if "--text" in args:
        params["text"] = "true"

    result = api_request("/transcript", params)

    # handle async job
    if result.get("_async"):
        job_id = result.get("jobId")
        if not job_id:
            print("Error: got 202 but no jobId in response", file=sys.stderr)
            sys.exit(1)
        result = poll_job(job_id)
        result.pop("_async", None)
        result.pop("_status", None)

    result.pop("_async", None)
    result.pop("_status", None)
    return result


def cmd_web(args):
    """Scrape a web page and return markdown content."""
    if not args:
        print("Error: URL required for web command", file=sys.stderr)
        sys.exit(1)

    return api_request("/web/scrape", {"url": args[0]})


def cmd_metadata(args):
    """Fetch social media metadata."""
    if not args:
        print("Error: URL required for metadata command", file=sys.stderr)
        sys.exit(1)

    return api_request("/metadata", {"url": args[0]})


COMMANDS = {
    "transcript": cmd_transcript,
    "web": cmd_web,
    "metadata": cmd_metadata,
}


def main():
    if len(sys.argv) < 3:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]
    if command not in COMMANDS:
        print(f"Error: unknown command '{command}'. Use: {', '.join(COMMANDS)}", file=sys.stderr)
        sys.exit(1)

    result = COMMANDS[command](sys.argv[2:])
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    print()  # trailing newline


if __name__ == "__main__":
    main()
