import { CustomScorer } from "./CustomScorer.js";
import path from "node:path";
import fs from "node:fs";
import { tmpdir } from "node:os";

describe("CustomScorer", () => {
  let tmpDir: string;
  let scorerPath: string;

  beforeEach(() => {
    tmpDir = fs.mkdtempSync(path.join(tmpdir(), "custom-scorer-test-"));
    scorerPath = path.join(tmpDir, "my-scorer.js");
  });

  afterEach(() => {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  });

  it("should load and execute a valid custom scorer", async () => {
    const code = `
      export default function(output, expected) {
        return {
          passed: output === expected.value,
          score: output === expected.value ? 1 : 0,
          reason: "Custom match"
        };
      }
    `;
    fs.writeFileSync(scorerPath, code);

    const scorer = new CustomScorer();
    const result = await scorer.score("foo", {
      type: "custom",
      value: "foo",
      customScorerPath: scorerPath,
    });

    expect(result.passed).toBe(true);
    expect(result.score).toBe(1);
    expect(result.reason).toBe("Custom match");
  });

  it("should handle boolean return value", async () => {
    const code = `
      export default function(output, expected) {
        return output === expected.value;
      }
    `;
    fs.writeFileSync(scorerPath, code);

    const scorer = new CustomScorer();
    const result = await scorer.score("foo", {
      type: "custom",
      value: "foo",
      customScorerPath: scorerPath,
    });

    expect(result.passed).toBe(true);
    expect(result.score).toBe(1.0);
  });

  it("should fail if customScorerPath is missing", async () => {
    const scorer = new CustomScorer();
    const result = await scorer.score("foo", { type: "custom" });
    expect(result.passed).toBe(false);
    expect(result.reason).toContain("Missing 'customScorerPath'");
  });

  it("should fail if file does not exist", async () => {
    const scorer = new CustomScorer();
    const result = await scorer.score("foo", {
      type: "custom",
      customScorerPath: "/non/existent/path.js",
    });
    expect(result.passed).toBe(false);
    expect(result.reason).toContain("Custom scorer error");
  });
});
