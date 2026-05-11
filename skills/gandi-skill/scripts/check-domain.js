#!/usr/bin/env node

/**
 * Check Domain Availability
 * Single domain lookup with pricing and details
 * 
 * Usage:
 *   node check-domain.js example.com
 *   node check-domain.js example  (will add .com if no TLD)
 */

import { checkAvailability, sanitizeDomain } from './gandi-api.js';

const rawDomain = process.argv[2];

if (!rawDomain) {
  console.error('Usage: node check-domain.js <domain>');
  console.error('Example: node check-domain.js example.com');
  process.exit(1);
}

// Add .com if no TLD provided
const domainWithTld = rawDomain.includes('.') ? rawDomain : `${rawDomain}.com`;

// Sanitize domain input for security
let domainToCheck;
try {
  domainToCheck = sanitizeDomain(domainWithTld);
} catch (error) {
  console.error(`❌ Invalid domain: ${error.message}`);
  process.exit(1);
}

console.log(`🔍 Checking availability for: ${domainToCheck}\n`);

try {
  const results = await checkAvailability([domainToCheck]);
  
  if (!results || !results.products || results.products.length === 0) {
    console.log('❌ No results returned from API');
    process.exit(1);
  }
  
  const product = results.products[0];
  const currency = results.currency || 'USD';
  
  // Display results
  console.log('Domain:', product.name);
  console.log('');
  
  if (product.status === 'available') {
    console.log('✅ Status: AVAILABLE');
    
    // Show pricing
    if (product.prices && product.prices.length > 0) {
      console.log('\n💰 Pricing:');
      product.prices.forEach(price => {
        const durationUnit = price.duration_unit === 'y' ? 'year' : price.duration_unit;
        const minDuration = price.min_duration || 1;
        const maxDuration = price.max_duration;
        const durationLabel = maxDuration && maxDuration !== minDuration 
          ? `${minDuration}-${maxDuration} ${durationUnit}s`
          : `${minDuration} ${durationUnit}${minDuration > 1 ? 's' : ''}`;
        
        const priceAmount = price.price_after_taxes.toFixed(2);
        
        // Show discount if available
        if (price.discount && price.normal_price_after_taxes) {
          const normalPrice = price.normal_price_after_taxes.toFixed(2);
          console.log(`  ${durationLabel}: $${priceAmount} ${currency} (normally $${normalPrice})`);
        } else {
          console.log(`  ${durationLabel}: $${priceAmount} ${currency}`);
        }
      });
    }
    
    // Show supported features
    if (product.process) {
      console.log('\n📋 Supported Features:');
      if (Array.isArray(product.process)) {
        product.process.forEach(feature => {
          console.log(`  • ${feature}`);
        });
      } else {
        console.log(`  • ${product.process}`);
      }
    }
    
    // Show TLD info
    if (product.tld) {
      console.log('\n🌐 TLD Information:');
      console.log(`  Extension: ${product.tld}`);
    }
    
  } else if (product.status === 'unavailable') {
    console.log('❌ Status: UNAVAILABLE (already registered)');
    
  } else if (product.status === 'pending') {
    console.log('⏳ Status: PENDING (registration in progress)');
    
  } else if (product.status === 'error') {
    console.log('⚠️  Status: ERROR');
    if (product.message) {
      console.log(`   Message: ${product.message}`);
    }
    
  } else {
    console.log(`ℹ️  Status: ${product.status}`);
  }
  
  // Show additional details
  if (product.taxes_included !== undefined) {
    console.log(`\n💵 Taxes included: ${product.taxes_included ? 'Yes' : 'No'}`);
  }
  
} catch (error) {
  console.error('❌ Error checking domain:', error.message);
  if (error.response) {
    console.error('API Response:', error.response);
  }
  process.exit(1);
}
