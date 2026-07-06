import * as fs from "node:fs";
import * as path from "node:path";
import type { SkillCompletionReport } from "../types/index.js";
import type { IReporter } from "./interfaces/IReporter.js";

/**
 * JSON 格式报告生成器
 */
export class JsonReporter implements IReporter {
  readonly format = "json";

  generate(reports: SkillCompletionReport[]): string {
    return JsonReporter.generate(reports);
  }

  async writeToFile(reports: SkillCompletionReport[], filePath: string): Promise<void> {
    return JsonReporter.writeToFile(reports, filePath);
  }

  static generate(reports: SkillCompletionReport[]): string {
    return JSON.stringify(reports, null, 2);
  }

  static writeToFile(reports: SkillCompletionReport[], filePath: string): void {
    const dir = path.dirname(filePath);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(filePath, JsonReporter.generate(reports), "utf-8");
  }
}
