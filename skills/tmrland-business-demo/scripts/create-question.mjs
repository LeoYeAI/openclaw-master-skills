#!/usr/bin/env node
import { tmrFetch, parseArgs } from "./_lib.mjs";

const { help, named } = parseArgs(process.argv);
if (help || !named["title-zh"] || !named["title-en"] || !named.category || !named.type) {
  console.error('Usage: create-question.mjs --title-zh X --title-en Y --category Z --type prediction|opinion|demo [--desc-zh X] [--desc-en Y]');
  process.exit(2);
}

const body = {
  title_zh: named["title-zh"],
  title_en: named["title-en"],
  category: named.category,
  question_type: named.type,
};
if (named["desc-zh"]) body.description_zh = named["desc-zh"];
if (named["desc-en"]) body.description_en = named["desc-en"];

const data = await tmrFetch("POST", "/apparatus/", body);
console.log(JSON.stringify(data, null, 2));
