const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

const IN = process.env.IN_FILE || 'order.json';

const RPC = process.env.RPC_URL || 'https://mainnet.base.org';
const SWAP_DEFAULT = '0x8a9969ed0A9bb3cDA7521DDaA614aE86e72e0A57';
const SWAP_ERC721 = '0x2aa29F096257bc6B253bfA9F6404B20Ae0ef9C4d';
const SWAP_ERC1155 = '0xD19783B48b11AFE1544b001c6d807A513e5A95cf';
const KIND_ERC20 = '0x36372b07';
const KIND_ERC721 = '0x80ac58cd';
const KIND_ERC1155 = '0xd9b67a26';

const SENDER_PRIVATE_KEY = process.env.SENDER_PRIVATE_KEY;
if (!SENDER_PRIVATE_KEY) {
  console.error('Missing SENDER_PRIVATE_KEY');
  process.exit(1);
}

const ERC20_ABI = [
  'function approve(address spender,uint256 amount) returns (bool)',
  'function allowance(address owner,address spender) view returns (uint256)',
  'function balanceOf(address owner) view returns (uint256)',
  'function decimals() view returns (uint8)',
];

const SWAP_ABI = [
  'function protocolFee() view returns (uint256)',
  'function requiredSenderKind() view returns (bytes4)',
  'function protocolFeeWallet() view returns (address)',
  'function swap(address recipient,uint256 maxRoyalty,(uint256 nonce,uint256 expiry,(address wallet,address token,bytes4 kind,uint256 id,uint256 amount) signer,(address wallet,address token,bytes4 kind,uint256 id,uint256 amount) sender,address affiliateWallet,uint256 affiliateAmount,uint8 v,bytes32 r,bytes32 s) order) external',
];

const ORDER_TYPES = {
  Order: [
    { name: 'nonce', type: 'uint256' },
    { name: 'expiry', type: 'uint256' },
    { name: 'protocolFee', type: 'uint256' },
    { name: 'signer', type: 'Party' },
    { name: 'sender', type: 'Party' },
    { name: 'affiliateWallet', type: 'address' },
    { name: 'affiliateAmount', type: 'uint256' },
  ],
  Party: [
    { name: 'wallet', type: 'address' },
    { name: 'token', type: 'address' },
    { name: 'kind', type: 'bytes4' },
    { name: 'id', type: 'uint256' },
    { name: 'amount', type: 'uint256' },
  ],
};

function getMaxGasLimit() {
  return ethers.BigNumber.from(process.env.MAX_GAS_LIMIT || '650000');
}


function resolveSwapAddress(payload, order) {
  if (process.env.SWAP_ADDRESS) return process.env.SWAP_ADDRESS;
  const fromMeta = payload?.meta?.verifyingContract || payload?.meta?.swapContract;
  if (fromMeta) return fromMeta;
  const senderKind = String(order?.sender?.kind || '').toLowerCase();
  if (senderKind === KIND_ERC721.toLowerCase()) return SWAP_ERC721;
  if (senderKind === KIND_ERC1155.toLowerCase()) return SWAP_ERC1155;
  return SWAP_DEFAULT;
}

async function getFeeOverrides(provider) {
  const gasPrice = await provider.getGasPrice();
  let maxPriorityFeePerGas = gasPrice.div(10); // cap prio to 10% of gas price
  if (maxPriorityFeePerGas.lte(0)) {
    maxPriorityFeePerGas = ethers.BigNumber.from(1);
  }
  let maxFeePerGas = gasPrice;
  if (maxFeePerGas.lt(maxPriorityFeePerGas)) {
    maxFeePerGas = maxPriorityFeePerGas;
  }
  return { gasPrice, maxPriorityFeePerGas, maxFeePerGas };
}

async function main() {
  const payload = JSON.parse(fs.readFileSync(path.resolve(IN), 'utf8'));
  const order = payload.order;
  const signature = payload.signature;

  const provider = new ethers.providers.JsonRpcProvider(RPC);
  const sender = new ethers.Wallet(SENDER_PRIVATE_KEY, provider);
  const swapAddress = resolveSwapAddress(payload, order);
  const swap = new ethers.Contract(swapAddress, SWAP_ABI, provider);

  const [protocolFee, requiredSenderKind, protocolFeeWallet] = await Promise.all([
    swap.protocolFee(),
    swap.requiredSenderKind(),
    swap.protocolFeeWallet(),
  ]);

  // Basic checks
  if (Number(order.expiry) <= Math.floor(Date.now() / 1000)) throw new Error('Order expired');
  const openOrder = String(order.sender.wallet).toLowerCase() === ethers.constants.AddressZero.toLowerCase();
  if (!openOrder && String(order.sender.wallet).toLowerCase() !== sender.address.toLowerCase()) {
    throw new Error('This order is not for this sender wallet');
  }
  if (String(order.sender.kind).toLowerCase() !== String(requiredSenderKind).toLowerCase()) throw new Error('Sender kind not allowed');
  if (Number(order.protocolFee) !== protocolFee.toNumber()) throw new Error('Protocol fee mismatch');

  // Verify signature
  const domain = {
    name: 'SWAP',
    version: '4.2',
    chainId: 8453,
    verifyingContract: swapAddress,
  };
  const recovered = ethers.utils.verifyTypedData(domain, ORDER_TYPES, order, signature);
  if (recovered.toLowerCase() !== String(order.signer.wallet).toLowerCase()) throw new Error('Bad signature');

  // Preflight checks for both sides
  const signerToken = new ethers.Contract(order.signer.token, ERC20_ABI, provider);
  const senderToken = new ethers.Contract(order.sender.token, ERC20_ABI, provider);

  const senderDec = await senderToken.decimals();
  const senderAmount = ethers.BigNumber.from(order.sender.amount);
  const signerAmount = ethers.BigNumber.from(order.signer.amount);
  const feeAmount = senderAmount.mul(protocolFee).div(10000);
  const total = senderAmount.add(feeAmount).add(ethers.BigNumber.from(order.affiliateAmount || 0));

  const [signerBal, signerAllowance] = await Promise.all([
    signerToken.balanceOf(order.signer.wallet),
    signerToken.allowance(order.signer.wallet, swapAddress),
  ]);
  if (signerBal.lt(signerAmount)) {
    throw new Error('Preflight failed: signer token balance is below order.signer.amount');
  }
  if (signerAllowance.lt(signerAmount)) {
    throw new Error('Preflight failed: signer allowance to Swap is below order.signer.amount');
  }

  const senderBal = await senderToken.balanceOf(sender.address);
  if (senderBal.lt(total)) {
    throw new Error('Preflight failed: sender token balance is below required total amount');
  }

  const allowance = await senderToken.allowance(sender.address, swapAddress);
  const feeOverrides = await getFeeOverrides(provider);
  console.log(JSON.stringify({
    gasPolicy: {
      gasPriceGwei: ethers.utils.formatUnits(feeOverrides.gasPrice, 'gwei'),
      maxPriorityFeePerGasGwei: ethers.utils.formatUnits(feeOverrides.maxPriorityFeePerGas, 'gwei'),
      maxFeePerGasGwei: ethers.utils.formatUnits(feeOverrides.maxFeePerGas, 'gwei'),
      maxGasLimit: getMaxGasLimit().toString(),
    },
  }, null, 2));

  if (allowance.lt(total)) {
    const tx = await senderToken.connect(sender).approve(swapAddress, total, {
      maxPriorityFeePerGas: feeOverrides.maxPriorityFeePerGas,
      maxFeePerGas: feeOverrides.maxFeePerGas,
    });
    console.log('approveSenderAssetTx', tx.hash);
    await tx.wait();
  }

  const split = ethers.utils.splitSignature(signature);

  const orderForCall = {
    nonce: ethers.BigNumber.from(order.nonce),
    expiry: ethers.BigNumber.from(order.expiry),
    signer: {
      wallet: order.signer.wallet,
      token: order.signer.token,
      kind: order.signer.kind,
      id: ethers.BigNumber.from(order.signer.id),
      amount: ethers.BigNumber.from(order.signer.amount),
    },
    sender: {
      wallet: order.sender.wallet,
      token: order.sender.token,
      kind: order.sender.kind,
      id: ethers.BigNumber.from(order.sender.id),
      amount: ethers.BigNumber.from(order.sender.amount),
    },
    affiliateWallet: order.affiliateWallet,
    affiliateAmount: ethers.BigNumber.from(order.affiliateAmount),
    v: split.v,
    r: split.r,
    s: split.s,
  };

  const recipient = process.env.RECIPIENT || sender.address;
  const maxRoyalty = Number(process.env.MAX_ROYALTY || '0');

  const maxGasLimit = getMaxGasLimit();
  let estimatedGas = null;
  let gasLimit = maxGasLimit;
  let usedManualGasFallback = false;
  try {
    estimatedGas = await swap.connect(sender).estimateGas.swap(recipient, maxRoyalty, orderForCall, {
      maxPriorityFeePerGas: feeOverrides.maxPriorityFeePerGas,
      maxFeePerGas: feeOverrides.maxFeePerGas,
    });
    if (estimatedGas.gt(maxGasLimit)) {
      throw new Error(`Preflight failed: estimated gas ${estimatedGas.toString()} exceeds MAX_GAS_LIMIT ${maxGasLimit.toString()}`);
    }
    gasLimit = estimatedGas.mul(120).div(100);
    if (gasLimit.gt(maxGasLimit)) {
      gasLimit = maxGasLimit;
    }
  } catch (e) {
    usedManualGasFallback = true;
    console.log(`estimateGas failed, using manual gas limit ${maxGasLimit.toString()}: ${e.message || e}`);
  }

  const tx = await swap.connect(sender).swap(recipient, maxRoyalty, orderForCall, {
    gasLimit,
    maxPriorityFeePerGas: feeOverrides.maxPriorityFeePerGas,
    maxFeePerGas: feeOverrides.maxFeePerGas,
  });
  console.log('swapTx', tx.hash);
  const receipt = await tx.wait();
  console.log('swapStatus', receipt.status, 'gasUsed', receipt.gasUsed.toString(), 'gasLimit', gasLimit.toString(), 'estimatedGas', estimatedGas ? estimatedGas.toString() : 'failed');

  console.log(JSON.stringify({
    sender: sender.address,
    signer: order.signer.wallet,
    senderToken: order.sender.token,
    signerToken: order.signer.token,
    senderAmount: ethers.utils.formatUnits(senderAmount, senderDec),
    feeAmount: ethers.utils.formatUnits(feeAmount, senderDec),
    protocolFeeWallet,
    swapAddress,
    usedManualGasFallback,
  }, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
