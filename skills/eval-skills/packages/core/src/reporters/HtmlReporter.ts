import * as fs from "node:fs";
import * as path from "node:path";
import type { SkillCompletionReport } from "../types/index.js";
import { MarkdownReporter } from "./MarkdownReporter.js";
import { marked } from "marked";
import type { IReporter } from "./interfaces/IReporter.js";

const HTML_STYLE = `
<style>
  :root {
    --primary: #4f46e5;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg: #f9fafb;
    --card-bg: #ffffff;
    --text: #1f2937;
    --text-muted: #6b7280;
    --border: #e5e7eb;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    background-color: var(--bg);
    color: var(--text);
    margin: 0;
    padding: 2rem;
    line-height: 1.5;
  }
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
  h1 {
    color: var(--primary);
    border-bottom: 2px solid var(--border);
    padding-bottom: 1rem;
    margin-bottom: 2rem;
  }
  h2 {
    color: var(--text);
    margin-top: 2rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
  }
  h3 {
    color: var(--text-muted);
    font-weight: 600;
  }
  
  /* Summary Cards */
  .summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  .card {
    background: var(--card-bg);
    border-radius: 0.75rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    border: 1px solid var(--border);
  }
  .card-title {
    font-size: 0.875rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
    font-weight: 500;
  }
  .card-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
  }
  
  /* Tables */
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: var(--card-bg);
    border-radius: 0.75rem;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin: 1.5rem 0;
    border: 1px solid var(--border);
  }
  th {
    background: #f3f4f6;
    font-weight: 600;
    text-align: left;
    padding: 1rem;
    border-bottom: 1px solid var(--border);
    color: var(--text-muted);
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  td {
    padding: 1rem;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }
  tr:last-child td {
    border-bottom: none;
  }
  tr:hover td {
    background-color: #f9fafb;
  }
  
  /* Status Badges */
  .badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
  }
  .badge-pass { background: #dcfce7; color: #166534; }
  .badge-fail { background: #fee2e2; color: #991b1b; }
  .badge-warn { background: #fef3c7; color: #92400e; }
  
  /* Code Blocks */
  pre {
    background: #1e293b;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    font-size: 0.875rem;
  }
  code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  }
  p > code {
    background: #f3f4f6;
    color: #db2777;
    padding: 0.2em 0.4em;
    border-radius: 0.25rem;
    font-size: 0.875em;
  }
</style>
`;

/**
 * HTML 格式报告生成器（单文件，内嵌 CSS）
 */
export class HtmlReporter implements IReporter {
  readonly format = "html";

  async generate(reports: SkillCompletionReport[]): Promise<string> {
    return HtmlReporter.generate(reports);
  }

  async writeToFile(reports: SkillCompletionReport[], filePath: string): Promise<void> {
    return HtmlReporter.writeToFile(reports, filePath);
  }

  static async generate(reports: SkillCompletionReport[]): Promise<string> {
    const md = MarkdownReporter.generate(reports);
    // Add container div wrapper to markdown content before parsing
    const body = await marked.parse(md);

    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>eval-skills Report</title>
  ${HTML_STYLE}
</head>
<body>
  <div class="container">
    ${body}
  </div>
</body>
</html>`;
  }

  static async writeToFile(reports: SkillCompletionReport[], filePath: string): Promise<void> {
    const dir = path.dirname(filePath);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(filePath, await HtmlReporter.generate(reports), "utf-8");
  }
  
  // Instance method compatibility
  async render(reports: SkillCompletionReport[]): Promise<string> {
      return HtmlReporter.generate(reports);
  }
}
