/**
 * LSP6 Permission Encoding/Decoding
 * Utilities for working with Universal Profile permissions
 */

import {
  PERMISSIONS,
  PERMISSION_NAMES,
  PERMISSION_PRESETS,
  PERMISSION_RISKS,
  DATA_KEYS,
} from './constants.js';

/**
 * Encode permission names into bytes32 format
 * @param {string[]} permissionNames - Array of permission names
 * @returns {string} Encoded permissions as hex string
 */
export function encodePermissions(permissionNames) {
  if (!Array.isArray(permissionNames)) {
    permissionNames = [permissionNames];
  }
  
  let combined = 0n;
  
  for (const name of permissionNames) {
    const upperName = name.toUpperCase();
    
    // Handle ALL_PERMISSIONS specially
    if (upperName === 'ALL_PERMISSIONS') {
      return PERMISSIONS.ALL_PERMISSIONS;
    }
    
    const permValue = PERMISSIONS[upperName];
    if (!permValue) {
      throw new Error(`Unknown permission: ${name}`);
    }
    
    combined |= BigInt(permValue);
  }
  
  // Pad to 32 bytes (64 hex chars + 0x prefix)
  return '0x' + combined.toString(16).padStart(64, '0');
}

/**
 * Combine multiple permission values
 * @param {string[]} permissions - Array of permission hex values or names
 * @returns {string} Combined permissions as hex string
 */
export function combinePermissions(permissions) {
  let combined = 0n;
  
  for (const perm of permissions) {
    if (typeof perm === 'string') {
      if (perm.startsWith('0x')) {
        combined |= BigInt(perm);
      } else {
        const permValue = PERMISSIONS[perm.toUpperCase()];
        if (permValue) {
          combined |= BigInt(permValue);
        }
      }
    } else if (typeof perm === 'bigint') {
      combined |= perm;
    }
  }
  
  return '0x' + combined.toString(16).padStart(64, '0');
}

/**
 * Decode permissions from bytes32 format
 * @param {string} permissionHex - Permissions as hex string
 * @returns {string[]} Array of permission names
 */
export function decodePermissions(permissionHex) {
  const permissions = [];
  const value = BigInt(permissionHex);
  
  // Check ALL_PERMISSIONS first
  if (value === BigInt(PERMISSIONS.ALL_PERMISSIONS)) {
    return ['ALL_PERMISSIONS'];
  }
  
  // Check each bit position
  for (let i = 0; i < 32; i++) {
    const bit = 1n << BigInt(i);
    if ((value & bit) !== 0n) {
      const name = PERMISSION_NAMES[i];
      if (name) {
        permissions.push(name);
      } else {
        permissions.push(`UNKNOWN_BIT_${i}`);
      }
    }
  }
  
  return permissions;
}

/**
 * Check if a permission set includes a specific permission
 * @param {string} permissionHex - Permissions as hex string
 * @param {string} permissionName - Permission name to check
 * @returns {boolean}
 */
export function hasPermission(permissionHex, permissionName) {
  const value = BigInt(permissionHex);
  const permValue = PERMISSIONS[permissionName.toUpperCase()];
  
  if (!permValue) {
    throw new Error(`Unknown permission: ${permissionName}`);
  }
  
  return (value & BigInt(permValue)) !== 0n;
}

/**
 * Add a permission to an existing permission set
 * @param {string} existingPermissions - Current permissions hex
 * @param {string} permissionToAdd - Permission name or hex to add
 * @returns {string} Updated permissions hex
 */
export function addPermission(existingPermissions, permissionToAdd) {
  const existing = BigInt(existingPermissions || '0x0');
  const toAdd = typeof permissionToAdd === 'string' && !permissionToAdd.startsWith('0x')
    ? BigInt(PERMISSIONS[permissionToAdd.toUpperCase()] || '0x0')
    : BigInt(permissionToAdd);
  
  return '0x' + (existing | toAdd).toString(16).padStart(64, '0');
}

/**
 * Remove a permission from an existing permission set
 * @param {string} existingPermissions - Current permissions hex
 * @param {string} permissionToRemove - Permission name or hex to remove
 * @returns {string} Updated permissions hex
 */
export function removePermission(existingPermissions, permissionToRemove) {
  const existing = BigInt(existingPermissions || '0x0');
  const toRemove = typeof permissionToRemove === 'string' && !permissionToRemove.startsWith('0x')
    ? BigInt(PERMISSIONS[permissionToRemove.toUpperCase()] || '0x0')
    : BigInt(permissionToRemove);
  
  return '0x' + (existing & ~toRemove).toString(16).padStart(64, '0');
}

/**
 * Get a preset permission configuration
 * @param {string} presetName - Name of the preset
 * @returns {{ permissions: string, name: string, description: string, riskLevel: string }}
 */
export function getPreset(presetName) {
  const preset = PERMISSION_PRESETS[presetName.toLowerCase()];
  if (!preset) {
    throw new Error(`Unknown preset: ${presetName}. Available: ${Object.keys(PERMISSION_PRESETS).join(', ')}`);
  }
  
  return {
    ...preset,
    permissions: encodePermissions(preset.permissions),
  };
}

/**
 * List all available presets
 * @returns {Object[]} Array of preset info objects
 */
export function listPresets() {
  return Object.entries(PERMISSION_PRESETS).map(([key, preset]) => ({
    key,
    ...preset,
    permissionsHex: encodePermissions(preset.permissions),
  }));
}

/**
 * Validate permissions for security risks
 * @param {string} permissionHex - Permissions as hex string
 * @returns {{ valid: boolean, warnings: string[], risks: string[], riskLevel: string }}
 */
export function validatePermissions(permissionHex) {
  const warnings = [];
  const risks = [];
  const decodedPerms = decodePermissions(permissionHex);
  
  let highestRiskLevel = 'LOW';
  const riskLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
  
  for (const perm of decodedPerms) {
    const riskInfo = PERMISSION_RISKS[perm];
    if (riskInfo) {
      const message = `${perm}: ${riskInfo.warning}`;
      
      if (riskInfo.level === 'CRITICAL') {
        risks.push(message);
        highestRiskLevel = 'CRITICAL';
      } else if (riskInfo.level === 'HIGH') {
        risks.push(message);
        if (riskLevels.indexOf(highestRiskLevel) < riskLevels.indexOf('HIGH')) {
          highestRiskLevel = 'HIGH';
        }
      } else if (riskInfo.level === 'MEDIUM') {
        warnings.push(message);
        if (riskLevels.indexOf(highestRiskLevel) < riskLevels.indexOf('MEDIUM')) {
          highestRiskLevel = 'MEDIUM';
        }
      } else {
        // LOW - don't add to warnings
      }
    }
  }
  
  return {
    valid: risks.length === 0,
    warnings,
    risks,
    riskLevel: highestRiskLevel,
    permissions: decodedPerms,
  };
}

/**
 * Build the data key for a controller's permissions
 * @param {string} controllerAddress - Controller address
 * @returns {string} Data key for permissions
 */
export function buildPermissionsDataKey(controllerAddress) {
  const prefix = DATA_KEYS['AddressPermissions:Permissions'];
  const address = controllerAddress.toLowerCase().replace('0x', '');
  return prefix + address;
}

/**
 * Build the data key for a controller's allowed calls
 * @param {string} controllerAddress - Controller address
 * @returns {string} Data key for allowed calls
 */
export function buildAllowedCallsDataKey(controllerAddress) {
  const prefix = DATA_KEYS['AddressPermissions:AllowedCalls'];
  const address = controllerAddress.toLowerCase().replace('0x', '');
  return prefix + address;
}

/**
 * Build the data key for a controller's allowed ERC725Y data keys
 * @param {string} controllerAddress - Controller address
 * @returns {string} Data key for allowed data keys
 */
export function buildAllowedDataKeysDataKey(controllerAddress) {
  const prefix = DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys'];
  const address = controllerAddress.toLowerCase().replace('0x', '');
  return prefix + address;
}

/**
 * Encode AllowedCalls restriction
 * @param {Object[]} allowedCalls - Array of allowed call configurations
 * @returns {string} Encoded allowed calls
 */
export function encodeAllowedCalls(allowedCalls) {
  if (!allowedCalls || allowedCalls.length === 0) {
    return '0x';
  }
  
  // Each allowed call entry is:
  // - 4 bytes: call types bitmask
  // - 20 bytes: address (or 0xFFFF...FFFF for any)
  // - 4 bytes: interface ID (or 0xFFFFFFFF for any)
  // - 4 bytes: function selector (or 0xFFFFFFFF for any)
  // Total: 32 bytes per entry
  
  let encoded = '0x';
  
  for (const call of allowedCalls) {
    // Call types: TRANSFERVALUE (0x1) | CALL (0x2) | STATICCALL (0x4) | DELEGATECALL (0x8)
    const callType = (call.callType || 0x0002).toString(16).padStart(8, '0');
    const address = (call.address || '0xffffffffffffffffffffffffffffffffffffffff').toLowerCase().replace('0x', '');
    const interfaceId = (call.interfaceId || '0xffffffff').replace('0x', '').padStart(8, '0');
    const functionSelector = (call.functionSelector || '0xffffffff').replace('0x', '').padStart(8, '0');
    
    encoded += callType + address + interfaceId + functionSelector;
  }
  
  return encoded;
}

/**
 * Decode AllowedCalls restriction
 * @param {string} encodedCalls - Encoded allowed calls hex string
 * @returns {Object[]} Array of allowed call configurations
 */
export function decodeAllowedCalls(encodedCalls) {
  if (!encodedCalls || encodedCalls === '0x' || encodedCalls.length < 66) {
    return [];
  }
  
  const data = encodedCalls.replace('0x', '');
  const calls = [];
  
  // Each entry is 64 hex chars (32 bytes)
  for (let i = 0; i < data.length; i += 64) {
    if (i + 64 > data.length) break;
    
    const entry = data.slice(i, i + 64);
    calls.push({
      callType: parseInt(entry.slice(0, 8), 16),
      address: '0x' + entry.slice(8, 48),
      interfaceId: '0x' + entry.slice(48, 56),
      functionSelector: '0x' + entry.slice(56, 64),
    });
  }
  
  return calls;
}

/**
 * Format permissions for display
 * @param {string} permissionHex - Permissions as hex string
 * @returns {string} Formatted permissions string
 */
export function formatPermissions(permissionHex) {
  const decoded = decodePermissions(permissionHex);
  const validation = validatePermissions(permissionHex);
  
  const lines = [];
  lines.push(`Permissions: ${permissionHex}`);
  lines.push(`Risk Level: ${validation.riskLevel}`);
  lines.push('');
  lines.push('Active Permissions:');
  
  for (const perm of decoded) {
    const risk = PERMISSION_RISKS[perm];
    const riskIcon = {
      CRITICAL: '🔴',
      HIGH: '🟠',
      MEDIUM: '🟡',
      LOW: '🟢',
    }[risk?.level || 'LOW'];
    
    lines.push(`  ${riskIcon} ${perm}`);
  }
  
  if (validation.risks.length > 0) {
    lines.push('');
    lines.push('⚠️ Security Risks:');
    for (const risk of validation.risks) {
      lines.push(`  - ${risk}`);
    }
  }
  
  if (validation.warnings.length > 0) {
    lines.push('');
    lines.push('⚡ Warnings:');
    for (const warning of validation.warnings) {
      lines.push(`  - ${warning}`);
    }
  }
  
  return lines.join('\n');
}

export default {
  encodePermissions,
  combinePermissions,
  decodePermissions,
  hasPermission,
  addPermission,
  removePermission,
  getPreset,
  listPresets,
  validatePermissions,
  buildPermissionsDataKey,
  buildAllowedCallsDataKey,
  buildAllowedDataKeysDataKey,
  encodeAllowedCalls,
  decodeAllowedCalls,
  formatPermissions,
};
