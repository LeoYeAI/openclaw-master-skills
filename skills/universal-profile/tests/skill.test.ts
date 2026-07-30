import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
  UniversalProfileError,
  ERROR_CODES,
} from '../../src/types/index.js';

// ==================== HOISTED MOCKS ====================

const {
  // ethers
  mockProviderInstance,
  MockJsonRpcProvider,
  mockWalletInstance,
  MockWallet,
  // crypto
  mockGenerateKeyPair,
  mockEncryptKey,
  mockDecryptKey,
  mockLoadKeystore,
  mockSaveKey,
  mockListStoredKeys,
  // permissions
  mockDecodePermissions,
  mockValidatePermissions,
  mockGetPresetConfig,
  // deployment
  mockDeployUniversalProfile,
  mockComputeDeploymentAddresses,
  mockGenerateSalt,
  // relay
  mockExecuteViaRelay,
  // profile
  mockGetProfileInfo,
  // tokens
  mockGetLSP7Info,
  mockGetLSP8Info,
  mockEncodeLSP7Transfer,
  mockEncodeLSP8Transfer,
  mockEncodeLSP7AuthorizeOperator,
  // dex
  mockGetQuoteWithSlippage,
  mockEncodeSwapExactTokensForTokens,
  mockGetDeadline,
  // marketplace
  mockGetListing,
  mockGetCollectionListings,
  mockEncodeBuyListing,
  mockGetListingOperations,
  // config
  mockLoadConfig,
  mockUpdateConfig,
  mockGetNetworkConfig,
  mockGetRpcUrl,
  mockGetRelayerUrl,
  mockHasUPConfig,
  mockHasControllerKey,
  mockSetUPConfig,
  mockSetControllerKeyConfig,
  mockResolveTokenAddress,
  // default config
  DEFAULT_TEST_CONFIG,
} = vi.hoisted(() => {
  const mockProviderInstance = { getNetwork: vi.fn() };
  const MockJsonRpcProvider = vi.fn(() => mockProviderInstance);
  const mockWalletInstance = {
    address: '0xControllerAddress1234567890abcdef12345678',
    provider: mockProviderInstance,
  };
  const MockWallet = vi.fn(() => mockWalletInstance);

  const DEFAULT_TEST_CONFIG = {
    version: '1.0.0',
    network: 'lukso',
    rpc: { lukso: 'https://rpc.lukso.network' },
    universalProfile: {
      address: '0xUPAddress1234567890abcdef1234567890abcdef',
      keyManager: '0xKMAddress1234567890abcdef1234567890abcdef',
    },
    controllerKey: {
      address: '0xCtrlAddr',
      label: 'default',
      encrypted: true,
      path: '/path/to/key.enc',
    },
    contracts: {},
    defaults: {
      slippage: 0.5,
      transactionDeadline: 1200,
      gasLimit: 'auto',
      confirmations: 1,
    },
    relay: {
      enabled: true,
      url: 'https://relay.test',
      fallbackToDirect: true,
    },
    ui: {
      authorizationUrl: 'https://up-auth.clawdbot.dev',
    },
    tokens: {
      known: {},
    },
  };

  return {
    mockProviderInstance,
    MockJsonRpcProvider,
    mockWalletInstance,
    MockWallet,

    mockGenerateKeyPair: vi.fn().mockReturnValue({
      privateKey: '0xabc123',
      publicKey: '0xpub456',
      address: '0xAddr789',
    }),
    mockEncryptKey: vi.fn().mockReturnValue({
      address: '0xAddr789',
      label: '',
      encryptedKey: 'enc',
      iv: 'iv',
      salt: 'salt',
      algorithm: 'aes-256-gcm',
      createdAt: '2025-01-01T00:00:00.000Z',
    }),
    mockDecryptKey: vi.fn().mockReturnValue('0xdecryptedPrivateKey'),
    mockLoadKeystore: vi.fn().mockReturnValue({
      address: '0xAddr789',
      label: 'test-key',
      encryptedKey: 'enc',
      iv: 'iv',
      salt: 'salt',
      algorithm: 'aes-256-gcm',
      createdAt: '2025-01-01T00:00:00.000Z',
    }),
    mockSaveKey: vi.fn().mockReturnValue('/path/to/key.enc'),
    mockListStoredKeys: vi.fn().mockReturnValue([]),

    mockDecodePermissions: vi.fn().mockReturnValue(['CALL', 'SETDATA']),
    mockValidatePermissions: vi.fn().mockReturnValue({
      valid: true,
      warnings: [],
      risks: [],
    }),
    mockGetPresetConfig: vi.fn().mockReturnValue({
      name: 'DeFi Trader',
      description: 'Trade tokens and interact with DeFi protocols',
      permissions: '0x0000000000000000000000000000000000000000000000000000000000040840',
      riskLevel: 'medium',
    }),

    mockDeployUniversalProfile: vi.fn().mockResolvedValue({
      upAddress: '0xUPAddress',
      keyManagerAddress: '0xKMAddress',
      transactionHash: '0xtxhash',
      blockNumber: 100,
    }),
    mockComputeDeploymentAddresses: vi.fn().mockResolvedValue({
      upAddress: '0xComputedUP',
      keyManagerAddress: '0xComputedKM',
    }),
    mockGenerateSalt: vi.fn().mockReturnValue('0xsalt'),

    mockExecuteViaRelay: vi.fn().mockResolvedValue({
      transactionHash: '0xrelayTxHash',
      success: true,
    }),

    mockGetProfileInfo: vi.fn().mockResolvedValue({
      address: '0xUPAddress',
      name: 'Test Profile',
      keyManager: '0xKMAddress',
      owner: '0xOwner',
      balance: 1000n,
      controllers: [],
      receivedAssets: { lsp7: [], lsp8: [] },
    }),

    mockGetLSP7Info: vi.fn().mockResolvedValue({
      address: '0xToken',
      name: 'Test Token',
      symbol: 'TST',
      decimals: 18,
      totalSupply: 1000000n,
      owner: '0xOwner',
      isNonDivisible: false,
    }),
    mockGetLSP8Info: vi.fn().mockResolvedValue({
      address: '0xCollection',
      name: 'Test Collection',
      symbol: 'TNFT',
      totalSupply: 100n,
      owner: '0xOwner',
      tokenIdFormat: 0,
    }),
    mockEncodeLSP7Transfer: vi.fn().mockReturnValue({
      operationType: 0,
      target: '0xToken',
      value: 0n,
      data: '0xlsp7data',
    }),
    mockEncodeLSP8Transfer: vi.fn().mockReturnValue({
      operationType: 0,
      target: '0xCollection',
      value: 0n,
      data: '0xlsp8data',
    }),
    mockEncodeLSP7AuthorizeOperator: vi.fn().mockReturnValue({
      operationType: 0,
      target: '0xToken',
      value: 0n,
      data: '0xauthorizedata',
    }),

    mockGetQuoteWithSlippage: vi.fn().mockResolvedValue({
      quote: {
        amountIn: 100n,
        amountOut: 95n,
        priceImpact: 0.5,
        path: ['0xTokenIn', '0xTokenOut'],
        executionPrice: 0.95,
      },
      minAmountOut: 90n,
    }),
    mockEncodeSwapExactTokensForTokens: vi.fn().mockReturnValue({
      operationType: 0,
      target: '0xRouter',
      value: 0n,
      data: '0xswapdata',
    }),
    mockGetDeadline: vi.fn().mockReturnValue(9999999999),

    mockGetListing: vi.fn().mockResolvedValue({
      listingId: 1n,
      seller: '0xSeller',
      nftContract: '0xCollection',
      tokenId: '0x01',
      price: 500n,
      startTime: 1000,
      endTime: 2000,
      isActive: true,
    }),
    mockGetCollectionListings: vi.fn().mockResolvedValue([]),
    mockEncodeBuyListing: vi.fn().mockReturnValue({
      operationType: 0,
      target: '0xMarketplace',
      value: 500n,
      data: '0xbuydata',
    }),
    mockGetListingOperations: vi.fn().mockReturnValue([
      { operationType: 0, target: '0xCollection', value: 0n, data: '0xapprove' },
      { operationType: 0, target: '0xMarketplace', value: 0n, data: '0xlist' },
    ]),

    mockLoadConfig: vi.fn().mockReturnValue({
      version: '1.0.0',
      network: 'lukso',
      rpc: { lukso: 'https://rpc.lukso.network' },
      universalProfile: {
        address: '0xUPAddress1234567890abcdef1234567890abcdef',
        keyManager: '0xKMAddress1234567890abcdef1234567890abcdef',
      },
      controllerKey: {
        address: '0xCtrlAddr',
        label: 'default',
        encrypted: true,
        path: '/path/to/key.enc',
      },
      contracts: {},
      defaults: {
        slippage: 0.5,
        transactionDeadline: 1200,
        gasLimit: 'auto',
        confirmations: 1,
      },
      relay: {
        enabled: true,
        url: 'https://relay.test',
        fallbackToDirect: true,
      },
      ui: {
        authorizationUrl: 'https://up-auth.clawdbot.dev',
      },
      tokens: {
        known: {},
      },
    }),
    mockUpdateConfig: vi.fn().mockImplementation((updates: Record<string, unknown>) => ({
      version: '1.0.0',
      network: 'lukso',
      ...updates,
    })),
    mockGetNetworkConfig: vi.fn().mockReturnValue({
      chainId: 42,
      rpcUrl: 'https://rpc.lukso.network',
      contracts: {
        LSP23_LINKED_CONTRACTS_FACTORY: '0xLSP23Factory',
        MARKETPLACE: '0xMarketplace',
        UNIVERSALSWAPS_ROUTER: '0xRouter',
        UNIVERSALSWAPS_FACTORY: '0xFactory',
        WLYX: '0xWLYX',
      },
    }),
    mockGetRpcUrl: vi.fn().mockReturnValue('https://rpc.test'),
    mockGetRelayerUrl: vi.fn().mockReturnValue(null),
    mockHasUPConfig: vi.fn().mockReturnValue(true),
    mockHasControllerKey: vi.fn().mockReturnValue(true),
    mockSetUPConfig: vi.fn(),
    mockSetControllerKeyConfig: vi.fn(),
    mockResolveTokenAddress: vi.fn().mockImplementation((addr: string) => addr),

    DEFAULT_TEST_CONFIG,
  };
});

// ==================== vi.mock CALLS ====================

vi.mock('ethers', () => ({
  JsonRpcProvider: MockJsonRpcProvider,
  Wallet: MockWallet,
  Provider: vi.fn(),
}));

vi.mock('../../src/lib/crypto.js', () => ({
  generateKeyPair: mockGenerateKeyPair,
  encryptKey: mockEncryptKey,
  decryptKey: mockDecryptKey,
  loadKeystore: mockLoadKeystore,
  saveKey: mockSaveKey,
  listStoredKeys: mockListStoredKeys,
}));

vi.mock('../../src/lib/permissions.js', () => ({
  decodePermissions: mockDecodePermissions,
  validatePermissions: mockValidatePermissions,
  getPresetConfig: mockGetPresetConfig,
}));

vi.mock('../../src/lib/deployment.js', () => ({
  deployUniversalProfile: mockDeployUniversalProfile,
  computeDeploymentAddresses: mockComputeDeploymentAddresses,
  generateSalt: mockGenerateSalt,
}));

vi.mock('../../src/lib/relay.js', () => ({
  executeViaRelay: mockExecuteViaRelay,
}));

vi.mock('../../src/lib/profile.js', () => ({
  getProfileInfo: mockGetProfileInfo,
}));

vi.mock('../../src/lib/tokens.js', () => ({
  getLSP7Info: mockGetLSP7Info,
  getLSP8Info: mockGetLSP8Info,
  encodeLSP7Transfer: mockEncodeLSP7Transfer,
  encodeLSP8Transfer: mockEncodeLSP8Transfer,
  encodeLSP7AuthorizeOperator: mockEncodeLSP7AuthorizeOperator,
}));

vi.mock('../../src/lib/dex.js', () => ({
  getQuoteWithSlippage: mockGetQuoteWithSlippage,
  encodeSwapExactTokensForTokens: mockEncodeSwapExactTokensForTokens,
  getDeadline: mockGetDeadline,
}));

vi.mock('../../src/lib/marketplace.js', () => ({
  getListing: mockGetListing,
  getCollectionListings: mockGetCollectionListings,
  encodeBuyListing: mockEncodeBuyListing,
  getListingOperations: mockGetListingOperations,
}));

vi.mock('../../src/utils/config.js', () => ({
  loadConfig: mockLoadConfig,
  updateConfig: mockUpdateConfig,
  getNetworkConfig: mockGetNetworkConfig,
  getRpcUrl: mockGetRpcUrl,
  getRelayerUrl: mockGetRelayerUrl,
  hasUPConfig: mockHasUPConfig,
  hasControllerKey: mockHasControllerKey,
  setUPConfig: mockSetUPConfig,
  setControllerKeyConfig: mockSetControllerKeyConfig,
  resolveTokenAddress: mockResolveTokenAddress,
}));

// ==================== IMPORT UNDER TEST ====================

import {
  UniversalProfileSkill,
  createUniversalProfileSkill,
} from '../../src/skill.js';

// ==================== SETUP ====================

beforeEach(() => {
  vi.clearAllMocks();

  // Restore default return values after clearAllMocks
  mockLoadConfig.mockReturnValue({ ...DEFAULT_TEST_CONFIG });
  mockHasUPConfig.mockReturnValue(true);
  mockHasControllerKey.mockReturnValue(true);
  mockGetRpcUrl.mockReturnValue('https://rpc.test');
  mockGetRelayerUrl.mockReturnValue(null);
  mockGetNetworkConfig.mockReturnValue({
    chainId: 42,
    rpcUrl: 'https://rpc.lukso.network',
    contracts: {
      LSP23_LINKED_CONTRACTS_FACTORY: '0xLSP23Factory',
      MARKETPLACE: '0xMarketplace',
      UNIVERSALSWAPS_ROUTER: '0xRouter',
      UNIVERSALSWAPS_FACTORY: '0xFactory',
      WLYX: '0xWLYX',
    },
  });
  mockExecuteViaRelay.mockResolvedValue({
    transactionHash: '0xrelayTxHash',
    success: true,
  });
  mockGetPresetConfig.mockReturnValue({
    name: 'DeFi Trader',
    description: 'Trade tokens and interact with DeFi protocols',
    permissions: '0x0000000000000000000000000000000000000000000000000000000000040840',
    riskLevel: 'medium',
  });
  mockGenerateKeyPair.mockReturnValue({
    privateKey: '0xabc123',
    publicKey: '0xpub456',
    address: '0xAddr789',
  });
  mockEncryptKey.mockReturnValue({
    address: '0xAddr789',
    label: '',
    encryptedKey: 'enc',
    iv: 'iv',
    salt: 'salt',
    algorithm: 'aes-256-gcm',
    createdAt: '2025-01-01T00:00:00.000Z',
  });
  mockDecryptKey.mockReturnValue('0xdecryptedPrivateKey');
  mockLoadKeystore.mockReturnValue({
    address: '0xAddr789',
    label: 'test-key',
    encryptedKey: 'enc',
    iv: 'iv',
    salt: 'salt',
    algorithm: 'aes-256-gcm',
    createdAt: '2025-01-01T00:00:00.000Z',
  });
  mockSaveKey.mockReturnValue('/path/to/key.enc');
  mockListStoredKeys.mockReturnValue([]);
  mockResolveTokenAddress.mockImplementation((addr: string) => addr);
  mockDeployUniversalProfile.mockResolvedValue({
    upAddress: '0xUPAddress',
    keyManagerAddress: '0xKMAddress',
    transactionHash: '0xtxhash',
    blockNumber: 100,
  });
  mockComputeDeploymentAddresses.mockResolvedValue({
    upAddress: '0xComputedUP',
    keyManagerAddress: '0xComputedKM',
  });
  mockGenerateSalt.mockReturnValue('0xsalt');
  mockGetProfileInfo.mockResolvedValue({
    address: '0xUPAddress',
    name: 'Test Profile',
    keyManager: '0xKMAddress',
    owner: '0xOwner',
    balance: 1000n,
    controllers: [],
    receivedAssets: { lsp7: [], lsp8: [] },
  });
  mockGetLSP7Info.mockResolvedValue({
    address: '0xToken',
    name: 'Test Token',
    symbol: 'TST',
    decimals: 18,
    totalSupply: 1000000n,
    owner: '0xOwner',
    isNonDivisible: false,
  });
  mockGetLSP8Info.mockResolvedValue({
    address: '0xCollection',
    name: 'Test Collection',
    symbol: 'TNFT',
    totalSupply: 100n,
    owner: '0xOwner',
    tokenIdFormat: 0,
  });
  mockEncodeLSP7Transfer.mockReturnValue({
    operationType: 0,
    target: '0xToken',
    value: 0n,
    data: '0xlsp7data',
  });
  mockEncodeLSP8Transfer.mockReturnValue({
    operationType: 0,
    target: '0xCollection',
    value: 0n,
    data: '0xlsp8data',
  });
  mockEncodeLSP7AuthorizeOperator.mockReturnValue({
    operationType: 0,
    target: '0xToken',
    value: 0n,
    data: '0xauthorizedata',
  });
  mockGetQuoteWithSlippage.mockResolvedValue({
    quote: {
      amountIn: 100n,
      amountOut: 95n,
      priceImpact: 0.5,
      path: ['0xTokenIn', '0xTokenOut'],
      executionPrice: 0.95,
    },
    minAmountOut: 90n,
  });
  mockEncodeSwapExactTokensForTokens.mockReturnValue({
    operationType: 0,
    target: '0xRouter',
    value: 0n,
    data: '0xswapdata',
  });
  mockGetDeadline.mockReturnValue(9999999999);
  mockGetListing.mockResolvedValue({
    listingId: 1n,
    seller: '0xSeller',
    nftContract: '0xCollection',
    tokenId: '0x01',
    price: 500n,
    startTime: 1000,
    endTime: 2000,
    isActive: true,
  });
  mockGetCollectionListings.mockResolvedValue([]);
  mockEncodeBuyListing.mockReturnValue({
    operationType: 0,
    target: '0xMarketplace',
    value: 500n,
    data: '0xbuydata',
  });
  mockGetListingOperations.mockReturnValue([
    { operationType: 0, target: '0xCollection', value: 0n, data: '0xapprove' },
    { operationType: 0, target: '0xMarketplace', value: 0n, data: '0xlist' },
  ]);
  mockDecodePermissions.mockReturnValue(['CALL', 'SETDATA']);
  mockValidatePermissions.mockReturnValue({
    valid: true,
    warnings: [],
    risks: [],
  });
  mockUpdateConfig.mockImplementation((updates: Record<string, unknown>) => ({
    ...DEFAULT_TEST_CONFIG,
    ...updates,
  }));
});

// ==================== TESTS ====================

// ==================== CONSTRUCTOR ====================

describe('UniversalProfileSkill constructor', () => {
  it('creates a provider using getRpcUrl when no rpcUrl option given', () => {
    new UniversalProfileSkill();
    expect(mockLoadConfig).toHaveBeenCalled();
    expect(MockJsonRpcProvider).toHaveBeenCalledWith('https://rpc.test');
  });

  it('creates a provider with explicit rpcUrl option', () => {
    new UniversalProfileSkill({ rpcUrl: 'https://custom-rpc.test' });
    expect(MockJsonRpcProvider).toHaveBeenCalledWith('https://custom-rpc.test');
  });

  it('passes network option to getRpcUrl', () => {
    new UniversalProfileSkill({ network: 'lukso-testnet' });
    expect(mockGetRpcUrl).toHaveBeenCalledWith('lukso-testnet');
  });

  it('does not create a wallet when no privateKey is given', () => {
    new UniversalProfileSkill();
    expect(MockWallet).not.toHaveBeenCalled();
  });

  it('creates a wallet when privateKey is given', () => {
    new UniversalProfileSkill({ privateKey: '0xprivatekey123' });
    expect(MockWallet).toHaveBeenCalledWith('0xprivatekey123', mockProviderInstance);
  });

  it('uses config network when no network option provided', () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      network: 'my-custom-network',
    });
    new UniversalProfileSkill();
    expect(mockGetRpcUrl).toHaveBeenCalledWith('my-custom-network');
  });
});

// ==================== CONFIGURATION ====================

describe('getConfig', () => {
  it('returns the loaded config', () => {
    const skill = new UniversalProfileSkill();
    const config = skill.getConfig();
    expect(config.version).toBe('1.0.0');
    expect(config.network).toBe('lukso');
  });

  it('returns an object with expected top-level keys', () => {
    const skill = new UniversalProfileSkill();
    const config = skill.getConfig();
    expect(config).toHaveProperty('version');
    expect(config).toHaveProperty('network');
    expect(config).toHaveProperty('rpc');
    expect(config).toHaveProperty('defaults');
    expect(config).toHaveProperty('relay');
    expect(config).toHaveProperty('ui');
    expect(config).toHaveProperty('tokens');
  });
});

describe('updateConfig', () => {
  it('calls updateConfig from the config module', () => {
    const skill = new UniversalProfileSkill();
    skill.updateConfig({ network: 'lukso-testnet' });
    expect(mockUpdateConfig).toHaveBeenCalledWith({ network: 'lukso-testnet' });
  });

  it('updates the internal config reference', () => {
    const updatedConfig = { ...DEFAULT_TEST_CONFIG, network: 'lukso-testnet' };
    mockUpdateConfig.mockReturnValue(updatedConfig);
    const skill = new UniversalProfileSkill();
    skill.updateConfig({ network: 'lukso-testnet' });
    expect(skill.getConfig().network).toBe('lukso-testnet');
  });
});

describe('isConfigured', () => {
  it('returns true when both hasUPConfig and hasControllerKey return true', () => {
    const skill = new UniversalProfileSkill();
    expect(skill.isConfigured()).toBe(true);
    expect(mockHasUPConfig).toHaveBeenCalled();
    expect(mockHasControllerKey).toHaveBeenCalled();
  });

  it('returns false when hasUPConfig returns false', () => {
    mockHasUPConfig.mockReturnValue(false);
    const skill = new UniversalProfileSkill();
    expect(skill.isConfigured()).toBe(false);
  });

  it('returns false when hasControllerKey returns false', () => {
    mockHasControllerKey.mockReturnValue(false);
    const skill = new UniversalProfileSkill();
    expect(skill.isConfigured()).toBe(false);
  });

  it('returns false when both return false', () => {
    mockHasUPConfig.mockReturnValue(false);
    mockHasControllerKey.mockReturnValue(false);
    const skill = new UniversalProfileSkill();
    expect(skill.isConfigured()).toBe(false);
  });
});

// ==================== KEY MANAGEMENT ====================

describe('generateKey', () => {
  it('calls generateKeyPair and returns the result', () => {
    const skill = new UniversalProfileSkill();
    const result = skill.generateKey();
    expect(mockGenerateKeyPair).toHaveBeenCalled();
    expect(result).toEqual({
      privateKey: '0xabc123',
      publicKey: '0xpub456',
      address: '0xAddr789',
    });
  });
});

describe('storeKey', () => {
  it('encrypts the key and saves it', () => {
    const skill = new UniversalProfileSkill();
    const result = skill.storeKey('0xprivkey', 'my-label', 'password');
    expect(mockEncryptKey).toHaveBeenCalledWith('0xprivkey', 'password');
    expect(mockSaveKey).toHaveBeenCalledWith(
      expect.objectContaining({ address: '0xAddr789' }),
      'my-label'
    );
    expect(result).toBe('/path/to/key.enc');
  });

  it('updates controller key config after saving', () => {
    const skill = new UniversalProfileSkill();
    skill.storeKey('0xprivkey', 'my-label', 'password');
    expect(mockSetControllerKeyConfig).toHaveBeenCalledWith(
      '0xAddr789',
      'my-label',
      '/path/to/key.enc'
    );
  });
});

describe('loadKey', () => {
  it('loads and decrypts the keystore, returns a Wallet', () => {
    const skill = new UniversalProfileSkill();
    const wallet = skill.loadKey('my-label', 'password');
    expect(mockLoadKeystore).toHaveBeenCalledWith('my-label');
    expect(mockDecryptKey).toHaveBeenCalledWith(
      expect.objectContaining({ address: '0xAddr789' }),
      'password'
    );
    expect(MockWallet).toHaveBeenCalledWith('0xdecryptedPrivateKey', mockProviderInstance);
    expect(wallet).toBeDefined();
  });
});

describe('listKeys', () => {
  it('calls listStoredKeys and returns the result', () => {
    const storedKeys = [
      { address: '0xA', label: 'key1', path: '/a', createdAt: '2025-01-01' },
    ];
    mockListStoredKeys.mockReturnValue(storedKeys);
    const skill = new UniversalProfileSkill();
    const result = skill.listKeys();
    expect(mockListStoredKeys).toHaveBeenCalled();
    expect(result).toEqual(storedKeys);
  });

  it('returns an empty array when no keys stored', () => {
    mockListStoredKeys.mockReturnValue([]);
    const skill = new UniversalProfileSkill();
    expect(skill.listKeys()).toEqual([]);
  });
});

// ==================== PROFILE MANAGEMENT ====================

describe('getProfileInfo', () => {
  it('throws UniversalProfileError when no UP address configured and none provided', async () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      universalProfile: undefined,
    });
    const skill = new UniversalProfileSkill();
    await expect(skill.getProfileInfo()).rejects.toThrow(UniversalProfileError);
    await expect(skill.getProfileInfo()).rejects.toThrow(
      'No Universal Profile address configured'
    );
  });

  it('thrown error has CONFIG_NOT_FOUND code when no UP address', async () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      universalProfile: undefined,
    });
    const skill = new UniversalProfileSkill();
    try {
      await skill.getProfileInfo();
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe(ERROR_CODES.CONFIG_NOT_FOUND);
    }
  });

  it('calls getProfileInfo with the provided address', async () => {
    const skill = new UniversalProfileSkill();
    await skill.getProfileInfo('0xExplicitAddress');
    expect(mockGetProfileInfo).toHaveBeenCalledWith('0xExplicitAddress', mockProviderInstance);
  });

  it('uses the configured UP address when no address argument given', async () => {
    const skill = new UniversalProfileSkill();
    await skill.getProfileInfo();
    expect(mockGetProfileInfo).toHaveBeenCalledWith(
      DEFAULT_TEST_CONFIG.universalProfile!.address,
      mockProviderInstance
    );
  });

  it('returns the profile info from the lib function', async () => {
    const skill = new UniversalProfileSkill();
    const info = await skill.getProfileInfo('0xSomeAddress');
    expect(info).toEqual(
      expect.objectContaining({
        address: '0xUPAddress',
        name: 'Test Profile',
      })
    );
  });
});

// ==================== DEPLOYMENT ====================

describe('deployProfile', () => {
  it('throws when no wallet is configured', async () => {
    const skill = new UniversalProfileSkill();
    await expect(skill.deployProfile()).rejects.toThrow(UniversalProfileError);
    await expect(skill.deployProfile()).rejects.toThrow(
      'No wallet configured'
    );
  });

  it('deploys a profile and updates config on success', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const result = await skill.deployProfile();
    expect(mockGenerateSalt).toHaveBeenCalled();
    expect(mockDeployUniversalProfile).toHaveBeenCalled();
    expect(mockSetUPConfig).toHaveBeenCalledWith('0xUPAddress', '0xKMAddress');
    expect(result.upAddress).toBe('0xUPAddress');
    expect(result.keyManagerAddress).toBe('0xKMAddress');
    expect(result.transactionHash).toBe('0xtxhash');
  });

  it('passes recovery address and funding amount to deploy', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await skill.deployProfile({
      recoveryAddress: '0xRecovery',
      fundingAmount: 500n,
    });
    expect(mockDeployUniversalProfile).toHaveBeenCalledWith(
      mockWalletInstance,
      expect.objectContaining({
        fundingAmount: 500n,
        recoveryAddress: '0xRecovery',
      })
    );
  });
});

describe('computeDeploymentAddresses', () => {
  it('throws when no wallet is configured', async () => {
    const skill = new UniversalProfileSkill();
    await expect(skill.computeDeploymentAddresses('0xsalt')).rejects.toThrow(
      'No wallet configured'
    );
  });

  it('returns computed addresses', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const result = await skill.computeDeploymentAddresses('0xmysalt');
    expect(mockComputeDeploymentAddresses).toHaveBeenCalledWith(
      expect.objectContaining({ salt: '0xmysalt' }),
      mockProviderInstance
    );
    expect(result.upAddress).toBe('0xComputedUP');
    expect(result.keyManagerAddress).toBe('0xComputedKM');
  });
});

// ==================== PERMISSIONS ====================

describe('getPermissionPreset', () => {
  it('calls getPresetConfig with the given preset', () => {
    const skill = new UniversalProfileSkill();
    const result = skill.getPermissionPreset('defi-trader');
    expect(mockGetPresetConfig).toHaveBeenCalledWith('defi-trader');
    expect(result).toHaveProperty('name');
    expect(result).toHaveProperty('permissions');
  });

  it('works with different preset values', () => {
    const skill = new UniversalProfileSkill();
    skill.getPermissionPreset('read-only');
    expect(mockGetPresetConfig).toHaveBeenCalledWith('read-only');
  });
});

describe('decodePermissions', () => {
  it('calls decodePermissions with the hex value', () => {
    const skill = new UniversalProfileSkill();
    const result = skill.decodePermissions('0xff');
    expect(mockDecodePermissions).toHaveBeenCalledWith('0xff');
    expect(result).toEqual(['CALL', 'SETDATA']);
  });
});

describe('validatePermissions', () => {
  it('calls validatePermissions with the hex value', () => {
    const skill = new UniversalProfileSkill();
    const result = skill.validatePermissions('0xff');
    expect(mockValidatePermissions).toHaveBeenCalledWith('0xff');
    expect(result).toEqual({ valid: true, warnings: [], risks: [] });
  });
});

// ==================== AUTHORIZATION URL ====================

describe('getAuthorizationUrl', () => {
  it('builds URL with controller address and default preset', () => {
    const skill = new UniversalProfileSkill();
    const url = skill.getAuthorizationUrl('0xController');
    expect(url).toContain('https://up-auth.clawdbot.dev');
    expect(url).toContain('controller=0xController');
    expect(url).toContain('preset=defi-trader');
    expect(url).toContain('network=lukso');
  });

  it('builds URL with explicit preset', () => {
    const skill = new UniversalProfileSkill();
    const url = skill.getAuthorizationUrl('0xController', 'read-only');
    expect(mockGetPresetConfig).toHaveBeenCalledWith('read-only');
    expect(url).toContain('preset=read-only');
  });

  it('includes permissions from the preset config', () => {
    const skill = new UniversalProfileSkill();
    const url = skill.getAuthorizationUrl('0xController');
    expect(url).toContain('permissions=');
    expect(url).toContain(
      '0x0000000000000000000000000000000000000000000000000000000000040840'
    );
  });

  it('includes UP address param when UP is configured', () => {
    const skill = new UniversalProfileSkill();
    const url = skill.getAuthorizationUrl('0xController');
    expect(url).toContain(
      `up=${DEFAULT_TEST_CONFIG.universalProfile!.address}`
    );
  });

  it('does not include UP param when no UP configured', () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      universalProfile: undefined,
    });
    const skill = new UniversalProfileSkill();
    const url = skill.getAuthorizationUrl('0xController');
    expect(url).not.toContain('up=');
  });

  it('returns a parseable URL', () => {
    const skill = new UniversalProfileSkill();
    const url = skill.getAuthorizationUrl('0xController');
    const parsed = new URL(url);
    expect(parsed.searchParams.get('controller')).toBe('0xController');
    expect(parsed.searchParams.get('preset')).toBe('defi-trader');
    expect(parsed.searchParams.get('network')).toBe('lukso');
  });
});

// ==================== EXECUTION ====================

describe('execute', () => {
  const validParams = {
    operationType: 0,
    target: '0xTarget',
    value: 0n,
    data: '0xdata',
  };

  it('throws when no wallet is configured', async () => {
    const skill = new UniversalProfileSkill();
    await expect(skill.execute(validParams)).rejects.toThrow(UniversalProfileError);
    await expect(skill.execute(validParams)).rejects.toThrow(
      'No wallet configured'
    );
  });

  it('thrown error has KEY_NOT_FOUND code when no wallet', async () => {
    const skill = new UniversalProfileSkill();
    try {
      await skill.execute(validParams);
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe(ERROR_CODES.KEY_NOT_FOUND);
    }
  });

  it('throws when no UP is configured', async () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      universalProfile: undefined,
    });
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await expect(skill.execute(validParams)).rejects.toThrow(
      'No Universal Profile configured'
    );
  });

  it('calls executeViaRelay with correct arguments', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await skill.execute(validParams);
    expect(mockExecuteViaRelay).toHaveBeenCalledWith(
      mockWalletInstance,
      DEFAULT_TEST_CONFIG.universalProfile!.address,
      DEFAULT_TEST_CONFIG.universalProfile!.keyManager,
      validParams,
      expect.objectContaining({
        relayerUrl: undefined,
        useDirect: false,
      })
    );
  });

  it('passes relayerUrl when getRelayerUrl returns a value', async () => {
    mockGetRelayerUrl.mockReturnValue('https://relay.test.com');
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await skill.execute(validParams);
    expect(mockExecuteViaRelay).toHaveBeenCalledWith(
      mockWalletInstance,
      expect.any(String),
      expect.any(String),
      validParams,
      expect.objectContaining({
        relayerUrl: 'https://relay.test.com',
      })
    );
  });

  it('sets useDirect=true when relay is disabled', async () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      relay: { ...DEFAULT_TEST_CONFIG.relay, enabled: false },
    });
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await skill.execute(validParams);
    expect(mockExecuteViaRelay).toHaveBeenCalledWith(
      mockWalletInstance,
      expect.any(String),
      expect.any(String),
      validParams,
      expect.objectContaining({
        useDirect: true,
      })
    );
  });

  it('returns the transaction hash', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const hash = await skill.execute(validParams);
    expect(hash).toBe('0xrelayTxHash');
  });
});

describe('executeBatch', () => {
  it('executes operations sequentially and returns last hash', async () => {
    let callCount = 0;
    mockExecuteViaRelay.mockImplementation(async () => {
      callCount++;
      return { transactionHash: `0xhash${callCount}`, success: true };
    });

    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const ops = [
      { operationType: 0, target: '0xA', value: 0n, data: '0x01' },
      { operationType: 0, target: '0xB', value: 0n, data: '0x02' },
      { operationType: 0, target: '0xC', value: 0n, data: '0x03' },
    ];
    const hash = await skill.executeBatch(ops);
    expect(mockExecuteViaRelay).toHaveBeenCalledTimes(3);
    expect(hash).toBe('0xhash3');
  });

  it('throws when no wallet is configured', async () => {
    const skill = new UniversalProfileSkill();
    const ops = [
      { operationType: 0, target: '0xA', value: 0n, data: '0x01' },
    ];
    await expect(skill.executeBatch(ops)).rejects.toThrow(
      'No wallet configured'
    );
  });
});

// ==================== TOKEN OPERATIONS ====================

describe('getTokenInfo', () => {
  it('calls getLSP7Info with token address and provider', async () => {
    const skill = new UniversalProfileSkill();
    const info = await skill.getTokenInfo('0xToken');
    expect(mockGetLSP7Info).toHaveBeenCalledWith('0xToken', mockProviderInstance);
    expect(info.name).toBe('Test Token');
    expect(info.symbol).toBe('TST');
  });
});

describe('getCollectionInfo', () => {
  it('calls getLSP8Info with collection address and provider', async () => {
    const skill = new UniversalProfileSkill();
    const info = await skill.getCollectionInfo('0xCollection');
    expect(mockGetLSP8Info).toHaveBeenCalledWith('0xCollection', mockProviderInstance);
    expect(info.name).toBe('Test Collection');
    expect(info.symbol).toBe('TNFT');
  });
});

describe('transferToken', () => {
  it('throws when no UP configured', async () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      universalProfile: undefined,
    });
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await expect(
      skill.transferToken('0xToken', '0xRecipient', 100n)
    ).rejects.toThrow('No Universal Profile configured');
  });

  it('encodes and executes an LSP7 transfer', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const hash = await skill.transferToken('0xToken', '0xRecipient', 100n);
    expect(mockEncodeLSP7Transfer).toHaveBeenCalledWith(
      '0xToken',
      DEFAULT_TEST_CONFIG.universalProfile!.address,
      '0xRecipient',
      100n
    );
    expect(hash).toBe('0xrelayTxHash');
  });
});

describe('transferNFT', () => {
  it('throws when no UP configured', async () => {
    mockLoadConfig.mockReturnValue({
      ...DEFAULT_TEST_CONFIG,
      universalProfile: undefined,
    });
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await expect(
      skill.transferNFT('0xCollection', '0xRecipient', '0x01')
    ).rejects.toThrow('No Universal Profile configured');
  });

  it('encodes and executes an LSP8 transfer', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const hash = await skill.transferNFT('0xCollection', '0xRecipient', '0x01');
    expect(mockEncodeLSP8Transfer).toHaveBeenCalledWith(
      '0xCollection',
      DEFAULT_TEST_CONFIG.universalProfile!.address,
      '0xRecipient',
      '0x01'
    );
    expect(hash).toBe('0xrelayTxHash');
  });
});

// ==================== DEX OPERATIONS ====================

describe('getSwapQuote', () => {
  it('throws when DEX router is not configured', async () => {
    mockGetNetworkConfig.mockReturnValue({
      contracts: {},
    });
    const skill = new UniversalProfileSkill();
    await expect(
      skill.getSwapQuote('0xIn', '0xOut', 100n)
    ).rejects.toThrow('DEX router not configured');
  });

  it('calls getQuoteWithSlippage with resolved addresses and default slippage', async () => {
    const skill = new UniversalProfileSkill();
    const result = await skill.getSwapQuote('0xIn', '0xOut', 100n);
    expect(mockResolveTokenAddress).toHaveBeenCalledWith('0xIn');
    expect(mockResolveTokenAddress).toHaveBeenCalledWith('0xOut');
    expect(mockGetQuoteWithSlippage).toHaveBeenCalledWith(
      '0xRouter',
      '0xFactory',
      '0xIn',
      '0xOut',
      100n,
      DEFAULT_TEST_CONFIG.defaults.slippage,
      mockProviderInstance
    );
    expect(result.minAmountOut).toBe(90n);
  });

  it('uses provided slippage over default', async () => {
    const skill = new UniversalProfileSkill();
    await skill.getSwapQuote('0xIn', '0xOut', 100n, 1.5);
    expect(mockGetQuoteWithSlippage).toHaveBeenCalledWith(
      expect.any(String),
      expect.any(String),
      expect.any(String),
      expect.any(String),
      100n,
      1.5,
      mockProviderInstance
    );
  });
});

describe('swap', () => {
  it('authorizes the router then executes the swap', async () => {
    let callOrder = 0;
    const calls: number[] = [];
    mockExecuteViaRelay.mockImplementation(async () => {
      callOrder++;
      calls.push(callOrder);
      return { transactionHash: `0xhash${callOrder}`, success: true };
    });

    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const hash = await skill.swap('0xIn', '0xOut', 100n);

    // First call is authorize, second is swap
    expect(mockEncodeLSP7AuthorizeOperator).toHaveBeenCalledWith(
      '0xIn',
      '0xRouter',
      100n
    );
    expect(mockEncodeSwapExactTokensForTokens).toHaveBeenCalled();
    expect(calls).toEqual([1, 2]);
    expect(hash).toBe('0xhash2');
  });

  it('passes the quote path and deadline to encodeSwapExactTokensForTokens', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await skill.swap('0xIn', '0xOut', 100n);
    expect(mockEncodeSwapExactTokensForTokens).toHaveBeenCalledWith(
      '0xRouter',
      expect.objectContaining({
        tokenIn: '0xIn',
        tokenOut: '0xOut',
        amountIn: 100n,
        amountOutMin: 90n,
        path: ['0xTokenIn', '0xTokenOut'],
      }),
      DEFAULT_TEST_CONFIG.universalProfile!.address
    );
  });
});

// ==================== MARKETPLACE OPERATIONS ====================

describe('getMarketplaceListings', () => {
  it('throws when marketplace is not configured', async () => {
    mockGetNetworkConfig.mockReturnValue({
      contracts: {},
    });
    const skill = new UniversalProfileSkill();
    await expect(
      skill.getMarketplaceListings('0xCollection')
    ).rejects.toThrow('Marketplace not configured');
  });

  it('calls getCollectionListings with correct args', async () => {
    const skill = new UniversalProfileSkill();
    await skill.getMarketplaceListings('0xCollection');
    expect(mockGetCollectionListings).toHaveBeenCalledWith(
      '0xMarketplace',
      '0xCollection',
      mockProviderInstance
    );
  });
});

describe('listNFT', () => {
  it('throws when marketplace is not configured', async () => {
    mockGetNetworkConfig.mockReturnValue({
      contracts: {},
    });
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await expect(
      skill.listNFT('0xCollection', '0x01', 500n)
    ).rejects.toThrow('Marketplace not configured');
  });

  it('calls getListingOperations and executes batch', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await skill.listNFT('0xCollection', '0x01', 500n, 14);
    expect(mockGetListingOperations).toHaveBeenCalledWith('0xMarketplace', {
      nftContract: '0xCollection',
      tokenId: '0x01',
      price: 500n,
      duration: 14 * 24 * 60 * 60,
    });
    // Two operations from mockGetListingOperations
    expect(mockExecuteViaRelay).toHaveBeenCalledTimes(2);
  });

  it('defaults duration to 7 days', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await skill.listNFT('0xCollection', '0x01', 500n);
    expect(mockGetListingOperations).toHaveBeenCalledWith(
      '0xMarketplace',
      expect.objectContaining({
        duration: 7 * 24 * 60 * 60,
      })
    );
  });
});

describe('buyNFT', () => {
  it('throws when marketplace is not configured', async () => {
    mockGetNetworkConfig.mockReturnValue({
      contracts: {},
    });
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    await expect(skill.buyNFT(1n)).rejects.toThrow(
      'Marketplace not configured'
    );
  });

  it('fetches the listing and executes buy', async () => {
    const skill = new UniversalProfileSkill({ privateKey: '0xpk' });
    const hash = await skill.buyNFT(1n);
    expect(mockGetListing).toHaveBeenCalledWith(
      '0xMarketplace',
      1n,
      mockProviderInstance
    );
    expect(mockEncodeBuyListing).toHaveBeenCalledWith(
      '0xMarketplace',
      1n,
      500n
    );
    expect(hash).toBe('0xrelayTxHash');
  });
});

// ==================== FACTORY FUNCTION ====================

describe('createUniversalProfileSkill', () => {
  it('returns a UniversalProfileSkill instance', () => {
    const skill = createUniversalProfileSkill();
    expect(skill).toBeInstanceOf(UniversalProfileSkill);
  });

  it('passes options to the constructor', () => {
    const skill = createUniversalProfileSkill({
      rpcUrl: 'https://custom.rpc',
      privateKey: '0xfactorykey',
    });
    expect(skill).toBeInstanceOf(UniversalProfileSkill);
    expect(MockJsonRpcProvider).toHaveBeenCalledWith('https://custom.rpc');
    expect(MockWallet).toHaveBeenCalledWith('0xfactorykey', mockProviderInstance);
  });

  it('works without options', () => {
    const skill = createUniversalProfileSkill();
    expect(skill).toBeInstanceOf(UniversalProfileSkill);
    expect(skill.getConfig()).toBeDefined();
  });

  it('passes network option through', () => {
    createUniversalProfileSkill({ network: 'lukso-testnet' });
    expect(mockGetRpcUrl).toHaveBeenCalledWith('lukso-testnet');
  });
});
