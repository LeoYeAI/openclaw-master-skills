import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";
import yaml from "js-yaml";
import type { GlobalConfig, EvalRunConfig, SelectStrategy } from "@eval-skills/core";
import { DEFAULT_GLOBAL_CONFIG } from "@eval-skills/core";

const CONFIG_FILENAMES = [
  "eval-skills.config.yaml",
  "eval-skills.config.yml",
  "eval-skills.config.json",
];

/**
 * 查找并加载全局配置文件
 */
export function loadGlobalConfig(configPath?: string): GlobalConfig {
  if (configPath) {
    return parseConfigFile(configPath) as GlobalConfig;
  }

  // 1. Check current directory
  for (const filename of CONFIG_FILENAMES) {
    const fullPath = path.resolve(filename);
    if (fs.existsSync(fullPath)) {
      return { ...DEFAULT_GLOBAL_CONFIG, ...(parseConfigFile(fullPath) as Partial<GlobalConfig>) };
    }
  }

  // 2. Check home directory
  const homeConfigPath = path.join(os.homedir(), ".eval-skills", "config.yaml");
  if (fs.existsSync(homeConfigPath)) {
    return { ...DEFAULT_GLOBAL_CONFIG, ...(parseConfigFile(homeConfigPath) as Partial<GlobalConfig>) };
  }

  return { ...DEFAULT_GLOBAL_CONFIG };
}

/**
 * 加载 SelectStrategy 文件
 */
export function loadStrategy(strategyPath: string): SelectStrategy {
  return parseConfigFile(strategyPath) as SelectStrategy;
}

/**
 * 解析 YAML 或 JSON 配置文件
 */
function parseConfigFile(filePath: string): Record<string, unknown> {
  const content = fs.readFileSync(filePath, "utf-8");
  if (filePath.endsWith(".json")) {
    return JSON.parse(content);
  }
  return (yaml.load(content) as Record<string, unknown>) ?? {};
}

/**
 * 构建 EvalRunConfig (从 CLI 参数合并)
 */
export function buildEvalConfig(
  opts: Record<string, unknown>,
  globalConfig: GlobalConfig,
): EvalRunConfig {
  return {
    skillPaths: (opts.skills as string[]) ?? [],
    benchmark: (opts.benchmark as string) ?? "",
    tasksFile: opts.tasks as string | undefined,
    concurrency: (opts.concurrency as number) ?? globalConfig.concurrency,
    timeoutMs: (opts.timeout as number) ?? globalConfig.timeoutMs,
    retries: (opts.retries as number) ?? 0,
    evaluator: (opts.evaluator as string) ?? "exact",
    output: {
      dir: (opts.outputDir as string) ?? globalConfig.outputDir,
      formats: (opts.format as string[]) ?? globalConfig.defaultFormats,
    },
    exitOnFail: opts.exitOnFail
      ? {
          enabled: true,
          minCompletionRate: (opts.minCompletion as number) ?? 0.7,
        }
      : undefined,
    dryRun: opts.dryRun as boolean | undefined,
    resume: opts.resume as boolean | undefined,
    runs: (opts.runs as number) ?? 1,
  };
}
