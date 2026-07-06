import { logger as pinoLogger } from "@eval-skills/core";
import chalk from "chalk";

class Logger {
  public level: "info" | "debug" = "info";
  public json: boolean = false;

  constructor() {
      // Sync level with pino if set via env
      if (process.env.LOG_LEVEL === "debug") {
          this.level = "debug";
      }
  }

  private format(level: string, msg: string, data?: any) {
    if (this.json) {
      // Use Pino for structured JSON output
      (pinoLogger as any)[level === "success" ? "info" : level](data || {}, msg);
      return;
    }
    
    switch (level) {
        case "info": console.log(chalk.blue("ℹ"), msg); break;
        case "success": console.log(chalk.green("✔"), msg); break;
        case "warn": console.log(chalk.yellow("⚠"), msg); break;
        case "error": console.error(chalk.red("✖"), msg); break;
        case "debug": console.log(chalk.gray("🐛"), msg); break;
        default: console.log(msg);
    }
  }

  info(msg: string, data?: any) { this.format("info", msg, data); }
  success(msg: string, data?: any) { this.format("success", msg, data); }
  warn(msg: string, data?: any) { this.format("warn", msg, data); }
  error(msg: string, data?: any) { this.format("error", msg, data); }
  debug(msg: string, data?: any) { 
      if (this.level === "debug") this.format("debug", msg, data); 
  }
  dim(msg: string) { 
      if (!this.json) console.log(chalk.dim(msg)); 
  }
}

export const log = new Logger();

export function printTable(headers: string[], rows: string[][]): void {
  if (log.json) {
      console.log(JSON.stringify({ table: { headers, rows } }));
      return;
  }
  // 计算列宽
  const widths = headers.map((h, i) =>
    Math.max(h.length, ...rows.map((r) => (r[i] ?? "").length)),
  );

  const sep = widths.map((w) => "-".repeat(w + 2)).join("+");
  const formatRow = (row: string[]) =>
    row.map((cell, i) => ` ${(cell ?? "").padEnd(widths[i]!)} `).join("|");

  console.log(formatRow(headers));
  console.log(sep);
  for (const row of rows) {
    console.log(formatRow(row));
  }
}
