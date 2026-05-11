#!/usr/bin/env node

/**
 * Renew an existing domain via Gandi Domain API
 * 
 * ⚠️  WARNING: Domain renewal costs real money and is NON-REFUNDABLE!
 * 
 * Usage:
 *   node renew-domain.js <domain> [options]
 * 
 * Options:
 *   --years <n>      Renewal duration (1-10 years, default: 1)
 *   --dry-run        Check pricing without renewing
 * 
 * Examples:
 *   node renew-domain.js example.com --dry-run
 *   node renew-domain.js example.com --years 2
 */

import {
  getDomain,
  checkAvailability,
  renewDomain
} from './gandi-api.js';
import readline from 'readline';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node renew-domain.js <domain> [options]');
  console.error('');
  console.error('Options:');
  console.error('  --years <n>      Renewal duration (1-10 years, default: 1)');
  console.error('  --dry-run        Check pricing without renewing');
  console.error('');
  console.error('⚠️  WARNING: Domain renewal costs real money and is NON-REFUNDABLE!');
  console.error('');
  console.error('Examples:');
  console.error('  node renew-domain.js example.com --dry-run');
  console.error('  node renew-domain.js example.com --years 2');
  process.exit(1);
}

const domain = args[0];
let years = 1;
let dryRun = false;

// Parse options
for (let i = 1; i < args.length; i++) {
  if (args[i] === '--years' && args[i + 1]) {
    years = parseInt(args[i + 1], 10);
    i++;
  } else if (args[i] === '--dry-run') {
    dryRun = true;
  }
}

// Validate years
if (isNaN(years) || years < 1 || years > 10) {
  console.error('❌ Error: Years must be between 1 and 10');
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

// Format date nicely
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  });
}

// Main function
async function main() {
  try {
    console.log('🔍 Checking domain information...');
    console.log('');
    
    // Get current domain info
    let domainInfo;
    try {
      domainInfo = await getDomain(domain);
    } catch (err) {
      if (err.statusCode === 404) {
        console.error(`❌ Domain ${domain} not found in your account`);
        console.error('   Make sure you own this domain and it\'s registered with Gandi.');
      } else {
        throw err;
      }
      process.exit(1);
    }
    
    // Show current domain status
    console.log(`📋 Domain: ${domain}`);
    console.log(`   Current expiration: ${formatDate(domainInfo.dates.registry_ends_at)}`);
    
    const daysUntilExpiry = Math.ceil((new Date(domainInfo.dates.registry_ends_at) - new Date()) / (1000 * 60 * 60 * 24));
    console.log(`   Days until expiry: ${daysUntilExpiry}`);
    
    if (domainInfo.autorenew) {
      console.log(`   Auto-renewal: ✅ ENABLED (${domainInfo.autorenew.duration} year(s))`);
    } else {
      console.log('   Auto-renewal: ❌ DISABLED');
    }
    
    console.log('');
    
    // Check if domain is renewable
    if (daysUntilExpiry > 365) {
      console.log('⚠️  Note: Domain expires in more than 1 year.');
      console.log('   Renewal will extend the expiration date from the current expiry,');
      console.log('   not from today\'s date.');
      console.log('');
    }
    
    // Get renewal pricing
    console.log('💰 Checking renewal pricing...');
    const availability = await checkAvailability([domain]);
    const pricingInfo = availability.products?.[0];
    
    if (!pricingInfo || !pricingInfo.prices) {
      console.error('❌ Error: Could not retrieve pricing information');
      process.exit(1);
    }
    
    const prices = pricingInfo.prices;
    const yearPrice = prices.find(p => p.duration_unit === 'y' && p.min_duration === years);
    const price1Year = prices.find(p => p.duration_unit === 'y' && p.min_duration === 1);
    
    if (!yearPrice && !price1Year) {
      console.error('❌ Error: Pricing information not available');
      process.exit(1);
    }
    
    const renewalPrice = yearPrice || price1Year;
    const pricePerYear = renewalPrice.price_after_taxes;
    const currency = renewalPrice.currency;
    const totalCost = years * pricePerYear;
    
    console.log('');
    console.log('💰 Renewal Pricing:');
    console.log(`   ${years} year(s): ${totalCost.toFixed(2)} ${currency}`);
    if (years > 1) {
      console.log(`   (${pricePerYear.toFixed(2)} ${currency} per year)`);
    }
    console.log('');
    
    // Calculate new expiration date
    const currentExpiry = new Date(domainInfo.dates.registry_ends_at);
    const newExpiry = new Date(currentExpiry);
    newExpiry.setFullYear(newExpiry.getFullYear() + years);
    
    console.log('📅 After renewal:');
    console.log(`   New expiration: ${formatDate(newExpiry)}`);
    console.log('');
    
    // If dry-run, stop here
    if (dryRun) {
      console.log('🏁 Dry run complete. No renewal performed.');
      console.log('');
      console.log('💡 To renew this domain, run without --dry-run:');
      console.log(`   node renew-domain.js ${domain} --years ${years}`);
      return;
    }
    
    // Show renewal summary
    console.log('═══════════════════════════════════════════════════════');
    console.log('                   RENEWAL SUMMARY');
    console.log('═══════════════════════════════════════════════════════');
    console.log(`   Domain: ${domain}`);
    console.log(`   Current expiry: ${formatDate(currentExpiry)}`);
    console.log(`   Renewal duration: ${years} year(s)`);
    console.log(`   New expiry: ${formatDate(newExpiry)}`);
    console.log(`   TOTAL COST: ${totalCost.toFixed(2)} ${currency}`);
    console.log('═══════════════════════════════════════════════════════');
    console.log('');
    console.log('⚠️  WARNING: DOMAIN RENEWAL IS NON-REFUNDABLE!');
    console.log('⚠️  You will be charged immediately.');
    console.log('⚠️  This action cannot be undone.');
    console.log('');
    
    // Require explicit "yes" confirmation
    const confirmed = await confirm('Type "yes" to confirm renewal: ');
    
    if (!confirmed) {
      console.log('❌ Renewal cancelled.');
      process.exit(0);
    }
    
    console.log('');
    console.log('⏳ Renewing domain...');
    console.log('');
    
    // Renew the domain
    const result = await renewDomain(domain, years);
    
    console.log('✅ Domain renewal successful!');
    console.log('');
    
    if (result.id) {
      console.log(`   Operation ID: ${result.id}`);
    }
    
    if (result.message) {
      console.log(`   Message: ${result.message}`);
    }
    
    console.log('');
    console.log('📧 You should receive a confirmation email shortly.');
    console.log('');
    console.log('🎉 Renewal complete!');
    console.log('');
    console.log(`   ${domain} is now renewed until ${formatDate(newExpiry)}`);
    console.log('');
    console.log('💡 Consider enabling auto-renewal to prevent accidental expiration:');
    console.log(`   node configure-autorenew.js ${domain} --enable`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    
    if (error.statusCode === 401) {
      console.error('');
      console.error('Authentication failed. Check your API token.');
    } else if (error.statusCode === 403) {
      console.error('');
      console.error('Permission denied. Ensure your API token has Domain: write scope.');
      console.error('Create a new token at: https://admin.gandi.net/organizations/account/pat');
    } else if (error.statusCode === 402) {
      console.error('');
      console.error('Payment failed. Check your Gandi account balance or payment method.');
    } else if (error.statusCode === 404) {
      console.error('');
      console.error('Domain not found or not accessible.');
    } else if (error.statusCode === 422) {
      console.error('');
      console.error('Renewal not allowed at this time. Domain may be:');
      console.error('  - Already renewed to maximum duration');
      console.error('  - In grace or redemption period');
      console.error('  - Locked or suspended');
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
