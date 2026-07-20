#!/usr/bin/env node
/**
 * Automatic Correction with Iterative Validation
 * 
 * Implements iterative feedback cycle:
 * 1. Validate content semantically
 * 2. Detect template/content mismatches
 * 3. Generate corrected versions with suggested templates
 * 4. Re-validate corrections
 * 5. Repeat until all diagrams pass or max iterations reached
 * 
 * This is the "right and hard things" implementation - proper engineering feedback loop.
 */

import fs from "fs";
import path from "path";
import { parseArgs } from "util";
import { validateSemantics, generateCorrections } from "./semantic-validate.mjs";

/**
 * Template placeholder mappings for auto-conversion
 */
const TEMPLATE_CONVERSIONS = {
  // Flowchart (sequential) → State-diagram
  'flowchart->state-diagram': (placeholders) => {
    const converted = {};
    let stateIndex = 1;
    let transitionIndex = 1;
    
    // Extract sequential actions
    const actions = Object.entries(placeholders)
      .filter(([k, v]) => k.includes('ACTION') || k.includes('LABEL'))
      .sort((a, b) => a[0].localeCompare(b[0]));
    
    for (const [key, value] of actions) {
      converted[`STATE_${stateIndex}`] = value;
      if (stateIndex > 1) {
        converted[`TRANSITION_${transitionIndex}_LABEL`] = 'Next';
        transitionIndex++;
      }
      stateIndex++;
    }
    
    return converted;
  },
  
  // Flowchart (sequential) → Timeline
  'flowchart->timeline': (placeholders) => {
    const converted = {};
    let eventIndex = 1;
    
    const actions = Object.entries(placeholders)
      .filter(([k, v]) => k.includes('ACTION') || k.includes('LABEL'))
      .sort((a, b) => a[0].localeCompare(b[0]));
    
    for (const [key, value] of actions) {
      converted[`EVENT_${eventIndex}`] = value;
      converted[`DATE_${eventIndex}`] = `Phase ${eventIndex}`;
      eventIndex++;
    }
    
    return converted;
  },
  
  // Architecture → Flowchart
  'architecture->flowchart': (placeholders) => {
    const converted = {};
    let actionIndex = 1;
    
    const components = Object.entries(placeholders)
      .filter(([k, v]) => k.includes('COMPONENT') && k.includes('LABEL'))
      .sort((a, b) => a[0].localeCompare(b[0]));
    
    if (components.length > 0) {
      converted.START_LABEL = components[0][1];
    }
    
    for (let i = 1; i < components.length; i++) {
      converted[`ACTION_${actionIndex}`] = components[i][1];
      actionIndex++;
    }
    
    if (components.length > 0) {
      converted.END_LABEL = 'Complete';
    }
    
    return converted;
  },
  
  // Sequence (single-actor) → Flowchart
  'sequence->flowchart': (placeholders) => {
    const converted = {};
    let actionIndex = 1;
    
    const messages = Object.entries(placeholders)
      .filter(([k, v]) => k.includes('MESSAGE'))
      .sort((a, b) => a[0].localeCompare(b[0]));
    
    if (messages.length > 0) {
      converted.START_LABEL = messages[0][1];
    }
    
    for (let i = 1; i < messages.length - 1; i++) {
      converted[`ACTION_${actionIndex}`] = messages[i][1];
      actionIndex++;
    }
    
    if (messages.length > 1) {
      converted.END_LABEL = messages[messages.length - 1][1];
    }
    
    return converted;
  },
  
  // Comparison (no coords) → Comparison-table
  'comparison->comparison-table': (placeholders) => {
    const converted = {};
    
    // Extract options
    const options = Object.entries(placeholders)
      .filter(([k, v]) => k.includes('OPTION') && !k.includes('_'));
    
    if (options.length >= 2) {
      converted.OPTION_1_TITLE = options[0][1];
      converted.OPTION_2_TITLE = options[1][1];
    }
    
    // Extract criteria
    const criteria = Object.entries(placeholders)
      .filter(([k, v]) => k.includes('CRITERION') || k.includes('LABEL'))
      .sort((a, b) => a[0].localeCompare(b[0]));
    
    for (let i = 0; i < Math.min(criteria.length, 4); i++) {
      const criterionIndex = i + 1;
      converted[`OPTION_1_CRITERION_${criterionIndex}`] = criteria[i][1];
      converted[`OPTION_2_CRITERION_${criterionIndex}`] = criteria[i][1];
    }
    
    return converted;
  },
  
  // Gantt (no temporal) → Timeline
  'gantt->timeline': (placeholders) => {
    const converted = {};
    let eventIndex = 1;
    
    const tasks = Object.entries(placeholders)
      .filter(([k, v]) => k.includes('TASK') && !k.includes('_'))
      .sort((a, b) => a[0].localeCompare(b[0]));
    
    for (const [key, value] of tasks) {
      converted[`EVENT_${eventIndex}`] = value;
      converted[`DATE_${eventIndex}`] = `Phase ${eventIndex}`;
      eventIndex++;
    }
    
    return converted;
  }
};

/**
 * Attempt to auto-convert placeholders to suggested template
 */
function convertPlaceholders(fromTemplate, toTemplate, originalPlaceholders) {
  const conversionKey = `${fromTemplate}->${toTemplate}`;
  
  if (TEMPLATE_CONVERSIONS[conversionKey]) {
    return TEMPLATE_CONVERSIONS[conversionKey](originalPlaceholders);
  }
  
  // No conversion available - return original
  return null;
}

/**
 * Iterative validation and correction cycle
 */
async function iterativeCorrection(content, maxIterations = 3) {
  const history = [];
  let iteration = 0;
  let currentContent = JSON.parse(JSON.stringify(content)); // Deep copy
  
  console.log(`\n🔄 Starting iterative correction cycle (max ${maxIterations} iterations)\n`);
  
  while (iteration < maxIterations) {
    iteration++;
    console.log(`\n${'─'.repeat(80)}`);
    console.log(`Iteration ${iteration}/${maxIterations}`);
    console.log(`${'─'.repeat(80)}\n`);
    
    let allPassed = true;
    const corrections = [];
    
    // Validate all diagrams
    for (const [index, diagram] of currentContent.diagrams.entries()) {
      const validation = validateSemantics(diagram.template, diagram.placeholders);
      
      console.log(`📊 Diagram ${index + 1}: ${diagram.template}`);
      
      if (validation.passed && validation.warnings.length === 0) {
        console.log(`   ✅ PASS\n`);
        continue;
      }
      
      allPassed = false;
      
      // Print issues
      if (validation.errors.length > 0) {
        console.log(`   ❌ Errors: ${validation.errors.length}`);
        for (const error of validation.errors) {
          console.log(`      - ${error.message}`);
        }
      }
      
      if (validation.warnings.length > 0) {
        console.log(`   ⚠️  Warnings: ${validation.warnings.length}`);
        for (const warning of validation.warnings) {
          console.log(`      - ${warning.message}`);
        }
      }
      
      // Generate corrections
      const suggestedCorrections = generateCorrections(validation, diagram);
      
      if (suggestedCorrections.length > 0) {
        const best = suggestedCorrections[0];
        console.log(`\n   💡 Auto-correction available:`);
        console.log(`      ${diagram.template} → ${best.suggestedTemplate} (${(best.confidence * 100).toFixed(0)}% confidence)`);
        console.log(`      Reason: ${best.reason}`);
        
        // Attempt conversion
        const convertedPlaceholders = convertPlaceholders(
          diagram.template,
          best.suggestedTemplate,
          diagram.placeholders
        );
        
        if (convertedPlaceholders) {
          console.log(`      ✅ Placeholder conversion available\n`);
          corrections.push({
            index,
            from: diagram.template,
            to: best.suggestedTemplate,
            placeholders: convertedPlaceholders,
            confidence: best.confidence,
            reason: best.reason
          });
        } else {
          console.log(`      ⚠️  Manual placeholder mapping required\n`);
        }
      } else {
        console.log(`\n   ℹ️  No auto-corrections available\n`);
      }
    }
    
    // Apply corrections
    if (corrections.length > 0) {
      console.log(`\n🔧 Applying ${corrections.length} corrections...\n`);
      
      for (const correction of corrections) {
        console.log(`   ${correction.index + 1}. ${correction.from} → ${correction.to}`);
        currentContent.diagrams[correction.index].template = correction.to;
        currentContent.diagrams[correction.index].placeholders = correction.placeholders;
        currentContent.diagrams[correction.index]._correctionHistory = currentContent.diagrams[correction.index]._correctionHistory || [];
        currentContent.diagrams[correction.index]._correctionHistory.push({
          iteration,
          from: correction.from,
          to: correction.to,
          reason: correction.reason,
          confidence: correction.confidence
        });
      }
      
      history.push({
        iteration,
        corrections: corrections.length,
        details: corrections
      });
    } else if (!allPassed) {
      console.log(`\n⚠️  Issues detected but no auto-corrections available. Stopping.\n`);
      break;
    }
    
    // Check if all passed
    if (allPassed) {
      console.log(`\n✅ All diagrams passed validation!\n`);
      break;
    }
  }
  
  // Final summary
  console.log(`\n${'═'.repeat(80)}`);
  console.log(`Final Results`);
  console.log(`${'═'.repeat(80)}\n`);
  
  console.log(`Iterations: ${iteration}/${maxIterations}`);
  console.log(`Total corrections applied: ${history.reduce((sum, h) => sum + h.corrections, 0)}\n`);
  
  if (history.length > 0) {
    console.log(`Correction history:`);
    for (const record of history) {
      console.log(`  Iteration ${record.iteration}: ${record.corrections} corrections`);
      for (const detail of record.details) {
        console.log(`    - Diagram ${detail.index + 1}: ${detail.from} → ${detail.to} (${detail.reason})`);
      }
    }
    console.log();
  }
  
  return {
    iterations: iteration,
    originalContent: content,
    correctedContent: currentContent,
    history
  };
}

/**
 * CLI entry point
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const { values: args } = parseArgs({
    options: {
      content: { type: "string", short: "c" },
      out: { type: "string", short: "o" },
      maxIterations: { type: "string", default: "3" }
    },
    strict: true
  });
  
  if (!args.content) {
    console.error('Usage: node auto-correct.mjs --content content.json [--out corrected.json] [--maxIterations 3]');
    process.exit(1);
  }
  
  const content = JSON.parse(fs.readFileSync(args.content, 'utf-8'));
  const maxIterations = parseInt(args.maxIterations);
  
  const result = await iterativeCorrection(content, maxIterations);
  
  if (args.out) {
    fs.writeFileSync(args.out, JSON.stringify(result.correctedContent, null, 2));
    console.log(`\n💾 Corrected content saved to: ${args.out}\n`);
    
    // Also save correction report
    const reportPath = args.out.replace('.json', '-report.json');
    fs.writeFileSync(reportPath, JSON.stringify({
      iterations: result.iterations,
      history: result.history,
      summary: {
        totalCorrections: result.history.reduce((sum, h) => sum + h.corrections, 0),
        converged: result.iterations < maxIterations
      }
    }, null, 2));
    console.log(`📊 Correction report saved to: ${reportPath}\n`);
  }
}

export { iterativeCorrection, convertPlaceholders };
