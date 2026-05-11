#!/usr/bin/env node

import fs from 'node:fs';
import process from 'node:process';

export function formatEveryMs(everyMs) {
  if (!Number.isFinite(everyMs) || everyMs <= 0) {
    return null;
  }
  if (everyMs % 3600000 === 0) {
    return `${everyMs / 3600000}h`;
  }
  if (everyMs % 60000 === 0) {
    return `${everyMs / 60000}m`;
  }
  if (everyMs % 1000 === 0) {
    return `${everyMs / 1000}s`;
  }
  return `${everyMs}ms`;
}

export function summarizeCronJob(job, target) {
  const id = job.id ?? job.jobId ?? job._id ?? null;
  const enabled = typeof job.enabled === 'boolean'
    ? job.enabled
    : typeof job.disabled === 'boolean'
      ? !job.disabled
      : null;

  let schedule = job.every ?? job.cron ?? job.at ?? null;
  if (!schedule && job.schedule && typeof job.schedule === 'object') {
    if (job.schedule.kind === 'every') {
      schedule = formatEveryMs(job.schedule.everyMs) ?? 'every';
    } else if (typeof job.schedule.cron === 'string' && job.schedule.cron) {
      schedule = job.schedule.cron;
    } else if (typeof job.schedule.at === 'string' && job.schedule.at) {
      schedule = job.schedule.at;
    } else if (typeof job.schedule.kind === 'string' && job.schedule.kind) {
      schedule = job.schedule.kind;
    }
  }

  return {
    id,
    name: job.name ?? target,
    enabled,
    schedule,
    raw: job,
  };
}

export function findCronJobByName(input, target) {
  const jobs = Array.isArray(input?.jobs) ? input.jobs : [];
  const job = jobs.find((candidate) => candidate && candidate.name === target);
  if (!job) {
    return null;
  }

  return summarizeCronJob(job, target);
}

function main() {
  const target = process.env.NAME;
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  const summary = findCronJobByName(input, target);

  if (!summary) {
    process.exit(2);
  }

  process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
