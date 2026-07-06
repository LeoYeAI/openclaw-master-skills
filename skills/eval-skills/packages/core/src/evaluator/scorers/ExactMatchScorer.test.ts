import { ExactMatchScorer } from "./ExactMatchScorer.js";
import type { ExpectedOutput } from "../../types/index.js";

function exact(value: unknown): ExpectedOutput {
  return { type: "exact", value };
}

describe("ExactMatchScorer", () => {
  const scorer = new ExactMatchScorer();

  it("returns score 1.0 for exact match", async () => {
    const result = await scorer.score("hello", exact("hello"));
    expect(result.score).toBe(1.0);
    expect(result.passed).toBe(true);
  });

  it("returns score 0.0 for mismatch with reason", async () => {
    const result = await scorer.score("hello", exact("world"));
    expect(result.score).toBe(0.0);
    expect(result.passed).toBe(false);
    expect(result.reason).toContain("world");
    expect(result.reason).toContain("hello");
  });

  it("extracts value from { result: ... }", async () => {
    const result = await scorer.score({ result: "42" }, exact("42"));
    expect(result.score).toBe(1.0);
    expect(result.passed).toBe(true);
  });

  it("extracts value from { output: ... }", async () => {
    const result = await scorer.score({ output: "42" }, exact("42"));
    expect(result.score).toBe(1.0);
  });

  it("extracts value from { answer: ... }", async () => {
    const result = await scorer.score({ answer: "42" }, exact("42"));
    expect(result.score).toBe(1.0);
  });

  it("is case sensitive by default", async () => {
    const result = await scorer.score("Hello", exact("hello"));
    expect(result.passed).toBe(false);
  });

  it("supports case insensitive mode", async () => {
    const insensitive = new ExactMatchScorer({ caseSensitive: false });
    const result = await insensitive.score("Hello", exact("hello"));
    expect(result.score).toBe(1.0);
    expect(result.passed).toBe(true);
  });

  it("handles numeric values by converting to string", async () => {
    const result = await scorer.score(42, exact(42));
    expect(result.score).toBe(1.0);
  });

  it("trims whitespace", async () => {
    const result = await scorer.score("  hello  ", exact(" hello "));
    expect(result.score).toBe(1.0);
  });

  it("handles null output", async () => {
    const result = await scorer.score(null, exact("null"));
    expect(result.score).toBe(1.0);
  });
});
