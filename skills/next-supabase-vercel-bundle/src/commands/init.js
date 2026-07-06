const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const inquirer = require('inquirer');

const TEMPLATE_DIR = path.join(__dirname, '../../templates');

const initCommand = new Command('init <project-name>')
  .description('Create a new Next.js + Supabase + Vercel project')
  .option('-t, --template <name>', 'Template to use', 'auth-db')
  .option('--no-typescript', 'Disable TypeScript')
  .option('--no-tailwind', 'Disable Tailwind CSS')
  .option('--no-eslint', 'Disable ESLint')
  .action(async (projectName, options) => {
    const spinner = ora('Creating project...').start();

    try {
      // Validate project name
      if (!projectName || projectName.length === 0) {
        spinner.fail('Project name is required');
        process.exit(1);
      }

      const template = options.template;
      const useTypescript = !options.noTypescript;
      const useTailwind = !options.noTailwind;
      const useEslint = !options.noEslint;

      // Validate template
      const validTemplates = ['minimal', 'auth', 'auth-db', 'full'];
      if (!validTemplates.includes(template)) {
        spinner.fail(`Invalid template: ${template}`);
        console.log(chalk.red(`Valid templates: ${validTemplates.join(', ')}`));
        process.exit(1);
      }

      spinner.text = `Creating ${projectName} with template: ${template}...`;

      // Create project with create-next-app
      const createNextAppCommand = [
        'npx',
        'create-next-app@latest',
        projectName,
        '--typescript',
        '--tailwind',
        '--eslint',
        '--app',
        '--src-dir',
        '--import-alias "@/*"',
        '--use-npm'
      ].filter(Boolean);

      execSync(createNextAppCommand.join(' '), { stdio: 'inherit' });

      spinner.text = 'Configuring Supabase...';

      // Create Supabase structure
      const projectPath = path.join(process.cwd(), projectName);
      await configureSupabase(projectPath, template, useTypescript);

      // Create environment template
      await createEnvTemplate(projectPath);

      spinner.text = 'Creating project structure...';

      // Create supabase/migrations directory
      await fs.ensureDir(path.join(projectPath, 'supabase/migrations'));

      // Copy template files if needed
      await copyTemplateFiles(projectPath, template, useTypescript);

      spinner.text = 'Installing dependencies...';

      // Install Supabase dependencies
      const installCommand = `cd ${projectPath} && npm install @supabase/supabase-js @supabase/ssr`;
      execSync(installCommand, { stdio: 'inherit' });

      // Initialize git
      spinner.text = 'Initializing git repository...';
      execSync(`cd ${projectPath} && git init`, { stdio: 'ignore' });

      spinner.succeed(chalk.green.bold(`✅ Project ${projectName} created successfully!\n`));

      // Print next steps
      console.log(chalk.cyan('Next steps:\n'));
      console.log(chalk.gray('1. Set your Supabase credentials in .env.local'));
      console.log(chalk.gray('2. Run: snv db:setup'));
      console.log(chalk.gray('3. Run: snv auth:setup'));
      console.log(chalk.gray('4. Run: snv dev\n'));
      console.log(chalk.cyan('Get started:'));
      console.log(chalk.white(`  cd ${projectName}`));
      console.log(chalk.white('  snv dev\n'));

    } catch (error) {
      spinner.fail(chalk.red(`Error creating project: ${error.message}`));
      process.exit(1);
    }
  });

async function configureSupabase(projectPath, template, useTypescript) {
  // Create lib/supabase.ts
  const libDir = path.join(projectPath, 'lib');
  await fs.ensureDir(libDir);

  const supabaseClientCode = useTypescript ? supabaseClientTS : supabaseClientJS;
  await fs.writeFile(path.join(libDir, 'supabase.ts'), supabaseClientCode);
}

async function createEnvTemplate(projectPath) {
  const envTemplate = `# Supabase Configuration
# Get these from: https://supabase.com/dashboard/project/_/settings/api

NEXT_PUBLIC_SUPABASE_URL=your_project_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# Optional - Service role key for server-side operations
SUPABASE_SERVICE_KEY=your_service_role_key_here
`;

  await fs.writeFile(path.join(projectPath, '.env.local'), envTemplate);
  await fs.writeFile(path.join(projectPath, '.env.example'), envTemplate);
}

async function copyTemplateFiles(projectPath, template, useTypescript) {
  const templateDir = path.join(TEMPLATE_DIR, template);
  const templateExists = await fs.pathExists(templateDir);

  if (templateExists) {
    const appDir = path.join(projectPath, 'src/app');
    await fs.copy(templateDir, appDir, { overwrite: false });
  }
}

// TypeScript version
const supabaseClientTS = `import { createClient } from '@supabase/supabase-js'

export const createSupabaseClient = () => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  return createClient(supabaseUrl, supabaseAnonKey)
}

export const supabase = createSupabaseClient()

// Server-side client with service role key
export const supabaseServer = () => {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY

  if (!supabaseServiceKey) {
    throw new Error('SUPABASE_SERVICE_KEY is required for server operations')
  }

  return createClient(supabaseUrl, supabaseServiceKey)
}
`;

// JavaScript version
const supabaseClientJS = `const { createClient } = require('@supabase/supabase-js')

function createSupabaseClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  return createClient(supabaseUrl, supabaseAnonKey)
}

const supabase = createSupabaseClient()

module.exports = {
  supabase,
  createSupabaseClient
}
`;

module.exports = initCommand;
