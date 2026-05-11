#!/usr/bin/env bash
set -euo pipefail

# ============================================
# Labnana Image Generation Script
# API: https://docs.marswave.ai/openapi-labnana.html
# Platform: macOS, Linux, Windows (Git Bash/WSL)
# ============================================

PROMPT=""
SIZE="2K"
RATIO="16:9"
REFERENCE_IMAGES=""

if [ $# -gt 0 ] && [[ "$1" != --* ]]; then
  PROMPT="${1:-}"
  SIZE="${2:-2K}"
  RATIO="${3:-16:9}"
  REFERENCE_IMAGES="${4:-}"
else
  while [ $# -gt 0 ]; do
    case "$1" in
      --prompt)
        PROMPT="${2:-}"
        shift 2
        ;;
      --size)
        SIZE="${2:-2K}"
        shift 2
        ;;
      --ratio)
        RATIO="${2:-16:9}"
        shift 2
        ;;
      --reference-images)
        REFERENCE_IMAGES="${2:-}"
        shift 2
        ;;
      --help)
        echo "Usage: $0 \"<prompt>\" [size] [ratio] [reference_images]" >&2
        echo "  size: 1K | 2K | 4K (default: 2K)" >&2
        echo "  ratio: 16:9 | 1:1 | 9:16 | 2:3 | 3:2 | 3:4 | 4:3 | 21:9 (default: 16:9)" >&2
        echo "  reference_images: comma-separated URLs (max 14), e.g. \"url1,url2\"" >&2
        exit 0
        ;;
      *)
        echo "Error: Unknown argument $1" >&2
        exit 1
        ;;
    esac
  done
fi

# Configuration
API_ENDPOINT="https://api.labnana.com/openapi/v1/images/generation"
AGENT_SKILLS_CLIENT_ID="PJBkELS1o_q9nJ~NzF2_Fmr21TNX&~eoJR49FFdFhD3U"
MAX_RETRIES=3
INITIAL_TIMEOUT=600
RETRY_DELAY=5

# Temp file tracking for interrupt cleanup
TEMP_OUTPUT_FILE=""

# ============================================
# Platform detection
# ============================================

detect_platform() {
  case "$(uname -s)" in
    Darwin*)  echo "macos" ;;
    Linux*)   echo "linux" ;;
    CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
    *)        echo "unknown" ;;
  esac
}

PLATFORM=$(detect_platform)

# ============================================
# Interrupt cleanup
# ============================================

cleanup() {
  if [ -n "$TEMP_OUTPUT_FILE" ] && [ -f "$TEMP_OUTPUT_FILE" ]; then
    rm -f "$TEMP_OUTPUT_FILE"
  fi
}

trap cleanup EXIT INT TERM

# ============================================
# Cross-platform utility functions
# ============================================

# Cross-platform sed -i (macOS and Linux syntax differs)
sed_inplace() {
  local file="$1"
  local pattern="$2"

  if [ "$PLATFORM" = "macos" ]; then
    sed -i '' "$pattern" "$file"
  else
    sed -i "$pattern" "$file"
  fi
}

# Cross-platform base64 decode
base64_decode() {
  local input="$1"
  local output="$2"

  # Try different base64 decode methods
  if echo "$input" | base64 -d > "$output" 2>/dev/null; then
    return 0
  elif echo "$input" | base64 -D > "$output" 2>/dev/null; then
    # macOS old version uses -D
    return 0
  elif echo "$input" | base64 --decode > "$output" 2>/dev/null; then
    # Some systems use --decode
    return 0
  elif command -v openssl &>/dev/null; then
    # Fallback: use openssl
    echo "$input" | openssl base64 -d > "$output" 2>/dev/null
    return $?
  else
    return 1
  fi
}

# Cross-platform curl finder
find_curl() {
  # Try different paths by priority
  local curl_paths=(
    "/usr/bin/curl"           # macOS, Linux standard path
    "/bin/curl"               # Some Linux distributions
    "/usr/local/bin/curl"     # Homebrew (macOS)
    "/mingw64/bin/curl"       # Git Bash (Windows)
    "/c/Windows/System32/curl.exe"  # Windows built-in curl
  )

  for path in "${curl_paths[@]}"; do
    if [ -x "$path" ]; then
      echo "$path"
      return 0
    fi
  done

  # Finally try curl in PATH
  if command -v curl &>/dev/null; then
    command -v curl
    return 0
  fi

  return 1
}

# Cross-platform shell config file getter
get_shell_rc() {
  local rc_files=()

  case "$PLATFORM" in
    macos)
      # macOS defaults to zsh, but may use bash
      rc_files=(~/.zshrc ~/.bash_profile ~/.bashrc ~/.profile)
      ;;
    linux)
      # Linux typically uses bashrc
      rc_files=(~/.bashrc ~/.zshrc ~/.profile)
      ;;
    windows)
      # Git Bash uses bashrc
      rc_files=(~/.bashrc ~/.bash_profile ~/.profile)
      ;;
    *)
      rc_files=(~/.bashrc ~/.zshrc ~/.profile)
      ;;
  esac

  # Return first existing file, or first as default
  for rc in "${rc_files[@]}"; do
    if [ -f "$rc" ]; then
      echo "$rc"
      return 0
    fi
  done

  # If none exist, return platform default
  case "$PLATFORM" in
    macos)  echo ~/.zshrc ;;
    *)      echo ~/.bashrc ;;
  esac
}

# Generate random number (compatible with environments without $RANDOM)
get_random() {
  if [ -n "${RANDOM:-}" ]; then
    echo $((RANDOM % 10000))
  elif [ -f /dev/urandom ]; then
    od -An -tu2 -N2 /dev/urandom | tr -d ' '
  else
    # Last fallback: use part of timestamp
    date +%N 2>/dev/null | cut -c1-4 || echo "0000"
  fi
}

# ============================================
# Environment variable loading (supports multiple formats)
# ============================================

load_env_var() {
  local var_name="$1"
  local rc_file
  local line
  local value=""

  for rc_file in ~/.zshrc ~/.bashrc ~/.bash_profile ~/.profile; do
    if [ -f "$rc_file" ]; then
      # Find export VAR=... lines (supports =, =", =' formats)
      line=$(grep -E "^export ${var_name}=" "$rc_file" 2>/dev/null | tail -1) || true
      if [ -n "$line" ]; then
        # Extract part after equals sign
        value="${line#*=}"
        # Remove leading/trailing quotes (double or single)
        value="${value#\"}"
        value="${value%\"}"
        value="${value#\'}"
        value="${value%\'}"
        # Expand $HOME and ~
        value="${value/\$HOME/$HOME}"
        value="${value/#\~/$HOME}"
        if [ -n "$value" ]; then
          export "$var_name"="$value"
          return 0
        fi
      fi
    fi
  done
  return 1
}

[ -z "${LISTENHUB_API_KEY:-}" ] && load_env_var "LISTENHUB_API_KEY" || true
[ -z "${LISTENHUB_OUTPUT_DIR:-}" ] && load_env_var "LISTENHUB_OUTPUT_DIR" || true

# ============================================
# Dependency check and installation guide
# ============================================

check_dependencies() {
  local missing_deps=()
  local install_cmd=""

  # Check jq
  if ! command -v jq &>/dev/null; then
    missing_deps+=("jq")
  fi

  # Check curl
  if ! find_curl &>/dev/null; then
    missing_deps+=("curl")
  fi

  # If missing dependencies, auto-install
  if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "→ Missing required tools: ${missing_deps[*]}" >&2
    echo "  Auto-installing..." >&2
    echo "" >&2

    case "$PLATFORM" in
      macos)
        install_cmd="brew install ${missing_deps[*]}"
        if ! command -v brew &>/dev/null; then
          echo "Error: Homebrew not detected" >&2
          echo "  Please install Homebrew first: https://brew.sh" >&2
          echo "  Or install manually: ${missing_deps[*]}" >&2
          exit 1
        fi
        ;;
      linux)
        # Detect Linux distribution
        if command -v apt-get &>/dev/null; then
          install_cmd="sudo apt-get update && sudo apt-get install -y ${missing_deps[*]}"
        elif command -v yum &>/dev/null; then
          install_cmd="sudo yum install -y ${missing_deps[*]}"
        elif command -v dnf &>/dev/null; then
          install_cmd="sudo dnf install -y ${missing_deps[*]}"
        elif command -v pacman &>/dev/null; then
          install_cmd="sudo pacman -S --noconfirm ${missing_deps[*]}"
        else
          echo "Error: No supported package manager detected" >&2
          echo "  Please install manually: ${missing_deps[*]}" >&2
          exit 1
        fi
        ;;
      windows)
        if command -v choco &>/dev/null; then
          install_cmd="choco install -y ${missing_deps[*]}"
        elif command -v scoop &>/dev/null; then
          install_cmd="scoop install ${missing_deps[*]}"
        else
          echo "Error: Chocolatey or Scoop not detected" >&2
          echo "  Please install a package manager first:" >&2
          echo "  - Chocolatey: https://chocolatey.org/install" >&2
          echo "  - Scoop: https://scoop.sh" >&2
          echo "  Or download manually: https://stedolan.github.io/jq/download/" >&2
          exit 1
        fi
        ;;
      *)
        echo "Error: Unsupported platform" >&2
        echo "  Please install manually: ${missing_deps[*]}" >&2
        exit 1
        ;;
    esac

    # Execute installation
    if eval "$install_cmd"; then
      echo "" >&2
      echo "✓ Dependencies installed successfully" >&2
      echo "" >&2
    else
      echo "" >&2
      echo "Error: Auto-installation failed" >&2
      echo "  Please run manually: $install_cmd" >&2
      exit 1
    fi
  fi
}

# ============================================
# First-time configuration check
# ============================================

setup_config() {
  local shell_rc
  shell_rc=$(get_shell_rc)

  echo "→ Welcome to Labnana image generation! Configuration needed." >&2
  echo "  Detected platform: $PLATFORM" >&2
  echo "" >&2

  # Check dependencies first
  check_dependencies

  # Configure API Key
  if [ -z "${LISTENHUB_API_KEY:-}" ]; then
    echo "1. API Key" >&2
    echo "   Visit https://listenhub.ai/settings/api-keys" >&2
    echo "   (Requires subscription)" >&2
    echo "" >&2
    echo -n "   Please paste your API key: " >&2
    read -r api_key

    if [ -z "$api_key" ]; then
      echo "Error: API key cannot be empty" >&2
      exit 1
    fi

    # Check if config already exists (avoid duplicate append)
    if ! grep -q "^export LISTENHUB_API_KEY=" "$shell_rc" 2>/dev/null; then
      echo "export LISTENHUB_API_KEY=\"$api_key\"" >> "$shell_rc"
    else
      # If exists, replace
      sed_inplace "$shell_rc" "s|^export LISTENHUB_API_KEY=.*|export LISTENHUB_API_KEY=\"$api_key\"|"
    fi
    export LISTENHUB_API_KEY="$api_key"
    echo "" >&2
  fi

  # Configure output path
  if [ -z "${LISTENHUB_OUTPUT_DIR:-}" ]; then
    echo "2. Output path" >&2
    echo -n "   Image save location (default: ~/Downloads): " >&2
    read -r output_dir

    # Default to ~/Downloads
    if [ -z "$output_dir" ]; then
      output_dir="$HOME/Downloads"
    fi

    # Expand ~ symbol
    output_dir="${output_dir/#\~/$HOME}"

    # Create directory if not exists
    mkdir -p "$output_dir"

    # Check if config already exists (avoid duplicate append)
    if ! grep -q "^export LISTENHUB_OUTPUT_DIR=" "$shell_rc" 2>/dev/null; then
      echo "export LISTENHUB_OUTPUT_DIR=\"$output_dir\"" >> "$shell_rc"
    else
      sed_inplace "$shell_rc" "s|^export LISTENHUB_OUTPUT_DIR=.*|export LISTENHUB_OUTPUT_DIR=\"$output_dir\"|"
    fi
    export LISTENHUB_OUTPUT_DIR="$output_dir"
    echo "" >&2
  fi

  echo "✓ Configuration saved to $shell_rc" >&2
  echo "" >&2
}

# Check and execute first-time configuration
  if [ -z "${LISTENHUB_API_KEY:-}" ] || [ -z "${LISTENHUB_OUTPUT_DIR:-}" ]; then
  setup_config
fi

# ============================================
# Parameter validation
# ============================================

if [ -z "$PROMPT" ]; then
  echo "Usage: $0 --prompt \"<prompt>\" [--size 1K|2K|4K] [--ratio 16:9|1:1|9:16|2:3|3:2|3:4|4:3|21:9] [--reference-images \"url1,url2\"]" >&2
  echo "  size: 1K | 2K | 4K (default: 2K)" >&2
  echo "  ratio: 16:9 | 1:1 | 9:16 | 2:3 | 3:2 | 3:4 | 4:3 | 21:9 (default: 16:9)" >&2
  echo "  reference-images: comma-separated URLs (max 14), e.g. \"url1,url2\"" >&2
  echo "" >&2
  echo "Examples:" >&2
  echo "  $0 --prompt \"a cute cat\" --size 2K --ratio 1:1" >&2
  echo "  $0 --prompt \"cyberpunk city at night\" --size 4K --ratio 16:9" >&2
  echo "  $0 --prompt \"similar style\" --size 2K --ratio 16:9 --reference-images \"https://example.com/ref1.jpg,https://example.com/ref2.png\"" >&2
  echo "" >&2
  echo "Legacy positional form is still supported:" >&2
  echo "  $0 \"a cute cat\" 2K 1:1" >&2
  exit 1
fi

# Validate size parameter
case "$SIZE" in
  1K|2K|4K) ;;
  *) echo "Error: size must be 1K, 2K or 4K" >&2; exit 1 ;;
esac

# Validate ratio parameter
case "$RATIO" in
  16:9|1:1|9:16|2:3|3:2|3:4|4:3|21:9) ;;
  *) echo "Error: ratio $RATIO not supported" >&2; exit 1 ;;
esac

# ============================================
# JSON construction (compatible with environments without jq)
# ============================================

# Infer MIME type from URL
detect_mime_type() {
  local url="$1"
  local ext="${url##*.}"
  ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')  # Convert to lowercase (bash 3.2 compatible)

  case "$ext" in
    jpg|jpeg) echo "image/jpeg" ;;
    png) echo "image/png" ;;
    gif) echo "image/gif" ;;
    webp) echo "image/webp" ;;
    bmp) echo "image/bmp" ;;
    *) echo "image/jpeg" ;;  # Default
  esac
}

# Build referenceImages JSON array
build_reference_images_json() {
  local urls="$1"
  local json_array="[]"

  if [ -z "$urls" ]; then
    echo "$json_array"
    return
  fi

  if command -v jq &> /dev/null; then
    # Use jq to build array
    local count=0
    json_array=$(echo "$urls" | tr ',' '\n' | while IFS= read -r url; do
      url=$(echo "$url" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')  # Trim whitespace (preserve special chars)
      if [ -n "$url" ]; then
        count=$((count + 1))
        if [ $count -gt 14 ]; then
          echo "Warning: Max 14 reference images supported, extras ignored" >&2
          break
        fi
        mime_type=$(detect_mime_type "$url")
        jq -n --arg uri "$url" --arg mime "$mime_type" \
          '{fileData: {fileUri: $uri, mimeType: $mime}}'
      fi
    done | jq -s '.')
  else
    # Manually build JSON array
    local items=()
    local count=0
    while IFS= read -r url; do
      url=$(echo "$url" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')  # Trim whitespace (preserve special chars)
      if [ -n "$url" ]; then
        count=$((count + 1))
        if [ $count -gt 14 ]; then
          echo "Warning: Max 14 reference images supported, extras ignored" >&2
          break
        fi
        mime_type=$(detect_mime_type "$url")
        # Escape special characters in URL
        local escaped_url="$url"
        escaped_url="${escaped_url//\\/\\\\}"
        escaped_url="${escaped_url//\"/\\\"}"
        items+=("{\"fileData\":{\"fileUri\":\"$escaped_url\",\"mimeType\":\"$mime_type\"}}")
      fi
    done < <(echo "$urls" | tr ',' '\n')

    if [ ${#items[@]} -gt 0 ]; then
      json_array="[$(IFS=,; echo "${items[*]}")]"
    fi
  fi

  echo "$json_array"
}

build_json_payload() {
  local prompt="$1"
  local size="$2"
  local ratio="$3"
  local ref_images="$4"

  if command -v jq &> /dev/null; then
    # When jq available, directly build complete JSON object (auto-handles all escaping)
    local ref_json
    ref_json=$(build_reference_images_json "$ref_images")

    jq -n \
      --arg prompt "$prompt" \
      --arg size "$size" \
      --arg ratio "$ratio" \
      --argjson refs "$ref_json" \
      'if ($refs | length) > 0 then
        {provider: "google", prompt: $prompt, imageConfig: {imageSize: $size, aspectRatio: $ratio}, referenceImages: $refs}
      else
        {provider: "google", prompt: $prompt, imageConfig: {imageSize: $size, aspectRatio: $ratio}}
      end'
  else
    # Without jq, manually escape JSON special characters
    local escaped_prompt="$prompt"
    # Escape in order: backslash must be first
    escaped_prompt="${escaped_prompt//\\/\\\\}"     # \ -> \\
    escaped_prompt="${escaped_prompt//\"/\\\"}"     # " -> \"
    escaped_prompt="${escaped_prompt//$'\n'/\\n}"   # newline -> \n
    escaped_prompt="${escaped_prompt//$'\r'/\\r}"   # carriage return -> \r
    escaped_prompt="${escaped_prompt//$'\t'/\\t}"   # Tab -> \t
    # Control characters (0x00-0x1F) except already handled \n\r\t, replace others with space
    escaped_prompt=$(printf '%s' "$escaped_prompt" | tr '\000-\010\013\014\016-\037' ' ')

    local base_json="{\"provider\":\"google\",\"prompt\":\"$escaped_prompt\",\"imageConfig\":{\"imageSize\":\"$size\",\"aspectRatio\":\"$ratio\"}"

    if [ -n "$ref_images" ]; then
      local ref_json
      ref_json=$(build_reference_images_json "$ref_images")
      echo "${base_json},\"referenceImages\":${ref_json}}"
    else
      echo "${base_json}}"
    fi
  fi
}

# ============================================
# API call (with retry and fallback)
# ============================================

call_api_with_retry() {
  local payload="$1"
  local attempt=1
  local timeout=$INITIAL_TIMEOUT
  local response=""
  local http_code=""
  local body=""
  local sleep_time=0

  # Find curl
  local curl_cmd
  curl_cmd=$(find_curl) || {
    echo "Error: curl command not found" >&2
    echo "  Please install curl: https://curl.se/download.html" >&2
    return 1
  }

  while [ $attempt -le $MAX_RETRIES ]; do
    echo "→ Generating... (attempt $attempt/$MAX_RETRIES, timeout ${timeout}s)" >&2

    response=$("$curl_cmd" -s -w "\n%{http_code}" -X POST \
      "$API_ENDPOINT" \
      -H "Authorization: Bearer $LISTENHUB_API_KEY" \
      -H "Content-Type: application/json" \
      -H "x-marswave-client-id: $AGENT_SKILLS_CLIENT_ID" \
      -d "$payload" \
      --max-time "$timeout" 2>&1) || true

    # Separate response body and status code
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    # Reset wait time
    sleep_time=$RETRY_DELAY

    # Handle various cases
    case "$http_code" in
      200)
        echo "$body"
        return 0
        ;;
      000)
        # Connection timeout or network error
        echo "  ⚠ Network timeout, retrying in ${sleep_time}s..." >&2
        ;;
      504|502|503)
        # Server timeout/gateway error
        echo "  ⚠ Service busy (HTTP $http_code), retrying in ${sleep_time}s..." >&2
        ;;
      429)
        # Rate limiting - wait longer
        sleep_time=$((RETRY_DELAY * 3))
        echo "  ⚠ Too many requests, retrying in ${sleep_time}s..." >&2
        ;;
      401)
        echo "Error: API Key invalid or expired" >&2
        echo "  Please check LISTENHUB_API_KEY or get a new one: https://listenhub.ai/settings/api-keys" >&2
        return 1
        ;;
      402)
        echo "Error: Insufficient credits" >&2
        echo "  Please recharge: https://labnana.com/pricing" >&2
        return 1
        ;;
      400)
        local error_msg
        error_msg=$(echo "$body" | grep -o '"message":"[^"]*"' | cut -d'"' -f4 2>/dev/null || echo "Request parameter error")
        echo "Error: $error_msg" >&2
        return 1
        ;;
      *)
        echo "  ⚠ Unknown error (HTTP $http_code), retrying in ${sleep_time}s..." >&2
        ;;
    esac

    # Wait before retry
    sleep $sleep_time
    attempt=$((attempt + 1))
    # Increment timeout (fallback strategy)
    timeout=$((timeout + 30))
  done

  echo "Error: Failed after multiple retries" >&2
  echo "  Last status: HTTP $http_code" >&2
  echo "  Suggestion: Try again later, or check network connection" >&2
  return 1
}

# ============================================
# Extract base64 image data
# ============================================

extract_image_data() {
  local body="$1"
  local base64_data=""

  if command -v jq &> /dev/null; then
    # When jq available, try multiple possible paths
    base64_data=$(echo "$body" | jq -r '
      .candidates[0].content.parts[0].inlineData.data //
      .candidates[0].content.parts[0].inline_data.data //
      .data //
      empty
    ' 2>/dev/null) || true
  else
    # Without jq, use grep to extract (base64 charset doesn't contain quotes, so this method is safe)
    base64_data=$(echo "$body" | grep -o '"data":"[^"]*"' | tail -1 | cut -d'"' -f4 2>/dev/null) || true
  fi

  if [ -z "$base64_data" ] || [ "$base64_data" = "null" ]; then
    return 1
  fi

  echo "$base64_data"
}

# ============================================
# Generate unique filename
# ============================================

generate_unique_filename() {
  local base_dir="$1"
  local prefix="$2"
  local ext="$3"
  local timestamp
  local random_suffix
  local filename

  # Timestamp accurate to seconds
  timestamp=$(date +%Y%m%d-%H%M%S)

  # Add 4-digit random to avoid same-second collision
  random_suffix=$(printf '%04d' "$(get_random)")

  filename="${base_dir}/${prefix}-${timestamp}-${random_suffix}.${ext}"

  # Extreme case: if file still exists, append more random
  while [ -f "$filename" ]; do
    random_suffix=$(printf '%04d' "$(get_random)")
    filename="${base_dir}/${prefix}-${timestamp}-${random_suffix}.${ext}"
  done

  echo "$filename"
}

# ============================================
# Main flow
# ============================================

# Ensure output directory exists
mkdir -p "$LISTENHUB_OUTPUT_DIR"

# Build request
PAYLOAD=$(build_json_payload "$PROMPT" "$SIZE" "$RATIO" "$REFERENCE_IMAGES")

# Call API (with retry)
BODY=$(call_api_with_retry "$PAYLOAD") || exit 1

# Extract image data
BASE64_DATA=$(extract_image_data "$BODY")
if [ -z "$BASE64_DATA" ]; then
  echo "Error: Cannot extract image data" >&2
  echo "  Response preview: $(echo "$BODY" | head -c 200)" >&2
  exit 1
fi

# Generate unique filename
OUTPUT_FILE=$(generate_unique_filename "$LISTENHUB_OUTPUT_DIR" "listenhub" "jpg")
TEMP_OUTPUT_FILE="$OUTPUT_FILE"  # Mark as temp file for trap cleanup

# Decode and save (cross-platform)
if ! base64_decode "$BASE64_DATA" "$OUTPUT_FILE"; then
  echo "Error: base64 decode failed" >&2
  echo "  Try installing openssl or check base64 command" >&2
  exit 1
fi

# Verify file
if [ ! -s "$OUTPUT_FILE" ]; then
  echo "Error: Generated file is empty" >&2
  rm -f "$OUTPUT_FILE"
  exit 1
fi

# Success, cancel temp file mark
TEMP_OUTPUT_FILE=""

# Output result
FILE_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
echo "✓ $OUTPUT_FILE ($FILE_SIZE)" >&2
echo "$OUTPUT_FILE"
