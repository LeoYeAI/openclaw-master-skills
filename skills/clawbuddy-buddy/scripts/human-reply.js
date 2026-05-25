#!/usr/bin/env node
/**
 * Human Reply Helper
 * Usage: node human-reply.js <session-id> "Your guidance here"
 * 
 * Writes human guidance to the consult file that the buddy listener polls for.
 * Use this when a hatchling question triggers [NEEDS_HUMAN] and you want to provide input.
 */

import fs from 'fs';

const [sessionId, ...messageParts] = process.argv.slice(2);
const message = messageParts.join(' ');

if (!sessionId || !message) {
  console.error('Usage: node human-reply.js <session-id> "Your guidance here"');
  console.error('');
  console.error('Check /tmp/buddy-consult-*.txt for pending consultations.');
  process.exit(1);
}

const consultFile = `/tmp/buddy-consult-${sessionId}.txt`;
fs.writeFileSync(consultFile, message, 'utf-8');
console.log(`✅ Guidance written for session ${sessionId}`);
console.log(`   The buddy listener will pick this up and generate a response.`);
