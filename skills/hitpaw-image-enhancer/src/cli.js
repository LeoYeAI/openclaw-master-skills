#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import path from 'path';
import fs from 'fs-extra';
import { HitPawClient } from './client.js';

const program = new Command();

program
  .name('enhance-image')
  .description('Enhance images using HitPaw AI API')
  .version('1.0.0');

program
  .option('-u, --url <url>', 'URL or local file path of the image')
  .option('-o, --output <path>', 'Output file path', 'output.jpg')
  .option('-m, --model <model>', 'Enhancement model', 'general_2x')
  .option('-e, --extension <ext>', 'Output extension (e.g., .jpg, .png)', '.jpg')
  .option('--dpi <number>', 'Target DPI for metadata')
  .option('--keep-exif', 'Preserve EXIF data', false)
  .option('--poll-interval <seconds>', 'Polling interval', '5')
  .option('--timeout <seconds>', 'Max wait time', '300')
  .requiredOption('-u, --url <url>', 'Image URL or local file path')
  .action(async (options) => {
    const apiKey = process.env.HITPAW_API_KEY;
    if (!apiKey) {
      console.error(chalk.red('Error: HITPAW_API_KEY environment variable is not set'));
      console.log(chalk.yellow('Set it with: export HITPAW_API_KEY="your_key"'));
      process.exit(1);
    }

    const { url, output, model, extension, dpi, keepExif, pollInterval, timeout } = options;

    // Handle local file: need to convert to public URL (not supported in this skill)
    // For now, only support URLs. For local files, user must upload somewhere first.
    if (fs.existsSync(url)) {
      console.error(chalk.red('Error: Local file paths are not directly supported.'));
      console.log(chalk.yellow('Please upload the image to a public URL first, or use a service like transfer.sh'));
      process.exit(1);
    }

    const client = new HitPawClient(apiKey);

    const spinner = ora('Enhancing image...').start();

    try {
      const result = await client.enhanceAndDownload(url, output, {
        model,
        extension,
        exif: keepExif,
        dpi: dpi ? parseInt(dpi) : undefined,
        pollInterval: parseInt(pollInterval),
        timeout: parseInt(timeout)
      });

      spinner.succeed(chalk.green('Enhancement complete!'));
      console.log(`Output: ${path.resolve(output)}`);
      console.log(`Coins consumed: ${result.coins}`);
    } catch (error) {
      spinner.fail(chalk.red('Enhancement failed'));
      console.error(chalk.red(error.message || 'Unknown error'));

      // Parse error response
      if (error.response?.data?.error_code) {
        const code = error.response.data.error_code;
        const messages = {
          110400000: 'Invalid API key',
          110402000: 'Insufficient coins',
          110400005: 'Unsupported model',
          110400007: 'Invalid extension',
          100429000: 'Rate limit exceeded'
        };
        console.error(chalk.yellow(`Error code ${code}: ${messages[code] || 'See documentation'}`));
      }

      process.exit(1);
    }
  });

program.parse();
