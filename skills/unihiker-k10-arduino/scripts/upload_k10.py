#!/usr/bin/env python3
"""
Unihiker K10 Arduino Upload - Python Version
Usage: python upload_k10.py <sketch.ino> [port]
"""

import sys
import os
import subprocess
import json
import glob

def find_arduino_cli():
    """Find arduino-cli executable"""
    # Check PATH
    for path in os.environ.get('PATH', '').split(os.pathsep):
        exe = os.path.join(path, 'arduino-cli.exe')
        if os.path.isfile(exe):
            return exe
    
    # Check common locations
    possible_paths = [
        os.path.expandvars(r'%LOCALAPPDATA%\Arduino15\packages\builtin\tools\arduino-cli'),
        os.path.expandvars(r'%PROGRAMFILES%\Arduino CLI\arduino-cli.exe'),
        os.path.expandvars(r'%PROGRAMFILES(x86)%\Arduino CLI\arduino-cli.exe'),
        os.path.expandvars(r'%USERPROFILE%\.arduino15\packages\builtin\tools\arduino-cli'),
    ]
    
    for path in possible_paths:
        if os.path.isdir(path):
            # Look for version subdirectories
            versions = glob.glob(os.path.join(path, '*', 'arduino-cli.exe'))
            if versions:
                return versions[0]
        elif os.path.isfile(path):
            return path
    
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_k10.py <sketch.ino> [port]")
        sys.exit(1)
    
    sketch = sys.argv[1]
    port = sys.argv[2] if len(sys.argv) > 2 else None
    fqbn = "UNIHIKER:esp32:k10"
    
    # Check sketch file
    if not os.path.isfile(sketch):
        print(f"[ERROR] Sketch file not found: {sketch}")
        sys.exit(1)
    
    sketch_path = os.path.abspath(sketch)
    sketch_dir = os.path.dirname(sketch_path)
    build_dir = os.path.join(sketch_dir, "build")
    
    print(f"[INFO] Sketch: {os.path.basename(sketch_path)}")
    print(f"[INFO] FQBN: {fqbn}")
    print(f"[INFO] Build dir: {build_dir}")
    
    # Find arduino-cli
    arduino_cli = find_arduino_cli()
    if not arduino_cli:
        print("[ERROR] arduino-cli not found")
        print("Please install arduino-cli from https://arduino.github.io/arduino-cli/latest/installation/")
        print("\nOr download it directly:")
        print("  curl -L -o arduino-cli.zip https://github.com/arduino/arduino-cli/releases/download/v1.2.0/arduino-cli_1.2.0_Windows_64bit.zip")
        print("  unzip arduino-cli.zip")
        sys.exit(1)
    
    print(f"[INFO] Using arduino-cli: {arduino_cli}")
    
    # Create build directory
    os.makedirs(build_dir, exist_ok=True)
    
    # Detect port if not specified
    if not port:
        print("[INFO] Detecting K10 port...")
        try:
            result = subprocess.run([arduino_cli, "board", "list", "--format", "json"], 
                                    capture_output=True, text=True)
            boards = json.loads(result.stdout)
            
            for board in boards:
                if 'matching_boards' in board and board['matching_boards']:
                    for match in board['matching_boards']:
                        if 'unihiker' in match.get('fqbn', '').lower():
                            port = board['port']['address']
                            break
                if not port and board['port']['protocol'] == 'serial':
                    # Fallback to any serial port
                    port = board['port']['address']
        except Exception as e:
            print(f"[WARN] Could not detect port: {e}")
    
    if not port:
        print("[ERROR] Could not detect K10 port")
        print("Please specify port manually or connect K10 board")
        sys.exit(1)
    
    print(f"[INFO] Port: {port}")
    
    # Compile
    print("[INFO] Compiling...")
    result = subprocess.run([arduino_cli, "compile", "--fqbn", fqbn, 
                            "--build-path", build_dir, sketch_path])
    if result.returncode != 0:
        print("[ERROR] Compilation failed")
        sys.exit(1)
    print("[OK] Compilation successful")
    
    # Upload
    print(f"[INFO] Uploading to {port}...")
    result = subprocess.run([arduino_cli, "upload", "-p", port, "--fqbn", fqbn,
                            "--input-dir", build_dir, sketch_path])
    if result.returncode != 0:
        print("[ERROR] Upload failed")
        print("Tips:")
        print("  - Make sure K10 is in bootloader mode (hold BOOT, press RST)")
        print(f"  - Check that the port is correct: {port}")
        sys.exit(1)
    
    print("[OK] Upload successful!")
    print("[INFO] Sketch is now running on K10")

if __name__ == "__main__":
    main()
