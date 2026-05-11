import { PublicKey } from '@solana/web3.js';
import { AxiosInstance } from 'axios';
import { SdkError } from './errors.js';
import { TransferInfo } from './transfers.js';

export function validateAddress(address: string, field: string): void {
  try {
    new PublicKey(address);
  } catch {
    throw new SdkError('INVALID_ADDRESS', `Invalid ${field} address: ${address}`);
  }
}

export function validateAmount(amount: string): number {
  const num = parseFloat(amount);
  if (isNaN(num) || num <= 0) {
    throw new SdkError('INVALID_AMOUNT', `Amount must be a positive number, got: ${amount}`);
  }
  return num;
}

export async function fetchTransfer(client: AxiosInstance, transferPda: string): Promise<TransferInfo> {
  const res = await client.get(`/api/transfers/${transferPda}`);
  const transfer = res.data?.data?.transfer;
  if (!transfer) {
    throw new SdkError('TRANSFER_NOT_FOUND', `Transfer not found: ${transferPda}`);
  }
  return transfer as TransferInfo;
}

export async function validateClaim(client: AxiosInstance, transferPda: string, claimerAddress: string): Promise<void> {
  const transfer = await fetchTransfer(client, transferPda);

  if (transfer.status !== 'ACTIVE') {
    throw new SdkError('TRANSFER_NOT_ACTIVE', `Transfer is ${transfer.status}, not ACTIVE`);
  }

  if (transfer.recipient !== claimerAddress) {
    throw new SdkError('NOT_RECIPIENT', `Wallet ${claimerAddress} is not the recipient. Recipient is ${transfer.recipient}`);
  }

  const now = Date.now();
  if (transfer.claimableAfter && now < new Date(transfer.claimableAfter).getTime()) {
    throw new SdkError('CLAIM_WINDOW_NOT_OPEN', `Claim window opens at ${transfer.claimableAfter}`);
  }
  if (transfer.claimableUntil && now > new Date(transfer.claimableUntil).getTime()) {
    throw new SdkError('CLAIM_WINDOW_CLOSED', `Claim window closed at ${transfer.claimableUntil}`);
  }
}

export async function validateCancel(client: AxiosInstance, transferPda: string, cancellerAddress: string): Promise<void> {
  const transfer = await fetchTransfer(client, transferPda);

  if (transfer.status !== 'ACTIVE') {
    throw new SdkError('TRANSFER_NOT_ACTIVE', `Transfer is ${transfer.status}, not ACTIVE`);
  }

  if (transfer.sender !== cancellerAddress) {
    throw new SdkError('NOT_SENDER', `Wallet ${cancellerAddress} is not the sender. Sender is ${transfer.sender}`);
  }
}

export async function validatePay(client: AxiosInstance, recipient: string, amount: string, senderAddress: string): Promise<number> {
  validateAddress(recipient, 'recipient');
  const amountNum = validateAmount(amount);

  try {
    const res = await client.get(`/api/wallet/${senderAddress}/balance`);
    const tokens = res.data?.data?.tokens || [];
    const usdc = tokens.find((t: any) => t.symbol === 'USDC');
    if (usdc && parseFloat(usdc.balance) < amountNum) {
      throw new SdkError('INSUFFICIENT_BALANCE', `Insufficient USDC balance: ${usdc.balance} < ${amountNum}`);
    }
  } catch (err) {
    if (err instanceof SdkError) throw err;
    // Balance check is best-effort; don't fail if the API is unreachable
  }

  return amountNum;
}
