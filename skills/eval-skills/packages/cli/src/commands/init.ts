import * as fs from "node:fs";
import * as path from "node:path";
import type { Command } from "commander";
import { log } from "../utils/output.js";

const DEFAULT_CONFIG = `# eval-skills configuration
concurrency: 4
timeoutMs: 30000
outputDir: ./reports
defaultFormats:
  - json
  - markdown
# llm:
#   model: gpt-4o
#   temperature: 0
`;

export function registerInitCommand(program: Command): void {
  program
    .command("init")
    .description("Initialize eval-skills project configuration")
    .option("--dir <dir>", "Project directory", ".")
    .action((opts) => {
      try {
        const dir = path.resolve(opts.dir);

        // 创建配置文件
        const configPath = path.join(dir, "eval-skills.config.yaml");
        if (!fs.existsSync(configPath)) {
          fs.writeFileSync(configPath, DEFAULT_CONFIG, "utf-8");
          log.success(`Created ${configPath}`);
        } else {
          log.dim(`Config already exists: ${configPath}`);
        }

        // 创建目录结构
        const dirs = ["skills", "benchmarks", "reports"];
        for (const d of dirs) {
          const fullPath = path.join(dir, d);
          if (!fs.existsSync(fullPath)) {
            fs.mkdirSync(fullPath, { recursive: true });
            log.success(`Created directory: ${d}/`);
          } else {
            log.dim(`Directory exists: ${d}/`);
          }
        }

        log.success("Project initialized! Run 'eval-skills --help' to get started.");
      } catch (err) {
        log.error((err as Error).message);
        process.exit(1);
      }
    });
}
