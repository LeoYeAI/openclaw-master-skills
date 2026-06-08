#!/usr/bin/env node
/**
 * stitch.mjs — CLI wrapper for Google Stitch SDK
 * Uses raw MCP tool calls because the SDK wrapper classes
 * don't match the actual API response structure.
 */

import { stitch } from '@google/stitch-sdk';
import { join } from 'node:path';
import {
  RUNS_DIR, makeRunDir, downloadFile, saveLatest, loadLatest,
  saveScreenArtifacts, saveResult, resolveUrl,
} from './artifacts.mjs';
import { checkScreenshotUrl, HIRES_SUFFIX } from './download.mjs';
import { applyDesignSystem } from './design-system.mjs';
import {
  setName, removeName, renameName, resolveName, listNames, normalizeAlias, loadNames, saveNames as saveNamesRaw,
} from './names.mjs';
import {
  appendEvent, readEvents, promptPreview, makeVariantGroupId,
  historyForAlias, aliasRevisions, lineage, rebuildNames,
} from './events.mjs';

// --- Helpers ---

function die(msg) {
  console.error(`Error: ${msg}`);
  process.exit(1);
}

function ok(data) {
  console.log(JSON.stringify({ ok: true, ...data }, null, 2));
}

function parseArgs(args) {
  const flags = {};
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const val = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
      flags[key] = val;
    } else {
      positional.push(args[i]);
    }
  }
  return { flags, positional };
}

// --- Argument Parsing ---

function resolveDevice(flag) {
  if (!flag) return undefined;
  const map = { desktop: 'DESKTOP', mobile: 'MOBILE', tablet: 'TABLET', agnostic: 'AGNOSTIC' };
  return map[flag.toLowerCase()] || die(`Unknown device: ${flag}`);
}

function resolveModel(flag) {
  if (!flag) return undefined;
  const map = { pro: 'GEMINI_3_1_PRO', flash: 'GEMINI_3_FLASH' };
  return map[flag.toLowerCase()] || die(`Unknown model: ${flag}`);
}

function resolveRange(flag) {
  if (!flag) return 'EXPLORE';
  const map = { refine: 'REFINE', explore: 'EXPLORE', reimagine: 'REIMAGINE' };
  return map[flag.toLowerCase()] || die(`Unknown range: ${flag}`);
}

function resolveAspects(flag) {
  if (!flag) return undefined;
  const valid = ['LAYOUT', 'COLOR_SCHEME', 'IMAGES', 'TEXT_FONT', 'TEXT_CONTENT'];
  return flag.split(',').map(a => {
    const upper = a.trim().toUpperCase();
    if (!valid.includes(upper)) die(`Unknown aspect: ${a}. Use: ${valid.join(', ')}`);
    return upper;
  });
}



async function resolveProjectId(flags) {
  if (flags.project) return flags.project;
  const latest = await loadLatest();
  if (latest?.projectId) return latest.projectId;
  die('No --project given and no latest-screen.json. Specify --project <id>.');
}

/** Extract screen ID from name like "projects/123/screens/abc" */
function extractScreenId(screen) {
  if (screen.id) return screen.id;
  if (screen.name) {
    const parts = screen.name.split('/');
    return parts[parts.length - 1];
  }
  return null;
}

async function cleanup() {
  try { await stitch.close(); } catch {}
}

/**
 * Robust tool call wrapper.
 * 
 * The Stitch MCP server uses SSE streaming. Long operations (generate, edit, variants)
 * can take 2-5 minutes. The TCP connection often drops before completion, causing
 * callTool to throw — but the server-side operation may still succeed.
 * 
 * Strategy (per SDK docs: "DO NOT RETRY, use get_screen if connection fails"):
 * 1. Call the tool
 * 2. If it succeeds → extract screen from response
 * 3. If it fails with a connection error → poll list_screens to find the new screen
 */
async function callToolRobust({ toolName, args, projectId, knownIds = null }) {
  try {
    const raw = await stitch.callTool(toolName, args);
    const screen = raw?.outputComponents?.[0]?.design?.screens?.[0];
    if (screen) return screen;
    // Response came back but no screen — try recovery
    console.error(`⚠️ No screen in response, attempting recovery via list_screens...`);
  } catch (err) {
    console.error(`⚠️ Connection error during ${toolName}: ${err.message}`);
    console.error(`   Attempting recovery via list_screens (server may still be processing)...`);
  }

  // Recovery: poll list_screens for a new screen that appeared after our call.
  // If knownIds is provided, filter to only screens that are genuinely new.
  for (let attempt = 1; attempt <= 6; attempt++) {
    const waitSec = attempt <= 3 ? 30 : 60;
    console.error(`   Recovery attempt ${attempt}/6 — waiting ${waitSec}s...`);
    await new Promise(r => setTimeout(r, waitSec * 1000));

    try {
      const listRaw = await stitch.callTool('list_screens', { projectId });
      const screens = listRaw?.screens || [];

      // Determine candidates: new screens only (when knownIds snapshot is available)
      let candidates;
      if (knownIds) {
        candidates = screens.filter(s => {
          const id = extractScreenId(s);
          return id && !knownIds.has(id);
        });
      } else {
        candidates = screens.length > 0 ? [screens[screens.length - 1]] : [];
      }

      if (candidates.length > 1) {
        console.error(`   ⚠️ Found ${candidates.length} new screens in recovery — taking the last one.`);
      }

      const candidate = candidates[candidates.length - 1];
      if (candidate) {
        const screenId = extractScreenId(candidate);
        if (screenId) {
          console.error(`   ✅ Found screen via recovery: ${screenId}`);
          const full = await stitch.callTool('get_screen', {
            projectId, screenId,
            name: `projects/${projectId}/screens/${screenId}`,
          });
          return full;
        }
      }
    } catch (pollErr) {
      console.error(`   Recovery poll failed: ${pollErr.message}`);
    }
  }

  die(`${toolName} failed and recovery could not find the screen. The operation may still be processing — check stitch.withgoogle.com.`);
}

// --- Commands ---

async function cmdProjects() {
  const raw = await stitch.callTool('list_projects', {});
  const projects = raw.projects || [];
  ok({
    count: projects.length,
    projects: projects.map(p => ({
      id: p.name?.split('/').pop() || p.id,
      title: p.title || '(untitled)',
    })),
  });
}

async function cmdCreate(title) {
  if (!title) die('Usage: create "Project Title"');
  const raw = await stitch.callTool('create_project', { title });
  const id = raw.name?.split('/').pop() || raw.id;
  ok({ projectId: id, title });
  console.error(`✅ Project "${title}" created: ${id}`);
}

async function cmdInfo(projectId) {
  if (!projectId) die('Usage: info <project-id>');
  const projectRaw = await stitch.callTool('get_project', { name: `projects/${projectId}` });
  const screenRaw = await stitch.callTool('list_screens', { projectId });
  const screens = screenRaw.screens || [];
  ok({
    projectId,
    title: projectRaw.title || '(untitled)',
    screenCount: screens.length,
    screens: screens.map(s => ({
      id: extractScreenId(s),
      title: s.title || s.name || '(unnamed)',
    })),
  });
}

async function cmdGenerate(projectId, prompt, flags) {
  if (!projectId || !prompt) die('Usage: generate <project-id> "prompt" [--device desktop] [--model pro] [--design-system <name>]');

  prompt = await applyDesignSystem(prompt, flags, die);
  const args = { projectId, prompt };
  const device = resolveDevice(flags.device);
  const model = resolveModel(flags.model);
  if (device) {
    args.deviceType = device;
  } else {
    args.deviceType = 'DESKTOP';
  }
  if (model) args.modelId = model;

  // Snapshot existing screen IDs so recovery can filter to genuinely new screens
  let knownIds = new Set();
  try {
    const listBefore = await stitch.callTool('list_screens', { projectId });
    for (const s of listBefore?.screens || []) {
      const id = extractScreenId(s);
      if (id) knownIds.add(id);
    }
  } catch { /* proceed without snapshot — recovery will be weaker */ }

  console.error(`🎨 Generating screen... (this may take 1-5 minutes)`);
  const screen = await callToolRobust({ toolName: 'generate_screen_from_text', args, projectId, knownIds });

  const screenId = extractScreenId(screen);
  const runDir = await makeRunDir('generate', prompt);
  const artifacts = await saveScreenArtifacts(runDir, screen);

  await saveResult(runDir, {
    projectId, screenId, prompt, device: device || 'default', model: model || 'default',
    title: screen.title, width: screen.width, height: screen.height,
    screenshotUrl: resolveUrl(screen.screenshot), htmlUrl: resolveUrl(screen.htmlCode),
    timestamp: new Date().toISOString(),
  });
  artifacts.push('result.json');

  await saveLatest(projectId, screenId, 'generate');
  const named = await autoName(projectId, screenId, flags.name, flags.force);

  // Emit event
  const runDirName = runDir.split('/').pop();
  await appendEvent(projectId, {
    op: 'generate',
    screenId,
    ...(named ? { alias: named } : {}),
    parentScreenId: null,
    promptPreview: promptPreview(prompt),
    runDir: runDirName,
  });

  ok({ projectId, screenId, prompt, runDir, artifacts, ...(named ? { alias: named } : {}) });
  console.error(`✅ Screen generated: ${screenId}`);
  console.error(`📁 Artifacts: ${runDir}`);
}

async function cmdEdit(screenId, prompt, flags) {
  if (!screenId || !prompt) die('Usage: edit <screen-id> "prompt" [--project <id>] [--design-system <name>]');
  const projectId = await resolveProjectId(flags);

  prompt = await applyDesignSystem(prompt, flags, die);
  const args = { projectId, prompt, selectedScreenIds: [screenId] };
  const device = resolveDevice(flags.device);
  const model = resolveModel(flags.model);
  if (device) {
    args.deviceType = device;
  } else {
    const inherited = await inheritDeviceType(projectId, screenId);
    if (inherited) args.deviceType = inherited;
  }
  if (model) args.modelId = model;

  // Snapshot existing screen IDs so recovery can filter to genuinely new screens
  let knownIds = new Set();
  try {
    const listBefore = await stitch.callTool('list_screens', { projectId });
    for (const s of listBefore?.screens || []) {
      const id = extractScreenId(s);
      if (id) knownIds.add(id);
    }
  } catch { /* proceed without snapshot — recovery will be weaker */ }

  console.error(`✏️ Editing screen... (this may take 1-5 minutes)`);
  const screen = await callToolRobust({ toolName: 'edit_screens', args, projectId, knownIds });

  const newScreenId = extractScreenId(screen);
  const runDir = await makeRunDir('edit', prompt);
  const artifacts = await saveScreenArtifacts(runDir, screen);

  await saveResult(runDir, {
    projectId, screenId: newScreenId, originalScreenId: screenId, prompt,
    title: screen.title, timestamp: new Date().toISOString(),
  });
  artifacts.push('result.json');

  await saveLatest(projectId, newScreenId, 'edit');
  const named = await autoName(projectId, newScreenId, flags.name, flags.force);

  // Emit event
  const editRunDirName = runDir.split('/').pop();
  await appendEvent(projectId, {
    op: 'edit',
    screenId: newScreenId,
    parentScreenId: screenId,
    ...(named ? { alias: named } : {}),
    promptPreview: promptPreview(prompt),
    runDir: editRunDirName,
  });

  ok({ projectId, screenId: newScreenId, originalScreenId: screenId, prompt, runDir, artifacts, ...(named ? { alias: named } : {}) });
  console.error(`✅ Screen edited: ${newScreenId}`);
  console.error(`📁 Artifacts: ${runDir}`);
}

async function cmdVariants(screenId, prompt, flags) {
  if (!screenId || !prompt) die('Usage: variants <screen-id> "prompt" [--project <id>] [--count 3] [--range explore] [--design-system <name>]');
  const projectId = await resolveProjectId(flags);

  prompt = await applyDesignSystem(prompt, flags, die);
  const count = parseInt(flags.count || '3', 10);
  if (isNaN(count) || count < 1 || count > 5) die('--count must be between 1 and 5');
  const variantOptions = {
    variantCount: count,
    creativeRange: resolveRange(flags.range),
  };
  const aspects = resolveAspects(flags.aspects);
  if (aspects) variantOptions.aspects = aspects;

  const args = { projectId, prompt, selectedScreenIds: [screenId], variantOptions };
  const device = resolveDevice(flags.device);
  const model = resolveModel(flags.model);
  if (device) {
    args.deviceType = device;
  } else {
    const inherited = await inheritDeviceType(projectId, screenId);
    if (inherited) args.deviceType = inherited;
  }
  if (model) args.modelId = model;

  console.error(`🔀 Generating ${variantOptions.variantCount} variants (${variantOptions.creativeRange})...`);
  
  // Snapshot existing screen IDs before the call for delta-based recovery
  let knownScreenIds = new Set();
  try {
    const listBefore = await stitch.callTool('list_screens', { projectId });
    for (const s of listBefore?.screens || []) {
      const id = extractScreenId(s);
      if (id) knownScreenIds.add(id);
    }
  } catch { /* proceed without snapshot — recovery will be weaker */ }

  let screens;
  try {
    const raw = await stitch.callTool('generate_variants', args);
    screens = raw?.outputComponents?.[0]?.design?.screens || [];
  } catch (err) {
    console.error(`⚠️ Connection error during variants: ${err.message}`);
    screens = [];
  }

  // Recovery: if no screens returned, poll for new screens via delta
  if (screens.length === 0) {
    console.error(`   Attempting delta recovery via list_screens...`);
    for (let attempt = 1; attempt <= 6; attempt++) {
      const waitSec = attempt <= 3 ? 30 : 60;
      console.error(`   Recovery attempt ${attempt}/6 — waiting ${waitSec}s...`);
      await new Promise(r => setTimeout(r, waitSec * 1000));
      try {
        const listAfter = await stitch.callTool('list_screens', { projectId });
        const allScreens = listAfter?.screens || [];
        const newScreens = allScreens.filter(s => {
          const id = extractScreenId(s);
          return id && !knownScreenIds.has(id);
        });
        if (newScreens.length > 0) {
          console.error(`   ✅ Found ${newScreens.length} new screen(s) via recovery.`);
          // Fetch full data for each new screen
          for (const s of newScreens) {
            const sid = extractScreenId(s);
            try {
              const full = await stitch.callTool('get_screen', {
                projectId, screenId: sid,
                name: `projects/${projectId}/screens/${sid}`,
              });
              screens.push(full);
            } catch { /* skip unreachable screens */ }
          }
          if (screens.length > 0) break;
        }
      } catch (pollErr) {
        console.error(`   Recovery poll failed: ${pollErr.message}`);
      }
    }
  }
  if (screens.length === 0) die('No variants in API response and recovery failed. The operation may still be processing — check stitch.withgoogle.com.');

  const runDir = await makeRunDir('variants', prompt);
  const allArtifacts = [];
  const variants = [];

  for (let i = 0; i < screens.length; i++) {
    const s = screens[i];
    const vid = extractScreenId(s);
    const arts = await saveScreenArtifacts(runDir, s, i);
    allArtifacts.push(...arts);
    const rawUrl = resolveUrl(s.screenshot);
    variants.push({
      index: i + 1,
      screenId: vid,
      title: s.title,
      screenshotUrl: rawUrl ? rawUrl + HIRES_SUFFIX : null,
    });
  }

  await saveResult(runDir, {
    projectId, originalScreenId: screenId, prompt, variantOptions,
    variants: variants.map(v => ({ ...v })),
    timestamp: new Date().toISOString(),
  });
  allArtifacts.push('result.json');

  if (variants.length > 0) {
    await saveLatest(projectId, variants[0].screenId, 'variants');
  }

  // For variants, --name applies to the first variant only. Others need manual naming.
  const named = variants.length > 0 ? await autoName(projectId, variants[0].screenId, flags.name, flags.force) : null;

  // Emit event
  const varRunDirName = runDir.split('/').pop();
  const vgId = makeVariantGroupId();
  await appendEvent(projectId, {
    op: 'variants',
    screenIds: variants.map(v => v.screenId),
    parentScreenId: screenId,
    variantGroupId: vgId,
    ...(named ? { alias: named } : {}),
    promptPreview: promptPreview(prompt),
    runDir: varRunDirName,
  });

  ok({ projectId, originalScreenId: screenId, prompt, variantCount: variants.length, runDir, variants, artifacts: allArtifacts, ...(named ? { alias: named } : {}) });
  console.error(`✅ ${variants.length} variants generated`);
  console.error(`📁 Artifacts: ${runDir}`);
}

async function cmdExport(screenId, flags) {
  if (!screenId) die('Usage: export <screen-id> [--project <id>]');
  const projectId = await resolveProjectId(flags);

  const raw = await stitch.callTool('get_screen', {
    projectId, screenId, name: `projects/${projectId}/screens/${screenId}`,
  });

  const runDir = await makeRunDir('export', screenId);
  const artifacts = await saveScreenArtifacts(runDir, raw);

  await saveResult(runDir, {
    projectId, screenId, title: raw.title,
    timestamp: new Date().toISOString(),
  });
  artifacts.push('result.json');

  ok({ projectId, screenId, runDir, artifacts });
  console.error(`✅ Export: ${runDir}`);
}

async function cmdHtml(screenId, flags) {
  if (!screenId) die('Usage: html <screen-id> [--project <id>]');
  const projectId = await resolveProjectId(flags);

  const raw = await stitch.callTool('get_screen', {
    projectId, screenId, name: `projects/${projectId}/screens/${screenId}`,
  });

  const htmlUrl = resolveUrl(raw.htmlCode);
  if (!htmlUrl) die('No HTML code in screen data');
  const runDir = await makeRunDir('html', screenId);
  await downloadFile(htmlUrl, join(runDir, 'screen.html'), { expectImage: false });

  ok({ projectId, screenId, runDir, artifacts: ['screen.html'] });
  console.error(`✅ HTML saved: ${runDir}/screen.html`);
}

async function cmdImage(screenId, flags) {
  if (!screenId) die('Usage: image <screen-id> [--project <id>]');
  const projectId = await resolveProjectId(flags);

  const raw = await stitch.callTool('get_screen', {
    projectId, screenId, name: `projects/${projectId}/screens/${screenId}`,
  });

  const imgUrl = resolveUrl(raw.screenshot);
  if (!imgUrl) die('No screenshot in screen data');
  const runDir = await makeRunDir('image', screenId);
  await downloadFile(imgUrl, join(runDir, 'screen.png'));

  ok({ projectId, screenId, runDir, artifacts: ['screen.png'] });
  console.error(`✅ Image saved: ${runDir}/screen.png`);
}

// --- Name Commands ---

async function cmdName(alias, screenId, flags) {
  if (!alias || !screenId) die('Usage: name <alias> <screen-id> [--project <id>] [--note "..."] [--force]');
  const projectId = await resolveProjectId(flags);
  const slug = await setName(projectId, alias, screenId, { note: flags.note, force: !!flags.force });
  ok({ projectId, alias: slug, screenId });
  console.error(`✅ Named: ${slug} → ${screenId}`);
}

async function cmdUnname(alias, flags) {
  if (!alias) die('Usage: unname <alias> [--project <id>]');
  const projectId = await resolveProjectId(flags);
  const slug = await removeName(projectId, alias);
  ok({ projectId, removed: slug });
  console.error(`✅ Removed alias: ${slug}`);
}

async function cmdRename(oldAlias, newAlias, flags) {
  if (!oldAlias || !newAlias) die('Usage: rename <old-alias> <new-alias> [--project <id>]');
  const projectId = await resolveProjectId(flags);
  const result = await renameName(projectId, oldAlias, newAlias);
  ok({ projectId, ...result });
  console.error(`✅ Renamed: ${result.from} → ${result.to}`);
}

async function cmdResolve(alias, flags) {
  if (!alias) die('Usage: resolve <alias> [--project <id>]');
  const projectId = await resolveProjectId(flags);
  const entry = await resolveName(projectId, alias);
  if (!entry) die(`Alias "${alias}" not found in project ${projectId}.`);
  ok({ projectId, alias, ...entry });
}

async function cmdNames(flags) {
  const projectId = await resolveProjectId(flags);
  const names = await listNames(projectId);
  const entries = Object.entries(names);

  if (flags.verify) {
    // Verify each alias against the Stitch API
    console.error(`🔍 Verifying ${entries.length} aliases against Stitch API...`);
    const results = [];
    for (const [alias, entry] of entries) {
      try {
        await stitch.callTool('get_screen', {
          projectId, screenId: entry.screenId,
          name: `projects/${projectId}/screens/${entry.screenId}`,
        });
        results.push({ alias, screenId: entry.screenId, status: 'ok' });
      } catch {
        results.push({ alias, screenId: entry.screenId, status: 'broken' });
        console.error(`   ⚠️ ${alias} → ${entry.screenId}: BROKEN (screen not found)`);
      }
    }
    ok({ projectId, count: results.length, screens: results });
  } else {
    ok({
      projectId,
      count: entries.length,
      screens: entries.map(([alias, e]) => ({
        alias, screenId: e.screenId, updatedAt: e.updatedAt, ...(e.note ? { note: e.note } : {}),
      })),
    });
  }
}

async function cmdShow(ref, flags) {
  if (!ref) die('Usage: show <alias|screenId> [--project <id>]');
  const projectId = await resolveProjectId(flags);

  // Try alias first, then treat as raw screen ID
  const entry = await resolveName(projectId, ref);
  const screenId = entry ? entry.screenId : ref;
  const alias = entry ? ref : null;

  let screen;
  try {
    screen = await stitch.callTool('get_screen', {
      projectId, screenId,
      name: `projects/${projectId}/screens/${screenId}`,
    });
  } catch (err) {
    if (alias) {
      die(`Alias "${alias}" exists (screen ${screenId}), but the screen was not found in Stitch. It may have been deleted. Use "unname ${alias}" to clean up.`);
    } else {
      die(`Screen "${ref}" not found in project ${projectId}.`);
    }
  }

  const imgUrl = resolveUrl(screen.screenshot);
  const hiresUrl = imgUrl ? imgUrl + HIRES_SUFFIX : null;

  // Verify the screenshot URL is live (CDN tokens expire). Use a HEAD request
  // to avoid downloading the full PNG just for validation.
  let screenshotUrl = hiresUrl;
  let screenshotReady = true;
  if (hiresUrl) {
    const result = await checkScreenshotUrl(hiresUrl, {
      projectId,
      screenId,
      getScreen: async ({ projectId: pid, screenId: sid }) => stitch.callTool('get_screen', {
        projectId: pid, screenId: sid, name: `projects/${pid}/screens/${sid}`,
      }),
      resolveUrl,
    });
    if (result.alive) {
      screenshotUrl = result.freshUrl;
    } else {
      screenshotUrl = null;
      screenshotReady = false;
      console.error(`⚠️ Screenshot URL is expired and could not be refreshed. screenshotReady: false`);
    }
  }

  ok({
    projectId,
    ...(alias ? { alias } : {}),
    screenId,
    title: screen.title,
    ...(entry?.updatedAt ? { updatedAt: entry.updatedAt } : {}),
    screenshotUrl,
    screenshotReady,
    ...(entry?.note ? { note: entry.note } : {}),
  });
  const label = alias ? `${alias} → ${screenId}` : screenId;
  console.error(`✅ ${label} (${screen.title || 'untitled'})`);
}

// --- History / Lineage / Rebuild commands ---

async function cmdHistory(alias, flags) {
  if (!alias) die('Usage: history <alias> [--project <id>]');
  const projectId = await resolveProjectId(flags);

  // Check if --rev N was passed
  const rev = flags.rev ? parseInt(flags.rev, 10) : null;

  if (rev !== null) {
    // Get specific revision (alias_set events)
    const revisions = await aliasRevisions(projectId, alias);
    if (revisions.length === 0) die(`No revisions found for alias "${alias}".`);
    if (rev < 1 || rev > revisions.length) die(`Revision ${rev} out of range (1-${revisions.length}).`);
    const target = revisions[rev - 1];
    ok({ projectId, alias, revision: rev, totalRevisions: revisions.length, event: target });
  } else {
    // Get full history
    const events = await historyForAlias(projectId, alias);
    if (events.length === 0) die(`No events found for alias "${alias}".`);
    ok({ projectId, alias, totalEvents: events.length, events });
  }
}

async function cmdLineage(screenIdOrAlias, flags) {
  if (!screenIdOrAlias) die('Usage: lineage <screen-id|alias> [--project <id>]');
  const projectId = await resolveProjectId(flags);

  // Try resolving as alias first
  let screenId = screenIdOrAlias;
  try {
    const entry = await resolveName(projectId, screenIdOrAlias);
    if (entry) screenId = entry.screenId;
  } catch {
    // Not a valid alias slug, treat as raw screenId
  }

  const chain = await lineage(projectId, screenId);
  if (chain.length === 0) {
    ok({ projectId, screenId, lineage: [], note: 'No lineage events found. Screen may predate event logging.' });
    return;
  }

  ok({
    projectId,
    screenId,
    depth: chain.length,
    lineage: chain.map(e => ({
      op: e.op,
      screenId: e.screenId || (e.screenIds ? e.screenIds[0] : null),
      parentScreenId: e.parentScreenId || null,
      promptPreview: e.promptPreview || null,
      ts: e.ts,
      alias: e.alias || null,
    })),
  });
}

async function cmdRebuild(flags) {
  const projectId = await resolveProjectId(flags);
  if (!projectId) die('Usage: rebuild --project <id>');

  // Load existing names as base (preserves pre-event-log aliases)
  const existing = await loadNames(projectId);
  const rebuilt = await rebuildNames(projectId, existing);
  const { saveNames: doSave } = await import('./names.mjs');
  await doSave(projectId, rebuilt);

  const count = Object.keys(rebuilt.names).length;
  ok({ projectId, rebuiltAliases: count, names: rebuilt.names });
  console.error(`✅ Rebuilt ${count} aliases from event log.`);
}

/** Inherit deviceType from an existing screen via get_screen API call */
async function inheritDeviceType(projectId, screenId) {
  try {
    const screenData = await stitch.callTool('get_screen', {
      projectId, screenId,
      name: `projects/${projectId}/screens/${screenId}`,
    });
    const device = screenData?.screen?.deviceType || screenData?.deviceType;
    const validDevices = ['DESKTOP', 'MOBILE', 'TABLET', 'AGNOSTIC'];
    if (device && validDevices.includes(device)) return device;
  } catch (err) {
    console.error(`⚠️ Could not inherit deviceType from ${screenId}: ${err.message || err}`);
  }
  return null;
}



/** Auto-name helper: called after generate/edit/variants if --name is provided */
async function autoName(projectId, screenId, alias, force) {
  if (!alias) return null;
  try {
    const slug = await setName(projectId, alias, screenId, { force });
    console.error(`📌 Named: ${slug} → ${screenId}`);
    return slug;
  } catch (err) {
    console.error(`⚠️ Auto-name failed: ${err.message}`);
    return null;
  }
}

// --- Main ---

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.error(`Usage: stitch.mjs <command> [args] [--flags]

Commands:
  projects                          List all projects
  create "title"                    Create a new project
  info <project-id>                 Show project details + screens
  generate <project-id> "prompt"    Generate a new screen
  edit <screen-id> "prompt"         Edit an existing screen
  variants <screen-id> "prompt"     Generate design variants
  html <screen-id>                  Download HTML code
  image <screen-id>                 Download screenshot
  export <screen-id>                Download HTML + screenshot

  Screen Names (Alias Registry):
  name <alias> <screen-id>          Name a screen (e.g. name concept-a abc123)
  unname <alias>                    Remove an alias
  rename <old> <new>                Rename an alias
  resolve <alias>                   Resolve alias to screen ID
  names                             List all named screens
  names --verify                    List + verify against Stitch API
  show <alias|screenId>             Show screen details via alias or screen ID
  history <alias>                   Show event history for an alias
  history <alias> --rev N           Show Nth alias revision
  lineage <screen-id|alias>         Walk the edit/variant DAG backwards
  rebuild                           Rebuild names.json from event log

Flags:
  --device desktop|mobile|tablet|agnostic  Device type (default: desktop for generate; inherited for edit/variants)
  --model pro|flash                 Model (default: SDK default)
  --project <id>                    Project ID (auto from latest-screen.json)
  --count 1-5                       Number of variants (default: 3)
  --range refine|explore|reimagine  Creative range (default: explore)
  --aspects layout,color_scheme     Variant aspects to change
  --name <alias>                    Auto-name screen after generate/edit/variants
  --note "text"                     Add a note when naming
  --force                           Overwrite existing alias
  --design-system <name>            Append design-systems/<name>.md to prompt`);
    process.exit(1);
  }

  const command = args[0];
  const { flags, positional } = parseArgs(args.slice(1));

  try {
    switch (command) {
      case 'projects': return await cmdProjects();
      case 'create': return await cmdCreate(positional[0]);
      case 'info': return await cmdInfo(positional[0]);
      case 'generate': return await cmdGenerate(positional[0], positional[1], flags);
      case 'edit': return await cmdEdit(positional[0], positional[1], flags);
      case 'variants': return await cmdVariants(positional[0], positional[1], flags);
      case 'html': return await cmdHtml(positional[0], flags);
      case 'image': return await cmdImage(positional[0], flags);
      case 'export': return await cmdExport(positional[0], flags);
      case 'name': return await cmdName(positional[0], positional[1], flags);
      case 'unname': return await cmdUnname(positional[0], flags);
      case 'rename': return await cmdRename(positional[0], positional[1], flags);
      case 'resolve': return await cmdResolve(positional[0], flags);
      case 'names': return await cmdNames(flags);
      case 'show': return await cmdShow(positional[0], flags);
      case 'history': return await cmdHistory(positional[0], flags);
      case 'lineage': return await cmdLineage(positional[0], flags);
      case 'rebuild': return await cmdRebuild(flags);
      default: die(`Unknown command: ${command}`);
    }
  } catch (err) {
    if (err.code || err.status) {
      die(`Stitch API: ${err.message}`);
    }
    throw err;
  } finally {
    await cleanup();
  }
}

main();
