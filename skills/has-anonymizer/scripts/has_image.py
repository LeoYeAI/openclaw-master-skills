#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "ultralytics>=8.3.0",
#     "opencv-python-headless>=4.8.0",
#     "pillow>=10.0.0",
# ]
# ///
"""HaS Image — Privacy anonymization for images via YOLO11 instance segmentation.

Usage:
    has-image scan --image photo.jpg [--type face] [--type id_card] [--conf 0.5]
    has-image hide --image photo.jpg [--output masked.jpg] [--method mosaic]
    has-image hide --dir ./photos/ [--output-dir ./.has/masked/]

See `has-image <command> --help` for details.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Category definitions (21 classes)
# ---------------------------------------------------------------------------

CATEGORIES: list[dict[str, str]] = [
    {"id": "0",  "name": "biometric_face",        "zh": "人脸"},
    {"id": "1",  "name": "biometric_fingerprint",  "zh": "指纹"},
    {"id": "2",  "name": "biometric_palmprint",    "zh": "掌纹"},
    {"id": "3",  "name": "id_card",                "zh": "身份证"},
    {"id": "4",  "name": "hk_macau_permit",        "zh": "港澳通行证"},
    {"id": "5",  "name": "passport",               "zh": "护照"},
    {"id": "6",  "name": "employee_badge",         "zh": "工牌"},
    {"id": "7",  "name": "license_plate",          "zh": "车牌"},
    {"id": "8",  "name": "bank_card",              "zh": "银行卡"},
    {"id": "9",  "name": "physical_key",           "zh": "钥匙"},
    {"id": "10", "name": "receipt",                 "zh": "收据"},
    {"id": "11", "name": "shipping_label",          "zh": "快递单"},
    {"id": "12", "name": "official_seal",           "zh": "公章"},
    {"id": "13", "name": "whiteboard",              "zh": "白板"},
    {"id": "14", "name": "sticky_note",             "zh": "便签"},
    {"id": "15", "name": "mobile_screen",           "zh": "手机屏幕"},
    {"id": "16", "name": "monitor_screen",          "zh": "显示器屏幕"},
    {"id": "17", "name": "medical_wristband",       "zh": "医用腕带"},
    {"id": "18", "name": "qr_code",                 "zh": "二维码"},
    {"id": "19", "name": "barcode",                 "zh": "条形码"},
    {"id": "20", "name": "paper",                   "zh": "纸张"},
]

# Build lookup helpers
_ID_TO_CAT = {int(c["id"]): c for c in CATEGORIES}
_NAME_TO_ID = {c["name"]: int(c["id"]) for c in CATEGORIES}
_ZH_TO_ID = {c["zh"]: int(c["id"]) for c in CATEGORIES}
ALL_NAMES = [c["name"] for c in CATEGORIES]
SCHEMA_VERSION = "1"

# Categories with structured encoding patterns that need adaptive mosaic strength.
# Default mosaic block size (~15px) can align with the encoding module size,
# leaving the code machine-readable after masking.
_ADAPTIVE_MOSAIC_CATEGORIES: set[int] = {
    _NAME_TO_ID["qr_code"],   # 18
    _NAME_TO_ID["barcode"],   # 19
}


@dataclass(frozen=True)
class CLIError(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return self.message


class StructuredArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that reports machine-readable errors."""

    def error(self, message: str) -> None:
        raise CLIError("invalid_arguments", message)


def _emit_json(payload: dict[str, Any], *, stream=None) -> None:
    target = stream or sys.stdout
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), file=target)


def _error_payload(code: str, message: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "error": {
            "code": code,
            "message": message,
        },
    }


def _absolute_path(path: Path | str) -> str:
    """Return a stable absolute path string without resolving symlink targets."""
    return str(Path(path).expanduser().absolute())


def _resolve_types(type_values: list[str] | None) -> set[int] | None:
    """Parse repeated --type flags into a set of class IDs, or None (= all)."""
    if not type_values:
        return None
    ids: set[int] = set()
    for raw_token in type_values:
        token = raw_token.strip()
        if not token:
            _die("invalid_type", "--type values must be non-empty strings.")
        # Try numeric ID
        if token.isdigit():
            cid = int(token)
            if cid in _ID_TO_CAT:
                ids.add(cid)
            else:
                _die("unknown_type", f"Unknown class ID: {cid}")
        # Try english name
        elif token in _NAME_TO_ID:
            ids.add(_NAME_TO_ID[token])
        # Try chinese name
        elif token in _ZH_TO_ID:
            ids.add(_ZH_TO_ID[token])
        # Try partial match (e.g. "face" -> "biometric_face")
        else:
            matches = [n for n in ALL_NAMES if token in n]
            if len(matches) == 1:
                ids.add(_NAME_TO_ID[matches[0]])
            elif len(matches) > 1:
                _die("ambiguous_type", f"Ambiguous type '{token}', matches: {matches}")
            else:
                _die(
                    "unknown_type",
                    f"Unknown type '{token}'. "
                    f"Valid types: {', '.join(ALL_NAMES)}"
                )
    return ids if ids else None


def _die(code: str, msg: str) -> None:
    raise CLIError(code, msg)


def _verbose(message: str) -> None:
    """Emit a progress message to stderr when --verbose is active."""
    if os.environ.get("HAS_IMAGE_VERBOSE") == "1":
        print(message, file=sys.stderr)


def _is_within_directory(path: Path, directory: Path) -> bool:
    """Return whether `path` resolves within `directory`."""
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------

_MODEL = None
_MODEL_LOCK = __import__("threading").Lock()
_DEFAULT_MODEL_PATH = os.path.expanduser(
    "~/.openclaw/tools/has-anonymizer/models/sensitive_seg_best.pt"
)


def _load_model(model_path: str | None = None):
    """Load YOLO11 segmentation model (lazy singleton, thread-safe)."""
    global _MODEL
    if _MODEL is not None:
        return _MODEL

    with _MODEL_LOCK:
        # Double-check after acquiring the lock.
        if _MODEL is not None:
            return _MODEL

        from ultralytics import YOLO

        path = model_path or os.environ.get("HAS_IMAGE_MODEL", _DEFAULT_MODEL_PATH)
        if not os.path.isfile(path):
            _die(
                "model_not_found",
                f"Model file not found: {path}\n"
                f"Download it via: openclaw install has-anonymizer "
                f"(or manually from HuggingFace)"
            )
        _verbose(f"Loading image model from {path}...")
        _MODEL = YOLO(path)
        _verbose("Image model loaded.")
        return _MODEL


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------

def _run_detection(
    image_path: str,
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
) -> dict[str, Any]:
    """Run YOLO detection on a single image and return structured results."""
    import cv2

    model = _load_model(model_path)
    results = model(image_path, conf=conf, verbose=False)

    # Phase 1: Collect ALL YOLO detections (unfiltered) for cv2 correction
    yolo_regions: list[tuple[int, list[int], dict[str, Any]]] = []
    if results and results[0].boxes is not None:
        result = results[0]
        for index, bbox, det in _iter_detection_regions(result, type_ids=None):
            yolo_regions.append((index, bbox, det))

    # Phase 2: cv2 code detection → correct YOLO + find new codes
    image = cv2.imread(image_path)
    cv2_codes = _run_cv2_code_detection(image) if image is not None else []
    new_cv2_dets = _apply_cv2_corrections(cv2_codes, yolo_regions)

    # Phase 3: Apply --type filtering AFTER correction
    detections = []
    summary: dict[str, int] = {}

    for _, _, det in yolo_regions:
        cls_id = _NAME_TO_ID.get(det["category"])
        if type_ids is not None and cls_id not in type_ids:
            continue
        detections.append(det)
        summary[det["category"]] = summary.get(det["category"], 0) + 1

    for det in new_cv2_dets:
        cls_id = _NAME_TO_ID.get(det["category"])
        if type_ids is not None and cls_id not in type_ids:
            continue
        detections.append(det)
        summary[det["category"]] = summary.get(det["category"], 0) + 1

    return {"detections": detections, "summary": summary}


def _iter_detection_regions(result, type_ids: set[int] | None):
    """Yield filtered detection metadata shared by scan/hide."""

    if result.boxes is None:
        return

    for index, box in enumerate(result.boxes):
        cls_id = int(box.cls[0].item())
        if type_ids is not None and cls_id not in type_ids:
            continue

        cat = _ID_TO_CAT.get(cls_id, {"name": f"unknown_{cls_id}", "zh": "未知"})
        confidence = float(box.conf[0].item())
        bbox = [int(x) for x in box.xyxy[0].tolist()]
        has_mask = result.masks is not None and index < len(result.masks.data)

        yield index, bbox, {
            "category": cat["name"],
            "category_zh": cat["zh"],
            "confidence": round(confidence, 4),
            "bbox": bbox,
            "has_mask": has_mask,
        }


def _build_detection_mask(result, index: int, bbox: list[int], image_shape: tuple[int, int]):
    """Build a segmentation or bbox mask for a detection."""

    import cv2
    import numpy as np

    h, w = image_shape
    has_mask = result.masks is not None and index < len(result.masks.data)
    if has_mask:
        seg_mask = result.masks.data[index].cpu().numpy()
        return cv2.resize(seg_mask, (w, h), interpolation=cv2.INTER_NEAREST).astype(np.uint8)

    mask = np.zeros((h, w), dtype=np.uint8)
    x1, y1, x2, y2 = bbox
    mask[y1:y2, x1:x2] = 1
    return mask


def _resolve_output_path(image_path: str, output_path: str | None) -> str:
    """Resolve the output path and refuse to overwrite the source image."""

    image = Path(image_path)
    target = Path(output_path) if output_path else image.parent / ".has" / "masked" / f"{image.stem}{image.suffix}"

    if target.resolve(strict=False) == image.resolve(strict=False):
        _die("refusing_overwrite", "Refusing to overwrite the original image; choose a different output path")

    return _absolute_path(target)


# ---------------------------------------------------------------------------
# Masking strategies
# ---------------------------------------------------------------------------

def _apply_mosaic(image, mask, strength: int):
    """Apply mosaic (pixelation) to masked region."""
    import cv2
    import numpy as np

    h, w = image.shape[:2]
    block = max(strength, 2)

    # Downscale then upscale to create pixelation
    small = cv2.resize(image, (max(w // block, 1), max(h // block, 1)),
                       interpolation=cv2.INTER_LINEAR)
    mosaic = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

    # Apply only within mask
    mask_bool = mask.astype(bool)
    image[mask_bool] = mosaic[mask_bool]
    return image


def _apply_blur(image, mask, strength: int):
    """Apply Gaussian blur to masked region."""
    import cv2
    import numpy as np

    # Kernel size must be odd; ensure a monotonic relationship with strength
    ksize = max(strength | 1, 3)

    blurred = cv2.GaussianBlur(image, (ksize, ksize), 0)
    mask_bool = mask.astype(bool)
    image[mask_bool] = blurred[mask_bool]
    return image


def _apply_fill(image, mask, color: tuple[int, int, int]):
    """Apply solid color fill to masked region."""
    mask_bool = mask.astype(bool)
    image[mask_bool] = color
    return image


def _adaptive_mosaic_strength(bbox: list[int], base_strength: int) -> int:
    """Calculate adaptive mosaic strength for structured-code categories.

    Ensures the mosaic block size is large enough to destroy encoding
    structure while preserving visual recognizability of the region.
    Formula: max(base_strength, bbox_short_side // 10, 20)
    """
    bbox_w = bbox[2] - bbox[0]
    bbox_h = bbox[3] - bbox[1]
    bbox_dim = min(bbox_w, bbox_h)
    return max(base_strength, bbox_dim // 10, 20)


def _verify_code_destroyed(image, bbox: list[int], cls_id: int | None = None) -> bool:
    """Check that a QR/barcode region is no longer machine-readable.

    Crops the bbox region (with small padding) and runs the appropriate
    detector:  cv2.QRCodeDetector for QR codes, cv2.barcode.BarcodeDetector
    for barcodes.  When cls_id is None, both detectors are tried.
    Returns True if the code is destroyed (good), False if still readable (bad).
    Cost: ~15ms per region — negligible vs. YOLO inference.
    """
    import cv2

    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox
    pad = 10
    roi = image[max(y1 - pad, 0):min(y2 + pad, h),
                max(x1 - pad, 0):min(x2 + pad, w)].copy()

    barcode_id = _NAME_TO_ID.get("barcode")  # 19

    # Check QR (unless explicitly barcode-only)
    if cls_id != barcode_id:
        qr_det = cv2.QRCodeDetector()
        ok, info, _, _ = qr_det.detectAndDecodeMulti(roi)
        if ok and any(info):
            return False

    # Check barcode (unless explicitly qr-only)
    if cls_id is None or cls_id == barcode_id:
        try:
            bar_det = cv2.barcode.BarcodeDetector()
            ok, decoded, _, _ = bar_det.detectAndDecodeMulti(roi)
            if ok and decoded is not None and any(decoded):
                return False
        except Exception:
            pass  # BarcodeDetector not available in older OpenCV builds

    return True


def _bbox_iou(b1: list[int], b2: list[int]) -> float:
    """Compute Intersection-over-Union between two [x1,y1,x2,y2] bboxes."""
    x1 = max(b1[0], b2[0])
    y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2])
    y2 = min(b1[3], b2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
    area2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
    union = area1 + area2 - inter
    return inter / union if union > 0 else 0.0


def _run_cv2_code_detection(image) -> list[tuple[list[int], str]]:
    """Detect QR codes and barcodes using OpenCV's algorithmic detectors.

    Returns a list of (bbox, category_name) tuples.  Runs both
    cv2.QRCodeDetector and cv2.barcode.BarcodeDetector.
    Cost: ~35-165 ms depending on image size.
    """
    import cv2

    codes: list[tuple[list[int], str]] = []

    # QR codes
    try:
        qr_det = cv2.QRCodeDetector()
        found, points = qr_det.detectMulti(image)
        if found and points is not None:
            for i in range(len(points)):
                pts = points[i].astype(int)
                bbox = [
                    int(pts[:, 0].min()), int(pts[:, 1].min()),
                    int(pts[:, 0].max()), int(pts[:, 1].max()),
                ]
                codes.append((bbox, "qr_code"))
    except Exception as exc:
        _verbose(f"cv2 QR detection error: {exc}")

    # Barcodes
    try:
        bar_det = cv2.barcode.BarcodeDetector()
        found, _decoded, _types, points = bar_det.detectAndDecodeMulti(image)
        if found and points is not None:
            for i in range(len(points)):
                pts = points[i].astype(int)
                bbox = [
                    int(pts[:, 0].min()), int(pts[:, 1].min()),
                    int(pts[:, 0].max()), int(pts[:, 1].max()),
                ]
                codes.append((bbox, "barcode"))
    except Exception as exc:
        _verbose(f"cv2 barcode detection error: {exc}")

    return codes


def _apply_cv2_corrections(
    cv2_codes: list[tuple[list[int], str]],
    yolo_regions: list[tuple[int, list[int], dict[str, Any]]],
    iou_threshold: float = 0.3,
) -> list[dict[str, Any]]:
    """Use cv2 code detections to correct YOLO and find missed codes.

    Two effects:
    1. **Correction**: If a cv2 code overlaps (IoU > threshold) a YOLO
       detection that is NOT already a code category, the YOLO detection's
       category is corrected in-place.  A ``corrected_from`` field is added.
    2. **New detections**: cv2 codes that don't overlap ANY YOLO detection
       are returned as new detection dicts (``cv2_fallback: true``).

    Corrections happen BEFORE ``--type`` filtering so the user gets the
    behaviour they expect from their ``--type`` flags.
    """
    if not cv2_codes:
        return []

    # Track which cv2 codes matched an existing YOLO region
    cv2_matched: set[int] = set()

    for cv2_idx, (cv2_bbox, cv2_cat_name) in enumerate(cv2_codes):
        for _region_idx, (_yolo_index, yolo_bbox, yolo_det) in enumerate(yolo_regions):
            if _bbox_iou(cv2_bbox, yolo_bbox) <= iou_threshold:
                continue
            cv2_matched.add(cv2_idx)
            # Only correct if YOLO's category is NOT already a code
            yolo_cat_id = _NAME_TO_ID.get(yolo_det["category"])
            if yolo_cat_id in _ADAPTIVE_MOSAIC_CATEGORIES:
                continue  # already correct
            cv2_cat_id = _NAME_TO_ID[cv2_cat_name]
            cat = _ID_TO_CAT[cv2_cat_id]
            old_cat = yolo_det["category"]
            yolo_det["corrected_from"] = old_cat
            yolo_det["category"] = cat["name"]
            yolo_det["category_zh"] = cat["zh"]
            _verbose(f"cv2 type correction: {old_cat} → {cat['name']}")
            break  # one correction per cv2 code

    # Build new-detection dicts for cv2 codes with no YOLO overlap at all
    new_dets: list[dict[str, Any]] = []
    for cv2_idx, (cv2_bbox, cv2_cat_name) in enumerate(cv2_codes):
        if cv2_idx in cv2_matched:
            continue
        cat = _ID_TO_CAT[_NAME_TO_ID[cv2_cat_name]]
        new_dets.append({
            "category": cat["name"],
            "category_zh": cat["zh"],
            "confidence": 1.0,
            "bbox": cv2_bbox,
            "has_mask": False,
            "cv2_fallback": True,
        })

    if new_dets:
        _verbose(f"cv2 fallback found {len(new_dets)} additional code(s)")
    return new_dets


def _parse_color(color_str: str) -> tuple[int, int, int]:
    """Parse hex color string to BGR tuple (OpenCV format)."""
    color_str = color_str.lstrip("#")
    if len(color_str) != 6:
        _die("invalid_color", f"Invalid color format: #{color_str}. Expected #RRGGBB")
    try:
        r = int(color_str[0:2], 16)
        g = int(color_str[2:4], 16)
        b = int(color_str[4:6], 16)
    except ValueError:
        _die("invalid_color", f"Invalid color format: #{color_str}. Expected #RRGGBB")
    return (b, g, r)  # BGR for OpenCV


def _resolve_fill_color(method: str, fill_color: str) -> tuple[int, int, int] | None:
    """Validate fill settings before any model work starts."""
    if method != "fill":
        return None
    return _parse_color(fill_color)


# ---------------------------------------------------------------------------
# Per-detection masking (shared by YOLO and cv2 fallback paths)
# ---------------------------------------------------------------------------

def _apply_masking_strategy(
    image,
    mask,
    det: dict[str, Any],
    method: str,
    strength: int,
    fill_color: tuple[int, int, int] | None,
    image_shape: tuple[int, int],
) -> tuple[Any, dict[str, Any]]:
    """Apply the chosen masking method to a single detection region.

    Returns the (possibly modified) image and updated detection dict.
    For code categories (qr_code, barcode) with mosaic method, applies
    adaptive strength and post-masking verification.
    """
    bbox = det["bbox"]
    cls_id = _NAME_TO_ID.get(det["category"])
    is_code = cls_id is not None and cls_id in _ADAPTIVE_MOSAIC_CATEGORIES

    if method == "mosaic":
        effective = (_adaptive_mosaic_strength(bbox, strength)
                     if is_code else strength)
        if effective != strength:
            _verbose(f"{det['category']}: adaptive strength "
                     f"{strength} → {effective}")
        image = _apply_mosaic(image, mask, effective)

        # Post-masking verification for code categories
        if is_code and not _verify_code_destroyed(image, bbox, cls_id):
            escalated = max(effective * 2, 60)
            _verbose(f"{det['category']}: still readable, "
                     f"escalating {effective} → {escalated}")
            image = _apply_mosaic(image, mask, escalated)
            if not _verify_code_destroyed(image, bbox, cls_id):
                _verbose(f"{det['category']}: still readable "
                         f"after escalation, applying fill")
                image = _apply_fill(image, mask, (0, 0, 0))
                det["fill_fallback"] = True
            else:
                effective = escalated
        det["effective_strength"] = effective
    elif method == "blur":
        image = _apply_blur(image, mask, strength)
    elif method == "fill":
        if fill_color is None:
            _die("missing_fill_color",
                 "Fill color is required when --method=fill")
        image = _apply_fill(image, mask, fill_color)

    return image, det


# ---------------------------------------------------------------------------
# Hide (mask) a single image
# ---------------------------------------------------------------------------

def _run_hide(
    image_path: str,
    output_path: str | None,
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
    method: str,
    strength: int,
    fill_color: tuple[int, int, int] | None,
) -> dict[str, Any]:
    """Detect and mask privacy regions in a single image."""
    import cv2
    import numpy as np

    model = _load_model(model_path)
    results = model(image_path, conf=conf, verbose=False)

    image = cv2.imread(image_path)
    if image is None:
        _die("read_failed", f"Failed to read image: {image_path}")

    h, w = image.shape[:2]
    original = image.copy()  # preserve for cv2 fallback

    # Phase 1: Collect ALL YOLO detections (unfiltered) for cv2 correction
    yolo_regions: list[tuple[int, list[int], dict[str, Any]]] = []
    result = None
    if results and results[0].boxes is not None:
        result = results[0]
        for index, bbox, det in _iter_detection_regions(result, type_ids=None):
            yolo_regions.append((index, bbox, det))

    # Phase 2: cv2 code detection on ORIGINAL → correct YOLO + find new
    cv2_codes = _run_cv2_code_detection(original)
    new_cv2_dets = _apply_cv2_corrections(cv2_codes, yolo_regions)

    # Phase 3: Apply --type filtering AFTER correction, then mask
    detections = []
    summary: dict[str, int] = {}

    for index, bbox, det in yolo_regions:
        cls_id = _NAME_TO_ID.get(det["category"])
        if type_ids is not None and cls_id not in type_ids:
            continue
        if result is not None:
            mask = _build_detection_mask(result, index, bbox, (h, w))
        else:
            mask = np.zeros((h, w), dtype=np.uint8)
            x1, y1, x2, y2 = bbox
            mask[y1:y2, x1:x2] = 1
        image, det = _apply_masking_strategy(
            image, mask, det, method, strength, fill_color, (h, w),
        )
        detections.append(det)
        summary[det["category"]] = summary.get(det["category"], 0) + 1

    for det in new_cv2_dets:
        cls_id = _NAME_TO_ID.get(det["category"])
        if type_ids is not None and cls_id not in type_ids:
            continue
        bbox = det["bbox"]
        x1, y1, x2, y2 = bbox
        mask = np.zeros((h, w), dtype=np.uint8)
        mask[y1:y2, x1:x2] = 1
        image, det = _apply_masking_strategy(
            image, mask, det, method, strength, fill_color, (h, w),
        )
        detections.append(det)
        summary[det["category"]] = summary.get(det["category"], 0) + 1

    output_path = _resolve_output_path(image_path, output_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(output_path, image):
        _die("write_failed", f"Failed to write masked image: {output_path}")

    return {
        "output": _absolute_path(output_path),
        "detections": detections,
        "summary": summary,
        "method": method,
        "strength": strength,
    }


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}


def _collect_images(dir_path: str) -> tuple[list[str], list[dict[str, str]]]:
    """Collect immediate image files from a directory plus skipped entries."""
    d = Path(dir_path)
    if not d.is_dir():
        _die("invalid_directory", f"Not a directory: {dir_path}")
    root = d.resolve()
    image_paths: list[str] = []
    skipped: list[dict[str, str]] = []
    for f in sorted(d.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() not in IMAGE_EXTENSIONS:
            skipped.append({"file": _absolute_path(f), "reason": "unsupported_extension"})
            continue
        try:
            resolved = f.resolve()
        except OSError as exc:
            skipped.append({"file": _absolute_path(f), "reason": str(exc)})
            continue
        if not _is_within_directory(resolved, root):
            skipped.append({"file": _absolute_path(f), "reason": "symlink_escape"})
            continue
        image_paths.append(_absolute_path(f))
    return image_paths, skipped


def run_scan_batch(
    image_paths: list[str],
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
    skipped: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Scan a batch of images serially while preserving input order."""
    if not image_paths:
        result: dict[str, Any] = {"results": [], "count": 0, "summary": {}}
        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
        return result

    results = []
    for idx, image_path in enumerate(image_paths):
        _verbose(f"Scanning image {idx + 1}/{len(image_paths)}: {Path(image_path).name}")
        result = _run_detection(image_path, model_path, conf, type_ids)
        result["file"] = image_path
        results.append(result)

    merged_summary: dict[str, int] = {}
    for result in results:
        for cat, count in result.get("summary", {}).items():
            merged_summary[cat] = merged_summary.get(cat, 0) + count

    result = {
        "results": results,
        "count": len(results),
        "summary": merged_summary,
    }
    if skipped:
        result["skipped"] = skipped
        result["skipped_count"] = len(skipped)
    return result


def run_hide_batch(
    image_paths: list[str],
    output_dir: str,
    model_path: str | None,
    conf: float,
    type_ids: set[int] | None,
    method: str,
    strength: int,
    fill_color: tuple[int, int, int] | None,
    skipped: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Hide privacy regions in a batch of images serially while preserving input order."""
    if not image_paths:
        result: dict[str, Any] = {"results": [], "count": 0}
        if skipped:
            result["skipped"] = skipped
            result["skipped_count"] = len(skipped)
        return result

    results = []
    for idx, image_path in enumerate(image_paths):
        _verbose(f"Masking image {idx + 1}/{len(image_paths)}: {Path(image_path).name}")
        output_path = str(Path(output_dir) / Path(image_path).name)
        result = _run_hide(
            image_path,
            output_path,
            model_path,
            conf,
            type_ids,
            method,
            strength,
            fill_color,
        )
        result["file"] = image_path
        results.append(result)

    result = {"results": results, "count": len(results)}
    if skipped:
        result["skipped"] = skipped
        result["skipped_count"] = len(skipped)
    return result


# ---------------------------------------------------------------------------
# Subcommand: detect
# ---------------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> None:
    type_ids = _resolve_types(args.type)

    t0 = time.time()
    if args.dir:
        image_paths, skipped = _collect_images(args.dir)
        batch_result = run_scan_batch(
            image_paths,
            args.model,
            args.conf,
            type_ids,
            skipped,
        )
        elapsed_ms = round((time.time() - t0) * 1000)
        _output("scan", batch_result, timing=args.timing, elapsed_ms=elapsed_ms)
    else:
        # Single image mode
        result = _run_detection(args.image, args.model, args.conf, type_ids)
        elapsed_ms = round((time.time() - t0) * 1000)
        _output("scan", result, timing=args.timing, elapsed_ms=elapsed_ms)


# ---------------------------------------------------------------------------
# Subcommand: hide
# ---------------------------------------------------------------------------

def cmd_hide(args: argparse.Namespace) -> None:
    type_ids = _resolve_types(args.type)
    fill_color = _resolve_fill_color(args.method, args.fill_color)

    t0 = time.time()
    if args.dir:
        if args.output:
            _die(
                "invalid_output_usage",
                "hide --dir does not support --output; use --output-dir instead.",
            )
        output_dir = args.output_dir or str(Path(args.dir) / ".has" / "masked")
        image_paths, skipped = _collect_images(args.dir)
        batch_result = run_hide_batch(
            image_paths,
            output_dir,
            args.model,
            args.conf,
            type_ids,
            args.method,
            args.strength,
            fill_color,
            skipped,
        )
        elapsed_ms = round((time.time() - t0) * 1000)
        _output("hide", batch_result, timing=args.timing, elapsed_ms=elapsed_ms)
    else:
        if args.output_dir:
            _die(
                "invalid_output_usage",
                "hide --image does not support --output-dir; use --output instead.",
            )
        # Single image mode
        result = _run_hide(
            args.image, args.output, args.model,
            args.conf, type_ids, args.method,
            args.strength, fill_color,
        )
        elapsed_ms = round((time.time() - t0) * 1000)
        _output("hide", result, timing=args.timing, elapsed_ms=elapsed_ms)


# ---------------------------------------------------------------------------
# Subcommand: categories
# ---------------------------------------------------------------------------

def cmd_categories(args: argparse.Namespace) -> None:
    if args.model is not None:
        _die(
            "invalid_model_usage",
            "categories does not support --model because it does not load the detection model.",
        )
    t0 = time.time()
    elapsed_ms = round((time.time() - t0) * 1000)
    _output("categories", {"categories": CATEGORIES}, timing=args.timing, elapsed_ms=elapsed_ms)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _output(
    command: str,
    data: dict[str, Any],
    *,
    timing: bool = False,
    elapsed_ms: int | None = None,
) -> None:
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "command": command,
    }
    payload.update(data)
    if timing and elapsed_ms is not None:
        payload["elapsed_ms"] = elapsed_ms
    _emit_json(payload)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    prog_name = os.environ.get("HAS_CLI_PROG", "has-image")
    shared_options = argparse.ArgumentParser(add_help=False)
    shared_options.add_argument(
        "--timing",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Include elapsed_ms in the JSON output",
    )
    shared_options.add_argument(
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Emit runtime status and progress messages to stderr",
    )
    model_option = argparse.ArgumentParser(add_help=False)
    model_option.add_argument(
        "--model",
        default=argparse.SUPPRESS,
        help=f"Model file path (env: HAS_IMAGE_MODEL, default: {_DEFAULT_MODEL_PATH})",
    )
    parser = StructuredArgumentParser(
        parents=[shared_options, model_option],
        prog=prog_name,
        description="HaS Image — Privacy anonymization for images (YOLO11)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            f"  {prog_name} scan --image photo.jpg --type face --type id_card\n"
            f"  {prog_name} hide --image photo.jpg --method mosaic --strength 20\n"
            f"  {prog_name} hide --dir ./photos/ --output-dir .has/masked/ --type face\n"
            f"  {prog_name} categories\n"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        parser_class=StructuredArgumentParser,
    )

    # --- scan ---
    scan_parser = subparsers.add_parser(
        "scan",
        parents=[shared_options, model_option],
        help="Scan image for privacy regions (no masking)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    scan_img_group = scan_parser.add_mutually_exclusive_group(required=True)
    scan_img_group.add_argument("--image", help="Input image path")
    scan_img_group.add_argument("--dir", help="Input directory for batch scanning")
    scan_parser.add_argument(
        "--type", action="append", default=None,
        help="Category filter; repeat the flag to add more categories. Default: all",
    )
    scan_parser.add_argument(
        "--conf", type=float, default=0.25,
        help="Confidence threshold (default: 0.25)",
    )
    scan_parser.set_defaults(func=cmd_scan)

    # --- hide ---
    hide_parser = subparsers.add_parser(
        "hide",
        parents=[shared_options, model_option],
        help="Detect and mask privacy regions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    img_group = hide_parser.add_mutually_exclusive_group(required=True)
    img_group.add_argument("--image", help="Input image path")
    img_group.add_argument("--dir", help="Input directory for batch processing")
    hide_parser.add_argument("--output", default=None, help="Output image path")
    hide_parser.add_argument("--output-dir", default=None, help="Output directory (batch mode)")
    hide_parser.add_argument(
        "--type", action="append", default=None,
        help="Category filter; repeat the flag to add more categories. Default: all",
    )
    hide_parser.add_argument(
        "--method", choices=["mosaic", "blur", "fill"], default="mosaic",
        help="Masking method (default: mosaic)",
    )
    hide_parser.add_argument(
        "--strength", type=int, default=15,
        help="Mosaic block size or blur radius (default: 15)",
    )
    hide_parser.add_argument(
        "--fill-color", default="#000000",
        help="Fill color for 'fill' method, hex format (default: #000000)",
    )
    hide_parser.add_argument(
        "--conf", type=float, default=0.25,
        help="Confidence threshold (default: 0.25)",
    )
    hide_parser.set_defaults(func=cmd_hide)

    # --- categories ---
    cat_parser = subparsers.add_parser(
        "categories",
        parents=[shared_options],
        help="List all supported privacy categories",
    )
    cat_parser.set_defaults(func=cmd_categories)

    return parser


def main() -> None:
    parser = build_parser()
    args: argparse.Namespace | None = None
    try:
        args = parser.parse_args()
        args.timing = getattr(args, "timing", False)
        args.verbose = getattr(args, "verbose", False)
        args.model = getattr(args, "model", None)
        if not args.command:
            raise CLIError("missing_command", "Choose a subcommand: scan, hide, or categories.")
        if args.verbose:
            os.environ["HAS_IMAGE_VERBOSE"] = "1"
        else:
            os.environ.pop("HAS_IMAGE_VERBOSE", None)
        args.func(args)
    except CLIError as exc:
        _emit_json(_error_payload(exc.code, exc.message))
        sys.exit(1)
    except (OSError, RuntimeError, ValueError) as exc:
        _emit_json(_error_payload("runtime_error", str(exc)))
        sys.exit(1)


if __name__ == "__main__":
    main()
