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
declare const hermes: AgentClient;
export { hermes };
