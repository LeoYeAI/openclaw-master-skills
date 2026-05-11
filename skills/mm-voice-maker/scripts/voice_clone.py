"""
MiniMax Voice API - Voice Cloning Module
Supports cloning voices from audio samples

Documentation:
- Upload Clone Audio: https://platform.minimaxi.com/docs/api-reference/voice-cloning-uploadcloneaudio
- Upload Prompt Audio: https://platform.minimaxi.com/docs/api-reference/voice-cloning-uploadprompt
- Clone API: https://platform.minimaxi.com/docs/api-reference/voice-cloning-clone
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from utils import (
    VoiceSetting,
    AudioSetting,
    make_request,
    parse_response,
    save_audio_from_hex,
    validate_voice_id,
    MINIMAX_VOICE_API_KEY,
    MINIMAX_API_BASE,
)


@dataclass
class ClonePrompt:
    """
    Clone prompt configuration
    Used to improve voice cloning similarity
    """
    prompt_audio_file_id: str  # Prompt audio file_id, duration must be <8 seconds
    prompt_text: str           # Transcript of the prompt audio

    def to_dict(self) -> Dict[str, str]:
        return {
            "prompt_audio": self.prompt_audio_file_id,
            "prompt_text": self.prompt_text,
        }


# ============================================================================
# File Upload
# ============================================================================

def upload_clone_audio(
    file_path: str,
    timeout: int = 120,
) -> str:
    """
    Upload source audio file for cloning
    
    File requirements:
    - Format: mp3, wav, m4a
    - Duration: 10 seconds ~ 5 minutes
    - Size: Max 20MB
    - Quality: Recommended no background noise, single speaker clear voice
    
    Args:
        file_path: Audio file path
        timeout: Upload timeout in seconds
    
    Returns:
        file_id: File ID for subsequent cloning operations
    
    Example:
        >>> file_id = upload_clone_audio("my_voice_sample.mp3")
        >>> print(f"File ID: {file_id}")
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    file_size = os.path.getsize(file_path)
    if file_size > 20 * 1024 * 1024:  # 20MB
        raise ValueError("File size exceeds 20MB limit")
    
    import requests
    
    url = f"{MINIMAX_API_BASE}/files/upload"
    headers = {"Authorization": f"Bearer {MINIMAX_VOICE_API_KEY}"}
    
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        data = {"purpose": "voice_clone"}
        
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=timeout,
        )
    
    response.raise_for_status()
    result = parse_response(response.json())
    
    return result.get("file", {}).get("file_id")


def upload_prompt_audio(
    file_path: str,
    timeout: int = 60,
) -> str:
    """
    Upload prompt audio sample
    
    Prompt audio provides more precise voice reference to improve cloning similarity.
    
    File requirements:
    - Format: mp3, wav, m4a
    - Duration: Max 8 seconds
    - Quality: Clear, no noise
    
    Args:
        file_path: Prompt audio file path
        timeout: Upload timeout in seconds
    
    Returns:
        file_id: File ID for ClonePrompt configuration
    
    Example:
        >>> prompt_file_id = upload_prompt_audio("short_sample.mp3")
        >>> clone_prompt = ClonePrompt(
        ...     prompt_audio_file_id=prompt_file_id,
        ...     prompt_text="This is the transcript of the sample audio"
        ... )
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    import requests
    
    url = f"{MINIMAX_API_BASE}/files/upload"
    headers = {"Authorization": f"Bearer {MINIMAX_VOICE_API_KEY}"}
    
    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        data = {"purpose": "prompt_audio"}
        
        response = requests.post(
            url,
            headers=headers,
            files=files,
            data=data,
            timeout=timeout,
        )
    
    response.raise_for_status()
    result = parse_response(response.json())
    
    return result.get("file", {}).get("file_id")


# ============================================================================
# Voice Cloning
# ============================================================================

def clone_voice(
    file_id: str,
    voice_id: str,
    clone_prompt: Optional[ClonePrompt] = None,
    preview_text: Optional[str] = None,
    preview_model: str = "speech-2.6-hd",
    need_noise_reduction: bool = False,
    need_volume_normalization: bool = False,
    language_boost: Optional[str] = None,
    aigc_watermark: bool = False,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Execute voice cloning
    
    Clone uploaded audio file into a new voice. The generated voice_id can be used 
    with text-to-speech APIs.
    
    Note:
    - Cloned voices are temporary and must be used with TTS API within 7 days to be permanently saved
    - voice_id must be unique and cannot duplicate existing voice IDs
    
    Args:
        file_id: Clone source audio file_id (from upload_clone_audio)
        voice_id: Custom ID for the new voice (8-256 chars, starts with letter, can contain letters/numbers/-/_)
        clone_prompt: Optional clone prompt config to improve similarity
        preview_text: Preview text to generate demo audio (max 1000 chars)
        preview_model: Model for preview audio generation
        need_noise_reduction: Whether to apply noise reduction to source audio
        need_volume_normalization: Whether to apply volume normalization to source audio
        language_boost: Language boost setting
        aigc_watermark: Whether to add audio rhythm identifier
        timeout: Request timeout in seconds
    
    Returns:
        API response containing:
        - voice_id: Cloned voice ID
        - demo_audio: Preview audio (hex-encoded), only returned when preview_text is provided
        - extra_info: Additional information
        - base_resp: Status information
    
    Example:
        >>> # Upload audio
        >>> file_id = upload_clone_audio("my_voice.mp3")
        >>> 
        >>> # Optional: Upload prompt audio
        >>> prompt_file_id = upload_prompt_audio("short_sample.mp3")
        >>> clone_prompt = ClonePrompt(
        ...     prompt_audio_file_id=prompt_file_id,
        ...     prompt_text="This is the sample audio content"
        ... )
        >>> 
        >>> # Execute cloning
        >>> result = clone_voice(
        ...     file_id=file_id,
        ...     voice_id="my-custom-voice-001",
        ...     clone_prompt=clone_prompt,
        ...     preview_text="Hello, this is the cloned voice",
        ... )
        >>> 
        >>> # Save preview audio
        >>> if result.get("demo_audio"):
        ...     save_audio_from_hex(result["demo_audio"], "preview.mp3")
    """
    # Validate voice_id format
    if not validate_voice_id(voice_id):
        raise ValueError(
            "Invalid voice_id format. Requirements: 8-256 characters, "
            "starts with letter, can contain letters, numbers, -, _, "
            "cannot end with - or _"
        )
    
    payload = {
        "file_id": file_id,
        "voice_id": voice_id,
        "need_noise_reduction": need_noise_reduction,
        "need_volume_normalization": need_volume_normalization,
        "aigc_watermark": aigc_watermark,
    }
    
    if clone_prompt:
        payload["clone_prompt"] = clone_prompt.to_dict()
    
    if preview_text:
        if len(preview_text) > 1000:
            raise ValueError("Preview text max 1000 characters")
        payload["text"] = preview_text
        payload["model"] = preview_model
    
    if language_boost:
        payload["language_boost"] = language_boost
    
    response = make_request(
        method="POST",
        endpoint="voice_clone",
        data=payload,
        timeout=timeout,
    )
    
    return parse_response(response)


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_clone_voice(
    audio_path: str,
    voice_id: str,
    preview_text: Optional[str] = None,
    output_preview_path: Optional[str] = None,
    noise_reduction: bool = True,
    volume_normalize: bool = True,
) -> Dict[str, Any]:
    """
    Quick voice cloning convenience function
    
    One-stop completion of audio upload and cloning operations.
    
    Args:
        audio_path: Source audio file path
        voice_id: Custom ID for new voice
        preview_text: Optional preview text
        output_preview_path: Optional preview audio save path
        noise_reduction: Whether to apply noise reduction
        volume_normalize: Whether to apply volume normalization
    
    Returns:
        Clone result dictionary containing voice_id and other info
    
    Example:
        >>> result = quick_clone_voice(
        ...     audio_path="speaker_sample.mp3",
        ...     voice_id="my-voice-clone",
        ...     preview_text="Test clone effect",
        ...     output_preview_path="clone_preview.mp3",
        ... )
        >>> print(f"Clone complete! Voice ID: {result['voice_id']}")
    """
    print(f"Uploading audio file: {audio_path}")
    file_id = upload_clone_audio(audio_path)
    print(f"Upload successful, File ID: {file_id}")
    
    print(f"Cloning voice...")
    result = clone_voice(
        file_id=file_id,
        voice_id=voice_id,
        preview_text=preview_text,
        need_noise_reduction=noise_reduction,
        need_volume_normalization=volume_normalize,
    )
    
    print(f"Clone successful! Voice ID: {voice_id}")
    
    # Save preview audio
    if output_preview_path and result.get("demo_audio"):
        save_audio_from_hex(result["demo_audio"], output_preview_path)
        result["preview_path"] = output_preview_path
        print(f"Preview audio saved to: {output_preview_path}")
    
    return result


def clone_voice_with_prompt(
    source_audio_path: str,
    prompt_audio_path: str,
    prompt_text: str,
    voice_id: str,
    preview_text: Optional[str] = None,
    output_preview_path: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    High-quality voice cloning with prompt audio
    
    Providing additional prompt audio and corresponding text can significantly 
    improve cloning similarity.
    
    Args:
        source_audio_path: Clone source audio file path (10s~5min)
        prompt_audio_path: Prompt audio file path (<8s)
        prompt_text: Transcript of prompt audio
        voice_id: Custom ID for new voice
        preview_text: Optional preview text
        output_preview_path: Optional preview audio save path
        **kwargs: Other parameters passed to clone_voice
    
    Returns:
        Clone result dictionary
    
    Example:
        >>> result = clone_voice_with_prompt(
        ...     source_audio_path="full_sample.mp3",
        ...     prompt_audio_path="short_clip.mp3",
        ...     prompt_text="This is the short clip transcript",
        ...     voice_id="high-quality-clone",
        ...     preview_text="Test high-quality clone effect",
        ... )
    """
    # Upload source audio
    print("Uploading source audio...")
    source_file_id = upload_clone_audio(source_audio_path)
    
    # Upload prompt audio
    print("Uploading prompt audio...")
    prompt_file_id = upload_prompt_audio(prompt_audio_path)
    
    # Build ClonePrompt
    clone_prompt = ClonePrompt(
        prompt_audio_file_id=prompt_file_id,
        prompt_text=prompt_text,
    )
    
    # Execute cloning
    print("Executing voice cloning...")
    result = clone_voice(
        file_id=source_file_id,
        voice_id=voice_id,
        clone_prompt=clone_prompt,
        preview_text=preview_text,
        **kwargs
    )
    
    print(f"Clone successful! Voice ID: {voice_id}")
    
    # Save preview audio
    if output_preview_path and result.get("demo_audio"):
        save_audio_from_hex(result["demo_audio"], output_preview_path)
        result["preview_path"] = output_preview_path
        print(f"Preview audio saved to: {output_preview_path}")
    
    return result
