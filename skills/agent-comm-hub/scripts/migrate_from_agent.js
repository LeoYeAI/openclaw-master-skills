#!/usr/bin/env node
/**
 * migrate_from_agent.js — Phase 2.1 数据迁移
 * 将历史消息中不规范的发件人标识规范化
 *
 * 运行前：确保 Hub 服务已停止（或使用离线备份数据库）
 * 运行方式：node scripts/migrate_from_agent.js
 */
import Database from "better-sqlite3";
import { resolve } from "path";

const DB_PATH = resolve(process.cwd(), "comm_hub.db");
const db = new Database(DB_PATH);

// 别名映射（与 src/identity.ts 保持同步）
const ALIAS_MAP = {
  qclaw:    "agent_1c11a7bd_1777129814251",
  workbuddy: "agent_workbuddy_a3f7c2e1_1777300825754",
  hermes:   "agent_hermes_54cfe58b_1777132066111",
};

console.log(`\n=== Phase 2.1: from_agent 格式规范化迁移 ===`);
console.log(`DB: ${DB_PATH}\n`);

let totalFrom = 0;
let totalTo = 0;

// 从 from_agent 开始迁移
for (const [alias, fullId] of Object.entries(ALIAS_MAP)) {
  const fromResult = db.prepare(
    `UPDATE messages SET from_agent = ? WHERE from_agent = ?`
  ).run(fullId, alias);
  if (fromResult.changes > 0) {
    console.log(`✅ from_agent: '${alias}' → '${fullId}' (${fromResult.changes} 行)`);
    totalFrom += fromResult.changes;
  }

  const toResult = db.prepare(
    `UPDATE messages SET to_agent = ? WHERE to_agent = ?`
  ).run(fullId, alias);
  if (toResult.changes > 0) {
    console.log(`✅ to_agent:   '${alias}' → '${fullId}' (${toResult.changes} 行)`);
    totalTo += toResult.changes;
  }
}

// 验证：确认无遗留别名
console.log(`\n验证：`);
// 检查 from_agent 是否还有别名
const remainingFrom = db.prepare(`
  SELECT DISTINCT from_agent FROM messages
  WHERE from_agent IN (${Object.keys(ALIAS_MAP).map(() => '?').join(',')})
`).all(...Object.keys(ALIAS_MAP));

if (remainingFrom.length === 0) {
  console.log(`✅ 所有 from_agent 已规范化`);
} else {
  console.log(`⚠️  仍有未处理的 from_agent: ${remainingFrom.map(r => r.from_agent).join(', ')}`);
}

const remainingTo = db.prepare(`
  SELECT DISTINCT to_agent FROM messages
  WHERE to_agent IN (${Object.keys(ALIAS_MAP).map(() => '?').join(',')})
`).all(...Object.keys(ALIAS_MAP));

if (remainingTo.length === 0) {
  console.log(`✅ 所有 to_agent 已规范化`);
} else {
  console.log(`⚠️  仍有未处理的 to_agent: ${remainingTo.map(r => r.to_agent).join(', ')}`);
}

// 统计
const total = db.prepare(`SELECT COUNT(*) as cnt FROM messages`).get();
console.log(`\n总计：迁移 ${totalFrom} 条 from_agent，${totalTo} 条 to_agent`);
console.log(`消息表总行数：${total.cnt}`);

db.close();
console.log(`\n✅ 迁移完成`);
