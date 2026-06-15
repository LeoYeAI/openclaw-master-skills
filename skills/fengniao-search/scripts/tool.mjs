#!/usr/bin/env node
// tool.mjs - CLI entrypoint for fengniao-search skill
import { discover, call } from "./client.mjs";

const [, , command, ...args] = process.argv;

function printHelp() {
  console.log(`
Fengniao Search Tool CLI

Commands:
  discover <query> [--limit N]
      Find tools matching a natural-language query.
      Returns tool candidates and similarity scores.

  call <tool_id> [--params '{"key":"value"}'] [--params "key=value&key2=value2"]
      Call a tool by its ID with optional params.
      --params '{"key":"value"}' accepts JSON or key=value pairs joined by , or &
      --params "key=value&key2=value2" can be repeated and is recommended on Windows.

Options:
  --help    Show this help message

Examples:
  node tool.mjs discover "企业股东信息" --limit 3
  node tool.mjs call biz_fuzzy_search --params '{"key":"腾讯"}'
  node tool.mjs call biz_shareholders --params "entid=AerjZTfkSh0"
`);
}

function isPlainObject(value) {
  return value != null && typeof value === "object" && !Array.isArray(value);
}

function parseScalar(value) {
  const raw = value.trim();
  if (raw === "true") return true;
  if (raw === "false") return false;
  if (raw === "null") return null;
  if (/^-?(?:0|[1-9]\d*)(?:\.\d+)?$/.test(raw)) return Number(raw);

  if (
    (raw.startsWith("{") && raw.endsWith("}")) ||
    (raw.startsWith("[") && raw.endsWith("]")) ||
    (raw.startsWith('"') && raw.endsWith('"'))
  ) {
    try {
      return JSON.parse(raw);
    } catch {
      // Keep the raw string when partial JSON is provided.
    }
  }

  return raw;
}

function parseKeyValueParams(raw) {
  const entries = raw
    .split(/[&,]/)
    .map((entry) => entry.trim())
    .filter(Boolean);

  if (entries.length === 0) {
    throw new Error("empty params");
  }

  const params = {};
  for (const entry of entries) {
    const eqIndex = entry.indexOf("=");
    if (eqIndex <= 0) {
      throw new Error(`invalid param entry: ${entry}`);
    }
    const key = entry.slice(0, eqIndex).trim();
    const value = entry.slice(eqIndex + 1);
    params[key] = parseScalar(value);
  }

  return params;
}

function parseParams(raw) {
  try {
    const parsed = JSON.parse(raw);
    if (!isPlainObject(parsed)) {
      throw new Error("params JSON must be an object");
    }
    return parsed;
  } catch {
    try {
      return parseKeyValueParams(raw);
    } catch {
      throw new Error(
        '--params must be valid JSON or key=value&key2=value2 pairs such as entid=AerjZTfkSh0'
      );
    }
  }
}

function parseFlags(args) {
  const flags = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--limit" && args[i + 1]) {
      flags.limit = parseInt(args[++i], 10);
    } else if (args[i] === "--params" && args[i + 1]) {
      try {
        flags.params = {
          ...(flags.params || {}),
          ...parseParams(args[++i]),
        };
      } catch (err) {
        console.error(`Error: ${err.message}`);
        process.exit(1);
      }
    } else if (args[i] === "--param" && args[i + 1]) {
      try {
        flags.params = {
          ...(flags.params || {}),
          ...parseKeyValueParams(args[++i]),
        };
      } catch {
        console.error(
          `Error: --param must use key=value format, received: ${args[i]}`
        );
        process.exit(1);
      }
    }
  }
  return flags;
}

async function main() {
  if (!command || command === "--help") {
    printHelp();
    process.exit(0);
  }

  try {
    if (command === "discover") {
      const query = args[0];
      if (!query) {
        console.error("Error: discover requires a query string");
        process.exit(1);
      }
      const flags = parseFlags(args.slice(1));
      const result = await discover(query, flags);
      console.log(JSON.stringify(result, null, 2));

    } else if (command === "call") {
      const toolId = args[0];
      if (!toolId) {
        console.error("Error: call requires a tool_id");
        process.exit(1);
      }
      const flags = parseFlags(args.slice(1));
      const result = await call(toolId, flags.params || {});
      console.log(JSON.stringify(result, null, 2));

    } else {
      console.error(`Unknown command: ${command}`);
      printHelp();
      process.exit(1);
    }
  } catch (err) {
    console.error("Error:", err.message);
    process.exit(1);
  }
}

main();
