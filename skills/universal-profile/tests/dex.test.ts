import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ethers } from 'ethers';

// ==================== Mock Setup ====================

// Mock contract instances keyed by rough ABI signature for identification
const mockRouterContract = {
  WETH: vi.fn(),
  getAmountsOut: vi.fn(),
};

const mockFactoryContract = {
  getPair: vi.fn(),
};

const mockPairContract = {
  token0: vi.fn(),
  token1: vi.fn(),
  getReserves: vi.fn(),
  totalSupply: vi.fn(),
  balanceOf: vi.fn(),
};

const mockLSP7TokenContract = {
  authorizedAmountFor: vi.fn(),
};

const mockERC20TokenContract = {
  allowance: vi.fn(),
};

// We need to mock the ethers Contract constructor while keeping everything else real.
// The dex module imports { ethers, Contract, Provider } from 'ethers'.
vi.mock('ethers', async () => {
  const actual = await vi.importActual<typeof import('ethers')>('ethers');

  class MockContract {
    address: string;
    abi: unknown;
    provider: unknown;

    constructor(address: string, abi: unknown, provider: unknown) {
      this.address = address;
      this.abi = abi;
      this.provider = provider;

      const abiStr = JSON.stringify(abi);

      // Identify by ABI content which contract type is being created
      if (abiStr.includes('WETH') && abiStr.includes('swapExactTokensForTokens')) {
        return Object.assign(this, mockRouterContract) as unknown as MockContract;
      }
      if (abiStr.includes('getPair') && abiStr.includes('allPairs')) {
        return Object.assign(this, mockFactoryContract) as unknown as MockContract;
      }
      if (abiStr.includes('getReserves') && abiStr.includes('token0')) {
        return Object.assign(this, mockPairContract) as unknown as MockContract;
      }
      if (abiStr.includes('authorizedAmountFor')) {
        return Object.assign(this, mockLSP7TokenContract) as unknown as MockContract;
      }
      if (abiStr.includes('allowance')) {
        return Object.assign(this, mockERC20TokenContract) as unknown as MockContract;
      }

      return this;
    }
  }

  return {
    ...actual,
    Contract: MockContract,
  };
});

// Import AFTER mock is set up
import {
  getSwapQuote,
  getQuoteWithSlippage,
  getPoolInfo,
  getLPBalance,
  needsRouterApproval,
  calculateMinOutput,
  getDeadline,
  encodeSwapExactTokensForTokens,
  encodeSwapExactETHForTokens,
  encodeSwapExactTokensForETH,
  encodeAddLiquidity,
  encodeAddLiquidityETH,
  encodeRemoveLiquidity,
  encodeLPApproval,
} from '../../src/lib/dex.js';

// ==================== Test Constants ====================

const ROUTER = '0x1111111111111111111111111111111111111111';
const FACTORY = '0x2222222222222222222222222222222222222222';
const TOKEN_A = '0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA';
const TOKEN_B = '0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB';
const WETH = '0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC';
const PAIR = '0xDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD';
const RECIPIENT = '0xEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE';
const OWNER = '0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF';
const FAKE_PROVIDER = {} as ethers.Provider;

// ==================== Tests ====================

describe('DEX Module', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // ==================== Pure Calculation Functions ====================

  describe('calculateMinOutput', () => {
    it('should apply 0.5% slippage correctly', () => {
      // 1000 - (1000 * 50 / 10000) = 1000 - 5 = 995
      const result = calculateMinOutput(1000n, 0.5);
      expect(result).toBe(995n);
    });

    it('should apply 1% slippage correctly', () => {
      // 10000 - (10000 * 100 / 10000) = 10000 - 100 = 9900
      const result = calculateMinOutput(10000n, 1);
      expect(result).toBe(9900n);
    });

    it('should apply 0% slippage (no change)', () => {
      const result = calculateMinOutput(1000n, 0);
      expect(result).toBe(1000n);
    });

    it('should apply 100% slippage (zero output)', () => {
      const result = calculateMinOutput(1000n, 100);
      expect(result).toBe(0n);
    });

    it('should apply 5% slippage correctly', () => {
      // 2000 - (2000 * 500 / 10000) = 2000 - 100 = 1900
      const result = calculateMinOutput(2000n, 5);
      expect(result).toBe(1900n);
    });

    it('should handle large amounts', () => {
      const amount = 1000000000000000000n; // 1e18
      // 1e18 - (1e18 * 50 / 10000) = 1e18 - 5e15 = 995000000000000000
      const result = calculateMinOutput(amount, 0.5);
      expect(result).toBe(995000000000000000n);
    });

    it('should handle zero amount', () => {
      const result = calculateMinOutput(0n, 0.5);
      expect(result).toBe(0n);
    });

    it('should handle fractional slippage like 0.3%', () => {
      // slippageBps = Math.floor(0.3 * 100) = 30
      // 10000 - (10000 * 30 / 10000) = 10000 - 30 = 9970
      const result = calculateMinOutput(10000n, 0.3);
      expect(result).toBe(9970n);
    });
  });

  describe('getDeadline', () => {
    let dateNowSpy: ReturnType<typeof vi.spyOn>;

    beforeEach(() => {
      dateNowSpy = vi.spyOn(Date, 'now').mockReturnValue(1700000000000); // fixed timestamp in ms
    });

    afterEach(() => {
      dateNowSpy.mockRestore();
    });

    it('should return default deadline (1200 seconds from now)', () => {
      const result = getDeadline();
      const expectedTimestamp = Math.floor(1700000000000 / 1000) + 1200;
      expect(result).toBe(expectedTimestamp);
    });

    it('should return custom deadline with provided seconds', () => {
      const result = getDeadline(600);
      const expectedTimestamp = Math.floor(1700000000000 / 1000) + 600;
      expect(result).toBe(expectedTimestamp);
    });

    it('should return deadline 0 seconds from now (current time)', () => {
      const result = getDeadline(0);
      const expectedTimestamp = Math.floor(1700000000000 / 1000);
      expect(result).toBe(expectedTimestamp);
    });

    it('should return deadline far in the future', () => {
      const result = getDeadline(86400); // 24 hours
      const expectedTimestamp = Math.floor(1700000000000 / 1000) + 86400;
      expect(result).toBe(expectedTimestamp);
    });

    it('should be a unix timestamp (seconds, not milliseconds)', () => {
      const result = getDeadline();
      // Should be in the range of seconds, not milliseconds
      expect(result).toBeLessThan(10000000000); // less than year 2286 in seconds
      expect(result).toBeGreaterThan(1000000000); // greater than 2001 in seconds
    });
  });

  // ==================== Encoding Functions ====================

  describe('encodeSwapExactTokensForTokens', () => {
    it('should return correct ExecuteParams shape', () => {
      const params = {
        tokenIn: TOKEN_A,
        tokenOut: TOKEN_B,
        amountIn: 1000n,
        amountOutMin: 950n,
        deadline: 1700001200,
      };

      const result = encodeSwapExactTokensForTokens(ROUTER, params, RECIPIENT);

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(ROUTER);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x[0-9a-fA-F]+$/);
    });

    it('should use default path [tokenIn, tokenOut] when no path provided', () => {
      const params = {
        tokenIn: TOKEN_A,
        tokenOut: TOKEN_B,
        amountIn: 1000n,
        amountOutMin: 950n,
        deadline: 1700001200,
      };

      const result = encodeSwapExactTokensForTokens(ROUTER, params, RECIPIENT);

      // Decode the data to verify the path
      const iface = new ethers.Interface([
        'function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline)',
      ]);
      const decoded = iface.decodeFunctionData('swapExactTokensForTokens', result.data);
      expect(decoded[0]).toBe(1000n);
      expect(decoded[1]).toBe(950n);
      expect(decoded[2][0].toLowerCase()).toBe(TOKEN_A.toLowerCase());
      expect(decoded[2][1].toLowerCase()).toBe(TOKEN_B.toLowerCase());
      expect(decoded[3].toLowerCase()).toBe(RECIPIENT.toLowerCase());
      expect(decoded[4]).toBe(BigInt(1700001200));
    });

    it('should use custom path when provided', () => {
      const customPath = [TOKEN_A, WETH, TOKEN_B];
      const params = {
        tokenIn: TOKEN_A,
        tokenOut: TOKEN_B,
        amountIn: 1000n,
        amountOutMin: 900n,
        deadline: 1700001200,
        path: customPath,
      };

      const result = encodeSwapExactTokensForTokens(ROUTER, params, RECIPIENT);

      const iface = new ethers.Interface([
        'function swapExactTokensForTokens(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline)',
      ]);
      const decoded = iface.decodeFunctionData('swapExactTokensForTokens', result.data);
      expect(decoded[2].length).toBe(3);
      expect(decoded[2][0].toLowerCase()).toBe(TOKEN_A.toLowerCase());
      expect(decoded[2][1].toLowerCase()).toBe(WETH.toLowerCase());
      expect(decoded[2][2].toLowerCase()).toBe(TOKEN_B.toLowerCase());
    });

    it('should have value of 0n for token-to-token swaps', () => {
      const params = {
        tokenIn: TOKEN_A,
        tokenOut: TOKEN_B,
        amountIn: 5000n,
        amountOutMin: 4500n,
        deadline: 1700001200,
      };

      const result = encodeSwapExactTokensForTokens(ROUTER, params, RECIPIENT);
      expect(result.value).toBe(0n);
    });
  });

  describe('encodeSwapExactETHForTokens', () => {
    it('should return correct ExecuteParams shape', () => {
      const amountIn = 1000000000000000000n; // 1 ETH/LYX
      const amountOutMin = 950n;
      const path = [WETH, TOKEN_A];
      const deadline = 1700001200;

      const result = encodeSwapExactETHForTokens(
        ROUTER,
        amountIn,
        amountOutMin,
        path,
        RECIPIENT,
        deadline
      );

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(ROUTER);
      expect(result.value).toBe(amountIn);
      expect(result.data).toMatch(/^0x[0-9a-fA-F]+$/);
    });

    it('should set value equal to amountIn (native token being sent)', () => {
      const amountIn = 5000000000000000000n; // 5 ETH
      const result = encodeSwapExactETHForTokens(
        ROUTER,
        amountIn,
        100n,
        [WETH, TOKEN_A],
        RECIPIENT,
        1700001200
      );
      expect(result.value).toBe(amountIn);
    });

    it('should encode correct function data', () => {
      const amountIn = 1000n;
      const amountOutMin = 900n;
      const path = [WETH, TOKEN_A];
      const deadline = 1700001200;

      const result = encodeSwapExactETHForTokens(
        ROUTER,
        amountIn,
        amountOutMin,
        path,
        RECIPIENT,
        deadline
      );

      const iface = new ethers.Interface([
        'function swapExactETHForTokens(uint amountOutMin, address[] calldata path, address to, uint deadline)',
      ]);
      const decoded = iface.decodeFunctionData('swapExactETHForTokens', result.data);
      expect(decoded[0]).toBe(amountOutMin);
      expect(decoded[1][0].toLowerCase()).toBe(WETH.toLowerCase());
      expect(decoded[1][1].toLowerCase()).toBe(TOKEN_A.toLowerCase());
      expect(decoded[2].toLowerCase()).toBe(RECIPIENT.toLowerCase());
      expect(decoded[3]).toBe(BigInt(deadline));
    });
  });

  describe('encodeSwapExactTokensForETH', () => {
    it('should return correct ExecuteParams shape', () => {
      const result = encodeSwapExactTokensForETH(
        ROUTER,
        1000n,
        900n,
        [TOKEN_A, WETH],
        RECIPIENT,
        1700001200
      );

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(ROUTER);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x[0-9a-fA-F]+$/);
    });

    it('should have value of 0n (selling tokens, not sending native)', () => {
      const result = encodeSwapExactTokensForETH(
        ROUTER,
        5000n,
        4500n,
        [TOKEN_A, WETH],
        RECIPIENT,
        1700001200
      );
      expect(result.value).toBe(0n);
    });

    it('should encode correct function data', () => {
      const amountIn = 2000n;
      const amountOutMin = 1800n;
      const path = [TOKEN_A, WETH];
      const deadline = 1700001200;

      const result = encodeSwapExactTokensForETH(
        ROUTER,
        amountIn,
        amountOutMin,
        path,
        RECIPIENT,
        deadline
      );

      const iface = new ethers.Interface([
        'function swapExactTokensForETH(uint amountIn, uint amountOutMin, address[] calldata path, address to, uint deadline)',
      ]);
      const decoded = iface.decodeFunctionData('swapExactTokensForETH', result.data);
      expect(decoded[0]).toBe(amountIn);
      expect(decoded[1]).toBe(amountOutMin);
      expect(decoded[2][0].toLowerCase()).toBe(TOKEN_A.toLowerCase());
      expect(decoded[2][1].toLowerCase()).toBe(WETH.toLowerCase());
      expect(decoded[3].toLowerCase()).toBe(RECIPIENT.toLowerCase());
      expect(decoded[4]).toBe(BigInt(deadline));
    });
  });

  describe('encodeAddLiquidity', () => {
    it('should return correct ExecuteParams shape', () => {
      const params = {
        tokenA: TOKEN_A,
        tokenB: TOKEN_B,
        amountADesired: 1000n,
        amountBDesired: 2000n,
        amountAMin: 950n,
        amountBMin: 1900n,
        deadline: 1700001200,
      };

      const result = encodeAddLiquidity(ROUTER, params, RECIPIENT);

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(ROUTER);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x[0-9a-fA-F]+$/);
    });

    it('should encode correct function data with all parameters', () => {
      const params = {
        tokenA: TOKEN_A,
        tokenB: TOKEN_B,
        amountADesired: 5000n,
        amountBDesired: 10000n,
        amountAMin: 4500n,
        amountBMin: 9000n,
        deadline: 1700001200,
      };

      const result = encodeAddLiquidity(ROUTER, params, RECIPIENT);

      const iface = new ethers.Interface([
        'function addLiquidity(address tokenA, address tokenB, uint amountADesired, uint amountBDesired, uint amountAMin, uint amountBMin, address to, uint deadline)',
      ]);
      const decoded = iface.decodeFunctionData('addLiquidity', result.data);
      expect(decoded[0].toLowerCase()).toBe(TOKEN_A.toLowerCase());
      expect(decoded[1].toLowerCase()).toBe(TOKEN_B.toLowerCase());
      expect(decoded[2]).toBe(5000n);
      expect(decoded[3]).toBe(10000n);
      expect(decoded[4]).toBe(4500n);
      expect(decoded[5]).toBe(9000n);
      expect(decoded[6].toLowerCase()).toBe(RECIPIENT.toLowerCase());
      expect(decoded[7]).toBe(BigInt(1700001200));
    });

    it('should have value of 0n for token-token liquidity', () => {
      const params = {
        tokenA: TOKEN_A,
        tokenB: TOKEN_B,
        amountADesired: 1000n,
        amountBDesired: 2000n,
        amountAMin: 950n,
        amountBMin: 1900n,
        deadline: 1700001200,
      };

      const result = encodeAddLiquidity(ROUTER, params, RECIPIENT);
      expect(result.value).toBe(0n);
    });
  });

  describe('encodeAddLiquidityETH', () => {
    it('should return correct ExecuteParams shape', () => {
      const amountETH = 1000000000000000000n; // 1 LYX

      const result = encodeAddLiquidityETH(
        ROUTER,
        TOKEN_A,
        5000n,  // amountTokenDesired
        4500n,  // amountTokenMin
        900n,   // amountETHMin
        amountETH,
        RECIPIENT,
        1700001200
      );

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(ROUTER);
      expect(result.value).toBe(amountETH);
      expect(result.data).toMatch(/^0x[0-9a-fA-F]+$/);
    });

    it('should set value equal to amountETH (native token being sent)', () => {
      const amountETH = 3000000000000000000n;

      const result = encodeAddLiquidityETH(
        ROUTER,
        TOKEN_A,
        5000n,
        4500n,
        2700n,
        amountETH,
        RECIPIENT,
        1700001200
      );

      expect(result.value).toBe(amountETH);
    });

    it('should encode correct function data', () => {
      const result = encodeAddLiquidityETH(
        ROUTER,
        TOKEN_A,
        5000n,  // amountTokenDesired
        4500n,  // amountTokenMin
        900n,   // amountETHMin
        1000n,  // amountETH
        RECIPIENT,
        1700001200
      );

      const iface = new ethers.Interface([
        'function addLiquidityETH(address token, uint amountTokenDesired, uint amountTokenMin, uint amountETHMin, address to, uint deadline)',
      ]);
      const decoded = iface.decodeFunctionData('addLiquidityETH', result.data);
      expect(decoded[0].toLowerCase()).toBe(TOKEN_A.toLowerCase());
      expect(decoded[1]).toBe(5000n);
      expect(decoded[2]).toBe(4500n);
      expect(decoded[3]).toBe(900n);
      expect(decoded[4].toLowerCase()).toBe(RECIPIENT.toLowerCase());
      expect(decoded[5]).toBe(BigInt(1700001200));
    });
  });

  describe('encodeRemoveLiquidity', () => {
    it('should return correct ExecuteParams shape', () => {
      const result = encodeRemoveLiquidity(
        ROUTER,
        TOKEN_A,
        TOKEN_B,
        1000n,  // liquidity
        450n,   // amountAMin
        900n,   // amountBMin
        RECIPIENT,
        1700001200
      );

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(ROUTER);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x[0-9a-fA-F]+$/);
    });

    it('should encode correct function data', () => {
      const result = encodeRemoveLiquidity(
        ROUTER,
        TOKEN_A,
        TOKEN_B,
        500n,
        200n,
        300n,
        RECIPIENT,
        1700001200
      );

      const iface = new ethers.Interface([
        'function removeLiquidity(address tokenA, address tokenB, uint liquidity, uint amountAMin, uint amountBMin, address to, uint deadline)',
      ]);
      const decoded = iface.decodeFunctionData('removeLiquidity', result.data);
      expect(decoded[0].toLowerCase()).toBe(TOKEN_A.toLowerCase());
      expect(decoded[1].toLowerCase()).toBe(TOKEN_B.toLowerCase());
      expect(decoded[2]).toBe(500n);
      expect(decoded[3]).toBe(200n);
      expect(decoded[4]).toBe(300n);
      expect(decoded[5].toLowerCase()).toBe(RECIPIENT.toLowerCase());
      expect(decoded[6]).toBe(BigInt(1700001200));
    });

    it('should have value of 0n', () => {
      const result = encodeRemoveLiquidity(
        ROUTER,
        TOKEN_A,
        TOKEN_B,
        1000n,
        450n,
        900n,
        RECIPIENT,
        1700001200
      );
      expect(result.value).toBe(0n);
    });
  });

  describe('encodeLPApproval', () => {
    it('should return correct ExecuteParams shape', () => {
      const result = encodeLPApproval(PAIR, ROUTER, 1000n);

      expect(result.operationType).toBe(0);
      expect(result.target).toBe(PAIR);
      expect(result.value).toBe(0n);
      expect(result.data).toMatch(/^0x[0-9a-fA-F]+$/);
    });

    it('should encode approve function correctly', () => {
      const amount = 999999999999n;
      const result = encodeLPApproval(PAIR, ROUTER, amount);

      const iface = new ethers.Interface([
        'function approve(address spender, uint value) external returns (bool)',
      ]);
      const decoded = iface.decodeFunctionData('approve', result.data);
      expect(decoded[0].toLowerCase()).toBe(ROUTER.toLowerCase());
      expect(decoded[1]).toBe(amount);
    });

    it('should target the pair address, not the router', () => {
      const result = encodeLPApproval(PAIR, ROUTER, 1000n);
      expect(result.target).toBe(PAIR);
    });

    it('should have value of 0n', () => {
      const result = encodeLPApproval(PAIR, ROUTER, 1000n);
      expect(result.value).toBe(0n);
    });
  });

  // ==================== Query Functions (Mocked Contract) ====================

  describe('getSwapQuote', () => {
    it('should return a SwapQuote with direct pair path', async () => {
      mockFactoryContract.getPair.mockResolvedValue(PAIR);
      mockRouterContract.WETH.mockResolvedValue(WETH);
      mockRouterContract.getAmountsOut.mockResolvedValue([1000n, 950n]);

      // For price impact calculation: getPair returns PAIR, then pair methods called
      mockPairContract.getReserves.mockResolvedValue([100000n, 200000n, 0]);
      mockPairContract.token0.mockResolvedValue(TOKEN_A);

      const quote = await getSwapQuote(
        ROUTER,
        FACTORY,
        TOKEN_A,
        TOKEN_B,
        1000n,
        FAKE_PROVIDER
      );

      expect(quote.amountIn).toBe(1000n);
      expect(quote.amountOut).toBe(950n);
      expect(quote.path).toEqual([TOKEN_A, TOKEN_B]);
      expect(typeof quote.priceImpact).toBe('number');
      expect(typeof quote.executionPrice).toBe('number');
    });

    it('should route through WETH when no direct pair exists', async () => {
      // First getPair call (direct) returns zero address
      mockFactoryContract.getPair
        .mockResolvedValueOnce(ethers.ZeroAddress)  // direct pair check
        .mockResolvedValueOnce(PAIR);               // for price impact

      mockRouterContract.WETH.mockResolvedValue(WETH);
      mockRouterContract.getAmountsOut.mockResolvedValue([1000n, 500n, 900n]);

      mockPairContract.getReserves.mockResolvedValue([100000n, 200000n, 0]);
      mockPairContract.token0.mockResolvedValue(TOKEN_A);

      const quote = await getSwapQuote(
        ROUTER,
        FACTORY,
        TOKEN_A,
        TOKEN_B,
        1000n,
        FAKE_PROVIDER
      );

      expect(quote.path).toEqual([TOKEN_A, WETH, TOKEN_B]);
      expect(quote.amountOut).toBe(900n);
    });

    it('should calculate execution price as amountOut / amountIn', async () => {
      mockFactoryContract.getPair.mockResolvedValue(PAIR);
      mockRouterContract.WETH.mockResolvedValue(WETH);
      mockRouterContract.getAmountsOut.mockResolvedValue([2000n, 4000n]);

      mockPairContract.getReserves.mockResolvedValue([100000n, 200000n, 0]);
      mockPairContract.token0.mockResolvedValue(TOKEN_A);

      const quote = await getSwapQuote(
        ROUTER,
        FACTORY,
        TOKEN_A,
        TOKEN_B,
        2000n,
        FAKE_PROVIDER
      );

      expect(quote.executionPrice).toBe(2); // 4000 / 2000
    });
  });

  describe('getQuoteWithSlippage', () => {
    it('should return both quote and minAmountOut', async () => {
      mockFactoryContract.getPair.mockResolvedValue(PAIR);
      mockRouterContract.WETH.mockResolvedValue(WETH);
      mockRouterContract.getAmountsOut.mockResolvedValue([1000n, 10000n]);

      mockPairContract.getReserves.mockResolvedValue([1000000n, 2000000n, 0]);
      mockPairContract.token0.mockResolvedValue(TOKEN_A);

      const result = await getQuoteWithSlippage(
        ROUTER,
        FACTORY,
        TOKEN_A,
        TOKEN_B,
        1000n,
        0.5,
        FAKE_PROVIDER
      );

      expect(result.quote).toBeDefined();
      expect(result.quote.amountOut).toBe(10000n);
      expect(result.minAmountOut).toBe(calculateMinOutput(10000n, 0.5));
      expect(result.minAmountOut).toBe(9950n);
    });

    it('should apply higher slippage correctly', async () => {
      mockFactoryContract.getPair.mockResolvedValue(PAIR);
      mockRouterContract.WETH.mockResolvedValue(WETH);
      mockRouterContract.getAmountsOut.mockResolvedValue([1000n, 5000n]);

      mockPairContract.getReserves.mockResolvedValue([1000000n, 2000000n, 0]);
      mockPairContract.token0.mockResolvedValue(TOKEN_A);

      const result = await getQuoteWithSlippage(
        ROUTER,
        FACTORY,
        TOKEN_A,
        TOKEN_B,
        1000n,
        5,
        FAKE_PROVIDER
      );

      // 5000 - (5000 * 500 / 10000) = 5000 - 250 = 4750
      expect(result.minAmountOut).toBe(4750n);
    });
  });

  describe('getPoolInfo', () => {
    it('should return PoolInfo when pair exists', async () => {
      mockFactoryContract.getPair.mockResolvedValue(PAIR);
      mockPairContract.token0.mockResolvedValue(TOKEN_A);
      mockPairContract.token1.mockResolvedValue(TOKEN_B);
      mockPairContract.getReserves.mockResolvedValue([50000n, 100000n, 0]);
      mockPairContract.totalSupply.mockResolvedValue(70000n);

      const info = await getPoolInfo(FACTORY, TOKEN_A, TOKEN_B, FAKE_PROVIDER);

      expect(info).not.toBeNull();
      expect(info!.pairAddress).toBe(PAIR);
      expect(info!.token0).toBe(TOKEN_A);
      expect(info!.token1).toBe(TOKEN_B);
      expect(info!.reserve0).toBe(50000n);
      expect(info!.reserve1).toBe(100000n);
      expect(info!.totalSupply).toBe(70000n);
    });

    it('should return null when pair does not exist', async () => {
      mockFactoryContract.getPair.mockResolvedValue(ethers.ZeroAddress);

      const info = await getPoolInfo(FACTORY, TOKEN_A, TOKEN_B, FAKE_PROVIDER);

      expect(info).toBeNull();
    });
  });

  describe('getLPBalance', () => {
    it('should return the LP balance for a holder', async () => {
      mockPairContract.balanceOf.mockResolvedValue(12345n);

      const balance = await getLPBalance(PAIR, OWNER, FAKE_PROVIDER);

      expect(balance).toBe(12345n);
    });

    it('should return 0n when holder has no LP tokens', async () => {
      mockPairContract.balanceOf.mockResolvedValue(0n);

      const balance = await getLPBalance(PAIR, OWNER, FAKE_PROVIDER);

      expect(balance).toBe(0n);
    });
  });

  describe('needsRouterApproval', () => {
    it('should return false when LSP7 authorizedAmountFor is sufficient', async () => {
      mockLSP7TokenContract.authorizedAmountFor.mockResolvedValue(5000n);

      const result = await needsRouterApproval(
        TOKEN_A,
        OWNER,
        ROUTER,
        1000n,
        FAKE_PROVIDER
      );

      expect(result).toBe(false);
    });

    it('should return true when LSP7 authorizedAmountFor is insufficient', async () => {
      mockLSP7TokenContract.authorizedAmountFor.mockResolvedValue(500n);

      const result = await needsRouterApproval(
        TOKEN_A,
        OWNER,
        ROUTER,
        1000n,
        FAKE_PROVIDER
      );

      expect(result).toBe(true);
    });

    it('should fall back to ERC20 allowance when authorizedAmountFor throws', async () => {
      mockLSP7TokenContract.authorizedAmountFor.mockRejectedValue(new Error('not LSP7'));
      mockERC20TokenContract.allowance.mockResolvedValue(2000n);

      const result = await needsRouterApproval(
        TOKEN_A,
        OWNER,
        ROUTER,
        1000n,
        FAKE_PROVIDER
      );

      expect(result).toBe(false);
    });

    it('should return true when ERC20 allowance is insufficient', async () => {
      mockLSP7TokenContract.authorizedAmountFor.mockRejectedValue(new Error('not LSP7'));
      mockERC20TokenContract.allowance.mockResolvedValue(100n);

      const result = await needsRouterApproval(
        TOKEN_A,
        OWNER,
        ROUTER,
        1000n,
        FAKE_PROVIDER
      );

      expect(result).toBe(true);
    });

    it('should return true when both authorizedAmountFor and allowance throw', async () => {
      mockLSP7TokenContract.authorizedAmountFor.mockRejectedValue(new Error('not LSP7'));
      mockERC20TokenContract.allowance.mockRejectedValue(new Error('not ERC20'));

      const result = await needsRouterApproval(
        TOKEN_A,
        OWNER,
        ROUTER,
        1000n,
        FAKE_PROVIDER
      );

      expect(result).toBe(true);
    });

    it('should return false when authorized amount equals the requested amount exactly', async () => {
      mockLSP7TokenContract.authorizedAmountFor.mockResolvedValue(1000n);

      const result = await needsRouterApproval(
        TOKEN_A,
        OWNER,
        ROUTER,
        1000n,
        FAKE_PROVIDER
      );

      // 1000 < 1000 is false, so approval is not needed
      expect(result).toBe(false);
    });
  });
});
