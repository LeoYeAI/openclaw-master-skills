#!/usr/bin/env node
/**
 * Mermaid Diagram Validator
 * 
 * Validates generated Mermaid diagrams for:
 * - Syntax correctness
 * - Rendering without errors
 * - Consistent theming
 * - File completeness
 */

import fs from "fs";
import path from "path";
import { parseArgs } from "util";
import { execSync } from "child_process";

const { values: args } = parseArgs({
  options: {
    dir: { type: "string", short: "d" },
  },
  strict: true,
});

if (!args.dir) {
  console.error("Error: --dir required.");
  console.error("Usage: node validate.mjs --dir diagrams/chapter-01");
  process.exit(1);
}

const diagramDir = args.dir;

if (!fs.existsSync(diagramDir)) {
  console.error(`Error: Directory not found: ${diagramDir}`);
  process.exit(1);
}

console.log(`\n🔍 Validating diagrams in: ${diagramDir}\n`);

const mmdFiles = fs.readdirSync(diagramDir).filter(f => f.endsWith(".mmd"));

if (mmdFiles.length === 0) {
  console.error("❌ No .mmd files found in directory.");
  process.exit(1);
}

let passCount = 0;
let failCount = 0;

for (const mmdFile of mmdFiles) {
  const mmdPath = path.join(diagramDir, mmdFile);
  const svgPath = mmdPath.replace(".mmd", ".svg");
  const pngPath = mmdPath.replace(".mmd", ".png");
  
  console.log(`📄 ${mmdFile}`);
  
  const checks = [];
  
  // Check 1: File exists and is readable
  try {
    const content = fs.readFileSync(mmdPath, "utf-8");
    checks.push({ name: "File readable", pass: true });
    
    // Check 2: Contains theme config
    const hasTheme = content.includes("%%{init:");
    checks.push({ name: "Theme configured", pass: hasTheme });
    
    // Check 3: No unresolved placeholders
    const hasPlaceholders = /\{\{[A-Z_0-9]+\}\}/.test(content);
    checks.push({ name: "No placeholders", pass: !hasPlaceholders });
    
  } catch (error) {
    checks.push({ name: "File readable", pass: false, error: error.message });
  }
  
  // Check 4: SVG rendered
  checks.push({ name: "SVG rendered", pass: fs.existsSync(svgPath) });
  
  // Check 5: PNG rendered
  checks.push({ name: "PNG rendered", pass: fs.existsSync(pngPath) });
  
  // Check 6: Can re-render without errors
  try {
    const testSvg = mmdPath.replace(".mmd", "-test.svg");
    execSync(`mmdc -i ${mmdPath} -o ${testSvg} -t default -b transparent`, {
      stdio: "ignore",
    });
    fs.unlinkSync(testSvg);
    checks.push({ name: "Syntax valid", pass: true });
  } catch (error) {
    checks.push({ name: "Syntax valid", pass: false, error: error.message });
  }
  
  // Print results
  const allPass = checks.every(c => c.pass);
  for (const check of checks) {
    const icon = check.pass ? "✅" : "❌";
    const msg = check.error ? ` (${check.error})` : "";
    console.log(`   ${icon} ${check.name}${msg}`);
  }
  
  if (allPass) {
    passCount++;
    console.log(`   ✅ PASS\n`);
  } else {
    failCount++;
    console.log(`   ❌ FAIL\n`);
  }
}

console.log(`\n📊 Validation Results:`);
console.log(`   ✅ Passed: ${passCount}/${mmdFiles.length}`);
console.log(`   ❌ Failed: ${failCount}/${mmdFiles.length}\n`);

if (failCount > 0) {
  process.exit(1);
}
