"""
build_windows.py -- 编译 ctp_bridge.dll (Windows x64)
需要: Visual Studio 2019+ 并勾选 C++ 开发工具
SDK:  TraderAPI / MdUserAPI 放置于 <repo>/api/win/
"""

import os
import subprocess
import sys
from pathlib import Path

BRIDGE_DIR = Path(__file__).parent
REPO_ROOT  = BRIDGE_DIR / ".." / ".." / ".."
WIN_SDK    = (REPO_ROOT / "api" / "win").resolve()
OUT_DIR    = (BRIDGE_DIR / "..").resolve()

TD_DLL = WIN_SDK / "thosttraderapi_se.dll"
TD_LIB = WIN_SDK / "thosttraderapi_se.lib"
MD_DLL = WIN_SDK / "thostmduserapi_se.dll"
MD_LIB = WIN_SDK / "thostmduserapi_se.lib"


def find_vcvars() -> Path:
    vswhere_candidates = [
        Path(os.environ.get("ProgramFiles(x86)", "")) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe",
        Path(os.environ.get("ProgramFiles", ""))      / "Microsoft Visual Studio" / "Installer" / "vswhere.exe",
    ]
    vswhere = next((p for p in vswhere_candidates if p.exists()), None)
    if not vswhere:
        sys.exit("[ERROR] 未找到 vswhere.exe，请安装 Visual Studio 2019+ 并勾选 C++ 开发工具")

    result = subprocess.run(
        [str(vswhere), "-latest", "-products", "*",
         "-requires", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
         "-property", "installationPath"],
        capture_output=True, text=True
    )
    vs_path = result.stdout.strip()
    if not vs_path:
        sys.exit("[ERROR] 未找到 Visual Studio C++ 组件，请安装 VS 2019+ 并勾选 C++ 开发工具")

    vcvars = Path(vs_path) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"
    if not vcvars.exists():
        sys.exit(f"[ERROR] 未找到 vcvars64.bat: {vcvars}")

    print(f"[INFO] Visual Studio: {vs_path}")
    return vcvars


def check_sdk():
    missing = [p for p in [TD_LIB, MD_LIB] if not p.exists()]
    if missing:
        print("[ERROR] 缺少 Windows CTP SDK 文件:")
        for p in missing:
            print(f"  {p}")
        print(f"\n  请将 CTP SDK 文件放入: {WIN_SDK}")
        print("  下载地址: https://www.sfit.com.cn/5_2_DocumentDown.htm")
        sys.exit(1)


def build(vcvars: Path):
    src = BRIDGE_DIR / "ctp_bridge.cpp"
    out_dll = OUT_DIR / "ctp_bridge.dll"

    # 通过 cmd /c "vcvars64.bat && cl ..." 在已激活环境中编译
    cl_cmd = (
        f'cl /nologo /LD /O2 /MD /std:c++17 /EHsc /utf-8 '
        f'/DCTPBRIDGE_EXPORTS '
        f'/I"{WIN_SDK}" '
        f'"{src}" '
        f'/link "{TD_LIB}" "{MD_LIB}" '
        f'/OUT:"{out_dll}" '
        f'/IMPLIB:"{OUT_DIR / "ctp_bridge.lib"}"'
    )
    full_cmd = f'cmd /c ""{vcvars}" >nul 2>&1 && {cl_cmd}"'

    print("[INFO] 编译 ctp_bridge.dll ...")
    ret = subprocess.call(full_cmd, shell=True)
    if ret != 0:
        sys.exit("[ERROR] 编译失败")

    # 拷贝 CTP DLL 到 scripts/ 目录
    import shutil
    for dll in [TD_DLL, MD_DLL]:
        if dll.exists():
            shutil.copy2(dll, OUT_DIR / dll.name)

    # 清理中间文件
    for ext in ["*.obj", "ctp_bridge.exp", "ctp_bridge.lib"]:
        for f in list(BRIDGE_DIR.glob(ext)) + list(OUT_DIR.glob(ext)):
            try:
                f.unlink()
            except OSError:
                pass

    print()
    print("[OK] 编译成功，输出文件：")
    print(f"     {out_dll}")
    print(f"     {OUT_DIR / 'thosttraderapi_se.dll'}")
    print(f"     {OUT_DIR / 'thostmduserapi_se.dll'}")
    print()
    print("[提示] 运行前确保以上三个 DLL 在同一目录，或加入系统 PATH。")


if __name__ == "__main__":
    check_sdk()
    vcvars = find_vcvars()
    build(vcvars)
