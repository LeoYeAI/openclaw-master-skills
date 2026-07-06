const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const fs = require('fs-extra');
const path = require('path');
const inquirer = require('inquirer');

const dbCommand = new Command('db:setup')
  .description('Configure Supabase database')
  .action(async () => {
    const spinner = ora('Setting up database...').start();

    try {
      // Verify .env.local exists
      const envPath = path.join(process.cwd(), '.env.local');
      if (!await fs.pathExists(envPath)) {
        spinner.fail(chalk.red('.env.local not found'));
        console.log(chalk.yellow('\nPlease set your Supabase credentials in .env.local first.'));
        process.exit(1);
      }

      // Load environment variables
      const envContent = await fs.readFile(envPath, 'utf-8');
      const lines = envContent.split('\n');
      let supabaseUrl, supabaseAnonKey;

      for (const line of lines) {
        if (line.includes('NEXT_PUBLIC_SUPABASE_URL=')) {
          supabaseUrl = line.split('=')[1].trim();
        }
        if (line.includes('NEXT_PUBLIC_SUPABASE_ANON_KEY=')) {
          supabaseAnonKey = line.split('=')[1].trim();
        }
      }

      if (!supabaseUrl || !supabaseAnonKey) {
        spinner.fail(chalk.red('Supabase credentials not found in .env.local'));
        process.exit(1);
      }

      spinner.text = 'Connecting to Supabase...';

      // Test connection to Supabase
      const { createClient } = require('@supabase/supabase-js');
      const supabase = createClient(supabaseUrl, supabaseAnonKey);

      // Test connection
      const { data, error } = await supabase.from('_test_connection').select('*').limit(1);
      if (error && error.code !== 'PGRST116') {
        // PGRST116 is "table does not exist", which is expected
        spinner.fail(chalk.red(`Failed to connect to Supabase: ${error.message}`));
        process.exit(1);
      }

      spinner.text = 'Checking for migrations...';

      // Check for migrations
      const migrationsDir = path.join(process.cwd(), 'supabase/migrations');
      const migrationsExist = await fs.pathExists(migrationsDir);

      if (migrationsExist) {
        const files = await fs.readdir(migrationsDir);
        const sqlFiles = files.filter(f => f.endsWith('.sql')).sort();

        if (sqlFiles.length > 0) {
          spinner.text = `Found ${sqlFiles.length} migration(s)`;

          const answer = await inquirer.prompt([
            {
              type: 'confirm',
              name: 'runMigrations',
              message: `Run ${sqlFiles.length} migration(s)?`,
              default: true
            }
          ]);

          if (answer.runMigrations) {
            spinner.text = 'Running migrations...';
            console.log(chalk.cyan('\n📋 Migrations to run:\n'));
            sqlFiles.forEach((file, index) => {
              console.log(chalk.gray(`  ${index + 1}. ${file}`));
            });

            spinner.info(chalk.yellow('Note: Migrations must be run manually in Supabase dashboard'));
            console.log(chalk.cyan('\nOpen: https://supabase.com/dashboard/project/_/sql/new\n'));
          }
        }
      }

      spinner.succeed(chalk.green.bold('✅ Database setup complete!\n'));

      // Print database info
      console.log(chalk.cyan('Database connected:'));
      console.log(chalk.white(`  URL: ${supabaseUrl}`));
      console.log(chalk.white(`  Migrations: ${migrationsExist ? 'Found in supabase/migrations/' : 'None yet'}\n`));
      console.log(chalk.gray('Create migrations with: snv db:migrate\n'));

    } catch (error) {
      spinner.fail(chalk.red(`Error setting up database: ${error.message}`));
      process.exit(1);
    }
  });

// Additional command for creating migrations
const migrateCommand = new Command('db:migrate')
  .description('Create a new database migration')
  .option('-n, --name <name>', 'Migration name')
  .action(async (options) => {
    const spinner = ora('Creating migration...').start();

    try {
      const migrationsDir = path.join(process.cwd(), 'supabase/migrations');
      await fs.ensureDir(migrationsDir);

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const name = options.name || 'new_migration';
      const filename = `${timestamp}_${name}.sql`;
      const filepath = path.join(migrationsDir, filename);

      await fs.writeFile(filepath, `-- Migration: ${name}\n-- Created: ${new Date().toISOString()}\n\n-- Add your SQL here\n`);

      spinner.succeed(chalk.green.bold(`✅ Migration created: ${filename}\n`));
      console.log(chalk.cyan('Edit:'), chalk.white(filepath));
      console.log(chalk.gray('\nRun with: snv db:setup\n'));

    } catch (error) {
      spinner.fail(chalk.red(`Error creating migration: ${error.message}`));
      process.exit(1);
    }
  });

module.exports = dbCommand;
module.exports.migrate = migrateCommand;
