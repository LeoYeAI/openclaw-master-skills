#!/usr/bin/env node
/**
 * Semantic Validation Test Runner
 * 
 * Runs comprehensive test suite for semantic validation rules.
 * Tests both positive cases (should pass) and negative cases (should fail with specific suggestions).
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { validateSemantics, generateCorrections } from "./semantic-validate.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const TESTS_FILE = path.join(__dirname, "../tests/semantic-validation-tests.json");

/**
 * Run all tests
 */
function runTests() {
  const testData = JSON.parse(fs.readFileSync(TESTS_FILE, 'utf-8'));
  
  console.log(`\n🧪 Running ${testData.testSuite} Test Suite\n`);
  console.log(`   Version: ${testData.version}`);
  console.log(`   Tests: ${testData.tests.length}\n`);
  console.log(`${'='.repeat(80)}\n`);
  
  let passed = 0;
  let failed = 0;
  const failures = [];
  
  for (const [index, test] of testData.tests.entries()) {
    const testNum = index + 1;
    const result = runTest(test, testNum);
    
    if (result.passed) {
      passed++;
      console.log(`✅ Test ${testNum}: ${test.name}`);
    } else {
      failed++;
      console.log(`❌ Test ${testNum}: ${test.name}`);
      failures.push({ testNum, test, result });
    }
  }
  
  console.log(`\n${'='.repeat(80)}\n`);
  console.log(`📊 Results: ${passed}/${testData.tests.length} passed\n`);
  
  if (failures.length > 0) {
    console.log(`❌ Failed Tests:\n`);
    for (const failure of failures) {
      console.log(`   Test ${failure.testNum}: ${failure.test.name}`);
      console.log(`   Expected: ${JSON.stringify(failure.test.expected)}`);
      console.log(`   Got: ${JSON.stringify(failure.result.actual)}`);
      console.log();
    }
  }
  
  return failed === 0;
}

/**
 * Run single test
 */
function runTest(test, testNum) {
  const validation = validateSemantics(test.template, test.placeholders);
  
  const actual = {
    pass: validation.passed && validation.warnings.length === 0,
    errors: validation.errors.length,
    warnings: validation.warnings.length
  };
  
  if (test.expected.suggestedTemplates) {
    const corrections = generateCorrections(validation, { placeholders: test.placeholders });
    actual.suggestedTemplates = corrections.map(c => c.suggestedTemplate);
  }
  
  // Check if actual matches expected
  let passed = true;
  
  if (test.expected.pass !== undefined && actual.pass !== test.expected.pass) {
    passed = false;
  }
  
  if (test.expected.errors !== undefined && actual.errors !== test.expected.errors) {
    passed = false;
  }
  
  if (test.expected.warnings !== undefined && actual.warnings !== test.expected.warnings) {
    passed = false;
  }
  
  if (test.expected.suggestedTemplates) {
    const suggestedMatch = test.expected.suggestedTemplates.some(expected =>
      actual.suggestedTemplates?.includes(expected)
    );
    if (!suggestedMatch) {
      passed = false;
    }
  }
  
  return { passed, actual };
}

/**
 * Run tests
 */
if (import.meta.url === `file://${process.argv[1]}`) {
  const allPassed = runTests();
  process.exit(allPassed ? 0 : 1);
}

export { runTests };
