#!/usr/bin/env python3
"""faster-whisper 语音转写 CLI。

用法:
    python3 transcribe.py --audio "path/to/audio.wav"
    python3 transcribe.py --audio "path/to/audio.wav" --language zh --model medium

依赖: faster-whisper (pip install faster-whisper)
输出: JSON 到 stdout（text, segments, language, duration）
"""

import argparse
import json
import os
import sys

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("错误: 未安装 faster-whisper，请运行: pip install faster-whisper", file=sys.stderr)
    sys.exit(1)


def transcribe(audio_path: str, language: str, model_size: str):
    if not os.path.isfile(audio_path):
        print(f"错误: 音频文件不存在: {audio_path}", file=sys.stderr)
        sys.exit(1)

    print(f"加载模型 {model_size}...", file=sys.stderr)
    model = WhisperModel(model_size, device="auto", compute_type="int8")

    print("开始转写...", file=sys.stderr)
    segments_iter, info = model.transcribe(audio_path, language=language, vad_filter=True)

    segments = []
    full_text_parts = []
    for seg in segments_iter:
        segments.append({
            "start": round(seg.start, 2),
            "end": round(seg.end, 2),
            "text": seg.text.strip(),
        })
        full_text_parts.append(seg.text.strip())

    result = {
        "text": "".join(full_text_parts),
        "segments": segments,
        "language": info.language,
        "duration": round(info.duration, 2),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="faster-whisper 语音转写 CLI")
    parser.add_argument("--audio", required=True, help="音频文件路径（推荐 16kHz mono WAV）")
    parser.add_argument("--language", default="zh", help="语言代码（默认 zh）")
    parser.add_argument("--model", default="medium", help="模型: tiny/base/small/medium/large-v3")
    args = parser.parse_args()
    transcribe(args.audio, args.language, args.model)


if __name__ == "__main__":
    main()
