#!/usr/bin/env node

/**
 * GoPlus AgentGuard Trust CLI — lightweight wrapper for SkillRegistry operations.
 *
 * Usage:
 *   node trust-cli.ts lookup --id <id> --source <source> --version <version> --hash <hash>
 *   node trust-cli.ts attest  --id <id> --source <source> --version <version> --hash <hash> --trust-level <level> [--preset <preset>] [--capabilities <json>] [--reviewed-by <name>] [--notes <text>] [--expires <iso>] [--force]
 *   node trust-cli.ts revoke  [--source <source>] [--key <record_key>] --reason <reason>
 *   node trust-cli.ts list    [--trust-level <level>] [--status <status>] [--source-pattern <pattern>]
 *   node trust-cli.ts hash    --path <dir>
 */

import { createAgentGuard, CAPABILITY_PRESETS, SkillScanner } from '@goplus/agentguard';

const args = process.argv.slice(2);
const command = args[0];

function getArg(name: string): string | undefined {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1 || idx + 1 >= args.length) return undefined;
  return args[idx + 1];
}

function hasFlag(name: string): boolean {
  return args.includes(`--${name}`);
}

async function main() {
  const registryPath = getArg('registry-path');
  const { registry } = createAgentGuard({ registryPath });

  switch (command) {
    case 'lookup': {
      const skill = {
        id: getArg('id') || '',
        source: getArg('source') || '',
        version_ref: getArg('version') || '',
        artifact_hash: getArg('hash') || '',
      };
      const record = await registry.lookup(skill);
      console.log(JSON.stringify(record, null, 2));
      break;
    }

    case 'attest': {
      const skill = {
        id: getArg('id') || '',
        source: getArg('source') || '',
        version_ref: getArg('version') || '',
        artifact_hash: getArg('hash') || '',
      };
      const trustLevel = (getArg('trust-level') || 'restricted') as
        | 'untrusted'
        | 'restricted'
        | 'trusted';

      let capabilities;
      const preset = getArg('preset');
      if (preset && preset in CAPABILITY_PRESETS) {
        capabilities =
          CAPABILITY_PRESETS[preset as keyof typeof CAPABILITY_PRESETS];
      } else if (getArg('capabilities')) {
        capabilities = JSON.parse(getArg('capabilities')!);
      }

      const force = hasFlag('force');
      const attestFn = force ? registry.forceAttest : registry.attest;
      const result = await attestFn.call(registry, {
        skill,
        trust_level: trustLevel,
        capabilities,
        review: {
          reviewed_by: getArg('reviewed-by') || 'cli',
          reviewed_at: new Date().toISOString(),
          notes: getArg('notes') || '',
        },
        expires_at: getArg('expires'),
      });
      console.log(JSON.stringify(result, null, 2));
      break;
    }

    case 'revoke': {
      const source = getArg('source');
      const key = getArg('key');
      const reason = getArg('reason') || 'Revoked via CLI';
      const result = await registry.revoke(
        { source, record_key: key },
        reason
      );
      console.log(JSON.stringify(result, null, 2));
      break;
    }

    case 'list': {
      const filters: Record<string, string> = {};
      const trustLevel = getArg('trust-level');
      const status = getArg('status');
      const sourcePattern = getArg('source-pattern');
      if (trustLevel) filters.trust_level = trustLevel;
      if (status) filters.status = status;
      if (sourcePattern) filters.source_pattern = sourcePattern;

      const records = await registry.list(filters);
      console.log(JSON.stringify(records, null, 2));
      break;
    }

    case 'hash': {
      const dirPath = getArg('path');
      if (!dirPath) {
        console.error('Error: --path is required for hash');
        process.exit(1);
      }
      const scanner = new SkillScanner({ useExternalScanner: false });
      const hash = await scanner.calculateArtifactHash(dirPath);
      console.log(JSON.stringify({ hash }));
      break;
    }

    default:
      console.error(
        'Usage: trust-cli.ts <lookup|attest|revoke|list|hash> [options]'
      );
      console.error('Run with --help for details.');
      process.exit(1);
  }
}

main().catch((err) => {
  console.error(JSON.stringify({ error: err.message }));
  process.exit(1);
});
