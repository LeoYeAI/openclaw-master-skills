#!/usr/bin/env python3
"""
Tunee AI Music Generation - Fetch model list.
Queries supported models and capabilities (lyrics, duration range, etc.).
Agent reads available models from stdout; reuse cached output in same session per SKILL; --refresh forces fresh API fetch.
"""

import json
import sys

import yaml

from utils import api_util
from utils import model_util


def _models_for_output(models: list[model_util.Model]) -> list[dict]:
    """Convert to compact structure for AI selection. Includes supports summary for vocals/instrumental filtering."""
    out = []
    for m in models:
        if not m.id or not m.id.strip():
            continue  # Skip invalid model
        capabilities = [c.to_dict() for c in m.capabilities]
        out.append({
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "capabilities": capabilities,
        })
    return out


def _print_models_yaml(models: list[model_util.Model]) -> None:
    """Print model list to stdout in YAML format."""
    data = {"models": _models_for_output(models)}
    print(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False))


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Tunee AI Music - List available models")
    parser.add_argument("--api-key", dest="api_key", default=None, help="API Key, or use env TUNEE_API_KEY")
    parser.add_argument("--refresh", action="store_true", help="Force fresh model list from API")
    args = parser.parse_args()

    access_key = api_util.resolve_access_key(args.api_key)

    if not args.refresh:
        models, from_cache = model_util.load_models_cache()
        if from_cache and models:
            _print_models_yaml(models)
            return

    try:
        models, raw_data = model_util.fetch_models(access_key)
    except api_util.TuneeAPIError as e:
        print(api_util.format_tunee_error(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Network request failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not models:
        print("Error: Could not parse model list from API. Retry later or contact platform support.", file=sys.stderr)
        print("Raw response (for debugging):", file=sys.stderr)
        print(json.dumps(raw_data, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    model_util.save_models_cache(models)
    _print_models_yaml(models)


if __name__ == "__main__":
    main()
