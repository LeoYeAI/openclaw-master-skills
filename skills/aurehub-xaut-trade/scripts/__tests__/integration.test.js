import { describe, it, expect } from 'vitest';

describe('module imports', () => {
  it('imports config', async () => {
    const m = await import('../lib/config.js');
    expect(typeof m.loadConfig).toBe('function');
    expect(typeof m.resolveToken).toBe('function');
  });
  it('imports provider', async () => {
    const m = await import('../lib/provider.js');
    expect(typeof m.createProvider).toBe('function');
    expect(typeof m.FallbackProvider).toBe('function');
  });
  it('imports signer', async () => {
    const m = await import('../lib/signer.js');
    expect(typeof m.createSigner).toBe('function');
  });
  it('imports erc20', async () => {
    const m = await import('../lib/erc20.js');
    expect(typeof m.getBalance).toBe('function');
    expect(typeof m.getAllowance).toBe('function');
    expect(typeof m.approve).toBe('function');
  });
  it('imports uniswap', async () => {
    const m = await import('../lib/uniswap.js');
    expect(typeof m.quote).toBe('function');
    expect(typeof m.buildSwap).toBe('function');
  });
  it('imports swap CLI parser', async () => {
    const m = await import('../swap.js');
    expect(typeof m.parseCliArgs).toBe('function');
  });
});
