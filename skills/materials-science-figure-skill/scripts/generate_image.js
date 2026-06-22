#!/usr/bin/env node

const fs = require("fs");
const path = require("path");
const { URL } = require("url");

const OFFICIAL_BASE_URL = "https://generativelanguage.googleapis.com";
const OFFICIAL_HOSTNAME = "generativelanguage.googleapis.com";
const DEFAULT_MODEL = process.env.NANOBANANA_MODEL || "gemini-3.1-flash-image-preview";
const DEFAULT_TIMEOUT = Number(process.env.NANOBANANA_TIMEOUT || "120");

function loadMaterialsFigureTemplates() {
  const templatePath = path.join(__dirname, "..", "references", "materials-science-figure-templates.json");
  return JSON.parse(fs.readFileSync(templatePath, "utf8"));
}

function parseArgs(argv) {
  const args = {
    prompt: "",
    promptFile: "",
    materialsFigure: "",
    lang: "en",
    styleNote: "",
    inputImages: [],
    outDir: "./output/nanobanana",
    prefix: "nanobanana",
    baseUrl: process.env.NANOBANANA_BASE_URL || "",
    model: DEFAULT_MODEL,
    apiKey: process.env.NANOBANANA_API_KEY || "",
    apiKeyFile: process.env.NANOBANANA_API_KEY_FILE || "",
    aspectRatio: "",
    imageSize: "",
    textOnly: false,
    includeThoughts: false,
    thinkingLevel: "",
    timeout: DEFAULT_TIMEOUT,
    printPrompt: false,
    allowThirdParty: false,
  };

  const parts = [...argv];
  if (parts.length === 0) {
    throw new Error("Usage: node scripts/generate_image.js [\"prompt\"] [--prompt-file file.md] [--input-image file.png]");
  }

  if (!parts[0].startsWith("--")) {
    args.prompt = parts.shift();
  }
  while (parts.length > 0) {
    const key = parts.shift();
    if (key === "--text-only") {
      args.textOnly = true;
      continue;
    }
    if (key === "--include-thoughts") {
      args.includeThoughts = true;
      continue;
    }
    if (key === "--print-prompt") {
      args.printPrompt = true;
      continue;
    }
    if (key === "--allow-third-party") {
      args.allowThirdParty = true;
      continue;
    }

    const value = parts.shift();
    if (!value) {
      throw new Error(`Missing value for ${key}`);
    }

    switch (key) {
      case "--input-image":
        args.inputImages.push(value);
        break;
      case "--materials-figure":
        args.materialsFigure = value;
        break;
      case "--prompt-file":
        args.promptFile = value;
        break;
      case "--lang":
        args.lang = value;
        break;
      case "--style-note":
        args.styleNote = value;
        break;
      case "--out-dir":
        args.outDir = value;
        break;
      case "--prefix":
        args.prefix = value;
        break;
      case "--base-url":
        args.baseUrl = value;
        break;
      case "--model":
        args.model = value;
        break;
      case "--api-key":
        args.apiKey = value;
        break;
      case "--api-key-file":
        args.apiKeyFile = value;
        break;
      case "--aspect-ratio":
        args.aspectRatio = value;
        break;
      case "--image-size":
        args.imageSize = value;
        break;
      case "--thinking-level":
        args.thinkingLevel = value;
        break;
      case "--timeout":
        args.timeout = Number(value);
        break;
      default:
        throw new Error(`Unknown argument: ${key}`);
    }
  }

  return args;
}

function imagePathToPart(imagePath) {
  if (!fs.existsSync(imagePath)) {
    throw new Error(`Input image not found: ${imagePath}`);
  }
  const ext = path.extname(imagePath).toLowerCase();
  const mimeType = ext === ".jpg" || ext === ".jpeg"
    ? "image/jpeg"
    : ext === ".webp"
      ? "image/webp"
      : "image/png";

  return {
    inlineData: {
      mimeType,
      data: fs.readFileSync(imagePath).toString("base64"),
    },
  };
}

function resolveBaseUrl(args) {
  if (!args.baseUrl) {
    throw new Error(
      `Missing base URL. Set NANOBANANA_BASE_URL or pass --base-url explicitly. Official Google example: ${OFFICIAL_BASE_URL}`,
    );
  }

  let parsed;
  try {
    parsed = new URL(args.baseUrl);
  } catch {
    throw new Error(`Invalid base URL: ${args.baseUrl}. Use an explicit https URL such as ${OFFICIAL_BASE_URL}.`);
  }

  if (parsed.protocol !== "https:") {
    throw new Error(`Invalid base URL: ${args.baseUrl}. Use an explicit https URL such as ${OFFICIAL_BASE_URL}.`);
  }

  return args.baseUrl.replace(/\/$/, "");
}

function assertEndpointAllowed(baseUrl, args) {
  const hostname = new URL(baseUrl).hostname;
  const allowThirdParty = args.allowThirdParty || process.env.NANOBANANA_ALLOW_THIRD_PARTY === "1";
  if (hostname !== OFFICIAL_HOSTNAME && !allowThirdParty) {
    throw new Error(
      "Refusing to send API keys or user-provided files to a third-party Gemini-compatible provider. " +
      "If you intend to use a non-official endpoint, set NANOBANANA_ALLOW_THIRD_PARTY=1 or pass --allow-third-party. " +
      `Official Google endpoint: ${OFFICIAL_BASE_URL}`,
    );
  }
}

function loadInputImages(imagePaths) {
  return imagePaths.map(imagePathToPart);
}

function resolvePrompt(args) {
  let rawPrompt = args.prompt;
  if (args.promptFile) {
    if (!fs.existsSync(args.promptFile)) {
      throw new Error(`Prompt file not found: ${args.promptFile}`);
    }
    rawPrompt = fs.readFileSync(args.promptFile, "utf8");
  }

  if (args.materialsFigure) {
    const subtype = loadMaterialsFigureTemplates()[args.materialsFigure];
    if (!subtype) {
      throw new Error(`Unknown materials figure subtype: ${args.materialsFigure}`);
    }
    if (!rawPrompt) {
      throw new Error("Provide scientific background as the positional prompt when using --materials-figure.");
    }
    let prompt = subtype[args.lang].replace("{background}", rawPrompt.trim());
    if (args.styleNote) {
      prompt += `\n\nAdditional Style Requirement:\n${args.styleNote}`;
    }
    return prompt;
  }

  if (!rawPrompt) {
    throw new Error("Missing prompt.");
  }
  return rawPrompt;
}

function resolveApiKey(args) {
  if (args.apiKey) {
    return args.apiKey;
  }
  if (args.apiKeyFile) {
    if (!fs.existsSync(args.apiKeyFile)) {
      throw new Error(`API key file not found: ${args.apiKeyFile}`);
    }
    return fs.readFileSync(args.apiKeyFile, "utf8").trim();
  }
  throw new Error("Missing API key. Set NANOBANANA_API_KEY, NANOBANANA_API_KEY_FILE, or pass --api-key.");
}

function buildPayload(args) {
  const parts = [{ text: resolvePrompt(args) }, ...loadInputImages(args.inputImages)];
  const payload = {
    contents: [
      {
        parts,
      },
    ],
    generationConfig: {
      responseModalities: args.textOnly ? ["TEXT"] : ["TEXT", "IMAGE"],
    },
  };

  if (args.aspectRatio || args.imageSize) {
    payload.generationConfig.imageConfig = {};
    if (args.aspectRatio) {
      payload.generationConfig.imageConfig.aspectRatio = args.aspectRatio;
    }
    if (args.imageSize) {
      payload.generationConfig.imageConfig.imageSize = args.imageSize;
    }
  }

  if (args.thinkingLevel || args.includeThoughts) {
    payload.generationConfig.thinkingConfig = {};
    if (args.thinkingLevel) {
      payload.generationConfig.thinkingConfig.thinkingLevel = args.thinkingLevel;
    }
    if (args.includeThoughts) {
      payload.generationConfig.thinkingConfig.includeThoughts = true;
    }
  }

  return payload;
}

async function requestJson(args) {
  const baseUrl = resolveBaseUrl(args);
  assertEndpointAllowed(baseUrl, args);
  const apiKey = resolveApiKey(args);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), args.timeout * 1000);

  try {
    const response = await fetch(
      `${baseUrl}/v1beta/models/${args.model}:generateContent`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-goog-api-key": apiKey,
        },
        body: JSON.stringify(buildPayload(args)),
        signal: controller.signal,
      },
    );

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`Request failed with HTTP ${response.status}: ${text}`);
    }
    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

function mimeToExt(mimeType) {
  if (!mimeType) return ".png";
  if (mimeType.includes("jpeg")) return ".jpg";
  if (mimeType.includes("webp")) return ".webp";
  return ".png";
}

function saveOutputs(json, args) {
  const candidates = json.candidates || [];
  if (!candidates.length || !candidates[0].content || !Array.isArray(candidates[0].content.parts)) {
    throw new Error(`Unexpected response shape: ${JSON.stringify(json)}`);
  }

  fs.mkdirSync(args.outDir, { recursive: true });
  let imageIndex = 0;
  let textIndex = 0;

  for (const part of candidates[0].content.parts) {
    if (part.text) {
      textIndex += 1;
      const filePath = path.join(args.outDir, `${args.prefix}-text-${textIndex}.txt`);
      fs.writeFileSync(filePath, part.text, "utf8");
      console.log(filePath);
      continue;
    }

    const inlineData = part.inlineData || part.inline_data;
    if (!inlineData || !inlineData.data) {
      continue;
    }

    imageIndex += 1;
    const filePath = path.join(
      args.outDir,
      `${args.prefix}-${imageIndex}${mimeToExt(inlineData.mimeType || inlineData.mime_type)}`,
    );
    fs.writeFileSync(filePath, Buffer.from(inlineData.data, "base64"));
    console.log(filePath);
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.printPrompt) {
    process.stdout.write(`${resolvePrompt(args)}\n`);
    return;
  }
  const json = await requestJson(args);
  saveOutputs(json, args);
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
