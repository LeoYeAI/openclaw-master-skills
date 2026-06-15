#!/usr/bin/env node
import { resolve } from 'node:path';
import process from 'node:process';
import { listTextFiles } from '/opt/homebrew/lib/node_modules/clawhub/dist/skills.js';
import { apiRequestForm } from '/opt/homebrew/lib/node_modules/clawhub/dist/http.js';
import { ApiRoutes, ApiV1PublishResponseSchema } from '/opt/homebrew/lib/node_modules/clawhub/dist/schema/index.js';
import { requireAuthToken } from '/opt/homebrew/lib/node_modules/clawhub/dist/cli/authToken.js';
import { getRegistry, DEFAULT_REGISTRY, DEFAULT_SITE } from '/opt/homebrew/lib/node_modules/clawhub/dist/cli/registry.js';

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith('--')) continue;
    const key = arg.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      out[key] = 'true';
    } else {
      out[key] = next;
      i += 1;
    }
  }
  return out;
}

const args = parseArgs(process.argv.slice(2));
const skillDir = resolve(args.path || process.env.HOME + '/skills/team-dispatch');
const slug = args.slug || 'team-dispatch';
const displayName = args.name || 'Team Dispatch';
const version = args.version;
const changelog = args.changelog || '';
const tags = (args.tags || 'latest').split(',').map(s => s.trim()).filter(Boolean);

if (!version) {
  console.error('Missing required --version');
  process.exit(2);
}

const token = await requireAuthToken();
const registry = await getRegistry(
  {
    workdir: process.cwd(),
    registry: DEFAULT_REGISTRY,
    registrySource: 'default',
    site: DEFAULT_SITE,
    noInput: false,
  },
  { cache: true }
);

const filesOnDisk = await listTextFiles(skillDir);
if (!filesOnDisk.some(file => ['skill.md', 'skills.md'].includes(file.relPath.toLowerCase()))) {
  console.error('SKILL.md required');
  process.exit(3);
}

const form = new FormData();
form.set(
  'payload',
  JSON.stringify({
    slug,
    displayName,
    version,
    changelog,
    tags,
    acceptLicenseTerms: true,
  })
);

for (const file of filesOnDisk) {
  const blob = new Blob([Buffer.from(file.bytes)], { type: file.contentType ?? 'text/plain' });
  form.append('files', blob, file.relPath);
}

try {
  const result = await apiRequestForm(
    registry,
    { method: 'POST', path: ApiRoutes.skills, token, form },
    ApiV1PublishResponseSchema
  );

  console.log(JSON.stringify({
    ok: true,
    slug,
    version,
    skillId: result.skillId,
    versionId: result.versionId,
    embeddingId: result.embeddingId,
  }, null, 2));
} catch (error) {
  console.error(error?.message || String(error));
  process.exit(1);
}
