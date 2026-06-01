#!/usr/bin/env python3
"""Build ASS subtitles with adaptive sizing and pre-wrapping.

This script turns a subtitle source into an ASS subtitle file.
Supported source formats:
- JSON subtitle event list
- SRT subtitle file

It applies the default PonyFlash subtitle style, scales values to the
target output size, and pre-wraps text before ffmpeg/libass renders it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from PIL import ImageFont  # type: ignore
except Exception:  # pragma: no cover - fallback path is intentional
    ImageFont = None


LATIN_FONT_NAME = "Noto Sans CJK SC"
CJK_FONT_NAME = "Noto Sans CJK SC"
DEFAULT_PRIMARY_COLOUR = "&H00FFFFFF"
DEFAULT_OUTLINE_COLOUR = "&H00000000"
DEFAULT_BACK_COLOUR = "&H00000000"


def is_cjk(char: str) -> bool:
    codepoint = ord(char)
    return (
        0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xF900 <= codepoint <= 0xFAFF
        or 0x3040 <= codepoint <= 0x30FF
        or 0xAC00 <= codepoint <= 0xD7AF
    )


def is_fullwidth_punctuation(char: str) -> bool:
    codepoint = ord(char)
    return (0x3000 <= codepoint <= 0x303F) or (0xFF00 <= codepoint <= 0xFFEF)


def load_font(font_path: Path, size: int) -> Any | None:
    if ImageFont is None:
        return None

    try:
        return ImageFont.truetype(str(font_path), size=size)
    except Exception:
        return None


class TextMeasurer:
    def __init__(self, latin_font_path: Path, cjk_font_path: Path, font_size: int):
        self.font_size = font_size
        self.latin_font = load_font(latin_font_path, font_size)
        self.cjk_font = load_font(cjk_font_path, font_size)

    def char_width(self, char: str) -> float:
        if not char:
            return 0.0

        if self.latin_font or self.cjk_font:
            font = self.cjk_font if is_cjk(char) or is_fullwidth_punctuation(char) else self.latin_font
            if font is None:
                font = self.cjk_font or self.latin_font
            if font is not None:
                try:
                    return float(font.getlength(char))
                except Exception:
                    bbox = font.getbbox(char)
                    return float(max(0, bbox[2] - bbox[0]))

        if char.isspace():
            return self.font_size * 0.33
        if is_cjk(char):
            return self.font_size * 1.0
        if is_fullwidth_punctuation(char):
            return self.font_size * 0.9
        if char.isascii() and char.isalnum():
            return self.font_size * 0.56
        if char.isascii():
            return self.font_size * 0.38
        return self.font_size * 0.8

    @lru_cache(maxsize=4096)
    def text_width(self, text: str) -> float:
        return sum(self.char_width(char) for char in text)


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char.isspace():
            start = index
            while index < len(text) and text[index].isspace():
                index += 1
            tokens.append(text[start:index])
            continue
        if char.isascii() and not char.isspace():
            start = index
            while index < len(text) and text[index].isascii() and not text[index].isspace():
                index += 1
            tokens.append(text[start:index])
            continue
        tokens.append(char)
        index += 1
    return tokens


def split_token_to_fit(token: str, max_width: float, measurer: TextMeasurer) -> list[str]:
    parts: list[str] = []
    current = ""
    for char in token:
        proposal = f"{current}{char}"
        if current and measurer.text_width(proposal) > max_width:
            parts.append(current)
            current = char
        else:
            current = proposal
    if current:
        parts.append(current)
    return parts or [token]


def wrap_text(text: str, max_width: float, measurer: TextMeasurer) -> list[str]:
    wrapped_lines: list[str] = []
    for paragraph in text.splitlines():
        tokens = tokenize(paragraph)
        lines: list[str] = []
        current = ""

        def push_current() -> None:
            nonlocal current
            if current.strip():
                lines.append(current.rstrip())
            current = ""

        for token in tokens:
            if token.isspace():
                if current:
                    current += " "
                continue

            candidate = token if not current else f"{current}{token}"
            if measurer.text_width(candidate) <= max_width:
                current = candidate
                continue

            if current:
                push_current()

            token = token.lstrip()
            if not token:
                continue

            if measurer.text_width(token) <= max_width:
                current = token
                continue

            for part in split_token_to_fit(token, max_width, measurer):
                if measurer.text_width(part) <= max_width:
                    if current:
                        push_current()
                    current = part
                else:
                    current = part

        push_current()
        if lines:
            wrapped_lines.extend(lines)
    return wrapped_lines


def ass_escape(text: str) -> str:
    return (
        text.replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
    )


def font_name_for_char(char: str, previous_font: str | None = None) -> str:
    if char.isspace():
        return previous_font or LATIN_FONT_NAME
    if is_cjk(char) or is_fullwidth_punctuation(char):
        return CJK_FONT_NAME
    return LATIN_FONT_NAME


def stylize_line(line: str) -> str:
    if not line:
        return ""

    chunks: list[tuple[str, str]] = []
    current_font: str | None = None
    current_text = ""

    for char in line:
        target_font = font_name_for_char(char, current_font)
        if current_font is None or target_font == current_font:
            current_font = target_font
            current_text += char
            continue

        chunks.append((current_font, current_text))
        current_font = target_font
        current_text = char

    if current_font is not None and current_text:
        chunks.append((current_font, current_text))

    return "".join(r"{\fn" + font_name + "}" + ass_escape(text) for font_name, text in chunks)


def ratio_or_default(width: int, height: int) -> float:
    return 0.90


def build_style(args: argparse.Namespace) -> dict[str, int]:
    short_edge = min(args.video_width, args.video_height)
    font_size = args.font_size or round(short_edge * 0.0556)
    return {
        "font_size": font_size,
        "margin_v": args.margin_v or round(args.video_height * 0.0963),
        "margin_l": args.margin_l or round(args.video_width * 0.0625),
        "margin_r": args.margin_r or round(args.video_width * 0.0625),
        "outline": args.outline if args.outline is not None else max(1, round(font_size * 0.0167)),
        "shadow": args.shadow if args.shadow is not None else 1,
        "blur": args.blur if args.blur is not None else 1,
    }


def parse_srt_timestamp(timestamp: str) -> str:
    match = re.match(r"^(\d{2}):(\d{2}):(\d{2})[,.](\d{1,3})$", timestamp.strip())
    if not match:
        raise SystemExit(f"Invalid SRT timestamp: {timestamp}")

    hours, minutes, seconds, millis = match.groups()
    centiseconds = round(int(millis.ljust(3, "0")[:3]) / 10)
    if centiseconds == 100:
        centiseconds = 99
    return f"{int(hours)}:{minutes}:{seconds}.{centiseconds:02d}"


def read_events_from_json(events_json: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(events_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON subtitle event file: {exc}") from exc

    if not isinstance(data, list):
        raise SystemExit("Subtitle event file must be a JSON array.")

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise SystemExit(f"Subtitle event #{index + 1} must be an object.")
        if "start" not in item or "end" not in item or "text" not in item:
            raise SystemExit(f"Subtitle event #{index + 1} must include start, end, and text.")
        normalized.append(item)
    return normalized


def read_events_from_srt(subtitle_file: Path) -> list[dict[str, Any]]:
    content = subtitle_file.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    if not content:
        return []

    events: list[dict[str, Any]] = []
    blocks = re.split(r"\n\s*\n", content)
    for index, block in enumerate(blocks, start=1):
        lines = [line.rstrip() for line in block.split("\n") if line.strip() != ""]
        if not lines:
            continue

        if re.fullmatch(r"\d+", lines[0]):
            lines = lines[1:]

        if not lines or "-->" not in lines[0]:
            raise SystemExit(f"Invalid SRT block #{index}: missing timestamp line.")

        timestamp_line = lines[0]
        text_lines = lines[1:]
        if not text_lines:
            raise SystemExit(f"Invalid SRT block #{index}: missing subtitle text.")

        start_raw, end_raw = [part.strip() for part in timestamp_line.split("-->", 1)]
        events.append(
            {
                "start": parse_srt_timestamp(start_raw),
                "end": parse_srt_timestamp(end_raw),
                "text": "\n".join(text_lines),
            }
        )

    return events


def read_events(source_path: Path) -> list[dict[str, Any]]:
    suffix = source_path.suffix.lower()
    if suffix == ".json":
        return read_events_from_json(source_path)
    if suffix == ".srt":
        return read_events_from_srt(source_path)
    raise SystemExit(f"Unsupported subtitle source format: {source_path.suffix}")


def build_ass(args: argparse.Namespace) -> str:
    style = build_style(args)
    source_path = Path(args.subtitle_file or args.events_json)
    events = read_events(source_path)

    max_width_ratio = args.wrap_width_ratio or ratio_or_default(args.video_width, args.video_height)
    max_text_width = args.video_width * max_width_ratio

    measurer = TextMeasurer(
        Path(args.latin_font_file),
        Path(args.cjk_font_file),
        style["font_size"],
    )

    dialogue_lines: list[str] = []
    for event in events:
        raw_text = str(event["text"])
        wrapped_lines = wrap_text(raw_text, max_text_width, measurer)
        wrapped = r"\N".join(stylize_line(line) for line in wrapped_lines) or stylize_line(raw_text)

        event_blur = event.get("blur")
        if event_blur is not None and int(event_blur) != style["blur"]:
            wrapped = r"{\blur" + str(int(event_blur)) + "}" + wrapped

        dialogue_lines.append(
            "Dialogue: 0,{start},{end},Default,,0,0,0,,{text}".format(
                start=event["start"],
                end=event["end"],
                text=wrapped,
            )
        )

    return "\n".join(
        [
            "[Script Info]",
            "ScriptType: v4.00+",
            f"PlayResX: {args.video_width}",
            f"PlayResY: {args.video_height}",
            "WrapStyle: 2",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            (
                "Style: Default,{font_name},{font_size},{primary_colour},{primary_colour},"
                "{outline_colour},{back_colour},0,0,0,0,100,100,0,0,1,{outline},{shadow},2,{margin_l},{margin_r},{margin_v},1"
            ).format(
                font_name=LATIN_FONT_NAME,
                font_size=style["font_size"],
                primary_colour=DEFAULT_PRIMARY_COLOUR,
                outline_colour=DEFAULT_OUTLINE_COLOUR,
                back_colour=DEFAULT_BACK_COLOUR,
                outline=style["outline"],
                shadow=style["shadow"],
                margin_l=style["margin_l"],
                margin_r=style["margin_r"],
                margin_v=style["margin_v"],
            ),
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
            *dialogue_lines,
            "",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build ASS subtitles with adaptive wrapping.")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--subtitle-file", help="Subtitle source file (.srt or .json).")
    source_group.add_argument("--events-json", help="Deprecated alias for JSON subtitle events.")
    parser.add_argument("--output-ass", required=True, help="Output ASS file path.")
    parser.add_argument("--video-width", type=int, required=True, help="Target output video width.")
    parser.add_argument("--video-height", type=int, required=True, help="Target output video height.")
    parser.add_argument("--latin-font-file", required=True, help="Primary latin font file path.")
    parser.add_argument("--cjk-font-file", required=True, help="CJK fallback font file path.")
    parser.add_argument("--wrap-width-ratio", type=float, help="Override max text width ratio.")
    parser.add_argument("--font-size", type=int, help="Override computed font size.")
    parser.add_argument("--margin-v", type=int, help="Override computed bottom margin.")
    parser.add_argument("--margin-l", type=int, help="Override computed left margin.")
    parser.add_argument("--margin-r", type=int, help="Override computed right margin.")
    parser.add_argument("--outline", type=int, help="Override computed outline width.")
    parser.add_argument("--shadow", type=int, help="Override computed shadow value.")
    parser.add_argument("--blur", type=int, help="Override default blur value.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ass = build_ass(args)
    output_path = Path(args.output_ass)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=output_path.parent,
        prefix=f".{output_path.stem}.",
        suffix=f"{output_path.suffix}.tmp",
        delete=False,
    ) as handle:
        handle.write(ass)
        temp_path = Path(handle.name)
    temp_path.replace(output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
