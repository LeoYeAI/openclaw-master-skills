import { describe, it, expect } from "vitest";
import { JsonSchemaScorer } from "./JsonSchemaScorer.js";

describe("JsonSchemaScorer", () => {
    it("should pass when output matches schema", async () => {
        const scorer = new JsonSchemaScorer();
        const schema = {
            type: "object",
            properties: {
                name: { type: "string" },
                age: { type: "number" }
            },
            required: ["name", "age"]
        };
        const output = { name: "John", age: 30 };
        
        const result = await scorer.score(output, { type: "schema", schema });
        expect(result.score).toBe(1.0);
        expect(result.passed).toBe(true);
    });

    it("should fail when output does not match schema", async () => {
        const scorer = new JsonSchemaScorer();
        const schema = {
            type: "object",
            properties: {
                name: { type: "string" }
            },
            required: ["name"]
        };
        const output = { age: 30 };
        
        const result = await scorer.score(output, { type: "schema", schema });
        expect(result.score).toBe(0.0);
        expect(result.passed).toBe(false);
        expect(result.reason).toContain("Schema validation failed");
    });

    it("should parse string output as JSON", async () => {
        const scorer = new JsonSchemaScorer();
        const schema = { type: "array" };
        const output = "[1, 2, 3]";
        
        const result = await scorer.score(output, { type: "schema", schema });
        expect(result.score).toBe(1.0);
        expect(result.passed).toBe(true);
    });

    it("should fail if string output is invalid JSON", async () => {
        const scorer = new JsonSchemaScorer();
        const schema = { type: "object" };
        const output = "{ invalid json";
        
        const result = await scorer.score(output, { type: "schema", schema });
        expect(result.score).toBe(0.0);
        expect(result.passed).toBe(false);
        expect(result.reason).toContain("Output is not valid JSON");
    });

    it("should return 0 if no schema provided", async () => {
        const scorer = new JsonSchemaScorer();
        const result = await scorer.score({}, { type: "schema" });
        expect(result.score).toBe(0.0);
        expect(result.passed).toBe(false);
        expect(result.reason).toContain("No schema provided");
    });
});
