#!/usr/bin/env node

/**
 * Test Gandi API Authentication
 * Verifies that your Personal Access Token is configured correctly
 */

import { testAuth, readToken, readApiUrl } from './gandi-api.js';

console.log('🔑 Testing Gandi API Authentication...\n');

try {
  // Show configuration
  console.log('Configuration:');
  console.log(`  API URL: ${readApiUrl()}`);
  
  try {
    const token = readToken();
    const masked = token.substring(0, 8) + '...' + token.substring(token.length - 4);
    console.log(`  Token: ${masked}`);
  } catch (error) {
    console.log(`  Token: ❌ ${error.message}`);
    process.exit(1);
  }
  
  console.log('\n📡 Making API request...\n');
  
  const result = await testAuth();
  
  if (result.success) {
    console.log('✅ Authentication successful!\n');
    console.log('Your organizations:');
    
    if (Array.isArray(result.organizations)) {
      result.organizations.forEach((org, index) => {
        console.log(`  ${index + 1}. ${org.name || 'Unnamed'} (${org.id})`);
        if (org.type) console.log(`     Type: ${org.type}`);
      });
    } else {
      console.log('  (No organization data returned)');
    }
    
    console.log('\n🎉 You\'re ready to use the Gandi skill!');
  } else {
    console.log('❌ Authentication failed\n');
    console.log(`Error: ${result.error}`);
    
    if (result.statusCode === 401) {
      console.log('\n💡 Tips:');
      console.log('  - Check that your token is correct');
      console.log('  - Verify the token hasn\'t expired');
      console.log('  - Create a new token at: https://admin.gandi.net/organizations/account/pat');
    } else if (result.statusCode === 403) {
      console.log('\n💡 Tips:');
      console.log('  - Check that your token has the required permissions');
      console.log('  - Verify you\'re a member of the organization');
      console.log('  - Token may have expired');
    } else if (result.statusCode === 429) {
      console.log('\n💡 Rate limit exceeded. Wait 60 seconds and try again.');
    }
    
    process.exit(1);
  }
  
} catch (error) {
  console.log('❌ Error:', error.message);
  process.exit(1);
}
