---
name: local-image-generation
# Local Text-to-Image (Windows · Z-Image-Turbo · OpenVINO)
description: >
  generate an image, create a picture, draw something, make an image of, text to image,
  paint a picture, illustrate, visualize, local image generation, AI art, image synthesis,
  offline image generation, no API key, local inference, generate art, create artwork,
  produce an image, render an image, AI drawing, image from text.
  Runs Z-Image-Turbo on-device on Windows via Intel OpenVINO. Prioritizes Intel iGPU
  (Xe / Arc), falls back to CPU. Bilingual prompts (English + Chinese) supported.
  SETUP requires network: downloads pip dependencies from GitHub and the model (~10 GB)
  from modelscope.cn. INFERENCE is fully offline after setup — no cloud API calls.
os: windows
requires:
  - python>=3.10
  - git
network:
  setup: required    # github.com (pip deps), modelscope.cn (~10 GB model)
  inference: offline
user-invocable: true
allowed-tools: Bash(python *), Bash(pip *), Bash(git *), Read, Glob, Write, message
---

**Model**: `snake7gun/Z-Image-Turbo-int4-ov` (ModelScope INT4)  
**SKILL_VERSION**: `v1.0.2`

> **Network usage**: Setup downloads pip dependencies (some pinned to git+https commits)
> from `github.com`, and the model (~10 GB, resume supported) from `modelscope.cn`.
> Inference is fully offline — no network calls once setup is complete.

> **First time?** Before using this skill, run these two scripts once in a terminal:
>
> ```
> python setup.py          # creates venv, installs dependencies (~5 min)
> python download_model.py # downloads the model (~10 GB, resumable)
> ```
>
> Both scripts are in the skill directory alongside this SKILL.md.

## Directory layout (all auto-created)

```
{USERNAME}_openvino\
├── venv\                          ← shared venv (created by setup.py)
└── imagegen\
    ├── state.json                 ← written by setup.py
    ├── generate_image.py          ← written in Step 2
    ├── Z-Image-Turbo-int4-ov\    ← downloaded by download_model.py (~10 GB)
    └── outputs\YYYYMMDD_HHMMSS_topic.png
```

---

## ⚠️ Agent instructions

1. **Windows / PowerShell only.** Never use Linux commands (`ls`, `rm`, `cat`). Never use `&&` or `call`.
2. **Every step reads `state.json` itself** — do not pass paths between steps manually.
3. **Use `VENV_PY` from state.json for all python calls** — never use system python for inference.
4. **CRITICAL — Never skip Step 2.** Always run the version-check python script to write `generate_image.py`. Never use the Write tool to create or modify it manually.
5. **CRITICAL — If `generate_image.py` fails**, do NOT rewrite it manually. Delete it and re-run Step 2's python script to regenerate.
6. **Goal**: generate an image and send the preview to the conversation.

**Auto-recovery policy — try before asking user:**

- If `STATE=MISSING` or `VENV_PY=BROKEN`: automatically run `setup.py` (up to 3 attempts). Only ask user if all 3 fail.
- If `MODEL_STATUS=MISSING`: automatically run `download_model.py` (up to 3 attempts). Stop if a single attempt exceeds 20 minutes — download supports resume, partial progress is not lost.
- Always announce before each attempt: `⚙️ Auto-installing environment (attempt N/3)…`

**Pipeline — follow exactly in order, no skipping:**

```
Step 0: expand prompt       → EXPANDED_PROMPT, TOPIC
Step 1: verify environment  → VENV_PY, IMAGE_GEN_DIR confirmed ready
         ↳ if STATE=MISSING or VENV_BROKEN: auto-run setup.py (3 attempts)
         ↳ if MODEL_STATUS=MISSING: auto-run download_model.py (3 attempts)
Step 2: verify deps + write generate_image.py → SCRIPT_UPDATE=DONE/SKIPPED  ← NEVER skip
Step 3: generate + send     → [SUCCESS] + image preview
```

---

## Step 0: expand prompt (LLM only — no tools)

Do two things simultaneously: **① expand the prompt** and **② extract a topic slug** (English snake_case, used for the filename).

Expansion structure: `[subject] [action/pose] [environment] [lighting/mood] [style] [quality tags]`

Prompts can be English or Chinese — no translation needed. Topic slug must always be English to avoid path encoding issues.

Quality tags: `photorealistic`, `8K resolution`, `cinematic lighting`, `masterpiece`

| Input | Topic slug | Expanded prompt |
|-------|-----------|-----------------|
| a panda | `panda_bamboo` | A giant panda sitting in a lush bamboo forest, sunlight filtering through leaves, photorealistic, 8K, wildlife photography |
| 赛博朋克城市 | `cyberpunk_city` | 未来感都市夜景，霓虹灯倒映在湿漉漉的街道，赛博朋克风，电影级，8K |

Show the result before proceeding:
```
📝 Input:    {user description}
   Expanded: {full prompt}
   Topic:    {topic_slug}
```

---

## Step 1: verify environment and model

> 🔍 Step 1/3: checking environment and model…

```
python -c "
import json, os, string, subprocess
from pathlib import Path

state = None
for d in string.ascii_uppercase:
    sf = Path(f'{d}:\\\\') / f'{os.environ.get(\"USERNAME\",\"user\").lower()}_openvino' / 'imagegen' / 'state.json'
    if sf.exists():
        state = json.loads(sf.read_text(encoding='utf-8'))
        break

if not state:
    print('STATE=MISSING')
    exit(1)

venv_py      = Path(state['VENV_PY'])
imagegen_dir = Path(state['IMAGE_GEN_DIR'])
model_dir    = imagegen_dir / 'Z-Image-Turbo-int4-ov'

r = subprocess.run([str(venv_py), '--version'], capture_output=True, timeout=10)
if r.returncode != 0:
    print('VENV_PY=BROKEN')
    exit(1)

print(f'VENV_PY={venv_py}')
print(f'IMAGE_GEN_DIR={imagegen_dir}')

required = ['transformer', 'vae_decoder', 'text_encoder']
missing  = [r for r in required if not (model_dir / r).exists()]
if not missing:
    total = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file()) / 1024**3
    print(f'MODEL_STATUS=READY  ({total:.2f} GB)')
else:
    print(f'MODEL_STATUS=MISSING  missing={missing}')
    exit(1)
"
```

**On success**: record `VENV_PY` and `IMAGE_GEN_DIR` from output, proceed to Step 2.

---

### If STATE=MISSING or VENV_PY=BROKEN → auto-run setup.py

```
python -c "
from pathlib import Path
p = Path(r'{baseDir}') / 'setup.py'
print(f'SETUP_PY={p}') if p.exists() else print('SETUP_PY=NOT_FOUND')
"
```

Announce and run (up to 3 attempts):
```
⚙️ Environment not initialized — auto-installing (attempt 1/3)…
```
```
python "<SETUP_PY path>"
```

Re-run Step 1's check after each attempt. If all 3 fail, show manual fallback below.

---

### If MODEL_STATUS=MISSING → auto-run download_model.py

```
python -c "
from pathlib import Path
p = Path(r'{baseDir}') / 'download_model.py'
print(f'DOWNLOAD_PY={p}') if p.exists() else print('DOWNLOAD_PY=NOT_FOUND')
"
```

Announce to user and ask how to proceed:
```
📥 Model not found — download required (~10 GB)
   Estimated time:
   • 100 Mbps → ~15 min
   •  50 Mbps → ~30 min
   •  10 Mbps → ~2 hr
   Download supports resume — safe to interrupt and retry.

   ✅ Start auto-download
   📂 I'll download manually — show me the link
```

**Auto-download** (up to 3 attempts, stop if a single attempt exceeds 20 minutes):
```
python "<DOWNLOAD_PY path>"
```

Re-run Step 1's check after each attempt.

**Manual download fallback:**

ModelScope page: **https://modelscope.cn/models/snake7gun/Z-Image-Turbo-int4-ov/files**

Place all files under `<IMAGE_GEN_DIR>\Z-Image-Turbo-int4-ov\`. Required subdirs:
```
Z-Image-Turbo-int4-ov\
├── transformer\
├── vae_decoder\
└── text_encoder\
```

Then re-run Step 1's check to verify.

---

### Manual fallback (only if all 3 setup auto-attempts fail)

```
python -c "
from pathlib import Path
skill_dir = Path(r'{baseDir}')
for script in ['setup.py', 'download_model.py']:
    p = skill_dir / script
    if p.exists(): print(f'{script}={p}')
"
```

Show user:
```
⚠️ Auto-install failed. Please run manually in a terminal:

① Install environment:
   python "<full path to setup.py>"
   Takes ~5 min, fully automated.

② Download model (~10 GB):
   python "<full path to download_model.py>"
   Resumable — safe to interrupt and retry.

Come back here when done.
```

---

## Step 2: verify deps and write generate_image.py

> ✍️ Step 2/3: checking dependencies and script version…

**First verify dependencies** (run via VENV_PY):

```
& "<VENV_PY>" -c "
import json, site
from pathlib import Path

EXPECTED_COMMITS = {
    'optimum_intel': '2f62e5ae',
    'diffusers':     'a1f36ee3',
}

def get_git_commit(pkg_name):
    dirs = site.getsitepackages()
    try: dirs += [site.getusersitepackages()]
    except Exception: pass
    for d in dirs:
        for dist in Path(d).glob(f'{pkg_name}*.dist-info'):
            url_file = dist / 'direct_url.json'
            if url_file.exists():
                data = json.loads(url_file.read_text(encoding='utf-8'))
                return data.get('vcs_info', {}).get('commit_id', 'no_vcs_info')
    return 'not_found'

results = {}
for pkg, imp in [('openvino','openvino'),('torch','torch'),('Pillow','PIL'),('modelscope','modelscope')]:
    try:
        ver = getattr(__import__(imp), '__version__', 'OK')
        results[pkg] = ('OK', ver)
    except ImportError as e:
        results[pkg] = ('MISSING', str(e))

try:
    from optimum.intel import OVZImagePipeline
    results['OVZImagePipeline'] = ('OK', 'importable')
except ImportError as e:
    results['OVZImagePipeline'] = ('MISSING', str(e))

for pkg_name, exp in EXPECTED_COMMITS.items():
    actual = get_git_commit(pkg_name)
    if actual == 'not_found':
        results[f'{pkg_name}@commit'] = ('MISSING', 'not installed via git+https')
    elif actual.startswith(exp):
        results[f'{pkg_name}@commit'] = ('OK', actual[:16])
    else:
        results[f'{pkg_name}@commit'] = ('WRONG', f'got {actual[:16]} want {exp}...')

all_ok = all(v[0] == 'OK' for v in results.values())
for k, (status, detail) in results.items():
    icon = '✅' if status == 'OK' else ('⚠️' if status == 'WRONG' else '❌')
    print(f'  {icon} {k}: {detail}')
print('DEP_CHECK=PASS' if all_ok else 'DEP_CHECK=FAIL')
"
```

| Output | Action |
|--------|--------|
| `DEP_CHECK=PASS` | ✅ Proceed to write script below |
| `DEP_CHECK=FAIL` (MISSING) | ⛔ Re-run `setup.py` and retry |
| `DEP_CHECK=FAIL` (`@commit` WRONG) | ⛔ Force reinstall: `& "<VENV_PY>" -m pip uninstall optimum-intel diffusers -y` then `& "<VENV_PY>" -m pip install -r "{baseDir}\requirements_imagegen.txt" --no-cache-dir` |

**Then write generate_image.py:**

```
python -c "
import json, os, string, re
from pathlib import Path

state = None
for d in string.ascii_uppercase:
    sf = Path(f'{d}:\\\\') / f'{os.environ.get(\"USERNAME\",\"user\").lower()}_openvino' / 'imagegen' / 'state.json'
    if sf.exists():
        state = json.loads(sf.read_text(encoding='utf-8'))
        break

if not state:
    print('[ERROR] state.json not found — re-run Step 1')
    exit(1)

imagegen_dir = Path(state['IMAGE_GEN_DIR'])
CURRENT_VERSION = 'v2.0.0'
script = imagegen_dir / 'generate_image.py'

existing = None
if script.exists():
    m = re.search(r\"SKILL_VERSION\s*=\s*[\\\"'](.*?)[\\\"']\", script.read_text(encoding='utf-8', errors='ignore'))
    if m: existing = m.group(1)

if existing == CURRENT_VERSION:
    print('SCRIPT_UPDATE=SKIPPED')
else:
    code = r\'\'\'
SKILL_VERSION = \"v1.0.2\"
import sys, io, os, json, string, argparse, re, subprocess
from datetime import datetime
from pathlib import Path

def get_state():
    for d in string.ascii_uppercase:
        sf = Path(f\"{d}:\\\\\") / f\"{os.environ.get('USERNAME','user').lower()}_openvino\" / \"imagegen\" / \"state.json\"
        if sf.exists():
            return json.loads(sf.read_text(encoding='utf-8'))
    return None

def get_device():
    import openvino as ov
    core = ov.Core()
    devs = core.available_devices
    print(f\"[INFO] Available devices: {devs}\")
    for d in devs:
        if \"GPU\" in d:
            print(f\"[INFO] Using Intel GPU: {d}\")
            return d
    print(\"[INFO] Using CPU\")
    return \"CPU\"

def make_filename(topic, prompt):
    date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    src = topic if topic else prompt[:30]
    safe = re.sub(r'[^\\w]', '_', src.strip())[:30].strip('_')
    return f\"{date_str}_{safe}.png\"

def generate(prompt, topic='', steps=9, width=512, height=512, seed=42, output_path=None):
    state = get_state()
    if not state:
        print(\"[ERROR] state.json not found — run setup.py\")
        sys.exit(1)

    imagegen_dir = Path(state['IMAGE_GEN_DIR'])
    model_dir    = imagegen_dir / 'Z-Image-Turbo-int4-ov'
    out_dir      = imagegen_dir / 'outputs'
    out_dir.mkdir(parents=True, exist_ok=True)

    required = ['transformer', 'vae_decoder', 'text_encoder']
    missing  = [r for r in required if not (model_dir / r).exists()]
    if missing:
        print(f\"[ERROR] Model incomplete: {missing} — run download_model.py\")
        sys.exit(1)

    device = get_device()
    print(f\"[INFO] Loading model: {model_dir}\")

    import torch
    from optimum.intel import OVZImagePipeline
    pipe = OVZImagePipeline.from_pretrained(str(model_dir), device=device)
    print(\"[INFO] Model loaded\")

    gen = torch.Generator('cpu').manual_seed(seed) if seed >= 0 else None
    print(f\"[INFO] Inference: steps={steps}, {width}x{height}, seed={seed}\")
    image = pipe(
        prompt=prompt, height=height, width=width,
        num_inference_steps=steps, guidance_scale=0.0, generator=gen
    ).images[0]

    if output_path is None:
        output_path = str(out_dir / make_filename(topic, prompt))
    image.save(output_path)
    print(f\"[SUCCESS] {output_path}\")
    try:
        subprocess.Popen(['explorer', output_path])
        print(\"[INFO] Opened in default viewer\")
    except Exception as e:
        print(f\"[WARN] Could not open image: {e}\")
    return output_path

if __name__ == \"__main__\":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    try:
        p = argparse.ArgumentParser()
        p.add_argument(\"--prompt\", required=True)
        p.add_argument(\"--topic\",  default='')
        p.add_argument(\"--steps\",  type=int, default=9)
        p.add_argument(\"--width\",  type=int, default=512)
        p.add_argument(\"--height\", type=int, default=512)
        p.add_argument(\"--seed\",   type=int, default=42)
        p.add_argument(\"--output\", default=None)
        args = p.parse_args()
        print(generate(args.prompt, args.topic, args.steps, args.width, args.height, args.seed, args.output))
        sys.stdout.flush()
    except Exception as e:
        import traceback
        print(f\"[FATAL] {type(e).__name__}: {e}\", flush=True)
        traceback.print_exc()
        sys.exit(1)
\'\'\'
    script.write_text(code.strip(), encoding='utf-8')
    print('SCRIPT_UPDATE=DONE')

print(f'EXISTS={script.exists()}')
"
```

| Output | Action |
|--------|--------|
| `SCRIPT_UPDATE=SKIPPED` | ✅ Already up to date, proceed to Step 3 |
| `SCRIPT_UPDATE=DONE` | ✅ Script written, proceed to Step 3 |
| `EXISTS=False` | ⛔ Write failed — check directory permissions on `IMAGE_GEN_DIR` |

---

## Step 3: generate image and send preview

> 🎨 Step 3/3: running inference…

Run these two commands separately:

```
$env:PYTHONUTF8 = "1"
```

```
& "<VENV_PY>" "<IMAGE_GEN_DIR>\generate_image.py" --prompt "EXPANDED_PROMPT" --topic "TOPIC" --steps 9 --seed 42
```

**Pass**: stdout contains `[SUCCESS]`. Record `OUTPUT_PATH` from the `[SUCCESS]` line.

Send preview via `message` tool:
```
action: "send"  filePath: "OUTPUT_PATH"  message: "✅ TOPIC"
```

**Final announcement:**
```
✅ Done! Path: <OUTPUT_PATH>
📝 Prompt: {expanded prompt}
⚙️ steps=9, 512×512, seed=42 | device: {CPU/GPU}
```

---

## Parameters

| Param | Default | Notes |
|-------|---------|-------|
| `--prompt` | required | English or Chinese |
| `--topic` | empty | English snake_case slug for filename |
| `--steps` | 9 | Higher = more detail; no hard limit |
| `--width/--height` | 512 | 512 / 768 / 1024 recommended |
| `--seed` | 42 | -1 = random |
| `--output` | auto | Custom absolute output path |

> `guidance_scale` is fixed at `0.0` and not exposed as a parameter.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `STATE=MISSING` | setup.py never run | Run `python setup.py` from the skill directory |
| `VENV_PY=BROKEN` | venv corrupted | Re-run `python setup.py` — rebuilds venv automatically |
| `MODEL_STATUS=MISSING` | download never run or interrupted | Run `python download_model.py` — resumes automatically |
| `DEP_CHECK=FAIL` (MISSING) | packages not installed in venv | Re-run `setup.py` |
| `DEP_CHECK=FAIL` (`@commit` WRONG) | PyPI release installed instead of pinned commit | Uninstall optimum-intel + diffusers, reinstall with `--no-cache-dir` |
| `@commit` shows `not installed via git+https` | git was missing when pip ran | Confirm git is installed, re-run `setup.py` |
| `[ERROR] Model incomplete` | Download interrupted mid-file | Re-run `download_model.py` — resumes automatically |
| `[ERROR] state.json not found` | state.json missing | Re-run Step 1 |
| `EXISTS=False` | No write permission on `IMAGE_GEN_DIR` | Check directory permissions |
| `RuntimeError` on GPU | Insufficient VRAM | Lower resolution or hardcode `return "CPU"` in `get_device()` |
| Black / noisy output | Too few steps | Use `--steps` ≥ 4; 9 recommended |
| Download timeout | Network issue or proxy needed | Configure proxy and retry — download supports resume |
