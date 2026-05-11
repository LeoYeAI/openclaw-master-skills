"""Style-aware prompt engine for website-style image generation.

Converts style profiles into effective AI image generation prompts.
Uses safe string replacement (not .format()) to prevent injection.
"""

import logging
import os

from utils import load_yaml

logger = logging.getLogger(__name__)

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_style_templates(prompts_dir: str | None = None) -> dict:
    """Load style prompt templates from YAML. Returns dict keyed by template id."""
    if prompts_dir is None:
        prompts_dir = os.path.join(SKILL_DIR, "prompts")
    path = os.path.join(prompts_dir, "style_templates.yaml")
    data = load_yaml(path)
    templates = {t["id"]: t for t in data.get("templates", [])}
    if not templates:
        raise ValueError(f"No templates found in {path}")
    logger.info("Loaded %d style templates", len(templates))
    return templates


def load_style_defaults(config_dir: str | None = None) -> dict:
    """Load default image type configurations."""
    if config_dir is None:
        config_dir = os.path.join(SKILL_DIR, "config")
    return load_yaml(os.path.join(config_dir, "style_defaults.yaml"))


def style_to_prompt_fragment(profile: dict) -> str:
    """Convert a style profile dict into a natural language prompt fragment.

    Produces specific, actionable visual instructions with exact hex values
    and concrete style directives. Uses negative constraints to avoid
    off-brand visuals.
    """
    colors = profile.get("colors", {})
    typo = profile.get("typography", {})
    traits = profile.get("design_traits", {})
    imagery = profile.get("imagery_style", {})
    personality = profile.get("brand_personality", "professional")

    lines = []

    # Overall aesthetic — be specific
    aesthetic = traits.get("aesthetic", "modern")
    lines.append(f"VISUAL STYLE: Strictly follow a {aesthetic} aesthetic.")
    lines.append(f"Brand personality: {personality}.")

    # Color palette with usage instructions
    primary = colors.get("primary", "#333333")
    secondary = colors.get("secondary", "#666666")
    accent = colors.get("accent", "#1A73E8")
    bg = colors.get("background", "#FFFFFF")
    text_color = colors.get("text_primary", "#333333")

    lines.append(f"COLOR PALETTE (use these EXACT hex values):")
    lines.append(f"  - Primary ({primary}): use for main visual elements, key shapes, dominant areas")
    lines.append(f"  - Secondary ({secondary}): use for supporting elements, secondary shapes")
    lines.append(f"  - Accent ({accent}): use sparingly for highlights, call-to-action, focal points")
    lines.append(f"  - Background ({bg}): base canvas color")
    lines.append(f"  - Text ({text_color}): any text elements")

    mood = colors.get("palette_mood", "")
    if mood:
        lines.append(f"  Color mood: {mood}.")

    # Determine color temperature for negative constraints
    primary_rgb = tuple(int(primary.lstrip("#")[i:i+2], 16) for i in (0, 2, 4)) if primary.startswith("#") and len(primary) == 7 else (0, 0, 0)
    r, g, b = primary_rgb
    if r > g and r > b:
        lines.append("  DO NOT introduce cool blues or greens unless specified above.")
    elif b > r and b > g:
        lines.append("  DO NOT introduce warm reds or oranges unless specified above.")

    # Typography with specific instructions
    heading_style = typo.get("heading_style", "bold sans-serif")
    body_style = typo.get("body_style", "regular sans-serif")
    typo_feel = typo.get("overall_feel", "modern")
    lines.append(f"TYPOGRAPHY: {typo_feel} feel.")
    lines.append(f"  - Headings: {heading_style}")
    lines.append(f"  - Body: {body_style}")

    # Design language with specific visual rules
    lines.append("DESIGN LANGUAGE:")
    if traits.get("border_radius"):
        lines.append(f"  - Corners: {traits['border_radius']}")
    if traits.get("shadow_style"):
        lines.append(f"  - Shadows: {traits['shadow_style']}")
    if traits.get("spacing"):
        lines.append(f"  - Layout: {traits['spacing']} spacing")
    if traits.get("gradient_use"):
        lines.append("  - Gradients: yes, use smooth gradients")
    else:
        lines.append("  - Gradients: NO gradients, use flat solid colors")
    if traits.get("layout_style"):
        lines.append(f"  - Structure: {traits['layout_style']}")

    # Imagery style
    if imagery.get("photo_style"):
        lines.append(f"IMAGERY: {imagery['photo_style']}.")
    keywords = imagery.get("mood_keywords", [])
    if keywords:
        lines.append(f"MOOD: {', '.join(keywords)}.")

    # Extended visual dimensions
    if imagery.get("icon_style"):
        lines.append(f"ICON STYLE: {imagery['icon_style']}.")
    if imagery.get("illustration_style"):
        lines.append(f"ILLUSTRATION STYLE: {imagery['illustration_style']}.")
    if imagery.get("photography_treatment"):
        lines.append(f"PHOTO TREATMENT: {imagery['photography_treatment']}.")
    if traits.get("pattern_style"):
        lines.append(f"PATTERNS/TEXTURES: {traits['pattern_style']}.")
    if traits.get("density"):
        lines.append(f"INFORMATION DENSITY: {traits['density']} — match this level of visual complexity.")

    # Negative constraints based on aesthetic
    negatives = {
        "minimalist": "busy patterns, excessive decoration, heavy textures, cluttered compositions, neon colors",
        "bold": "muted colors, passive compositions, excessive whitespace, thin fonts",
        "vibrant": "muted colors, passive compositions, excessive whitespace, thin fonts",
        "luxury": "cheap-looking effects, neon colors, cartoon styles, low contrast, flat design",
        "premium": "cheap-looking effects, neon colors, cartoon styles, low contrast, flat design",
        "corporate": "playful illustrations, neon colors, grunge textures, handwritten fonts",
        "playful": "corporate stiffness, monochrome palettes, rigid grids, serif fonts",
        "tech": "organic shapes, watercolor textures, vintage aesthetics, warm earth tones",
        "organic": "sharp geometric edges, digital/tech aesthetics, neon colors, dark backgrounds",
    }
    for key, neg in negatives.items():
        if key in aesthetic.lower():
            lines.append(f"AVOID: {neg}.")
            break

    return "\n".join(lines)


def render_styled_prompt(template: dict, style_fragment: str,
                         content_description: str,
                         dimensions: str = "") -> str:
    """Render a single styled prompt using safe string replacement.

    Uses .replace() instead of .format() to prevent injection from
    user-controlled content_description containing {key} patterns.
    """
    prompt = template["prompt"]
    prompt = prompt.replace("{style_instructions}", style_fragment)
    prompt = prompt.replace("{content_description}", content_description)
    prompt = prompt.replace("{dimensions}", dimensions)
    return prompt.strip()


def build_styled_prompts(config: dict, prompts_dir: str | None = None,
                         config_dir: str | None = None) -> list[dict]:
    """Build all rendered prompts from a styled image config.

    Args:
        config: Dict with 'style_profile' and 'requests' keys.
            requests is a list of dicts with:
                - image_type: str (template id)
                - content_description: str
                - width: int (optional)
                - height: int (optional)
        prompts_dir: Path to prompts directory.
        config_dir: Path to config directory.

    Returns:
        List of dicts with keys: index, image_type, name, filename, prompt,
        width, height, reference_image_url.
    """
    templates = load_style_templates(prompts_dir)
    defaults = load_style_defaults(config_dir)
    image_type_defaults = defaults.get("image_types", {})

    style_profile = config.get("style_profile", {})
    if not style_profile:
        logger.warning("Empty style_profile in config, prompts will use generic style")

    style_fragment = style_to_prompt_fragment(style_profile)
    screenshot_path = style_profile.get("screenshot_path", "")

    requests = config.get("requests", [])
    if not requests:
        logger.warning("No image requests found in config")
        return []

    results = []
    for i, req in enumerate(requests, start=1):
        image_type = req.get("image_type", "custom")
        template = templates.get(image_type)
        if not template:
            logger.warning("Unknown image type '%s', falling back to 'custom'", image_type)
            template = templates.get("custom")
            if not template:
                logger.error("No 'custom' template available, skipping request %d", i)
                continue

        content_desc = req.get("content_description", "").strip()
        if not content_desc:
            content_desc = "A visually appealing image matching the brand style"
            logger.warning("Empty content_description for request %d, using default", i)

        # Determine dimensions
        type_defaults = image_type_defaults.get(image_type, {})
        width = req.get("width", type_defaults.get("width", 1200))
        height = req.get("height", type_defaults.get("height", 1200))
        dimensions_str = f"{width}x{height}"

        prompt = render_styled_prompt(template, style_fragment, content_desc, dimensions_str)

        # Reference image: use request-specific or fall back to screenshot
        ref_image = req.get("reference_image_url", screenshot_path)

        results.append({
            "index": i,
            "image_type": image_type,
            "name": template.get("name", image_type),
            "filename": template.get("filename", f"{i:02d}_{image_type}"),
            "prompt": prompt,
            "width": width,
            "height": height,
            "reference_image_url": ref_image,
        })

    logger.info("Built %d styled prompts", len(results))
    return results
