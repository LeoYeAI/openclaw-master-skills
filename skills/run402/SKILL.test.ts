import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml } from "yaml";

const __dirname = dirname(fileURLToPath(import.meta.url));
const raw = readFileSync(join(__dirname, "SKILL.md"), "utf-8");

// Split frontmatter from body
const fmMatch = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
assert.ok(fmMatch, "SKILL.md must have YAML frontmatter delimited by ---");

const frontmatter = parseYaml(fmMatch[1]);
const body = fmMatch[2];

// ── Frontmatter ────────────────────────────────────────────────

describe("frontmatter", () => {
  it("has required name field", () => {
    assert.equal(frontmatter.name, "run402");
  });

  it("has required description field", () => {
    assert.ok(
      typeof frontmatter.description === "string" &&
        frontmatter.description.length > 0,
      "description must be a non-empty string",
    );
  });

  it("has openclaw metadata", () => {
    assert.ok(frontmatter.metadata?.openclaw, "metadata.openclaw must exist");
  });

  it("has valid emoji", () => {
    assert.equal(frontmatter.metadata.openclaw.emoji, "🐘");
  });

  it("has homepage URL", () => {
    assert.ok(
      frontmatter.metadata.openclaw.homepage.startsWith("https://"),
      "homepage must be an HTTPS URL",
    );
  });

  it("requires npx binary", () => {
    assert.deepEqual(frontmatter.metadata.openclaw.requires.bins, ["npx"]);
  });

  it("has node install spec for run402-mcp", () => {
    const install = frontmatter.metadata.openclaw.install;
    assert.ok(Array.isArray(install), "install must be an array");
    assert.equal(install.length, 1);
    assert.equal(install[0].kind, "node");
    assert.equal(install[0].package, "run402-mcp");
    assert.ok(
      install[0].bins.includes("run402-mcp"),
      "bins must include run402-mcp",
    );
  });

  it("has primaryEnv set to RUN402_API_BASE", () => {
    assert.equal(frontmatter.metadata.openclaw.primaryEnv, "RUN402_API_BASE");
  });
});

// ── Slug validation ────────────────────────────────────────────

describe("skill slug", () => {
  it("matches ^[a-z0-9][a-z0-9-]*$", () => {
    assert.match(frontmatter.name, /^[a-z0-9][a-z0-9-]*$/);
  });
});

// ── Body — tool references ─────────────────────────────────────

const TOOLS = [
  "provision_postgres_project",
  "run_sql",
  "rest_query",
  "upload_file",
  "renew_project",
];

describe("body tool references", () => {
  for (const tool of TOOLS) {
    it(`references tool: ${tool}`, () => {
      assert.ok(body.includes(tool), `body must mention ${tool}`);
    });
  }
});

// ── Body — required sections ───────────────────────────────────

const REQUIRED_SECTIONS = [
  "Standard Workflow",
  "Payment Handling",
  "Tips & Guardrails",
  "Tools Reference",
  "Wallet Setup",
];

describe("body required sections", () => {
  for (const section of REQUIRED_SECTIONS) {
    it(`has section: ${section}`, () => {
      assert.ok(body.includes(section), `body must contain "${section}" section`);
    });
  }
});

// ── Markdown integrity ─────────────────────────────────────────

describe("markdown integrity", () => {
  it("has no unclosed fenced code blocks", () => {
    const fences = body.match(/^```/gm) || [];
    assert.equal(
      fences.length % 2,
      0,
      `found ${fences.length} fence markers — expected an even number`,
    );
  });

  it("starts with a heading", () => {
    const firstLine = body.trimStart().split("\n")[0];
    assert.ok(firstLine.startsWith("#"), "body should start with a markdown heading");
  });
});
