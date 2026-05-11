"""Website style extraction and normalization.

Extracts visual style data from CSS/DOM and screenshot analysis,
normalizes colors, and builds structured style profiles.
"""

import colorsys
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

# --- Constants ---
WHITE_THRESHOLD = 240
BLACK_THRESHOLD = 30
CLUSTER_DISTANCE_THRESHOLD = 0.02
MAX_SCREENSHOT_MB = 5.0


def parse_css_color(color_str: str) -> tuple[int, int, int] | None:
    """Parse a CSS color string (rgb/rgba/hex) to an (R, G, B) tuple.

    Returns None if the string cannot be parsed.
    Values are clamped to 0-255.
    """
    color_str = color_str.strip()

    # rgb(r, g, b) or rgba(r, g, b, a)
    m = re.match(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", color_str)
    if m:
        r = max(0, min(255, int(m.group(1))))
        g = max(0, min(255, int(m.group(2))))
        b = max(0, min(255, int(m.group(3))))
        return r, g, b

    # Hex: #RGB, #RRGGBB, #RRGGBBAA
    m = re.match(r"#([0-9a-fA-F]{3,8})$", color_str)
    if m:
        hex_val = m.group(1)
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        if len(hex_val) >= 6:
            return (
                int(hex_val[0:2], 16),
                int(hex_val[2:4], 16),
                int(hex_val[4:6], 16),
            )

    return None


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB tuple to hex string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple. Returns (255,255,255) on error."""
    result = parse_css_color(hex_color)
    if result is None:
        logger.warning("Invalid hex color '%s', defaulting to white", hex_color)
        return (255, 255, 255)
    return result


def hsl_distance(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    """Compute perceptual distance between two RGB colors in HSL space.

    Hue is weighted 2x since hue differences are more perceptually distinct.
    """
    h1, l1, s1 = colorsys.rgb_to_hls(c1[0] / 255, c1[1] / 255, c1[2] / 255)
    h2, l2, s2 = colorsys.rgb_to_hls(c2[0] / 255, c2[1] / 255, c2[2] / 255)

    # Hue is circular (0-1 wraps around)
    dh = min(abs(h1 - h2), 1 - abs(h1 - h2))
    dl = abs(l1 - l2)
    ds = abs(s1 - s2)

    return (dh * 2) ** 2 + dl ** 2 + ds ** 2


def is_near_white(rgb: tuple[int, int, int], threshold: int = WHITE_THRESHOLD) -> bool:
    """Check if a color is near white."""
    return all(c >= threshold for c in rgb)


def is_near_black(rgb: tuple[int, int, int], threshold: int = BLACK_THRESHOLD) -> bool:
    """Check if a color is near black."""
    return all(c <= threshold for c in rgb)


def cluster_colors(colors: list[tuple[int, int, int]],
                   distance_threshold: float = CLUSTER_DISTANCE_THRESHOLD
                   ) -> list[tuple[tuple[int, int, int], int]]:
    """Cluster similar colors together using greedy algorithm.

    Colors are sorted by HSL before clustering for deterministic results.

    Returns:
        List of (representative_color, count) sorted by count descending.
    """
    if not colors:
        return []

    # Sort by HSL for deterministic clustering
    def hsl_key(c: tuple[int, int, int]) -> tuple:
        h, l, s = colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)
        return (h, l, s)

    sorted_colors = sorted(colors, key=hsl_key)

    clusters: list[tuple[tuple[int, int, int], int]] = []
    for color in sorted_colors:
        merged = False
        for i, (rep, count) in enumerate(clusters):
            if hsl_distance(color, rep) < distance_threshold:
                clusters[i] = (rep, count + 1)
                merged = True
                break
        if not merged:
            clusters.append((color, 1))

    clusters.sort(key=lambda x: x[1], reverse=True)
    return clusters


def normalize_colors(raw_colors: list[str]) -> dict:
    """Parse CSS color strings, cluster, and assign primary/secondary/accent roles.

    Returns:
        Dict with keys: primary, secondary, accent, background, text_primary.
        Falls back to sensible defaults when data is insufficient.
    """
    defaults = {
        "primary": "#333333",
        "secondary": "#666666",
        "accent": "#1A73E8",
        "background": "#FFFFFF",
        "text_primary": "#333333",
    }

    parsed = []
    for c in raw_colors:
        rgb = parse_css_color(c)
        if rgb:
            parsed.append(rgb)

    if not parsed:
        logger.warning("No valid colors to normalize, using defaults")
        return defaults

    # Separate into categories
    whites = [c for c in parsed if is_near_white(c)]
    blacks = [c for c in parsed if is_near_black(c)]
    chromatic = [c for c in parsed if not is_near_white(c) and not is_near_black(c)]

    # Cluster chromatic colors
    clusters = cluster_colors(chromatic)

    # Assign roles with safe fallbacks
    background = rgb_to_hex(*whites[0]) if whites else "#FFFFFF"
    text_primary = rgb_to_hex(*blacks[0]) if blacks else "#333333"

    if len(clusters) == 0:
        logger.warning("No chromatic colors found, using defaults for primary/secondary/accent")
        return {**defaults, "background": background, "text_primary": text_primary}

    primary = rgb_to_hex(*clusters[0][0])
    secondary = rgb_to_hex(*clusters[1][0]) if len(clusters) > 1 else primary
    accent = rgb_to_hex(*clusters[2][0]) if len(clusters) > 2 else primary

    # If primary is very dark, it's likely a text color; promote secondary
    _, l, _ = colorsys.rgb_to_hls(
        clusters[0][0][0] / 255, clusters[0][0][1] / 255, clusters[0][0][2] / 255
    )
    if l < 0.15 and len(clusters) > 1:
        primary, secondary = secondary, primary

    return {
        "primary": primary,
        "secondary": secondary,
        "accent": accent,
        "background": background,
        "text_primary": text_primary,
    }


def build_style_profile(css_data: dict, screenshot_analysis: dict, url: str) -> dict:
    """Merge CSS extraction data and screenshot analysis into a style profile.

    Args:
        css_data: Dict from JS extraction with keys: textColors, backgroundColors,
                  bodyFonts, headingFonts, avgBorderRadius, hasGradient, hasShadow,
                  fontWeights, letterSpacings, lineHeights, gradientColors.
        screenshot_analysis: Dict from Claude vision analysis with keys: aesthetic,
                             palette_mood, spacing, photo_style, mood_keywords,
                             brand_personality, typography_feel.
        url: Source URL.

    Returns:
        Canonical style profile dict.
    """
    # Normalize all collected colors (including gradient colors)
    all_colors = (
        css_data.get("textColors", [])
        + css_data.get("backgroundColors", [])
        + css_data.get("gradientColors", [])
    )
    colors = normalize_colors(all_colors)
    colors["palette_mood"] = screenshot_analysis.get("palette_mood", "neutral")

    # Typography with font weight and spacing details
    heading_fonts = css_data.get("headingFonts", [])
    body_fonts = css_data.get("bodyFonts", [])
    font_weights = css_data.get("fontWeights", {})
    letter_spacings = css_data.get("letterSpacings", [])
    line_heights = css_data.get("lineHeights", [])

    heading_weight = font_weights.get("heading", "bold")
    body_weight = font_weights.get("body", "regular")

    # Clean font names (strip quotes)
    clean_heading = heading_fonts[0].strip("'\"") if heading_fonts else "sans-serif"
    clean_body = body_fonts[0].strip("'\"") if body_fonts else "sans-serif"

    # Determine letter-spacing description
    avg_spacing = 0
    if letter_spacings:
        avg_spacing = sum(letter_spacings) / len(letter_spacings)
    spacing_desc = (
        "tight letter-spacing" if avg_spacing < -0.5
        else "wide letter-spacing" if avg_spacing > 1
        else "normal letter-spacing"
    )

    # Determine line-height description
    avg_line_height = 1.5
    if line_heights:
        avg_line_height = sum(line_heights) / len(line_heights)
    lh_desc = (
        "compact line-height" if avg_line_height < 1.3
        else "generous line-height" if avg_line_height > 1.8
        else "standard line-height"
    )

    typography = {
        "heading_style": f"{clean_heading}, {heading_weight}, {spacing_desc}",
        "body_style": f"{clean_body}, {body_weight}, {lh_desc}",
        "overall_feel": screenshot_analysis.get("typography_feel", "modern"),
    }

    # Design traits
    avg_radius = css_data.get("avgBorderRadius", 0)
    radius_desc = (
        "sharp corners" if avg_radius < 2
        else "slightly rounded" if avg_radius < 8
        else "fully rounded" if avg_radius > 20
        else "rounded"
    )

    shadow_detail = css_data.get("shadowDetail", "")
    shadow_desc = (
        shadow_detail if shadow_detail
        else "soft shadows" if css_data.get("hasShadow") else "flat, no shadows"
    )

    design_traits = {
        "aesthetic": screenshot_analysis.get("aesthetic", "modern"),
        "border_radius": radius_desc,
        "shadow_style": shadow_desc,
        "spacing": screenshot_analysis.get("spacing", "balanced"),
        "gradient_use": css_data.get("hasGradient", False),
        "layout_style": screenshot_analysis.get("layout_style", ""),
    }

    # Imagery (extended dimensions)
    imagery_style = {
        "photo_style": screenshot_analysis.get("photo_style", "clean photography"),
        "mood_keywords": screenshot_analysis.get("mood_keywords", ["professional"]),
        "icon_style": screenshot_analysis.get("icon_style", ""),
        "illustration_style": screenshot_analysis.get("illustration_style", ""),
        "photography_treatment": screenshot_analysis.get("photography_treatment", ""),
    }

    # Extended design traits
    design_traits["pattern_style"] = screenshot_analysis.get("pattern_style", "")
    design_traits["density"] = screenshot_analysis.get("density", "")

    profile = {
        "source_url": url,
        "colors": colors,
        "typography": typography,
        "design_traits": design_traits,
        "imagery_style": imagery_style,
        "brand_personality": screenshot_analysis.get("brand_personality", "professional"),
        "screenshot_path": screenshot_analysis.get("screenshot_path", ""),
    }

    logger.info("Built style profile for %s (primary=%s, aesthetic=%s)",
                url, colors["primary"], design_traits["aesthetic"])
    return profile


def validate_screenshot(path: str) -> bool:
    """Validate screenshot file exists and is within size limits.

    Returns True if valid, logs warnings for issues.
    """
    if not path:
        logger.info("No screenshot path provided")
        return False

    if not os.path.isfile(path):
        logger.warning("Screenshot file not found: %s", path)
        return False

    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > MAX_SCREENSHOT_MB:
        logger.warning("Screenshot %.1f MB exceeds %.1f MB limit: %s",
                        size_mb, MAX_SCREENSHOT_MB, path)
        return False

    logger.info("Screenshot validated: %s (%.1f MB)", path, size_mb)
    return True


def compress_screenshot(path: str, max_width: int = 1920) -> str:
    """Compress a screenshot if it's too large. Returns path to compressed file."""
    from PIL import Image

    img = Image.open(path)
    w, h = img.size

    if w <= max_width:
        return path

    ratio = max_width / w
    new_size = (max_width, int(h * ratio))
    img = img.resize(new_size, Image.LANCZOS)

    compressed_path = path.rsplit(".", 1)[0] + "_compressed.jpg"
    img.save(compressed_path, "JPEG", quality=85)
    logger.info("Compressed screenshot: %s -> %s (%dx%d)", path, compressed_path, *new_size)
    return compressed_path


def save_style_profile(profile: dict, output_path: str) -> str:
    """Save style profile to JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    logger.info("Saved style profile to %s", output_path)
    return output_path


def load_style_profile(path: str) -> dict:
    """Load a previously saved style profile."""
    with open(path, "r", encoding="utf-8") as f:
        profile = json.load(f)
    logger.info("Loaded style profile from %s", path)
    return profile
