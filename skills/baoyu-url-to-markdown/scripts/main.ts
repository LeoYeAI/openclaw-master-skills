import { createInterface } from "node:readline";
import { writeFile, mkdir, access } from "node:fs/promises";
import path from "node:path";
import process from "node:process";

import { CdpConnection, getFreePort, findExistingChromePort, launchChrome, waitForChromeDebugPort, waitForNetworkIdle, waitForPageLoad, autoScroll, evaluateScript, killChrome } from "./cdp.js";
import { absolutizeUrlsScript, extractContent, createMarkdownDocument, type ConversionResult } from "./html-to-markdown.js";
import { localizeMarkdownMedia, countRemoteMedia } from "./media-localizer.js";
import { resolveUrlToMarkdownDataDir } from "./paths.js";
import { DEFAULT_TIMEOUT_MS, CDP_CONNECT_TIMEOUT_MS, NETWORK_IDLE_TIMEOUT_MS, POST_LOAD_DELAY_MS, SCROLL_STEP_WAIT_MS, SCROLL_MAX_STEPS } from "./constants.js";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

interface Args {
  url: string;
  output?: string;
  outputDir?: string;
  wait: boolean;
  timeout: number;
  downloadMedia: boolean;
  browserMode: BrowserMode;
}

type BrowserMode = "auto" | "headless" | "headed";

interface CaptureAttemptOptions {
  headless: boolean;
  wait: boolean;
  existingPort?: number;
  waitPrompt?: string;
}

interface CaptureSnapshot {
  html: string;
  finalUrl: string;
}

const BROWSER_MODES = new Set<BrowserMode>(["auto", "headless", "headed"]);

function parseArgs(argv: string[]): Args {
  const args: Args = {
    url: "",
    wait: false,
    timeout: DEFAULT_TIMEOUT_MS,
    downloadMedia: false,
    browserMode: "auto",
  };
  for (let i = 2; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === "--wait" || arg === "-w") {
      args.wait = true;
    } else if (arg === "-o" || arg === "--output") {
      args.output = argv[++i];
    } else if (arg === "--timeout" || arg === "-t") {
      args.timeout = parseInt(argv[++i], 10) || DEFAULT_TIMEOUT_MS;
    } else if (arg === "--output-dir") {
      args.outputDir = argv[++i];
    } else if (arg === "--download-media") {
      args.downloadMedia = true;
    } else if (arg === "--browser") {
      args.browserMode = (argv[++i] as BrowserMode | undefined) ?? "auto";
    } else if (arg === "--headless") {
      args.browserMode = "headless";
    } else if (arg === "--headed" || arg === "--noheadless" || arg === "--no-headless") {
      args.browserMode = "headed";
    } else if (!arg.startsWith("-") && !args.url) {
      args.url = arg;
    }
  }
  return args;
}

const SLUG_STOP_WORDS = new Set([
  "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
  "have", "has", "had", "do", "does", "did", "will", "would", "shall",
  "should", "may", "might", "must", "can", "could", "to", "of", "in",
  "for", "on", "with", "at", "by", "from", "as", "into", "through",
  "during", "before", "after", "above", "below", "between", "out",
  "off", "over", "under", "again", "further", "then", "once", "here",
  "there", "when", "where", "why", "how", "all", "both", "each",
  "few", "more", "most", "other", "some", "such", "no", "nor", "not",
  "only", "own", "same", "so", "than", "too", "very", "just", "but",
  "and", "or", "if", "this", "that", "these", "those", "it", "its",
  "http", "https", "www", "com", "org", "net", "post", "article",
]);

function extractSlugFromContent(content: string): string | null {
  const body = content.replace(/^---\n[\s\S]*?\n---\n?/, "").slice(0, 1000);
  const words = body
    .replace(/[^\w\s-]/g, " ")
    .split(/\s+/)
    .filter((w) => /^[a-zA-Z]/.test(w) && w.length >= 2 && !SLUG_STOP_WORDS.has(w.toLowerCase()))
    .map((w) => w.toLowerCase());

  const unique: string[] = [];
  const seen = new Set<string>();
  for (const w of words) {
    if (!seen.has(w)) {
      seen.add(w);
      unique.push(w);
      if (unique.length >= 6) break;
    }
  }
  return unique.length >= 2 ? unique.join("-").slice(0, 50) : null;
}

function generateSlug(title: string, url: string, content?: string): string {
  const asciiWords = title
    .replace(/[^\w\s]/g, " ")
    .split(/\s+/)
    .filter((w) => /[a-zA-Z]/.test(w) && w.length >= 2 && !SLUG_STOP_WORDS.has(w.toLowerCase()))
    .map((w) => w.toLowerCase());

  if (asciiWords.length >= 2) {
    return asciiWords.slice(0, 6).join("-").slice(0, 50);
  }

  if (content) {
    const contentSlug = extractSlugFromContent(content);
    if (contentSlug) return contentSlug;
  }

  const GENERIC_PATH_SEGMENTS = new Set(["status", "article", "post", "posts", "p", "blog", "news", "articles"]);
  const parsed = new URL(url);
  const pathSlug = parsed.pathname
    .split("/")
    .filter((s) => s.length > 0 && !/^\d{10,}$/.test(s) && !GENERIC_PATH_SEGMENTS.has(s.toLowerCase()))
    .join("-")
    .toLowerCase()
    .replace(/[^\w-]/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 40);

  const prefix = asciiWords.slice(0, 2).join("-");
  const combined = prefix ? `${prefix}-${pathSlug}` : pathSlug;
  return combined.slice(0, 50) || "page";
}

function formatTimestamp(): string {
  const now = new Date();
  const pad = (n: number) => n.toString().padStart(2, "0");
  return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
}

function deriveHtmlSnapshotPath(markdownPath: string): string {
  const parsed = path.parse(markdownPath);
  const basename = parsed.ext ? parsed.name : parsed.base;
  return path.join(parsed.dir, `${basename}-captured.html`);
}

function extractTitleFromMarkdownDocument(document: string): string {
  const normalized = document.replace(/\r\n/g, "\n");
  const frontmatterMatch = normalized.match(/^---\n([\s\S]*?)\n---\n?/);
  if (frontmatterMatch) {
    const titleLine = frontmatterMatch[1]
      .split("\n")
      .find((line) => /^title:\s*/i.test(line));

    if (titleLine) {
      const rawValue = titleLine.replace(/^title:\s*/i, "").trim();
      const unquoted = rawValue
        .replace(/^"(.*)"$/, "$1")
        .replace(/^'(.*)'$/, "$1")
        .replace(/\\"/g, '"');
      if (unquoted) return unquoted;
    }
  }

  const headingMatch = normalized.match(/^#\s+(.+)$/m);
  return headingMatch?.[1]?.trim() ?? "";
}

function buildDefuddleApiUrl(targetUrl: string): string {
  return `https://defuddle.md/${encodeURIComponent(targetUrl)}`;
}

async function fetchDefuddleApiMarkdown(targetUrl: string): Promise<{ markdown: string; title: string }> {
  const apiUrl = buildDefuddleApiUrl(targetUrl);
  const response = await fetch(apiUrl, {
    headers: {
      accept: "text/markdown,text/plain;q=0.9,*/*;q=0.1",
    },
  });

  if (!response.ok) {
    throw new Error(`defuddle.md returned ${response.status} ${response.statusText}`);
  }

  const markdown = (await response.text()).replace(/\r\n/g, "\n").trim();
  if (!markdown) {
    throw new Error("defuddle.md returned empty markdown");
  }

  return {
    markdown,
    title: extractTitleFromMarkdownDocument(markdown),
  };
}

async function generateOutputPath(url: string, title: string, outputDir?: string, content?: string): Promise<string> {
  const domain = new URL(url).hostname.replace(/^www\./, "");
  const slug = generateSlug(title, url, content);
  const dataDir = outputDir ? path.resolve(outputDir) : resolveUrlToMarkdownDataDir();
  const basePath = path.join(dataDir, domain, slug, `${slug}.md`);

  if (!(await fileExists(basePath))) {
    return basePath;
  }

  const timestampSlug = `${slug}-${formatTimestamp()}`;
  return path.join(dataDir, domain, timestampSlug, `${timestampSlug}.md`);
}

function defaultWaitPrompt(): string {
  return "A browser window has been opened. If the page requires login or verification, complete it first, then press Enter to capture.";
}

async function waitForUserSignal(prompt: string): Promise<void> {
  console.log(prompt);
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  await new Promise<void>((resolve) => {
    rl.once("line", () => { rl.close(); resolve(); });
  });
}

async function captureUrlOnce(args: Args, options: CaptureAttemptOptions): Promise<ConversionResult> {
  const reusing = options.existingPort !== undefined;
  const port = options.existingPort ?? await getFreePort();
  const chrome = reusing ? null : await launchChrome(args.url, port, options.headless);

  if (reusing) {
    console.log(`Reusing existing Chrome on port ${port}`);
  } else {
    console.log(`Launching Chrome (${options.headless ? "headless" : "headed"})...`);
  }

  let cdp: CdpConnection | null = null;
  let targetId: string | null = null;
  try {
    const wsUrl = await waitForChromeDebugPort(port, 30_000);
    cdp = await CdpConnection.connect(wsUrl, CDP_CONNECT_TIMEOUT_MS);

    let sessionId: string;
    if (reusing) {
      const created = await cdp.send<{ targetId: string }>("Target.createTarget", { url: args.url });
      targetId = created.targetId;
      const attached = await cdp.send<{ sessionId: string }>("Target.attachToTarget", { targetId, flatten: true });
      sessionId = attached.sessionId;
      await cdp.send("Network.enable", {}, { sessionId });
      await cdp.send("Page.enable", {}, { sessionId });
    } else {
      const targets = await cdp.send<{ targetInfos: Array<{ targetId: string; type: string; url: string }> }>("Target.getTargets");
      const pageTarget = targets.targetInfos.find(t => t.type === "page" && t.url.startsWith("http"));
      if (!pageTarget) throw new Error("No page target found");
      targetId = pageTarget.targetId;
      const attached = await cdp.send<{ sessionId: string }>("Target.attachToTarget", { targetId, flatten: true });
      sessionId = attached.sessionId;
      await cdp.send("Network.enable", {}, { sessionId });
      await cdp.send("Page.enable", {}, { sessionId });
    }

    if (options.wait) {
      await waitForUserSignal(options.waitPrompt ?? defaultWaitPrompt());
    } else {
      console.log("Waiting for page to load...");
      await Promise.race([
        waitForPageLoad(cdp, sessionId, 15_000),
        sleep(8_000)
      ]);
      await waitForNetworkIdle(cdp, sessionId, NETWORK_IDLE_TIMEOUT_MS);
      await sleep(POST_LOAD_DELAY_MS);
      console.log("Scrolling to trigger lazy load...");
      await autoScroll(cdp, sessionId, SCROLL_MAX_STEPS, SCROLL_STEP_WAIT_MS);
      await sleep(POST_LOAD_DELAY_MS);
    }

    console.log("Capturing page content...");
    const snapshot = await evaluateScript<CaptureSnapshot>(
      cdp, sessionId, absolutizeUrlsScript, args.timeout
    );
    return await extractContent(snapshot.html, snapshot.finalUrl || args.url, {
      preserveBase64Images: args.downloadMedia,
    });
  } finally {
    if (reusing) {
      if (cdp && targetId) {
        try { await cdp.send("Target.closeTarget", { targetId }, { timeoutMs: 5_000 }); } catch {}
      }
      if (cdp) cdp.close();
    } else {
      if (cdp) {
        try { await cdp.send("Browser.close", {}, { timeoutMs: 5_000 }); } catch {}
        cdp.close();
      }
      if (chrome) killChrome(chrome);
    }
  }
}

async function runHeadedFlow(
  args: Args,
  options: { existingPort?: number; wait: boolean; waitPrompt?: string }
): Promise<ConversionResult> {
  return await captureUrlOnce(args, {
    headless: false,
    wait: options.wait,
    existingPort: options.existingPort,
    waitPrompt: options.waitPrompt,
  });
}

async function captureUrl(args: Args): Promise<ConversionResult> {
  const existingPort = await findExistingChromePort();
  if (existingPort !== null) {
    console.log("Found an existing Chrome session for this profile. Reusing it instead of launching a new browser.");
    return await runHeadedFlow(args, {
      existingPort,
      wait: args.wait,
      waitPrompt: args.wait ? defaultWaitPrompt() : undefined,
    });
  }

  if (args.browserMode === "headless") {
    return await captureUrlOnce(args, { headless: true, wait: false });
  }

  if (args.browserMode === "headed") {
    return await runHeadedFlow(args, {
      wait: args.wait,
      waitPrompt: args.wait ? defaultWaitPrompt() : undefined,
    });
  }

  if (args.wait) {
    return await runHeadedFlow(args, {
      wait: true,
      waitPrompt: defaultWaitPrompt(),
    });
  }

  try {
    return await captureUrlOnce(args, { headless: true, wait: false });
  } catch (error) {
    const headlessMessage = error instanceof Error ? error.message : String(error);
    console.warn(`Headless capture failed: ${headlessMessage}`);
    console.log("Retrying with a visible browser window...");

    try {
      return await runHeadedFlow(args, { wait: false });
    } catch (headedError) {
      const headedMessage = headedError instanceof Error ? headedError.message : String(headedError);
      throw new Error(`Headless capture failed (${headlessMessage}); headed retry failed (${headedMessage})`);
    }
  }
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv);
  if (!args.url) {
    console.error("Usage: bun main.ts <url> [-o output.md] [--output-dir dir] [--wait] [--browser auto|headless|headed] [--timeout ms] [--download-media]");
    process.exit(1);
  }

  try {
    new URL(args.url);
  } catch {
    console.error(`Invalid URL: ${args.url}`);
    process.exit(1);
  }

  if (!BROWSER_MODES.has(args.browserMode)) {
    console.error(`Invalid --browser mode: ${args.browserMode}. Expected auto, headless, or headed.`);
    process.exit(1);
  }

  if (args.wait && args.browserMode === "headless") {
    console.error("Error: --wait requires a visible browser. Use --browser auto or --browser headed.");
    process.exit(1);
  }

  if (args.output) {
    const stat = await import("node:fs").then(fs => fs.statSync(args.output!, { throwIfNoEntry: false }));
    if (stat?.isDirectory()) {
      console.error(`Error: -o path is a directory, not a file: ${args.output}`);
      process.exit(1);
    }
  }

  console.log(`Fetching: ${args.url}`);
  console.log(`Mode: ${args.wait ? "wait" : "auto"}`);
  console.log(`Browser: ${args.browserMode}`);

  let outputPath: string;
  let htmlSnapshotPath: string | null = null;
  let document: string;
  let conversionMethod: string;
  let fallbackReason: string | undefined;

  try {
    const result = await captureUrl(args);
    document = createMarkdownDocument(result);
    outputPath = args.output || await generateOutputPath(result.metadata.url || args.url, result.metadata.title, args.outputDir, document);
    const outputDir = path.dirname(outputPath);
    htmlSnapshotPath = deriveHtmlSnapshotPath(outputPath);
    await mkdir(outputDir, { recursive: true });
    await writeFile(htmlSnapshotPath, result.rawHtml, "utf-8");
    conversionMethod = result.conversionMethod;
    fallbackReason = result.fallbackReason;
  } catch (error) {
    const primaryError = error instanceof Error ? error.message : String(error);
    console.warn(`Primary capture failed: ${primaryError}`);
    console.warn("Trying defuddle.md API fallback...");

    try {
      const remoteResult = await fetchDefuddleApiMarkdown(args.url);
      document = remoteResult.markdown;
      outputPath = args.output || await generateOutputPath(args.url, remoteResult.title, args.outputDir, document);
      await mkdir(path.dirname(outputPath), { recursive: true });
      conversionMethod = "defuddle-api";
      fallbackReason = `Local browser capture failed: ${primaryError}`;
    } catch (remoteError) {
      const remoteMessage = remoteError instanceof Error ? remoteError.message : String(remoteError);
      throw new Error(`Local browser capture failed (${primaryError}); defuddle.md fallback failed (${remoteMessage})`);
    }
  }

  if (args.downloadMedia) {
    const mediaResult = await localizeMarkdownMedia(document, {
      markdownPath: outputPath,
      log: console.log,
    });
    document = mediaResult.markdown;
    if (mediaResult.downloadedImages > 0 || mediaResult.downloadedVideos > 0) {
      console.log(`Downloaded: ${mediaResult.downloadedImages} images, ${mediaResult.downloadedVideos} videos`);
    }
  } else {
    const { images, videos } = countRemoteMedia(document);
    if (images > 0 || videos > 0) {
      console.log(`Remote media found: ${images} images, ${videos} videos`);
    }
  }

  await writeFile(outputPath, document, "utf-8");

  console.log(`Saved: ${outputPath}`);
  if (htmlSnapshotPath) {
    console.log(`Saved HTML: ${htmlSnapshotPath}`);
  } else {
    console.log("Saved HTML: unavailable (defuddle.md fallback)");
  }
  console.log(`Title: ${extractTitleFromMarkdownDocument(document) || "(no title)"}`);
  console.log(`Converter: ${conversionMethod}`);
  if (fallbackReason) {
    console.warn(`Fallback used: ${fallbackReason}`);
  }
}

main().catch((err) => {
  console.error("Error:", err instanceof Error ? err.message : String(err));
  process.exit(1);
});
