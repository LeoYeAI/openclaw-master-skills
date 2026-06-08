#!/usr/bin/env npx tsx
/**
 * diagram-to-image: Convert Excalidraw / DrawIO content to PNG.
 *
 * Prerequisites:
 *   System Chrome/Chromium installed, OR: npx playwright install chromium
 *
 * Usage:
 *   npx tsx scripts/diagram-to-image.ts excalidraw input.json output.png
 *   npx tsx scripts/diagram-to-image.ts drawio    input.xml  output.png
 *   cat input.json | npx tsx scripts/diagram-to-image.ts excalidraw - output.png
 *
 * Options:
 *   --scale <n>        PNG scale factor (default: 2)
 *   --background <hex> Background color (default: #ffffff)
 *   --padding <n>      Export padding in px (default: 20)
 *
 * Programmatic:
 *   import { renderDiagram } from './scripts/diagram-to-image';
 *   const buf = await renderDiagram({ type: 'excalidraw', content: '...' });
 */

import * as fs from 'fs/promises';
import * as path from 'path';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type DiagramType = 'excalidraw' | 'drawio';

export interface RenderOptions {
  type: DiagramType;
  /** Raw content: JSON string (excalidraw) or XML (drawio) */
  content: string;
  /** PNG scale factor (default 2) */
  scale?: number;
  /** Background color (default #ffffff) */
  background?: string;
  /** Export padding in px (default 20) */
  padding?: number;
}

export interface RenderResult {
  /** Output buffer (PNG binary) */
  data: Buffer;
}

// ---------------------------------------------------------------------------
// Lazy Playwright import
// ---------------------------------------------------------------------------

async function getPlaywright() {
  const projectRoot = __dirname;
  const candidates = [
    'playwright',
    'playwright-core',
    ...findPnpmPackage(projectRoot, 'playwright'),
    ...findPnpmPackage(projectRoot, 'playwright-core'),
  ];
  for (const id of candidates) {
    try {
      const mod = await import(id);
      const pw = mod.default ?? mod;
      if (pw.chromium) return pw;
    } catch { /* try next */ }
  }
  throw new Error(
    'Playwright not found. Install it:\n  npm i -D playwright\n  npx playwright install chromium',
  );
}

async function launchBrowser(pw: any) {
  const systemChromePaths = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
  ];

  for (const execPath of systemChromePaths) {
    try {
      require('fs').accessSync(execPath);
      return await pw.chromium.launch({
        executablePath: execPath,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
      });
    } catch { /* try next */ }
  }

  return await pw.chromium.launch();
}

function findPnpmPackage(projectRoot: string, name: string): string[] {
  const pnpmDir = path.join(projectRoot, 'node_modules/.pnpm');
  try {
    const entries = require('fs').readdirSync(pnpmDir);
    return entries
      .filter((e: string) => e.startsWith(`${name}@`))
      .map((e: string) => path.join(pnpmDir, e, 'node_modules', name));
  } catch {
    return [];
  }
}

// ---------------------------------------------------------------------------
// Input Validation
// ---------------------------------------------------------------------------

function validateHexColor(color: string): string {
  // Only allow valid hex colors (3, 4, 6, or 8 hex digits with # prefix)
  if (/^#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/.test(color)) {
    return color;
  }
  console.warn(`Invalid background color "${color}", falling back to #ffffff`);
  return '#ffffff';
}

function validateScale(scale: number): number {
  const n = Math.round(scale);
  if (n >= 1 && n <= 10) return n;
  console.warn(`Invalid scale ${scale}, falling back to 2`);
  return 2;
}

function validatePadding(padding: number): number {
  const n = Math.round(padding);
  if (n >= 0 && n <= 200) return n;
  console.warn(`Invalid padding ${padding}, falling back to 20`);
  return 20;
}

// ---------------------------------------------------------------------------
// HTML Templates
//
// All browser-side logic lives INSIDE the HTML templates as plain JS strings.
// This avoids tsx/esbuild injecting Node-specific helpers (__name etc.)
// into code that will run in the browser via page.evaluate().
// ---------------------------------------------------------------------------

function excalidrawHtml(background: string): string {
  return `<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,400;0,600;0,700;1,400&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Lilita+One&display=swap');
  body { margin: 0; background: ${background}; }
</style>
</head>
<body>
<script type="module">
try {
  const mod = await import('https://esm.sh/@excalidraw/excalidraw@0.18.0?bundle-deps&no-dts');

  await Promise.all([
    document.fonts.load('16px Nunito'),
    document.fonts.load('20px "Lilita One"'),
    document.fonts.ready,
  ]);

  window.__excalib = {
    exportToBlob: mod.exportToBlob,
    convert: mod.convertToExcalidrawElements,
  };

  // ---- Bridge function called from Node via page.evaluate('window.__xxx(...)') ----

  window.__exportPng = async function(raw, bg, padding, scale) {
    var lib = window.__excalib;
    var elements = JSON.parse(raw);
    if (!Array.isArray(elements) && Array.isArray(elements && elements.elements)) {
      elements = elements.elements;
    }
    if (
      elements.length > 0
      && elements[0].version === undefined
      && elements[0].versionNonce === undefined
      && lib.convert
    ) {
      elements = lib.convert(elements);
    }
    var blob = await lib.exportToBlob({
      elements: elements,
      appState: { viewBackgroundColor: bg, exportBackground: true },
      files: {},
      exportPadding: padding,
      mimeType: 'image/png',
      quality: 1,
      getDimensions: function(w, h) {
        return { width: w * scale, height: h * scale, scale: scale };
      },
    });
    var buf = await blob.arrayBuffer();
    var bytes = new Uint8Array(buf);
    var binary = '';
    for (var i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  };

  window.__ready = true;
} catch (e) {
  window.__error = (e && e.message) || String(e);
  window.__ready = true;
}
</script>
</body></html>`;
}

function drawioHtml(xml: string, background: string): string {
  // Embed XML into a .mxgraph div BEFORE viewer-static.min.js loads.
  // The viewer auto-processes .mxgraph elements on load via GraphViewer.
  const config = JSON.stringify({
    xml,
    highlight: '#0000ff',
    nav: false,
    resize: true,
    toolbar: '',
    border: 20,
  });
  // Escape for safe HTML attribute embedding
  const escapedConfig = config
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  return `<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
  body { margin: 0; background: ${background}; }
  .geDiagramContainer { overflow: visible !important; }
</style>
</head>
<body>
<div id="graph-container" class="mxgraph" data-mxgraph="${escapedConfig}"></div>
<script src="https://viewer.diagrams.net/js/viewer-static.min.js"><\/script>
<script>
  // viewer-static.min.js auto-renders .mxgraph divs on load.
  // Poll until the SVG appears in the container.
  function waitForSvg() {
    var container = document.getElementById('graph-container');
    // The viewer wraps content in .geDiagramContainer > svg
    var svg = container.querySelector('svg');
    if (svg && svg.getBBox) {
      try {
        var bbox = svg.getBBox();
        if (bbox.width > 0 && bbox.height > 0) {
          window.__ready = true;
          return;
        }
      } catch(_e) {}
    }
    setTimeout(waitForSvg, 200);
  }
  // Give the viewer time to initialize (it processes on DOMContentLoaded)
  setTimeout(waitForSvg, 500);

  // Timeout after 30s
  setTimeout(function() {
    if (!window.__ready) {
      window.__error = 'DrawIO viewer rendering timed out';
      window.__ready = true;
    }
  }, 30000);
</script>
</body></html>`;
}

// ---------------------------------------------------------------------------
// Renderers — all browser logic is called via string-based page.evaluate()
// to avoid tsx __name injection issues
// ---------------------------------------------------------------------------

async function waitForReady(page: any, timeoutMs = 120_000) {
  await page.waitForFunction('window.__ready === true', { timeout: timeoutMs });
  const error = await page.evaluate('window.__error');
  if (error) {
    throw new Error(`Library loading failed: ${error}`);
  }
}

async function renderExcalidraw(
  page: any,
  content: string,
  opts: Required<Pick<RenderOptions, 'scale' | 'background' | 'padding'>>,
): Promise<Buffer> {
  await page.setContent(excalidrawHtml(opts.background), { waitUntil: 'domcontentloaded' });
  await waitForReady(page);

  // Pass data via exposeFunction to avoid string escaping issues with large JSON
  await page.evaluate(`window.__inputData = ${JSON.stringify(content)}`);

  const base64: string = await page.evaluate(
    `window.__exportPng(window.__inputData, ${JSON.stringify(opts.background)}, ${opts.padding}, ${opts.scale})`,
  );
  return Buffer.from(base64, 'base64');
}

async function renderDrawio(
  page: any,
  content: string,
  opts: Required<Pick<RenderOptions, 'scale' | 'background'>>,
): Promise<Buffer> {
  // XML is embedded directly in the HTML template; viewer auto-renders on load
  await page.setContent(drawioHtml(content, opts.background), { waitUntil: 'domcontentloaded' });
  await waitForReady(page);

  // PNG: screenshot the rendered SVG element (pixel-perfect, correct fonts)
  const svgElement = await page.$('#graph-container svg');
  if (!svgElement) {
    throw new Error('DrawIO rendering failed: no SVG element found');
  }
  const screenshot = await svgElement.screenshot({ type: 'png' });
  return screenshot;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function renderDiagram(opts: RenderOptions): Promise<RenderResult> {
  const pw = await getPlaywright();
  const browser = await launchBrowser(pw);
  const scale = validateScale(opts.scale ?? 2);
  const background = validateHexColor(opts.background ?? '#ffffff');
  const padding = validatePadding(opts.padding ?? 20);

  try {
    const page = await browser.newPage();

    let data: Buffer;
    switch (opts.type) {
      case 'excalidraw':
        data = await renderExcalidraw(page, opts.content, { scale, background, padding });
        break;
      case 'drawio':
        data = await renderDrawio(page, opts.content, { scale, background });
        break;
      default:
        throw new Error(`Unknown diagram type: ${opts.type}`);
    }

    return { data };
  } finally {
    await browser.close();
  }
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function printUsage() {
  console.log(`
Usage:
  npx tsx scripts/diagram-to-image.ts <type> <input> <output> [options]

Arguments:
  type    Diagram type: excalidraw | drawio
  input   Input file path (use "-" for stdin)
  output  Output file path (.png)

Options:
  --scale <n>        PNG scale factor (default: 2)
  --background <hex> Background color (default: #ffffff)
  --padding <n>      Export padding in px (default: 20)

Examples:
  npx tsx scripts/diagram-to-image.ts excalidraw diagram.json out.png
  npx tsx scripts/diagram-to-image.ts drawio diagram.xml out.png
`);
}

async function readStdin(): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf-8');
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }

  const positional: string[] = [];
  const flags: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--') && i + 1 < args.length) {
      flags[args[i].slice(2)] = args[++i];
    } else {
      positional.push(args[i]);
    }
  }

  if (positional.length < 3) {
    console.error('Error: Expected 3 positional arguments: <type> <input> <output>');
    printUsage();
    process.exit(1);
  }

  const [typeStr, inputPath, outputPath] = positional;
  const type = typeStr as DiagramType;

  if (!['excalidraw', 'drawio'].includes(type)) {
    console.error(`Error: Unknown diagram type "${type}". Use excalidraw or drawio.`);
    process.exit(1);
  }

  let content: string;
  if (inputPath === '-') {
    content = await readStdin();
  } else {
    content = await fs.readFile(inputPath, 'utf-8');
  }

  if (!content.trim()) {
    console.error('Error: Input content is empty.');
    process.exit(1);
  }

  const scale = validateScale(flags.scale ? Number(flags.scale) : 2);
  const background = validateHexColor(flags.background ?? '#ffffff');
  const padding = validatePadding(flags.padding ? Number(flags.padding) : 20);

  console.log(`Rendering ${type} diagram → PNG (scale=${scale})...`);

  try {
    const result = await renderDiagram({
      type,
      content,
      scale,
      background,
      padding,
    });

    await fs.writeFile(outputPath, result.data);
    console.log(`Done: ${outputPath} (${(result.data.length / 1024).toFixed(1)} KB)`);
  } catch (err: any) {
    console.error(`Error: ${err?.message || err}`);
    process.exit(1);
  }
}

const isDirectRun = process.argv[1] && (
  process.argv[1].endsWith('diagram-to-image.ts')
  || process.argv[1].endsWith('diagram-to-image.js')
);

if (isDirectRun) {
  main();
}
