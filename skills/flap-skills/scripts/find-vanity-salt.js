#!/usr/bin/env node
/**
 * 计算 createToken 所需的 _salt（bytes32），使 CREATE2 部署出的代币地址满足 Portal 要求的 vanity 后缀。
 * 文档：https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal
 * - 税收代币 (tax)：后缀 7777
 * - 标准代币 (no tax)：后缀 8888
 */

import { keccak256, toHex, getContractAddress, hexToBytes } from "viem";
import crypto from "crypto";

/**
 * Portal / 实现地址见：https://docs.flap.sh/flap/developers/token-launcher-developers/deployed-contract-addresses
 * Vanity 尾号见：https://docs.flap.sh/flap/developers/token-launcher-developers/launch-token-through-portal#3-find-the-salt-vanity-suffix
 */
const PORTAL_BSC = "0xe2cE6ab80874Fa9Fa2aAE65D277Dd6B8e65C9De0";
const STANDARD_TOKEN_IMPL_BSC = "0x8b4329947e34b6d56d71a3385cac122bade7d78d";
const TAX_TOKEN_V1_IMPL_BSC = "0x29e6383F0ce68507b5A72a53c2B118a118332aA8";
const TAX_TOKEN_V2_IMPL_BSC = "0xae562c6A05b798499507c6276C6Ed796027807BA";

function getInitCode(implAddress) {
  const impl = implAddress.toLowerCase().replace(/^0x/, "").padStart(40, "0");
  return ("0x3d602d80600a3d3981f3363d3d373d3d3d363d73" + impl + "5af43d82803e903d91602b57fd5bf3");
}

function predictTokenAddress(salt, tokenImpl, portal = PORTAL_BSC) {
  const bytecode = getInitCode(tokenImpl);
  const addr = getContractAddress({
    from: portal,
    salt: hexToBytes(salt),
    bytecode,
    opcode: "CREATE2",
  });
  return addr;
}

/**
 * 根据税点与分配选择实现合约与尾号：
 * - 0 税（standard）：尾号 8888，Standard Token Impl
 * - 税收且 mktBps==10000：尾号 7777，Tax Token V1 Impl
 * - 税收且 mktBps<10000：尾号 7777，Tax Token V2 Impl
 */
function getImplAndSuffix(taxRate, mktBps = 10000) {
  if (taxRate === 0) {
    return { suffix: "8888", impl: STANDARD_TOKEN_IMPL_BSC };
  }
  if (mktBps >= 10000) {
    return { suffix: "7777", impl: TAX_TOKEN_V1_IMPL_BSC };
  }
  return { suffix: "7777", impl: TAX_TOKEN_V2_IMPL_BSC };
}

/**
 * 寻找使代币地址以 suffix 结尾的 salt。
 * @param {string} suffix - 4 字符，如 "7777" 或 "8888"
 * @param {string} tokenImpl - Portal 使用的 token 实现地址（8888 用 Standard，7777 用 Tax V1 或 V2）
 */
export function findVanitySalt(suffix = "7777", tokenImpl = TAX_TOKEN_V1_IMPL_BSC, portal = PORTAL_BSC) {
  if (suffix.length !== 4) {
    throw new Error("suffix 必须为 4 个字符，如 7777 或 8888");
  }
  const suffixLower = suffix.toLowerCase();

  let salt = keccak256(toHex(crypto.randomBytes(32)));
  let iterations = 0;

  while (true) {
    const addr = predictTokenAddress(salt, tokenImpl, portal);
    if (addr.toLowerCase().endsWith(suffixLower)) {
      return { salt, address: addr, iterations };
    }
    salt = keccak256(salt);
    iterations++;
    if (iterations % 100000 === 0) {
      process.stdout.write(`\r已尝试 ${iterations} 次...`);
    }
  }
}

async function main() {
  const args = process.argv.slice(2);
  const suffix = (args[0] || "7777").toLowerCase();
  const implArg = (args[1] || "").toLowerCase(); // "v2" 或 "standard" / "8888" 时选对应 impl
  if (!/^[0-9a-f]{4}$/.test(suffix)) {
    console.error("用法: node find-vanity-salt.js <suffix> [impl]");
    console.error("  suffix: 8888 = 0 税标准代币（用 Standard Impl），7777 = 税收代币（用 Tax Impl）");
    console.error("  impl:   可选。7777 时填 v2 表示 Tax V2 Impl（四档分配），不填默认 Tax V1 Impl（全营销）");
    process.exit(1);
  }

  const tokenImpl =
    suffix === "8888"
      ? STANDARD_TOKEN_IMPL_BSC
      : implArg === "v2"
        ? TAX_TOKEN_V2_IMPL_BSC
        : TAX_TOKEN_V1_IMPL_BSC;

  console.log("正在计算 salt（后缀 " + suffix + "，impl: " + (suffix === "8888" ? "Standard" : implArg === "v2" ? "Tax V2" : "Tax V1") + "），请稍候…");
  const { salt, address, iterations } = findVanitySalt(suffix, tokenImpl);
  console.log("\n结果:");
  console.log("  salt (bytes32):", salt);
  console.log("  预测代币地址:  ", address);
  console.log("  迭代次数:      ", iterations);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
