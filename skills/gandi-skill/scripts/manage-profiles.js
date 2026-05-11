#!/usr/bin/env node

/**
 * Manage Gandi organization profiles
 * 
 * Usage:
 *   node manage-profiles.js <action> [options]
 * 
 * Actions:
 *   list                          - List all profiles
 *   add <name> <token>            - Add a new profile
 *   remove <name>                 - Remove a profile
 *   default <name>                - Set default profile
 *   show <name>                   - Show profile details
 *   migrate                       - Migrate legacy token to profile
 * 
 * Examples:
 *   node manage-profiles.js list
 *   node manage-profiles.js add personal YOUR_TOKEN
 *   node manage-profiles.js add work YOUR_TOKEN --set-default
 *   node manage-profiles.js default personal
 *   node manage-profiles.js remove old-profile
 */

import {
  listProfiles,
  addProfile,
  removeProfile,
  setDefaultProfile,
  getProfile,
  migrateLegacyToken
} from './profile-manager.js';

// Parse command line arguments
const args = process.argv.slice(2);

if (args.length < 1) {
  console.error('Usage: node manage-profiles.js <action> [options]');
  console.error('');
  console.error('Actions:');
  console.error('  list                          - List all profiles');
  console.error('  add <name> <token>            - Add a new profile');
  console.error('  remove <name>                 - Remove a profile');
  console.error('  default <name>                - Set default profile');
  console.error('  show <name>                   - Show profile details');
  console.error('  migrate                       - Migrate legacy token');
  console.error('');
  console.error('Examples:');
  console.error('  node manage-profiles.js list');
  console.error('  node manage-profiles.js add personal YOUR_TOKEN');
  console.error('  node manage-profiles.js add work YOUR_TOKEN --set-default');
  console.error('  node manage-profiles.js default personal');
  console.error('  node manage-profiles.js show personal');
  process.exit(1);
}

const action = args[0];

// List profiles
async function listAction() {
  console.log('📋 Gandi Organization Profiles');
  console.log('');
  
  const { profiles, default: defaultProfile } = listProfiles();
  
  if (Object.keys(profiles).length === 0) {
    console.log('No profiles configured.');
    console.log('');
    console.log('💡 To add a profile:');
    console.log('   node manage-profiles.js add <name> <token>');
    console.log('');
    console.log('📝 Get your Personal Access Token at:');
    console.log('   https://admin.gandi.net/organizations/account/pat');
    return;
  }
  
  Object.entries(profiles).forEach(([name, profile]) => {
    const isDefault = name === defaultProfile;
    console.log(`${isDefault ? '✅' : '  '} ${name}`);
    console.log(`   Organization: ${profile.org_name} (${profile.org_type})`);
    console.log(`   ID: ${profile.org_id}`);
    console.log(`   Token: ${profile.token_file}`);
    console.log('');
  });
  
  if (defaultProfile) {
    console.log(`Default profile: ${defaultProfile} ✅`);
  } else {
    console.log('⚠️  No default profile set');
  }
  
  console.log('');
  console.log('💡 To use a specific profile:');
  console.log('   Use --profile <name> flag with any command');
  console.log('   Example: node list-domains.js --profile work');
}

// Add profile
async function addAction(name, token, setDefault = false) {
  if (!name || !token) {
    console.error('❌ Usage: node manage-profiles.js add <name> <token>');
    process.exit(1);
  }
  
  console.log(`📝 Adding profile "${name}"...`);
  console.log('');
  
  try {
    const profile = await addProfile(name, token, { setDefault });
    
    console.log('✅ Profile added successfully!');
    console.log('');
    console.log(`   Name: ${name}`);
    console.log(`   Organization: ${profile.org_name}`);
    console.log(`   Type: ${profile.org_type}`);
    console.log(`   ID: ${profile.org_id}`);
    
    if (setDefault) {
      console.log('   ✅ Set as default profile');
    }
    
    console.log('');
    console.log('💡 To use this profile:');
    console.log(`   node list-domains.js --profile ${name}`);
    console.log('');
    console.log('💡 To set as default:');
    console.log(`   node manage-profiles.js default ${name}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Remove profile
async function removeAction(name) {
  if (!name) {
    console.error('❌ Usage: node manage-profiles.js remove <name>');
    process.exit(1);
  }
  
  console.log(`🗑️  Removing profile "${name}"...`);
  console.log('');
  
  try {
    removeProfile(name);
    
    console.log('✅ Profile removed successfully!');
    console.log('');
    console.log('📋 To see remaining profiles:');
    console.log('   node manage-profiles.js list');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Set default profile
async function defaultAction(name) {
  if (!name) {
    console.error('❌ Usage: node manage-profiles.js default <name>');
    process.exit(1);
  }
  
  console.log(`⚙️  Setting default profile to "${name}"...`);
  console.log('');
  
  try {
    setDefaultProfile(name);
    
    console.log('✅ Default profile updated!');
    console.log('');
    console.log(`   All commands will now use the "${name}" profile by default`);
    console.log('   unless you specify --profile <other-name>');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Show profile details
async function showAction(name) {
  if (!name) {
    console.error('❌ Usage: node manage-profiles.js show <name>');
    process.exit(1);
  }
  
  try {
    const profile = getProfile(name);
    const { default: defaultProfile } = listProfiles();
    
    console.log(`📋 Profile: ${name}`);
    console.log('');
    console.log(`   Organization: ${profile.org_name}`);
    console.log(`   Type: ${profile.org_type}`);
    console.log(`   ID: ${profile.org_id}`);
    console.log(`   Token File: ${profile.token_file}`);
    
    if (name === defaultProfile) {
      console.log(`   Status: ✅ Default profile`);
    }
    
    console.log('');
    console.log('💡 To use this profile:');
    console.log(`   node list-domains.js --profile ${name}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Migrate legacy token
async function migrateAction() {
  console.log('📦 Checking for legacy token...');
  console.log('');
  
  try {
    const result = await migrateLegacyToken();
    
    if (!result) {
      console.log('ℹ️  No legacy token found or profiles already exist.');
      console.log('');
      console.log('💡 To add a profile manually:');
      console.log('   node manage-profiles.js add <name> <token>');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Main function
async function main() {
  try {
    switch (action.toLowerCase()) {
      case 'list':
        await listAction();
        break;
        
      case 'add':
        const name = args[1];
        const token = args[2];
        const setDefault = args.includes('--set-default');
        await addAction(name, token, setDefault);
        break;
        
      case 'remove':
      case 'delete':
        await removeAction(args[1]);
        break;
        
      case 'default':
      case 'set-default':
        await defaultAction(args[1]);
        break;
        
      case 'show':
      case 'info':
        await showAction(args[1]);
        break;
        
      case 'migrate':
        await migrateAction();
        break;
        
      default:
        console.error(`❌ Unknown action: ${action}`);
        console.error('Valid actions: list, add, remove, default, show, migrate');
        process.exit(1);
    }
    
  } catch (error) {
    console.error('❌ Unexpected error:', error.message);
    process.exit(1);
  }
}

main();
