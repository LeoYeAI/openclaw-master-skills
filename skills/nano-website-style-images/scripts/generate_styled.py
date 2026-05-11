#!/usr/bin/env python3
"""Website Style Image Generator - CLI entry point.

Generates images matching a website's visual style using AI.

Usage:
    # From JSON config file:
    python scripts/generate_styled.py --from-json /tmp/styled_image_config.json

    # Load a saved style profile:
    python scripts/generate_styled.py --load-profile /path/to/style_profile.json \\
        --requests '[{"image_type":"hero_banner","content_description":"Spring sale"}]'

    # Dry run (print prompts without calling API):
    python scripts/generate_styled.py --from-json /tmp/styled_image_config.json --dry-run

    # Generate specific image types only:
    python scripts/generate_styled.py --from-json /tmp/styled_image_config.json --types hero_banner,social_square
"""

import argparse
import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Skill directory setup — all imports are local, no cross-skill dependencies
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_DIR, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from api_client import NanoBananaClient
from postprocess import ensure_rgb, resize_with_padding, embed_srgb_profile, optimize_file_size
from style_extractor import hex_to_rgb, validate_screenshot, compress_screenshot
from style_prompt_engine import build_styled_prompts, load_style_defaults
from utils import setup_logging, slugify, load_yaml, resolve_env_vars, get_visual_root

logger = logging.getLogger(__name__)

MAX_CONCURRENT = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate images matching a website's visual style",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("--from-json", type=str,
                        help="Path to JSON config with style_profile and requests")
    parser.add_argument("--load-profile", type=str,
                        help="Path to a saved style_profile.json (skip extraction)")
    parser.add_argument("--requests", type=str,
                        help="JSON array of image requests (use with --load-profile)")
    parser.add_argument("--output-dir", type=str,
                        help="Output directory (default: output/styled/<source-slug>)")
    parser.add_argument("--types", type=str, default="",
                        help="Comma-separated image types to generate")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print rendered prompts without calling the API")
    parser.add_argument("--skip-postprocess", action="store_true",
                        help="Skip post-processing (keep raw images)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    return parser.parse_args()


def load_config(args: argparse.Namespace) -> dict:
    """Load config from JSON file or from --load-profile + --requests."""
    if args.from_json:
        with open(args.from_json, "r", encoding="utf-8") as f:
            config = json.load(f)
        logger.info("Loaded config from %s", args.from_json)
    elif args.load_profile:
        from style_extractor import load_style_profile
        profile = load_style_profile(args.load_profile)
        requests_data = json.loads(args.requests) if args.requests else []
        config = {"style_profile": profile, "requests": requests_data}
        logger.info("Loaded profile from %s with %d requests",
                    args.load_profile, len(requests_data))
    else:
        print("Error: --from-json or --load-profile is required", file=sys.stderr)
        sys.exit(1)

    if "style_profile" not in config:
        print("Error: config must contain 'style_profile' key", file=sys.stderr)
        sys.exit(1)
    if not config.get("requests"):
        print("Error: config must contain non-empty 'requests' list", file=sys.stderr)
        sys.exit(1)

    return config


def validate_and_prepare_screenshot(config: dict) -> None:
    """Validate screenshot and compress if needed."""
    screenshot_path = config.get("style_profile", {}).get("screenshot_path", "")
    if not screenshot_path:
        return

    if not validate_screenshot(screenshot_path):
        logger.warning("Screenshot validation failed, proceeding without reference image")
        config["style_profile"]["screenshot_path"] = ""
        return

    size_mb = os.path.getsize(screenshot_path) / (1024 * 1024)
    if size_mb > 3.0:
        compressed = compress_screenshot(screenshot_path)
        config["style_profile"]["screenshot_path"] = compressed
        logger.info("Using compressed screenshot: %s", compressed)


def generate_single_styled(client: NanoBananaClient, prompt_info: dict,
                           output_dir: str) -> dict:
    """Generate a single styled image: submit, poll, download."""
    idx = prompt_info["index"]
    name = prompt_info["name"]
    prompt = prompt_info["prompt"]
    filename = prompt_info["filename"]
    ref_url = prompt_info.get("reference_image_url", "")

    logger.info("Image %d [%s]: Submitting...", idx, name)

    try:
        result = client.submit_and_wait(prompt, ref_url if ref_url else None)

        if result.status != "FINISHED" or not result.image_url:
            logger.error("Image %d [%s]: Generation failed (status: %s)", idx, name, result.status)
            return {"index": idx, "name": name, "success": False, "error": result.status}

        output_path = os.path.join(output_dir, f"{filename}.png")
        client.download_image(result.image_url, output_path)

        return {
            "index": idx, "name": name, "success": True, "raw_path": output_path,
            "width": prompt_info["width"], "height": prompt_info["height"],
            "image_type": prompt_info["image_type"],
            "prompt": prompt,
        }

    except Exception as e:
        logger.error("Image %d [%s]: Error - %s", idx, name, str(e))
        return {"index": idx, "name": name, "success": False, "error": str(e)}


def postprocess_styled(input_path: str, output_path: str,
                       target_w: int, target_h: int,
                       bg_color: tuple[int, int, int] = (255, 255, 255),
                       max_size_mb: float = 10.0,
                       jpeg_quality: int = 92) -> str:
    """Post-process a styled image: RGB conversion, resize, sRGB, optimize."""
    from PIL import Image

    image = Image.open(input_path)
    image = ensure_rgb(image)
    image = resize_with_padding(image, (target_w, target_h), bg_color)
    image = embed_srgb_profile(image)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    optimize_file_size(image, output_path, max_size_mb, jpeg_quality)

    return output_path


def save_manifest(results: list[dict], config: dict, output_dir: str) -> None:
    """Save generation manifest with results and config."""
    manifest = {
        "source_url": config.get("style_profile", {}).get("source_url", ""),
        "images": [],
    }

    for r in results:
        entry = {"index": r["index"], "name": r["name"], "success": r["success"]}
        if r["success"]:
            entry["path"] = r.get("final_path", r.get("raw_path", ""))
            entry["image_type"] = r.get("image_type", "")
            entry["dimensions"] = f"{r.get('width', 0)}x{r.get('height', 0)}"
        else:
            entry["error"] = r.get("error", "unknown")
        manifest["images"].append(entry)

    manifest_path = os.path.join(output_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    logger.info("Saved manifest to %s", manifest_path)

    profile = config.get("style_profile", {})
    if profile:
        from style_extractor import save_style_profile
        save_style_profile(profile, os.path.join(output_dir, "style_profile.json"))


def main():
    args = parse_args()
    setup_logging(args.verbose)

    config = load_config(args)
    style_profile = config["style_profile"]
    source_url = style_profile.get("source_url", "website")

    validate_and_prepare_screenshot(config)

    if args.types:
        selected_types = {t.strip() for t in args.types.split(",")}
        config["requests"] = [
            r for r in config.get("requests", [])
            if r.get("image_type") in selected_types
        ]
        if not config["requests"]:
            print(f"No requests match types: {args.types}", file=sys.stderr)
            sys.exit(1)

    # Output directory
    visual_root = get_visual_root()
    if args.output_dir:
        output_dir = args.output_dir
    else:
        slug = slugify(source_url.replace("https://", "").replace("http://", "").split("/")[0])
        output_dir = os.path.join(visual_root, "output", "styled", slug)

    os.makedirs(output_dir, exist_ok=True)

    # Build prompts
    prompts_dir = os.path.join(SKILL_DIR, "prompts")
    config_dir = os.path.join(SKILL_DIR, "config")
    all_prompts = build_styled_prompts(config, prompts_dir, config_dir)

    if not all_prompts:
        print("No valid image requests to process.")
        return

    # Dry run
    if args.dry_run:
        print(f"\n{'='*60}")
        print(f"DRY RUN - Style source: {source_url}")
        print(f"{'='*60}\n")
        for p in all_prompts:
            print(f"--- Image {p['index']}: {p['name']} ({p['width']}x{p['height']}) ---")
            print(f"Type: {p['image_type']}")
            print(f"Filename: {p['filename']}.jpg")
            print(f"Reference: {p.get('reference_image_url', 'none') or 'none'}")
            print(f"\nPrompt:\n{p['prompt']}")
            print(f"\n{'='*60}\n")
        print(f"Total: {len(all_prompts)} images would be generated.")
        return

    # Load API config — now from this skill's own config/
    api_config_path = os.path.join(SKILL_DIR, "config", "api.yaml")
    api_config = load_yaml(api_config_path)
    api_config = resolve_env_vars(api_config)
    client = NanoBananaClient(api_config)

    # Generate concurrently
    print(f"\nGenerating {len(all_prompts)} styled images (source: {source_url})")
    print(f"Output: {output_dir}\n")

    results = []
    with ThreadPoolExecutor(max_workers=min(MAX_CONCURRENT, len(all_prompts))) as executor:
        futures = {
            executor.submit(generate_single_styled, client, p, output_dir): p
            for p in all_prompts
        }
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "OK" if result["success"] else "FAILED"
            print(f"  Image {result['index']} [{result['name']}]: {status}")

    # Post-process in place (overwrite raw with final)
    if not args.skip_postprocess:
        defaults = load_style_defaults(config_dir)
        output_cfg = defaults.get("output", {})
        max_mb = output_cfg.get("max_file_size_mb", 10)
        quality = output_cfg.get("jpeg_quality", 92)

        bg_hex = style_profile.get("colors", {}).get("background", "#FFFFFF")
        bg_rgb = hex_to_rgb(bg_hex)

        for result in results:
            if result["success"]:
                raw_path = result["raw_path"]
                final_path = raw_path.replace(".png", ".jpg")
                try:
                    postprocess_styled(
                        raw_path, final_path,
                        result["width"], result["height"],
                        bg_rgb, max_mb, quality,
                    )
                    result["final_path"] = final_path
                    # Remove raw png after successful postprocess
                    if os.path.exists(raw_path) and raw_path != final_path:
                        os.remove(raw_path)
                except Exception as e:
                    logger.error("Post-processing failed for image %d: %s",
                                 result["index"], str(e))
                    result["final_path"] = raw_path

    # Summary
    results.sort(key=lambda r: r["index"])
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    success_count = 0
    for r in results:
        if r["success"]:
            success_count += 1
            path = r.get("final_path", r.get("raw_path", ""))
            print(f"  Image {r['index']} [{r['name']}]: {path}")
        else:
            print(f"  Image {r['index']} [{r['name']}]: FAILED - {r.get('error', 'unknown')}")

    print(f"\nResult: {success_count}/{len(results)} images generated successfully.")
    print(f"Output directory: {output_dir}")

    save_manifest(results, config, output_dir)


if __name__ == "__main__":
    main()
