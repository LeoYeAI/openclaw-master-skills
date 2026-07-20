import { createClient } from './client.js';
import { formatApiError, formatNetworkError, isApiSuccess } from './errors.js';
import { hasTaskOutput, normalizeBatchPhase, normalizeTaskCollection, normalizeTaskResult, toPhase } from './normalize.js';

export async function executeStatus(input, ctx, options) {
  const { outputKey, outputLabel, allowBatch = false } = options;
  const taskId = input.taskId || input['task-id'] || input.task_id;
  const batchId = input.batchId || input['batch-id'] || input.batch_id;

  if (!taskId && !(allowBatch && batchId)) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'VALIDATION',
      errorCategory: 'validation',
      errorTitle: 'Missing identifier',
      retryable: false,
      field: allowBatch && !taskId ? 'task_id|batch_id' : 'task_id',
      hint: allowBatch ? 'Provide either a task ID or a batch ID.' : 'Provide a task ID and retry.',
      errorMessage: allowBatch
        ? 'Either --task-id or --batch-id is required.'
        : 'The status script requires `--task-id <task-id>`.',
    };
  }

  const client = createClient(ctx);
  if (allowBatch && batchId) return queryBatch(client, batchId, { outputKey, outputLabel });
  return queryTask(client, taskId, { outputKey, outputLabel });
}

async function queryTask(client, taskId, options) {
  const { outputKey, outputLabel } = options;

  let res;
  try {
    res = await client.get(`/v1/generation/${taskId}/status`, { retries: 3 });
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(res)) {
    return formatApiError(res);
  }

  const task = normalizeTaskResult(res.data);
  const phase = toPhase(task.taskStatus);
  const missingOutputs = phase === 'completed' && !hasTaskOutput(task, outputKey);
  return {
    ok: phase !== 'failed' && !missingOutputs,
    phase: missingOutputs ? 'failed' : phase,
    batchId: null,
    taskIds: task.taskId ? [task.taskId] : [],
    taskId: task.taskId,
    taskStatus: task.taskStatus,
    [outputKey]: task[outputKey],
    lyrics: task.lyrics,
    coverUrl: task.coverUrl,
    balance: null,
    errorCode: phase === 'failed' || missingOutputs ? 'TASK_FAILED' : null,
    errorCategory: phase === 'failed' || missingOutputs ? 'task' : null,
    errorTitle: phase === 'failed'
      ? 'Task failed'
      : missingOutputs
        ? `Missing ${outputLabel} output`
        : null,
    retryable: phase === 'failed' || missingOutputs ? false : null,
    field: null,
    hint: phase === 'failed' || missingOutputs ? 'Check the task payload and existing task status before submitting a new job.' : null,
    errorMessage: missingOutputs
      ? `Task reached a completed state but returned no ${outputLabel} URLs.`
      : phase === 'failed'
        ? (task.msg || 'Task failed')
        : null,
  };
}

async function queryBatch(client, batchId, options) {
  const { outputKey, outputLabel } = options;

  let res;
  try {
    res = await client.get(`/v1/generation/batch/${batchId}/status`, { retries: 3 });
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(res)) {
    return formatApiError(res);
  }

  const tasks = normalizeTaskCollection(res.data);
  const phase = normalizeBatchPhase(tasks, { outputKey });

  return {
    ok: phase !== 'failed',
    phase,
    batchId,
    tasks,
    errorCode: phase === 'failed' ? 'TASK_FAILED' : null,
    errorCategory: phase === 'failed' ? 'task' : null,
    errorTitle: phase === 'failed' ? 'Batch failed' : null,
    retryable: phase === 'failed' ? false : null,
    field: null,
    hint: phase === 'failed' ? 'Inspect individual task states in the batch before retrying.' : null,
    errorMessage: phase === 'failed'
      ? `One or more tasks in the batch failed or returned no ${outputLabel} URLs.`
      : null,
  };
}
