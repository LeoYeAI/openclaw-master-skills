#!/usr/bin/env node
/**
 * Quick test for underscore support in DNS record names
 */

import { sanitizeRecordName } from './scripts/gandi-api.js';

const testCases = [
  // Should pass - service records with underscores
  { name: '_dmarc', expected: '_dmarc', shouldPass: true },
  { name: 'resend._domainkey', expected: 'resend._domainkey', shouldPass: true },
  { name: '_imap._tcp', expected: '_imap._tcp', shouldPass: true },
  { name: '_domainkey.mail', expected: '_domainkey.mail', shouldPass: true },
  
  // Should still pass - regular records
  { name: 'www', expected: 'www', shouldPass: true },
  { name: 'mail.example', expected: 'mail.example', shouldPass: true },
  { name: '*', expected: '*', shouldPass: true },
  { name: '@', expected: '@', shouldPass: true },
  
  // Should still fail - invalid formats
  { name: 'www_test', expected: null, shouldPass: false }, // Underscore not at start
  { name: 'test..example', expected: null, shouldPass: false }, // Path traversal
  { name: 'test/example', expected: null, shouldPass: false }, // Path separator
];

console.log('Testing underscore support in DNS record names...\n');

let passed = 0;
let failed = 0;

for (const test of testCases) {
  try {
    const result = sanitizeRecordName(test.name);
    if (test.shouldPass) {
      if (result === test.expected) {
        console.log(`✅ PASS: "${test.name}" → "${result}"`);
        passed++;
      } else {
        console.log(`❌ FAIL: "${test.name}" expected "${test.expected}", got "${result}"`);
        failed++;
      }
    } else {
      console.log(`❌ FAIL: "${test.name}" should have thrown error but returned "${result}"`);
      failed++;
    }
  } catch (error) {
    if (!test.shouldPass) {
      console.log(`✅ PASS: "${test.name}" correctly rejected (${error.message})`);
      passed++;
    } else {
      console.log(`❌ FAIL: "${test.name}" should have passed but threw: ${error.message}`);
      failed++;
    }
  }
}

console.log(`\nResults: ${passed} passed, ${failed} failed`);
process.exit(failed > 0 ? 1 : 0);
