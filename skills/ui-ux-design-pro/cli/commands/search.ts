import chalk from 'chalk';
import { searchDesign } from '../lib/search';

export async function searchCommand(query: string, options: { domain?: string; format?: string }) {
  // console.log(chalk.blue(`Searching for "${query}"...`));
  
  try {
    const hits = await searchDesign(query, options.domain);

    if (hits.length === 0) {
      console.log(chalk.yellow(`No results found for "${query}"`));
      return;
    }

    if (options.format === 'json') {
      console.log(JSON.stringify(hits, null, 2));
      return;
    }

    // Markdown Output (Default for LLM)
    console.log(`\n# Search Results: "${query}"\n`);
    
    // Group by category
    const grouped: Record<string, typeof hits> = {};
    for (const hit of hits) {
      if (!grouped[hit.category]) grouped[hit.category] = [];
      grouped[hit.category]!.push(hit);
    }

    for (const [category, items] of Object.entries(grouped)) {
      console.log(`## ${category.toUpperCase()}\n`);
      
      for (const item of items) {
        // console.log(`### ${item.title} (Score: ${item.score.toFixed(2)})`);
        console.log(`### ${item.title}`);
        
        for (const [key, val] of Object.entries(item.data)) {
          if (val && String(val).trim() && key !== 'title' && key !== 'name' && key !== 'Category') {
            console.log(`- **${key}**: ${String(val).replace(/\n/g, ' ')}`);
          }
        }
        console.log('');
      }
      console.log('---\n');
    }

  } catch (err) {
    console.error(chalk.red('Search failed:'), err);
    process.exit(1);
  }
}
