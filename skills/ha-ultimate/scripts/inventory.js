#!/usr/bin/env node
/**
 * Home Assistant Entity Inventory Generator
 *
 * Generates ENTITIES.md with all HA entities organized by domain,
 * including name, area, and current state. Run this before first use
 * so the agent knows what devices are available.
 *
 * Based on the inventory script by Paco (mia personal skill).
 *
 * Usage: node scripts/inventory.js [output_path]
 * Env:   HA_URL, HA_TOKEN
 */

const fs = require('fs');
const path = require('path');

// Load .env if present
const envPath = path.resolve(__dirname, '..', '.env');
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const match = line.match(/^([^#=]+)=(.*)$/);
    if (match && !process.env[match[1].trim()]) {
      process.env[match[1].trim()] = match[2].trim();
    }
  });
}

const HA_URL = process.env.HA_URL || 'http://homeassistant.local:8123';
const HA_TOKEN = process.env.HA_TOKEN;

if (!HA_TOKEN) {
  console.error('Error: HA_TOKEN not found in environment or .env file.');
  console.error('Set it with: export HA_TOKEN="your-long-lived-access-token"');
  process.exit(1);
}

const outputArg = process.argv[2];
const outputPath = outputArg
  ? path.resolve(outputArg)
  : path.resolve(__dirname, '..', 'ENTITIES.md');

// Jinja2 template to get all entities with area info
const template = `{"entities": [{% for state in states %}{"id": "{{ state.entity_id }}", "name": "{{ state.name | default('Unknown') | replace('"', '\\\\"') }}", "area": "{{ area_name(state.entity_id) | default('No Area') | replace('"', '\\\\"') }}", "domain": "{{ state.domain }}", "state": "{{ state.state | replace('"', '\\\\"') }}"}{{ "," if not loop.last }}{% endfor %}]}`;

async function fetchInventory() {
  try {
    console.log(`Fetching inventory from ${HA_URL}...`);

    const response = await fetch(`${HA_URL}/api/template`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${HA_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ template }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`HTTP ${response.status}: ${errorText}`);
    }

    const result = await response.text();
    let data;
    try {
      data = JSON.parse(result);
    } catch (e) {
      console.error('Failed to parse response. Raw output (first 500 chars):');
      console.error(result.substring(0, 500));
      throw new Error('Template response is not valid JSON');
    }

    if (!data || !data.entities) {
      throw new Error('Invalid response structure — missing entities array');
    }

    // Group by domain
    const byDomain = {};
    data.entities.forEach(entity => {
      if (!byDomain[entity.domain]) byDomain[entity.domain] = [];
      byDomain[entity.domain].push(entity);
    });

    // Priority order for domains
    const priority = [
      'light', 'switch', 'sensor', 'binary_sensor', 'climate', 'cover',
      'lock', 'fan', 'media_player', 'vacuum', 'alarm_control_panel',
      'person', 'zone', 'scene', 'script', 'automation', 'calendar',
      'weather', 'notify', 'input_boolean', 'input_number', 'input_select',
      'input_text', 'input_datetime', 'tts',
    ];

    const domains = Object.keys(byDomain).sort((a, b) => {
      const idxA = priority.indexOf(a);
      const idxB = priority.indexOf(b);
      if (idxA !== -1 && idxB !== -1) return idxA - idxB;
      if (idxA !== -1) return -1;
      if (idxB !== -1) return 1;
      return a.localeCompare(b);
    });

    // Build markdown
    const now = new Date().toISOString();
    let md = `# Home Assistant Entities\n\n`;
    md += `> Auto-generated on ${now}\n`;
    md += `> Source: ${HA_URL}\n`;
    md += `> Total: ${data.entities.length} entities across ${domains.length} domains\n\n`;

    // Summary table
    md += `## Summary\n\n| Domain | Count |\n|--------|-------|\n`;
    for (const domain of domains) {
      md += `| ${domain} | ${byDomain[domain].length} |\n`;
    }
    md += '\n';

    // Detail tables
    for (const domain of domains) {
      md += `## ${domain.toUpperCase()}\n\n`;
      md += `| Entity ID | Name | Area | State |\n|---|---|---|---|\n`;
      byDomain[domain]
        .sort((a, b) => a.id.localeCompare(b.id))
        .forEach(e => {
          const name = (e.name || '').replace(/\|/g, '-');
          const area = (e.area || '').replace(/\|/g, '-');
          const state = (e.state || '').replace(/\|/g, '-');
          md += `| \`${e.id}\` | ${name} | ${area} | ${state} |\n`;
        });
      md += '\n';
    }

    fs.writeFileSync(outputPath, md);
    console.log(`✅ Inventory saved to ${outputPath}`);
    console.log(`   ${data.entities.length} entities across ${domains.length} domains`);

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

fetchInventory();
