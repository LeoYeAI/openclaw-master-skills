import { AxiosInstance } from 'axios';
import { createHttpClient, ClientConfig } from './client.js';
import { SdkError } from './errors.js';

export interface TokenInfo {
  mint: string;
  name: string;
  symbol: string;
  decimals: number;
}

export interface PoolInfo {
  poolPda: string;
  poolId: string;
  operatorKey: string;
  feeBps: number;
}

export interface TransferInfo {
  transferPda: string;
  sender: string;
  recipient: string;
  amount: string;
  amountRaw: string;
  status: string;
  memo?: string;
  token: TokenInfo;
  pool: PoolInfo;
  createTxid: string;
  claimTxid?: string;
  cancelTxid?: string;
  claimableAfter?: string;
  claimableUntil?: string;
  createdAt: string;
  updatedAt: string;
}

export async function getTransfer(
  transferPda: string,
  config?: ClientConfig,
): Promise<TransferInfo> {
  const client = createHttpClient(config);
  const res = await client.get(`/api/transfers/${transferPda}`);
  const transfer = res.data.data.transfer;
  if (!transfer) {
    throw new SdkError('TRANSFER_NOT_FOUND', `Transfer not found: ${transferPda}`);
  }
  return transfer as TransferInfo;
}
