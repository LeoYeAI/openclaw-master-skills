#!/usr/bin/env tsx
/**
 * KnowledgeIngestSkill — 知识摄入入口
 *
 * 从对话或文档中提取并存储结构化知识。
 *
 * 用法:
 *   tsx ingest.ts --file <path> --source <label>
 *   tsx ingest.ts --text "内容" --source <label>
 */

import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { Kivo } from '../../../src/kivo.js';

const DB_PATH = resolve(process.cwd(), '.kivo/knowledge.db');

function parseArgs() {
  const args = process.argv.slice(2);
  let file: string | undefined;
  let text: string | undefined;
  let source = 'cli';

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--file':
        file = args[++i];
        break;
      case '--text':
        text = args[++i];
        break;
      case '--source':
        source = args[++i];
        break;
    }
  }

  if (!file && !text) {
    console.error('用法: tsx ingest.ts --file <path> | --text "内容" [--source <label>]');
    process.exit(1);
  }

  const content = file ? readFileSync(resolve(file), 'utf-8') : text!;
  return { content, source };
}

async function main() {
  const { content, source } = parseArgs();

  const kivo = new Kivo({ dbPath: DB_PATH });
  await kivo.init();

  try {
    const result = await kivo.ingest(content, source);

    console.log(`✓ 摄入完成`);
    console.log(`  条目数: ${result.entries.length}`);
    console.log(`  冲突数: ${result.conflicts.length}`);

    if (result.entries.length > 0) {
      console.log(`  条目列表:`);
      for (const entry of result.entries) {
        console.log(`    - [${entry.type}] ${entry.title}`);
      }
    }

    if (result.conflicts.length > 0) {
      console.log(`  冲突详情:`);
      for (const c of result.conflicts) {
        console.log(`    ⚠ ${c.incomingId} ↔ ${c.existingId} (${c.verdict})`);
      }
    }
  } finally {
    await kivo.shutdown();
  }
}

main().catch(err => {
  console.error('摄入失败:', err.message);
  process.exit(1);
});
