#!/usr/bin/env python3
"""Fetch Figma node metadata and export images via REST API (quota-aware).

Usage:
  python3 fetch_figma_rest.py --file-key FILE_KEY --nodes "305:2,304:60"

Common options:
  --metadata-only                # Skip image API entirely
  --batch-size 3                 # Smaller batches reduce 429 risk
  --sleep-ms 1200                # Pause between image batches
  --max-retries 3                # Retries for transient errors
  --max-retry-after 60           # If 429 asks >60s, stop image pulling
  --quota-aware                  # Gracefully degrade to metadata-only on hard 429
  --force-refresh                # Ignore local image cache

If --token is not provided, reads FIGMA_TOKEN from environment.
"""

import argparse
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Dict, List, Optional, Tuple

API = "https://api.figma.com/v1"


class QuotaExceeded(RuntimeError):
    """Raised when retry-after is too large and should trigger graceful degradation."""


def parse_retry_after(err: urllib.error.HTTPError, fallback: int = 20) -> int:
    raw = err.headers.get("Retry-After") if err.headers else None
    if raw and raw.strip().isdigit():
        return int(raw.strip())
    return fallback


def chunked(items: List[str], size: int):
    for i in range(0, len(items), size):
        yield items[i : i + size]


def json_request(
    url: str,
    token: str,
    *,
    max_retries: int,
    max_retry_after: int,
    timeout: int = 60,
) -> Dict:
    attempt = 0
    while True:
        attempt += 1
        req = urllib.request.Request(url, headers={"X-Figma-Token": token})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code != 429:
                body = ""
                try:
                    body = e.read().decode("utf-8", errors="ignore")[:400]
                except Exception:
                    pass
                raise RuntimeError(f"HTTP {e.code}: {body or e.reason}") from e

            retry_after = parse_retry_after(e)
            if retry_after > max_retry_after:
                raise QuotaExceeded(
                    f"HTTP 429 Retry-After={retry_after}s exceeds cap {max_retry_after}s"
                ) from e
            if attempt >= max_retries:
                raise QuotaExceeded(
                    f"HTTP 429 after {attempt} attempts (Retry-After={retry_after}s)"
                ) from e

            print(
                f"WARN: 429 rate limit (attempt {attempt}/{max_retries}), "
                f"sleep {retry_after}s then retry"
            )
            time.sleep(retry_after)


def download_file(url: str, out_path: pathlib.Path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, out_path)


def safe_name(node_id: str) -> str:
    return node_id.replace(":", "-")


def parse_args():
    p = argparse.ArgumentParser(description="Fetch Figma nodes + images via REST API")
    p.add_argument("--file-key", required=True, help="Figma file key from URL")
    p.add_argument("--nodes", required=True, help="Comma-separated node IDs (e.g. 305:2,304:60)")
    p.add_argument("--out-dir", default="./rest-assets")
    p.add_argument("--scale", type=float, default=2)
    p.add_argument("--format", default="png")
    p.add_argument("--token", default=None)

    p.add_argument("--metadata-only", action="store_true", help="Only fetch nodes.json; skip image export")
    p.add_argument("--batch-size", type=int, default=3, help="Image API node batch size")
    p.add_argument("--sleep-ms", type=int, default=1200, help="Sleep between image batches")
    p.add_argument("--max-retries", type=int, default=3, help="Max retries per API request")
    p.add_argument(
        "--max-retry-after",
        type=int,
        default=60,
        help="If 429 Retry-After exceeds this value (seconds), stop image pull",
    )
    p.add_argument(
        "--quota-aware",
        action="store_true",
        help="On hard 429, continue with metadata-only output instead of failing",
    )
    p.add_argument("--force-refresh", action="store_true", help="Ignore local cached images")
    return p.parse_args()


def main():
    args = parse_args()

    token = args.token or os.environ.get("FIGMA_TOKEN")
    if not token:
        raise SystemExit("ERROR: FIGMA_TOKEN not set. Pass --token or set env var.")

    out = pathlib.Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    nodes = [n.strip() for n in args.nodes.split(",") if n.strip()]
    if not nodes:
        raise SystemExit("ERROR: --nodes is empty.")

    # 1) Fetch node metadata once (cheap, always useful)
    ids_csv = ",".join(nodes)
    ids_enc = urllib.parse.quote(ids_csv, safe=":,")
    nodes_url = f"{API}/files/{args.file_key}/nodes?ids={ids_enc}"
    nodes_data = json_request(
        nodes_url,
        token,
        max_retries=max(args.max_retries, 1),
        max_retry_after=max(args.max_retry_after, 1),
    )
    (out / "nodes.json").write_text(json.dumps(nodes_data, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.metadata_only:
        (out / "images.json").write_text(json.dumps({"images": {}}, ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "manifest.json").write_text(json.dumps([{"node": n, "status": "metadata-only"} for n in nodes], ensure_ascii=False, indent=2), encoding="utf-8")
        (out / "quota-status.json").write_text(
            json.dumps({"mode": "metadata-only", "reason": "--metadata-only"}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"DONE (metadata-only): {out}")
        return

    manifest = []
    needs_fetch = []
    for node_id in nodes:
        file_path = out / f"node-{safe_name(node_id)}.{args.format}"
        if file_path.exists() and not args.force_refresh:
            manifest.append({"node": node_id, "status": "cached", "file": str(file_path)})
        else:
            needs_fetch.append(node_id)

    images_all: Dict[str, Optional[str]] = {}
    quota_blocked = False
    quota_reason = ""

    # 2) Pull image URLs in small batches (expensive, prone to 429)
    sleep_sec = max(args.sleep_ms, 0) / 1000.0
    for batch in chunked(needs_fetch, max(args.batch_size, 1)):
        ids_enc_batch = urllib.parse.quote(",".join(batch), safe=":,")
        img_url = (
            f"{API}/images/{args.file_key}?ids={ids_enc_batch}"
            f"&format={urllib.parse.quote(args.format)}&scale={args.scale}"
        )
        try:
            img_data = json_request(
                img_url,
                token,
                max_retries=max(args.max_retries, 1),
                max_retry_after=max(args.max_retry_after, 1),
            )
            images_all.update(img_data.get("images", {}))
        except QuotaExceeded as e:
            quota_blocked = True
            quota_reason = str(e)
            if args.quota_aware:
                print(f"WARN: {quota_reason}; quota-aware mode enabled, stop image pulling")
                break
            raise

        if sleep_sec > 0:
            time.sleep(sleep_sec)

    # 3) Download what we got
    for node_id in needs_fetch:
        u = images_all.get(node_id)
        file_path = out / f"node-{safe_name(node_id)}.{args.format}"
        if not u:
            status = "missing"
            if quota_blocked:
                status = "quota-blocked"
            manifest.append({"node": node_id, "status": status})
            continue

        try:
            download_file(u, file_path)
            manifest.append({"node": node_id, "status": "ok", "file": str(file_path)})
        except Exception as e:
            manifest.append({"node": node_id, "status": "failed", "error": str(e)})

    (out / "images.json").write_text(json.dumps({"images": images_all}, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "quota-status.json").write_text(
        json.dumps(
            {
                "mode": "degraded-metadata" if quota_blocked else "normal",
                "quotaBlocked": quota_blocked,
                "reason": quota_reason,
                "batchSize": max(args.batch_size, 1),
                "maxRetryAfter": max(args.max_retry_after, 1),
                "quotaAware": bool(args.quota_aware),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"DONE: {out}")
    for m in manifest:
        print(f"  {m['node']}: {m['status']}")


if __name__ == "__main__":
    main()
