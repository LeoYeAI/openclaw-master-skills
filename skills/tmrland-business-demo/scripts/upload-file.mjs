#!/usr/bin/env node
import { parseArgs } from "./_lib.mjs";
import { readFileSync } from "node:fs";
import { basename } from "node:path";

const API_KEY = (process.env.TMR_API_KEY ?? "").trim();
const BASE_URL = (process.env.TMR_BASE_URL ?? "https://tmrland.com/api/v1").replace(/\/$/, "");

const { help, positional } = parseArgs(process.argv);
if (help || !positional[0]) {
  console.error("Usage: upload-file.mjs <file-path>");
  process.exit(2);
}

const filePath = positional[0];
const fileName = basename(filePath);
const fileData = readFileSync(filePath);

const formData = new FormData();
formData.append("file", new Blob([fileData]), fileName);

const resp = await fetch(`${BASE_URL}/uploads/`, {
  method: "POST",
  headers: { "Authorization": `Bearer ${API_KEY}` },
  body: formData,
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  console.error(`API error ${resp.status}: ${text}`);
  process.exit(1);
}

const data = await resp.json();
console.log(JSON.stringify(data, null, 2));
