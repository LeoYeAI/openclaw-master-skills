#!/usr/bin/env tsx
/**
 * KnowledgeQuerySkill — 知识查询入口
 *
 * 检索知识库并返回相关知识条目。
 * 使用 ContextInjector 进行语义检索 + 相关性评分。
 *
 * 用法:
 *   tsx query.ts --query "查询文本" [--budget <tokens>]
 */

import { resolve } from 'node:path';
import { ContextInjector } from '../../../src/injection/context-injector.js';
import { KnowledgeRepository } from '../../../src/repository/knowledge-repository.js';
import { SQLiteProvider } from '../../../src/repository/sqlite-provider.js';

const DB_PATH = resolve(process.cwd(), '.kivo/knowledge.db');

function parseArgs() {
  const args = process.argv.slice(2);
  let query: string | undefined;
  let budget = 2000;

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--query':
        query = args[++i];
        break;
      case '--budget':
        budget = parseInt(args[++i], 10);
        break;
    }
  }

  if (!query) {
    console.error('用法: tsx query.ts --query "查询文本" [--budget <tokens>]');
    process.exit(1);
  }

  return { query, budget };
}

async function main() {
  const { query, budget } = parseArgs();

  const provider = new SQLiteProvider({ dbPath: DB_PATH });
  const repository = new KnowledgeRepository(provider);
  const injector = new ContextInjector({ repository });

  try {
    const response = await injector.inject({
      userQuery: query,
      tokenBudget: budget,
    });

    if (response.entries.length === 0) {
      console.log('未找到相关知识条目。');
      return;
    }

    console.log(`✓ 查询完成 — ${response.entries.length} 条匹配，${response.tokensUsed} tokens`);
    if (response.truncated) {
      console.log('  (结果已截断，可增大 --budget)');
    }

    console.log('\n--- 条目摘要 ---');
    for (const e of response.entries) {
      console.log(`  [${e.type}] ${e.summary} (${e.entryId})`);
    }
  } finally {
    await provider.close();
  }
}

main().catch(err => {
  console.error('查询失败:', err.message);
  process.exit(1);
});
