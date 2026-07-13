#!/bin/bash
# Download audio from Bilibili video and transcribe with faster-whisper
# Usage: bash bilibili_transcribe.sh <bvid_or_url> [model_size]
# model_size: tiny, base (default), small, medium, large-v3

set -e

BVID_OR_URL="$1"
MODEL="${2:-base}"
OUTDIR="/tmp/bilibili_audio"
mkdir -p "$OUTDIR"

# Extract BV ID
BVID=$(echo "$BVID_OR_URL" | grep -oE 'BV[a-zA-Z0-9]+')
if [ -z "$BVID" ]; then
    echo "Error: Cannot extract BV ID from: $BVID_OR_URL" >&2
    exit 1
fi

AUDIO_FILE="$OUTDIR/${BVID}.mp3"
TRANSCRIPT_JSON="$OUTDIR/${BVID}_transcript.json"
TRANSCRIPT_TXT="$OUTDIR/${BVID}_transcript.txt"

# Step 1: Download audio (skip if already exists)
if [ -f "$AUDIO_FILE" ]; then
    echo "Audio already exists: $AUDIO_FILE" >&2
else
    echo "Downloading audio for $BVID..." >&2
    yt-dlp --cookies-from-browser chrome \
        -x --audio-format mp3 --audio-quality 5 \
        -o "$OUTDIR/${BVID}.%(ext)s" \
        --no-playlist \
        "https://www.bilibili.com/video/${BVID}/" 2>&1 | grep -E '(Downloading|download|Destination|Deleting|Error)' >&2
    echo "Audio downloaded: $AUDIO_FILE" >&2
fi

# Step 2: Transcribe with faster-whisper + opencc for t2s conversion
echo "Transcribing with faster-whisper (model: $MODEL)..." >&2
uv run --with "faster-whisper" --with "opencc-python-reimplemented" python3 - "$AUDIO_FILE" "$MODEL" "$TRANSCRIPT_JSON" "$TRANSCRIPT_TXT" << 'PYEOF'
import sys, json, time
from faster_whisper import WhisperModel
import opencc

audio_file = sys.argv[1]
model_size = sys.argv[2]
json_out = sys.argv[3]
txt_out = sys.argv[4]

converter = opencc.OpenCC('t2s')

print(f"Loading {model_size} model...", file=sys.stderr, flush=True)
model = WhisperModel(model_size, device="cpu", compute_type="int8")

print("Transcribing...", file=sys.stderr, flush=True)
start = time.time()
segments, info = model.transcribe(audio_file, language="zh", beam_size=5, vad_filter=True)

results = []
for seg in segments:
    text = converter.convert(seg.text.strip())
    results.append({"start": round(seg.start, 1), "end": round(seg.end, 1), "text": text})
    if len(results) % 100 == 0:
        print(f"  {len(results)} segments ({seg.end:.0f}s)...", file=sys.stderr, flush=True)

elapsed = time.time() - start
print(f"Done: {len(results)} segments in {elapsed:.0f}s", file=sys.stderr, flush=True)

with open(json_out, "w") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

full_text = " ".join([s["text"] for s in results])
with open(txt_out, "w") as f:
    f.write(full_text)

# Output JSON to stdout for piping
json.dump({"segments": len(results), "duration_s": results[-1]["end"] if results else 0,
           "chars": len(full_text), "json_path": json_out, "txt_path": txt_out}, sys.stdout)
PYEOF

echo "" >&2
echo "Transcript saved to: $TRANSCRIPT_JSON and $TRANSCRIPT_TXT" >&2
