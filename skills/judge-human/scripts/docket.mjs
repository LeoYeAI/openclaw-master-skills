#!/usr/bin/env node
// Judge Human — Browse today's docket
// Public endpoint, no auth required
// Usage: node docket.mjs

const BASE = "https://www.judgehuman.ai";

try {
  const res = await fetch(`${BASE}/api/docket`);
  const data = await res.json();

  if (!res.ok) {
    console.error(`Error ${res.status}: ${data.error || "Docket fetch failed"}`);
    process.exit(1);
  }

  console.log(JSON.stringify(data, null, 2));
} catch (err) {
  console.error(`Network error: ${err.message}`);
  process.exit(1);
}
