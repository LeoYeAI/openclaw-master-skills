/**
 * uniswap.js — Quote via QuoterV2 and build swap calldata via SwapRouter02
 *
 * Uses ethers v6 ABI encoding directly instead of @uniswap/v3-sdk SwapRouter
 * to avoid a JSBI class identity mismatch between @uniswap/sdk-core@6 and
 * @uniswap/v3-sdk@3.20 that causes Trade.minimumAmountOut to throw.
 */

import { Interface, AbiCoder, parseUnits } from 'ethers6';

// ---------------------------------------------------------------------------
// ABIs
// ---------------------------------------------------------------------------

const QUOTER_V2_ABI = [
  'function quoteExactInputSingle((address tokenIn, address tokenOut, uint256 amountIn, uint24 fee, uint160 sqrtPriceLimitX96)) external returns (uint256 amountOut, uint160 sqrtPriceX96After, uint32 initializedTicksCrossed, uint256 gasEstimate)',
];

// SwapRouter02 exactInputSingle (used for ERC-20 → ERC-20)
const SWAP_ROUTER_ABI = [
  'function exactInputSingle((address tokenIn, address tokenOut, uint24 fee, address recipient, uint256 amountIn, uint256 amountOutMinimum, uint160 sqrtPriceLimitX96)) external payable returns (uint256 amountOut)',
];

const ZERO_ADDRESS = '0x0000000000000000000000000000000000000000';

// ---------------------------------------------------------------------------
// quote()
// ---------------------------------------------------------------------------

/**
 * Get an on-chain quote from Uniswap V3 QuoterV2.
 *
 * @param {object} params
 * @param {{ address: string, decimals: number }} params.tokenIn
 * @param {{ address: string, decimals: number }} params.tokenOut
 * @param {string} params.amountIn  Human-readable amount (e.g. "1.5")
 * @param {number} params.fee       Pool fee tier (e.g. 3000)
 * @param {{ quoter: string }} params.contracts
 * @param {object} params.provider  ethers-compatible provider
 * @returns {Promise<{ amountOut: string, amountOutRaw: bigint, sqrtPriceX96: bigint, gasEstimate: bigint }>}
 */
export async function quote({ tokenIn, tokenOut, amountIn, fee, contracts, provider }) {
  const iface = new Interface(QUOTER_V2_ABI);

  const amountInRaw = parseUnits(amountIn, tokenIn.decimals);

  const calldata = iface.encodeFunctionData('quoteExactInputSingle', [{
    tokenIn: tokenIn.address,
    tokenOut: tokenOut.address,
    amountIn: amountInRaw,
    fee,
    sqrtPriceLimitX96: 0n,
  }]);

  const raw = await provider.call({ to: contracts.quoter, data: calldata });

  const coder = AbiCoder.defaultAbiCoder();
  const [amountOutRaw, sqrtPriceX96After, , gasEstimate] = coder.decode(
    ['uint256', 'uint160', 'uint32', 'uint256'],
    raw,
  );

  // Convert decoded values to plain bigints (ethers returns BigInt natively in v6)
  const amountOutBig = BigInt(amountOutRaw.toString());
  const sqrtPriceBig = BigInt(sqrtPriceX96After.toString());
  const gasEstimateBig = BigInt(gasEstimate.toString());

  // Format human-readable output
  const divisor = 10n ** BigInt(tokenOut.decimals);
  const whole = amountOutBig / divisor;
  const remainder = amountOutBig % divisor;
  const fracStr = remainder.toString().padStart(tokenOut.decimals, '0').replace(/0+$/, '') || '0';
  const amountOutFormatted = `${whole}.${fracStr}`;

  return {
    amountOut: amountOutFormatted,
    amountOutRaw: amountOutBig,
    sqrtPriceX96: sqrtPriceBig,
    gasEstimate: gasEstimateBig,
  };
}

// ---------------------------------------------------------------------------
// buildSwap()
// ---------------------------------------------------------------------------

/**
 * Build SwapRouter02 exactInputSingle calldata.
 *
 * slippage is already baked into minAmountOut by the caller — we pass it
 * directly as amountOutMinimum.
 *
 * @param {object} params
 * @param {{ address: string, decimals: number }} params.tokenIn
 * @param {{ address: string, decimals: number }} params.tokenOut
 * @param {string} params.amountIn     Human-readable amount in
 * @param {string} params.minAmountOut Human-readable minimum amount out
 * @param {number} params.fee          Pool fee tier
 * @param {string} params.recipient    Recipient address
 * @param {number} params.deadline     Unix timestamp deadline
 * @param {{ router: string }} params.contracts
 * @returns {{ to: string, data: string, value: bigint }}
 */
function truncateDecimals(amount, decimals) {
  const str = String(amount);
  const dot = str.indexOf('.');
  if (dot === -1 || str.length - dot - 1 <= decimals) return str;
  return str.slice(0, dot + 1 + decimals);
}

export function buildSwap({ tokenIn, tokenOut, amountIn, minAmountOut, fee, recipient, deadline, contracts }) {
  const isEth = tokenIn.address === ZERO_ADDRESS;

  const amountInRaw = parseUnits(amountIn, tokenIn.decimals);
  const amountOutMinRaw = parseUnits(truncateDecimals(minAmountOut, tokenOut.decimals), tokenOut.decimals);

  const iface = new Interface(SWAP_ROUTER_ABI);

  // When the input token is native ETH, use WETH address for the swap struct
  // and send value with the transaction. SwapRouter02 handles WETH wrapping.
  const WETH = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2';
  const tokenInAddress = isEth ? WETH : tokenIn.address;

  const data = iface.encodeFunctionData('exactInputSingle', [{
    tokenIn: tokenInAddress,
    tokenOut: tokenOut.address,
    fee,
    recipient,
    amountIn: amountInRaw,
    amountOutMinimum: amountOutMinRaw,
    sqrtPriceLimitX96: 0n,
  }]);

  return {
    to: contracts.router,
    data,
    value: isEth ? amountInRaw : 0n,
  };
}
