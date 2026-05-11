#!/usr/bin/env node

/**
 * Show Gandi skill configuration status
 * Displays configuration from all sources (Gateway, profiles, legacy files)
 */

import {
  getApiToken,
  getApiUrl,
  getDomainCheckerConfig,
  listOrganizations,
  getConfigSummary
} from './config-helper.js';

console.log('🔍 Gandi Skill Configuration Status');
console.log('');
console.log('═'.repeat(70));
console.log('');

// Overall summary
const summary = getConfigSummary();

console.log('📋 Configuration Sources:');
console.log('');

// Gateway Config
if (summary.gatewayConfig) {
  if (summary.gatewayConfig.error) {
    console.log('❌ Gateway Config: Error - ' + summary.gatewayConfig.error);
  } else {
    console.log('✅ Gateway Config: Available');
    console.log(`   Single Token: ${summary.gatewayConfig.hasApiToken ? 'Yes' : 'No'}`);
    console.log(`   Organizations: ${summary.gatewayConfig.organizationCount}`);
    console.log(`   Domain Checker: ${summary.gatewayConfig.hasDomainChecker ? 'Configured' : 'Using defaults'}`);
  }
} else {
  console.log('ℹ️  Gateway Config: Not found');
}
console.log('');

// Profile Config
if (summary.profileConfig) {
  if (summary.profileConfig.error) {
    console.log('❌ Profile Config: Error - ' + summary.profileConfig.error);
  } else if (summary.profileConfig.profileCount > 0) {
    console.log('✅ Profile Config: Available');
    console.log(`   Profiles: ${summary.profileConfig.profileCount} (${summary.profileConfig.profiles.join(', ')})`);
    console.log(`   Default: ${summary.profileConfig.defaultProfile || 'None'}`);
  } else {
    console.log('ℹ️  Profile Config: No profiles configured');
  }
} else {
  console.log('ℹ️  Profile Config: Not available');
}
console.log('');

// Legacy Files
if (summary.legacyFiles.token || summary.legacyFiles.url) {
  console.log('📄 Legacy Files:');
  console.log(`   Token: ${summary.legacyFiles.token ? '~/.config/gandi/api_token' : 'Not found'}`);
  console.log(`   URL: ${summary.legacyFiles.url ? '~/.config/gandi/api_url' : 'Not found'}`);
} else {
  console.log('ℹ️  Legacy Files: Not found');
}
console.log('');

// Environment Variables
if (summary.envVars.GANDI_API_TOKEN) {
  console.log('🌍 Environment Variables:');
  console.log('   GANDI_API_TOKEN: Set');
} else {
  console.log('ℹ️  Environment Variables: GANDI_API_TOKEN not set');
}
console.log('');

console.log('═'.repeat(70));
console.log('');

// Active configuration
console.log('⚙️  Active Configuration:');
console.log('');

try {
  const tokenInfo = getApiToken();
  console.log(`✅ API Token: Found (source: ${tokenInfo.source})`);
  if (tokenInfo.orgName) {
    console.log(`   Organization: ${tokenInfo.orgName}`);
  }
  if (tokenInfo.sharingId) {
    console.log(`   Sharing ID: ${tokenInfo.sharingId}`);
  }
} catch (error) {
  console.log(`❌ API Token: ${error.message}`);
}
console.log('');

const apiUrl = getApiUrl();
console.log(`📡 API URL: ${apiUrl}`);
console.log('');

// Organizations
const orgs = listOrganizations();
if (orgs.length > 0) {
  console.log(`🏢 Organizations (${orgs.length}):`);
  orgs.forEach(org => {
    const defaultMarker = org.default ? ' ✅ DEFAULT' : '';
    console.log(`   • ${org.label || org.name}${defaultMarker}`);
    console.log(`     Name: ${org.name}`);
    console.log(`     ID: ${org.sharingId}`);
  });
  console.log('');
}

// Domain Checker Config
const checkerConfig = getDomainCheckerConfig();
console.log('🔍 Domain Checker Configuration:');
console.log(`   TLD Mode: ${checkerConfig.tlds.mode}`);
console.log(`   Default TLDs: ${checkerConfig.tlds.defaults.length}`);
console.log(`   Custom TLDs: ${checkerConfig.tlds.custom.length}`);
console.log(`   Max TLDs to Check: ${checkerConfig.limits.maxTlds}`);
console.log(`   Max Variations: ${checkerConfig.limits.maxVariations}`);
console.log(`   Rate Limit: ${checkerConfig.rateLimit.maxRequestsPerMinute} req/min`);
console.log('');

console.log('═'.repeat(70));
console.log('');

// Recommendations
console.log('💡 Configuration Recommendations:');
console.log('');

if (!summary.gatewayConfig) {
  console.log('📝 For centralized management, configure via Gateway Console:');
  console.log('   1. Open Gateway Console UI');
  console.log('   2. Navigate to Skills → gandi → Config');
  console.log('   3. Add your API token and preferences');
  console.log('');
}

if (summary.profileConfig && summary.profileConfig.profileCount > 0 && summary.gatewayConfig) {
  console.log('ℹ️  You have both Gateway config and profile config.');
  console.log('   Gateway config takes precedence.');
  console.log('   Consider migrating profiles to Gateway config for consistency.');
  console.log('');
}

if (summary.legacyFiles.token && (summary.gatewayConfig || summary.profileConfig?.profileCount > 0)) {
  console.log('📦 Legacy token file detected alongside newer config.');
  console.log('   Consider removing ~/.config/gandi/api_token after migration.');
  console.log('   Run: node manage-profiles.js migrate');
  console.log('');
}

if (!summary.gatewayConfig && !summary.profileConfig?.profileCount && !summary.legacyFiles.token && !summary.envVars.GANDI_API_TOKEN) {
  console.log('❌ No configuration found!');
  console.log('');
  console.log('To get started:');
  console.log('');
  console.log('Option 1 - Gateway Console (Recommended):');
  console.log('   Configure via Gateway Console UI');
  console.log('');
  console.log('Option 2 - Profile-based:');
  console.log('   node manage-profiles.js add primary YOUR_TOKEN');
  console.log('');
  console.log('Option 3 - Legacy file:');
  console.log('   mkdir -p ~/.config/gandi');
  console.log('   echo "YOUR_TOKEN" > ~/.config/gandi/api_token');
  console.log('   chmod 600 ~/.config/gandi/api_token');
  console.log('');
  console.log('Get your token at: https://admin.gandi.net/organizations/account/pat');
}

console.log('✅ Configuration check complete!');
