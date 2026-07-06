#!/usr/bin/env node

const { Command } = require('commander');
const chalk = require('chalk');
const path = require('path');

// Import commands
const initCommand = require('./src/commands/init');
const devCommand = require('./src/commands/dev');
const deployCommand = require('./src/commands/deploy');
const dbCommand = require('./src/commands/db');
const authCommand = require('./src/commands/auth');
const storageCommand = require('./src/commands/storage');

const program = new Command();

program
  .name('snv')
  .description('Next-Supabase-Vercel Bundle - Complete automation for the modern full-stack development cycle')
  .version('1.0.0')
  .option('--debug', 'Enable debug mode', false);

// Add commands
program.addCommand(initCommand);
program.addCommand(devCommand);
program.addCommand(deployCommand);
program.addCommand(dbCommand);
program.addCommand(authCommand);
program.addCommand(storageCommand);

// Error handling
program.exitOverride((err) => {
  if (err.code === 'commander.help' || err.code === 'commander.version') {
    process.exit(0);
  }
  if (err.code === 'commander.helpDisplayed') {
    process.exit(0);
  }
});

// Parse arguments
program.parse(process.argv);

// Show help if no command provided
if (!process.argv.slice(2).length) {
  console.log(chalk.cyan.bold('\n🚀 Next-Supabase-Vercel Bundle\n'));
  console.log(chalk.gray('Complete automation for Next.js + Supabase + Vercel development\n'));
  program.outputHelp();
  console.log(chalk.gray('\nRun "snv <command> --help" for command details\n'));
}
