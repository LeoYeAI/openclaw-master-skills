#!/usr/bin/env python3
"""
Tunee AI Music Generation - AI entry point.
Outputs structured JSON [{id, url, title}, ...] to stdout; url is the work share page (not a direct audio file).
Does not download to local.
"""

import argparse
import json
import sys

from utils.api_util import (
    API_GENERATE,
    format_tunee_error,
    request_tunee_api,
    resolve_access_key,
    TuneeAPIError,
)
from utils.model_util import (
    BIZ_TYPE_INSTRUMENTAL,
    BIZ_TYPE_SONG,
    fetch_models,
    get_models_by_biz_type,
    load_models_cache,
    model_supports_biz_type,
    save_models_cache,
)


def get_share_results(data: dict) -> list[dict] | None:
    """Extract [{id, url}, ...] from itemList using shareUrl (work page links)."""
    item_list = data.get("itemList")
    if not item_list or not isinstance(item_list, list):
        return None
    results: list[dict] = []
    for item in item_list:
        if not isinstance(item, dict):
            continue
        url = item.get("shareUrl")
        if not url:
            continue
        item_id = item.get("itemId") or item.get("item_id")
        if item_id:
            results.append({"id": str(item_id), "url": url})
    return results if results else None


def main():
    parser = argparse.ArgumentParser(description="Tunee AI Music Generation")
    parser.add_argument("--prompt", required=True, help="Style, mood, or scene description")
    parser.add_argument(
        "--title",
        required=True,
        help="Song or track title; must be confirmed by user or proposed by AI",
    )
    parser.add_argument("--lyrics", default="", help="Full lyrics (required for lyric mode)")
    parser.add_argument(
        "--model",
        required=True,
        help="Model ID; must match list_models.py stdout; run that script first if no list in this conversation",
    )
    parser.add_argument("--api-key", dest="api_key", default=None, help="API Key, or use env TUNEE_API_KEY")
    args = parser.parse_args()

    title = args.title.strip()
    if not title:
        print("Error: Title cannot be empty or whitespace only. Provide a valid song/track title.", file=sys.stderr)
        sys.exit(1)

    access_key = resolve_access_key(args.api_key)

    models, from_cache = load_models_cache()
    if not from_cache or not models:
        try:
            models, raw_data = fetch_models(access_key)
            save_models_cache(models)
            if not models:
                print("Error: Could not parse model list from API.", file=sys.stderr)
                print("Raw response (for debugging):", file=sys.stderr)
                print(json.dumps(raw_data, ensure_ascii=False, indent=2), file=sys.stderr)
                print("Run: python scripts/list_models.py --refresh to fetch model list", file=sys.stderr)
                sys.exit(1)
        except TuneeAPIError as e:
            print(format_tunee_error(e), file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Failed to fetch model list: {e}", file=sys.stderr)
            print("Check network or run: python scripts/list_models.py --refresh", file=sys.stderr)
            sys.exit(1)
    if not models:
        print("Error: No model list. Run: python scripts/list_models.py --refresh", file=sys.stderr)
        sys.exit(1)

    valid_ids = [m.id for m in models]
    if args.model not in valid_ids:
        print(f"Unsupported model ID: {args.model}", file=sys.stderr)
        print("Run: python scripts/list_models.py to see available models", file=sys.stderr)
        sys.exit(1)

    # Validate model capability: lyrics require Song, instrumental requires Instrumental
    required_biz_type = BIZ_TYPE_SONG if args.lyrics.strip() else BIZ_TYPE_INSTRUMENTAL
    model_info = next((m for m in models if m.id == args.model), None)
    if model_info and not model_supports_biz_type(model_info, required_biz_type):
        mode_desc = "lyrics (vocals)" if required_biz_type == BIZ_TYPE_SONG else "instrumental"
        print(f"Error: Model {args.model} does not support {mode_desc} generation", file=sys.stderr)
        supported = get_models_by_biz_type(models, required_biz_type)
        if supported:
            ids = ", ".join(m.id for m in supported)
            print(f"Models supporting {mode_desc}: {ids}", file=sys.stderr)
        print("Run: python scripts/list_models.py to see model capabilities", file=sys.stderr)
        sys.exit(1)

    payload = {
        "prompt": "",
        "style": args.prompt,
        "title": title,
        "instrumental": True if not args.lyrics else False,
        "lyric": args.lyrics,
        "action": "generate",
        "model": args.model,
        "modelKey": args.model,
        "callback_url": "https://example.com/callback",
        "source": "tunee",
        "custom": True,
        "needCover": True,
        "coverPrompt": title,
    }
    if args.lyrics:
        payload["lyrics"] = args.lyrics

    try:
        resp = request_tunee_api(API_GENERATE, access_key, payload, timeout=120)
    except TuneeAPIError as e:
        print(format_tunee_error(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Network request failed: {e}", file=sys.stderr)
        sys.exit(1)

    results = get_share_results(resp.data)
    if results:
        for r in results:
            r["title"] = title
        print(json.dumps(results, ensure_ascii=False))
        return

    print(f"Could not parse response: {json.dumps(resp.raw, ensure_ascii=False, indent=2)}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
