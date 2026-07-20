const { ethers } = require('ethers');

const RPC = process.env.RPC_URL || 'https://mainnet.base.org';

const SWAP = process.env.SWAP_ADDRESS || '0x8a9969ed0A9bb3cDA7521DDaA614aE86e72e0A57';
const WETH = process.env.WETH_ADDRESS || '0x4200000000000000000000000000000000000006';
const USDC = process.env.USDC_ADDRESS || '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913';

const SENDER_PRIVATE_KEY = process.env.SENDER_PRIVATE_KEY;
const SIGNER_PRIVATE_KEY = process.env.SIGNER_PRIVATE_KEY;

if (!SENDER_PRIVATE_KEY || !SIGNER_PRIVATE_KEY) {
  console.error('Missing SENDER_PRIVATE_KEY or SIGNER_PRIVATE_KEY');
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
  'function protocolFeeWallet() view returns (address)',
  'function requiredSenderKind() view returns (bytes4)',
  'function nonceUsed(address signer,uint256 nonce) view returns (bool)',
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

async function main() {
  const provider = new ethers.providers.JsonRpcProvider(RPC);
  const sender = new ethers.Wallet(SENDER_PRIVATE_KEY, provider);
  const signer = new ethers.Wallet(SIGNER_PRIVATE_KEY, provider);

  const swap = new ethers.Contract(SWAP, SWAP_ABI, provider);
  const protocolFee = await swap.protocolFee();
  const requiredSenderKind = await swap.requiredSenderKind();
  const protocolFeeWallet = await swap.protocolFeeWallet();

  const weth = new ethers.Contract(WETH, ERC20_ABI, provider);
  const usdc = new ethers.Contract(USDC, ERC20_ABI, provider);

  const [wethDec, usdcDec] = await Promise.all([weth.decimals(), usdc.decimals()]);

  const senderAmount = ethers.utils.parseUnits(process.env.SENDER_WETH || '0.001', wethDec);
  const signerAmount = ethers.utils.parseUnits(process.env.SIGNER_USDC || '0.994', usdcDec);

  const feeAmount = senderAmount.mul(protocolFee).div(10000);
  const senderTotal = senderAmount.add(feeAmount);

  const before = {
    sender: {
      address: sender.address,
      eth: ethers.utils.formatEther(await provider.getBalance(sender.address)),
      weth: ethers.utils.formatUnits(await weth.balanceOf(sender.address), wethDec),
      usdc: ethers.utils.formatUnits(await usdc.balanceOf(sender.address), usdcDec),
    },
    signer: {
      address: signer.address,
      eth: ethers.utils.formatEther(await provider.getBalance(signer.address)),
      weth: ethers.utils.formatUnits(await weth.balanceOf(signer.address), wethDec),
      usdc: ethers.utils.formatUnits(await usdc.balanceOf(signer.address), usdcDec),
    },
  };

  const wethSender = weth.connect(sender);
  const usdcSigner = usdc.connect(signer);

  const allowanceWeth = await weth.allowance(sender.address, SWAP);
  if (allowanceWeth.lt(senderTotal)) {
    const tx = await wethSender.approve(SWAP, senderTotal);
    console.log('approveWETH', tx.hash);
    await tx.wait();
  }

  const allowanceUsdc = await usdc.allowance(signer.address, SWAP);
  if (allowanceUsdc.lt(signerAmount)) {
    const tx = await usdcSigner.approve(SWAP, signerAmount);
    console.log('approveUSDC', tx.hash);
    await tx.wait();
  }

  const nonce = Number(process.env.NONCE || Math.floor(Date.now() / 1000));
  const used = await swap.nonceUsed(signer.address, nonce);
  if (used) throw new Error('Nonce already used. Set NONCE to a fresh value.');
  const expiry = Number(process.env.EXPIRY || (nonce + 3600));

  const kindErc20 = requiredSenderKind;

  const orderToSign = {
    nonce,
    expiry,
    protocolFee: protocolFee.toNumber(),
    signer: {
      wallet: signer.address,
      token: USDC,
      kind: kindErc20,
      id: 0,
      amount: signerAmount.toString(),
    },
    sender: {
      wallet: sender.address,
      token: WETH,
      kind: kindErc20,
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
    verifyingContract: SWAP,
  };

  const sig = await signer._signTypedData(domain, ORDER_TYPES, orderToSign);
  const split = ethers.utils.splitSignature(sig);

  const orderForCall = {
    nonce,
    expiry,
    signer: {
      wallet: signer.address,
      token: USDC,
      kind: kindErc20,
      id: 0,
      amount: signerAmount,
    },
    sender: {
      wallet: sender.address,
      token: WETH,
      kind: kindErc20,
      id: 0,
      amount: senderAmount,
    },
    affiliateWallet: ethers.constants.AddressZero,
    affiliateAmount: 0,
    v: split.v,
    r: split.r,
    s: split.s,
  };

  const swapSender = swap.connect(sender);
  const tx = await swapSender.swap(sender.address, 0, orderForCall);
  console.log('swapTx', tx.hash);
  const receipt = await tx.wait();
  console.log('swapStatus', receipt.status, 'gasUsed', receipt.gasUsed.toString());

  const after = {
    sender: {
      address: sender.address,
      eth: ethers.utils.formatEther(await provider.getBalance(sender.address)),
      weth: ethers.utils.formatUnits(await weth.balanceOf(sender.address), wethDec),
      usdc: ethers.utils.formatUnits(await usdc.balanceOf(sender.address), usdcDec),
    },
    signer: {
      address: signer.address,
      eth: ethers.utils.formatEther(await provider.getBalance(signer.address)),
      weth: ethers.utils.formatUnits(await weth.balanceOf(signer.address), wethDec),
      usdc: ethers.utils.formatUnits(await usdc.balanceOf(signer.address), usdcDec),
    },
    protocolFeeWallet: {
      address: protocolFeeWallet,
      weth: ethers.utils.formatUnits(await weth.balanceOf(protocolFeeWallet), wethDec),
    },
  };

  console.log(JSON.stringify({
    swap: SWAP,
    protocolFee: protocolFee.toString(),
    senderAmount: ethers.utils.formatUnits(senderAmount, wethDec),
    signerAmount: ethers.utils.formatUnits(signerAmount, usdcDec),
    feeAmount: ethers.utils.formatUnits(feeAmount, wethDec),
    before,
    after,
  }, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
