import { archivePhRuleParser } from "./archive-ph.js";
import { xArticleRuleParser } from "./x-article.js";
import { xStatusRuleParser } from "./x-status.js";
import type { UrlRuleParser } from "../types.js";

export const URL_RULE_PARSERS: UrlRuleParser[] = [
  archivePhRuleParser,
  xArticleRuleParser,
  xStatusRuleParser,
];
