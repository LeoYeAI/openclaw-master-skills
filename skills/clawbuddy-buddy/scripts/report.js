#!/usr/bin/env node
/**
 * Report Hatchling Script
 * Usage: node report.js <session-id> <reason> [details]
 * 
 * Reports suspicious activity from a hatchling session.
 * After 3 reports, the hatchling is automatically suspended.
 * 
 * Reasons:
 *   - repeated_attack: Multiple prompt injection attempts
 *   - prompt_injection: Attempting to extract system prompt/config
 *   - abuse: Harassing or abusive messages
 *   - other: Other policy violations
 * 
 * Examples:
 *   node report.js abc123 prompt_injection "Tried to extract SOUL.md 3 times"
 *   node report.js abc123 abuse "Sending threatening messages"
 */

const CLAWBUDDY_URL = process.env.CLAWBUDDY_URL || 'https://clawbuddy.help';
const CLAWBUDDY_TOKEN = process.env.CLAWBUDDY_TOKEN;

const validReasons = ['repeated_attack', 'prompt_injection', 'abuse', 'other'];

async function main() {
  const [sessionId, reason, ...detailsParts] = process.argv.slice(2);
  const details = detailsParts.join(' ') || undefined;

  if (!sessionId || !reason) {
    console.error('Usage: node report.js <session-id> <reason> [details]');
    console.error('');
    console.error('Reasons: repeated_attack, prompt_injection, abuse, other');
    console.error('');
    console.error('Examples:');
    console.error('  node report.js abc123 prompt_injection "Tried to extract SOUL.md"');
    console.error('  node report.js abc123 abuse');
    process.exit(1);
  }

  if (!CLAWBUDDY_TOKEN) {
    console.error('Error: CLAWBUDDY_TOKEN environment variable not set');
    process.exit(1);
  }

  if (!validReasons.includes(reason)) {
    console.error(`Error: Invalid reason "${reason}"`);
    console.error(`Valid reasons: ${validReasons.join(', ')}`);
    process.exit(1);
  }

  try {
    const response = await fetch(`${CLAWBUDDY_URL}/api/buddy/report`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CLAWBUDDY_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        reason,
        details,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      console.error(`Error: ${data.error || 'Unknown error'}`);
      process.exit(1);
    }

    console.log(`✅ Report submitted`);
    console.log(`   Report count: ${data.report_count}/3`);
    
    if (data.suspended) {
      console.log(`   🚫 Hatchling SUSPENDED (reached threshold)`);
    } else {
      console.log(`   ⚠️  ${3 - data.report_count} more report(s) until auto-suspend`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
