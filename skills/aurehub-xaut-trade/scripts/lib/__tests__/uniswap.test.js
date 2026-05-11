import { describe, it, expect, vi } from 'vitest';
import { AbiCoder } from 'ethers6';
import { quote, buildSwap } from '../uniswap.js';

// QuoterV2 returns (uint256 amountOut, uint160 sqrtPriceX96After, uint32 initializedTicksCrossed, uint256 gasEstimate)
function encodeQuoterResponse({ amountOut, sqrtPriceX96After, initializedTicksCrossed, gasEstimate }) {
  const coder = AbiCoder.defaultAbiCoder();
  return coder.encode(
    ['uint256', 'uint160', 'uint32', 'uint256'],
    [amountOut, sqrtPriceX96After, initializedTicksCrossed, gasEstimate],
  );
}

const TOKEN_WETH = { address: '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', decimals: 18 };
const TOKEN_XAUT = { address: '0x68749665FF8D2d112Fa859AA293F07A622782F38', decimals: 6 };

const CONTRACTS = {
  quoter: '0x61fFE014bA17989E743c5F6cB21bF9697530B21e',
  router: '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45',
};

describe('quote', () => {
  it('returns amountOut, amountOutRaw, sqrtPriceX96, and gasEstimate from QuoterV2', async () => {
    // 1 XAUT (6 decimals) = 1_000_000 raw
    const rawAmountOut = 1_000_000n;
    // 79228162514264337593543950336 = 2^96, the Uniswap V3 sqrtPriceX96 value for price = 1.0
    // sqrtPriceX96 = sqrt(price) * 2^96; at price=1.0 this equals exactly 2^96
    const rawSqrtPrice = 79228162514264337593543950336n;
    const rawGasEstimate = 150_000n;

    const encodedResponse = encodeQuoterResponse({
      amountOut: rawAmountOut,
      sqrtPriceX96After: rawSqrtPrice,
      initializedTicksCrossed: 1,
      gasEstimate: rawGasEstimate,
    });

    const provider = { call: vi.fn().mockResolvedValue(encodedResponse) };

    const result = await quote({
      tokenIn: TOKEN_WETH,
      tokenOut: TOKEN_XAUT,
      amountIn: '1',
      fee: 3000,
      contracts: CONTRACTS,
      provider,
    });

    // provider.call should have been called once with quoter address
    expect(provider.call).toHaveBeenCalledOnce();
    const callArg = provider.call.mock.calls[0][0];
    expect(callArg.to).toBe(CONTRACTS.quoter);
    expect(typeof callArg.data).toBe('string');
    expect(callArg.data.startsWith('0x')).toBe(true);

    // Result shape
    expect(result.amountOutRaw).toBe(rawAmountOut);
    expect(result.amountOut).toBe('1.0'); // 1_000_000 / 10^6
    expect(result.sqrtPriceX96).toBe(rawSqrtPrice);
    expect(result.gasEstimate).toBe(rawGasEstimate);
  });
});

describe('buildSwap', () => {
  it('returns tx params with to, data, and value fields', () => {
    const recipient = '0x' + '1'.repeat(40);
    const deadline = Math.floor(Date.now() / 1000) + 600;

    const result = buildSwap({
      tokenIn: TOKEN_WETH,
      tokenOut: TOKEN_XAUT,
      amountIn: '1',
      minAmountOut: '0.99',
      fee: 3000,
      recipient,
      deadline,
      contracts: CONTRACTS,
    });

    expect(result.to).toBe(CONTRACTS.router);
    expect(typeof result.data).toBe('string');
    expect(result.data.startsWith('0x')).toBe(true);
    expect(result.data.length).toBeGreaterThan(10);
    // value should be a bigint (0 for ERC-20 → ERC-20 swaps)
    expect(typeof result.value).toBe('bigint');
  });

  it('sets value to amountIn in wei for ETH input', () => {
    const TOKEN_ETH = { address: '0x0000000000000000000000000000000000000000', decimals: 18 };
    const recipient = '0x' + '1'.repeat(40);
    const deadline = Math.floor(Date.now() / 1000) + 600;

    const result = buildSwap({
      tokenIn: TOKEN_ETH,
      tokenOut: TOKEN_XAUT,
      amountIn: '1',
      minAmountOut: '0.99',
      fee: 3000,
      recipient,
      deadline,
      contracts: CONTRACTS,
    });

    expect(result.to).toBe(CONTRACTS.router);
    expect(result.value).toBe(1_000_000_000_000_000_000n); // 1 ETH in wei
  });
});
