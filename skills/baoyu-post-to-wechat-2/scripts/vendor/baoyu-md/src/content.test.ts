import assert from "node:assert/strict";
import test from "node:test";

import {
  extractSummaryFromBody,
  extractTitleFromMarkdown,
  parseFrontmatter,
  pickFirstString,
  serializeFrontmatter,
  stripWrappingQuotes,
  toFrontmatterString,
} from "./content.ts";

test("parseFrontmatter extracts YAML fields and strips wrapping quotes", () => {
  const input = `---
title: "Hello World"
author: ‘Baoyu’
summary: plain text
---
# Heading

Body`;

  const result = parseFrontmatter(input);

  assert.deepEqual(result.frontmatter, {
    title: "Hello World",
    author: "Baoyu",
    summary: "plain text",
  });
  assert.match(result.body, /^# Heading/);
});

test("parseFrontmatter returns original content when no frontmatter exists", () => {
  const input = "# No frontmatter";
  assert.deepEqual(parseFrontmatter(input), {
    frontmatter: {},
    body: input,
  });
});

test("serializeFrontmatter renders YAML only when fields exist", () => {
  assert.equal(serializeFrontmatter({}), "");
  assert.equal(
    serializeFrontmatter({ title: "Hello", author: "Baoyu" }),
    "---\ntitle: Hello\nauthor: Baoyu\n---\n",
  );
});

test("quote and frontmatter string helpers normalize mixed scalar values", () => {
  assert.equal(stripWrappingQuotes(`" quoted "`), "quoted");
  assert.equal(stripWrappingQuotes("“ 中文标题 ”"), "中文标题");
  assert.equal(stripWrappingQuotes("plain"), "plain");

  assert.equal(toFrontmatterString("'hello'"), "hello");
  assert.equal(toFrontmatterString(42), "42");
  assert.equal(toFrontmatterString(false), "false");
  assert.equal(toFrontmatterString({}), undefined);

  assert.equal(
    pickFirstString({ summary: 123, title: "" }, ["title", "summary"]),
    "123",
  );
});

test("markdown title and summary extraction skip non-body content and clean formatting", () => {
  const markdown = `
![cover](cover.png)
## “My Title”

Body paragraph
`;
  assert.equal(extractTitleFromMarkdown(markdown), "My Title");

  const summary = extractSummaryFromBody(
    `
# Heading
> quote
- list
1. ordered
\`\`\`
code
\`\`\`
This is **the first paragraph** with [a link](https://example.com) and \`inline code\` that should be summarized cleanly.
`,
    70,
  );

  assert.equal(
    summary,
    "This is the first paragraph with a link and inline code that should...",
  );
});
