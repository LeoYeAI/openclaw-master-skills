"""Post-processing for website-style generated images."""

import logging
import os

from PIL import Image, ImageCms

logger = logging.getLogger(__name__)


def ensure_rgb(image: Image.Image) -> Image.Image:
    """Convert image to RGB mode, compositing RGBA onto white background."""
    if image.mode == "RGBA":
        bg = Image.new("RGB", image.size, (255, 255, 255))
        bg.paste(image, mask=image.split()[3])
        return bg
    if image.mode != "RGB":
        return image.convert("RGB")
    return image


def resize_with_padding(image: Image.Image, target_size: tuple[int, int],
                        bg_color: tuple[int, int, int] = (255, 255, 255)) -> Image.Image:
    """Resize image to fit within target_size, maintaining aspect ratio, padding with bg_color."""
    target_w, target_h = target_size
    orig_w, orig_h = image.size

    scale = min(target_w / orig_w, target_h / orig_h)
    new_w = int(orig_w * scale)
    new_h = int(orig_h * scale)

    resized = image.resize((new_w, new_h), Image.LANCZOS)

    canvas = Image.new("RGB", target_size, bg_color)
    offset_x = (target_w - new_w) // 2
    offset_y = (target_h - new_h) // 2
    canvas.paste(resized, (offset_x, offset_y))

    return canvas


def embed_srgb_profile(image: Image.Image) -> Image.Image:
    """Embed sRGB ICC profile into the image."""
    srgb_profile = ImageCms.createProfile("sRGB")
    icc_data = ImageCms.ImageCmsProfile(srgb_profile).tobytes()
    image.info["icc_profile"] = icc_data
    return image


def optimize_file_size(image: Image.Image, output_path: str,
                       max_mb: float = 10.0, initial_quality: int = 92) -> str:
    """Save image as JPEG, reducing quality if file size exceeds max_mb."""
    quality = initial_quality
    icc_profile = image.info.get("icc_profile")

    while quality >= 70:
        save_kwargs = {"quality": quality, "optimize": True}
        if icc_profile:
            save_kwargs["icc_profile"] = icc_profile
        image.save(output_path, "JPEG", **save_kwargs)

        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        if file_size_mb <= max_mb:
            logger.info("Saved %s (%.1f MB, quality=%d)", output_path, file_size_mb, quality)
            return output_path

        logger.debug("File size %.1f MB exceeds %.1f MB at quality %d, reducing...",
                     file_size_mb, max_mb, quality)
        quality -= 5

    logger.warning("Could not reduce %s below %.1f MB (final: %.1f MB)",
                   output_path, max_mb, os.path.getsize(output_path) / (1024 * 1024))
    return output_path
