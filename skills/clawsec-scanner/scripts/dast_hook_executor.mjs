#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

function parseArgs(argv) {
  const parsed = {
    handler: "",
    exportName: "default",
    eventB64: "",
    contextB64: "",
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "--handler") {
      parsed.handler = String(argv[i + 1] ?? "").trim();
      i += 1;
      continue;
    }

    if (token === "--export") {
      parsed.exportName = String(argv[i + 1] ?? "default").trim() || "default";
      i += 1;
      continue;
    }

    if (token === "--event") {
      parsed.eventB64 = String(argv[i + 1] ?? "").trim();
      i += 1;
      continue;
    }

    if (token === "--context") {
      parsed.contextB64 = String(argv[i + 1] ?? "").trim();
      i += 1;
      continue;
    }

    throw new Error(`Unknown argument: ${token}`);
  }

  if (!parsed.handler) {
    throw new Error("Missing required --handler");
  }

  if (!parsed.eventB64) {
    throw new Error("Missing required --event");
  }

  if (!parsed.contextB64) {
    throw new Error("Missing required --context");
  }

  return parsed;
}

function decodeBase64Json(value, label) {
  try {
    const decoded = Buffer.from(value, "base64").toString("utf8");
    return JSON.parse(decoded);
  } catch (error) {
    throw new Error(`Failed to decode ${label}: ${error instanceof Error ? error.message : String(error)}`);
  }
}

async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function loadTypeScriptCompiler() {
  if (process.env.CLAWSEC_DAST_DISABLE_TYPESCRIPT === "1") {
    return null;
  }

  try {
    const imported = await import("typescript");
    return imported.default || imported;
  } catch {
    // Ignore and try require path next.
  }

  try {
    const req = createRequire(import.meta.url);
    return req("typescript");
  } catch {
    return null;
  }
}

async function importTypeScriptModule(tsPath) {
  const tsCompiler = await loadTypeScriptCompiler();
  if (!tsCompiler || typeof tsCompiler.transpileModule !== "function") {
    throw new Error(
      `Cannot execute TypeScript hook (${tsPath}): typescript compiler not available. ` +
        "Install 'typescript' or provide a JavaScript handler file.",
    );
  }

  const source = await fs.readFile(tsPath, "utf8");
  const transpiled = tsCompiler.transpileModule(source, {
    compilerOptions: {
      module: tsCompiler.ModuleKind.ESNext,
      target: tsCompiler.ScriptTarget.ES2022,
      moduleResolution: tsCompiler.ModuleResolutionKind.NodeNext,
      esModuleInterop: true,
      sourceMap: false,
      inlineSourceMap: false,
      declaration: false,
    },
    fileName: tsPath,
    reportDiagnostics: false,
  });

  const tempFile = path.join(
    path.dirname(tsPath),
    `.clawsec-dast-${path.basename(tsPath, ".ts")}-${process.pid}-${Date.now()}.mjs`,
  );

  await fs.writeFile(tempFile, transpiled.outputText, "utf8");

  try {
    return await import(`${pathToFileURL(tempFile).href}?ts=${Date.now()}`);
  } finally {
    try {
      await fs.unlink(tempFile);
    } catch {
      // best-effort cleanup
    }
  }
}

async function loadHookModule(handlerPath) {
  const fullPath = path.resolve(handlerPath);
  const exists = await fileExists(fullPath);
  if (!exists) {
    throw new Error(`Hook handler does not exist: ${fullPath}`);
  }

  const ext = path.extname(fullPath).toLowerCase();

  if (ext === ".ts") {
    return importTypeScriptModule(fullPath);
  }

  return import(`${pathToFileURL(fullPath).href}?v=${Date.now()}`);
}

function resolveHandlerExport(mod, exportName) {
  if (exportName && exportName !== "default") {
    if (typeof mod?.[exportName] === "function") {
      return mod[exportName];
    }
    throw new Error(`Hook export '${exportName}' is not a function`);
  }

  if (typeof mod?.default === "function") {
    return mod.default;
  }

  if (typeof mod?.handler === "function") {
    return mod.handler;
  }

  throw new Error("Hook module does not export a handler function");
}

function normalizeTimestamp(event) {
  const timestamp = event?.timestamp;
  if (typeof timestamp === "string" || typeof timestamp === "number") {
    const parsed = new Date(timestamp);
    if (!Number.isNaN(parsed.getTime())) {
      event.timestamp = parsed;
    }
  }
}

function summarizeMessages(messages) {
  if (!Array.isArray(messages)) {
    return {
      count: 0,
      charCount: 0,
    };
  }

  let charCount = 0;

  for (const message of messages) {
    if (typeof message === "string") {
      charCount += message.length;
      continue;
    }

    try {
      charCount += JSON.stringify(message).length;
    } catch {
      charCount += 0;
    }
  }

  return {
    count: messages.length,
    charCount,
  };
}

function coreEventShape(event) {
  return {
    type: event?.type ?? null,
    action: event?.action ?? null,
    sessionKey: event?.sessionKey ?? null,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const event = decodeBase64Json(args.eventB64, "event payload");
  const context = decodeBase64Json(args.contextB64, "context payload");

  normalizeTimestamp(event);

  const startedAt = Date.now();
  const before = coreEventShape(event);

  try {
    const mod = await loadHookModule(args.handler);
    const handler = resolveHandlerExport(mod, args.exportName);

    await handler(event, context);

    const after = coreEventShape(event);
    const messageSummary = summarizeMessages(event?.messages);

    const payload = {
      ok: true,
      duration_ms: Date.now() - startedAt,
      core_before: before,
      core_after: after,
      messages_count: messageSummary.count,
      messages_char_count: messageSummary.charCount,
    };

    process.stdout.write(JSON.stringify(payload));
  } catch (error) {
    const after = coreEventShape(event);
    const messageSummary = summarizeMessages(event?.messages);

    const payload = {
      ok: false,
      duration_ms: Date.now() - startedAt,
      core_before: before,
      core_after: after,
      messages_count: messageSummary.count,
      messages_char_count: messageSummary.charCount,
      error: error instanceof Error ? error.message : String(error),
    };

    process.stdout.write(JSON.stringify(payload));
  }
}

main().catch((error) => {
  process.stderr.write(`${error instanceof Error ? error.stack || error.message : String(error)}\n`);
  process.exit(1);
});
