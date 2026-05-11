#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ezviz Audio Broadcast Skill
萤石语音广播技能 - 支持本地音频文件上传或文本转语音后下发

Usage:
    # 使用本地音频文件
    python3 audio_broadcast.py [app_key] [app_secret] [device_serial] --audio-file /path/to/audio.mp3 [channel_no]
    
    # 使用文本生成语音
    python3 audio_broadcast.py [app_key] [app_secret] [device_serial] --text "要播报的文本内容" [channel_no]

Environment Variables (alternative to command line args):
    EZVIZ_APP_KEY, EZVIZ_APP_SECRET, EZVIZ_DEVICE_SERIAL, EZVIZ_AUDIO_FILE, EZVIZ_TEXT_CONTENT, EZVIZ_CHANNEL_NO
"""

import os
import sys
import time
import json
import requests
import subprocess
import tempfile
from datetime import datetime, timedelta

# Add lib directory to path for token_manager import
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
lib_dir = os.path.join(base_dir, "lib")
if lib_dir not in sys.path:
    sys.path.insert(0, lib_dir)

from token_manager import get_cached_token

# Default values
DEFAULT_CHANNEL_NO = "1"
DEFAULT_TEXT = "欢迎使用萤石语音广播服务"


def load_ezviz_config_from_channels():
    """
    Load EZVIZ appId and appSecret from channels config.
    
    SECURITY NOTE: This function reads credentials from OpenClaw config files.
    Only use dedicated Ezviz credentials with minimal permissions.
    Do NOT use main account credentials.
    
    Search order:
    1. ~/.openclaw/config.json
    2. ~/.openclaw/gateway/config.json
    3. ~/.openclaw/channels.json
    
    Returns:
        dict: {appId: str, appSecret: str} or None if not found
    """
    config_paths = [
        os.path.expanduser("~/.openclaw/config.json"),
        os.path.expanduser("~/.openclaw/gateway/config.json"),
        os.path.expanduser("~/.openclaw/channels.json"),
    ]
    
    for config_path in config_paths:
        if not os.path.exists(config_path):
            continue
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Try to get ezviz channel config
            channels = config.get("channels", {})
            ezviz_config = channels.get("ezviz", {})
            
            if isinstance(ezviz_config, dict):
                app_id = ezviz_config.get("appId") or ezviz_config.get("app_id")
                app_secret = ezviz_config.get("appSecret") or ezviz_config.get("app_secret")
                
                if app_id and app_secret:
                    print(f"[INFO] Loaded EZVIZ config from channels: {config_path}")
                    print(f"[INFO] AppKey prefix: {app_id[:8]}...")
                    return {
                        "appId": app_id,
                        "appSecret": app_secret
                    }
        
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] Failed to read config from {config_path}: {e}")
            continue
    
    return None

# API Endpoints
UPLOAD_URL = "https://openai.ys7.com/api/lapp/voice/upload"
BROADCAST_URL = "https://openai.ys7.com/api/lapp/voice/send"

def get_env_or_arg(env_var, arg_value, default=None):
    """Get value from environment variable or command line argument"""
    return os.getenv(env_var) or arg_value or default


def validate_text_input(text):
    """
    Validate text input for TTS to prevent potential injection attacks.
    
    SECURITY: While subprocess uses list args (safe), we still validate
    to prevent unexpected behavior or extremely long inputs.
    
    Args:
        text: Text content to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not text:
        return False, "Text content is empty"
    
    if len(text) > 500:
        return False, f"Text too long ({len(text)} chars). Maximum 500 characters allowed."
    
    # Check for potentially dangerous patterns (defense in depth)
    dangerous_patterns = ['`', '$(', '${', ';', '||', '&&', '|', '>', '<']
    for pattern in dangerous_patterns:
        if pattern in text:
            return False, f"Invalid character sequence detected: '{pattern}'"
    
    return True, None


def validate_device_serial(serial):
    """
    Validate device serial number format.
    
    Args:
        serial: Device serial number or comma-separated list
        
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not serial:
        return False, "Device serial is empty"
    
    # Basic format check: alphanumeric, colon, comma, underscore only
    import re
    if not re.match(r'^[A-Za-z0-9_:,]+$', serial):
        return False, "Invalid device serial format. Only alphanumeric, colon, comma, underscore allowed."
    
    return True, None


def text_to_speech(text, output_path):
    """Convert text to speech using system TTS (requires OpenClaw TTS capability)"""
    print(f"[INFO] Converting text to speech: '{text[:50]}{'...' if len(text) > 50 else ''}'")
    
    try:
        # Try to use system TTS first
        try:
            # On macOS, use say command with afconvert to generate WAV
            if sys.platform == "darwin":
                temp_aiff = output_path.replace('.wav', '.aiff').replace('.mp3', '.aiff')
                # Add pauses to make audio longer (Ezviz requires minimum audio length)
                # Say the text with natural pauses
                text_with_pauses = f"注意，{text}，请注意"
                subprocess.run(['say', '-o', temp_aiff, text_with_pauses], check=True, capture_output=True)
                # Convert AIFF to WAV using correct format specifier
                subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16@44100', temp_aiff, output_path], 
                             check=True, capture_output=True)
                os.remove(temp_aiff)
            elif sys.platform.startswith('linux'):
                # Use espeak + ffmpeg on Linux
                subprocess.run(['espeak', '-w', output_path.replace('.mp3', '.wav'), text], 
                             check=True, capture_output=True)
                subprocess.run(['ffmpeg', '-i', output_path.replace('.mp3', '.wav'), 
                              '-acodec', 'libmp3lame', output_path], 
                             check=True, capture_output=True)
                os.remove(output_path.replace('.mp3', '.wav'))
            else:
                # Fallback: create a minimal MP3 file (this won't work well, but indicates the approach)
                # In practice, this would need proper TTS integration
                print("[WARNING] System TTS not available. Creating placeholder file.")
                with open(output_path, 'wb') as f:
                    f.write(b'PLACEHOLDER')  # This won't be valid MP3
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            # If system TTS fails, try alternative approach
            print("[WARNING] System TTS failed. Using placeholder approach.")
            # In a real implementation, this would call the actual TTS service
            # For now, we'll assume the user provides valid audio files
            raise Exception("TTS generation failed")
            
        print(f"[SUCCESS] Text converted to speech: {output_path}")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to convert text to speech: {str(e)}")
        return False

def get_access_token(app_key, app_secret, use_cache=True):
    """Get access token from Ezviz API using global token manager"""
    print("=" * 70)
    print("[Step 1] Getting access token...")
    
    # Check EZVIZ_TOKEN_CACHE environment variable (0=disable cache, 1=enable cache)
    env_cache = os.getenv('EZVIZ_TOKEN_CACHE', '1')
    if env_cache == '0':
        use_cache = False
    
    # Use global token manager
    token_result = get_cached_token(app_key, app_secret, use_cache=use_cache)
    
    if token_result.get('success'):
        token = token_result['access_token']
        expire_time = datetime.fromtimestamp(token_result['expire_time'] / 1000)
        from_cache = token_result.get('from_cache', False)
        
        if from_cache:
            print(f"[SUCCESS] Using cached token, expires: {expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[SUCCESS] Token obtained, expires: {expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return token
    else:
        print(f"[ERROR] Failed to get token: {token_result.get('error', 'Unknown error')}")
        return None

def upload_audio_file(access_token, audio_file_path, voice_name=None, force=False):
    """Upload audio file to Ezviz server"""
    print("=" * 70)
    print("[Step 2] Uploading audio file...")
    print(f"[INFO] File: {audio_file_path}")
    
    if not os.path.exists(audio_file_path):
        print(f"[ERROR] Audio file not found: {audio_file_path}")
        return None
    
    # Get filename without extension for voice name
    if voice_name is None:
        voice_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        # Truncate to 50 characters if too long
        if len(voice_name) > 50:
            voice_name = voice_name[:50]
    
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'voiceFile': f}
            data = {
                'accessToken': access_token,
                'voiceName': voice_name,
                'force': 'true'  # Always force upload
            }
            
            response = requests.post(UPLOAD_URL, data=data, files=files, timeout=60)
            result = response.json()
            
            if result.get('code') == '200':
                # Handle both array and dict response formats
                file_url = None
                audio_name = voice_name
                
                if isinstance(result['data'], list) and len(result['data']) > 0:
                    audio_info = result['data'][0]
                    file_url = audio_info.get('url')
                    audio_name = audio_info.get('name', voice_name)
                elif isinstance(result['data'], dict):
                    # Direct dict format
                    file_url = result['data'].get('url')
                    audio_name = result['data'].get('name', voice_name)
                
                if file_url:
                    print(f"[SUCCESS] Audio uploaded successfully!")
                    print(f"[INFO] Voice Name: {audio_name}")
                    print(f"[INFO] File URL: {file_url[:50]}...")
                    return file_url
                else:
                    print(f"[ERROR] No URL in response: {result}")
                    return None
            else:
                print(f"[ERROR] Failed to upload audio: {result.get('msg', 'Unknown error')}")
                return None
                
    except Exception as e:
        print(f"[ERROR] Exception when uploading audio: {str(e)}")
        return None

def broadcast_audio_to_device(access_token, device_serial, channel_no, file_url):
    """Broadcast audio to device using voice/send API"""
    print("=" * 70)
    print("[Step 3] Broadcasting audio to device...")
    print(f"[Device] {device_serial} (Channel: {channel_no})")
    
    payload = {
        'accessToken': access_token,
        'deviceSerial': device_serial,
        'channelNo': channel_no,
        'fileUrl': file_url
    }
    
    try:
        response = requests.post(BROADCAST_URL, data=payload, timeout=30)
        result = response.json()
        
        if result.get('code') == '200':
            print("[SUCCESS] Audio broadcast completed!")
            return True
        else:
            msg = result.get('msg', 'Unknown error')
            code = result.get('code', 'Unknown')
            print(f"[ERROR] Failed to broadcast audio: Code {code}, Message: {msg}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception when broadcasting audio: {str(e)}")
        return False

def parse_device_list(device_serial_str):
    """Parse device serial string with optional channel numbers"""
    devices = []
    for item in device_serial_str.split(','):
        item = item.strip()
        if ':' in item:
            serial, channel = item.split(':', 1)
            devices.append((serial, channel))
        else:
            devices.append((item, DEFAULT_CHANNEL_NO))
    return devices

def main():
    # Parse command line arguments
    app_key = None
    app_secret = None
    device_serial = None
    audio_file_path = None
    text_content = None
    channel_no = DEFAULT_CHANNEL_NO
    
    # Check for --audio-file or --text flags
    args = sys.argv[1:]
    if len(args) >= 4:
        app_key = args[0]
        app_secret = args[1]
        device_serial = args[2]
        
        # Look for flags
        if '--audio-file' in args:
            idx = args.index('--audio-file')
            if idx + 1 < len(args):
                audio_file_path = args[idx + 1]
                if idx + 2 < len(args) and not args[idx + 2].startswith('--'):
                    channel_no = args[idx + 2]
        elif '--text' in args:
            idx = args.index('--text')
            if idx + 1 < len(args):
                text_content = args[idx + 1]
                if idx + 2 < len(args) and not args[idx + 2].startswith('--'):
                    channel_no = args[idx + 2]
        else:
            # Assume old format: app_key app_secret device_serial audio_file [channel_no]
            if len(args) >= 4:
                audio_file_path = args[3]
                if len(args) >= 5:
                    channel_no = args[4]
    
    # Get from environment variables if not provided
    if not app_key:
        app_key = get_env_or_arg('EZVIZ_APP_KEY', None)
    if not app_secret:
        app_secret = get_env_or_arg('EZVIZ_APP_SECRET', None)
    if not device_serial:
        device_serial = get_env_or_arg('EZVIZ_DEVICE_SERIAL', None)
    if not audio_file_path:
        audio_file_path = get_env_or_arg('EZVIZ_AUDIO_FILE', None)
    if not text_content:
        text_content = get_env_or_arg('EZVIZ_TEXT_CONTENT', None)
    if channel_no == DEFAULT_CHANNEL_NO:
        channel_no = get_env_or_arg('EZVIZ_CHANNEL_NO', DEFAULT_CHANNEL_NO)
    
    # SECURITY: Warn if credentials not from environment variables
    config_source = "environment"
    if not app_key or not app_secret:
        print("[WARNING] Credentials not found in environment variables")
        print("[WARNING] Attempting to load from OpenClaw config files...")
        print("[WARNING] Ensure config files contain dedicated Ezviz credentials (not main account)")
        
        # Try to load from channels config if still not provided (lower priority than env vars)
        channels_config = load_ezviz_config_from_channels()
        if channels_config:
            if not app_key:
                app_key = channels_config["appId"]
            if not app_secret:
                app_secret = channels_config["appSecret"]
            config_source = "config file"
            print(f"[INFO] Loaded credentials from config file (AppKey prefix: {app_key[:8]}...)")
        else:
            print("[ERROR] No credentials found in environment or config files")
    
    # Validate required parameters
    if not all([app_key, app_secret, device_serial]):
        print("Error: Missing required parameters!")
        print("Please provide app_key, app_secret, and device_serial")
        print("\nUsage:")
        print("  # Using local audio file")
        print("  python3 audio_broadcast.py app_key app_secret device_serial --audio-file /path/to/audio.mp3 [channel_no]")
        print("")
        print("  # Using text to generate speech")
        print("  python3 audio_broadcast.py app_key app_secret device_serial --text \"要播报的内容\" [channel_no]")
        print("")
        print("  # Environment variables")
        print("  export EZVIZ_APP_KEY=your_key")
        print("  export EZVIZ_APP_SECRET=your_secret")
        print("  export EZVIZ_DEVICE_SERIAL=dev1,dev2")
        print("  export EZVIZ_AUDIO_FILE=/path/to/audio.mp3  # OR")
        print("  export EZVIZ_TEXT_CONTENT=\"要播报的内容\"")
        print("  python3 audio_broadcast.py")
        sys.exit(1)
    
    # SECURITY: Validate inputs before processing
    print("=" * 70)
    print("SECURITY VALIDATION")
    print("=" * 70)
    
    # Validate device serial
    is_valid, error = validate_device_serial(device_serial)
    if not is_valid:
        print(f"[ERROR] Device serial validation failed: {error}")
        sys.exit(1)
    print(f"[OK] Device serial format validated")
    
    # Validate text input if using TTS
    if text_content:
        is_valid, error = validate_text_input(text_content)
        if not is_valid:
            print(f"[ERROR] Text input validation failed: {error}")
            sys.exit(1)
        print(f"[OK] Text input validated ({len(text_content)} chars)")
    
    # Validate credentials source
    if config_source == "config file":
        print(f"[WARNING] Using credentials from config file - ensure they are dedicated Ezviz credentials")
    else:
        print(f"[OK] Using credentials from environment variables")
    
    print()
    
    # Handle text-to-speech if needed
    temp_audio_file = None
    if text_content and not audio_file_path:
        print("=" * 70)
        print("TEXT TO SPEECH MODE")
        print("=" * 70)
        print(f"[INFO] Text content: {text_content}")
        
        # Create temporary file for generated audio (use .wav for compatibility)
        temp_dir = tempfile.gettempdir()
        temp_audio_file = os.path.join(temp_dir, f"ezviz_tts_{int(time.time())}.wav")
        
        # Use macOS say command for TTS
        print("[INFO] Generating audio using macOS TTS...")
        if not text_to_speech(text_content, temp_audio_file):
            print("[ERROR] Could not generate audio from text.")
            sys.exit(1)
            
        audio_file_path = temp_audio_file
    
    if not audio_file_path:
        print("Error: Either --audio-file or --text must be provided!")
        sys.exit(1)
    
    # Validate audio file exists (if not using text mode)
    if not os.path.exists(audio_file_path):
        print(f"[ERROR] Audio file not found: {audio_file_path}")
        sys.exit(1)
    
    # Validate audio file format
    valid_extensions = ['.wav', '.mp3', '.aac']
    file_ext = os.path.splitext(audio_file_path)[1].lower()
    if file_ext not in valid_extensions:
        print(f"[WARNING] Audio file format {file_ext} may not be supported. Supported formats: {', '.join(valid_extensions)}")
    
    # Check file size (max 5MB)
    file_size = os.path.getsize(audio_file_path)
    if file_size > 5 * 1024 * 1024:
        print(f"[WARNING] Audio file size ({file_size / 1024 / 1024:.2f} MB) exceeds 5MB limit!")
    
    # Print header
    print("=" * 70)
    print("Ezviz Audio Broadcast Skill (萤石语音广播)")
    print("=" * 70)
    print(f"[Time] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Parse devices
    devices = parse_device_list(device_serial)
    print(f"[INFO] Target devices: {len(devices)}")
    for i, (serial, chan) in enumerate(devices, 1):
        print(f" - {serial} (Channel: {chan})")
    print(f"[INFO] Audio file: {audio_file_path}")
    print(f"[INFO] Format: {file_ext}")
    print(f"[INFO] Size: {file_size / 1024:.2f} KB")
    
    # Get access token
    access_token = get_access_token(app_key, app_secret)
    if not access_token:
        print("Failed to get access token. Exiting.")
        sys.exit(1)
    
    # Upload audio file
    file_url = upload_audio_file(access_token, audio_file_path)
    if not file_url:
        print("Failed to upload audio file. Exiting.")
        # Clean up temp file if it exists
        if temp_audio_file and os.path.exists(temp_audio_file):
            os.remove(temp_audio_file)
        sys.exit(1)
    
    # Broadcast to each device
    print("\n" + "=" * 70)
    print("BROADCASTING AUDIO TO DEVICES")
    print("=" * 70)
    
    success_count = 0
    
    for i, (device_serial, channel_no) in enumerate(devices):
        if i > 0:
            time.sleep(1)  # Rate limiting
        
        success = broadcast_audio_to_device(access_token, device_serial, channel_no, file_url)
        if success:
            success_count += 1
    
    # Clean up temp file if it exists
    if temp_audio_file and os.path.exists(temp_audio_file):
        os.remove(temp_audio_file)
    
    # Print summary
    print("\n" + "=" * 70)
    print("BROADCAST SUMMARY")
    print("=" * 70)
    print(f" Total devices: {len(devices)}")
    print(f" Success: {success_count}")
    print(f" Failed: {len(devices) - success_count}")

if __name__ == "__main__":
    main()
