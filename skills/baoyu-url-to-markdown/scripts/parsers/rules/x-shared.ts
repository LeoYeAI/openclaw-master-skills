import { convertHtmlFragmentToMarkdown } from "../../legacy-converter.js";
import { normalizeMarkdown } from "../../markdown-conversion-shared.js";

export const DEFAULT_X_OG_IMAGE = "https://abs.twimg.com/rweb/ssr/default/v2/og/image.png";

export type MediaResult = {
  lines: string[];
  urls: string[];
};

export function isXHost(hostname: string): boolean {
  const normalized = hostname.toLowerCase();
  return (
    normalized === "x.com" ||
    normalized === "twitter.com" ||
    normalized.endsWith(".x.com") ||
    normalized.endsWith(".twitter.com")
  );
}

export function parseUrl(input: string): URL | null {
  try {
    return new URL(input);
  } catch {
    return null;
  }
}

export function isXStatusPath(pathname: string): boolean {
  return /^\/[^/]+\/status(?:es)?\/\d+$/i.test(pathname) || /^\/i\/web\/status\/\d+$/i.test(pathname);
}

export function isXArticlePath(pathname: string): boolean {
  return /^\/[^/]+\/article\/\d+$/i.test(pathname) || /^\/(?:i\/)?article\/\d+$/i.test(pathname);
}

export function cleanText(value: string | null | undefined): string {
  return (value ?? "").replace(/\s+/g, " ").trim();
}

export function cleanUserLabel(value: string | null | undefined): string {
  return cleanText(value).replace(/\bVerified account\b/gi, "").replace(/\s{2,}/g, " ").trim();
}

export function escapeMarkdownAlt(text: string): string {
  return text.replace(/[\[\]]/g, "\\$&");
}

export function normalizeAlt(text: string | null | undefined): string {
  const cleaned = cleanText(text);
  if (!cleaned || /^(image|photo)$/i.test(cleaned)) return "";
  return escapeMarkdownAlt(cleaned);
}

export function summarizeText(text: string, maxLength: number): string | undefined {
  const normalized = cleanText(text);
  if (!normalized) return undefined;
  return normalized.length > maxLength
    ? `${normalized.slice(0, maxLength - 3)}...`
    : normalized;
}

export function buildTweetTitle(text: string, fallback: string): string {
  return summarizeText(text, 80) ?? fallback;
}

export function normalizeXMarkdown(markdown: string): string {
  return normalizeMarkdown(markdown.replace(/^(#{1,6})\s*\n+([^\n])/gm, "$1 $2"));
}

export function inferLanguage(text: string, fallback?: string): string | undefined {
  const normalized = cleanText(text);
  if (!normalized) return fallback;

  const han = (normalized.match(/\p{Script=Han}/gu) || []).length;
  const hiragana = (normalized.match(/\p{Script=Hiragana}/gu) || []).length;
  const katakana = (normalized.match(/\p{Script=Katakana}/gu) || []).length;
  const hangul = (normalized.match(/\p{Script=Hangul}/gu) || []).length;

  if (hangul >= 8) return "ko";
  if (hiragana + katakana >= 8) return "ja";
  if (han >= 16) return "zh";
  return fallback;
}

export function buildQuoteMarkdown(markdown: string, author?: string): string {
  const normalized = normalizeMarkdown(markdown);
  if (!normalized) return "";

  const lines = normalized.split("\n");
  const prefixed = lines.map((line) => (line ? `> ${line}` : ">")).join("\n");
  const header = author ? `> Quote from ${author}` : "> Quote";
  return `${header}\n${prefixed}`;
}

export function pickFirstValidLinkText(userNameEl: Element | null | undefined): {
  name?: string;
  username?: string;
  author?: string;
} {
  if (!userNameEl) return {};

  const linkTexts = Array.from(userNameEl.querySelectorAll("a[href]"))
    .map((link) => cleanUserLabel(link.textContent))
    .filter(Boolean);

  let username = linkTexts.find((text) => text.startsWith("@"));
  let name = linkTexts.find((text) => !text.startsWith("@") && !/^(promote|more)$/i.test(text));

  if (!username || !name) {
    const text = cleanUserLabel(userNameEl.textContent);
    const fallbackMatch = text.match(/^(.*?)\s*(@[A-Za-z0-9_]+)(?:\s*·.*)?$/);
    if (fallbackMatch) {
      name = name ?? cleanText(fallbackMatch[1]);
      username = username ?? cleanText(fallbackMatch[2]);
    }
  }

  const author = name && username ? `${name} (${username})` : username ?? name;
  return { name, username, author };
}

export function extractPublishedForCurrentUrl(root: ParentNode, url: string): string | undefined {
  const parsed = parseUrl(url);
  if (!parsed) return undefined;
  const currentPath = parsed.pathname.toLowerCase();

  for (const timeElement of root.querySelectorAll("a[href] time[datetime]")) {
    const href = timeElement.closest("a")?.getAttribute("href");
    const hrefUrl = href ? parseUrl(href.startsWith("http") ? href : `${parsed.origin}${href}`) : null;
    if (hrefUrl?.pathname.toLowerCase() === currentPath) {
      return timeElement.getAttribute("datetime") ?? undefined;
    }
  }

  return root.querySelector("time[datetime]")?.getAttribute("datetime") ?? undefined;
}

export function collectMediaMarkdown(root: ParentNode, seen: Set<string>): MediaResult {
  const lines: string[] = [];
  const urls: string[] = [];
  const rootElement = root as Element & {
    getAttribute?: (name: string) => string | null;
  };
  const photoNodes = [
    ...(typeof rootElement.getAttribute === "function" &&
    rootElement.getAttribute("data-testid") === "tweetPhoto"
      ? [rootElement]
      : []),
    ...Array.from(root.querySelectorAll("[data-testid='tweetPhoto']")),
  ];

  for (const node of photoNodes) {
    const img = node.querySelector("img");
    const imageUrl = img?.getAttribute("src");
    if (imageUrl && !seen.has(imageUrl)) {
      seen.add(imageUrl);
      urls.push(imageUrl);
      lines.push(`![${normalizeAlt(img?.getAttribute("alt"))}](${imageUrl})`);
    }

    const video = node.querySelector("video");
    const posterUrl = video?.getAttribute("poster");
    if (posterUrl && !seen.has(posterUrl)) {
      seen.add(posterUrl);
      urls.push(posterUrl);
      lines.push(`![video](${posterUrl})`);
    }

    const videoUrl = video?.getAttribute("src") ?? video?.querySelector("source")?.getAttribute("src");
    if (videoUrl && !seen.has(videoUrl)) {
      seen.add(videoUrl);
      urls.push(videoUrl);
      lines.push(`[video](${videoUrl})`);
    }
  }

  return { lines, urls };
}

export function materializeTweetPhotoNodes(root: Element): void {
  for (const photo of Array.from(root.querySelectorAll("[data-testid='tweetPhoto']"))) {
    const document = photo.ownerDocument;
    const container = document.createElement("span");

    const img = photo.querySelector("img");
    const imageUrl = img?.getAttribute("src");
    if (imageUrl) {
      const image = document.createElement("img");
      image.setAttribute("src", imageUrl);
      const alt = normalizeAlt(img?.getAttribute("alt"));
      if (alt) {
        image.setAttribute("alt", alt);
      }
      container.appendChild(image);
    }

    const video = photo.querySelector("video");
    const posterUrl = video?.getAttribute("poster");
    if (posterUrl) {
      const poster = document.createElement("img");
      poster.setAttribute("src", posterUrl);
      poster.setAttribute("alt", "video");
      container.appendChild(poster);
    }

    const videoUrl = video?.getAttribute("src") ?? video?.querySelector("source")?.getAttribute("src");
    if (videoUrl) {
      if (container.childNodes.length > 0) {
        container.appendChild(document.createTextNode(" "));
      }
      const link = document.createElement("a");
      link.setAttribute("href", videoUrl);
      link.textContent = "video";
      container.appendChild(link);
    }

    if (container.childNodes.length === 0) {
      photo.remove();
      continue;
    }

    photo.replaceWith(container);
  }
}

function collapseLinkedMediaContainers(root: Element): void {
  for (const anchor of Array.from(root.querySelectorAll("a[href]"))) {
    const images = Array.from(anchor.querySelectorAll("img"));
    if (images.length !== 1) continue;
    if (cleanText(anchor.textContent)) continue;

    const image = images[0].cloneNode(true);
    anchor.replaceChildren(image);
  }
}

export function convertXRichTextElementToMarkdown(node: Element): string {
  const clone = node.cloneNode(true) as Element;
  materializeTweetPhotoNodes(clone);
  collapseLinkedMediaContainers(clone);
  return normalizeXMarkdown(convertHtmlFragmentToMarkdown(clone.innerHTML));
}

export function sanitizeCoverImage(primary?: string, fallback?: string): string | undefined {
  if (primary) return primary;
  if (!fallback || fallback === DEFAULT_X_OG_IMAGE) return undefined;
  return fallback;
}
