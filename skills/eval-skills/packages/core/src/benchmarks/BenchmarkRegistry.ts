import fs from "node:fs";
import path from "node:path";
import type { Benchmark, BenchmarkMeta } from "../types/index.js";
import { EvalSkillsError, EvalSkillsErrorCode } from "../errors.js";

/**
 * Benchmark 加载和管理注册表
 */
export class BenchmarkRegistry {
  private benchmarks: Map<string, Benchmark> = new Map();

  /**
   * 从 JSON 文件加载 Benchmark
   */
  loadFromFile(filePath: string): Benchmark {
    if (!fs.existsSync(filePath)) {
      throw new EvalSkillsError(
        EvalSkillsErrorCode.BENCHMARK_NOT_FOUND,
        `Benchmark file not found: ${filePath}`,
        { filePath },
      );
    }

    const content = fs.readFileSync(filePath, "utf-8");
    let benchmark: Benchmark;

    try {
      benchmark = JSON.parse(content);
    } catch {
      throw new EvalSkillsError(
        EvalSkillsErrorCode.BENCHMARK_SCHEMA_ERR,
        `Invalid JSON in benchmark file: ${filePath}`,
        { filePath },
      );
    }

    this.register(benchmark);
    return benchmark;
  }

  /**
   * 注册一个 Benchmark
   */
  register(benchmark: Benchmark): void {
    this.benchmarks.set(benchmark.id, benchmark);
  }

  /**
   * 按 ID 获取 Benchmark
   */
  get(id: string): Benchmark | undefined {
    return this.benchmarks.get(id);
  }

  /**
   * 列出所有可用 Benchmark（返回元信息，不含 tasks）
   */
  list(): BenchmarkMeta[] {
    return Array.from(this.benchmarks.values()).map((b) => ({
      id: b.id,
      name: b.name,
      version: b.version,
      domain: b.domain,
      taskCount: b.tasks.length,
      scoringMethod: b.scoringMethod,
    }));
  }

  /**
   * 从目录批量加载内置 benchmark JSON 文件
   * 支持两种结构：
   * - benchmarks/xxx.json（直接 JSON 文件）
   * - benchmarks/xxx/benchmark.json（子目录中的 benchmark.json）
   * - benchmarks/definitions/xxx.json (定义目录)
   */
  loadBuiltins(benchmarksDir: string): void {
    if (!fs.existsSync(benchmarksDir)) {
      return;
    }

    const entries = fs.readdirSync(benchmarksDir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(benchmarksDir, entry.name);

      if (entry.isFile() && entry.name.endsWith(".json")) {
        this.loadFromFile(fullPath);
      } else if (entry.isDirectory()) {
        if (entry.name === "definitions") {
            // Load from definitions subdirectory
            const defEntries = fs.readdirSync(fullPath, { withFileTypes: true });
            for (const defEntry of defEntries) {
                if (defEntry.isFile() && defEntry.name.endsWith(".json")) {
                    this.loadFromFile(path.join(fullPath, defEntry.name));
                }
            }
        } else {
            // 支持子目录中的 benchmark.json
            const benchmarkFile = path.join(fullPath, "benchmark.json");
            if (fs.existsSync(benchmarkFile)) {
              this.loadFromFile(benchmarkFile);
            }
        }
      }
    }
  }
}
