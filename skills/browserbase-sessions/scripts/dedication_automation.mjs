#!/usr/bin/env node

import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import "dotenv/config";
import { Stagehand } from "@browserbasehq/stagehand";

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

function usage() {
  return [
    "Usage:",
    "  node scripts/dedication_automation.mjs --dedication \"<what to say>\" [options]",
    "",
    "Required:",
    "  --dedication         Dedication theme/message for the song",
    "",
    "Recommended:",
    "  --chatgpt-url        Custom GPT URL for Suno Hitmaker",
    "  --session-id         Existing RUNNING Browserbase session id (preferred if already logged into Google)",
    "  --context-id         Browserbase context id with ChatGPT + Suno logged in",
    "",
    "Optional:",
    "  --to                 Recipient name",
    "  --from               Sender name",
    "  --mood               Mood guidance",
    "  --style              Style guidance",
    "  --lyrics-prompt      Override lyrics prompt (skip ChatGPT phase)",
    "  --style-prompt       Override style prompt (skip ChatGPT phase)",
    "  --negative-styles    Exclusions for Suno",
    "  --vocal-gender       male|female",
    "  --lyrics-mode        manual|auto",
    "  --bb-timeout-sec     Browserbase session timeout (default: 3600)",
    "  --output-json        Output summary path (default: /tmp/dedication-result-<ts>.json)",
    "  --keep-open          Keep browser session running at end",
    "  --verbose            Stagehand verbose logs",
    "",
    "Environment:",
    "  BROWSERBASE_API_KEY, BROWSERBASE_PROJECT_ID",
    "  BROWSERBASE_SESSION_ID (fallback for --session-id)",
    "  CHATGPT_HITMAKER_URL (fallback for --chatgpt-url)",
    "  OPENAI_API_KEY or STAGEHAND_MODEL_API_KEY (optional; placeholder is used when not invoking Stagehand LLM tools)",
  ].join("\n");
}

function required(value, name) {
  if (!value) throw new Error(`${name} is required.`);
  return value;
}

function nowStamp() {
  return new Date().toISOString().replace(/[:.]/g, "-");
}

async function sleep(page, ms) {
  await page.waitForTimeout(ms);
}

function toBool(value) {
  if (value === true) return true;
  if (!value) return false;
  return ["1", "true", "yes", "y", "on"].includes(String(value).toLowerCase());
}

function trimText(s, max = 6000) {
  if (!s) return "";
  return s.length > max ? `${s.slice(0, max)}...` : s;
}

function extractJsonObject(text) {
  if (!text) return null;

  const fence = text.match(/```json\s*([\s\S]*?)```/i) || text.match(/```\s*([\s\S]*?)```/i);
  if (fence && fence[1]) {
    try {
      return JSON.parse(fence[1].trim());
    } catch {}
  }

  const start = text.indexOf("{");
  if (start === -1) return null;
  let depth = 0;
  let inString = false;
  let escape = false;

  for (let i = start; i < text.length; i += 1) {
    const ch = text[i];
    if (escape) {
      escape = false;
      continue;
    }
    if (ch === "\\") {
      escape = true;
      continue;
    }
    if (ch === '"') {
      inString = !inString;
      continue;
    }
    if (inString) continue;
    if (ch === "{") depth += 1;
    if (ch === "}") {
      depth -= 1;
      if (depth === 0) {
        const candidate = text.slice(start, i + 1);
        try {
          return JSON.parse(candidate);
        } catch {
          return null;
        }
      }
    }
  }

  return null;
}

function buildFallbackSpec(args) {
  const to = args.to ? ` for ${args.to}` : "";
  const from = args.from ? ` from ${args.from}` : "";
  const mood = args.mood || "warm, emotional, modern pop";
  const style = args.style || "pop, cinematic, heartfelt";

  return {
    title: `Dedication${to}`.trim(),
    lyrics_prompt: `Write a dedication song${to}${from}. Theme: ${args.dedication}. Mood: ${mood}. Include a memorable chorus and vivid imagery.`,
    style_prompt: style,
    negative_styles: args["negative-styles"] || "",
    vocal_gender: (args["vocal-gender"] || "").toLowerCase(),
    lyrics_mode: (args["lyrics-mode"] || "manual").toLowerCase(),
  };
}

async function findVisibleSelector(page, selectors) {
  return page.evaluate((candidateSelectors) => {
    const isVisible = (el) => {
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    for (const selector of candidateSelectors) {
      const el = document.querySelector(selector);
      if (isVisible(el)) return selector;
    }
    return null;
  }, selectors);
}

async function waitForVisibleSelector(page, selectors, timeoutMs = 45000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const selector = await findVisibleSelector(page, selectors);
    if (selector) return selector;
    await sleep(page, 500);
  }
  return null;
}

async function clickByExactText(page, text) {
  return page.evaluate((targetText) => {
    const isVisible = (el) => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    const buttons = [...document.querySelectorAll("button")];
    const found = buttons.find((b) => isVisible(b) && (b.textContent || "").trim() === targetText);
    if (!found) return false;
    found.click();
    return true;
  }, text);
}

async function fillChatComposer(page, message) {
  return page.evaluate((promptText) => {
    const isVisible = (el) => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    const candidates = [
      document.querySelector("#prompt-textarea"),
      document.querySelector("textarea[placeholder*='Message']"),
      document.querySelector("textarea[data-testid='prompt-textarea']"),
      document.querySelector("div[contenteditable='true'][id='prompt-textarea']"),
      document.querySelector("div[contenteditable='true'][data-testid='composer-input']"),
    ].filter(Boolean);

    const el = candidates.find(isVisible);
    if (!el) return false;

    el.focus();
    if (el.tagName === "TEXTAREA") {
      el.value = promptText;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    }

    el.textContent = promptText;
    el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: promptText }));
    return true;
  }, message);
}

async function clickChatSend(page) {
  return page.evaluate(() => {
    const isVisible = (el) => {
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    const selectors = [
      "button[data-testid='send-button']",
      "button[aria-label*='Send']",
      "button[aria-label*='send']",
      "button[title*='Send']",
    ];

    for (const selector of selectors) {
      const btn = document.querySelector(selector);
      if (btn && !btn.disabled && isVisible(btn)) {
        btn.click();
        return true;
      }
    }

    return false;
  });
}

async function getLatestAssistantText(page) {
  return page.evaluate(() => {
    const pickText = (nodes) => {
      if (!nodes.length) return "";
      const node = nodes[nodes.length - 1];
      return (node.innerText || node.textContent || "").trim();
    };

    const direct = [...document.querySelectorAll("[data-message-author-role='assistant']")];
    if (direct.length) return pickText(direct);

    const roles = [...document.querySelectorAll("article")].filter((a) => {
      const txt = (a.getAttribute("data-message-author-role") || "").toLowerCase();
      return txt === "assistant";
    });
    if (roles.length) return pickText(roles);

    const markdownBlocks = [...document.querySelectorAll("main [data-testid^='conversation-turn-']")];
    return pickText(markdownBlocks);
  });
}

async function waitForChatResponse(page, timeoutMs = 180000) {
  const started = Date.now();
  let last = "";
  let stableCount = 0;

  while (Date.now() - started < timeoutMs) {
    const latest = await getLatestAssistantText(page);
    if (latest && latest.length > 60) {
      if (latest === last) {
        stableCount += 1;
      } else {
        stableCount = 0;
        last = latest;
      }

      if (stableCount >= 3) return latest;
    }
    await sleep(page, 2000);
  }

  return last;
}

async function detectSunoCaptcha(page) {
  return page.evaluate(() => {
    const isVisible = (el) => {
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const findCreate = () => {
      const exact = document.querySelector("button[aria-label='Create song']");
      if (exact) return exact;
      const byText = [...document.querySelectorAll("button")].find((b) => {
        if (!isVisible(b)) return false;
        const txt = (b.textContent || "").trim().toLowerCase();
        return txt === "create" || txt.includes("create");
      });
      return byText || null;
    };

    const bodyText = (document.body?.innerText || "").toLowerCase();
    const iframes = [...document.querySelectorAll("iframe")].map((f) => f.src || "");
    const hasHCaptcha = iframes.some((src) => /hcaptcha|newassets\.hcaptcha|js\.hcaptcha/.test(src));
    const hasWarmText =
      bodyText.includes("stay warm") ||
      bodyText.includes("click on objects used to stay warm") ||
      bodyText.includes("captcha");

    const creditsMatch = bodyText.match(/\b(\d+)\s+credits\b/i);
    const createBtn = findCreate();

    return {
      hasHCaptcha,
      hasWarmText,
      challengeVisible: hasHCaptcha || hasWarmText,
      credits: creditsMatch ? Number(creditsMatch[1]) : null,
      createDisabled: createBtn ? Boolean(createBtn.disabled) : null,
      createText: createBtn ? (createBtn.textContent || "").trim() : null,
    };
  });
}

async function waitForSunoCreateReady(page, timeoutMs = 90000) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const ready = await page.evaluate(() => {
      const isVisible = (el) => {
        if (!el) return false;
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
      };

      const hasCreateButton = [...document.querySelectorAll("button")].some((b) => {
        if (!isVisible(b)) return false;
        const txt = (b.textContent || "").trim().toLowerCase();
        const aria = (b.getAttribute("aria-label") || "").toLowerCase();
        return txt.includes("create") || aria.includes("create song");
      });

      const hasComposer = [...document.querySelectorAll("textarea")].some((t) => {
        if (!isVisible(t)) return false;
        const ph = (t.placeholder || "").toLowerCase();
        return ph.includes("lyrics") || ph.includes("write some lyrics") || ph.includes("styles");
      });

      return hasCreateButton && hasComposer;
    });

    if (ready) return true;
    await sleep(page, 1000);
  }
  return false;
}

async function fillSunoCustomForm(page, spec) {
  return page.evaluate((input) => {
    const isVisible = (el) => {
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };

    const setValue = (el, value) => {
      if (!el) return false;
      el.focus();
      el.value = value;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      return true;
    };

    const clickByText = (text) => {
      const needle = text.trim().toLowerCase();
      const buttons = [...document.querySelectorAll("button")];
      const btn = buttons.find((b) => {
        if (!isVisible(b)) return false;
        const value = (b.textContent || "").trim().toLowerCase();
        return value === needle || value.includes(needle);
      });
      if (!btn) return false;
      btn.click();
      return true;
    };

    clickByText("Custom");
    clickByText("Advanced");

    const visibleTextareas = [...document.querySelectorAll("textarea")].filter(isVisible);

    const lyrics = visibleTextareas
      .filter(isVisible)
      .find((el) => (el.placeholder || "").toLowerCase().includes("write some lyrics or a prompt"));

    const style = visibleTextareas.find((el) => {
      const placeholder = (el.placeholder || "").toLowerCase();
      return (
        placeholder.includes("infantil") ||
        placeholder.includes("styles") ||
        placeholder.includes("describe the sound")
      );
    });

    const fallbackLyrics = lyrics || visibleTextareas[0] || null;
    const fallbackStyle =
      style ||
      visibleTextareas.find((el) => el !== fallbackLyrics) ||
      null;

    const exclude = [...document.querySelectorAll("input")]
      .filter(isVisible)
      .find((el) => (el.placeholder || "").toLowerCase().includes("exclude styles"));

    const title = [...document.querySelectorAll("input")]
      .filter(isVisible)
      .find((el) => (el.placeholder || "").toLowerCase().includes("song title"));

    const lyricsSet = setValue(fallbackLyrics, input.lyrics_prompt || "");
    const styleSet = setValue(fallbackStyle, input.style_prompt || "");
    const excludeSet = input.negative_styles ? setValue(exclude, input.negative_styles) : false;
    const titleSet = input.title ? setValue(title, input.title) : false;

    if (input.vocal_gender === "male") clickByText("Male");
    if (input.vocal_gender === "female") clickByText("Female");
    if (input.lyrics_mode === "manual") clickByText("Manual");
    if (input.lyrics_mode === "auto") clickByText("Auto");

    return {
      lyricsSet,
      styleSet,
      excludeSet,
      titleSet,
      textareasVisible: visibleTextareas.length,
    };
  }, spec);
}

async function clickSunoCreate(page) {
  return page.evaluate(() => {
    const isVisible = (el) => {
      if (!el) return false;
      const rect = el.getBoundingClientRect();
      return rect.width > 0 && rect.height > 0;
    };
    const btn =
      document.querySelector("button[aria-label='Create song']") ||
      [...document.querySelectorAll("button")].find((b) => {
        if (!isVisible(b)) return false;
        const txt = (b.textContent || "").trim().toLowerCase();
        return txt === "create" || txt.includes("create");
      });
    if (!btn || btn.disabled) return false;
    btn.click();
    return true;
  });
}

async function waitForCaptchaClear(page, maxWaitMs, captchaEvents) {
  const started = Date.now();
  let last = null;

  while (Date.now() - started < maxWaitMs) {
    const state = await detectSunoCaptcha(page);
    last = state;
    if (!state.challengeVisible) return { cleared: true, state };

    await sleep(page, 3000);
  }

  return { cleared: false, state: last, events: [...captchaEvents] };
}

function buildHitmakerPrompt(args) {
  const pieces = [
    "You are Suno Hitmaker.",
    "Generate one dedication song concept for Suno.",
    "Return ONLY valid JSON.",
    "JSON keys: title, lyrics_prompt, style_prompt, negative_styles, vocal_gender, lyrics_mode.",
    `Dedication: ${args.dedication}`,
  ];

  if (args.to) pieces.push(`Recipient: ${args.to}`);
  if (args.from) pieces.push(`From: ${args.from}`);
  if (args.mood) pieces.push(`Mood: ${args.mood}`);
  if (args.style) pieces.push(`Style guidance: ${args.style}`);

  pieces.push("Constraints: lyrics_mode must be manual or auto, vocal_gender must be male or female or empty string.");

  return pieces.join("\n");
}

async function run() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    process.exit(0);
  }

  required(args.dedication, "--dedication");

  const browserbaseApiKey = required(process.env.BROWSERBASE_API_KEY, "BROWSERBASE_API_KEY");
  const browserbaseProjectId = required(process.env.BROWSERBASE_PROJECT_ID, "BROWSERBASE_PROJECT_ID");

  const chatgptUrl = args["chatgpt-url"] || process.env.CHATGPT_HITMAKER_URL || "";
  const existingSessionId = args["session-id"] || process.env.BROWSERBASE_SESSION_ID || "";
  const contextId = args["context-id"] || process.env.BROWSERBASE_CONTEXT_ID || "";
  const timeoutSec = Number(args["bb-timeout-sec"] || 3600);
  const keepOpen = toBool(args["keep-open"]);

  const outputJson =
    args["output-json"] || path.join("/tmp", `dedication-result-${nowStamp()}.json`);

  const modelApiKey = process.env.STAGEHAND_MODEL_API_KEY || process.env.OPENAI_API_KEY || "sk-placeholder";

  const stagehandOptions = {
    env: "BROWSERBASE",
    apiKey: browserbaseApiKey,
    projectId: browserbaseProjectId,
    model: {
      provider: "openai",
      modelName: "openai/gpt-4o-mini",
      apiKey: modelApiKey,
    },
    waitForCaptchaSolves: true,
    verbose: toBool(args.verbose) ? 1 : 0,
  };

  if (existingSessionId) {
    stagehandOptions.browserbaseSessionID = existingSessionId;
  } else {
    stagehandOptions.browserbaseSessionCreateParams = {
      projectId: browserbaseProjectId,
      timeout: timeoutSec,
      keepAlive: true,
      proxies: true,
      browserSettings: {
        solveCaptchas: true,
        recordSession: true,
        logSession: true,
        ...(contextId ? { context: { id: contextId, persist: true } } : {}),
      },
    };
  }

  const stagehand = new Stagehand(stagehandOptions);

  const captchaEvents = [];
  const artifacts = [];
  let summary = null;

  try {
    await stagehand.init();
    const page = stagehand.context.activePage() || stagehand.context.pages()[0];
    if (!page) throw new Error("No page available after Stagehand init.");

    page.on("console", (msg) => {
      const text = msg.text();
      if (
        text.includes("browserbase-solving-started") ||
        text.includes("browserbase-solving-finished")
      ) {
        captchaEvents.push({ ts: new Date().toISOString(), text });
      }
    });

    const sessionId = stagehand.browserbaseSessionID || null;
    const debugUrl = stagehand.browserbaseDebugURL || null;

    console.log(JSON.stringify({ status: "info", sessionId, debugUrl }, null, 2));

    let songSpec = null;
    const skipChatgpt = Boolean(args["lyrics-prompt"] || args["style-prompt"]);

    if (skipChatgpt) {
      songSpec = {
        ...buildFallbackSpec(args),
        lyrics_prompt: args["lyrics-prompt"] || buildFallbackSpec(args).lyrics_prompt,
        style_prompt: args["style-prompt"] || buildFallbackSpec(args).style_prompt,
      };
    } else {
      required(chatgptUrl, "--chatgpt-url or CHATGPT_HITMAKER_URL");

      await page.goto(chatgptUrl, { waitUntil: "domcontentloaded", timeoutMs: 120000 });
      await sleep(page, 2500);

      const loginWall = await page.evaluate(() => {
        const txt = (document.body?.innerText || "").toLowerCase();
        return txt.includes("log in") && txt.includes("sign up") && !txt.includes("prompt");
      });
      if (loginWall) {
        throw new Error(
          "ChatGPT appears logged out in this context. Use a Browserbase context logged into chatgpt.com, then rerun.",
        );
      }

      const composerSelector = await waitForVisibleSelector(page, [
        "#prompt-textarea",
        "textarea[placeholder*='Message']",
        "textarea[data-testid='prompt-textarea']",
        "div[contenteditable='true'][id='prompt-textarea']",
        "div[contenteditable='true'][data-testid='composer-input']",
      ]);

      if (!composerSelector) {
        throw new Error("Could not find ChatGPT composer. Check that the custom GPT page is loaded and logged in.");
      }

      const prompt = buildHitmakerPrompt(args);
      const filled = await fillChatComposer(page, prompt);
      if (!filled) throw new Error("Failed to fill ChatGPT composer.");

      const sent = await clickChatSend(page);
      if (!sent) {
        throw new Error("Failed to click ChatGPT send button.");
      }

      const assistantText = await waitForChatResponse(page, 180000);
      if (!assistantText || assistantText.length < 20) {
        throw new Error("Did not receive a usable response from Suno Hitmaker GPT.");
      }

      const parsed = extractJsonObject(assistantText);
      songSpec = parsed && typeof parsed === "object" ? parsed : null;
      if (!songSpec) {
        songSpec = buildFallbackSpec(args);
      }

      songSpec = {
        ...buildFallbackSpec(args),
        ...songSpec,
      };

      const chatShot = `/tmp/dedication-chatgpt-${nowStamp()}.png`;
      await page.screenshot({ path: chatShot });
      artifacts.push(chatShot);
    }

    await page.goto("https://suno.com/create", { waitUntil: "domcontentloaded", timeoutMs: 120000 });
    await sleep(page, 3000);
    const sunoReady = await waitForSunoCreateReady(page, 90000);
    if (!sunoReady) {
      throw new Error("Suno create page did not become ready (composer/create button not visible).");
    }

    const sunoLoginWall = await page.evaluate(() => {
      const txt = (document.body?.innerText || "").toLowerCase();
      return txt.includes("sign in") && txt.includes("sign up") && !txt.includes("create");
    });
    if (sunoLoginWall) {
      throw new Error(
        "Suno appears logged out in this context. Use a Browserbase context logged into suno.com, then rerun.",
      );
    }

    const before = await detectSunoCaptcha(page);
    const fillResult = await fillSunoCustomForm(page, songSpec);

    const createClickedInitial = await clickSunoCreate(page);
    await sleep(page, 2000);

    const afterClick = await detectSunoCaptcha(page);
    let captchaWaitResult = null;
    let retriedCreate = false;

    if (afterClick.challengeVisible) {
      captchaWaitResult = await waitForCaptchaClear(page, 120000, captchaEvents);
      if (captchaWaitResult.cleared) {
        retriedCreate = await clickSunoCreate(page);
      }
    }

    await sleep(page, 2500);
    const finalState = await detectSunoCaptcha(page);

    const sunoShot = `/tmp/dedication-suno-${nowStamp()}.png`;
    await page.screenshot({ path: sunoShot });
    artifacts.push(sunoShot);

    summary = {
      status: "success",
      sessionId,
      attachedToExistingSession: Boolean(existingSessionId),
      requestedSessionId: existingSessionId || null,
      debugUrl,
      contextId: contextId || null,
      usedProxy: true,
      captchaSolvingEnabled: true,
      songSpec,
      fillResult,
      createClickedInitial,
      retriedCreate,
      before,
      afterClick,
      captchaWaitResult,
      finalState,
      captchaEvents,
      artifacts,
      notes: [
        "If finalState.challengeVisible is true, CAPTCHA still needs solving or another retry.",
        "If credits dropped or a new pending track appears, generation started.",
      ],
      generatedAt: new Date().toISOString(),
    };

    await fs.writeFile(outputJson, `${JSON.stringify(summary, null, 2)}\n`, "utf8");
    console.log(JSON.stringify({ status: "ok", outputJson, summary }, null, 2));
  } finally {
    if (!keepOpen) {
      await stagehand.close();
    }
  }
}

run().catch(async (err) => {
  const payload = {
    status: "error",
    error: err?.message || String(err),
    stack: trimText(err?.stack || "", 8000),
    ts: new Date().toISOString(),
  };
  console.error(JSON.stringify(payload, null, 2));
  process.exit(1);
});
