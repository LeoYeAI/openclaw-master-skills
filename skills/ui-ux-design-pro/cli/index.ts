#!/usr/bin/env bun
import { cac } from 'cac';
import chalk from 'chalk';
import packageJson from './package.json';
const { version } = packageJson;
import { searchCommand } from './commands/search';
import { iconsCommand } from './commands/icons';
import { auditCommand } from './commands/audit';
import { generateSystemCommand } from './commands/generate';


const cli = cac('design-cli');

cli
  .command('search <query>', 'Search across all design databases')
  .option('--domain <domain>', 'Restrict search to a specific domain (style, icon, color, etc.)')
  .option('--format <format>', 'Output format (markdown, json)', { default: 'markdown' })
  .action(searchCommand);

cli
  .command('icons [query]', 'List or search icon libraries')
  .action(iconsCommand);

cli
  .command('audit <files...>', 'Audit UI files for mistakes')
  .option('--format <format>', 'Output format (text, json, markdown)', { default: 'text' })
  .option('--output <file>', 'Output file path')
  .action(auditCommand);

cli
  .command('generate <query>', 'Generate a design system from a query')
  .option('--stack <stack>', 'Tech stack (e.g. nextjs)')
  .option('--output <file>', 'Output file path')
  .option('--format <format>', 'Output format (json, css, text)', { default: 'text' })
  .action(generateSystemCommand);

cli.help();
cli.version(version);

try {
  cli.parse();
} catch (error) {
  console.error(chalk.red('Error:'), error instanceof Error ? error.message : error);
  process.exit(1);
}