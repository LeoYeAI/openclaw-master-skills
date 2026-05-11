import chalk from 'chalk';
import { searchDesign } from '../lib/search';
import { generateAllTokens, generateTypographyScale, hexToHsl, hslToHex } from '../lib/generators';
import { writeFile } from 'fs/promises';

interface GenerateOptions {
  stack?: string;
  output?: string;
  format?: 'json' | 'css' | 'text' | 'markdown';
}

// --- Extraction Logic ---

async function extractPrimaryColor(results: Record<string, any[]>): Promise<string> {
   // Priority 1: Check 'color' domain (colors.csv) for structured hex
   if (results['color']) {
     for (const hit of results['color']) {
       const data = JSON.parse(hit.raw || '{}');
       // Check for explicit hex columns
       for (const key of ['Primary (Hex)', 'Primary Hex', 'Hex', 'Primary']) {
         if (data[key] && String(data[key]).startsWith('#')) {
           return String(data[key]).trim(); // Return immediately if found in colors.csv
         }
       }
     }
   }

   // Priority 2: Check 'style' and 'product' domains with Regex extraction
   const colorRegex = /#([0-9A-Fa-f]{3,6})\b/;
   for (const domain of ['style', 'product', 'landing', 'color']) { // Check color again as fallback
     if (results[domain]) {
       for (const hit of results[domain]) {
         const data = hit.data || {};
         
         // Look in specific columns first
         const targetKeys = ['Primary Colors', 'Primary (Hex)', 'Primary', 'primary', 'Design System Variables', 'CSS/Technical Keywords', 'Background (Hex)'];
         
         for (const key of targetKeys) {
            if (data[key]) {
              const match = String(data[key]).match(colorRegex);
              if (match) return match[0];
            }
         }
       }
     }
   }
   return '#2563EB'; // Fallback Blue
}

async function extractFont(results: Record<string, any[]>): Promise<string> {
  // Priority 1: 'typography' domain
  if (results['typography']) {
    for (const hit of results['typography']) {
       const data = hit.data || {};
       // Typography.csv has 'Heading Font' column
       if (data['Heading Font']) return String(data['Heading Font']).trim();
       if (data['Font Pairing Name']) {
          // If name is "Playfair + Source", take the first one
          const fontPairing = String(data['Font Pairing Name']).trim();
          // Ensure fontPairing is not "null" or "undefined" string from String() conversion
          if (fontPairing && fontPairing !== 'null' && fontPairing !== 'undefined') {
            return fontPairing.split('+')[0]?.trim() || 'Inter';
          }
       }
    }
  }

  // Priority 2: Extract from 'style' domain keywords
  if (results['style']) {
     for (const hit of results['style']) {
        const data = hit.data || {};
        const text = (data['CSS/Technical Keywords'] || '') + (data['Design System Variables'] || '');
        
        // Naive check for common fonts in our dataset
        const commonFonts = ['Inter', 'Roboto', 'Open Sans', 'Lato', 'Montserrat', 'Playfair Display', 'Merriweather', 'Space Grotesk', 'Courier New', 'Share Tech Mono', 'Russo One'];
        for (const font of commonFonts) {
           if (text.toLowerCase().includes(font.toLowerCase())) return font;
        }
        
        if (text.includes('monospace')) return 'Courier New';
        if (text.includes('serif')) return 'Merriweather';
     }
  }
  return 'Inter';
}

async function extractStyleName(results: Record<string, any[]>): Promise<string> {
    // Try to find a style name from 'style' domain
    if (results['style']) {
        for (const hit of results['style']) {
             const data = hit.data || {};
             if (data['Style Category']) return data['Style Category'];
             if (data['name']) return data['name'];
        }
    }
    // Fallback: Use the query title-cased if reasonable length
    return 'Custom Design';
}

// --- Architectural Palette Generator ---

type ColorScale = Record<number, string>;
interface ArchitecturalPalette {
  primary: ColorScale;
  neutral: ColorScale;
  success: ColorScale;
  warning: ColorScale;
  error: ColorScale;
}

function generateTwScale(baseHex: string, saturationAdjust: number = 0): ColorScale {
  const [h, s, l] = hexToHsl(baseHex);
  const scale: ColorScale = {};
  
  // Figma/Tailwind standard lightness steps (approximate)
  const steps = [
    { stop: 50, l: 95 },
    { stop: 100, l: 90 },
    { stop: 200, l: 80 },
    { stop: 300, l: 70 },
    { stop: 400, l: 60 },
    { stop: 500, l: 50 }, // Base
    { stop: 600, l: 40 },
    { stop: 700, l: 30 },
    { stop: 800, l: 20 },
    { stop: 900, l: 10 },
    { stop: 950, l: 5 },
  ];

  steps.forEach(step => {
    // Optical adjustment: very light/dark shades often need slightly more saturation to not look washed out
    let newS = s + saturationAdjust;
    if (step.stop <= 100 || step.stop >= 900) newS += 5;
    
    // Clamp saturation
    newS = Math.max(0, Math.min(100, newS));
    
    scale[step.stop] = hslToHex(h, newS, step.l);
  });

  return scale;
}

function generateArchitecturalPalette(primaryHex: string): ArchitecturalPalette {
  return {
    primary: generateTwScale(primaryHex),
    // Neutral: Desaturated primary (classic architectural pattern)
    neutral: generateTwScale(primaryHex, -15), // Reduced saturation
    // Semantic Colors (fixed hues, matching primary lightness rhythm)
    success: generateTwScale('#22C55E'), // Green-500
    warning: generateTwScale('#EAB308'), // Yellow-500
    error: generateTwScale('#EF4444'),   // Red-500
  };
}

// --- Markdown Generator ---


function generateEnhancedMarkdown(system: any, components: { atoms: any[], molecules: any[], organisms: any[] }) {
  const { meta, style, palette, type_scale, tokens } = system;
  const stackInfo = meta.stack ? ` | **Tech Stack**: ${meta.stack}` : '';

  const renderSection = (title: string, items: any[]) => {
    if (!items || !items.length) return '';
    return `## ${title}
${items.map((item: any) => `
### ${item.title}
> ${item.data.Description || ''}

| Feature | Details |
| :--- | :--- |
| **Usage** | ${item.data.Usage || 'N/A'} |
| **Variants** | ${item.data.State_Variants || 'N/A'} |
| **CSS Variable** | \`${item.data.CSS_Variables || 'N/A'}\` |

**Code Example (Tailwind)**
\`\`\`tsx
${item.data.Code_Snippet || '// No snippet available'}
\`\`\`

> [!TIP]
> **Best Practice**: ${item.data.Best_Practices || 'Follow standard UI guidelines.'}

> [!NOTE]
> **Accessibility**: ${item.data.Accessibility_Note || 'Ensure accessible contrast and semantic HTML.'}

`).join('\n')}
`;
  };
  
  let md = `# Design System: ${style.name}\n\n`;
  md += `> **Query**: "${meta.query}"${stackInfo} | **Generated**: ${new Date(meta.generated_at).toLocaleDateString()}\n\n`;
  
  md += `## 01. Foundation\n`;
  md += `- **Primary Color**: \`${style.primary_color}\` ![${style.primary_color}](https://via.placeholder.com/15/${style.primary_color.substring(1)}/000000?text=+)\n`;
  md += `- **Typography**: **${style.font_family}** (Headings & Body)\n\n`;

  md += `### Color Palette\n`;
  const renderScale = (name: string, scale: Record<number, string>) => {
    let table = `#### ${name}\n`;
    table += `| Stop | Hex | Preview |\n| :--- | :--- | :--- |\n`;
    for (const [stop, hex] of Object.entries(scale)) {
      const cleanHex = hex.substring(1);
      table += `| **${stop}** | \`${hex}\` | ![${hex}](https://via.placeholder.com/80x30/${cleanHex}/${cleanHex}?text=+) |\n`;
    }
    return table + '\n';
  };

  md += renderScale('Primary Brand', palette.primary);
  md += renderScale('Neutral', palette.neutral);
  
  md += `### Tokens
- **Spacing Base**: ${tokens.spacing?.base || '4px'}
- **Radius**: ${tokens.radius?.default || '4px'}
- **Shadows**: Soft, layered shadows for depth.

`;

  md += `## 02. Atoms
${renderSection('Atoms', components.atoms)}

## 03. Molecules
${renderSection('Molecules', components.molecules)}

## 04. Organisms
${renderSection('Organisms', components.organisms)}

---
*Generated by Design Pro CLI v0.1.1*`;
  return md;
}

// --- Main Command ---

export async function generateSystemCommand(query: string, options: GenerateOptions) {
  // 1. Search across domains
  const domains = ['product', 'style', 'color', 'landing', 'typography', 'reasoning', 'ux', 'chart'];
  const allResults: Record<string, any[]> = {};
  
  for (const domain of domains) {
    const hits = await searchDesign(query, domain);
    if (hits.length > 0) {
      allResults[domain] = hits;
    }
  }

  // 2. Extract key parameters
  const primaryColor = await extractPrimaryColor(allResults);
  const fontFamily = await extractFont(allResults);
  const styleName = await extractStyleName(allResults);

  // 3. Generate System
  const architecturalPalette = generateArchitecturalPalette(primaryColor);
  const typeScale = generateTypographyScale(16, 1.25, 8);
  const tokens = generateAllTokens(primaryColor, '#64748B', 12, fontFamily);

  const system = {
    meta: {
      query,
      stack: options.stack,
      generated_at: new Date().toISOString(),
      version: '2.0.0',
    },
    style: {
      name: styleName,
      primary_color: primaryColor,
      font_family: fontFamily,
    },
    palette: architecturalPalette,
    type_scale: typeScale,
    tokens,
  };

  // 4. Gather Components
  const atoms = await searchDesign('Atom', 'components');
  const molecules = await searchDesign('Molecule', 'components');
  const organisms = await searchDesign('Organism', 'components');

  // Determine Output Format
  let outputContent = '';
  const isMarkdown = options.output?.endsWith('.md') || options.format === 'markdown';

  if (isMarkdown) {
    outputContent = generateEnhancedMarkdown(system, { atoms, molecules, organisms });
  } else if (options.format === 'json') {
    outputContent = JSON.stringify({ ...system, components: { atoms, molecules, organisms } }, null, 2);
  } else {
    // Legacy CLI Text output
    console.log(chalk.bold(`\n  Design System: ${styleName}`));
    console.log(`  Query: ${query}`);
    console.log(`  Primary: ${chalk.hex(primaryColor)(primaryColor)}`);
    console.log(`  Font: ${fontFamily}`);
    console.log(chalk.green('  (Full architectural palette generated internally)'));
    return;
  }

  // 4. Write Output or Print
  if (options.output) {
    await writeFile(options.output, outputContent);
    console.log(chalk.green(`  ✨ Design system saved to: ${options.output}`));
  } else {
    console.log(outputContent);
  }
}
