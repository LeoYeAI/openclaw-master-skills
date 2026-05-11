"""
Content Claw - Image Generator

Takes an image spec (JSON from agent prompts) and generates an image using fal.ai.
Saves the image to the specified output path.

Usage:
    uv run generate_image.py <spec-json-file> <output-path>
    uv run generate_image.py --prompt "description" <output-path>

Environment:
    FAL_KEY - Required. Set in .env file.
"""

import json
import os
import sys
from pathlib import Path


def spec_to_prompt(spec: dict) -> str:
    """Convert an image spec JSON (from agent prompts) into an image generation prompt."""
    parts = []

    # Diagram type
    diagram_type = spec.get("diagram_type")
    layout = spec.get("style", {}).get("layout", "")
    sub_type = diagram_type or layout

    # Title and description
    title = spec.get("title", spec.get("headline", ""))
    if title:
        parts.append(f'Title: "{title}"')

    subtitle = spec.get("subtitle", spec.get("subheadline", spec.get("description", "")))
    if subtitle:
        parts.append(f"Subtitle: {subtitle}")

    # Content sections
    sections = spec.get("sections", [])
    if sections:
        section_text = []
        for s in sections:
            heading = s.get("heading", "")
            content = s.get("content", "")
            section_text.append(f"- {heading}: {content}")
        parts.append("Content:\n" + "\n".join(section_text))

    # Details (for posters)
    details = spec.get("details", [])
    if details:
        parts.append("Details: " + ", ".join(details))

    # Components (for diagrams)
    components = spec.get("components", [])
    if components:
        comp_text = []
        for c in components:
            comp_text.append(f"- {c.get('label', '')}: {c.get('description', '')}")
        parts.append("Components:\n" + "\n".join(comp_text))

    # Connections (for diagrams)
    connections = spec.get("connections", [])
    if connections:
        conn_text = []
        for c in connections:
            conn_text.append(f"- {c.get('from', '')} -> {c.get('to', '')}: {c.get('label', '')}")
        parts.append("Connections:\n" + "\n".join(conn_text))

    # Style guidance
    style = spec.get("style", {})
    tone = style.get("tone", "professional")
    primary_color = style.get("primary_color")
    accent_color = style.get("accent_color")

    style_parts = [f"{tone} style"]
    if primary_color:
        style_parts.append(f"primary color {primary_color}")
    if accent_color:
        style_parts.append(f"accent color {accent_color}")

    # CTA (for posters)
    cta = spec.get("call_to_action")
    if cta:
        parts.append(f"Call to action: {cta}")

    # Build the full prompt
    content_description = "\n".join(parts)

    if diagram_type:
        prompt = (
            f"Create a clean, modern {diagram_type} diagram for social media. "
            f"{', '.join(style_parts)}. "
            f"Clear labels, readable at small sizes, white or light background. "
            f"\n\n{content_description}"
        )
    elif "poster" in sub_type or "banner" in sub_type:
        prompt = (
            f"Create a modern event poster for social media. "
            f"{', '.join(style_parts)}. "
            f"Bold typography, clean layout, eye-catching. "
            f"\n\n{content_description}"
        )
    else:
        # Default: infographic
        prompt = (
            f"Create a clean, modern infographic for social media. "
            f"{', '.join(style_parts)}. "
            f"Clear visual hierarchy, readable at small sizes, {layout or 'vertical'} layout. "
            f"\n\n{content_description}"
        )

    return prompt


FAL_MODELS = {
    "recraft-v4": "fal-ai/recraft/v4/pro/text-to-image",
    "ideogram-v3": "fal-ai/ideogram/v3",
    "flux-2": "fal-ai/flux-2-flex",
    "flux-pro": "fal-ai/flux-pro/v1.1",
}

# Model selection by content type:
# - Recraft V4: best for infographics, diagrams, logos. Strong composition,
#   lighting, and text rendering. #1 on HuggingFace benchmarks.
# - Ideogram V3: best for posters and banners. Near-perfect typography,
#   bold design.
# - Flux 2: best for photorealistic content and general high-quality generation.
MODEL_FOR_FORMAT = {
    "infographic": "recraft-v4",
    "diagram": "recraft-v4",
    "poster": "ideogram-v3",
}

DEFAULT_MODEL = "recraft-v4"


def hex_to_rgb(hex_color: str) -> dict:
    """Convert '#RRGGBB' to {'r': int, 'g': int, 'b': int}."""
    h = hex_color.lstrip("#")
    return {"r": int(h[0:2], 16), "g": int(h[2:4], 16), "b": int(h[4:6], 16)}


def build_model_args(model_name: str, prompt: str, width: int, height: int, spec: dict | None = None) -> dict:
    """Build model-specific fal.ai arguments from the spec."""
    spec = spec or {}
    style = spec.get("style", {})
    primary_color = style.get("primary_color")
    accent_color = style.get("accent_color")
    image_params = spec.get("image_params", {})

    base = {
        "prompt": prompt,
        "image_size": {"width": width, "height": height},
        "num_images": 1,
    }

    if model_name == "recraft-v4":
        # Recraft supports colors array and background_color
        colors = []
        if primary_color:
            colors.append(hex_to_rgb(primary_color))
        if accent_color:
            colors.append(hex_to_rgb(accent_color))
        if colors:
            base["colors"] = colors
        bg = image_params.get("background_color")
        if bg:
            base["background_color"] = hex_to_rgb(bg) if isinstance(bg, str) else bg

    elif model_name == "ideogram-v3":
        # Ideogram supports rendering_speed, style, negative_prompt, color_palette
        base["rendering_speed"] = image_params.get("rendering_speed", "QUALITY")
        base["style"] = image_params.get("style", "DESIGN")
        base["expand_prompt"] = image_params.get("expand_prompt", True)
        neg = image_params.get("negative_prompt")
        if neg:
            base["negative_prompt"] = neg
        # Build color_palette from brand colors
        if primary_color or accent_color:
            members = []
            if primary_color:
                members.append({"hex_color": primary_color, "weight": 0.6})
            if accent_color:
                members.append({"hex_color": accent_color, "weight": 0.4})
            base["color_palette"] = {"members": members}

    elif model_name in ("flux-2", "flux-pro"):
        # Flux supports guidance_scale, num_inference_steps, output_format
        base["guidance_scale"] = image_params.get("guidance_scale", 5.0)
        base["num_inference_steps"] = image_params.get("num_inference_steps", 40)
        base["output_format"] = image_params.get("output_format", "png")

    # Seed support for all models
    seed = image_params.get("seed")
    if seed is not None:
        base["seed"] = seed

    return base


def generate_image(prompt: str, output_path: str, size: str = "1024x1024", model: str | None = None, spec: dict | None = None) -> dict:
    """Generate an image using fal.ai and save to output_path."""
    import fal_client
    import httpx

    api_key = os.getenv("FAL_KEY")
    if not api_key:
        return {"error": "FAL_KEY not set. Add it to your .env file."}

    os.environ["FAL_KEY"] = api_key

    model_name = model or DEFAULT_MODEL
    fal_model = FAL_MODELS.get(model_name, FAL_MODELS[DEFAULT_MODEL])

    width, height = (int(d) for d in size.split("x"))

    arguments = build_model_args(model_name, prompt, width, height, spec)

    result = fal_client.subscribe(fal_model, arguments=arguments)

    image_url = result["images"][0]["url"]

    img_resp = httpx.get(image_url, timeout=60)
    img_resp.raise_for_status()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    return {
        "output_path": output_path,
        "image_url": image_url,
        "size": size,
        "model": model_name,
        "fal_model": fal_model,
        "bytes": len(img_resp.content),
    }


def main():
    if len(sys.argv) < 3:
        print(
            json.dumps({"error": "Usage: generate_image.py <spec.json|--prompt 'text'> <output.png>"}),
            file=sys.stderr,
        )
        sys.exit(1)

    # Load only FAL_KEY from .env (scoped loader)
    allowed = {"FAL_KEY"}
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key in allowed:
                os.environ.setdefault(key, value.strip())

    if sys.argv[1] == "--prompt":
        prompt = sys.argv[2]
        output_path = sys.argv[3]
        model = None
        spec = None
    else:
        spec_path = sys.argv[1]
        output_path = sys.argv[2]
        with open(spec_path) as f:
            spec = json.load(f)
        prompt = spec_to_prompt(spec)
        # Auto-select model from spec's sub_format or style.layout
        sub_format = spec.get("sub_format", spec.get("diagram_type", ""))
        layout = spec.get("style", {}).get("layout", "")
        model = spec.get("model") or MODEL_FOR_FORMAT.get(sub_format) or MODEL_FOR_FORMAT.get(layout)

    try:
        result = generate_image(prompt, output_path, model=model, spec=spec)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
