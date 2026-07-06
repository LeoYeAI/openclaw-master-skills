const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');

const devCommand = new Command('dev')
  .description('Start local development server')
  .option('-p, --port <number>', 'Port to run on', '3000')
  .action(async (options) => {
    const spinner = ora('Starting development server...').start();

    try {
      // Verify .env.local exists
      const envPath = path.join(process.cwd(), '.env.local');
      if (!await fs.pathExists(envPath)) {
        spinner.fail(chalk.red('.env.local not found. Please set your Supabase credentials first.'));
        console.log(chalk.yellow('\nRun: snv db:setup\n'));
        process.exit(1);
      }

      // Start Next.js dev server
      spinner.text = 'Starting Next.js dev server...';
      execSync(`npm run dev -- --port ${options.port}`, { stdio: 'inherit' });

    } catch (error) {
      spinner.fail(chalk.red(`Error starting dev server: ${error.message}`));
      process.exit(1);
    }
  });

module.exports = devCommand;
