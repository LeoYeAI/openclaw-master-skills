import * as path from "node:path";
import type { Command } from "commander";
import ora from "ora";
import {
  EvaluationEngine,
  BenchmarkRegistry,
  JsonReporter,
  MarkdownReporter,
  HtmlReporter,
  CsvReporter,
  SqliteStore,
} from "@eval-skills/core";
import type { SkillCompletionReport, ReportFormat } from "@eval-skills/core";
import { log } from "../utils/output.js";
import { loadGlobalConfig, buildEvalConfig } from "../utils/config.js";
import { writeReports } from "../utils/reportWriter.js";

export function registerEvalCommand(program: Command): void {
  program
    .command("eval")
    .description("Evaluate Skills against a Benchmark")
    .requiredOption("--skills <paths...>", "Skill paths (files or directories)")
    .option("--benchmark <id|path>", "Benchmark ID or local path", "coding-easy")
    .option("--tasks <file>", "Custom tasks file (replaces benchmark)")
    .option("--concurrency <n>", "Concurrency level", "4")
    .option("--timeout <ms>", "Per-task timeout in ms", "30000")
    .option("--retries <n>", "Retry count on failure", "0")
    .option("--runs <n>", "Number of runs for consistency check", "1")
    .option("--evaluator <type>", "Scorer type: exact_match|contains|llm_judge", "exact")
    .option("--exit-on-fail", "Exit with code 1 if below threshold")
    .option("--min-completion <rate>", "Threshold for exit-on-fail", "0.7")
    .option("--output-dir <dir>", "Report output directory", "./reports")
    .option("--format <formats...>", "Output formats: json|markdown|html|csv", ["json", "markdown"])
    .option("--dry-run", "Validate config only, do not execute")
    .option("--benchmarks-dir <dir>", "Built-in benchmarks directory")
    .option("-c, --config <path>", "Config file path")
    .option("--store <path>", "SQLite store path", "./eval-skills.db")
    .action(async (opts) => {
      const spinner = ora({
        text: "Initializing evaluation...",
        isEnabled: !log.json // Disable spinner in JSON mode
      }).start();

      let sqliteStore: SqliteStore | undefined;
      try {
        const globalConfig = loadGlobalConfig(opts.config);
        const evalConfig = buildEvalConfig(
          {
            skills: opts.skills,
            benchmark: opts.benchmark,
            tasks: opts.tasks,
            concurrency: parseInt(opts.concurrency, 10),
            timeout: parseInt(opts.timeout, 10),
            retries: parseInt(opts.retries, 10),
            runs: parseInt(opts.runs, 10),
            evaluator: opts.evaluator,
            exitOnFail: opts.exitOnFail,
            minCompletion: parseFloat(opts.minCompletion),
            outputDir: opts.outputDir,
            format: opts.format,
            dryRun: opts.dryRun,
          },
          globalConfig,
        );

        if (opts.store) {
            sqliteStore = new SqliteStore(path.resolve(opts.store));
        }

        // 加载内置 benchmarks
        const benchmarkRegistry = new BenchmarkRegistry();
        const benchmarksDir = opts.benchmarksDir ?? path.resolve(process.cwd(), "benchmarks");
        try {
          benchmarkRegistry.loadBuiltins(benchmarksDir);
        } catch {
          // 内置 benchmarks 可能不存在
        }

        const engine = new EvaluationEngine({ benchmarkRegistry, sqliteStore });

        // 绑定进度事件
        engine.on("progress", ({ completed, total, percent }) => {
          spinner.text = `Evaluating... ${completed}/${total} tasks (${percent}%)`;
        });

        engine.on("task:error", ({ skillId, taskId, error }) => {
          spinner.warn(`Task ${taskId} for ${skillId} failed: ${error}`);
          spinner.start();
        });

        spinner.text = "Running evaluation...";
        const reports = await engine.evaluate(evalConfig);

        spinner.succeed(`Evaluation complete! ${reports.length} skill(s) evaluated.`);

        // 输出报告
        await writeReports({
            reports,
            outputDir: evalConfig.output.dir,
            formats: evalConfig.output.formats
        });

        // 打印摘要
        printSummary(reports);

        // exit-on-fail 检查
        if (evalConfig.exitOnFail?.enabled) {
          const minRate = evalConfig.exitOnFail.minCompletionRate;
          const failedSkills = reports.filter(
            (r) => r.summary.completionRate < minRate,
          );
          if (failedSkills.length > 0) {
            log.error(
              `${failedSkills.length} skill(s) below threshold (${minRate}): ${failedSkills.map((s) => s.skillId).join(", ")}`,
            );
            process.exit(1);
          }
        }
      } catch (err) {
        spinner.fail((err as Error).message);
        process.exit(1);
      } finally {
        if (sqliteStore) {
            sqliteStore.close();
        }
      }
    });
}

function printSummary(reports: SkillCompletionReport[]): void {
  console.log("");
  const sorted = [...reports].sort(
    (a, b) => b.summary.compositeScore - a.summary.compositeScore,
  );
  for (const r of sorted) {
    const s = r.summary;
    const cr = (s.completionRate * 100).toFixed(1);
    const er = (s.errorRate * 100).toFixed(1);
    const cs = s.compositeScore.toFixed(3);
    log.info(`${r.skillId} — CR: ${cr}% | ER: ${er}% | Score: ${cs}`);
  }
  console.log("");
}
