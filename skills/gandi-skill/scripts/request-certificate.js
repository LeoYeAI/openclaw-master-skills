#!/usr/bin/env node

/**
 * Request SSL/TLS certificate via Gandi
 * 
 * ⚠️  WARNING: Gandi SSL certificates may have costs. Check pricing before requesting.
 * 
 * Usage:
 *   node request-certificate.js <domain> [options]
 * 
 * Options:
 *   --method <dns|email|http>   Validation method (default: dns)
 *   --dry-run                   Show what would be requested without requesting
 * 
 * Examples:
 *   node request-certificate.js example.com --dry-run
 *   node request-certificate.js example.com --method dns
 */

import {
  getDomain,
  requestCertificate
} from './gandi-api.js';
import readline from 'readline';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node request-certificate.js <domain> [options]');
  console.error('');
  console.error('Options:');
  console.error('  --method <dns|email|http>   Validation method (default: dns)');
  console.error('  --dry-run                   Check setup without requesting');
  console.error('');
  console.error('⚠️  WARNING: Gandi SSL certificates may have costs associated with them.');
  console.error('');
  console.error('Examples:');
  console.error('  node request-certificate.js example.com --dry-run');
  console.error('  node request-certificate.js example.com --method dns');
  console.error('');
  console.error('💡 Note: This requests certificates through Gandi\'s certificate service.');
  console.error('   For free Let\'s Encrypt certificates, consider using certbot or acme.sh');
  console.error('   directly on your web server.');
  process.exit(1);
}

const domain = args[0];
let method = 'dns';
let dryRun = false;

// Parse options
for (let i = 1; i < args.length; i++) {
  if (args[i] === '--method' && args[i + 1]) {
    method = args[i + 1].toLowerCase();
    i++;
  } else if (args[i] === '--dry-run') {
    dryRun = true;
  }
}

// Validate method
if (!['dns', 'email', 'http'].includes(method)) {
  console.error(`❌ Invalid validation method: ${method}`);
  console.error('   Valid methods: dns, email, http');
  process.exit(1);
}

// Prompt for confirmation
function confirm(message) {
  return new Promise((resolve) => {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.question(message, (answer) => {
      rl.close();
      resolve(answer.toLowerCase() === 'yes');
    });
  });
}

// Main function
async function main() {
  try {
    console.log(`🔒 SSL Certificate Request for ${domain}`);
    console.log('');
    
    // Check if domain exists
    let domainInfo;
    try {
      domainInfo = await getDomain(domain);
    } catch (err) {
      if (err.statusCode === 404) {
        console.error(`❌ Domain ${domain} not found in your account`);
        process.exit(1);
      }
      throw err;
    }
    
    console.log('📋 Domain verified in your account');
    console.log('');
    
    // Show validation method info
    console.log('🔐 Validation Method:');
    console.log('');
    
    if (method === 'dns') {
      console.log('   Method: DNS Validation (dns-01)');
      console.log('   • You will need to add TXT records to your DNS');
      console.log('   • Records will be provided after request');
      console.log('   • Validation happens automatically once records are added');
      console.log('   • Works with wildcard certificates');
    } else if (method === 'email') {
      console.log('   Method: Email Validation');
      console.log('   • Validation email sent to domain admin addresses');
      console.log('   • Valid addresses: admin@, webmaster@, postmaster@');
      console.log('   • Click link in email to validate');
      console.log('   • Does not work for wildcard certificates');
    } else if (method === 'http') {
      console.log('   Method: HTTP Validation (http-01)');
      console.log('   • File placed on your web server for validation');
      console.log('   • Must be accessible via HTTP on port 80');
      console.log('   • Does not work for wildcard certificates');
    }
    
    console.log('');
    
    // Dry run check
    if (dryRun) {
      console.log('🏁 Dry run complete. No certificate requested.');
      console.log('');
      console.log('💡 To request this certificate, run without --dry-run');
      console.log('');
      console.log('⚠️  IMPORTANT: Gandi SSL certificates may have associated costs.');
      console.log('   Check your Gandi account pricing before proceeding.');
      console.log('   https://www.gandi.net/en-US/domain/ssl');
      return;
    }
    
    // Warning and confirmation
    console.log('═'.repeat(70));
    console.log('         ⚠️  SSL CERTIFICATE REQUEST WARNING ⚠️');
    console.log('═'.repeat(70));
    console.log('');
    console.log('⚠️  IMPORTANT CONSIDERATIONS:');
    console.log('');
    console.log('1. COST:');
    console.log('   Gandi SSL certificates may have associated costs.');
    console.log('   Check pricing at: https://www.gandi.net/en-US/domain/ssl');
    console.log('');
    console.log('2. ALTERNATIVES:');
    console.log('   • Let\'s Encrypt: Free certificates (use certbot/acme.sh)');
    console.log('   • Cloudflare: Free SSL with CDN');
    console.log('   • Your hosting provider may offer free SSL');
    console.log('');
    console.log('3. VALIDATION REQUIRED:');
    console.log('   After requesting, you must complete domain validation');
    console.log(`   using ${method.toUpperCase()} method.`);
    console.log('');
    console.log('4. CERTIFICATE TYPE:');
    console.log('   This will request a certificate through Gandi\'s service.');
    console.log('   Review certificate options in your Gandi account first.');
    console.log('');
    console.log('═'.repeat(70));
    console.log('');
    
    // Require explicit confirmation
    const confirmed = await confirm('Type "yes" to proceed with certificate request: ');
    
    if (!confirmed) {
      console.log('❌ Certificate request cancelled.');
      process.exit(0);
    }
    
    console.log('');
    console.log('⏳ Requesting certificate...');
    console.log('');
    
    // Request certificate
    const result = await requestCertificate(domain, { dcv_method: method });
    
    console.log('✅ Certificate request submitted successfully!');
    console.log('');
    
    if (result.id || result.uuid) {
      console.log(`   Certificate ID: ${result.id || result.uuid}`);
    }
    
    if (result.status) {
      console.log(`   Status: ${result.status}`);
    }
    
    console.log('');
    console.log('📝 Next Steps:');
    console.log('');
    
    if (method === 'dns') {
      console.log('1. Add DNS TXT records for validation');
      console.log('   Records will be provided in the certificate details');
      console.log('2. Wait for validation (usually automated)');
      console.log('3. Certificate will be issued once validated');
    } else if (method === 'email') {
      console.log('1. Check admin email addresses for validation email');
      console.log('   (admin@, webmaster@, postmaster@)');
      console.log('2. Click validation link in email');
      console.log('3. Certificate will be issued once validated');
    } else if (method === 'http') {
      console.log('1. Place validation file on your web server');
      console.log('   File location will be provided in certificate details');
      console.log('2. Ensure file is accessible via HTTP');
      console.log('3. Certificate will be issued once validated');
    }
    
    console.log('');
    console.log('📊 To check certificate status:');
    console.log(`   node cert-details.js ${result.id || result.uuid || '<cert-id>'}`);
    console.log('');
    console.log('📋 To list all certificates:');
    console.log('   node list-certificates.js');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Possible causes:');
      console.error('  - API token lacks required scopes');
      console.error('  - SSL certificate service not available for your account');
      console.error('  - No active SSL certificate subscription');
      console.error('');
      console.error('💡 Gandi SSL certificates require a subscription or purchase.');
      console.error('   Visit: https://www.gandi.net/en-US/domain/ssl');
    } else if (error.statusCode === 402) {
      console.error('');
      console.error('Payment required. SSL certificate requests may have costs.');
      console.error('Check your Gandi account balance or SSL subscription.');
    } else if (error.statusCode === 404) {
      console.error('');
      console.error('Certificate API endpoint not found.');
      console.error('This feature may not be available for your account type.');
    } else if (error.statusCode === 422) {
      console.error('');
      console.error('Validation failed. Possible issues:');
      console.error('  - Domain configuration problems');
      console.error('  - Certificate already exists for this domain');
      console.error('  - Invalid validation method for domain type');
      if (error.response) {
        console.error('Details:', JSON.stringify(error.response, null, 2));
      }
    } else if (error.response) {
      console.error('API response:', JSON.stringify(error.response, null, 2));
    }
    
    process.exit(1);
  }
}

main();
