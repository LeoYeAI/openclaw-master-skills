"""
Nodes — 节点实现

每种节点类型对应一个执行函数。
所有函数签名统一: (step, ctx, log, bridge=None) -> NodeResult

OpenClaw 深度绑定:
- llm / agent / skill / message 节点全部通过 GatewayBridge 调用
- 同一工作流内共享 session，Agent 具备完整对话上下文
- 不再 fork 子进程，所有交互走 Gateway WebSocket RPC
"""

import json
import os
import subprocess
import time
import urllib.request
import urllib.parse
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from .context import Context
from .sandbox import execute_code

if TYPE_CHECKING:
    from .bridge import GatewayBridge


@dataclass
class NodeResult:
    """节点执行结果"""
    success: bool = True
    output: Any = None
    error: str = ""
    action: str = ""  # "" | "abort" | "skip" | "ask"

    def to_dict(self) -> Dict[str, Any]:
        d = {"success": self.success}
        if self.output is not None:
            d["output"] = self.output
        if self.error:
            d["error"] = self.error
        if self.action:
            d["action"] = self.action
        return d


LogFunc = Callable[[str, str], None]


# ── Script 节点 ──────────────────────────────────────────

def run_script(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """运行 Shell 命令 / Python 脚本"""
    command = step.get("command") or step.get("script") or step.get("file") or ""
    inline = step.get("inline")

    if inline:
        # 写入临时文件执行
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(ctx.resolve(inline))
            tmp_path = f.name
        command = f"python3 {tmp_path}"

    command = ctx.resolve(command)
    if not command:
        return NodeResult(success=False, error="script 节点: 未指定命令")

    log(f"执行命令: {command}", "INFO")

    timeout = step.get("timeout", 300)
    cwd = ctx.resolve(step.get("cwd")) if step.get("cwd") else None

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            env={**os.environ, **{k: str(v) for k, v in (step.get("env") or {}).items()}},
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode == 0:
            log(f"脚本输出: {stdout[:500]}", "INFO")
            # 尝试解析 JSON 输出
            output = stdout
            try:
                output = json.loads(stdout)
            except (json.JSONDecodeError, ValueError):
                pass
            return NodeResult(success=True, output=output)
        else:
            log(f"脚本失败 (exit={result.returncode}): {stderr[:500]}", "ERROR")
            return NodeResult(success=False, output=stdout, error=stderr)

    except subprocess.TimeoutExpired:
        return NodeResult(success=False, error=f"脚本超时 ({timeout}s)")
    except Exception as e:
        return NodeResult(success=False, error=str(e))
    finally:
        if inline:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


# ── LLM 节点 ─────────────────────────────────────────────

def run_llm(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    调用 LLM 进行推理 — 通过 Gateway Bridge 深度绑定 OpenClaw。

    同一工作流的多次 LLM 调用共享同一个 session，
    Agent 可以看到之前所有步骤的对话上下文。

    YAML 示例:
      - type: llm
        prompt: "分析以下数据: {{data}}"
        thinking: medium      # 可选 off|minimal|low|medium|high
        timeout: 120
        session: shared       # 可选，默认 shared (共享工作流 session)
    """
    prompt = ctx.resolve(step.get("prompt", ""))
    if not prompt:
        return NodeResult(success=False, error="llm 节点: 缺少 prompt")

    thinking = step.get("thinking", "")
    timeout = step.get("timeout", 120)
    timeout_ms = timeout * 1000

    if not bridge:
        return NodeResult(success=False, error="llm 节点: Gateway Bridge 未初始化，无法连接 OpenClaw")

    # 使用独立 session 还是共享工作流 session
    session_mode = step.get("session", "shared")
    session_key = None  # None = 使用 bridge 默认的工作流 session
    if session_mode == "isolated":
        # 创建临时独立 session
        import uuid
        session_key = f"agent:{bridge.agent_id}:openclaw-workflow:isolated:{uuid.uuid4().hex[:8]}"

    log(f"🧠 LLM 调用 (session={bridge.session_key}): {prompt[:100]}...", "INFO")

    resp = bridge.agent_call(
        message=prompt,
        session_key=session_key,
        thinking=thinking,
        timeout_ms=timeout_ms,
    )

    if resp.success:
        output = {
            "text": resp.text,
            "model": resp.model,
            "session_id": resp.session_id,
            "session_key": resp.session_key,
            "usage": resp.usage,
            "run_id": resp.run_id,
        }
        log(f"🧠 LLM 响应 ({resp.model}): {resp.text[:300]}", "INFO")
        return NodeResult(success=True, output=output)
    else:
        return NodeResult(success=False, error=f"LLM 调用失败: {resp.error}")


# ── Skill 节点 ────────────────────────────────────────────

def run_skill(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    调用 OpenClaw 已有 Skill — 通过 Gateway Bridge 深度绑定。

    通过同一会话让 Agent 调用指定 Skill，Agent 拥有完整上下文。

    YAML 示例:
      - type: skill
        action: "transmission.add"
        args:
          url: "magnet:?xt=..."
        instruction: "添加这个种子到NAS"
    """
    action = ctx.resolve(step.get("action", ""))
    if not action:
        return NodeResult(success=False, error="skill 节点: 缺少 action")

    if not bridge:
        return NodeResult(success=False, error="skill 节点: Gateway Bridge 未初始化")

    args = ctx.resolve(step.get("args", {}))
    instruction = ctx.resolve(step.get("instruction", ""))
    timeout = step.get("timeout", 300)
    timeout_ms = timeout * 1000

    # 构建指令: 让 Agent 在当前会话上下文中使用指定的 Skill
    if instruction:
        message = instruction
    else:
        args_desc = json.dumps(args, ensure_ascii=False) if args else ""
        message = f"请使用 {action} 技能"
        if args_desc:
            message += f"，参数: {args_desc}"

    log(f"🔧 调用 Skill: {action} (session={bridge.session_key})", "INFO")

    resp = bridge.agent_call(
        message=message,
        timeout_ms=timeout_ms,
    )

    if resp.success:
        output = {
            "text": resp.text,
            "session_key": resp.session_key,
            "run_id": resp.run_id,
        }
        log(f"🔧 Skill 响应: {resp.text[:300]}", "INFO")
        return NodeResult(success=True, output=output)
    else:
        return NodeResult(success=False, error=f"Skill 调用失败: {resp.error}")


# ── Condition 节点 ────────────────────────────────────────

def run_condition(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    条件分支。
    返回 output = {"branch": "then"|"else", "steps": [...]}
    引擎需要递归执行返回的子步骤。
    """
    condition = ctx.resolve(step.get("if", ""))
    if not condition:
        return NodeResult(success=False, error="condition 节点: 缺少 if 表达式")

    result = ctx.eval_condition(condition)
    branch = "then" if result else "else"

    log(f"条件 '{condition}' → {result} → 执行 {branch} 分支", "INFO")

    sub_steps = step.get(branch, [])
    return NodeResult(success=True, output={"branch": branch, "steps": sub_steps})


# ── Loop 节点 ─────────────────────────────────────────────

def run_loop(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    循环节点。
    返回 output = {"items": [...], "var": "item", "steps": [...]}
    引擎需要迭代执行。
    """
    var_name = step.get("as") or step.get("var") or "item"
    do_steps = step.get("do") or step.get("steps", [])

    # foreach 模式
    foreach = step.get("foreach")
    if foreach is not None:
        items = ctx.resolve(foreach)
        if isinstance(items, str):
            try:
                items = json.loads(items)
            except (json.JSONDecodeError, ValueError):
                items = items.split(",")
        if not isinstance(items, (list, tuple)):
            items = [items]
    else:
        # times 模式
        times = step.get("times", 0)
        times = ctx.resolve(times)
        if isinstance(times, str):
            times = int(times)
        items = list(range(times))

    log(f"循环 {len(items)} 次, 变量名: {var_name}", "INFO")

    # 并行循环选项: parallel: true + max_parallel: N
    parallel = step.get("parallel", False)
    max_parallel = step.get("max_parallel", 4)
    if isinstance(max_parallel, str):
        max_parallel = int(ctx.resolve(max_parallel))

    return NodeResult(success=True, output={
        "items": items,
        "var": var_name,
        "steps": do_steps,
        "parallel": parallel,
        "max_parallel": max_parallel,
    })


# ── Wait 节点 ─────────────────────────────────────────────

def run_wait(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """延时等待"""
    seconds = step.get("seconds", 0)
    seconds = ctx.resolve(seconds)
    if isinstance(seconds, str):
        seconds = float(seconds)

    until_cond = step.get("until")

    if until_cond:
        # 轮询等待条件为真
        poll_interval = step.get("poll_interval", 5)
        max_wait = step.get("max_wait", 300)
        elapsed = 0

        log(f"等待条件: {until_cond} (最长 {max_wait}s)", "INFO")
        while elapsed < max_wait:
            if ctx.eval_condition(ctx.resolve(until_cond)):
                log("等待条件满足", "INFO")
                return NodeResult(success=True, output={"waited": elapsed})
            time.sleep(poll_interval)
            elapsed += poll_interval

        return NodeResult(success=False, error=f"等待超时 ({max_wait}s)")
    else:
        log(f"等待 {seconds} 秒", "INFO")
        time.sleep(seconds)
        return NodeResult(success=True, output={"waited": seconds})


# ── Set 节点 ──────────────────────────────────────────────

def run_set(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """设置变量"""
    var = step.get("var", "")
    value = ctx.resolve(step.get("value"))

    if not var:
        return NodeResult(success=False, error="set 节点: 缺少 var")

    ctx.set_global(var, value)
    log(f"设置变量: {var} = {repr(value)[:200]}", "INFO")
    return NodeResult(success=True, output=value)


# ── Log 节点 ──────────────────────────────────────────────

def run_log(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """记录日志"""
    message = ctx.resolve(step.get("message", ""))
    level = step.get("level", "INFO")
    log(message, level)
    return NodeResult(success=True, output=message)


# ── HTTP 节点 ─────────────────────────────────────────────

def run_http(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """发起 HTTP 请求"""
    url = ctx.resolve(step.get("url", ""))
    if not url:
        return NodeResult(success=False, error="http 节点: 缺少 url")

    method = (step.get("method") or "GET").upper()
    headers = ctx.resolve(step.get("headers", {}))
    body = ctx.resolve(step.get("body"))
    params = ctx.resolve(step.get("params", {}))
    timeout = step.get("timeout", 30)

    # URL 参数
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)

    log(f"HTTP {method} {url}", "INFO")

    try:
        data = None
        if body is not None:
            if isinstance(body, (dict, list)):
                data = json.dumps(body, ensure_ascii=False).encode("utf-8")
                headers.setdefault("Content-Type", "application/json")
            else:
                data = str(body).encode("utf-8")

        req = urllib.request.Request(url, data=data, method=method)
        for k, v in headers.items():
            req.add_header(k, str(v))

        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_data = resp.read().decode("utf-8")
            status = resp.status

            try:
                resp_json = json.loads(resp_data)
            except (json.JSONDecodeError, ValueError):
                resp_json = None

            output = {
                "status": status,
                "body": resp_json if resp_json is not None else resp_data,
                "headers": dict(resp.headers),
            }

            log(f"HTTP 响应: {status}", "INFO")
            return NodeResult(success=True, output=output)

    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            body_text = e.read().decode("utf-8")[:1000]
        except Exception:
            pass
        return NodeResult(success=False, error=f"HTTP {e.code}: {e.reason}\n{body_text}")
    except Exception as e:
        return NodeResult(success=False, error=str(e))


# ── Code 节点 ─────────────────────────────────────────────

def run_code(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """执行内联 Python 代码 (沙箱)"""
    code = step.get("python", "")
    if not code:
        return NodeResult(success=False, error="code 节点: 缺少 python 代码")

    code = ctx.resolve(code)

    # 将上下文变量注入沙箱
    variables = ctx.dump()["variables"]
    variables.update(ctx.dump()["step_outputs"])

    log("执行内联代码", "INFO")

    result = execute_code(code, variables=variables)

    if result.success:
        if result.output:
            log(f"代码输出: {result.output[:500]}", "INFO")
        # 使用 is not None 而非 truthiness，避免 [] / 0 / "" 等 falsy 值丢失
        output = result.result if result.result is not None else result.output
        return NodeResult(success=True, output=output)
    else:
        log(f"代码执行失败: {result.error}", "ERROR")
        return NodeResult(success=False, error=result.error)


# ── Agent 节点 ────────────────────────────────────────────

def run_agent(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    调用 OpenClaw Agent — 通过 Gateway Bridge 深度绑定。

    与 llm 节点的区别:
    - agent 节点支持 deliver (将结果投递到通讯渠道)
    - agent 节点允许指定 system prompt 覆盖
    - 同样共享工作流 session，拥有完整对话上下文

    YAML 示例:
      - type: agent
        message: "生成今日销售报告"
        thinking: medium
        deliver: true
        deliver_channel: imessage
        deliver_target: "+861234"
    """
    message = ctx.resolve(step.get("message", ""))
    if not message:
        return NodeResult(success=False, error="agent 节点: 缺少 message")

    if not bridge:
        return NodeResult(success=False, error="agent 节点: Gateway Bridge 未初始化")

    thinking = step.get("thinking", "")
    timeout = step.get("timeout", 300)
    timeout_ms = timeout * 1000
    deliver = step.get("deliver", False)
    deliver_channel = step.get("deliver_channel", "")
    deliver_target = ctx.resolve(step.get("deliver_target", ""))

    log(f"🤖 调用 Agent (session={bridge.session_key}): {message[:100]}...", "INFO")

    # 1) 通过 Gateway 调用 Agent (共享 session)
    resp = bridge.agent_call(
        message=message,
        thinking=thinking,
        timeout_ms=timeout_ms,
    )

    if not resp.success:
        return NodeResult(success=False, error=f"Agent 调用失败: {resp.error}")

    output = {
        "text": resp.text,
        "model": resp.model,
        "session_key": resp.session_key,
        "session_id": resp.session_id,
        "run_id": resp.run_id,
        "usage": resp.usage,
    }

    log(f"🤖 Agent 响应 ({resp.model}): {resp.text[:300]}", "INFO")

    # 2) 如果需要 deliver，通过 openclaw message send 投递
    if deliver and deliver_channel and deliver_target:
        log(f"📤 投递到 {deliver_channel} → {deliver_target}", "INFO")
        deliver_cmd = [
            "openclaw", "message", "send",
            "--channel", deliver_channel,
            "--target", deliver_target,
            "--message", resp.text,
            "--json",
        ]
        try:
            dr = subprocess.run(deliver_cmd, capture_output=True, text=True, timeout=60)
            if dr.returncode == 0:
                log("📤 消息投递成功", "INFO")
                output["delivered"] = True
            else:
                log(f"📤 消息投递失败: {dr.stderr.strip()}", "WARN")
                output["delivered"] = False
        except Exception as e:
            log(f"📤 消息投递异常: {e}", "WARN")
            output["delivered"] = False

    return NodeResult(success=True, output=output)


# ── Subagent 节点 ─────────────────────────────────────────


def _cleanup_single_subagent(bridge, spawn_session_key: str, child_session_key: str, log: LogFunc):
    """清理单个 subagent 的 spawn + child session"""
    cleaned = 0
    for key in (spawn_session_key, child_session_key):
        if key and bridge.cleanup_session(key):
            cleaned += 1
    if cleaned:
        log(f"🧹 已清理 {cleaned} 个 session (spawn+child)", "DEBUG")


# ── 批量 Spawn (Batch Spawn) ─────────────────────────────

def batch_spawn_subagents(
    items: list,
    step_template: dict,
    ctx: "Context",
    log: "LogFunc",
    bridge: "GatewayBridge",
    batch_size: int = 8,
) -> list:
    """
    批量创建 subagent — 一次 agent_call 让 Agent 并行调用多个 sessions_spawn。

    利用 OpenClaw Agent 在单轮对话中可以发起多个工具调用的能力:
    Agent 收到 "请同时创建以下 N 个子代理" 的指令后，会在一次响应中
    发出 N 个 sessions_spawn toolCall，Gateway 并行处理。

    对比:
    - 旧方式: 24 个 subagent × 25s/个 = 600s (串行)
    - 新方式: 24 个 subagent / 8 per batch × ~30s/batch = ~90s (批量并行)

    Args:
        items: 循环 items 列表
        step_template: subagent 步骤模板 (包含 task, label 等)
        ctx: 主 Context
        log: 日志函数
        bridge: GatewayBridge 实例
        batch_size: 每批 spawn 数量 (默认 8，与 maxConcurrent 协调)

    Returns:
        spawn_results 列表，每项为 dict:
        {
            "spawn_session_key": str,
            "child_session_key": str,
            "child_run_id": str,
            "mode": str,
            "item": original_item,
            "item_index": int,
        }
    """
    import uuid as _uuid

    if not items:
        return []

    var_name = step_template.get("_var_name", "item")
    model = step_template.get("model", "")
    thinking = step_template.get("thinking", "")
    timeout = step_template.get("timeout", 300)
    mode = step_template.get("mode", "run")
    cleanup = step_template.get("cleanup", "auto")
    spawn_timeout_ms = int(step_template.get("spawn_timeout", 180000))  # 批量需更长超时
    spawn_max_retries = int(step_template.get("spawn_retries", 2))

    all_results = []

    # 分批处理
    for batch_start in range(0, len(items), batch_size):
        batch = items[batch_start:batch_start + batch_size]
        batch_end = batch_start + len(batch)

        log(f"🏭 批量 spawn [{batch_start+1}-{batch_end}/{len(items)}] ({len(batch)} 个)", "INFO")

        # ── 并发控制 — 等待空位 ──
        # 仅在「当前已接近/达到并发上限」时等待。
        # 旧逻辑使用 active + len(batch) <= max_concurrent + 2，
        # 当 active=0 且 batch 比较大时会触发无意义等待（直到 throttle_timeout）。
        # 这里改为只看当前活跃数，避免出现“还没开始 spawn 就先等满 300s”的情况。
        max_concurrent = bridge.get_subagent_concurrency_limit()
        throttle_headroom = int(step_template.get("throttle_headroom", 2))
        throttle_limit = max(1, max_concurrent + throttle_headroom)
        throttle_max = int(step_template.get("throttle_timeout", 300))
        throttle_wait = 0
        while throttle_wait < throttle_max:
            active = bridge.count_active_subagents()
            if active < throttle_limit:
                break
            if throttle_wait == 0:
                log(
                    f"🏭 并发限制: 活跃 {active}/{max_concurrent} "
                    f"(阈值 {throttle_limit})，等待空位...",
                    "INFO",
                )
            time.sleep(3)
            throttle_wait += 3

        # ── 构建批量 spawn 指令 ──
        spawn_specs = []
        for i, item in enumerate(batch):
            idx = batch_start + i
            # 为每个 item 解析 task 和 label
            child_ctx = ctx.create_child_context({
                var_name: item,
                f"{var_name}_index": idx,
                "loop_index": idx,
                "loop_length": len(items),
            })
            task = child_ctx.resolve(step_template.get("task", ""))
            label = child_ctx.resolve(step_template.get("label", ""))

            spec_parts = [f'  task: "{task}"']
            if label:
                spec_parts.append(f'  label: "{label}"')
            if model:
                spec_parts.append(f'  model: "{model}"')
            if thinking:
                spec_parts.append(f'  thinking: "{thinking}"')
            if timeout:
                spec_parts.append(f'  runTimeoutSeconds: {timeout}')
            if mode and mode != "run":
                spec_parts.append(f'  mode: "{mode}"')
            # cleanup: sessions_spawn 只接受 "delete" 或 "keep"，不接受 "auto"
            if cleanup == "keep":
                spec_parts.append(f'  cleanup: "keep"')
            else:
                spec_parts.append(f'  cleanup: "delete"')

            spawn_specs.append(f"子代理 #{idx+1}:\n" + "\n".join(spec_parts))

        instruction = (
            f"请立即使用 sessions_spawn 工具同时创建以下 {len(batch)} 个子代理。\n"
            f"你必须在一次响应中并行调用 {len(batch)} 次 sessions_spawn 工具，每次对应一个子代理。\n"
            f"不要自己执行任务，只调用工具。\n\n"
            + "\n\n".join(spawn_specs)
        )

        # ── 使用 factory session 发送批量指令 ──
        factory_key = bridge.factory_session_key
        if not factory_key:
            # 如果没有 factory session，创建临时 spawn session
            factory_key = f"agent:{bridge.agent_id}:openclaw-workflow:spawn:{_uuid.uuid4().hex[:8]}"

        spawn_resp = None
        last_error = ""
        for attempt in range(1 + spawn_max_retries):
            spawn_resp = bridge.agent_call(
                message=instruction,
                session_key=factory_key,
                timeout_ms=spawn_timeout_ms,
            )
            if spawn_resp.success:
                break
            last_error = spawn_resp.error or ""
            is_timeout = "timeout" in last_error.lower() or "超时" in last_error
            if not is_timeout or attempt >= spawn_max_retries:
                break
            retry_delay = 5 * (attempt + 1)
            log(f"🏭 Gateway 超时，{retry_delay}s 后重试 ({attempt+1}/{spawn_max_retries})...", "WARN")
            time.sleep(retry_delay)

        if not spawn_resp or not spawn_resp.success:
            log(f"🏭 批量 spawn 失败: {last_error}", "ERROR")
            # 为本批所有 item 生成失败结果
            for i, item in enumerate(batch):
                idx = batch_start + i
                all_results.append({
                    "spawn_session_key": factory_key,
                    "child_session_key": "",
                    "child_run_id": "",
                    "mode": mode,
                    "item": item,
                    "item_index": idx,
                    "error": last_error,
                })
            continue

        # ── 从 JSONL 提取所有 childSessionKey ──
        # agent_call 返回后，JSONL 已写入完成
        time.sleep(1)  # 给 JSONL 写入缓冲
        spawn_infos = bridge.extract_all_spawn_info_from_session_log(factory_key)

        # 本批之前的 spawn 结果数 = 之前批次已提取的总数
        prev_count = len(all_results)
        # 取本批新增的 (跳过之前批次的)
        batch_infos = spawn_infos[prev_count:]

        log(f"🏭 从 JSONL 提取到 {len(batch_infos)} 个 childSessionKey (本批期望 {len(batch)})", "INFO")

        for i, item in enumerate(batch):
            idx = batch_start + i
            if i < len(batch_infos):
                info = batch_infos[i]
                child_key = info.get("child_session_key", "")
                child_run = info.get("child_run_id", "")

                # 缓存 child session ID
                if child_key:
                    bridge.cache_child_session_id(child_key)
                    bridge.track_factory_subagent(child_key, child_run, "")
                    log(f"🏭 [{idx+1}/{len(items)}] 子代理已创建: {child_key[:40]}...", "INFO")

                all_results.append({
                    "spawn_session_key": factory_key,
                    "child_session_key": child_key,
                    "child_run_id": child_run,
                    "mode": info.get("mode", mode),
                    "item": item,
                    "item_index": idx,
                })
            else:
                log(f"🏭 [{idx+1}/{len(items)}] 未能提取 childSessionKey", "WARN")
                all_results.append({
                    "spawn_session_key": factory_key,
                    "child_session_key": "",
                    "child_run_id": "",
                    "mode": mode,
                    "item": item,
                    "item_index": idx,
                    "error": "missing childSessionKey from batch response",
                })

        # 轮换 factory session — 防止上下文膨胀
        bridge._factory_spawn_count += len(batch)
        bridge.maybe_rotate_factory()
        if bridge.factory_session_key:
            factory_key = bridge.factory_session_key

    log(f"🏭 批量 spawn 完成: {len(all_results)}/{len(items)} 个", "INFO")
    return all_results


def run_subagent(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    创建 OpenClaw 子代理 (Subagent) 执行独立任务。

    实现原理:
    1. 为每次 spawn 创建一次性隔离 session，避免污染工作流主 session 的上下文
    2. 在该隔离 session 中让 Agent 调用 `sessions_spawn` 工具
    3. 从 Agent 响应中提取 childSessionKey
    4. 如果 wait=true，通过读取 parent session 的 JSONL 文件轮询检测
       OpenClaw auto-announce 推送的 [Internal task completion event]
    5. 从 completion event 中提取子代理返回的结果

    说明:
    - `sessions_spawn` 在当前 OpenClaw 版本中是 Agent 工具，不是 Gateway 直接 RPC
    - 因此这里的 session 只是工具调用载体，不是把“session”当成“subagent”

    子代理特性:
    - 独立会话: 隔离的 session key (agent:<id>:subagent:<uuid>)
    - 非阻塞: sessions_spawn 立即返回，子代理异步执行
    - 可等待: wait=true 时轮询 session JSONL 直到出现 completion event
    - 并发感知: min(subagents.maxConcurrent, agents.defaults.maxConcurrent) 防止 lane 过载
    - 精简环境: 仅加载 AGENTS.md，无 session tools
    - 自动清理: wait=true 完成后自动删除 spawn + child session (cleanup=auto)
    - 内置重试: Gateway timeout 自动重试 (spawn_retries=2, spawn_timeout=120s)

    YAML 示例:
      - type: subagent
        task: "分析以下数据并生成报告: {{data}}"
        label: "数据分析师"
        model: "claude-sonnet-4-20250514"
        thinking: medium
        timeout: 300
        wait: true
        poll_interval: 5
        mode: run           # run (一次性) | session (持久)
        cleanup: auto        # auto (wait 完成后清理) | keep (保留)
    """
    import uuid as _uuid

    task = ctx.resolve(step.get("task", ""))
    if not task:
        return NodeResult(success=False, error="subagent 节点: 缺少 task")

    if not bridge:
        return NodeResult(success=False, error="subagent 节点: Gateway Bridge 未初始化")

    label = ctx.resolve(step.get("label", ""))
    model = ctx.resolve(step.get("model", ""))
    thinking = step.get("thinking", "")
    timeout = step.get("timeout", 300)
    wait = step.get("wait", False)
    poll_interval = step.get("poll_interval", 5)
    mode = step.get("mode", "run")
    cleanup = step.get("cleanup", "auto")

    # ── 1) 模式选择 ──
    # 有 factory session → subagent 模式 (循环中，由 engine 预开启)
    # 无 factory session → 子会话模式 (直接执行，无需 sessions_spawn)
    if not bridge.factory_session_key:
        return _run_subagent_child_session(
            step, ctx, log, bridge, task, label, thinking,
            timeout, wait, mode, cleanup, poll_interval,
        )

    # ── 以下为 subagent 模式 (factory + sessions_spawn) ──
    spawn_session_key = bridge.factory_session_key

    # ── 2) 构建 spawn 指令 ──
    spawn_params = [f'- task: "{task}"']
    if label:
        spawn_params.append(f'- label: "{label}"')
    if model:
        spawn_params.append(f'- model: "{model}"')
    if thinking:
        spawn_params.append(f'- thinking: "{thinking}"')
    if timeout:
        spawn_params.append(f'- runTimeoutSeconds: {timeout}')
    if mode and mode != "run":
        spawn_params.append(f'- mode: "{mode}"')
    if cleanup and cleanup != "keep":
        spawn_params.append(f'- cleanup: "{cleanup}"')

    spawn_instruction = (
        "请立即使用 sessions_spawn 工具创建一个子代理。"
        "你必须直接调用 sessions_spawn 工具，不要自己执行这个任务。\n\n"
        "sessions_spawn 参数:\n" + "\n".join(spawn_params)
    )

    # ── 2.5) 并发控制 — 尊重 subagents.maxConcurrent 限制 ──
    # 从 openclaw.json 读取并发限制，如果活跃子代理已达上限，等待直到有空位
    max_concurrent = bridge.get_subagent_concurrency_limit()
    throttle_wait = 0
    throttle_max = int(step.get("throttle_timeout", 300))  # 等待空位的最大时间
    while throttle_wait < throttle_max:
        active = bridge.count_active_subagents()
        if active < max_concurrent:
            break
        if throttle_wait == 0:
            log(f"🧬 并发限制: 活跃子代理 {active}/{max_concurrent}，等待空位...", "INFO")
        time.sleep(3)
        throttle_wait += 3
    else:
        log(f"🧬 并发等待超时 ({throttle_max}s)，仍然尝试创建", "WARN")

    # ── 3) 指示 Agent 调用 sessions_spawn 工具 ──
    spawn_timeout_ms = int(step.get("spawn_timeout", 120000))
    spawn_max_retries = int(step.get("spawn_retries", 2))
    spawn_resp = None
    last_error = ""

    # ── Subagent 模式: 序列化 spawn，批次控制，轮换 session ──
    with bridge.factory_lock:
        bridge._factory_spawn_count += 1
        spawn_num = bridge._factory_spawn_count
        total_expected = bridge._factory_total_expected

        # 批次间隔 (每 N 个 spawn 暂停，给 Gateway 喘息)
        batch_size = int(step.get("spawn_batch_size", 10))
        batch_delay = float(step.get("spawn_batch_delay", 1))
        if batch_size > 0 and spawn_num > 1 and (spawn_num - 1) % batch_size == 0:
            log(f"🏭 批次间隔: 已创建 {spawn_num - 1} 个，暂停 {batch_delay}s", "INFO")
            time.sleep(batch_delay)

        # 检查是否需要轮换 factory session (控制上下文增长)
        bridge.maybe_rotate_factory()
        spawn_session_key = bridge.factory_session_key

        progress = f"[{spawn_num}/{total_expected}]" if total_expected else f"[{spawn_num}]"
        log(f"🏭 {progress} 创建子代理: {label or '(unnamed)'}", "INFO")

        for attempt in range(1 + spawn_max_retries):
            spawn_resp = bridge.agent_call(
                message=spawn_instruction,
                session_key=spawn_session_key,
                timeout_ms=spawn_timeout_ms,
            )
            if spawn_resp.success:
                break
            last_error = spawn_resp.error or ""
            is_timeout = "timeout" in last_error.lower() or "超时" in last_error
            if not is_timeout or attempt >= spawn_max_retries:
                break
            retry_delay = 5 * (attempt + 1)
            log(f"🏭 Gateway 超时，{retry_delay}s 后重试 ({attempt+1}/{spawn_max_retries})...", "WARN")
            time.sleep(retry_delay)

    if not spawn_resp or not spawn_resp.success:
        return NodeResult(success=False, error=f"子代理创建失败: {last_error}")

    # ── 4) 提取 childSessionKey ──
    # 策略 A: 从 Gateway 返回的响应中提取 (text/raw JSON)
    spawn_info = bridge.extract_spawn_info(spawn_resp)
    child_session_key = spawn_info.get("child_session_key", "")
    child_run_id = spawn_info.get("child_run_id", "")

    # 策略 B: 如果响应中提取不到，等待 JSONL 写入后从 session log 中读取
    # Gateway --expect-final 有时返回空文本 (Agent 直接 yield 无 text)
    # 或 Agent 不在文本中包含 key，但 JSONL 总有完整的 toolResult
    if not child_session_key:
        # 给 JSONL 一点写入时间
        time.sleep(1)
        log_info = bridge.extract_spawn_info_from_session_log(spawn_session_key)
        if log_info.get("child_session_key"):
            child_session_key = log_info["child_session_key"]
            child_run_id = log_info.get("child_run_id", child_run_id)
            spawn_info.update(log_info)
            log(f"🧬 从 session log 中提取到 childSessionKey", "DEBUG")

    spawn_output = {
        "spawn_session_key": spawn_session_key,
        "child_session_key": child_session_key,
        "child_run_id": child_run_id,
        "mode": spawn_info.get("mode", mode),
    }

    if child_session_key:
        log(f"🧬 子代理已创建 (child={child_session_key}, run={child_run_id})", "INFO")
        # 立即缓存 child session 的 session ID
        # Gateway 在 subagent 完成后会从 sessions.json 中删除 subagent 条目，
        # 导致 wait_subagents 阶段无法通过 get_session_id() 查找。
        # 在此处缓存确保后续策略 B 检测始终有效。
        cached_id = bridge.cache_child_session_id(child_session_key)
        if cached_id:
            log(f"🧬 已缓存 child session ID: {cached_id[:12]}...", "DEBUG")
    else:
        log(f"🧬 子代理创建指令已发送，但未能提取 childSessionKey", "WARN")
        log(f"🧬 Agent 响应: {spawn_resp.text[:300]}", "DEBUG")

    # ── 5) 如果不需要等待，直接返回 ──
    # spawn session 的 JSONL 只在 wait=true 时被读取 (检测 completion event)
    # wait=false 时 spawn session 没有后续用途，必须立即清理：
    # - 防止 spawn session 累积 → 并发计数膨胀 → 阻塞后续创建
    # - 防止 Gateway session 资源泄漏
    if not wait:
        bridge.track_factory_subagent(child_session_key, child_run_id, label)
        log(f"🏭 子代理已创建，保留 factory session", "DEBUG")
        spawn_output["waited"] = False
        log("🏭 子代理已异步启动，不等待完成", "INFO")
        return NodeResult(success=True, output=spawn_output)

    # ── 6) 等待子代理完成 — 读取 session JSONL 文件 ──
    if not child_session_key:
        log("🧬 无法等待: 未获取到 childSessionKey", "WARN")
        spawn_output["waited"] = False
        spawn_output["error"] = "missing childSessionKey"
        return NodeResult(success=True, output=spawn_output)

    log(f"🧬 等待子代理完成 (poll={poll_interval}s, timeout={timeout}s)...", "INFO")
    log(f"🧬 监听 session: {spawn_session_key} → 等待 child: {child_session_key}", "DEBUG")

    elapsed = 0
    while elapsed < timeout:
        time.sleep(poll_interval)
        elapsed += poll_interval

        # 读取 parent (spawn) session 的 JSONL，查找 completion event
        found, status, result_text = bridge.find_subagent_completion(
            parent_session_key=spawn_session_key,
            child_session_key=child_session_key,
        )

        if found:
            log(f"🧬 子代理已完成: status={status} (耗时约 {elapsed}s)", "INFO")
            if result_text:
                log(f"🧬 子代理结果: {result_text[:300]}", "INFO")

            spawn_output["waited"] = True
            spawn_output["wait_timeout"] = False
            spawn_output["elapsed"] = elapsed
            spawn_output["status"] = status or "completed"
            spawn_output["result"] = result_text or ""
            spawn_output["text"] = result_text or ""

            # 等待完成后自动清理 session
            if cleanup != "keep":
                # Subagent 模式: 只清理 child session，factory session 由 engine 管理
                if child_session_key:
                    bridge.cleanup_session(child_session_key)

            is_success = status and "successfully" in status
            return NodeResult(success=is_success if status else True, output=spawn_output)

        if elapsed % 30 < poll_interval:
            log(f"🧬 子代理仍在运行 ({elapsed}s / {timeout}s)...", "INFO")

    # 超时
    log(f"🧬 等待子代理超时 ({timeout}s)", "WARN")
    spawn_output["waited"] = True
    spawn_output["wait_timeout"] = True
    spawn_output["elapsed"] = elapsed
    return NodeResult(success=True, output=spawn_output)


# ── Wait Subagents 节点 ──────────────────────────────────

def run_wait_subagents(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    等待多个 fire-and-forget Subagent 全部完成并收集结果。

    标准化的 subagent 汇合 (fan-in) 模式:
    1. 读取 tracker 列表 (由 subagent 节点 + code 节点在 loop 中积累)
    2. 轮询每个子代理的 session JSONL 文件检测 completion event
    3. 返回所有结果列表

    YAML 示例:
      - id: wait_all
        type: wait_subagents
        tracker: "{{init_tracker}}"
        max_wait: 600
        poll_interval: 5
        extra_fields:          # 可选，从 tracker item 透传到结果中的字段名
          - email_id
          - subject
    """
    if not bridge:
        return NodeResult(success=False, error="wait_subagents 节点: Gateway Bridge 未初始化")

    # ── 解析参数 ──
    tracker_raw = step.get("tracker", "")
    if isinstance(tracker_raw, str):
        tracker_raw = ctx.resolve(tracker_raw)

    # tracker 可能是 list (直接引用) 或 JSON string
    if isinstance(tracker_raw, list):
        tracker = tracker_raw
    elif isinstance(tracker_raw, str):
        try:
            tracker = json.loads(tracker_raw)
        except (json.JSONDecodeError, ValueError):
            tracker = []
    else:
        tracker = []

    if not tracker:
        log("⏳ tracker 为空，没有需要等待的 Subagent", "WARN")
        return NodeResult(success=True, output=[])

    max_wait = int(step.get("max_wait", 600))
    poll_sec = int(step.get("poll_interval", 5))
    extra_fields = step.get("extra_fields", [])

    log(f"⏳ 等待 {len(tracker)} 个 Subagent 完成 (max_wait={max_wait}s, poll={poll_sec}s)...", "INFO")

    # ── 轮询循环 ──
    results = []
    pending = list(range(len(tracker)))
    elapsed = 0

    while pending and elapsed < max_wait:
        # 每轮 poll 刷新一次 sessions.json 缓存
        # 避免 N 个 pending 项各自读一次文件 (100 项 × 每 5 秒 = 灾难性 IO)
        bridge.refresh_session_index_cache()

        still_pending = []
        for idx in pending:
            item = tracker[idx]
            sk = item.get("spawn_session_key", "")
            ck = item.get("child_session_key", "")

            if not sk or not ck:
                # 缺少 key，直接标记失败
                entry = {
                    "status": "no_key",
                    "classification": "无法获取分类结果 (缺少 session key)",
                }
                for f in extra_fields:
                    entry[f] = item.get(f, "")
                results.append(entry)
                continue

            found, status, result_text = bridge.find_subagent_completion(
                parent_session_key=sk,
                child_session_key=ck,
            )

            if found:
                entry = {
                    "status": status or "completed",
                    "classification": result_text or "(无结果文本)",
                    "result": result_text or "",
                }
                for f in extra_fields:
                    entry[f] = item.get(f, "")
                results.append(entry)
                label = ""
                for f in extra_fields:
                    if item.get(f):
                        label = str(item[f])[:40]
                        break
                if not label:
                    label = ck[:30]
                log(f"✅ [{len(results)}/{len(tracker)}] {label}", "INFO")
            else:
                still_pending.append(idx)

        pending = still_pending
        if pending:
            time.sleep(poll_sec)
            elapsed += poll_sec
            if elapsed % 30 < poll_sec:
                log(f"⏳ 仍有 {len(pending)} 个运行中 ({elapsed}s/{max_wait}s)...", "INFO")

    # 超时的 subagent 标记 timeout
    for idx in pending:
        item = tracker[idx]
        entry = {
            "status": "timeout",
            "classification": "分类超时",
            "result": "",
        }
        for f in extra_fields:
            entry[f] = item.get(f, "")
        results.append(entry)

    completed = sum(1 for r in results if r["status"] != "timeout" and r["status"] != "no_key")
    timed_out = sum(1 for r in results if r["status"] == "timeout")
    log(f"📊 全部完成: {len(results)} 个, 成功 {completed}, 超时 {timed_out}", "INFO")

    # ── 自动清理 subagent sessions ──
    # 每个 subagent 创建 2 个 session (spawn + child)，全部完成后批量删除
    cleanup_mode = step.get("cleanup", "auto")
    if cleanup_mode != "keep" and bridge:
        # auto: 清理已完成的 subagent sessions
        # all: 清理所有 (包括 timeout 的)
        if cleanup_mode == "completed":
            # 只清理已完成的
            completed_items = []
            for i, item in enumerate(tracker):
                if i < len(results) and results[i].get("status") not in ("timeout", "no_key"):
                    completed_items.append(item)
            cleanup_tracker = completed_items
        else:
            # auto 或 all: 清理所有 (包括 timeout 的 — session 已无用)
            cleanup_tracker = tracker

        if cleanup_tracker:
            stats = bridge.cleanup_subagent_sessions(cleanup_tracker, log_func=log)
            bridge.invalidate_session_cache()
            log(f"🧹 Session 清理完成: 删除 {stats['cleaned']} 个, 失败 {stats['failed']} 个", "INFO")

    return NodeResult(success=True, output=results)


# ── Message 节点 ──────────────────────────────────────────

def run_message(step: dict, ctx: Context, log: LogFunc, bridge: "GatewayBridge" = None) -> NodeResult:
    """
    通过 OpenClaw 发送消息。

    优先使用 Gateway Bridge 让 Agent 代发 (保持 session 上下文)，
    如果指定了 direct: true 则走 openclaw message send CLI。

    YAML 示例:
      - type: message
        channel: imessage
        target: "+8617600510003"
        message: "今日报告: {{report}}"
        media: "/path/to/file"    # 可选
        direct: false             # 可选，默认 false (通过 Agent 代发)
    """
    # when 条件守卫
    when = step.get("when")
    if when and not ctx.eval_condition(ctx.resolve(when)):
        log("条件不满足，跳过消息发送", "INFO")
        return NodeResult(success=True, output="skipped")

    channel = ctx.resolve(step.get("channel", "imessage"))
    target = ctx.resolve(step.get("target", ""))
    message = ctx.resolve(step.get("message", ""))
    media = ctx.resolve(step.get("media")) if step.get("media") else None
    account = ctx.resolve(step.get("account")) if step.get("account") else None
    direct = step.get("direct", False)

    if not target:
        return NodeResult(success=False, error="message 节点: 缺少 target")
    if not message and not media:
        return NodeResult(success=False, error="message 节点: 缺少 message 或 media")

    log(f"📨 发送消息 ({channel} → {target}): {message[:80]}...", "INFO")

    # 方式 1: 通过 Agent 代发 (有 session 上下文，Agent 知道工作流执行情况)
    if not direct and bridge:
        agent_instruction = (
            f"请通过 {channel} 向 {target} 发送以下消息:\n\n{message}"
        )
        if media:
            agent_instruction += f"\n\n附件: {media}"

        resp = bridge.agent_call(message=agent_instruction, timeout_ms=60000)

        if resp.success:
            log(f"📨 Agent 代发消息成功 (session={resp.session_key})", "INFO")
            return NodeResult(success=True, output={
                "text": resp.text,
                "method": "agent",
                "session_key": resp.session_key,
            })
        else:
            log(f"📨 Agent 代发失败，回退到直接发送: {resp.error}", "WARN")
            # 回退到直接发送

    # 方式 2: 直接通过 openclaw message send CLI
    cmd = ["openclaw", "message", "send",
           "--channel", channel,
           "--target", target,
           "--json"]
    if message:
        cmd.extend(["--message", message])
    if media:
        cmd.extend(["--media", media])
    if account:
        cmd.extend(["--account", account])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            output = result.stdout.strip()
            try:
                output = json.loads(output)
            except (json.JSONDecodeError, ValueError):
                pass
            log(f"📨 消息直接发送成功", "INFO")
            return NodeResult(success=True, output={"result": output, "method": "direct"})
        else:
            error = result.stderr.strip() or result.stdout.strip()
            log(f"📨 消息发送失败: {error[:200]}", "ERROR")
            return NodeResult(success=False, error=error)
    except subprocess.TimeoutExpired:
        return NodeResult(success=False, error="消息发送超时")
    except FileNotFoundError:
        return NodeResult(success=False, error="openclaw CLI 未安装")


# ── 节点路由表 ────────────────────────────────────────────

NODE_HANDLERS: Dict[str, Callable] = {
    "script": run_script,
    "llm": run_llm,
    "skill": run_skill,
    "condition": run_condition,
    "loop": run_loop,
    "wait": run_wait,
    "set": run_set,
    "log": run_log,
    "http": run_http,
    "code": run_code,
    "agent": run_agent,
    "subagent": run_subagent,
    "wait_subagents": run_wait_subagents,
    "message": run_message,
}
