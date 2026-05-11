/**
 * parse-config.js — Parse OpenClaw JSON5 config and extract a value
 * Usage: node parse-config.js <config-path> <dot.path> [default-value]
 * 
 * Handles JSON5/JS object literal configs (unquoted keys, trailing commas, 
 * single-quoted strings, comments)
 */

const fs = require('fs');

const configPath = process.argv[2];
const dotPath = process.argv[3];
const defaultVal = process.argv[4] || '';

if (!configPath || !dotPath) {
  console.error('Usage: node parse-config.js <config-path> <dot.path> [default]');
  process.exit(1);
}

try {
  const raw = fs.readFileSync(configPath, 'utf8');
  // Evaluate as JS object literal — handles JSON5, trailing commas, unquoted keys, etc.
  const config = new Function('return (' + raw + ')')();
  
  // Navigate dot path
  let val = config;
  for (const key of dotPath.split('.')) {
    if (val === undefined || val === null) break;
    val = val[key];
  }
  
  if (val === undefined || val === null) {
    console.log(defaultVal);
  } else if (typeof val === 'object') {
    console.log(JSON.stringify(val));
  } else {
    console.log(val);
  }
} catch (e) {
  console.error(`Error: ${e.message}`);
  console.log(defaultVal);
}
