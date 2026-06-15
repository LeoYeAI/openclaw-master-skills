import { convertHtmlFragmentToMarkdown } from "../../legacy-converter.js";
import {
  normalizeMarkdown,
  pickString,
  type ConversionResult,
} from "../../markdown-conversion-shared.js";
import type { UrlRuleParser, UrlRuleParserContext } from "../types.js";

const ARCHIVE_HOSTS = new Set([
  "archive.ph",
  "archive.is",
  "archive.today",
  "archive.md",
  "archive.vn",
  "archive.li",
  "archive.fo",
]);

function isArchiveHost(url: string): boolean {
  try {
    return ARCHIVE_HOSTS.has(new URL(url).hostname.toLowerCase());
  } catch {
    return false;
  }
}

function readOriginalUrl(document: Document): string | undefined {
  const value = document.querySelector("input[name='q']")?.getAttribute("value")?.trim();
  if (!value) return undefined;

  try {
    return new URL(value).href;
  } catch {
    return undefined;
  }
}

function summarize(text: string, maxLength: number): string | undefined {
  const normalized = text.replace(/\s+/g, " ").trim();
  if (!normalized) return undefined;
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, Math.max(0, maxLength - 1)).trimEnd()}…`;
}

function pickContentRoot(document: Document): Element | null {
  return (
    document.querySelector("#CONTENT") ??
    document.querySelector("#content") ??
    document.body
  );
}

function pickContentTitle(root: Element, fallbackTitle: string): string {
  const contentTitle = pickString(
    root.querySelector("h1")?.textContent,
    root.querySelector("[itemprop='headline']")?.textContent,
    root.querySelector("article h2")?.textContent
  );
  if (contentTitle) return contentTitle;
  if (fallbackTitle && !/^archive\./i.test(fallbackTitle.trim())) return fallbackTitle;
  return "";
}

function parseArchivePage(context: UrlRuleParserContext): ConversionResult | null {
  const root = pickContentRoot(context.document);
  if (!root) return null;

  const markdown = normalizeMarkdown(convertHtmlFragmentToMarkdown(root.innerHTML));
  if (!markdown) return null;

  const originalUrl = readOriginalUrl(context.document) ?? context.baseMetadata.url;
  const bodyText = root.textContent?.replace(/\s+/g, " ").trim() ?? "";
  const published = root.querySelector("time[datetime]")?.getAttribute("datetime") ?? undefined;
  const coverImage = root.querySelector("img[src]")?.getAttribute("src") ?? undefined;

  return {
    metadata: {
      ...context.baseMetadata,
      url: originalUrl,
      title: pickContentTitle(root, context.baseMetadata.title),
      description: summarize(bodyText, 220) ?? context.baseMetadata.description,
      published: pickString(published, context.baseMetadata.published) ?? undefined,
      coverImage: pickString(coverImage, context.baseMetadata.coverImage) ?? undefined,
    },
    markdown,
    rawHtml: context.html,
    conversionMethod: "parser:archive-ph",
  };
}

export const archivePhRuleParser: UrlRuleParser = {
  id: "archive-ph",
  supports(context) {
    return isArchiveHost(context.url);
  },
  parse: parseArchivePage,
};
