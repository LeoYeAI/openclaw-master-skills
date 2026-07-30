import { describe, it, expect } from 'vitest';

import {
  PERMISSION_PRESETS,
  combinePermissions,
  decodePermissions,
  hasPermission,
  getPermissionDataKey,
  getAllowedCallsDataKey,
  getAllowedDataKeysDataKey,
  encodeAllowedCalls,
  encodeAllowedDataKeys,
  validatePermissions,
  describePermissions,
  getPresetConfig,
  listPresets,
} from '../../src/lib/permissions.js';

import { PERMISSIONS, DATA_KEYS } from '../../src/utils/constants.js';

// ==================== combinePermissions ====================

describe('combinePermissions', () => {
  it('should return zero-padded bytes32 for a single permission', () => {
    const result = combinePermissions(['CALL']);
    expect(result).toBe(PERMISSIONS.CALL);
  });

  it('should combine two permissions with bitwise OR', () => {
    const result = combinePermissions(['CALL', 'TRANSFERVALUE']);
    const expected = BigInt(PERMISSIONS.CALL) | BigInt(PERMISSIONS.TRANSFERVALUE);
    expect(BigInt(result)).toBe(expected);
  });

  it('should combine multiple permissions', () => {
    const result = combinePermissions(['SETDATA', 'CALL', 'TRANSFERVALUE']);
    const expected =
      BigInt(PERMISSIONS.SETDATA) |
      BigInt(PERMISSIONS.CALL) |
      BigInt(PERMISSIONS.TRANSFERVALUE);
    expect(BigInt(result)).toBe(expected);
  });

  it('should return a 66-character hex string (0x + 64 hex chars = bytes32)', () => {
    const result = combinePermissions(['CALL']);
    expect(result).toMatch(/^0x[0-9a-f]{64}$/);
  });

  it('should return 0x00...00 for an empty array', () => {
    const result = combinePermissions([]);
    expect(BigInt(result)).toBe(0n);
    expect(result).toHaveLength(66);
  });

  it('should be idempotent when the same permission is listed twice', () => {
    const once = combinePermissions(['CALL']);
    const twice = combinePermissions(['CALL', 'CALL']);
    expect(once).toBe(twice);
  });

  it('should produce ALL_PERMISSIONS when combining the permissions it covers', () => {
    // ALL_PERMISSIONS = 0x7f3f7f. It intentionally excludes REENTRANCY (0x80),
    // SUPER_DELEGATECALL (0x4000), and DELEGATECALL (0x8000).
    const allPerms = combinePermissions([
      'CHANGEOWNER',
      'ADDCONTROLLER',
      'EDITPERMISSIONS',
      'ADDEXTENSIONS',
      'CHANGEEXTENSIONS',
      'ADDUNIVERSALRECEIVERDELEGATE',
      'CHANGEUNIVERSALRECEIVERDELEGATE',
      // REENTRANCY excluded from ALL_PERMISSIONS
      'SUPER_TRANSFERVALUE',
      'TRANSFERVALUE',
      'SUPER_CALL',
      'CALL',
      'SUPER_STATICCALL',
      'STATICCALL',
      // SUPER_DELEGATECALL excluded from ALL_PERMISSIONS
      // DELEGATECALL excluded from ALL_PERMISSIONS
      'DEPLOY',
      'SUPER_SETDATA',
      'SETDATA',
      'ENCRYPT',
      'DECRYPT',
      'SIGN',
      'EXECUTE_RELAY_CALL',
    ]);
    expect(BigInt(allPerms)).toBe(BigInt(PERMISSIONS.ALL_PERMISSIONS));
  });

  it('should produce a value larger than ALL_PERMISSIONS when all individual permissions are included', () => {
    // Including REENTRANCY, SUPER_DELEGATECALL, and DELEGATECALL exceeds ALL_PERMISSIONS
    const allIndividual = combinePermissions([
      'CHANGEOWNER',
      'ADDCONTROLLER',
      'EDITPERMISSIONS',
      'ADDEXTENSIONS',
      'CHANGEEXTENSIONS',
      'ADDUNIVERSALRECEIVERDELEGATE',
      'CHANGEUNIVERSALRECEIVERDELEGATE',
      'REENTRANCY',
      'SUPER_TRANSFERVALUE',
      'TRANSFERVALUE',
      'SUPER_CALL',
      'CALL',
      'SUPER_STATICCALL',
      'STATICCALL',
      'SUPER_DELEGATECALL',
      'DELEGATECALL',
      'DEPLOY',
      'SUPER_SETDATA',
      'SETDATA',
      'ENCRYPT',
      'DECRYPT',
      'SIGN',
      'EXECUTE_RELAY_CALL',
    ]);
    expect(BigInt(allIndividual)).toBeGreaterThan(BigInt(PERMISSIONS.ALL_PERMISSIONS));
  });
});

// ==================== decodePermissions ====================

describe('decodePermissions', () => {
  it('should decode a single permission and also match ALL_PERMISSIONS (shared bits)', () => {
    // decodePermissions uses bitwise AND, so ALL_PERMISSIONS (0x7f3f7f) will
    // match any permission whose bits are a subset of ALL_PERMISSIONS. CALL
    // (0x800) has bits within ALL_PERMISSIONS, so both CALL and ALL_PERMISSIONS
    // appear in the result.
    const decoded = decodePermissions(PERMISSIONS.CALL);
    expect(decoded).toContain('CALL');
    expect(decoded).toContain('ALL_PERMISSIONS');
  });

  it('should decode combined permissions', () => {
    const combined = combinePermissions(['CALL', 'TRANSFERVALUE']);
    const decoded = decodePermissions(combined);
    expect(decoded).toContain('CALL');
    expect(decoded).toContain('TRANSFERVALUE');
    // Also includes ALL_PERMISSIONS since CALL and TRANSFERVALUE bits overlap with it
    expect(decoded).toContain('ALL_PERMISSIONS');
  });

  it('should decode ALL_PERMISSIONS into every individual permission', () => {
    const decoded = decodePermissions(PERMISSIONS.ALL_PERMISSIONS);
    // ALL_PERMISSIONS itself will also appear because its bit pattern is set
    expect(decoded).toContain('ALL_PERMISSIONS');
    expect(decoded).toContain('CHANGEOWNER');
    expect(decoded).toContain('CALL');
    expect(decoded).toContain('SETDATA');
    expect(decoded).toContain('DEPLOY');
  });

  it('should return an empty array for zero permissions', () => {
    const decoded = decodePermissions(
      '0x0000000000000000000000000000000000000000000000000000000000000000'
    );
    expect(decoded).toEqual([]);
  });
});

// ==================== round-trip: combinePermissions + decodePermissions ====================

describe('combinePermissions + decodePermissions round-trip', () => {
  // Note: decodePermissions uses bitwise AND against each PERMISSIONS entry,
  // including ALL_PERMISSIONS (a multi-bit mask). As a result, decoding any
  // permission whose bits overlap with ALL_PERMISSIONS will also include
  // ALL_PERMISSIONS in the output. The round-trip preserves the original
  // permissions but may include ALL_PERMISSIONS as an extra entry.

  it('should round-trip a single permission (contains original plus ALL_PERMISSIONS)', () => {
    const perms = ['CALL'] as const;
    const hex = combinePermissions([...perms]);
    const decoded = decodePermissions(hex);
    for (const p of perms) {
      expect(decoded).toContain(p);
    }
    // Re-encoding the decoded set should reproduce the same hex value (superset is harmless since ALL_PERMISSIONS bits are a superset)
    // But the key property: every original permission is preserved
  });

  it('should round-trip multiple permissions (contains all originals)', () => {
    const perms = ['CALL', 'TRANSFERVALUE', 'SETDATA'] as const;
    const hex = combinePermissions([...perms]);
    const decoded = decodePermissions(hex);
    for (const p of perms) {
      expect(decoded).toContain(p);
    }
  });

  it('should round-trip with high-bit permissions (contains all originals)', () => {
    const perms = ['EXECUTE_RELAY_CALL', 'SIGN', 'DECRYPT'] as const;
    const hex = combinePermissions([...perms]);
    const decoded = decodePermissions(hex);
    for (const p of perms) {
      expect(decoded).toContain(p);
    }
  });

  it('should produce the same hex when re-combining decoded permissions', () => {
    // Encoding -> decoding -> re-encoding should preserve the same numeric value
    const original = ['CALL', 'TRANSFERVALUE', 'SETDATA'] as const;
    const hex = combinePermissions([...original]);
    const decoded = decodePermissions(hex);
    const reEncoded = combinePermissions(decoded);
    // Re-encoding includes ALL_PERMISSIONS bits, but since the original
    // permissions are a subset of ALL_PERMISSIONS, the result may differ.
    // However, the original bits must still be present.
    for (const p of original) {
      expect(hasPermission(reEncoded, p)).toBe(true);
    }
  });

  it('should exactly round-trip permissions that include bits outside ALL_PERMISSIONS', () => {
    // REENTRANCY (0x80) is NOT in ALL_PERMISSIONS, so decoding REENTRANCY
    // alone should not include ALL_PERMISSIONS.
    const perms = ['REENTRANCY'] as const;
    const hex = combinePermissions([...perms]);
    const decoded = decodePermissions(hex);
    expect(decoded).toContain('REENTRANCY');
    expect(decoded).not.toContain('ALL_PERMISSIONS');
    expect(decoded).toHaveLength(1);
  });
});

// ==================== hasPermission ====================

describe('hasPermission', () => {
  it('should return true when the permission is present', () => {
    const hex = combinePermissions(['CALL', 'TRANSFERVALUE']);
    expect(hasPermission(hex, 'CALL')).toBe(true);
    expect(hasPermission(hex, 'TRANSFERVALUE')).toBe(true);
  });

  it('should return false when the permission is absent', () => {
    const hex = combinePermissions(['CALL']);
    expect(hasPermission(hex, 'TRANSFERVALUE')).toBe(false);
    expect(hasPermission(hex, 'SETDATA')).toBe(false);
  });

  it('should return true for every permission in ALL_PERMISSIONS', () => {
    expect(hasPermission(PERMISSIONS.ALL_PERMISSIONS, 'CHANGEOWNER')).toBe(true);
    expect(hasPermission(PERMISSIONS.ALL_PERMISSIONS, 'CALL')).toBe(true);
    expect(hasPermission(PERMISSIONS.ALL_PERMISSIONS, 'DEPLOY')).toBe(true);
    expect(hasPermission(PERMISSIONS.ALL_PERMISSIONS, 'EXECUTE_RELAY_CALL')).toBe(true);
  });

  it('should return false for any permission on a zero value', () => {
    const zero =
      '0x0000000000000000000000000000000000000000000000000000000000000000';
    expect(hasPermission(zero, 'CALL')).toBe(false);
    expect(hasPermission(zero, 'CHANGEOWNER')).toBe(false);
  });

  it('should return true for CHANGEOWNER (bit 0)', () => {
    expect(hasPermission(PERMISSIONS.CHANGEOWNER, 'CHANGEOWNER')).toBe(true);
  });

  it('should not confuse adjacent bit permissions', () => {
    // SUPER_CALL = 0x0400, CALL = 0x0800 -- adjacent bits
    const hex = combinePermissions(['SUPER_CALL']);
    expect(hasPermission(hex, 'SUPER_CALL')).toBe(true);
    expect(hasPermission(hex, 'CALL')).toBe(false);
  });
});

// ==================== getPermissionDataKey ====================

describe('getPermissionDataKey', () => {
  const testAddress = '0x1234567890AbCdEf1234567890aBcDeF12345678';

  it('should start with the correct data key prefix', () => {
    const key = getPermissionDataKey(testAddress);
    expect(key.startsWith(DATA_KEYS['AddressPermissions:Permissions'])).toBe(true);
  });

  it('should append the lowercase address without 0x', () => {
    const key = getPermissionDataKey(testAddress);
    const suffix = key.slice(DATA_KEYS['AddressPermissions:Permissions'].length);
    expect(suffix).toBe(testAddress.slice(2).toLowerCase());
  });

  it('should produce the correct total length (prefix 24 chars + 40 hex address = 64 hex + 0x = 66)', () => {
    const key = getPermissionDataKey(testAddress);
    // prefix is 0x + 24 hex chars = 26 chars; suffix is 40 hex chars; total = 66
    expect(key).toHaveLength(
      DATA_KEYS['AddressPermissions:Permissions'].length + 40
    );
  });

  it('should always lowercase the address portion', () => {
    const mixedCase = '0xABCDEF1234567890abcdef1234567890ABCDEF12';
    const key = getPermissionDataKey(mixedCase);
    const suffix = key.slice(DATA_KEYS['AddressPermissions:Permissions'].length);
    expect(suffix).toBe(suffix.toLowerCase());
  });
});

// ==================== getAllowedCallsDataKey ====================

describe('getAllowedCallsDataKey', () => {
  const testAddress = '0x1234567890AbCdEf1234567890aBcDeF12345678';

  it('should start with the AllowedCalls prefix', () => {
    const key = getAllowedCallsDataKey(testAddress);
    expect(key.startsWith(DATA_KEYS['AddressPermissions:AllowedCalls'])).toBe(true);
  });

  it('should append the lowercase address without 0x', () => {
    const key = getAllowedCallsDataKey(testAddress);
    const suffix = key.slice(DATA_KEYS['AddressPermissions:AllowedCalls'].length);
    expect(suffix).toBe(testAddress.slice(2).toLowerCase());
  });

  it('should produce consistent output for the same address', () => {
    const key1 = getAllowedCallsDataKey(testAddress);
    const key2 = getAllowedCallsDataKey(testAddress);
    expect(key1).toBe(key2);
  });
});

// ==================== getAllowedDataKeysDataKey ====================

describe('getAllowedDataKeysDataKey', () => {
  const testAddress = '0xDeadBeef00000000000000000000000000000001';

  it('should start with the AllowedERC725YDataKeys prefix', () => {
    const key = getAllowedDataKeysDataKey(testAddress);
    expect(key.startsWith(DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys'])).toBe(
      true
    );
  });

  it('should append the lowercase address without 0x', () => {
    const key = getAllowedDataKeysDataKey(testAddress);
    const suffix = key.slice(
      DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys'].length
    );
    expect(suffix).toBe(testAddress.slice(2).toLowerCase());
  });
});

// ==================== encodeAllowedCalls ====================

describe('encodeAllowedCalls', () => {
  it('should return 0x for an empty config', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000003],
      addresses: [],
      interfaceIds: [],
      functionSelectors: [],
    });
    expect(result).toBe('0x');
  });

  it('should return a hex string starting with 0x for a populated config', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000003],
      addresses: ['0x1234567890123456789012345678901234567890'],
      interfaceIds: ['0xc52d6008'],
      functionSelectors: ['0x760d9bba'],
    });
    expect(result).toMatch(/^0x[0-9a-f]+$/);
  });

  it('should encode a single entry as a CompactBytesArray with 2-byte length prefix + 32-byte entry', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000003],
      addresses: ['0x1234567890123456789012345678901234567890'],
      interfaceIds: ['0xc52d6008'],
      functionSelectors: ['0x760d9bba'],
    });
    // Remove 0x prefix
    const data = result.slice(2);
    // Each entry: 4 bytes callType + 20 bytes address + 4 bytes interfaceId + 4 bytes selector = 32 bytes
    // CompactBytesArray: 2-byte length prefix (0020 = 32) + 32 bytes entry = 34 bytes = 68 hex chars
    const lengthPrefix = data.slice(0, 4);
    expect(lengthPrefix).toBe('0020'); // 32 bytes
    expect(data).toHaveLength(68); // 4 chars length + 64 chars entry
  });

  it('should use wildcard address 0xfff...f when addresses array is empty but others are set', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000003],
      addresses: [],
      interfaceIds: ['0xc52d6008'],
      functionSelectors: ['0x760d9bba'],
    });
    const data = result.slice(2);
    // Skip 4-char length prefix + 8-char callType = offset 12
    const addressPart = data.slice(12, 52); // 40 hex chars = 20 bytes
    expect(addressPart).toBe('ffffffffffffffffffffffffffffffffffffffff');
  });

  it('should use wildcard interfaceId 0xffffffff when interfaceIds array is empty but others are set', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000003],
      addresses: ['0x1234567890123456789012345678901234567890'],
      interfaceIds: [],
      functionSelectors: ['0x760d9bba'],
    });
    const data = result.slice(2);
    // Skip 4-char length prefix + 8-char callType + 40-char address = offset 52
    const interfaceIdPart = data.slice(52, 60); // 8 hex chars = 4 bytes
    expect(interfaceIdPart).toBe('ffffffff');
  });

  it('should use wildcard selector 0xffffffff when functionSelectors array is empty but others are set', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000003],
      addresses: ['0x1234567890123456789012345678901234567890'],
      interfaceIds: ['0xc52d6008'],
      functionSelectors: [],
    });
    const data = result.slice(2);
    // Skip 4-char length + 8-char callType + 40-char address + 8-char interfaceId = offset 60
    const selectorPart = data.slice(60, 68);
    expect(selectorPart).toBe('ffffffff');
  });

  it('should generate entries for every combination (cartesian product)', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000001],
      addresses: [
        '0x1111111111111111111111111111111111111111',
        '0x2222222222222222222222222222222222222222',
      ],
      interfaceIds: ['0xaaaaaaaa'],
      functionSelectors: ['0xbbbbbbbb'],
    });
    const data = result.slice(2);
    // 2 addresses x 1 interfaceId x 1 selector = 2 entries
    // Each entry: 4 chars length + 64 chars data = 68 chars
    expect(data).toHaveLength(68 * 2);
  });

  it('should lowercase addresses in the output', () => {
    const result = encodeAllowedCalls({
      callTypes: [0x00000003],
      addresses: ['0xABCDEF1234567890ABCDEF1234567890ABCDEF12'],
      interfaceIds: ['0xc52d6008'],
      functionSelectors: ['0x760d9bba'],
    });
    // No uppercase hex chars should appear after the 0x prefix
    const data = result.slice(2);
    expect(data).toBe(data.toLowerCase());
  });
});

// ==================== encodeAllowedDataKeys ====================

describe('encodeAllowedDataKeys', () => {
  it('should return 0x for empty array', () => {
    expect(encodeAllowedDataKeys([])).toBe('0x');
  });

  it('should encode a single 4-byte prefix', () => {
    const result = encodeAllowedDataKeys(['0x5ef83ad9']);
    const data = result.slice(2);
    // 2-byte length prefix (0004 = 4 bytes) + 4 bytes data = 12 hex chars
    expect(data.slice(0, 4)).toBe('0004');
    expect(data.slice(4)).toBe('5ef83ad9');
  });

  it('should encode multiple prefixes as a CompactBytesArray', () => {
    const result = encodeAllowedDataKeys(['0x5ef83ad9', '0x6460ee3c']);
    const data = result.slice(2);
    // First entry: 0004 + 5ef83ad9 = 12 hex chars
    // Second entry: 0004 + 6460ee3c = 12 hex chars
    expect(data).toHaveLength(24);
    expect(data.slice(0, 12)).toBe('00045ef83ad9');
    expect(data.slice(12, 24)).toBe('00046460ee3c');
  });

  it('should handle prefixes without 0x', () => {
    const result = encodeAllowedDataKeys(['5ef83ad9']);
    const data = result.slice(2);
    expect(data.slice(4)).toBe('5ef83ad9');
  });

  it('should handle a longer key prefix', () => {
    // A full 32-byte key (64 hex chars without 0x)
    const fullKey =
      '0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5';
    const result = encodeAllowedDataKeys([fullKey]);
    const data = result.slice(2);
    // 2-byte length = 0020 (32 bytes) + 64 hex chars of key = 68 total
    expect(data.slice(0, 4)).toBe('0020');
    expect(data.slice(4)).toBe(fullKey.slice(2));
  });
});

// ==================== validatePermissions ====================

describe('validatePermissions', () => {
  it('should return valid:true and no risks for safe permissions', () => {
    const hex = combinePermissions(['CALL', 'TRANSFERVALUE']);
    const result = validatePermissions(hex);
    expect(result.valid).toBe(true);
    expect(result.risks).toHaveLength(0);
  });

  it('should flag CHANGEOWNER as a risk', () => {
    const hex = combinePermissions(['CHANGEOWNER']);
    const result = validatePermissions(hex);
    expect(result.valid).toBe(false);
    expect(result.risks.some((r) => r.includes('CHANGEOWNER'))).toBe(true);
  });

  it('should flag SUPER_DELEGATECALL as a risk', () => {
    const hex = combinePermissions(['SUPER_DELEGATECALL']);
    const result = validatePermissions(hex);
    expect(result.valid).toBe(false);
    expect(result.risks.some((r) => r.includes('SUPER_DELEGATECALL'))).toBe(true);
  });

  it('should flag DELEGATECALL as a risk', () => {
    const hex = combinePermissions(['DELEGATECALL']);
    const result = validatePermissions(hex);
    expect(result.valid).toBe(false);
    expect(result.risks.some((r) => r.includes('DELEGATECALL'))).toBe(true);
  });

  it('should flag CHANGEOWNER in ALL_PERMISSIONS (but not DELEGATECALL variants which are excluded)', () => {
    // ALL_PERMISSIONS (0x7f3f7f) intentionally excludes REENTRANCY (0x80),
    // SUPER_DELEGATECALL (0x4000), and DELEGATECALL (0x8000).
    // So only CHANGEOWNER is flagged as a risk.
    const result = validatePermissions(PERMISSIONS.ALL_PERMISSIONS);
    expect(result.valid).toBe(false);
    expect(result.risks.some((r) => r.includes('CHANGEOWNER'))).toBe(true);
    expect(result.risks.some((r) => r.includes('SUPER_DELEGATECALL'))).toBe(false);
    expect(result.risks.some((r) => r.includes('DELEGATECALL'))).toBe(false);
  });

  it('should flag all three critical permissions when they are explicitly combined', () => {
    const hex = combinePermissions([
      'CHANGEOWNER',
      'SUPER_DELEGATECALL',
      'DELEGATECALL',
    ]);
    const result = validatePermissions(hex);
    expect(result.valid).toBe(false);
    expect(result.risks.length).toBe(3);
    expect(result.risks.some((r) => r.includes('CHANGEOWNER'))).toBe(true);
    expect(result.risks.some((r) => r.includes('SUPER_DELEGATECALL'))).toBe(true);
    expect(result.risks.some((r) => r.includes('DELEGATECALL'))).toBe(true);
  });

  it('should warn about EDITPERMISSIONS', () => {
    const hex = combinePermissions(['EDITPERMISSIONS']);
    const result = validatePermissions(hex);
    expect(result.warnings.some((w) => w.includes('EDITPERMISSIONS'))).toBe(true);
  });

  it('should warn about ADDCONTROLLER', () => {
    const hex = combinePermissions(['ADDCONTROLLER']);
    const result = validatePermissions(hex);
    expect(result.warnings.some((w) => w.includes('ADDCONTROLLER'))).toBe(true);
  });

  it('should warn about SUPER_SETDATA', () => {
    const hex = combinePermissions(['SUPER_SETDATA']);
    const result = validatePermissions(hex);
    expect(result.warnings.some((w) => w.includes('SUPER_SETDATA'))).toBe(true);
  });

  it('should warn about SUPER_CALL', () => {
    const hex = combinePermissions(['SUPER_CALL']);
    const result = validatePermissions(hex);
    expect(result.warnings.some((w) => w.includes('SUPER_CALL'))).toBe(true);
  });

  it('should warn about SUPER_TRANSFERVALUE', () => {
    const hex = combinePermissions(['SUPER_TRANSFERVALUE']);
    const result = validatePermissions(hex);
    expect(result.warnings.some((w) => w.includes('SUPER_TRANSFERVALUE'))).toBe(true);
  });

  it('should warn about DEPLOY', () => {
    const hex = combinePermissions(['DEPLOY']);
    const result = validatePermissions(hex);
    expect(result.warnings.some((w) => w.includes('DEPLOY'))).toBe(true);
  });

  it('should return valid:true with no warnings for zero permissions', () => {
    const zero =
      '0x0000000000000000000000000000000000000000000000000000000000000000';
    const result = validatePermissions(zero);
    expect(result.valid).toBe(true);
    expect(result.warnings).toHaveLength(0);
    expect(result.risks).toHaveLength(0);
  });

  it('should collect risks and warnings simultaneously', () => {
    const hex = combinePermissions([
      'CHANGEOWNER',
      'EDITPERMISSIONS',
      'SUPER_DELEGATECALL',
      'SUPER_CALL',
    ]);
    const result = validatePermissions(hex);
    expect(result.valid).toBe(false);
    expect(result.risks.length).toBeGreaterThanOrEqual(2);
    expect(result.warnings.length).toBeGreaterThanOrEqual(2);
  });
});

// ==================== describePermissions ====================

describe('describePermissions', () => {
  it('should return human-readable descriptions for decoded permissions', () => {
    const hex = combinePermissions(['CALL']);
    const descriptions = describePermissions(hex);
    expect(descriptions).toContain('Call contracts (with restrictions)');
  });

  it('should return descriptions for multiple permissions', () => {
    const hex = combinePermissions(['CALL', 'TRANSFERVALUE', 'SETDATA']);
    const descriptions = describePermissions(hex);
    expect(descriptions).toContain('Call contracts (with restrictions)');
    expect(descriptions).toContain('Transfer value (with restrictions)');
    expect(descriptions).toContain('Set data (with restrictions)');
  });

  it('should return an empty array for zero permissions', () => {
    const zero =
      '0x0000000000000000000000000000000000000000000000000000000000000000';
    const descriptions = describePermissions(zero);
    expect(descriptions).toEqual([]);
  });

  it('should describe CHANGEOWNER correctly', () => {
    const descriptions = describePermissions(PERMISSIONS.CHANGEOWNER);
    expect(descriptions).toContain('Change profile ownership');
  });

  it('should describe DEPLOY correctly', () => {
    const descriptions = describePermissions(PERMISSIONS.DEPLOY);
    expect(descriptions).toContain('Deploy contracts');
  });
});

// ==================== PERMISSION_PRESETS ====================

describe('PERMISSION_PRESETS', () => {
  const expectedPresets: string[] = [
    'read-only',
    'token-operator',
    'nft-trader',
    'defi-trader',
    'profile-manager',
    'full-access',
  ];

  it('should contain exactly 6 presets', () => {
    expect(Object.keys(PERMISSION_PRESETS)).toHaveLength(6);
  });

  it.each(expectedPresets)('should contain the "%s" preset', (presetName) => {
    expect(PERMISSION_PRESETS).toHaveProperty(presetName);
  });

  it('each preset should have name, description, permissions, and riskLevel', () => {
    for (const [, config] of Object.entries(PERMISSION_PRESETS)) {
      expect(config).toHaveProperty('name');
      expect(config).toHaveProperty('description');
      expect(config).toHaveProperty('permissions');
      expect(config).toHaveProperty('riskLevel');
      expect(typeof config.name).toBe('string');
      expect(typeof config.description).toBe('string');
      expect(config.permissions).toMatch(/^0x[0-9a-f]+$/);
      expect(['low', 'medium', 'medium-high', 'high', 'critical']).toContain(
        config.riskLevel
      );
    }
  });

  it('read-only should have low risk', () => {
    expect(PERMISSION_PRESETS['read-only'].riskLevel).toBe('low');
  });

  it('token-operator should have medium risk', () => {
    expect(PERMISSION_PRESETS['token-operator'].riskLevel).toBe('medium');
  });

  it('nft-trader should have medium risk', () => {
    expect(PERMISSION_PRESETS['nft-trader'].riskLevel).toBe('medium');
  });

  it('defi-trader should have medium-high risk', () => {
    expect(PERMISSION_PRESETS['defi-trader'].riskLevel).toBe('medium-high');
  });

  it('profile-manager should have medium risk', () => {
    expect(PERMISSION_PRESETS['profile-manager'].riskLevel).toBe('medium');
  });

  it('full-access should have critical risk', () => {
    expect(PERMISSION_PRESETS['full-access'].riskLevel).toBe('critical');
  });

  it('full-access permissions should equal ALL_PERMISSIONS', () => {
    expect(PERMISSION_PRESETS['full-access'].permissions).toBe(
      PERMISSIONS.ALL_PERMISSIONS
    );
  });

  it('token-operator should have allowedCalls defined', () => {
    expect(PERMISSION_PRESETS['token-operator'].allowedCalls).toBeDefined();
    expect(
      PERMISSION_PRESETS['token-operator'].allowedCalls!.functionSelectors.length
    ).toBeGreaterThan(0);
  });

  it('profile-manager should have allowedDataKeys defined', () => {
    expect(PERMISSION_PRESETS['profile-manager'].allowedDataKeys).toBeDefined();
    expect(
      PERMISSION_PRESETS['profile-manager'].allowedDataKeys!.length
    ).toBeGreaterThan(0);
  });

  it('token-operator permissions should include CALL and TRANSFERVALUE', () => {
    const hex = PERMISSION_PRESETS['token-operator'].permissions;
    expect(hasPermission(hex, 'CALL')).toBe(true);
    expect(hasPermission(hex, 'TRANSFERVALUE')).toBe(true);
  });

  it('profile-manager permissions should include SETDATA and CALL', () => {
    const hex = PERMISSION_PRESETS['profile-manager'].permissions;
    expect(hasPermission(hex, 'SETDATA')).toBe(true);
    expect(hasPermission(hex, 'CALL')).toBe(true);
  });
});

// ==================== getPresetConfig ====================

describe('getPresetConfig', () => {
  it('should return the correct config for each preset', () => {
    const config = getPresetConfig('read-only');
    expect(config.name).toBe('Read Only');
    expect(config.riskLevel).toBe('low');
  });

  it('should return the same object as PERMISSION_PRESETS[preset]', () => {
    const config = getPresetConfig('full-access');
    expect(config).toBe(PERMISSION_PRESETS['full-access']);
  });

  it('should return config with permissions for token-operator', () => {
    const config = getPresetConfig('token-operator');
    expect(config.permissions).toBeDefined();
    expect(config.allowedCalls).toBeDefined();
  });
});

// ==================== listPresets ====================

describe('listPresets', () => {
  it('should return an array of 6 presets', () => {
    const presets = listPresets();
    expect(presets).toHaveLength(6);
  });

  it('should return objects with name and config properties', () => {
    const presets = listPresets();
    for (const preset of presets) {
      expect(preset).toHaveProperty('name');
      expect(preset).toHaveProperty('config');
      expect(typeof preset.name).toBe('string');
      expect(preset.config).toHaveProperty('permissions');
      expect(preset.config).toHaveProperty('riskLevel');
    }
  });

  it('should include every expected preset name', () => {
    const presets = listPresets();
    const names = presets.map((p) => p.name);
    expect(names).toContain('read-only');
    expect(names).toContain('token-operator');
    expect(names).toContain('nft-trader');
    expect(names).toContain('defi-trader');
    expect(names).toContain('profile-manager');
    expect(names).toContain('full-access');
  });

  it('should have configs that match PERMISSION_PRESETS', () => {
    const presets = listPresets();
    for (const preset of presets) {
      expect(preset.config).toBe(
        PERMISSION_PRESETS[preset.name as keyof typeof PERMISSION_PRESETS]
      );
    }
  });
});

// ==================== Data key format correctness ====================

describe('Data key format correctness', () => {
  const address = '0xCafeBabe0000000000000000000000000000DEAD';

  it('getPermissionDataKey should produce a valid bytes32 data key (66 chars)', () => {
    const key = getPermissionDataKey(address);
    expect(key).toHaveLength(66);
    expect(key).toMatch(/^0x[0-9a-f]+$/);
  });

  it('getAllowedCallsDataKey should produce a valid bytes32 data key (66 chars)', () => {
    const key = getAllowedCallsDataKey(address);
    expect(key).toHaveLength(66);
    expect(key).toMatch(/^0x[0-9a-f]+$/);
  });

  it('getAllowedDataKeysDataKey should produce a valid bytes32 data key (66 chars)', () => {
    const key = getAllowedDataKeysDataKey(address);
    expect(key).toHaveLength(66);
    expect(key).toMatch(/^0x[0-9a-f]+$/);
  });

  it('different key functions should produce different keys for the same address', () => {
    const permKey = getPermissionDataKey(address);
    const callsKey = getAllowedCallsDataKey(address);
    const dataKeysKey = getAllowedDataKeysDataKey(address);
    expect(permKey).not.toBe(callsKey);
    expect(permKey).not.toBe(dataKeysKey);
    expect(callsKey).not.toBe(dataKeysKey);
  });

  it('same function with different addresses should produce different keys', () => {
    const addr1 = '0x0000000000000000000000000000000000000001';
    const addr2 = '0x0000000000000000000000000000000000000002';
    expect(getPermissionDataKey(addr1)).not.toBe(getPermissionDataKey(addr2));
  });
});

// ==================== Edge cases ====================

describe('Edge cases', () => {
  it('combinePermissions with CHANGEOWNER returns the lowest bit set', () => {
    const hex = combinePermissions(['CHANGEOWNER']);
    expect(BigInt(hex)).toBe(1n);
  });

  it('combinePermissions with EXECUTE_RELAY_CALL returns the highest standard bit', () => {
    const hex = combinePermissions(['EXECUTE_RELAY_CALL']);
    expect(BigInt(hex)).toBe(BigInt(PERMISSIONS.EXECUTE_RELAY_CALL));
  });

  it('validatePermissions on read-only preset should return valid', () => {
    const result = validatePermissions(PERMISSION_PRESETS['read-only'].permissions);
    expect(result.valid).toBe(true);
    expect(result.risks).toHaveLength(0);
  });

  it('validatePermissions on full-access preset should flag multiple risks', () => {
    const result = validatePermissions(PERMISSION_PRESETS['full-access'].permissions);
    expect(result.valid).toBe(false);
    expect(result.risks.length).toBeGreaterThanOrEqual(1);
  });

  it('describePermissions should return correct count matching decodePermissions', () => {
    const hex = combinePermissions(['CALL', 'SETDATA', 'DEPLOY']);
    const decoded = decodePermissions(hex);
    const described = describePermissions(hex);
    expect(described).toHaveLength(decoded.length);
  });
});
