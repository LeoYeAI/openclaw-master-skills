"""
MiniMax Voice API - Voice Management Module
Provides functions to list, query, and delete voices.

Docs: https://platform.minimaxi.com/document/Voice%20List
"""

from typing import Optional, Dict, Any, List
from enum import Enum

try:
    from .utils import make_request, parse_response, SYSTEM_VOICES
except ImportError:
    from utils import make_request, parse_response, SYSTEM_VOICES


class VoiceType(Enum):
    """Voice type filter for listing voices."""
    SYSTEM = "system"
    VOICE_CLONING = "voice_cloning"
    VOICE_GENERATION = "voice_generation"
    ALL = "all"


def get_voices(
    voice_type: VoiceType = VoiceType.ALL,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    List voices filtered by type.

    Args:
        voice_type: Filter by voice type (system, cloning, generation, or all).
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response containing voice list.

    Raises:
        ValueError: If the API returns an error.
    """
    payload: Dict[str, Any] = {}

    if voice_type != VoiceType.ALL:
        payload["voice_type"] = voice_type.value

    response = make_request(
        method="POST",
        endpoint="voice/list",
        data=payload,
        timeout=timeout,
    )

    return parse_response(response)


def get_system_voices(timeout: int = 30) -> List[Dict[str, Any]]:
    """
    Get all system preset voices.

    Args:
        timeout: Request timeout in seconds.

    Returns:
        List of system voice dicts with voice_id, name, etc.
    """
    try:
        result = get_voices(voice_type=VoiceType.SYSTEM, timeout=timeout)
        voices = result.get("voice_list", [])
        return voices
    except Exception:
        return [{"voice_id": vid, "name": vid} for vid in SYSTEM_VOICES]


def get_all_custom_voices(timeout: int = 30) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all custom voices, split into cloned and designed categories.

    Args:
        timeout: Request timeout in seconds.

    Returns:
        Dict with keys "cloned" and "designed", each a list of voice dicts.
    """
    cloned: List[Dict[str, Any]] = []
    designed: List[Dict[str, Any]] = []

    try:
        clone_result = get_voices(voice_type=VoiceType.VOICE_CLONING, timeout=timeout)
        cloned = clone_result.get("voice_list", [])
    except Exception:
        pass

    try:
        design_result = get_voices(voice_type=VoiceType.VOICE_GENERATION, timeout=timeout)
        designed = design_result.get("voice_list", [])
    except Exception:
        pass

    return {
        "cloned": cloned,
        "designed": designed,
    }


def delete_voice(
    voice_id: str,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Delete a custom voice.

    Only custom voices (cloned or designed) can be deleted. System voices
    cannot be removed.

    Args:
        voice_id: The voice_id to delete.
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response confirming deletion.

    Raises:
        ValueError: If the API returns an error.
    """
    payload: Dict[str, Any] = {
        "voice_id": voice_id,
    }

    response = make_request(
        method="POST",
        endpoint="voice/delete",
        data=payload,
        timeout=timeout,
    )

    return parse_response(response)
