import { readFile } from 'fs/promises';
import { join } from 'path';
import { parse } from 'csv-parse/sync';
import chalk from 'chalk';

const DATA_FILE = join(import.meta.dir, '../data/icon-libraries.csv');

interface IconLibrary {
  name: string;
  count: string;
  type: string;
  best_for: string;
  docs_url: string;
  cdn_url: string;
  implementation_type: string;
}

export async function iconsCommand(query?: string) {
  try {
    const csvContent = await readFile(DATA_FILE, 'utf-8');
    const records = parse(csvContent, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    }) as IconLibrary[];

    if (query) {
      const results = records.filter((r) => 
        r.name.toLowerCase().includes(query.toLowerCase())
      );

      if (results.length === 0) {
        console.log(chalk.yellow(`No icon libraries found matching "${query}"`));
        return;
      }

      console.log(`\n# Icon Libraries Matching "${query}"\n`);
      for (const r of results) {
        console.log(`## ${r.name}`);
        console.log(`- **Count**: ${r.count}`);
        console.log(`- **Type**: ${r.implementation_type}`);
        console.log(`- **Best For**: ${r.best_for}`);
        console.log(`- **Docs**: ${r.docs_url}`);
        console.log(`- **CDN**: \`${r.cdn_url}\``);
        console.log('');
      }
    } else {
      console.log(`\n# Top Icon Libraries (2025)\n`);
      console.log('| Name | Count | Type | Best For |');
      console.log('|---|---|---|---|');
      for (const r of records) {
        console.log(`| ${r.name} | ${r.count} | ${r.implementation_type} | ${r.best_for} |`);
      }
      console.log('\nRun `design-cli icons [name]` for details.\n');
    }

  } catch (err) {
    console.error(chalk.red('Failed to load icons:'), err);
  }
}
