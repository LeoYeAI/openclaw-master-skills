#!/usr/bin/env bash
# sentinel-input.sh — Runtime input guard for OpenClaw agents
# Scans external content for prompt injection, data exfiltration, command injection,
# and social engineering BEFORE the agent processes it.
#
# Usage:
#   echo "untrusted content" | sentinel-input.sh [--json] [--strict] [--clean]
#
# Exit codes:
#   0 = clean
#   1 = threat detected (HIGH or CRITICAL)
#   2 = warning only (when not --strict)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load config
CONFIG_FILE="${HOME}/.sentinel/config.sh"
[[ -f "$CONFIG_FILE" ]] && source "$CONFIG_FILE"

# Defaults
SENTINEL_THRESHOLD="${SENTINEL_THRESHOLD:-HIGH}"
SENTINEL_LOG="${SENTINEL_LOG:-$HOME/.sentinel/threats.jsonl}"
SENTINEL_CHECK_INJECTION="${SENTINEL_CHECK_INJECTION:-true}"
SENTINEL_CHECK_EXFIL="${SENTINEL_CHECK_EXFIL:-true}"
SENTINEL_CHECK_COMMANDS="${SENTINEL_CHECK_COMMANDS:-true}"
SENTINEL_CHECK_SOCIAL_ENG="${SENTINEL_CHECK_SOCIAL_ENG:-true}"
SENTINEL_CRYPTO_PATTERNS="${SENTINEL_CRYPTO_PATTERNS:-true}"

# Parse args
JSON_MODE=false
STRICT_MODE=false
CLEAN_MODE=false
for arg in "$@"; do
  case "$arg" in
    --json)   JSON_MODE=true ;;
    --strict) STRICT_MODE=true ;;
    --clean)  CLEAN_MODE=true ;;
  esac
done

# Read stdin
INPUT=$(cat)

if [[ -z "$INPUT" ]]; then
  [[ "$JSON_MODE" == true ]] && echo '{"status":"clean","threats":[]}'
  exit 0
fi

# ============================================================
# PHASE 1: Normalize encoding
# ============================================================
NORMALIZED="$INPUT"

# Decode base64 chunks (catch encoded payloads)
while IFS= read -r b64chunk; do
  decoded=$(echo "$b64chunk" | base64 -d 2>/dev/null || true)
  if [[ -n "$decoded" ]]; then
    NORMALIZED="$NORMALIZED $decoded"
  fi
done < <(echo "$INPUT" | grep -oP '[A-Za-z0-9+/]{20,}={0,2}' || true)

# Strip zero-width characters (U+200B, U+200C, U+200D, U+FEFF, etc.)
NORMALIZED=$(echo "$NORMALIZED" | sed 's/\xe2\x80\x8b//g; s/\xe2\x80\x8c//g; s/\xe2\x80\x8d//g; s/\xef\xbb\xbf//g')

# Strip HTML/XML tags for content analysis
STRIPPED=$(echo "$NORMALIZED" | sed 's/<[^>]*>//g')
NORMALIZED="$NORMALIZED $STRIPPED"

# Create space-collapsed version (catches "i g n o r e" -> "ignore")
# Remove spaces between single characters
COLLAPSED=$(echo "$NORMALIZED" | sed -E 's/\b([a-zA-Z]) ([a-zA-Z]) ([a-zA-Z]) ([a-zA-Z])/\1\2\3\4/g; s/\b([a-zA-Z]) ([a-zA-Z]) ([a-zA-Z])/\1\2\3/g; s/\b([a-zA-Z]) ([a-zA-Z])\b/\1\2/g')
# Brute force: also try just stripping all single-letter-space patterns
COLLAPSED2=$(echo "$NORMALIZED" | sed 's/\([a-zA-Z]\) \([a-zA-Z]\) /\1\2/g' | sed 's/\([a-zA-Z]\) \([a-zA-Z]\)$/\1\2/')
NORMALIZED="$NORMALIZED $COLLAPSED $COLLAPSED2"

# Leet speak normalization (1->i, 0->o, 3->e, 4->a, 5->s, 7->t, @->a)
DELEET=$(echo "$NORMALIZED" | sed 's/1/i/g; s/0/o/g; s/3/e/g; s/4/a/g; s/5/s/g; s/7/t/g; s/@/a/g')
NORMALIZED="$NORMALIZED $DELEET"

# Lowercase for pattern matching
LOWER=$(echo "$NORMALIZED" | tr '[:upper:]' '[:lower:]')

# ============================================================
# PHASE 2: Pattern matching
# ============================================================
THREATS=()
SEVERITY="CLEAN"
CATEGORIES=()

update_severity() {
  local new="$1"
  case "$SEVERITY" in
    CLEAN)   SEVERITY="$new" ;;
    WARNING) [[ "$new" == "HIGH" || "$new" == "CRITICAL" ]] && SEVERITY="$new" ;;
    HIGH)    [[ "$new" == "CRITICAL" ]] && SEVERITY="$new" ;;
  esac
}

# --- PROMPT INJECTION (EN) ---
if [[ "$SENTINEL_CHECK_INJECTION" == true ]]; then
  INJECTION_PATTERNS=(
    "ignore (all |your )?previous (instructions|context|rules|directives)"
    "ignore (all |your )?prior (instructions|context|rules)"
    "disregard (all |your )?(previous|prior|above) (instructions|rules|context)"
    "forget (all |your )?(previous|prior|earlier) (instructions|context|rules)"
    "you are now (in )?(developer|debug|admin|god|unrestricted|jailbreak) mode"
    "you are (now )?dan"
    "act as (an )?unrestricted"
    "override (all )?safety"
    "bypass (all )?(safety|security|content|moderation)"
    "enter (developer|debug|admin|maintenance) mode"
    "system prompt (is|says|contains|override)"
    "reveal (your|the) (system|original|initial) (prompt|instructions)"
    "repeat (your|the) (system|original) (prompt|instructions)"
    "print (your|the) (system|original) (prompt|instructions)"
    "what (is|are) your (system |original |initial )?(prompt|instructions|rules)"
    "security warnings are test artifacts"
    "this is a test environment"
    "i am (your |the )?(developer|creator|admin|administrator|owner)"
    "new (instructions|rules|directives) (override|replace|supersede)"
    "from now on,? (you |your )?(will|must|should|are)"
    "pretend (you are|to be|that you)"
    "role.?play as"
    "simulation mode"
    "hypothetically,? (if you |you )?(were|could|had no)"
  )

  for pattern in "${INJECTION_PATTERNS[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("prompt_injection_en: matched '$pattern'")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done

  # --- PROMPT INJECTION (RU) ---
  RU_PATTERNS=(
    "игнорируй (все )?(предыдущие|прежние) (инструкции|указания|правила)"
    "забудь (все )?(предыдущие|прежние) (инструкции|указания)"
    "ты теперь (работаешь )?(без ограничений|в режиме разработчика|в режиме администратора)"
    "теперь работаешь без ограничений"
    "теперь без ограничений"
    "отмени (все )?(предыдущие|прежние) (правила|ограничения)"
    "покажи (свой|свои|системный) (промпт|инструкции)"
    "покажи мне свои инструкции"
    "повтори (свой|свои|системный) (промпт|инструкции)"
    "обойди (все )?(ограничения|защиту|безопасность)"
    "новые (инструкции|правила) (заменяют|отменяют)"
    "я (твой |являюсь )?(разработчик|создатель|администратор|владелец)"
    "я твой разработчик"
    "режим (разработчика|администратора|отладки|тестирования)"
    "притворись,? что ты"
  )

  for pattern in "${RU_PATTERNS[@]}"; do
    if echo "$NORMALIZED" | LC_ALL=en_US.UTF-8 grep -qP "$pattern"; then
      THREATS+=("prompt_injection_ru: matched '$pattern'")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done

  # --- PROMPT INJECTION (ZH) ---
  ZH_PATTERNS=(
    "忽略(之前|以前|先前)的(指令|指示|规则|说明)"
    "你现在是(开发者|管理员|调试|无限制)模式"
    "无视(之前|以前)的(规则|限制|指令)"
    "绕过(安全|内容|审核)(限制|过滤|检查)"
    "显示(你的|系统)(提示|指令|提示词)"
    "重复(你的|系统)(提示|指令|提示词)"
  )

  for pattern in "${ZH_PATTERNS[@]}"; do
    if echo "$NORMALIZED" | grep -qP "$pattern"; then
      THREATS+=("prompt_injection_zh: matched")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done

  # --- PROMPT INJECTION (ES) ---
  ES_PATTERNS=(
    "ignora (todas |las )?(instrucciones|reglas|directivas) (anteriores|previas)"
    "olvida (todas )?(las )?(instrucciones|reglas) (anteriores|previas)"
    "ahora (eres|estás en) (modo )?(desarrollador|administrador|sin restricciones)"
    "muestra (tu|el) (prompt|instrucciones) del sistema"
  )

  for pattern in "${ES_PATTERNS[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("prompt_injection_es: matched")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done

  # --- PROMPT INJECTION (AR) ---
  AR_PATTERNS=(
    "تجاهل (جميع |كل )?التعليمات السابقة"
    "أنت الآن في وضع المطور"
    "اعرض تعليمات النظام"
    "تخطى (قيود|حماية) الأمان"
  )

  for pattern in "${AR_PATTERNS[@]}"; do
    if echo "$NORMALIZED" | grep -qP "$pattern"; then
      THREATS+=("prompt_injection_ar: matched")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done
fi

# --- DATA EXFILTRATION ---
if [[ "$SENTINEL_CHECK_EXFIL" == true ]]; then
  EXFIL_PATTERNS=(
    "webhook\.site"
    "requestbin\.(com|net)"
    "ngrok\.(io|app)"
    "burpcollaborator\.net"
    "interact\.sh"
    "oastify\.com"
    "canarytokens\.com"
    "pipedream\.net"
    "hookbin\.com"
    "169\.254\.169\.254"
    "metadata\.google\.internal"
    "100\.100\.100\.200"
    "fd00:ec2::254"
    "curl [^|]*\| ?(bash|sh|zsh|source)"
    "wget [^&]*&& ?(bash|sh|chmod)"
    "fetch\(['\"][^'\"]*\.(sh|py|rb|pl)"
  )

  for pattern in "${EXFIL_PATTERNS[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("data_exfil: matched '$pattern'")
      CATEGORIES+=("data_exfil")
      update_severity "CRITICAL"
    fi
  done
fi

# --- COMMAND INJECTION ---
if [[ "$SENTINEL_CHECK_COMMANDS" == true ]]; then
  CMD_PATTERNS=(
    "rm -rf [/~]"
    "chmod (777|666|u\+s)"
    "mkfs\."
    "dd if=/dev/(zero|random|urandom) of=/"
    ":(){ :\|:& };:"
    "\beval\b.*\\\$"
    "python[23]? -c ['\"].*exec"
    "base64 -d.*\| ?(bash|sh|python|perl|ruby)"
    "echo [A-Za-z0-9+/]*= *\| *base64 -d"
    "curl.*-o.*/tmp/.*&&.*chmod"
    "wget.*-O.*/tmp/.*&&.*chmod"
    "\bsudo\b.*\b(rm|chmod|chown|mv|dd|mkfs)\b"
    "nc -[elp]"
    "/dev/tcp/"
    "bash -i >& /dev/tcp/"
    "reverse.?shell"
  )

  for pattern in "${CMD_PATTERNS[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("command_injection: matched '$pattern'")
      CATEGORIES+=("command_injection")
      update_severity "CRITICAL"
    fi
  done
fi

# --- SOCIAL ENGINEERING ---
if [[ "$SENTINEL_CHECK_SOCIAL_ENG" == true ]]; then
  SE_PATTERNS=(
    "please (run|execute|install|type|enter|paste|copy).*\b(curl|wget|pip|npm|brew|apt|yum|bash|sh|python)\b"
    "run (this|the following) (command|script|installer)"
    "install (this|the) (dependency|prerequisite|required|package)"
    "update your (config|configuration|settings) by running"
    "execute (this|the following) (in |on )?(your )?(terminal|shell|command ?line)"
    "disable (your )?(firewall|antivirus|security|defender)"
    "add (this|the following) to your (\.bashrc|\.zshrc|\.profile|crontab)"
    "share (your|the) (api key|token|password|credentials|secret)"
    "send (me|us) your (api key|token|password|credentials)"
    "i (just )?need your (api.?key|token|password|credentials|private.?key|secret|seed.?phrase)"
    "for (verification|debugging|testing|troubleshooting).*(share|send|provide|paste) (your )?(api.?key|token|password|credentials)"
    "(urgently|immediately|quickly|asap|right now) (run|execute|install|download)"
    "(your|the) (account|system|agent) (has been|is|was) (compromised|hacked|breached).*run"
    "scan this qr code"
    "(don't|do not) (tell|show|share|mention).*(to )?(anyone|others|your (team|admin|manager))"
    "(keep|this is) (this )?(between us|a secret|confidential)"
    "override code.*share (the |your )?(contents|env|config|key)"
  )

  for pattern in "${SE_PATTERNS[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("social_engineering: matched '$pattern'")
      CATEGORIES+=("social_engineering")
      update_severity "HIGH"
    fi
  done
fi

# --- EXTENDED INJECTION PATTERNS (catches evasion techniques) ---
if [[ "$SENTINEL_CHECK_INJECTION" == true ]]; then
  EXT_INJECTION=(
    "summarize your (system )?prompt"
    "translate your (system )?(prompt|instructions) (into|to)"
    "encode your (system )?(prompt|instructions) (in|to|as) (base64|hex|json)"
    "\[system\]"
    "\[admin\]"
    "\[developer\]"
    "###\s*(system|admin|developer)\s*(override|message|instruction)"
    "begin new (system )?prompt"
    "end of (system )?prompt.*begin"
    "end of (previous )?prompt\\.? new (system )?instructions"
    "new (instructions|rules) override"
    "new system instructions:? (disregard|ignore|forget|bypass|override)"
    "step 1:? (forget|ignore|disregard).*step [23]"
    "i am (an? )?(openai|anthropic|google|meta) (employee|engineer|researcher)"
    "(authorized|approved) (by|from) (openai|anthropic|google|admin)"
    "(safety|content|moderation) (filter|check|system) (disabled|off|bypassed)"
    "(error|warning):?.*(safety|security) (module|system|filter) (offline|disabled|failed)"
    "maintenance mode (activated|enabled|on)"
    "whatever you do,? do not (show|reveal|display|output)"
    "i really need this.*(can you|please).*(just this once|exception).*(ignore|bypass)"
    "for (my |the )?(thesis|research|homework|paper).*(ignore|bypass|skip)"
    "new role:? (unrestricted|unfiltered|unlimited|free|no rules)"
    "override previous instructions"
    "disregard (all )?safety filters"
  )

  for pattern in "${EXT_INJECTION[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("prompt_injection_advanced: matched '$pattern'")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done

  # Extended RU patterns
  EXT_RU=(
    "в целях тестирования.*(покажи|выведи|напиши)"
    "пожалуйста.*(покажи|выведи).*(системн|инструкци|промпт)"
  )
  for pattern in "${EXT_RU[@]}"; do
    if echo "$NORMALIZED" | LC_ALL=en_US.UTF-8 grep -qP "$pattern" 2>/dev/null; then
      THREATS+=("prompt_injection_ru_ext: matched")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done

  # Extended ZH
  EXT_ZH=(
    "假设你没有.*限制.*显示"
    "请假设"
  )
  for pattern in "${EXT_ZH[@]}"; do
    if echo "$NORMALIZED" | LC_ALL=en_US.UTF-8 grep -qP "$pattern" 2>/dev/null; then
      THREATS+=("prompt_injection_zh_ext: matched")
      CATEGORIES+=("prompt_injection")
      update_severity "CRITICAL"
    fi
  done
fi

# --- EXTENDED EXFILTRATION ---
if [[ "$SENTINEL_CHECK_EXFIL" == true ]]; then
  EXT_EXFIL=(
    "dnslog\.(com|io|net)"
    "dnsbin\.(com|io|net)"
    "<img[^>]*src=['\"]https?://[^'\"]*\.(com|io|net)/[^'\"]*['\"]"
    "https?://[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}(:[0-9]+)?/(collect|hook|log|receive|data|exfil|steal)"
    "pastebin\.com"
    "localhost(:[0-9]+)?/(admin|config|env|debug|internal)"
    "192\.168\.[0-9]"
    "10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]"
  )

  for pattern in "${EXT_EXFIL[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("data_exfil_ext: matched '$pattern'")
      CATEGORIES+=("data_exfil")
      update_severity "HIGH"
    fi
  done
fi

# --- EXTENDED COMMAND INJECTION ---
if [[ "$SENTINEL_CHECK_COMMANDS" == true ]]; then
  EXT_CMD=(
    ":\(\)\{ :\|:& \};:"
    "python[23]? -c ['\"].*import (os|subprocess|socket)"
    "node -e ['\"].*child_process"
    "perl -e ['\"].*system"
    "echo .* >> ~/\.ssh/authorized_keys"
    "curl -d .*\\\$\(env\)"
    "curl -d .*\\\$\(cat "
  )

  for pattern in "${EXT_CMD[@]}"; do
    if echo "$LOWER" | grep -qPi "$pattern"; then
      THREATS+=("command_injection_ext: matched '$pattern'")
      CATEGORIES+=("command_injection")
      update_severity "CRITICAL"
    fi
  done
fi

# ============================================================
# PHASE 2.5: Premium patterns check (if installed)
# ============================================================
PREMIUM_CHECK="$SCRIPT_DIR/sentinel-premium-check.sh"
if [[ -x "$PREMIUM_CHECK" ]]; then
  PREMIUM_RESULT=$(echo "$INPUT" | bash "$PREMIUM_CHECK" input 2>/dev/null || true)
  if echo "$PREMIUM_RESULT" | grep -q '"threat_count"'; then
    P_COUNT=$(echo "$PREMIUM_RESULT" | grep -oP '"threat_count":\K[0-9]+' || echo 0)
    P_SEV=$(echo "$PREMIUM_RESULT" | grep -oP '"severity":"\K[^"]+' || echo "")
    P_THREATS=$(echo "$PREMIUM_RESULT" | grep -oP '"threats":\[\K[^\]]+' || echo "")
    if [[ $P_COUNT -gt 0 ]]; then
      # Parse premium threat categories
      while IFS= read -r pt; do
        pt_clean=$(echo "$pt" | tr -d '"')
        [[ -n "$pt_clean" ]] && THREATS+=("premium:$pt_clean") && CATEGORIES+=("$pt_clean")
      done < <(echo "$P_THREATS" | tr ',' '\n')
      [[ -n "$P_SEV" ]] && update_severity "$P_SEV"
    fi
  fi
fi

# ============================================================
# PHASE 3: Output results
# ============================================================

# Deduplicate categories
UNIQUE_CATS=($(printf '%s\n' "${CATEGORIES[@]}" 2>/dev/null | sort -u || true))
CAT_STRING=$(IFS='+'; echo "${UNIQUE_CATS[*]}" 2>/dev/null || echo "none")
THREAT_COUNT=${#THREATS[@]}

# Log threats
if [[ $THREAT_COUNT -gt 0 ]]; then
  mkdir -p "$(dirname "$SENTINEL_LOG")"
  SNIPPET=$(echo "$INPUT" | head -c 200 | tr '\n' ' ')
  LOG_ENTRY=$(cat <<EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","direction":"input","severity":"$SEVERITY","categories":"$CAT_STRING","threat_count":$THREAT_COUNT,"snippet":"$(echo "$SNIPPET" | sed 's/"/\\"/g')","action":"$(if [[ "$CLEAN_MODE" == true ]]; then echo "sanitized"; else echo "blocked"; fi)"}
EOF
)
  echo "$LOG_ENTRY" >> "$SENTINEL_LOG" 2>/dev/null || true
fi

# Output
if [[ "$JSON_MODE" == true ]]; then
  if [[ $THREAT_COUNT -eq 0 ]]; then
    echo '{"status":"clean","severity":"CLEAN","threats":[]}'
    exit 0
  else
    THREATS_JSON="["
    for i in "${!THREATS[@]}"; do
      [[ $i -gt 0 ]] && THREATS_JSON+=","
      THREATS_JSON+="\"$(echo "${THREATS[$i]}" | sed 's/"/\\"/g')\""
    done
    THREATS_JSON+="]"
    echo "{\"status\":\"threat\",\"severity\":\"$SEVERITY\",\"categories\":\"$CAT_STRING\",\"threat_count\":$THREAT_COUNT,\"threats\":$THREATS_JSON}"
    exit 1
  fi
fi

if [[ $THREAT_COUNT -eq 0 ]]; then
  if [[ "$CLEAN_MODE" == true ]]; then
    echo "$INPUT"
  else
    echo "✅ Clean — no threats detected"
  fi
  exit 0
fi

# Severity emoji
case "$SEVERITY" in
  CRITICAL) EMOJI="🔴" ;;
  HIGH)     EMOJI="🟠" ;;
  WARNING)  EMOJI="🟡" ;;
  *)        EMOJI="⚪" ;;
esac

echo "$EMOJI $SEVERITY [$CAT_STRING]: $THREAT_COUNT threat(s) detected"
echo ""
for threat in "${THREATS[@]}"; do
  echo "  → $threat"
done
echo ""
echo "⚠️  Do NOT process this content. Review manually."

if [[ "$CLEAN_MODE" == true ]]; then
  echo ""
  echo "--- SANITIZED OUTPUT (threats stripped) ---"
  CLEANED="$INPUT"
  for pattern in "${INJECTION_PATTERNS[@]}" "${EXFIL_PATTERNS[@]}" "${CMD_PATTERNS[@]}" "${SE_PATTERNS[@]}"; do
    CLEANED=$(echo "$CLEANED" | sed -E "s/$pattern/[REDACTED]/gI" 2>/dev/null || echo "$CLEANED")
  done
  echo "$CLEANED"
fi

# Exit code based on severity
case "$SEVERITY" in
  CRITICAL|HIGH) exit 1 ;;
  WARNING)
    if [[ "$STRICT_MODE" == true ]]; then
      exit 1
    else
      exit 2
    fi
    ;;
  *) exit 0 ;;
esac
