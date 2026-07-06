#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named["business-id"] || !named["task-type"] || !named.payload) {
  console.error('Usage: create-a2a-task.mjs --business-id <id> --task-type <type> --payload \'{"key":"val"}\'');
  process.exit(2);
}

const body = {
  business_id: named["business-id"],
  task_type: named["task-type"],
  payload: JSON.parse(named.payload),
};

const data = await tmrFetch("POST", "/a2a/task", body);
console.log(JSON.stringify(data, null, 2));
