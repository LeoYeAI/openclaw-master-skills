"""
MiniMax Voice API - Synchronous Text-to-Speech Module
Supports both HTTP and WebSocket methods

Documentation:
- HTTP: https://platform.minimaxi.com/docs/api-reference/speech-t2a-http
- WebSocket: https://platform.minimaxi.com/docs/api-reference/speech-t2a-websocket
"""

import json
import asyncio
import websockets
from typing import Optional, Dict, Any, List, Callable, Generator
from dataclasses import dataclass, field

from utils import (
    MINIMAX_VOICE_API_KEY,
    MINIMAX_API_BASE,
    VoiceSetting,
    AudioSetting,
    get_headers,
    make_request,
    parse_response,
    save_audio_from_hex,
)


# ============================================================================
# HTTP Synchronous Text-to-Speech
# ============================================================================

def synthesize_speech_http(
    text: str,
    model: str = "speech-2.6-hd",
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    stream: bool = False,
    pronunciation_dict: Optional[Dict[str, List[str]]] = None,
    timber_weights: Optional[List[Dict[str, Any]]] = None,
    language_boost: Optional[str] = None,
    voice_modify: Optional[Dict[str, Any]] = None,
    subtitle_enable: bool = False,
    output_format: str = "hex",
    aigc_watermark: bool = False,
    timeout: int = 120,
) -> Dict[str, Any]:
    """
    HTTP Synchronous Text-to-Speech
    
    Args:
        text: Text to synthesize, max 10000 characters. Supports pause marker <#x#>
        model: Model version (speech-2.6-hd, speech-2.6-turbo, speech-02-hd, speech-02-turbo, speech-01-hd, speech-01-turbo)
        voice_setting: Voice settings (voice_id, speed, vol, pitch, emotion)
        audio_setting: Audio settings (sample_rate, bitrate, format, channel)
        stream: Whether to enable streaming output, default False
        pronunciation_dict: Pronunciation dictionary for custom pronunciation. Format: {"tone": ["word/(pronunciation)"]}
        timber_weights: Mixed voice weight settings
        language_boost: Language boost, can be set to specific language or "auto"
        voice_modify: Voice effect settings
        subtitle_enable: Whether to enable subtitles, only valid for non-streaming
        output_format: Output format "hex" or "url", streaming only supports hex
        aigc_watermark: Whether to add audio rhythm identifier
        timeout: Request timeout in seconds
    
    Returns:
        API response containing:
        - data.audio: Audio data (hex-encoded) or URL
        - data.status: Status code
        - extra_info: Audio metadata (duration, sample rate, size, etc.)
        - trace_id: Session ID
    
    Example:
        >>> voice = VoiceSetting(voice_id="male-qn-qingse", speed=1.0, emotion="happy")
        >>> audio = AudioSetting(format="mp3", sample_rate=32000)
        >>> result = synthesize_speech_http(
        ...     text="Hello, nice to meet you!",
        ...     model="speech-2.6-hd",
        ...     voice_setting=voice,
        ...     audio_setting=audio
        ... )
        >>> save_audio_from_hex(result["data"]["audio"], "output.mp3")
    """
    if not voice_setting:
        voice_setting = VoiceSetting(voice_id="male-qn-qingse")
    
    if not audio_setting:
        audio_setting = AudioSetting()
    
    payload = {
        "model": model,
        "text": text,
        "stream": stream,
        "voice_setting": voice_setting.to_dict(),
        "audio_setting": audio_setting.to_dict(),
        "subtitle_enable": subtitle_enable,
        "output_format": output_format,
        "aigc_watermark": aigc_watermark,
    }
    
    if pronunciation_dict:
        payload["pronunciation_dict"] = pronunciation_dict
    
    if timber_weights:
        payload["timber_weights"] = timber_weights
    
    if language_boost:
        payload["language_boost"] = language_boost
    
    if voice_modify:
        payload["voice_modify"] = voice_modify
    
    response = make_request(
        method="POST",
        endpoint="t2a_v2",
        data=payload,
        timeout=timeout,
    )
    
    return parse_response(response)


def synthesize_speech_http_stream(
    text: str,
    model: str = "speech-2.6-hd",
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    **kwargs
) -> Generator[bytes, None, None]:
    """
    HTTP Streaming Text-to-Speech
    
    Args:
        text: Text to synthesize
        model: Model version
        voice_setting: Voice settings
        audio_setting: Audio settings
        **kwargs: Other parameters same as synthesize_speech_http
    
    Yields:
        Audio data chunks (bytes)
    
    Example:
        >>> voice = VoiceSetting(voice_id="female-shaonv")
        >>> chunks = []
        >>> for chunk in synthesize_speech_http_stream("This is a long text...", voice_setting=voice):
        ...     chunks.append(chunk)
        >>> audio_data = b"".join(chunks)
    """
    import requests
    
    if not voice_setting:
        voice_setting = VoiceSetting(voice_id="male-qn-qingse")
    
    if not audio_setting:
        audio_setting = AudioSetting()
    
    payload = {
        "model": model,
        "text": text,
        "stream": True,
        "voice_setting": voice_setting.to_dict(),
        "audio_setting": audio_setting.to_dict(),
    }
    
    # Merge other parameters
    for key in ["pronunciation_dict", "timber_weights", "language_boost", "voice_modify"]:
        if key in kwargs and kwargs[key]:
            payload[key] = kwargs[key]
    
    headers = get_headers()
    url = f"{MINIMAX_API_BASE}/t2a_v2"
    
    with requests.post(url, headers=headers, json=payload, stream=True, timeout=300) as response:
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")
                if line_str.startswith("data:"):
                    data = json.loads(line_str[5:].strip())
                    if "data" in data and "audio" in data["data"]:
                        audio_hex = data["data"]["audio"]
                        if audio_hex:
                            yield bytes.fromhex(audio_hex)


# ============================================================================
# WebSocket Synchronous Text-to-Speech
# ============================================================================

@dataclass
class WebSocketTTSConfig:
    """WebSocket TTS Configuration"""
    model: str = "speech-2.6-hd"
    voice_setting: VoiceSetting = field(default_factory=lambda: VoiceSetting(voice_id="male-qn-qingse"))
    audio_setting: AudioSetting = field(default_factory=AudioSetting)
    pronunciation_dict: Optional[Dict[str, List[str]]] = None
    language_boost: Optional[str] = None


class WebSocketTTSClient:
    """
    WebSocket TTS Client
    Supports streaming text segments and real-time audio reception
    
    Documentation: https://platform.minimaxi.com/docs/api-reference/speech-t2a-websocket
    
    Workflow:
    1. Connect to WebSocket
    2. Send task_start event
    3. After receiving task_started, send task_continue events (can be multiple)
    4. Send task_finish event to end the task
    5. Receive audio data until task_finished
    
    Example:
        >>> async def main():
        ...     config = WebSocketTTSConfig(
        ...         model="speech-2.6-hd",
        ...         voice_setting=VoiceSetting(voice_id="male-qn-qingse")
        ...     )
        ...     client = WebSocketTTSClient(config)
        ...     
        ...     audio_chunks = []
        ...     async for chunk in client.synthesize_stream(["Hello", "World"]):
        ...         audio_chunks.append(chunk)
        ...     
        ...     # Save audio
        ...     with open("output.mp3", "wb") as f:
        ...         f.write(b"".join(audio_chunks))
        >>> 
        >>> asyncio.run(main())
    """
    
    WS_URL = "wss://api.minimaxi.com/ws/v1/t2a_v2"
    
    def __init__(self, config: Optional[WebSocketTTSConfig] = None):
        self.config = config or WebSocketTTSConfig()
        self._ws = None
    
    async def connect(self) -> None:
        """Establish WebSocket connection"""
        headers = {"Authorization": f"Bearer {MINIMAX_VOICE_API_KEY}"}
        self._ws = await websockets.connect(
            self.WS_URL,
            extra_headers=headers,
        )
        
        # Wait for connection success event
        response = await self._ws.recv()
        data = json.loads(response)
        if data.get("event") != "connected_success":
            raise ConnectionError(f"WebSocket connection failed: {data}")
    
    async def close(self) -> None:
        """Close WebSocket connection"""
        if self._ws:
            await self._ws.close()
            self._ws = None
    
    async def _send_task_start(self) -> None:
        """Send task start event"""
        message = {
            "event": "task_start",
            "model": self.config.model,
            "voice_setting": self.config.voice_setting.to_dict(),
            "audio_setting": self.config.audio_setting.to_dict(),
        }
        
        if self.config.pronunciation_dict:
            message["pronunciation_dict"] = self.config.pronunciation_dict
        
        if self.config.language_boost:
            message["language_boost"] = self.config.language_boost
        
        await self._ws.send(json.dumps(message))
        
        # Wait for task_started event
        response = await self._ws.recv()
        data = json.loads(response)
        if data.get("event") != "task_started":
            raise RuntimeError(f"Task start failed: {data}")
    
    async def _send_task_continue(self, text: str) -> None:
        """Send text continue event"""
        message = {
            "event": "task_continue",
            "text": text,
        }
        await self._ws.send(json.dumps(message))
    
    async def _send_task_finish(self) -> None:
        """Send task finish event"""
        message = {"event": "task_finish"}
        await self._ws.send(json.dumps(message))
    
    async def synthesize_stream(
        self,
        text_segments: List[str],
        on_audio_chunk: Optional[Callable[[bytes], None]] = None,
    ) -> List[bytes]:
        """
        Streaming text-to-speech synthesis
        
        Args:
            text_segments: List of text segments
            on_audio_chunk: Optional callback function, called when audio chunk is received
        
        Returns:
            List of audio data chunks
        """
        try:
            await self.connect()
            await self._send_task_start()
            
            # Send all text segments
            for segment in text_segments:
                await self._send_task_continue(segment)
            
            # Send finish signal
            await self._send_task_finish()
            
            # Collect audio data
            audio_chunks = []
            while True:
                response = await self._ws.recv()
                data = json.loads(response)
                event = data.get("event")
                
                if event == "task_continued":
                    # Received audio data
                    audio_hex = data.get("data", {}).get("audio")
                    if audio_hex:
                        chunk = bytes.fromhex(audio_hex)
                        audio_chunks.append(chunk)
                        if on_audio_chunk:
                            on_audio_chunk(chunk)
                
                elif event == "task_finished":
                    break
                
                elif event == "task_failed":
                    error = data.get("data", {}).get("error_message", "Unknown error")
                    raise RuntimeError(f"Task failed: {error}")
            
            return audio_chunks
        
        finally:
            await self.close()
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


async def synthesize_speech_websocket(
    text_segments: List[str],
    model: str = "speech-2.6-hd",
    voice_setting: Optional[VoiceSetting] = None,
    audio_setting: Optional[AudioSetting] = None,
    **kwargs
) -> bytes:
    """
    WebSocket text-to-speech convenience function
    
    Args:
        text_segments: List of text segments
        model: Model version
        voice_setting: Voice settings
        audio_setting: Audio settings
        **kwargs: Other configuration parameters
    
    Returns:
        Complete audio data (bytes)
    
    Example:
        >>> import asyncio
        >>> audio = asyncio.run(synthesize_speech_websocket(
        ...     ["First segment", "Second segment"],
        ...     voice_setting=VoiceSetting(voice_id="female-shaonv")
        ... ))
        >>> with open("output.mp3", "wb") as f:
        ...     f.write(audio)
    """
    config = WebSocketTTSConfig(
        model=model,
        voice_setting=voice_setting or VoiceSetting(voice_id="male-qn-qingse"),
        audio_setting=audio_setting or AudioSetting(),
        pronunciation_dict=kwargs.get("pronunciation_dict"),
        language_boost=kwargs.get("language_boost"),
    )
    
    client = WebSocketTTSClient(config)
    chunks = await client.synthesize_stream(text_segments)
    return b"".join(chunks)


# ============================================================================
# Convenience Functions
# ============================================================================

def quick_tts(
    text: str,
    voice_id: str = "male-qn-qingse",
    output_path: Optional[str] = None,
    **kwargs
) -> bytes:
    """
    Quick text-to-speech convenience function
    
    Args:
        text: Text to synthesize
        voice_id: Voice ID
        output_path: Optional output file path. If provided, audio will be saved to this path.
        **kwargs: Other parameters passed to synthesize_speech_http
    
    Returns:
        bytes: Audio data as bytes. Also saves to output_path if specified.
    
    Example:
        >>> # Get audio bytes
        >>> audio = quick_tts("Hello world", voice_id="female-shaonv")
        >>> 
        >>> # Get audio bytes AND save to file
        >>> audio = quick_tts("Hello world", output_path="hello.mp3")
    """
    voice_setting = VoiceSetting(voice_id=voice_id)
    result = synthesize_speech_http(
        text=text,
        voice_setting=voice_setting,
        **kwargs
    )
    
    audio_hex = result.get("data", {}).get("audio", "")
    audio_bytes = bytes.fromhex(audio_hex)
    
    if output_path:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
    
    return audio_bytes
