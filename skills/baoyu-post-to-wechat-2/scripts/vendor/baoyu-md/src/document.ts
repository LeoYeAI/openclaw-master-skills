import fs from "node:fs";
import path from "node:path";

import type { ReadTimeResults } from "reading-time";

import {
  COLOR_PRESETS,
  DEFAULT_STYLE,
  FONT_FAMILY_MAP,
  THEME_STYLE_DEFAULTS,
} from "./constants.js";
import {
  extractSummaryFromBody,
  extractTitleFromMarkdown,
  pickFirstString,
  stripWrappingQuotes,
} from "./content.js";
import { loadExtendConfig } from "./extend-config.js";
import {
  buildCss,
  buildHtmlDocument,
  inlineCss,
  loadCodeThemeCss,
  modifyHtmlStructure,
  normalizeInlineCss,
  removeFirstHeading,
} from "./html-builder.js";
import { initRenderer, postProcessHtml, renderMarkdown } from "./renderer.js";
import { loadThemeCss, normalizeThemeCss } from "./themes.js";
import type { HtmlDocumentMeta, IOpts, StyleConfig, ThemeName } from "./types.js";

export interface RenderMarkdownDocumentOptions {
  codeTheme?: string;
  countStatus?: boolean;
  citeStatus?: boolean;
  defaultTitle?: string;
  fontFamily?: string;
  fontSize?: string;
  isMacCodeBlock?: boolean;
  isShowLineNumber?: boolean;
  keepTitle?: boolean;
  legend?: string;
  primaryColor?: string;
  theme?: ThemeName;
  themeMode?: IOpts["themeMode"];
}

export interface RenderMarkdownDocumentResult {
  contentHtml: string;
  html: string;
  meta: HtmlDocumentMeta;
  readingTime: ReadTimeResults;
  style: StyleConfig;
  yamlData: Record<string, unknown>;
}

export function resolveColorToken(value?: string): string | undefined {
  if (!value) return undefined;
  return COLOR_PRESETS[value] ?? value;
}

export function resolveFontFamilyToken(value?: string): string | undefined {
  if (!value) return undefined;
  return FONT_FAMILY_MAP[value] ?? value;
}

export function formatTimestamp(date = new Date()): string {
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(
    date.getDate(),
  )}${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;
}

export function buildMarkdownDocumentMeta(
  markdown: string,
  yamlData: Record<string, unknown>,
  defaultTitle = "document",
): HtmlDocumentMeta {
  const title = pickFirstString(yamlData, ["title"])
    || extractTitleFromMarkdown(markdown)
    || defaultTitle;
  const author = pickFirstString(yamlData, ["author"]);
  const description = pickFirstString(yamlData, ["description", "summary"])
    || extractSummaryFromBody(markdown, 120);

  return {
    title: stripWrappingQuotes(title),
    author: author ? stripWrappingQuotes(author) : undefined,
    description: description ? stripWrappingQuotes(description) : undefined,
  };
}

export function resolveMarkdownStyle(options: RenderMarkdownDocumentOptions = {}): StyleConfig {
  const theme = options.theme ?? "default";
  const themeDefaults = THEME_STYLE_DEFAULTS[theme] ?? {};

  return {
    ...DEFAULT_STYLE,
    ...themeDefaults,
    ...(options.primaryColor !== undefined ? { primaryColor: options.primaryColor } : {}),
    ...(options.fontFamily !== undefined ? { fontFamily: options.fontFamily } : {}),
    ...(options.fontSize !== undefined ? { fontSize: options.fontSize } : {}),
  };
}

export function resolveRenderOptions(
  options: RenderMarkdownDocumentOptions = {},
): RenderMarkdownDocumentOptions {
  const extendConfig = loadExtendConfig();

  return {
    codeTheme: options.codeTheme ?? extendConfig.default_code_theme ?? "github",
    countStatus: options.countStatus ?? extendConfig.count ?? false,
    citeStatus: options.citeStatus ?? extendConfig.cite ?? false,
    defaultTitle: options.defaultTitle,
    fontFamily: options.fontFamily ?? resolveFontFamilyToken(extendConfig.default_font_family ?? undefined),
    fontSize: options.fontSize ?? extendConfig.default_font_size ?? undefined,
    isMacCodeBlock: options.isMacCodeBlock ?? extendConfig.mac_code_block ?? true,
    isShowLineNumber: options.isShowLineNumber ?? extendConfig.show_line_number ?? false,
    keepTitle: options.keepTitle ?? extendConfig.keep_title ?? false,
    legend: options.legend ?? extendConfig.legend ?? "alt",
    primaryColor: options.primaryColor ?? resolveColorToken(extendConfig.default_color ?? undefined),
    theme: options.theme ?? extendConfig.default_theme ?? "default",
    themeMode: options.themeMode,
  };
}

export async function renderMarkdownDocument(
  markdown: string,
  options: RenderMarkdownDocumentOptions = {},
): Promise<RenderMarkdownDocumentResult> {
  const resolvedOptions = resolveRenderOptions(options);
  const theme = resolvedOptions.theme ?? "default";
  const codeTheme = resolvedOptions.codeTheme ?? "github";
  const style = resolveMarkdownStyle(resolvedOptions);

  const { baseCss, themeCss } = loadThemeCss(theme);
  const css = normalizeThemeCss(buildCss(baseCss, themeCss, style));
  const codeThemeCss = loadCodeThemeCss(codeTheme);

  const renderer = initRenderer({
    citeStatus: resolvedOptions.citeStatus ?? false,
    countStatus: resolvedOptions.countStatus ?? false,
    isMacCodeBlock: resolvedOptions.isMacCodeBlock ?? true,
    isShowLineNumber: resolvedOptions.isShowLineNumber ?? false,
    legend: resolvedOptions.legend ?? "alt",
    themeMode: resolvedOptions.themeMode,
  });

  const { yamlData, markdownContent, readingTime } = renderer.parseFrontMatterAndContent(markdown);
  const { html: baseHtml, readingTime: readingTimeResult } = renderMarkdown(markdown, renderer);

  let contentHtml = postProcessHtml(baseHtml, readingTimeResult, renderer);
  if (!(resolvedOptions.keepTitle ?? false)) {
    contentHtml = removeFirstHeading(contentHtml);
  }

  const meta = buildMarkdownDocumentMeta(
    markdownContent,
    yamlData as Record<string, unknown>,
    resolvedOptions.defaultTitle,
  );
  const html = buildHtmlDocument(meta, css, contentHtml, codeThemeCss);
  const inlinedHtml = normalizeInlineCss(await inlineCss(html), style);

  return {
    contentHtml,
    html: modifyHtmlStructure(inlinedHtml),
    meta,
    readingTime,
    style,
    yamlData: yamlData as Record<string, unknown>,
  };
}

export async function renderMarkdownFileToHtml(
  inputPath: string,
  options: RenderMarkdownDocumentOptions = {},
): Promise<RenderMarkdownDocumentResult & {
  backupPath?: string;
  outputPath: string;
}> {
  const markdown = fs.readFileSync(inputPath, "utf-8");
  const outputPath = path.resolve(
    path.dirname(inputPath),
    `${path.basename(inputPath, path.extname(inputPath))}.html`,
  );
  const result = await renderMarkdownDocument(markdown, {
    ...options,
    defaultTitle: options.defaultTitle ?? path.basename(outputPath, ".html"),
  });

  let backupPath: string | undefined;
  if (fs.existsSync(outputPath)) {
    backupPath = `${outputPath}.bak-${formatTimestamp()}`;
    fs.renameSync(outputPath, backupPath);
  }

  fs.writeFileSync(outputPath, result.html, "utf-8");

  return {
    ...result,
    backupPath,
    outputPath,
  };
}
