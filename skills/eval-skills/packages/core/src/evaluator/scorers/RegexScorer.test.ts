import { describe, it, expect } from "vitest";
import { RegexScorer } from "./RegexScorer.js";

describe("RegexScorer", () => {
    it("should pass when all patterns match", async () => {
        const scorer = new RegexScorer();
        const result = await scorer.score("Hello world", {
            type: "regex",
            patterns: ["Hello", "world"]
        });
        expect(result.score).toBe(1.0);
        expect(result.passed).toBe(true);
    });

    it("should partially score when some patterns match", async () => {
        const scorer = new RegexScorer();
        const result = await scorer.score("Hello world", {
            type: "regex",
            patterns: ["Hello", "foo"]
        });
        expect(result.score).toBe(0.5);
        expect(result.passed).toBe(false);
    });

    it("should fail when no patterns match", async () => {
        const scorer = new RegexScorer();
        const result = await scorer.score("Hello world", {
            type: "regex",
            patterns: ["foo", "bar"]
        });
        expect(result.score).toBe(0.0);
        expect(result.passed).toBe(false);
    });
});
