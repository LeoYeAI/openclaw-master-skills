"""
MiniMax Voice API - Common Utilities Module
Provides API configuration, authentication, and common helper functions
"""

import os
import requests
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass


# API Configuration
MINIMAX_VOICE_API_KEY = os.getenv("MINIMAX_VOICE_API_KEY")
MINIMAX_API_BASE = os.getenv("MINIMAX_API_BASE", "https://api.minimaxi.com/v1")
MINIMAX_API_BASE_BACKUP = "https://api-bj.minimaxi.com/v1"

# Available Models
AVAILABLE_MODELS = [
    "speech-2.8-hd",  # Latest HD model, best voice similarity and tone detail (recommended for highest quality)
    "speech-2.8-turbo",  # Latest Turbo model, fast with excellent quality
    "speech-2.6-hd",  # HD model, excellent prosody and natural generation
    "speech-2.6-turbo",  # Turbo model, fast processing with good quality
    "speech-02-hd",  # HD model
    "speech-02-turbo",  # Fast model
    "speech-01-hd",  # Legacy HD model
    "speech-01-turbo",  # Legacy fast model
]

# Supported Audio Formats
AUDIO_FORMATS = ["mp3", "wav", "flac", "pcm"]

# Supported Languages
SUPPORTED_LANGUAGES = [
    "Chinese", "Chinese,Yue", "English", "Arabic", "Russian", "Spanish",
    "French", "Portuguese", "German", "Turkish", "Dutch", "Ukrainian",
    "Vietnamese", "Indonesian", "Japanese", "Italian", "Korean", "Thai",
    "Polish", "Romanian", "Greek", "Czech", "Finnish", "Hindi", "Bulgarian",
    "Danish", "Hebrew", "Malay", "Persian", "Slovak", "Swedish", "Croatian",
    "Filipino", "Hungarian", "Norwegian", "Slovenian", "Catalan", "Nynorsk",
    "Tamil", "Afrikaans", "auto"
]

# System Preset Voices
SYSTEM_VOICES = [
    "male-qn-qingse",      # Young male voice
    "male-qn-jingying",    # Elite male voice
    "male-qn-badao",       # Dominant male voice
    "male-qn-daxuesheng",  # College student male voice
    "female-shaonv",       # Young female voice
    "female-yujie",        # Mature female voice
    "female-chengshu",     # Mature/sophisticated female voice
    "female-tianmei",      # Sweet female voice
    "presenter_male",      # Male presenter
    "presenter_female",    # Female presenter
    "audiobook_male_1",    # Audiobook male voice 1
    "audiobook_male_2",    # Audiobook male voice 2
    "audiobook_female_1",  # Audiobook female voice 1
    "audiobook_female_2",  # Audiobook female voice 2
]


@dataclass
class VoiceSetting:
    """
    Voice setting parameters.

    Args:
        voice_id: Voice ID (e.g., "male-qn-qingse", "female-shaonv")
        speed: Speech speed 0.5-2.0 (default: 1.0)
        volume: Volume 0.1-10.0 (default: 1.0)
        pitch: Pitch adjustment -12 to 12 (default: 0)
        emotion: Emotion tag (happy, sad, angry, fearful, disgusted, surprised, calm, fluent, whisper)
                  - For speech-2.8-hd/turbo: automatic emotion matching (recommended)
                  - For speech-2.6-hd/turbo: supports all 9 emotions
                  - For older models: supports happy, sad, angry, fearful, disgusted, surprised, calm
    """
    voice_id: str
    speed: float = 1.0       # Speed 0.5-2.0
    volume: float = 1.0      # Volume 0.1-10
    pitch: int = 0           # Pitch -12 to 12
    emotion: Optional[str] = None  # Emotion tag

    def __post_init__(self):
        # Validate emotion if provided
        # Note: fluent and whisper only work with speech-2.6-hd/turbo
        valid_emotions = {"happy", "sad", "angry", "fearful", "disgusted", "surprised", "calm", "fluent", "whisper"}
        if self.emotion and self.emotion not in valid_emotions:
            raise ValueError(
                f"Invalid emotion '{self.emotion}'. Must be one of: {', '.join(sorted(valid_emotions))}"
            )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "voice_id": self.voice_id,
            "speed": self.speed,
            "vol": self.volume,  # API expects 'vol'
            "pitch": self.pitch,
        }
        if self.emotion:
            result["emotion"] = self.emotion
        return result


@dataclass
class AudioSetting:
    """Audio setting parameters"""
    sample_rate: int = 32000   # Sample rate: 16000, 24000, 32000
    bitrate: int = 128000      # Bitrate: 64000, 128000, 192000
    format: str = "mp3"        # Format: mp3, wav, flac, pcm
    channel: int = 1           # Channel: 1(mono), 2(stereo)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_rate": self.sample_rate,
            "bitrate": self.bitrate,
            "format": self.format,
            "channel": self.channel,
        }


def get_headers(content_type: str = "application/json") -> Dict[str, str]:
    """Get request headers"""
    if not MINIMAX_VOICE_API_KEY:
        raise ValueError("MINIMAX_VOICE_API_KEY environment variable is not set")
    
    return {
        "Authorization": f"Bearer {MINIMAX_VOICE_API_KEY}",
        "Content-Type": content_type,
        "Accept-Encoding": "gzip, deflate",  # Avoid brotli which can cause decode errors
    }


def make_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    files: Optional[Dict] = None,
    params: Optional[Dict] = None,
    timeout: int = 120,
    use_backup: bool = False
) -> Dict[str, Any]:
    """
    Generic API request method
    
    Args:
        method: HTTP method (GET, POST, etc.)
        endpoint: API endpoint path
        data: Request body data (JSON)
        files: File upload data
        params: URL query parameters
        timeout: Request timeout in seconds
        use_backup: Whether to use backup API address
    
    Returns:
        JSON response from API
    
    Raises:
        requests.exceptions.RequestException: Request failed
    """
    base_url = MINIMAX_API_BASE_BACKUP if use_backup else MINIMAX_API_BASE
    url = f"{base_url}/{endpoint.lstrip('/')}"
    
    if files:
        headers = {
            "Authorization": f"Bearer {MINIMAX_VOICE_API_KEY}",
            "Accept-Encoding": "gzip, deflate",  # Avoid brotli decode errors
        }
    else:
        headers = get_headers()
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=data if not files else None,
        data=data if files else None,
        files=files,
        params=params,
        timeout=timeout,
    )
    
    response.raise_for_status()
    return response.json()


def parse_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse API response and check status code
    
    Args:
        response: API response data
    
    Returns:
        Processed response data
    
    Raises:
        ValueError: API returned error status
    """
    base_resp = response.get("base_resp", {})
    status_code = base_resp.get("status_code", 0)
    
    if status_code != 0:
        status_msg = base_resp.get("status_msg", "Unknown error")
        raise ValueError(f"API Error [{status_code}]: {status_msg}")
    
    return response


def save_audio_from_hex(hex_data: str, output_path: str) -> str:
    """
    Save hex-encoded audio data to file
    
    Args:
        hex_data: Hex-encoded audio data
        output_path: Output file path
    
    Returns:
        Saved file path
    """
    audio_bytes = bytes.fromhex(hex_data)
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    return output_path


def download_audio_from_url(url: str, output_path: str, timeout: int = 60) -> str:
    """
    Download audio file from URL
    
    Args:
        url: Audio file URL
        output_path: Output file path
        timeout: Download timeout in seconds
    
    Returns:
        Saved file path
    """
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    return output_path


def validate_voice_id(voice_id: str) -> bool:
    """
    Validate voice_id format
    Rules: 8-256 characters, starts with letter, can contain letters, numbers, -, _, 
           cannot end with - or _
    
    Args:
        voice_id: The voice_id to validate
    
    Returns:
        Whether valid
    """
    import re
    if not voice_id or len(voice_id) < 8 or len(voice_id) > 256:
        return False
    
    pattern = r'^[a-zA-Z][a-zA-Z0-9_-]*[a-zA-Z0-9]$'
    return bool(re.match(pattern, voice_id))


def format_pause_marker(seconds: float) -> str:
    """
    Generate pause marker
    
    Args:
        seconds: Pause duration in seconds, range 0.01-99.99
    
    Returns:
        Pause marker string <#x#>
    """
    if seconds < 0.01 or seconds > 99.99:
        raise ValueError("Pause duration must be between 0.01 and 99.99 seconds")
    
    return f"<#{seconds:.2f}#>"
