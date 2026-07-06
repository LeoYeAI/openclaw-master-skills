import * as fs from "node:fs";
import type { Command } from "commander";
import { SkillSelector, SkillStore } from "@eval-skills/core";
import type { SkillCompletionReport, SelectStrategy } from "@eval-skills/core";
import { log, printTable } from "../utils/output.js";
import { loadStrategy } from "../utils/config.js";

export function registerSelectCommand(program: Command): void {
  program
    .command("select")
    .description("Filter and rank Skills based on evaluation reports")
    .requiredOption("--from <path>", "Candidate Skills directory or JSON file")
    .option("--strategy <file>", "SelectStrategy YAML/JSON file")
    .option("--reports <file>", "Evaluation reports JSON file")
    .option("--min-completion <rate>", "Min completion rate (overrides strategy)")
    .option("--top-k <n>", "Return top K results")
    .option("--output <file>", "Output file (default: stdout)")
    .action((opts) => {
      try {
        // 加载 Skills
        const store = new SkillStore();
        const skills = store.loadDir(opts.from);

        // 加载报告
        let reports: SkillCompletionReport[] = [];
        if (opts.reports) {
          const raw = fs.readFileSync(opts.reports, "utf-8");
          reports = JSON.parse(raw);
        }

        // 加载策略
        let strategy: SelectStrategy = {
          filters: {},
          sortBy: "compositeScore",
          order: "desc",
        };
        if (opts.strategy) {
          strategy = loadStrategy(opts.strategy);
        }

        // 覆盖参数
        if (opts.minCompletion) {
          strategy.filters.minCompletionRate = parseFloat(opts.minCompletion);
        }
        if (opts.topK) {
          strategy.topK = parseInt(opts.topK, 10);
        }

        const result = SkillSelector.select(skills, reports, strategy);

        if (result.selected.length === 0) {
          log.warn("No skills passed the filter criteria.");
          return;
        }

        log.info(`Selected ${result.selected.length} of ${result.total} skills:`);
        printTable(
          ["Rank", "Skill ID", "Completion", "Error Rate", "Score"],
          result.selected.map((s) => [
            String(s.rank),
            s.skill.id,
            `${(s.report.summary.completionRate * 100).toFixed(1)}%`,
            `${(s.report.summary.errorRate * 100).toFixed(1)}%`,
            s.report.summary.compositeScore.toFixed(3),
          ]),
        );

        // 输出到文件
        if (opts.output) {
          const output = JSON.stringify(
            result.selected.map((s) => s.skill),
            null,
            2,
          );
          fs.writeFileSync(opts.output, output, "utf-8");
          log.success(`Results written to ${opts.output}`);
        }
      } catch (err) {
        log.error((err as Error).message);
        process.exit(1);
      }
    });
}
