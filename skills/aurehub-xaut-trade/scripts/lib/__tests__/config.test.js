import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { mkdirSync, rmSync, writeFileSync } from 'fs';
import { join } from 'path';
import { tmpdir } from 'os';
import { loadConfig, resolveToken } from '../config.js';

let testDir;

beforeEach(() => {
  testDir = join(tmpdir(), `config-test-${Date.now()}-${Math.random().toString(36).slice(2)}`);
  mkdirSync(testDir, { recursive: true });
});

afterEach(() => {
  rmSync(testDir, { recursive: true, force: true });
});

describe('loadConfig', () => {
  it('parses .env file correctly (key=value, ignores comments and blanks)', () => {
    const envContent = [
      '# This is a comment',
      '',
      'PRIVATE_KEY=0xdeadbeef',
      '  ',
      'RPC_URL=https://mainnet.example.com',
      '# another comment',
      'QUOTED_VAL="hello world"',
      "SINGLE_QUOTED='foo bar'",
    ].join('\n');

    writeFileSync(join(testDir, '.env'), envContent);

    const config = loadConfig(testDir);

    expect(config.env.PRIVATE_KEY).toBe('0xdeadbeef');
    expect(config.env.RPC_URL).toBe('https://mainnet.example.com');
    expect(config.env.QUOTED_VAL).toBe('hello world');
    expect(config.env.SINGLE_QUOTED).toBe('foo bar');
    expect(Object.keys(config.env)).not.toContain('');
  });

  it('resolves token symbol to address and decimals via resolveToken', () => {
    const yamlContent = [
      'tokens:',
      '  USDT:',
      '    address: "0xdAC17F958D2ee523a2206206994597C13D831ec7"',
      '    decimals: 6',
      '  XAUT:',
      '    address: "0x68749665FF8D2d112Fa859AA293F07A622782F38"',
      '    decimals: 6',
    ].join('\n');

    writeFileSync(join(testDir, 'config.yaml'), yamlContent);

    const config = loadConfig(testDir);
    const token = resolveToken(config, 'USDT');

    expect(token.address).toBe('0xdAC17F958D2ee523a2206206994597C13D831ec7');
    expect(token.decimals).toBe(6);
  });

  it('throws on unknown token symbol', () => {
    const yamlContent = [
      'tokens:',
      '  USDT:',
      '    address: "0xdAC17F958D2ee523a2206206994597C13D831ec7"',
      '    decimals: 6',
    ].join('\n');

    writeFileSync(join(testDir, 'config.yaml'), yamlContent);

    const config = loadConfig(testDir);

    expect(() => resolveToken(config, 'UNKNOWN')).toThrow(/unknown token/i);
  });

  it('returns undefined wallet_mode when not set in yaml', () => {
    const yamlContent = [
      'tokens:',
      '  USDT:',
      '    address: "0xdAC17F958D2ee523a2206206994597C13D831ec7"',
      '    decimals: 6',
    ].join('\n');

    writeFileSync(join(testDir, 'config.yaml'), yamlContent);

    const config = loadConfig(testDir);

    expect(config.yaml.wallet_mode).toBeUndefined();
  });

  it('silently returns empty objects when files do not exist', () => {
    // testDir exists but has no .env or config.yaml
    const config = loadConfig(testDir);

    expect(config.env).toEqual({});
    expect(config.yaml).toEqual({});
    expect(config.configDir).toBe(testDir);
  });
});
