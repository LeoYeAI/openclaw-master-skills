#!/bin/bash
# Audio Normalizer for Final Cut Pro
# Normalizes audio to broadcast standard (-23 LUFS)

INPUT_FILE="$1"
OUTPUT_FILE="$2"

if [ -z "$INPUT_FILE" ]; then
    echo "❌ 用法：audio-normalizer.sh <输入文件> [输出文件]"
    exit 1
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ 文件不存在：$INPUT_FILE"
    exit 1
fi

# Default output path
if [ -z "$OUTPUT_FILE" ]; then
    OUTPUT_FILE="${INPUT_FILE%.*}-normalized.${INPUT_FILE##*.}"
fi

echo "🔊 音频标准化工具"
echo "📁 输入：$INPUT_FILE"
echo "📤 输出：$OUTPUT_FILE"
echo ""

# Step 1: Analyze current audio levels
echo "📊 步骤 1: 分析当前音频电平..."

ffmpeg -i "$INPUT_FILE" -af loudnorm=I=-16:TP=-1.5:LRA=11:print_format=summary -f null - 2>&1 | \
    grep -E "Input Integrated|Input True Peak|Input Threshold|Target Offset" > /tmp/audio-analysis.txt

if [ -s /tmp/audio-analysis.txt ]; then
    echo "当前音频状态："
    cat /tmp/audio-analysis.txt
    echo ""
else
    echo "⚠️  无法分析音频电平，继续处理..."
fi

# Step 2: Normalize audio
echo "🔧 步骤 2: 标准化音频到广播标准 (-23 LUFS)..."

ffmpeg -i "$INPUT_FILE" -af "loudnorm=I=-23:TP=-2:LRA=7" -c:v copy -y "$OUTPUT_FILE" 2>&1 | tail -5

if [ -f "$OUTPUT_FILE" ]; then
    echo ""
    echo "✅ 标准化完成！"
    echo ""
    
    # Verify output
    echo "📊 验证输出文件："
    ffprobe -v error -show_entries stream=codec_name,channels,sample_rate -of default=noprint_wrappers=1 "$OUTPUT_FILE"
    echo ""
    echo "📁 输出位置：$OUTPUT_FILE"
else
    echo "❌ 处理失败"
    exit 1
fi

rm -f /tmp/audio-analysis.txt

echo ""
echo "💡 提示："
echo "- 广播标准：-23 LUFS (EBU R128)"
echo "- YouTube 推荐：-14 LUFS"
echo "- 播客标准：-16 到 -20 LUFS"
