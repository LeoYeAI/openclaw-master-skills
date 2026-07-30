import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import * as path from 'path';
import {
  getHomeDir,
  getConfigDir,
  getConfigPath,
  ensureConfigDir,
  getDefaultConfig,
  loadConfig,
  saveConfig,
  updateConfig,
  getNetworkConfig,
  getRpcUrl,
  getRelayerUrl,
  hasUPConfig,
  hasControllerKey,
  setUPConfig,
  setControllerKeyConfig,
  addKnownToken,
  getKnownToken,
  resolveTokenAddress,
} from '../../src/utils/config.js';
import { UniversalProfileError } from '../../src/types/index.js';
import { NETWORKS, DEFAULT_NETWORK, DEFAULTS } from '../../src/utils/constants.js';

// ==================== MOCK fs MODULE ====================

vi.mock('fs', () => ({
  existsSync: vi.fn(),
  readFileSync: vi.fn(),
  writeFileSync: vi.fn(),
  mkdirSync: vi.fn(),
  readdirSync: vi.fn(),
}));

import * as fs from 'fs';

const mockedExistsSync = vi.mocked(fs.existsSync);
const mockedReadFileSync = vi.mocked(fs.readFileSync);
const mockedWriteFileSync = vi.mocked(fs.writeFileSync);
const mockedMkdirSync = vi.mocked(fs.mkdirSync);

// ==================== ENVIRONMENT HELPERS ====================

const originalEnv = { ...process.env };

function resetEnv() {
  // Restore original values for HOME, USERPROFILE, UP_CONFIG_PATH
  if (originalEnv.HOME !== undefined) {
    process.env.HOME = originalEnv.HOME;
  } else {
    delete process.env.HOME;
  }
  if (originalEnv.USERPROFILE !== undefined) {
    process.env.USERPROFILE = originalEnv.USERPROFILE;
  } else {
    delete process.env.USERPROFILE;
  }
  if (originalEnv.UP_CONFIG_PATH !== undefined) {
    process.env.UP_CONFIG_PATH = originalEnv.UP_CONFIG_PATH;
  } else {
    delete process.env.UP_CONFIG_PATH;
  }
}

beforeEach(() => {
  vi.clearAllMocks();
});

afterEach(() => {
  resetEnv();
});

// ==================== PATH FUNCTIONS ====================

describe('getHomeDir', () => {
  it('returns HOME when set', () => {
    process.env.HOME = '/mock/home';
    delete process.env.USERPROFILE;
    expect(getHomeDir()).toBe('/mock/home');
  });

  it('falls back to USERPROFILE when HOME is not set', () => {
    delete process.env.HOME;
    process.env.USERPROFILE = 'C:\\Users\\mockuser';
    expect(getHomeDir()).toBe('C:\\Users\\mockuser');
  });

  it('falls back to ~ when neither HOME nor USERPROFILE is set', () => {
    delete process.env.HOME;
    delete process.env.USERPROFILE;
    expect(getHomeDir()).toBe('~');
  });

  it('prefers HOME over USERPROFILE when both are set', () => {
    process.env.HOME = '/unix/home';
    process.env.USERPROFILE = 'C:\\Windows\\home';
    expect(getHomeDir()).toBe('/unix/home');
  });
});

describe('getConfigDir', () => {
  it('returns UP_CONFIG_PATH when set', () => {
    process.env.UP_CONFIG_PATH = '/custom/config/dir';
    expect(getConfigDir()).toBe('/custom/config/dir');
  });

  it('returns default path under HOME when UP_CONFIG_PATH is not set', () => {
    delete process.env.UP_CONFIG_PATH;
    process.env.HOME = '/mock/home';
    expect(getConfigDir()).toBe(
      path.join('/mock/home', '.clawdbot', 'universal-profile')
    );
  });

  it('uses USERPROFILE when HOME is not set and UP_CONFIG_PATH is not set', () => {
    delete process.env.UP_CONFIG_PATH;
    delete process.env.HOME;
    process.env.USERPROFILE = 'C:\\Users\\test';
    expect(getConfigDir()).toBe(
      path.join('C:\\Users\\test', '.clawdbot', 'universal-profile')
    );
  });
});

describe('getConfigPath', () => {
  it('returns config.json inside the config directory', () => {
    process.env.UP_CONFIG_PATH = '/custom/dir';
    expect(getConfigPath()).toBe(path.join('/custom/dir', 'config.json'));
  });

  it('uses the default config dir when UP_CONFIG_PATH is not set', () => {
    delete process.env.UP_CONFIG_PATH;
    process.env.HOME = '/home/user';
    const expected = path.join(
      '/home/user',
      '.clawdbot',
      'universal-profile',
      'config.json'
    );
    expect(getConfigPath()).toBe(expected);
  });
});

describe('ensureConfigDir', () => {
  it('creates directory when it does not exist', () => {
    process.env.UP_CONFIG_PATH = '/test/config/dir';
    mockedExistsSync.mockReturnValue(false);

    const result = ensureConfigDir();

    expect(result).toBe('/test/config/dir');
    expect(mockedMkdirSync).toHaveBeenCalledWith('/test/config/dir', {
      recursive: true,
    });
  });

  it('does not create directory when it already exists', () => {
    process.env.UP_CONFIG_PATH = '/test/config/dir';
    mockedExistsSync.mockReturnValue(true);

    const result = ensureConfigDir();

    expect(result).toBe('/test/config/dir');
    expect(mockedMkdirSync).not.toHaveBeenCalled();
  });

  it('returns the config directory path', () => {
    process.env.UP_CONFIG_PATH = '/some/path';
    mockedExistsSync.mockReturnValue(true);

    expect(ensureConfigDir()).toBe('/some/path');
  });
});

// ==================== DEFAULT CONFIG ====================

describe('getDefaultConfig', () => {
  it('returns a config with version 1.0.0', () => {
    const config = getDefaultConfig();
    expect(config.version).toBe('1.0.0');
  });

  it('uses the default network', () => {
    const config = getDefaultConfig();
    expect(config.network).toBe(DEFAULT_NETWORK);
  });

  it('contains RPC entries for all defined networks', () => {
    const config = getDefaultConfig();
    for (const networkName of Object.keys(NETWORKS)) {
      expect(config.rpc[networkName]).toBe(NETWORKS[networkName].rpcUrl);
    }
  });

  it('has undefined universalProfile and controllerKey', () => {
    const config = getDefaultConfig();
    expect(config.universalProfile).toBeUndefined();
    expect(config.controllerKey).toBeUndefined();
  });

  it('contains contracts for all defined networks', () => {
    const config = getDefaultConfig();
    for (const networkName of Object.keys(NETWORKS)) {
      expect(config.contracts[networkName]).toBeDefined();
      expect(config.contracts[networkName].lsp23Factory).toBe(
        NETWORKS[networkName].contracts.LSP23_LINKED_CONTRACTS_FACTORY
      );
    }
  });

  it('sets default slippage from DEFAULTS constant', () => {
    const config = getDefaultConfig();
    expect(config.defaults.slippage).toBe(DEFAULTS.slippage);
  });

  it('sets default transactionDeadline from DEFAULTS constant', () => {
    const config = getDefaultConfig();
    expect(config.defaults.transactionDeadline).toBe(DEFAULTS.transactionDeadline);
  });

  it('sets default confirmations from DEFAULTS constant', () => {
    const config = getDefaultConfig();
    expect(config.defaults.confirmations).toBe(DEFAULTS.confirmations);
  });

  it('sets gasLimit to auto by default', () => {
    const config = getDefaultConfig();
    expect(config.defaults.gasLimit).toBe('auto');
  });

  it('has relay enabled by default with fallback to direct', () => {
    const config = getDefaultConfig();
    expect(config.relay.enabled).toBe(true);
    expect(config.relay.fallbackToDirect).toBe(true);
  });

  it('has relay URL from the default network', () => {
    const config = getDefaultConfig();
    expect(config.relay.url).toBe(NETWORKS[DEFAULT_NETWORK].relayerUrl || '');
  });

  it('has default UI authorization URL', () => {
    const config = getDefaultConfig();
    expect(config.ui.authorizationUrl).toBe('https://up-auth.clawdbot.dev');
  });

  it('has empty known tokens by default', () => {
    const config = getDefaultConfig();
    expect(config.tokens.known).toEqual({});
  });
});

// ==================== LOAD CONFIG ====================

describe('loadConfig', () => {
  it('returns default config when config file does not exist', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);

    const config = loadConfig();
    const defaults = getDefaultConfig();

    expect(config.version).toBe(defaults.version);
    expect(config.network).toBe(defaults.network);
    expect(config.defaults.slippage).toBe(defaults.defaults.slippage);
  });

  it('does not call readFileSync when file does not exist', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);

    loadConfig();

    expect(mockedReadFileSync).not.toHaveBeenCalled();
  });

  it('reads and parses config file when it exists', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    const fileContent = JSON.stringify({
      version: '2.0.0',
      network: 'lukso-testnet',
    });
    mockedExistsSync.mockReturnValue(true);
    mockedReadFileSync.mockReturnValue(fileContent);

    const config = loadConfig();

    expect(mockedReadFileSync).toHaveBeenCalledWith(
      path.join('/test/dir', 'config.json'),
      'utf8'
    );
    expect(config.version).toBe('2.0.0');
    expect(config.network).toBe('lukso-testnet');
  });

  it('merges loaded config with defaults (loaded values override)', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    const customConfig = {
      network: 'lukso-testnet',
      defaults: {
        slippage: 1.0,
        transactionDeadline: 600,
        gasLimit: 500000,
        confirmations: 3,
      },
    };
    mockedExistsSync.mockReturnValue(true);
    mockedReadFileSync.mockReturnValue(JSON.stringify(customConfig));

    const config = loadConfig();

    // Custom values should override
    expect(config.network).toBe('lukso-testnet');
    expect(config.defaults.slippage).toBe(1.0);
    expect(config.defaults.confirmations).toBe(3);
    // Default values should be present for unset fields
    expect(config.version).toBe('1.0.0');
    expect(config.relay).toBeDefined();
    expect(config.ui).toBeDefined();
  });

  it('preserves universalProfile from loaded config', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    const customConfig = {
      universalProfile: {
        address: '0x1234567890abcdef1234567890abcdef12345678',
        keyManager: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
      },
    };
    mockedExistsSync.mockReturnValue(true);
    mockedReadFileSync.mockReturnValue(JSON.stringify(customConfig));

    const config = loadConfig();

    expect(config.universalProfile).toEqual(customConfig.universalProfile);
  });

  it('throws UniversalProfileError when config file has invalid JSON', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);
    mockedReadFileSync.mockReturnValue('{ invalid json }');

    expect(() => loadConfig()).toThrow(UniversalProfileError);
  });

  it('thrown error for invalid JSON includes CONFIG_NOT_FOUND code', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);
    mockedReadFileSync.mockReturnValue('not json');

    try {
      loadConfig();
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe('UP_CONFIG_NOT_FOUND');
    }
  });

  it('thrown error includes config path in details', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);
    mockedReadFileSync.mockReturnValue('bad');

    try {
      loadConfig();
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect((err as UniversalProfileError).details).toHaveProperty('path');
      expect((err as UniversalProfileError).details!.path).toBe(
        path.join('/test/dir', 'config.json')
      );
    }
  });

  it('throws UniversalProfileError when readFileSync throws', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);
    mockedReadFileSync.mockImplementation(() => {
      throw new Error('EACCES: permission denied');
    });

    expect(() => loadConfig()).toThrow(UniversalProfileError);
  });
});

// ==================== SAVE CONFIG ====================

describe('saveConfig', () => {
  it('calls ensureConfigDir before writing', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);

    const config = getDefaultConfig();
    saveConfig(config);

    // ensureConfigDir checks existsSync for the dir
    expect(mockedExistsSync).toHaveBeenCalled();
  });

  it('writes JSON to the config file path', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);

    const config = getDefaultConfig();
    saveConfig(config);

    expect(mockedWriteFileSync).toHaveBeenCalledWith(
      path.join('/test/dir', 'config.json'),
      expect.any(String),
      'utf8'
    );
  });

  it('writes pretty-printed JSON (2-space indentation)', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);

    const config = getDefaultConfig();
    saveConfig(config);

    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    expect(writtenContent).toBe(JSON.stringify(config, null, 2));
  });

  it('creates the config directory if it does not exist', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);

    const config = getDefaultConfig();
    saveConfig(config);

    expect(mockedMkdirSync).toHaveBeenCalledWith('/test/dir', {
      recursive: true,
    });
  });

  it('written JSON can be parsed back to the original config', () => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(true);

    const config = getDefaultConfig();
    saveConfig(config);

    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    const parsed = JSON.parse(writtenContent);
    expect(parsed.version).toBe(config.version);
    expect(parsed.network).toBe(config.network);
    expect(parsed.defaults.slippage).toBe(config.defaults.slippage);
  });
});

// ==================== UPDATE CONFIG ====================

describe('updateConfig', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
  });

  it('merges updates with current config', () => {
    // loadConfig returns defaults when file doesn't exist
    mockedExistsSync.mockReturnValue(false);

    const updated = updateConfig({ network: 'lukso-testnet' });

    expect(updated.network).toBe('lukso-testnet');
    // Other defaults should remain
    expect(updated.version).toBe('1.0.0');
  });

  it('saves the merged config', () => {
    mockedExistsSync.mockReturnValue(false);

    updateConfig({ network: 'lukso-testnet' });

    // saveConfig is called which invokes ensureConfigDir + writeFileSync
    expect(mockedWriteFileSync).toHaveBeenCalled();
    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    const parsed = JSON.parse(writtenContent);
    expect(parsed.network).toBe('lukso-testnet');
  });

  it('returns the updated config object', () => {
    mockedExistsSync.mockReturnValue(false);

    const result = updateConfig({
      defaults: {
        slippage: 2.0,
        transactionDeadline: 300,
        gasLimit: 100000,
        confirmations: 5,
      },
    });

    expect(result.defaults.slippage).toBe(2.0);
    expect(result.defaults.confirmations).toBe(5);
  });

  it('merges with existing file config when file exists', () => {
    const existingConfig = {
      ...getDefaultConfig(),
      network: 'lukso-testnet',
      tokens: { known: { USDT: '0xabc' } },
    };
    // First call to existsSync is for loadConfig (getConfigPath), second is for saveConfig (ensureConfigDir)
    mockedExistsSync.mockImplementation((p) => {
      const pStr = String(p);
      if (pStr.endsWith('config.json')) return true;
      return true; // dir exists
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(existingConfig));

    const result = updateConfig({ version: '3.0.0' });

    expect(result.version).toBe('3.0.0');
    expect(result.network).toBe('lukso-testnet');
    expect(result.tokens.known.USDT).toBe('0xabc');
  });
});

// ==================== GET NETWORK CONFIG ====================

describe('getNetworkConfig', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false); // loadConfig returns defaults
  });

  it('returns config for lukso-mainnet when no argument is given (default network)', () => {
    const netConfig = getNetworkConfig();

    expect(netConfig.chainId).toBe(NETWORKS['lukso-mainnet'].chainId);
    expect(netConfig.name).toBe(NETWORKS['lukso-mainnet'].name);
  });

  it('returns config for a specified network', () => {
    const netConfig = getNetworkConfig('lukso-testnet');

    expect(netConfig.chainId).toBe(NETWORKS['lukso-testnet'].chainId);
    expect(netConfig.name).toBe(NETWORKS['lukso-testnet'].name);
  });

  it('throws UniversalProfileError for an unknown network', () => {
    expect(() => getNetworkConfig('ethereum-mainnet')).toThrow(
      UniversalProfileError
    );
  });

  it('thrown error for unknown network has NETWORK_ERROR code', () => {
    try {
      getNetworkConfig('nonexistent-network');
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe('UP_NETWORK_ERROR');
    }
  });

  it('thrown error message includes the unknown network name', () => {
    try {
      getNetworkConfig('bad-network');
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect((err as UniversalProfileError).message).toContain('bad-network');
    }
  });

  it('overrides rpcUrl with custom RPC from loaded config', () => {
    const customConfig = {
      ...getDefaultConfig(),
      rpc: {
        'lukso-mainnet': 'https://custom.rpc.example.com',
        'lukso-testnet': NETWORKS['lukso-testnet'].rpcUrl,
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(customConfig));

    const netConfig = getNetworkConfig('lukso-mainnet');

    expect(netConfig.rpcUrl).toBe('https://custom.rpc.example.com');
  });

  it('returns base NETWORKS rpcUrl when no custom RPC is set for the network', () => {
    const netConfig = getNetworkConfig('lukso-mainnet');

    expect(netConfig.rpcUrl).toBe(NETWORKS['lukso-mainnet'].rpcUrl);
  });

  it('includes contracts merged from NETWORKS and config', () => {
    const netConfig = getNetworkConfig('lukso-mainnet');

    expect(netConfig.contracts).toBeDefined();
    expect(netConfig.contracts.LSP23_LINKED_CONTRACTS_FACTORY).toBe(
      NETWORKS['lukso-mainnet'].contracts.LSP23_LINKED_CONTRACTS_FACTORY
    );
  });
});

// ==================== GET RPC URL ====================

describe('getRpcUrl', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);
  });

  it('returns default RPC URL for the default network when no argument given', () => {
    const url = getRpcUrl();
    expect(url).toBe(NETWORKS[DEFAULT_NETWORK].rpcUrl);
  });

  it('returns RPC URL for a specified network', () => {
    const url = getRpcUrl('lukso-testnet');
    expect(url).toBe(NETWORKS['lukso-testnet'].rpcUrl);
  });

  it('returns custom RPC URL when set in config', () => {
    const customConfig = {
      ...getDefaultConfig(),
      rpc: {
        'lukso-mainnet': 'https://my-custom-rpc.com',
        'lukso-testnet': NETWORKS['lukso-testnet'].rpcUrl,
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(customConfig));

    const url = getRpcUrl('lukso-mainnet');
    expect(url).toBe('https://my-custom-rpc.com');
  });

  it('returns empty string for a network not in NETWORKS and not in config', () => {
    const url = getRpcUrl('unknown-network');
    expect(url).toBe('');
  });
});

// ==================== GET RELAYER URL ====================

describe('getRelayerUrl', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);
  });

  it('returns relayer URL for the default network when no argument given', () => {
    const url = getRelayerUrl();
    expect(url).toBe(NETWORKS[DEFAULT_NETWORK].relayerUrl);
  });

  it('returns relayer URL for a specified network', () => {
    const url = getRelayerUrl('lukso-testnet');
    expect(url).toBe(NETWORKS['lukso-testnet'].relayerUrl);
  });

  it('returns null for an unknown network', () => {
    const url = getRelayerUrl('nonexistent');
    expect(url).toBeNull();
  });
});

// ==================== HAS UP CONFIG ====================

describe('hasUPConfig', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
  });

  it('returns false when no config file exists (defaults have no UP config)', () => {
    mockedExistsSync.mockReturnValue(false);

    expect(hasUPConfig()).toBe(false);
  });

  it('returns true when universalProfile address and keyManager are set', () => {
    const configWithUP = {
      ...getDefaultConfig(),
      universalProfile: {
        address: '0x1234567890abcdef1234567890abcdef12345678',
        keyManager: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithUP));

    expect(hasUPConfig()).toBe(true);
  });

  it('returns false when universalProfile.address is empty string', () => {
    const configWithEmptyUP = {
      ...getDefaultConfig(),
      universalProfile: {
        address: '',
        keyManager: '0xabcdefabcdefabcdefabcdefabcdefabcdefabcd',
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithEmptyUP));

    expect(hasUPConfig()).toBe(false);
  });

  it('returns false when universalProfile.keyManager is empty string', () => {
    const configWithEmptyKM = {
      ...getDefaultConfig(),
      universalProfile: {
        address: '0x1234567890abcdef1234567890abcdef12345678',
        keyManager: '',
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithEmptyKM));

    expect(hasUPConfig()).toBe(false);
  });

  it('returns false when universalProfile is undefined', () => {
    const configNoUP = {
      ...getDefaultConfig(),
      universalProfile: undefined,
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configNoUP));

    expect(hasUPConfig()).toBe(false);
  });
});

// ==================== HAS CONTROLLER KEY ====================

describe('hasControllerKey', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
  });

  it('returns false when no config file exists (defaults have no controller key)', () => {
    mockedExistsSync.mockReturnValue(false);

    expect(hasControllerKey()).toBe(false);
  });

  it('returns true when controllerKey address and path are set', () => {
    const configWithKey = {
      ...getDefaultConfig(),
      controllerKey: {
        address: '0x1234567890abcdef1234567890abcdef12345678',
        label: 'test-key',
        encrypted: true,
        path: '/keys/test-key.enc',
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithKey));

    expect(hasControllerKey()).toBe(true);
  });

  it('returns false when controllerKey.address is empty string', () => {
    const config = {
      ...getDefaultConfig(),
      controllerKey: {
        address: '',
        label: 'test-key',
        encrypted: true,
        path: '/keys/test-key.enc',
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(config));

    expect(hasControllerKey()).toBe(false);
  });

  it('returns false when controllerKey.path is empty string', () => {
    const config = {
      ...getDefaultConfig(),
      controllerKey: {
        address: '0x1234567890abcdef1234567890abcdef12345678',
        label: 'test-key',
        encrypted: true,
        path: '',
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(config));

    expect(hasControllerKey()).toBe(false);
  });

  it('returns false when controllerKey is undefined', () => {
    mockedExistsSync.mockReturnValue(false);

    expect(hasControllerKey()).toBe(false);
  });
});

// ==================== SET UP CONFIG ====================

describe('setUPConfig', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);
  });

  it('saves the UP address and key manager to config', () => {
    const upAddr = '0x1111111111111111111111111111111111111111';
    const kmAddr = '0x2222222222222222222222222222222222222222';

    setUPConfig(upAddr, kmAddr);

    expect(mockedWriteFileSync).toHaveBeenCalled();
    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    const parsed = JSON.parse(writtenContent);
    expect(parsed.universalProfile.address).toBe(upAddr);
    expect(parsed.universalProfile.keyManager).toBe(kmAddr);
  });
});

// ==================== SET CONTROLLER KEY CONFIG ====================

describe('setControllerKeyConfig', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);
  });

  it('saves the controller key config with encrypted set to true', () => {
    const addr = '0x3333333333333333333333333333333333333333';
    const label = 'my-controller';
    const keyPath = '/keys/my-controller.enc';

    setControllerKeyConfig(addr, label, keyPath);

    expect(mockedWriteFileSync).toHaveBeenCalled();
    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    const parsed = JSON.parse(writtenContent);
    expect(parsed.controllerKey.address).toBe(addr);
    expect(parsed.controllerKey.label).toBe(label);
    expect(parsed.controllerKey.encrypted).toBe(true);
    expect(parsed.controllerKey.path).toBe(keyPath);
  });
});

// ==================== TOKEN MANAGEMENT ====================

describe('addKnownToken', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
    mockedExistsSync.mockReturnValue(false);
  });

  it('adds a token with uppercased symbol to the config', () => {
    const address = '0x4444444444444444444444444444444444444444';

    addKnownToken('usdt', address);

    expect(mockedWriteFileSync).toHaveBeenCalled();
    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    const parsed = JSON.parse(writtenContent);
    expect(parsed.tokens.known.USDT).toBe(address);
  });

  it('preserves existing known tokens when adding a new one', () => {
    const existingConfig = {
      ...getDefaultConfig(),
      tokens: { known: { DAI: '0xdai' } },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(existingConfig));

    addKnownToken('USDC', '0xusdc');

    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    const parsed = JSON.parse(writtenContent);
    expect(parsed.tokens.known.DAI).toBe('0xdai');
    expect(parsed.tokens.known.USDC).toBe('0xusdc');
  });

  it('uppercases mixed-case symbol input', () => {
    addKnownToken('UsDt', '0xaddr');

    const writtenContent = mockedWriteFileSync.mock.calls[0][1] as string;
    const parsed = JSON.parse(writtenContent);
    expect(parsed.tokens.known.USDT).toBe('0xaddr');
  });
});

describe('getKnownToken', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
  });

  it('returns undefined when token is not known', () => {
    mockedExistsSync.mockReturnValue(false);

    expect(getKnownToken('UNKNOWN')).toBeUndefined();
  });

  it('returns address for a known token', () => {
    const configWithTokens = {
      ...getDefaultConfig(),
      tokens: { known: { USDT: '0xtoken_address' } },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithTokens));

    expect(getKnownToken('USDT')).toBe('0xtoken_address');
  });

  it('uppercases the symbol before lookup', () => {
    const configWithTokens = {
      ...getDefaultConfig(),
      tokens: { known: { USDT: '0xtoken_address' } },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithTokens));

    expect(getKnownToken('usdt')).toBe('0xtoken_address');
    expect(getKnownToken('Usdt')).toBe('0xtoken_address');
  });
});

// ==================== RESOLVE TOKEN ADDRESS ====================

describe('resolveTokenAddress', () => {
  beforeEach(() => {
    process.env.UP_CONFIG_PATH = '/test/dir';
  });

  it('returns the input directly when it starts with 0x', () => {
    mockedExistsSync.mockReturnValue(false);

    const address = '0x1234567890abcdef1234567890abcdef12345678';
    expect(resolveTokenAddress(address)).toBe(address);
  });

  it('returns known token address when symbol is registered', () => {
    const configWithTokens = {
      ...getDefaultConfig(),
      tokens: { known: { USDT: '0xusdt_address' } },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithTokens));

    expect(resolveTokenAddress('USDT')).toBe('0xusdt_address');
  });

  it('is case-insensitive for known token lookups', () => {
    const configWithTokens = {
      ...getDefaultConfig(),
      tokens: { known: { USDT: '0xusdt_address' } },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithTokens));

    expect(resolveTokenAddress('usdt')).toBe('0xusdt_address');
  });

  it('returns WLYX address for LYX when wlyx is configured', () => {
    const wlyxAddress = '0xwlyx_contract_address';
    const configWithWLYX = {
      ...getDefaultConfig(),
      contracts: {
        'lukso-mainnet': {
          lsp23Factory: '0xfactory',
          wlyx: wlyxAddress,
        },
        'lukso-testnet': {
          lsp23Factory: '0xfactory2',
        },
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithWLYX));

    expect(resolveTokenAddress('LYX')).toBe(wlyxAddress);
  });

  it('handles lowercase lyx input', () => {
    const wlyxAddress = '0xwlyx_contract';
    const configWithWLYX = {
      ...getDefaultConfig(),
      contracts: {
        'lukso-mainnet': {
          lsp23Factory: '0xfactory',
          wlyx: wlyxAddress,
        },
        'lukso-testnet': {
          lsp23Factory: '0xfactory2',
        },
      },
    };
    mockedExistsSync.mockImplementation((p) => {
      if (String(p).endsWith('config.json')) return true;
      return true;
    });
    mockedReadFileSync.mockReturnValue(JSON.stringify(configWithWLYX));

    expect(resolveTokenAddress('lyx')).toBe(wlyxAddress);
  });

  it('throws UniversalProfileError for unknown token symbol', () => {
    mockedExistsSync.mockReturnValue(false);

    expect(() => resolveTokenAddress('UNKNOWN_TOKEN')).toThrow(
      UniversalProfileError
    );
  });

  it('thrown error for unknown token has INVALID_ADDRESS code', () => {
    mockedExistsSync.mockReturnValue(false);

    try {
      resolveTokenAddress('NONEXISTENT');
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect(err).toBeInstanceOf(UniversalProfileError);
      expect((err as UniversalProfileError).code).toBe('UP_INVALID_ADDRESS');
    }
  });

  it('thrown error message includes the unknown symbol', () => {
    mockedExistsSync.mockReturnValue(false);

    try {
      resolveTokenAddress('FAKECOIN');
      expect.unreachable('Should have thrown');
    } catch (err) {
      expect((err as UniversalProfileError).message).toContain('FAKECOIN');
    }
  });

  it('throws for LYX when WLYX is not configured (null)', () => {
    // Default config has WLYX as null for mainnet per constants
    mockedExistsSync.mockReturnValue(false);

    expect(() => resolveTokenAddress('LYX')).toThrow(UniversalProfileError);
  });

  it('does not treat addresses starting with 0x as token symbols', () => {
    mockedExistsSync.mockReturnValue(false);

    const addr = '0xdeadbeef';
    // Should return as-is, not try to look up as symbol
    expect(resolveTokenAddress(addr)).toBe(addr);
  });
});
