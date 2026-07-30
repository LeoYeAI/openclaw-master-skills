#!/usr/bin/env node
/**
 * Universal Profile Skill for Clawdbot
 * Main entry point and CLI command handlers
 */

import {
  PERMISSIONS,
  PERMISSION_PRESETS,
  CHAINS,
  DATA_KEYS,
  ABIS,
} from './lib/constants.js';

import {
  encodePermissions,
  decodePermissions,
  combinePermissions,
  validatePermissions,
  getPreset,
  listPresets,
  formatPermissions,
  hasPermission,
} from './lib/permissions.js';

import {
  getProvider,
  generateKeyPair,
  encryptAndStoreKey,
  loadKey,
  listKeys,
  isUniversalProfile,
  getKeyManager,
  getProfileInfo,
  getControllerPermissions,
  listControllers,
  formatProfileInfo,
} from './lib/profile.js';

import {
  loadConfig,
  saveConfig,
  setConfigValue,
  getConfigValue,
  getChainConfig,
  getProfileConfig,
  saveProfileConfig,
  formatConfig,
} from './lib/config.js';

/**
 * Parse command line arguments
 * @param {string[]} args - Command line arguments
 * @returns {Object} Parsed command and options
 */
function parseArgs(args) {
  const result = {
    command: [],
    options: {},
    positional: [],
  };
  
  let i = 0;
  while (i < args.length) {
    const arg = args[i];
    
    if (arg.startsWith('--')) {
      const key = arg.slice(2);
      const nextArg = args[i + 1];
      
      if (nextArg && !nextArg.startsWith('-')) {
        result.options[key] = nextArg;
        i += 2;
      } else {
        result.options[key] = true;
        i += 1;
      }
    } else if (arg.startsWith('-')) {
      const key = arg.slice(1);
      const nextArg = args[i + 1];
      
      if (nextArg && !nextArg.startsWith('-')) {
        result.options[key] = nextArg;
        i += 2;
      } else {
        result.options[key] = true;
        i += 1;
      }
    } else {
      if (result.command.length < 2) {
        result.command.push(arg);
      } else {
        result.positional.push(arg);
      }
      i += 1;
    }
  }
  
  return result;
}

/**
 * Command handlers
 */
const commands = {
  /**
   * up key generate - Generate a new controller key
   */
  'key:generate': async (args) => {
    const { options } = args;
    
    console.log('🔐 Generating new controller key...\n');
    
    const keyPair = generateKeyPair();
    
    console.log(`✓ Address: ${keyPair.address}`);
    console.log(`✓ Public Key: ${keyPair.publicKey}`);
    
    if (options.save) {
      const password = options.password || process.env.UP_KEYSTORE_PASSWORD;
      
      if (!password) {
        console.log('\n⚠️ No password provided. Use --password <password> or set UP_KEYSTORE_PASSWORD');
        console.log('\nPrivate Key (save this securely!):');
        console.log(keyPair.privateKey);
        return;
      }
      
      await encryptAndStoreKey(keyPair.privateKey, password);
      console.log(`\n✓ Key saved to encrypted keystore`);
      console.log('\n⚠️ IMPORTANT: Remember your password! It cannot be recovered.');
    } else {
      console.log('\nPrivate Key (save this securely!):');
      console.log(keyPair.privateKey);
      console.log('\nTo save to keystore, use: up key generate --save --password <password>');
    }
    
    return keyPair;
  },
  
  /**
   * up key list - List stored keys
   */
  'key:list': async () => {
    const keys = await listKeys();
    
    if (keys.length === 0) {
      console.log('No keys stored. Generate one with: up key generate --save');
      return [];
    }
    
    console.log('Stored Keys:\n');
    for (const key of keys) {
      console.log(`  ${key.address}`);
      if (key.createdAt) {
        console.log(`    Created: ${new Date(key.createdAt).toLocaleDateString()}`);
      }
    }
    
    return keys;
  },
  
  /**
   * up status - Check configuration status
   */
  'status': async (args) => {
    const { options } = args;
    const config = await loadConfig();
    
    console.log(formatConfig(config));
    
    // Check keystore
    const keys = await listKeys();
    if (keys.length > 0) {
      console.log(`\n📋 Stored Keys: ${keys.length}`);
      for (const key of keys) {
        console.log(`   - ${key.address}`);
      }
    } else {
      console.log('\n⚠️ No keys stored. Run: up key generate --save');
    }
    
    // Check chain connectivity
    const chainName = options.chain || config.defaultChain;
    const chainConfig = await getChainConfig(chainName);
    
    if (chainConfig) {
      try {
        const provider = getProvider(chainConfig);
        const blockNumber = await provider.getBlockNumber();
        console.log(`\n✓ Connected to ${chainName} (block ${blockNumber})`);
      } catch (err) {
        console.log(`\n✗ Failed to connect to ${chainName}: ${err.message}`);
      }
    }
    
    return { config, keys };
  },
  
  /**
   * up profile info - Get profile information
   */
  'profile:info': async (args) => {
    const { positional, options } = args;
    const config = await loadConfig();
    
    // Get address from args or config
    let upAddress = positional[0];
    
    if (!upAddress) {
      const chainName = options.chain || config.defaultChain;
      const chainConfig = await getChainConfig(chainName);
      const profileConfig = await getProfileConfig(chainConfig?.chainId || chainName);
      
      if (profileConfig?.upAddress) {
        upAddress = profileConfig.upAddress;
      } else {
        console.log('Usage: up profile info <address>');
        console.log('Or configure a default profile first.');
        return null;
      }
    }
    
    const chainName = options.chain || config.defaultChain;
    const chainConfig = await getChainConfig(chainName);
    const provider = getProvider(chainConfig);
    
    // Check if valid UP
    const isUP = await isUniversalProfile(upAddress, provider);
    if (!isUP) {
      console.log(`⚠️ ${upAddress} does not appear to be a Universal Profile`);
      return null;
    }
    
    const info = await getProfileInfo(upAddress, provider);
    console.log(formatProfileInfo(info));
    
    // List controllers if any
    if (info.keyManager && info.controllersCount > 0) {
      console.log('\nControllers:');
      const controllers = await listControllers(upAddress, provider);
      for (const ctrl of controllers) {
        const permsShort = ctrl.permissionNames.slice(0, 3).join(', ');
        const more = ctrl.permissionNames.length > 3 ? ` +${ctrl.permissionNames.length - 3} more` : '';
        console.log(`  ${ctrl.address.slice(0, 10)}...${ctrl.address.slice(-4)}: ${permsShort}${more}`);
      }
    }
    
    return info;
  },
  
  /**
   * up profile configure - Configure a profile for use
   */
  'profile:configure': async (args) => {
    const { positional, options } = args;
    
    if (positional.length === 0) {
      console.log('Usage: up profile configure <up-address> [--key-manager <km-address>] [--chain <chain>]');
      return null;
    }
    
    const upAddress = positional[0];
    const config = await loadConfig();
    const chainName = options.chain || config.defaultChain;
    const chainConfig = await getChainConfig(chainName);
    
    const provider = getProvider(chainConfig);
    
    // Verify it's a UP
    const isUP = await isUniversalProfile(upAddress, provider);
    if (!isUP) {
      console.log(`⚠️ ${upAddress} does not appear to be a Universal Profile`);
      return null;
    }
    
    // Get Key Manager
    let kmAddress = options['key-manager'];
    if (!kmAddress) {
      kmAddress = await getKeyManager(upAddress, provider);
    }
    
    if (!kmAddress) {
      console.log(`⚠️ Could not find Key Manager for ${upAddress}`);
      console.log('Specify manually with --key-manager <address>');
      return null;
    }
    
    // Save profile config
    const profileConfig = {
      upAddress,
      keyManagerAddress: kmAddress,
    };
    
    await saveProfileConfig(chainConfig.chainId, profileConfig);
    
    console.log(`✓ Profile configured for ${chainName}`);
    console.log(`  UP: ${upAddress}`);
    console.log(`  Key Manager: ${kmAddress}`);
    
    return profileConfig;
  },
  
  /**
   * up permissions encode - Encode permissions
   */
  'permissions:encode': async (args) => {
    const { positional } = args;
    
    if (positional.length === 0) {
      console.log('Usage: up permissions encode <permission1> [<permission2> ...]');
      console.log('\nAvailable permissions:');
      Object.keys(PERMISSIONS).forEach(p => console.log(`  - ${p}`));
      return null;
    }
    
    try {
      const encoded = encodePermissions(positional);
      console.log(encoded);
      return encoded;
    } catch (err) {
      console.log(`Error: ${err.message}`);
      return null;
    }
  },
  
  /**
   * up permissions decode - Decode permissions
   */
  'permissions:decode': async (args) => {
    const { positional } = args;
    
    if (positional.length === 0) {
      console.log('Usage: up permissions decode <permissions-hex>');
      return null;
    }
    
    const permHex = positional[0];
    console.log(formatPermissions(permHex));
    
    return decodePermissions(permHex);
  },
  
  /**
   * up permissions presets - List permission presets
   */
  'permissions:presets': async () => {
    const presets = listPresets();
    
    console.log('Permission Presets:\n');
    
    for (const preset of presets) {
      const riskIcon = {
        LOW: '🟢',
        MEDIUM: '🟡',
        HIGH: '🟠',
        CRITICAL: '🔴',
      }[preset.riskLevel];
      
      console.log(`${riskIcon} ${preset.key}`);
      console.log(`   ${preset.description}`);
      console.log(`   Permissions: ${preset.permissions.join(', ')}`);
      console.log(`   Hex: ${preset.permissionsHex.slice(0, 18)}...`);
      if (preset.warning) {
        console.log(`   ⚠️ ${preset.warning}`);
      }
      console.log('');
    }
    
    return presets;
  },
  
  /**
   * up permissions validate - Validate permissions for security
   */
  'permissions:validate': async (args) => {
    const { positional } = args;
    
    if (positional.length === 0) {
      console.log('Usage: up permissions validate <permissions-hex>');
      return null;
    }
    
    const permHex = positional[0];
    const result = validatePermissions(permHex);
    
    const levelIcon = {
      LOW: '🟢',
      MEDIUM: '🟡',
      HIGH: '🟠',
      CRITICAL: '🔴',
    }[result.riskLevel];
    
    console.log(`${levelIcon} Risk Level: ${result.riskLevel}\n`);
    
    console.log('Active Permissions:');
    result.permissions.forEach(p => console.log(`  - ${p}`));
    
    if (result.risks.length > 0) {
      console.log('\n⚠️ SECURITY RISKS:');
      result.risks.forEach(r => console.log(`  🔴 ${r}`));
    }
    
    if (result.warnings.length > 0) {
      console.log('\n⚡ Warnings:');
      result.warnings.forEach(w => console.log(`  🟡 ${w}`));
    }
    
    if (result.valid) {
      console.log('\n✓ No critical security risks detected');
    } else {
      console.log('\n✗ Critical security risks detected - review carefully!');
    }
    
    return result;
  },
  
  /**
   * up authorize url - Generate authorization URL
   */
  'authorize:url': async (args) => {
    const { options } = args;
    const config = await loadConfig();
    
    // Get or generate controller key
    const keys = await listKeys();
    let controllerAddress;
    
    if (keys.length > 0) {
      controllerAddress = keys[0].address;
    } else {
      console.log('No keys found. Generate one first:');
      console.log('  up key generate --save --password <password>\n');
      return null;
    }
    
    // Get permissions
    let permissions;
    const presetName = options.permissions || 'token-operator';
    
    if (presetName.startsWith('0x')) {
      permissions = presetName;
    } else {
      try {
        const preset = getPreset(presetName);
        permissions = preset.permissions;
        console.log(`Using preset: ${preset.name}`);
        console.log(`Description: ${preset.description}\n`);
      } catch (err) {
        console.log(`Unknown preset: ${presetName}`);
        console.log('Available presets: read-only, token-operator, nft-trader, defi-trader, profile-manager, full-access');
        return null;
      }
    }
    
    const chainName = options.chain || config.defaultChain;
    const chainConfig = await getChainConfig(chainName);
    
    // Generate URL (placeholder - actual UI would be hosted)
    const authUrl = `https://up-auth.example.com/?controller=${controllerAddress}&permissions=${permissions}&chain=${chainConfig.chainId}`;
    
    console.log(`✓ Controller Address: ${controllerAddress}`);
    console.log(`✓ Permissions: ${permissions.slice(0, 18)}...`);
    console.log(`✓ Chain: ${chainName} (${chainConfig.chainId})`);
    console.log(`\nAuthorization URL:`);
    console.log(authUrl);
    console.log(`\nInstructions:`);
    console.log('1. Open the URL in a browser with UP extension');
    console.log('2. Connect your Universal Profile');
    console.log('3. Review and approve the permissions');
    console.log('4. Clawdbot will be added as a controller');
    
    return { controllerAddress, permissions, url: authUrl };
  },
  
  /**
   * up config show - Show current configuration
   */
  'config:show': async () => {
    const config = await loadConfig();
    console.log(JSON.stringify(config, null, 2));
    return config;
  },
  
  /**
   * up config set - Set a configuration value
   */
  'config:set': async (args) => {
    const { positional } = args;
    
    if (positional.length < 2) {
      console.log('Usage: up config set <key> <value>');
      console.log('\nAllowed keys:');
      console.log('  defaultChain - Default chain (lukso, lukso-testnet)');
      console.log('\nNote: keystorePath and profiles cannot be changed at runtime for security.');
      return null;
    }
    
    const [key, value] = positional;
    await setConfigValue(key, value);
    console.log(`✓ Set ${key} = ${value}`);
    
    return { key, value };
  },
  
  /**
   * up quota - Check relay quota
   */
  'quota': async (args) => {
    const { options } = args;
    const network = options.chain === 'lukso-testnet' ? 'testnet' : 'mainnet';
    
    console.log('🔍 Checking relay quota...\n');
    
    const { getRelayQuota } = await import('./lib/execute/relay.js');
    const data = await getRelayQuota({ network });
    
    const used = data.totalQuota - data.quota;
    const pct = ((data.quota / data.totalQuota) * 100).toFixed(1);
    const resetDate = new Date(data.resetDate * 1000);
    
    console.log(`⛽ Relay Quota`);
    console.log(`  Remaining: ${data.quota.toLocaleString()} ${data.unit} (${pct}%)`);
    console.log(`  Used:      ${used.toLocaleString()} ${data.unit}`);
    console.log(`  Total:     ${data.totalQuota.toLocaleString()} ${data.unit}`);
    console.log(`  Resets:    ${resetDate.toLocaleDateString()} ${resetDate.toLocaleTimeString()}`);
    
    return data;
  },

  /**
   * up help - Show help
   */
  'help': async () => {
    console.log(`
Universal Profile Skill for Clawdbot

Usage: up <command> [subcommand] [options]

Commands:
  key generate [--save] [--password <pw>]  Generate a new controller key
  key list                                 List stored keys
  
  status [--chain <chain>]                 Check configuration status
  
  profile info [<address>] [--chain]       Get profile information
  profile configure <address> [--chain]    Configure a profile for use
  
  permissions encode <perm1> [perm2...]    Encode permissions to hex
  permissions decode <hex>                 Decode permissions from hex
  permissions presets                      List permission presets
  permissions validate <hex>               Validate permissions for security
  
  authorize url [--permissions <preset>]   Generate authorization URL
  
  quota [--chain <chain>]                  Check relay gas quota
  
  config show                              Show current configuration
  config set <key> <value>                 Set configuration value
  
  help                                     Show this help

Options:
  --chain <name>       Chain to use (lukso, lukso-testnet)
  --password <pw>      Password for keystore operations
  --permissions <p>    Permission preset or hex value

Examples:
  up key generate --save --password mysecret
  up profile info 0x1234...
  up permissions encode CALL TRANSFERVALUE
  up permissions validate 0x0000...0801
  up authorize url --permissions token-operator
`);
  },
};

/**
 * Main entry point
 */
export async function main(args) {
  const parsed = parseArgs(args);
  
  // Build command key
  const cmdParts = parsed.command;
  let handler;
  
  if (cmdParts.length === 0 || cmdParts[0] === 'help') {
    handler = commands['help'];
  } else if (cmdParts.length === 1) {
    // Single word command like "status"
    handler = commands[cmdParts[0]];
  } else {
    // Two word command like "key generate"
    const cmdKey = `${cmdParts[0]}:${cmdParts[1]}`;
    handler = commands[cmdKey];
    
    // Adjust positional args
    if (parsed.command.length > 2) {
      parsed.positional = [...parsed.command.slice(2), ...parsed.positional];
    }
  }
  
  if (!handler) {
    console.log(`Unknown command: ${cmdParts.join(' ')}`);
    console.log('Run "up help" for usage information.');
    return null;
  }
  
  try {
    return await handler(parsed);
  } catch (err) {
    console.error(`Error: ${err.message}`);
    if (process.env.DEBUG) {
      console.error(err.stack);
    }
    return null;
  }
}

// CLI entry point
if (process.argv[1] === new URL(import.meta.url).pathname || 
    process.argv[1]?.endsWith('/index.js')) {
  main(process.argv.slice(2)).catch(console.error);
}

// Export everything for programmatic use
export {
  // Constants
  PERMISSIONS,
  PERMISSION_PRESETS,
  CHAINS,
  DATA_KEYS,
  ABIS,
  
  // Permissions
  encodePermissions,
  decodePermissions,
  combinePermissions,
  validatePermissions,
  getPreset,
  listPresets,
  formatPermissions,
  hasPermission,
  
  // Profile
  getProvider,
  generateKeyPair,
  encryptAndStoreKey,
  loadKey,
  listKeys,
  isUniversalProfile,
  getKeyManager,
  getProfileInfo,
  getControllerPermissions,
  listControllers,
  formatProfileInfo,
  
  // Config
  loadConfig,
  saveConfig,
  setConfigValue,
  getConfigValue,
  getChainConfig,
  getProfileConfig,
  saveProfileConfig,
  formatConfig,
};

export default {
  main,
  commands,
};
