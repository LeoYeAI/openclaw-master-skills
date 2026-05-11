#!/usr/bin/env node

import { pathToFileURL } from 'node:url';
import { getDefaultBaseUrl, isHttpBaseUrl, normalizeBaseUrl } from './base-url.mjs';

const DEFAULT_BASE_URL = getDefaultBaseUrl();

export const AGENT_TASK_DEFAULT_BASE_URL = DEFAULT_BASE_URL;

export async function resolveAgentTaskAuth(params = {}) {
  const explicitToken = readToken(params.explicitAgentTaskToken);
  const envToken = readToken(process.env.AGENT_TASK_TOKEN);
  const agentTaskToken = explicitToken || envToken;

  if (!agentTaskToken) {
    throw createAuthError(
      401,
      'AUTH_UNAUTHORIZED',
      'agent task token is required (pass [agent_task_token] CLI arg or set AGENT_TASK_TOKEN)'
    );
  }

  return {
    baseUrl: normalizeBaseUrl(params.baseUrl),
    agentTaskToken,
    source: explicitToken ? 'explicit' : 'env'
  };
}

function readToken(value) {
  if (typeof value !== 'string') {
    return '';
  }
  return value.trim();
}

function createAuthError(status, code, message) {
  const error = new Error(message);
  error.status = status;
  error.code = code;
  return error;
}

function parseCliArgs(args) {
  if (args.length === 0) {
    return {
      explicitAgentTaskToken: '',
      baseUrl: DEFAULT_BASE_URL
    };
  }

  const first = args[0] ?? '';
  if (isHttpBaseUrl(first)) {
    return {
      explicitAgentTaskToken: '',
      baseUrl: first
    };
  }

  return {
    explicitAgentTaskToken: first,
    baseUrl: args[1] ?? DEFAULT_BASE_URL
  };
}

async function main() {
  try {
    const auth = await resolveAgentTaskAuth(parseCliArgs(process.argv.slice(2)));
    console.log(
      JSON.stringify({
        base_url: auth.baseUrl,
        source: auth.source,
        agent_task_token_available: Boolean(auth.agentTaskToken)
      })
    );
  } catch (error) {
    const status = Number.isFinite(error?.status) ? error.status : 500;
    const code = typeof error?.code === 'string' ? error.code : 'SYSTEM_INTERNAL_ERROR';
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`${JSON.stringify({ event: 'agent_task_auth_failed', status, code, message })}\n`);
    process.exit(1);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
