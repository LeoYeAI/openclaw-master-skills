import type { ConversionResult } from "../../markdown-conversion-shared.js";
import type { UrlRuleParser, UrlRuleParserContext } from "../types.js";
import {
  buildQuoteMarkdown,
  buildTweetTitle,
  cleanText,
  collectMediaMarkdown,
  convertXRichTextElementToMarkdown,
  extractPublishedForCurrentUrl,
  inferLanguage,
  isXHost,
  isXStatusPath,
  normalizeXMarkdown,
  parseUrl,
  pickFirstValidLinkText,
  sanitizeCoverImage,
  summarizeText,
} from "./x-shared.js";

function parseXStatus(context: UrlRuleParserContext): ConversionResult | null {
  const article = context.document.querySelector("article[data-testid='tweet'], article") as Element | null;
  if (!article) return null;

  const tweetTextElements = Array.from(article.querySelectorAll("[data-testid='tweetText']")) as Element[];
  if (tweetTextElements.length === 0) return null;

  const userNameElements = Array.from(article.querySelectorAll("[data-testid='User-Name']")) as Element[];
  const mainTextElement = tweetTextElements[0];
  const mainIdentity = pickFirstValidLinkText(userNameElements[0]);
  const published = extractPublishedForCurrentUrl(article, context.url);
  const mainMarkdown = normalizeXMarkdown(convertXRichTextElementToMarkdown(mainTextElement));
  if (!mainMarkdown) return null;

  const parts = [mainMarkdown];
  const quotedTextElements = tweetTextElements.slice(1);
  const quotedUserNameElements = userNameElements.slice(1);

  quotedTextElements.forEach((element, index) => {
    const quoteMarkdown = normalizeXMarkdown(convertXRichTextElementToMarkdown(element));
    if (!quoteMarkdown) return;
    const quoteIdentity = pickFirstValidLinkText(quotedUserNameElements[index]);
    parts.push(buildQuoteMarkdown(quoteMarkdown, quoteIdentity.author));
  });

  const media = collectMediaMarkdown(article, new Set<string>());
  if (media.lines.length > 0) {
    parts.push(media.lines.join("\n\n"));
  }

  const mainText = cleanText(mainTextElement.textContent);
  const markdown = normalizeXMarkdown(parts.join("\n\n"));

  return {
    metadata: {
      ...context.baseMetadata,
      title: buildTweetTitle(mainText, context.baseMetadata.title),
      description: summarizeText(mainText, 220) ?? context.baseMetadata.description,
      author: mainIdentity.author ?? context.baseMetadata.author,
      published: published ?? context.baseMetadata.published,
      coverImage: sanitizeCoverImage(media.urls[0], context.baseMetadata.coverImage),
      language: inferLanguage(mainText, context.baseMetadata.language),
    },
    markdown,
    rawHtml: context.html,
    conversionMethod: "parser:x-status",
  };
}

export const xStatusRuleParser: UrlRuleParser = {
  id: "x-status",
  supports(context) {
    const parsed = parseUrl(context.url);
    if (!parsed || !isXHost(parsed.hostname)) {
      return false;
    }

    return isXStatusPath(parsed.pathname) && Boolean(context.document.querySelector("[data-testid='tweetText']"));
  },
  parse(context): ConversionResult | null {
    return parseXStatus(context);
  },
};
