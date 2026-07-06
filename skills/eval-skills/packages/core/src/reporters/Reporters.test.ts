import { describe, it, expect } from "vitest";
import { JsonReporter } from "./JsonReporter.js";
import { CsvReporter } from "./CsvReporter.js";
import { MarkdownReporter } from "./MarkdownReporter.js";
import { HtmlReporter } from "./HtmlReporter.js";
import type { SkillCompletionReport } from "../types/index.js";

const mockReport: SkillCompletionReport = {
  skillId: "skill-1",
  benchmarkId: "bench-1",
  summary: {
    completionRate: 0.8,
    partialScore: 0.75,
    errorRate: 0.1,
    consistencyScore: 0.9,
    compositeScore: 0.85,
    tokenCost: {
        promptTokens: 100,
        completionTokens: 50,
        totalTokens: 150
    }
  },
  latency: {
    p50Ms: 100,
    p90Ms: 200,
    p95Ms: 250,
    p99Ms: 300,
    avgMs: 150,
    minMs: 50,
    maxMs: 500,
  },
  taskResults: [
    {
      skillId: "skill-1",
      taskId: "task-1",
      runId: 1,
      status: "pass",
      score: 1.0,
      latencyMs: 100,
      scorerType: "exact",
    },
    {
      skillId: "skill-1",
      taskId: "task-2",
      runId: 1,
      status: "fail",
      score: 0.5,
      latencyMs: 200,
      scorerType: "contains",
    },
  ],
  evaluatorMetadata: {},
};

describe("Reporters", () => {
  describe("JsonReporter", () => {
    it("should generate valid JSON string", () => {
      const json = JsonReporter.generate([mockReport]);
      const parsed = JSON.parse(json);
      expect(parsed).toHaveLength(1);
      expect(parsed[0].skillId).toBe("skill-1");
    });
  });

  describe("CsvReporter", () => {
    it("should generate CSV with headers and escaped values", () => {
      const csv = CsvReporter.generate([mockReport]);
      const lines = csv.split("\n");
      expect(lines[0]).toContain("skillId,benchmarkId");
      expect(lines[1]).toContain("skill-1,bench-1");
    });
  });

  describe("MarkdownReporter", () => {
    it("should generate markdown table", () => {
      const md = MarkdownReporter.generate([mockReport]);
      expect(md).toContain("# eval-skills Report");
      expect(md).toContain("skill-1");
      expect(md).toContain("80.0%");
    });
  });

  describe("HtmlReporter", () => {
    it("should generate HTML with styles", async () => {
      const html = await HtmlReporter.generate([mockReport]);
      expect(html).toContain("<!DOCTYPE html>");
      expect(html).toContain("<style>");
      expect(html).toContain("skill-1");
      expect(html).toContain("bench-1");
    });
  });
});
