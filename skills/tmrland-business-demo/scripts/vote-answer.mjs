#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, positional, named } = parseArgs(process.argv);
if (help || !positional[0] || !named.direction) {
  console.error("Usage: vote-answer.mjs <answer-id> --direction like|dislike");
  process.exit(2);
}

const direction = named.direction;
if (direction !== "like" && direction !== "dislike") {
  console.error("Error: --direction must be 'like' or 'dislike'");
  process.exit(2);
}

const data = await tmrFetch("POST", `/apparatus/answers/${positional[0]}/${direction}`);
console.log(JSON.stringify(data, null, 2));
