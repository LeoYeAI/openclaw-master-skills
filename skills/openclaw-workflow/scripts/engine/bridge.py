"""
OpenClaw Gateway Bridge — 与 OpenClaw Gateway 的原生集成

通过 Gateway WebSocket RPC 协议实现:
- 会话管理 (创建/复用 session)
- Agent 调用 (复用 OpenClaw 的模型配置和上下文)
- 消息发送 (通过 OpenClaw 的渠道系统)
- 子代理状态检测 (通过 session JSONL 文件读取 completion event)

协议格式: openclaw gateway call <method> --params <json>
会话键格式: agent:<agentId>:<namespace> (如 agent:main:openclaw-workflow:run123)
子代理会话键格式: agent:<agentId>:subagent:<uuid>
"""

import json
import os
import re
import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


@dataclass
class GatewayConfig:
    """Gateway 连接配置"""
    port: int = 18789
    token: str = ""
    timeout_ms: int = 120000  # 默认 2 分钟

    @classmethod
    def from_config(cls) -> "GatewayConfig":
        """从 openclaw.json 读取配置"""
        config_path = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
        if not config_path.exists():
            return cls()
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
            gw = data.get("gateway", {})
            auth = gw.get("auth", {})
            return cls(
                port=gw.get("port", 18789),
                token=auth.get("token", ""),
            )
        except Exception:
            return cls()


@dataclass
class AgentResponse:
    """Agent 调用响应"""
    success: bool = True
    text: str = ""
    run_id: str = ""
    session_id: str = ""
    session_key: str = ""
    model: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)
    error: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "success": self.success,
            "text": self.text,
            "run_id": self.run_id,
            "session_id": self.session_id,
            "session_key": self.session_key,
            "model": self.model,
        }
        if self.usage:
            d["usage"] = self.usage
        if self.error:
            d["error"] = self.error
        return d


class GatewayBridge:
    """
    OpenClaw Gateway RPC 桥接层。

    通过 `openclaw gateway call` CLI 发送 RPC 请求到 Gateway。
    每个工作流运行使用独立的 session namespace，保持对话上下文。
    """

    def __init__(
        self,
        config: Optional[GatewayConfig] = None,
        session_namespace: Optional[str] = None,
        agent_id: str = "main",
        log_callback: Optional[Callable[[str, str], None]] = None,
    ):
        self.config = config or GatewayConfig.from_config()
        self.agent_id = agent_id
        self._log = log_callback or (lambda msg, level: print(f"[{level}] {msg}"))

        # 每个工作流运行有独立的 session namespace
        # 格式: agent:main:openclaw-workflow:<run_id>
        if session_namespace:
            self.session_namespace = session_namespace
        else:
            run_id = str(uuid.uuid4())[:8]
            self.session_namespace = f"openclaw-workflow:{run_id}"

        self._idempotency_counter = 0

        # 进程内跟踪已完成的 spawn session keys
        # Gateway 会覆写 sessions.json，导致 cleanup_session() 删除的 entry 被恢复
        # 因此用内存集合来准确跟踪哪些 spawn 已完成、不应计入并发
        self._completed_spawn_keys: set = set()

        # sessions.json 读取缓存 — 避免 wait_subagents 中 N 个 pending 项
        # 每轮 poll 都各自读一次 sessions.json（100 项 × 每 5 秒 = 灾难性 IO）
        # 缓存在每次 poll 循环开始时刷新一次，整轮复用
        self._session_index_cache: Optional[Dict[str, Any]] = None
        self._session_index_cache_ts: float = 0

        # child session key → session ID 持久映射
        # Gateway 在 subagent 完成后会从 sessions.json 中删除 subagent 条目，
        # 导致 get_session_id() 无法再通过 key 查找到 session ID。
        # 因此在 run_subagent 阶段拿到 child_session_key 后立即缓存其 session ID，
        # 供后续 wait_subagents 的策略 B 使用。
        self._child_session_id_cache: Dict[str, str] = {}

        # ── 工厂 session (Factory Pattern) ──
        # 循环中批量创建 subagent 时，复用单个 session 而非为每个 spawn 创建独立 session
        # 子会话模式: N subagent = N child session (session 即 subagent)
        # subagent 模式: N subagent = ≤ceil(N/rotate) factory + N child ≈ N + 几个
        self._factory_session_key: Optional[str] = None
        self._factory_lock = threading.Lock()
        self._factory_spawn_count: int = 0
        self._factory_total_expected: int = 0
        self._factory_rotate_every: int = 20
        self._factory_all_keys: List[str] = []
        self._factory_subagents: List[Dict[str, Any]] = []

    def _is_protected_session_key(self, session_key: str) -> bool:
        """
        返回该 session key 是否属于绝不允许删除的受保护会话。

        保护原则：
        - 永远不删除主对话会话 `agent:<id>:main`
        - 不碰非本工作流命名空间的普通会话
        """
        if not session_key:
            return True

        protected_main = f"agent:{self.agent_id}:main"
        if session_key == protected_main:
            return True

        return False

    # ── 工厂 Session 管理 ──────────────────────────────────

    @property
    def factory_session_key(self) -> Optional[str]:
        """当前工厂 session key，None 表示未开启工厂模式。"""
        return self._factory_session_key

    @property
    def factory_lock(self) -> threading.Lock:
        """工厂 session 的序列化锁。多线程并行循环中使用。"""
        return self._factory_lock

    def open_factory_session(self, total_expected: int = 0, rotate_every: int = 20) -> str:
        """
        开启工厂 session，用于批量创建 subagent。

        工厂模式优势:
        - 子会话模式: 100 subagent = 100 child session = 100 个
        - subagent 模式 (工厂): 100 subagent = ~5 factory (轮换) + 100 child = ~105 个

        Args:
            total_expected: 预计创建的 subagent 总数 (用于进度显示)
            rotate_every: 每 N 次 spawn 后轮换 factory session (控制上下文增长)

        Returns:
            factory session key
        """
        key = f"agent:{self.agent_id}:openclaw-workflow:factory:{uuid.uuid4().hex[:8]}"
        self._factory_session_key = key
        self._factory_spawn_count = 0
        self._factory_total_expected = total_expected
        self._factory_rotate_every = rotate_every
        self._factory_all_keys = [key]
        self._factory_subagents = []
        self._log(
            f"🏭 工厂 session 已开启: {key} "
            f"(预计 {total_expected} 个子代理, 每 {rotate_every} 个轮换)",
            "INFO",
        )
        return key

    def maybe_rotate_factory(self) -> None:
        """
        检查是否需要轮换工厂 session (上下文增长控制)。

        每次 spawn 都会向 factory session 添加 ~2 条消息 (user + assistant),
        累积 N 次后上下文会膨胀，导致 Agent 推理变慢且成本增加。
        定期轮换创建新的空 session 来避免此问题。

        应在 factory_lock 内调用。
        """
        if not self._factory_session_key:
            return
        if self._factory_rotate_every <= 0:
            return
        if (self._factory_spawn_count > 0
                and self._factory_spawn_count % self._factory_rotate_every == 0):
            new_key = f"agent:{self.agent_id}:openclaw-workflow:factory:{uuid.uuid4().hex[:8]}"
            self._factory_all_keys.append(new_key)
            self._factory_session_key = new_key
            self._log(
                f"🏭 工厂 session 轮换 (已创建 {self._factory_spawn_count} 个): {new_key}",
                "INFO",
            )

    def track_factory_subagent(
        self, child_session_key: str, child_run_id: str, label: str = ""
    ) -> None:
        """记录通过工厂创建的 subagent (用于状态追踪和进度监控)。"""
        import time as _time
        self._factory_subagents.append({
            "child_session_key": child_session_key,
            "child_run_id": child_run_id,
            "label": label,
            "created_at": _time.time(),
            "factory_key": self._factory_session_key,
        })

    def get_factory_stats(self) -> Dict[str, Any]:
        """获取工厂 session 统计信息。"""
        return {
            "total_spawned": self._factory_spawn_count,
            "total_expected": self._factory_total_expected,
            "factory_sessions_used": len(self._factory_all_keys),
            "subagents_tracked": len(self._factory_subagents),
        }

    def get_factory_child_session_keys(self) -> List[str]:
        """返回工厂模式下已追踪的 child session keys。"""
        keys: List[str] = []
        for item in self._factory_subagents:
            if not isinstance(item, dict):
                continue
            ck = item.get("child_session_key", "")
            if ck:
                keys.append(ck)
        return keys

    def close_factory_session(self) -> None:
        """
        关闭工厂 session (重置内部状态)。

        注意: 不会立即删除 factory session 的 JSONL 文件,
        因为 wait_subagents 步骤可能需要读取 factory session
        中的 auto-announce completion event (策略 A)。
        实际清理由 cleanup_workflow_sessions() 在工作流结束时统一执行。
        """
        if not self._factory_session_key:
            return
        stats = self.get_factory_stats()
        self._log(
            f"🏭 工厂 session 已关闭: "
            f"创建 {stats['total_spawned']}/{stats['total_expected']} 个子代理, "
            f"使用 {stats['factory_sessions_used']} 个 factory session",
            "INFO",
        )
        # 重置状态但不删除 session (wait_subagents 可能需要读取)
        self._factory_session_key = None
        self._factory_spawn_count = 0
        self._factory_total_expected = 0
        # 保留 _factory_all_keys 和 _factory_subagents 供 cleanup_workflow_sessions 使用

    def refresh_session_index_cache(self) -> Dict[str, Any]:
        """刷新 sessions.json 缓存，返回完整索引。"""
        import time as _time
        try:
            with open(self.sessions_index_path, "r") as f:
                self._session_index_cache = json.load(f)
            self._session_index_cache_ts = _time.time()
        except Exception:
            self._session_index_cache = {}
        return self._session_index_cache

    def invalidate_session_cache(self) -> None:
        """使缓存失效。"""
        self._session_index_cache = None

    @property
    def session_key(self) -> str:
        """当前会话键"""
        return f"agent:{self.agent_id}:{self.session_namespace}"

    def _next_idempotency_key(self) -> str:
        """生成唯一的幂等键"""
        self._idempotency_counter += 1
        return f"{self.session_namespace}:{self._idempotency_counter}"

    # ── 核心 RPC 调用 ─────────────────────────────────────

    def _call_gateway(
        self,
        method: str,
        params: Dict[str, Any],
        timeout_ms: Optional[int] = None,
        expect_final: bool = True,
    ) -> Dict[str, Any]:
        """
        调用 Gateway RPC 方法。

        底层执行: openclaw gateway call <method> --params <json> [--expect-final]
        """
        timeout_ms = timeout_ms or self.config.timeout_ms

        cmd = ["openclaw", "gateway", "call", method, "--json"]
        cmd.extend(["--params", json.dumps(params, ensure_ascii=False)])
        cmd.extend(["--timeout", str(timeout_ms)])

        if self.config.token:
            cmd.extend(["--token", self.config.token])

        if expect_final:
            cmd.append("--expect-final")

        timeout_sec = (timeout_ms / 1000) + 15  # CLI 额外缓冲

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )

            stdout = result.stdout.strip()
            if result.returncode == 0 and stdout:
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError:
                    return {"error": f"无法解析响应: {stdout[:500]}"}
            else:
                stderr = result.stderr.strip()
                return {"error": stderr or stdout or "Gateway 调用失败"}

        except subprocess.TimeoutExpired:
            return {"error": f"Gateway 调用超时 ({timeout_sec}s)"}
        except FileNotFoundError:
            return {"error": "openclaw CLI 未安装或不在 PATH 中"}

    # ── Agent 调用 ────────────────────────────────────────

    def agent_call(
        self,
        message: str,
        session_key: Optional[str] = None,
        thinking: str = "",
        timeout_ms: Optional[int] = None,
        expect_final: bool = True,
    ) -> AgentResponse:
        """
        通过 Gateway 调用 Agent (复用会话上下文)。

        这是 LLM/Agent 节点的底层调用。
        同一个 session_key 内的多次调用共享对话上下文,
        Agent 能看到工作流之前步骤的对话记录。

        Args:
            expect_final: 是否等待 Agent 完成响应。
                True (默认): 使用 --expect-final，同步等待完整结果。
                False: 发送消息后立即返回，Agent 在后台处理。
                用于子会话模式 wait=false 的异步执行。
        """
        key = session_key or self.session_key
        idem_key = self._next_idempotency_key()

        self._log(f"Gateway RPC: agent (session={key})", "DEBUG")

        params: Dict[str, Any] = {
            "idempotencyKey": idem_key,
            "message": message,
            "sessionKey": key,
        }
        if thinking:
            params["thinking"] = thinking

        data = self._call_gateway("agent", params, timeout_ms=timeout_ms, expect_final=expect_final)

        if "error" in data and "runId" not in data:
            return AgentResponse(success=False, error=str(data["error"]))

        # 解析标准 Agent 响应
        try:
            payloads = data.get("result", {}).get("payloads", [])
            text = "\n".join(p.get("text", "") for p in payloads if p.get("text"))
            meta = data.get("result", {}).get("meta", {})
            agent_meta = meta.get("agentMeta", {})

            return AgentResponse(
                success=data.get("status") == "ok",
                text=text,
                run_id=data.get("runId", ""),
                session_id=agent_meta.get("sessionId", ""),
                session_key=key,
                model=agent_meta.get("model", ""),
                usage=agent_meta.get("usage", {}),
                raw=data,
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"解析响应失败: {e}",
                raw=data,
            )

    # ── 健康检查 ──────────────────────────────────────────

    def health(self) -> Dict[str, Any]:
        """检查 Gateway 健康状态"""
        return self._call_gateway("health", {}, timeout_ms=5000, expect_final=False)

    def is_available(self) -> bool:
        """Gateway 是否可用"""
        result = self.health()
        return result.get("ok", False) is True

    # ── Session 文件读取 (子代理完成检测) ─────────────────

    @property
    def sessions_dir(self) -> Path:
        """Session 文件存储目录"""
        return Path(os.path.expanduser(
            f"~/.openclaw/agents/{self.agent_id}/sessions"
        ))

    @property
    def sessions_index_path(self) -> Path:
        """Session 索引文件路径"""
        return self.sessions_dir / "sessions.json"

    def get_session_id(self, session_key: str) -> Optional[str]:
        """
        通过 sessionKey 查找 sessionId。

        优先使用内存缓存 (refresh_session_index_cache 刷新)，
        缓存未命中时 fallback 到直接读文件。
        """
        # 先查缓存
        if self._session_index_cache is not None:
            entry = self._session_index_cache.get(session_key)
            if entry:
                return entry.get("sessionId")
            return None

        # 无缓存时读文件
        try:
            with open(self.sessions_index_path, "r") as f:
                index = json.load(f)
            entry = index.get(session_key)
            if entry:
                return entry.get("sessionId")
        except Exception as e:
            self._log(f"读取 sessions.json 失败: {e}", "WARN")
        return None

    def find_subagent_completion(
        self,
        parent_session_key: str,
        child_session_key: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        检测子代理是否已完成并提取结果。

        使用两级检测策略:

        策略 A (精确): 读取 parent (spawn) session 的 JSONL，查找 auto-announce
        完成事件。仅在 wait=true 或 spawn session 未被清理时可用。

        策略 B (直读): 直接读取 child session 的 JSONL，检查子代理是否已产出
        assistant 回复。这是 wait=false 模式的主要检测路径，因为 spawn session
        在 run_subagent 返回时已被清理。

        Returns:
            (found, status, result_text)
            - found: 是否找到完成事件
            - status: "completed successfully" | "completed" | "failed" | None
            - result_text: 子代理的输出文本 | None
        """
        # ── 策略 A: 从 parent (spawn) session 的 auto-announce 检测 ──
        result = self._find_completion_from_parent(parent_session_key, child_session_key)
        if result[0]:
            return result

        # ── 策略 B: 直接读取 child session JSONL 检测 ──
        # wait=false 模式下 spawn session 已被清理，无法走策略 A
        # 子代理完成后，其 JSONL 中必有 assistant 回复
        return self._find_completion_from_child(child_session_key)

    def _find_completion_from_parent(
        self,
        parent_session_key: str,
        child_session_key: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """策略 A: 从 parent session 的 auto-announce 事件检测完成。"""
        # 快速路径: 已知已清理的 spawn session，跳过所有 IO
        if parent_session_key in self._completed_spawn_keys:
            return False, None, None
        session_id = self.get_session_id(parent_session_key)
        if not session_id:
            return False, None, None

        jsonl_path = self.sessions_dir / f"{session_id}.jsonl"
        if not jsonl_path.exists():
            return False, None, None

        try:
            with open(jsonl_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if entry.get("type") != "message":
                        continue

                    msg = entry.get("message", {})

                    # 检查 provenance 来精确匹配子代理完成事件
                    prov = msg.get("provenance", {})
                    if (prov.get("sourceSessionKey") == child_session_key
                            and prov.get("sourceTool") == "subagent_announce"):
                        content = msg.get("content", [])
                        if isinstance(content, list):
                            for c in content:
                                text = c.get("text", "")
                                if "Internal task completion event" in text:
                                    status = self._extract_field(text, "status")
                                    result = self._extract_child_result(text)
                                    return True, status, result

                    # 备用: 没有 provenance 但内容中包含对应 session_key
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            text = c.get("text", "")
                            if ("Internal task completion event" in text
                                    and child_session_key in text):
                                status = self._extract_field(text, "status")
                                result = self._extract_child_result(text)
                                return True, status, result

        except Exception as e:
            self._log(f"读取 parent session JSONL 失败: {e}", "WARN")

        return False, None, None

    def _find_completion_from_child(
        self,
        child_session_key: str,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        策略 B: 直接读取 child session JSONL 检测完成。

        子代理的 JSONL 结构:
        - session header / model_change 等元数据
        - user message (任务 prompt)
        - assistant message (分类结果)  ← 有这个就说明完成了

        这是 wait=false 模式的主要检测路径。
        """
        # 优先从内存缓存获取 session_id
        # Gateway 在 subagent 完成后会从 sessions.json 中移除条目，
        # 导致 get_session_id() 返回 None，此时必须依赖预先缓存的映射
        session_id = self._child_session_id_cache.get(child_session_key)
        if not session_id:
            session_id = self.get_session_id(child_session_key)
            if session_id:
                self._child_session_id_cache[child_session_key] = session_id
        if not session_id:
            return False, None, None

        jsonl_path = self.sessions_dir / f"{session_id}.jsonl"
        if not jsonl_path.exists():
            # Gateway 清理 subagent session 时会将 JSONL 文件 rename 为
            # {session_id}.jsonl.deleted.{timestamp} 而非真正删除。
            # 搜索这种 renamed 文件以恢复读取能力。
            import glob
            deleted_pattern = str(self.sessions_dir / f"{session_id}.jsonl.deleted.*")
            deleted_files = glob.glob(deleted_pattern)
            if deleted_files:
                # 取最新的一个（按文件名排序，timestamp 在后缀中）
                jsonl_path = Path(sorted(deleted_files)[-1])
            else:
                return False, None, None

        try:
            has_user = False
            last_assistant_text = None

            with open(jsonl_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if entry.get("type") != "message":
                        continue

                    msg = entry.get("message", {})
                    role = msg.get("role", "")

                    if role == "user":
                        has_user = True
                    elif role == "assistant" and has_user:
                        # 提取 assistant 回复文本
                        content = msg.get("content", [])
                        if isinstance(content, list):
                            texts = []
                            for c in content:
                                if isinstance(c, dict) and c.get("type") == "text":
                                    texts.append(c.get("text", ""))
                                elif isinstance(c, dict) and c.get("type") == "thinking":
                                    pass  # 跳过 thinking blocks
                            if texts:
                                last_assistant_text = "\n".join(texts).strip()
                        elif isinstance(content, str) and content.strip():
                            last_assistant_text = content.strip()

            if has_user and last_assistant_text is not None:
                self._log(
                    f"策略B: 从 child session 直接检测到完成 "
                    f"(child={child_session_key[:30]}…, "
                    f"结果长度={len(last_assistant_text)})",
                    "DEBUG",
                )
                return True, "completed", last_assistant_text

        except Exception as e:
            self._log(f"读取 child session JSONL 失败: {e}", "WARN")

        return False, None, None

    @staticmethod
    def _extract_child_result(text: str) -> Optional[str]:
        """从完成事件文本中提取子代理的返回结果"""
        m = re.search(
            r"<<<BEGIN_UNTRUSTED_CHILD_RESULT>>>\s*(.*?)\s*<<<END_UNTRUSTED_CHILD_RESULT>>>",
            text,
            re.DOTALL,
        )
        return m.group(1).strip() if m else None

    @staticmethod
    def _extract_field(text: str, field_name: str) -> Optional[str]:
        """从事件文本中提取字段值 (如 'status: completed successfully')"""
        m = re.search(rf"^{field_name}:\s*(.+)$", text, re.MULTILINE)
        return m.group(1).strip() if m else None

    def mark_spawn_completed(self, spawn_session_key: str) -> None:
        """
        标记 spawn session 已完成。

        由于 Gateway 拥有 sessions.json 并会覆写我们的删除操作，
        必须在进程内存中跟踪已完成的 spawn，以便 count_active_subagents()
        能正确排除它们。
        """
        self._completed_spawn_keys.add(spawn_session_key)

    def cache_child_session_id(self, child_session_key: str) -> Optional[str]:
        """
        缓存 child session 的 session ID。

        在 run_subagent 创建子代理后立即调用，从 sessions.json 中查找并缓存
        child_session_key → sessionId 的映射。
        Gateway 后续可能从 sessions.json 中删除此条目（subagent 完成后自动清理），
        但缓存始终有效。

        Returns:
            缓存的 session_id 或 None
        """
        if child_session_key in self._child_session_id_cache:
            return self._child_session_id_cache[child_session_key]

        session_id = self.get_session_id(child_session_key)
        if session_id:
            self._child_session_id_cache[child_session_key] = session_id
        return session_id

    # ── Session 清理 ────────────────────────────────────────

    def cleanup_session(self, session_key: str) -> bool:
        """
        删除单个 session (从 sessions.json 索引 + JSONL 文件)。

        由于 Gateway 没有 session destroy RPC，我们直接操作文件系统:
        1. 从 sessions.json 移除 entry
        2. 删除对应的 .jsonl 文件 (如果存在)

        Returns:
            True 如果成功清理, False 如果 session 不存在或失败
        """
        if self._is_protected_session_key(session_key):
            self._log(f"跳过受保护 session: {session_key}", "DEBUG")
            return False

        try:
            index_path = self.sessions_index_path
            if not index_path.exists():
                return False

            with open(index_path, "r") as f:
                index = json.load(f)

            entry = index.pop(session_key, None)
            if entry is None:
                return False

            # 删除 JSONL 文件
            session_id = entry.get("sessionId", "")
            if session_id:
                jsonl_path = self.sessions_dir / f"{session_id}.jsonl"
                if jsonl_path.exists():
                    jsonl_path.unlink()

            # 写回 sessions.json
            with open(index_path, "w") as f:
                json.dump(index, f, ensure_ascii=False)

            return True
        except Exception as e:
            self._log(f"清理 session {session_key} 失败: {e}", "WARN")
            return False

    def cleanup_subagent_sessions(
        self,
        tracker: List[Dict[str, Any]],
        log_func: Optional[Callable] = None,
    ) -> Dict[str, int]:
        """
        批量清理 subagent 相关的 session (spawn + child)。

        每个 subagent 创建时产生 2 个 session:
        - spawn session: agent:main:openclaw-workflow:spawn:<hex>
        - child session: agent:main:subagent:<uuid>

        Args:
            tracker: subagent tracker 列表，每项包含 spawn_session_key 和 child_session_key
            log_func: 可选的日志回调

        Returns:
            {"cleaned": N, "failed": N, "total": N}
        """
        _log = log_func or self._log
        cleaned = 0
        failed = 0
        keys_to_remove = []

        # 收集所有需要清理的 session keys (去重)
        seen = set()
        for item in tracker:
            sk = item.get("spawn_session_key", "")
            ck = item.get("child_session_key", "")
            if sk and sk not in seen and not self._is_protected_session_key(sk):
                keys_to_remove.append(sk)
                seen.add(sk)
            if ck and ck not in seen and not self._is_protected_session_key(ck):
                keys_to_remove.append(ck)
                seen.add(ck)

        if not keys_to_remove:
            return {"cleaned": 0, "failed": 0, "total": 0}

        # 批量删除: 一次读写 sessions.json
        try:
            index_path = self.sessions_index_path
            with open(index_path, "r") as f:
                index = json.load(f)

            for key in keys_to_remove:
                entry = index.pop(key, None)
                if entry:
                    session_id = entry.get("sessionId", "")
                    if session_id:
                        jsonl_path = self.sessions_dir / f"{session_id}.jsonl"
                        try:
                            if jsonl_path.exists():
                                jsonl_path.unlink()
                        except Exception:
                            pass
                    cleaned += 1
                else:
                    failed += 1

            with open(index_path, "w") as f:
                json.dump(index, f, ensure_ascii=False)

        except Exception as e:
            _log(f"批量清理 sessions 失败: {e}", "WARN")
            return {"cleaned": cleaned, "failed": len(keys_to_remove), "total": len(keys_to_remove)}

        _log(f"🧹 已清理 {cleaned} 个 session ({len(tracker)} 个 subagent)", "INFO")
        return {"cleaned": cleaned, "failed": failed, "total": len(keys_to_remove)}

    def get_subagent_concurrency_limit(self) -> int:
        """
        从 openclaw.json 读取 subagent 并发限制。

        综合考虑两个限制:
        - agents.defaults.subagents.maxConcurrent (子代理专属限制, 默认 20)
        - agents.defaults.maxConcurrent (Gateway 嵌入式运行全局并发限制, 默认 4)

        取两者中较小值作为实际限制，因为 Gateway 嵌入式运行 (nested lane)
        受全局并发限制约束。即使 subagents.maxConcurrent=20，
        如果 agents.defaults.maxConcurrent=4，实际只能同时运行 4 个。
        """
        try:
            config_path = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
            if not config_path.exists():
                return 4
            with open(config_path, "r") as f:
                data = json.load(f)
            defaults = data.get("agents", {}).get("defaults", {})
            subagent_max = defaults.get("subagents", {}).get("maxConcurrent", 20)
            # Gateway 全局嵌入式运行并发限制 — 这是真正的瓶颈
            global_max = defaults.get("maxConcurrent", 4)
            # 取较小值，确保不超过 Gateway 实际处理能力
            effective = min(subagent_max, global_max)
            self._log(f"并发限制: subagent={subagent_max}, global={global_max}, effective={effective}", "DEBUG")
            return effective
        except Exception:
            return 4

    def count_active_subagents(self, max_age_sec: int = 180) -> int:
        """
        统计当前正在进行中的 spawn 调用数。

        只计数 agent:*:openclaw-workflow:spawn:* session。

        设计原则:
        - spawn 占位 session 由我们创建，在 agent_call() 返回后立即 cleanup_session()
        - 因此它存在 ⟺ 对应的 Gateway nested lane 调用正在进行中
        - 完成后立刻消失，不会误判

        不计数 agent:*:subagent:* 的原因:
        - 子代理 session 在子代理完成后仍然保留在 sessions.json 里，不会自动消失
        - wait=false 模式下子代理 3-7s 即完成，但 session 残留 → 被误算为"活跃"
        - 导致并发计数器永远饱和，所有后续 spawn 都被 throttle 300s

        Args:
            max_age_sec: spawn session 的最大存活时间 (秒)，超过此时间视为残留不计入
        """
        import time as _time
        try:
            now_ms = int(_time.time() * 1000)
            cutoff_ms = now_ms - (max_age_sec * 1000)

            with open(self.sessions_index_path, "r") as f:
                index = json.load(f)
            count = 0
            for k, v in index.items():
                # 只计数 spawn 占位 session（生命周期受我们精确控制）
                if ":openclaw-workflow:spawn:" not in k:
                    continue
                # 排除已完成的 spawn（Gateway 覆写 sessions.json 导致
                # cleanup_session 删除的 entry 被恢复，所以用内存集合判断）
                if k in self._completed_spawn_keys:
                    continue
                updated_at = v.get("updatedAt", 0)
                if updated_at > cutoff_ms:
                    count += 1
            return count
        except Exception:
            return 0

    def cleanup_workflow_sessions(self, extra_spawn_keys: Optional[List[str]] = None) -> Dict[str, int]:
        """
        清理当前工作流运行产生的所有 session 残留。

        应在工作流结束时 (无论成功/失败) 调用。清理:
        1. 工作流运行 session (agent:main:openclaw-workflow:<ns>)
        2. 所有 spawn 占位 session (agent:main:openclaw-workflow:spawn:*)
        3. extra_spawn_keys 中额外指定的 key (如 context 中记录的)

        注意:
        - 这里绝不能删除 `agent:<id>:main` 这样的主会话
        - 这里只清理由本工作流 skill 创建的隔离/占位 session

        Returns:
            {"cleaned": N, "total": N}
        """
        cleaned = 0
        total = 0
        try:
            index_path = self.sessions_index_path
            with open(index_path, "r") as f:
                index = json.load(f)

            keys_to_remove = []

            # 1) 工作流主 session
            main_key = self.session_key
            if main_key in index and not self._is_protected_session_key(main_key):
                keys_to_remove.append(main_key)

            # 2) 所有 spawn 占位 session (由本 skill 创建，命名模式固定)
            spawn_prefix = f"agent:{self.agent_id}:openclaw-workflow:spawn:"
            for k in list(index.keys()):
                if k.startswith(spawn_prefix) and not self._is_protected_session_key(k):
                    keys_to_remove.append(k)

            # 2b) 所有 factory session (工厂模式创建)
            factory_prefix = f"agent:{self.agent_id}:openclaw-workflow:factory:"
            for k in list(index.keys()):
                if k.startswith(factory_prefix) and not self._is_protected_session_key(k):
                    keys_to_remove.append(k)

            # 2c) 所有 child session (子会话模式创建)
            child_prefix = f"agent:{self.agent_id}:openclaw-workflow:child:"
            for k in list(index.keys()):
                if k.startswith(child_prefix) and not self._is_protected_session_key(k):
                    keys_to_remove.append(k)
            # 也清理本次运行记录的所有 factory keys
            for k in self._factory_all_keys:
                if k and k in index and k not in keys_to_remove:
                    keys_to_remove.append(k)

            # 3) 额外指定的 keys
            if extra_spawn_keys:
                for k in extra_spawn_keys:
                    if k and k in index and k not in keys_to_remove and not self._is_protected_session_key(k):
                        keys_to_remove.append(k)

            total = len(keys_to_remove)
            for key in keys_to_remove:
                entry = index.pop(key, None)
                if entry:
                    session_id = entry.get("sessionId", "")
                    if session_id:
                        jsonl_path = self.sessions_dir / f"{session_id}.jsonl"
                        try:
                            if jsonl_path.exists():
                                jsonl_path.unlink()
                        except Exception:
                            pass
                    cleaned += 1

            with open(index_path, "w") as f:
                json.dump(index, f, ensure_ascii=False)

            if cleaned > 0:
                self._log(f"🧹 工作流 session 清理: 删除 {cleaned}/{total} 个 (主={main_key})", "INFO")
        except Exception as e:
            self._log(f"清理工作流 sessions 失败: {e}", "WARN")

        return {"cleaned": cleaned, "total": total}

    def extract_spawn_info(self, agent_response: "AgentResponse") -> Dict[str, str]:
        """
        从 Agent 响应中提取 sessions_spawn 的返回信息。

        Gateway --expect-final 模式下 payloads 只有最终 text,
        不含中间 tool call/result。所以需要多策略提取:

        1. 从 raw payloads 找 toolResult (有时 Gateway 会包含)
        2. 从整个 raw JSON 中找 JSON 格式的 childSessionKey
        3. 从 agent text 中直接匹配 agent:main:subagent:<uuid> 模式
        """
        info: Dict[str, str] = {}

        # 策略 1: 从 raw 数据中查找 toolResult
        try:
            raw = agent_response.raw
            payloads = raw.get("result", {}).get("payloads", [])
            for payload in payloads:
                for key in ("toolResult", "tool_result"):
                    tr = payload.get(key)
                    if tr and isinstance(tr, dict) and "childSessionKey" in tr:
                        info["child_session_key"] = tr.get("childSessionKey", "")
                        info["child_run_id"] = tr.get("runId", "")
                        info["mode"] = tr.get("mode", "")
                        return info
        except Exception:
            pass

        # 策略 2: 从整个 raw JSON 中找 childSessionKey 的 JSON 格式
        raw_str = json.dumps(agent_response.raw, ensure_ascii=False)
        if "childSessionKey" in raw_str:
            try:
                m = re.search(r'"childSessionKey"\s*:\s*"([^"]+)"', raw_str)
                if m:
                    info["child_session_key"] = m.group(1)
                m2 = re.search(r'"runId"\s*:\s*"([^"]+)"', raw_str)
                if m2:
                    info["child_run_id"] = m2.group(1)
                if info:
                    return info
            except Exception:
                pass

        # 策略 3: 从 text 和 raw JSON 中直接匹配 subagent session key 模式
        # Agent 常以 markdown 格式返回: `agent:main:subagent:uuid`
        # 也可能出现在 raw JSON 的 payloads text 中
        text = agent_response.text
        _subagent_key_re = re.compile(
            r'agent:[a-zA-Z0-9_-]+:subagent:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        )
        _uuid_re = re.compile(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        )

        # 搜索 text 和 raw JSON
        for source in [text, raw_str]:
            if not source:
                continue
            m = _subagent_key_re.search(source)
            if m:
                info["child_session_key"] = m.group(0)
                # 找 runId — 优先找标记的，否则找所有 UUID 中排除 child_session_key 中已有的
                m2 = re.search(
                    r'(?:运行ID|runId|Run\s*ID|任务ID)[^\n]*?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})',
                    source,
                    re.IGNORECASE,
                )
                if m2:
                    info["child_run_id"] = m2.group(1)
                return info

        return info

    def extract_spawn_info_from_session_log(self, spawn_session_key: str) -> Dict[str, str]:
        """
        从 spawn session 的 JSONL 日志中直接提取 childSessionKey。

        当 Gateway --expect-final 返回空文本或 Agent 未在文本中包含 key 时,
        我们可以直接读取 spawn session 的 JSONL 找 sessions_spawn 的 toolResult。
        这是最可靠的方式，因为 JSONL 包含完整的工具调用记录。

        注意: 工厂模式下同一个 session 中会有多次 sessions_spawn 调用,
        因此必须返回最后一个 toolResult (最新的 spawn)，而非第一个。
        """
        all_info = self.extract_all_spawn_info_from_session_log(spawn_session_key)
        return all_info[-1] if all_info else {}

    def extract_all_spawn_info_from_session_log(
        self, session_key: str
    ) -> List[Dict[str, str]]:
        """
        从 session 的 JSONL 日志中提取所有 sessions_spawn 的 toolResult。

        批量 spawn 模式下，一次 agent_call 可能触发 Agent 同时调用多个
        sessions_spawn 工具，JSONL 中会有多条 toolResult 记录。

        Returns:
            按出现顺序排列的 spawn info 列表，每项包含:
            - child_session_key: 子代理 session key
            - child_run_id: 子代理 run ID
            - mode: 运行模式
        """
        results: List[Dict[str, str]] = []
        try:
            session_id = self.get_session_id(session_key)
            if not session_id:
                return results

            jsonl_path = self.sessions_dir / f"{session_id}.jsonl"
            if not jsonl_path.exists():
                return results

            with open(jsonl_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    msg = entry.get("message", {})
                    if msg.get("role") != "toolResult":
                        continue
                    if msg.get("toolName") != "sessions_spawn":
                        continue
                    # 跳过错误的 toolResult
                    if msg.get("isError"):
                        continue
                    content = msg.get("content", [])
                    if isinstance(content, list):
                        for c in content:
                            text = c.get("text", "")
                            if "childSessionKey" in text:
                                try:
                                    data = json.loads(text)
                                    results.append({
                                        "child_session_key": data.get("childSessionKey", ""),
                                        "child_run_id": data.get("runId", ""),
                                        "mode": data.get("mode", ""),
                                    })
                                except json.JSONDecodeError:
                                    candidate: Dict[str, str] = {}
                                    m = re.search(r'"childSessionKey"\s*:\s*"([^"]+)"', text)
                                    if m:
                                        candidate["child_session_key"] = m.group(1)
                                    m2 = re.search(r'"runId"\s*:\s*"([^"]+)"', text)
                                    if m2:
                                        candidate["child_run_id"] = m2.group(1)
                                    if candidate:
                                        results.append(candidate)
        except Exception as e:
            self._log(f"从 session log 提取 spawn info 失败: {e}", "WARN")

        return results


def get_bridge(
    session_namespace: Optional[str] = None,
    agent_id: str = "main",
    log_callback: Optional[Callable] = None,
) -> GatewayBridge:
    """获取一个 Gateway Bridge 实例"""
    return GatewayBridge(
        session_namespace=session_namespace,
        agent_id=agent_id,
        log_callback=log_callback,
    )
