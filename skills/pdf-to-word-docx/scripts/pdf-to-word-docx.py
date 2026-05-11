# ---------------------------------------------------------------------------
# pdf to word
# Built on ComPDFKit Conversion SDK (https://www.compdf.com)
#
# © 2014-2026 PDF Technologies, Inc., a KDAN Company. All Rights Reserved.
#
# License: Commercial / Proprietary
# Contact: support@compdf.com
# Terms of Service: https://www.compdf.com/terms-of-service
# ---------------------------------------------------------------------------

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from ComPDFKitConversion import (
    ALL,
    ARABIC,
    AUTO,
    BINARY,
    BMP,
    BOX,
    CHINESE,
    CHINESE_TRA,
    COLOR,
    CYRILLIC,
    DEVANAGARI,
    ENGLISH,
    ESLAV,
    FLOW,
    FOR_DOCUMENT,
    FOR_PAGE,
    FOR_TABLE,
    GIF,
    GRAY,
    GREEK,
    INVALID_CHARACTER,
    INVALID_CHARACTER_AND_SCAN_PAGE,
    JAPANESE,
    JPEG,
    JPEG2000,
    JPG,
    KANNADA,
    KOREAN,
    LATIN,
    MULTIPLE_PAGE,
    MULTIPLE_PAGE_WITH_BOOKMARK,
    PNG,
    SCAN_PAGE,
    SINGLE_PAGE,
    SINGLE_PAGE_WITH_BOOKMARK,
    TAMIL,
    TELUGU,
    TGA,
    THAI,
    TIFF,
    UNKNOWN,
    WEBP,
    CPDFConversion,
    ConvertOptions,
    ErrorCode,
    LibraryManager,
)


EXCEL_WORKSHEET_OPTIONS = {
    "for-table": FOR_TABLE,
    "for-page": FOR_PAGE,
    "for-document": FOR_DOCUMENT,
}

PAGE_LAYOUT_MODES = {
    "box": BOX,
    "flow": FLOW,
}

HTML_OPTIONS = {
    "single-page": SINGLE_PAGE,
    "single-page-with-bookmark": SINGLE_PAGE_WITH_BOOKMARK,
    "multiple-page": MULTIPLE_PAGE,
    "multiple-page-with-bookmark": MULTIPLE_PAGE_WITH_BOOKMARK,
}

IMAGE_COLOR_MODES = {
    "color": COLOR,
    "gray": GRAY,
    "binary": BINARY,
}

IMAGE_TYPES = {
    "jpg": JPG,
    "jpeg": JPEG,
    "jpeg2000": JPEG2000,
    "png": PNG,
    "bmp": BMP,
    "tiff": TIFF,
    "tga": TGA,
    "gif": GIF,
    "webp": WEBP,
}

OCR_OPTIONS = {
    "invalid-character": INVALID_CHARACTER,
    "scan-page": SCAN_PAGE,
    "invalid-character-and-scan-page": INVALID_CHARACTER_AND_SCAN_PAGE,
    "all": ALL,
}

OCR_LANGUAGES = {
    "auto": AUTO,
    "chinese": CHINESE,
    "chinese-tra": CHINESE_TRA,
    "english": ENGLISH,
    "korean": KOREAN,
    "japanese": JAPANESE,
    "latin": LATIN,
    "devanagari": DEVANAGARI,
    "cyrillic": CYRILLIC,
    "arabic": ARABIC,
    "tamil": TAMIL,
    "telugu": TELUGU,
    "kannada": KANNADA,
    "thai": THAI,
    "greek": GREEK,
    "eslav": ESLAV,
}

DOCUMENT_AI_MODEL_URL = "https://download.compdf.com/skills/model/documentai.model"
DOCUMENT_AI_MODEL_ENV = "COMPDF_DOCUMENT_AI_MODEL"
DOCUMENT_AI_MODEL_RETRY_DELAYS = (2, 5, 10)

LICENSE_URL = "https://download.compdf.com/skills/license/license.xml"
LICENSE_RETRY_DELAYS = (2, 5, 10)

# Trial license usage limit
TRIAL_KEY_FINGERPRINT = "49a6fbe9b5966c54b43defaa1fc7d5fd418aefd9e3c63c74beb06c22c27c28ee"
TRIAL_USAGE_LIMIT = 200
PURCHASE_URL = "https://www.compdf.com/contact-sales"
SUPPORTED_FORMATS = {
    "word": "start_pdf_to_word",
    "excel": "start_pdf_to_excel",
    "ppt": "start_pdf_to_ppt",
    "html": "start_pdf_to_html",
    "rtf": "start_pdf_to_rtf",
    "image": "start_pdf_to_image",
    "txt": "start_pdf_to_txt",
    "json": "start_pdf_to_json",
    "markdown": "start_pdf_to_markdown",
    "csv": "start_pdf_to_excel",
}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".gif", ".webp", ".tga", ".jp2"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert PDF to Word, PPT, or Excel with ComPDFKitConversion."
    )
    parser.add_argument("format", choices=sorted(SUPPORTED_FORMATS))
    parser.add_argument("input_pdf")
    parser.add_argument("output_path")
    parser.add_argument("--source-type", choices=["auto", "pdf", "image"], default="auto")
    parser.add_argument("--password", default="", help="PDF password")
    parser.add_argument("--page-ranges", help='Page ranges like "1-3,5"')
    parser.add_argument("--enable-ocr", action="store_true")
    parser.add_argument(
        "--enable-ai-layout",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable AI layout analysis (default: True, use --no-enable-ai-layout to disable)",
    )
    parser.add_argument(
        "--contain-image",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include images in output (default: True, use --no-contain-image to disable)",
    )
    parser.add_argument(
        "--contain-annotation",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include annotations in output (default: True, use --no-contain-annotation to disable)",
    )
    parser.add_argument(
        "--contain-page-background-image",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include page background images (default: True, use --no-contain-page-background-image to disable)",
    )
    parser.add_argument("--formula-to-image", action="store_true")
    parser.add_argument("--transparent-text", action="store_true")
    parser.add_argument("--output-document-per-page", action="store_true")
    parser.add_argument(
        "--auto-create-folder",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Auto-create folder for multi-document output (default: True, use --no-auto-create-folder to disable)",
    )
    parser.add_argument(
        "--json-contain-table",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Include tables in JSON output (default: True, use --no-json-contain-table to disable)",
    )
    parser.add_argument(
        "--txt-table-format",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Format tables in TXT output (default: True, use --no-txt-table-format to disable)",
    )
    parser.add_argument(
        "--page-layout-mode",
        choices=sorted(PAGE_LAYOUT_MODES),
    )
    parser.add_argument("--font-name")
    parser.add_argument("--excel-all-content", action="store_true")
    parser.add_argument("--excel-csv-format", action="store_true")
    parser.add_argument(
        "--excel-worksheet-option",
        choices=sorted(EXCEL_WORKSHEET_OPTIONS),
    )
    parser.add_argument(
        "--html-option",
        choices=sorted(HTML_OPTIONS),
        help="HTML output mode (default: SDK default single-page)",
    )
    parser.add_argument(
        "--image-color-mode",
        choices=sorted(IMAGE_COLOR_MODES),
        help="Image color mode for image output (default: SDK default color)",
    )
    parser.add_argument("--image-path-enhance", action="store_true",
                        help="Enable image path enhancement")
    parser.add_argument("--image-scaling", type=float, default=1.0,
                        help="Image scaling factor (default: 1.0)")
    parser.add_argument(
        "--image-type",
        choices=sorted(IMAGE_TYPES),
        help="Image output format (default: SDK default jpg)",
    )
    parser.add_argument(
        "--ocr-option",
        choices=sorted(OCR_OPTIONS),
        help="OCR option scope (default: SDK default all)",
    )
    parser.add_argument(
        "--ocr-language",
        nargs="+",
        choices=sorted(OCR_LANGUAGES),
        default=["auto"],
        help="OCR language(s), can specify multiple (default: auto). "
             "Example: --ocr-language chinese english",
    )
    return parser


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


def resolve_resource_path(scripts_dir: Path) -> Path:
    return scripts_dir


def detect_source_type(input_path: Path, source_type: str) -> str:
    if source_type != "auto":
        return source_type
    if input_path.suffix.lower() == ".pdf":
        return "pdf"
    if input_path.suffix.lower() in IMAGE_SUFFIXES:
        return "image"
    raise RuntimeError(f"Cannot detect source type from file extension: {input_path}")


def get_converter_method_name(format_name: str) -> str:
    try:
        return SUPPORTED_FORMATS[format_name]
    except KeyError as exc:
        raise RuntimeError(f"Unsupported target format: {format_name}") from exc


def resolve_converter(format_name: str):
    method_name = get_converter_method_name(format_name)
    converter = getattr(CPDFConversion, method_name, None)
    if converter is None:
        raise RuntimeError(f"Current SDK does not provide converter method: {method_name}")
    return converter


def resolve_output_target(format_name: str, input_path: Path, output_path: Path) -> Path:
    if format_name != "html":
        return output_path
    if output_path.suffix.lower() == ".html":
        return output_path.with_suffix("")
    return output_path


def needs_document_ai_model(args: argparse.Namespace) -> bool:
    return bool(args.enable_ocr or args.enable_ai_layout)


def resolve_ocr_languages(args: argparse.Namespace) -> list:
    return [OCR_LANGUAGES[lang] for lang in args.ocr_language]


def download_file(url: str, destination: Path, timeout: int = 120) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=timeout) as response, destination.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)


def get_document_ai_model_path(scripts_dir: Path) -> Path:
    override = os.getenv(DOCUMENT_AI_MODEL_ENV)
    if override:
        return Path(override)
    return scripts_dir / "documentai.model"


def ensure_document_ai_model(scripts_dir: Path) -> Path:
    model_path = get_document_ai_model_path(scripts_dir)
    if model_path.is_file() and model_path.stat().st_size > 0:
        return model_path
    temp_path = model_path.with_suffix(model_path.suffix + ".part")
    last_error: Exception | None = None
    for attempt in range(len(DOCUMENT_AI_MODEL_RETRY_DELAYS) + 1):
        try:
            print(f"documentai.model not found, downloading from {DOCUMENT_AI_MODEL_URL}...", file=sys.stderr)
            if temp_path.exists():
                temp_path.unlink()
            download_file(DOCUMENT_AI_MODEL_URL, temp_path)
            if not temp_path.is_file() or temp_path.stat().st_size == 0:
                raise RuntimeError("Downloaded documentai.model is empty")
            temp_path.replace(model_path)
            break
        except Exception as exc:
            last_error = exc
            if temp_path.exists():
                temp_path.unlink()
            if attempt >= len(DOCUMENT_AI_MODEL_RETRY_DELAYS):
                raise RuntimeError(f"Failed to prepare documentai.model: {exc}") from exc
            time.sleep(DOCUMENT_AI_MODEL_RETRY_DELAYS[attempt])
    return model_path


def configure_options(args: argparse.Namespace) -> ConvertOptions:
    options = ConvertOptions()
    if args.page_layout_mode is not None:
        options.page_layout_mode = PAGE_LAYOUT_MODES[args.page_layout_mode]
    if args.enable_ocr:
        options.enable_ocr = True
    # CLI defaults now match SDK ConvertOptions() defaults:
    #   enable_ai_layout=True, contain_image=True, contain_annotation=True,
    #   contain_page_background_image=True, auto_create_folder=True,
    #   json_contain_table=True, txt_table_format=True
    options.enable_ai_layout = bool(args.enable_ai_layout)
    options.contain_image = bool(args.contain_image)
    options.contain_annotation = bool(args.contain_annotation)
    options.contain_page_background_image = bool(args.contain_page_background_image)
    options.auto_create_folder = bool(args.auto_create_folder)
    options.json_contain_table = bool(args.json_contain_table)
    options.txt_table_format = bool(args.txt_table_format)
    if args.formula_to_image:
        options.formula_to_image = True
    if args.transparent_text:
        options.transparent_text = True
    if args.output_document_per_page:
        options.output_document_per_page = True
    if args.excel_all_content:
        options.excel_all_content = True
    if args.excel_csv_format or args.format == "csv":
        options.excel_csv_format = True
    if args.excel_worksheet_option is not None:
        options.excel_worksheet_option = EXCEL_WORKSHEET_OPTIONS[args.excel_worksheet_option]
    if args.page_ranges:
        options.page_ranges = args.page_ranges
    if args.font_name:
        options.font_name = args.font_name
    if args.html_option is not None:
        options.html_option = HTML_OPTIONS[args.html_option]
    if args.image_color_mode is not None:
        options.image_color_mode = IMAGE_COLOR_MODES[args.image_color_mode]
    if args.image_path_enhance:
        options.image_path_enhance = True
    options.image_scaling = args.image_scaling
    if args.image_type is not None:
        options.image_type = IMAGE_TYPES[args.image_type]
    if args.ocr_option is not None:
        options.ocr_option = OCR_OPTIONS[args.ocr_option]
    return options


def read_license_key(license_path: Path) -> str:
    try:
        root = ET.fromstring(license_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to read license.xml: {exc}") from exc
    key_text = root.findtext("key")
    if key_text is None or not key_text.strip():
        raise RuntimeError(f"Missing key field in license.xml: {license_path}")
    return key_text.strip()


def is_trial_license(license_key: str) -> bool:
    return hashlib.sha256(license_key.encode()).hexdigest() == TRIAL_KEY_FINGERPRINT


def get_usage_file() -> Path:
    return Path.home() / ".pdf-to-word-docx" / "usage.json"


def read_usage_count() -> int:
    usage_file = get_usage_file()
    if not usage_file.is_file():
        return 0
    try:
        data = json.loads(usage_file.read_text(encoding="utf-8"))
        return int(data.get("count", 0))
    except (json.JSONDecodeError, ValueError, OSError):
        return 0


def increment_usage_count() -> int:
    usage_file = get_usage_file()
    current = read_usage_count()
    new_count = current + 1
    usage_file.parent.mkdir(parents=True, exist_ok=True)
    usage_file.write_text(
        json.dumps({"count": new_count}, indent=2),
        encoding="utf-8",
    )
    return new_count


def check_trial_usage_limit(license_key: str) -> None:
    if not is_trial_license(license_key):
        return
    count = read_usage_count()
    remaining = TRIAL_USAGE_LIMIT - count
    if remaining <= 0:
        raise RuntimeError(
            f"Trial license usage limit reached ({TRIAL_USAGE_LIMIT} conversions). "
            f"Please purchase a license at: {PURCHASE_URL}"
        )


def ensure_license_file(scripts_dir: Path) -> Path:
    license_path = scripts_dir / "license.xml"
    if license_path.is_file() and license_path.stat().st_size > 0:
        return license_path
    temp_path = license_path.with_suffix(license_path.suffix + ".part")
    last_error: Exception | None = None
    for attempt in range(len(LICENSE_RETRY_DELAYS) + 1):
        try:
            print(f"license.xml not found, downloading from {LICENSE_URL}...", file=sys.stderr)
            if temp_path.exists():
                temp_path.unlink()
            download_file(LICENSE_URL, temp_path, timeout=30)
            if not temp_path.is_file() or temp_path.stat().st_size == 0:
                raise RuntimeError("Downloaded license.xml is empty")
            temp_path.replace(license_path)
            break
        except Exception as exc:
            last_error = exc
            if temp_path.exists():
                temp_path.unlink()
            if attempt >= len(LICENSE_RETRY_DELAYS):
                raise RuntimeError(f"Failed to download license.xml: {exc}") from exc
            time.sleep(LICENSE_RETRY_DELAYS[attempt])
    return license_path


def verify_license(scripts_dir: Path) -> str:
    license_path = ensure_license_file(scripts_dir)
    license_key = read_license_key(license_path)
    error = LibraryManager.license_verify(license_key, "", "")
    if error != ErrorCode.SUCCESS:
        if is_trial_license(license_key):
            raise RuntimeError(
                f"Trial license expired or invalid: {error.name} ({int(error)}). "
                f"Please purchase a license at: {PURCHASE_URL}"
            )
        raise RuntimeError(f"License verification failed: {error.name} ({int(error)})")
    return license_key


def convert(args: argparse.Namespace) -> ErrorCode:
    scripts_dir = Path(__file__).resolve().parent
    input_pdf = Path(args.input_pdf)
    if not input_pdf.is_file():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf}")
    source_type = detect_source_type(input_pdf, args.source_type)

    # --- Intelligent defaults ---
    # Image input: auto-enable OCR so text extraction works
    if source_type == "image" and not args.enable_ocr:
        args.enable_ocr = True
        print("Auto-enabled OCR for image input.", file=sys.stderr)
    # HTML output: default to box layout for better rendering fidelity
    if args.format == "html" and args.page_layout_mode is None:
        args.page_layout_mode = "box"
        print("Auto-set page layout mode to BOX for HTML output.", file=sys.stderr)

    output_path = Path(args.output_path)
    target_path = resolve_output_target(args.format, input_pdf, output_path)
    if target_path.parent and not target_path.parent.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
    if args.format == "html":
        target_path.mkdir(parents=True, exist_ok=True)

    resource_path = resolve_resource_path(scripts_dir)
    LibraryManager.initialize(str(resource_path))

    license_key = verify_license(scripts_dir)
    check_trial_usage_limit(license_key)
    options = configure_options(args)
    if needs_document_ai_model(args):
        model_path = ensure_document_ai_model(scripts_dir)
        ocr_langs = resolve_ocr_languages(args)
        model_error = LibraryManager.set_document_ai_model(str(model_path), ocr_langs)
        if model_error != ErrorCode.SUCCESS:
            raise RuntimeError(f"Document AI model initialization failed: {model_error.name} ({int(model_error)})")
        if args.enable_ocr:
            LibraryManager.set_ocr_language(ocr_langs)

    converter = resolve_converter(args.format)
    result = converter(
        str(input_pdf),
        args.password,
        str(target_path),
        options,
    )

    if result == ErrorCode.SUCCESS and is_trial_license(license_key):
        new_count = increment_usage_count()
        remaining = TRIAL_USAGE_LIMIT - new_count
        if remaining > 0:
            print(
                f"Trial license: {new_count}/{TRIAL_USAGE_LIMIT} conversions used, "
                f"{remaining} remaining.",
                file=sys.stderr,
            )
        else:
            print(
                f"Trial license: all {TRIAL_USAGE_LIMIT} conversions used. "
                f"Please purchase a license at: {PURCHASE_URL}",
                file=sys.stderr,
            )

    return result


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        error = convert(args)
        if error != ErrorCode.SUCCESS:
            print(f"Conversion failed: {error.name} ({int(error)})", file=sys.stderr)
            return int(error)
        print(f"Conversion succeeded: {args.output_path}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    finally:
        try:
            LibraryManager.release()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
