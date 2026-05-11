/**
 * hermes-integration.ts
 * Hermes 侧接入示例
 *
 * Hermes 需要做的配置（3步，10分钟完成）：
 *
 * 步骤 1：安装依赖
 *   npm install eventsource
 *
 * 步骤 2：在 Hermes 的启动脚本/入口文件中引入本文件
 *   import "./hermes-integration.js";
 *
 * 步骤 3：设置环境变量
 *   export HUB_URL=http://localhost:3100  (Hub 服务器地址)
 *   export HERMES_ID=hermes               (本 Agent 的唯一 ID，可自定义)
 *
 * 完成！Hermes 启动后会自动：
 *  - 连接 Hub 的 SSE 端点
 *  - 接收 WorkBuddy 分配的任务并自主执行
 *  - 汇报执行进度和结果
 *  - 断线后自动重连
 */
import { AgentClient } from "../client-sdk/agent-client.js";

const HERMES_ID = process.env.HERMES_ID ?? "hermes";
const HUB_URL   = process.env.HUB_URL   ?? "http://localhost:3100";

// ─── 1. 创建 Hermes 客户端 ─────────────────────────────
const hermes = new AgentClient({
  agentId: HERMES_ID,
  hubUrl:  HUB_URL,

  // ╔══════════════════════════════════════════════════╗
  // ║  核心：收到任务时自主执行，无需人工干预              ║
  // ╚══════════════════════════════════════════════════╝
  onTaskAssigned: async (task) => {
    console.log(`\n[Hermes] 📋 收到来自 ${task.assigned_by} 的任务`);
    console.log(`  任务ID:  ${task.id}`);
    console.log(`  优先级: ${task.priority}`);
    console.log(`  描述:    ${task.description}`);
    if (task.context) console.log(`  上下文: ${task.context}`);

    // ── 第一步：立刻回报"已接收，开始执行" ─────────────
    await hermes.updateTaskStatus(task.id, "in_progress", undefined, 5);

    try {
      // ── 第二步：调用 Hermes 自己的执行能力 ────────────
      // 在这里对接你的 Hermes Agent 核心逻辑
      // 可以是：LLM 调用、工具调用、文件操作、数据处理等
      const result = await executeHermesTask(task);

      // ── 第三步：汇报完成 ────────────────────────────
      await hermes.updateTaskStatus(task.id, "completed", result, 100);
      console.log(`[Hermes] ✅ 任务 ${task.id} 已完成`);

    } catch (err: any) {
      await hermes.updateTaskStatus(task.id, "failed", `执行错误: ${err.message}`, 0);
      console.error(`[Hermes] ❌ 任务 ${task.id} 失败:`, err.message);
    }
  },

  // ── 收到普通消息 ───────────────────────────────────
  onMessage: async (msg) => {
    console.log(`\n[Hermes] 💬 来自 ${msg.from_agent}: ${msg.content}`);

    // 处理不同类型的消息
    if (msg.type === "ack") {
      console.log(`[Hermes] 收到确认消息，无需回复`);
      return;
    }

    // 普通消息，可触发 Hermes 的对话能力
    await handleHermesMessage(msg);
  },

  // ── 收到任务进度更新（自己委托给别人的任务）────────────
  onTaskUpdated: async (upd) => {
    const icon = upd.status === "completed" ? "✅" : upd.status === "failed" ? "❌" : "⏳";
    console.log(`\n[Hermes] ${icon} 委托任务进度: ${upd.task_id}`);
    console.log(`  状态: ${upd.status}  进度: ${upd.progress}%`);
    if (upd.result) {
      console.log(`  结果: ${upd.result}`);
      // 可以在这里把 WorkBuddy 的执行结果进一步处理
      await processTaskResult(upd.task_id, upd.result);
    }
  },
});

// ─── 2. 启动 Hermes 客户端 ─────────────────────────────
hermes.start();
console.log(`[Hermes] 已启动，Agent ID: ${HERMES_ID}`);
console.log(`[Hermes] 正在连接 Hub: ${HUB_URL}`);

// ─── 任务执行核心逻辑（对接你的 Hermes 业务代码）──────────
async function executeHermesTask(task: any): Promise<string> {
  const { description, context, id } = task;

  // ── 中途汇报进度示例 ───────────────────────────────
  await hermes.updateTaskStatus(id, "in_progress", "正在收集数据...", 20);

  // TODO: 在这里对接 Hermes 的实际能力：
  //  - 调用 LLM（如 Claude API）
  //  - 执行 MCP 工具（WebSearch、文件读写等）
  //  - 访问数据库或外部 API
  //  - 运行 Python 脚本等

  // 示例：模拟分阶段执行
  await new Promise(r => setTimeout(r, 1500));
  await hermes.updateTaskStatus(id, "in_progress", "正在分析处理...", 60);

  await new Promise(r => setTimeout(r, 1500));
  await hermes.updateTaskStatus(id, "in_progress", "正在生成报告...", 90);

  await new Promise(r => setTimeout(r, 500));

  // 返回结构化结果
  return JSON.stringify({
    summary:  `Hermes 完成了任务：${description.slice(0, 80)}`,
    data:     { processed: true, context },
    timestamp: new Date().toISOString(),
  }, null, 2);
}

// ─── 消息处理逻辑 ──────────────────────────────────────
async function handleHermesMessage(msg: any): Promise<void> {
  // TODO: 根据业务需求处理消息
  // 示例：简单回复
  if (msg.content.includes("你好")) {
    await hermes.sendMessage(msg.from_agent, "你好！Hermes 在线，随时待命。");
  }
}

// ─── 处理收到的任务结果 ────────────────────────────────
async function processTaskResult(taskId: string, result: string): Promise<void> {
  // TODO: 处理 WorkBuddy 返回的结果
  console.log(`[Hermes] 处理任务 ${taskId} 的结果...`);
}

// ─── 导出实例（供其他模块使用）──────────────────────────
export { hermes };
