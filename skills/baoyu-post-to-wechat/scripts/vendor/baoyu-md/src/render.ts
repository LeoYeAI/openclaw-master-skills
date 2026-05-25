#!/usr/bin/env npx tsx

import path from "node:path";
import { parseArgs, printUsage } from "./cli.js";
import { renderMarkdownFileToHtml } from "./document.js";

async function main(): Promise<void> {
  const options = parseArgs(process.argv.slice(2));
  if (!options) {
    printUsage();
    process.exit(1);
  }

  const inputPath = path.resolve(process.cwd(), options.inputPath);
  if (!inputPath.toLowerCase().endsWith(".md")) {
    console.error("Input file must end with .md");
    process.exit(1);
  }

  const result = await renderMarkdownFileToHtml(inputPath, {
    codeTheme: options.codeTheme,
    countStatus: options.countStatus,
    citeStatus: options.citeStatus,
    fontFamily: options.fontFamily,
    fontSize: options.fontSize,
    isMacCodeBlock: options.isMacCodeBlock,
    isShowLineNumber: options.isShowLineNumber,
    keepTitle: options.keepTitle,
    legend: options.legend,
    primaryColor: options.primaryColor,
    theme: options.theme,
  });

  if (result.backupPath) {
    console.log(`Backup created: ${result.backupPath}`);
  }
  console.log(`HTML written: ${result.outputPath}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
