#!/usr/bin/env node
/**
 * Skill Market script
 * Create, manage, and publish skills to the ClawFriend Skill Market
 */

import fs from 'fs';
import {
  apiRequest,
  checkApiKey,
  success,
  error,
  warning,
  info,
  prettyJson
} from './utils.js';

/**
 * Create a new skill
 */
async function createSkill(options) {
  if (!checkApiKey()) process.exit(1);

  const { name, description, isActive, version, file, content: inlineContent } = options;

  if (!name) { error('--name is required'); process.exit(1); }
  if (!version) { error('--version is required (e.g. 1.0.0)'); process.exit(1); }

  let content = inlineContent;
  if (file) {
    if (!fs.existsSync(file)) { error(`File not found: ${file}`); process.exit(1); }
    content = fs.readFileSync(file, 'utf8');
  }
  if (!content) { error('--file or --content is required'); process.exit(1); }

  info(`Creating skill "${name}"...`);

  const body = {
    name,
    content,
    type: 'skill',
    visibility: 'public',
    version_number: version,
    ...(description && { description }),
    ...(isActive !== undefined && { is_active: isActive })
  };

  const skill = await apiRequest('/v1/academy/skills', {
    method: 'POST',
    body: JSON.stringify(body)
  });

  success(`Skill created!`);
  console.log('\n📦 Skill Details:');
  console.log(prettyJson({
    id: skill.id,
    name: skill.name,
    type: skill.type,
    visibility: skill.visibility,
    is_active: skill.is_active,
    created_at: skill.created_at
  }));
  console.log(`\n🔗 Market URL: https://clawfriend.ai/skill-market/${skill.id}`);

  return skill;
}

/**
 * List skills
 */
async function listSkills(options) {
  if (!checkApiKey()) process.exit(1);

  const { search, type, page = 1, limit = 20 } = options;

  const params = new URLSearchParams({ page, limit });
  if (search) params.set('search', search);
  if (type) params.set('type', type);

  info('Fetching skills...');
  const result = await apiRequest(`/v1/academy/skills?${params}`);

  const skills = result.data || result;
  const total = result.total || skills.length;

  console.log(`\n📋 Skills (${skills.length}/${total} total):\n`);
  if (!skills.length) {
    console.log('No skills found.');
    return;
  }

  skills.forEach((s, i) => {
    console.log(`${i + 1}. [${s.type}] ${s.name}`);
    console.log(`   ID: ${s.id}`);
    console.log(`   Visibility: ${s.visibility} | Active: ${s.is_active} | Likes: ${s.like_count || 0} | Downloads: ${s.download_count || 0}`);
    if (s.description) console.log(`   ${s.description}`);
    console.log();
  });
}

/**
 * Get skill by ID
 */
async function getSkill(skillId) {
  if (!checkApiKey()) process.exit(1);
  if (!skillId) { error('Skill ID is required'); process.exit(1); }

  info(`Fetching skill ${skillId}...`);
  const skill = await apiRequest(`/v1/academy/skills/${skillId}`);

  console.log('\n📦 Skill:');
  console.log(prettyJson({
    id: skill.id,
    name: skill.name,
    type: skill.type,
    visibility: skill.visibility,
    is_active: skill.is_active,
    like_count: skill.like_count,
    download_count: skill.download_count,
    can_view_full_content: skill.can_view_full_content,
    tags: (skill.tags || []).map(t => t.name),
    versions: (skill.versions || []).map(v => ({ id: v.id, version: v.versionNumber, created_at: v.created_at })),
    created_at: skill.created_at,
    updated_at: skill.updated_at
  }));

  return skill;
}

/**
 * Update skill metadata
 */
async function updateSkill(skillId, options) {
  if (!checkApiKey()) process.exit(1);
  if (!skillId) { error('Skill ID is required'); process.exit(1); }

  const { name, description, content: inlineContent, file, isActive } = options;

  let content = inlineContent;
  if (file) {
    if (!fs.existsSync(file)) { error(`File not found: ${file}`); process.exit(1); }
    content = fs.readFileSync(file, 'utf8');
  }

  const body = { type: 'skill', visibility: 'public' };
  if (name !== undefined) body.name = name;
  if (description !== undefined) body.description = description;
  if (content !== undefined) body.content = content;
  if (isActive !== undefined) body.is_active = isActive;

  if (!Object.keys(body).length) {
    warning('Nothing to update. Provide at least one of: --name, --description, --content, --file, --visibility, --is-active');
    return;
  }

  info(`Updating skill ${skillId}...`);
  const skill = await apiRequest(`/v1/academy/skills/${skillId}`, {
    method: 'PUT',
    body: JSON.stringify(body)
  });

  success('Skill updated!');
  console.log(prettyJson({ id: skill.id, name: skill.name, updated_at: skill.updated_at }));
}

/**
 * Add a new version to a skill
 */
async function addVersion(skillId, options) {
  if (!checkApiKey()) process.exit(1);
  if (!skillId) { error('Skill ID is required'); process.exit(1); }

  const { version, file, content: inlineContent, name, description } = options;

  if (!version) { error('--version is required (e.g. 1.1.0)'); process.exit(1); }

  let content = inlineContent;
  if (file) {
    if (!fs.existsSync(file)) { error(`File not found: ${file}`); process.exit(1); }
    content = fs.readFileSync(file, 'utf8');
  }
  if (!content) { error('--file or --content is required'); process.exit(1); }

  const body = {
    version_number: version,
    content,
    type: 'skill',
    ...(name && { name }),
    ...(description !== undefined && { description })
  };

  info(`Adding version ${version} to skill ${skillId}...`);
  const ver = await apiRequest(`/v1/academy/skills/${skillId}/versions`, {
    method: 'POST',
    body: JSON.stringify(body)
  });

  success(`Version ${ver.versionNumber} added!`);
  console.log(prettyJson({
    id: ver.id,
    versionNumber: ver.versionNumber,
    name: ver.name,
    type: ver.type,
    created_at: ver.created_at
  }));
}

/**
 * Delete a skill
 */
async function deleteSkill(skillId) {
  if (!checkApiKey()) process.exit(1);
  if (!skillId) { error('Skill ID is required'); process.exit(1); }

  info(`Deleting skill ${skillId}...`);
  await apiRequest(`/v1/academy/skills/${skillId}`, { method: 'DELETE' });
  success('Skill deleted.');
}

/**
 * Toggle like on a skill
 */
async function likeSkill(skillId) {
  if (!checkApiKey()) process.exit(1);
  if (!skillId) { error('Skill ID is required'); process.exit(1); }

  const result = await apiRequest(`/v1/academy/skills/${skillId}/like`, { method: 'POST' });
  const action = result.liked ? 'Liked' : 'Unliked';
  success(`${action} skill! Total likes: ${result.like_count}`);
}

/**
 * Get trending tags
 */
async function trendingTags(limit = 20) {
  info('Fetching trending tags...');
  const result = await apiRequest(`/v1/academy/tags/trending?limit=${limit}`);
  const tags = result.tags || result;

  console.log('\n🏷️  Trending Tags:\n');
  tags.forEach((t, i) => {
    console.log(`${i + 1}. ${t.name} (${t.category || 'general'}) — used ${t.usage_count} time(s)`);
  });
}

/**
 * Parse CLI arguments
 */
function parseArgs(args) {
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const next = args[i + 1];
      if (next && !next.startsWith('--')) {
        if (next === 'true') opts[key] = true;
        else if (next === 'false') opts[key] = false;
        else opts[key] = next;
        i++;
      } else {
        opts[key] = true;
      }
    }
  }
  return opts;
}

/**
 * Main CLI
 */
async function main() {
  const command = process.argv[2];
  const args = process.argv.slice(3);
  const opts = parseArgs(args);
  // First positional arg after command (not preceded by a flag)
  const skillId = args.find(a => !a.startsWith('--') && args[args.indexOf(a) - 1]?.startsWith('--') !== true);

  try {
    switch (command) {
      case 'create':
        await createSkill(opts);
        break;

      case 'list':
        await listSkills(opts);
        break;

      case 'get':
        await getSkill(skillId);
        break;

      case 'update':
        await updateSkill(skillId, opts);
        break;

      case 'add-version':
        await addVersion(skillId, opts);
        break;

      case 'delete':
        await deleteSkill(skillId);
        break;

      case 'like':
        await likeSkill(skillId);
        break;

      case 'trending-tags':
        await trendingTags(opts.limit);
        break;

      default:
        console.log('ClawFriend Skill Market Manager\n');
        console.log('Usage:');
        console.log('  node scripts/skill-market.js create      --name <name> --version <x.y.z> --file <path>   [type=skill, visibility=public]');
        console.log('  node scripts/skill-market.js list        [--search <query>] [--type <skill|workflow>]');
        console.log('  node scripts/skill-market.js get         <skill-id>');
        console.log('  node scripts/skill-market.js update      <skill-id> [--name <n>] [--description <d>] [--file <path>] [--visibility <public|private>] [--is-active <true|false>]');
        console.log('  node scripts/skill-market.js add-version <skill-id> --version <x.y.z> --file <path>');
        console.log('  node scripts/skill-market.js delete      <skill-id>');
        console.log('  node scripts/skill-market.js like        <skill-id>');
        console.log('  node scripts/skill-market.js trending-tags [--limit <n>]');
        console.log('\nExamples:');
        console.log('  node scripts/skill-market.js create --name "DeFi Analyzer" --version 1.0.0 --file ./my-skill.md');
        console.log('  node scripts/skill-market.js list --search trading');
        console.log('  node scripts/skill-market.js add-version abc-123 --version 1.1.0 --file ./my-skill-v2.md');
        console.log('  node scripts/skill-market.js update abc-123 --is-active false');
        break;
    }
  } catch (e) {
    error(e.message);
    if (e.data) console.log('Details:', prettyJson(e.data));
    process.exit(1);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
