#!/usr/bin/env node

const args = process.argv.slice(2);

// Parse args
const queries = [];
let jsonOutput = false;

for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (arg === "--json") {
    jsonOutput = true;
  } else if (!arg.startsWith("-")) {
    queries.push(arg);
  }
}

if (queries.length === 0) {
  console.error("Usage: search.mjs <query> [query2] [query3...] [--json]");
  console.error("Example: search.mjs 'What is Perplexity?' 'Latest AI news'");
  process.exit(1);
}

const apiKey = process.env.PERPLEXITY_API_KEY;
if (!apiKey) {
  console.error("Error: PERPLEXITY_API_KEY environment variable not set");
  process.exit(1);
}

async function search(queries) {
  const response = await fetch("https://api.perplexity.ai/search", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: queries,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Perplexity API error (${response.status}): ${error}`);
  }

  return response.json();
}

function formatResult(result, query) {
  const lines = [];
  
  if (query) {
    lines.push(`## ${query}\n`);
  }

  // Handle array of search results
  if (Array.isArray(result)) {
    for (const item of result.slice(0, 5)) { // Top 5 results
      if (item.title) lines.push(`**${item.title}**`);
      if (item.url) lines.push(item.url);
      if (item.snippet) {
        // Clean up snippet - take first paragraph
        const clean = item.snippet.split('\n')[0].slice(0, 300);
        lines.push(clean + (item.snippet.length > 300 ? '...' : ''));
      }
      lines.push('');
    }
  } else if (result.results) {
    // Nested results format
    for (const item of result.results.slice(0, 5)) {
      if (item.title) lines.push(`**${item.title}**`);
      if (item.url) lines.push(item.url);
      if (item.snippet) {
        const clean = item.snippet.split('\n')[0].slice(0, 300);
        lines.push(clean + (item.snippet.length > 300 ? '...' : ''));
      }
      lines.push('');
    }
  } else {
    // Unknown format, dump it
    lines.push(JSON.stringify(result, null, 2));
  }

  return lines.join('\n');
}

try {
  const result = await search(queries);
  
  if (jsonOutput) {
    console.log(JSON.stringify(result, null, 2));
  } else {
    // The API returns an object with results array
    if (Array.isArray(result)) {
      // Multiple queries might return array
      result.forEach((r, i) => {
        console.log(formatResult(r, queries.length > 1 ? queries[i] : null));
      });
    } else if (result.results) {
      // Single query with results
      console.log(formatResult(result.results, queries[0]));
    } else {
      // Fallback - show top-level items if they look like search results
      const items = Object.values(result).filter(v => 
        v && typeof v === 'object' && (v.title || v.url || v.snippet)
      );
      if (items.length > 0) {
        console.log(formatResult(items, queries[0]));
      } else {
        // Just dump it nicely
        console.log(JSON.stringify(result, null, 2));
      }
    }
  }
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
