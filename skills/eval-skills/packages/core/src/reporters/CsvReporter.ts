import type { SkillCompletionReport } from "../types/index.js";
import fs from "node:fs";
import path from "node:path";
import type { IReporter } from "./interfaces/IReporter.js";

/**
 * CSV 报告生成器
 */
export class CsvReporter implements IReporter {
  readonly format = "csv";

  generate(reports: SkillCompletionReport[]): string {
    return CsvReporter.generate(reports);
  }

  async writeToFile(reports: SkillCompletionReport[], filePath: string): Promise<void> {
    return CsvReporter.writeToFile(reports, filePath);
  }

  /**
   * 生成 CSV 字符串
   */
  static generate(reports: SkillCompletionReport[]): string {
    const headers = [
        "skillId",
        "benchmarkId",
        "completionRate",
        "partialScore",
        "errorRate",
        "p50Ms",
        "p95Ms",
        "compositeScore"
    ];
    
    const escape = (field: string) => {
        if (field.includes(",") || field.includes("\n") || field.includes('"')) {
            return `"${field.replace(/"/g, '""')}"`;
        }
        return field;
    };

    const rows = reports.map(r => [
      escape(r.skillId),
      escape(r.benchmarkId),
      r.summary.completionRate.toFixed(4),
      r.summary.partialScore.toFixed(4),
      r.summary.errorRate.toFixed(4),
      r.latency.p50Ms.toString(),
      r.latency.p95Ms.toString(),
      r.summary.compositeScore.toFixed(4)
    ]);
    
    return [
        headers.join(","),
        ...rows.map(r => r.join(","))
    ].join("\n");
  }

  /**
   * 写入 CSV 文件
   */
  static writeToFile(reports: SkillCompletionReport[], filePath: string): void {
    const content = CsvReporter.generate(reports);
    const dir = path.dirname(filePath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(filePath, content, "utf-8");
  }
}
