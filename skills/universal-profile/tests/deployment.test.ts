import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ethers } from 'ethers';

// vi.hoisted runs before vi.mock hoisting, so the variable is available
// to the mock factory even after hoisting reorders the calls.
const { mockContractConstructor } = vi.hoisted(() => ({
  mockContractConstructor: vi.fn(),
}));

vi.mock('ethers', async () => {
  const actual = await vi.importActual<typeof import('ethers')>('ethers');
  return {
    ...actual,
    Contract: mockContractConstructor,
  };
});

import {
  generateSalt,
  preparePostDeploymentData,
  prepareDeploymentParams,
  isDeployed,
  verifyDeployment,
  computeDeploymentAddresses,
  deployUniversalProfile,
} from '../../src/lib/deployment.js';

import {
  NETWORKS,
  DATA_KEYS,
  PERMISSIONS,
} from '../../src/utils/constants.js';

import type { DeploymentConfig } from '../../src/types/index.js';
import { UniversalProfileError } from '../../src/types/index.js';

// ==================== Test Fixtures ====================

const CONTROLLER_ADDRESS = '0x1234567890AbCdEf1234567890aBcDeF12345678';
const RECOVERY_ADDRESS = '0xDeadBeef00000000000000000000000000000001';
const FAKE_UP_ADDRESS = '0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
const FAKE_KM_ADDRESS = '0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB';
const MAINNET_CONFIG = NETWORKS['lukso-mainnet'];

function makeDeploymentConfig(overrides?: Partial<DeploymentConfig>): DeploymentConfig {
  return {
    salt: 'test-salt-value',
    fundingAmount: 0n,
    controllerKey: CONTROLLER_ADDRESS,
    network: 'lukso-mainnet',
    ...overrides,
  };
}

// ==================== generateSalt ====================

describe('generateSalt', () => {
  it('should use "clawdbot" as the default prefix', () => {
    const salt = generateSalt();
    expect(salt.startsWith('clawdbot-')).toBe(true);
  });

  it('should use a custom prefix when provided', () => {
    const salt = generateSalt('myprefix');
    expect(salt.startsWith('myprefix-')).toBe(true);
  });

  it('should match the pattern {prefix}-{timestamp}-{random}', () => {
    const salt = generateSalt();
    expect(salt).toMatch(/^clawdbot-\d+-[a-z0-9]+$/);
  });

  it('should match the pattern {customprefix}-{timestamp}-{random}', () => {
    const salt = generateSalt('custom');
    expect(salt).toMatch(/^custom-\d+-[a-z0-9]+$/);
  });

  it('should generate unique salts on successive calls', () => {
    const salt1 = generateSalt();
    const salt2 = generateSalt();
    expect(salt1).not.toBe(salt2);
  });

  it('should include a timestamp portion that is a valid number', () => {
    const salt = generateSalt();
    const parts = salt.split('-');
    const timestamp = Number(parts[1]);
    expect(Number.isFinite(timestamp)).toBe(true);
    expect(timestamp).toBeGreaterThan(0);
  });

  it('should have a random portion that is non-empty', () => {
    const salt = generateSalt();
    const parts = salt.split('-');
    expect(parts[2].length).toBeGreaterThan(0);
  });
});

// ==================== preparePostDeploymentData ====================

describe('preparePostDeploymentData', () => {
  it('should return a non-empty hex string starting with 0x', () => {
    const data = preparePostDeploymentData(CONTROLLER_ADDRESS);
    expect(data).toMatch(/^0x[0-9a-fA-F]+$/);
    expect(data.length).toBeGreaterThan(2);
  });

  describe('without recovery address', () => {
    it('should encode data that decodes to 3 keys and 3 values', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataKeys: string[] = decoded[0];
      const dataValues: string[] = decoded[1];

      // Without recovery: AddressPermissions[].length, AddressPermissions[0], Permissions:<controller>
      expect(dataKeys).toHaveLength(3);
      expect(dataValues).toHaveLength(3);
    });

    it('should set AddressPermissions[].length to 1', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataKeys: string[] = decoded[0];
      const dataValues: string[] = decoded[1];

      // First key is AddressPermissions[].length
      expect(dataKeys[0]).toBe(DATA_KEYS['AddressPermissions[]'].length);

      // Value should encode 1
      const countValue = dataValues[0];
      expect(BigInt(countValue)).toBe(1n);
    });

    it('should store the controller address at index 0', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataValues: string[] = decoded[1];

      // Second value is the controller address
      expect(dataValues[1].toLowerCase()).toBe(CONTROLLER_ADDRESS.toLowerCase());
    });

    it('should set ALL_PERMISSIONS for the controller', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataKeys: string[] = decoded[0];
      const dataValues: string[] = decoded[1];

      const expectedPermKey =
        DATA_KEYS['AddressPermissions:Permissions'] +
        CONTROLLER_ADDRESS.slice(2).toLowerCase();
      expect(dataKeys[2]).toBe(expectedPermKey);
      expect(dataValues[2]).toBe(PERMISSIONS.ALL_PERMISSIONS);
    });
  });

  describe('with recovery address', () => {
    it('should encode data that decodes to 5 keys and 5 values', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS, RECOVERY_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataKeys: string[] = decoded[0];
      const dataValues: string[] = decoded[1];

      expect(dataKeys).toHaveLength(5);
      expect(dataValues).toHaveLength(5);
    });

    it('should set AddressPermissions[].length to 2', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS, RECOVERY_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataValues: string[] = decoded[1];

      expect(BigInt(dataValues[0])).toBe(2n);
    });

    it('should store the recovery address at index 1', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS, RECOVERY_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataValues: string[] = decoded[1];

      // Index 3: length(0), controller-addr(1), controller-perm(2), recovery-addr(3)
      expect(dataValues[3].toLowerCase()).toBe(RECOVERY_ADDRESS.toLowerCase());
    });

    it('should set recovery permissions to CHANGEOWNER | ADDCONTROLLER | EDITPERMISSIONS', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS, RECOVERY_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataKeys: string[] = decoded[0];
      const dataValues: string[] = decoded[1];

      const expectedRecoveryPermKey =
        DATA_KEYS['AddressPermissions:Permissions'] +
        RECOVERY_ADDRESS.slice(2).toLowerCase();
      expect(dataKeys[4]).toBe(expectedRecoveryPermKey);

      const expectedRecovery =
        BigInt(PERMISSIONS.CHANGEOWNER) |
        BigInt(PERMISSIONS.ADDCONTROLLER) |
        BigInt(PERMISSIONS.EDITPERMISSIONS);
      expect(BigInt(dataValues[4])).toBe(expectedRecovery);
    });

    it('should still have ALL_PERMISSIONS for the primary controller', () => {
      const data = preparePostDeploymentData(CONTROLLER_ADDRESS, RECOVERY_ADDRESS);
      const decoded = ethers.AbiCoder.defaultAbiCoder().decode(
        ['bytes32[]', 'bytes[]'],
        data
      );
      const dataValues: string[] = decoded[1];

      expect(dataValues[2]).toBe(PERMISSIONS.ALL_PERMISSIONS);
    });
  });
});

// ==================== prepareDeploymentParams ====================

describe('prepareDeploymentParams', () => {
  it('should return an object with primaryContractDeploymentInit and secondaryContractDeploymentInit', () => {
    const config = makeDeploymentConfig();
    const result = prepareDeploymentParams(config, MAINNET_CONFIG);

    expect(result).toHaveProperty('primaryContractDeploymentInit');
    expect(result).toHaveProperty('secondaryContractDeploymentInit');
  });

  describe('primaryContractDeploymentInit', () => {
    it('should have a salt that is a keccak256 hash (bytes32 hex)', () => {
      const config = makeDeploymentConfig();
      const { primaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(primaryContractDeploymentInit.salt).toMatch(/^0x[0-9a-f]{64}$/);
    });

    it('should derive salt from config.salt via keccak256', () => {
      const config = makeDeploymentConfig({ salt: 'deterministic-salt' });
      const { primaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      const expectedSalt = ethers.keccak256(ethers.toUtf8Bytes('deterministic-salt'));
      expect(primaryContractDeploymentInit.salt).toBe(expectedSalt);
    });

    it('should use the correct UP implementation address from network config', () => {
      const config = makeDeploymentConfig();
      const { primaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(primaryContractDeploymentInit.implementationContract).toBe(
        MAINNET_CONFIG.contracts.UP_IMPLEMENTATION
      );
    });

    it('should set fundingAmount from config', () => {
      const config = makeDeploymentConfig({ fundingAmount: 1000n });
      const { primaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(primaryContractDeploymentInit.fundingAmount).toBe(1000n);
    });

    it('should have initializationCalldata that encodes initialize(address(0))', () => {
      const config = makeDeploymentConfig();
      const { primaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      const iface = new ethers.Interface(['function initialize(address initialOwner)']);
      const expectedCalldata = iface.encodeFunctionData('initialize', [ethers.ZeroAddress]);

      expect(primaryContractDeploymentInit.initializationCalldata).toBe(expectedCalldata);
    });
  });

  describe('secondaryContractDeploymentInit', () => {
    it('should use the correct Key Manager implementation address', () => {
      const config = makeDeploymentConfig();
      const { secondaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(secondaryContractDeploymentInit.implementationContract).toBe(
        MAINNET_CONFIG.contracts.KEY_MANAGER_IMPLEMENTATION
      );
    });

    it('should have fundingAmount of 0n', () => {
      const config = makeDeploymentConfig();
      const { secondaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(secondaryContractDeploymentInit.fundingAmount).toBe(0n);
    });

    it('should have addPrimaryContractAddress set to true', () => {
      const config = makeDeploymentConfig();
      const { secondaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(secondaryContractDeploymentInit.addPrimaryContractAddress).toBe(true);
    });

    it('should have initializationCalldata as the initialize(address) selector', () => {
      const config = makeDeploymentConfig();
      const { secondaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(secondaryContractDeploymentInit.initializationCalldata).toBe('0xc4d66de8');
    });

    it('should have extraInitializationParams as 0x', () => {
      const config = makeDeploymentConfig();
      const { secondaryContractDeploymentInit } = prepareDeploymentParams(config, MAINNET_CONFIG);

      expect(secondaryContractDeploymentInit.extraInitializationParams).toBe('0x');
    });
  });

  it('should produce deterministic results for the same input', () => {
    const config = makeDeploymentConfig();
    const result1 = prepareDeploymentParams(config, MAINNET_CONFIG);
    const result2 = prepareDeploymentParams(config, MAINNET_CONFIG);

    expect(result1.primaryContractDeploymentInit.salt).toBe(
      result2.primaryContractDeploymentInit.salt
    );
    expect(result1.primaryContractDeploymentInit.initializationCalldata).toBe(
      result2.primaryContractDeploymentInit.initializationCalldata
    );
  });
});

// ==================== isDeployed ====================

describe('isDeployed', () => {
  it('should return false when provider.getCode returns "0x"', async () => {
    const mockProvider = {
      getCode: vi.fn().mockResolvedValue('0x'),
    } as any;

    const result = await isDeployed(FAKE_UP_ADDRESS, mockProvider);
    expect(result).toBe(false);
    expect(mockProvider.getCode).toHaveBeenCalledWith(FAKE_UP_ADDRESS);
  });

  it('should return true when provider.getCode returns actual bytecode', async () => {
    const mockProvider = {
      getCode: vi.fn().mockResolvedValue('0x6080604052'),
    } as any;

    const result = await isDeployed(FAKE_UP_ADDRESS, mockProvider);
    expect(result).toBe(true);
  });

  it('should pass the address argument to provider.getCode', async () => {
    const mockProvider = {
      getCode: vi.fn().mockResolvedValue('0x'),
    } as any;

    await isDeployed('0x0000000000000000000000000000000000000042', mockProvider);
    expect(mockProvider.getCode).toHaveBeenCalledWith(
      '0x0000000000000000000000000000000000000042'
    );
  });
});

// ==================== verifyDeployment ====================

describe('verifyDeployment', () => {
  let mockUpInstance: any;
  let mockKmInstance: any;

  function makeMockProvider({
    upCode = '0x6080604052',
    kmCode = '0x6080604052',
  }: {
    upCode?: string;
    kmCode?: string;
  } = {}) {
    return {
      getCode: vi.fn().mockImplementation((address: string) => {
        if (address === FAKE_UP_ADDRESS) return Promise.resolve(upCode);
        if (address === FAKE_KM_ADDRESS) return Promise.resolve(kmCode);
        return Promise.resolve('0x');
      }),
    };
  }

  beforeEach(() => {
    mockUpInstance = {
      owner: vi.fn().mockResolvedValue(FAKE_KM_ADDRESS),
      getData: vi.fn().mockResolvedValue(PERMISSIONS.ALL_PERMISSIONS),
    };

    mockKmInstance = {
      getFunction: vi.fn().mockReturnValue(
        vi.fn().mockResolvedValue(FAKE_UP_ADDRESS)
      ),
    };

    mockContractConstructor.mockReset();
    mockContractConstructor.mockImplementation(
      (address: string) => {
        if (address === FAKE_UP_ADDRESS) return mockUpInstance;
        if (address === FAKE_KM_ADDRESS) return mockKmInstance;
        return {};
      }
    );
  });

  it('should return true when all checks pass', async () => {
    const provider = makeMockProvider();

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(true);
  });

  it('should return false when UP has no code', async () => {
    const provider = makeMockProvider({ upCode: '0x' });

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(false);
  });

  it('should return false when Key Manager has no code', async () => {
    const provider = makeMockProvider({ kmCode: '0x' });

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(false);
  });

  it('should return false when UP owner is not the Key Manager', async () => {
    const provider = makeMockProvider();
    mockUpInstance.owner = vi.fn().mockResolvedValue(
      '0x0000000000000000000000000000000000000099'
    );

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(false);
  });

  it('should return false when Key Manager target is not the UP', async () => {
    const provider = makeMockProvider();
    mockKmInstance.getFunction = vi.fn().mockReturnValue(
      vi.fn().mockResolvedValue('0x0000000000000000000000000000000000000099')
    );

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(false);
  });

  it('should return false when controller has no permissions (returns 0x)', async () => {
    const provider = makeMockProvider();
    mockUpInstance.getData = vi.fn().mockResolvedValue('0x');

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(false);
  });

  it('should return false when controller permissions are null', async () => {
    const provider = makeMockProvider();
    mockUpInstance.getData = vi.fn().mockResolvedValue(null);

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(false);
  });

  it('should query UP.getData with the correct permission key for the expected controller', async () => {
    const provider = makeMockProvider();

    await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    const expectedKey =
      DATA_KEYS['AddressPermissions:Permissions'] +
      CONTROLLER_ADDRESS.slice(2).toLowerCase();
    expect(mockUpInstance.getData).toHaveBeenCalledWith(expectedKey);
  });

  it('should compare owner and target case-insensitively', async () => {
    const provider = makeMockProvider();
    // Return addresses in lowercase while FAKE_ constants are uppercase
    mockUpInstance.owner = vi.fn().mockResolvedValue(FAKE_KM_ADDRESS.toLowerCase());
    mockKmInstance.getFunction = vi.fn().mockReturnValue(
      vi.fn().mockResolvedValue(FAKE_UP_ADDRESS.toLowerCase())
    );

    const result = await verifyDeployment(
      FAKE_UP_ADDRESS,
      FAKE_KM_ADDRESS,
      CONTROLLER_ADDRESS,
      provider as any
    );

    expect(result).toBe(true);
  });
});

// ==================== computeDeploymentAddresses ====================

describe('computeDeploymentAddresses', () => {
  beforeEach(() => {
    mockContractConstructor.mockReset();
  });

  it('should throw UniversalProfileError for unknown network', async () => {
    const config = makeDeploymentConfig({ network: 'unknown-network' });
    const mockProvider = {} as any;

    await expect(
      computeDeploymentAddresses(config, mockProvider)
    ).rejects.toThrow(UniversalProfileError);

    await expect(
      computeDeploymentAddresses(config, mockProvider)
    ).rejects.toThrow('Unknown network: unknown-network');
  });

  it('should return upAddress and keyManagerAddress from factory.computeERC1167Addresses', async () => {
    const mockComputeERC1167Addresses = vi
      .fn()
      .mockResolvedValue([FAKE_UP_ADDRESS, FAKE_KM_ADDRESS]);

    mockContractConstructor.mockImplementation(() => ({
      computeERC1167Addresses: mockComputeERC1167Addresses,
    }));

    const config = makeDeploymentConfig();
    const mockProvider = {} as any;

    const result = await computeDeploymentAddresses(config, mockProvider);

    expect(result.upAddress).toBe(FAKE_UP_ADDRESS);
    expect(result.keyManagerAddress).toBe(FAKE_KM_ADDRESS);
  });

  it('should create the Contract with the correct factory address and provider', async () => {
    const mockComputeERC1167Addresses = vi
      .fn()
      .mockResolvedValue([FAKE_UP_ADDRESS, FAKE_KM_ADDRESS]);

    mockContractConstructor.mockImplementation(() => ({
      computeERC1167Addresses: mockComputeERC1167Addresses,
    }));

    const config = makeDeploymentConfig();
    const mockProvider = { _isMockProvider: true } as any;

    await computeDeploymentAddresses(config, mockProvider);

    expect(mockContractConstructor).toHaveBeenCalledWith(
      MAINNET_CONFIG.contracts.LSP23_LINKED_CONTRACTS_FACTORY,
      expect.anything(),
      mockProvider
    );
  });

  it('should pass the post deployment module address to computeERC1167Addresses', async () => {
    const mockComputeERC1167Addresses = vi
      .fn()
      .mockResolvedValue([FAKE_UP_ADDRESS, FAKE_KM_ADDRESS]);

    mockContractConstructor.mockImplementation(() => ({
      computeERC1167Addresses: mockComputeERC1167Addresses,
    }));

    const config = makeDeploymentConfig();
    const mockProvider = {} as any;

    await computeDeploymentAddresses(config, mockProvider);

    expect(mockComputeERC1167Addresses).toHaveBeenCalledWith(
      expect.anything(),
      expect.anything(),
      MAINNET_CONFIG.contracts.UP_POST_DEPLOYMENT_MODULE,
      expect.any(String)
    );
  });

  it('should propagate errors from the factory contract call', async () => {
    mockContractConstructor.mockImplementation(() => ({
      computeERC1167Addresses: vi.fn().mockRejectedValue(new Error('RPC failed')),
    }));

    const config = makeDeploymentConfig();
    const mockProvider = {} as any;

    await expect(
      computeDeploymentAddresses(config, mockProvider)
    ).rejects.toThrow('RPC failed');
  });

  it('should work with lukso-testnet network as well', async () => {
    const mockComputeERC1167Addresses = vi
      .fn()
      .mockResolvedValue([FAKE_UP_ADDRESS, FAKE_KM_ADDRESS]);

    mockContractConstructor.mockImplementation(() => ({
      computeERC1167Addresses: mockComputeERC1167Addresses,
    }));

    const config = makeDeploymentConfig({ network: 'lukso-testnet' });
    const mockProvider = {} as any;

    const result = await computeDeploymentAddresses(config, mockProvider);

    expect(result.upAddress).toBe(FAKE_UP_ADDRESS);
    expect(result.keyManagerAddress).toBe(FAKE_KM_ADDRESS);
    expect(mockContractConstructor).toHaveBeenCalledWith(
      NETWORKS['lukso-testnet'].contracts.LSP23_LINKED_CONTRACTS_FACTORY,
      expect.anything(),
      mockProvider
    );
  });
});

// ==================== deployUniversalProfile ====================

describe('deployUniversalProfile', () => {
  const FAKE_TX_HASH = '0x' + 'ab'.repeat(32);
  const FAKE_BLOCK_NUMBER = 42;

  beforeEach(() => {
    mockContractConstructor.mockReset();
  });

  function makeMockSigner(getCodeReturn: string = '0x') {
    return {
      provider: {
        getCode: vi.fn().mockResolvedValue(getCodeReturn),
      },
    } as any;
  }

  function makeMockFactory({
    computeResult = [FAKE_UP_ADDRESS, FAKE_KM_ADDRESS] as [string, string],
    deployResult,
    receiptResult,
  }: {
    computeResult?: [string, string];
    deployResult?: any;
    receiptResult?: any;
  } = {}) {
    const receipt = receiptResult ?? {
      status: 1,
      hash: FAKE_TX_HASH,
      blockNumber: FAKE_BLOCK_NUMBER,
    };

    const tx = deployResult ?? {
      hash: FAKE_TX_HASH,
      wait: vi.fn().mockResolvedValue(receipt),
    };

    return {
      computeERC1167Addresses: vi.fn().mockResolvedValue(computeResult),
      deployERC1167Proxies: vi.fn().mockResolvedValue(tx),
    };
  }

  it('should throw UniversalProfileError for unknown network', async () => {
    const config = makeDeploymentConfig({ network: 'no-such-network' });
    const signer = makeMockSigner();

    await expect(
      deployUniversalProfile(signer, config)
    ).rejects.toThrow(UniversalProfileError);

    await expect(
      deployUniversalProfile(signer, config)
    ).rejects.toThrow('Unknown network: no-such-network');
  });

  it('should throw when UP is already deployed at predicted address', async () => {
    const factory = makeMockFactory();
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x6080604052');

    await expect(
      deployUniversalProfile(signer, config)
    ).rejects.toThrow('Universal Profile already deployed at this address');
  });

  it('should return a DeploymentResult on successful deployment', async () => {
    const factory = makeMockFactory();
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x');

    const result = await deployUniversalProfile(signer, config);

    expect(result).toEqual({
      upAddress: FAKE_UP_ADDRESS,
      keyManagerAddress: FAKE_KM_ADDRESS,
      transactionHash: FAKE_TX_HASH,
      blockNumber: FAKE_BLOCK_NUMBER,
    });
  });

  it('should call deployERC1167Proxies with the correct value option', async () => {
    const factory = makeMockFactory();
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig({ fundingAmount: 5000n });
    const signer = makeMockSigner('0x');

    await deployUniversalProfile(signer, config);

    expect(factory.deployERC1167Proxies).toHaveBeenCalledWith(
      expect.anything(),
      expect.anything(),
      MAINNET_CONFIG.contracts.UP_POST_DEPLOYMENT_MODULE,
      expect.any(String),
      { value: 5000n }
    );
  });

  it('should throw when the transaction receipt is null', async () => {
    const tx = {
      hash: FAKE_TX_HASH,
      wait: vi.fn().mockResolvedValue(null),
    };
    const factory = {
      computeERC1167Addresses: vi.fn().mockResolvedValue([FAKE_UP_ADDRESS, FAKE_KM_ADDRESS]),
      deployERC1167Proxies: vi.fn().mockResolvedValue(tx),
    };
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x');

    await expect(
      deployUniversalProfile(signer, config)
    ).rejects.toThrow('Deployment transaction failed');
  });

  it('should throw when the transaction receipt status is not 1', async () => {
    const receipt = {
      status: 0,
      hash: FAKE_TX_HASH,
      blockNumber: FAKE_BLOCK_NUMBER,
    };
    const tx = {
      hash: FAKE_TX_HASH,
      wait: vi.fn().mockResolvedValue(receipt),
    };
    const factory = {
      computeERC1167Addresses: vi.fn().mockResolvedValue([FAKE_UP_ADDRESS, FAKE_KM_ADDRESS]),
      deployERC1167Proxies: vi.fn().mockResolvedValue(tx),
    };
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x');

    await expect(
      deployUniversalProfile(signer, config)
    ).rejects.toThrow('Deployment transaction failed');
  });

  it('should create the factory Contract with the signer (not just provider)', async () => {
    const factory = makeMockFactory();
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x');

    await deployUniversalProfile(signer, config);

    expect(mockContractConstructor).toHaveBeenCalledWith(
      MAINNET_CONFIG.contracts.LSP23_LINKED_CONTRACTS_FACTORY,
      expect.anything(),
      signer
    );
  });

  it('should compute addresses before deploying', async () => {
    const factory = makeMockFactory();
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x');

    await deployUniversalProfile(signer, config);

    const computeOrder = factory.computeERC1167Addresses.mock.invocationCallOrder[0];
    const deployOrder = factory.deployERC1167Proxies.mock.invocationCallOrder[0];
    expect(computeOrder).toBeLessThan(deployOrder);
  });

  it('should check signer.provider.getCode to detect already-deployed UP', async () => {
    const factory = makeMockFactory();
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x');

    await deployUniversalProfile(signer, config);

    expect(signer.provider.getCode).toHaveBeenCalledWith(FAKE_UP_ADDRESS);
  });

  it('should propagate errors from deployERC1167Proxies', async () => {
    const factory = {
      computeERC1167Addresses: vi.fn().mockResolvedValue([FAKE_UP_ADDRESS, FAKE_KM_ADDRESS]),
      deployERC1167Proxies: vi.fn().mockRejectedValue(new Error('Insufficient funds')),
    };
    mockContractConstructor.mockImplementation(() => factory);

    const config = makeDeploymentConfig();
    const signer = makeMockSigner('0x');

    await expect(
      deployUniversalProfile(signer, config)
    ).rejects.toThrow('Insufficient funds');
  });
});
