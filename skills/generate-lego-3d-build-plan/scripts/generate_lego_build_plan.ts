#!/usr/bin/env node

const ENDPOINT = "https://agent.deepnlp.org/agent_router";
const UNIQUE_ID = "craftsman-agent/craftsman-agent";
const API_ID = "generate_lego_build_plan";
const ENV_KEY = "DEEPNLP_ONEKEY_ROUTER_ACCESS";
const ONEKEY_HEADER = "X-OneKey";

function validateImageUrls(urls: string[]) {
  for (const url of urls) {
    try {
      const parsed = new URL(url);
      if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
        throw new Error(`Invalid ref image URL scheme: ${url}`);
      }
    } catch (err) {
      throw new Error(`Invalid ref image URL: ${url}`);
    }
  }
}

function parseArgs(argv: string[]) {
  const args: Record<string, string | string[]> = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--prompt" || token === "--mode" || token === "--images") {
      const value = argv[i + 1];
      i += 1;
      if (token === "--images") {
        const list = (args[token] as string[]) || [];
        list.push(value);
        args[token] = list;
      } else {
        args[token] = value;
      }
    }
  }

  return {
    prompt: (args["--prompt"] as string) || "",
    mode: (args["--mode"] as string) || "basic",
    images: (args["--images"] as string[]) || [],
  };
}

async function main() {
  const { prompt, mode, images } = parseArgs(process.argv.slice(2));
  if (!prompt) {
    console.error("Missing --prompt");
    process.exit(1);
  }

  let apiKey = process.env[ENV_KEY];
  if (!apiKey) {
    console.error("DEEPNLP_ONEKEY_ROUTER_ACCESS is not set. Set it before running.");
    console.error("Set with: export DEEPNLP_ONEKEY_ROUTER_ACCESS=YOUR_API_KEY");
    apiKey = "";
  }

  const url = new URL(ENDPOINT);
  validateImageUrls(images);

  const payload = {
    unique_id: UNIQUE_ID,
    api_id: API_ID,
    data: {
      prompt: prompt,
      images: images,
      mode,
    },
  };

  const response = await fetch(url.toString(), {
    method: "POST",
    headers: { "Content-Type": "application/json", [ONEKEY_HEADER]: apiKey },
    body: JSON.stringify(payload),
  });

  const text = await response.text();
  if (!response.ok) {
    console.error(`HTTP ${response.status}: ${text}`);
    process.exit(1);
  }

  try {
    const json = JSON.parse(text);
    console.log(JSON.stringify(json, null, 2));
  } catch {
    console.log(text);
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
