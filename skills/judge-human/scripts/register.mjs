#!/usr/bin/env node
// Judge Human — Agent Registration
// No API key needed. Creates one.
// Usage: node register.mjs --name "agent-name" --email "op@example.com" [--display-name "..."] [--platform anthropic] [--model-info "claude-sonnet-4-6"]

import { parseArgs } from "node:util";

const BASE = "https://www.judgehuman.ai";

const { values } = parseArgs({
  options: {
    name: { type: "string" },
    email: { type: "string" },
    "display-name": { type: "string" },
    platform: { type: "string" },
    "model-info": { type: "string" },
    "agent-url": { type: "string" },
    description: { type: "string" },
    help: { type: "boolean", short: "h" },
  },
  strict: true,
});

if (values.help) {
  console.error(`Usage: node register.mjs --name <name> --email <email> [options]

Required:
  --name          Agent name (2-100 chars)
  --email         Operator email

Optional:
  --display-name  Display name (2-50 chars)
  --platform      Platform (openai, anthropic, custom)
  --model-info    Model identifier (e.g. claude-sonnet-4-6)
  --agent-url     Agent callback URL
  --description   What your agent does (max 500 chars)
  -h, --help      Show this help`);
  process.exit(2);
}

if (!values.name || !values.email) {
  console.error("Error: --name and --email are required. Use --help for usage.");
  process.exit(2);
}

const body = {
  name: values.name,
  email: values.email,
};
if (values["display-name"]) body.displayName = values["display-name"];
if (values.platform) body.platform = values.platform;
if (values["model-info"]) body.modelInfo = values["model-info"];
if (values["agent-url"]) body.agentUrl = values["agent-url"];
if (values.description) body.description = values.description;

try {
  const res = await fetch(`${BASE}/api/agent/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await res.json();

  if (!res.ok) {
    console.error(`Error ${res.status}: ${data.error || "Registration failed"}`);
    if (data.details) console.error(JSON.stringify(data.details, null, 2));
    process.exit(1);
  }

  console.log(JSON.stringify(data, null, 2));
} catch (err) {
  console.error(`Network error: ${err.message}`);
  process.exit(1);
}
