"""
download_model.py — Download Z-Image-Turbo-int4-ov from ModelScope.

Run once from a terminal (NOT inside OpenClaw):
    python download_model.py

- Downloads ~10 GB to your local {USERNAME}_openvino\imagegen\ directory
- Resume supported: safe to Ctrl+C and re-run, will continue from where it stopped
- Run setup.py first if you haven't already
"""

import json, os, string, subprocess, sys
from pathlib import Path

MODEL_ID = "snake7gun/Z-Image-Turbo-int4-ov"
TOTAL_GB = 10.0

# ── Find state.json ────────────────────────────────────────
def find_state():
    for d in string.ascii_uppercase:
        sf = Path(f"{d}:\\") / f"{os.environ.get('USERNAME', 'user').lower()}_openvino" / "imagegen" / "state.json"
        if sf.exists():
            return json.loads(sf.read_text(encoding="utf-8"))
    return None

state = find_state()
if not state:
    print("[ERROR] state.json not found.")
    print("  Please run setup.py first:")
    print(f"    python \"{Path(__file__).parent / 'setup.py'}\"")
    sys.exit(1)

venv_py = Path(state["VENV_PY"])
if not venv_py.exists():
    print(f"[ERROR] venv not found at {venv_py}")
    print("  Please re-run setup.py.")
    sys.exit(1)

# ── Self-relaunch inside venv ──────────────────────────────
# This ensures modelscope and all deps are available.
if Path(sys.executable).resolve() != venv_py.resolve():
    print(f"[INFO] Switching to venv python: {venv_py}")
    result = subprocess.run([str(venv_py), str(Path(__file__).resolve())])
    sys.exit(result.returncode)

# ─────────────────────────────────────────────────────────────
# From here on we are running inside the venv
# ─────────────────────────────────────────────────────────────
import threading, time
from modelscope import snapshot_download

imagegen_dir = Path(state["IMAGE_GEN_DIR"])
model_dir    = imagegen_dir / "Z-Image-Turbo-int4-ov"

# ── Check if already complete ──────────────────────────────
def get_size_gb(path):
    if not path.exists():
        return 0.0
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / 1024**3

def model_complete():
    required = ["transformer", "vae_decoder", "text_encoder"]
    return all((model_dir / r).exists() for r in required)

print("=" * 55)
print("  local-image-generation  ·  Model Download")
print("=" * 55)
print(f"\n  Model dir: {model_dir}")

if model_complete():
    gb = get_size_gb(model_dir)
    print(f"\n  Model already complete ({gb:.2f} GB) ✅")
    print("  You can use the skill right away.")
    sys.exit(0)

existing_gb = get_size_gb(model_dir)
if existing_gb > 0.01:
    print(f"\n  Resuming download — {existing_gb:.2f} GB already on disk")
else:
    print(f"\n  Starting fresh download (~{TOTAL_GB} GB)")

print(f"""
  Estimated time:
    100 Mbps → ~15 min
     50 Mbps → ~30 min
     10 Mbps → ~2 hr

  Progress updates every 30 seconds.
  Safe to Ctrl+C and re-run — download will resume.
""")

model_dir.mkdir(parents=True, exist_ok=True)

# ── Download with progress watchdog ───────────────────────
_stop = threading.Event()
t0    = time.time()

def watchdog():
    prev = existing_gb * 1024**3
    print("[Progress] Download started...", flush=True)
    while not _stop.wait(30):
        try:
            total   = sum(f.stat().st_size for f in model_dir.rglob("*") if f.is_file())
            now     = time.time()
            speed   = (total - prev) / 30
            pct     = min(total / (TOTAL_GB * 1024**3) * 100, 99.9)
            elapsed = now - t0
            eta     = (TOTAL_GB * 1024**3 - total) / speed if speed > 0 else 0
            print(
                f"[Progress] {total/1024**3:.2f}/{TOTAL_GB:.1f} GB  "
                f"{pct:.1f}%  {speed/1024**2:.1f} MB/s  "
                f"elapsed {int(elapsed//60)}m{int(elapsed%60):02d}s  "
                f"ETA ~{int(eta//60)}m{int(eta%60):02d}s",
                flush=True
            )
            prev = total
        except Exception:
            pass

threading.Thread(target=watchdog, daemon=True).start()

try:
    snapshot_download(MODEL_ID, local_dir=str(model_dir))
    _stop.set()

    if model_complete():
        gb = get_size_gb(model_dir)
        print(f"\n{'='*55}")
        print(f"  Download complete! ({gb:.2f} GB) ✅")
        print(f"  You can now use the image generation skill in OpenClaw.")
        print(f"{'='*55}")
    else:
        print("\n[WARN] Download finished but model appears incomplete.")
        print("  Re-run this script to resume.")

except KeyboardInterrupt:
    _stop.set()
    print("\n[INFO] Download interrupted.")
    print("  Re-run this script to continue from where it stopped.")

except Exception as e:
    _stop.set()
    err = str(e).lower()
    if any(x in err for x in ["disk", "space"]):
        print(f"\n[ERROR] Disk full: {e}")
        print("  Free up space and re-run.")
    elif any(x in err for x in ["timeout", "connection", "network"]):
        print(f"\n[ERROR] Network error: {e}")
        print("  Check your connection and re-run.")
        print(f"  Manual download: https://modelscope.cn/models/{MODEL_ID}/files")
        print(f"  Place files under: {model_dir}")
        print(f"  Required subdirs: transformer/  vae_decoder/  text_encoder/")
    else:
        print(f"\n[ERROR] {e}")
        print("  Re-run to retry.")
        print(f"  Manual download: https://modelscope.cn/models/{MODEL_ID}/files")
        print(f"  Place files under: {model_dir}")
