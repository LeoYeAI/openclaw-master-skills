#!/usr/bin/env npx ts-node
/**
 * web-autopilot: Browser Recorder
 * Records all user interactions + network traffic through any web app.
 * Supports SSO login, multi-tab capture, REST/GraphQL/Form.
 */

import { chromium, Browser, BrowserContext, Page, Request, Response } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import { program } from 'commander';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface CapturedRequest {
  id: string;
  seqNum: number;
  timestamp: number;
  relativeMs: number;
  method: string;
  url: string;
  headers: Record<string, string>;
  postData: string | null;
  postDataParsed?: any;
  resourceType: string;
}

export interface CapturedResponse {
  requestId: string;
  timestamp: number;
  status: number;
  statusText: string;
  headers: Record<string, string>;
  mimeType: string;
  body: string | null;
  bodyParsed?: any;
  truncated: boolean;
  isRedirect: boolean;
}

export interface UserAction {
  seqNum: number;
  timestamp: number;
  relativeMs: number;
  type: 'navigate' | 'click' | 'input' | 'select' | 'submit' | 'marker' | 'screenshot';
  url: string;
  target?: string;
  targetText?: string;
  targetType?: string;
  value?: string;
  label?: string;
  screenshotFile?: string;
}

export interface Recording {
  version: '1.0';
  taskName: string;
  startTime: number;
  endTime: number;
  durationMs: number;
  ssoUrl: string;
  finalUrl: string;
  requests: CapturedRequest[];
  responses: Record<string, CapturedResponse>;
  actions: UserAction[];
  finalCookies: any[];
  finalLocalStorage: Record<string, string>;
  finalSessionStorage: Record<string, string>;
  notes: string[];
  screenshotCount: number;
}

// ─── Config ───────────────────────────────────────────────────────────────────

const SKIP_RESOURCE_TYPES = new Set(['image', 'stylesheet', 'font', 'media', 'eventsource', 'ping']);
const SKIP_URL_PATTERNS: RegExp[] = [
  /google-analytics\.com/, /googletagmanager\.com/, /analytics\./,
  /hotjar\.com/, /fullstory\.com/, /mixpanel\.com/, /segment\.io/,
  /sentry\.io/, /bugsnag\.com/, /logrocket\.com/,
  /\.woff2?($|\?)/, /\.ttf($|\?)/, /\.eot($|\?)/,
  /\.png($|\?)/, /\.jpe?g($|\?)/, /\.gif($|\?)/, /\.svg($|\?)/,
  /\.ico($|\?)/, /\.webp($|\?)/, /^data:/, /^blob:/,
];
const MAX_BODY_SIZE = 200_000;

// ─── Helpers ──────────────────────────────────────────────────────────────────

function shouldCapture(request: Request): boolean {
  if (SKIP_RESOURCE_TYPES.has(request.resourceType())) return false;
  const url = request.url();
  if (SKIP_URL_PATTERNS.some(p => p.test(url))) return false;
  return true;
}

function tryParseJSON(str: string | null): any {
  if (!str) return undefined;
  try { return JSON.parse(str); } catch { return undefined; }
}

function tryParseFormData(str: string | null): any {
  if (!str) return undefined;
  try {
    const params = new URLSearchParams(str);
    const obj: Record<string, string> = {};
    params.forEach((v, k) => { obj[k] = v; });
    return Object.keys(obj).length > 0 ? obj : undefined;
  } catch { return undefined; }
}

function extractPostData(request: Request): { raw: string | null; parsed: any } {
  const raw = request.postData();
  if (!raw) return { raw: null, parsed: undefined };
  const contentType = request.headers()['content-type'] || '';
  let parsed: any;
  if (contentType.includes('application/json')) {
    parsed = tryParseJSON(raw);
  } else if (contentType.includes('application/x-www-form-urlencoded')) {
    parsed = tryParseFormData(raw);
  } else if (contentType.includes('multipart/form-data')) {
    parsed = { _note: 'multipart/form-data - see raw postData' };
  }
  return { raw: raw.length > 10_000 ? raw.substring(0, 10_000) + '...[truncated]' : raw, parsed };
}

// ─── Main ─────────────────────────────────────────────────────────────────────

program
  .name('record')
  .description('Record browser operations for web-autopilot automation')
  .requiredOption('-n, --name <name>', 'Task name (e.g. "提交报销单")')
  .option('-s, --sso-url <url>', 'SSO portal URL to open first')
  .option('-a, --app-url <url>', 'Directly open app URL (skip SSO)')
  .option('-o, --output <dir>', 'Output base directory', `${process.env.HOME}/.openclaw/rpa/recordings`)
  .option('--viewport <WxH>', 'Browser window size', '1440x900')
  .option('--no-screenshots', 'Disable auto screenshots at markers')
  .parse();

const opts = program.opts();

async function main() {
  const taskName: string = opts.name;
  const safeName = taskName.replace(/[^\w\u4e00-\u9fff-]/g, '_');
  const outputDir = path.join(opts.output, safeName);
  const ssDir = path.join(outputDir, 'screenshots');

  fs.mkdirSync(outputDir, { recursive: true });
  fs.mkdirSync(ssDir, { recursive: true });

  const startTime = Date.now();
  const requests: CapturedRequest[] = [];
  const responses: Record<string, CapturedResponse> = {};
  const actions: UserAction[] = [];
  const notes: string[] = [];

  const requestIndex = new WeakMap<Request, string>();
  let seqCounter = 0;
  let screenshotCount = 0;

  console.log('\n🎬  web-autopilot / recorder');
  console.log(`    Task    : ${taskName}`);
  console.log(`    Output  : ${outputDir}\n`);

  const browser: Browser = await chromium.launch({ headless: false, args: ['--start-maximized'] });
  const context: BrowserContext = await browser.newContext({ viewport: null, ignoreHTTPSErrors: true });
  const page: Page = await context.newPage();

  // ── Inject action tracker ──────────────────────────────────────────────────
  await context.addInitScript(() => {
    (window as any).__rpa_actions = [];
    function genSelector(el: Element): string {
      if (!el || el.nodeType !== 1) return 'unknown';
      const e = el as HTMLElement;
      if (e.id) return `#${e.id}`;
      const testId = e.getAttribute('data-testid') || e.getAttribute('data-test-id');
      if (testId) return `[data-testid="${testId}"]`;
      const name = e.getAttribute('name');
      if (name) return `[name="${name}"]`;
      const ariaLabel = e.getAttribute('aria-label');
      if (ariaLabel) return `[aria-label="${ariaLabel.substring(0, 40)}"]`;
      const classes = Array.from(e.classList).filter(c => !/^(hover|focus|active|is-|has-|ng-|v-)/.test(c)).slice(0, 2);
      return e.tagName.toLowerCase() + (classes.length ? '.' + classes.join('.') : '');
    }
    document.addEventListener('click', (e: MouseEvent) => {
      const target = e.composedPath()[0] as HTMLElement;
      if (!target) return;
      (window as any).__rpa_actions.push({ type: 'click', timestamp: Date.now(), url: location.href, target: genSelector(target), targetText: target.textContent?.trim().substring(0, 80), targetTag: target.tagName?.toLowerCase() });
    }, { capture: true, passive: true });
    document.addEventListener('change', (e: Event) => {
      const target = e.target as HTMLInputElement;
      if (!target || !['INPUT', 'SELECT', 'TEXTAREA'].includes(target.tagName)) return;
      (window as any).__rpa_actions.push({ type: target.tagName === 'SELECT' ? 'select' : 'input', timestamp: Date.now(), url: location.href, target: genSelector(target), targetType: target.type || target.tagName.toLowerCase(), name: target.name, value: target.type === 'password' ? '[REDACTED]' : (target.value || '').substring(0, 500) });
    }, { capture: true, passive: true });
    document.addEventListener('submit', (e: SubmitEvent) => {
      const form = e.target as HTMLFormElement;
      if (!form) return;
      const fields: Record<string, string> = {};
      const fd = new FormData(form);
      fd.forEach((v, k) => { if (!k.toLowerCase().includes('password')) { fields[k] = typeof v === 'string' ? v.substring(0, 200) : '[file]'; } });
      (window as any).__rpa_actions.push({ type: 'submit', timestamp: Date.now(), url: location.href, target: genSelector(form), fields });
    }, { capture: true, passive: true });
  });

  // ── Network capture (context level — all tabs) ─────────────────────────────
  context.on('request', (req: Request) => {
    if (!shouldCapture(req)) return;
    const id = `req_${String(++seqCounter).padStart(4, '0')}`;
    requestIndex.set(req, id);
    const { raw, parsed } = extractPostData(req);
    requests.push({ id, seqNum: seqCounter, timestamp: Date.now(), relativeMs: Date.now() - startTime, method: req.method(), url: req.url(), headers: req.headers(), postData: raw, postDataParsed: parsed, resourceType: req.resourceType() });
  });

  context.on('response', async (res: Response) => {
    const id = requestIndex.get(res.request());
    if (!id) return;
    const contentType = res.headers()['content-type'] || '';
    const isText = /json|text|xml|form|javascript|graphql/.test(contentType);
    let body: string | null = null;
    let bodyParsed: any;
    let truncated = false;
    if (isText) {
      try {
        const raw = await res.text();
        if (raw.length > MAX_BODY_SIZE) { body = raw.substring(0, MAX_BODY_SIZE); truncated = true; } else { body = raw; }
        bodyParsed = tryParseJSON(body);
      } catch {}
    }
    responses[id] = { requestId: id, timestamp: Date.now(), status: res.status(), statusText: res.statusText(), headers: res.headers(), mimeType: contentType, body, bodyParsed, truncated, isRedirect: res.status() >= 300 && res.status() < 400 };
  });

  // ── Navigation tracking (all tabs) ────────────────────────────────────────
  context.on('page', (newPage) => {
    process.stdout.write(`  🆕 New tab: ${newPage.url() || '(loading)'}\n`);
    newPage.on('framenavigated', (frame) => {
      if (frame !== newPage.mainFrame()) return;
      const url = frame.url();
      actions.push({ seqNum: ++seqCounter, timestamp: Date.now(), relativeMs: Date.now() - startTime, type: 'navigate', url, label: `[new-tab] ${url}` });
      process.stdout.write(`  ↗  [tab] ${url.substring(0, 100)}\n`);
    });
  });
  page.on('framenavigated', (frame) => {
    if (frame !== page.mainFrame()) return;
    const url = frame.url();
    actions.push({ seqNum: ++seqCounter, timestamp: Date.now(), relativeMs: Date.now() - startTime, type: 'navigate', url, label: url });
    process.stdout.write(`  ↗  ${url.substring(0, 100)}\n`);
  });

  // ── Open initial URL ───────────────────────────────────────────────────────
  const startUrl = opts.ssoUrl || opts.appUrl;
  if (startUrl) {
    console.log(`🔗 Opening: ${startUrl}\n`);
    await page.goto(startUrl, { waitUntil: 'domcontentloaded', timeout: 30_000 }).catch(() => {});
  }

  // ── Interactive control ────────────────────────────────────────────────────
  console.log('─'.repeat(60));
  console.log('📋  Controls:');
  console.log('    Enter          → Add a marker (annotate what you did)');
  console.log('    s + Enter      → Take a screenshot');
  console.log('    done + Enter   → Stop recording and save');
  console.log('    Ctrl+C         → Emergency stop and save');
  console.log('─'.repeat(60));
  console.log('💡  Now perform your task in the browser.\n');

  const rl = readline.createInterface({ input: process.stdin, terminal: false });

  await new Promise<void>((resolve) => {
    rl.on('line', async (line) => {
      const input = line.trim().toLowerCase();
      if (input === 'done' || input === 'q' || input === 'exit') { console.log('\n⏹  Stopping recording...'); resolve(); return; }
      if (input === 's' || input === 'screenshot') {
        screenshotCount++;
        const ssFile = path.join(ssDir, `screenshot_${screenshotCount}_${Date.now()}.png`);
        await page.screenshot({ path: ssFile, fullPage: false });
        actions.push({ seqNum: ++seqCounter, timestamp: Date.now(), relativeMs: Date.now() - startTime, type: 'screenshot', url: page.url(), screenshotFile: path.basename(ssFile) });
        console.log(`  📸 Screenshot saved: ${path.basename(ssFile)}`);
        return;
      }
      const label = line.trim() || `Marker at ${new Date().toISOString()}`;
      actions.push({ seqNum: ++seqCounter, timestamp: Date.now(), relativeMs: Date.now() - startTime, type: 'marker', url: page.url(), label });
      console.log(`  📌 Marker: "${label}"`);
    });
    rl.on('close', resolve);
    process.on('SIGINT', () => { console.log('\n⚠️  Interrupted - saving recording...'); resolve(); });
  });

  // ── Collect final state ────────────────────────────────────────────────────
  process.stdout.write('\n⏳  Collecting final browser state...\n');
  try {
    const injectedActions: any[] = await page.evaluate(() => (window as any).__rpa_actions || []);
    for (const a of injectedActions) { actions.push({ seqNum: ++seqCounter, timestamp: a.timestamp, relativeMs: a.timestamp - startTime, ...a }); }
  } catch {}
  actions.sort((a, b) => a.timestamp - b.timestamp);
  const finalCookies = await context.cookies();
  let finalLocalStorage: Record<string, string> = {};
  let finalSessionStorage: Record<string, string> = {};
  try {
    finalLocalStorage = await page.evaluate(() => { const d: Record<string, string> = {}; for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i)!; d[k] = localStorage.getItem(k)!; } return d; });
    finalSessionStorage = await page.evaluate(() => { const d: Record<string, string> = {}; for (let i = 0; i < sessionStorage.length; i++) { const k = sessionStorage.key(i)!; d[k] = sessionStorage.getItem(k)!; } return d; });
  } catch {}

  const endTime = Date.now();
  const recording: Recording = { version: '1.0', taskName, startTime, endTime, durationMs: endTime - startTime, ssoUrl: opts.ssoUrl || '', finalUrl: page.url(), requests, responses, actions, finalCookies, finalLocalStorage, finalSessionStorage, notes, screenshotCount };

  // ── Save ───────────────────────────────────────────────────────────────────
  fs.writeFileSync(path.join(outputDir, 'recording.json'), JSON.stringify(recording, null, 2));
  const businessRequests = requests.filter(r => !SKIP_RESOURCE_TYPES.has(r.resourceType) && (r.method !== 'GET' || r.url.includes('/api/') || r.url.includes('/graphql')));
  const summaryLines = [
    `Task       : ${taskName}`, `Recorded   : ${new Date(startTime).toISOString()}`,
    `Duration   : ${Math.round(recording.durationMs / 1000)}s`,
    `Requests   : ${requests.length} total, ${businessRequests.length} business API calls`,
    `Actions    : ${actions.length}`, `Screenshots: ${screenshotCount}`,
    `Final URL  : ${recording.finalUrl}`, `SSO URL    : ${recording.ssoUrl || 'N/A'}`, '',
    'Business API calls:',
    ...businessRequests.slice(0, 30).map(r => { const resp = responses[r.id]; return `  [${resp ? resp.status : '?'}] ${r.method.padEnd(6)} ${r.url}`; }),
    '', 'Cookies captured:',
    ...finalCookies.slice(0, 20).map(c => `  ${c.domain} | ${c.name}=${c.value.substring(0, 30)}`),
  ];
  fs.writeFileSync(path.join(outputDir, 'summary.txt'), summaryLines.join('\n'));

  await context.close();
  await browser.close();

  console.log('\n✅  Recording complete!');
  console.log(`    ${requests.length} requests | ${businessRequests.length} business APIs | ${actions.length} actions`);
  console.log(`    Saved to: ${outputDir}`);
  console.log(`\n📊  Next step:`);
  console.log(`    Tell me to analyze the recording at: ${outputDir}\n`);
}

main().catch(err => { console.error('\n❌ Fatal error:', err.message); process.exit(1); });
