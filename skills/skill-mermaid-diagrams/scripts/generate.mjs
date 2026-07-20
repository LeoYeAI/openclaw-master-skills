#!/usr/bin/env node
/**
 * Mermaid Diagrams Generator
 * 
 * Renders Mermaid diagrams from pre-generated content JSON files.
 * Designed to work with AI subagent patterns.
 * 
 * Usage:
 *   node generate.mjs --content diagrams/chapter-01/content.json --out diagrams/chapter-01
 */

import fs from "fs";
import path from "path";
import { parseArgs } from "util";
import { fileURLToPath } from "url";
import { execSync } from "child_process";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TEMPLATES_DIR = path.join(__dirname, "../assets");

// Parse arguments
const { values: args } = parseArgs({
  options: {
    content: { type: "string", short: "c" },
    out: { type: "string", short: "o", default: "./diagrams" },
  },
  strict: true,
});

if (!args.content) {
  console.error("Error: --content required.");
  console.error("Usage: node generate.mjs --content content.json --out output-dir");
  process.exit(1);
}

const outDir = args.out;

// Ensure output directory exists
fs.mkdirSync(outDir, { recursive: true });

// Load content JSON
let content;
try {
  content = JSON.parse(fs.readFileSync(args.content, "utf-8"));
} catch (error) {
  console.error(`❌ Failed to load content file: ${error.message}`);
  process.exit(1);
}

console.log(`\n📖 Rendering diagrams from: ${args.content}`);
console.log(`📊 Found ${content.diagrams.length} diagrams to render\n`);

/**
 * Validate content before rendering
 */
function validateContent(templateContent, template, placeholders) {
  const warnings = [];
  
  // Check 1: Unresolved placeholders
  const unresolvedMatches = templateContent.match(/\{\{[A-Z_0-9]+\}\}/g);
  if (unresolvedMatches) {
    warnings.push(`⚠️  Unresolved placeholders: ${unresolvedMatches.join(", ")}`);
  }
  
  // Check 2: Text length (readability)
  const maxLengths = {
    'architecture': 50,
    'flowchart': 40,
    'sequence': 30,
    'concept-map': 35,
    'radial-concept': 40,
    'timeline': 25,
    'comparison': 35,
    'comparison-table': 40,
    'gantt': 40,
    'mindmap': 30,
    'class-diagram': 35,
    'state-diagram': 30
  };
  
  const maxLength = maxLengths[template] || 50;
  for (const [key, value] of Object.entries(placeholders)) {
    if (typeof value === 'string' && value.length > maxLength) {
      warnings.push(`⚠️  ${key}: "${value}" (${value.length} chars, recommend <${maxLength})`);
    }
  }
  
  // Check 3: Special characters that might break Mermaid
  const problematicChars = /[<>{}[\]]/;
  for (const [key, value] of Object.entries(placeholders)) {
    if (typeof value === 'string' && problematicChars.test(value)) {
      warnings.push(`⚠️  ${key}: contains special characters (<>{}[]) that may break rendering`);
    }
  }
  
  return warnings;
}

/**
 * Render a single diagram from content
 */
async function renderDiagramFromContent(diagramData, index) {
  const { template, placeholders } = diagramData;
  const templatePath = path.join(TEMPLATES_DIR, `${template}.mmd`);
  
  if (!fs.existsSync(templatePath)) {
    console.error(`   ❌ Template not found: ${template}`);
    return null;
  }
  
  let templateContent = fs.readFileSync(templatePath, "utf-8");
  
  // Fill template with placeholders
  for (const [key, value] of Object.entries(placeholders)) {
    templateContent = templateContent.replaceAll(`{{${key}}}`, value);
  }
  
  // Validate before saving
  const warnings = validateContent(templateContent, template, placeholders);
  if (warnings.length > 0) {
    console.log(`\n⚠️  Validation warnings for ${template}:`);
    warnings.forEach(w => console.log(`   ${w}`));
    console.log();
  }
  
  // Save .mmd file
  const mmdPath = path.join(outDir, `diagram-${String(index + 1).padStart(2, "0")}-${template}.mmd`);
  fs.writeFileSync(mmdPath, templateContent);
  console.log(`   💾 Saved: ${path.basename(mmdPath)}`);
  
  return { template, mmdPath, index };
}

/**
 * Step 3: Validate and render diagrams
 */
async function renderDiagram({ mmdPath, templateName, index }) {
  const svgPath = mmdPath.replace(".mmd", ".svg");
  const pngPath = mmdPath.replace(".mmd", ".png");
  
  try {
    // Validate syntax by attempting to render
    execSync(`mmdc -i ${mmdPath} -o ${svgPath} -t default -b transparent`, {
      stdio: "ignore",
    });
    
    // Also render PNG for compatibility
    execSync(`mmdc -i ${mmdPath} -o ${pngPath} -t default -b transparent -w 1200`, {
      stdio: "ignore",
    });
    
    console.log(`   ✅ Rendered: ${svgPath} + ${pngPath}`);
    return true;
  } catch (error) {
    console.error(`   ❌ Rendering failed for ${templateName}:`, error.message);
    return false;
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    // Check if mmdc is installed
    try {
      execSync("which mmdc", { stdio: "ignore" });
    } catch {
      console.error("❌ Error: mermaid-cli (mmdc) not found.");
      console.error("   Install with: npm install -g @mermaid-js/mermaid-cli");
      process.exit(1);
    }
    
    // Render all diagrams from content
    const results = [];
    for (let i = 0; i < content.diagrams.length; i++) {
      const result = await renderDiagramFromContent(content.diagrams[i], i);
      if (result) results.push(result);
    }
    
    if (results.length === 0) {
      console.error("\n❌ No diagrams rendered successfully.");
      process.exit(1);
    }
    
    console.log(`\n🎨 Rendering to SVG/PNG...\n`);
    
    // Render to SVG/PNG
    let successCount = 0;
    for (const result of results) {
      const success = await renderDiagram(result);
      if (success) successCount++;
    }
    
    console.log(`\n✅ Successfully rendered ${successCount}/${results.length} diagrams in ${outDir}\n`);
    
    // Save summary
    const summary = {
      source: args.content,
      generated: new Date().toISOString(),
      diagrams: results.map((r, i) => ({
        index: i + 1,
        template: r.template,
        files: {
          source: path.basename(r.mmdPath),
          svg: path.basename(r.mmdPath).replace(".mmd", ".svg"),
          png: path.basename(r.mmdPath).replace(".mmd", ".png"),
        },
      })),
    };
    
    fs.writeFileSync(
      path.join(outDir, "summary.json"),
      JSON.stringify(summary, null, 2)
    );
    
  } catch (error) {
    console.error("\n❌ Fatal error:", error.message);
    process.exit(1);
  }
}

main();
