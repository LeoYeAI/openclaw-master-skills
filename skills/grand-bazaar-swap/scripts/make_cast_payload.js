const fs = require('fs');
const path = require('path');
const { ethers } = require('ethers');

const IN = process.env.IN_FILE || 'order.json';
const OUT = process.env.OUT_FILE || '';
const WEB_BASE = process.env.AIRSWAP_WEB_BASE || 'https://dex.airswap.xyz/#/order/';
const MINIAPP_BASE = process.env.MINIAPP_BASE || 'https://the-grand-bazaar.vercel.app/';

function short(addr) {
  return `${addr.slice(0, 6)}…${addr.slice(-4)}`;
}

function fmtAmount(amountAtomic, decimals) {
  return ethers.utils.formatUnits(ethers.BigNumber.from(amountAtomic), decimals);
}

function main() {
  const payload = JSON.parse(fs.readFileSync(path.resolve(IN), 'utf8'));
  const order = payload.order;

  const signerMeta = payload?.meta?.signerToken || {};
  const senderMeta = payload?.meta?.senderToken || {};

  const signerSymbol = signerMeta.symbol || 'TOKEN_A';
  const senderSymbol = senderMeta.symbol || 'TOKEN_B';
  const signerDecimals = Number.isInteger(signerMeta.decimals) ? signerMeta.decimals : 18;
  const senderDecimals = Number.isInteger(senderMeta.decimals) ? senderMeta.decimals : 18;

  const signerAmountHuman = fmtAmount(order.signer.amount, signerDecimals);
  const senderAmountHuman = fmtAmount(order.sender.amount, senderDecimals);

  const protocolFeeBps = Number(order.protocolFee || 0);
  const senderAmountBn = ethers.BigNumber.from(order.sender.amount);
  const feeAmountBn = senderAmountBn.mul(protocolFeeBps).div(10000);
  const totalSenderBn = senderAmountBn.add(feeAmountBn);
  const feeAmountHuman = fmtAmount(feeAmountBn.toString(), senderDecimals);
  const totalSenderHuman = fmtAmount(totalSenderBn.toString(), senderDecimals);

  const openOrder = String(order.sender.wallet).toLowerCase() === ethers.constants.AddressZero.toLowerCase();
  const expiryUnix = Number(order.expiry);
  const expiryIso = new Date(expiryUnix * 1000).toISOString();

  const compressed = payload?.airswapWeb?.compressedOrder;
  const orderPath = payload?.airswapWeb?.orderPath || (compressed ? `/order/${compressed}` : '');
  const encodedCompressed = compressed ? encodeURIComponent(compressed) : '';
  const orderUrl = compressed
    ? (WEB_BASE.endsWith('/#/order/') || WEB_BASE.includes('/#/order/')
        ? `${WEB_BASE}${encodedCompressed}`
        : `${WEB_BASE}/order/${encodedCompressed}`)
    : '';

  const miniappUrl = (MINIAPP_BASE && compressed)
    ? `${MINIAPP_BASE}${MINIAPP_BASE.includes('?') ? '&' : '?'}order=${encodedCompressed}`
    : '';

  const humanText = [
    `AirSwap OTC order on Base`,
    `Offer: ${signerAmountHuman} ${signerSymbol}`,
    `For: ${senderAmountHuman} ${senderSymbol}`,
    `Protocol fee: ${feeAmountHuman} ${senderSymbol} (${protocolFeeBps} bps)`,
    `Total taker pays: ${totalSenderHuman} ${senderSymbol}`,
    `Signer: ${short(order.signer.wallet)}`,
    `Sender: ${openOrder ? 'OPEN' : short(order.sender.wallet)}`,
    `Expiry: ${expiryIso}`,
    miniappUrl ? `Miniapp: ${miniappUrl}` : null,
    orderUrl ? `AirSwap Web: ${orderUrl}` : null,
    compressed ? `GBZ1:${compressed}` : null,
  ].filter(Boolean).join('\n');

  const castPayload = {
    type: 'airswap-order',
    version: 1,
    chainId: Number(payload?.meta?.chainId || 8453),
    protocol: 'airswap-swap',
    side: {
      signerGives: {
        token: order.signer.token,
        symbol: signerSymbol,
        amount: order.signer.amount,
        amountHuman: signerAmountHuman,
      },
      senderGives: {
        token: order.sender.token,
        symbol: senderSymbol,
        amount: order.sender.amount,
        amountHuman: senderAmountHuman,
      },
    },
    signerWallet: order.signer.wallet,
    senderWallet: openOrder ? 'OPEN' : order.sender.wallet,
    expiry: {
      unix: expiryUnix,
      iso: expiryIso,
    },
    airswapWeb: {
      compressedOrder: compressed || null,
      orderPath: orderPath || null,
      orderUrl: orderUrl || null,
    },
    miniapp: {
      orderUrl: miniappUrl || null,
    },
  };

  const out = {
    text: humanText,
    payload: castPayload,
  };

  if (OUT) {
    fs.writeFileSync(path.resolve(OUT), JSON.stringify(out, null, 2));
    console.log(`wrote ${OUT}`);
  } else {
    console.log(JSON.stringify(out, null, 2));
  }
}

main();
