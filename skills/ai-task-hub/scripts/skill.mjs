#!/usr/bin/env node

import { basename } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { AGENT_TASK_DEFAULT_BASE_URL, resolveAgentTaskAuth } from './agent-task-auth.mjs';
import { normalizeExecutePayload } from './attachment-normalize.mjs';
import { emitTelemetry, extractRequestContext } from './telemetry.mjs';

const ACTIONS = {
  'portal.skill.execute': { method: 'POST' },
  'portal.skill.poll': { method: 'GET' },
  'portal.skill.presentation': { method: 'GET' }
};

const IMAGE_CAPABILITIES = new Set([
  'human_detect',
  'image_tagging',
  'face-detect',
  'person-detect',
  'hand-detect',
  'body-keypoints-2d',
  'body-contour-63pt',
  'face-keypoints-106pt',
  'head-pose',
  'face-feature-classification',
  'face-action-classification',
  'face-image-quality',
  'face-emotion-recognition',
  'face-physical-attributes',
  'face-social-attributes',
  'political-figure-recognition',
  'designated-person-recognition',
  'exhibit-image-recognition',
  'person-instance-segmentation',
  'person-semantic-segmentation',
  'concert-cutout',
  'full-body-matting',
  'head-matting',
  'product-cutout'
]);
const NON_VISUAL_SERVICE_IDS = new Set([
  'svc_cf_tts_report',
  'svc_cf_embeddings',
  'svc_cf_reranker',
  'svc_cf_asr',
  'svc_cf_tts_low_cost',
  'svc_cf_markdown_convert'
]);
const GUIDANCE_ASSET_PRIORITY = ['overlay', 'cutout', 'mask'];

export async function runSkillAction(params = {}, options = {}) {
  const fetchImpl = options.fetchImpl ?? fetch;
  const emitStderr = options.emitStderr ?? defaultEmitStderr;
  const resolveAgentTaskAuthImpl = options.resolveAgentTaskAuthImpl ?? resolveAgentTaskAuth;
  const normalizeExecutePayloadImpl = options.normalizeExecutePayloadImpl ?? normalizeExecutePayload;
  const emitTelemetryImpl = options.emitTelemetryImpl ?? emitTelemetry;

  const action = typeof params.action === 'string' ? params.action.trim() : '';
  if (!ACTIONS[action]) {
    return createLocalResult(400, 'VALIDATION_BAD_REQUEST', `unsupported action: ${action || '<empty>'}`);
  }

  const payload = toObject(params.payload);

  let auth;
  try {
    auth = await resolveAgentTaskAuthImpl({
      explicitAgentTaskToken: params.explicitAgentTaskToken,
      baseUrl: params.baseUrl
    });
  } catch (error) {
    return createLocalResult(
      Number.isFinite(error?.status) ? error.status : 401,
      typeof error?.code === 'string' ? error.code : 'AUTH_UNAUTHORIZED',
      asMessage(error)
    );
  }

  let request;
  try {
    request = await buildActionRequest(action, payload, normalizeExecutePayloadImpl);
  } catch (error) {
    return createLocalResult(
      Number.isFinite(error?.status) ? error.status : 400,
      typeof error?.code === 'string' ? error.code : 'VALIDATION_BAD_REQUEST',
      asMessage(error),
      error?.details
    );
  }

  const capability = action === 'portal.skill.execute' ? readText(request.body?.capability) : null;
  const runIdHint =
    action === 'portal.skill.poll' || action === 'portal.skill.presentation'
      ? resolveOptionalIdentifier(payload, ['run_id', 'runId'])
      : null;

  if (action === 'portal.skill.execute') {
    void emitTelemetryImpl({
      eventName: 'agent.execute.start',
      status: 'ok',
      capability: capability ?? undefined
    });
  } else if (action === 'portal.skill.poll') {
    void emitTelemetryImpl({
      eventName: 'agent.poll.start',
      status: 'ok',
      runId: runIdHint ?? undefined
    });
  }

  const response = await fetchImpl(`${auth.baseUrl}${request.path}`, {
    method: request.method,
    headers: {
      'X-Agent-Task-Token': auth.agentTaskToken,
      ...(request.method === 'POST' ? { 'Content-Type': 'application/json' } : {})
    },
    ...(request.body !== undefined ? { body: JSON.stringify(request.body) } : {})
  });

  const body = await response.text();
  const parsed = parseJson(body);
  let apiError = response.ok ? null : parseApiError(parsed, body, response.status);

  if (response.ok) {
    emitStderr({
      event: 'portal_action_success',
      action,
      status: response.status
    });
  } else {
    apiError = parseApiError(parsed, body, response.status);
    emitStderr({
      event: 'portal_action_failed',
      action,
      status: response.status,
      code: apiError.code,
      message: apiError.message,
      request_id: apiError.requestId
    });

    if (apiError.code === 'POINTS_INSUFFICIENT') {
      const rechargeUrl =
        parsed &&
        typeof parsed === 'object' &&
        parsed.error &&
        typeof parsed.error === 'object' &&
        parsed.error.details &&
        typeof parsed.error.details === 'object' &&
        typeof parsed.error.details.recharge_url === 'string'
          ? parsed.error.details.recharge_url
          : null;

      emitStderr({
        event: 'portal_action_recharge_hint',
        action,
        recharge_url: rechargeUrl,
        recommended_next_action: rechargeUrl ? 'open recharge_url' : 'contact host recharge entry'
      });
    }
  }

  const context = extractRequestContext(body);
  if (action === 'portal.skill.execute') {
    const actionApiError = response.ok ? null : parseApiError(parsed, body, response.status);
    void emitTelemetryImpl({
      eventName: response.ok ? 'agent.execute.success' : 'agent.execute.failed',
      status: response.ok ? 'ok' : 'error',
      capability: capability ?? undefined,
      runId: context.runId ?? undefined,
      requestId: context.requestId ?? actionApiError?.requestId ?? undefined,
      properties: response.ok
        ? {}
        : {
            code: actionApiError?.code,
            message: actionApiError?.message
          }
    });
  } else if (action === 'portal.skill.poll') {
    const actionApiError = response.ok ? null : parseApiError(parsed, body, response.status);
    void emitTelemetryImpl({
      eventName: response.ok ? 'agent.poll.terminal' : 'agent.poll.failed',
      status: response.ok ? 'ok' : 'error',
      runId: context.runId ?? runIdHint ?? undefined,
      requestId: context.requestId ?? actionApiError?.requestId ?? undefined,
      properties: response.ok
        ? {
            run_status: context.status
          }
        : {
            code: actionApiError?.code,
            message: actionApiError?.message
          }
    });
  }

  const responseBody = buildGuidedResponseBody({
    action,
    request,
    ok: response.ok,
    parsed,
    body
  });

  return {
    ok: response.ok,
    status: response.status,
    body: responseBody
  };
}

async function buildActionRequest(action, payload, normalizeExecutePayloadImpl) {
  switch (action) {
    case 'portal.skill.execute': {
      const normalized = await normalizeExecutePayloadImpl(payload);

      const capability = readRequiredString(normalized.capability, 'capability is required');
      const input = toObject(normalized.input);
      if (Object.keys(input).length === 0) {
        throw createActionError(400, 'VALIDATION_BAD_REQUEST', 'input must be an object');
      }

      const body = {
        capability,
        input
      };

      const requestId = typeof normalized.request_id === 'string' ? normalized.request_id.trim() : '';
      if (requestId) {
        body.request_id = requestId;
      }

      return {
        method: 'POST',
        path: '/agent/skill/execute',
        body
      };
    }
    case 'portal.skill.poll': {
      const runId = resolveIdentifier(payload, ['run_id', 'runId'], 'run_id is required');
      return {
        method: 'GET',
        path: `/agent/skill/runs/${encodeURIComponent(runId)}`
      };
    }
    case 'portal.skill.presentation': {
      const runId = resolveIdentifier(payload, ['run_id', 'runId'], 'run_id is required');
      const includeFiles = payload.include_files === undefined ? true : payload.include_files;
      return {
        method: 'GET',
        path: buildPathWithQuery(`/agent/skill/runs/${encodeURIComponent(runId)}/presentation`, {
          channel: payload.channel,
          include_files: includeFiles
        })
      };
    }
    default:
      throw createActionError(400, 'VALIDATION_BAD_REQUEST', `unsupported action: ${action}`);
  }
}

function buildPathWithQuery(path, query) {
  const entries = Object.entries(query).filter((entry) => {
    const value = entry[1];
    return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean';
  });
  if (entries.length === 0) {
    return path;
  }
  const search = new URLSearchParams();
  for (const [key, value] of entries) {
    search.set(key, String(value));
  }
  return `${path}?${search.toString()}`;
}

function readRequiredString(value, message) {
  if (typeof value !== 'string' || !value.trim()) {
    throw createActionError(400, 'VALIDATION_BAD_REQUEST', message);
  }
  return value.trim();
}

function resolveIdentifier(payload, keys, message) {
  for (const key of keys) {
    const value = payload[key];
    if (typeof value === 'string' && value.trim()) {
      return value.trim();
    }
  }
  throw createActionError(400, 'VALIDATION_BAD_REQUEST', message);
}

function resolveOptionalIdentifier(payload, keys) {
  for (const key of keys) {
    const value = payload[key];
    if (typeof value === 'string' && value.trim()) {
      return value.trim();
    }
  }
  return null;
}

function readText(value) {
  if (typeof value !== 'string') {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function createActionError(status, code, message, details) {
  const error = new Error(message);
  error.status = status;
  error.code = code;
  error.details = details;
  return error;
}

function createLocalResult(status, code, message, details = undefined) {
  const body = JSON.stringify({
    request_id: '',
    data: null,
    error: {
      code,
      message,
      ...(details ? { details } : {})
    }
  });

  return {
    ok: false,
    status,
    body
  };
}

function parseApiError(parsed, body, status) {
  const requestId = typeof parsed?.request_id === 'string' ? parsed.request_id : null;
  const error = parsed?.error;
  if (error && typeof error === 'object') {
    return {
      code: typeof error.code === 'string' ? error.code : `HTTP_${status}`,
      message: typeof error.message === 'string' ? error.message : body,
      requestId
    };
  }

  return {
    code: `HTTP_${status}`,
    message: body,
    requestId
  };
}

function parseJson(body) {
  try {
    const parsed = JSON.parse(body);
    return parsed && typeof parsed === 'object' ? parsed : null;
  } catch {
    return null;
  }
}

function buildGuidedResponseBody({ action, request, ok, parsed, body }) {
  if (!ok || !parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
    return body;
  }

  const data = toObject(parsed.data);
  if (Object.keys(data).length === 0) {
    return body;
  }

  const guidance = buildAgentGuidance(action, request, data);
  if (!guidance) {
    return body;
  }

  const currentGuidance = toObject(data.agent_guidance);
  const enriched = {
    ...parsed,
    data: {
      ...data,
      agent_guidance: {
        ...currentGuidance,
        ...guidance
      }
    }
  };

  return JSON.stringify(enriched);
}

function buildAgentGuidance(action, request, data) {
  if (action === 'portal.skill.execute') {
    return buildExecuteGuidance(request, data);
  }
  if (action === 'portal.skill.poll') {
    return buildPollGuidance(data);
  }
  if (action === 'portal.skill.presentation') {
    return buildPresentationGuidance(data);
  }
  return null;
}

function buildExecuteGuidance(request, data) {
  const capability = readText(request?.body?.capability);
  if (!capability || !IMAGE_CAPABILITIES.has(capability)) {
    return null;
  }

  const runId = resolveOptionalIdentifier(data, ['run_id', 'runId']);
  return {
    visualization: createVisualizationGuidance({
      runId,
      capability,
      source: 'execute'
    })
  };
}

function buildPollGuidance(data) {
  const runId = resolveOptionalIdentifier(data, ['run_id', 'runId']);
  const serviceId = readText(data.service_id);
  const output = data.output;
  const geometry = summarizeGeometry(output);

  if (!isLikelyVisualService(serviceId) && !hasAnyGeometry(geometry)) {
    return null;
  }

  return {
    visualization: createVisualizationGuidance({
      runId,
      serviceId,
      geometry,
      source: 'poll'
    })
  };
}

function buildPresentationGuidance(data) {
  const runId = resolveOptionalIdentifier(data, ['run_id', 'runId']);
  const serviceId = readText(data.service_id);
  const visual = toObject(data.visual);
  const spec = toObject(visual.spec);
  const geometry = summarizeGeometry(spec.layers ?? spec);
  const assets = summarizePresentationAssets(visual);

  if (!hasAnyGeometry(geometry) && !assets.available && !isLikelyVisualService(serviceId)) {
    return null;
  }

  return {
    visualization: createVisualizationGuidance({
      runId,
      serviceId,
      geometry,
      assets,
      source: 'presentation'
    })
  };
}

function createVisualizationGuidance({ runId, capability = null, serviceId = null, geometry = null, assets = null, source }) {
  const geometrySummary = geometry ?? { boxes: 0, points: 0, masks: 0 };
  const hasGeometry = hasAnyGeometry(geometrySummary);

  return {
    source,
    ...(runId ? { run_id: runId } : {}),
    ...(capability ? { capability } : {}),
    ...(serviceId ? { service_id: serviceId } : {}),
    flow: [
      {
        step: 'fetch_rendered_assets',
        action: 'portal.skill.presentation',
        payload: {
          ...(runId ? { run_id: runId } : {}),
          include_files: true
        }
      },
      {
        step: 'asset_priority',
        kinds: GUIDANCE_ASSET_PRIORITY
      },
      {
        step: 'manual_draw_fallback',
        coordinate_space: 'pixel',
        origin: 'top_left',
        bbox_fields: ['xmin', 'ymin', 'xmax', 'ymax'],
        point_fields: ['x', 'y'],
        score_fields: ['score', 'confidence'],
        default_min_score: 0.3
      }
    ],
    detected_geometry: {
      boxes: geometrySummary.boxes,
      points: geometrySummary.points,
      masks: geometrySummary.masks,
      manual_primitives: resolveManualPrimitives(geometrySummary)
    },
    ...(assets?.available
      ? {
          rendered_assets: assets.byKind
        }
      : {}),
    can_render_manually: hasGeometry
  };
}

function summarizePresentationAssets(visual) {
  const files = toObject(visual.files);
  const assetRows = Array.isArray(files.assets) ? files.assets : [];
  const byKind = {};

  for (const row of assetRows) {
    const asset = toObject(row);
    const kind = readText(asset.kind);
    const url = readText(asset.url);
    if (!kind || !url) {
      continue;
    }
    if (!Array.isArray(byKind[kind])) {
      byKind[kind] = [];
    }
    byKind[kind].push(url);
  }

  return {
    available: Object.keys(byKind).length > 0,
    byKind
  };
}

function summarizeGeometry(input) {
  const summary = {
    boxes: 0,
    points: 0,
    masks: 0
  };
  visitGeometry(input, summary, 0);
  return summary;
}

function visitGeometry(value, summary, depth) {
  if (depth > 8 || value === null || value === undefined) {
    return;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      visitGeometry(item, summary, depth + 1);
    }
    return;
  }

  if (typeof value !== 'object') {
    return;
  }

  const record = value;
  if (isBoxRecord(record)) {
    summary.boxes += 1;
  }
  if (isPointRecord(record)) {
    summary.points += 1;
  }
  if (isMaskRecord(record)) {
    summary.masks += 1;
  }

  for (const nested of Object.values(record)) {
    visitGeometry(nested, summary, depth + 1);
  }
}

function isBoxRecord(record) {
  return (
    (hasFinite(record, 'xmin') && hasFinite(record, 'ymin') && hasFinite(record, 'xmax') && hasFinite(record, 'ymax')) ||
    (hasFinite(record, 'x') && hasFinite(record, 'y') && hasFinite(record, 'width') && hasFinite(record, 'height'))
  );
}

function isPointRecord(record) {
  if (!hasFinite(record, 'x') || !hasFinite(record, 'y')) {
    return false;
  }
  return !('width' in record || 'height' in record || 'xmin' in record || 'xmax' in record || 'ymin' in record || 'ymax' in record);
}

function isMaskRecord(record) {
  const kind = readText(record.kind);
  if (kind === 'mask' || kind === 'segmentation' || kind === 'confidence') {
    return true;
  }
  const dataUrl = readText(record.data_url);
  return typeof dataUrl === 'string' && dataUrl.startsWith('data:image/');
}

function hasFinite(record, key) {
  return typeof record[key] === 'number' && Number.isFinite(record[key]);
}

function hasAnyGeometry(geometry) {
  return geometry.boxes > 0 || geometry.points > 0 || geometry.masks > 0;
}

function resolveManualPrimitives(geometry) {
  const primitives = [];
  if (geometry.boxes > 0) {
    primitives.push('bbox_xyxy');
  }
  if (geometry.points > 0) {
    primitives.push('keypoint_xy');
  }
  if (geometry.masks > 0) {
    primitives.push('mask_alpha');
  }
  return primitives;
}

function isLikelyVisualService(serviceId) {
  return Boolean(serviceId) && !NON_VISUAL_SERVICE_IDS.has(serviceId);
}

function toObject(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {};
  }
  return { ...value };
}

function defaultEmitStderr(event) {
  process.stderr.write(`${JSON.stringify(event)}\n`);
}

function asMessage(error) {
  return error instanceof Error ? error.message : String(error);
}

function parseCliArgs(args) {
  if (args.length === 0) {
    return {
      explicitAgentTaskToken: '',
      action: 'portal.skill.execute',
      payloadJson: '{}',
      baseUrl: AGENT_TASK_DEFAULT_BASE_URL
    };
  }

  const first = args[0] ?? '';
  const firstLooksLikeAction = Boolean(ACTIONS[first]);

  if (firstLooksLikeAction) {
    return {
      explicitAgentTaskToken: '',
      action: first,
      payloadJson: args[1] ?? '{}',
      baseUrl: args[2] ?? AGENT_TASK_DEFAULT_BASE_URL
    };
  }

  return {
    explicitAgentTaskToken: first,
    action: args[1] ?? 'portal.skill.execute',
    payloadJson: args[2] ?? '{}',
    baseUrl: args[3] ?? AGENT_TASK_DEFAULT_BASE_URL
  };
}

async function main() {
  const parsed = parseCliArgs(process.argv.slice(2));

  let payload;
  try {
    payload = JSON.parse(parsed.payloadJson);
  } catch {
    const result = createLocalResult(400, 'VALIDATION_BAD_REQUEST', 'payload_json must be valid JSON object');
    process.stdout.write(`${result.body}\n`);
    process.exit(1);
  }

  const result = await runSkillAction({
    explicitAgentTaskToken: parsed.explicitAgentTaskToken,
    action: parsed.action,
    payload,
    baseUrl: parsed.baseUrl
  });

  process.stdout.write(`${result.body}\n`);
  if (!result.ok) {
    process.exit(1);
  }
}

const importedScriptName = basename(fileURLToPath(import.meta.url));
const invokedScriptName = process.argv[1] ? basename(process.argv[1]) : '';

if (
  process.argv[1] &&
  (import.meta.url === pathToFileURL(process.argv[1]).href || invokedScriptName === importedScriptName)
) {
  await main();
}
