"""
Engine — 核心工作流执行引擎

状态机管理器: 维护流程节点、支持断点恢复、重试、人工介入。
与 OpenClaw Gateway 深度绑定: 每个工作流运行创建独立 session，
所有 LLM/Agent/Skill 调用共享对话上下文。
"""

import json
import os
import time
import uuid
import yaml
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .context import Context
from .nodes import NODE_HANDLERS, NodeResult, batch_spawn_subagents
from .schema import validate_workflow
from .bridge import GatewayBridge, get_bridge

# 线程局部存储 — 并行循环中每个线程拥有独立的 Context
_engine_tls = threading.local()


# ── 运行状态 ──────────────────────────────────────────────

class StepRecord:
    """单步执行记录"""

    def __init__(self, step_id: str, step_name: str, step_type: str):
        self.step_id = step_id
        self.step_name = step_name
        self.step_type = step_type
        self.status = "pending"  # pending | running | success | failed | skipped
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None
        self.result: Optional[Dict] = None
        self.error: str = ""
        self.retries: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_name": self.step_name,
            "step_type": self.step_type,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "result": self.result,
            "error": self.error,
            "retries": self.retries,
        }


class RunRecord:
    """工作流运行记录"""

    def __init__(self, flow_id: str, run_id: Optional[str] = None):
        self.flow_id = flow_id
        self.run_id = run_id or str(uuid.uuid4())
        self.status = "pending"  # pending | running | success | failed | aborted
        self.started_at: Optional[str] = None
        self.finished_at: Optional[str] = None
        self.steps: List[StepRecord] = []
        self.current_step_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "flow_id": self.flow_id,
            "run_id": self.run_id,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "current_step_index": self.current_step_index,
            "steps": [s.to_dict() for s in self.steps],
        }


# ── 主引擎 ────────────────────────────────────────────────

class WorkflowEngine:
    """
    OpenClaw Workflow 核心执行引擎。

    功能:
    - 加载并验证 YAML 工作流
    - 顺序/分支/循环执行节点
    - 变量管道 (Context)
    - 重试 & 错误处理
    - 执行快照 & 断点恢复
    - 实时日志回调
    """

    # 持久化目录（运行态数据不写入 skill 包目录，避免污染标准 skill 结构）
    RUNS_DIR = Path(os.path.expanduser("~/.openclaw/workspace/.openclaw-workflow/runs"))

    def __init__(
        self,
        workflow_file: Optional[str] = None,
        workflow_data: Optional[Dict] = None,
        log_callback: Optional[Callable[[str, str], None]] = None,
        event_callback: Optional[Callable[[str, Dict], None]] = None,
        bridge: Optional[GatewayBridge] = None,
        agent_id: str = "main",
    ):
        self.workflow_file = workflow_file
        self.workflow_data = workflow_data
        self.log_callback = log_callback
        self.event_callback = event_callback
        self._main_ctx = Context()  # 主线程上下文 (通过 ctx 属性访问)
        self.run_record: Optional[RunRecord] = None
        self._aborted = False
        self._agent_id = agent_id
        self._snapshot_lock = threading.Lock()  # 并行循环时保护快照写入

        # Gateway Bridge (延迟初始化 — 在 run() 中创建，使用 run_id 作为 session namespace)
        self._bridge = bridge

    # ── 线程安全的上下文访问 ──────────────────────────────

    @property
    def ctx(self) -> Context:
        """
        获取当前线程的 Context。
        并行循环中每个工作线程有独立的子 Context (thread-local),
        主线程返回 _main_ctx。
        """
        return getattr(_engine_tls, 'ctx', self._main_ctx)

    @ctx.setter
    def ctx(self, value: Context):
        """设置主线程 Context (仅在 run() 初始化时调用)"""
        self._main_ctx = value

    # ── 日志 ──────────────────────────────────────────────

    def _log(self, msg: str, level: str = "INFO"):
        ts = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{ts}] [{level}] {msg}"
        print(formatted, flush=True)
        if self.log_callback:
            self.log_callback(msg, level)

    def _emit(self, event: str, data: Dict):
        if self.event_callback:
            self.event_callback(event, data)

    # ── 加载 ──────────────────────────────────────────────

    def load(self) -> Dict:
        """加载工作流定义"""
        if self.workflow_data:
            return self.workflow_data

        if not self.workflow_file:
            raise ValueError("未指定工作流文件或数据")

        path = Path(self.workflow_file).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"工作流文件不存在: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data

    def validate(self) -> tuple:
        """验证工作流定义"""
        data = self.load()
        return validate_workflow(data)

    # ── 执行 ──────────────────────────────────────────────

    def run(self) -> RunRecord:
        """执行工作流"""
        data = self.load()

        # 验证
        is_valid, errors = validate_workflow(data)
        if not is_valid:
            self._log("工作流验证失败:", "ERROR")
            for e in errors:
                self._log(str(e), "ERROR")
            raise ValueError(f"工作流验证失败: {len(errors)} 个错误")

        # 初始化
        flow_id = data.get("flow_id") or data.get("name") or "unnamed"
        self.run_record = RunRecord(flow_id)
        self.run_record.status = "running"
        self.run_record.started_at = datetime.now().isoformat()

        # 初始化 Gateway Bridge (使用 run_id 作为 session namespace)
        # 同一工作流运行内的所有 LLM/Agent/Skill 调用共享这个 session
        if not self._bridge:
            session_ns = f"openclaw-workflow:{flow_id}:{self.run_record.run_id[:8]}"
            self._bridge = get_bridge(
                session_namespace=session_ns,
                agent_id=self._agent_id,
                log_callback=self._log,
            )
            if self._bridge.is_available():
                self._log(f"🔗 Gateway Bridge 已连接 (session={self._bridge.session_key})")
            else:
                self._log("⚠️  Gateway 不可达，OpenClaw 依赖节点可能失败", "WARN")

        # 加载设置
        settings = data.get("settings", {})
        global_retry = settings.get("retry", 0)
        global_retry_delay = settings.get("retry_delay", 5)
        global_on_error = settings.get("on_error", "stop")
        global_timeout = settings.get("timeout", 300)

        # 加载变量
        variables = data.get("variables", {})
        self.ctx = Context(variables)

        # 运行步骤
        steps = data.get("steps", [])

        self._log(f"🚀 开始执行工作流: {flow_id} (共 {len(steps)} 步)")
        self._emit("workflow_start", {
            "flow_id": flow_id,
            "steps": len(steps),
            "session_key": self._bridge.session_key if self._bridge else None,
        })

        try:
            success = self._execute_steps(
                steps, global_retry, global_retry_delay, global_on_error, global_timeout
            )

            self.run_record.status = "success" if success else "failed"
        except KeyboardInterrupt:
            self._log("⛔ 工作流被用户中断", "WARN")
            self.run_record.status = "aborted"
        except Exception as e:
            self._log(f"💥 工作流异常: {e}", "ERROR")
            self.run_record.status = "failed"
        finally:
            # ── 清理工作流产生的所有 session ──
            # 无论成功、失败还是中断，都必须清理:
            # 1. 工作流主 session (agent:main:openclaw-workflow:<ns>)
            # 2. 所有 spawn 占位 session (agent:main:openclaw-workflow:spawn:*)
            # 3. 已完成的 subagent child session (通过 tracker)
            # 这防止了 session 泄漏：之前如果工作流在 spawn 阶段失败，
            # 永远走不到 wait_subagents 的清理逻辑，导致 spawn session 累积
            if self._bridge:
                try:
                    # 从 context 中提取 tracker (如果有)，一并清理 child sessions
                    extra_keys = []
                    if self.ctx:
                        tracker = self.ctx.get("init_tracker")
                        if isinstance(tracker, list):
                            for item in tracker:
                                if isinstance(item, dict):
                                    ck = item.get("child_session_key", "")
                                    if ck:
                                        extra_keys.append(ck)

                    # 工厂模式兜底: 循环中断/失败时，某些 child key 可能尚未 append 到 tracker
                    # 这里补充 bridge 内部追踪到的 child sessions，避免残留
                    if hasattr(self._bridge, "get_factory_child_session_keys"):
                        for ck in self._bridge.get_factory_child_session_keys():
                            if ck and ck not in extra_keys:
                                extra_keys.append(ck)
                    self._bridge.cleanup_workflow_sessions(extra_spawn_keys=extra_keys)
                except Exception as e:
                    self._log(f"⚠️ Session 清理异常: {e}", "WARN")

        self.run_record.finished_at = datetime.now().isoformat()
        self._log(f"{'✅' if self.run_record.status == 'success' else '❌'} 工作流完成: {self.run_record.status}")
        self._emit("workflow_end", self.run_record.to_dict())

        # 持久化运行记录
        self._save_run()

        return self.run_record

    def _execute_steps(
        self,
        steps: List[Dict],
        global_retry: int,
        global_retry_delay: float,
        global_on_error: str,
        global_timeout: int,
    ) -> bool:
        """执行一组步骤"""
        for i, step in enumerate(steps):
            if self._aborted:
                return False

            step_id = step.get("id") or f"step_{i}"
            step_name = step.get("name") or step_id
            step_type = step.get("type", "log")

            # when 条件守卫
            when = step.get("when")
            if when and not self.ctx.eval_condition(self.ctx.resolve(when)):
                self._log(f"⏭️  跳过步骤 [{step_name}]: 条件不满足", "INFO")
                continue

            # 创建步骤记录
            record = StepRecord(step_id, step_name, step_type)
            record.status = "running"
            record.started_at = datetime.now().isoformat()
            self.run_record.steps.append(record)
            self.run_record.current_step_index = i

            self._log(f"▶️  步骤 {i+1}/{len(steps)}: [{step_name}] ({step_type})")
            self._emit("step_start", {"index": i, "step": step})

            # 确定重试策略
            retry = step.get("retry", global_retry)
            retry_delay = step.get("retry_delay", global_retry_delay)
            on_error = step.get("on_error", global_on_error)

            # 执行 (含重试)
            node_result = self._execute_with_retry(step, retry, retry_delay, record)

            record.finished_at = datetime.now().isoformat()

            if node_result.success:
                record.status = "success"
                record.result = node_result.to_dict()

                # 保存输出到上下文
                export_key = step.get("export") or step.get("save_to") or step_id
                if node_result.output is not None:
                    self.ctx.set_output(export_key, node_result.output)

                # 处理控制流节点
                if step_type == "condition":
                    sub_steps = node_result.output.get("steps", [])
                    if sub_steps:
                        branch_ok = self._execute_steps(
                            sub_steps, global_retry, global_retry_delay, global_on_error, global_timeout
                        )
                        if not branch_ok:
                            return False

                elif step_type == "loop":
                    loop_ok = self._execute_loop(
                        node_result.output, global_retry, global_retry_delay, global_on_error, global_timeout
                    )
                    if not loop_ok:
                        return False

                self._emit("step_end", {"index": i, "result": node_result.to_dict()})

            else:
                record.status = "failed"
                record.error = node_result.error
                record.result = node_result.to_dict()

                self._log(f"❌ 步骤失败: {node_result.error}", "ERROR")
                self._emit("step_error", {"index": i, "error": node_result.error})

                # 错误策略
                if on_error == "stop" or node_result.action == "abort":
                    self._log("⛔ 工作流停止", "ERROR")
                    return False
                elif on_error == "skip":
                    record.status = "skipped"
                    self._log("⏭️  跳过失败步骤，继续执行", "WARN")
                    continue
                elif on_error == "ask":
                    self._log("🤚 需要人工介入 (当前自动跳过)", "WARN")
                    record.status = "skipped"
                    continue
                else:
                    # 默认停止
                    return False

            # 保存快照
            self._save_snapshot()

        return True

    def _execute_with_retry(
        self, step: Dict, max_retries: int, retry_delay: float, record: StepRecord
    ) -> NodeResult:
        """执行节点并处理重试"""
        step_type = step.get("type", "log")
        handler = NODE_HANDLERS.get(step_type)

        if not handler:
            return NodeResult(success=False, error=f"未知节点类型: {step_type}")

        attempt = 0
        while True:
            # 所有 handler 统一传入 bridge 参数
            result = handler(step, self.ctx, self._log, self._bridge)

            if result.success or attempt >= max_retries:
                record.retries = attempt
                return result

            attempt += 1
            self._log(f"🔄 重试 ({attempt}/{max_retries}), 等待 {retry_delay}s...", "WARN")
            time.sleep(retry_delay)

    @staticmethod
    def _steps_contain_type(steps: List[Dict], step_type: str) -> bool:
        """检查步骤列表 (含嵌套) 是否包含指定类型的节点。"""
        for s in steps:
            if s.get("type") == step_type:
                return True
            for key in ("then", "else", "do", "steps"):
                nested = s.get(key, [])
                if isinstance(nested, list) and WorkflowEngine._steps_contain_type(nested, step_type):
                    return True
        return False

    @staticmethod
    def _detect_batch_spawn_pattern(sub_steps: List[Dict]) -> Optional[Dict]:
        """
        检测循环体是否为 "subagent(wait=false) + code(collect)" 的 fire-and-forget 模式。

        标准模式:
          do:
            - type: subagent         # wait=false (默认)
              id: spawn_xxx
              task: "..."
            - type: code             # 收集 spawn 信息到 tracker
              id: collect_xxx

        Returns:
            如果匹配，返回 {"subagent_step": dict, "collect_step": dict | None, "other_steps": list}
            如果不匹配，返回 None
        """
        if not sub_steps:
            return None

        subagent_step = None
        collect_step = None
        other_steps = []

        for s in sub_steps:
            stype = s.get("type", "")
            if stype == "subagent" and not s.get("wait", False):
                if subagent_step is not None:
                    # 多个 subagent 步骤 — 不走批量
                    return None
                subagent_step = s
            elif stype == "code" and subagent_step is not None:
                # subagent 后面的 code 步骤视为 collect
                collect_step = s
            else:
                other_steps.append(s)

        if subagent_step is None:
            return None

        return {
            "subagent_step": subagent_step,
            "collect_step": collect_step,
            "other_steps": other_steps,
        }

    def _execute_loop(
        self,
        loop_data: Dict,
        global_retry: int,
        global_retry_delay: float,
        global_on_error: str,
        global_timeout: int,
    ) -> bool:
        """执行循环 — 自动选择最优执行模式"""
        parallel = loop_data.get("parallel", False)
        if parallel:
            return self._execute_loop_parallel(
                loop_data, global_retry, global_retry_delay, global_on_error, global_timeout
            )

        items = loop_data.get("items", [])
        var_name = loop_data.get("var", "item")
        sub_steps = loop_data.get("steps", [])

        # ── 检测是否可以用批量 spawn 模式 ──
        # 标准的 subagent fire-and-forget + collect 模式可以用批量 spawn 加速
        batch_pattern = self._detect_batch_spawn_pattern(sub_steps) if self._bridge else None

        if batch_pattern and len(items) > 1:
            return self._execute_loop_batch_spawn(
                items, var_name, sub_steps, batch_pattern,
                global_retry, global_retry_delay, global_on_error, global_timeout,
            )

        # ── 串行模式 (默认/回退) ──
        _has_subagent = self._steps_contain_type(sub_steps, "subagent")
        if _has_subagent and self._bridge:
            self._bridge.open_factory_session(total_expected=len(items))

        try:
            for idx, item in enumerate(items):
                self._log(f"🔁 循环 [{idx+1}/{len(items)}]: {var_name} = {str(item)[:100]}", "INFO")

                self.ctx.push_scope({
                    var_name: item,
                    f"{var_name}_index": idx,
                    "loop_index": idx,
                    "loop_length": len(items),
                })

                try:
                    ok = self._execute_steps(
                        sub_steps, global_retry, global_retry_delay, global_on_error, global_timeout
                    )
                    if not ok:
                        return False
                finally:
                    self.ctx.pop_scope()
        finally:
            if _has_subagent and self._bridge and self._bridge.factory_session_key:
                self._bridge.close_factory_session()

        return True

    def _execute_loop_batch_spawn(
        self,
        items: List,
        var_name: str,
        sub_steps: List[Dict],
        batch_pattern: Dict,
        global_retry: int,
        global_retry_delay: float,
        global_on_error: str,
        global_timeout: int,
    ) -> bool:
        """
        批量 spawn 模式 — 一次 agent_call 创建多个 subagent。

        利用 OpenClaw Agent 在单轮对话中可以并行调用多个 sessions_spawn 工具的能力，
        将 N 个 subagent 分批 (每批 batch_size 个) 发送给 Agent，大幅减少创建时间:
        - 旧方式: 24 × 25s = 600s (串行)
        - 新方式: 24 / 8 × ~30s = ~90s (批量并行)

        执行流程:
        1. 开启 factory session
        2. 调用 batch_spawn_subagents() 一次性创建所有 subagent
        3. 为每个 item 执行 collect step (收集 spawn 信息到 tracker)
        4. 执行 other_steps (如果有)
        """
        subagent_step = batch_pattern["subagent_step"]
        collect_step = batch_pattern.get("collect_step")
        other_steps = batch_pattern.get("other_steps", [])

        batch_size = int(subagent_step.get("spawn_batch_size", 8))
        subagent_id = subagent_step.get("id") or subagent_step.get("name") or "subagent"
        collect_id = collect_step.get("id") or collect_step.get("name") or "collect" if collect_step else None

        self._log(
            f"🏭 批量 spawn 模式: {len(items)} 个 subagent, "
            f"每批 {batch_size} 个, 预计 {(len(items) + batch_size - 1) // batch_size} 批",
            "INFO",
        )

        # 开启 factory session
        self._bridge.open_factory_session(total_expected=len(items))

        try:
            # 传递 var_name 给 batch_spawn 用于模板解析
            step_template = dict(subagent_step)
            step_template["_var_name"] = var_name

            # ── 阶段 1: 批量 spawn ──
            spawn_results = batch_spawn_subagents(
                items=items,
                step_template=step_template,
                ctx=self._main_ctx,
                log=self._log,
                bridge=self._bridge,
                batch_size=batch_size,
            )

            # ── 阶段 2: 为每个 item 执行 collect step + other steps ──
            for idx, item in enumerate(items):
                # 取对应的 spawn 结果
                if idx < len(spawn_results):
                    spawn_output = spawn_results[idx]
                else:
                    spawn_output = {
                        "spawn_session_key": "",
                        "child_session_key": "",
                        "child_run_id": "",
                        "mode": subagent_step.get("mode", "run"),
                        "waited": False,
                    }

                # 设置 subagent 步骤的输出到 context (模拟 run_subagent 的返回值)
                self.ctx.set_output(subagent_id, spawn_output)

                # 创建局部作用域
                self.ctx.push_scope({
                    var_name: item,
                    f"{var_name}_index": idx,
                    "loop_index": idx,
                    "loop_length": len(items),
                })

                try:
                    # 执行 collect step
                    if collect_step:
                        from .nodes import NODE_HANDLERS
                        handler = NODE_HANDLERS.get(collect_step.get("type", "code"))
                        if handler:
                            result = handler(collect_step, self.ctx, self._log, self._bridge)
                            if result.success and result.output is not None:
                                export_key = (
                                    collect_step.get("export")
                                    or collect_step.get("save_to")
                                    or collect_step.get("id")
                                    or "collect"
                                )
                                self.ctx.set_output(export_key, result.output)

                    # 执行 other_steps
                    if other_steps:
                        ok = self._execute_steps(
                            other_steps, global_retry, global_retry_delay,
                            global_on_error, global_timeout,
                        )
                        if not ok:
                            return False
                finally:
                    self.ctx.pop_scope()

                # 保存快照
                self._save_snapshot()

        finally:
            if self._bridge.factory_session_key:
                self._bridge.close_factory_session()

        return True

    def _execute_loop_parallel(
        self,
        loop_data: Dict,
        global_retry: int,
        global_retry_delay: float,
        global_on_error: str,
        global_timeout: int,
    ) -> bool:
        """
        并行执行循环 — 使用线程池同时运行多个迭代。

        设计要点:
        - 每个线程通过 thread-local 获得独立的子 Context (共享 globals 引用)
        - Python GIL 保证 dict/list 原子操作 (如 tracker.append) 的线程安全
        - subprocess.run (Gateway RPC) 天然线程安全 (各自独立进程)
        - 快照写入通过 _snapshot_lock 防止文件损坏
        - max_parallel 限制并发数，与 subagent.maxConcurrent 配合防止 lane 过载
        """
        items = loop_data.get("items", [])
        var_name = loop_data.get("var", "item")
        sub_steps = loop_data.get("steps", [])
        max_parallel = loop_data.get("max_parallel", 4)
        total = len(items)

        self._log(f"🔁 并行循环启动: {total} 项, 最大并发: {max_parallel}", "INFO")

        # 工厂 session: 批量 subagent 创建共享 session，减少 session 数量
        _has_subagent = self._steps_contain_type(sub_steps, "subagent")
        if _has_subagent and self._bridge:
            self._bridge.open_factory_session(total_expected=total)

        failed_event = threading.Event()
        completed_count = [0]  # mutable for closure
        count_lock = threading.Lock()

        def run_iteration(idx: int, item):
            """单次循环迭代 — 在工作线程中执行"""
            if failed_event.is_set() or self._aborted:
                return True  # 跳过，但不标记为失败

            # 创建线程隔离的子 Context
            child_ctx = self._main_ctx.create_child_context({
                var_name: item,
                f"{var_name}_index": idx,
                "loop_index": idx,
                "loop_length": total,
            })

            # 设置 thread-local Context — self.ctx 属性会自动返回此上下文
            _engine_tls.ctx = child_ctx

            try:
                self._log(
                    f"🔁 并行循环 [{idx+1}/{total}]: {var_name} = {str(item)[:100]}",
                    "INFO",
                )
                ok = self._execute_steps(
                    sub_steps,
                    global_retry,
                    global_retry_delay,
                    global_on_error,
                    global_timeout,
                )
                if not ok:
                    failed_event.set()
                    return False

                with count_lock:
                    completed_count[0] += 1
                return True

            except Exception as e:
                self._log(f"❌ 并行循环 [{idx+1}/{total}] 异常: {e}", "ERROR")
                failed_event.set()
                return False
            finally:
                # 清除 thread-local Context，防止线程复用时残留
                if hasattr(_engine_tls, 'ctx'):
                    del _engine_tls.ctx

        # ── 使用线程池执行 ──
        with ThreadPoolExecutor(max_workers=max_parallel) as pool:
            future_to_idx = {
                pool.submit(run_iteration, i, item): i
                for i, item in enumerate(items)
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    result = future.result()
                    if not result:
                        self._log(f"❌ 并行循环迭代 [{idx+1}/{total}] 失败", "ERROR")
                except Exception as e:
                    self._log(f"❌ 并行循环迭代 [{idx+1}/{total}] 异常: {e}", "ERROR")
                    failed_event.set()

        # 关闭工厂 session (如果已开启)
        if _has_subagent and self._bridge and self._bridge.factory_session_key:
            self._bridge.close_factory_session()

        if failed_event.is_set():
            self._log(
                f"❌ 并行循环完成: {completed_count[0]}/{total} 成功 (有失败)",
                "ERROR",
            )
            return False

        self._log(f"✅ 并行循环完成: {completed_count[0]}/{total} 全部成功", "INFO")
        return True

    # ── 持久化 ────────────────────────────────────────────

    def _save_run(self):
        """保存运行记录"""
        self.RUNS_DIR.mkdir(parents=True, exist_ok=True)
        path = self.RUNS_DIR / f"{self.run_record.run_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.run_record.to_dict(), f, ensure_ascii=False, indent=2)
        self._log(f"📝 运行记录已保存: {path.name}")

    def _save_snapshot(self):
        """保存执行快照 (用于断点恢复) — 线程安全"""
        if not self.run_record:
            return
        with self._snapshot_lock:
            self.RUNS_DIR.mkdir(parents=True, exist_ok=True)
            path = self.RUNS_DIR / f"{self.run_record.run_id}.snapshot.json"
            snapshot = {
                "run": self.run_record.to_dict(),
                "context": self._main_ctx.snapshot(),  # 始终用主 Context 快照
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, ensure_ascii=False, indent=2)

    # ── 断点恢复 ──────────────────────────────────────────

    @classmethod
    def resume(cls, run_id: str, **kwargs) -> "WorkflowEngine":
        """从断点恢复执行"""
        snap_path = cls.RUNS_DIR / f"{run_id}.snapshot.json"
        if not snap_path.exists():
            raise FileNotFoundError(f"快照不存在: {snap_path}")

        with open(snap_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        engine = cls(**kwargs)
        engine.ctx.restore(snapshot["context"])
        # TODO: 从 current_step_index 恢复执行
        return engine

    # ── 工具方法 ──────────────────────────────────────────

    @staticmethod
    def list_workflows(
        directory: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """列出可用的工作流文件"""
        skill_dir = Path(__file__).resolve().parents[2]
        search_dirs = []
        if directory:
            search_dirs.append(Path(directory))

        # 默认搜索目录
        search_dirs.extend([
            skill_dir / "references" / "examples",
            Path(os.path.expanduser("~/.openclaw/workspace")),
        ])

        workflows = []
        seen_paths = set()
        for d in search_dirs:
            if not d.exists():
                continue
            for ext in ("*.yaml", "*.yml"):
                for f in d.rglob(ext):
                    real = str(f.resolve())
                    if real in seen_paths:
                        continue
                    seen_paths.add(real)
                    try:
                        with open(f, "r", encoding="utf-8") as fh:
                            data = yaml.safe_load(fh)
                        if isinstance(data, dict) and "steps" in data:
                            workflows.append({
                                "file": str(f),
                                "name": data.get("name") or data.get("flow_id") or f.stem,
                                "description": data.get("description", ""),
                                "steps": len(data.get("steps", [])),
                            })
                    except Exception:
                        pass

        return workflows

    @staticmethod
    def list_runs() -> List[Dict]:
        """列出历史运行记录"""
        runs_dir = WorkflowEngine.RUNS_DIR
        if not runs_dir.exists():
            return []

        runs = []
        for f in sorted(runs_dir.glob("*.json"), reverse=True):
            if f.name.endswith(".snapshot.json"):
                continue
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    runs.append(json.load(fh))
            except Exception:
                pass

        return runs[:50]  # 最近 50 条

    def abort(self):
        """中止执行"""
        self._aborted = True
        self._log("⛔ 收到中止信号", "WARN")
