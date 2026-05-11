#!/usr/bin/env node

/**
 * List email forwards for a domain
 * Usage: node list-email-forwards.js <domain>
 */

import { listEmailForwards, sanitizeDomain } from './gandi-api.js';

const [,, rawDomain] = process.argv;

if (!rawDomain) {
  console.error('❌ Usage: node list-email-forwards.js <domain>');
  console.error('');
  console.error('Example:');
  console.error('  node list-email-forwards.js example.com');
  process.exit(1);
}

// Sanitize domain input for security
let domain;
try {
  domain = sanitizeDomain(rawDomain);
} catch (error) {
  console.error(`❌ Invalid domain: ${error.message}`);
  process.exit(1);
}

async function main() {
  try {
    console.log(`📧 Fetching email forwards for ${domain}...`);
    console.log('');
    
    const forwards = await listEmailForwards(domain);
    
    if (!forwards || forwards.length === 0) {
      console.log('ℹ️  No email forwards configured for this domain.');
      console.log('');
      console.log('💡 Create an email forward with:');
      console.log(`   node add-email-forward.js ${domain} hello you@example.com`);
      console.log('');
      console.log('💡 Create catch-all forward:');
      console.log(`   node add-email-forward.js ${domain} @ catchall@example.com`);
      return;
    }
    
    console.log(`Found ${forwards.length} email forward(s):\n`);
    
    forwards.forEach((forward, index) => {
      const source = forward.source === '@' ? '@ (catch-all)' : forward.source;
      
      console.log(`${index + 1}. ${source}@${domain}`);
      console.log(`   Forwards to:`);
      forward.destinations.forEach(dest => {
        console.log(`   → ${dest}`);
      });
      console.log('');
    });
    
    console.log('──────────────────────────────────────────────────');
    console.log(`Total: ${forwards.length} forward(s)`);
    console.log('');
    console.log('💡 To add a forward:');
    console.log(`   node add-email-forward.js ${domain} <mailbox> <destination>`);
    console.log('');
    console.log('💡 To delete a forward:');
    console.log(`   node delete-email-forward.js ${domain} <mailbox>`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('   Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('   Permission denied. Ensure your token has Email read access.');
    } else if (error.statusCode === 404) {
      console.error(`   Domain ${domain} not found or email service not enabled.`);
      console.error('   Enable Gandi Mail service in your domain settings.');
    } else if (error.response) {
      console.error('   API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
