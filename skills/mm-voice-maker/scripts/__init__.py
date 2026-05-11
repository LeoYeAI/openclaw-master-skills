"""
MiniMax Voice API SDK
=====================

A complete Python SDK for MiniMax Voice API, supporting text-to-speech synthesis,
voice cloning, voice design, and voice management.

Modules:
--------
- sync_tts: Synchronous TTS (HTTP/WebSocket)
- async_tts: Asynchronous TTS (long text)
- voice_clone: Voice cloning
- voice_design: Voice design
- voice_management: Voice management

Prerequisites:
--------------
Set environment variable MINIMAX_VOICE_API_KEY

Quick Start:
------------
>>> from scripts import quick_tts
>>> audio = quick_tts("Hello world", output_path="hello.mp3")

>>> from scripts import VoiceSetting, synthesize_speech_http
>>> voice = VoiceSetting(voice_id="male-qn-qingse", speed=1.0)
>>> result = synthesize_speech_http(text="Test text", voice_setting=voice)
"""

# Common utilities and configuration
from .utils import (
    MINIMAX_VOICE_API_KEY,
    MINIMAX_API_BASE,
    AVAILABLE_MODELS,
    AUDIO_FORMATS,
    SUPPORTED_LANGUAGES,
    SYSTEM_VOICES,
    VoiceSetting,
    AudioSetting,
    get_headers,
    make_request,
    parse_response,
    save_audio_from_hex,
    download_audio_from_url,
    validate_voice_id,
    format_pause_marker,
)

# Audio Processing (FFmpeg-based)
from .audio_processing import (
    SUPPORTED_FORMATS,
    AudioInfo,
    check_ffmpeg_installed,
    get_ffmpeg_path,
    probe_audio_file,
    convert_audio,
    convert_audio_simple,
    merge_audio_files,
    concatenate_audio_files,
    normalize_audio,
    adjust_volume,
    trim_audio,
    remove_silence,
    apply_effects,
    optimize_for_speech,
    create_audio_from_segments,
)

# Synchronous TTS
from .sync_tts import (
    synthesize_speech_http,
    synthesize_speech_http_stream,
    WebSocketTTSConfig,
    WebSocketTTSClient,
    synthesize_speech_websocket,
    quick_tts,
)

# Asynchronous TTS
from .async_tts import (
    AsyncTaskStatus,
    create_async_tts_task,
    upload_text_file,
    query_async_tts_task,
    get_task_status,
    wait_for_task,
    async_tts_full_flow,
    async_tts_from_file,
)

# Voice Cloning
from .voice_clone import (
    ClonePrompt,
    upload_clone_audio,
    upload_prompt_audio,
    clone_voice,
    quick_clone_voice,
    clone_voice_with_prompt,
)

# Voice Design
from .voice_design import (
    design_voice,
    quick_design_voice,
    VOICE_PROMPT_TEMPLATES,
    design_voice_from_template,
    list_voice_templates,
)

# Voice Management
from .voice_management import (
    VoiceType,
    get_voices,
    get_system_voices,
    get_cloned_voices,
    get_designed_voices,
    get_all_custom_voices,
    delete_voice,
    delete_cloned_voice,
    delete_designed_voice,
    list_all_voices,
    voice_exists,
    get_voice_info,
    cleanup_unused_voices,
)

# Segment-based TTS (multi-voice, multi-emotion workflow)
from .segment_tts import (
    VALID_EMOTIONS,
    SegmentInfo,
    ValidationResult,
    validate_segments_file,
    load_segments,
    generate_segment_audio,
    generate_from_segments,
    merge_segment_audio,
    process_segments_to_audio,
    clear_voice_cache,
)

__all__ = [
    # Configuration and utilities
    "MINIMAX_VOICE_API_KEY",
    "MINIMAX_API_BASE",
    "AVAILABLE_MODELS",
    "AUDIO_FORMATS",
    "SUPPORTED_LANGUAGES",
    "SYSTEM_VOICES",
    "VoiceSetting",
    "AudioSetting",
    "get_headers",
    "make_request",
    "parse_response",
    "save_audio_from_hex",
    "download_audio_from_url",
    "validate_voice_id",
    "format_pause_marker",

    # Audio Processing (FFmpeg-based)
    "SUPPORTED_FORMATS",
    "AudioInfo",
    "check_ffmpeg_installed",
    "get_ffmpeg_path",
    "probe_audio_file",
    "convert_audio",
    "convert_audio_simple",
    "merge_audio_files",
    "concatenate_audio_files",
    "normalize_audio",
    "adjust_volume",
    "trim_audio",
    "remove_silence",
    "apply_effects",
    "optimize_for_speech",
    "create_audio_from_segments",

    # Synchronous TTS
    "synthesize_speech_http",
    "synthesize_speech_http_stream",
    "WebSocketTTSConfig",
    "WebSocketTTSClient",
    "synthesize_speech_websocket",
    "quick_tts",

    # Asynchronous TTS
    "AsyncTaskStatus",
    "create_async_tts_task",
    "upload_text_file",
    "query_async_tts_task",
    "get_task_status",
    "wait_for_task",
    "async_tts_full_flow",
    "async_tts_from_file",

    # Voice Cloning
    "ClonePrompt",
    "upload_clone_audio",
    "upload_prompt_audio",
    "clone_voice",
    "quick_clone_voice",
    "clone_voice_with_prompt",

    # Voice Design
    "design_voice",
    "quick_design_voice",
    "VOICE_PROMPT_TEMPLATES",
    "design_voice_from_template",
    "list_voice_templates",

    # Voice Management
    "VoiceType",
    "get_voices",
    "get_system_voices",
    "get_cloned_voices",
    "get_designed_voices",
    "get_all_custom_voices",
    "delete_voice",
    "delete_cloned_voice",
    "delete_designed_voice",
    "list_all_voices",
    "voice_exists",
    "get_voice_info",
    "cleanup_unused_voices",
    
    # Segment-based TTS
    "VALID_EMOTIONS",
    "SegmentInfo",
    "ValidationResult",
    "validate_segments_file",
    "load_segments",
    "generate_segment_audio",
    "generate_from_segments",
    "merge_segment_audio",
    "process_segments_to_audio",
    "clear_voice_cache",
]

__version__ = "1.0.0"
