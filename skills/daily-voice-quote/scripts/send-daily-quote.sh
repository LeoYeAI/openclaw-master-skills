#!/bin/bash
# Daily Voice Quote - 每日名言語音
# 使用前請設定環境變數（見下方說明）

set -e

# ============================================
# 環境變數設定（必須）
# ============================================
# ELEVENLABS_API_KEY       - ElevenLabs API Key
# LINE_CHANNEL_ACCESS_TOKEN - LINE Channel Access Token
# VOICE_NAME               - ElevenLabs 語音名稱（用於 sag -v）
# LINE_USER_ID             - LINE 使用者或群組 ID
# AUDIO_PUBLIC_URL         - 公開 URL base（如 https://YOUR_PUBLIC_HOST）

# 選填
# QUOTES_FILE              - 名言清單檔案（預設 references/quotes.md）
# AUDIO_LOCAL_PATH         - 本地路徑（需對應公開 URL，預設 /tmp）
# SPEAKER_NAME             - 語音稿中的說話者名稱（預設：空）
# SPEED                    - 語速（預設：0.95）
# STABILITY                - 穩定度（預設：1.0）
# SIMILARITY               - 相似度（預設：0.85）

# ============================================
# 預設值
# ============================================
AUDIO_LOCAL_PATH="${AUDIO_LOCAL_PATH:-/tmp}"
SPEED="${SPEED:-0.95}"
STABILITY="${STABILITY:-1.0}"
SIMILARITY="${SIMILARITY:-0.85}"

# ============================================
# 檢查必要環境變數
# ============================================
check_env() {
    local missing=""
    [ -z "$ELEVENLABS_API_KEY" ] && missing="$missing ELEVENLABS_API_KEY"
    [ -z "$LINE_CHANNEL_ACCESS_TOKEN" ] && missing="$missing LINE_CHANNEL_ACCESS_TOKEN"
    [ -z "$VOICE_NAME" ] && missing="$missing VOICE_NAME"
    [ -z "$LINE_USER_ID" ] && missing="$missing LINE_USER_ID"
    [ -z "$AUDIO_PUBLIC_URL" ] && missing="$missing AUDIO_PUBLIC_URL"

    if [ -n "$missing" ]; then
        echo "❌ 缺少環境變數:$missing"
        exit 1
    fi
}

# ============================================
# 讀取名言清單
# 來源：references/quotes.md
# 格式：
# 1. **Author**: "Quote"
#    - Translation
# ============================================
load_quotes() {
    local script_dir skill_dir
    script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
    skill_dir=$(cd "$script_dir/.." && pwd)

    QUOTES_FILE="${QUOTES_FILE:-$skill_dir/references/quotes.md}"

    if [ ! -f "$QUOTES_FILE" ]; then
        echo "❌ 找不到名言清單檔案: $QUOTES_FILE"
        exit 1
    fi

    mapfile -t QUOTES < <(
        awk '
        /^[0-9]+\./ {
            if (match($0, /\*\*(.*)\*\*: "(.*)"/, m)) {
                author=m[1]; quote_en=m[2]; getting=1; next;
            }
        }
        getting && /^[[:space:]]*-[[:space:]]*/ {
            sub(/^[[:space:]]*-[[:space:]]*/, "");
            quote_zh=$0;
            print author "|" quote_en "|" quote_zh;
            getting=0;
        }
        ' "$QUOTES_FILE"
    )

    if [ ${#QUOTES[@]} -eq 0 ]; then
        echo "❌ 無法從名言清單解析內容：$QUOTES_FILE"
        exit 1
    fi
}

# ============================================
# 主程式
# ============================================
main() {
    check_env
    load_quotes

    # 選擇今日名言
    DAY_OF_YEAR=$(date +%j)
    QUOTE_INDEX=$((DAY_OF_YEAR % ${#QUOTES[@]}))

    IFS='|' read -r AUTHOR QUOTE_EN QUOTE_ZH <<< "${QUOTES[$QUOTE_INDEX]}"

    echo "📜 今日名言 (#$((QUOTE_INDEX + 1)))："
    echo "   $AUTHOR: \"$QUOTE_EN\""
    echo "   $QUOTE_ZH"

    # 組合語音稿
    GREETING="早安"
    [ -n "$SPEAKER_NAME" ] && GREETING="早安，我是${SPEAKER_NAME}。"

    SCRIPT="${GREETING}[short pause] 今天想分享 ${AUTHOR} 的一句話：${QUOTE_ZH} [short pause] ${QUOTE_EN} [short pause] 願這句話能為你的一天帶來力量。加油！"

    echo ""
    echo "🎙️ 語音稿："
    echo "   $SCRIPT"

    # 生成語音
    echo ""
    echo "⏳ 生成語音中..."

    ELEVENLABS_API_KEY="$ELEVENLABS_API_KEY" sag -v "$VOICE_NAME" \
        --speed "$SPEED" --stability "$STABILITY" --similarity "$SIMILARITY" \
        -o "$AUDIO_LOCAL_PATH/daily-quote.mp3" "$SCRIPT"

    # 轉換為 m4a
    echo "⏳ 轉換為 m4a..."
    FFMPEG_OUTPUT=$(ffmpeg -i "$AUDIO_LOCAL_PATH/daily-quote.mp3" \
        -c:a aac -b:a 128k "$AUDIO_LOCAL_PATH/daily-quote.m4a" -y 2>&1)

    # 取得音訊長度
    DURATION_STR=$(echo "$FFMPEG_OUTPUT" | grep -oE 'time=[0-9:.]+' | tail -1 | cut -d= -f2)
    if [ -n "$DURATION_STR" ]; then
        # 轉換 HH:MM:SS.ms 為毫秒
        IFS=':' read -r H M S <<< "$DURATION_STR"
        DURATION_MS=$(echo "($H * 3600 + $M * 60 + $S) * 1000" | bc | cut -d. -f1)
    else
        # 備用方案：使用 ffprobe
        DURATION_MS=$(ffprobe -v error -show_entries format=duration \
            -of default=noprint_wrappers=1:nokey=1 \
            "$AUDIO_LOCAL_PATH/daily-quote.m4a" | awk '{printf "%.0f", $1 * 1000}')
    fi

    echo "📊 音訊長度：${DURATION_MS} 毫秒"

    # 發送到 LINE
    echo ""
    echo "📤 發送到 LINE..."

    RESPONSE=$(curl -s -X POST https://api.line.me/v2/bot/message/push \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $LINE_CHANNEL_ACCESS_TOKEN" \
        -d '{
            "to": "'"$LINE_USER_ID"'",
            "messages": [{
                "type": "audio",
                "originalContentUrl": "'"$AUDIO_PUBLIC_URL"'/daily-quote.m4a",
                "duration": '"$DURATION_MS"'
            }]
        }')

    if [ "$RESPONSE" = "{}" ]; then
        echo "✅ 發送成功！"
    else
        echo "❌ 發送失敗：$RESPONSE"
        exit 1
    fi
}

main "$@"
