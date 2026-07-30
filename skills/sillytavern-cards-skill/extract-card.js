#!/usr/bin/env node

// SillyTavern Character Card Extractor
// Reads TavernAI V1/V2/V3 character data from PNG tEXt chunks
// Usage: node extract-card.js <path-to-png-or-json>

const fs = require("fs");
const path = require("path");

function extractPngTextChunks(buffer) {
  const chunks = [];
  // PNG signature is 8 bytes
  let offset = 8;

  while (offset < buffer.length) {
    const length = buffer.readUInt32BE(offset);
    const type = buffer.toString("ascii", offset + 4, offset + 8);
    const data = buffer.subarray(offset + 8, offset + 8 + length);
    // Skip CRC (4 bytes)
    offset += 12 + length;

    if (type === "tEXt") {
      const nullIndex = data.indexOf(0x00);
      if (nullIndex !== -1) {
        const keyword = data.toString("ascii", 0, nullIndex);
        const value = data.toString("ascii", nullIndex + 1);
        chunks.push({ keyword, value });
      }
    }
  }

  return chunks;
}

function decodeCardData(base64String) {
  const json = Buffer.from(base64String, "base64").toString("utf-8");
  return JSON.parse(json);
}

function normalizeCard(raw) {
  // V2/V3: has spec wrapper
  if (raw.spec === "chara_card_v2" || raw.spec === "chara_card_v3") {
    return raw;
  }

  // V1: raw fields at top level, wrap in V2 envelope
  if (raw.name && raw.description && raw.first_mes) {
    return {
      spec: "chara_card_v2",
      spec_version: "2.0",
      data: {
        name: raw.name,
        description: raw.description,
        personality: raw.personality || "",
        scenario: raw.scenario || "",
        first_mes: raw.first_mes,
        mes_example: raw.mes_example || "",
        system_prompt: "",
        post_history_instructions: "",
        alternate_greetings: [],
        tags: [],
        creator: "",
        creator_notes: "",
        character_version: "",
        character_book: null,
        extensions: {},
      },
    };
  }

  throw new Error("Unrecognized character card format");
}

function extractFromPng(filePath) {
  const buffer = fs.readFileSync(filePath);

  // Verify PNG signature
  const pngSignature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
  if (buffer.subarray(0, 8).compare(pngSignature) !== 0) {
    throw new Error("Not a valid PNG file");
  }

  const textChunks = extractPngTextChunks(buffer);

  // Prefer V3 (ccv3 chunk) over V2 (chara chunk)
  const v3Chunk = textChunks.find((c) => c.keyword === "ccv3");
  if (v3Chunk) {
    const data = decodeCardData(v3Chunk.value);
    return normalizeCard(data);
  }

  const charaChunk = textChunks.find((c) => c.keyword === "chara");
  if (charaChunk) {
    const data = decodeCardData(charaChunk.value);
    return normalizeCard(data);
  }

  throw new Error(
    'No character data found in PNG. Expected tEXt chunk with keyword "chara" or "ccv3".'
  );
}

function extractFromJson(filePath) {
  const content = fs.readFileSync(filePath, "utf-8");
  const data = JSON.parse(content);
  return normalizeCard(data);
}

// Main
const filePath = process.argv[2];
if (!filePath) {
  console.error("Usage: node extract-card.js <path-to-png-or-json>");
  process.exit(1);
}

if (!fs.existsSync(filePath)) {
  console.error(`File not found: ${filePath}`);
  process.exit(1);
}

const ext = path.extname(filePath).toLowerCase();

try {
  let card;
  if (ext === ".json") {
    card = extractFromJson(filePath);
  } else if (ext === ".png" || ext === ".webp") {
    card = extractFromPng(filePath);
  } else {
    // Try PNG first, fall back to JSON
    try {
      card = extractFromPng(filePath);
    } catch {
      card = extractFromJson(filePath);
    }
  }

  console.log(JSON.stringify(card, null, 2));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
