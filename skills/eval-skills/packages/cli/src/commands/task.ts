import { Command } from "commander";
import { OnDemandEvaluator, type OnDemandConfig } from "@eval-skills/core";
import { log } from "../utils/output.js";

export function registerTaskCommand(program: Command): void {
  program
    .command("task")
    .description("Evaluate a single task on demand")
    .requiredOption("--skill <path>", "Path to skill.json or skill directory")
    .requiredOption("--input <json>", "Input JSON string")
    .option("--judge <prompt>", "LLM judge prompt")
    .option("--schema <json>", "JSON Schema for validation")
    .option("--regex <patterns...>", "Regex patterns to match")
    .option("--custom <path>", "Path to custom scorer module")
    .option("--timeout <ms>", "Timeout in ms", "30000")
    .option("--model <name>", "LLM model name (for judge)")
    .option("--output <format>", "Output format: json|text", "text")
    .action(async (opts) => {
      try {
        let input: Record<string, unknown>;
        try {
            input = JSON.parse(opts.input);
        } catch (e) {
            throw new Error("Invalid input JSON");
        }

        let strategy: OnDemandConfig["scoringStrategy"];

        if (opts.judge) {
            strategy = { type: "llm_judge", judgePrompt: opts.judge };
        } else if (opts.schema) {
            try {
                strategy = { type: "schema", schema: JSON.parse(opts.schema) };
            } catch (e) {
                throw new Error("Invalid schema JSON");
            }
        } else if (opts.regex) {
            strategy = { type: "regex", patterns: opts.regex };
        } else if (opts.custom) {
            strategy = { type: "custom", customScorerPath: opts.custom };
        } else {
            throw new Error("One of --judge, --schema, --regex, or --custom must be provided");
        }

        const config: OnDemandConfig = {
            skillPath: opts.skill,
            input,
            scoringStrategy: strategy,
            timeoutMs: parseInt(opts.timeout, 10),
            llmConfig: opts.model ? { model: opts.model } : undefined
        };

        const evaluator = new OnDemandEvaluator();
        const result = await evaluator.evaluate(config);

        if (opts.output === "json") {
            console.log(JSON.stringify(result, null, 2));
        } else {
            log.info(`Skill: ${result.skillId}`);
            if (result.status === "pass") {
                log.success(`Status: ${result.status.toUpperCase()}`);
            } else {
                log.error(`Status: ${result.status.toUpperCase()}`);
            }
            log.info(`Score: ${result.score}`);
            log.info(`Latency: ${result.latencyMs}ms`);
            
            if (result.reason) {
                log.info(`Reason: ${result.reason}`);
            }
            if (result.error) {
                log.error(`Error: ${result.error}`);
            }
            if (result.output) {
                log.info(`Output: ${JSON.stringify(result.output, null, 2)}`);
            }
            if (result.usage) {
                log.info(`Tokens: ${result.usage.totalTokens} (Prompt: ${result.usage.promptTokens}, Completion: ${result.usage.completionTokens})`);
            }
        }

      } catch (err) {
        log.error(`Task evaluation failed: ${(err as Error).message}`);
        process.exit(1);
      }
    });
}
