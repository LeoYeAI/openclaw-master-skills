#!/usr/bin/env node
/**
 * Four.meme - token list (REST API)
 * POST /meme-api/v1/public/token/search
 *
 * Usage: fourmeme token-list [options]
 *   New: --type= --listType= --keyword= --symbol= --tag= --status= --sort= --version= --pageIndex= --pageSize=
 *   Legacy: --orderBy=Hot|TimeDesc|Time (maps to type+sort), --tokenName= (->keyword), --labels= (->tag), --listedPancake= (->status)
 * Output: JSON list of tokens.
 */

const API_BASE = 'https://four.meme/meme-api/v1';

const ORDERBY_TO_TYPE: Record<string, { type: string; sort?: string }> = {
  Hot: { type: 'HOT' },
  TimeDesc: { type: 'NEW', sort: 'DESC' },
  Time: { type: 'NEW' },
};

function parseArg(name: string, defaultValue: string): string {
  const prefix = `--${name}=`;
  for (let i = 2; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg.startsWith(prefix)) return arg.slice(prefix.length);
  }
  return defaultValue;
}

async function main() {
  const orderBy = parseArg('orderBy', 'Hot');
  const tokenName = parseArg('tokenName', '');
  const listedPancake = parseArg('listedPancake', 'false');
  const pageIndex = parseArg('pageIndex', '1');
  const pageSize = parseArg('pageSize', '20');
  const symbol = parseArg('symbol', '');
  const labels = parseArg('labels', '');

  // New params (override legacy when provided)
  const typeArg = parseArg('type', '');
  const listType = parseArg('listType', '');
  const keyword = parseArg('keyword', tokenName);
  const tagArg = parseArg('tag', labels);
  const statusArg = parseArg('status', '');
  const sortArg = parseArg('sort', '');
  const version = parseArg('version', '');

  const body: Record<string, string | number | string[]> = {
    pageIndex: parseInt(pageIndex, 10) || 1,
    pageSize: parseInt(pageSize, 10) || 20,
  };

  if (listType) {
    body.listType = listType;
  } else if (listedPancake === 'true') {
    body.listType = 'NOR_DEX';
  } else {
    body.listType = 'NOR';
  }

  if (typeArg) {
    body.type = typeArg;
  } else if (body.listType === 'NOR_DEX') {
    body.type = 'NEW';
    body.sort = 'DESC';
  } else if (ORDERBY_TO_TYPE[orderBy]) {
    const mapped = ORDERBY_TO_TYPE[orderBy];
    body.type = mapped.type;
    if (mapped.sort) body.sort = mapped.sort;
  } else {
    body.type = 'HOT';
  }
  if (keyword) body.keyword = keyword;
  if (symbol) body.symbol = symbol;
  if (tagArg) {
    body.tag = tagArg.split(',').map((s) => s.trim()).filter(Boolean);
  }
  if (statusArg) body.status = statusArg;
  else if (body.listType === 'NOR_DEX') body.status = 'TRADE';
  if (sortArg) body.sort = sortArg;
  else if (!body.sort) body.sort = 'DESC';
  if (version) body.version = version;

  const url = `${API_BASE}/public/token/search`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  const ok = (data.code === 0 || data.code === '0') && res.ok;

  if (!ok) {
    throw new Error(`token/search failed: ${res.status} ${JSON.stringify(data)}`);
  }
  console.log(JSON.stringify(data, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
