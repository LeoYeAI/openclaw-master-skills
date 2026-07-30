import { describe, it, expect, vi, beforeEach } from 'vitest';

import { DATA_KEYS, INTERFACE_IDS, PERMISSIONS } from '../../src/utils/constants.js';
import { UniversalProfileError, ERROR_CODES } from '../../src/types/index.js';

// ==================== Helpers ====================

const VALID_UP_ADDRESS = '0x1234567890AbcdEF1234567890aBcdef12345678';
const VALID_CONTROLLER = '0xabCDEF1234567890ABcDEF1234567890aBCDeF12';
const VALID_KM_ADDRESS = '0xdEADbeEF00000000000000000000000000000001';
const ZERO_PERMISSIONS = '0x0000000000000000000000000000000000000000000000000000000000000000';

/**
 * Build a mock contract whose methods are vi.fn() stubs.
 */
function createMockContract() {
  return {
    getData: vi.fn(),
    getDataBatch: vi.fn(),
    owner: vi.fn(),
    supportsInterface: vi.fn(),
    getFunction: vi.fn(),
  };
}

/**
 * Build a mock provider with getCode and getBalance stubs.
 */
function createMockProvider() {
  return {
    getCode: vi.fn(),
    getBalance: vi.fn(),
  } as any;
}

// Shared mock for the Contract constructor. The vi.mock factory below captures
// this reference. In beforeEach we swap out `contractFactory` to point at a fresh
// mock contract, and the factory closure picks it up.
let contractFactory: (...args: any[]) => any;

vi.mock('ethers', async () => {
  const actual = await vi.importActual<typeof import('ethers')>('ethers');
  return {
    ...actual,
    Contract: vi.fn((...args: any[]) => contractFactory(...args)),
  };
});

// We import profile AFTER the mock is set up (vi.mock is hoisted anyway).
import {
  getProfileInfo,
  getControllers,
  isController,
  getControllerPermissions,
  getReceivedAssets,
  getData,
  getDataBatch,
  getKeyManager,
  verifyKeyManager,
} from '../../src/lib/profile.js';

// We also need actual ethers utilities (isAddress, getAddress, etc.)
import { ethers } from 'ethers';

// ==================== Setup ====================

let mockContract: ReturnType<typeof createMockContract>;
let mockProvider: ReturnType<typeof createMockProvider>;

beforeEach(() => {
  vi.clearAllMocks();
  mockContract = createMockContract();
  contractFactory = () => mockContract;
  mockProvider = createMockProvider();
});

// ==================== getProfileInfo ====================

describe('getProfileInfo', () => {
  it('should throw on an invalid address', async () => {
    await expect(getProfileInfo('not-an-address', mockProvider)).rejects.toThrow(
      UniversalProfileError
    );
    await expect(getProfileInfo('not-an-address', mockProvider)).rejects.toThrow(
      /Invalid address/
    );
  });

  it('should throw with INVALID_ADDRESS code for invalid address', async () => {
    try {
      await getProfileInfo('0xZZZ', mockProvider);
      expect.unreachable('should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe(ERROR_CODES.INVALID_ADDRESS);
    }
  });

  it('should throw when no contract code exists at address', async () => {
    mockProvider.getCode.mockResolvedValue('0x');

    await expect(getProfileInfo(VALID_UP_ADDRESS, mockProvider)).rejects.toThrow(
      /No contract found/
    );
  });

  it('should throw with NOT_AUTHORIZED code when no contract at address', async () => {
    mockProvider.getCode.mockResolvedValue('0x');

    try {
      await getProfileInfo(VALID_UP_ADDRESS, mockProvider);
      expect.unreachable('should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe(ERROR_CODES.NOT_AUTHORIZED);
    }
  });

  it('should throw when address is not a Universal Profile (supportsInterface returns false)', async () => {
    mockProvider.getCode.mockResolvedValue('0x6080604052');
    mockContract.supportsInterface.mockResolvedValue(false);

    await expect(getProfileInfo(VALID_UP_ADDRESS, mockProvider)).rejects.toThrow(
      /not a Universal Profile/
    );
  });

  it('should throw with INVALID_ADDRESS code when not a UP', async () => {
    mockProvider.getCode.mockResolvedValue('0x6080604052');
    mockContract.supportsInterface.mockResolvedValue(false);

    try {
      await getProfileInfo(VALID_UP_ADDRESS, mockProvider);
      expect.unreachable('should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe(ERROR_CODES.INVALID_ADDRESS);
    }
  });

  it('should treat supportsInterface rejection as not a UP', async () => {
    mockProvider.getCode.mockResolvedValue('0x6080604052');
    mockContract.supportsInterface.mockRejectedValue(new Error('revert'));

    await expect(getProfileInfo(VALID_UP_ADDRESS, mockProvider)).rejects.toThrow(
      /not a Universal Profile/
    );
  });

  it('should return full profile info on success', async () => {
    const ownerAddress = '0x0000000000000000000000000000000000000042';
    const balance = 1000000000000000000n;

    mockProvider.getCode.mockResolvedValue('0x6080604052');
    mockProvider.getBalance.mockResolvedValue(balance);

    mockContract.supportsInterface.mockResolvedValue(true);
    mockContract.owner.mockResolvedValue(ownerAddress);

    // Profile metadata -- return 0x so no name/description parsed
    // Controllers array length -- return 0x (no controllers)
    // Received assets array length -- return 0x (no assets)
    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS.LSP3Profile) return '0x';
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x';
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x';
      return '0x';
    });

    const info = await getProfileInfo(VALID_UP_ADDRESS, mockProvider);

    expect(info.address).toBe(VALID_UP_ADDRESS);
    expect(info.owner).toBe(ownerAddress);
    expect(info.keyManager).toBe(ownerAddress);
    expect(info.balance).toBe(balance);
    expect(info.controllers).toEqual([]);
    expect(info.receivedAssets).toEqual({ lsp7: [], lsp8: [] });
  });

  it('should return name and description when metadata is decodable', async () => {
    const ownerAddress = '0x0000000000000000000000000000000000000042';

    mockProvider.getCode.mockResolvedValue('0x6080604052');
    mockProvider.getBalance.mockResolvedValue(0n);

    mockContract.supportsInterface.mockResolvedValue(true);
    mockContract.owner.mockResolvedValue(ownerAddress);

    // Encode a JSON profile as hex bytes
    const profileJson = JSON.stringify({
      LSP3Profile: { name: 'TestProfile', description: 'A test profile' },
    });
    const profileHex = ethers.hexlify(ethers.toUtf8Bytes(profileJson));

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS.LSP3Profile) return profileHex;
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x';
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x';
      return '0x';
    });

    const info = await getProfileInfo(VALID_UP_ADDRESS, mockProvider);

    expect(info.name).toBe('TestProfile');
    expect(info.description).toBe('A test profile');
  });

  it('should handle profile metadata with VerifiableURI prefix gracefully', async () => {
    const ownerAddress = '0x0000000000000000000000000000000000000042';

    mockProvider.getCode.mockResolvedValue('0x6080604052');
    mockProvider.getBalance.mockResolvedValue(0n);

    mockContract.supportsInterface.mockResolvedValue(true);
    mockContract.owner.mockResolvedValue(ownerAddress);

    // VerifiableURI prefix: 0x6f357c6a...
    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS.LSP3Profile)
        return '0x6f357c6a0000000000000000000000000000000000000000000000000000000000';
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x';
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x';
      return '0x';
    });

    const info = await getProfileInfo(VALID_UP_ADDRESS, mockProvider);

    // VerifiableURI is not fetched in current implementation, so name/description are undefined
    expect(info.name).toBeUndefined();
    expect(info.description).toBeUndefined();
  });

  it('should gracefully handle metadata read failure', async () => {
    const ownerAddress = '0x0000000000000000000000000000000000000042';

    mockProvider.getCode.mockResolvedValue('0x6080604052');
    mockProvider.getBalance.mockResolvedValue(0n);

    mockContract.supportsInterface.mockResolvedValue(true);
    mockContract.owner.mockResolvedValue(ownerAddress);

    let lsp3CallCount = 0;
    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS.LSP3Profile) {
        lsp3CallCount++;
        if (lsp3CallCount <= 1) throw new Error('revert');
        return '0x';
      }
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x';
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x';
      return '0x';
    });

    const info = await getProfileInfo(VALID_UP_ADDRESS, mockProvider);

    // Should not throw -- metadata error is swallowed
    expect(info.name).toBeUndefined();
    expect(info.description).toBeUndefined();
  });
});

// ==================== getControllers ====================

describe('getControllers', () => {
  it('should return an empty array when no controllers exist', async () => {
    mockContract.getData.mockResolvedValue('0x');

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);
    expect(controllers).toEqual([]);
  });

  it('should return an empty array when length data is null', async () => {
    mockContract.getData.mockResolvedValue(null);

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);
    expect(controllers).toEqual([]);
  });

  it('should parse a single controller with permissions', async () => {
    const controllerAddressRaw =
      '0x000000000000000000000000' + VALID_CONTROLLER.slice(2).toLowerCase();
    const permissionHex = PERMISSIONS.CALL;

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['AddressPermissions[]'].length) {
        return '0x01';
      }
      // Index key for element 0
      if (
        key.startsWith(DATA_KEYS['AddressPermissions[]'].index) &&
        key !== DATA_KEYS['AddressPermissions[]'].length
      ) {
        return controllerAddressRaw;
      }
      // Permissions key
      if (key.startsWith(DATA_KEYS['AddressPermissions:Permissions'])) {
        return permissionHex;
      }
      // Allowed calls / data keys
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedCalls'])) {
        return '0x';
      }
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys'])) {
        return '0x';
      }
      return '0x';
    });

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);

    expect(controllers).toHaveLength(1);
    expect(controllers[0].address).toBe(ethers.getAddress(VALID_CONTROLLER));
    expect(controllers[0].permissions).toBe(permissionHex);
    expect(controllers[0].decodedPermissions).toContain('CALL');
    expect(controllers[0].allowedCalls).toBeUndefined();
    expect(controllers[0].allowedDataKeys).toBeUndefined();
  });

  it('should include allowedCalls when present', async () => {
    const controllerAddressRaw =
      '0x000000000000000000000000' + VALID_CONTROLLER.slice(2).toLowerCase();
    const allowedCallsData = '0x0020aabbccdd11111111111111111111111111111111111111c52d6008760d9bba';

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x01';
      if (
        key.startsWith(DATA_KEYS['AddressPermissions[]'].index) &&
        key !== DATA_KEYS['AddressPermissions[]'].length
      ) {
        return controllerAddressRaw;
      }
      if (key.startsWith(DATA_KEYS['AddressPermissions:Permissions'])) return PERMISSIONS.CALL;
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedCalls'])) return allowedCallsData;
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys'])) return '0x';
      return '0x';
    });

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);

    expect(controllers[0].allowedCalls).toBe(allowedCallsData);
  });

  it('should include allowedDataKeys when present', async () => {
    const controllerAddressRaw =
      '0x000000000000000000000000' + VALID_CONTROLLER.slice(2).toLowerCase();
    const allowedDataKeysData = '0x00045ef83ad9';

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x01';
      if (
        key.startsWith(DATA_KEYS['AddressPermissions[]'].index) &&
        key !== DATA_KEYS['AddressPermissions[]'].length
      ) {
        return controllerAddressRaw;
      }
      if (key.startsWith(DATA_KEYS['AddressPermissions:Permissions'])) return PERMISSIONS.SETDATA;
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedCalls'])) return '0x';
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys']))
        return allowedDataKeysData;
      return '0x';
    });

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);

    expect(controllers[0].allowedDataKeys).toBe(allowedDataKeysData);
  });

  it('should skip entries where controller address data is 0x', async () => {
    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x02';
      // Index key -- differentiate by last portion
      if (
        key.startsWith(DATA_KEYS['AddressPermissions[]'].index) &&
        key !== DATA_KEYS['AddressPermissions[]'].length
      ) {
        const indexHex = key.slice(DATA_KEYS['AddressPermissions[]'].index.length);
        const index = parseInt(indexHex, 16);
        if (index === 0) return '0x';
        return '0x000000000000000000000000' + VALID_CONTROLLER.slice(2).toLowerCase();
      }
      if (key.startsWith(DATA_KEYS['AddressPermissions:Permissions'])) return PERMISSIONS.CALL;
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedCalls'])) return '0x';
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys'])) return '0x';
      return '0x';
    });

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);

    // Only the second valid entry should be included
    expect(controllers).toHaveLength(1);
  });

  it('should handle allowedCalls read failure gracefully', async () => {
    const controllerAddressRaw =
      '0x000000000000000000000000' + VALID_CONTROLLER.slice(2).toLowerCase();

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x01';
      if (
        key.startsWith(DATA_KEYS['AddressPermissions[]'].index) &&
        key !== DATA_KEYS['AddressPermissions[]'].length
      ) {
        return controllerAddressRaw;
      }
      if (key.startsWith(DATA_KEYS['AddressPermissions:Permissions'])) return PERMISSIONS.CALL;
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedCalls']))
        throw new Error('revert');
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys'])) return '0x';
      return '0x';
    });

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);

    expect(controllers).toHaveLength(1);
    expect(controllers[0].allowedCalls).toBeUndefined();
  });

  it('should handle allowedDataKeys read failure gracefully', async () => {
    const controllerAddressRaw =
      '0x000000000000000000000000' + VALID_CONTROLLER.slice(2).toLowerCase();

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['AddressPermissions[]'].length) return '0x01';
      if (
        key.startsWith(DATA_KEYS['AddressPermissions[]'].index) &&
        key !== DATA_KEYS['AddressPermissions[]'].length
      ) {
        return controllerAddressRaw;
      }
      if (key.startsWith(DATA_KEYS['AddressPermissions:Permissions'])) return PERMISSIONS.CALL;
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedCalls'])) return '0x';
      if (key.startsWith(DATA_KEYS['AddressPermissions:AllowedERC725YDataKeys']))
        throw new Error('revert');
      return '0x';
    });

    const controllers = await getControllers(VALID_UP_ADDRESS, mockProvider);

    expect(controllers).toHaveLength(1);
    expect(controllers[0].allowedDataKeys).toBeUndefined();
  });
});

// ==================== isController ====================

describe('isController', () => {
  it('should return true when controller has non-zero permissions', async () => {
    mockContract.getData.mockResolvedValue(PERMISSIONS.CALL);

    const result = await isController(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBe(true);
  });

  it('should return true for ALL_PERMISSIONS', async () => {
    mockContract.getData.mockResolvedValue(PERMISSIONS.ALL_PERMISSIONS);

    const result = await isController(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBe(true);
  });

  it('should return false when permissions are zero', async () => {
    mockContract.getData.mockResolvedValue(ZERO_PERMISSIONS);

    const result = await isController(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBe(false);
  });

  it('should return false when permissions are 0x', async () => {
    mockContract.getData.mockResolvedValue('0x');

    const result = await isController(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBe(false);
  });

  it('should return falsy when permissions are null', async () => {
    mockContract.getData.mockResolvedValue(null);

    const result = await isController(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBeFalsy();
  });

  it('should query the correct permission data key for the controller', async () => {
    mockContract.getData.mockResolvedValue(PERMISSIONS.CALL);

    await isController(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);

    const expectedKey =
      DATA_KEYS['AddressPermissions:Permissions'] +
      VALID_CONTROLLER.slice(2).toLowerCase();
    expect(mockContract.getData).toHaveBeenCalledWith(expectedKey);
  });
});

// ==================== getControllerPermissions ====================

describe('getControllerPermissions', () => {
  it('should return the permission hex when set', async () => {
    mockContract.getData.mockResolvedValue(PERMISSIONS.CALL);

    const result = await getControllerPermissions(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBe(PERMISSIONS.CALL);
  });

  it('should return null when permissions are 0x', async () => {
    mockContract.getData.mockResolvedValue('0x');

    const result = await getControllerPermissions(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBeNull();
  });

  it('should return null when permissions are null/undefined', async () => {
    mockContract.getData.mockResolvedValue(null);

    const result = await getControllerPermissions(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBeNull();
  });

  it('should return the full permissions value for ALL_PERMISSIONS', async () => {
    mockContract.getData.mockResolvedValue(PERMISSIONS.ALL_PERMISSIONS);

    const result = await getControllerPermissions(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);
    expect(result).toBe(PERMISSIONS.ALL_PERMISSIONS);
  });

  it('should query the correct permission data key', async () => {
    mockContract.getData.mockResolvedValue(PERMISSIONS.SETDATA);

    await getControllerPermissions(VALID_UP_ADDRESS, VALID_CONTROLLER, mockProvider);

    const expectedKey =
      DATA_KEYS['AddressPermissions:Permissions'] +
      VALID_CONTROLLER.slice(2).toLowerCase();
    expect(mockContract.getData).toHaveBeenCalledWith(expectedKey);
  });
});

// ==================== getReceivedAssets ====================

describe('getReceivedAssets', () => {
  it('should return empty arrays when no received assets exist', async () => {
    mockContract.getData.mockResolvedValue('0x');

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);
    expect(result).toEqual({ lsp7: [], lsp8: [] });
  });

  it('should return empty arrays when length data is null', async () => {
    mockContract.getData.mockResolvedValue(null);

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);
    expect(result).toEqual({ lsp7: [], lsp8: [] });
  });

  it('should classify an LSP7 asset correctly', async () => {
    const assetAddress = '0x1111111111111111111111111111111111111111';
    const assetAddressRaw = '0x000000000000000000000000' + assetAddress.slice(2);

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x01';
      return assetAddressRaw;
    });

    const assetMock = {
      ...createMockContract(),
      supportsInterface: vi.fn().mockImplementation(async (interfaceId: string) => {
        if (interfaceId === INTERFACE_IDS.LSP7DigitalAsset) return true;
        return false;
      }),
    };

    let contractCallIndex = 0;
    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      // First call: UP contract (in getReceivedAssets)
      if (contractCallIndex === 1) return mockContract;
      // Subsequent calls: asset contracts
      return assetMock;
    };

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);

    expect(result.lsp7).toContain(ethers.getAddress(assetAddress));
    expect(result.lsp8).toHaveLength(0);
  });

  it('should classify an LSP8 asset correctly', async () => {
    const assetAddress = '0x2222222222222222222222222222222222222222';
    const assetAddressRaw = '0x000000000000000000000000' + assetAddress.slice(2);

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x01';
      return assetAddressRaw;
    });

    const assetMock = {
      ...createMockContract(),
      supportsInterface: vi.fn().mockImplementation(async (interfaceId: string) => {
        if (interfaceId === INTERFACE_IDS.LSP7DigitalAsset) return false;
        if (interfaceId === INTERFACE_IDS.LSP8IdentifiableDigitalAsset) return true;
        return false;
      }),
    };

    let contractCallIndex = 0;
    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      if (contractCallIndex === 1) return mockContract;
      return assetMock;
    };

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);

    expect(result.lsp8).toContain(ethers.getAddress(assetAddress));
    expect(result.lsp7).toHaveLength(0);
  });

  it('should handle asset that is neither LSP7 nor LSP8', async () => {
    const assetAddress = '0x3333333333333333333333333333333333333333';
    const assetAddressRaw = '0x000000000000000000000000' + assetAddress.slice(2);

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x01';
      return assetAddressRaw;
    });

    const assetMock = {
      ...createMockContract(),
      supportsInterface: vi.fn().mockResolvedValue(false),
    };

    let contractCallIndex = 0;
    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      if (contractCallIndex === 1) return mockContract;
      return assetMock;
    };

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);

    expect(result.lsp7).toHaveLength(0);
    expect(result.lsp8).toHaveLength(0);
  });

  it('should handle supportsInterface failure gracefully for assets', async () => {
    const assetAddress = '0x4444444444444444444444444444444444444444';
    const assetAddressRaw = '0x000000000000000000000000' + assetAddress.slice(2);

    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x01';
      return assetAddressRaw;
    });

    const assetMock = {
      ...createMockContract(),
      supportsInterface: vi.fn().mockRejectedValue(new Error('revert')),
    };

    let contractCallIndex = 0;
    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      if (contractCallIndex === 1) return mockContract;
      return assetMock;
    };

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);

    // Both interface checks throw, so asset is not classified
    expect(result.lsp7).toHaveLength(0);
    expect(result.lsp8).toHaveLength(0);
  });

  it('should skip asset entries where data is 0x', async () => {
    mockContract.getData.mockImplementation(async (key: string) => {
      if (key === DATA_KEYS['LSP5ReceivedAssets[]'].length) return '0x01';
      // Index data is empty
      return '0x';
    });

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);

    expect(result.lsp7).toHaveLength(0);
    expect(result.lsp8).toHaveLength(0);
  });

  it('should return empty arrays when the entire read throws', async () => {
    mockContract.getData.mockRejectedValue(new Error('network error'));

    const result = await getReceivedAssets(VALID_UP_ADDRESS, mockProvider);
    expect(result).toEqual({ lsp7: [], lsp8: [] });
  });
});

// ==================== getData ====================

describe('getData', () => {
  it('should pass through the data key and return the result', async () => {
    const dataKey = DATA_KEYS.LSP3Profile;
    const dataValue = '0xdeadbeef';
    mockContract.getData.mockResolvedValue(dataValue);

    const result = await getData(VALID_UP_ADDRESS, dataKey, mockProvider);

    expect(result).toBe(dataValue);
    expect(mockContract.getData).toHaveBeenCalledWith(dataKey);
  });

  it('should return 0x when no data is set', async () => {
    mockContract.getData.mockResolvedValue('0x');

    const result = await getData(VALID_UP_ADDRESS, '0xaabbccdd', mockProvider);
    expect(result).toBe('0x');
  });

  it('should propagate errors from the contract', async () => {
    mockContract.getData.mockRejectedValue(new Error('contract error'));

    await expect(getData(VALID_UP_ADDRESS, '0xaabbccdd', mockProvider)).rejects.toThrow(
      'contract error'
    );
  });
});

// ==================== getDataBatch ====================

describe('getDataBatch', () => {
  it('should pass through multiple data keys and return results', async () => {
    const keys = [DATA_KEYS.LSP3Profile, DATA_KEYS.LSP4TokenName];
    const values = ['0xaa', '0xbb'];
    mockContract.getDataBatch.mockResolvedValue(values);

    const result = await getDataBatch(VALID_UP_ADDRESS, keys, mockProvider);

    expect(result).toEqual(values);
    expect(mockContract.getDataBatch).toHaveBeenCalledWith(keys);
  });

  it('should return empty results for empty keys', async () => {
    mockContract.getDataBatch.mockResolvedValue([]);

    const result = await getDataBatch(VALID_UP_ADDRESS, [], mockProvider);
    expect(result).toEqual([]);
  });

  it('should propagate errors from the contract', async () => {
    mockContract.getDataBatch.mockRejectedValue(new Error('batch error'));

    await expect(
      getDataBatch(VALID_UP_ADDRESS, ['0xaa'], mockProvider)
    ).rejects.toThrow('batch error');
  });
});

// ==================== getKeyManager ====================

describe('getKeyManager', () => {
  it('should return the owner address of the UP', async () => {
    mockContract.owner.mockResolvedValue(VALID_KM_ADDRESS);

    const result = await getKeyManager(VALID_UP_ADDRESS, mockProvider);
    expect(result).toBe(VALID_KM_ADDRESS);
  });

  it('should propagate errors from the contract', async () => {
    mockContract.owner.mockRejectedValue(new Error('owner error'));

    await expect(getKeyManager(VALID_UP_ADDRESS, mockProvider)).rejects.toThrow('owner error');
  });
});

// ==================== verifyKeyManager ====================

describe('verifyKeyManager', () => {
  it('should return true when owner matches and target matches', async () => {
    let contractCallIndex = 0;

    const upMock = {
      ...createMockContract(),
      owner: vi.fn().mockResolvedValue(VALID_KM_ADDRESS),
    };

    const kmTargetFn = vi.fn().mockResolvedValue(VALID_UP_ADDRESS);
    const kmMock = {
      ...createMockContract(),
      getFunction: vi.fn().mockReturnValue(kmTargetFn),
    };

    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      if (contractCallIndex === 1) return upMock;
      return kmMock;
    };

    const result = await verifyKeyManager(VALID_UP_ADDRESS, VALID_KM_ADDRESS, mockProvider);
    expect(result).toBe(true);
  });

  it('should return false when owner does not match key manager address', async () => {
    const differentOwner = '0x9999999999999999999999999999999999999999';

    const upMock = {
      ...createMockContract(),
      owner: vi.fn().mockResolvedValue(differentOwner),
    };

    contractFactory = () => upMock;

    const result = await verifyKeyManager(VALID_UP_ADDRESS, VALID_KM_ADDRESS, mockProvider);
    expect(result).toBe(false);
  });

  it('should return false when target does not match UP address', async () => {
    const differentTarget = '0x8888888888888888888888888888888888888888';

    let contractCallIndex = 0;

    const upMock = {
      ...createMockContract(),
      owner: vi.fn().mockResolvedValue(VALID_KM_ADDRESS),
    };

    const kmTargetFn = vi.fn().mockResolvedValue(differentTarget);
    const kmMock = {
      ...createMockContract(),
      getFunction: vi.fn().mockReturnValue(kmTargetFn),
    };

    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      if (contractCallIndex === 1) return upMock;
      return kmMock;
    };

    const result = await verifyKeyManager(VALID_UP_ADDRESS, VALID_KM_ADDRESS, mockProvider);
    expect(result).toBe(false);
  });

  it('should be case-insensitive for address comparison', async () => {
    const lowerUp = VALID_UP_ADDRESS.toLowerCase();
    const upperKm = VALID_KM_ADDRESS.toUpperCase();

    let contractCallIndex = 0;

    const upMock = {
      ...createMockContract(),
      owner: vi.fn().mockResolvedValue(upperKm),
    };

    const kmTargetFn = vi.fn().mockResolvedValue(lowerUp);
    const kmMock = {
      ...createMockContract(),
      getFunction: vi.fn().mockReturnValue(kmTargetFn),
    };

    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      if (contractCallIndex === 1) return upMock;
      return kmMock;
    };

    // Even though casing differs, the comparison should pass
    const result = await verifyKeyManager(lowerUp, upperKm, mockProvider);
    expect(result).toBe(true);
  });

  it('should call getFunction with "target"', async () => {
    let contractCallIndex = 0;

    const upMock = {
      ...createMockContract(),
      owner: vi.fn().mockResolvedValue(VALID_KM_ADDRESS),
    };

    const kmTargetFn = vi.fn().mockResolvedValue(VALID_UP_ADDRESS);
    const kmMock = {
      ...createMockContract(),
      getFunction: vi.fn().mockReturnValue(kmTargetFn),
    };

    contractFactory = (...args: any[]) => {
      contractCallIndex++;
      if (contractCallIndex === 1) return upMock;
      return kmMock;
    };

    await verifyKeyManager(VALID_UP_ADDRESS, VALID_KM_ADDRESS, mockProvider);

    expect(kmMock.getFunction).toHaveBeenCalledWith('target');
  });
});
