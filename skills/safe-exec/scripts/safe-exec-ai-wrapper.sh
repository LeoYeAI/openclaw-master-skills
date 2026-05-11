#!/bin/bash
# SafeExec AI Wrapper - 上下文感知集成
# 用于 OpenClaw Agent 集成，自动传递用户消息上下文

SAFE_EXEC_BIN="$HOME/.local/bin/safe-exec"

# 从参数或环境变量获取上下文
if [[ $# -ge 2 ]]; then
    # 命令行参数模式: safe-exec-ai "用户上下文" "命令"
    USER_CONTEXT="$1"
    COMMAND="$2"
    shift 2
elif [[ -n "${SAFEXEC_CONTEXT:-}" ]]; then
    # 环境变量模式
    USER_CONTEXT="$SAFEXEC_CONTEXT"
    COMMAND="$1"
    shift
else
    # 没有上下文，直接执行
    exec $SAFE_EXEC_BIN "$@"
    exit $?
fi

# 导出上下文环境变量
export SAFEXEC_CONTEXT="$USER_CONTEXT"

# 执行命令
exec $SAFE_EXEC_BIN "$COMMAND"
