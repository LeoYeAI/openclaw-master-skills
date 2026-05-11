#!/usr/bin/env tsx
/**
 * ConflictResolveSkill — 冲突裁决入口
 *
 * 处理知识冲突的人工裁决请求。
 * 注意：ConflictResolver 是纯策略类，需要配合 Repository 获取冲突记录和条目。
 * 当前为 stub 实现，待 Repository 暴露冲突查询接口后完善。
 *
 * 用法:
 *   tsx resolve.ts --list
 *   tsx resolve.ts --id <conflict-id> --verdict newer-wins|confidence-wins|manual
 */

import { resolve } from 'node:path';
import { ConflictResolver, type ResolutionResult } from '../../../src/conflict/conflict-resolver.js';
import type { ConflictRecord, ResolutionStrategy } from '../../../src/conflict/conflict-record.js';
import { KnowledgeRepository } from '../../../src/repository/knowledge-repository.js';
import { SQLiteProvider } from '../../../src/repository/sqlite-provider.js';

const DB_PATH = resolve(process.cwd(), '.kivo/knowledge.db');

function parseArgs() {
  const args = process.argv.slice(2);
  let list = false;
  let id: string | undefined;
  let verdict: ResolutionStrategy | undefined;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--list':
        list = true;
        break;
      case '--id':
        id = args[++i];
        break;
      case '--verdict':
        verdict = args[++i] as ResolutionStrategy;
        break;
    }
  }

  if (!list && !id) {
    console.error('用法: tsx resolve.ts --list | --id <conflict-id> --verdict newer-wins|confidence-wins|manual');
    process.exit(1);
  }

  if (id && !verdict) {
    console.error('错误: --id 必须配合 --verdict 使用');
    process.exit(1);
  }

  return { list, id, verdict };
}

async function main() {
  const { list, id, verdict } = parseArgs();

  const provider = new SQLiteProvider({ dbPath: DB_PATH });
  const repository = new KnowledgeRepository(provider);

  try {
    if (list) {
      // TODO: 待 Repository 暴露 listUnresolvedConflicts() 接口后实现
      // 当前通过 repository 查询 unresolved conflict records
      console.log('⚠ 冲突列表功能待 Repository 冲突查询接口完善后实现。');
      console.log('  当前可通过 src/conflict/conflict-detector.ts 检测冲突。');
      return;
    }

    // TODO: 完整实现需要：
    // 1. 从 Repository 获取 ConflictRecord (by id)
    // 2. 获取 incoming 和 existing KnowledgeEntry
    // 3. 调用 ConflictResolver.resolve(record, incoming, existing, strategy)
    // 当前为 stub，展示调用方式
    console.log(`⚠ 裁决功能 stub — 待 Repository 冲突查询接口完善后实现。`);
    console.log(`  冲突 ID: ${id}`);
    console.log(`  策略: ${verdict}`);
    console.log('');
    console.log('  完整流程:');
    console.log('    1. repository.getConflictRecord(id)');
    console.log('    2. repository.getEntry(record.incomingId)');
    console.log('    3. repository.getEntry(record.existingId)');
    console.log('    4. resolver.resolve(record, incoming, existing, strategy)');
  } finally {
    await provider.close();
  }
}

main().catch(err => {
  console.error('裁决失败:', err.message);
  process.exit(1);
});
