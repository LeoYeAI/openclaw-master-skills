#!/usr/bin/env node
/**
 * Four.meme - token rankings (REST API)
 * POST /meme-api/v1/public/token/ranking
 * Body: { type, rankingKind?, version?, symbol?, minCap?, maxCap?, minVol?, maxVol?, minHold?, maxHold?, pageSize? }
 *
 * Usage: fourmeme token-rankings <type> [options]
 *   type: NEW | PROGRESS | VOL_MIN_5 | VOL_MIN_30 | VOL_HOUR_1 | VOL_HOUR_4 | VOL_DAY_1 | VOL | LAST | HOT | CAP | DEX
 *   Legacy (mapped): Time->NEW, ProgressDesc->PROGRESS, TradingDesc->VOL_DAY_1, Hot->HOT, Graduated->DEX
 *   options: --rankingKind= --version= --symbol= --minCap= --maxCap= --minVol= --maxVol= --minHold= --maxHold= --pageSize=20
 * Output: JSON ranking list.
 */

const API_BASE = 'https://four.meme/meme-api/v1';

const VALID_TYPES = [
  'NEW',
  'PROGRESS',
  'VOL_MIN_5',
  'VOL_MIN_30',
  'VOL_HOUR_1',
  'VOL_HOUR_4',
  'VOL_DAY_1',
  'VOL',
  'LAST',
  'HOT',
  'CAP',
  'DEX',
];

const LEGACY_MAP: Record<string, string> = {
  Time: 'NEW',
  ProgressDesc: 'PROGRESS',
  TradingDesc: 'VOL_DAY_1',
  Hot: 'HOT',
  Graduated: 'DEX',
};

function parseArg(name: string, defaultValue?: string): string | undefined {
  const prefix = `--${name}=`;
  for (let i = 3; i < process.argv.length; i++) {
    const arg = process.argv[i];
    if (arg.startsWith(prefix)) return arg.slice(prefix.length);
  }
  return defaultValue;
}

function parseNumArg(name: string): number | undefined {
  const v = parseArg(name);
  if (v === undefined) return undefined;
  const n = Number(v);
  return Number.isNaN(n) ? undefined : n;
}

async function main() {
  const typeArg = process.argv[2];
  const type = typeArg ? (LEGACY_MAP[typeArg] ?? typeArg) : undefined;

  if (!type || !VALID_TYPES.includes(type)) {
    console.error('Usage: fourmeme token-rankings <type> [options]');
    console.error(
      'type: NEW | PROGRESS | VOL_MIN_5 | VOL_MIN_30 | VOL_HOUR_1 | VOL_HOUR_4 | VOL_DAY_1 | VOL | LAST | HOT | CAP | DEX'
    );
    console.error('Legacy: Time, ProgressDesc, TradingDesc, Hot, Graduated');
    console.error('options: --rankingKind= --version= --symbol= --minCap= --maxCap= --minVol= --maxVol= --minHold= --maxHold= --pageSize=20');
    process.exit(1);
  }

  const body: Record<string, string | number> = { type };

  const rankingKind = parseArg('rankingKind');
  if (rankingKind) body.rankingKind = rankingKind;

  const version = parseArg('version');
  if (version) body.version = version;

  const symbol = parseArg('symbol');
  if (symbol) body.symbol = symbol;

  const minCap = parseNumArg('minCap');
  if (minCap !== undefined) body.minCap = minCap;

  const maxCap = parseNumArg('maxCap');
  if (maxCap !== undefined) body.maxCap = maxCap;

  const minVol = parseNumArg('minVol');
  if (minVol !== undefined) body.minVol = minVol;

  const maxVol = parseNumArg('maxVol');
  if (maxVol !== undefined) body.maxVol = maxVol;

  const minHold = parseNumArg('minHold');
  if (minHold !== undefined) body.minHold = minHold;

  const maxHold = parseNumArg('maxHold');
  if (maxHold !== undefined) body.maxHold = maxHold;

  const pageSize = parseNumArg('pageSize');
  if (pageSize !== undefined) body.pageSize = pageSize;

  const url = `${API_BASE}/public/token/ranking`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`token/ranking failed: ${res.status} ${await res.text()}`);
  }
  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

main().catch((e) => {
  console.error(e.message || e);
  process.exit(1);
});
