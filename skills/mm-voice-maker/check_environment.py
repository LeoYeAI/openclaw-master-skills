#!/usr/bin/env python3
"""
Environment Check Script for MiniMax Voice Maker

This script verifies all required dependencies and configurations
before using the mmVoice_Maker skill.

Usage:
    python check_environment.py
    
    # Or with auto-fix
    python check_environment.py --fix
"""

import os
import sys
import subprocess
import importlib.util
from typing import List, Tuple, Optional


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"  {text}")


def check_python_version() -> bool:
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python version: {version.major}.{version.minor}.{version.micro} (Required: 3.8+)")
        print_info("Please upgrade Python to 3.8 or higher")
        return False


def check_package(package_name: str, import_name: Optional[str] = None) -> bool:
    """Check if Python package is installed"""
    import_name = import_name or package_name
    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        print_success(f"Package '{package_name}' is installed")
        return True
    else:
        print_error(f"Package '{package_name}' is NOT installed")
        print_info(f"Install: pip install {package_name}")
        return False


def check_ffmpeg() -> Tuple[bool, Optional[str]]:
    """Check if FFmpeg is installed"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print_success(f"FFmpeg is installed: {version_line}")
            
            # Get path
            path_result = subprocess.run(
                ["which", "ffmpeg"],
                capture_output=True,
                text=True
            )
            ffmpeg_path = path_result.stdout.strip()
            print_info(f"Path: {ffmpeg_path}")
            return True, ffmpeg_path
        else:
            print_error("FFmpeg is installed but not working properly")
            return False, None
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        print_error("FFmpeg is NOT installed")
        print_info("Install instructions:")
        print_info("  macOS:   brew install ffmpeg")
        print_info("  Ubuntu:  sudo apt install ffmpeg")
        print_info("  Windows: https://ffmpeg.org/download.html")
        return False, None


def check_api_key() -> Tuple[bool, Optional[str]]:
    """Check if MINIMAX_VOICE_API_KEY is set"""
    api_key = os.getenv("MINIMAX_VOICE_API_KEY")
    if api_key:
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print_success(f"MINIMAX_VOICE_API_KEY is set: {masked_key}")
        print_info(f"Key length: {len(api_key)} characters")
        return True, api_key
    else:
        print_error("MINIMAX_VOICE_API_KEY is NOT set")
        print_info("Set it with:")
        print_info('  export MINIMAX_VOICE_API_KEY="your-api-key-here"')
        print_info("Or add to ~/.bashrc or ~/.zshrc for persistence")
        return False, None


def check_workspace() -> bool:
    """Check if we're in the correct workspace"""
    current_dir = os.getcwd()
    if "mmVoice_Maker" in current_dir:
        print_success(f"Working directory: {current_dir}")
        return True
    else:
        print_warning(f"Current directory: {current_dir}")
        print_info("Consider navigating to mmVoice_Maker directory")
        return True  # Not a critical error


def check_scripts_directory() -> bool:
    """Check if scripts directory exists"""
    scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
    if os.path.isdir(scripts_dir):
        print_success(f"Scripts directory found: {scripts_dir}")
        
        # Check key files
        required_files = [
            "utils.py",
            "sync_tts.py",
            "async_tts.py",
            "audio_processing.py",
            "voice_clone.py",
            "voice_design.py",
            "voice_management.py",
        ]
        
        missing = []
        for file in required_files:
            file_path = os.path.join(scripts_dir, file)
            if not os.path.isfile(file_path):
                missing.append(file)
        
        if missing:
            print_warning(f"Missing script files: {', '.join(missing)}")
            return False
        else:
            print_info(f"All {len(required_files)} required scripts present")
            return True
    else:
        print_error(f"Scripts directory NOT found: {scripts_dir}")
        return False


def test_imports() -> bool:
    """Test importing the scripts package"""
    try:
        # Add scripts to path
        scripts_path = os.path.join(os.path.dirname(__file__), "scripts")
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        # Try importing key modules
        from utils import MINIMAX_VOICE_API_KEY, VoiceSetting, AudioSetting
        print_success("Successfully imported core modules")
        return True
    except ImportError as e:
        print_error(f"Failed to import modules: {e}")
        return False


def run_quick_test() -> bool:
    """Run a quick API connectivity test (without generating audio)"""
    print_info("Testing API connectivity...")
    
    api_key = os.getenv("MINIMAX_VOICE_API_KEY")
    if not api_key:
        print_warning("Skipping API test (no API key)")
        return False
    
    try:
        import requests
        
        # Test with a simple ping to the API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Try to list system voices (lightweight operation)
        url = "https://api.minimaxi.com/v1/text_to_speech/voice_list"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print_success("API connectivity test passed")
            data = response.json()
            if "data" in data and "audio_voices" in data["data"]:
                voice_count = len(data["data"]["audio_voices"])
                print_info(f"Found {voice_count} system voices")
            return True
        elif response.status_code == 401:
            print_error("API key is invalid (401 Unauthorized)")
            print_info("Please check your MINIMAX_VOICE_API_KEY")
            return False
        else:
            print_warning(f"API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_warning(f"Network error during API test: {e}")
        return False
    except Exception as e:
        print_warning(f"Error during API test: {e}")
        return False


def main():
    """Main environment check routine"""
    print_header("MiniMax Voice Maker - Environment Check")
    
    results = {}
    
    # 1. Python version
    print(f"\n{Colors.BOLD}1. Python Version{Colors.END}")
    results['python'] = check_python_version()
    
    # 2. Required packages
    print(f"\n{Colors.BOLD}2. Required Python Packages{Colors.END}")
    packages = [
        ("requests", None),
        ("websockets", None),
        ("dataclasses", None),
    ]
    
    package_results = []
    for pkg, import_name in packages:
        package_results.append(check_package(pkg, import_name))
    results['packages'] = all(package_results)
    
    # 3. FFmpeg
    print(f"\n{Colors.BOLD}3. FFmpeg{Colors.END}")
    results['ffmpeg'], _ = check_ffmpeg()
    
    # 4. API Key
    print(f"\n{Colors.BOLD}4. MiniMax API Key{Colors.END}")
    results['api_key'], _ = check_api_key()
    
    # 5. Workspace
    print(f"\n{Colors.BOLD}5. Workspace Check{Colors.END}")
    results['workspace'] = check_workspace()
    
    # 6. Scripts directory
    print(f"\n{Colors.BOLD}6. Scripts Directory{Colors.END}")
    results['scripts'] = check_scripts_directory()
    
    # 7. Import test
    print(f"\n{Colors.BOLD}7. Module Import Test{Colors.END}")
    results['imports'] = test_imports()
    
    # 8. API connectivity test (optional)
    if results.get('api_key') and '--test-api' in sys.argv:
        print(f"\n{Colors.BOLD}8. API Connectivity Test{Colors.END}")
        results['api_test'] = run_quick_test()
    
    # Summary
    print_header("Summary")
    
    critical_checks = ['python', 'packages', 'ffmpeg', 'api_key', 'scripts', 'imports']
    critical_passed = [results.get(check, False) for check in critical_checks]
    
    if all(critical_passed):
        print_success(f"{Colors.BOLD}All critical checks passed! ✓{Colors.END}")
        print_info("\nYou're ready to use mmVoice_Maker!")
        print_info("\nQuick start:")
        print_info("  python -c \"from scripts import quick_tts; quick_tts('Hello', output_path='test.mp3')\"")
        return 0
    else:
        failed = [check for check in critical_checks if not results.get(check, False)]
        print_error(f"{Colors.BOLD}Some checks failed: {', '.join(failed)}{Colors.END}")
        print_info("\nPlease fix the issues above before using mmVoice_Maker")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
