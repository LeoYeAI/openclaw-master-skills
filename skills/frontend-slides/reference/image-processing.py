"""
Image processing helpers for Frontend Slides.
Use when user provides images: crop_circle for logos, resize_max for large files, add_padding for breathing room.
Dependency: pip install Pillow
"""
from PIL import Image, ImageDraw


def crop_circle(input_path, output_path):
    """Crop a square image to a circle with transparent background (e.g. logos on modern/clean styles)."""
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    size = min(w, h)
    left = (w - size) // 2
    top = (h - size) // 2
    img = img.crop((left, top, left + size, top + size))
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, size, size], fill=255)
    img.putalpha(mask)
    img.save(output_path, "PNG")


def resize_max(input_path, output_path, max_dim=1200):
    """Resize image so largest dimension <= max_dim. Preserves aspect ratio. Use for images > 1MB."""
    img = Image.open(input_path)
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    img.save(output_path, quality=85)


def add_padding(input_path, output_path, padding=40, bg_color=(0, 0, 0, 0)):
    """Add transparent padding around an image (screenshots that need breathing room)."""
    img = Image.open(input_path).convert("RGBA")
    w, h = img.size
    new = Image.new("RGBA", (w + 2 * padding, h + 2 * padding), bg_color)
    new.paste(img, (padding, padding), img)
    new.save(output_path, "PNG")


# When to apply:
# - Square logo on rounded aesthetics → crop_circle()
# - Image > 1MB → resize_max(max_dim=1200)
# - Screenshot needs breathing room → add_padding()
# - Wrong aspect ratio → manual img.crop((left, top, right, bottom))
# Save processed images with _processed suffix; never overwrite originals.
