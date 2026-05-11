"""
MiniMax Voice API - Voice Cloning Module
Provides voice cloning from audio samples.

Workflow:
  1. Upload a reference audio file (10s–5min)
  2. Clone the voice with a custom voice_id
  3. Use the cloned voice_id in TTS calls

Docs: https://platform.minimaxi.com/document/Voice%20Cloning
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

try:
    from .utils import (
        VoiceSetting,
        AudioSetting,
        make_request,
        parse_response,
        save_audio_from_hex,
        validate_voice_id,
        MINIMAX_API_KEY,
        MINIMAX_API_BASE,
    )
except ImportError:
    from utils import (
        VoiceSetting,
        AudioSetting,
        make_request,
        parse_response,
        save_audio_from_hex,
        validate_voice_id,
        MINIMAX_API_KEY,
        MINIMAX_API_BASE,
    )


@dataclass
class ClonePrompt:
    """Prompt audio configuration for voice cloning with guided text."""
    file_id: str
    text: str


def upload_clone_audio(
    file_path: str,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Upload an audio file for voice cloning.

    The audio should be 10 seconds to 5 minutes, clear speech with minimal
    background noise. Supported formats: mp3, wav, m4a.

    Args:
        file_path: Path to the audio file.
        timeout: Upload timeout in seconds.

    Returns:
        Parsed API response containing file_id.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If the API returns an error.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f)}
        data = {"purpose": "voice_clone"}
        response = make_request(
            method="POST",
            endpoint="files/upload",
            files=files,
            data=data,
            timeout=timeout,
        )

    result = parse_response(response)
    # Extract file_id from nested response structure
    file_obj = result.get("file", {})
    if file_obj and "file_id" in file_obj:
        result["file_id"] = file_obj["file_id"]
    return result


def upload_prompt_audio(
    file_path: str,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Upload a prompt audio file for guided voice cloning.

    This is an optional step — the prompt audio provides text-aligned
    reference material for higher-quality cloning.

    Args:
        file_path: Path to the prompt audio file.
        timeout: Upload timeout in seconds.

    Returns:
        Parsed API response containing file_id.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If the API returns an error.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Prompt audio file not found: {file_path}")

    file_name = os.path.basename(file_path)
    with open(file_path, "rb") as f:
        files = {"file": (file_name, f)}
        data = {"purpose": "voice_clone"}
        response = make_request(
            method="POST",
            endpoint="files/upload",
            files=files,
            data=data,
            timeout=timeout,
        )

    result = parse_response(response)
    file_obj = result.get("file", {})
    if file_obj and "file_id" in file_obj:
        result["file_id"] = file_obj["file_id"]
    return result


def clone_voice(
    voice_id: str,
    file_id: str,
    prompt: Optional[ClonePrompt] = None,
    demo_text: Optional[str] = None,
    model: str = "speech-02-hd",
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Clone a voice from an uploaded audio file.

    Args:
        voice_id: Custom voice ID to assign (8–256 chars, starts with letter).
        file_id: File ID from upload_clone_audio().
        prompt: Optional ClonePrompt for guided cloning.
        demo_text: Optional demo text to generate a preview with the cloned voice.
        model: TTS model for the cloned voice.
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response. May contain demo audio if demo_text was provided.

    Raises:
        ValueError: If voice_id is invalid or the API returns an error.
    """
    if not validate_voice_id(voice_id):
        raise ValueError(
            f"Invalid voice_id '{voice_id}'. Must be 8-256 characters, "
            "start with a letter, contain only letters/numbers/-/_, "
            "and not end with - or _."
        )

    payload: Dict[str, Any] = {
        "voice_id": voice_id,
        "file_id": file_id,
    }

    if prompt is not None:
        payload["prompt"] = {
            "file_id": prompt.file_id,
            "text": prompt.text,
        }

    if demo_text is not None:
        payload["text"] = demo_text
        payload["model"] = model

    response = make_request(
        method="POST",
        endpoint="voice_clone",
        data=payload,
        timeout=timeout,
    )

    return parse_response(response)


def quick_clone_voice(
    audio_path: str,
    voice_id: str,
    demo_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function: upload audio and clone in one call.

    Args:
        audio_path: Path to the reference audio file.
        voice_id: Custom voice ID to assign.
        demo_text: Optional text to generate a demo with the cloned voice.

    Returns:
        Clone API response.

    Raises:
        FileNotFoundError: If audio_path does not exist.
        ValueError: If the API returns an error.
    """
    upload_result = upload_clone_audio(audio_path)

    file_id = upload_result.get("file_id")
    if not file_id:
        raise ValueError("Upload succeeded but no file_id was returned")

    return clone_voice(
        voice_id=voice_id,
        file_id=file_id,
        demo_text=demo_text,
    )
