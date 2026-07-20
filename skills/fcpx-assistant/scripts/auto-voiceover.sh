#!/bin/bash
# Auto Voice-Over Generator using Qwen TTS
# Generates narration from script text

SCRIPT_TEXT="$1"
OUTPUT_FILE="$2"

if [ -z "$SCRIPT_TEXT" ]; then
    echo "❌ 用法：auto-voiceover.sh <脚本文本> [输出文件]"
    echo "   或者：auto-voiceover.sh --file <脚本文件> [输出文件]"
    exit 1
fi

# Handle file input
if [ "$SCRIPT_TEXT" = "--file" ]; then
    SCRIPT_FILE="$2"
    OUTPUT_FILE="$3"
    
    if [ -z "$SCRIPT_FILE" ] || [ ! -f "$SCRIPT_FILE" ]; then
        echo "❌ 脚本文件不存在：$SCRIPT_FILE"
        exit 1
    fi
    
    SCRIPT_TEXT=$(cat "$SCRIPT_FILE")
fi

# Default output path
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="/tmp/voiceover-$(date +%s).mp3"
fi

echo "🎙️ 自动配音生成器 (Qwen TTS)"
echo "📝 文本长度：${#SCRIPT_TEXT} 字符"
echo "📤 输出：$OUTPUT_FILE"
echo ""

# Call Qwen TTS API
echo "🔊 正在生成语音..."

curl -s -X POST "http://127.0.0.1:7860/gradio_api/call/generate_voice_fn" \
    -H "Content-Type: application/json" \
    -d "{
        \"data\": [
            \"$SCRIPT_TEXT\",
            \"default\",
            \"auto\"
        ]
    }" > /tmp/tts-response.json 2>/dev/null

# Parse response and save audio
if [ -s /tmp/tts-response.json ]; then
    # Extract audio file path from response
    AUDIO_PATH=$(cat /tmp/tts-response.json | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Response format depends on TTS API
    print(data.get('data', [''])[0] if isinstance(data, dict) else '')
except:
    print('')
" 2>/dev/null)
    
    if [ -n "$AUDIO_PATH" ] && [ -f "$AUDIO_PATH" ]; then
        cp "$AUDIO_PATH" "$OUTPUT_FILE"
        echo "✅ 语音生成完成！"
        echo ""
        echo "📁 输出文件：$OUTPUT_FILE"
        
        # Get audio duration
        DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$OUTPUT_FILE" 2>/dev/null)
        echo "⏱️ 音频时长：${DURATION}s"
    else
        echo "⚠️  TTS 生成失败，请检查 Qwen TTS 服务是否运行"
        echo ""
        echo "💡 手动生成方法："
        echo "1. 访问 http://127.0.0.1:7860"
        echo "2. 输入文本生成语音"
        echo "3. 下载音频文件"
    fi
else
    echo "❌ TTS API 调用失败"
    echo ""
    echo "💡 请确保 Qwen TTS 服务正在运行："
    echo "   http://127.0.0.1:7860"
fi

rm -f /tmp/tts-response.json
