"""
MiniMax Voice API - Voice Management Module
Manage system voices and custom voices (cloned/designed)

Documentation:
- Get Voices: https://platform.minimaxi.com/docs/api-reference/voice-management-get
- Delete Voice: https://platform.minimaxi.com/docs/api-reference/voice-management-delete
"""

from typing import Optional, Dict, Any, List
from enum import Enum

from utils import (
    make_request,
    parse_response,
    SYSTEM_VOICES,
)


class VoiceType(Enum):
    """Voice type"""
    SYSTEM = "system"                    # System preset voices
    VOICE_CLONING = "voice_cloning"      # Cloned voices
    VOICE_GENERATION = "voice_generation"  # Designed/generated voices
    ALL = "all"                          # All types


# ============================================================================
# Get Voice Information
# ============================================================================

def get_voices(
    voice_type: VoiceType = VoiceType.ALL,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Get available voice list
    
    Args:
        voice_type: Voice type filter
            - VoiceType.SYSTEM: System preset voices only
            - VoiceType.VOICE_CLONING: Cloned voices only
            - VoiceType.VOICE_GENERATION: Designed voices only
            - VoiceType.ALL: All types
        timeout: Request timeout in seconds
    
    Returns:
        API response containing:
        - system_voice: System voice list (if requested)
        - voice_cloning: Cloned voice list (if requested)
        - voice_generation: Designed voice list (if requested)
    
    Example:
        >>> # Get all voices
        >>> result = get_voices(VoiceType.ALL)
        >>> 
        >>> # View system voices
        >>> for voice in result.get("system_voice", []):
        ...     print(f"ID: {voice['voice_id']}, Name: {voice['name']}")
        >>> 
        >>> # Get only cloned voices
        >>> my_clones = get_voices(VoiceType.VOICE_CLONING)
    """
    payload = {
        "voice_type": voice_type.value,
    }
    
    response = make_request(
        method="POST",
        endpoint="get_voice",
        data=payload,
        timeout=timeout,
    )
    
    return parse_response(response)


def get_system_voices() -> List[Dict[str, Any]]:
    """
    Get system preset voice list
    
    Returns:
        System voice list, each voice contains:
        - voice_id: Voice ID
        - name: Voice name
        - description: Voice description
    
    Example:
        >>> voices = get_system_voices()
        >>> for v in voices:
        ...     print(f"{v['voice_id']}: {v.get('name', 'N/A')}")
    """
    result = get_voices(VoiceType.SYSTEM)
    return result.get("system_voice", [])


def get_cloned_voices() -> List[Dict[str, Any]]:
    """
    Get user's cloned voice list
    
    Returns:
        Cloned voice list, each voice contains:
        - voice_id: Voice ID
        - created_time: Creation time
        - status: Status
    
    Example:
        >>> voices = get_cloned_voices()
        >>> for v in voices:
        ...     print(f"{v['voice_id']} (created at {v.get('created_time', 'N/A')})")
    """
    result = get_voices(VoiceType.VOICE_CLONING)
    return result.get("voice_cloning", [])


def get_designed_voices() -> List[Dict[str, Any]]:
    """
    Get user's designed voice list
    
    Returns:
        Designed voice list, each voice contains:
        - voice_id: Voice ID
        - created_time: Creation time
        - status: Status
    
    Example:
        >>> voices = get_designed_voices()
        >>> for v in voices:
        ...     print(f"{v['voice_id']} (created at {v.get('created_time', 'N/A')})")
    """
    result = get_voices(VoiceType.VOICE_GENERATION)
    return result.get("voice_generation", [])


def get_all_custom_voices() -> Dict[str, List[Dict[str, Any]]]:
    """
    Get all custom voices (cloned + designed)
    
    Returns:
        Dictionary containing cloned and designed lists
    
    Example:
        >>> custom = get_all_custom_voices()
        >>> print(f"Cloned voices count: {len(custom['cloned'])}")
        >>> print(f"Designed voices count: {len(custom['designed'])}")
    """
    result = get_voices(VoiceType.ALL)
    return {
        "cloned": result.get("voice_cloning", []),
        "designed": result.get("voice_generation", []),
    }


# ============================================================================
# Delete Voice
# ============================================================================

def delete_voice(
    voice_id: str,
    voice_type: VoiceType,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Delete custom voice
    
    Note: Can only delete user's own cloned or designed voices, cannot delete system voices
    
    Args:
        voice_id: Voice ID to delete
        voice_type: Voice type
            - VoiceType.VOICE_CLONING: Delete cloned voice
            - VoiceType.VOICE_GENERATION: Delete designed voice
        timeout: Request timeout in seconds
    
    Returns:
        API response containing:
        - voice_id: Deleted voice ID
        - created_time: Voice creation time
        - base_resp: Status information
    
    Raises:
        ValueError: Attempting to delete system voice
    
    Example:
        >>> # Delete cloned voice
        >>> result = delete_voice("my-cloned-voice", VoiceType.VOICE_CLONING)
        >>> print(f"Deleted voice: {result['voice_id']}")
        >>> 
        >>> # Delete designed voice
        >>> result = delete_voice("my-designed-voice", VoiceType.VOICE_GENERATION)
    """
    if voice_type == VoiceType.SYSTEM:
        raise ValueError("Cannot delete system voices")
    
    if voice_type == VoiceType.ALL:
        raise ValueError("Must specify concrete voice type for deletion: VOICE_CLONING or VOICE_GENERATION")
    
    payload = {
        "voice_id": voice_id,
        "voice_type": voice_type.value,
    }
    
    response = make_request(
        method="POST",
        endpoint="delete_voice",
        data=payload,
        timeout=timeout,
    )
    
    return parse_response(response)


def delete_cloned_voice(voice_id: str) -> Dict[str, Any]:
    """
    Delete cloned voice convenience function
    
    Args:
        voice_id: Cloned voice ID
    
    Returns:
        Delete result
    
    Example:
        >>> delete_cloned_voice("my-cloned-voice-001")
    """
    return delete_voice(voice_id, VoiceType.VOICE_CLONING)


def delete_designed_voice(voice_id: str) -> Dict[str, Any]:
    """
    Delete designed voice convenience function
    
    Args:
        voice_id: Designed voice ID
    
    Returns:
        Delete result
    
    Example:
        >>> delete_designed_voice("my-designed-voice-001")
    """
    return delete_voice(voice_id, VoiceType.VOICE_GENERATION)


# ============================================================================
# Utility Functions
# ============================================================================

def list_all_voices(show_details: bool = True) -> None:
    """
    Print all available voice information
    
    Args:
        show_details: Whether to show detailed information
    
    Example:
        >>> list_all_voices()
    """
    result = get_voices(VoiceType.ALL)
    
    # System voices
    system_voices = result.get("system_voice", [])
    print(f"\nSystem Preset Voices ({len(system_voices)} total):")
    print("-" * 50)
    for voice in system_voices:
        voice_id = voice.get("voice_id", "N/A")
        name = voice.get("name", "")
        desc = voice.get("description", "")
        if show_details:
            print(f"  {voice_id}")
            if name:
                print(f"    Name: {name}")
            if desc:
                print(f"    Description: {desc[:50]}...")
        else:
            print(f"  {voice_id} - {name}")
    
    # Cloned voices
    cloned_voices = result.get("voice_cloning", [])
    print(f"\nCloned Voices ({len(cloned_voices)} total):")
    print("-" * 50)
    if cloned_voices:
        for voice in cloned_voices:
            voice_id = voice.get("voice_id", "N/A")
            created = voice.get("created_time", "N/A")
            print(f"  {voice_id} (created at {created})")
    else:
        print("  (none)")
    
    # Designed voices
    designed_voices = result.get("voice_generation", [])
    print(f"\nDesigned Voices ({len(designed_voices)} total):")
    print("-" * 50)
    if designed_voices:
        for voice in designed_voices:
            voice_id = voice.get("voice_id", "N/A")
            created = voice.get("created_time", "N/A")
            print(f"  {voice_id} (created at {created})")
    else:
        print("  (none)")


def voice_exists(voice_id: str) -> bool:
    """
    Check if voice exists
    
    Args:
        voice_id: Voice ID to check
    
    Returns:
        Whether exists
    
    Example:
        >>> if voice_exists("my-voice"):
        ...     print("Voice exists")
    """
    result = get_voices(VoiceType.ALL)
    
    # Check system voices
    for voice in result.get("system_voice", []):
        if voice.get("voice_id") == voice_id:
            return True
    
    # Check cloned voices
    for voice in result.get("voice_cloning", []):
        if voice.get("voice_id") == voice_id:
            return True
    
    # Check designed voices
    for voice in result.get("voice_generation", []):
        if voice.get("voice_id") == voice_id:
            return True
    
    return False


def get_voice_info(voice_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information for specified voice
    
    Args:
        voice_id: Voice ID
    
    Returns:
        Voice info dictionary, None if not found
    
    Example:
        >>> info = get_voice_info("male-qn-qingse")
        >>> if info:
        ...     print(f"Type: {info['type']}")
        ...     print(f"Name: {info.get('name', 'N/A')}")
    """
    result = get_voices(VoiceType.ALL)
    
    # Search system voices
    for voice in result.get("system_voice", []):
        if voice.get("voice_id") == voice_id:
            return {**voice, "type": "system"}
    
    # Search cloned voices
    for voice in result.get("voice_cloning", []):
        if voice.get("voice_id") == voice_id:
            return {**voice, "type": "cloned"}
    
    # Search designed voices
    for voice in result.get("voice_generation", []):
        if voice.get("voice_id") == voice_id:
            return {**voice, "type": "designed"}
    
    return None


def cleanup_unused_voices(dry_run: bool = True) -> List[str]:
    """
    Clean up unused custom voices
    
    Warning: This will delete all cloned and designed voices, use with caution
    
    Args:
        dry_run: If True, only shows voices to be deleted without actually deleting
    
    Returns:
        List of deleted (or to be deleted) voice IDs
    
    Example:
        >>> # Preview first
        >>> to_delete = cleanup_unused_voices(dry_run=True)
        >>> print(f"Will delete {len(to_delete)} voices")
        >>> 
        >>> # Confirm and actually delete
        >>> cleanup_unused_voices(dry_run=False)
    """
    deleted_ids = []
    
    # Get all custom voices
    result = get_voices(VoiceType.ALL)
    
    cloned = result.get("voice_cloning", [])
    designed = result.get("voice_generation", [])
    
    if dry_run:
        print("=== Preview Mode (no actual deletion) ===")
    else:
        print("=== Deleting Voices ===")
    
    # Delete cloned voices
    for voice in cloned:
        voice_id = voice.get("voice_id")
        if voice_id:
            if dry_run:
                print(f"  [Preview] Will delete cloned voice: {voice_id}")
            else:
                try:
                    delete_cloned_voice(voice_id)
                    print(f"  [Deleted] Cloned voice: {voice_id}")
                except Exception as e:
                    print(f"  [Failed] Cloned voice {voice_id}: {e}")
                    continue
            deleted_ids.append(voice_id)
    
    # Delete designed voices
    for voice in designed:
        voice_id = voice.get("voice_id")
        if voice_id:
            if dry_run:
                print(f"  [Preview] Will delete designed voice: {voice_id}")
            else:
                try:
                    delete_designed_voice(voice_id)
                    print(f"  [Deleted] Designed voice: {voice_id}")
                except Exception as e:
                    print(f"  [Failed] Designed voice {voice_id}: {e}")
                    continue
            deleted_ids.append(voice_id)
    
    print(f"\nTotal {len(deleted_ids)} voices " + ("will be deleted" if dry_run else "deleted"))
    return deleted_ids
