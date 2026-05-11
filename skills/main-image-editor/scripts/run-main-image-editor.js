#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { parseIntentRequest } from "../lib/intent-parser.js";
import { executeTransactionalBatch } from "../lib/task-orchestrator.js";

function parseArgs(argv) {
  const args = {
    request: "",
    dryRun: false,
    force: false,
    index: "",
    threshold: undefined,
    help: false,
  };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--request") {
      args.request = argv[i + 1] || "";
      i += 1;
    } else if (arg === "--dry-run") {
      args.dryRun = true;
    } else if (arg === "--force") {
      args.force = true;
    } else if (arg === "--index") {
      args.index = argv[i + 1] || "";
      i += 1;
    } else if (arg === "--threshold") {
      args.threshold = Number(argv[i + 1]);
      i += 1;
    } else if (arg === "--help" || arg === "-h") {
      args.help = true;
    }
  }
  return args;
}

function readRequest(filePath) {
  const resolved = path.resolve(filePath);
  const raw = fs.readFileSync(resolved, "utf8");
  return JSON.parse(raw);
}

function printResultAndExit(payload, code) {
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exit(code);
}

function normalizeRequest(base, args) {
  const request = { ...(base || {}) };
  const exec = request.execution || {};
  request.execution = {
    ...exec,
    dryRun: Boolean(args.dryRun || exec.dryRun),
    force: Boolean(args.force || exec.force),
    indexPath: args.index || exec.indexPath,
    rollbackPolicy: "rollback_all",
  };
  if (Number.isFinite(args.threshold)) {
    request.confidenceThreshold = Number(args.threshold);
  }
  return request;
}

function resolveExports(request) {
  const requestText = String(request?.text || "");
  const skipExport = /(不导出|仅修改|只改文案|不需要导图)/.test(requestText);
  const toDesktop = /(桌面)/.test(String(request?.text || ""));
  if (skipExport) return [];
  return [
    {
      format: "png",
      mode: "layer_sets",
      dir: toDesktop ? "~/Desktop" : undefined,
      folderName: `main-image-${Date.now()}`,
    },
  ];
}

function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.request) {
    process.stdout.write(
      "Usage: run-main-image-editor.js --request <request.json> [--dry-run] [--force] [--index <index>] [--threshold <0-1>]\n",
    );
    process.exit(args.help ? 0 : 1);
  }

  let request;
  try {
    request = normalizeRequest(readRequest(args.request), args);
  } catch (error) {
    printResultAndExit(
      {
        status: "error",
        code: "E_TASK_INVALID",
        message: `Cannot read request: ${error.message}`,
      },
      1,
    );
  }

  const parsed = parseIntentRequest(request);
  if (!parsed.ok) {
    printResultAndExit(
      {
        requestId: request.requestId || `main-image-request-${Date.now()}`,
        status: "error",
        code: parsed.code,
        message: parsed.message,
      },
      1,
    );
  }

  const threshold = Number.isFinite(Number(request.confidenceThreshold))
    ? Number(request.confidenceThreshold)
    : 0.8;
  const execution = request.execution || {};
  const exports = resolveExports(request);
  const result = executeTransactionalBatch({
    previewTasks: parsed.tasks,
    threshold,
    force: Boolean(execution.force),
    dryRun: Boolean(execution.dryRun),
    indexPath: execution.indexPath,
    screenshotPath: request.screenshotPath,
    bundleZip: execution.bundleZip !== false,
    bundle: {
      zipName: `main-image-${Date.now()}.zip`,
    },
    exports,
    keepBackups: false,
  });

  const payload = {
    requestId: request.requestId || `main-image-request-${Date.now()}`,
    ...result.result,
  };
  printResultAndExit(payload, payload.status === "error" ? 1 : 0);
}

main();
