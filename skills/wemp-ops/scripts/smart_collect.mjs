#!/usr/bin/env node
/**
 * 智能热点采集 - AI 扩展关键词后调用 fetch_news.py
 */
import { spawn } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadConfig, output, outputError, parseArgs, formatDate, writeData } from './lib/utils.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const FETCH_SCRIPT = join(__dirname, 'fetch_news.py');

async function collectFromSource(source, keywords, limit, deep) {
  const args = ['python3', FETCH_SCRIPT, '--source', source, '--limit', String(limit)];
  if (keywords?.length) args.push('--keyword', keywords.join(','));
  if (deep) args.push('--deep');

  return new Promise((resolve, reject) => {
    const proc = spawn(args[0], args.slice(1), { stdio: ['pipe', 'pipe', 'pipe'], timeout: 120000 });
    let stdout = '', stderr = '';
    proc.stdout.on('data', d => { stdout += d; });
    proc.stderr.on('data', d => { stderr += d; process.stderr.write(d); });
    proc.on('close', code => {
      if (code !== 0) return reject(new Error(`采集失败 (${source}): ${stderr.slice(0, 300)}`));
      try { resolve(JSON.parse(stdout)); } catch (e) { reject(new Error(`解析失败 (${source}): ${e.message}`)); }
    });
    proc.on('error', reject);
  });
}

function scoreRelevance(item, keywords) {
  const title = (item.title || '').toLowerCase();
  const content = (item.content || '').toLowerCase();
  let score = 0;
  for (const kw of keywords) {
    const k = kw.toLowerCase();
    if (title.includes(k)) score += 0.3;
    if (content.includes(k)) score += 0.15;
  }
  const heat = parseInt(String(item.score).replace(/[^0-9]/g, '')) || 0;
  if (heat > 500) score += 0.2;
  else if (heat > 100) score += 0.1;
  return Math.min(score, 1);
}

async function main() {
  const args = parseArgs();
  if (!args.query) { outputError(new Error('请指定 --query 参数')); return; }

  const keywords = args.keywords ? args.keywords.split(',').map(k => k.trim()) : [];
  const sources = args.sources ? args.sources.split(',').map(s => s.trim()) : ['hackernews', 'v2ex', '36kr'];
  const deep = args.deep === true || args.deep === 'true';
  const count = parseInt(args.count) || 20;

  console.error(`\n🔍 智能采集`);
  console.error(`   需求: ${args.query}`);
  console.error(`   关键词: ${keywords.join(', ')}`);
  console.error(`   数据源: ${sources.join(', ')}`);
  console.error('');

  const allItems = [];
  for (const source of sources) {
    try {
      const items = await collectFromSource(source, keywords, Math.ceil(count / sources.length) + 5, deep);
      allItems.push(...items);
    } catch (e) { console.error(`[采集] ${source} 失败: ${e.message}`); }
  }

  // 评分、去重、排序
  const scored = allItems.map(i => ({ ...i, relevance: scoreRelevance(i, keywords) }));
  scored.sort((a, b) => b.relevance - a.relevance);
  const seen = new Set();
  const unique = scored.filter(i => {
    const k = (i.title || '').toLowerCase().replace(/[^a-z0-9\u4e00-\u9fa5]/g, '').slice(0, 30);
    if (seen.has(k)) return false;
    seen.add(k); return true;
  }).slice(0, count);

  const result = { query: args.query, keywords, sources, deep, date: formatDate(), items: unique, collectedAt: new Date().toISOString() };
  writeData('collected-news.json', result);

  console.error(`\n✅ 采集完成，共 ${unique.length} 条`);
  console.error('\n📰 相关度最高的 5 条:');
  for (const item of unique.slice(0, 5)) {
    const tag = item.relevance > 0.5 ? '🔥' : item.relevance > 0.2 ? '📌' : '📄';
    console.error(`  ${tag} [${item.source}] ${(item.title || '').slice(0, 50)}`);
  }

  output(true, result);
}

main();
