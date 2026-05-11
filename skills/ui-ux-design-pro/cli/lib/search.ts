import { create, insertMultiple, search as oramaSearch } from '@orama/orama';
import { stemmer } from '@orama/stemmers/english';
import { parse } from 'csv-parse/sync';
import { readdir, readFile } from 'fs/promises';
import { join } from 'path';
import chalk from 'chalk';

// Define the "Masterpiece" Schema
// We map all distinct CSVs into this unified structure for global search
type DesignDoc = {
  id: string;
  category: string; // The domain/filename (e.g., 'style', 'color')
  title: string;    // The primary name/key
  content: string;  // The full searchable text
  raw: string;      // Original data as JSON string for display
};

const DATA_DIR = join(import.meta.dir, '../data');

// Map CSV filenames to their "primary key" column for the title
const TITLE_KEYS: Record<string, string[]> = {
  'styles.csv': ['Style Category', 'Style', 'Name'],
  'colors.csv': ['Industry', 'Palette'],
  'icons.csv': ['Name', 'Library'],
  'icon-libraries.csv': ['name'],
  'ui-reasoning.csv': ['Category', 'Pattern'],
  'ux-guidelines.csv': ['Issue', 'Category'],
  'typography.csv': ['Pairing', 'Font'],
  'ai-hallucinations.csv': ['Error_Name', 'Category'],
  'components.csv': ['Name', 'Category'],
};

// Global index singleton
let db: any = null;

export async function getIndex() {
  if (db) return db;

  // Initialize Orama
  db = await create({
    schema: {
      id: 'string',
      category: 'string',
      title: 'string',
      content: 'string',
      raw: 'string',
    },
    components: {
      tokenizer: {
        stemming: true,
        stemmer,
      },
    },
  });

  // Load all CSVs
  try {
    const files = await readdir(DATA_DIR);
    const csvFiles = files.filter(f => f.endsWith('.csv'));
    
    // console.log(chalk.gray(`Indexing ${csvFiles.length} databases...`));

    const docs: DesignDoc[] = [];

    for (const file of csvFiles) {
      const category = file.replace('.csv', '');
      const filePath = join(DATA_DIR, file);
      const csvContent = await readFile(filePath, 'utf-8');
      
      try {
        const records = parse(csvContent, {
          columns: true,
          skip_empty_lines: true,
          trim: true,
          relax_column_count: true,
          relax_quotes: true,
        });

        for (const row of records) {
          // Find a suitable title
          let title = 'Unknown';
          const possibleKeys = TITLE_KEYS[file] || Object.keys(row as object);
          for (const key of possibleKeys) {
            if ((row as Record<string, string>)[key]) {
              title = (row as Record<string, string>)[key] || 'Unknown';
              break;
            }
          }

          // Create a rich content string for searching
          // Filter out negative columns to avoid "Do Not Use For: Healthcare" matching "Healthcare" query
          const negativeKeys = ['Do Not Use For', 'Don\'t', 'Code Example Bad'];
          
          const content = Object.entries(row as object)
            .filter(([key]) => !negativeKeys.some(neg => key.includes(neg)))
            .map(([_, val]) => val)
            .join(' ');

          docs.push({
            id: `${category}-${Math.random().toString(36).slice(2)}`,
            category,
            title,
            content,
            raw: JSON.stringify(row),
          });
        }
      } catch (parseErr) {
        console.warn(chalk.yellow(`Warning: Failed to parse ${file}:`), parseErr instanceof Error ? parseErr.message : parseErr);
      }
    }

    await insertMultiple(db, docs);
    return db;

  } catch (err) {
    console.error(chalk.red('Failed to index data:'), err);
    return db;
  }
}

export async function searchDesign(query: string, domain?: string) {
  const index = await getIndex();
  
  const results = await oramaSearch(index, {
    term: query,
    properties: '*', // Search all fields
    threshold: 0.2, // Fuzzy tolerance
    tolerance: 1,
    limit: 20,
    where: domain ? { category: domain } : undefined,
    boost: {
      title: 2,
      category: 1.5,
      content: 1,
    },
  });

  return results.hits.map(hit => ({
    id: hit.document.id,
    score: hit.score,
    category: hit.document.category,
    title: hit.document.title,
    data: JSON.parse(hit.document.raw as string),
  }));
}
