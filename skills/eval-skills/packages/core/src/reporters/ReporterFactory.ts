import type { IReporter } from "./interfaces/IReporter.js";
import { JsonReporter } from "./JsonReporter.js";
import { MarkdownReporter } from "./MarkdownReporter.js";
import { HtmlReporter } from "./HtmlReporter.js";
import { CsvReporter } from "./CsvReporter.js";

export class ReporterFactory {
  static create(format: string): IReporter {
    switch (format.toLowerCase()) {
      case "json": return new JsonReporter();
      case "markdown": 
      case "md":
        return new MarkdownReporter();
      case "html": return new HtmlReporter();
      case "csv": return new CsvReporter();
      default: throw new Error(`Unknown report format: ${format}`);
    }
  }
}
