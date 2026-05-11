#!/usr/bin/env node
/**
 * Minimal UI server with path whitelist.
 * Serves only demo_ui.html and whitelisted data files from ../openwechat_im_client.
 * Binds to 127.0.0.1 only. Does NOT expose parent directory or other skills.
 */
const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 8765;
const HOST = "127.0.0.1";

const SCRIPTS_DIR = path.resolve(__dirname);
const SKILL_ROOT = path.join(SCRIPTS_DIR, "..");
const DATA_DIR = path.join(SKILL_ROOT, "..", "openwechat_im_client");

// config.json excluded: contains token; user-visible data only
const DATA_WHITELIST = new Set([
  "profile.json",
  "contacts.json",
  "stats.json",
  "context_snapshot.json",
  "inbox_pushed.md",
  "conversations.md",
  "sse_channel.log",
]);

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".log": "text/plain; charset=utf-8",
};

function serve(req, res) {
  const url = new URL(req.url || "/", `http://${HOST}`);
  let p = decodeURIComponent(url.pathname);

  if (p === "/" || p === "") p = "/demo_ui.html";
  if (p === "/demo_ui.html") p = "/demo_ui.html";

  if (p === "/demo_ui.html") {
    const filePath = path.join(SCRIPTS_DIR, "demo_ui.html");
    if (!filePath.startsWith(SCRIPTS_DIR) || !fs.existsSync(filePath)) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
    res.end(fs.readFileSync(filePath));
    return;
  }

  if (p.startsWith("/openwechat_im_client/")) {
    const name = path.basename(p);
    if (!DATA_WHITELIST.has(name)) {
      res.writeHead(403);
      res.end("Forbidden");
      return;
    }
    const filePath = path.join(DATA_DIR, name);
    const resolved = path.resolve(filePath);
    const dataDirResolved = path.resolve(DATA_DIR);
    const rel = path.relative(dataDirResolved, resolved);
    if (rel.startsWith("..") || path.isAbsolute(rel)) {
      res.writeHead(403);
      res.end("Forbidden");
      return;
    }
    if (!fs.existsSync(filePath)) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    const ext = path.extname(filePath);
    res.writeHead(200, { "Content-Type": MIME[ext] || "application/octet-stream" });
    res.end(fs.readFileSync(filePath));
    return;
  }

  res.writeHead(404);
  res.end("Not found");
}

const server = http.createServer(serve);
server.listen(PORT, HOST, () => {
  console.log(`Demo UI: http://${HOST}:${PORT}/demo_ui.html`);
});
