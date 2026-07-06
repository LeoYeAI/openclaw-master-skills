import * as fs from "node:fs";
import * as path from "node:path";
import { ReporterFactory } from "@eval-skills/core";
import type { SkillCompletionReport, ReportFormat } from "@eval-skills/core";
import { log } from "./output.js";

export interface WriteReportOptions {
  reports: SkillCompletionReport[];
  outputDir: string;
  formats: ReportFormat[];
  timestamp?: string;
}

/**
 * Writes evaluation reports to disk in specified formats.
 */
export async function writeReports(options: WriteReportOptions): Promise<string[]> {
  const { reports, outputDir, formats, timestamp = new Date().toISOString().replace(/[:.]/g, "-") } = options;
  
  if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
  }

  const writtenFiles: string[] = [];
  
  for (const format of formats) {
    const baseName = `eval-result-${timestamp}`;
    let filePath = "";

    try {
        const reporter = ReporterFactory.create(format);
        
        switch (format) {
          case "json": 
            filePath = path.join(outputDir, `${baseName}.json`);
            break;
          case "markdown": 
            filePath = path.join(outputDir, `${baseName}.md`);
            break;
          case "html": 
            filePath = path.join(outputDir, `${baseName}.html`);
            break;
          case "csv": 
            filePath = path.join(outputDir, `${baseName}.csv`);
            break;
          default:
            // Fallback for unknown format if ReporterFactory supports it but we didn't handle extension
            filePath = path.join(outputDir, `${baseName}.${format}`);
        }

        await reporter.writeToFile(reports, filePath);
        log.info(`${format.toUpperCase()} report: ${filePath}`);
        writtenFiles.push(filePath);

    } catch (err) {
        log.error(`Failed to write ${format} report: ${(err as Error).message}`);
    }
  }
  
  return writtenFiles;
}
