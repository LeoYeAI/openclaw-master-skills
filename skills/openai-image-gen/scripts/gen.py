#!/usr/bin/env python3

import argparse
import base64
import datetime as _dt
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request


def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")


def _slug(text: str, max_len: int = 60) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:max_len] or "image").strip("-")


def _default_out_dir() -> str:
    projects_tmp = os.path.expanduser("~/Projects/tmp")
    if os.path.isdir(projects_tmp):
        return os.path.join(projects_tmp, f"openai-image-gen-{_stamp()}")
    return os.path.join(os.getcwd(), "tmp", f"openai-image-gen-{_stamp()}")


def _api_url() -> str:
    base = (
        os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or "https://api.openai.com"
    ).rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/images/generations"
    return f"{base}/v1/images/generations"


def _random_prompts(count: int) -> list[str]:
    subjects = [
        "a lobster piloting a vintage scooter",
        "a raccoon librarian in a tiny art-deco library",
        "a glass whale floating above a desert",
        "a moss-covered robot tending a bonsai garden",
        "a candlelit map room with impossible staircases",
        "a retro-futurist diner on the moon at dusk",
        "a hummingbird made of stained glass",
        "a porcelain teapot city in the clouds",
        "a midnight train station built inside a giant clock",
        "a tiny submarine exploring a glowing kelp forest",
        "a baroque observatory with brass telescopes and fog",
        "a koi pond shaped like a circuit board",
    ]
    styles = [
        "ultra-detailed studio photo",
        "35mm film still",
        "risograph poster",
        "oil painting on linen",
        "watercolor with ink linework",
        "isometric diorama",
        "mid-century editorial illustration",
        "high-end product shot",
    ]
    lighting = [
        "softbox lighting",
        "golden hour",
        "neon rim light",
        "overcast diffuse light",
        "candlelight with deep shadows",
        "dramatic chiaroscuro",
    ]
    palettes = [
        "copper + teal + cream",
        "cobalt + vermilion + bone",
        "sage + sand + charcoal",
        "magenta + midnight blue + silver",
    ]

    random.shuffle(subjects)
    prompts: list[str] = []
    for i in range(count):
        subj = subjects[i % len(subjects)]
        prompts.append(
            f"{random.choice(styles)} of {subj}. "
            f"Lighting: {random.choice(lighting)}. "
            f"Palette: {random.choice(palettes)}. "
            "Crisp, no text, no watermark."
        )
    return prompts


def _post_json(url: str, api_key: str, payload: dict, timeout_s: int) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            data = json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            raise SystemExit(f"OpenAI HTTP {e.code}: {raw[:300]!r}")
        raise SystemExit(f"OpenAI HTTP {e.code}: {json.dumps(data, indent=2)[:1200]}")
    except Exception as e:
        raise SystemExit(f"request failed: {e}")

    try:
        return json.loads(raw)
    except Exception:
        raise SystemExit(f"invalid JSON response: {raw[:300]!r}")


def _write_index(out_dir: str, items: list[dict]) -> None:
    html = [
        "<!doctype html>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>openai-image-gen</title>",
        "<style>",
        "body{font-family:ui-sans-serif,system-ui;margin:24px;max-width:1060px}",
        ".card{display:grid;grid-template-columns:220px 1fr;gap:16px;align-items:start;margin:18px 0}",
        "img{width:220px;height:220px;object-fit:cover;border-radius:14px;box-shadow:0 14px 38px rgba(0,0,0,.14)}",
        "pre{white-space:pre-wrap;margin:0;background:#111;color:#eee;padding:12px 14px;border-radius:14px;line-height:1.35}",
        "</style>",
        "<h1>openai-image-gen</h1>",
    ]
    for it in items:
        html.append("<div class='card'>")
        html.append(f"<a href='{it['file']}'><img src='{it['file']}'></a>")
        html.append(f"<pre>{it['prompt']}</pre>")
        html.append("</div>")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(html))


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="openai-image-gen",
        description="Generate a batch of images via OpenAI Images API (random prompts by default).",
    )
    p.add_argument("--count", type=int, default=8)
    p.add_argument("--model", default="gpt-image-1.5")
    p.add_argument("--size", default="1024x1024")
    p.add_argument("--quality", default="high")
    p.add_argument("--timeout", type=int, default=180, help="per-request timeout (seconds)")
    p.add_argument("--sleep", type=float, default=0.2, help="pause between requests (seconds)")
    p.add_argument("--out-dir", default=None)
    p.add_argument("--api-key", default=None)
    p.add_argument("--prompt", action="append", default=None, help="repeatable; overrides random prompts")
    p.add_argument("--dry-run", action="store_true", help="print prompts + exit (no API calls)")
    args = p.parse_args(argv)

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("missing OPENAI_API_KEY (or --api-key)", file=sys.stderr)
        return 2

    out_dir = args.out_dir or _default_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    prompts = args.prompt if args.prompt else _random_prompts(args.count)
    if args.dry_run:
        for i, pr in enumerate(prompts, 1):
            print(f"{i:02d} {pr}")
        print(f"out_dir={out_dir}")
        return 0

    url = _api_url()
    items: list[dict] = []

    for i, prompt in enumerate(prompts, 1):
        payload = {
            "model": args.model,
            "prompt": prompt,
            "size": args.size,
            "quality": args.quality,
            "n": 1,
            "response_format": "b64_json",
        }
        data = _post_json(url=url, api_key=api_key, payload=payload, timeout_s=args.timeout)
        b64 = (data.get("data") or [{}])[0].get("b64_json")
        if not b64:
            raise SystemExit(f"unexpected response: {json.dumps(data, indent=2)[:1200]}")

        png = base64.b64decode(b64)
        filename = f"{i:02d}-{_slug(prompt)}.png"
        path = os.path.join(out_dir, filename)
        with open(path, "wb") as f:
            f.write(png)

        items.append(
            {
                "file": filename,
                "prompt": prompt,
                "model": args.model,
                "size": args.size,
                "quality": args.quality,
            }
        )
        print(f"wrote {filename}")
        if args.sleep > 0:
            time.sleep(args.sleep)

    with open(os.path.join(out_dir, "prompts.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    _write_index(out_dir, items)
    print(f"out_dir={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
