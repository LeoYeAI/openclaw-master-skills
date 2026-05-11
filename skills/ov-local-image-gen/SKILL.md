---
name: local-image-generation
description: >
  本地文生图、AI画图、生成图像、画一张图、帮我画、生成图片、创作图像、制作一幅图、
  图像生成、文字生成图片、AI绘画、画个XX、我想要一张XX的图、本地生图、离线生图。
  generate an image, create a picture, draw something, make an image of, text to image,
  paint a picture, illustrate, visualize, local image generation, AI art, image synthesis.
  使用 Z-Image-Turbo 模型在本机 Windows 离线运行，支持中英双语提示词，
  自动优先 Intel iGPU 推理，无需联网，不调用任何云端 API。
user-invocable: true
allowed-tools: Bash(python *), Bash(pip *), Bash(cd *), Bash(call *), Bash(git *), Bash(winget *), Read, Glob, Write, message
---

# 本地文生图 (Windows · Z-Image-Turbo · OpenVINO)

**模型**：`snake7gun/Z-Image-Turbo-int4-ov`（ModelScope INT4）  
**接口**：`optimum.intel.OVZImagePipeline`  
**技能目录**：`{baseDir}`（含 `SKILL.md` 与 `requirements_imagegen.txt`）  
**SKILL_VERSION**：`v1.0`　← Step 4 用此版本号判断是否覆写脚本

## 目录结构（全部自动生成）

```
<IMAGE_GEN_DIR>\               ← 自动定位或创建（如 D:\image-gen-local）
├── image_gen\                 ← venv（Pre-flight 后 Step 2 自动创建）
├── generate_image.py          ← Step 4 自动写入
├── Z-Image-Turbo-int4-ov\     ← 首次自动从 ModelScope 下载（约 10 GB）
└── outputs\20260318_panda_bamboo.png  ← 文件名：YYYYMMDD_HHMMSS_topic_en.png
```

---

## ⚠️ AI 助手执行须知

1. 每次只执行一个命令，等输出后再决定下一步。
2. 遇错立即停止，对照末尾"错误排查"表处理。
3. 所有路径用双引号包裹。
4. `{baseDir}` 由运行时自动注入为本 SKILL.md 所在目录的绝对路径（例如 `C:\Users\you\skills\local-image-generation`）。若注入失败或命令报路径不存在，请将 `{baseDir}` 手动替换为该目录的实际绝对路径后再执行。`requirements_imagegen.txt` 位于此目录下。
5. **唯一目标**：生成图像并在对话中预览。

**执行流程（不可跳过）**：
```
Pre-flight: 检查 Python ≥3.10 + git  → PYTHON_OK + GIT_OK
Step 0:     扩充提示词 + 提炼主题词   → 展示给用户
Step 1:     定位工作目录              → IMAGE_GEN_DIR
Step 2:     激活 venv，验证依赖       → DEP_CHECK=PASS
Step 3:     检查磁盘空间 + 模型       → MODEL_STATUS=READY 则跳过下载
Step 4:     写入脚本（版本检查）      → SCRIPT_UPDATE=DONE/SKIPPED
Step 5:     生图 + 预览               → 发送图像到对话
```

**进度播报**：每步开始前向用户播报，格式：`🔍 Pre-flight：检查运行环境…`

---

## Pre-flight：检查运行环境（首次使用必做，后续可跳过）

> 🔍 Pre-flight：检查 Python 和 git…

### 检查 Python 版本

```bat
python --version
```

**判断结果**：

| 输出 | 操作 |
|------|------|
| `Python 3.10.x` 或更高 | ✅ `PYTHON_OK`，继续检查 git |
| `Python 3.8 / 3.9` | ⛔ 版本过低，需升级（见下方） |
| `'python' 不是内部或外部命令` | ⛔ Python 未安装，需安装（见下方） |

**Python 未安装或版本过低时**，用 PowerShell 一键下载静默安装（推荐，无需管理员权限）：

```powershell
$f = "$env:TEMP\python-installer.exe"
Invoke-WebRequest "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe" -OutFile $f
Start-Process $f -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1" -Wait
Remove-Item $f
```

> `PrependPath=1` 自动加 PATH；`Include_pip=1` 同时装 pip；`InstallAllUsers=0` 无需管理员权限。

安装完成后**重启终端**，执行 `python --version` 确认输出 `Python 3.12.x`。

若偏好手动安装：直接下载 **https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe**，运行时**务必勾选 "Add python.exe to PATH"**。

### 检查 git

```bat
git --version
```

**判断结果**：

| 输出 | 操作 |
|------|------|
| `git version 2.x.x` | ✅ `GIT_OK`，Pre-flight 通过 |
| `'git' 不是内部或外部命令` | ⛔ git 未安装，需安装（见下方） |

**git 未安装时**，用 PowerShell 一键下载静默安装：

```powershell
$f = "$env:TEMP\git-installer.exe"
Invoke-WebRequest "https://github.com/git-for-windows/git/releases/download/v2.49.0.windows.1/Git-2.49.0-64-bit.exe" -OutFile $f
Start-Process $f -ArgumentList "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS=icons,ext\reg\shellhere,assoc,assoc_sh" -Wait
Remove-Item $f
```

安装完成后**重启终端**，执行 `git --version` 确认。

若偏好手动安装：浏览器打开 **https://git-scm.com/download/win**，下载并运行安装程序，全程保持默认选项即可。

> git 是 `requirements_imagegen.txt` 中 `git+https://` 依赖的必要工具，缺少时 `pip install` 会报 `git: command not found`。

**Pre-flight 通过标准**：`python --version` ≥ 3.10 且 `git --version` 有输出。  
播报：`✅ Python 和 git 就绪，开始执行主流程。`

---

## Step 0：扩充提示词（LLM 自身完成，无需工具）

同时完成两件事：**① 扩充提示词** ② **提炼主题词**（用于文件名，**必须为英文 snake_case**）

扩充结构：`[主体] [动作/姿态] [环境/背景] [光线/氛围] [风格] [质量词]`

**支持中英双语**，无需翻译。中文场景优先用中文，英文输入保持英文。  
**主题词统一使用英文**（snake_case，如 `panda_bamboo`），避免中文路径编码问题。

质量词参考：`超写实/photorealistic`、`8K分辨率/8K resolution`、`电影级光照/cinematic lighting`、`杰作/masterpiece`

| 输入 | 主题词（英文） | 扩充后提示词 |
|------|--------|------------|
| 一只熊猫 | `panda_bamboo` | 一只大熊猫坐在翠绿竹林中，阳光透过竹叶洒落，超写实，8K，野生动物摄影 |
| cyberpunk city | `cyberpunk_city` | A futuristic megacity at night, neon signs on rain-slicked streets, cyberpunk, cinematic, 8K |

完成后**必须展示**：
```
📝 原始输入：{用户描述}
   扩充后：{完整提示词}
   主题词：{topic_en}（英文，用于文件命名）
```

---

## Step 1：定位工作目录

> 🔍 Step 1/5：正在定位工作目录…

```python
python -c "
import string, shutil
from pathlib import Path
drives = [f'{d}:\\\\' for d in string.ascii_uppercase if Path(f'{d}:\\\\').exists()]
print(f'[INFO] 检测到磁盘: {drives}')
found = None
for drive in drives:
    candidate = Path(drive) / 'image-gen-local'
    if candidate.exists():
        found = candidate
        break
if not found:
    best = max(drives, key=lambda d: shutil.disk_usage(d).free)
    found = Path(best) / 'image-gen-local'
    found.mkdir(parents=True, exist_ok=True)
    print(f'[INFO] 已创建: {found}')
print(f'IMAGE_GEN_DIR={found}')
"
```

**成功标准**：输出含 `IMAGE_GEN_DIR=` 的行，记录路径，后续替换 `<IMAGE_GEN_DIR>`。

---

## Step 2：激活 venv 并验证依赖

> ⚙️ Step 2/5：验证 Python 环境和依赖…

```bat
call "<IMAGE_GEN_DIR>\image_gen\Scripts\activate.bat"
python -c "import sys; print(sys.executable)"
```

**成功标准**：路径含 `image_gen`。

**若 venv 不存在**（activate.bat 报错），按顺序逐条执行，不可合并：
```bat
python -m ensurepip --upgrade
```
```bat
python -m venv "<IMAGE_GEN_DIR>\image_gen"
```
```bat
call "<IMAGE_GEN_DIR>\image_gen\Scripts\activate.bat"
```
```bat
python -m pip install --upgrade pip
```
```bat
pip install -r "{baseDir}\requirements_imagegen.txt"
```

> ⚠️ **关键**：`pip install` 必须在 `activate.bat` 执行之后运行，否则包会装进系统 Python 而不是 venv，导致 venv 内依赖验证失败。
> 激活成功的标志是命令行前缀出现 `(image_gen)`，如 `(image_gen) C:\image-gen-local>`。

**验证依赖（必须执行）**：

> ⚠️ 执行前确认命令行前缀为 `(image_gen)`，否则先执行 `call "<IMAGE_GEN_DIR>\image_gen\Scripts\activate.bat"`。

```python
python -c "
import json, site
from pathlib import Path

# 期望的 git commit hash（前8位匹配）
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

# 普通包
for pkg, imp in [('openvino','openvino'),('torch','torch'),('Pillow','PIL'),('modelscope','modelscope')]:
    try:
        ver = getattr(__import__(imp), '__version__', 'OK')
        results[pkg] = ('OK', ver)
    except ImportError as e:
        results[pkg] = ('MISSING', str(e))

# OVZImagePipeline 可用性
try:
    from optimum.intel import OVZImagePipeline
    results['OVZImagePipeline'] = ('OK', 'importable')
except ImportError as e:
    results['OVZImagePipeline'] = ('MISSING', str(e))

# git commit 精确验证
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

| 输出 | 操作 |
|------|------|
| `DEP_CHECK=PASS` | ✅ 进入 Step 3，播报：`✅ 环境就绪。` |
| `DEP_CHECK=FAIL`（MISSING） | ⛔ 执行 `pip install -r "{baseDir}\requirements_imagegen.txt"` 后重新验证 |
| `DEP_CHECK=FAIL`（`@commit` 显示 WRONG） | ⛔ commit 不匹配，执行下方强制重装 |

**commit 不匹配时强制重装**：
```bat
pip uninstall optimum-intel diffusers -y
pip install -r "{baseDir}\requirements_imagegen.txt" --no-cache-dir
```
> `--no-cache-dir` 防止 pip 读取旧缓存导致 commit 未更新。

---

## Step 3：检查磁盘空间 + 模型

> 📦 Step 3/5：检查磁盘空间和模型文件…

**先检查磁盘空间**（模型约 10 GB，venv 约 3 GB，需至少 15 GB 余量）：

```python
python -c "
import shutil
from pathlib import Path
target = Path(r'<IMAGE_GEN_DIR>')
free_gb = shutil.disk_usage(target).free / (1024**3)
print(f'DISK_FREE={free_gb:.1f}GB')
if free_gb < 15:
    print('DISK_STATUS=LOW')
    print(f'[WARN] 可用空间不足 15 GB，模型下载可能中途失败')
else:
    print('DISK_STATUS=OK')
"
```

| 输出 | 操作 |
|------|------|
| `DISK_STATUS=OK` | ✅ 继续检查模型 |
| `DISK_STATUS=LOW` | ⚠️ 告知用户释放空间后再继续，或确认用户知情并选择继续 |

**检查模型文件**：

```python
python -c "
from pathlib import Path
model_dir = Path(r'<IMAGE_GEN_DIR>') / 'Z-Image-Turbo-int4-ov'
required = ['transformer', 'vae_decoder', 'text_encoder']
missing = [r for r in required if not (model_dir / r).exists()]
print('MODEL_STATUS=READY') if not missing else print('MODEL_STATUS=MISSING')
print(f'MODEL_DIR={model_dir}')
if missing: print(f'MISSING_DIRS={missing}')
"
```

| 输出 | 操作 | 播报 |
|------|------|------|
| `MODEL_STATUS=READY` | ✅ 跳到 Step 4 | `✅ 模型已就绪。` |
| `MODEL_STATUS=MISSING` | ⬇️ 先看下方"时间预估 + 手动下载说明"，再执行自动下载 | — |

---

### 📋 首次下载须知（MODEL_STATUS=MISSING 时必读）

向用户播报以下内容，然后询问是否继续自动下载：

```
📥 模型首次下载约 10 GB，预计耗时：
   • 100 Mbps 宽带：约 15 分钟
   •  50 Mbps 宽带：约 30 分钟
   •  10 Mbps 宽带：约 2 小时
   下载期间请保持终端开启，支持断点续传——中断后重跑此步会自动从断点继续，无需重头下载。
   ✅ 准备好了，开始自动下载
   📂 我想手动下载，跳过自动下载
```

**若用户选择手动下载**，跳转至下方"手动下载兜底"章节。  
**若用户选择自动下载**，继续执行下方下载命令。

---

### 🤖 自动下载（tqdm 进度条 + 后台监控）

```python
python -c "
import sys, time, threading
from pathlib import Path
from modelscope import snapshot_download

model_dir = Path(r'<IMAGE_GEN_DIR>') / 'Z-Image-Turbo-int4-ov'
model_dir.mkdir(parents=True, exist_ok=True)

# ── 后台监控线程：每 30 秒打印目录已下载大小和速度 ──
_stop = threading.Event()

def watchdog():
    prev = 0
    while not _stop.wait(30):
        try:
            total = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
            speed = (total - prev) / 30
            print(f'[进度] 已下载 {total/1024**3:.2f} GB  速度 {speed/1024**2:.1f} MB/s', flush=True)
            prev = total
        except Exception:
            pass

t = threading.Thread(target=watchdog, daemon=True)
t.start()

try:
    # snapshot_download 内置 tqdm 进度条，自动断点续传
    snapshot_download(
        'snake7gun/Z-Image-Turbo-int4-ov',
        local_dir=str(model_dir),
        ignore_file_pattern=[r'\.git.*']
    )
    print('MODEL_DOWNLOAD=DONE')
except KeyboardInterrupt:
    print('[WARN] 下载被中断，已保留进度。重新运行此步将从断点续传。')
    print('MODEL_DOWNLOAD=INTERRUPTED')
except Exception as e:
    err = str(e).lower()
    if 'disk' in err or 'space' in err or 'no space' in err:
        print(f'[ERROR] 磁盘空间不足: {e}')
        print('MODEL_DOWNLOAD=FAIL_DISK')
    elif 'timeout' in err or 'connection' in err or 'network' in err:
        print(f'[ERROR] 网络错误: {e}')
        print('MODEL_DOWNLOAD=FAIL_NETWORK')
    else:
        print(f'[ERROR] 未知错误: {e}')
        print('MODEL_DOWNLOAD=FAIL_UNKNOWN')
finally:
    _stop.set()
"
```

| 输出 | 操作 |
|------|------|
| `MODEL_DOWNLOAD=DONE` | ✅ 继续 Step 4，播报：`✅ 模型下载完成。` |
| `MODEL_DOWNLOAD=INTERRUPTED` | ⚠️ 告知用户重跑此步即可断点续传，无需重头下载 |
| `MODEL_DOWNLOAD=FAIL_DISK` | ⛔ 提示释放磁盘空间后重试 |
| `MODEL_DOWNLOAD=FAIL_NETWORK` | ⛔ 提示检查网络/代理，或改用下方手动下载 |
| `MODEL_DOWNLOAD=FAIL_UNKNOWN` | ⛔ 输出原始错误信息，建议改用手动下载 |

---

### 📂 手动下载兜底

> 网络不稳定、下载反复失败，或希望用下载工具（如 IDM / aria2）时使用此方案。

**① 浏览器或下载工具下载模型**

ModelScope 页面：**https://modelscope.cn/models/snake7gun/Z-Image-Turbo-int4-ov/files**

点击页面上的"下载模型"或逐个下载文件，也可用命令行工具：
```bat
pip install modelscope
python -c "from modelscope import snapshot_download; snapshot_download('snake7gun/Z-Image-Turbo-int4-ov', local_dir=r'<IMAGE_GEN_DIR>\Z-Image-Turbo-int4-ov')"
```
> 若下载中断，重跑上方命令即可从断点续传，`snapshot_download` 会自动跳过已完成的文件。

**② 确认放置目录**

下载完成后，确保目录结构如下（三个子目录缺一不可）：
```
<IMAGE_GEN_DIR>\Z-Image-Turbo-int4-ov\
├── transformer\
├── vae_decoder\
└── text_encoder\
```

**③ 重新验证**

```python
python -c "
from pathlib import Path
model_dir = Path(r'<IMAGE_GEN_DIR>') / 'Z-Image-Turbo-int4-ov'
required = ['transformer', 'vae_decoder', 'text_encoder']
missing = [r for r in required if not (model_dir / r).exists()]
print('MODEL_STATUS=READY') if not missing else print(f'MODEL_STATUS=MISSING  缺少: {missing}')
"
```

`MODEL_STATUS=READY` 后继续 Step 4。

---

## Step 4：写入生图脚本（版本检查）

> ✍️ Step 4/5：检查脚本版本…

```python
python -c "
from pathlib import Path
import re

CURRENT_VERSION = 'v2.0'
script = Path(r'<IMAGE_GEN_DIR>') / 'generate_image.py'

existing_version = None
if script.exists():
    m = re.search(r\"SKILL_VERSION\s*=\s*[\\\"'](.*?)[\\\"']\", script.read_text(encoding='utf-8', errors='ignore'))
    if m: existing_version = m.group(1)

if existing_version == CURRENT_VERSION:
    print('SCRIPT_UPDATE=SKIPPED (already up to date)')
    print(f'EXISTS={script.exists()}')
else:
    print(f'SCRIPT_VERSION_OLD={existing_version} -> NEW={CURRENT_VERSION}')
    print('SCRIPT_UPDATE=WRITING...')
    code = r'''
SKILL_VERSION = \"v2.0\"

import sys, io, os, subprocess, argparse, string, re
from datetime import datetime
from pathlib import Path
import openvino as ov
import torch
from optimum.intel import OVZImagePipeline
from PIL import Image

def get_image_gen_dir():
    for d in string.ascii_uppercase:
        c = Path(f\"{d}:\\\\\") / \"image-gen-local\"
        if c.exists(): return c
    return Path(__file__).resolve().parent

def get_device():
    core = ov.Core()
    devs = core.available_devices
    print(f\"[INFO] 可用设备: {devs}\")
    for d in devs:
        if \"GPU\" in d:
            print(f\"[INFO] 使用 Intel GPU: {d}\")
            return d
    print(\"[INFO] 使用 CPU\")
    return \"CPU\"

def make_filename(prompt, topic):
    date_str = datetime.now().strftime(\"%Y%m%d_%H%M%S\")
    src = topic if topic else prompt[:30]
    safe = re.sub(r'[^\\w]', '_', src.strip())[:30].strip('_')
    return f\"{date_str}_{safe}.png\"

def generate(prompt, topic='', steps=9, width=512, height=512, seed=42, output_path=None):
    root = get_image_gen_dir()
    model_dir = root / \"Z-Image-Turbo-int4-ov\"
    out_dir = root / \"outputs\"
    out_dir.mkdir(parents=True, exist_ok=True)

    missing = [r for r in [\"transformer\",\"vae_decoder\",\"text_encoder\"] if not (model_dir/r).exists()]
    if missing:
        print(f\"[ERROR] 模型不完整: {missing}，请执行 Step 3\")
        sys.exit(1)

    device = get_device()
    print(f\"[INFO] 加载模型: {model_dir}\")
    pipe = OVZImagePipeline.from_pretrained(str(model_dir), device=device)
    print(\"[INFO] 模型加载完成\")

    gen = torch.Generator(\"cpu\").manual_seed(seed) if seed >= 0 else None
    print(f\"[INFO] 推理: steps={steps}, {width}x{height}, seed={seed}\")
    image = pipe(prompt=prompt, height=height, width=width,
                 num_inference_steps=steps, guidance_scale=0.0, generator=gen).images[0]

    if output_path is None:
        output_path = str(out_dir / make_filename(prompt, topic))
    image.save(output_path)
    print(f\"[SUCCESS] 图像已保存: {output_path}\")
    try:
        # 用 explorer.exe 打开：独立进程、原生 Unicode 路径、不依赖 Shell 消息循环
        subprocess.Popen(['explorer', output_path])
        print(\"[INFO] 已用默认程序打开图像\")
    except Exception as e:
        print(f\"[WARN] 打开图像失败: {e}\")
    return output_path

if __name__ == \"__main__\":
    # 强制 stdout UTF-8，避免中文路径在 Windows GBK 终端乱码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
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
'''
    script.write_text(code.strip(), encoding='utf-8')
    print('SCRIPT_UPDATE=DONE')

print(f'EXISTS={script.exists()}')
"
```

| 输出 | 含义 |
|------|------|
| `SCRIPT_UPDATE=SKIPPED` | ✅ 已是最新，进入 Step 5 |
| `SCRIPT_UPDATE=DONE` | ✅ 已覆写，进入 Step 5 |
| `EXISTS=False` | ⛔ 写入失败，检查目录写权限 |

播报：`✅ 脚本版本 v2.0 就绪。`

---

## Step 5：执行生图并预览

> 🎨 Step 5/5：开始推理…

```bat
set PYTHONUTF8=1 && call "<IMAGE_GEN_DIR>\image_gen\Scripts\activate.bat" && python "<IMAGE_GEN_DIR>\generate_image.py" --prompt "Step0扩充提示词" --topic "Step0主题词" --steps 9 --seed 42
```

> ⚠️ 三条命令用 `&&` 串联在同一行，确保 `PYTHONUTF8=1` 与 venv 激活对后续 `python` 调用均有效。若运行时不支持 `&&`，请逐条执行：先 `set PYTHONUTF8=1`，再 `call activate.bat`，最后 `python ...`。

**成功标准**：stdout **最后一行**为 `.png` 绝对路径，记为 `<IMAGE_PATH>`。

**用默认图片软件打开**：脚本内部已调用 `subprocess.Popen(['explorer', path])` 自动打开，无需额外命令。
> `PYTHONUTF8=1` 强制 Python 用 UTF-8 I/O；脚本内用 `subprocess.Popen(['explorer', path])` 打开图像——`explorer.exe` 作为独立进程启动，原生支持 Unicode 路径，不依赖 Shell 消息循环，彻底解决 `os.startfile` 在子进程中静默失效的问题。

**预览**：使用 `message` 工具发送图像：
```
action: "send"  filePath: "<IMAGE_PATH>"  message: "✅ {主题词}"
```

**完成播报**：
```
✅ 生成完成！路径：<IMAGE_PATH>
📝 提示词：{扩充后提示词}
⚙️ steps=9, 512×512, seed=42 | 设备：{CPU/GPU}
```

---

## 参数说明

| 参数 | 默认 | 说明 |
|------|------|------|
| `--prompt` | 必填 | 中英文均可 |
| `--topic` | 空 | 主题词，用于文件名 |
| `--steps` | 9 | 步数越多越精细，建议 ≥ 4；无上限，但越高越慢 |
| `--width/--height` | 512 | 建议 512/768/1024 |
| `--seed` | 42 | -1=随机 |
| `--output` | 自动 | 自定义完整路径 |

> `guidance_scale` 固定 `0.0`，不暴露为参数。

---

## 错误排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `'python' 不是内部命令` | Python 未安装或未加 PATH | PowerShell 静默安装（见 Pre-flight），重启终端 |
| `Python 3.8/3.9` 版本过低 | 需 ≥ 3.10 | 同上，重新安装 3.12 |
| `'git' 不是内部命令` / `git: command not found` | git 未安装或未加 PATH | PowerShell 静默安装（见 Pre-flight），重启终端 |
| `No module named pip` | pip 缺失 | `python -m ensurepip --upgrade` |
| `DEP_CHECK=FAIL` 但包明明装了 | pip install 时 venv 未激活，包装进了系统 Python | 激活 venv 后重新执行 `pip install -r requirements_imagegen.txt` |
| `DEP_CHECK=FAIL` / `OVZImagePipeline MISSING` | optimum-intel 未装或版本错 | `pip install -r "{baseDir}\requirements_imagegen.txt"` |
| `@commit` 显示 WRONG | pip 装了 PyPI 正式版而非指定 commit | `pip uninstall optimum-intel diffusers -y` 后 `pip install -r requirements_imagegen.txt --no-cache-dir` |
| `@commit` 显示 `not installed via git+https` | git 未安装，pip 跳过了 git 依赖 | 先完成 Pre-flight git 安装，再重装依赖 |
| `DISK_STATUS=LOW` | 磁盘空间不足 | 释放至少 15 GB 后重试 |
| `[ERROR] 模型不完整` | 下载中断 | 删除模型目录，重跑 Step 3 |
| `activate.bat 找不到` | venv 未建 | 执行 Step 2 创建命令 |
| `RuntimeError` on GPU | 显存不足 | 降分辨率或 `get_device()` 改 `return "CPU"` |
| 生图全黑/噪点 | 步数太少 | `--steps` ≥ 4，推荐 9 |
| 下载超时 | 网络问题 | 配置代理后重试 |
| `EXISTS=False` | 无写权限 | 确认目录可写 |
