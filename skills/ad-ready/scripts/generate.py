#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx>=0.25.0",
#     "beautifulsoup4>=4.12.0",
# ]
# ///
"""
Ad-Ready: Generate advertising images from product URLs using brand-aware AI pipeline.

IMPORTANT inputs:
  --product-image  Product photo (download from product page) — REQUIRED
  --logo           Brand logo — OPTIONAL (use only if found easily in good quality)
  --reference      Reference ad to clone — OPTIONAL (only when explicitly requested)
  --brand-profile  Brand profile (NEVER leave as "No Brand" if brand is known)
  --prompt-profile Funnel stage (match to campaign objective)

Note: logo and reference use server-side bypass. Empty string = not used.

Usage:
    uv run generate.py --product-url "https://shop.example.com/product" \
        --product-image product.jpg --logo logo.png \
        --brand-profile Nike --prompt-profile Master_prompt_05_Conversion \
        --output ad.png

    # Auto-fetch product image and logo:
    uv run generate.py --product-url "https://shop.example.com/product" \
        --brand-profile Nike --prompt-profile Master_prompt_05_Conversion \
        --auto-fetch --output ad.png
"""

import argparse
import httpx
import os
import sys
import time
import json
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

DEPLOYMENT_ID = "e37318e6-ef21-4aab-bc90-8fb29624cd15"
API_BASE = "https://api.comfydeploy.com/api"

# Dynamic brand profiles from catalog
BRANDS_DIR = Path.home() / "clawd" / "ad-ready" / "configs" / "Brands"

PROMPT_PROFILES = [
    "Master_prompt_01_Awareness",
    "Master_prompt_02_Interest",
    "Master_prompt_03_Consideration",
    "Master_prompt_04_Evaluation",
    "Master_prompt_05_Conversion",
    "Master_prompt_06_Retention",
    "Master_prompt_07_Loyalty",
    "Master_prompt_08_Advocacy",
    "Master_prompt_09_Morfeo_Creative"
]

# Stage selection guide — use this to choose the right profile for each request
# ┌─────────────────────┬──────────────────────────────────────────────────────────────────┐
# │ Stage               │ Best For                                                         │
# ├─────────────────────┼──────────────────────────────────────────────────────────────────┤
# │ 01_Awareness        │ Brand discovery, first impressions. Dynamic scenes, world-build  │
# │                     │ -ing, high-concept creativity. Scroll-stopping visuals.           │
# │ 02_Interest         │ Sustained attention, introduce value. Clear visual idea with a   │
# │                     │ micro-world hinting at use-case. "Learn More" CTAs.              │
# │ 03_Consideration    │ Informed evaluation. Communicate WHAT product does, key          │
# │                     │ differentiator, proof cues. Structured and informative.           │
# │ 04_Evaluation       │ Validate purchase decision. Trust anchors, proof, authority.     │
# │                     │ Reviews, certifications, quality signals.                         │
# │ 05_Conversion       │ Trigger purchase action. Clean, minimal, CTA-dominant.           │
# │                     │ ⚠️ WARNING: Produces minimal/sterile visuals by design.           │
# │ 06_Retention        │ Post-purchase confidence. "You made the right choice."           │
# │                     │ Gentle guidance, onboarding feel.                                │
# │ 07_Loyalty          │ Emotional bond over time. Lifestyle, identity, belonging.        │
# │                     │ Editorial and aspirational.                                       │
# │ 08_Advocacy         │ Turn customers into ambassadors. Share-worthy, community,        │
# │                     │ signal belonging. Organic, social-native feel.                    │
# │ 09_Morfeo_Creative  │ 🎨 CREATIVE MODE. Cinematic, narrative-rich, slightly surreal.   │
# │                     │ Best for visually striking ads. NEVER white backgrounds.          │
# │                     │ Think: movie stills + magical realism + high fashion.             │
# └─────────────────────┴──────────────────────────────────────────────────────────────────┘
#
# DEFAULT SELECTION LOGIC:
# - If user says "ad" or "anuncio" without specifying → use 09_Morfeo_Creative
# - If user asks for "awareness" / "brand discovery" → use 01_Awareness
# - If user asks for "conversion" / "compra" / "CTA" → use 05_Conversion
# - If user asks for creative/original/surreal → use 09_Morfeo_Creative
# - If user asks for "lifestyle" / "editorial" → use 07_Loyalty
# - When in doubt, prefer 09_Morfeo_Creative over 05_Conversion

ASPECT_RATIOS = ["1:1", "4:5", "5:4", "9:16", "16:9", "2:3", "3:2", "3:4", "4:3", "21:9"]


def get_api_key(provided_key: str | None) -> str | None:
    if provided_key:
        return provided_key
    return os.environ.get("COMFY_DEPLOY_API_KEY")


def get_available_brands() -> list[str]:
    """Scan the brands catalog directory for available profiles."""
    brands = ["No Brand"]
    if BRANDS_DIR.exists():
        for f in sorted(BRANDS_DIR.iterdir()):
            if f.suffix == ".json" and not f.name.startswith(("_", ".")):
                brands.append(f.stem)
    return brands


def upload_file(client: httpx.Client, api_key: str, file_path: str) -> str:
    """Upload a local file to ComfyDeploy and return the URL."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()
    if ext in [".jpg", ".jpeg"]:
        content_type = "image/jpeg"
    elif ext == ".webp":
        content_type = "image/webp"
    else:
        content_type = "image/png"

    with open(path, "rb") as f:
        files = {"file": (path.name, f, content_type)}
        response = client.post(
            f"{API_BASE}/file/upload",
            headers={"Authorization": f"Bearer {api_key}"},
            files=files
        )

    if response.status_code != 200:
        raise Exception(f"Upload failed ({response.status_code}): {response.text}")

    data = response.json()
    url = data.get("file_url") or data.get("url") or data.get("download_url")
    if not url:
        raise Exception(f"No URL in upload response: {data}")

    print(f"  ✓ Uploaded: {path.name} → {url[:80]}...", flush=True)
    return url


def resolve_image(client: httpx.Client, api_key: str, value: str) -> str:
    """If value is a local path, upload it. If URL, return as-is."""
    if value.startswith("http://") or value.startswith("https://"):
        return value
    return upload_file(client, api_key, value)


def download_to_file(client: httpx.Client, url: str, dest: Path) -> bool:
    """Download a URL to a local file. Returns True on success."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "image/*,*/*;q=0.8",
        }
        response = client.get(url, headers=headers, follow_redirects=True, timeout=20.0)
        if response.status_code == 200 and len(response.content) > 1000:
            content_type = response.headers.get("content-type", "")
            if "image" in content_type or "octet" in content_type or len(response.content) > 5000:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(response.content)
                size_kb = len(response.content) / 1024
                print(f"  ✓ Downloaded: {dest.name} ({size_kb:.0f}KB)", flush=True)
                return True
    except Exception as e:
        print(f"  ✗ Download failed: {e}", flush=True)
    return False


def fetch_product_image(client: httpx.Client, product_url: str, dest: Path) -> bool:
    """Try to find and download the main product image from a product page."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  ⚠ beautifulsoup4 not available for product image extraction", flush=True)
        return False

    print("  Fetching product page for main image...", flush=True)
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,*/*",
        }
        response = client.get(product_url, headers=headers, follow_redirects=True, timeout=20.0)
        if response.status_code != 200:
            print(f"  ✗ Could not fetch product page ({response.status_code})", flush=True)
            return False

        soup = BeautifulSoup(response.text, "html.parser")

        # Strategy 1: og:image meta tag (most reliable)
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"):
            img_url = urljoin(product_url, og_img["content"])
            print(f"  Found og:image: {img_url[:80]}...", flush=True)
            if download_to_file(client, img_url, dest):
                return True

        # Strategy 2: Large images in the page
        images = soup.find_all("img")
        candidates = []
        for img in images:
            src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
            if not src:
                continue
            src = urljoin(product_url, src)
            # Skip tiny images, icons, tracking pixels
            width = img.get("width", "0")
            height = img.get("height", "0")
            try:
                w = int(str(width).replace("px", ""))
                h = int(str(height).replace("px", ""))
            except ValueError:
                w, h = 0, 0
            # Prefer images with product-related attributes
            alt = (img.get("alt") or "").lower()
            classes = " ".join(img.get("class", [])).lower()
            is_product = any(kw in alt + classes for kw in ["product", "hero", "main", "gallery", "zoom"])
            candidates.append((src, w * h if w and h else 0, is_product))

        # Sort: product-related first, then by size
        candidates.sort(key=lambda x: (x[2], x[1]), reverse=True)

        for src, _, _ in candidates[:5]:
            if download_to_file(client, src, dest):
                return True

    except Exception as e:
        print(f"  ✗ Error fetching product image: {e}", flush=True)

    return False


def fetch_brand_logo(client: httpx.Client, brand_name: str, dest: Path) -> bool:
    """Try to find and download a brand logo."""
    if not brand_name or brand_name == "No Brand":
        return False

    print(f"  Searching for {brand_name} logo...", flush=True)

    # Try common logo CDNs and patterns
    clean_name = brand_name.lower().replace("_", "").replace(" ", "").replace("-", "")
    logo_attempts = [
        f"https://logo.clearbit.com/{clean_name}.com",
        f"https://logo.clearbit.com/{clean_name}.com.ar",
        f"https://img.logo.dev/{clean_name}.com?token=pk_X-1ZO13GSgeOoUrIuJ6GMQ",
    ]

    for url in logo_attempts:
        if download_to_file(client, url, dest):
            return True

    print(f"  ⚠ Could not auto-download logo for '{brand_name}'", flush=True)
    print(f"    → Please provide --logo manually (download from brand website)", flush=True)
    return False


def queue_run(client: httpx.Client, api_key: str, inputs: dict) -> str:
    response = client.post(
        f"{API_BASE}/run/deployment/queue",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "deployment_id": DEPLOYMENT_ID,
            "inputs": inputs
        }
    )
    if response.status_code != 200:
        raise Exception(f"Queue failed ({response.status_code}): {response.text}")
    data = response.json()
    run_id = data.get("run_id")
    print(f"  ✓ Queued run: {run_id}", flush=True)
    return run_id


def poll_run(client: httpx.Client, api_key: str, run_id: str, timeout: int = 600) -> dict:
    start = time.time()
    dots = 0
    while time.time() - start < timeout:
        response = client.get(
            f"{API_BASE}/run/{run_id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        if response.status_code != 200:
            raise Exception(f"Poll failed: {response.text}")
        data = response.json()
        status = data.get("status")
        if status == "success":
            elapsed = time.time() - start
            print(f"\n  ✓ Generation complete ({elapsed:.0f}s)", flush=True)
            return data
        elif status in ["failed", "error"]:
            raise Exception(f"Run failed: {json.dumps(data, indent=2)[:1000]}")
        dots += 1
        if dots % 6 == 0:
            elapsed = time.time() - start
            print(f"  ⏳ {status}... ({elapsed:.0f}s)", flush=True)
        time.sleep(5)
    raise TimeoutError(f"Timed out after {timeout}s")


def find_output_images(result: dict) -> list[str]:
    """Extract image URLs from run outputs."""
    urls = []
    for output in result.get("outputs", []):
        images = output.get("data", {}).get("images", [])
        for img in images:
            url = img.get("url")
            if url and not url.endswith("_debug.png"):
                urls.append(url)
    return urls


def download_image(client: httpx.Client, url: str, path: str):
    response = client.get(url, timeout=30.0)
    if response.status_code != 200:
        raise Exception(f"Download failed: {response.text}")
    with open(path, "wb") as f:
        f.write(response.content)
    size_mb = len(response.content) / (1024 * 1024)
    print(f"  ✓ Saved: {path} ({size_mb:.1f}MB)", flush=True)


def validate_inputs(args) -> list[str]:
    """Validate inputs and return list of warnings."""
    warnings = []

    if args.brand_profile == "No Brand":
        warnings.append("⚠️  brand-profile is 'No Brand'. If a brand is known, always specify it!")

    if not args.product_image and not args.auto_fetch:
        warnings.append("⚠️  No --product-image provided. Scraping is fragile — provide one for best results.")

    return warnings


def main():
    parser = argparse.ArgumentParser(
        description="Ad-Ready: AI advertising image generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full generation with all inputs:
  uv run generate.py --product-url "https://..." --product-image product.jpg \\
    --logo logo.png --brand-profile Nike \\
    --prompt-profile Master_prompt_05_Conversion --output ad.png

  # Auto-fetch product image and logo:
  uv run generate.py --product-url "https://..." --brand-profile Nike \\
    --prompt-profile Master_prompt_05_Conversion --auto-fetch --output ad.png
"""
    )

    parser.add_argument("--product-url", required=True, help="Product page URL to scrape")
    parser.add_argument("--product-image", help="Product image (local path or URL). RECOMMENDED.")
    parser.add_argument("--model", "-m", help="Model/talent face image (local path or URL)")
    parser.add_argument("--reference", help="Reference ad to clone (local path or URL). OPTIONAL — only when explicitly requested.")
    parser.add_argument("--logo", help="Brand logo image (local path or URL). OPTIONAL — use if found easily in good quality.")
    parser.add_argument("--brand-profile", default="No Brand",
                       help="Brand profile name from catalog. Use brand-analyzer to create new ones.")
    parser.add_argument("--prompt-profile", default="Master_prompt_09_Morfeo_Creative",
                       help="Funnel stage prompt profile (default: Morfeo Creative)")
    parser.add_argument("--aspect-ratio", default="4:5", choices=ASPECT_RATIOS,
                       help="Output aspect ratio (default: 4:5)")
    parser.add_argument("--language", default="es",
                       help="Output language for ad copy/CTA (default: es)")
    parser.add_argument("--creative-brief", default="",
                       help="Creative direction text: describe scene, mood, style concept")
    parser.add_argument("--output", "-o", required=True, help="Output filename")
    parser.add_argument("--api-key", help="ComfyDeploy API key (or set COMFY_DEPLOY_API_KEY)")
    parser.add_argument("--auto-fetch", action="store_true",
                       help="Auto-download product image and brand logo if not provided")
    parser.add_argument("--list-brands", action="store_true",
                       help="List available brand profiles and exit")

    args = parser.parse_args()

    # List brands mode
    if args.list_brands:
        brands = get_available_brands()
        print(f"Available brand profiles ({len(brands)}):")
        for b in brands:
            print(f"  {b}")
        sys.exit(0)

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Error: No API key. Set COMFY_DEPLOY_API_KEY or use --api-key", file=sys.stderr)
        sys.exit(1)

    # Validate brand profile exists
    available_brands = get_available_brands()
    if args.brand_profile not in available_brands:
        print(f"Error: Brand profile '{args.brand_profile}' not found in catalog.", file=sys.stderr)
        print(f"Available brands: {', '.join(available_brands[:10])}...", file=sys.stderr)
        print(f"Use brand-analyzer skill to create it first.", file=sys.stderr)
        sys.exit(1)

    # Validate prompt profile
    if args.prompt_profile not in PROMPT_PROFILES:
        print(f"Error: Invalid prompt profile '{args.prompt_profile}'", file=sys.stderr)
        print(f"Valid profiles: {', '.join(PROMPT_PROFILES)}", file=sys.stderr)
        sys.exit(1)

    # Show warnings
    warnings = validate_inputs(args)
    if warnings:
        print("\n⚠️  Input warnings:", flush=True)
        for w in warnings:
            print(f"  {w}", flush=True)
        print("", flush=True)

    with httpx.Client(timeout=60.0) as client:
        print("═══════════════════════════════════════════", flush=True)
        print("  Ad-Ready: Advertising Image Generator", flush=True)
        print("═══════════════════════════════════════════", flush=True)

        producto_url = ""
        model_url = ""
        referencia_url = ""
        marca_url = ""

        # --- Auto-fetch if enabled ---
        if args.auto_fetch:
            print("\n📥 Auto-fetching assets...", flush=True)
            tmp = Path("/tmp/ad-ready")
            tmp.mkdir(exist_ok=True)

            # Product image
            if not args.product_image:
                product_dest = tmp / "product.jpg"
                if fetch_product_image(client, args.product_url, product_dest):
                    args.product_image = str(product_dest)

            # Brand logo
            if not args.logo and args.brand_profile != "No Brand":
                logo_dest = tmp / "logo.png"
                if fetch_brand_logo(client, args.brand_profile, logo_dest):
                    args.logo = str(logo_dest)

        # --- Resolve and upload images ---
        print("\n📤 Uploading assets to ComfyDeploy...", flush=True)

        if args.product_image:
            producto_url = resolve_image(client, api_key, args.product_image)
        else:
            print("  ⚠ No product image — relying on scraper (less reliable)", flush=True)

        if args.model:
            model_url = resolve_image(client, api_key, args.model)

        if args.reference:
            referencia_url = resolve_image(client, api_key, args.reference)

        if args.logo:
            marca_url = resolve_image(client, api_key, args.logo)

        inputs = {
            "producto": producto_url,
            "product_url": args.product_url,
            "model": model_url,
            "referencia": referencia_url,
            "marca": marca_url,
            "brand_profile": args.brand_profile,
            "prompt_profile": args.prompt_profile,
            "aspect_ratio": args.aspect_ratio,
        }

        # Only include language and creative_brief when explicitly provided (on-demand)
        if args.language and args.language != "es":
            inputs["language"] = args.language
        if args.creative_brief:
            inputs["creative_brief"] = args.creative_brief

        print(f"\n🎯 Generation Settings:", flush=True)
        print(f"  Product URL:  {args.product_url[:70]}{'...' if len(args.product_url) > 70 else ''}", flush=True)
        print(f"  Brand:        {args.brand_profile}", flush=True)
        print(f"  Funnel Stage: {args.prompt_profile.split('_')[-1]}", flush=True)
        print(f"  Aspect Ratio: {args.aspect_ratio}", flush=True)
        print(f"  Language:     {args.language}", flush=True)
        if args.creative_brief:
            print(f"  Brief:        {args.creative_brief[:60]}{'...' if len(args.creative_brief) > 60 else ''}", flush=True)
        print(f"  Product Img:  {'✓' if producto_url else '✗ (none)'}", flush=True)
        print(f"  Logo:         {'✓' if marca_url else '— (skipped)'}", flush=True)
        print(f"  Reference:    {'✓' if referencia_url else '— (off)'}", flush=True)
        print(f"  Model:        {'✓' if model_url else '— (no talent)'}", flush=True)

        # Check for critical missing inputs
        missing_critical = []
        if not producto_url:
            missing_critical.append("product image")
        if args.brand_profile == "No Brand":
            missing_critical.append("brand profile")

        if missing_critical:
            print(f"\n⚠️  Missing: {', '.join(missing_critical)}", flush=True)
            print(f"  Proceeding anyway, but output quality may be lower.", flush=True)

        print(f"\n🚀 Queuing generation...", flush=True)
        run_id = queue_run(client, api_key, inputs)

        print(f"⏳ Waiting for completion...", flush=True)
        result = poll_run(client, api_key, run_id, timeout=600)

        image_urls = find_output_images(result)
        if not image_urls:
            print("\n❌ No output images found!", file=sys.stderr)
            outputs = result.get("outputs", [])
            if outputs:
                print(f"Raw outputs: {json.dumps(outputs, indent=2)[:2000]}", file=sys.stderr)
            sys.exit(1)

        print(f"\n📸 Found {len(image_urls)} output image(s)", flush=True)

        # Download the last image (typically the final processed one)
        download_image(client, image_urls[-1], args.output)

        # If multiple images, save all
        if len(image_urls) > 1:
            base = Path(args.output)
            for i, url in enumerate(image_urls[:-1]):
                extra_path = base.parent / f"{base.stem}_v{i+1}{base.suffix}"
                download_image(client, url, str(extra_path))

        print(f"\n✅ Done! Output: {args.output}", flush=True)


if __name__ == "__main__":
    main()
