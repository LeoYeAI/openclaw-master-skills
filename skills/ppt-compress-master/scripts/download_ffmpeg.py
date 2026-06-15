#!/usr/bin/env python3
"""
Download and extract ffmpeg for the current platform (Windows/macOS/Linux).

Supported platforms:
- Windows (x64): from gyan.dev
- macOS (Intel/ARM): from evermeet.cx
- Linux (x64): from johnvansickle.com
"""
import urllib.request
import zipfile
import tarfile
import os
import shutil
import sys
import glob
import platform
import stat

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(SCRIPT_DIR, "bin")

# Download URLs for different platforms
FFMPEG_URLS = {
    'windows': {
        'url': 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
        'type': 'zip',
        'binaries': ['ffmpeg.exe', 'ffprobe.exe'],
    },
    'darwin': {  # macOS
        # evermeet.cx provides macOS builds
        'ffmpeg_url': 'https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip',
        'ffprobe_url': 'https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip',
        'type': 'zip_separate',
        'binaries': ['ffmpeg', 'ffprobe'],
    },
    'linux': {
        'url': 'https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz',
        'type': 'tar.xz',
        'binaries': ['ffmpeg', 'ffprobe'],
    },
}


def get_platform():
    """Detect the current platform."""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'darwin'
    elif system == 'linux':
        return 'linux'
    else:
        return None


def make_executable(path):
    """Make a file executable (Unix-like systems)."""
    if os.path.exists(path):
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def download_file(url, dest_path):
    """Download a file with progress indication."""
    print(f"[INFO] Downloading from {url} ...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"[INFO] Downloaded to {dest_path}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download: {e}")
        return False


def download_windows():
    """Download and extract ffmpeg for Windows."""
    config = FFMPEG_URLS['windows']
    zip_path = os.path.join(SCRIPT_DIR, "ffmpeg_download.zip")
    
    if not download_file(config['url'], zip_path):
        return False
    
    print("[INFO] Extracting...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(SCRIPT_DIR)
    except Exception as e:
        print(f"[ERROR] Failed to extract: {e}")
        return False
    
    # Find the extracted bin directory
    pattern = os.path.join(SCRIPT_DIR, "ffmpeg-*-essentials_build", "bin")
    matches = glob.glob(pattern)
    if not matches:
        pattern = os.path.join(SCRIPT_DIR, "ffmpeg-*", "bin")
        matches = glob.glob(pattern)
    
    if matches:
        src_bin = matches[0]
        for fname in config['binaries']:
            src = os.path.join(src_bin, fname)
            dst = os.path.join(BIN_DIR, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"[INFO] Copied {fname} to {BIN_DIR}")
    
    # Cleanup
    os.remove(zip_path)
    for d in glob.glob(os.path.join(SCRIPT_DIR, "ffmpeg-*-essentials_build")):
        shutil.rmtree(d, ignore_errors=True)
    for d in glob.glob(os.path.join(SCRIPT_DIR, "ffmpeg-*")):
        if os.path.isdir(d) and d != BIN_DIR:
            shutil.rmtree(d, ignore_errors=True)
    
    return True


def download_macos():
    """Download and extract ffmpeg for macOS."""
    config = FFMPEG_URLS['darwin']
    
    # Download ffmpeg
    ffmpeg_zip = os.path.join(SCRIPT_DIR, "ffmpeg.zip")
    if not download_file(config['ffmpeg_url'], ffmpeg_zip):
        return False
    
    print("[INFO] Extracting ffmpeg...")
    try:
        with zipfile.ZipFile(ffmpeg_zip, "r") as zf:
            zf.extractall(BIN_DIR)
        os.remove(ffmpeg_zip)
    except Exception as e:
        print(f"[ERROR] Failed to extract ffmpeg: {e}")
        return False
    
    # Download ffprobe
    ffprobe_zip = os.path.join(SCRIPT_DIR, "ffprobe.zip")
    if not download_file(config['ffprobe_url'], ffprobe_zip):
        return False
    
    print("[INFO] Extracting ffprobe...")
    try:
        with zipfile.ZipFile(ffprobe_zip, "r") as zf:
            zf.extractall(BIN_DIR)
        os.remove(ffprobe_zip)
    except Exception as e:
        print(f"[ERROR] Failed to extract ffprobe: {e}")
        return False
    
    # Make executables
    for fname in config['binaries']:
        make_executable(os.path.join(BIN_DIR, fname))
    
    return True


def download_linux():
    """Download and extract ffmpeg for Linux."""
    config = FFMPEG_URLS['linux']
    archive_path = os.path.join(SCRIPT_DIR, "ffmpeg_download.tar.xz")
    
    if not download_file(config['url'], archive_path):
        return False
    
    print("[INFO] Extracting...")
    try:
        with tarfile.open(archive_path, "r:xz") as tf:
            tf.extractall(SCRIPT_DIR)
    except Exception as e:
        print(f"[ERROR] Failed to extract: {e}")
        return False
    
    # Find the extracted directory
    matches = glob.glob(os.path.join(SCRIPT_DIR, "ffmpeg-*-amd64-static"))
    if not matches:
        matches = glob.glob(os.path.join(SCRIPT_DIR, "ffmpeg-*-static"))
    
    if matches:
        src_dir = matches[0]
        for fname in config['binaries']:
            src = os.path.join(src_dir, fname)
            dst = os.path.join(BIN_DIR, fname)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                make_executable(dst)
                print(f"[INFO] Copied {fname} to {BIN_DIR}")
    
    # Cleanup
    os.remove(archive_path)
    for d in glob.glob(os.path.join(SCRIPT_DIR, "ffmpeg-*-static")):
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
    for d in glob.glob(os.path.join(SCRIPT_DIR, "ffmpeg-*-amd64-static")):
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True)
    
    return True


def main():
    os.makedirs(BIN_DIR, exist_ok=True)
    
    # Detect platform
    plat = get_platform()
    if plat is None:
        print(f"[ERROR] Unsupported platform: {platform.system()}")
        print("[INFO] Supported platforms: Windows, macOS, Linux")
        sys.exit(1)
    
    print(f"[INFO] Detected platform: {plat}")
    
    # Check if already downloaded
    config = FFMPEG_URLS[plat]
    binaries = config['binaries']
    
    ffmpeg_path = os.path.join(BIN_DIR, binaries[0])
    ffprobe_path = os.path.join(BIN_DIR, binaries[1])
    
    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        print(f"[INFO] ffmpeg already exists at {BIN_DIR}")
        return
    
    # Download for the detected platform
    success = False
    if plat == 'windows':
        success = download_windows()
    elif plat == 'darwin':
        success = download_macos()
    elif plat == 'linux':
        success = download_linux()
    
    # Verify
    if success and os.path.exists(ffmpeg_path):
        print(f"[SUCCESS] ffmpeg is ready at {ffmpeg_path}")
    else:
        print("[ERROR] Failed to download/extract ffmpeg")
        print("\n[INFO] Manual installation alternatives:")
        if plat == 'windows':
            print("  - Download from: https://www.gyan.dev/ffmpeg/builds/")
            print("  - Or install via: choco install ffmpeg")
        elif plat == 'darwin':
            print("  - Install via: brew install ffmpeg")
        elif plat == 'linux':
            print("  - Install via: sudo apt install ffmpeg  (Debian/Ubuntu)")
            print("  - Install via: sudo dnf install ffmpeg  (Fedora)")
            print("  - Install via: sudo pacman -S ffmpeg    (Arch)")
        sys.exit(1)


if __name__ == "__main__":
    main()
