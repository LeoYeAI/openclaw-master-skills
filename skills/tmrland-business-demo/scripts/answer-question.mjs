#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named.question || !named.zh || !named.en) {
  console.error('Usage: answer-question.mjs --question <id> --zh "答案..." --en "Answer..." [--direction bullish|bearish|neutral]');
  process.exit(2);
}

const body = {
  answer_text_zh: named.zh,
  answer_text_en: named.en,
};
if (named.direction) body.prediction_direction = named.direction;

const data = await tmrFetch("POST", `/apparatus/${named.question}/answers`, body);
console.log(JSON.stringify(data, null, 2));
