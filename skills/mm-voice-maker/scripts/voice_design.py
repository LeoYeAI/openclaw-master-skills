"""
MiniMax Voice API - Voice Design Module
Create custom voices through text descriptions

Documentation:
- https://platform.minimaxi.com/docs/api-reference/voice-design-design
"""

from typing import Optional, Dict, Any

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
    model: str = "speech-02-hd",
    aigc_watermark: bool = False,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Design new voice through text description
    
    Use natural language to describe desired voice characteristics. AI will generate 
    a matching voice based on the description. The generated voice can be used for 
    subsequent text-to-speech synthesis.
    
    Args:
        prompt: Voice description text, describe voice characteristics in detail
            Example: "A gentle young female voice with soft, sweet tones, suitable for bedtime stories"
            Recommended to include: gender, age group, voice characteristics, emotional tone, use case, etc.
        preview_text: Text for generating trial audio
        voice_id: Optional custom voice ID, auto-generated if not provided
            Rules: 8-256 chars, starts with letter, can contain letters/numbers/-/_
        model: Model version, recommended speech-02-hd
        aigc_watermark: Whether to add rhythm identifier to trial audio
        timeout: Request timeout in seconds
    
    Returns:
        API response containing:
        - voice_id: Generated voice ID
        - trial_audio: Trial audio (hex-encoded)
        - extra_info: Additional information
        - trace_id: Session ID
    
    Note:
    - Designed voices are temporary and must be used with TTS API within 7 days to be permanently saved
    - Trial audio incurs charges
    
    Example:
        >>> result = design_voice(
        ...     prompt="A deep, resonant middle-aged male voice, suitable for news broadcasting",
        ...     preview_text="Welcome to today's news program",
        ... )
        >>> 
        >>> voice_id = result["voice_id"]
        >>> print(f"Generated voice ID: {voice_id}")
        >>> 
        >>> # Save trial audio
        >>> save_audio_from_hex(result["trial_audio"], "trial.mp3")
    """
    # Validate custom voice_id
    if voice_id and not validate_voice_id(voice_id):
        raise ValueError(
            "Invalid voice_id format. Requirements: 8-256 characters, "
            "starts with letter, can contain letters, numbers, -, _, "
            "cannot end with - or _"
        )
    
    payload = {
        "prompt": prompt,
        "preview_text": preview_text,
        "model": model,
        "aigc_watermark": aigc_watermark,
    }
    
    if voice_id:
        payload["voice_id"] = voice_id
    
    response = make_request(
        method="POST",
        endpoint="voice_design",
        data=payload,
        timeout=timeout,
    )
    
    return parse_response(response)


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_design_voice(
    prompt: str,
    preview_text: str,
    output_path: Optional[str] = None,
    voice_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Quick voice design convenience function
    
    Args:
        prompt: Voice description
        preview_text: Trial text
        output_path: Optional trial audio save path
        voice_id: Optional custom voice ID
    
    Returns:
        Design result containing voice_id and other info
    
    Example:
        >>> result = quick_design_voice(
        ...     prompt="Energetic young female voice, full of vitality",
        ...     preview_text="Hello everyone, nice to meet you!",
        ...     output_path="trial.mp3",
        ... )
        >>> print(f"Voice ID: {result['voice_id']}")
    """
    result = design_voice(
        prompt=prompt,
        preview_text=preview_text,
        voice_id=voice_id,
    )
    
    # Save trial audio
    if output_path and result.get("trial_audio"):
        save_audio_from_hex(result["trial_audio"], output_path)
        result["output_path"] = output_path
        print(f"Trial audio saved to: {output_path}")
    
    print(f"Voice design successful! Voice ID: {result.get('voice_id')}")
    return result


# ============================================================================
# Common Voice Description Templates
# ============================================================================

VOICE_PROMPT_TEMPLATES = {
    # Male voice templates
    "male_news_anchor": "A deep, authoritative middle-aged male voice with clear articulation, moderate pace, professional and trustworthy, suitable for news broadcasting and documentary narration",
    "male_audiobook": "A warm, refined middle-aged male voice, deep and emotionally compelling, unhurried narration style, suitable for audiobook reading",
    "male_youth": "A bright, cheerful young male voice, full of energy and enthusiasm, natural and lively tone, suitable for variety show dubbing and youth content",
    "male_business": "A mature, composed business male voice, professional and reliable, confident and poised tone, suitable for corporate promotion and business scenarios",
    
    # Female voice templates
    "female_gentle": "A gentle, sweet young female voice, soft and friendly tone, natural like a girl next door, suitable for assistants and customer service",
    "female_narrator": "An elegant, sophisticated mature female voice, clear and pleasant, fluent and natural expression, suitable for audiobooks and course explanations",
    "female_lively": "A vivacious, playful young female voice, full of youthful energy, lively and interesting tone, suitable for animation dubbing and children's content",
    "female_professional": "A capable, professional working woman's voice, confident and poised, standard pronunciation, suitable for news broadcasting and business scenarios",
    
    # Special styles
    "storyteller": "A kind, warm storytelling voice, slow and gentle pace, like an elder sharing stories, suitable for bedtime stories and children's content",
    "emotional": "An emotionally expressive performance voice, capable of expressing joy, anger, sadness and other emotions, dramatic tension, suitable for audiobooks and radio dramas",
    "asmr_style": "A soft, soothing ASMR-style voice, lower volume with noticeable breathing, creates relaxing and pleasant feelings",
}


def design_voice_from_template(
    template_key: str,
    preview_text: str,
    voice_id: Optional[str] = None,
    output_path: Optional[str] = None,
    custom_modifier: str = "",
) -> Dict[str, Any]:
    """
    Design voice using preset templates
    
    Args:
        template_key: Template key, see VOICE_PROMPT_TEMPLATES for options
        preview_text: Trial text
        voice_id: Optional custom voice ID
        output_path: Optional trial audio save path
        custom_modifier: Optional additional description, appended to template
    
    Returns:
        Design result
    
    Available templates:
        - male_news_anchor: News anchor male voice
        - male_audiobook: Audiobook male voice
        - male_youth: Youth male voice
        - male_business: Business male voice
        - female_gentle: Gentle female voice
        - female_narrator: Narrator female voice
        - female_lively: Lively female voice
        - female_professional: Professional female voice
        - storyteller: Storytelling voice
        - emotional: Emotional performance voice
        - asmr_style: ASMR style voice
    
    Example:
        >>> result = design_voice_from_template(
        ...     template_key="female_gentle",
        ...     preview_text="Hello, how can I help you?",
        ...     custom_modifier="with a slight southern accent",
        ...     output_path="gentle_voice.mp3",
        ... )
    """
    if template_key not in VOICE_PROMPT_TEMPLATES:
        available = ", ".join(VOICE_PROMPT_TEMPLATES.keys())
        raise ValueError(f"Unknown template: {template_key}. Available templates: {available}")
    
    prompt = VOICE_PROMPT_TEMPLATES[template_key]
    if custom_modifier:
        prompt = f"{prompt}. {custom_modifier}"
    
    return quick_design_voice(
        prompt=prompt,
        preview_text=preview_text,
        voice_id=voice_id,
        output_path=output_path,
    )


def list_voice_templates() -> Dict[str, str]:
    """
    List all available voice description templates
    
    Returns:
        Template dictionary {template_name: description}
    """
    return VOICE_PROMPT_TEMPLATES.copy()
