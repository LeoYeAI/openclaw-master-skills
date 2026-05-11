/**
 * skill-ui-bridge OpenClaw Plugin v4.0
 *
 * 方案：监听 gateway_start hook，在 gateway 启动后把 manifest + bootstrap.js
 * 内联写入 control-ui 的 index.html。同时在 gateway_stop 时还原原始文件。
 *
 * 原因：control-ui 静态文件服务优先级高于插件 HTTP handler，
 * 无法在运行时拦截 GET /，因此在启动时直接修改静态文件是唯一的插件方案。
 */

import path from "node:path";
import fs from "node:fs";
import { createRequire } from "node:module";

const PLUGIN_ID = "skill-ui-bridge";
const MANIFEST_PATH = "/plugins/skill-ui/manifest";
const INLINE_MARKER = "/* skill-ui-bridge:inline */";

// ─── Plugin definition ────────────────────────────────────────────────────────

const plugin = {
  id: PLUGIN_ID,
  name: "Skill UI Bridge",
  description: "Injects skill-ui HTML renderer into control-ui at gateway startup",

  register(api) {
    const bootstrapSrc = resolveBootstrapSrc();
    const skillsDir = resolveSkillsDir(api);

    if (!bootstrapSrc) {
      api.logger.warn(`${PLUGIN_ID}: cannot find skill-ui-bridge.js source, aborting`);
      return;
    }

    // gateway_start: 注入 index.html
    api.on("gateway_start", async () => {
      try {
        await injectIndexHtml({ bootstrapSrc, skillsDir, logger: api.logger });
      } catch (err) {
        api.logger.warn(`${PLUGIN_ID}: inject failed: ${err?.message}`);
      }
    });

    // gateway_stop: 还原 index.html
    api.on("gateway_stop", async () => {
      try {
        restoreIndexHtml(api.logger);
      } catch (err) {
        api.logger.warn(`${PLUGIN_ID}: restore failed: ${err?.message}`);
      }
    });

    // 同时注册 manifest HTTP 路由（需要鉴权，供调试用）
    const handler = createManifestHandler({ skillsDir, logger: api.logger });
    if (typeof api.registerHttpRoute === 'function') {
      api.registerHttpRoute({ path: '/plugins/skill-ui/manifest', handler });
    } else if (typeof api.registerHttpHandler === 'function') {
      api.registerHttpHandler(handler);
    }

    api.logger.info(`${PLUGIN_ID}: registered (gateway_start hook will inject index.html)`);
  },
};

export default plugin;

// ─── 注入 / 还原 ──────────────────────────────────────────────────────────────

const STATIC_JS_NAME = "skill-ui-init.js";

async function injectIndexHtml({ bootstrapSrc, skillsDir, logger }) {
  const indexPath = resolveIndexHtmlPath();
  if (!indexPath) {
    logger.warn(`${PLUGIN_ID}: cannot find control-ui index.html`);
    return;
  }

  const staticDir = path.dirname(indexPath);
  const staticJsPath = path.join(staticDir, STATIC_JS_NAME);

  // 1. 把 manifest + bootstrap 合并写成同源静态 JS（CSP script-src 'self' 允许同源文件）
  const manifest = buildManifest(skillsDir, logger);
  const bootstrapJs = fs.readFileSync(bootstrapSrc, "utf-8");
  const bootstrapPatched = patchBootstrap(bootstrapJs);

  const initJs = [
    `// skill-ui-bridge auto-generated`,
    `window.__skillUiManifest = ${JSON.stringify(manifest)};`,
    ``,
    bootstrapPatched,
  ].join("\n");

  fs.writeFileSync(staticJsPath, initJs, "utf-8");
  logger.info(`${PLUGIN_ID}: wrote ${staticJsPath} (${initJs.length} chars)`);

  // 2. index.html 用 <script src> 加载同源文件（CSP 允许）
  let html = fs.readFileSync(indexPath, "utf-8");
  html = cleanInjection(html);

  const scriptTag = `<script src="./${STATIC_JS_NAME}"></script>`;
  html = html.replace("</head>", `${scriptTag}\n</head>`);

  const backupPath = indexPath + ".orig";
  if (!fs.existsSync(backupPath)) {
    fs.writeFileSync(backupPath, fs.readFileSync(indexPath, "utf-8"), "utf-8");
  }

  fs.writeFileSync(indexPath, html, "utf-8");
  logger.info(`${PLUGIN_ID}: injected index.html with <script src="./${STATIC_JS_NAME}">`);
}

function restoreIndexHtml(logger) {
  const indexPath = resolveIndexHtmlPath();
  if (!indexPath) return;
  const backupPath = indexPath + ".orig";
  if (fs.existsSync(backupPath)) {
    fs.copyFileSync(backupPath, indexPath);
    logger.info(`${PLUGIN_ID}: restored original index.html`);
  }
  const staticJsPath = path.join(path.dirname(indexPath), STATIC_JS_NAME);
  if (fs.existsSync(staticJsPath)) {
    fs.unlinkSync(staticJsPath);
    logger.info(`${PLUGIN_ID}: removed ${STATIC_JS_NAME}`);
  }
}

function cleanInjection(html) {
  html = html.replace(/<script>\nwindow\.__skillUiManifest[\s\S]*?<\/script>\n?/g, "");
  html = html.replace(/<script>\/\* skill-ui-bridge:inline \*\/[\s\S]*?<\/script>\n?/g, "");
  html = html.replace(/<script src="\/plugins\/skill-ui\/bootstrap\.js"><\/script>\n?/g, "");
  html = html.replace(/<script src="\.\/skill-ui-init\.js"><\/script>\n?/g, "");
  return html;
}

function patchBootstrap(js) {
  // skill-ui-bridge.js v2+ 已经原生支持 window.__skillUiManifest，无需 patch
  // 保留此函数以兼容旧版本：检查是否已包含 __skillUiManifest 分支
  if (js.includes('window.__skillUiManifest')) return js;

  // 旧版本 patch：在 boot() 开头优先读 window.__skillUiManifest
  const original = `async function boot() {
    try {
      var authHeader = getAuthHeader();
      var fetchOpts = authHeader ? { headers: { 'Authorization': authHeader } } : {};
      var r = await fetch('/plugins/skill-ui/manifest', fetchOpts);
      if (!r.ok) { console.warn('[skill-ui-bridge] manifest', r.status); return; }
      var m = await r.json();`;

  const patched = `async function boot() {
    try {
      var m;
      if (window.__skillUiManifest) {
        m = window.__skillUiManifest;
      } else {
        var authHeader = getAuthHeader();
        var fetchOpts = authHeader ? { headers: { 'Authorization': authHeader } } : {};
        var r = await fetch('/plugins/skill-ui/manifest', fetchOpts);
        if (!r.ok) { console.warn('[skill-ui-bridge] manifest', r.status); return; }
        m = await r.json();
      }`;

  if (js.includes(original)) return js.replace(original, patched);
  return js;
}

// ─── Manifest builder ─────────────────────────────────────────────────────────

function buildManifest(skillsDir, logger) {
  const manifest = { skills: [], timestamp: Date.now() };
  if (!skillsDir || !fs.existsSync(skillsDir)) return manifest;
  try {
    const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (entry.name.startsWith(".") || entry.name.includes("..")) continue;
      const configPath = path.join(skillsDir, entry.name, "ui-config.json");
      if (!fs.existsSync(configPath)) continue;
      try {
        const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
        manifest.skills.push({ name: entry.name, config });
      } catch (err) {
        logger?.warn(`${PLUGIN_ID}: bad ui-config.json in '${entry.name}': ${err?.message}`);
      }
    }
  } catch (err) {
    logger?.warn(`${PLUGIN_ID}: cannot read skillsDir: ${err?.message}`);
  }
  return manifest;
}

// ─── Manifest HTTP handler（调试用）──────────────────────────────────────────

function createManifestHandler({ skillsDir, logger }) {
  return async (req, res) => {
    const pathname = new URL(req.url ?? "/", "http://localhost").pathname;
    if (pathname !== MANIFEST_PATH) return false;
    if (req.method === "OPTIONS") {
      res.writeHead(204, CORS_HEADERS);
      res.end();
      return true;
    }
    const manifest = buildManifest(skillsDir, logger);
    const body = JSON.stringify(manifest);
    res.writeHead(200, {
      "Content-Type": "application/json; charset=utf-8",
      "Content-Length": Buffer.byteLength(body),
      ...CORS_HEADERS,
    });
    res.end(body);
    return true;
  };
}

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

// ─── 路径解析 ─────────────────────────────────────────────────────────────────

function resolveBootstrapSrc() {
  try {
    const selfUrl = new URL(import.meta.url);
    const candidate = path.join(path.dirname(selfUrl.pathname), "skill-ui-bridge.js");
    if (fs.existsSync(candidate)) return candidate;
  } catch (_) {}
  return null;
}

function resolveSkillsDir(api) {
  try {
    const workspaceDir =
      api.config?.agents?.defaults?.workspace ?? api.config?.workspace ?? null;
    if (workspaceDir) return path.join(workspaceDir, "skills");
  } catch (_) {}
  return null;
}

function resolveIndexHtmlPath() {
  const candidates = [
    "/usr/local/lib/node_modules/openclaw/dist/control-ui/index.html",
    "/usr/local/lib/.nvm/versions/node/v22.17.0/lib/node_modules/openclaw/dist/control-ui/index.html",
  ];
  try {
    const req = createRequire(import.meta.url);
    const pkgMain = req.resolve("openclaw");
    const pkgDir = path.dirname(pkgMain);
    candidates.unshift(path.join(pkgDir, "control-ui", "index.html"));
    candidates.unshift(path.join(path.dirname(pkgDir), "control-ui", "index.html"));
  } catch (_) {}
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
}
