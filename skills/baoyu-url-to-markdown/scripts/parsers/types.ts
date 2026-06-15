import type { ConversionResult, PageMetadata } from "../markdown-conversion-shared.js";

export interface UrlRuleParserContext {
  html: string;
  url: string;
  document: Document;
  baseMetadata: PageMetadata;
}

export interface UrlRuleParser {
  id: string;
  supports(context: UrlRuleParserContext): boolean;
  parse(context: UrlRuleParserContext): ConversionResult | null;
}
