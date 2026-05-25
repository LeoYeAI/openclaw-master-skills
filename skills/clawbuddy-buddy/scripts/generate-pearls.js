#!/usr/bin/env node
/**
 * Generate Pearls from Agent Experience
 *
 * Reads the agent's memory files, tools, and configuration, then calls the
 * local OpenClaw gateway to generate sanitized, topic-based pearl files.
 *
 * Usage:
 *   node scripts/generate-pearls.js              # Full generation from all memory
 *   node scripts/generate-pearls.js --topic "Hetzner server setup"  # Single topic
 *
 * Environment:
 *   OPENCLAW_GATEWAY_URL   - Gateway URL (default: http://10.0.1.1:18789)
 *   OPENCLAW_GATEWAY_TOKEN - Gateway auth token
 *   OPENCLAW_MODEL         - Model to use (default: anthropic/claude-sonnet-4-5-20250929)
 *   PEARLS_DIR           - Output directory (default: ./pearls relative to skill)
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const GATEWAY_URL = process.env.OPENCLAW_GATEWAY_URL || 'http://10.0.1.1:18789';
const GATEWAY_TOKEN = process.env.OPENCLAW_GATEWAY_TOKEN || '';
const MODEL = process.env.OPENCLAW_MODEL || 'anthropic/claude-sonnet-4-5-20250929';

// Security: Only allow localhost gateways for pearl generation
// Pearl generation reads sensitive workspace files (MEMORY.md, AGENTS.md, TOOLS.md)
// and sends content to the gateway. Remote gateways = data exfiltration risk.
function isLocalhostUrl(url) {
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.toLowerCase();
    return host === 'localhost' || 
           host === '127.0.0.1' || 
           host === '::1' ||
           host.startsWith('10.') ||      // Private network (common for OpenClaw)
           host.startsWith('192.168.') ||  // Private network
           host.startsWith('172.16.') ||   // Private network
           host.startsWith('172.17.') ||   // Docker default
           host.startsWith('172.18.') ||   // Docker
           host.endsWith('.local');        // mDNS local
  } catch {
    return false;
  }
}

if (!isLocalhostUrl(GATEWAY_URL)) {
  console.error('❌ SECURITY: Pearl generation only works with localhost/private network gateways.');
  console.error(`   OPENCLAW_GATEWAY_URL (${GATEWAY_URL}) appears to be a remote host.`);
  console.error('   Pearl generation reads sensitive workspace files and sends to the gateway.');
  console.error('   Use a local gateway (127.0.0.1, localhost, 10.x.x.x, 192.168.x.x).');
  process.exit(1);
}

// Resolve pearls dir relative to the skill root (one level up from scripts/)
const SKILL_DIR = path.resolve(__dirname, '..');
const PEARLS_DIR = process.env.PEARLS_DIR
  ? path.resolve(process.env.PEARLS_DIR)
  : path.join(SKILL_DIR, 'pearls');

// Workspace root is typically the agent's home directory
const WORKSPACE = process.env.WORKSPACE || process.cwd();

function readFileIfExists(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf-8');
  } catch {
    return null;
  }
}

function getRecentMemoryFiles(memoryDir, daysBack = 30) {
  if (!fs.existsSync(memoryDir)) return [];

  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - daysBack);

  const files = [];
  for (const name of fs.readdirSync(memoryDir)) {
    if (!name.endsWith('.md')) continue;
    // Match YYYY-MM-DD.md pattern
    const match = name.match(/^(\d{4}-\d{2}-\d{2})\.md$/);
    if (!match) continue;
    const fileDate = new Date(match[1]);
    if (fileDate >= cutoff) {
      const content = readFileIfExists(path.join(memoryDir, name));
      if (content) files.push({ name, content });
    }
  }
  return files.sort((a, b) => a.name.localeCompare(b.name));
}

async function callGateway(messages) {
  const res = await fetch(`${GATEWAY_URL}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${GATEWAY_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: MODEL,
      messages,
      max_tokens: 8192,
    }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Gateway error: ${res.status} ${errText}`);
  }

  const data = await res.json();
  return data.choices?.[0]?.message?.content || '';
}

// Max source context size in characters (~50KB keeps us well within token limits)
const MAX_CONTEXT_CHARS = parseInt(process.env.MAX_CONTEXT_CHARS || '50000');

function truncate(text, maxChars) {
  if (text.length <= maxChars) return text;
  return text.slice(0, maxChars) + '\n\n[...truncated...]';
}

function buildSourceContext() {
  const sections = [];
  let totalChars = 0;

  // Priority order: MEMORY.md first (curated), then AGENTS.md, TOOLS.md, then daily files
  const memory = readFileIfExists(path.join(WORKSPACE, 'MEMORY.md'));
  if (memory) {
    const section = `## MEMORY.md (Long-term Memory)\n${memory}`;
    sections.push(section);
    totalChars += section.length;
  }

  const agents = readFileIfExists(path.join(WORKSPACE, 'AGENTS.md'));
  if (agents && totalChars < MAX_CONTEXT_CHARS) {
    const section = `## AGENTS.md (Agent Playbook)\n${agents}`;
    sections.push(section);
    totalChars += section.length;
  }

  const tools = readFileIfExists(path.join(WORKSPACE, 'TOOLS.md'));
  if (tools && totalChars < MAX_CONTEXT_CHARS) {
    const section = `## TOOLS.md (Local Tool Notes)\n${tools}`;
    sections.push(section);
    totalChars += section.length;
  }

  // Add daily files until we hit the limit, newest first (most relevant)
  const recentFiles = getRecentMemoryFiles(path.join(WORKSPACE, 'memory'));
  if (recentFiles.length > 0 && totalChars < MAX_CONTEXT_CHARS) {
    const reversed = recentFiles.reverse(); // newest first
    const included = [];
    for (const f of reversed) {
      const entry = `### ${f.name}\n${f.content}`;
      if (totalChars + entry.length > MAX_CONTEXT_CHARS) break;
      included.push(entry);
      totalChars += entry.length;
    }
    if (included.length > 0) {
      sections.push(`## Recent Daily Memory Files (${included.length} of ${recentFiles.length} included)\n${included.join('\n\n')}`);
    }
  }

  return sections.join('\n\n---\n\n');
}

const GENERATION_PROMPT = `You are a knowledge extraction system. Your job is to read an AI agent's memory files and configuration, then produce a set of topic-based pearl files that capture generalizable knowledge and best practices.

CRITICAL PRIVACY RULES -- you MUST follow these:
- STRIP ALL personal data: real names, dates of birth, addresses, phone numbers, email addresses, family member names or relationships, employer names, health info, financial details
- STRIP ALL credentials: API keys, tokens, passwords, SSH keys, IP addresses, hostnames, port numbers
- STRIP ALL infrastructure specifics: server names, domain names, service URLs, database names, container names, project IDs
- STRIP ALL hardware specifics: exact server models, CPU/RAM/disk specs, machine types (e.g. "CAX31"), pricing tiers
- STRIP ALL location data: datacenter locations, cities, countries, regions, cloud availability zones
- STRIP ALL network details: Tailscale IPs, VPN configs, port numbers, firewall rules, proxy setups
- Replace specific people with generic references: "the human", "a user", "a team member"
- Replace specific services/tools with generic descriptions unless they are public/open-source projects
- Replace specific hardware with generic guidance: "an ARM VPS with moderate specs" not "Hetzner CAX31 8 vCPU 16GB"
- Keep ONLY generalizable knowledge: patterns, lessons learned, best practices, techniques, workflows

OUTPUT FORMAT:
Produce your output as a series of pearl files separated by markers. Each pearl starts with:
===PEARL: filename-slug===
followed by the markdown content of that pearl.

Choose topics based on the actual content provided. Suggested topic areas (use only those that have real content to draw from):
- openclaw-basics -- Core patterns for OpenClaw agents
- memory-management -- How to use memory files effectively
- skill-development -- Building and maintaining skills
- safety-and-privacy -- Security best practices
- automation -- Heartbeats, cron, scheduling
- troubleshooting -- Debugging and problem-solving patterns
- communication -- Group chats, messaging etiquette
- Any other domain-specific expertise found in the source material

Each pearl should be:
- Self-contained and focused on one topic
- Written as guidance from an experienced agent to a learning agent
- Practical with concrete (but sanitized) examples
- ASCII only -- no emojis, no unicode arrows (use -> and --)

Do NOT include a pearl if you don't have substantial content for it. Quality over quantity.`;

const TOPIC_PROMPT = `You are a knowledge extraction system. Your job is to read an AI agent's memory files and produce a SINGLE focused pearl on a specific topic.

CRITICAL PRIVACY RULES -- you MUST follow these:
- STRIP ALL personal data: real names, dates of birth, addresses, phone numbers, email addresses, family member names, employer names, health info, financial details
- STRIP ALL credentials: API keys, tokens, passwords, SSH keys, IP addresses, hostnames, port numbers
- STRIP ALL infrastructure specifics: server names, domain names, service URLs, database names, container names, project IDs
- STRIP ALL hardware specifics: exact server models, CPU/RAM/disk specs, machine types, pricing tiers
- STRIP ALL location data: datacenter locations, cities, countries, regions, cloud availability zones
- STRIP ALL network details: Tailscale IPs, VPN configs, port numbers, firewall rules, proxy setups
- Replace specific people with generic references: "the human", "a user", "a team member"
- Replace specific hardware with generic guidance: "an ARM VPS" not exact specs
- Keep ONLY generalizable knowledge: patterns, lessons learned, best practices, techniques

OUTPUT FORMAT:
Produce ONLY the markdown content for this single pearl. Do NOT use the ===PEARL:=== markers.
Start directly with a # heading for the topic.

The pearl should be:
- Focused entirely on the requested topic
- Written as guidance from an experienced agent to a learning agent
- Practical with concrete (but sanitized) examples
- ASCII only -- no emojis, no unicode (use -> and --)

If there is no relevant content for this topic in the source material, say so clearly and produce a short pearl with whatever general knowledge you have about it.`;

function parseArgs() {
  const args = process.argv.slice(2);
  const result = { topic: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--topic' && args[i + 1]) {
      result.topic = args[i + 1];
      i++;
    }
  }
  return result;
}

function topicToSlug(topic) {
  return topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

async function generateSinglePearl(topic) {
  console.log(`Generating pearl for topic: "${topic}"`);
  console.log('Reading source files from workspace:', WORKSPACE);

  const sourceContext = buildSourceContext();
  if (!sourceContext.trim()) {
    console.error('No source files found. Nothing to generate from.');
    process.exit(1);
  }

  console.log(`Source context: ${Math.round(sourceContext.length / 1024)}KB`);
  console.log(`Calling gateway (${MODEL})...`);

  const response = await callGateway([
    { role: 'system', content: TOPIC_PROMPT },
    { role: 'user', content: `Generate a pearl about: ${topic}\n\nSource material:\n\n${sourceContext}` },
  ]);

  if (!response) {
    console.error('Empty response from gateway.');
    process.exit(1);
  }

  if (!fs.existsSync(PEARLS_DIR)) {
    fs.mkdirSync(PEARLS_DIR, { recursive: true });
  }

  const slug = topicToSlug(topic);
  const filename = `${slug}.md`;
  const filePath = path.join(PEARLS_DIR, filename);
  fs.writeFileSync(filePath, response.trim() + '\n');
  console.log(`Written: ${filename} (${Math.round(response.length / 1024)}KB)`);
}

async function generateAllPearls() {
  console.log('Reading source files from workspace:', WORKSPACE);

  const sourceContext = buildSourceContext();
  if (!sourceContext.trim()) {
    console.error('No source files found. Nothing to generate pearls from.');
    process.exit(1);
  }

  console.log(`Source context: ${Math.round(sourceContext.length / 1024)}KB`);
  console.log(`Calling gateway (${MODEL})...`);

  const response = await callGateway([
    { role: 'system', content: GENERATION_PROMPT },
    { role: 'user', content: `Here are the source files to extract knowledge from:\n\n${sourceContext}` },
  ]);

  if (!response) {
    console.error('Empty response from gateway.');
    process.exit(1);
  }

  // Parse pearls from response
  const pearlPattern = /===PEARL:\s*(.+?)===\n([\s\S]*?)(?====PEARL:|$)/g;
  const pearls = [];
  let match;
  while ((match = pearlPattern.exec(response)) !== null) {
    const slug = match[1].trim().replace(/[^a-z0-9-]/g, '');
    const content = match[2].trim();
    if (slug && content) {
      pearls.push({ slug, content });
    }
  }

  if (pearls.length === 0) {
    console.error('No pearls parsed from response. Raw output:');
    console.error(response.slice(0, 500));
    process.exit(1);
  }

  // Write pearls
  if (!fs.existsSync(PEARLS_DIR)) {
    fs.mkdirSync(PEARLS_DIR, { recursive: true });
  }

  // Clean existing pearls (idempotent regeneration)
  for (const existing of fs.readdirSync(PEARLS_DIR)) {
    if (existing.endsWith('.md')) {
      fs.unlinkSync(path.join(PEARLS_DIR, existing));
    }
  }

  for (const pearl of pearls) {
    const filename = `${pearl.slug}.md`;
    const filePath = path.join(PEARLS_DIR, filename);
    fs.writeFileSync(filePath, pearl.content + '\n');
    console.log(`  Written: ${filename} (${Math.round(pearl.content.length / 1024)}KB)`);
  }

  console.log(`\nGenerated ${pearls.length} pearl(s) in ${PEARLS_DIR}`);

  // Auto-update specialties and description on the relay
  await updateRelayProfile(pearls);
}

/**
 * Extract human-readable specialty names from pearl filenames/content.
 * Converts slugs like "docker-coolify" to "Docker & Coolify".
 */
function slugToTitle(slug) {
  return slug
    .split('-')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
    .replace(/ And /g, ' & ');
}

/**
 * Build a markdown description from pearl topics.
 */
function buildDescription(pearls) {
  const topics = pearls.map(l => slugToTitle(l.slug));
  return `Buddy with expertise in: ${topics.join(', ')}.`;
}

/**
 * Update buddy specialties and description on the relay after pearl generation.
 */
async function updateRelayProfile(pearls) {
  const RELAY_URL = process.env.CLAWBUDDY_URL || 'https://clawbuddy.help';
  const RELAY_TOKEN = process.env.CLAWBUDDY_TOKEN;

  if (!RELAY_TOKEN) {
    console.log('CLAWBUDDY_TOKEN not set — skipping relay profile update.');
    return;
  }

  const specialties = pearls.map(l => slugToTitle(l.slug));
  const description = buildDescription(pearls);

  console.log(`Updating relay profile:`);
  console.log(`  Specialties: ${specialties.join(', ')}`);
  console.log(`  Description: ${description}`);

  try {
    const res = await fetch(`${RELAY_URL}/api/buddy/profile`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${RELAY_TOKEN}`,
      },
      body: JSON.stringify({ specialties, description }),
    });

    if (res.ok) {
      const data = await res.json();
      console.log(`Relay profile updated.`);
    } else {
      const err = await res.text();
      console.warn(`Failed to update relay profile (${res.status}): ${err}`);
    }
  } catch (err) {
    console.warn(`Could not reach relay to update profile: ${err.message}`);
  }
}

const { topic } = parseArgs();

async function main() {
  if (topic) {
    await generateSinglePearl(topic);
  } else {
    await generateAllPearls();
  }
}

main().catch(err => {
  console.error('Failed to generate pearls:', err.message);
  process.exit(1);
});
