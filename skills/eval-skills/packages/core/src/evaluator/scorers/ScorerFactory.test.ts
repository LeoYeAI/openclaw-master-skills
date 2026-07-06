import { ScorerFactory } from "./ScorerFactory.js";
import { ExactMatchScorer } from "./ExactMatchScorer.js";
import { ContainsScorer } from "./ContainsScorer.js";
import { JsonSchemaScorer } from "./JsonSchemaScorer.js";
import { LlmJudgeScorer } from "./LlmJudgeScorer.js";

describe("ScorerFactory", () => {
  describe("ExactMatchScorer creation", () => {
    it("should create ExactMatchScorer for 'exact' type", () => {
      const scorer = ScorerFactory.create("exact");

      expect(scorer).toBeInstanceOf(ExactMatchScorer);
      expect(scorer.type).toBe("exact_match");
    });

    it("should create ExactMatchScorer for 'exact_match' type", () => {
      const scorer = ScorerFactory.create("exact_match");

      expect(scorer).toBeInstanceOf(ExactMatchScorer);
      expect(scorer.type).toBe("exact_match");
    });

    it("should pass caseSensitive option to ExactMatchScorer", async () => {
      const scorerSensitive = ScorerFactory.create("exact", { caseSensitive: true });
      const scorerInsensitive = ScorerFactory.create("exact", { caseSensitive: false });

      const resultSensitive = await scorerSensitive.score("Hello", { type: "exact", value: "hello" });
      const resultInsensitive = await scorerInsensitive.score("Hello", { type: "exact", value: "hello" });

      expect(resultSensitive.passed).toBe(false);
      expect(resultInsensitive.passed).toBe(true);
    });

    it("should default caseSensitive to true for ExactMatchScorer", async () => {
      const scorer = ScorerFactory.create("exact");
      const result = await scorer.score("Hello", { type: "exact", value: "hello" });

      expect(result.passed).toBe(false);
    });
  });

  describe("ContainsScorer creation", () => {
    it("should create ContainsScorer for 'contains' type", () => {
      const scorer = ScorerFactory.create("contains");

      expect(scorer).toBeInstanceOf(ContainsScorer);
      expect(scorer.type).toBe("contains");
    });

    it("should pass caseSensitive option to ContainsScorer", async () => {
      const scorerSensitive = ScorerFactory.create("contains", { caseSensitive: true });
      const scorerInsensitive = ScorerFactory.create("contains", { caseSensitive: false });

      const expected = { type: "contains" as const, keywords: ["HELLO"] };
      const resultSensitive = await scorerSensitive.score("hello world", expected);
      const resultInsensitive = await scorerInsensitive.score("hello world", expected);

      expect(resultSensitive.passed).toBe(false);
      expect(resultInsensitive.passed).toBe(true);
    });

    it("should default caseSensitive to false for ContainsScorer", async () => {
      const scorer = ScorerFactory.create("contains");
      const result = await scorer.score("hello world", { type: "contains", keywords: ["HELLO"] });

      expect(result.passed).toBe(true);
    });
  });

  describe("JsonSchemaScorer creation", () => {
    it("should create JsonSchemaScorer for 'schema' type", () => {
      const scorer = ScorerFactory.create("schema");

      expect(scorer).toBeInstanceOf(JsonSchemaScorer);
    });

    it("should create JsonSchemaScorer for 'json_schema' type", () => {
      const scorer = ScorerFactory.create("json_schema");

      expect(scorer).toBeInstanceOf(JsonSchemaScorer);
    });
  });

  describe("LlmJudgeScorer creation", () => {
    it("should create LlmJudgeScorer for 'llm_judge' type", () => {
      const scorer = ScorerFactory.create("llm_judge");

      expect(scorer).toBeInstanceOf(LlmJudgeScorer);
    });

    it("should pass model option to LlmJudgeScorer", () => {
      const scorer = ScorerFactory.create("llm_judge", { model: "gpt-4" });

      expect(scorer).toBeInstanceOf(LlmJudgeScorer);
      // Internal state check - the scorer should have the model configured
    });

    it("should pass baseUrl option to LlmJudgeScorer", () => {
      const scorer = ScorerFactory.create("llm_judge", { baseUrl: "https://custom-api.com" });

      expect(scorer).toBeInstanceOf(LlmJudgeScorer);
    });

    it("should handle undefined options for LlmJudgeScorer", () => {
      const scorer = ScorerFactory.create("llm_judge", {});

      expect(scorer).toBeInstanceOf(LlmJudgeScorer);
    });
  });

  describe("unknown type handling", () => {
    it("should throw error for unknown scorer type", () => {
      expect(() => ScorerFactory.create("unknown_type")).toThrow('Unknown scorer type: "unknown_type"');
    });

    it("should throw error for empty string type", () => {
      expect(() => ScorerFactory.create("")).toThrow('Unknown scorer type: ""');
    });

    it("should throw error for typo in type name", () => {
      expect(() => ScorerFactory.create("excat")).toThrow('Unknown scorer type: "excat"');
    });

    it("should throw error for case mismatch (types are case sensitive)", () => {
      expect(() => ScorerFactory.create("EXACT")).toThrow('Unknown scorer type: "EXACT"');
    });

    it("should throw error for null-like string", () => {
      expect(() => ScorerFactory.create("null")).toThrow('Unknown scorer type: "null"');
    });
  });

  describe("options handling", () => {
    it("should handle undefined options", () => {
      const scorer = ScorerFactory.create("exact");
      expect(scorer).toBeInstanceOf(ExactMatchScorer);
    });

    it("should handle empty options object", () => {
      const scorer = ScorerFactory.create("exact", {});
      expect(scorer).toBeInstanceOf(ExactMatchScorer);
    });

    it("should ignore unknown options", () => {
      const scorer = ScorerFactory.create("exact", { unknownOption: "value" });
      expect(scorer).toBeInstanceOf(ExactMatchScorer);
    });
  });
});
