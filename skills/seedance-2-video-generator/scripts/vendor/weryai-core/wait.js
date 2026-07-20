import { log, sleep } from './client.js';
import { hasTaskOutput, normalizeBatchPhase, normalizeTaskCollection, normalizeTaskResult, toPhase } from './normalize.js';
import { isApiSuccess } from './errors.js';

export function resolvePollIntervalMs(ctx, elapsedMs, options = {}) {
  const configured = Number(ctx?.pollIntervalMs);
  if (Number.isFinite(configured) && configured >= 0) {
    return configured;
  }

  const profile = options.pollProfile || ctx?.pollProfile || 'standard';
  if (profile === 'fast') {
    if (elapsedMs < 30_000) return 2_000;
    if (elapsedMs < 120_000) return 4_000;
    return 6_000;
  }
  if (profile === 'slow') {
    if (elapsedMs < 30_000) return 6_000;
    if (elapsedMs < 120_000) return 10_000;
    return 15_000;
  }

  if (elapsedMs < 30_000) return 3_000;
  if (elapsedMs < 120_000) return 6_000;
  return 10_000;
}

export async function pollSubmittedTasks(client, options) {
  const { batchId, taskIds, allowBatch = false } = options;
  if (!Array.isArray(taskIds) || taskIds.length === 0) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'PROTOCOL',
      errorCategory: 'server',
      errorTitle: 'Unexpected API response',
      retryable: false,
      field: 'task_ids',
      hint: 'The API reported success but did not return task IDs. Inspect the raw response before retrying.',
      errorMessage: 'API returned success but no task_ids.',
    };
  }
  if (taskIds.length > 1) {
    return batchId && allowBatch
      ? pollBatch(client, options)
      : pollMultipleTasks(client, options);
  }
  return pollSingleTask(client, { ...options, taskId: taskIds[0] });
}

export async function pollSingleTask(client, options) {
  const { taskId, batchId = null, taskIds = taskId ? [taskId] : [], ctx, outputKey, outputLabel, pollProfile } = options;
  const start = Date.now();

  while (true) {
    const elapsed = Date.now() - start;
    if (elapsed >= ctx.pollTimeoutMs) {
      return {
        ok: false,
        phase: 'failed',
        batchId,
        taskIds,
        taskId,
        taskStatus: 'unknown',
        [outputKey]: null,
        errorCode: 'TIMEOUT',
        errorCategory: 'timeout',
        errorTitle: 'Polling timed out',
        retryable: true,
        field: null,
        hint: 'The task may still be running. Use the status command to inspect the existing task before submitting a new one.',
        errorMessage: `Poll timeout after ${Math.round(elapsed / 1000)}s.`,
      };
    }

    await sleep(resolvePollIntervalMs(ctx, elapsed, { pollProfile }));

    let res;
    try {
      res = await client.get(`/v1/generation/${taskId}/status`, { retries: 3 });
    } catch (err) {
      log(`Warning: poll query failed (${err.message}), will retry next interval.`);
      continue;
    }

    if (!isApiSuccess(res)) {
      log(`Warning: poll returned status ${res.status}, will retry next interval.`);
      continue;
    }

    const task = normalizeTaskResult(res.data);
    const phase = toPhase(task.taskStatus);
    const missingOutputs = phase === 'completed' && !hasTaskOutput(task, outputKey);
    const elapsedSec = Math.round((Date.now() - start) / 1000);
    log(`Polling ${taskId}... status: ${task.taskStatus} (${elapsedSec}s elapsed)`);

    if (phase === 'completed' || phase === 'failed') {
      return {
        ok: phase === 'completed' && !missingOutputs,
        phase: missingOutputs ? 'failed' : phase,
        batchId,
        taskIds,
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
        hint: phase === 'failed' || missingOutputs ? 'Check the existing task state and parameters before retrying.' : null,
        errorMessage: missingOutputs
          ? `Task reached a completed state but returned no ${outputLabel} URLs.`
          : phase === 'failed'
            ? (task.msg || 'Task failed')
            : null,
      };
    }
  }
}

export async function pollMultipleTasks(client, options) {
  const { taskIds, ctx, outputKey, outputLabel, pollProfile } = options;
  const start = Date.now();

  while (true) {
    const elapsed = Date.now() - start;
    if (elapsed >= ctx.pollTimeoutMs) {
      return {
        ok: false,
        phase: 'failed',
        batchId: null,
        taskIds,
        tasks: null,
        errorCode: 'TIMEOUT',
        errorCategory: 'timeout',
        errorTitle: 'Polling timed out',
        retryable: true,
        field: null,
        hint: 'The tasks may still be running. Inspect the existing task IDs before submitting a new batch.',
        errorMessage: `Poll timeout after ${Math.round(elapsed / 1000)}s.`,
      };
    }

    await sleep(resolvePollIntervalMs(ctx, elapsed, { pollProfile }));

    const tasks = [];
    let shouldRetry = false;

    for (const taskId of taskIds) {
      let res;
      try {
        res = await client.get(`/v1/generation/${taskId}/status`, { retries: 3 });
      } catch (err) {
        log(`Warning: poll query failed for ${taskId} (${err.message}), will retry next interval.`);
        shouldRetry = true;
        break;
      }

      if (!isApiSuccess(res)) {
        log(`Warning: poll returned status ${res.status} for ${taskId}, will retry next interval.`);
        shouldRetry = true;
        break;
      }

      tasks.push(normalizeTaskResult(res.data));
    }

    if (shouldRetry) {
      continue;
    }

    const phase = normalizeBatchPhase(tasks, { outputKey });
    const elapsedSec = Math.round((Date.now() - start) / 1000);
    const summary = tasks.map((task) => `${task.taskId}:${task.taskStatus}`).join(', ');
    log(`Polling tasks... [${summary}] (${elapsedSec}s elapsed)`);

    if (phase === 'completed' || phase === 'failed') {
      return {
        ok: phase === 'completed',
        phase,
        batchId: null,
        taskIds,
        tasks,
        errorCode: phase === 'failed' ? 'TASK_FAILED' : null,
        errorCategory: phase === 'failed' ? 'task' : null,
        errorTitle: phase === 'failed' ? 'Batch failed' : null,
        retryable: phase === 'failed' ? false : null,
        field: null,
        hint: phase === 'failed' ? `Inspect the existing batch and task statuses before retrying.` : null,
        errorMessage: phase === 'failed'
          ? `One or more tasks failed or returned no ${outputLabel} URLs.`
          : null,
      };
    }
  }
}

export async function pollBatch(client, options) {
  const { batchId, taskIds, ctx, outputKey, outputLabel, pollProfile } = options;
  const start = Date.now();

  while (true) {
    const elapsed = Date.now() - start;
    if (elapsed >= ctx.pollTimeoutMs) {
      return {
        ok: false,
        phase: 'failed',
        batchId,
        taskIds,
        tasks: null,
        errorCode: 'TIMEOUT',
        errorCategory: 'timeout',
        errorTitle: 'Polling timed out',
        retryable: true,
        field: null,
        hint: 'The batch may still be running. Inspect the existing batch before submitting a new one.',
        errorMessage: `Poll timeout after ${Math.round(elapsed / 1000)}s.`,
      };
    }

    await sleep(resolvePollIntervalMs(ctx, elapsed, { pollProfile }));

    let res;
    try {
      res = await client.get(`/v1/generation/batch/${batchId}/status`, { retries: 3 });
    } catch (err) {
      log(`Warning: batch poll failed (${err.message}), will retry next interval.`);
      continue;
    }

    if (!isApiSuccess(res)) {
      log(`Warning: batch poll returned status ${res.status}, will retry next interval.`);
      continue;
    }

    const tasks = normalizeTaskCollection(res.data);
    const phase = normalizeBatchPhase(tasks, { outputKey });
    const elapsedSec = Math.round((Date.now() - start) / 1000);
    const summary = tasks.map((task) => task.taskStatus).join(', ');
    log(`Polling batch ${batchId}... [${summary}] (${elapsedSec}s elapsed)`);

    if (phase === 'completed' || phase === 'failed') {
      return {
        ok: phase === 'completed',
        phase,
        batchId,
        taskIds,
        tasks,
        errorCode: phase === 'failed' ? 'TASK_FAILED' : null,
        errorCategory: phase === 'failed' ? 'task' : null,
        errorTitle: phase === 'failed' ? 'Batch failed' : null,
        retryable: phase === 'failed' ? false : null,
        field: null,
        hint: phase === 'failed' ? `Inspect the existing batch and task statuses before retrying.` : null,
        errorMessage: phase === 'failed'
          ? `One or more tasks in the batch failed or returned no ${outputLabel} URLs.`
          : null,
      };
    }
  }
}
