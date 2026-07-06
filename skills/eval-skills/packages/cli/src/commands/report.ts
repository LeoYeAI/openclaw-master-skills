import * as fs from "node:fs";
import type { Command } from "commander";
import {
  MarkdownReporter,
  HtmlReporter,
  DiffReporter,
} from "@eval-skills/core";
import type { SkillCompletionReport } from "@eval-skills/core";
import { log } from "../utils/output.js";

export function registerReportCommand(program: Command): void {
  const reportCmd = program
    .command("report")
    .description("Convert or compare evaluation reports");

  reportCmd
    .command("convert")
    .description("Convert JSON report to another format")
    .requiredOption("--input <file>", "Input JSON report file")
    .option("--format <format>", "Output format: markdown|html", "markdown")
    .option("--output <file>", "Output file path")
    .action((opts) => {
      try {
        const raw = fs.readFileSync(opts.input, "utf-8");
        const reports: SkillCompletionReport[] = JSON.parse(raw);

        let content: string;
        if (opts.format === "html") {
          content = HtmlReporter.generate(reports);
        } else {
          content = MarkdownReporter.generate(reports);
        }

        if (opts.output) {
          fs.writeFileSync(opts.output, content, "utf-8");
          log.success(`Report written to ${opts.output}`);
        } else {
          console.log(content);
        }
      } catch (err) {
        log.error((err as Error).message);
        process.exit(1);
      }
    });

  reportCmd
    .command("diff <reportA> <reportB>")
    .description("Compare two evaluation reports")
    .option("--label-a <label>", "Label for report A", "Before")
    .option("--label-b <label>", "Label for report B", "After")
    .option("--output <file>", "Output file path")
    .action((reportAPath, reportBPath, opts) => {
      try {
        const rawA = fs.readFileSync(reportAPath, "utf-8");
        const rawB = fs.readFileSync(reportBPath, "utf-8");
        const reportsA: SkillCompletionReport[] = JSON.parse(rawA);
        const reportsB: SkillCompletionReport[] = JSON.parse(rawB);

        const diff = DiffReporter.generateDiff(reportsA, reportsB, opts.labelA, opts.labelB);

        if (opts.output) {
          fs.writeFileSync(opts.output, diff, "utf-8");
          log.success(`Diff report written to ${opts.output}`);
        } else {
          console.log(diff);
        }
      } catch (err) {
        log.error((err as Error).message);
        process.exit(1);
      }
    });
}
