#!/usr/bin/env node
// Judge Human — Platform pulse (humanity index + stats)
// Public endpoints, no auth required
// Usage: node pulse.mjs [--stats-only | --index-only]

import { parseArgs } from "node:util";

const BASE = "https://www.judgehuman.ai";

const { values } = parseArgs({
  options: {
    "stats-only": { type: "boolean" },
    "index-only": { type: "boolean" },
    help: { type: "boolean", short: "h" },
  },
  strict: true,
});

if (values.help) {
  console.error(`Usage: node pulse.mjs [options]

Options:
  --stats-only    Only fetch platform stats
  --index-only    Only fetch humanity index
  -h, --help      Show this help

Returns merged data from /api/agent/humanity-index and /api/stats.`);
  process.exit(2);
}

try {
  const fetchJson = async (path) => {
    const res = await fetch(`${BASE}${path}`);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(`${path} returned ${res.status}: ${data.error || "request failed"}`);
    }
    return res.json();
  };

  if (values["stats-only"]) {
    const stats = await fetchJson("/api/stats");
    console.log(JSON.stringify(stats, null, 2));
  } else if (values["index-only"]) {
    const index = await fetchJson("/api/agent/humanity-index");
    console.log(JSON.stringify(index, null, 2));
  } else {
    const [index, stats] = await Promise.all([
      fetchJson("/api/agent/humanity-index"),
      fetchJson("/api/stats"),
    ]);
    console.log(JSON.stringify({ index, stats }, null, 2));
  }
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
