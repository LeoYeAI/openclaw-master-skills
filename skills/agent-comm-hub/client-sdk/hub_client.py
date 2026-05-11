#!/usr/bin/env python3
"""
hub_client.py — Agent Synergy Hub Python SDK (Phase 2)

功能：
  1. Agent 注册（邀请码）+ Token 管理
  2. MCP 工具调用封装（HTTP POST /mcp，含 initialize 握手）
  3. SSE 长连接订阅（自动重连 + 客户端去重）
  4. 记忆存储/召回（支持溯源字段 source_agent_id/source_task_id）
  5. 事件路由（new_message / task_assigned / task_updated）
  6. 信任分管理（set_trust_score，admin only）
  7. Agent 查询（支持 role/capability 筛选）

用法：
  from hub_client import SynergyHubClient

  hub = SynergyHubClient(hub_url="http://localhost:3100")

  # 注册
  result = hub.register(invite_code="abc12345", name="my_agent")
  hub.set_token(result["api_token"])

  # 心跳
  hub.heartbeat()

  # 消息
  hub.send_message(to="other_agent", content="Hello!")

  # 记忆
  hub.store_memory(content="重要信息", scope="collective")

  # SSE 订阅
  hub.on_message = lambda msg: print(f"收到: {msg}")
  hub.connect_sse()  # 阻塞

设计原则：
  - 零外部依赖（仅 stdlib）
  - MCP Streamable HTTP Transport 无状态模式
  - 客户端去重（_hub_event_id）
  - SSE 指数退避重连
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import http.client
import socket

# ─── 日志 ──────────────────────────────────────────────────────────

logger = logging.getLogger("hub_client")

# ─── 类型 ──────────────────────────────────────────────────────────

MessageHandler = Callable[[Dict[str, Any]], None]
TaskHandler = Callable[[Dict[str, Any]], None]
TaskUpdateHandler = Callable[[Dict[str, Any]], None]


class HubError(Exception):
    """Hub SDK 错误基类"""
    def __init__(self, message: str, code: int = 0):
        super().__init__(message)
        self.code = code


class AuthError(HubError):
    """认证错误 (401/403)"""
    pass


class RateLimitError(HubError):
    """速率限制 (429)"""
    pass


class ToolError(HubError):
    """MCP 工具调用错误"""
    pass


# ─── SynergyHubClient ──────────────────────────────────────────────

class SynergyHubClient:
    """
    Agent Synergy Hub 客户端

    覆盖 MCP 工具调用 + SSE 事件订阅 + 客户端去重
    """

    def __init__(
        self,
        hub_url: str = "http://localhost:3100",
        agent_id: Optional[str] = None,
        token: Optional[str] = None,
        reconnect_base: float = 2.0,
        reconnect_max: float = 60.0,
        sse_timeout: int = 90,
        mcp_timeout: int = 15,
    ):
        self.hub_url = hub_url.rstrip("/")
        self.agent_id = agent_id
        self._token = token
        self._role: Optional[str] = None

        # SSE 配置
        self._reconnect_base = reconnect_base
        self._reconnect_max = reconnect_max
        self._sse_timeout = sse_timeout
        self._mcp_timeout = mcp_timeout

        # SSE 状态
        self._sse_running = False
        self._sse_thread: Optional[threading.Thread] = None
        self._reconnect_delay = reconnect_base

        # 客户端去重（_hub_event_id）
        self._seen_event_ids: set[int] = set()
        self._seen_event_ids_lock = threading.Lock()
        self._seen_event_ids_ordered: list[int] = []  # 有序列表，用于按插入顺序清理
        self._dedup_max_size = 10000  # 防止内存泄漏

        # SSE 断线重连：Last-Event-ID 跟踪
        self._last_event_id: Optional[str] = None
        self._last_event_id_lock = threading.Lock()

        # 事件回调
        self.on_message: Optional[MessageHandler] = None
        self.on_task_assigned: Optional[TaskHandler] = None
        self.on_task_updated: Optional[TaskUpdateHandler] = None

        # MCP 连接状态（无状态模式，无需 session）
        self._initialized = False
        self._init_lock = threading.Lock()

    # ── 属性 ─────────────────────────────────────────────

    @property
    def token(self) -> Optional[str]:
        return self._token

    @property
    def role(self) -> Optional[str]:
        return self._role

    @property
    def is_connected(self) -> bool:
        return self._sse_running

    # ── Token 管理 ───────────────────────────────────────

    def set_token(self, token: str) -> None:
        """设置 API Token（注册后调用）"""
        self._token = token
        self._initialized = False  # 重新握手

    # ── 底层 HTTP ────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[dict] = None,
        headers: Optional[dict] = None,
        timeout: Optional[int] = None,
    ) -> bytes:
        """底层 HTTP 请求"""
        url = f"{self.hub_url}{path}"
        req_headers = headers or {}

        if data is not None:
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            req_headers.setdefault("Content-Type", "application/json")
        else:
            body = None

        req = Request(url, data=body, method=method, headers=req_headers)
        t = timeout or self._mcp_timeout

        try:
            with urlopen(req, timeout=t) as resp:
                return resp.read()
        except HTTPError as e:
            if e.code in (401, 403):
                raise AuthError(f"Authentication failed: {e.code}", e.code)
            if e.code == 429:
                raise RateLimitError("Rate limit exceeded", 429)
            raise HubError(f"HTTP {e.code}: {e.reason}", e.code)
        except URLError as e:
            raise HubError(f"Connection error: {e.reason}")
        except Exception as e:
            raise HubError(f"Request failed: {e}")

    def _auth_headers(self) -> dict:
        """构建认证请求头"""
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    # ── MCP 协议 ─────────────────────────────────────────

    def _ensure_initialized(self) -> None:
        """确保 MCP 握手完成（线程安全）"""
        if self._initialized:
            return

        with self._init_lock:
            if self._initialized:
                return
            self._do_initialize()

    def _do_initialize(self) -> None:
        """执行 MCP initialize 握手"""
        # Step 1: initialize
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {
                    "name": f"hub-client-python-{self.agent_id or 'unknown'}",
                    "version": "1.0.0",
                },
            },
        }

        resp_body = self._raw_mcp(init_payload)

        if "error" in resp_body:
            raise HubError(f"MCP initialize failed: {resp_body['error']}")

        logger.debug("MCP initialized (stateless)")

        # Step 2: initialized 通知
        notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        self._raw_mcp(notif)

        self._initialized = True

    def _raw_mcp(self, payload: dict) -> dict:
        """
        底层 MCP POST 请求
        处理 SSE 格式响应（text/event-stream）和普通 JSON 响应
        """
        raw = self._request("POST", "/mcp", data=payload, headers=self._auth_headers())
        text = raw.decode("utf-8", errors="replace")

        # 尝试 SSE 格式解析
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("data: "):
                json_str = line[6:]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        # 尝试直接 JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"raw": text}

    def _call_tool(self, tool_name: str, args: dict) -> Any:
        """
        调用 MCP 工具
        自动处理 initialize 握手、响应解析、错误检查
        """
        self._ensure_initialized()

        payload = {
            "jsonrpc": "2.0",
            "id": uuid.uuid4().hex,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": args},
        }

        resp = self._raw_mcp(payload)

        # 错误处理
        if "error" in resp:
            err = resp["error"]
            msg = err.get("message", str(err))
            code = err.get("code", -1)
            raise ToolError(f"MCP tool [{tool_name}] error: {msg}", code)

        # 从 result.content[0].text 提取结果
        result = resp.get("result")
        if isinstance(result, dict):
            content = result.get("content", [])
            if content and isinstance(content, list) and len(content) > 0:
                item = content[0]
                # 如果 content item 是错误类型
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    if text:
                        # 检查是否是错误消息（MCP tool handler 抛出的 Error）
                        error_prefixes = ("Error:", "error:", "Permission denied", "Authentication required", "MCP error")
                        if any(text.startswith(p) for p in error_prefixes):
                            raise ToolError(f"MCP tool [{tool_name}] error: {text}")
                        try:
                            return json.loads(text)
                        except json.JSONDecodeError:
                            return text
            return result

        # resp 本身可能是直接的 JSON 结果（某些边缘情况）
        if isinstance(resp, dict) and "raw" in resp and "result" not in resp:
            raw_text = resp.get("raw", "")
            try:
                return json.loads(raw_text)
            except (json.JSONDecodeError, TypeError):
                return raw_text

        return resp

    # ═══════════════════════════════════════════════════════
    # 对外 API — 注册 / 心跳 / 查询
    # ═══════════════════════════════════════════════════════

    def register(self, invite_code: str, name: str, agent_id: Optional[str] = None) -> dict:
        """
        注册新 Agent

        Args:
            invite_code: 管理员生成的邀请码
            name: Agent 显示名称
            agent_id: 可选的自定义 Agent ID（不传则自动生成）

        Returns:
            {"success": true, "agent_id": "...", "api_token": "...", "role": "member"}
        """
        args: dict = {"invite_code": invite_code, "name": name}
        if agent_id:
            args["agent_id"] = agent_id

        result = self._call_tool("register_agent", args)

        if result.get("success"):
            self.agent_id = result.get("agent_id", self.agent_id)
            self.set_token(result.get("api_token", ""))
            self._role = result.get("role")
            logger.info(f"注册成功: {self.agent_id} (role={self._role})")

        return result

    def heartbeat(self) -> dict:
        """
        上报心跳

        Returns:
            {"success": true, "agent_id": "...", "status": "online"}
        """
        return self._call_tool("heartbeat", {"agent_id": self.agent_id})

    def query_agents(
        self,
        status: Optional[str] = None,
        role: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> dict:
        """
        查询已注册 Agent 列表

        Args:
            status: 可选，筛选状态（online/offline/all）
            role: 可选，角色筛选（admin/member）
            capability: 可选，能力筛选

        Returns:
            {"agents": [...], "count": N}
            每个 agent 包含 trust_score 字段
        """
        args: dict = {}
        if status:
            args["status"] = status
        if role:
            args["role"] = role
        if capability:
            args["capability"] = capability
        return self._call_tool("query_agents", args)

    def set_trust_score(self, agent_id: str, delta: int) -> dict:
        """
        调整 Agent 信任分（admin only）

        Args:
            agent_id: 目标 Agent ID
            delta: 信任分增量（-100 到 +100）

        Returns:
            {"ok": true, "new_score": N} 或 {"ok": false, "error": "..."}
        """
        return self._call_tool("set_trust_score", {
            "agent_id": agent_id,
            "delta": delta,
        })

    def get_online_agents(self) -> List[str]:
        """
        获取在线 Agent ID 列表

        Returns:
            在线 Agent ID 列表
        """
        result = self._call_tool("get_online_agents", {})
        return result.get("online_agents", [])

    def revoke_token(self, token_id: str) -> dict:
        """
        吊销 Token（admin only）

        Args:
            token_id: 要吊销的 Token ID
        """
        return self._call_tool("revoke_token", {"token_id": token_id})

    # ═══════════════════════════════════════════════════════
    # 对外 API — 消息
    # ═══════════════════════════════════════════════════════

    def send_message(
        self,
        to: str,
        content: str,
        msg_type: str = "message",
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        发送消息给另一个 Agent

        Args:
            to: 目标 Agent ID
            content: 消息内容
            msg_type: 消息类型（message/task_result/等）
            metadata: 可选的元数据

        Returns:
            {"success": true, "message_id": "..."}
        """
        args: dict = {
            "from": self.agent_id,
            "to": to,
            "content": content,
            "type": msg_type,
        }
        if metadata is not None:
            args["metadata"] = metadata
        return self._call_tool("send_message", args)

    def broadcast_message(
        self,
        agent_ids: List[str],
        content: str,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        广播消息给多个 Agent

        Args:
            agent_ids: 目标 Agent ID 列表
            content: 消息内容
            metadata: 可选元数据
        """
        args: dict = {
            "from": self.agent_id,
            "agent_ids": agent_ids,
            "content": content,
        }
        # 只在有值时传 metadata，避免 MCP schema 校验 null 为 object 报错
        if metadata is not None:
            args["metadata"] = metadata
        return self._call_tool("broadcast_message", args)

    def acknowledge_message(self, message_id: str) -> dict:
        """确认消息已收到"""
        return self._call_tool("acknowledge_message", {"message_id": message_id})

    # ═══════════════════════════════════════════════════════
    # 对外 API — 任务
    # ═══════════════════════════════════════════════════════

    def assign_task(
        self,
        to: str,
        description: str,
        context: Optional[str] = None,
        priority: str = "normal",
    ) -> dict:
        """
        分配任务给另一个 Agent

        Args:
            to: 目标 Agent ID
            description: 任务描述
            context: 可选上下文
            priority: 优先级（normal/high/low）
        """
        return self._call_tool("assign_task", {
            "from": self.agent_id,
            "to": to,
            "description": description,
            "context": context,
            "priority": priority,
        })

    def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[str] = None,
        progress: int = 0,
    ) -> dict:
        """
        更新任务状态

        Args:
            task_id: 任务 ID
            status: 状态（in_progress/completed/failed）
            result: 可选结果
            progress: 进度（0-100）
        """
        return self._call_tool("update_task_status", {
            "task_id": task_id,
            "agent_id": self.agent_id,
            "status": status,
            "result": result,
            "progress": progress,
        })

    def get_task_status(self, task_id: str) -> dict:
        """查询任务状态"""
        return self._call_tool("get_task_status", {"task_id": task_id})

    # ═══════════════════════════════════════════════════════
    # 对外 API — 记忆
    # ═══════════════════════════════════════════════════════

    def store_memory(
        self,
        content: str,
        title: Optional[str] = None,
        scope: str = "private",
        tags: Optional[List[str]] = None,
        source_task_id: Optional[str] = None,
    ) -> dict:
        """
        存储记忆

        Args:
            content: 记忆内容（最多 10000 字符）
            title: 可选标题
            scope: 可见范围（private/group/collective）
            tags: 可选标签列表
            source_task_id: 可选，关联任务 ID（用于溯源追踪）
              注意：source_agent_id 由服务端自动注入（collective/group 时）

        Returns:
            {"success": true, "memory_id": "...", "scope": "...",
             "source_agent_id": "...", "source_task_id": "..."}
        """
        args: dict = {"content": content, "scope": scope}
        if title:
            args["title"] = title
        if tags:
            args["tags"] = tags
        if source_task_id:
            args["source_task_id"] = source_task_id
        return self._call_tool("store_memory", args)

    def recall_memory(
        self,
        query: str,
        scope: str = "all",
        limit: int = 10,
    ) -> dict:
        """
        全文搜索召回记忆

        Args:
            query: 搜索关键词
            scope: 搜索范围（private/group/collective/all）
            limit: 最大返回数量

        Returns:
            {"results": [...], "count": N}
        """
        return self._call_tool("recall_memory", {
            "query": query,
            "scope": scope,
            "limit": limit,
        })

    def list_memories(
        self,
        scope: str = "all",
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        列出可访问的记忆

        Args:
            scope: 筛选范围
            limit: 每页数量
            offset: 偏移量
        """
        return self._call_tool("list_memories", {
            "scope": scope,
            "limit": limit,
            "offset": offset,
        })

    def delete_memory(self, memory_id: str) -> dict:
        """删除记忆"""
        return self._call_tool("delete_memory", {"memory_id": memory_id})

    # ═══════════════════════════════════════════════════════
    # 对外 API — Evolution Engine（经验共享 + 策略传播）
    # ═══════════════════════════════════════════════════════

    def share_experience(
        self,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        task_id: Optional[str] = None,
    ) -> dict:
        """
        分享经验（直接 approved，无需审批）

        Args:
            title: 经验标题（3-200 字符）
            content: 经验内容（10-5000 字符，Markdown）
            tags: 可选标签列表（最多 10 个）
            task_id: 可选，关联任务 ID

        Returns:
            {"success": true, "strategy_id": N, "status": "approved"}
        """
        args: dict = {"title": title, "content": content}
        if tags is not None:
            args["tags"] = tags
        if task_id:
            args["task_id"] = task_id
        return self._call_tool("share_experience", args)

    def propose_strategy(
        self,
        title: str,
        content: str,
        category: str = "workflow",
        task_id: Optional[str] = None,
    ) -> dict:
        """
        提议策略（需 admin 审批）

        Args:
            title: 策略标题（3-200 字符）
            content: 策略内容（10-5000 字符）
            category: 分类（workflow/fix/tool_config/prompt_template/other）
            task_id: 可选，关联任务 ID

        Returns:
            {"success": true, "strategy_id": N, "status": "pending"}
        """
        args: dict = {"title": title, "content": content, "category": category}
        if task_id:
            args["task_id"] = task_id
        return self._call_tool("propose_strategy", args)

    def list_strategies(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        proposer_id: Optional[str] = None,
        limit: int = 20,
    ) -> dict:
        """
        查询策略列表

        Args:
            status: 筛选状态（pending/approved/rejected/all）
            category: 筛选分类（experience/workflow/fix/tool_config/prompt_template/other/all）
            proposer_id: 筛选提议者
            limit: 最大返回数量（1-50）

        Returns:
            {"strategies": [...], "count": N}
        """
        args: dict = {"limit": limit}
        if status:
            args["status"] = status
        if category:
            args["category"] = category
        if proposer_id:
            args["proposer_id"] = proposer_id
        return self._call_tool("list_strategies", args)

    def search_strategies(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> dict:
        """
        FTS5 全文搜索策略

        Args:
            query: 搜索关键词（2-200 字符）
            category: 可选分类筛选
            limit: 最大返回数量（1-20）

        Returns:
            {"results": [...], "count": N}
        """
        args: dict = {"query": query, "limit": limit}
        if category:
            args["category"] = category
        return self._call_tool("search_strategies", args)

    def apply_strategy(
        self,
        strategy_id: int,
        context: Optional[str] = None,
    ) -> dict:
        """
        采纳策略（记录到 strategy_applications，apply_count++）

        Args:
            strategy_id: 策略 ID
            context: 可选，应用场景描述（最多 500 字符）

        Returns:
            {"success": true, "application_id": N}
        """
        args: dict = {"strategy_id": strategy_id}
        if context:
            args["context"] = context
        return self._call_tool("apply_strategy", args)

    def feedback_strategy(
        self,
        strategy_id: int,
        feedback: str,
        comment: Optional[str] = None,
        applied: Optional[bool] = None,
    ) -> dict:
        """
        对策略反馈（每个 Agent 对同一策略只能反馈一次）

        Args:
            strategy_id: 策略 ID
            feedback: 反馈类型（positive/negative/neutral）
            comment: 可选备注（最多 500 字符）
            applied: 可选，是否实际采纳到工作中

        Returns:
            {"success": true, "feedback_id": N}
        """
        args: dict = {"strategy_id": strategy_id, "feedback": feedback}
        if comment:
            args["comment"] = comment
        if applied is not None:
            args["applied"] = applied
        return self._call_tool("feedback_strategy", args)

    def approve_strategy(
        self,
        strategy_id: int,
        action: str,
        reason: str,
    ) -> dict:
        """
        审批策略（admin only）

        Args:
            strategy_id: 策略 ID
            action: 审批动作（approve/reject）
            reason: 审批理由（最多 1000 字符）

        Returns:
            {"success": true, "strategy_id": N, "new_status": "approved"/"rejected"}
        """
        return self._call_tool("approve_strategy", {
            "strategy_id": strategy_id,
            "action": action,
            "reason": reason,
        })

    def get_evolution_status(self) -> dict:
        """
        查看进化指标统计

        Returns:
            {
                "total_experiences": N,
                "total_strategies": N,
                "pending_approval": N,
                "approved_rate": "X%",
                "top_contributors": [...],
                "recent_approved": [...],
            }
        """
        return self._call_tool("get_evolution_status", {})

    # ═══════════════════════════════════════════════════════
    # 对外 API — Phase 4b Day 2: 依赖链 + 并行组
    # ═══════════════════════════════════════════════════════

    def add_dependency(
        self,
        upstream_id: str,
        downstream_id: str,
        dep_type: str = "finish_to_start",
    ) -> dict:
        """
        添加任务依赖关系（自动环检测）

        Args:
            upstream_id: 上游任务 ID
            downstream_id: 下游任务 ID
            dep_type: 依赖类型（finish_to_start/start_to_start/finish_to_finish/start_to_finish）
        """
        return self._call_tool("add_dependency", {
            "upstream_id": upstream_id,
            "downstream_id": downstream_id,
            "dep_type": dep_type,
        })

    def remove_dependency(self, upstream_id: str, downstream_id: str) -> dict:
        """删除任务依赖关系"""
        return self._call_tool("remove_dependency", {
            "upstream_id": upstream_id,
            "downstream_id": downstream_id,
        })

    def get_task_dependencies(self, task_id: str) -> dict:
        """查询任务的所有依赖关系"""
        return self._call_tool("get_task_dependencies", {"task_id": task_id})

    def check_dependencies_satisfied(self, task_id: str) -> dict:
        """检查任务依赖是否全部满足"""
        return self._call_tool("check_dependencies_satisfied", {"task_id": task_id})

    def create_parallel_group(self, task_ids: List[str], group_name: str = "parallel_group") -> dict:
        """
        创建并行任务组

        Args:
            task_ids: 并行任务 ID 列表（至少 2 个）
            group_name: 组名
        """
        return self._call_tool("create_parallel_group", {
            "task_ids": task_ids,
            "group_name": group_name,
        })

    # ═══════════════════════════════════════════════════════
    # 对外 API — Phase 4b Day 3: 交接协议 + 质量门
    # ═══════════════════════════════════════════════════════

    def request_handoff(self, task_id: str, target_agent_id: str) -> dict:
        """请求任务交接"""
        return self._call_tool("request_handoff", {
            "task_id": task_id,
            "target_agent_id": target_agent_id,
        })

    def accept_handoff(self, task_id: str) -> dict:
        """接受任务交接"""
        return self._call_tool("accept_handoff", {"task_id": task_id})

    def reject_handoff(self, task_id: str, reason: Optional[str] = None) -> dict:
        """拒绝任务交接"""
        args: dict = {"task_id": task_id}
        if reason:
            args["reason"] = reason
        return self._call_tool("reject_handoff", args)

    def add_quality_gate(
        self,
        pipeline_id: str,
        gate_name: str,
        criteria: str,
        after_order: int,
    ) -> dict:
        """
        在 Pipeline 中添加质量门

        Args:
            pipeline_id: Pipeline ID
            gate_name: 质量门名称
            criteria: 评估规则（JSON 格式）
            after_order: 在哪个 order_index 之后阻塞
        """
        return self._call_tool("add_quality_gate", {
            "pipeline_id": pipeline_id,
            "gate_name": gate_name,
            "criteria": criteria,
            "after_order": after_order,
        })

    def evaluate_quality_gate(
        self,
        gate_id: str,
        status: str,
        result: Optional[str] = None,
    ) -> dict:
        """
        评估质量门（通过/失败）

        Args:
            gate_id: 质量门 ID
            status: 评估结果（passed/failed）
            result: 评估说明
        """
        args: dict = {"gate_id": gate_id, "status": status}
        if result:
            args["result"] = result
        return self._call_tool("evaluate_quality_gate", args)

    # ═══════════════════════════════════════════════════════
    # 对外 API — Phase 4b Day 4: 分级审批
    # ═══════════════════════════════════════════════════════

    def propose_strategy_tiered(
        self,
        title: str,
        content: str,
        category: str = "workflow",
        task_id: Optional[str] = None,
    ) -> dict:
        """
        提议策略（分级审批）
        Hub 自动判定审批等级：
          - auto: 高信任+低风险 → 自动通过 + 72h 观察窗口
          - peer: 中等信任 → peer 审批
          - admin: 默认 → admin 审批
          - super: 高风险 → 人工审批

        Args:
            title: 策略标题（3-200 字符）
            content: 策略内容（10-5000 字符）
            category: 分类（workflow/fix/tool_config/prompt_template/other）
            task_id: 可选，关联任务 ID
        """
        args: dict = {"title": title, "content": content, "category": category}
        if task_id:
            args["task_id"] = task_id
        return self._call_tool("propose_strategy_tiered", args)

    def check_veto_window(self, strategy_id: int) -> dict:
        """
        检查策略的否决窗口状态

        Args:
            strategy_id: 策略 ID
        """
        return self._call_tool("check_veto_window", {"strategy_id": strategy_id})

    def veto_strategy(self, strategy_id: int, reason: str) -> dict:
        """
        撤回处于否决窗口内的策略（admin only）

        Args:
            strategy_id: 策略 ID
            reason: 撤回理由
        """
        return self._call_tool("veto_strategy", {
            "strategy_id": strategy_id,
            "reason": reason,
        })

    # ═══════════════════════════════════════════════════════
    # 对外 API — Phase 5a: Security 增强
    # ═══════════════════════════════════════════════════════

    def set_agent_role(
        self,
        agent_id: str,
        role: str,
        managed_group_id: Optional[str] = None,
    ) -> dict:
        """设置 Agent 角色（admin only）

        Args:
            agent_id: 目标 Agent ID
            role: 新角色（admin / member / group_admin）
            managed_group_id: 管理组 ID（仅 group_admin 需要指定）

        Returns:
            { success, agent_id, old_role, new_role, managed_group_id }
        """
        params: dict = {"agent_id": agent_id, "role": role}
        if managed_group_id is not None:
            params["managed_group_id"] = managed_group_id
        return self._call_tool("set_agent_role", params)

    def recalculate_trust_scores(
        self,
        agent_id: Optional[str] = None,
    ) -> dict:
        """手动重算信任分（admin only）

        基于多因子自动计算：verified capabilities (+3)、approved strategies (+2)、
        positive feedback (+1)、negative feedback (-2)、rejected applications (-3)、
        revoked tokens (-10)。base=50, clamp(0,100)。

        Args:
            agent_id: 指定 Agent ID（可选，不传则全部重算）

        Returns:
            { success, agent_id, new_score } 或 { success, total_agents, scores }
        """
        params: dict = {}
        if agent_id is not None:
            params["agent_id"] = agent_id
        return self._call_tool("recalculate_trust_scores", params)

    # ═══════════════════════════════════════════════════════
    # 对外 API — Phase 6: 搜索 + Pipeline（补齐）
    # ═══════════════════════════════════════════════════════

    def search_messages(
        self,
        query: str,
        *,
        from_agent: Optional[str] = None,
        to_agent: Optional[str] = None,
        limit: int = 50,
    ) -> dict:
        """搜索消息（FTS5 全文检索）"""
        params: dict = {"query": query, "limit": limit}
        if from_agent:
            params["from_agent"] = from_agent
        if to_agent:
            params["to_agent"] = to_agent
        return self._call_tool("search_messages", params)

    def search_memories(
        self,
        query: str,
        *,
        scope: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 50,
    ) -> dict:
        """搜索记忆（FTS5 全文检索）"""
        params: dict = {"query": query, "limit": limit}
        if scope:
            params["scope"] = scope
        if agent_id:
            params["agent_id"] = agent_id
        return self._call_tool("search_memories", params)

    def create_pipeline(self, name: str, description: str = "") -> dict:
        """创建 Pipeline（任务容器）"""
        return self._call_tool("create_pipeline", {
            "name": name,
            "description": description,
        })

    def get_pipeline(self, pipeline_id: str) -> dict:
        """获取 Pipeline 详情"""
        return self._call_tool("get_pipeline", {"pipeline_id": pipeline_id})

    def list_pipelines(self, *, status: Optional[str] = None) -> dict:
        """列出 Pipelines"""
        params: dict = {}
        if status:
            params["status"] = status
        return self._call_tool("list_pipelines", params)

    def add_task_to_pipeline(
        self,
        pipeline_id: str,
        description: str,
        *,
        assigned_to: Optional[str] = None,
        priority: str = "medium",
        depends_on: Optional[list] = None,
    ) -> dict:
        """向 Pipeline 添加任务"""
        params: dict = {
            "pipeline_id": pipeline_id,
            "description": description,
            "priority": priority,
        }
        if assigned_to:
            params["assigned_to"] = assigned_to
        if depends_on:
            params["depends_on"] = depends_on
        return self._call_tool("add_task_to_pipeline", params)

    def cancel_task(self, task_id: str, reason: str = "") -> dict:
        """取消任务"""
        params: dict = {"task_id": task_id}
        if reason:
            params["reason"] = reason
        return self._call_tool("cancel_task", params)

    # ═══════════════════════════════════════════════════════
    # 对外 API — 消费追踪
    # ═══════════════════════════════════════════════════════

    def mark_consumed(self, resource: str, resource_type: str = "file", action: str = "processed", notes: Optional[str] = None) -> dict:
        """标记资源已消费（去重）"""
        args: dict = {
            "agent_id": self.agent_id,
            "resource": resource,
            "resource_type": resource_type,
            "action": action,
        }
        if notes:
            args["notes"] = notes
        return self._call_tool("mark_consumed", args)

    def check_consumed(self, resource: str) -> dict:
        """检查资源是否已消费"""
        return self._call_tool("check_consumed", {
            "agent_id": self.agent_id,
            "resource": resource,
        })

    # ═══════════════════════════════════════════════════════
    # SSE 订阅 + 自动重连 + 客户端去重
    # ═══════════════════════════════════════════════════════

    def connect_sse(self, blocking: bool = True) -> None:
        """
        连接 SSE 事件流

        Args:
            blocking: True=阻塞当前线程，False=后台线程

        使用方法：
            # 阻塞模式（适合独立脚本）
            hub.connect_sse(blocking=True)

            # 非阻塞模式（适合集成到其他应用）
            hub.connect_sse(blocking=False)
            # 后续可通过 hub.disconnect_sse() 停止
        """
        if self._sse_running:
            logger.warning("SSE 已在运行中")
            return

        if blocking:
            self._sse_loop()
        else:
            self._sse_thread = threading.Thread(
                target=self._sse_loop,
                name=f"sse-{self.agent_id or 'unknown'}",
                daemon=True,
            )
            self._sse_thread.start()

    def disconnect_sse(self) -> None:
        """断开 SSE 连接"""
        self._sse_running = False
        logger.info(f"[{self.agent_id}] SSE 断开请求")

    def _sse_loop(self) -> None:
        """SSE 连接主循环（含自动重连）"""
        self._sse_running = True
        self._reconnect_delay = self._reconnect_base

        while self._sse_running:
            if not self.agent_id:
                logger.error("agent_id 未设置，无法连接 SSE")
                break

            try:
                url = f"{self.hub_url}/events/{self.agent_id}"

                logger.info(f"[{self.agent_id}] SSE 连接: {self.hub_url}")
                conn = self._create_sse_connection(url)
                logger.info(f"[{self.agent_id}] SSE 已连接")
                self._reconnect_delay = self._reconnect_base
                self._read_sse_http_client(conn)

            except AuthError:
                logger.error(f"[{self.agent_id}] SSE 认证失败，停止重连")
                break
            except Exception as e:
                if not self._sse_running:
                    break
                logger.warning(f"[{self.agent_id}] SSE 断线: {e}")
                self._wait_reconnect()

        self._sse_running = False
        logger.info(f"[{self.agent_id}] SSE 主循环退出")

    def _create_sse_connection(self, url: str) -> http.client.HTTPConnection:
        """使用 http.client 建立 SSE 连接（更好控制读取行为）"""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or 80
        path = parsed.path + ("?" + parsed.query if parsed.query else "")

        conn = http.client.HTTPConnection(host, port, timeout=self._sse_timeout)
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        # 断线重连时携带 Last-Event-ID
        with self._last_event_id_lock:
            if self._last_event_id is not None:
                headers["Last-Event-ID"] = self._last_event_id

        conn.request("GET", path, headers=headers)
        resp = conn.getresponse()

        if resp.status == 401:
            raise AuthError("SSE authentication failed", 401)
        if resp.status != 200:
            raise HubError(f"SSE connection failed: HTTP {resp.status}", resp.status)

        return conn

    def _read_sse_http_client(self, conn: http.client.HTTPConnection) -> None:
        """使用 http.client 逐行读取 SSE 流"""
        resp = conn.sock  # 底层 socket
        buffer = ""

        while self._sse_running:
            try:
                # 使用 makefile 获取类文件对象，设置小缓冲
                f = conn.sock.makefile("r", encoding="utf-8", errors="replace", newline=None)
                while self._sse_running:
                    line = f.readline()
                    if not line:
                        break
                    buffer += line

                    # 按 \n\n 分割 SSE 事件
                    while "\n\n" in buffer:
                        event_text, buffer = buffer.split("\n\n", 1)
                        self._parse_sse_event(event_text.strip())
                f.close()
                break
            except (socket.timeout, OSError) as e:
                if not self._sse_running:
                    break
                # 超时或连接错误，触发重连
                raise HubError(f"SSE read error: {e}")
            except Exception as e:
                if not self._sse_running:
                    break
                raise

    def _parse_sse_event(self, event_text: str) -> None:
        """解析单个 SSE 事件"""
        lines = event_text.split("\n")
        data = ""
        event_id: Optional[str] = None

        for line in lines:
            if line.startswith("data:"):
                data = line[5:].strip()
            elif line.startswith("id:"):
                # 记录 Last-Event-ID 用于断线重连
                event_id = line[3:].strip()
                with self._last_event_id_lock:
                    self._last_event_id = event_id
            elif line.startswith(":"):
                # SSE 心跳注释
                pass

        if not data:
            return

        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            logger.debug(f"非 JSON SSE 数据: {data[:80]}")
            return

        # 处理 MCP 包装格式（result.content[0].text）
        if "result" in payload and "jsonrpc" in payload:
            result = payload.get("result", {})
            if isinstance(result, dict) and "content" in result:
                for item in result.get("content", []):
                    if isinstance(item, dict) and item.get("type") == "text":
                        try:
                            inner = json.loads(item["text"])
                            self._handle_event(inner)
                        except (json.JSONDecodeError, TypeError):
                            pass
            return

        # 直接事件格式
        self._handle_event(payload)

    def _handle_event(self, data: dict) -> None:
        """
        事件路由 + 客户端去重
        """
        event_type = data.get("event", "unknown")

        # ── 客户端去重 ─────────────────────────────────
        event_id = data.get("_hub_event_id")
        if event_id is not None:
            with self._seen_event_ids_lock:
                if event_id in self._seen_event_ids:
                    logger.debug(f"去重: event_id={event_id}")
                    return
                self._seen_event_ids.add(event_id)
                self._seen_event_ids_ordered.append(event_id)
                # 防止内存泄漏：保留最新的一半（按插入顺序）
                if len(self._seen_event_ids) > self._dedup_max_size:
                    trim_count = self._dedup_max_size // 2
                    old_ids = self._seen_event_ids_ordered[:trim_count]
                    self._seen_event_ids_ordered = self._seen_event_ids_ordered[trim_count:]
                    for old_id in old_ids:
                        self._seen_event_ids.discard(old_id)

        # ── 事件路由 ───────────────────────────────────
        if event_type == "new_message":
            msg = data.get("message", data)
            logger.info(f"[消息] 来自 {msg.get('from_agent', '?')}: {str(msg.get('content', ''))[:60]}")
            if self.on_message:
                try:
                    self.on_message(msg)
                except Exception as e:
                    logger.error(f"on_message 回调异常: {e}")

        elif event_type == "task_assigned":
            task = data.get("task", data)
            logger.info(f"[任务] 来自 {task.get('assigned_by', '?')}: {str(task.get('description', ''))[:60]}")
            if self.on_task_assigned:
                try:
                    self.on_task_assigned(task)
                except Exception as e:
                    logger.error(f"on_task_assigned 回调异常: {e}")

        elif event_type == "task_updated":
            update = data.get("update", data)
            logger.debug(f"[更新] 任务 {update.get('task_id', '')[:16]} → {update.get('status')}")
            if self.on_task_updated:
                try:
                    self.on_task_updated(update)
                except Exception as e:
                    logger.error(f"on_task_updated 回调异常: {e}")

        elif event_type == "pending_messages":
            messages = data.get("messages", [])
            if messages:
                logger.info(f"[积压] 补发 {len(messages)} 条消息")
                for msg in messages:
                    if self.on_message:
                        try:
                            self.on_message(msg)
                        except Exception as e:
                            logger.error(f"on_message 回调异常: {e}")

        else:
            logger.debug(f"[未知事件] {event_type}: {json.dumps(data, ensure_ascii=False)[:100]}")

    def _wait_reconnect(self) -> None:
        """指数退避等待重连"""
        delay = self._reconnect_delay
        logger.info(f"[{self.agent_id}] {delay:.1f}s 后重连...")
        time.sleep(delay)
        self._reconnect_delay = min(self._reconnect_delay * 2, self._reconnect_max)

    # ═══════════════════════════════════════════════════════
    # REST API（供补充调用）
    # ═══════════════════════════════════════════════════════

    def health_check(self) -> dict:
        """健康检查（免认证）"""
        raw = self._request("GET", "/health", timeout=5)
        return json.loads(raw.decode("utf-8"))

    def generate_invite(self, role: str = "member") -> dict:
        """生成邀请码（admin only）"""
        raw = self._request("POST", "/admin/invite/generate", data={"role": role}, headers=self._auth_headers())
        return json.loads(raw.decode("utf-8"))

    def get_tasks(self, status: str = "pending") -> dict:
        """REST API 获取任务列表"""
        raw = self._request(
            "GET", f"/api/tasks?agent_id={self.agent_id}&status={status}",
            headers=self._auth_headers(),
        )
        return json.loads(raw.decode("utf-8"))

    def get_messages(self, status: str = "unread") -> dict:
        """REST API 获取消息列表"""
        raw = self._request(
            "GET", f"/api/messages?agent_id={self.agent_id}&status={status}",
            headers=self._auth_headers(),
        )
        return json.loads(raw.decode("utf-8"))

    def update_task_via_rest(self, task_id: str, status: str, result: Optional[str] = None, progress: int = 0) -> dict:
        """REST API 更新任务状态"""
        raw = self._request(
            "PATCH", f"/api/tasks/{task_id}/status",
            data={"status": status, "result": result, "progress": progress},
            headers=self._auth_headers(),
        )
        return json.loads(raw.decode("utf-8"))

    # ═══════════════════════════════════════════════════════
    # 辅助方法
    # ═══════════════════════════════════════════════════════

    def __repr__(self) -> str:
        return (
            f"SynergyHubClient(agent_id={self.agent_id!r}, "
            f"hub={self.hub_url!r}, connected={self._sse_running})"
        )


# ─── 便捷入口 ─────────────────────────────────────────────────────

def create_client(
    hub_url: str = "http://localhost:3100",
    invite_code: Optional[str] = None,
    name: Optional[str] = None,
    agent_id: Optional[str] = None,
) -> SynergyHubClient:
    """
    便捷工厂方法：创建并可选注册客户端

    Usage:
        # 仅创建（后续手动注册）
        client = create_client(hub_url="http://localhost:3100")

        # 创建 + 注册
        client = create_client(
            hub_url="http://localhost:3100",
            invite_code="abc12345",
            name="my_agent",
        )
    """
    client = SynergyHubClient(hub_url=hub_url, agent_id=agent_id)

    if invite_code and name:
        client.register(invite_code=invite_code, name=name, agent_id=agent_id)

    return client
