import * as path from "node:path";
import * as fs from "node:fs";
import type { Command } from "commander";
import ora from "ora";
import {
  EvaluationEngine,
  BenchmarkRegistry,
  SkillStore,
  SkillFinder,
  SkillSelector,
  JsonReporter,
  MarkdownReporter,
  HtmlReporter,
  CsvReporter,
  SqliteStore,
} from "@eval-skills/core";
import type {
  SkillCompletionReport,
  ReportFormat,
  SelectStrategy,
  Skill,
} from "@eval-skills/core";
import { log } from "../utils/output.js";
import { loadGlobalConfig, loadStrategy, buildEvalConfig } from "../utils/config.js";
import { writeReports } from "../utils/reportWriter.js";

export function registerRunCommand(program: Command): void {
  program
    .command("run")
    .description("End-to-end pipeline: find -> select -> eval -> report")
    .option("-q, --query <string>", "Search query for find step")
    .option("--strategy <file>", "SelectStrategy file for select step")
    .option("--benchmark <id|path>", "Benchmark for eval step", "coding-easy")
    .option("--concurrency <n>", "Concurrency level", "4")
    .option("--timeout <ms>", "Per-task timeout in ms", "30000")
    .option("--retries <n>", "Retry count on failure", "0")
    .option("--runs <n>", "Number of runs for consistency check", "1")
    .option("--output-dir <dir>", "Output directory", "./reports")
    .option("--format <formats...>", "Output formats: json|markdown|html|csv", ["json", "markdown"])
    .option("--top-k <n>", "Top K skills to select", "5")
    .option("--skills-dir <dir>", "Skills directory to scan", "./skills")
    .option("--min-completion <rate>", "Min completion rate", "0.7")
    .option("--evaluator <type>", "Scorer type", "exact")
    .option("--benchmarks-dir <dir>", "Built-in benchmarks directory")
    .option("-c, --config <path>", "Config file path")
    .option("--store <path>", "SQLite store path", "./eval-skills.db")
    .action(async (opts) => {
      const spinner = ora({
        text: "Starting end-to-end pipeline...",
        isEnabled: !log.json
      }).start();

      let sqliteStore: SqliteStore | undefined;
      try {
        const globalConfig = loadGlobalConfig(opts.config);

        if (opts.store) {
            sqliteStore = new SqliteStore(path.resolve(opts.store));
        }

        // ========== Step 1: Find Skills ==========
        spinner.text = "[1/4] Finding skills...";

        const store = new SkillStore();
        const skillsDir = path.resolve(opts.skillsDir);

        if (fs.existsSync(skillsDir)) {
          store.loadDir(skillsDir);
        }

        let candidateSkills: Skill[];

        if (opts.query) {
          const finder = new SkillFinder(store);
          const findResult = finder.find({
            query: opts.query,
            limit: 50, // broad find, let select narrow it down
          });
          candidateSkills = findResult.skills;
          log.info(`[Find] Found ${findResult.total} skills matching "${opts.query}"`);
        } else {
          candidateSkills = store.list();
          log.info(`[Find] Loaded ${candidateSkills.length} skills from ${skillsDir}`);
        }

        if (candidateSkills.length === 0) {
          spinner.fail("No skills found. Check --skills-dir or --query.");
          return;
        }

        // ========== Step 2: Evaluate ==========
        spinner.text = `[2/4] Evaluating ${candidateSkills.length} skill(s)...`;

        const benchmarkRegistry = new BenchmarkRegistry();
        const benchmarksDir = opts.benchmarksDir ?? path.resolve(process.cwd(), "benchmarks");
        try {
          benchmarkRegistry.loadBuiltins(benchmarksDir);
        } catch {
          // built-in benchmarks may not exist
        }

        // Build skill paths from candidate skills for eval config
        const skillPaths = candidateSkills.map((s) => {
          // Use the stored source path if available
          const sourcePath = store.getSourcePath(s.id);
          return sourcePath || opts.skillsDir;
        });
        // Deduplicate
        const uniqueSkillPaths = [...new Set(skillPaths)];

        const evalConfig = buildEvalConfig(
          {
            skills: uniqueSkillPaths,
            benchmark: opts.benchmark,
            concurrency: parseInt(opts.concurrency, 10),
            timeout: parseInt(opts.timeout, 10),
            retries: parseInt(opts.retries, 10),
            runs: parseInt(opts.runs, 10),
            evaluator: opts.evaluator,
            outputDir: opts.outputDir,
            format: opts.format,
            dryRun: false,
          },
          globalConfig,
        );

        const engine = new EvaluationEngine({
          skillStore: store,
          benchmarkRegistry,
          sqliteStore,
        });

        engine.on("progress", ({ completed, total, percent }) => {
          spinner.text = `[2/4] Evaluating... ${completed}/${total} tasks (${percent}%)`;
        });

        const reports = await engine.evaluate(evalConfig);

        log.info(`[Eval] Evaluated ${reports.length} skill(s) against benchmark "${opts.benchmark}"`);

        // ========== Step 3: Select ==========
        spinner.text = "[3/4] Selecting top skills...";

        let strategy: SelectStrategy = {
          filters: {
            minCompletionRate: parseFloat(opts.minCompletion),
          },
          sortBy: "compositeScore",
          order: "desc",
          topK: parseInt(opts.topK, 10),
        };

        if (opts.strategy) {
          strategy = loadStrategy(opts.strategy);
          if (opts.topK) {
            strategy.topK = parseInt(opts.topK, 10);
          }
        }

        const selectResult = SkillSelector.select(candidateSkills, reports, strategy);

        log.info(
          `[Select] ${selectResult.selected.length} of ${selectResult.total} skills passed filters`,
        );

        // ========== Step 4: Report ==========
        spinner.text = "[4/4] Generating reports...";

        // Generate reports for selected skills only (if any passed)
        const selectedSkillIds = new Set(selectResult.selected.map((s) => s.skill.id));
        const selectedReports = reports.filter((r) => selectedSkillIds.has(r.skillId));
        const finalReports = selectedReports.length > 0 ? selectedReports : reports;

        const ts = new Date().toISOString().replace(/[:.]/g, "-");
        const formats: ReportFormat[] = opts.format;
        const outputDir = opts.outputDir;

        await writeReports({
            reports: finalReports,
            outputDir: outputDir,
            formats: formats
        });

        spinner.succeed("Pipeline complete!");

        // Print summary
        console.log("");
        log.info("=== Pipeline Results ===");
        console.log("");

        const sorted = [...finalReports].sort(
          (a, b) => b.summary.compositeScore - a.summary.compositeScore,
        );

        for (const r of sorted) {
          const s = r.summary;
          const cr = (s.completionRate * 100).toFixed(1);
          const er = (s.errorRate * 100).toFixed(1);
          const cs = s.compositeScore.toFixed(3);
          const rank = selectResult.selected.find((x) => x.skill.id === r.skillId)?.rank;
          const prefix = rank ? `#${rank}` : "  ";
          log.info(`${prefix} ${r.skillId} — CR: ${cr}% | ER: ${er}% | Score: ${cs}`);
        }

        console.log("");

        if (selectResult.selected.length > 0) {
          log.success(
            `Top ${selectResult.selected.length} selected: ${selectResult.selected.map((s) => s.skill.id).join(", ")}`,
          );
        } else {
          log.warn("No skills passed the selection criteria.");
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
