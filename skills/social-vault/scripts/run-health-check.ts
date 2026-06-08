/**
 * SocialVault 健康检查 CLI 入口
 *
 * 此文件是唯一同时引用文件操作和网络验证的组装点。
 * health-check.ts 仅做文件 I/O，session-verifier.ts 仅做网络请求。
 *
 * 用法: npx tsx scripts/run-health-check.ts [vault-dir] [skill-dir]
 */

import { resolve } from "node:path";
import { runHealthCheck, formatReport } from "./health-check.js";
import { verifyViaApi } from "./session-verifier.js";

const vaultDir = resolve(process.argv[2] || "vault");
const skillDir = resolve(process.argv[3] || ".");

runHealthCheck(vaultDir, skillDir, verifyViaApi).then((results) => {
  const report = formatReport(results);
  console.log(report);

  const hasIssues = results.some(
    (r) => r.currentStatus === "expired" || r.currentStatus === "degraded"
  );

  if (hasIssues) {
    process.exit(1);
  }
}).catch((err) => {
  console.error(`健康检查失败: ${(err as Error).message}`);
  process.exit(2);
});
