import { AdapterRegistry } from "../adapters/AdapterRegistry.js";
import { TaskExecutor } from "./TaskExecutor.js";
import { ScorerFactory } from "./scorers/ScorerFactory.js";
import type { Skill, Task, TaskResult, ExpectedOutput, JSONSchema } from "../types/index.js";
import { nanoid } from "nanoid";
import * as fs from "node:fs";
import * as path from "node:path";

export interface OnDemandConfig {
  skillPath: string;
  input: Record<string, unknown>;
  scoringStrategy: {
    type: "llm_judge" | "schema" | "regex" | "custom";
    judgePrompt?: string;
    schema?: JSONSchema;
    patterns?: string[];
    customScorerPath?: string;
  };
  timeoutMs?: number;
  llmConfig?: {
      model?: string;
      baseUrl?: string;
  };
}

export class OnDemandEvaluator {
  private adapterRegistry: AdapterRegistry;

  constructor() {
    this.adapterRegistry = new AdapterRegistry();
  }

  async evaluate(config: OnDemandConfig): Promise<TaskResult> {
    // 1. Load Skill
    let skill: Skill;
    let absPath = path.resolve(config.skillPath);
    
    if (fs.existsSync(absPath)) {
        const stat = fs.statSync(absPath);
        if (stat.isDirectory()) {
            absPath = path.join(absPath, "skill.json");
            if (!fs.existsSync(absPath)) {
                throw new Error(`skill.json not found in directory: ${config.skillPath}`);
            }
        }

        const content = fs.readFileSync(absPath, "utf-8");
        try {
            skill = JSON.parse(content);
        } catch (e) {
            throw new Error(`Failed to parse skill JSON: ${(e as Error).message}`);
        }

        // Handle subprocess entrypoint resolution
        if (skill.adapterType === "subprocess" && skill.entrypoint) {
            const skillDir = path.dirname(absPath);
            const parts = skill.entrypoint.match(/(?:[^\s"]+|"[^"]*")+/g) || [];
            if (parts.length > 1) {
              const scriptFile = parts.slice(1).join(" ").replace(/^"|"$/g, "");
              const absScript = path.resolve(skillDir, scriptFile);
              if (fs.existsSync(absScript)) {
                skill.entrypoint = `${parts[0]} "${absScript}"`;
              }
            }
        }
    } else {
        throw new Error(`Skill file not found: ${config.skillPath}`);
    }

    // 2. Construct Task
    const taskId = nanoid();
    const evaluatorType = config.scoringStrategy.type;
    
    const expectedOutput: ExpectedOutput = {
        type: evaluatorType,
        judgePrompt: config.scoringStrategy.judgePrompt,
        schema: config.scoringStrategy.schema,
        patterns: config.scoringStrategy.patterns,
        customScorerPath: config.scoringStrategy.customScorerPath,
    };

    const task: Task = {
        id: taskId,
        description: "On-demand evaluation task",
        inputData: config.input,
        expectedOutput,
        evaluator: {
            type: evaluatorType,
            customScorerPath: config.scoringStrategy.customScorerPath
        },
        timeoutMs: config.timeoutMs ?? 30000,
    };

    // 3. Execute
    const executor = new TaskExecutor({
        concurrency: 1,
        timeoutMs: task.timeoutMs,
        retries: 0
    });

    const results = await executor.execute(
        [{ skill, task, runId: 1 }],
        (s) => this.adapterRegistry.resolveForSkill(s),
        (t) => ScorerFactory.create(t.evaluator.type, config.llmConfig)
    );

    if (results.length === 0 || !results[0]) {
        throw new Error("Evaluation failed to produce results");
    }

    return results[0];
  }
}
