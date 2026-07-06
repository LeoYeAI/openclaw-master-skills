const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const fs = require('fs-extra');
const path = require('path');
const { execSync } = require('child_process');
const inquirer = require('inquirer');

const deployCommand = new Command('deploy')
  .description('Deploy project to Vercel')
  .option('--prod', 'Deploy to production')
  .action(async (options) => {
    const spinner = ora('Deploying to Vercel...').start();

    try {
      // Verify Vercel CLI is installed
      try {
        execSync('which vercel', { stdio: 'ignore' });
      } catch (error) {
        spinner.fail(chalk.red('Vercel CLI not installed'));
        console.log(chalk.yellow('\nInstall it with: npm i -g vercel\n'));
        process.exit(1);
      }

      // Check if project is linked
      spinner.text = 'Checking Vercel project status...';
      let isLinked = false;
      try {
        execSync('vercel ls', { stdio: 'ignore' });
        isLinked = true;
      } catch (error) {
        // Not linked, will prompt
      }

      // Link project if not linked
      if (!isLinked) {
        spinner.text = 'Linking project to Vercel...';
        try {
          execSync('vercel link --yes', { stdio: 'inherit' });
        } catch (error) {
          // Link already exists or other issue
        }
      }

      // Build project
      spinner.text = 'Building project...';
      execSync('npm run build', { stdio: 'inherit' });

      // Deploy to Vercel
      spinner.text = 'Deploying to Vercel...';
      const deployFlags = options.prod ? '--prod' : '';
      execSync(`vercel deploy ${deployFlags}`, { stdio: 'inherit' });

      spinner.succeed(chalk.green.bold('✅ Deployed successfully!\n'));

      // Check environment variables
      spinner.text = 'Checking environment variables...';
      checkEnvVars();

    } catch (error) {
      spinner.fail(chalk.red(`Error deploying: ${error.message}`));
      process.exit(1);
    }
  });

function checkEnvVars() {
  const envPath = path.join(process.cwd(), '.env.local');
  const envExists = fs.existsSync(envPath);

  if (!envExists) {
    console.log(chalk.yellow('\n⚠️  Warning: .env.local not found'));
    console.log(chalk.cyan('Set environment variables in Vercel dashboard:\n'));
    console.log(chalk.gray('  https://vercel.com/dashboard\n'));
    return;
  }

  const envContent = fs.readFileSync(envPath, 'utf-8');
  const hasSupabaseUrl = envContent.includes('NEXT_PUBLIC_SUPABASE_URL');
  const hasSupabaseKey = envContent.includes('NEXT_PUBLIC_SUPABASE_ANON_KEY');

  if (!hasSupabaseUrl || !hasSupabaseKey) {
    console.log(chalk.yellow('\n⚠️  Warning: Supabase credentials missing in .env.local'));
    console.log(chalk.cyan('Set them in Vercel dashboard:\n'));
    console.log(chalk.gray('  https://vercel.com/dashboard\n'));
  }
}

module.exports = deployCommand;
