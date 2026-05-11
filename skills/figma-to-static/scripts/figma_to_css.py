#!/usr/bin/env python3
"""Parse Figma nodes.json and extract CSS properties for each node.

Usage:
  python3 figma_to_css.py --nodes nodes.json [--out styles.yaml]

Reads Figma REST API node export, outputs CSS variable/property mappings
per node for quick copy-paste into styles.css.
"""
import argparse, json, sys
from pathlib import Path


def color_to_css(c):
    """Convert Figma 0-1 RGBA to CSS color string."""
    if not c:
        return None
    r = round(c.get("r", 0) * 255)
    g = round(c.get("g", 0) * 255)
    b = round(c.get("b", 0) * 255)
    a = c.get("a", 1)
    if a < 1:
        return f"rgba({r}, {g}, {b}, {a})"
    return f"rgb({r}, {g}, {b})"


def parse_node(node, depth=0):
    """Recursively extract CSS-relevant properties from a Figma node."""
    props = {}
    name = node.get("name", "unnamed")
    ntype = node.get("type", "")

    # Background fill
    fills = node.get("fills") or []
    bg_colors = []
    for f in fills:
        if f.get("type") in ("SOLID", "COLOR"):
            c = color_to_css(f.get("color"))
            if c:
                bg_colors.append(c)
    if bg_colors:
        props["background-color"] = bg_colors[0] if len(bg_colors) == 1 else f"/* multiple fills: {bg_colors} */"

    # Border / stroke
    strokes = node.get("strokes") or []
    for s in strokes:
        if s.get("type") in ("SOLID", "COLOR"):
            c = color_to_css(s.get("color"))
            w = s.get("weight", 1)
            props["border"] = f"{w}px solid {c}" if c else f"{w}px solid"

    # Border radius (per-corner if different)
    cr = node.get("cornerRadius")
    tcr = node.get("topLeftRadius", cr)
    trcr = node.get("topRightRadius", cr)
    brcr = node.get("bottomRightRadius", cr)
    blcr = node.get("bottomLeftRadius", cr)
    if cr is not None or any(v is not None for v in [tcr, trcr, brcr, blcr]):
        vals = [tcr, trcr, brcr, blcr]
        if all(v == vals[0] for v in vals):
            props["border-radius"] = f"{vals[0]}px"
        else:
            props["border-radius"] = f"{vals[0]}px {vals[1]}px {vals[2]}px {vals[3]}px"

    # Opacity
    opacity = node.get("opacity")
    if opacity is not None and opacity < 1:
        props["opacity"] = str(opacity)

    # Effects (shadow)
    effects = node.get("effects") or []
    shadows = []
    for e in effects:
        if e.get("type") == "DROP_SHADOW":
            c = color_to_css(e.get("color"))
            x = e.get("offset", {}).get("x", 0)
            y = e.get("offset", {}).get("y", 4)
            r = e.get("spread", 0)
            b = e.get("radius", 4)
            shadows.append(f"{x}px {y}px {b}px {r}px {c}")
    if shadows:
        props["box-shadow"] = ", ".join(shadows)

    # Text properties
    style = node.get("style") or {}
    if style:
        if style.get("fontFamily"):
            props["font-family"] = f'"{style["fontFamily"]}"'
        if style.get("fontSize"):
            props["font-size"] = f'{style["fontSize"]}px'
        if style.get("fontWeight"):
            props["font-weight"] = str(style["fontWeight"])
        if style.get("textAlignHorizontal"):
            align = style["textAlignHorizontal"]
            css_map = {"LEFT": "left", "CENTER": "center", "RIGHT": "right", "JUSTIFIED": "justify"}
            props["text-align"] = css_map.get(align, align.lower() if align else "left")
        if style.get("lineHeightPx"):
            fs = style.get("fontSize", 16)
            ratio = style["lineHeightPx"] / fs
            props["line-height"] = f"{ratio:.2f}"
        elif style.get("lineHeightPercent"):
            props["line-height"] = f"{style['lineHeightPercent'] / 100:.2f}"
        if style.get("letterSpacing"):
            props["letter-spacing"] = f'{style["letterSpacing"]}px'
        text_fills = style.get("fills") or []
        for f in text_fills:
            if f.get("type") in ("SOLID", "COLOR"):
                c = color_to_css(f.get("color"))
                if c:
                    props["color"] = c

    # Layout / auto-layout
    layout_mode = node.get("layoutMode")
    if layout_mode:
        flex_map = {"HORIZONTAL": "row", "VERTICAL": "column"}
        props["display"] = "flex"
        props["flex-direction"] = flex_map.get(layout_mode, layout_mode.lower())

    item_spacing = node.get("itemSpacing")
    if item_spacing is not None:
        props["gap"] = f"{item_spacing}px"

    primary_align = node.get("primaryAxisAlignItems")
    if primary_align:
        pa_map = {"MIN": "flex-start", "CENTER": "center", "MAX": "flex-end", "SPACE_BETWEEN": "space-between"}
        axis = "justify-content"
        if layout_mode == "HORIZONTAL":
            axis = "justify-content"
        else:
            axis = "align-items"
        props[axis] = pa_map.get(primary_align, primary_align.lower())

    counter_align = node.get("counterAxisAlignItems")
    if counter_align:
        ca_map = {"MIN": "flex-start", "CENTER": "center", "MAX": "flex-end"}
        axis = "align-items" if layout_mode == "HORIZONTAL" else "justify-content"
        props[axis] = ca_map.get(counter_align, counter_align.lower())

    pad_top = node.get("paddingTop")
    pad_bottom = node.get("paddingBottom")
    pad_left = node.get("paddingLeft")
    pad_right = node.get("paddingRight")
    if any(v is not None for v in [pad_top, pad_bottom, pad_left, pad_right]):
        props["padding"] = f"{pad_top or 0}px {pad_right or 0}px {pad_bottom or 0}px {pad_left or 0}px"

    # Size
    bbox = node.get("absoluteBoundingBox") or {}
    w = bbox.get("width")
    h = bbox.get("height")
    if w:
        props["/* width */"] = f"{w}px"
    if h:
        props["/* height */"] = f"{h}px"

    return name, props, ntype


def format_css(name, props):
    """Format as CSS custom properties block."""
    safe_name = name.lower().replace(" ", "-").replace("/", "-")
    lines = [f"/* {name} ({props.get('/* _type */', '')}) */"]
    lines.append(f".{safe_name} {{")
    for k, v in props.items():
        if not k.startswith("/* "):
            lines.append(f"  {k}: {v};")
    lines.append("}")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="Extract CSS from Figma nodes.json")
    p.add_argument("--nodes", required=True, help="Path to nodes.json from Figma REST API")
    p.add_argument("--out", default=None, help="Output CSS file path (default: stdout)")
    p.add_argument("--depth", type=int, default=5, help="Max recursion depth")
    args = p.parse_args()

    data = json.loads(Path(args.nodes).read_text(encoding="utf-8"))
    result = []

    def walk(node, d):
        if d > args.depth:
            return
        name, props, ntype = parse_node(node, d)
        if props:
            props["/* _type */"] = ntype
            result.append(format_css(name, props))
        for child in node.get("children", []):
            walk(child, d + 1)

    for nid, entry in data.get("nodes", {}).items():
        walk(entry.get("document", {}), 0)

    output = "\n\n".join(result)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote {len(result)} selectors to {args.out}")
    else:
        print(output)


if __name__ == "__main__":
    main()
