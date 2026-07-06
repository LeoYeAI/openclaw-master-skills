import type { SkillCompletionReport } from "../../types/index.js";

export interface IReporter {
  readonly format: string;
  generate(reports: SkillCompletionReport[]): string | Promise<string>;
  writeToFile(reports: SkillCompletionReport[], outputPath: string): Promise<void>;
}
