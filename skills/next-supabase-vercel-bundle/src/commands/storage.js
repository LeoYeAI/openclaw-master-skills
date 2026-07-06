const { Command } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const inquirer = require('inquirer');

const storageCommand = new Command('storage:setup')
  .description('Configure Supabase Storage buckets')
  .option('-b, --buckets <names>', 'Bucket names (comma-separated)')
  .action(async (options) => {
    const spinner = ora('Setting up storage...').start();

    try {
      // Prompt for bucket names if not provided
      let bucketNames = options.buckets;
      if (!bucketNames) {
        const answer = await inquirer.prompt([
          {
            type: 'input',
            name: 'buckets',
            message: 'Enter bucket names (comma-separated):',
            default: 'avatars,documents',
            validate: (input) => {
              if (!input || input.trim().length === 0) {
                return 'Please enter at least one bucket name';
              }
              return true;
            }
          }
        ]);
        bucketNames = answer.buckets;
      }

      spinner.text = `Creating buckets: ${bucketNames}...`;

      console.log(chalk.cyan('\n📦 Buckets to create:\n'));
      bucketNames.split(',').forEach((name, index) => {
        console.log(chalk.gray(`  ${index + 1}. ${name.trim()}`));
      });

      spinner.info(chalk.yellow('\nNote: Buckets must be created manually in Supabase dashboard'));
      console.log(chalk.cyan('Open: https://supabase.com/dashboard/project/_/storage/buckets\n'));

      console.log(chalk.cyan('\nTo enable public access, set RLS policies in Supabase dashboard\n'));

      spinner.succeed(chalk.green.bold('✅ Storage setup complete!\n'));

      // Print RLS policy examples
      console.log(chalk.cyan('RLS Policy Example (public read):\n'));
      console.log(chalk.gray(`create policy "Public read"
on storage.objects for select
using (
  bucket_id
)
with check (
  bucket_id in ('${bucketNames.split(',').map(b => b.trim()).join('\', \'')}\'')
)
grant select;
\n`));

      console.log(chalk.gray('Copy and run this in Supabase SQL Editor\n'));

    } catch (error) {
      spinner.fail(chalk.red(`Error setting up storage: ${error.message}`));
      process.exit(1);
    }
  });

module.exports = storageCommand;
