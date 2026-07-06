import { ContainsScorer } from "./ContainsScorer.js";
import type { ExpectedOutput } from "../../types/index.js";

function contains(keywords: string[]): ExpectedOutput {
  return { type: "contains", keywords };
}

describe("ContainsScorer", () => {
  const scorer = new ContainsScorer();

  it("returns score 1.0 when all keywords present", async () => {
    const result = await scorer.score(
      "The quick brown fox jumps over the lazy dog",
      contains(["quick", "fox", "dog"]),
    );
    expect(result.score).toBe(1.0);
    expect(result.passed).toBe(true);
  });

  it("returns partial score for partial match", async () => {
    const result = await scorer.score("hello world", contains(["hello", "earth"]));
    expect(result.score).toBe(0.5);
    expect(result.passed).toBe(false);
    expect(result.reason).toContain("earth");
  });

  it("returns 0 when no keywords match", async () => {
    const result = await scorer.score("abc", contains(["xyz", "123"]));
    expect(result.score).toBe(0);
    expect(result.passed).toBe(false);
  });

  it("returns score 1.0 for empty keywords list", async () => {
    const result = await scorer.score("anything", contains([]));
    expect(result.score).toBe(1.0);
    expect(result.passed).toBe(true);
    expect(result.reason).toContain("No keywords");
  });

  it("is case insensitive by default", async () => {
    const result = await scorer.score("Hello World", contains(["hello", "world"]));
    expect(result.score).toBe(1.0);
  });

  it("supports case sensitive mode", async () => {
    const sensitive = new ContainsScorer({ caseSensitive: true });
    const result = await sensitive.score("Hello World", contains(["hello"]));
    expect(result.score).toBe(0);
    expect(result.passed).toBe(false);
  });

  it("works with object output (JSON.stringify)", async () => {
    const output = { result: "Hinton and Hopfield won the Nobel Prize" };
    const result = await scorer.score(output, contains(["Hinton", "Hopfield"]));
    expect(result.score).toBe(1.0);
  });

  it("lists missing keywords in reason", async () => {
    const result = await scorer.score("aaa", contains(["aaa", "bbb", "ccc"]));
    expect(result.reason).toContain("bbb");
    expect(result.reason).toContain("ccc");
    expect(result.reason).toContain("1/3");
  });
});
