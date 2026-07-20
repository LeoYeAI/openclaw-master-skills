const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');
const LZString = require('lz-string');

const RPC = process.env.RPC_URL || 'https://mainnet.base.org';
const SWAP_DEFAULT = '0x8a9969ed0A9bb3cDA7521DDaA614aE86e72e0A57';
const SWAP_ERC721 = '0x2aa29F096257bc6B253bfA9F6404B20Ae0ef9C4d';
const SWAP_ERC1155 = '0xD19783B48b11AFE1544b001c6d807A513e5A95cf';
const KIND_ERC20 = '0x36372b07';
const KIND_ERC721 = '0x80ac58cd';
const KIND_ERC1155 = '0xd9b67a26';

const SIGNER_PRIVATE_KEY = process.env.SIGNER_PRIVATE_KEY;
if (!SIGNER_PRIVATE_KEY) {
  console.error('Missing SIGNER_PRIVATE_KEY');
  process.exit(1);
}

const SIGNER_TOKEN = process.env.SIGNER_TOKEN; // ERC20 for now
const SENDER_TOKEN = process.env.SENDER_TOKEN; // ERC20 required by this Swap deployment
const SIGNER_AMOUNT = process.env.SIGNER_AMOUNT; // human units
const SENDER_AMOUNT = process.env.SENDER_AMOUNT; // human units
const OPEN_ORDER = (process.env.OPEN_ORDER || '').toLowerCase() === '1' || (process.env.OPEN_ORDER || '').toLowerCase() === 'true';
const SENDER_WALLET = process.env.SENDER_WALLET; // address that will submit swap if not open

if (!SIGNER_TOKEN || !SENDER_TOKEN || !SIGNER_AMOUNT || !SENDER_AMOUNT || (!OPEN_ORDER && !SENDER_WALLET)) {
  console.error('Missing one of SIGNER_TOKEN, SENDER_TOKEN, SIGNER_AMOUNT, SENDER_AMOUNT. Also need SENDER_WALLET unless OPEN_ORDER=true');
  process.exit(1);
}

const OUT = process.env.OUT_FILE || 'order.json';

const ERC20_ABI = [
  'function approve(address spender,uint256 amount) returns (bool)',
  'function allowance(address owner,address spender) view returns (uint256)',
  'function balanceOf(address owner) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
];

const SWAP_ABI = [
  'function protocolFee() view returns (uint256)',
  'function requiredSenderKind() view returns (bytes4)',
  'function nonceUsed(address signer,uint256 nonce) view returns (bool)',
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

function fullOrderToAirswapWebParams(fullOrder) {
  return [
    String(fullOrder.chainId),
    String(fullOrder.swapContract),
    String(fullOrder.nonce),
    String(fullOrder.expiry),
    String(fullOrder.signerWallet),
    String(fullOrder.signerToken),
    String(fullOrder.signerAmount),
    String(fullOrder.protocolFee),
    String(fullOrder.senderWallet),
    String(fullOrder.senderToken),
    String(fullOrder.senderAmount),
    String(fullOrder.v),
    String(fullOrder.r),
    String(fullOrder.s),
  ];
}

function compressFullOrderERC20LikeAirswapWeb(fullOrder) {
  const csv = fullOrderToAirswapWebParams(fullOrder).join(',');
  return LZString.compressToEncodedURIComponent(csv);
}


async function detectTokenKind(token, provider) {
  try {
    const c = new ethers.Contract(token, ['function supportsInterface(bytes4 interfaceId) view returns (bool)'], provider);
    const [is721, is1155] = await Promise.all([
      c.supportsInterface(KIND_ERC721).catch(() => false),
      c.supportsInterface(KIND_ERC1155).catch(() => false),
    ]);
    if (is1155) return KIND_ERC1155;
    if (is721) return KIND_ERC721;
  } catch {}
  return KIND_ERC20;
}

async function resolveSwapAddress(senderToken, provider) {
  if (process.env.SWAP_ADDRESS) return process.env.SWAP_ADDRESS;
  const kind = await detectTokenKind(senderToken, provider);
  if (kind === KIND_ERC721) return SWAP_ERC721;
  if (kind === KIND_ERC1155) return SWAP_ERC1155;
  return SWAP_DEFAULT;
}

async function main() {
  const provider = new ethers.providers.JsonRpcProvider(RPC);
  const signer = new ethers.Wallet(SIGNER_PRIVATE_KEY, provider);

  const swapAddress = await resolveSwapAddress(SENDER_TOKEN, provider);
  const swap = new ethers.Contract(swapAddress, SWAP_ABI, provider);
  const protocolFee = await swap.protocolFee();
  const requiredSenderKind = await swap.requiredSenderKind();

  const signerToken = new ethers.Contract(SIGNER_TOKEN, ERC20_ABI, provider);
  const senderToken = new ethers.Contract(SENDER_TOKEN, ERC20_ABI, provider);
  const [signerDec, senderDec, signerSym, senderSym] = await Promise.all([
    signerToken.decimals(),
    senderToken.decimals(),
    signerToken.symbol().catch(() => ''),
    senderToken.symbol().catch(() => ''),
  ]);

  const signerAmount = ethers.utils.parseUnits(SIGNER_AMOUNT, signerDec);
  const senderAmount = ethers.utils.parseUnits(SENDER_AMOUNT, senderDec);

  // Signer must approve their asset to Swap.
  const allowance = await signerToken.allowance(signer.address, swapAddress);
  if (allowance.lt(signerAmount)) {
    const tx = await signerToken.connect(signer).approve(swapAddress, signerAmount);
    console.log('approveSignerAssetTx', tx.hash);
    await tx.wait();
  }

  // Nonce policy: pick a fresh random-ish nonce and ensure unused.
  let nonce = BigInt(process.env.NONCE || '0');
  if (nonce === 0n) {
    nonce = BigInt(Math.floor(Date.now() / 1000)) * 1000000n + BigInt(Math.floor(Math.random() * 1000000));
  }
  const nonceNum = nonce.toString();
  const used = await swap.nonceUsed(signer.address, nonceNum);
  if (used) throw new Error('Nonce already used. Rerun.');

  const expiry = Number(process.env.EXPIRY || (Math.floor(Date.now() / 1000) + 3600));

  const senderWallet = OPEN_ORDER ? ethers.constants.AddressZero : SENDER_WALLET;

  const orderToSign = {
    nonce: nonceNum,
    expiry,
    protocolFee: protocolFee.toNumber(),
    signer: {
      wallet: signer.address,
      token: SIGNER_TOKEN,
      kind: requiredSenderKind,
      id: 0,
      amount: signerAmount.toString(),
    },
    sender: {
      wallet: senderWallet,
      token: SENDER_TOKEN,
      kind: requiredSenderKind,
      id: 0,
      amount: senderAmount.toString(),
    },
    affiliateWallet: ethers.constants.AddressZero,
    affiliateAmount: 0,
  };

  const domain = {
    name: 'SWAP',
    version: '4.2',
    chainId: 8453,
    verifyingContract: swapAddress,
  };

  const sig = await signer._signTypedData(domain, ORDER_TYPES, orderToSign);

  const split = ethers.utils.splitSignature(sig);
  const fullOrder = {
    chainId: 8453,
    swapContract: swapAddress,
    nonce: orderToSign.nonce,
    expiry: String(orderToSign.expiry),
    signerWallet: orderToSign.signer.wallet,
    signerToken: orderToSign.signer.token,
    signerAmount: String(orderToSign.signer.amount),
    protocolFee: String(orderToSign.protocolFee),
    senderWallet: orderToSign.sender.wallet,
    senderToken: orderToSign.sender.token,
    senderAmount: String(orderToSign.sender.amount),
    v: String(split.v),
    r: split.r,
    s: split.s,
  };

  const compressedOrder = compressFullOrderERC20LikeAirswapWeb(fullOrder);

  const payload = {
    meta: {
      chainId: 8453,
      rpc: RPC,
      verifyingContract: swapAddress,
      requiredSenderKind,
      protocolFeeBps: protocolFee.toString(),
      createdAt: new Date().toISOString(),
      signerToken: { address: SIGNER_TOKEN, symbol: signerSym, decimals: signerDec },
      senderToken: { address: SENDER_TOKEN, symbol: senderSym, decimals: senderDec },
      note: 'Send this JSON to the sender agent. Do not include private keys.',
    },
    order: orderToSign,
    signature: sig,
    airswapWeb: {
      compressedOrder,
      orderPath: `/order/${compressedOrder}`,
    },
  };

  fs.writeFileSync(path.resolve(OUT), JSON.stringify(payload, null, 2));
  console.log('wrote', OUT);
  console.log('compressedOrder', compressedOrder);
  console.log(JSON.stringify({ signer: signer.address, senderWallet, openOrder: OPEN_ORDER, nonce: nonceNum, expiry, swapAddress }));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
