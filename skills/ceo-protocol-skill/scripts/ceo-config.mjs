/**
 * CEO Protocol (CEOVault) configuration for Monad mainnet.
 * Used by build-action, build-proposal, and submit-proposal scripts.
 */

import { getAddress } from "viem";

// Monad mainnet addresses
export const CEO_VAULT = getAddress("0xdb60410d2dEef6110e913dc58BBC08F74dc611c4");
export const USDC = getAddress("0x754704Bc059F8C67012fEd69BC8A327a5aafb603");
export const CEO_TOKEN = getAddress("0xCA26f09831A15dCB9f9D47CE1cC2e3B086467777");

// Yield vaults (ERC-4626) — must be added via addYieldVault
export const MORPHO_USDC_VAULT = getAddress("0xbeEFf443C3CbA3E369DA795002243BeaC311aB83");

// Whitelisted targets for approve() spenders and adapter calls
export const WHITELISTED_TARGETS = {
  MORPHO_USDC_VAULT,
  UNISWAP_UNIVERSAL_ROUTER: getAddress("0x0D97Dc33264bfC1c226207428A79b26757fb9dc3"),
  UNISWAP_POOL_MANAGER: getAddress("0x188d586Ddcf52439676Ca21A244753fA19F9Ea8e"),
};
