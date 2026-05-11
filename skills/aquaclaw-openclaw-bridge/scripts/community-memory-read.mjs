#!/usr/bin/env node

import process from 'node:process';
import { pathToFileURL } from 'node:url';

import {
  DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE,
  listCommunityMemoryNotes,
  loadCommunityMemoryIndex,
  loadCommunityMemoryState,
  resolveCommunityMemoryPaths,
} from './community-memory-common.mjs';
import { formatTimestamp, parseArgValue, parsePositiveInt } from './hosted-aqua-common.mjs';

const VALID_FORMATS = new Set(['json', 'markdown']);
const VALID_VIEWS = new Set(['full', 'brief']);
export const DEFAULT_COMMUNITY_MEMORY_BRIEF_LIMIT = 3;

function printHelp() {
  console.log(`Usage: community-memory-read.mjs [options]

Options:
  --workspace-root <path>        OpenClaw workspace root
  --config-path <path>           Hosted Aqua config path
  --community-memory-dir <path>  Local community-memory root override
  --limit <n>                    Local page size (default: ${DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE})
  --cursor <id>                  Continue after the given note id
  --venue-slug <slug>            Filter by venue slug
  --tag <tag>                    Filter by tag
  --format <fmt>                 json|markdown (default: markdown)
  --view <view>                  full|brief (default: full)
  --help                         Show this message

Notes:
  - This command reads the local profile-scoped community-memory mirror only.
  - It never calls live Aqua APIs.
`);
}

export function parseOptions(argv) {
  const options = {
    communityMemoryDir: process.env.AQUACLAW_COMMUNITY_MEMORY_DIR || null,
    configPath: process.env.AQUACLAW_HOSTED_CONFIG || null,
    cursor: null,
    format: 'markdown',
    limit: Number.parseInt(process.env.AQUACLAW_COMMUNITY_MEMORY_READ_LIMIT || String(DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE), 10),
    tag: null,
    venueSlug: null,
    view: 'full',
    workspaceRoot: process.env.OPENCLAW_WORKSPACE_ROOT || null,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];

    if (arg === '--help') {
      printHelp();
      process.exit(0);
    }
    if (arg.startsWith('--workspace-root')) {
      options.workspaceRoot = parseArgValue(argv, index, arg, '--workspace-root').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--config-path')) {
      options.configPath = parseArgValue(argv, index, arg, '--config-path').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--community-memory-dir')) {
      options.communityMemoryDir = parseArgValue(argv, index, arg, '--community-memory-dir').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--limit')) {
      options.limit = parsePositiveInt(parseArgValue(argv, index, arg, '--limit'), '--limit');
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--cursor')) {
      options.cursor = parseArgValue(argv, index, arg, '--cursor').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--venue-slug')) {
      options.venueSlug = parseArgValue(argv, index, arg, '--venue-slug').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--tag')) {
      options.tag = parseArgValue(argv, index, arg, '--tag').trim();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--format')) {
      options.format = parseArgValue(argv, index, arg, '--format').trim().toLowerCase();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    if (arg.startsWith('--view')) {
      options.view = parseArgValue(argv, index, arg, '--view').trim().toLowerCase();
      if (!arg.includes('=')) {
        index += 1;
      }
      continue;
    }
    throw new Error(`unknown option: ${arg}`);
  }

  if (!VALID_FORMATS.has(options.format)) {
    throw new Error('--format must be json or markdown');
  }
  if (!VALID_VIEWS.has(options.view)) {
    throw new Error('--view must be full or brief');
  }

  return options;
}

function formatNoteMarkdown(note) {
  const lines = [
    `- ${formatTimestamp(note.createdAt)} | ${note.npcId ?? 'unknown'} | ${note.venueSlug ?? 'no-venue'}`,
    `  ${note.summary || '(no summary)'}`,
  ];

  if (note.body) {
    lines.push(`  ${note.body}`);
  }
  if (note.tags.length > 0) {
    lines.push(`  tags: ${note.tags.join(', ')}`);
  }
  lines.push(`  mention: ${note.mentionPolicy ?? 'n/a'} | freshness: ${note.freshnessScore ?? 'n/a'}`);
  return lines.join('\n');
}

function formatReadResultMarkdown(result) {
  const lines = [
    'Local community memory.',
    `- Root: ${result.paths.communityMemoryRoot}`,
    `- Profile: ${result.paths.profileId ?? 'legacy'}`,
    `- Last sync: ${formatTimestamp(result.state.lastSyncedAt)}`,
    `- Total notes: ${result.state.totalKnownNotes}`,
    `- Full backfill complete: ${result.state.fullBackfillCompletedAt ? 'yes' : 'no'}`,
    `- Returned items: ${result.page.items.length}`,
  ];

  if (result.page.nextCursor) {
    lines.push(`- Next cursor: ${result.page.nextCursor}`);
  }
  if (result.page.items.length > 0) {
    lines.push('');
    lines.push(...result.page.items.map((note) => formatNoteMarkdown(note)));
  }

  return lines.join('\n');
}

export function summarizeCommunityMemoryNoteForBrief(note) {
  const mentionPolicy = note?.mentionPolicy ?? 'n/a';
  const summary = typeof note?.summary === 'string' ? note.summary.trim() : '';
  const summaryVisible = mentionPolicy !== 'private_only' && summary.length > 0;

  return {
    id: note?.id ?? null,
    createdAt: note?.createdAt ?? null,
    npcId: note?.npcId ?? null,
    venueSlug: note?.venueSlug ?? null,
    tags: Array.isArray(note?.tags) ? [...note.tags] : [],
    mentionPolicy,
    freshnessScore: note?.freshnessScore ?? null,
    summary: summaryVisible ? summary : null,
    summaryVisible,
    redactionReason: mentionPolicy === 'private_only' ? 'private_only' : summaryVisible ? null : 'missing_summary',
  };
}

export function summarizeCommunityMemoryForBrief(result) {
  return {
    mode: 'brief',
    scope: 'local_profile_mirror',
    paths: {
      communityMemoryRoot: result.paths.communityMemoryRoot,
      profileId: result.paths.profileId ?? 'legacy',
    },
    state: {
      lastSyncedAt: result.state.lastSyncedAt,
      totalKnownNotes: result.state.totalKnownNotes,
      fullBackfillCompletedAt: result.state.fullBackfillCompletedAt,
      returnedItems: result.page.items.length,
      nextCursor: result.page.nextCursor ?? null,
    },
    recoveredIndex: result.recoveredIndex,
    recoveredIndexReason: result.recoveredIndexReason,
    recoveredState: result.recoveredState,
    recoveredStateReason: result.recoveredStateReason,
    items: result.page.items.map((note) => summarizeCommunityMemoryNoteForBrief(note)),
  };
}

function formatBriefNoteMarkdown(note, index) {
  const lines = [
    `${index + 1}. [${formatTimestamp(note.createdAt)}] ${note.npcId ?? 'unknown'} | ${note.venueSlug ?? 'no-venue'}`,
  ];

  if (note.summaryVisible && note.summary) {
    lines.push(`   summary: ${note.summary}`);
  } else if (note.redactionReason === 'private_only') {
    lines.push('   summary: (private-only note retained locally)');
  } else {
    lines.push('   summary: (no sharable summary)');
  }
  if (note.tags.length > 0) {
    lines.push(`   tags: ${note.tags.join(', ')}`);
  }
  lines.push(`   mention: ${note.mentionPolicy} | freshness: ${note.freshnessScore ?? 'n/a'}`);
  return lines.join('\n');
}

export function formatCommunityMemoryBriefMarkdown(
  summary,
  {
    title = '## Community Memory',
  } = {},
) {
  const lines = [
    title,
    `- Profile: ${summary.paths.profileId ?? 'legacy'}`,
    `- Last sync: ${formatTimestamp(summary.state.lastSyncedAt)}`,
    `- Total notes: ${summary.state.totalKnownNotes}`,
    `- Notes shown: ${summary.state.returnedItems}`,
    `- Backfill complete: ${summary.state.fullBackfillCompletedAt ? 'yes' : 'no'}`,
    '- Scope: compact local inspection only; note bodies are omitted here.',
    '- Privacy rule: private_only notes stay redacted in this surface.',
  ];

  if (summary.recoveredState) {
    lines.push(`- State recovery: ${summary.recoveredStateReason ?? 'yes'}`);
  }
  if (summary.recoveredIndex) {
    lines.push(`- Index recovery: ${summary.recoveredIndexReason ?? 'yes'}`);
  }
  if (summary.state.nextCursor) {
    lines.push(`- Next cursor: ${summary.state.nextCursor}`);
  }
  if (summary.items.length > 0) {
    lines.push('');
    lines.push(...summary.items.map((note, index) => formatBriefNoteMarkdown(note, index)));
  } else {
    lines.push('');
    lines.push('- No local community memory notes yet.');
  }

  return lines.join('\n');
}

export async function readCommunityMemory({
  workspaceRoot = process.env.OPENCLAW_WORKSPACE_ROOT,
  configPath = process.env.AQUACLAW_HOSTED_CONFIG,
  communityMemoryDir = process.env.AQUACLAW_COMMUNITY_MEMORY_DIR,
  limit = DEFAULT_COMMUNITY_MEMORY_PAGE_SIZE,
  cursor = null,
  venueSlug = null,
  tag = null,
} = {}) {
  const paths = resolveCommunityMemoryPaths({
    workspaceRoot,
    configPath,
    communityMemoryDir,
  });
  const stateResult = await loadCommunityMemoryState(paths.statePath);
  const indexResult = await loadCommunityMemoryIndex(paths);
  const page = listCommunityMemoryNotes({
    index: indexResult.index,
    limit,
    cursor,
    venueSlug,
    tag,
  });

  return {
    paths,
    state: stateResult.state,
    recoveredIndex: indexResult.recovered,
    recoveredIndexReason: indexResult.recoveryReason,
    recoveredState: stateResult.recovered,
    recoveredStateReason: stateResult.recoveryReason,
    page,
  };
}

async function main(argv = process.argv.slice(2)) {
  const options = parseOptions(argv);
  const result = await readCommunityMemory(options);
  const payload = options.view === 'brief' ? summarizeCommunityMemoryForBrief(result) : result;
  if (options.format === 'json') {
    console.log(JSON.stringify(payload, null, 2));
    return;
  }
  console.log(
    options.view === 'brief'
      ? formatCommunityMemoryBriefMarkdown(payload)
      : formatReadResultMarkdown(result),
  );
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error instanceof Error ? error.message : String(error));
    process.exit(1);
  });
}
