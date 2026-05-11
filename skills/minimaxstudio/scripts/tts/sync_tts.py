"""
MiniMax Voice API - Synchronous TTS Module
Provides synchronous text-to-speech synthesis via HTTP and WebSocket APIs.

HTTP API docs:  https://platform.minimaxi.com/document/T2A%20V2
WebSocket docs: https://platform.minimaxi.com/document/T2A%20V2%20WebSocket
"""

import json
import asyncio
import websockets
from typing import Optional, Dict, Any, List, Callable, Generator
from dataclasses import dataclass, field

try:
    from .utils import (
        MINIMAX_API_KEY,
        MINIMAX_API_BASE,
        VoiceSetting,
        AudioSetting,
        get_headers,
        make_request,
        parse_response,
        save_audio_from_hex,
    )
except ImportError:
    from utils import (
        MINIMAX_API_KEY,
        MINIMAX_API_BASE,
        VoiceSetting,
        AudioSetting,
        get_headers,
        make_request,
        parse_response,
        save_audio_from_hex,
    )


def synthesize_speech_http(
    text: str,
    model: str = "speech-2.6-hd",
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    stream: bool = False,
    pronunciation_dict: Optional[Dict[str, Any]] = None,
    timber_weights: Optional[List[Dict[str, Any]]] = None,
    language_boost: Optional[str] = None,
    voice_modify: Optional[Dict[str, Any]] = None,
    subtitle_enable: bool = False,
    output_format: str = "hex",
    aigc_watermark: bool = False,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    Synthesize speech using the HTTP T2A V2 API.

    Args:
        text: Text to synthesize (max 10,000 characters).
        model: TTS model name.
        voice_setting: Voice configuration (voice_id, speed, volume, pitch, emotion).
        audio_setting: Audio output configuration (sample_rate, bitrate, format, channel).
        stream: Whether to use streaming mode.
        pronunciation_dict: Custom pronunciation dictionary.
        timber_weights: Timber weight configuration for voice mixing.
        language_boost: Language to boost for multilingual synthesis.
        voice_modify: Voice modification parameters.
        subtitle_enable: Whether to return subtitle/timing data.
        output_format: Output format — "hex" for hex-encoded audio, "url" for download URL.
        aigc_watermark: Whether to embed AIGC watermark.
        timeout: Request timeout in seconds.

    Returns:
        Parsed API response dict containing audio data.

    Raises:
        ValueError: If API returns an error status.
        requests.exceptions.RequestException: If the HTTP request fails.
    """
    if voice_setting is None:
        voice_setting = VoiceSetting(voice_id="male-qn-qingse")

    if audio_setting is None:
        audio_setting = AudioSetting()

    payload: Dict[str, Any] = {
        "model": model,
        "text": text,
        "voice_setting": voice_setting.to_dict(),
        "audio_setting": audio_setting.to_dict(),
        "stream": stream,
        "subtitle_enable": subtitle_enable,
        "output_format": output_format,
        "aigc_watermark": aigc_watermark,
    }

    if pronunciation_dict is not None:
        payload["pronunciation_dict"] = pronunciation_dict

    if timber_weights is not None:
        payload["timber_weights"] = timber_weights

    if language_boost is not None:
        payload["language_boost"] = language_boost

    if voice_modify is not None:
        payload["voice_modify"] = voice_modify

    response = make_request(
        method="POST",
        endpoint="t2a_v2",
        data=payload,
        timeout=timeout,
    )

    return parse_response(response)


def quick_tts(
    text: str,
    voice_id: str = "male-qn-qingse",
    model: str = "speech-2.6-hd",
    output_path: Optional[str] = None,
    emotion: Optional[str] = None,
    speed: float = 1.0,
    volume: float = 1.0,
    pitch: int = 0,
    audio_format: str = "mp3",
    sample_rate: int = 32000,
) -> str:
    """
    Convenience function for quick text-to-speech synthesis.

    Builds VoiceSetting and AudioSetting from simple parameters, calls the HTTP
    API, and optionally saves the result to a file.

    Args:
        text: Text to synthesize.
        voice_id: Voice identifier (system or custom).
        model: TTS model name.
        output_path: If provided, save the audio to this file path.
        emotion: Emotion tag (happy, sad, angry, etc.). None for automatic.
        speed: Speech speed 0.5–2.0.
        volume: Volume 0.1–10.0.
        pitch: Pitch adjustment -12 to 12.
        audio_format: Audio format (mp3, wav, flac, pcm).
        sample_rate: Audio sample rate (16000, 24000, 32000).

    Returns:
        Hex-encoded audio data string.

    Raises:
        ValueError: If the API returns an error or no audio data is found.
    """
    voice_setting = VoiceSetting(
        voice_id=voice_id,
        speed=speed,
        volume=volume,
        pitch=pitch,
        emotion=emotion,
    )

    audio_setting = AudioSetting(
        sample_rate=sample_rate,
        format=audio_format,
    )

    result = synthesize_speech_http(
        text=text,
        model=model,
        voice_setting=voice_setting,
        audio_setting=audio_setting,
    )

    # Extract hex audio data from response
    audio_data = result.get("data", {}).get("audio", "")
    if not audio_data:
        extra_info = result.get("extra_info", {})
        audio_data = extra_info.get("audio", "")

    if not audio_data:
        raise ValueError("No audio data returned from API")

    if output_path:
        save_audio_from_hex(audio_data, output_path)

    return audio_data
