import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { LlmJudgeScorer } from "./LlmJudgeScorer.js";
import OpenAI from "openai";

// Mock OpenAI
const mockCreate = vi.fn();
vi.mock("openai", () => {
    return {
        default: class {
            chat = {
                completions: {
                    create: mockCreate
                }
            }
        }
    }
});

describe("LlmJudgeScorer", () => {
    beforeEach(() => {
        process.env.EVAL_SKILLS_LLM_KEY = "test-key";
        vi.clearAllMocks();
    });

    afterEach(() => {
        delete process.env.EVAL_SKILLS_LLM_KEY;
        delete process.env.OPENAI_API_KEY;
    });

    it("should pass when LLM returns high score", async () => {
        mockCreate.mockResolvedValue({
            choices: [{ message: { content: "8.5" } }]
        });

        const scorer = new LlmJudgeScorer({ passThreshold: 0.8 });
        const result = await scorer.score("some output", { type: "llm_judge", judgePrompt: "Rate it" });

        expect(result.score).toBe(0.85);
        expect(result.passed).toBe(true);
        expect(mockCreate).toHaveBeenCalled();
    });

    it("should fail when LLM returns low score", async () => {
        mockCreate.mockResolvedValue({
            choices: [{ message: { content: "0.5" } }]
        }); // 0.5/10 = 0.05 normalized

        const scorer = new LlmJudgeScorer({ passThreshold: 0.5 });
        const result = await scorer.score("bad output", { type: "llm_judge" });

        expect(result.score).toBe(0.05);
        expect(result.passed).toBe(false);
    });

    it("should handle non-numeric response", async () => {
        mockCreate.mockResolvedValue({
            choices: [{ message: { content: "I cannot rate this." } }]
        });

        const scorer = new LlmJudgeScorer();
        const result = await scorer.score("output", { type: "llm_judge" });

        expect(result.score).toBe(0.0);
        expect(result.passed).toBe(false);
        expect(result.reason).toContain("non-numeric response");
    });

    it("should fallback to OPENAI_API_KEY if EVAL_SKILLS_LLM_KEY missing", async () => {
        delete process.env.EVAL_SKILLS_LLM_KEY;
        process.env.OPENAI_API_KEY = "fallback-key";
        
        mockCreate.mockResolvedValue({
            choices: [{ message: { content: "10" } }]
        });

        const scorer = new LlmJudgeScorer();
        const result = await scorer.score("output", { type: "llm_judge" });
        
        expect(result.score).toBe(1.0);
    });

    it("should throw if no API key present", async () => {
        delete process.env.EVAL_SKILLS_LLM_KEY;
        delete process.env.OPENAI_API_KEY;
        
        const scorer = new LlmJudgeScorer();
        await expect(scorer.score("output", { type: "llm_judge" })).rejects.toThrow("environment variable is not set");
    });
});
