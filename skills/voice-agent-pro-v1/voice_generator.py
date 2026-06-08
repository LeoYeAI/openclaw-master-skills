#!/usr/bin/env python3
"""
voice_generator.py — Voice Agent
Handles TTS generation, voice clone management, and call logging.

Usage:
  python3 voice_generator.py tts --text "Hello" --output out.mp3
  python3 voice_generator.py tts --script /workspace/voice/scripts/vsl.md
  python3 voice_generator.py status
  python3 voice_generator.py calls --action list
  python3 voice_generator.py calls --action summary
"""

import argparse
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

CONFIG_FILE  = "/workspace/voice/config.json"
OUTPUT_DIR   = "/workspace/voice/output/"
SCRIPTS_DIR  = "/workspace/voice/scripts/"
CALLS_DIR    = "/workspace/voice/calls/"
AUDIT_FILE   = "/workspace/AUDIT.md"
ERRORS_FILE  = "/workspace/.learnings/ERRORS.md"


# ── Config ────────────────────────────────────────────────────────────────────

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_config(data):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_api_key():
    cfg = load_config()
    key = cfg.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print("❌ ELEVENLABS_API_KEY not found in config.json or .env")
        print("   Run voice-agent setup first, or set the key manually.")
        sys.exit(1)
    return key


def get_voice_id():
    cfg = load_config()
    vid = cfg.get("ELEVENLABS_VOICE_ID") or os.environ.get("ELEVENLABS_VOICE_ID")
    if not vid:
        print("❌ ELEVENLABS_VOICE_ID not found")
        print("   Voice clone not yet created. Run voice-agent setup.")
        sys.exit(1)
    return vid


# ── Logging ───────────────────────────────────────────────────────────────────

def log_audit(msg):
    os.makedirs(os.path.dirname(AUDIT_FILE), exist_ok=True)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {msg}\n")


def log_error(error_type, description, action, resolution="pending"):
    os.makedirs(os.path.dirname(ERRORS_FILE), exist_ok=True)
    with open(ERRORS_FILE, "a", encoding="utf-8") as f:
        f.write(
            f"\n[{datetime.now().strftime('%Y-%m-%d')}] {error_type}\n"
            f"  Description: {description}\n"
            f"  Action taken: {action}\n"
            f"  Resolution: {resolution}\n"
        )


# ── TTS ───────────────────────────────────────────────────────────────────────

def chunk_text(text, max_chars=900):
    """Split text into chunks at sentence boundaries."""
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current = ""
    for s in sentences:
        if len(current) + len(s) + 2 <= max_chars:
            current += s + ". "
        else:
            if current:
                chunks.append(current.strip())
            current = s + ". "
    if current:
        chunks.append(current.strip())
    return chunks


def tts_chunk(api_key, voice_id, text, model="eleven_multilingual_v2"):
    """Convert one text chunk to audio bytes via ElevenLabs API."""
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model,
            output_format="mp3_44100_128",
        )
        return b"".join(audio)
    except ImportError:
        # Fallback to requests if SDK not installed
        import requests
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        data = {
            "text": text,
            "model_id": model,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.content


def generate_tts(text, output_path, model="eleven_multilingual_v2"):
    """Generate full MP3 from text, handling chunking and concatenation."""
    api_key  = get_api_key()
    voice_id = get_voice_id()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    chunks = chunk_text(text)
    print(f"  Generating {len(chunks)} chunk(s)...")

    tmp_files = []
    for i, chunk in enumerate(chunks):
        tmp_path = f"/tmp/voice_chunk_{i:03d}.mp3"
        print(f"  Chunk {i+1}/{len(chunks)}: {len(chunk)} chars")
        audio_bytes = tts_chunk(api_key, voice_id, chunk, model)
        with open(tmp_path, "wb") as f:
            f.write(audio_bytes)
        tmp_files.append(tmp_path)

    if len(tmp_files) == 1:
        import shutil
        shutil.copy(tmp_files[0], output_path)
    else:
        # Concatenate with ffmpeg
        list_file = "/tmp/voice_concat_list.txt"
        with open(list_file, "w") as f:
            for p in tmp_files:
                f.write(f"file '{p}'\n")
        result = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", list_file, "-c", "copy", output_path],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            log_error("FFMPEG_CONCAT_FAILED", result.stderr,
                      "ffmpeg concat failed", "pending")
            # Fallback: use first chunk only
            import shutil
            shutil.copy(tmp_files[0], output_path)
            print("  ⚠️  ffmpeg concat failed — saved first chunk only")

    # Cleanup temp files
    for p in tmp_files:
        try:
            os.remove(p)
        except Exception:
            pass

    duration = get_mp3_duration(output_path)
    log_audit(f"TTS generated: {os.path.basename(output_path)} — {duration}s")
    print(f"  ✅ Saved: {output_path} ({duration}s)")
    return output_path


def get_mp3_duration(path):
    """Get MP3 duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True
        )
        return round(float(result.stdout.strip()), 1)
    except Exception:
        return "?"


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_tts(args):
    """Generate TTS from text or script file."""
    if args.script:
        script_path = args.script
        if not os.path.exists(script_path):
            print(f"❌ Script not found: {script_path}")
            sys.exit(1)
        with open(script_path, encoding="utf-8") as f:
            text = f.read()
        name = Path(script_path).stem
    elif args.text:
        text = args.text
        name = "output"
    else:
        print("❌ Provide --text or --script")
        sys.exit(1)

    output = args.output or os.path.join(OUTPUT_DIR, f"{name}.mp3")
    model  = args.model or "eleven_multilingual_v2"

    print(f"\n🎙️  Generating TTS...")
    print(f"  Text length: {len(text)} chars")
    print(f"  Model: {model}")
    print(f"  Output: {output}")
    generate_tts(text, output, model)


def cmd_status(args):
    """Show voice agent configuration status."""
    cfg = load_config()
    print("\n🎙️  Voice Agent Status")
    print(f"  API Key:    {'✅ configured' if cfg.get('ELEVENLABS_API_KEY') else '❌ missing'}")
    print(f"  Voice ID:   {'✅ ' + cfg.get('ELEVENLABS_VOICE_ID', '')[:12] + '...' if cfg.get('ELEVENLABS_VOICE_ID') else '❌ missing (voice not cloned)'}")
    print(f"  Agent ID:   {'✅ configured' if cfg.get('ELEVENLABS_AGENT_ID') else '⚪ not configured (calls disabled)'}")
    print(f"  Twilio:     {'✅ connected' if cfg.get('TWILIO_CONFIGURED') else '⚪ not configured (calls disabled)'}")
    print(f"  Setup date: {cfg.get('setup_date', 'not set')}")

    # Check voice samples
    samples_dir = "/workspace/voice/samples/"
    if os.path.exists(samples_dir):
        samples = [f for f in os.listdir(samples_dir) if f.endswith('.mp3')]
        print(f"  Samples:    {len(samples)} MP3 file(s) in samples/")
    else:
        print(f"  Samples:    ❌ /workspace/voice/samples/ not found")

    # Check output files
    if os.path.exists(OUTPUT_DIR):
        outputs = list(Path(OUTPUT_DIR).glob("*.mp3"))
        print(f"  Outputs:    {len(outputs)} MP3 file(s) generated")


def cmd_calls(args):
    """Manage call queue and history."""
    pending_dir = os.path.join(CALLS_DIR, "pending/")
    history_dir = os.path.join(CALLS_DIR, "history/")

    if args.action == "list":
        if not os.path.exists(pending_dir):
            print("No pending calls.")
            return
        files = list(Path(pending_dir).glob("*.json"))
        print(f"\n📞 Pending calls: {len(files)}")
        for f in files:
            with open(f) as fp:
                lead = json.load(fp)
            print(f"  {f.stem}: {lead.get('name', '?')} — {lead.get('phone', '?')} — {lead.get('reason', '?')}")

    elif args.action == "summary":
        if not os.path.exists(history_dir):
            print("No call history.")
            return
        files = list(Path(history_dir).glob("*.json"))
        outcomes = {}
        scores = []
        for f in files:
            with open(f) as fp:
                call = json.load(fp)
            outcome = call.get("outcome", "unknown")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
            if "score" in call:
                scores.append(call["score"])

        print(f"\n📊 Call History Summary ({len(files)} calls)")
        for outcome, count in sorted(outcomes.items()):
            print(f"  {outcome}: {count}")
        if scores:
            avg = sum(scores) / len(scores)
            print(f"  Avg qualification score: {avg:.1f}/10")

        log_audit(f"Call summary generated: {len(files)} calls reviewed")



def cmd_apply_config(args):
    """Write credentials to config.json — no container restart needed."""
    cfg = load_config()

    if args.api_key:
        cfg["ELEVENLABS_API_KEY"] = args.api_key
        print(f"  ✅ ELEVENLABS_API_KEY set")

    if args.voice_id:
        cfg["ELEVENLABS_VOICE_ID"] = args.voice_id
        print(f"  ✅ ELEVENLABS_VOICE_ID set: {args.voice_id[:8]}...")

    if args.agent_id:
        cfg["ELEVENLABS_AGENT_ID"] = args.agent_id
        print(f"  ✅ ELEVENLABS_AGENT_ID set")

    if not args.setup_date:
        from datetime import date
        cfg["setup_date"] = date.today().isoformat()

    save_config(cfg)
    log_audit(f"Config updated via apply-config — {list(cfg.keys())}")
    print(f"\n✅ config.json updated — credentials active immediately")
    print(f"   No container restart needed.")

    # Verify the key works
    if args.api_key or cfg.get("ELEVENLABS_API_KEY"):
        import urllib.request
        key = args.api_key or cfg["ELEVENLABS_API_KEY"]
        try:
            req = urllib.request.Request(
                "https://api.elevenlabs.io/v1/user",
                headers={"xi-api-key": key}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                import json
                data = json.loads(resp.read())
                plan = data.get("subscription", {}).get("tier", "unknown")
                print(f"   API key verified ✅ — plan: {plan}")
        except Exception as e:
            print(f"   API key check failed: {e}")

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Voice Agent — ElevenLabs TTS & Calls")
    sub = parser.add_subparsers(dest="command")

    # tts
    p_tts = sub.add_parser("tts", help="Generate audio from text or script")
    p_tts.add_argument("--text",   help="Text to convert")
    p_tts.add_argument("--script", help="Path to .md script file")
    p_tts.add_argument("--output", help="Output MP3 path")
    p_tts.add_argument("--model",  help="ElevenLabs model",
                       choices=["eleven_flash_v2_5", "eleven_multilingual_v2", "eleven_v3"],
                       default="eleven_multilingual_v2")

    # status
    sub.add_parser("status", help="Show configuration status")

    # calls
    p_calls = sub.add_parser("calls", help="Manage call queue and history")
    p_calls.add_argument("--action", choices=["list", "summary"], default="list")

    # apply-config — write credentials to config.json, no restart needed
    p_cfg = sub.add_parser("apply-config", help="Write credentials to config.json (no container restart needed)")
    p_cfg.add_argument("--api-key",    help="ELEVENLABS_API_KEY to save")
    p_cfg.add_argument("--voice-id",   help="ELEVENLABS_VOICE_ID to save")
    p_cfg.add_argument("--agent-id",   help="ELEVENLABS_AGENT_ID (optional — for calls)")

    args = parser.parse_args()

    dispatch = {
        "tts":          cmd_tts,
        "status":       cmd_status,
        "calls":        cmd_calls,
        "apply-config": cmd_apply_config,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
