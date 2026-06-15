import {
  isMarkdownUsable,
  normalizeMarkdown,
  parseDocument,
  type ConversionResult,
  type PageMetadata,
} from "../markdown-conversion-shared.js";
import { URL_RULE_PARSERS } from "./rules/index.js";
import type { UrlRuleParserContext } from "./types.js";

export type { UrlRuleParser, UrlRuleParserContext } from "./types.js";

export function tryUrlRuleParsers(
  html: string,
  url: string,
  baseMetadata: PageMetadata
): ConversionResult | null {
  const document = parseDocument(html);
  const context: UrlRuleParserContext = {
    html,
    url,
    document,
    baseMetadata,
  };

  for (const parser of URL_RULE_PARSERS) {
    if (!parser.supports(context)) continue;

    try {
      const result = parser.parse(context);
      if (!result) continue;

      const markdown = normalizeMarkdown(result.markdown);
      if (!isMarkdownUsable(markdown, html)) continue;

      return {
        ...result,
        markdown,
      };
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      console.warn(`[url-to-markdown] parser ${parser.id} failed: ${message}`);
    }
  }

  return null;
}
