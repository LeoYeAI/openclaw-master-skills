#!/usr/bin/env python3
"""Visual diff with region heatmap: compare rendered screenshot against target.

Usage:
  python3 visual_diff.py --current current.png --target design-main.png [--diff diff.png] [--regions 5]

Outputs:
  - Global MAE + MAE-based similarity
  - Global SSIM (structure similarity)
  - Composite score (weighted MAE + SSIM)
  - Diff image with region heatmap showing per-region error
"""

import argparse
import json
from pathlib import Path


def compute_ssim(gray_a, gray_b):
    """Compute global SSIM.

    Prefer numpy when available; otherwise fallback to pure Python on a downscaled image.
    """
    # Downscale for speed/stability on tall screenshots
    max_side = 512
    if max(gray_a.size) > max_side:
        ratio = max_side / max(gray_a.size)
        new_size = (max(1, int(gray_a.width * ratio)), max(1, int(gray_a.height * ratio)))
        gray_a = gray_a.resize(new_size)
        gray_b = gray_b.resize(new_size)

    try:
        import numpy as np

        a = np.asarray(gray_a, dtype=np.float64)
        b = np.asarray(gray_b, dtype=np.float64)

        mu_a = a.mean()
        mu_b = b.mean()
        var_a = ((a - mu_a) ** 2).mean()
        var_b = ((b - mu_b) ** 2).mean()
        cov_ab = ((a - mu_a) * (b - mu_b)).mean()
    except Exception:
        a = list(gray_a.getdata())
        b = list(gray_b.getdata())
        n = len(a)
        if n == 0:
            return None

        mu_a = sum(a) / n
        mu_b = sum(b) / n

        var_a = 0.0
        var_b = 0.0
        cov_ab = 0.0
        for x, y in zip(a, b):
            da = x - mu_a
            db = y - mu_b
            var_a += da * da
            var_b += db * db
            cov_ab += da * db
        var_a /= n
        var_b /= n
        cov_ab /= n

    L = 255.0
    c1 = (0.01 * L) ** 2
    c2 = (0.03 * L) ** 2

    num = (2 * mu_a * mu_b + c1) * (2 * cov_ab + c2)
    den = (mu_a**2 + mu_b**2 + c1) * (var_a + var_b + c2)
    if den == 0:
        return 1.0

    ssim = num / den
    return max(-1.0, min(1.0, float(ssim)))


def main():
    p = argparse.ArgumentParser(description="Compare images with region heatmap")
    p.add_argument("--current", required=True)
    p.add_argument("--target", required=True)
    p.add_argument("--diff", default="diff.png")
    p.add_argument("--regions", type=int, default=5, help="Grid divisions (NxN)")
    p.add_argument("--threshold", type=float, default=30.0, help="MAE threshold to flag a region as 'bad'")
    p.add_argument(
        "--json-out",
        default=None,
        help="Optional path to write machine-readable metrics JSON",
    )
    p.add_argument(
        "--ssim-weight",
        type=float,
        default=0.4,
        help="Weight of SSIM in composite score (0~1). MAE weight is (1-ssim-weight)",
    )
    args = p.parse_args()

    from PIL import Image, ImageChops, ImageStat, ImageDraw, ImageFont

    cur = Image.open(args.current).convert("RGB")
    tgt = Image.open(args.target).convert("RGB").resize(cur.size)
    diff = ImageChops.difference(cur, tgt)

    # Global MAE stats
    stat = ImageStat.Stat(diff)
    mae = sum(stat.mean) / 3
    mae_similarity = max(0, 100 - mae / 255 * 100)

    # Global SSIM (grayscale)
    ssim = compute_ssim(cur.convert("L"), tgt.convert("L"))
    ssim_similarity = None if ssim is None else max(0.0, min(100.0, (ssim + 1) * 50))

    w_ssim = min(max(args.ssim_weight, 0.0), 1.0)
    w_mae = 1.0 - w_ssim
    if ssim_similarity is None:
        composite = mae_similarity
    else:
        composite = w_mae * mae_similarity + w_ssim * ssim_similarity

    # Region heatmap (still MAE-driven)
    n = args.regions
    rw, rh = max(1, cur.width // n), max(1, cur.height // n)
    overlay = Image.new("RGBA", cur.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    bad_regions = []

    for row in range(n):
        for col in range(n):
            x0, y0 = col * rw, row * rh
            x1 = cur.width if col == n - 1 else (col + 1) * rw
            y1 = cur.height if row == n - 1 else (row + 1) * rh
            box = (x0, y0, x1, y1)

            region = diff.crop(box)
            rstat = ImageStat.Stat(region)
            rmae = sum(rstat.mean) / 3
            pct = min(rmae / 255, 1.0)

            if pct < 0.5:
                r_val = int(255 * pct * 2)
                g_val = 255
            else:
                r_val = 255
                g_val = int(255 * (1 - pct) * 2)
            alpha = int(40 + pct * 100)

            draw.rectangle(box, fill=(r_val, g_val, 0, alpha))
            draw.rectangle(box, outline=(255, 255, 255, 80))

            if rmae > args.threshold:
                bad_regions.append({"row": row, "col": col, "mae": round(rmae, 2), "box": box})

    diff_rgba = diff.convert("RGBA")
    composite_img = Image.alpha_composite(diff_rgba, overlay).convert("RGB")

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except Exception:
        font = ImageFont.load_default()

    for br in bad_regions:
        x, y = br["box"][0] + 4, br["box"][1] + 4
        draw2 = ImageDraw.Draw(composite_img)
        draw2.rectangle([x - 2, y - 2, x + 90, y + 18], fill=(0, 0, 0, 180))
        draw2.text((x, y), f"MAE {br['mae']}", fill=(255, 80, 80), font=font)

    draw3 = ImageDraw.Draw(composite_img)
    for i in range(1, n):
        draw3.line([(i * rw, 0), (i * rw, cur.height)], fill=(255, 255, 255, 60), width=1)
        draw3.line([(0, i * rh), (cur.width, i * rh)], fill=(255, 255, 255, 60), width=1)

    Path(args.diff).parent.mkdir(parents=True, exist_ok=True)
    composite_img.save(args.diff)

    print(f"Global MAE: {mae:.2f}")
    print(f"MAE Similarity: {mae_similarity:.2f}%")
    if ssim is None:
        print("SSIM: unavailable (numpy not installed)")
    else:
        print(f"SSIM: {ssim:.4f}")
        print(f"SSIM Similarity: {ssim_similarity:.2f}%")
    print(f"Composite Similarity: {composite:.2f}% (mae={w_mae:.2f}, ssim={w_ssim:.2f})")
    print(f"Regions: {n}x{n}, threshold: {args.threshold}")
    print(f"Bad regions ({len(bad_regions)}):")
    for br in bad_regions:
        print(f"  Row {br['row']}, Col {br['col']}: MAE {br['mae']}")
    print(f"Diff saved: {args.diff}")

    if args.json_out:
        payload = {
            "mae": mae,
            "maeSimilarity": mae_similarity,
            "ssim": ssim,
            "ssimSimilarity": ssim_similarity,
            "compositeSimilarity": composite,
            "weights": {"mae": w_mae, "ssim": w_ssim},
            "regions": n,
            "threshold": args.threshold,
            "badRegions": bad_regions,
            "diff": args.diff,
        }
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Metrics JSON saved: {out}")


if __name__ == "__main__":
    main()
