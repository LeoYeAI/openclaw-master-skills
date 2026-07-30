#!/usr/bin/env python3
"""
Clack — Voice Relay Server for OpenClaw

WebSocket relay: voice input → STT → OpenClaw agent → TTS → audio back.

Supported providers:
  STT: elevenlabs, openai, deepgram
  TTS: elevenlabs, openai, deepgram

Environment variables:
  STT_PROVIDER          - STT provider (default: elevenlabs)
  TTS_PROVIDER          - TTS provider (default: elevenlabs)
  ELEVENLABS_API_KEY    - ElevenLabs API key
  OPENAI_API_KEY        - OpenAI API key
  DEEPGRAM_API_KEY      - Deepgram API key
  OPENCLAW_GATEWAY_URL  - OpenClaw gateway URL (default: http://127.0.0.1:18789)
  OPENCLAW_GATEWAY_TOKEN - OpenClaw gateway bearer token
  RELAY_AUTH_TOKEN       - Client auth token
  VOICE_RELAY_PORT       - Server port (default: 9878)
  TTS_VOICE             - Voice ID/name (provider-specific)
  CLACK_HISTORY_DIR     - History storage dir (default: /var/lib/clack/history)
  CLACK_MAX_HISTORY     - Max messages to keep (default: 50)
"""

import asyncio
import json
import os
import io
import struct
import hmac
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, AsyncIterator
from difflib import SequenceMatcher

import aiohttp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


# ── Utilities ──

def pcm_to_wav(pcm_data: bytes, sample_rate: int = 16000, channels: int = 1, bits_per_sample: int = 16) -> bytes:
    data_size = len(pcm_data)
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    buf = io.BytesIO()
    buf.write(b'RIFF')
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<I', 16))
    buf.write(struct.pack('<H', 1))
    buf.write(struct.pack('<H', channels))
    buf.write(struct.pack('<I', sample_rate))
    buf.write(struct.pack('<I', byte_rate))
    buf.write(struct.pack('<H', block_align))
    buf.write(struct.pack('<H', bits_per_sample))
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    buf.write(pcm_data)
    return buf.getvalue()


def _is_echo(transcript: str, last_response: str) -> bool:
    t = transcript.lower().strip().replace("[speaker speaker_0]: ", "")
    r = last_response.lower().strip()
    if t in r or r in t:
        return True
    ratio = SequenceMatcher(None, t, r).ratio()
    if ratio > 0.6:
        print(f"[Echo] Similarity: {ratio:.2f}")
        return True
    return False


# ── STT Providers ──

class STTProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_pcm: bytes) -> Optional[str]:
        """Transcribe PCM audio, return text or None."""
        pass


class ElevenLabsSTT(STTProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def transcribe(self, audio_pcm: bytes) -> Optional[str]:
        async with aiohttp.ClientSession() as session:
            wav_data = pcm_to_wav(audio_pcm)
            print(f"[STT/11labs] Sending {len(wav_data)} bytes WAV")
            form = aiohttp.FormData()
            form.add_field('file', wav_data, filename='audio.wav', content_type='audio/wav')
            form.add_field('model_id', 'scribe_v1')
            form.add_field('diarize', 'false')
            form.add_field('tag_audio_events', 'false')
            async with session.post(
                "https://api.elevenlabs.io/v1/speech-to-text",
                headers={"xi-api-key": self.api_key},
                data=form
            ) as resp:
                if resp.status != 200:
                    print(f"[STT/11labs] Error: {resp.status} - {await resp.text()}")
                    return None
                result = await resp.json()
                lang_prob = result.get("language_probability", 0)
                text = result.get("text", "").strip()
                print(f"[STT/11labs] Raw: '{text[:200]}' (lang_prob={lang_prob:.2f})")
                if lang_prob < 0.4 or len(text) < 2:
                    print(f"[STT/11labs] Filtered: low confidence or too short")
                    return None
                # Filter hallucinated noise: only punctuation/whitespace
                import re as _re
                if not _re.search(r'[a-zA-ZäöüÄÖÜß]', text):
                    print(f"[STT/11labs] Filtered: no real words")
                    return None
                # Filter suspiciously long transcripts (likely hallucination)
                if len(text) > 500:
                    print(f"[STT/11labs] Filtered: too long ({len(text)} chars, likely hallucination)")
                    return None
                # Detect repetitive/nonsense hallucinations
                words = text.split()
                if len(words) > 5:
                    unique_ratio = len(set(w.lower() for w in words)) / len(words)
                    if unique_ratio < 0.3:
                        print(f"[STT/11labs] Filtered: repetitive (unique ratio {unique_ratio:.2f})")
                        return None
                words = result.get("words", [])
                if words:
                    confidences = [w.get("confidence", 1.0) for w in words if "confidence" in w]
                    if confidences and sum(confidences) / len(confidences) < 0.4:
                        print(f"[STT/11labs] Filtered: low word confidence")
                        return None
                if words and any(w.get("speaker_id") for w in words):
                    parts, cur_spk, cur_txt = [], None, []
                    for w in words:
                        spk = w.get("speaker_id", "?")
                        if spk != cur_spk:
                            if cur_txt:
                                parts.append(f"[Speaker {cur_spk}]: {' '.join(cur_txt)}")
                            cur_spk, cur_txt = spk, [w.get("text", "")]
                        else:
                            cur_txt.append(w.get("text", ""))
                    if cur_txt:
                        parts.append(f"[Speaker {cur_spk}]: {' '.join(cur_txt)}")
                    return "\n".join(parts)
                return text if text else None


class OpenAISTT(STTProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def transcribe(self, audio_pcm: bytes) -> Optional[str]:
        async with aiohttp.ClientSession() as session:
            wav_data = pcm_to_wav(audio_pcm)
            print(f"[STT/openai] Sending {len(wav_data)} bytes WAV")
            form = aiohttp.FormData()
            form.add_field('file', wav_data, filename='audio.wav', content_type='audio/wav')
            form.add_field('model', 'whisper-1')
            async with session.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                data=form
            ) as resp:
                if resp.status != 200:
                    print(f"[STT/openai] Error: {resp.status} - {await resp.text()}")
                    return None
                result = await resp.json()
                text = result.get("text", "").strip()
                print(f"[STT/openai] Text: '{text[:200]}'")
                if len(text) < 2 or len(text) > 500:
                    return None
                return text


class DeepgramSTT(STTProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def transcribe(self, audio_pcm: bytes) -> Optional[str]:
        async with aiohttp.ClientSession() as session:
            wav_data = pcm_to_wav(audio_pcm)
            print(f"[STT/deepgram] Sending {len(wav_data)} bytes WAV")
            async with session.post(
                "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&detect_language=true",
                headers={"Authorization": f"Token {self.api_key}", "Content-Type": "audio/wav"},
                data=wav_data
            ) as resp:
                if resp.status != 200:
                    print(f"[STT/deepgram] Error: {resp.status} - {await resp.text()}")
                    return None
                result = await resp.json()
                alt = result.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0]
                text = alt.get("transcript", "").strip()
                confidence = alt.get("confidence", 0)
                print(f"[STT/deepgram] Text: '{text[:200]}' (conf={confidence:.2f})")
                if confidence < 0.4 or len(text) < 2:
                    print(f"[STT/deepgram] Filtered")
                    return None
                return text


# ── TTS Providers ──

class TTSProvider(ABC):
    @abstractmethod
    async def synthesize_stream(self, text: str, send_audio) -> bool:
        """Stream TTS audio via send_audio(bytes) callback. Return True if audio was sent."""
        pass


class ElevenLabsTTS(TTSProvider):
    def __init__(self, api_key: str, voice_id: str = "bIHbv24MWmeRgasZH58o"):
        self.api_key = api_key
        self.voice_id = voice_id

    async def synthesize_stream(self, text: str, send_audio) -> bool:
        async with aiohttp.ClientSession() as session:
            payload = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            }
            async with session.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}?output_format=pcm_16000",
                headers={"xi-api-key": self.api_key, "Content-Type": "application/json"},
                json=payload
            ) as resp:
                if resp.status != 200:
                    print(f"[TTS/11labs] Error: {resp.status} - {await resp.text()}")
                    return False
                total = 0
                buf = bytearray()
                CHUNK_SIZE = 16000
                async for chunk in resp.content.iter_any():
                    buf.extend(chunk)
                    while len(buf) >= CHUNK_SIZE:
                        await send_audio(bytes(buf[:CHUNK_SIZE]))
                        total += CHUNK_SIZE
                        del buf[:CHUNK_SIZE]
                if buf:
                    if len(buf) % 2 != 0:
                        buf.append(0)
                    await send_audio(bytes(buf))
                    total += len(buf)
                print(f"[TTS/11labs] Streamed {total} bytes PCM")
                return total > 0


class OpenAITTS(TTSProvider):
    def __init__(self, api_key: str, voice: str = "alloy"):
        self.api_key = api_key
        self.voice = voice

    async def synthesize_stream(self, text: str, send_audio) -> bool:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": "tts-1",
                "input": text,
                "voice": self.voice,
                "response_format": "pcm",  # raw 24kHz 16-bit mono PCM
            }
            async with session.post(
                "https://api.openai.com/v1/audio/speech",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload
            ) as resp:
                if resp.status != 200:
                    print(f"[TTS/openai] Error: {resp.status} - {await resp.text()}")
                    return False
                # OpenAI returns 24kHz PCM, we need to resample to 16kHz
                total = 0
                buf = bytearray()
                CHUNK_SIZE = 24000  # 500ms at 24kHz
                async for chunk in resp.content.iter_any():
                    buf.extend(chunk)
                    while len(buf) >= CHUNK_SIZE:
                        resampled = _resample_24k_to_16k(bytes(buf[:CHUNK_SIZE]))
                        await send_audio(resampled)
                        total += len(resampled)
                        del buf[:CHUNK_SIZE]
                if buf:
                    if len(buf) % 2 != 0:
                        buf.append(0)
                    resampled = _resample_24k_to_16k(bytes(buf))
                    await send_audio(resampled)
                    total += len(resampled)
                print(f"[TTS/openai] Streamed {total} bytes PCM (resampled 24k→16k)")
                return total > 0


class DeepgramTTS(TTSProvider):
    def __init__(self, api_key: str, voice: str = "aura-asteria-en"):
        self.api_key = api_key
        self.voice = voice

    async def synthesize_stream(self, text: str, send_audio) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.deepgram.com/v1/speak?model={self.voice}&encoding=linear16&sample_rate=16000",
                headers={"Authorization": f"Token {self.api_key}", "Content-Type": "application/json"},
                json={"text": text}
            ) as resp:
                if resp.status != 200:
                    print(f"[TTS/deepgram] Error: {resp.status} - {await resp.text()}")
                    return False
                total = 0
                buf = bytearray()
                CHUNK_SIZE = 16000
                async for chunk in resp.content.iter_any():
                    buf.extend(chunk)
                    while len(buf) >= CHUNK_SIZE:
                        await send_audio(bytes(buf[:CHUNK_SIZE]))
                        total += CHUNK_SIZE
                        del buf[:CHUNK_SIZE]
                if buf:
                    if len(buf) % 2 != 0:
                        buf.append(0)
                    await send_audio(bytes(buf))
                    total += len(buf)
                print(f"[TTS/deepgram] Streamed {total} bytes PCM")
                return total > 0


def _resample_24k_to_16k(data: bytes) -> bytes:
    """Simple 3:2 decimation from 24kHz to 16kHz (linear interpolation)."""
    import array
    samples = array.array('h')
    samples.frombytes(data[:len(data) - len(data) % 2])
    n = len(samples)
    out = array.array('h')
    ratio = 24000 / 16000  # 1.5
    out_len = int(n / ratio)
    for i in range(out_len):
        src = i * ratio
        idx = int(src)
        frac = src - idx
        if idx + 1 < n:
            val = int(samples[idx] * (1 - frac) + samples[idx + 1] * frac)
        else:
            val = samples[min(idx, n - 1)]
        out.append(max(-32768, min(32767, val)))
    return out.tobytes()


# ── Provider factory ──

def create_stt_provider() -> Optional[STTProvider]:
    provider = os.getenv("STT_PROVIDER", "elevenlabs").lower()
    if provider == "elevenlabs":
        key = os.getenv("ELEVENLABS_API_KEY", "")
        return ElevenLabsSTT(key) if key else None
    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        return OpenAISTT(key) if key else None
    elif provider == "deepgram":
        key = os.getenv("DEEPGRAM_API_KEY", "")
        return DeepgramSTT(key) if key else None
    print(f"[STT] Unknown provider: {provider}")
    return None


def create_tts_provider() -> Optional[TTSProvider]:
    provider = os.getenv("TTS_PROVIDER", "elevenlabs").lower()
    voice = os.getenv("TTS_VOICE", "")
    if provider == "elevenlabs":
        key = os.getenv("ELEVENLABS_API_KEY", "")
        return ElevenLabsTTS(key, voice or "bIHbv24MWmeRgasZH58o") if key else None
    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY", "")
        return OpenAITTS(key, voice or "alloy") if key else None
    elif provider == "deepgram":
        key = os.getenv("DEEPGRAM_API_KEY", "")
        return DeepgramTTS(key, voice or "aura-asteria-en") if key else None
    print(f"[TTS] Unknown provider: {provider}")
    return None


# ── App setup ──

app = FastAPI(title="Clack Voice Relay")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

OPENCLAW_GATEWAY_URL = os.getenv("OPENCLAW_GATEWAY_URL", "http://127.0.0.1:18789")
OPENCLAW_GATEWAY_TOKEN = os.getenv("OPENCLAW_GATEWAY_TOKEN", "")
RELAY_AUTH_TOKEN = os.getenv("RELAY_AUTH_TOKEN", "")
DEFAULT_VOICE_ID = "bIHbv24MWmeRgasZH58o"
VOICE_ALIASES = {
    "will": "bIHbv24MWmeRgasZH58o",
    "aria": "9BWtsMINqrJLrRacOk9x",
    "roger": "CwhRBWXzGAHq8TQ4Fs17",
    "sarah": "EXAVITQu4vr4xnSDxMaL",
    "laura": "FGY2WhTYpPnrIDTdsKH5",
    "charlie": "IKne3meq5aSn9XLyUdCD",
    "george": "JBFqnCBsd6RMkjVDRZzb",
    "callum": "N2lVS1w4EtoT3dr4eOWO",
    "river": "SAz9YHcvj6GT2YYXdXww",
    "liam": "TX3LPaxmHKxFdv7VOQHJ",
    "charlotte": "XB0fDUnXU5powFXDhCwa",
    "alice": "Xb7hH8MSUJpSbSDYk0k2",
    "matilda": "XrExE9yKIg1WjnnlVkGX",
    "jessica": "cgSgspJ2msm6clMCkdW9",
    "eric": "cjVigY5qzO86Huf0OWal",
    "chris": "iP95p4xoKVk53GoZ742B",
    "brian": "nPczCjzI2devNBz1zQrb",
    "daniel": "onwK4e9ZLuTAKqWW03F9",
    "lily": "pFZP5JQG7iQjIQuC4Bku",
    "bill": "pqHfZKP75CvOlQylNhV4",
}
VOICE_METADATA = [
    {"id": "bIHbv24MWmeRgasZH58o", "name": "Will", "gender": "male", "accent": "American", "style": "warm, relaxed"},
    {"id": "9BWtsMINqrJLrRacOk9x", "name": "Aria", "gender": "female", "accent": "American", "style": "expressive, confident"},
    {"id": "CwhRBWXzGAHq8TQ4Fs17", "name": "Roger", "gender": "male", "accent": "American", "style": "deep, authoritative"},
    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "gender": "female", "accent": "American", "style": "soft, friendly"},
    {"id": "FGY2WhTYpPnrIDTdsKH5", "name": "Laura", "gender": "female", "accent": "American", "style": "gentle, soothing"},
    {"id": "IKne3meq5aSn9XLyUdCD", "name": "Charlie", "gender": "male", "accent": "Australian", "style": "casual, natural"},
    {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "George", "gender": "male", "accent": "British", "style": "warm, narrative"},
    {"id": "N2lVS1w4EtoT3dr4eOWO", "name": "Callum", "gender": "male", "accent": "Scottish", "style": "intense, character"},
    {"id": "SAz9YHcvj6GT2YYXdXww", "name": "River", "gender": "nonbinary", "accent": "American", "style": "calm, confident"},
    {"id": "TX3LPaxmHKxFdv7VOQHJ", "name": "Liam", "gender": "male", "accent": "American", "style": "articulate, neutral"},
    {"id": "XB0fDUnXU5powFXDhCwa", "name": "Charlotte", "gender": "female", "accent": "Swedish", "style": "elegant, seductive"},
    {"id": "Xb7hH8MSUJpSbSDYk0k2", "name": "Alice", "gender": "female", "accent": "British", "style": "confident, clear"},
    {"id": "XrExE9yKIg1WjnnlVkGX", "name": "Matilda", "gender": "female", "accent": "American", "style": "warm, pleasant"},
    {"id": "cgSgspJ2msm6clMCkdW9", "name": "Jessica", "gender": "female", "accent": "American", "style": "expressive, upbeat"},
    {"id": "cjVigY5qzO86Huf0OWal", "name": "Eric", "gender": "male", "accent": "American", "style": "friendly, conversational"},
    {"id": "iP95p4xoKVk53GoZ742B", "name": "Chris", "gender": "male", "accent": "American", "style": "casual, clear"},
    {"id": "nPczCjzI2devNBz1zQrb", "name": "Brian", "gender": "male", "accent": "American", "style": "deep, narrative"},
    {"id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel", "gender": "male", "accent": "British", "style": "authoritative, deep"},
    {"id": "pFZP5JQG7iQjIQuC4Bku", "name": "Lily", "gender": "female", "accent": "British", "style": "warm, clear"},
    {"id": "pqHfZKP75CvOlQylNhV4", "name": "Bill", "gender": "male", "accent": "American", "style": "trustworthy, documentary"},
]
MAX_INPUT_CHARS = int(os.getenv("CLACK_MAX_INPUT_CHARS", "300"))

DEFAULT_SYSTEM_PROMPT = (
    "You are a voice assistant. The user is talking to you via voice. "
    "RESPONSE RULES — these are MANDATORY:\n"
    "- Keep responses to 1-3 sentences MAX. This is spoken conversation, not text.\n"
    "- NEVER use bullet points, numbered lists, markdown, or headers.\n"
    "- NEVER give long explanations. Be brief like a real person talking.\n"
    "- If the user asks something complex, give a short summary and offer to elaborate.\n"
    "- Respond naturally and directly. No filler phrases.\n"
    "- Do not include or reference any metadata, labels, or formatting artifacts.\n"
    "SAFETY: This is a voice session — transcription errors and hallucinations are common. "
    "NEVER execute destructive actions (delete files, send emails/messages, modify system settings, "
    "run shell commands, make purchases, or change configurations) based on voice input alone. "
    "For any action that modifies data or has external effects, describe what you WOULD do and ask for explicit confirmation. "
    "Read-only actions (search, weather, info lookups) are fine without confirmation."
)

stt_provider = create_stt_provider()
tts_provider = create_tts_provider()

STT_NAME = os.getenv("STT_PROVIDER", "elevenlabs")
TTS_NAME = os.getenv("TTS_PROVIDER", "elevenlabs")
print(f"[Clack] Starting voice relay server...")
print(f"[Clack] STT: {STT_NAME} ({'ready' if stt_provider else 'NOT CONFIGURED'})")
print(f"[Clack] TTS: {TTS_NAME} ({'ready' if tts_provider else 'NOT CONFIGURED'})")
print(f"[Clack] Gateway: {OPENCLAW_GATEWAY_URL}")
print(f"[Clack] Relay auth: {'ENABLED' if RELAY_AUTH_TOKEN else 'DISABLED (open!)'}")


# ── History ──

HISTORY_DIR = Path(os.getenv("CLACK_HISTORY_DIR", "/var/lib/clack/history"))
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
MAX_HISTORY_MESSAGES = int(os.getenv("CLACK_MAX_HISTORY", "50"))


def _history_path() -> Path:
    return HISTORY_DIR / "conversation.json"


def load_history() -> list:
    path = _history_path()
    if path.exists():
        try:
            data = json.loads(path.read_text())
            print(f"[History] Loaded {len(data)} messages")
            return data[-MAX_HISTORY_MESSAGES:]
        except Exception as e:
            print(f"[History] Error loading: {e}")
    return []


def save_history(history: list):
    path = _history_path()
    try:
        path.write_text(json.dumps(history[-MAX_HISTORY_MESSAGES:]))
    except Exception as e:
        print(f"[History] Error saving: {e}")


def verify_token(token: str) -> bool:
    if not RELAY_AUTH_TOKEN:
        return True
    return hmac.compare_digest(token, RELAY_AUTH_TOKEN)


# ── Pairing ──

import secrets
import string

_pairing_codes: dict = {}  # code -> {"expires": timestamp}
PAIRING_TTL = 300  # 5 minutes


def _generate_pairing_code() -> str:
    """Generate a 6-char alphanumeric one-time pairing code."""
    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    _pairing_codes[code] = {"expires": time.time() + PAIRING_TTL}
    # Clean expired codes
    now = time.time()
    expired = [c for c, v in _pairing_codes.items() if v["expires"] < now]
    for c in expired:
        del _pairing_codes[c]
    return code


def _redeem_pairing_code(code: str) -> bool:
    """Validate and consume a one-time pairing code."""
    code = code.upper().strip()
    entry = _pairing_codes.pop(code, None)
    if not entry:
        return False
    if time.time() > entry["expires"]:
        return False
    return True


# ── Context store ──
# Persistent context that gets injected into the system prompt.
# Can be set via HTTP endpoint or WebSocket message.

CONTEXT_FILE = HISTORY_DIR / "context.json"


def load_context() -> dict:
    """Load saved context. Returns dict with 'text' and optional metadata."""
    if CONTEXT_FILE.exists():
        try:
            return json.loads(CONTEXT_FILE.read_text())
        except Exception as e:
            print(f"[Context] Error loading: {e}")
    return {}


def save_context(ctx: dict):
    """Save context to disk."""
    try:
        CONTEXT_FILE.write_text(json.dumps(ctx))
        print(f"[Context] Saved: {json.dumps(ctx)[:100]}")
    except Exception as e:
        print(f"[Context] Error saving: {e}")


# ── Voice Session ──

class VoiceSession:
    def __init__(self, websocket: WebSocket, config: dict):
        self.websocket = websocket
        self.config = config
        self.user_context = load_context()
        self.system_prompt = self._build_system_prompt(config)
        self.conversation_history = load_history()
        self.audio_buffer = bytearray()
        self.last_assistant_response = ""
        self.processing = False

        # Allow per-session voice override
        voice = config.get("voice", "")
        if voice and tts_provider and isinstance(tts_provider, ElevenLabsTTS):
            self.tts = ElevenLabsTTS(tts_provider.api_key, VOICE_ALIASES.get(voice, voice))
        else:
            self.tts = tts_provider
        self.stt = stt_provider

        # Apply context from start config if provided
        if config.get("context"):
            self.update_context(config["context"])

    def _build_system_prompt(self, config: dict) -> str:
        """Build system prompt with optional user context injected."""
        base = config.get("systemPrompt", DEFAULT_SYSTEM_PROMPT)
        ctx = self.user_context
        if ctx.get("text"):
            base += f"\n\nUSER CONTEXT (provided by the user — use this to inform your responses):\n{ctx['text']}"
        return base

    def update_context(self, text: str):
        """Update the user context and rebuild system prompt."""
        self.user_context = {"text": text, "updated": time.time()}
        save_context(self.user_context)
        self.system_prompt = self._build_system_prompt(self.config)
        print(f"[Context] Updated: {text[:100]}")

    async def send_json(self, data: dict):
        await self.websocket.send_text(json.dumps(data))

    async def send_audio(self, audio_data: bytes):
        await self.websocket.send_bytes(audio_data)

    async def transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        if not self.stt:
            print("[STT] No provider configured")
            return None
        MAX_CHUNK = 960000
        if len(audio_data) > MAX_CHUNK:
            chunks = [audio_data[i:i + MAX_CHUNK] for i in range(0, len(audio_data), MAX_CHUNK)]
            print(f"[STT] Splitting {len(audio_data)} bytes into {len(chunks)} chunks")
            parts = [await self.stt.transcribe(c) for c in chunks]
            combined = " ".join(p for p in parts if p)
            return combined if combined.strip() else None
        return await self.stt.transcribe(audio_data)

    async def greet(self):
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.conversation_history,
            {"role": "user", "content": "[Voice session started. Greet the user briefly.]"},
        ]
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {OPENCLAW_GATEWAY_TOKEN}", "Content-Type": "application/json"}
            payload = {"model": "openclaw", "messages": messages, "max_tokens": 150}
            try:
                async with session.post(
                    f"{OPENCLAW_GATEWAY_URL}/v1/chat/completions",
                    headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        greeting = result["choices"][0]["message"]["content"]
                    else:
                        greeting = "Hey!"
            except Exception:
                greeting = "Hey!"
        self.conversation_history.append({"role": "assistant", "content": greeting})
        self.last_assistant_response = greeting
        print(f"[Greeting] {greeting}")
        await self.send_json({"type": "response_text", "text": greeting})
        await self.send_json({"type": "response_start", "format": "pcm_16000"})
        if self.tts:
            await self.tts.synthesize_stream(greeting[:500], self.send_audio)
        await self.send_json({"type": "response_end"})

    async def get_llm_response(self, user_message: str) -> Optional[str]:
        self.conversation_history.append({"role": "user", "content": user_message})
        save_history(self.conversation_history)
        messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history

        async def _llm_call():
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {OPENCLAW_GATEWAY_TOKEN}", "Content-Type": "application/json"}
                payload = {"model": "openclaw", "messages": messages, "max_tokens": 150}
                async with session.post(
                    f"{OPENCLAW_GATEWAY_URL}/v1/chat/completions",
                    headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        print(f"[LLM] OpenClaw error: {resp.status} - {await resp.text()}")
                        return None

        # Run LLM call with keepalive pings to prevent client timeout
        try:
            llm_task = asyncio.create_task(_llm_call())
            while not llm_task.done():
                done, _ = await asyncio.wait({llm_task}, timeout=5.0)
                if not done:
                    try:
                        await self.send_json({"type": "processing", "stage": "thinking"})
                        print(f"[LLM] Still waiting, sent keepalive")
                    except Exception:
                        pass
            content = llm_task.result()
            if content:
                self.conversation_history.append({"role": "assistant", "content": content})
                save_history(self.conversation_history)
                return content
            return "Sorry, I had trouble processing that."
        except Exception as e:
            print(f"[LLM] Connection error: {e}")
            return "Sorry, I couldn't reach the assistant right now."


# ── HTTP endpoints ──

@app.get("/")
async def root():
    return {"status": "ok", "service": "Clack Voice Relay", "stt": STT_NAME, "tts": TTS_NAME}

@app.get("/health")
async def health():
    return {"status": "ok", "backend": "openclaw", "stt": STT_NAME, "tts": TTS_NAME}

@app.get("/voices")
async def list_voices(token: str = Query(default="")):
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    default = os.getenv("TTS_VOICE", "bIHbv24MWmeRgasZH58o")
    return {"voices": VOICE_METADATA, "default": default}


@app.get("/pair")
async def create_pairing(token: str = Query(default="")):
    """Generate a one-time pairing code. Requires admin auth (relay token)."""
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    code = _generate_pairing_code()
    print(f"[Pair] Generated code: {code} (expires in {PAIRING_TTL}s)")
    return {"code": code, "expires_in": PAIRING_TTL}


@app.post("/pair")
async def redeem_pairing(code: str = Query(default="")):
    """Redeem a pairing code to get the auth token. No auth required."""
    if not code:
        return {"error": "code required"}, 400
    if _redeem_pairing_code(code):
        print(f"[Pair] Code redeemed successfully")
        return {"token": RELAY_AUTH_TOKEN}
    else:
        print(f"[Pair] Invalid/expired code: {code}")
        return {"error": "invalid or expired code"}, 401


@app.get("/history")
async def get_history(token: str = Query(default="")):
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    history = load_history()
    return {"messages": history, "count": len(history)}

@app.delete("/history")
async def clear_history(token: str = Query(default="")):
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    path = _history_path()
    if path.exists():
        path.unlink()
    return {"cleared": True}


@app.get("/context")
async def get_context(token: str = Query(default="")):
    """Get the current user context."""
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    return load_context() or {"text": ""}


@app.put("/context")
async def set_context_put(token: str = Query(default=""), text: str = Query(default="")):
    """Set user context via query param."""
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    if not text:
        return {"error": "text required"}, 400
    ctx = {"text": text[:1000], "updated": time.time()}
    save_context(ctx)
    return {"ok": True, "context": ctx}


from fastapi import Request

@app.post("/context")
async def set_context_post(request: Request, token: str = Query(default="")):
    """Set user context via JSON body: {"text": "..."}"""
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    try:
        body = await request.json()
        text = body.get("text", "")
    except Exception:
        return {"error": "invalid JSON"}, 400
    if not text:
        return {"error": "text required"}, 400
    ctx = {"text": text[:1000], "updated": time.time()}
    save_context(ctx)
    return {"ok": True, "context": ctx}


@app.delete("/context")
async def clear_context(token: str = Query(default="")):
    """Clear user context."""
    if not verify_token(token):
        return {"error": "unauthorized"}, 401
    if CONTEXT_FILE.exists():
        CONTEXT_FILE.unlink()
    return {"cleared": True}


# ── WebSocket ──

@app.websocket("/voice")
async def voice_endpoint(websocket: WebSocket, token: str = Query(default="")):
    await websocket.accept()
    print(f"[WS] Client connected: {websocket.client}")
    authenticated = verify_token(token) if token else not RELAY_AUTH_TOKEN
    session = None
    try:
        while True:
            message = await websocket.receive()
            if "text" in message:
                data = json.loads(message["text"])
                msg_type = data.get("type")
                if msg_type == "auth" and not authenticated:
                    if verify_token(data.get("token", "")):
                        authenticated = True
                        await websocket.send_text(json.dumps({"type": "auth_ok"}))
                    else:
                        await websocket.send_text(json.dumps({"type": "auth_failed"}))
                        await websocket.close(code=4001, reason="Invalid token")
                        return
                    continue
                if not authenticated:
                    await websocket.send_text(json.dumps({"type": "auth_required"}))
                    await websocket.close(code=4001, reason="Authentication required")
                    return
                if msg_type == "start":
                    config = data.get("config", {})
                    session = VoiceSession(websocket, config)
                    print(f"[WS] Session started")
                    await session.send_json({"type": "ready"})
                    if session.conversation_history:
                        print(f"[WS] Resuming ({len(session.conversation_history)} messages)")
                    await session.greet()
                elif msg_type == "set_context" and session:
                    ctx_text = data.get("text", "")
                    if ctx_text:
                        session.update_context(ctx_text)
                        await session.send_json({"type": "context_updated", "text": ctx_text})
                    else:
                        # Clear context
                        session.user_context = {}
                        if CONTEXT_FILE.exists():
                            CONTEXT_FILE.unlink()
                        session.system_prompt = session._build_system_prompt(session.config)
                        await session.send_json({"type": "context_cleared"})
                elif msg_type == "end_speech" and session:
                    if session.processing:
                        print(f"[WS] Ignoring end_speech — still processing")
                        session.audio_buffer = bytearray()
                        continue
                    if session.audio_buffer:
                        session.processing = True
                        print(f"[WS] Processing {len(session.audio_buffer)} bytes")
                        await session.send_json({"type": "processing", "stage": "transcribing"})
                        transcript = await session.transcribe_audio(bytes(session.audio_buffer))
                        if not transcript:
                            await session.send_json({"type": "processing", "stage": "filtered"})
                            await session.send_json({"type": "response_end"})
                            session.audio_buffer = bytearray()
                            session.processing = False
                            continue
                        if session.last_assistant_response and _is_echo(transcript, session.last_assistant_response):
                            print(f"[STT] Filtered: echo")
                            await session.send_json({"type": "processing", "stage": "filtered"})
                            await session.send_json({"type": "response_end"})
                            session.audio_buffer = bytearray()
                            session.processing = False
                            continue
                        # Strip speaker labels — they confuse the LLM
                        import re
                        transcript = re.sub(r'\[Speaker \w+\]:\s*', '', transcript).strip()
                        # Enforce input length limit
                        if len(transcript) > MAX_INPUT_CHARS:
                            print(f"[STT] Truncated: {len(transcript)} → {MAX_INPUT_CHARS} chars")
                            transcript = transcript[:MAX_INPUT_CHARS]
                        print(f"[STT] Transcript: {transcript}")
                        await session.send_json({"type": "transcript", "text": transcript, "final": True})
                        await session.send_json({"type": "processing", "stage": "thinking"})
                        response = await session.get_llm_response(transcript)
                        if response:
                            print(f"[LLM] Response: {response[:100]}...")
                            session.last_assistant_response = response
                            await session.send_json({"type": "response_text", "text": response})
                            await session.send_json({"type": "processing", "stage": "speaking"})
                            await session.send_json({"type": "response_start", "format": "pcm_16000"})
                            if session.tts:
                                await session.tts.synthesize_stream(response[:500], session.send_audio)
                            await session.send_json({"type": "response_end"})
                        session.audio_buffer = bytearray()
                        session.processing = False
                elif msg_type == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            elif "bytes" in message and session:
                if not authenticated:
                    continue
                session.audio_buffer.extend(message["bytes"])
    except WebSocketDisconnect:
        print(f"[WS] Client disconnected")
    except Exception as e:
        print(f"[WS] Error: {e}")
    finally:
        print(f"[WS] Session ended")


if __name__ == "__main__":
    port = int(os.getenv("VOICE_RELAY_PORT", "9878"))
    uvicorn.run(app, host="0.0.0.0", port=port, ws_ping_interval=20, ws_ping_timeout=30)
