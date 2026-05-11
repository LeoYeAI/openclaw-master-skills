"""
MiniMax Voice API - Voice Design Module
Provides voice generation from text descriptions and templates.

Use this to create custom voices by describing the desired voice
characteristics (e.g., "A warm, deep male voice with a British accent").

Docs: https://platform.minimaxi.com/document/Voice%20Generation
"""

from typing import Optional, Dict, Any

try:
    from .utils import (
        make_request,
        parse_response,
        save_audio_from_hex,
        validate_voice_id,
    )
except ImportError:
    from utils import (
        make_request,
        parse_response,
        save_audio_from_hex,
        validate_voice_id,
    )


def design_voice(
    prompt: str,
    preview_text: str,
    voice_id: Optional[str] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Design a new voice from a natural-language description.

    The API generates a voice matching the prompt and produces a trial
    audio clip from preview_text so you can hear the result.

    Args:
        prompt: Natural-language voice description
                (e.g., "A gentle young female voice with a calm tone").
        preview_text: Text to synthesize as a preview of the designed voice.
        voice_id: Optional custom voice ID to assign. If None, the API will
                  generate one. Must be 8–256 chars if provided.
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response containing voice_id and trial_audio (hex).

    Raises:
        ValueError: If voice_id is invalid or the API returns an error.
    """
    if voice_id is not None and not validate_voice_id(voice_id):
        raise ValueError(
            f"Invalid voice_id '{voice_id}'. Must be 8-256 characters, "
            "start with a letter, contain only letters/numbers/-/_, "
            "and not end with - or _."
        )

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "preview_text": preview_text,
    }

    if voice_id is not None:
        payload["voice_id"] = voice_id

    response = make_request(
        method="POST",
        endpoint="voice_design",
        data=payload,
        timeout=timeout,
    )

    return parse_response(response)


def design_voice_from_template(
    template: str,
    preview_text: str,
    voice_id: Optional[str] = None,
    gender: Optional[str] = None,
    age: Optional[str] = None,
    language: Optional[str] = None,
    accent: Optional[str] = None,
    tone: Optional[str] = None,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Design a voice from structured template descriptions.

    Builds a prompt from template attributes and delegates to design_voice().

    Args:
        template: Base template description (e.g., "narrator", "customer service").
        preview_text: Text to synthesize as a preview.
        voice_id: Optional custom voice ID to assign.
        gender: Gender descriptor (e.g., "male", "female").
        age: Age descriptor (e.g., "young", "middle-aged", "elderly").
        language: Primary language (e.g., "English", "Chinese").
        accent: Accent descriptor (e.g., "British", "Southern American").
        tone: Tone descriptor (e.g., "warm", "authoritative", "cheerful").
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response containing voice_id and trial_audio (hex).

    Raises:
        ValueError: If voice_id is invalid or the API returns an error.
    """
    parts = [template]

    if gender:
        parts.append(f"{gender} voice")
    if age:
        parts.append(f"{age}")
    if language:
        parts.append(f"speaking {language}")
    if accent:
        parts.append(f"with a {accent} accent")
    if tone:
        parts.append(f"in a {tone} tone")

    prompt = ", ".join(parts)

    return design_voice(
        prompt=prompt,
        preview_text=preview_text,
        voice_id=voice_id,
        timeout=timeout,
    )
