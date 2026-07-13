#!/usr/bin/env python3
"""
Shared utilities for the video-editing skill.

Provides platform detection, GPU/encoder detection, font finding,
mirror configuration, and dependency checking.
"""

import json
import os
import platform
import re
import subprocess
import sys
import urllib.request
import urllib.error


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------

def detect_platform():
    """Return one of: 'macos', 'linux', 'wsl', 'windows'."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Windows":
        return "windows"
    if system == "Linux":
        # WSL detection
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    return "wsl"
        except (IOError, OSError):
            pass
        return "linux"
    return "linux"  # fallback


def is_apple_silicon():
    """Check if running on Apple Silicon (arm64 Mac)."""
    return detect_platform() == "macos" and platform.machine() == "arm64"


def is_china_locale():
    """Heuristic: detect if the user is likely in China."""
    import locale
    import time
    # Check timezone
    try:
        tz = time.tzname
        if any("CST" in t or "Asia/Shanghai" in t or "Asia/Chongqing" in t for t in tz):
            return True
    except Exception:
        pass
    # Check TZ env
    tz_env = os.environ.get("TZ", "")
    if "Asia/Shanghai" in tz_env or "Asia/Chongqing" in tz_env:
        return True
    # Check locale
    try:
        loc = locale.getlocale()[0] or ""
        if loc.startswith("zh_CN") or loc.startswith("zh_Hans"):
            return True
    except Exception:
        pass
    # Check LANG env
    lang = os.environ.get("LANG", "") + os.environ.get("LANGUAGE", "")
    if "zh_CN" in lang:
        return True
    return False


# ---------------------------------------------------------------------------
# GPU & encoder detection
# ---------------------------------------------------------------------------

def _run_quiet(cmd):
    """Run a command and return stdout, or empty string on failure."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return r.stdout
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return ""


def detect_gpu():
    """Detect available GPU type.

    Returns dict with keys:
        type: 'nvidia' | 'apple' | 'intel' | 'amd' | 'none'
        cuda: bool
        mps: bool  (Apple Metal Performance Shaders)
        qsv: bool  (Intel Quick Sync)
        amf: bool  (AMD AMF)
        videotoolbox: bool
    """
    info = {
        "type": "none",
        "cuda": False,
        "mps": False,
        "qsv": False,
        "amf": False,
        "videotoolbox": False,
    }

    plat = detect_platform()

    # NVIDIA CUDA
    if _run_quiet(["nvidia-smi"]).strip():
        info["type"] = "nvidia"
        info["cuda"] = True
        return info

    # Apple Silicon MPS
    if plat == "macos" and is_apple_silicon():
        info["type"] = "apple"
        info["mps"] = True
        info["videotoolbox"] = True
        return info

    # macOS Intel — still has VideoToolbox
    if plat == "macos":
        info["type"] = "intel"
        info["videotoolbox"] = True
        return info

    # Check ffmpeg encoders for QSV / AMF
    enc_out = _run_quiet(["ffmpeg", "-hide_banner", "-encoders"])
    if "h264_qsv" in enc_out:
        info["type"] = "intel"
        info["qsv"] = True
    if "h264_amf" in enc_out:
        info["type"] = "amd"
        info["amf"] = True

    # Linux VAAPI
    if plat in ("linux", "wsl") and os.path.exists("/dev/dri/renderD128"):
        if info["type"] == "none":
            info["type"] = "intel"  # most likely

    return info


def get_ffmpeg_encoder(gpu_info=None):
    """Choose the best available H.264 encoder.

    Returns (encoder_name, extra_args_list).
    """
    if gpu_info is None:
        gpu_info = detect_gpu()

    # NVIDIA
    if gpu_info.get("cuda"):
        return "h264_nvenc", ["-preset", "p4", "-cq", "20"]

    # Apple VideoToolbox
    if gpu_info.get("videotoolbox"):
        return "h264_videotoolbox", ["-q:v", "65"]

    # Intel QSV
    if gpu_info.get("qsv"):
        return "h264_qsv", ["-global_quality", "23"]

    # AMD AMF
    if gpu_info.get("amf"):
        return "h264_amf", ["-quality", "balanced", "-rc", "cqp", "-qp_i", "20", "-qp_p", "22"]

    # CPU fallback
    return "libx264", ["-preset", "fast", "-crf", "18"]


def get_ffmpeg_encode_args(gpu_info=None):
    """Return full ffmpeg video encode arguments list: ['-c:v', encoder, ...extra]."""
    encoder, extra = get_ffmpeg_encoder(gpu_info)
    return ["-c:v", encoder] + extra


# ---------------------------------------------------------------------------
# Whisper engine detection
# ---------------------------------------------------------------------------

def detect_whisper_engine():
    """Detect the best available Whisper engine.

    Returns one of: 'faster-whisper', 'openai-whisper', 'none'.
    """
    # Try faster-whisper first
    try:
        import faster_whisper  # noqa: F401
        return "faster-whisper"
    except ImportError:
        pass

    # Try openai whisper
    try:
        import whisper  # noqa: F401
        return "openai-whisper"
    except ImportError:
        pass

    return "none"


def recommend_whisper_model(gpu_info=None):
    """Recommend a Whisper model size based on available hardware.

    Returns (model_name, reason).
    """
    if gpu_info is None:
        gpu_info = detect_gpu()

    if gpu_info.get("cuda"):
        return "large-v3", "NVIDIA GPU detected, large model runs fast on CUDA"

    if gpu_info.get("mps"):
        # Apple Silicon — large-v3-turbo is ideal
        return "large-v3-turbo", "Apple Silicon detected, turbo model balances speed and quality"

    if gpu_info.get("qsv"):
        return "medium", "Intel iGPU detected, medium model is the best balance for CPU+iGPU"

    if gpu_info.get("amf"):
        return "medium", "AMD iGPU detected, medium model is the best balance for CPU+iGPU"

    # CPU only
    return "small", "No GPU detected, small model offers best speed/quality on CPU"


def get_whisper_device(gpu_info=None):
    """Return the device string for Whisper inference.

    Returns (device, compute_type) tuple.
    """
    if gpu_info is None:
        gpu_info = detect_gpu()

    if gpu_info.get("cuda"):
        return "cuda", "float16"

    if gpu_info.get("mps"):
        # faster-whisper doesn't support MPS yet; use CPU with int8
        engine = detect_whisper_engine()
        if engine == "openai-whisper":
            return "cpu", "float32"  # openai-whisper on Mac
        return "cpu", "int8"  # faster-whisper CPU

    # CPU (including Intel/AMD iGPU — Whisper can't use QSV/AMF)
    engine = detect_whisper_engine()
    if engine == "faster-whisper":
        return "cpu", "int8"
    return "cpu", "float32"


# ---------------------------------------------------------------------------
# Mirror / China support
# ---------------------------------------------------------------------------

PIP_MIRRORS = {
    "tsinghua": "https://pypi.tuna.tsinghua.edu.cn/simple",
    "aliyun": "https://mirrors.aliyun.com/pypi/simple/",
    "ustc": "https://pypi.mirrors.ustc.edu.cn/simple/",
}

HF_MIRROR = "https://hf-mirror.com"


def get_pip_mirror_args():
    """Return pip install args for China mirror, or empty list if not needed."""
    if is_china_locale() or os.environ.get("USE_CN_MIRROR"):
        return ["-i", PIP_MIRRORS["tsinghua"],
                "--trusted-host", "pypi.tuna.tsinghua.edu.cn"]
    return []


def get_hf_endpoint():
    """Return HuggingFace endpoint — mirror for China, default otherwise."""
    if os.environ.get("HF_ENDPOINT"):
        return os.environ["HF_ENDPOINT"]
    if is_china_locale() or os.environ.get("USE_CN_MIRROR"):
        return HF_MIRROR
    return "https://huggingface.co"


def setup_china_env():
    """Set environment variables for China mirror if applicable."""
    if is_china_locale() or os.environ.get("USE_CN_MIRROR"):
        os.environ.setdefault("HF_ENDPOINT", HF_MIRROR)
        print(f"[mirror] HuggingFace mirror: {HF_MIRROR}")
        return True
    return False


# ---------------------------------------------------------------------------
# Font finding (consolidated)
# ---------------------------------------------------------------------------

GOOGLE_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
GOOGLE_FONT_URL_CN = "https://cdn.jsdelivr.net/gh/google/fonts@main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"
GOOGLE_FONT_FILENAME = "NotoSansSC[wght].ttf"


def find_chinese_font(custom_font_path=None):
    """Find a suitable Chinese font. Returns (font_path, font_name) or (None, fallback_name)."""
    if custom_font_path and os.path.isfile(custom_font_path):
        name = _guess_font_name(custom_font_path)
        return custom_font_path, name

    # Check cached Google font
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_fonts_dir = os.path.join(os.path.dirname(script_dir), "fonts")
    google_font_path = os.path.join(skill_fonts_dir, GOOGLE_FONT_FILENAME)

    if os.path.isfile(google_font_path):
        return google_font_path, "Noto Sans SC"

    # Try downloading
    font_path = _download_font(skill_fonts_dir, google_font_path)
    if font_path:
        return font_path, "Noto Sans SC"

    # System font fallback
    plat = detect_platform()
    return _find_system_font(plat)


def _download_font(fonts_dir, target_path):
    """Try downloading Noto Sans SC font. Uses CDN mirror for China."""
    urls = []
    if is_china_locale() or os.environ.get("USE_CN_MIRROR"):
        urls.append(GOOGLE_FONT_URL_CN)
    urls.append(GOOGLE_FONT_URL)

    for url in urls:
        try:
            os.makedirs(fonts_dir, exist_ok=True)
            print(f"[font] Downloading Noto Sans SC...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(target_path, "wb") as f:
                    f.write(resp.read())
            print(f"[font] Downloaded: {target_path}")
            return target_path
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            print(f"[font] Download failed from {url}: {e}")
            continue
    return None


def _find_system_font(plat):
    """Find system Chinese font by platform. Returns (path, name) or (None, fallback_name)."""
    candidates = []
    if plat == "macos":
        import glob
        candidates = [
            ("/System/Library/Fonts/PingFang.ttc", "PingFang SC"),
            ("/System/Library/Fonts/STHeiti Medium.ttc", "Heiti SC"),
            ("/Library/Fonts/PingFang.ttc", "PingFang SC"),
        ]
        # AssetsV2
        for p in glob.glob("/System/Library/AssetsV2/**/PingFang.ttc", recursive=True):
            candidates.append((p, "PingFang SC"))
    elif plat == "windows":
        windir = os.environ.get("WINDIR", os.environ.get("SystemRoot", r"C:\Windows"))
        candidates = [
            (os.path.join(windir, "Fonts", "msyhbd.ttc"), "Microsoft YaHei"),
            (os.path.join(windir, "Fonts", "msyh.ttc"), "Microsoft YaHei"),
            (os.path.join(windir, "Fonts", "simhei.ttf"), "SimHei"),
        ]
    elif plat == "wsl":
        # WSL: check Linux fonts first, then Windows fonts via /mnt/c
        candidates = [
            ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "Noto Sans CJK SC"),
            ("/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc", "Noto Sans CJK SC"),
            ("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", "Noto Sans CJK SC"),
            ("/mnt/c/Windows/Fonts/msyhbd.ttc", "Microsoft YaHei"),
            ("/mnt/c/Windows/Fonts/msyh.ttc", "Microsoft YaHei"),
            ("/mnt/c/Windows/Fonts/simhei.ttf", "SimHei"),
        ]
    else:  # linux
        candidates = [
            ("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "Noto Sans CJK SC"),
            ("/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc", "Noto Sans CJK SC"),
            ("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", "Noto Sans CJK SC"),
            ("/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", "Droid Sans Fallback"),
        ]

    for path, name in candidates:
        if os.path.isfile(path):
            print(f"[font] Using system font: {path}")
            return path, name

    # fc-match fallback (Linux/WSL)
    if plat in ("linux", "wsl"):
        try:
            result = subprocess.run(
                ["fc-match", "-f", "%{file}", ":lang=zh"],
                capture_output=True, text=True, check=True, timeout=5
            )
            fp = result.stdout.strip()
            if fp and os.path.isfile(fp):
                print(f"[font] Using fc-match font: {fp}")
                return fp, _guess_font_name(fp)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    # Fallback name (no file found)
    fallback = {
        "macos": "PingFang SC",
        "windows": "Microsoft YaHei",
        "wsl": "Microsoft YaHei",
        "linux": "Noto Sans CJK SC",
    }
    print("[font] WARNING: No Chinese font file found. Subtitles may show as boxes.", file=sys.stderr)
    return None, fallback.get(plat, "Noto Sans CJK SC")


def _guess_font_name(font_path):
    """Guess ASS font name from file path."""
    base = os.path.basename(font_path).lower()
    if "pingfang" in base:
        return "PingFang SC"
    if "notosanssc" in base or "notosanscjk" in base:
        return "Noto Sans SC"
    if "msyh" in base:
        return "Microsoft YaHei"
    if "simhei" in base:
        return "SimHei"
    if "heiti" in base:
        return "Heiti SC"
    return "Noto Sans SC"


# ---------------------------------------------------------------------------
# FFmpeg feature validation
# ---------------------------------------------------------------------------

def check_ffmpeg():
    """Check ffmpeg availability and required features.

    Returns dict with 'available', 'version', 'has_libass', 'has_drawtext'.
    """
    info = {"available": False, "version": "", "has_libass": False, "has_drawtext": False}
    # Version
    out = _run_quiet(["ffmpeg", "-version"])
    if not out:
        return info
    info["available"] = True
    m = re.search(r"ffmpeg version (\S+)", out)
    if m:
        info["version"] = m.group(1)
    # Build config
    cfg = _run_quiet(["ffmpeg", "-hide_banner", "-buildconf"])
    info["has_libass"] = "--enable-libass" in cfg
    info["has_drawtext"] = "--enable-libfreetype" in cfg
    return info


def check_dependencies():
    """Check all required dependencies. Returns list of (name, status, message)."""
    results = []
    # ffmpeg
    ff = check_ffmpeg()
    if ff["available"]:
        results.append(("ffmpeg", "ok", f"v{ff['version']}"))
        if not ff["has_libass"]:
            results.append(("ffmpeg-libass", "warn", "libass not found, subtitle burning may fail"))
        if not ff["has_drawtext"]:
            results.append(("ffmpeg-drawtext", "warn", "libfreetype not found, cover text may fail"))
    else:
        results.append(("ffmpeg", "missing", "Install: brew install ffmpeg (macOS) / apt install ffmpeg (Linux)"))

    # ffprobe
    if _run_quiet(["ffprobe", "-version"]):
        results.append(("ffprobe", "ok", ""))
    else:
        results.append(("ffprobe", "missing", "Usually bundled with ffmpeg"))

    # Python whisper
    engine = detect_whisper_engine()
    if engine == "faster-whisper":
        results.append(("whisper", "ok", "faster-whisper (recommended)"))
    elif engine == "openai-whisper":
        results.append(("whisper", "ok", "openai-whisper (consider upgrading to faster-whisper)"))
    else:
        results.append(("whisper", "missing", "Install: pip install faster-whisper (recommended) or pip install openai-whisper"))

    # GPU
    gpu = detect_gpu()
    encoder, _ = get_ffmpeg_encoder(gpu)
    results.append(("gpu", "info", f"type={gpu['type']}, encoder={encoder}"))

    return results


def print_env_report():
    """Print a diagnostic environment report."""
    plat = detect_platform()
    gpu = detect_gpu()
    engine = detect_whisper_engine()
    model, reason = recommend_whisper_model(gpu)
    encoder, _ = get_ffmpeg_encoder(gpu)

    print("=" * 50)
    print("Video Editing Skill — Environment Report")
    print("=" * 50)
    print(f"Platform      : {plat}" + (" (Apple Silicon)" if is_apple_silicon() else ""))
    print(f"China locale  : {is_china_locale()}")
    print(f"GPU type      : {gpu['type']}")
    print(f"FFmpeg encoder: {encoder}")
    print(f"Whisper engine: {engine or 'not installed'}")
    print(f"Recommended model: {model} ({reason})")
    print()

    deps = check_dependencies()
    for name, status, msg in deps:
        icon = {"ok": "+", "warn": "!", "missing": "X", "info": "i"}[status]
        print(f"  [{icon}] {name}: {msg}")
    print("=" * 50)


# ---------------------------------------------------------------------------
# Path utilities (cross-platform)
# ---------------------------------------------------------------------------

def escape_ffmpeg_path(path):
    """Escape a file path for use inside ffmpeg filter strings."""
    # FFmpeg filter syntax uses : and \ as special chars
    path = path.replace("\\", "/")  # normalize to forward slashes
    path = path.replace(":", "\\:")
    path = path.replace("'", "'\\''")
    return path


def sanitize_title(text):
    """Remove special characters that may cause rendering issues."""
    text = re.sub(r'[{}\\\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    text = re.sub(r'[<>|@#$%^&*~`]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ---------------------------------------------------------------------------
# Main (diagnostic)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print_env_report()
