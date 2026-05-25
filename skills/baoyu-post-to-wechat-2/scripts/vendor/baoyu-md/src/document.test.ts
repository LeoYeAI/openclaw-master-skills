import assert from "node:assert/strict";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import test, { type TestContext } from "node:test";

import { COLOR_PRESETS, FONT_FAMILY_MAP } from "./constants.ts";
import {
  buildMarkdownDocumentMeta,
  formatTimestamp,
  resolveColorToken,
  resolveFontFamilyToken,
  resolveMarkdownStyle,
  resolveRenderOptions,
} from "./document.ts";

function useCwd(t: TestContext, cwd: string): void {
  const previous = process.cwd();
  process.chdir(cwd);
  t.after(() => {
    process.chdir(previous);
  });
}

async function makeTempDir(prefix: string): Promise<string> {
  return fs.mkdtemp(path.join(os.tmpdir(), prefix));
}

test("document token resolvers map known presets and allow passthrough values", () => {
  assert.equal(resolveColorToken("green"), COLOR_PRESETS.green);
  assert.equal(resolveColorToken("#123456"), "#123456");
  assert.equal(resolveColorToken(), undefined);

  assert.equal(resolveFontFamilyToken("mono"), FONT_FAMILY_MAP.mono);
  assert.equal(resolveFontFamilyToken("Custom Font"), "Custom Font");
  assert.equal(resolveFontFamilyToken(), undefined);
});

test("formatTimestamp uses compact sortable datetime output", () => {
  const date = new Date("2026-03-13T21:04:05.000Z");
  const pad = (value: number) => String(value).padStart(2, "0");
  const expected = `${date.getFullYear()}${pad(date.getMonth() + 1)}${pad(
    date.getDate(),
  )}${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;

  assert.equal(formatTimestamp(date), expected);
});

test("buildMarkdownDocumentMeta prefers frontmatter and falls back to markdown title and summary", () => {
  const metaFromYaml = buildMarkdownDocumentMeta(
    "# Markdown Title\n\nBody summary paragraph that should be ignored.",
    {
      title: `" YAML Title "`,
      author: "'Baoyu'",
      summary: `" YAML Summary "`,
    },
    "fallback",
  );

  assert.deepEqual(metaFromYaml, {
    title: "YAML Title",
    author: "Baoyu",
    description: "YAML Summary",
  });

  const metaFromMarkdown = buildMarkdownDocumentMeta(
    `## “Markdown Title”\n\nThis is the first body paragraph that should become the summary because it is long enough.`,
    {},
    "fallback",
  );

  assert.equal(metaFromMarkdown.title, "Markdown Title");
  assert.match(metaFromMarkdown.description ?? "", /^This is the first body paragraph/);
});

test("resolveMarkdownStyle merges theme defaults with explicit overrides", () => {
  const style = resolveMarkdownStyle({
    theme: "modern",
    primaryColor: "#112233",
    fontFamily: "Custom Sans",
  });

  assert.equal(style.primaryColor, "#112233");
  assert.equal(style.fontFamily, "Custom Sans");
  assert.equal(style.fontSize, "15px");
  assert.equal(style.containerBg, "rgba(250, 249, 245, 1)");
});

test("resolveRenderOptions loads workspace EXTEND settings and lets explicit options win", async (t) => {
  const root = await makeTempDir("baoyu-md-render-options-");
  useCwd(t, root);

  const extendPath = path.join(
    root,
    ".baoyu-skills",
    "baoyu-markdown-to-html",
    "EXTEND.md",
  );
  await fs.mkdir(path.dirname(extendPath), { recursive: true });
  await fs.writeFile(
    extendPath,
    `---
default_theme: modern
default_color: green
default_font_family: mono
default_font_size: 17
default_code_theme: nord
mac_code_block: false
show_line_number: true
cite: true
count: true
legend: title-alt
keep_title: true
---
`,
  );

  const fromExtend = resolveRenderOptions();
  assert.equal(fromExtend.theme, "modern");
  assert.equal(fromExtend.primaryColor, COLOR_PRESETS.green);
  assert.equal(fromExtend.fontFamily, FONT_FAMILY_MAP.mono);
  assert.equal(fromExtend.fontSize, "17px");
  assert.equal(fromExtend.codeTheme, "nord");
  assert.equal(fromExtend.isMacCodeBlock, false);
  assert.equal(fromExtend.isShowLineNumber, true);
  assert.equal(fromExtend.citeStatus, true);
  assert.equal(fromExtend.countStatus, true);
  assert.equal(fromExtend.legend, "title-alt");
  assert.equal(fromExtend.keepTitle, true);

  const explicit = resolveRenderOptions({
    theme: "simple",
    fontSize: "18px",
    keepTitle: false,
  });
  assert.equal(explicit.theme, "simple");
  assert.equal(explicit.fontSize, "18px");
  assert.equal(explicit.keepTitle, false);
});
