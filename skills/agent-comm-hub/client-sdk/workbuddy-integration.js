/**
 * workbuddy-integration.ts
 * WorkBuddy 侧接入示例
 *
 * 这个文件展示 WorkBuddy 如何：
 *  1. 连接 Hub（一行代码）
 *  2. 向 Hermes 分配任务
 *  3. 实时接收 Hermes 的执行结果
 *  4. 处理 Hermes 发来的协作请求
 */
import { AgentClient } from "../client-sdk/agent-client.js";
// ─── 1. 创建 WorkBuddy 客户端 ──────────────────────────
const workbuddy = new AgentClient({
    agentId: "workbuddy",
    hubUrl: process.env.HUB_URL ?? "http://localhost:3100",
    // ── 收到任务时（Hermes 委托 WorkBuddy 做某事）──────────
    onTaskAssigned: async (task) => {
        console.log(`\n[WorkBuddy] 📋 收到来自 ${task.assigned_by} 的任务`);
        console.log(`  描述: ${task.description}`);
        console.log(`  优先级: ${task.priority}`);
        // 立刻回报"已开始"
        await workbuddy.updateTaskStatus(task.id, "in_progress", undefined, 0);
        try {
            // ── 在这里放 WorkBuddy 的实际执行逻辑 ──────────────
            const result = await executeWorkBuddyTask(task.description, task.context);
            await workbuddy.updateTaskStatus(task.id, "completed", result, 100);
            console.log(`[WorkBuddy] ✅ 任务 ${task.id} 完成`);
        }
        catch (err) {
            await workbuddy.updateTaskStatus(task.id, "failed", err.message, 0);
            console.error(`[WorkBuddy] ❌ 任务 ${task.id} 失败:`, err.message);
        }
    },
    // ── 收到普通消息 ──────────────────────────────────────
    onMessage: async (msg) => {
        console.log(`\n[WorkBuddy] 💬 来自 ${msg.from_agent}: ${msg.content}`);
        // 根据消息内容决定是否需要回复
        if (msg.content.includes("确认")) {
            await workbuddy.sendMessage(msg.from_agent, "已确认，WorkBuddy 收到。");
        }
    },
    // ── 任务进度回调（自己发出去的任务被执行时触发）─────────
    onTaskUpdated: async (upd) => {
        const icon = upd.status === "completed" ? "✅" : upd.status === "failed" ? "❌" : "⏳";
        console.log(`\n[WorkBuddy] ${icon} 任务 ${upd.task_id} 进度更新`);
        console.log(`  状态: ${upd.status}  进度: ${upd.progress}%`);
        if (upd.result)
            console.log(`  结果: ${upd.result}`);
    },
});
// ─── 2. 启动 ───────────────────────────────────────────
workbuddy.start();
// ─── 3. 示例：向 Hermes 分配任务 ──────────────────────
async function runDemo() {
    // 等待连接稳定
    await new Promise(r => setTimeout(r, 1000));
    // 先检查 Hermes 是否在线
    const online = await workbuddy.getOnlineAgents();
    console.log("\n[WorkBuddy] 当前在线 Agents:", online);
    if (online.includes("hermes")) {
        // 分配任务给 Hermes
        const result = await workbuddy.assignTask("hermes", "请分析最近 7 天辽宁省媒体融合相关新闻，提取关键事件并按重要性排序，输出 Markdown 格式报告", "重点关注：辽望客户端、北斗融媒、省级媒体政策。输出结构：摘要 + 事件列表 + 趋势分析", "high");
        console.log("\n[WorkBuddy] 任务已分配:", result);
    }
    else {
        console.log("[WorkBuddy] Hermes 不在线，任务将在其上线后自动推送");
        // 即使离线也可以分配，Hub 会自动补发
        await workbuddy.assignTask("hermes", "这是一条离线任务，Hermes 上线后会自动收到并执行", "", "normal");
    }
}
// ─── 任务执行逻辑（接入你的实际业务代码）──────────────
async function executeWorkBuddyTask(description, context) {
    // TODO: 替换为 WorkBuddy 真实的 Agent SDK 调用
    console.log(`[WorkBuddy] 执行任务: ${description}`);
    await new Promise(r => setTimeout(r, 2000)); // 模拟执行耗时
    return `WorkBuddy 执行完成: ${description.slice(0, 50)}...`;
}
// 运行示例
runDemo().catch(console.error);
//# sourceMappingURL=workbuddy-integration.js.map