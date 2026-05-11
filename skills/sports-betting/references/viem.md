# Viem (minimal)

**Install:** `npm install viem`.  
**Setup:** RPC = `process.env.POLYGON_RPC_URL` or first default from [references/polygon.md](references/polygon.md). Create `publicClient` and `walletClient` from private key + `http(rpcUrl)` + chain `polygon` (from `viem/chains`). Use `privateKeyToAccount` from `viem/accounts`.

- **Balance (POL):** `publicClient.getBalance({ address })` — native gas token on Polygon; use to ensure the wallet can pay for approve and claim txs.
- **Balance (USDT):** `publicClient.readContract({ address: betToken, abi: erc20Abi, functionName: 'balanceOf', args: [bettor] })`. Bet token and 6 decimals from [references/polygon.md](references/polygon.md). Require balance ≥ stake + relayerFeeAmount (from payload) before placing a bet.
- **Allowance:** `publicClient.readContract({ address: betToken, abi: erc20Abi, functionName: 'allowance', args: [bettor, relayer] })`. If result < bet amount + relayerFeeAmount + buffer → approve. Buffer = 0.2 USDT = 200000 (6 decimals).
- **Approve:** Encode `approve(relayer, betAmount + relayerFeeAmount + 200000)` — i.e. stake + relayer fee + 0.2 USDT buffer. The relayer cannot spend more than needed for this bet plus a small buffer. `walletClient.sendTransaction({ to: betToken, data: encodeFunctionData({ abi: erc20Abi, functionName: 'approve', args: [relayer, stake + relayerFeeAmount + 200000n] }) })`. Wait for receipt.
- **Bet sign:** `walletClient.signTypedData({ account, domain: payload.domain, types: payload.types, primaryType, message: payload.signableClientBetData })`. Use `primaryType: 'ClientComboBetData'` if `payload.types.ClientComboBetData` exists, else `'ClientBetData'`. No tx; then POST signature to `payload.apiUrl`.
- **Claim:** `walletClient.sendTransaction({ to: payload.to, data: payload.data, value: 0n, chainId: payload.chainId })`. Wait for receipt.

ERC-20 ABI (minimal): `allowance(address,address) view returns (uint256)`, `approve(address,uint256) returns (bool)`, `balanceOf(address) view returns (uint256)`. Use viem `parseAbi` or equivalent.
