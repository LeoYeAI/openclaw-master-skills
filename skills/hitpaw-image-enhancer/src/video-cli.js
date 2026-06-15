#!/usr/bin/env node
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import path from 'path';
import fs from 'fs-extra';
import { HitPawClient } from './client.js';

const program = new Command();

program
  .name('enhance-video')
  .description('Enhance videos using HitPaw AI Video Enhancement API')
  .version('1.0.0');

program
  .option('-u, --url <url>', 'URL or local file path of the video')
  .option('-o, --output <path>', 'Output file path', 'output.mp4')
  .option('-m, --model <model>', 'Enhancement model (see models table below)', 'general_restore_2x')
  .option('-r, --resolution <wxh>', 'Target resolution (required, e.g., 1920x1080)')
  .option('-e, --extension <ext>', 'Output extension (e.g., .mp4, .mov, .avi)', '.mp4')
  .option('--original-resolution <wxh>', 'Original video resolution (optional, e.g., 1280x720)')
  .option('--poll-interval <seconds>', 'Polling interval (default 10s for video)', '10')
  .option('--timeout <seconds>', 'Max wait time (default 600s for video)', '600')
  .requiredOption('-u, --url <url>', 'Video URL or local file path')
  .action(async (options) => {
    const apiKey = process.env.HITPAW_API_KEY;
    if (!apiKey) {
      console.error(chalk.red('Error: HITPAW_API_KEY environment variable is not set'));
      console.log(chalk.yellow('Set it with: export HITPAW_API_KEY="your_key"'));
      process.exit(1);
    }

    const { url, output, model, resolution, extension, original_resolution, pollInterval, timeout } = options;

    // Parse resolution strings
<<<<<<< HEAD
    const parseRes = (str: string): [number, number] => {
=======
    const parseRes = (str) => {
>>>>>>> 96b5b31 (docs: 丰富 HitPaw API 功能文档)
      const [w, h] = str.split('x').map(Number);
      if (!w || !h) throw new Error(`Invalid resolution format: ${str}. Use WxH (e.g., 1920x1080)`);
      return [w, h];
    };

    if (!resolution) {
      console.error(chalk.red('Error: --resolution (-r) is required for video enhancement'));
      console.log(chalk.yellow('Example: -r 1920x1080'));
      process.exit(1);
    }

    const targetRes = parseRes(resolution);
    const originalRes = original_resolution ? parseRes(original_resolution) : undefined;

    if (fs.existsSync(url)) {
      console.error(chalk.red('Error: Local file paths are not directly supported.'));
      console.log(chalk.yellow('Please upload the video to a public URL first.'));
      process.exit(1);
    }

    const client = new HitPawClient(apiKey);

    const spinner = ora('Enhancing video...').start();

    try {
      const result = await client.enhanceVideoAndDownload(url, output, {
        model,
        resolution: targetRes,
        extension,
        original_resolution: originalRes,
        pollInterval: parseInt(pollInterval),
        timeout: parseInt(timeout)
      });

      spinner.succeed(chalk.green('Video enhancement complete!'));
      console.log(`Output: ${path.resolve(output)}`);
      console.log(`Coins consumed: ${result.coins}`);
<<<<<<< HEAD
    } catch (error: any) {
=======
    } catch (error) {
>>>>>>> 96b5b31 (docs: 丰富 HitPaw API 功能文档)
      spinner.fail(chalk.red('Video enhancement failed'));
      console.error(chalk.red(error.message || 'Unknown error'));

      if (error.response?.data?.error_code) {
        const code = error.response.data.error_code;
<<<<<<< HEAD
        const messages: Record<number, string> = {
=======
        const messages = {
>>>>>>> 96b5b31 (docs: 丰富 HitPaw API 功能文档)
          110400000: 'Invalid API key',
          110402000: 'Insufficient coins',
          110400005: 'Unsupported model',
          110400007: 'Invalid extension',
          110400008: 'Invalid video URL',
          110400009: 'Input resolution over limit',
          110400010: 'Target resolution over limit',
          110400011: 'Video duration over limit',
          100429000: 'Rate limit exceeded'
        };
        console.error(chalk.yellow(`Error code ${code}: ${messages[code] || 'See documentation'}`));
      }

      process.exit(1);
    }
  });

program.parse();