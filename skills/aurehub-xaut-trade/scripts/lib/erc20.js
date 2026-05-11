import { Interface, formatUnits, parseUnits } from 'ethers6';

const ERC20_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function allowance(address,address) view returns (uint256)',
  'function approve(address,uint256) returns (bool)',
];

const iface = new Interface(ERC20_ABI);

/**
 * Get the token balance of an address.
 *
 * @param {{ address: string, decimals: number }} token
 * @param {string} address
 * @param {object} provider  ethers provider (or compatible mock with .call())
 * @returns {Promise<string>}  Human-readable balance formatted with token decimals
 */
export async function getBalance(token, address, provider) {
  const data = iface.encodeFunctionData('balanceOf', [address]);
  const raw = await provider.call({ to: token.address, data });
  const [value] = iface.decodeFunctionResult('balanceOf', raw);
  return formatUnits(value, token.decimals);
}

/**
 * Get the ERC-20 allowance granted by owner to spender.
 *
 * @param {{ address: string, decimals: number }} token
 * @param {string} owner
 * @param {string} spender
 * @param {object} provider
 * @returns {Promise<string>}  Human-readable allowance formatted with token decimals
 */
export async function getAllowance(token, owner, spender, provider) {
  const data = iface.encodeFunctionData('allowance', [owner, spender]);
  const raw = await provider.call({ to: token.address, data });
  const [value] = iface.decodeFunctionResult('allowance', raw);
  return formatUnits(value, token.decimals);
}

/**
 * Approve a spender to transfer tokens on behalf of the signer.
 *
 * For tokens like USDT that revert when changing a non-zero allowance directly,
 * pass `opts.requiresResetApprove = true` to first reset to 0 before setting the
 * new value.
 *
 * @param {{ address: string, decimals: number }} token
 * @param {string} spender
 * @param {string} amount  Human-readable amount (e.g. "1000")
 * @param {object} signer  ethers signer (or compatible mock)
 * @param {{ requiresResetApprove?: boolean, fallbackProvider?: object }} opts
 * @returns {Promise<{ hash: string }>}
 */
export async function approve(token, spender, amount, signer, opts = {}) {
  const rawAmount = parseUnits(amount, token.decimals);
  const timeoutMs = (opts.timeoutSeconds ?? 300) * 1000;
  const waitForReceipt = async (sentTx) => {
    // Use fallbackProvider.waitForTransaction when available for RPC resilience
    if (opts.fallbackProvider?.waitForTransaction) {
      return Promise.race([
        opts.fallbackProvider.waitForTransaction(sentTx.hash, 1, timeoutMs),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error(
            `Approve tx not confirmed within ${timeoutMs / 1000}s (txHash: ${sentTx.hash}). It may still be pending.`
          )), timeoutMs)
        ),
      ]);
    }
    return Promise.race([
      sentTx.wait(),
      new Promise((_, reject) =>
        setTimeout(() => reject(new Error(
          `Approve tx not confirmed within ${timeoutMs / 1000}s (txHash: ${sentTx.hash}). It may still be pending.`
        )), timeoutMs)
      ),
    ]);
  };

  if (opts.requiresResetApprove) {
    const resetData = iface.encodeFunctionData('approve', [spender, 0n]);
    const resetTx = await signer.sendTransaction({ to: token.address, data: resetData });
    const resetReceipt = await waitForReceipt(resetTx);
    if (!resetReceipt || resetReceipt.status !== 1) {
      throw new Error(`Allowance reset failed (txHash: ${resetTx.hash}). Approval not sent.`);
    }
  }

  const data = iface.encodeFunctionData('approve', [spender, rawAmount]);
  const tx = await signer.sendTransaction({ to: token.address, data });
  const receipt = await waitForReceipt(tx);
  if (!receipt || receipt.status !== 1) {
    throw new Error(`Approval failed (txHash: ${tx.hash}). Check token contract and allowance.`);
  }

  return { hash: tx.hash };
}
