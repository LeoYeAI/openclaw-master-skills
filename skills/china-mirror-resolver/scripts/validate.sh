#!/usr/bin/env bash
# ============================================================
# china-mirror-resolver / validate.sh
# Validate baseline mirror reachability (Linux / macOS)
# Usage: bash validate.sh [tool] [--json]
#   tool: pip|npm|conda|docker|go|rust|maven|homebrew|github|huggingface|yum|all
#   --json: output machine-readable JSON instead of colored text
#   default: all
#
# SECURITY MANIFEST:
#   Environment variables accessed: none
#   External endpoints called: mirror source URLs (read-only HTTP GET)
#   Local files read: none
#   Local files written: none
# ============================================================

# Fix #1: use set -uo pipefail without -e to avoid ((0++)) exit trap
set -uo pipefail

GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[0;33m'; CYAN='\033[0;36m'; NC='\033[0m'

TOOL="all"
JSON_MODE=false
for arg in "$@"; do
    case "$arg" in
        --json) JSON_MODE=true ;;
        *) TOOL="$arg" ;;
    esac
done

PASS=0; FAIL=0; SKIP=0
JSON_RESULTS="["

# Fix #2: portable millisecond timer (works on macOS without GNU date or python3)
_now_ms() {
    # Try GNU date (Linux, brew coreutils on macOS)
    if date +%s%N >/dev/null 2>&1; then
        echo $(( $(date +%s%N) / 1000000 ))
    # Try perl (available on macOS by default)
    elif command -v perl >/dev/null 2>&1; then
        perl -MTime::HiRes=time -e 'printf "%d\n", time()*1000'
    # Try python3
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c 'import time;print(int(time.time()*1000))'
    # Fallback: second-level precision
    else
        echo $(( $(date +%s) * 1000 ))
    fi
}

check_url() {
    local name="$1" url="$2" expect_code="${3:-200}"
    local code elapsed start end

    start=$(_now_ms)
    code=$(curl -o /dev/null -s -w "%{http_code}" --max-time 10 "$url" 2>/dev/null || echo "000")
    end=$(_now_ms)
    elapsed=$(( end - start ))

    local status="FAIL"
    if [[ "$code" == "$expect_code" ]] || [[ "$expect_code" == "any" && "$code" != "000" ]]; then
        status="OK"
    elif [[ "$code" == "401" && "$expect_code" == "401" ]]; then
        status="OK"
    fi

    if [[ "$status" == "OK" ]]; then
        # Fix #1: use PASS=$((PASS+1)) instead of ((PASS++)) to avoid exit on zero
        PASS=$((PASS + 1))
        if ! $JSON_MODE; then
            printf "  ${GREEN}[OK]${NC}   %-30s HTTP %s | %sms\n" "$name" "$code" "$elapsed"
        fi
    else
        FAIL=$((FAIL + 1))
        if ! $JSON_MODE; then
            printf "  ${RED}[FAIL]${NC} %-30s HTTP %s | %sms\n" "$name" "$code" "$elapsed"
        fi
    fi

    # JSON output accumulation
    if $JSON_MODE; then
        [[ "$JSON_RESULTS" != "[" ]] && JSON_RESULTS="${JSON_RESULTS},"
        JSON_RESULTS="${JSON_RESULTS}{\"name\":\"${name}\",\"url\":\"${url}\",\"status\":\"${status}\",\"http_code\":\"${code}\",\"time_ms\":${elapsed}}"
    fi
}

section() {
    if ! $JSON_MODE; then
        printf "\n${CYAN}--- %s ---${NC}\n" "$1"
    fi
}

# ---- pip ----
if [[ "$TOOL" == "all" || "$TOOL" == "pip" ]]; then
    section "pip"
    check_url "Tsinghua TUNA"  "https://pypi.tuna.tsinghua.edu.cn/simple/"
    check_url "Aliyun"         "https://mirrors.aliyun.com/pypi/simple/"
    check_url "USTC"           "https://pypi.mirrors.ustc.edu.cn/simple/"
    check_url "Tencent"        "https://mirrors.cloud.tencent.com/pypi/simple/"
fi

# ---- npm ----
if [[ "$TOOL" == "all" || "$TOOL" == "npm" ]]; then
    section "npm"
    check_url "npmmirror"      "https://registry.npmmirror.com/"
    check_url "Huawei"         "https://repo.huaweicloud.com/repository/npm/"
fi

# ---- conda ----
if [[ "$TOOL" == "all" || "$TOOL" == "conda" ]]; then
    section "conda"
    check_url "Tsinghua Main"  "https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/"
    check_url "USTC"           "https://mirrors.ustc.edu.cn/anaconda/pkgs/main/"
    check_url "Aliyun"         "https://mirrors.aliyun.com/anaconda/pkgs/main/"
fi

# ---- Docker ----
if [[ "$TOOL" == "all" || "$TOOL" == "docker" ]]; then
    section "Docker"
    check_url "1ms.run"        "https://docker.1ms.run/v2/"        "401"
    check_url "xuanyuan.me"    "https://docker.xuanyuan.me/v2/"    "401"
    check_url "daocloud.io"    "https://docker.m.daocloud.io/v2/"  "401"
    check_url "linkedbus"      "https://docker.linkedbus.com/v2/"  "401"
fi

# ---- Go ----
if [[ "$TOOL" == "all" || "$TOOL" == "go" ]]; then
    section "Go"
    check_url "goproxy.cn"     "https://goproxy.cn/"
    check_url "goproxy.io"     "https://goproxy.io/"
fi

# ---- Rust ----
if [[ "$TOOL" == "all" || "$TOOL" == "rust" ]]; then
    section "Rust"
    check_url "USTC crates"    "https://mirrors.ustc.edu.cn/crates.io-index/"
    check_url "Tsinghua crates" "https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/"
    check_url "RsProxy.cn"    "https://rsproxy.cn/"
fi

# ---- Maven ----
if [[ "$TOOL" == "all" || "$TOOL" == "maven" ]]; then
    section "Maven"
    check_url "Aliyun Public" "https://maven.aliyun.com/repository/public/"
    check_url "Huawei"        "https://repo.huaweicloud.com/repository/maven/" "any"
fi

# ---- Homebrew ----
if [[ "$TOOL" == "all" || "$TOOL" == "homebrew" ]]; then
    section "Homebrew"
    check_url "Tsinghua Bottles" "https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles/"
    check_url "USTC Bottles"     "https://mirrors.ustc.edu.cn/homebrew-bottles/"
fi

# ---- GitHub ----
if [[ "$TOOL" == "all" || "$TOOL" == "github" ]]; then
    section "GitHub Accelerator"
    check_url "ghfast.top"     "https://ghfast.top/"
    check_url "gh-proxy.com"   "https://gh-proxy.com/"
    check_url "ghp.ci"         "https://ghp.ci/"
fi

# ---- HuggingFace ----
if [[ "$TOOL" == "all" || "$TOOL" == "huggingface" ]]; then
    section "HuggingFace"
    check_url "hf-mirror.com"  "https://hf-mirror.com/"
fi

# ---- yum/dnf ----
if [[ "$TOOL" == "all" || "$TOOL" == "yum" ]]; then
    section "yum/dnf"
    check_url "Tsinghua CentOS" "https://mirrors.tuna.tsinghua.edu.cn/centos/"
    check_url "Aliyun CentOS"   "https://mirrors.aliyun.com/centos/"
    check_url "USTC CentOS"     "https://mirrors.ustc.edu.cn/centos/"
fi

# ---- Output ----
if $JSON_MODE; then
    JSON_RESULTS="${JSON_RESULTS}]"
    echo "$JSON_RESULTS"
else
    TOTAL=$((PASS + FAIL))
    printf "\n${CYAN}========================================${NC}\n"
    printf "  Total: %d | ${GREEN}PASS: %d${NC} | ${RED}FAIL: %d${NC}\n" "$TOTAL" "$PASS" "$FAIL"
    printf "${CYAN}========================================${NC}\n"
fi
