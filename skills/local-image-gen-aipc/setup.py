"""
setup.py — One-time environment setup for local-image-generation skill.

Run once from a terminal:
    python setup.py

What this does:
  1. Creates a shared Python venv under {USERNAME}_openvino\venv\
  2. Checks git is available (required for pinned git+https dependencies)
  3. Installs all required packages into the venv
  4. Writes state.json so the skill knows where everything is

After this, run:
    python download_model.py
"""

import json, os, shutil, string, subprocess, sys
from pathlib import Path

REQUIREMENTS_FILE = "requirements_imagegen.txt"

PACKAGES_FALLBACK = [
    "openvino>=2024.5.0",
    "torch>=2.1.0",
    "Pillow>=10.0.0",
    "modelscope>=1.14.0",
    "git+https://github.com/huggingface/optimum-intel.git@2f62e5ae#egg=optimum-intel[openvino]",
    "git+https://github.com/huggingface/diffusers.git@a1f36ee3",
]

# ── Banner ─────────────────────────────────────────────────
print("=" * 55)
print("  local-image-generation  ·  Environment Setup")
print("=" * 55)

# ── Check Python version ───────────────────────────────────
vi = sys.version_info
if vi < (3, 10):
    print(f"\n[ERROR] Python {vi.major}.{vi.minor} detected — need >= 3.10")
    print("  Download: https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe")
    sys.exit(1)
print(f"\n  Python {vi.major}.{vi.minor}.{vi.micro} OK ✅")

# ── Check git ──────────────────────────────────────────────
r = subprocess.run(["git", "--version"], capture_output=True)
if r.returncode != 0:
    print("\n[ERROR] git not found — required for pinned git+https dependencies")
    print("  Download: https://git-scm.com/download/win")
    sys.exit(1)
print(f"  {r.stdout.decode().strip()} OK ✅")

# ── Locate root directory ──────────────────────────────────
username  = os.environ.get("USERNAME", "user").lower()
root_name = f"{username}_openvino"
drives    = [f"{d}:\\" for d in string.ascii_uppercase if Path(f"{d}:\\").exists()]

root = next(
    (Path(d) / root_name for d in drives if (Path(d) / root_name).exists()),
    None
)
if not root:
    best = max(drives, key=lambda d: shutil.disk_usage(d).free)
    root = Path(best) / root_name

imagegen_dir = root / "imagegen"
venv_dir     = root / "venv"
venv_py      = venv_dir / "Scripts" / "python.exe"

root.mkdir(parents=True, exist_ok=True)
imagegen_dir.mkdir(parents=True, exist_ok=True)

print(f"\n  Root:     {root}")
print(f"  Imagegen: {imagegen_dir}")
print(f"  Venv:     {venv_dir}")

# ── Create or validate venv ────────────────────────────────
print("\n[1/3] Checking venv...")

venv_ok = False
if venv_py.exists():
    try:
        r = subprocess.run([str(venv_py), "--version"], capture_output=True, timeout=10)
        if r.returncode == 0:
            print(f"  Existing venv OK: {r.stdout.decode().strip()}")
            venv_ok = True
    except Exception:
        pass

if not venv_ok:
    if venv_dir.exists():
        print("  Existing venv is broken — rebuilding...")
        shutil.rmtree(venv_dir, ignore_errors=True)
    print("  Creating venv...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    venv_py = venv_dir / "Scripts" / "python.exe"
    r = subprocess.run([str(venv_py), "--version"], capture_output=True)
    print(f"  Venv created: {r.stdout.decode().strip()} ✅")

def venv_run(args, **kw):
    return subprocess.run([str(venv_py)] + args, **kw)

# ── Upgrade pip ────────────────────────────────────────────
print("\n[2/3] Upgrading pip...")
venv_run(["-m", "pip", "install", "--upgrade", "pip", "--quiet"], check=True)
print("  pip upgraded ✅")

# ── Install packages ───────────────────────────────────────
print("\n[3/3] Installing packages (this may take ~5 min)...")

req_file = Path(__file__).parent / REQUIREMENTS_FILE
if req_file.exists():
    print(f"  Using {req_file}")
    venv_run(["-m", "pip", "install", "-r", str(req_file)], check=True)
else:
    print(f"  {REQUIREMENTS_FILE} not found — installing fallback list")
    venv_run(["-m", "pip", "install"] + PACKAGES_FALLBACK, check=True)

print("  Packages installed ✅")

# ── Write state.json ───────────────────────────────────────
state = {
    "ROOT":          str(root),
    "IMAGE_GEN_DIR": str(imagegen_dir),
    "VENV_DIR":      str(venv_dir),
    "VENV_PY":       str(venv_py),
    "VENV_EXISTS":   True,
}
state_file = imagegen_dir / "state.json"
state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
print(f"\n  state.json written: {state_file} ✅")

# ── Create outputs dir ─────────────────────────────────────
(imagegen_dir / "outputs").mkdir(exist_ok=True)

# ── Verify ─────────────────────────────────────────────────
print("\n[Verify] Checking installation...")

verify_script = """
results = {}
for pkg, imp in [
    ("openvino",   "openvino"),
    ("torch",      "torch"),
    ("Pillow",     "PIL"),
    ("modelscope", "modelscope"),
]:
    try:
        ver = getattr(__import__(imp), "__version__", "OK")
        results[pkg] = ("OK", ver)
    except ImportError as e:
        results[pkg] = ("FAIL", str(e))

try:
    from optimum.intel import OVZImagePipeline
    results["OVZImagePipeline"] = ("OK", "importable")
except ImportError as e:
    results["OVZImagePipeline"] = ("FAIL", str(e))

fail = [k for k, (s, _) in results.items() if s == "FAIL"]
for k, (s, d) in results.items():
    icon = "OK  " if s == "OK" else "FAIL"
    print(f"  [{icon}] {k}: {d}")
print()
print("VERIFY=PASS" if not fail else f"VERIFY=FAIL  {fail}")
"""
venv_run(["-c", verify_script])

# ── Done ───────────────────────────────────────────────────
print()
print("=" * 55)
print("  Setup complete!")
print()
print("  Next step — download the model (~10 GB):")
print(f"    python \"{Path(__file__).parent / 'download_model.py'}\"")
print("=" * 55)
