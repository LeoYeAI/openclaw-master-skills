---
name: local-image-ocr-aipc
version: 1.0.0
description: >
  Image OCR, text recognition, extract text from image, scan document, read image text,
  invoice OCR, receipt OCR, contract recognition, table extraction, business card OCR,
  ID recognition, screenshot text extraction, document digitization.
  Runs locally on Windows using the GLM-OCR model, supports mixed Chinese/English text,
  prioritizes Intel iGPU inference, no cloud API calls.
user-invocable: true
allowed-tools: Bash(powershell *), Bash(llama-cli *), Read, Write, message
---

# Image OCR — Local AI PC (Windows · GLM-OCR · llama.cpp Vulkan)

**Model**: `ggml-org/GLM-OCR-GGUF` (Q8_0, HuggingFace / hf-mirror)  
**Inference**: `llama-cli` (llama.cpp Vulkan prebuilt)  
**SKILL_VERSION**: `1.0.0`

## Directory Structure (auto-created or user-specified)

```
<OCR_DIR>\                        ← auto-selected drive or user-specified (e.g. C:\image-ocr or D:\image-ocr)
├── llama.cpp\                    ← llama-cli.exe and related binaries
└── models\
    └── GLM-OCR-GGUF\
        ├── GLM-OCR-Q8_0.gguf        ← main model (~950 MB)
        └── mmproj-GLM-OCR-Q8_0.gguf ← vision projection layer (~484 MB, required)
```

> ## ⚠️ Before You Install — Security & Compliance Disclosure
>
> **This is an instruction-only skill** (no install spec). The agent will execute PowerShell steps
> described in this file to set up a local OCR environment. Review before granting autonomous execution.
>
> **What this skill does to your system:**
>
> | Action | Source | Risk |
> |--------|--------|------|
> | Download and extract `llama-cli.exe` and related binaries | `github.com/ggml-org/llama.cpp` releases | Medium — runs a downloaded executable |
> | Download model files (~1.5 GB total) | `huggingface.co` or `modelscope.cn` | Low — large file transfer |
> | Auto-install **Miniforge** if Python not found | `github.com/conda-forge/miniforge` | Medium — modifies user Python environment |
> | Create `<OCR_DIR>` and write files to disk | Local filesystem only | Low |
>
> **Recommendations before proceeding:**
>
> 1. **Do not run as administrator.** All steps are designed for standard user permissions.
>    Install to a dedicated directory (e.g. `C:\image-ocr`) and inspect files before executing.
> 2. **Verify checksums before executing.** Step 1 automatically fetches and validates the SHA256
>    hash of the llama.cpp ZIP before extraction. Step 2 computes and displays SHA256 hashes for
>    each model file so you can cross-check them against the HuggingFace model page. If any hash
>    does not match, stop and do not proceed.
> 3. **Prefer manual execution.** Run the PowerShell steps in this file yourself rather than
>    granting the agent full autonomy. Each step is self-contained and can be run independently.
> 4. **HUGGINGFACE_TOKEN is optional and sensitive.** The GLM-OCR model (`ggml-org/GLM-OCR-GGUF`)
>    is publicly available — no token is needed. If you use a gated model, set
>    `$env:HUGGINGFACE_TOKEN` only when necessary and treat it as a secret credential.
> 5. **Miniforge auto-install modifies your environment.** If you are uncomfortable with automatic
>    Python installation, decline that step and provide a Python path manually via `$customPythonExe`.
>
> **Trusted sources used by this skill:**
> - `https://github.com/ggml-org/llama.cpp/releases`
> - `https://huggingface.co/ggml-org/GLM-OCR-GGUF`
> - `https://github.com/conda-forge/miniforge` *(only if Miniforge auto-install is triggered)*
>
> **Dependencies**: Model files are downloaded via Python's `huggingface_hub` (`hf download`)
> or `modelscope`. If Python is not installed, Step 2 will automatically install Miniforge
> to `%USERPROFILE%\miniforge3` (no admin rights required).

---

## ⚠️ AI Assistant Instructions

1. Execute one command at a time; wait for output before proceeding.
2. Stop immediately on error; refer to the Troubleshooting table at the end.
3. Wrap all paths in double quotes.
4. `<OCR_DIR>` is the absolute working directory path, determined after Pre-flight.
5. **Single goal**: Recognize image content and return text results.

**Execution flow (do not skip steps)**:
```
Pre-flight: Check working dir + llama.cpp + models      → STATUS values
Step 1:     Install / update llama.cpp (only if MISSING) → LLAMA_OK
Step 2:     Download models (only if MISSING)            → MODEL_OK
Step 3:     Process recognition result + output          → Return result
```

**Progress reporting**: Announce each step before starting, e.g.: `🔍 Pre-flight: Checking environment…`

---

## Pre-flight: Check Environment

> 🔍 Pre-flight: Checking working directory, llama.cpp, and model files…

### Locate Working Directory

```powershell
# ── Fix encoding for non-ASCII paths (required at the start of every PowerShell script) ──
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# ── Optional: if you already have a path, fill it in; leave blank to auto-select drive ──
$customOcrDir = ""   # e.g. "C:\image-ocr" or "D:\image-ocr"
# ──────────────────────────────────────────────────────────────────────────────────────────

if ($customOcrDir -and (Test-Path (Split-Path $customOcrDir))) {
    $OCR_DIR = $customOcrDir
    New-Item -ItemType Directory -Force -Path $OCR_DIR | Out-Null
    Write-Host "OCR_DIR=$OCR_DIR (user-specified)"
} else {
    $best = Get-PSDrive -PSProvider FileSystem |
        Where-Object { $_.Free -gt 0 } |
        Sort-Object Free -Descending |
        Select-Object -First 1
    $OCR_DIR = Join-Path "$($best.Root)" "image-ocr"
    New-Item -ItemType Directory -Force -Path $OCR_DIR | Out-Null
    Write-Host "OCR_DIR=$OCR_DIR (auto-selected drive: $($best.Name))"
}
$env:OCR_DIR = $OCR_DIR
```

**Success criteria**: Output contains a line with `OCR_DIR=`. Record the path and substitute `<OCR_DIR>` in subsequent steps.

---

### Check llama.cpp

```powershell
$llamaDir = "<OCR_DIR>\llama.cpp"
$cliExe   = "$llamaDir\llama-cli.exe"

if (Test-Path $cliExe) {
    $ver = & $cliExe --version 2>&1
    if ($ver -match "version:\s*(\d+)") {
        $build = [int]$Matches[1]
        if ($build -ge 8400) {
            Write-Host "OK: llama.cpp build $build >= b8400, skip Step 1"
            Write-Host "LLAMA_STATUS=READY"
        } else {
            Write-Host "WARN: llama.cpp build $build < b8400, upgrade required"
            Write-Host "LLAMA_STATUS=OUTDATED"
        }
    }
} else {
    Write-Host "ERROR: llama-cli.exe not found"
    Write-Host "LLAMA_STATUS=MISSING"
    Write-Host "   Checked path: $llamaDir"
}
```

---

### Check Model Files

```powershell
$modelDir   = "<OCR_DIR>\models\GLM-OCR-GGUF"
$modelFile  = "$modelDir\GLM-OCR-Q8_0.gguf"
$mmprojFile = "$modelDir\mmproj-GLM-OCR-Q8_0.gguf"

$modelOk  = Test-Path $modelFile
$mmprojOk = Test-Path $mmprojFile

if ($modelOk -and $mmprojOk) {
    Write-Host "OK: GLM-OCR model files ready, skip Step 2"
    Write-Host "MODEL_STATUS=READY"
} else {
    if (-not $modelOk)  { Write-Host "ERROR: Missing GLM-OCR-Q8_0.gguf" }
    if (-not $mmprojOk) { Write-Host "ERROR: Missing mmproj-GLM-OCR-Q8_0.gguf" }
    Write-Host "MODEL_STATUS=MISSING"
    Write-Host "   Checked path: $modelDir"
}
```

| Output | Action |
|--------|--------|
| Both `READY` | ✅ Skip to Step 3 |
| `LLAMA_STATUS=MISSING/OUTDATED` | ⬇️ Execute Step 1 |
| `MODEL_STATUS=MISSING` | ⬇️ Execute Step 2 |

Announce: `✅ Environment check complete. Execute steps as needed.`

---


## Step 1: Install / Update llama.cpp Vulkan

> ⬇️ Step 1: Downloading and installing llama.cpp Vulkan… (only when `LLAMA_STATUS=MISSING/OUTDATED`)

> **Consent required**: Before proceeding, inform the user:
> - A ZIP (~50–100 MB) will be downloaded from `github.com/ggml-org/llama.cpp/releases`
> - It will be extracted to `<OCR_DIR>\llama.cpp\` and the original ZIP will be deleted
> - `llama-cli.exe` will be placed on disk and called directly by this skill
>
> Ask the user to confirm before running the download command.

```powershell
$tag      = "b8400"   # Replace with the latest tag from https://github.com/ggml-org/llama.cpp/releases/latest
$llamaDir = "<OCR_DIR>\llama.cpp"
$zip      = "$env:TEMP\llama-vulkan.zip"
$url      = "https://github.com/ggml-org/llama.cpp/releases/download/$tag/llama-$tag-bin-win-vulkan-x64.zip"

Write-Host "Downloading llama.cpp $tag ..."
Invoke-WebRequest -Uri $url -OutFile $zip

# ── Checksum verification ──────────────────────────────────────────────────────
# Fetch the SHA256 checksum file published alongside the release and verify the
# downloaded ZIP before extracting. Do NOT extract if the hash does not match.
$sha256Url = "https://github.com/ggml-org/llama.cpp/releases/download/$tag/llama-$tag-bin-win-vulkan-x64.zip.sha256"
try {
    $expectedHash = (Invoke-WebRequest -Uri $sha256Url -UseBasicParsing).Content.Trim().Split(" ")[0].ToUpper()
    $actualHash   = (Get-FileHash $zip -Algorithm SHA256).Hash.ToUpper()
    if ($expectedHash -ne $actualHash) {
        Write-Host "ERROR: SHA256 mismatch — file may be corrupted or tampered."
        Write-Host "  Expected: $expectedHash"
        Write-Host "  Actual:   $actualHash"
        Remove-Item $zip -Force
        Write-Host "LLAMA_INSTALL=HASH_MISMATCH"
        exit 1
    }
    Write-Host "OK: SHA256 verified: $actualHash"
} catch {
    Write-Host "WARN: Could not fetch checksum file. Proceeding without verification."
    Write-Host "WARN: Manually verify the ZIP at: $sha256Url"
}
# ──────────────────────────────────────────────────────────────────────────────

New-Item -ItemType Directory -Force -Path $llamaDir | Out-Null
Expand-Archive $zip -DestinationPath $llamaDir -Force
Remove-Item $zip
Write-Host "LLAMA_INSTALL=DONE"
```

| Output | Action |
|--------|--------|
| `LLAMA_INSTALL=DONE` | ✅ Continue to Step 2 to download models |
| `LLAMA_INSTALL=HASH_MISMATCH` | ⛔ Stop immediately — do not extract. Re-download or verify manually |
| Download error | ⛔ Check network, or manually download from browser and extract to `<OCR_DIR>\llama.cpp\` |

Announce: `✅ llama.cpp installed. Continue to Step 2 to download models.`

---

## Step 2: Download GLM-OCR Models

> 📦 Step 2: Checking Python and downloading GLM-OCR models… (only when `MODEL_STATUS=MISSING`)

> **Note**: Models are downloaded via Python's `hf download` (huggingface_hub) or `modelscope`.
> The script will auto-locate any existing Python installation; **if none is found, Miniforge will
> be installed automatically** to `%USERPROFILE%\miniforge3` (no admin rights required).

### First-time Download Notice (required reading when MODEL_STATUS=MISSING)

Announce the following to the user, then ask whether to proceed:

```
📥 First-time model download is approximately 1.5 GB
   (GLM-OCR-Q8_0.gguf ~950 MB + mmproj ~484 MB).
   Estimated download time:
   • 100 Mbps connection: ~2 minutes
   •  50 Mbps connection: ~4 minutes
   •  10 Mbps connection: ~20 minutes

   Downloads support resumption — if interrupted, re-running this step
   will automatically continue from where it left off.

   ✅ Ready — start automatic download
   📂 I prefer to download manually — skip automatic download
```

- User chooses **automatic download** → continue with Python check and download commands below
- User chooses **manual download** → jump to the "Manual Download Fallback" section at the end of this step

---

### Check Disk Space

```powershell
$drive = Split-Path "<OCR_DIR>" -Qualifier
$free  = (Get-PSDrive ($drive.TrimEnd(':'))).Free / 1GB
Write-Host "DISK_FREE=$([math]::Round($free,1))GB"
if ($free -lt 2) {
    Write-Host "DISK_STATUS=LOW"
    Write-Host "[WARN] Less than 2 GB available — download may fail"
} else {
    Write-Host "DISK_STATUS=OK"
}
```

| Output | Action |
|--------|--------|
| `DISK_STATUS=OK` | ✅ Continue to Python check |
| `DISK_STATUS=LOW` | ⚠️ Ask user to free space before continuing |

### Check Python

```powershell
# ── Optional: if you know the Python path, fill it in; leave blank to auto-search ──
$customPythonExe = ""   # e.g. "C:\Python311\python.exe"
# ──────────────────────────────────────────────────────────────────────────────────

$pythonExe = $null

# 1. User-specified path
if ($customPythonExe -and (Test-Path $customPythonExe)) {
    $ver = & $customPythonExe --version 2>&1
    Write-Host "OK: Using specified Python: $customPythonExe -> $ver"
    $pythonExe = $customPythonExe
}

# 2. Search PATH
if (-not $pythonExe) {
    foreach ($cmd in @("python", "python3", "py")) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            $ver = & $cmd --version 2>&1
            Write-Host "OK: Found Python in PATH: $cmd -> $ver"
            $pythonExe = (Get-Command $cmd).Source
            break
        }
    }
}

# 3. Scan common install directories
if (-not $pythonExe) {
    $searchPaths = @(
        "$env:USERPROFILE\miniforge3\python.exe",
        "$env:USERPROFILE\miniconda3\python.exe",
        "$env:USERPROFILE\anaconda3\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe",
        "C:\Python3*\python.exe"
    )
    foreach ($pattern in $searchPaths) {
        $found = Get-Item $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            $ver = & $found.FullName --version 2>&1
            Write-Host "OK: Found Python in common directory: $($found.FullName) -> $ver"
            $pythonExe = $found.FullName
            break
        }
    }
}

if ($pythonExe) {
    $env:PYTHON_EXE = $pythonExe
    Write-Host "PYTHON_OK"
} else {
    Write-Host "ERROR: Python not found. Install Miniforge or set `$customPythonExe"
    Write-Host "PYTHON_MISSING"
}
```

**If Python is not found**, install Miniforge:

> **Consent required**: Miniforge will be silently installed to `%USERPROFILE%\miniforge3`.
> This installs a Python runtime and conda/pip toolchain. No admin rights are needed.
> Source: `github.com/conda-forge/miniforge`. Confirm with the user before proceeding.

```powershell
$mf = "$env:TEMP\Miniforge3-Windows-x86_64.exe"
Invoke-WebRequest `
  -Uri "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe" `
  -OutFile $mf
Start-Process $mf -ArgumentList "/S /D=$env:USERPROFILE\miniforge3" -Wait
Remove-Item $mf
$env:PYTHON_EXE = "$env:USERPROFILE\miniforge3\python.exe"
& $env:PYTHON_EXE --version
Write-Host "PYTHON_OK"
```

### Download Models

**Option A: hf download (recommended)**

```powershell
& $env:PYTHON_EXE -m pip install huggingface_hub -q

# For users in China: set mirror (skip if outside China)
$env:HF_ENDPOINT = "https://hf-mirror.com"

$modelDir = "<OCR_DIR>\models\GLM-OCR-GGUF"
New-Item -ItemType Directory -Force -Path $modelDir | Out-Null

hf download ggml-org/GLM-OCR-GGUF `
  --include "GLM-OCR-Q8_0.gguf" "mmproj-GLM-OCR-Q8_0.gguf" `
  --local-dir $modelDir

Write-Host "MODEL_DOWNLOAD=DONE"
```

**Option B: ModelScope (alternative for users in China)**

```powershell
& $env:PYTHON_EXE -m pip install modelscope -q
& $env:PYTHON_EXE -c "
from modelscope.hub.file_download import model_file_download
import os
dest = r'<OCR_DIR>\models\GLM-OCR-GGUF'
os.makedirs(dest, exist_ok=True)
model_file_download('ggml-org/GLM-OCR-GGUF', file_path='GLM-OCR-Q8_0.gguf', local_dir=dest)
model_file_download('ggml-org/GLM-OCR-GGUF', file_path='mmproj-GLM-OCR-Q8_0.gguf', local_dir=dest)
print('MODEL_DOWNLOAD=DONE')
"
```

**Verify (size + integrity):**

```powershell
$modelDir = "<OCR_DIR>\models\GLM-OCR-GGUF"

# Expected sizes (approximate — reject if significantly different)
$expected = @{
    "GLM-OCR-Q8_0.gguf"        = 950   # MB
    "mmproj-GLM-OCR-Q8_0.gguf" = 484   # MB
}

foreach ($file in $expected.Keys) {
    $path = "$modelDir\$file"
    if (Test-Path $path) {
        $sizeMB = [math]::Round((Get-Item $path).Length / 1MB, 0)
        $expMB  = $expected[$file]
        if ([math]::Abs($sizeMB - $expMB) -gt 50) {
            Write-Host "WARN: $file size $sizeMB MB differs from expected ~$expMB MB — may be incomplete"
        } else {
            Write-Host "OK: $file  $sizeMB MB"
        }
        # Compute and display SHA256 so the user can cross-check against HuggingFace
        $hash = (Get-FileHash $path -Algorithm SHA256).Hash
        Write-Host "  SHA256: $hash"
        Write-Host "  Cross-check at: https://huggingface.co/ggml-org/GLM-OCR-GGUF/blob/main/$file"
    } else {
        Write-Host "ERROR: $file not found at $path"
    }
}
```

> Cross-check the printed SHA256 values against the checksums shown on the HuggingFace model page
> before proceeding. If they differ, delete the file and re-download.

| Output | Action |
|--------|--------|
| `MODEL_DOWNLOAD=DONE` | ✅ Continue to Step 3 |
| Timeout / repeated failure | ⚠️ Direct user to "Manual Download Fallback" section, or switch between Option A / B and retry |

Announce: `✅ Model download complete.`

---

### Manual Download Fallback

If automatic download repeatedly fails, guide the user to download manually and place files in the correct directory:

```
⚠️ Automatic download failed. Please manually download the following two files:

1. GLM-OCR-Q8_0.gguf (~950 MB)
   HuggingFace: https://huggingface.co/ggml-org/GLM-OCR-GGUF/resolve/main/GLM-OCR-Q8_0.gguf
   HF Mirror:   https://hf-mirror.com/ggml-org/GLM-OCR-GGUF/resolve/main/GLM-OCR-Q8_0.gguf
   ModelScope:  https://modelscope.cn/models/ggml-org/GLM-OCR-GGUF/resolve/master/GLM-OCR-Q8_0.gguf

2. mmproj-GLM-OCR-Q8_0.gguf (~484 MB)
   HuggingFace: https://huggingface.co/ggml-org/GLM-OCR-GGUF/resolve/main/mmproj-GLM-OCR-Q8_0.gguf
   HF Mirror:   https://hf-mirror.com/ggml-org/GLM-OCR-GGUF/resolve/main/mmproj-GLM-OCR-Q8_0.gguf
   ModelScope:  https://modelscope.cn/models/ggml-org/GLM-OCR-GGUF/resolve/master/mmproj-GLM-OCR-Q8_0.gguf

Once downloaded, place both files into:
   <OCR_DIR>\models\GLM-OCR-GGUF\

Then re-run the Verify command to confirm the files are intact before continuing to Step 3.
```

---

## Step 3: Process Recognition Result

> 🔍 Step 3: Processing GLM-OCR recognition result…

### Determine Input Source

| Situation | Action |
|-----------|--------|
| User message contains a local file path (e.g. `C:\Users\...\xxx.png`) | ⬇️ Case A: extract path from message, call `llama-cli` |
| User uploaded an image via the interface; OpenClaw provides a temp path | ⬇️ Case B: retrieve temp path from context, call `llama-cli` |
| Neither | ⛔ Ask user to provide a local file path or upload an image |

---

### Case A: User Provides a Local File Path

Extract the file path from the user's message, then call `llama-cli` directly:

```powershell
# ── Fix encoding ──
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$imgPath = "<file path extracted from user message>"
$m       = "<OCR_DIR>\models\GLM-OCR-GGUF\GLM-OCR-Q8_0.gguf"
$mm      = "<OCR_DIR>\models\GLM-OCR-GGUF\mmproj-GLM-OCR-Q8_0.gguf"

if (-not (Test-Path $imgPath)) {
    Write-Host "ERROR: File not found: $imgPath"
    exit 1
}

$cliExe = "<OCR_DIR>\llama.cpp\llama-cli.exe"
$result = & $cliExe `
  -m $m `
  --mmproj $mm `
  --image $imgPath `
  -p "Please recognize and extract all text from this image. Output the text content line by line, preserving the original layout." `
  -ngl 99 `
  --device Vulkan0 `
  -c 12000 `
  2>$null

Write-Host $result
```

**Success criteria**: stdout contains the recognized text content.

---

### Case B: User Uploaded an Image via the Interface

OpenClaw saves uploaded images to a temporary path. Retrieve that path from context and call `llama-cli` the same way:

```powershell
# ── Fix encoding ──
chcp 65001 | Out-Null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# imgPath is the temporary image path provided by OpenClaw in context
$imgPath = "<temporary image path provided by OpenClaw>"
$m       = "<OCR_DIR>\models\GLM-OCR-GGUF\GLM-OCR-Q8_0.gguf"
$mm      = "<OCR_DIR>\models\GLM-OCR-GGUF\mmproj-GLM-OCR-Q8_0.gguf"

if (-not (Test-Path $imgPath)) {
    Write-Host "ERROR: File not found: $imgPath"
    exit 1
}

$cliExe = "<OCR_DIR>\llama.cpp\llama-cli.exe"
$result = & $cliExe `
  -m $m `
  --mmproj $mm `
  --image $imgPath `
  -p "Please recognize and extract all text from this image. Output the text content line by line, preserving the original layout." `
  -ngl 99 `
  --device Vulkan0 `
  -c 12000 `
  2>$null

Write-Host $result
```

**Success criteria**: stdout contains the recognized text content.

---

### Format Output

Once the recognized text is obtained, process it according to the user's intent:

| Scenario | Handling |
|----------|----------|
| General text extraction | Output the recognized text as-is, preserving original layout |
| Invoice / receipt | Extract structured fields from the text; output as JSON + human-readable format |
| Table | Reformat the recognized text as a Markdown table |
| Business card | Extract name, title, company, phone, email, address; output as JSON |
| ID / certificate | Output structured by original layout |
| Screenshot / document | Organize output by paragraph |
| User-defined | Process according to the user's stated requirements |

**Completion announcement**:

```
✅ Recognition complete!
Let me know if you'd like to re-process, change the output format, or export to a file.
```

| Situation | Handling |
|-----------|----------|
| `ERROR: File not found` | File path does not exist — ask user to verify the path |
| Empty / garbled output | Low image quality — ask user to retake or rescan |
| Blurry / low-resolution image | Ask user to retake or zoom in before retrying |
| No text detected | Inform user that no recognizable text was found in the image |

---

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| `llama-cli` command not found | llama-cli.exe path not set correctly | Verify `<OCR_DIR>\llama.cpp\llama-cli.exe` exists |
| `ggml_vulkan: no devices found` | Vulkan driver not installed | Update GPU driver |
| `error: unable to open model` | Incorrect model path | Re-run Pre-flight model check to verify path |
| `MODEL_DOWNLOAD=` no output | Download interrupted | Switch between Option A / B, or configure proxy |
| `PYTHON_MISSING` | Python not installed | Install Miniforge (see Step 2) |
| Garbled / blank output | Low image quality | Improve image quality |
| VRAM insufficient / crash | Not enough GPU memory | Lower `-ngl` value, or use `--device none` |

---

## References

- llama.cpp Releases: https://github.com/ggml-org/llama.cpp/releases
- GLM-OCR GGUF: https://huggingface.co/ggml-org/GLM-OCR-GGUF
