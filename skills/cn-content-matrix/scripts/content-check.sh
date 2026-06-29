#!/usr/bin/env bash
set -euo pipefail

# content-check.sh — 内容合规辅助检查脚本
# 用法: content-check.sh <文件路径> <平台代号: xhs|wechat|douyin|bilibili>

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFERENCES_DIR="$SCRIPT_DIR/../references"
SENSITIVE_WORDS_FILE="$REFERENCES_DIR/sensitive-words.md"

# ============================================================
# 参数校验
# ============================================================

if [[ $# -lt 2 ]]; then
    echo "❌ 用法: $0 <文件路径> <平台代号>"
    echo "   平台代号: xhs | wechat | douyin | bilibili"
    exit 1
fi

FILE_PATH="$1"
PLATFORM="$2"

if [[ ! -f "$FILE_PATH" ]]; then
    echo "❌ 文件不存在: $FILE_PATH"
    exit 1
fi

case "$PLATFORM" in
    xhs|wechat|douyin|bilibili) ;;
    *)
        echo "❌ 不支持的平台代号: $PLATFORM"
        echo "   支持: xhs | wechat | douyin | bilibili"
        exit 1
        ;;
esac

if [[ ! -f "$SENSITIVE_WORDS_FILE" ]]; then
    echo "⚠️  敏感词文件不存在: $SENSITIVE_WORDS_FILE（跳过敏感词检查）"
    SKIP_SENSITIVE=true
else
    SKIP_SENSITIVE=false
fi

# ============================================================
# 提取正文（跳过 YAML frontmatter 和结尾备注）
# ============================================================

CONTENT=$(awk '
    BEGIN { in_frontmatter=0; frontmatter_done=0; in_notes=0 }
    /^---$/ && !frontmatter_done { in_frontmatter = !in_frontmatter; if (!in_frontmatter) frontmatter_done=1; next }
    in_frontmatter { next }
    /^<!-- 以下为生成器备注/ { in_notes=1 }
    !in_notes && frontmatter_done { print }
' "$FILE_PATH")

# ============================================================
# 1. 字数检查
# ============================================================

# 统计中文字符+英文单词数（近似字数）
CHAR_COUNT=$(echo "$CONTENT" | sed 's/[[:space:]]//g' | sed 's/#//g' | wc -m | tr -d ' ')
# 更精确：中文字符数 + 英文单词数
CN_CHARS=$(echo "$CONTENT" | grep -oP '[\x{4e00}-\x{9fff}]' 2>/dev/null | wc -l || echo "$CHAR_COUNT")
WORD_COUNT=$CN_CHARS

# 平台字数范围
case "$PLATFORM" in
    xhs)      MIN_WORDS=300;  MAX_WORDS=800;  PLATFORM_NAME="小红书" ;;
    wechat)   MIN_WORDS=1500; MAX_WORDS=8000; PLATFORM_NAME="微信公众号" ;;
    douyin)   MIN_WORDS=200;  MAX_WORDS=5000; PLATFORM_NAME="抖音" ;;
    bilibili) MIN_WORDS=3000; MAX_WORDS=15000; PLATFORM_NAME="B站专栏" ;;
esac

WORD_STATUS="PASS"
WORD_MSG="字数 ${WORD_COUNT}，范围 ${MIN_WORDS}-${MAX_WORDS}"
if (( WORD_COUNT < MIN_WORDS )); then
    WORD_STATUS="FAIL"
    WORD_MSG="字数 ${WORD_COUNT} 低于最低要求 ${MIN_WORDS}"
elif (( WORD_COUNT > MAX_WORDS )); then
    WORD_STATUS="FAIL"
    WORD_MSG="字数 ${WORD_COUNT} 超过上限 ${MAX_WORDS}"
elif (( WORD_COUNT < MIN_WORDS + (MAX_WORDS - MIN_WORDS) / 10 )) || (( WORD_COUNT > MAX_WORDS - (MAX_WORDS - MIN_WORDS) / 10 )); then
    WORD_STATUS="WARNING"
    WORD_MSG="字数 ${WORD_COUNT} 接近边界（${MIN_WORDS}-${MAX_WORDS}）"
fi

# ============================================================
# 2. 敏感词检查（🔴 硬违禁词）
# ============================================================

SENSITIVE_STATUS="PASS"
SENSITIVE_MSG="未发现硬违禁词"
SENSITIVE_HITS=""

if [[ "$SKIP_SENSITIVE" == "false" ]]; then
    # 提取全平台通用硬违禁词（引流类）
    COMMON_WORDS="微信|vx|wx|V信|薇信|威信|加我|私我|私聊|淘口令|最好|最佳|最优|最强|最大|最先进|最低价|唯一|独一无二|100%|绝对|保证|零风险|第一|全网第一|No.1|根治|治愈|药到病除|特效|祖传秘方|月瘦|躺瘦|稳赚不赔|保本保息|日入过万|躺赚"

    # 平台特有硬违禁词
    case "$PLATFORM" in
        xhs)
            PLATFORM_WORDS="链接在|评论区有链接|暴富|日入|月入|年入|信用卡套现"
            ;;
        wechat)
            PLATFORM_WORDS="转发领红包|分享抽奖|不转不是中国人|帮我砍一刀|帮我助力"
            ;;
        douyin)
            PLATFORM_WORDS="赚钱|搞钱"
            ;;
        bilibili)
            PLATFORM_WORDS=""
            ;;
    esac

    ALL_WORDS="$COMMON_WORDS"
    if [[ -n "${PLATFORM_WORDS:-}" ]]; then
        ALL_WORDS="${ALL_WORDS}|${PLATFORM_WORDS}"
    fi

    # 执行检查
    SENSITIVE_HITS=$(echo "$CONTENT" | grep -oE "$ALL_WORDS" 2>/dev/null | sort | uniq -c | sort -rn || true)

    if [[ -n "$SENSITIVE_HITS" ]]; then
        HIT_COUNT=$(echo "$SENSITIVE_HITS" | wc -l | tr -d ' ')
        SENSITIVE_STATUS="FAIL"
        SENSITIVE_MSG="发现 ${HIT_COUNT} 类硬违禁词"
    fi
fi

# ============================================================
# 3. Emoji 密度检查（主要针对小红书）
# ============================================================

EMOJI_STATUS="PASS"
EMOJI_MSG=""

# 统计 emoji 数量（匹配常见 emoji Unicode 范围）
EMOJI_COUNT=$(echo "$CONTENT" | grep -oP '[\x{1F300}-\x{1F9FF}\x{2600}-\x{27BF}\x{FE00}-\x{FE0F}\x{1FA00}-\x{1FA9F}]' 2>/dev/null | wc -l || echo "0")

case "$PLATFORM" in
    xhs)
        if (( EMOJI_COUNT < 5 )); then
            EMOJI_STATUS="FAIL"
            EMOJI_MSG="Emoji ${EMOJI_COUNT} 个，小红书要求至少 5 个"
        elif (( EMOJI_COUNT > 20 )); then
            EMOJI_STATUS="WARNING"
            EMOJI_MSG="Emoji ${EMOJI_COUNT} 个，超过 20 个可能过多"
        else
            EMOJI_MSG="Emoji ${EMOJI_COUNT} 个（推荐 5-20）"
        fi
        ;;
    wechat)
        if (( EMOJI_COUNT > 10 )); then
            EMOJI_STATUS="WARNING"
            EMOJI_MSG="Emoji ${EMOJI_COUNT} 个，公众号建议少用 emoji"
        else
            EMOJI_MSG="Emoji ${EMOJI_COUNT} 个（公众号适度即可）"
        fi
        ;;
    douyin)
        EMOJI_MSG="Emoji ${EMOJI_COUNT} 个（抖音脚本不强制要求）"
        ;;
    bilibili)
        EMOJI_MSG="Emoji ${EMOJI_COUNT} 个（B站专栏适度即可）"
        ;;
esac

# ============================================================
# 4. 段落长度检查
# ============================================================

PARA_STATUS="PASS"
PARA_MSG=""

# 统计最长段落字数
LONGEST_PARA=$(echo "$CONTENT" | awk '
    /^$/ { if (len > max) max = len; len = 0; next }
    { len += length($0) }
    END { if (len > max) max = len; print max }
')

case "$PLATFORM" in
    xhs)
        if (( LONGEST_PARA > 200 )); then
            PARA_STATUS="WARNING"
            PARA_MSG="最长段落 ${LONGEST_PARA} 字符，小红书建议每段不超过 3 句"
        else
            PARA_MSG="最长段落 ${LONGEST_PARA} 字符（OK）"
        fi
        ;;
    wechat)
        if (( LONGEST_PARA > 800 )); then
            PARA_STATUS="WARNING"
            PARA_MSG="最长段落 ${LONGEST_PARA} 字符，建议适当分段"
        else
            PARA_MSG="最长段落 ${LONGEST_PARA} 字符（OK）"
        fi
        ;;
    douyin)
        PARA_MSG="最长段落 ${LONGEST_PARA} 字符"
        ;;
    bilibili)
        if (( LONGEST_PARA > 600 )); then
            PARA_STATUS="WARNING"
            PARA_MSG="最长段落 ${LONGEST_PARA} 字符，B站建议每段 3-5 句"
        else
            PARA_MSG="最长段落 ${LONGEST_PARA} 字符（OK）"
        fi
        ;;
esac

# ============================================================
# 综合结果
# ============================================================

# 确定总评
OVERALL="PASS"
if [[ "$WORD_STATUS" == "FAIL" || "$SENSITIVE_STATUS" == "FAIL" || "$EMOJI_STATUS" == "FAIL" ]]; then
    OVERALL="FAIL"
elif [[ "$WORD_STATUS" == "WARNING" || "$SENSITIVE_STATUS" == "WARNING" || "$EMOJI_STATUS" == "WARNING" || "$PARA_STATUS" == "WARNING" ]]; then
    OVERALL="WARNING"
fi

# 输出报告
echo "============================================"
echo " 内容合规检查报告"
echo " 平台: ${PLATFORM_NAME} (${PLATFORM})"
echo " 文件: ${FILE_PATH}"
echo "============================================"
echo ""
echo "总评: ${OVERALL}"
echo ""
echo "--- 逐项检查 ---"
echo ""
printf "%-12s %-10s %s\n" "[字数]" "$WORD_STATUS" "$WORD_MSG"
printf "%-12s %-10s %s\n" "[敏感词]" "$SENSITIVE_STATUS" "$SENSITIVE_MSG"
printf "%-12s %-10s %s\n" "[Emoji]" "$EMOJI_STATUS" "$EMOJI_MSG"
printf "%-12s %-10s %s\n" "[段落]" "$PARA_STATUS" "$PARA_MSG"

if [[ -n "$SENSITIVE_HITS" ]]; then
    echo ""
    echo "--- 🔴 命中的硬违禁词 ---"
    echo "$SENSITIVE_HITS"
fi

echo ""
echo "============================================"

# 退出码：0=PASS, 1=WARNING, 2=FAIL
case "$OVERALL" in
    PASS)    exit 0 ;;
    WARNING) exit 1 ;;
    FAIL)    exit 2 ;;
esac
