import {
  normalizeMarkdown,
  pickString,
  type ConversionResult,
} from "../../markdown-conversion-shared.js";
import type { UrlRuleParser, UrlRuleParserContext } from "../types.js";
import {
  cleanText,
  collectMediaMarkdown,
  convertXRichTextElementToMarkdown,
  extractPublishedForCurrentUrl,
  inferLanguage,
  isXArticlePath,
  isXHost,
  normalizeXMarkdown,
  parseUrl,
  pickFirstValidLinkText,
  sanitizeCoverImage,
  summarizeText,
} from "./x-shared.js";

function collectArticleMarkdown(root: Element): { markdown: string; mediaUrls: string[] } {
  const parts: string[] = [];
  const seenMedia = new Set<string>();
  const mediaUrls: string[] = [];

  function pushPart(value: string): void {
    const normalized = normalizeMarkdown(value);
    if (!normalized) return;
    parts.push(normalized);
  }

  function walk(node: Element): void {
    const testId = node.getAttribute("data-testid");

    if (testId === "twitterArticleRichTextView" || testId === "longformRichTextComponent") {
      const bodyMedia = collectMediaMarkdown(node, seenMedia);
      mediaUrls.push(...bodyMedia.urls.filter((url) => !mediaUrls.includes(url)));
      pushPart(convertXRichTextElementToMarkdown(node));
      return;
    }

    if (testId === "tweetPhoto") {
      const media = collectMediaMarkdown(node, seenMedia);
      mediaUrls.push(...media.urls.filter((url) => !mediaUrls.includes(url)));
      for (const line of media.lines) pushPart(line);
      return;
    }

    if (
      testId === "twitter-article-title" ||
      testId === "User-Name" ||
      testId === "Tweet-User-Avatar" ||
      testId === "reply" ||
      testId === "retweet" ||
      testId === "like" ||
      testId === "bookmark" ||
      testId === "caret" ||
      testId === "app-text-transition-container"
    ) {
      return;
    }

    if (node.tagName === "TIME" || node.tagName === "BUTTON") {
      return;
    }

    for (const child of Array.from(node.children)) {
      walk(child);
    }
  }

  for (const child of Array.from(root.children)) {
    walk(child);
  }

  return {
    markdown: normalizeXMarkdown(parts.join("\n\n")),
    mediaUrls,
  };
}

function parseXArticle(context: UrlRuleParserContext): ConversionResult | null {
  const articleRoot = context.document.querySelector("[data-testid='twitterArticleReadView']") as Element | null;
  if (!articleRoot) return null;

  const title = cleanText(
    context.document.querySelector("[data-testid='twitter-article-title']")?.textContent
  );
  const identity = pickFirstValidLinkText(
    context.document.querySelector("[data-testid='User-Name']")
  );
  const published = extractPublishedForCurrentUrl(articleRoot, context.url);
  const { markdown, mediaUrls } = collectArticleMarkdown(articleRoot);
  if (!markdown) return null;

  const bodyText = cleanText(
    context.document.querySelector("[data-testid='twitterArticleRichTextView']")?.textContent ??
    context.document.querySelector("[data-testid='longformRichTextComponent']")?.textContent
  );

  return {
    metadata: {
      ...context.baseMetadata,
      title: pickString(title, context.baseMetadata.title) ?? "",
      description: summarizeText(bodyText, 220) ?? context.baseMetadata.description,
      author: pickString(identity.author, context.baseMetadata.author) ?? undefined,
      published: pickString(published, context.baseMetadata.published) ?? undefined,
      coverImage: sanitizeCoverImage(mediaUrls[0], context.baseMetadata.coverImage),
      language: inferLanguage(bodyText, context.baseMetadata.language),
    },
    markdown,
    rawHtml: context.html,
    conversionMethod: "parser:x-article",
  };
}

export const xArticleRuleParser: UrlRuleParser = {
  id: "x-article",
  supports(context) {
    const parsed = parseUrl(context.url);
    if (!parsed || !isXHost(parsed.hostname)) {
      return false;
    }

    return (
      isXArticlePath(parsed.pathname) ||
      Boolean(
        context.document.querySelector("[data-testid='twitterArticleReadView']") ||
        context.document.querySelector("[data-testid='twitterArticleRichTextView']")
      )
    );
  },
  parse(context) {
    return parseXArticle(context);
  },
};
