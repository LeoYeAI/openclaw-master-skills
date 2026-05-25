import assert from "node:assert/strict";
import test from "node:test";

import { DEFAULT_STYLE } from "./constants.ts";
import {
  buildCss,
  buildHtmlDocument,
  modifyHtmlStructure,
  normalizeCssText,
  normalizeInlineCss,
  removeFirstHeading,
} from "./html-builder.ts";

test("buildCss injects style variables and concatenates base and theme CSS", () => {
  const css = buildCss("body { color: red; }", ".theme { color: blue; }");

  assert.match(css, /--md-primary-color: #0F4C81;/);
  assert.match(css, /body \{ color: red; \}/);
  assert.match(css, /\.theme \{ color: blue; \}/);
});

test("buildHtmlDocument includes optional meta tags and code theme CSS", () => {
  const html = buildHtmlDocument(
    {
      title: "Doc",
      author: "Baoyu",
      description: "Summary",
    },
    "body { color: red; }",
    "<article>Hello</article>",
    ".hljs { color: blue; }",
  );

  assert.match(html, /<title>Doc<\/title>/);
  assert.match(html, /meta name="author" content="Baoyu"/);
  assert.match(html, /meta name="description" content="Summary"/);
  assert.match(html, /<style>body \{ color: red; \}<\/style>/);
  assert.match(html, /<style>\.hljs \{ color: blue; \}<\/style>/);
  assert.match(html, /<article>Hello<\/article>/);
});

test("normalizeCssText and normalizeInlineCss replace variables and strip declarations", () => {
  const rawCss = `
:root { --md-primary-color: #000; --md-font-size: 12px; --foreground: 0 0% 5%; }
.box { color: var(--md-primary-color); font-size: var(--md-font-size); background: hsl(var(--foreground)); }
`;

  const normalizedCss = normalizeCssText(rawCss, DEFAULT_STYLE);
  assert.match(normalizedCss, /color: #0F4C81/);
  assert.match(normalizedCss, /font-size: 16px/);
  assert.match(normalizedCss, /background: #3f3f3f/);
  assert.doesNotMatch(normalizedCss, /--md-primary-color/);

  const normalizedHtml = normalizeInlineCss(
    `<style>${rawCss}</style><div style="color: var(--md-primary-color)"></div>`,
    DEFAULT_STYLE,
  );
  assert.match(normalizedHtml, /color: #0F4C81/);
  assert.doesNotMatch(normalizedHtml, /var\(--md-primary-color\)/);
});

test("HTML structure helpers hoist nested lists and remove the first heading", () => {
  const nestedList = `<ul><li>Parent<ul><li>Child</li></ul></li></ul>`;
  assert.equal(
    modifyHtmlStructure(nestedList),
    `<ul><li>Parent</li><ul><li>Child</li></ul></ul>`,
  );

  const html = `<h1>Title</h1><p>Intro</p><h2>Sub</h2>`;
  assert.equal(removeFirstHeading(html), `<p>Intro</p><h2>Sub</h2>`);
});
