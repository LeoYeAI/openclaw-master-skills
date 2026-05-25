#!/usr/bin/env node
/**
 * AAWP NFT Manager — ERC-721 & ERC-1155 Operations
 *
 * Commands:
 *   nft.js --chain base balance                        List all NFTs owned by wallet
 *   nft.js --chain base balance --contract 0x...       NFTs from specific collection
 *   nft.js --chain base info <contract> <tokenId>      Token metadata & owner
 *   nft.js --chain base transfer <contract> <tokenId> <to>          ERC-721 transfer
 *   nft.js --chain base transfer <contract> <tokenId> <to> <amount> ERC-1155 transfer
 *   nft.js --chain base approve <contract> <operator>               Approve operator
 *   nft.js --chain base revoke <contract> <operator>                Revoke approval
 *   nft.js --chain base mint <contract> [data]                      Call mint() on contract
 *   nft.js --chain base floor <contract>               Fetch floor price via public API
 *
 * Chains: base, eth, arb, op, polygon, bsc
 */
'use strict';

const net = require('net');
const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const https = require('https');

const S = path.join(__dirname, '..');
const ENSURE_SCRIPT = path.join(__dirname, 'ensure-daemon.sh');
const CHAINS_FILE = path.join(S, 'config/chains.json');
const CHAINS = JSON.parse(fs.readFileSync(CHAINS_FILE, 'utf8'));

// ── ABIs ──────────────────────────────────────────────────────────────────────
const ERC721_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function ownerOf(uint256 tokenId) view returns (address)',
  'function tokenURI(uint256 tokenId) view returns (string)',
  'function name() view returns (string)',
  'function symbol() view returns (string)',
  'function totalSupply() view returns (uint256)',
  'function tokenOfOwnerByIndex(address owner, uint256 index) view returns (uint256)',
  'function safeTransferFrom(address from, address to, uint256 tokenId)',
  'function transferFrom(address from, address to, uint256 tokenId)',
  'function approve(address to, uint256 tokenId)',
  'function setApprovalForAll(address operator, bool approved)',
  'function isApprovedForAll(address owner, address operator) view returns (bool)',
  'function getApproved(uint256 tokenId) view returns (address)',
  'function supportsInterface(bytes4 interfaceId) view returns (bool)',
];

const ERC1155_ABI = [
  'function balanceOf(address account, uint256 id) view returns (uint256)',
  'function balanceOfBatch(address[] accounts, uint256[] ids) view returns (uint256[])',
  'function uri(uint256 id) view returns (string)',
  'function safeTransferFrom(address from, address to, uint256 id, uint256 amount, bytes data)',
  'function safeBatchTransferFrom(address from, address to, uint256[] ids, uint256[] amounts, bytes data)',
  'function setApprovalForAll(address operator, bool approved)',
  'function isApprovedForAll(address account, address operator) view returns (bool)',
];

// ERC-165 interface IDs
const IFACE_ERC721  = '0x80ac58cd';
const IFACE_ERC1155 = '0xd9b67a26';

// ── Known popular NFT contracts (for display) ─────────────────────────────────
const KNOWN_COLLECTIONS = {
  eth: {
    '0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D': 'BAYC',
    '0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB': 'CryptoPunks',
    '0x60E4d786628Fea6478F785A6d7e704777c86a7c6': 'MAYC',
    '0x49cF6f5d44E70224e2E23fDcdd2C053F30aDA28B': 'CloneX',
  },
  base: {
    '0xd4307E0A04171d895F1BEF42FF0a7B88e78FD5e2': 'OnchainGasPower',
  },
};

// ── Alch/public APIs for NFT enumeration ─────────────────────────────────────
// Uses public endpoints — no API key required for basic queries
const NFT_APIS = {
  eth:     'https://eth-mainnet.g.alchemy.com/nft/v3',
  base:    'https://base-mainnet.g.alchemy.com/nft/v3',
  arb:     'https://arb-mainnet.g.alchemy.com/nft/v3',
  op:      'https://opt-mainnet.g.alchemy.com/nft/v3',
  polygon: 'https://polygon-mainnet.g.alchemy.com/nft/v3',
};

// BSC uses BscScan API (public, no key for basic NFT queries)
const BSCSCAN_API = 'https://api.bscscan.com/api';

// BSC NFT known collections
const KNOWN_COLLECTIONS_BSC = {
  '0x0a8901b0E25DEb55A87524f0cC164E9644020EBA': 'PancakeSwap Positions',
  '0x9f5f463351e5B5f9Ade68ADE0bf1a6f1069a6Ba6': 'PancakeSwap LP',
};

// OpenSea stats API (public, no key for basic)
const OPENSEA_CHAIN_SLUGS = {
  eth:     'ethereum',
  base:    'base',
  arb:     'arbitrum',
  op:      'optimism',
  polygon: 'matic',
};

// ── Parse args ────────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
let chainArg = 'base';
let contractFilter = null;
const filteredArgv = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i] === '--chain' && argv[i + 1])    { chainArg = argv[++i]; }
  else if (argv[i] === '--contract' && argv[i + 1]) { contractFilter = argv[++i]; }
  else filteredArgv.push(argv[i]);
}
const cmd = filteredArgv[0];

// ── Helpers ───────────────────────────────────────────────────────────────────
function getChain(key) {
  const cfg = CHAINS[key];
  if (!cfg) { console.error(`❌ Unknown chain: ${key}`); process.exit(1); }
  return { key, ...cfg };
}

function getProvider(cfg) {
  return new ethers.JsonRpcProvider(cfg.rpcOverride || cfg.rpc);
}

function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'AAWP-NFT/1.0' } }, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); } catch { resolve({}); }
      });
    }).on('error', reject);
  });
}

async function detectStandard(contract, provider) {
  try {
    const c = new ethers.Contract(contract, ERC721_ABI, provider);
    const is721 = await c.supportsInterface(IFACE_ERC721).catch(() => false);
    if (is721) return '721';
    const c1 = new ethers.Contract(contract, ERC1155_ABI, provider);
    const is1155 = await c1.supportsInterface(IFACE_ERC1155).catch(() => false);
    if (is1155) return '1155';
  } catch {}
  return '721'; // default assumption
}

function shortenAddr(addr) {
  return addr.slice(0, 6) + '...' + addr.slice(-4);
}

// ── Daemon signing ────────────────────────────────────────────────────────────
function signViaSocket(payload) {
  return new Promise((resolve, reject) => {
    try { require('child_process').execSync(`bash "${ENSURE_SCRIPT}"`, { stdio: 'ignore' }); } catch {}
    const lockFile = '/tmp/.aawp-daemon.lock';
    if (!fs.existsSync(lockFile)) return reject(new Error('Daemon not running. Run: bash scripts/ensure-daemon.sh'));
    const socketPath = fs.readFileSync(lockFile, 'utf8').trim().split('\n')[1];
    if (!socketPath) return reject(new Error('Socket path not found in lock file'));
    const client = net.createConnection(socketPath);
    let buf = '';
    client.on('connect', () => client.write(JSON.stringify(payload) + '\n'));
    client.on('data', d => { buf += d.toString(); });
    client.on('end', () => { try { resolve(JSON.parse(buf)); } catch (e) { reject(new Error('Bad daemon response: ' + buf)); } });
    client.on('error', reject);
    setTimeout(() => { client.destroy(); reject(new Error('Daemon timeout')); }, 15000);
  });
}

async function getWalletAddress(chain) {
  const resp = await signViaSocket({ action: 'get_address', chain_id: chain.chainId });
  if (resp.error) throw new Error(resp.error);
  return resp.address;
}

async function sendTx(chain, txRequest) {
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);
  const [nonce, feeData, gasEstimate] = await Promise.all([
    provider.getTransactionCount(walletAddr, 'latest'),
    provider.getFeeData(),
    provider.estimateGas({ ...txRequest, from: walletAddr }).catch(() => BigInt(200000)),
  ]);
  const tx = {
    ...txRequest,
    from: walletAddr,
    nonce,
    chainId: chain.chainId,
    gasLimit: gasEstimate * BigInt(12) / BigInt(10),
    maxFeePerGas: feeData.maxFeePerGas || feeData.gasPrice,
    maxPriorityFeePerGas: feeData.maxPriorityFeePerGas || BigInt(1000000),
  };
  if (!tx.maxFeePerGas) {
    tx.gasPrice = feeData.gasPrice;
    delete tx.maxFeePerGas;
    delete tx.maxPriorityFeePerGas;
  }
  const resp = await signViaSocket({ action: 'sign_transaction', chain_id: chain.chainId, tx });
  if (resp.error) throw new Error(resp.error);
  const sent = await provider.broadcastTransaction(resp.signed);
  console.log(`📡 TX broadcast: ${sent.hash}`);
  console.log(`   Waiting for confirmation...`);
  return await sent.wait(1);
}

// ── Commands ──────────────────────────────────────────────────────────────────

async function cmdBalance(chainKey) {
  const chain = getChain(chainKey);
  const walletAddr = await getWalletAddress(chain);
  const provider = getProvider(chain);

  console.log(`\n🖼️  NFT Balance — ${chain.name}`);
  console.log(`   Wallet: ${walletAddr}\n`);

  // If specific contract provided, scan that one directly on-chain
  if (contractFilter) {
    await scanSingleContract(contractFilter, walletAddr, provider, chain);
    return;
  }

  // BSC: use BscScan NFT transfer events API
  if (chainKey === 'bsc') {
    try {
      const url = `${BSCSCAN_API}?module=account&action=tokennfttx&address=${walletAddr}&startblock=0&endblock=99999999&sort=desc&apikey=YourApiKeyToken`;
      const data = await httpGet(url);
      if (data.status === '1' && data.result?.length > 0) {
        // Deduplicate — keep only tokens still owned (last transfer TO wallet)
        const owned = new Map();
        for (const tx of data.result) {
          const key = `${tx.contractAddress}-${tx.tokenID}`;
          if (!owned.has(key)) {
            if (tx.to.toLowerCase() === walletAddr.toLowerCase()) {
              owned.set(key, tx);
            }
          }
        }
        const ownedList = [...owned.values()];
        if (ownedList.length === 0) {
          console.log('   No NFTs found.');
          return;
        }
        console.log(`   Found ~${ownedList.length} NFT(s) (from recent transfer history):\n`);
        for (const tx of ownedList.slice(0, 20)) {
          const cName = KNOWN_COLLECTIONS_BSC[tx.contractAddress] || tx.tokenName || shortenAddr(tx.contractAddress);
          console.log(`   [ERC-721] ${cName} — Token #${tx.tokenID}`);
          console.log(`          Contract: ${tx.contractAddress}  Symbol: ${tx.tokenSymbol}`);
          console.log();
        }
        if (ownedList.length > 20) console.log(`   ... and ${ownedList.length - 20} more.`);
      } else {
        console.log('   No NFT transfers found (BscScan). Specify --contract to scan on-chain.');
      }
    } catch (e) {
      console.log(`   BscScan query failed: ${e.message}. Specify --contract to scan on-chain.`);
    }
    return;
  }

  // Try Alchemy NFT API if available (free tier, no key)
  const apiBase = NFT_APIS[chainKey];
  if (apiBase) {
    try {
      const url = `${apiBase}/demo/getNFTsForOwner?owner=${walletAddr}&withMetadata=true&pageSize=20`;
      const data = await httpGet(url);
      if (data.ownedNfts && data.ownedNfts.length > 0) {
        console.log(`   Found ${data.totalCount || data.ownedNfts.length} NFT(s):\n`);
        for (const nft of data.ownedNfts) {
          const contract = nft.contract?.address || '?';
          const tokenId  = nft.tokenId || nft.id?.tokenId || '?';
          const name     = nft.name || nft.title || `Token #${parseInt(tokenId, 16) || tokenId}`;
          const cName    = nft.contract?.name || KNOWN_COLLECTIONS[chainKey]?.[contract] || shortenAddr(contract);
          const standard = nft.tokenType || 'ERC721';
          const balance  = nft.balance || '1';
          console.log(`   [${standard}] ${cName} — ${name}`);
          console.log(`          Contract: ${contract}  TokenID: ${parseInt(tokenId, 16) || tokenId}  Balance: ${balance}`);
          if (nft.image?.cachedUrl || nft.media?.[0]?.gateway) {
            console.log(`          Image: ${nft.image?.cachedUrl || nft.media[0].gateway}`);
          }
          console.log();
        }
        if (data.totalCount > 20) {
          console.log(`   ... and ${data.totalCount - 20} more. Use --contract to filter.`);
        }
        return;
      }
      console.log('   No NFTs found (via Alchemy public API).');
      return;
    } catch {
      // Fall through to on-chain
    }
  }

  console.log('   (No API available for this chain — specify --contract to scan on-chain)');
}

async function scanSingleContract(contractAddr, walletAddr, provider, chain) {
  const standard = await detectStandard(contractAddr, provider);
  console.log(`   Contract: ${contractAddr} (${standard === '721' ? 'ERC-721' : 'ERC-1155'})\n`);

  if (standard === '721') {
    const c = new ethers.Contract(contractAddr, ERC721_ABI, provider);
    const [name, symbol, balance] = await Promise.all([
      c.name().catch(() => 'Unknown'),
      c.symbol().catch(() => '?'),
      c.balanceOf(walletAddr).catch(() => BigInt(0)),
    ]);
    console.log(`   Collection: ${name} (${symbol})`);
    console.log(`   You own: ${balance} token(s)\n`);

    // Try to enumerate via tokenOfOwnerByIndex (ERC-721 Enumerable)
    const count = Number(balance);
    if (count > 0 && count <= 50) {
      for (let i = 0; i < count; i++) {
        try {
          const tokenId = await c.tokenOfOwnerByIndex(walletAddr, i);
          const uri = await c.tokenURI(tokenId).catch(() => 'N/A');
          console.log(`   Token #${tokenId}: ${uri.slice(0, 80)}${uri.length > 80 ? '...' : ''}`);
        } catch {
          console.log(`   Token at index ${i}: (enumeration not supported)`);
          break;
        }
      }
    }
  } else {
    console.log('   ERC-1155: specify token IDs directly with `info` command');
  }
}

async function cmdInfo(chainKey, contractAddr, tokenId) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);
  const standard = await detectStandard(contractAddr, provider);

  console.log(`\n🔍 NFT Info — ${chain.name}`);
  console.log(`   Contract: ${contractAddr}`);
  console.log(`   Token ID: ${tokenId}`);
  console.log(`   Standard: ERC-${standard}\n`);

  if (standard === '721') {
    const c = new ethers.Contract(contractAddr, ERC721_ABI, provider);
    const [name, symbol, owner, uri] = await Promise.all([
      c.name().catch(() => '?'),
      c.symbol().catch(() => '?'),
      c.ownerOf(tokenId).catch(() => 'N/A'),
      c.tokenURI(tokenId).catch(() => 'N/A'),
    ]);
    console.log(`   Collection: ${name} (${symbol})`);
    console.log(`   Owner:      ${owner}`);
    console.log(`   Token URI:  ${uri}`);

    // Try to fetch metadata
    if (uri && (uri.startsWith('http') || uri.startsWith('ipfs'))) {
      const url = uri.replace('ipfs://', 'https://ipfs.io/ipfs/');
      try {
        const meta = await httpGet(url);
        if (meta.name) console.log(`   Name:       ${meta.name}`);
        if (meta.description) console.log(`   Desc:       ${meta.description.slice(0, 100)}`);
        if (meta.image) console.log(`   Image:      ${meta.image}`);
        if (meta.attributes?.length) {
          console.log(`   Traits:     ${meta.attributes.map(a => `${a.trait_type}=${a.value}`).join(', ')}`);
        }
      } catch { /* metadata fetch failed */ }
    }
  } else {
    const c = new ethers.Contract(contractAddr, ERC1155_ABI, provider);
    const uri = await c.uri(tokenId).catch(() => 'N/A');
    console.log(`   URI: ${uri}`);
  }
  console.log();
}

async function cmdTransfer(chainKey, contractAddr, tokenId, toAddr, amount) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);
  const walletAddr = await getWalletAddress(chain);
  const standard = await detectStandard(contractAddr, provider);

  if (!ethers.isAddress(toAddr)) {
    console.error(`❌ Invalid recipient address: ${toAddr}`);
    process.exit(1);
  }

  console.log(`\n📤 Transferring NFT — ${chain.name}`);
  console.log(`   From:     ${walletAddr}`);
  console.log(`   To:       ${toAddr}`);
  console.log(`   Contract: ${contractAddr}`);
  console.log(`   Token ID: ${tokenId}`);

  let data;
  if (standard === '721') {
    const iface = new ethers.Interface(ERC721_ABI);
    data = iface.encodeFunctionData('safeTransferFrom', [walletAddr, toAddr, BigInt(tokenId)]);
    console.log(`   Standard: ERC-721`);
  } else {
    const transferAmount = BigInt(amount || 1);
    const iface = new ethers.Interface(ERC1155_ABI);
    data = iface.encodeFunctionData('safeTransferFrom', [walletAddr, toAddr, BigInt(tokenId), transferAmount, '0x']);
    console.log(`   Standard: ERC-1155  Amount: ${transferAmount}`);
  }

  const receipt = await sendTx(chain, { to: contractAddr, data, value: BigInt(0) });
  console.log(`\n✅ Transfer complete! Block: ${receipt.blockNumber}`);
  console.log(`   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

async function cmdApprove(chainKey, contractAddr, operatorAddr, revoke) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);
  const walletAddr = await getWalletAddress(chain);
  const standard = await detectStandard(contractAddr, provider);
  const approved = !revoke;

  if (!ethers.isAddress(operatorAddr)) {
    console.error(`❌ Invalid operator address: ${operatorAddr}`);
    process.exit(1);
  }

  // Check current state
  let isApproved = false;
  try {
    if (standard === '721') {
      const c = new ethers.Contract(contractAddr, ERC721_ABI, provider);
      isApproved = await c.isApprovedForAll(walletAddr, operatorAddr);
    } else {
      const c = new ethers.Contract(contractAddr, ERC1155_ABI, provider);
      isApproved = await c.isApprovedForAll(walletAddr, operatorAddr);
    }
  } catch {}

  if (approved && isApproved) {
    console.log(`✅ Already approved. No action needed.`);
    return;
  }
  if (!approved && !isApproved) {
    console.log(`✅ Already not approved. No action needed.`);
    return;
  }

  const iface = new ethers.Interface(standard === '721' ? ERC721_ABI : ERC1155_ABI);
  const data = iface.encodeFunctionData('setApprovalForAll', [operatorAddr, approved]);
  const action = approved ? 'Approving' : 'Revoking';
  console.log(`\n🔑 ${action} operator for ERC-${standard}...`);
  console.log(`   Contract: ${contractAddr}`);
  console.log(`   Operator: ${operatorAddr}`);

  const receipt = await sendTx(chain, { to: contractAddr, data, value: BigInt(0) });
  console.log(`\n✅ ${action} complete! Block: ${receipt.blockNumber}`);
  console.log(`   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

async function cmdMint(chainKey, contractAddr, extraData) {
  const chain = getChain(chainKey);
  const walletAddr = await getWalletAddress(chain);

  // Try common mint function signatures
  const mintSignatures = [
    { sig: 'mint()', data: '0x1249c58b' },
    { sig: 'mint(address)', fn: (addr) => new ethers.Interface(['function mint(address to)']).encodeFunctionData('mint', [addr]) },
    { sig: 'publicMint()', data: '0x2db11544' },
  ];

  console.log(`\n🎨 Minting from ${contractAddr} on ${chain.name}...`);
  console.log(`   Wallet: ${walletAddr}`);
  console.log(`   Note: Using standard mint() signature. If this fails, use wallet-manager call directly.\n`);

  // Default: call mint(address to) with wallet address
  const iface = new ethers.Interface(['function mint(address to)']);
  let data;
  try {
    data = iface.encodeFunctionData('mint', [walletAddr]);
  } catch {
    data = '0x1249c58b'; // mint() no args
  }

  if (extraData) {
    // User provided custom calldata
    data = extraData.startsWith('0x') ? extraData : '0x' + extraData;
  }

  const receipt = await sendTx(chain, { to: contractAddr, data, value: BigInt(0) });
  console.log(`\n✅ Mint TX confirmed! Block: ${receipt.blockNumber}`);
  console.log(`   TX: ${chain.explorer}/tx/${receipt.hash}`);
}

async function cmdFloor(chainKey, contractAddr) {
  const chain = getChain(chainKey);
  const provider = getProvider(chain);

  // Get collection name
  let collectionName = KNOWN_COLLECTIONS[chainKey]?.[contractAddr];
  if (!collectionName) {
    try {
      const c = new ethers.Contract(contractAddr, ERC721_ABI, provider);
      collectionName = await c.name();
    } catch {
      collectionName = shortenAddr(contractAddr);
    }
  }

  console.log(`\n📊 Floor Price — ${collectionName} on ${chain.name}`);
  console.log(`   Contract: ${contractAddr}\n`);

  // Try OpenSea stats API (v2, public)
  const chainSlug = OPENSEA_CHAIN_SLUGS[chainKey];
  if (chainSlug) {
    try {
      const url = `https://api.opensea.io/api/v2/collections?asset_contract_address=${contractAddr}&chain=${chainSlug}`;
      const data = await httpGet(url);
      if (data.results?.[0]) {
        const col = data.results[0];
        const stats = col.stats;
        console.log(`   OpenSea Collection: ${col.name || collectionName}`);
        if (stats) {
          if (stats.floor_price) console.log(`   Floor Price:  ${stats.floor_price} ${chain.nativeCurrency}`);
          if (stats.total_volume) console.log(`   Total Volume: ${parseFloat(stats.total_volume).toFixed(2)} ${chain.nativeCurrency}`);
          if (stats.num_owners) console.log(`   Owners:       ${stats.num_owners}`);
          if (stats.total_supply) console.log(`   Supply:       ${stats.total_supply}`);
        }
        console.log(`   OpenSea:  https://opensea.io/collection/${col.collection}`);
      } else {
        console.log('   Not found on OpenSea.');
      }
    } catch (e) {
      console.log(`   OpenSea API unavailable: ${e.message}`);
    }
  }

  // Try Blur (ETH only)
  if (chainKey === 'eth') {
    console.log(`   Blur:     https://blur.io/collection/${contractAddr}`);
  }
  console.log(`   Explorer: ${chain.explorer}/address/${contractAddr}`);
  console.log();
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  if (!cmd) {
    console.log(`
AAWP NFT Manager — ERC-721 & ERC-1155

Usage: nft.js [--chain <chain>] <command> [args]

Commands:
  balance [--contract 0x...]            List NFTs owned by wallet
  info <contract> <tokenId>             Show token metadata & owner
  transfer <contract> <tokenId> <to>    Transfer ERC-721
  transfer <contract> <tokenId> <to> <amount>  Transfer ERC-1155
  approve <contract> <operator>         Set approval for all
  revoke  <contract> <operator>         Revoke approval for all
  mint <contract> [calldata]            Call mint() on contract
  floor <contract>                      Get floor price from OpenSea

Supported chains: ${Object.keys(CHAINS).join(', ')}

Examples:
  nft.js --chain base balance
  nft.js --chain eth balance --contract 0xBC4CA0Ed...
  nft.js --chain eth info 0xBC4CA0Ed... 1234
  nft.js --chain base transfer 0xNFT... 42 0xRecipient...
  nft.js --chain eth floor 0xBC4CA0Ed...
  nft.js --chain base mint 0xContract...
`);
    process.exit(0);
  }

  switch (cmd) {
    case 'balance':
      await cmdBalance(chainArg);
      break;
    case 'info': {
      const [, contract, tokenId] = filteredArgv;
      if (!contract || !tokenId) { console.error('Usage: nft.js --chain <chain> info <contract> <tokenId>'); process.exit(1); }
      await cmdInfo(chainArg, contract, tokenId);
      break;
    }
    case 'transfer': {
      const [, contract, tokenId, to, amount] = filteredArgv;
      if (!contract || !tokenId || !to) { console.error('Usage: nft.js --chain <chain> transfer <contract> <tokenId> <to> [amount]'); process.exit(1); }
      await cmdTransfer(chainArg, contract, tokenId, to, amount);
      break;
    }
    case 'approve': {
      const [, contract, operator] = filteredArgv;
      if (!contract || !operator) { console.error('Usage: nft.js --chain <chain> approve <contract> <operator>'); process.exit(1); }
      await cmdApprove(chainArg, contract, operator, false);
      break;
    }
    case 'revoke': {
      const [, contract, operator] = filteredArgv;
      if (!contract || !operator) { console.error('Usage: nft.js --chain <chain> revoke <contract> <operator>'); process.exit(1); }
      await cmdApprove(chainArg, contract, operator, true);
      break;
    }
    case 'mint': {
      const [, contract, extraData] = filteredArgv;
      if (!contract) { console.error('Usage: nft.js --chain <chain> mint <contract> [calldata]'); process.exit(1); }
      await cmdMint(chainArg, contract, extraData);
      break;
    }
    case 'floor': {
      const [, contract] = filteredArgv;
      if (!contract) { console.error('Usage: nft.js --chain <chain> floor <contract>'); process.exit(1); }
      await cmdFloor(chainArg, contract);
      break;
    }
    default:
      console.error(`❌ Unknown command: ${cmd}`);
      process.exit(1);
  }
}

main().catch(err => {
  console.error('❌ Error:', err.message);
  process.exit(1);
});
