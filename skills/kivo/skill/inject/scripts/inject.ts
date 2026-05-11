#!/usr/bin/env tsx
/**
 * ContextInjectSkill — 上下文注入入口
 *
 * 为当前任务自动注入相关知识上下文。
 *
 * 用法:
 *   tsx inject.ts --query "当前请求" [--budget <tokens>] [--format markdown|plain]
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
  let format: 'markdown' | 'plain' = 'markdown';

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--query':
        query = args[++i];
        break;
      case '--budget':
        budget = parseInt(args[++i], 10);
        break;
      case '--format':
        format = args[++i] as 'markdown' | 'plain';
        break;
    }
  }

  if (!query) {
    console.error('用法: tsx inject.ts --query "当前请求" [--budget <tokens>] [--format markdown|plain]');
    process.exit(1);
  }

  return { query, budget, format };
}

async function main() {
  const { query, budget, format } = parseArgs();

  const provider = new SQLiteProvider({ dbPath: DB_PATH });
  const repository = new KnowledgeRepository(provider);
  const injector = new ContextInjector({ repository });

  try {
    const response = await injector.inject({
      userQuery: query,
      tokenBudget: budget,
    });

    if (response.entries.length === 0) {
      console.log('无相关知识可注入。');
      return;
    }

    console.log(`✓ 注入完成 — ${response.entries.length} 条，${response.tokensUsed} tokens`);
    if (response.truncated) {
      console.log('  (结果已截断，可增大 --budget)');
    }

    console.log('\n--- 注入上下文 ---\n');
    console.log(response.injectedContext);
  } finally {
    await provider.close();
  }
}

main().catch(err => {
  console.error('注入失败:', err.message);
  process.exit(1);
});
