export class SdkError extends Error {
  constructor(
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = 'SdkError';
  }
}

export const ANCHOR_ERROR_MAP: Record<number, { code: string; message: string }> = {
  6000: { code: 'ANCHOR_MATH_OVERFLOW', message: 'Mathematical overflow occurred' },
  6001: { code: 'ANCHOR_TRANSFER_NOT_ACTIVE', message: 'Transfer is not in active status' },
  6002: { code: 'ANCHOR_CANNOT_CLAIM', message: 'Claim deadline has passed' },
  6003: { code: 'ANCHOR_CONDITIONS_NOT_MET', message: 'Release conditions not met' },
  6004: { code: 'ANCHOR_INVALID_CONDITION', message: 'Invalid condition parameters' },
  6005: { code: 'ANCHOR_INSUFFICIENT_FUNDS', message: 'Insufficient funds in vault' },
  6006: { code: 'ANCHOR_POOL_PAUSED', message: 'Pool is paused' },
  6007: { code: 'ANCHOR_UNAUTHORIZED', message: 'Unauthorized action' },
  6008: { code: 'ANCHOR_INVALID_TIME_WINDOW', message: 'Invalid time window' },
  6009: { code: 'ANCHOR_DEPOSIT_TOO_SMALL', message: 'Deposit amount too small' },
  6010: { code: 'ANCHOR_INVALID_FEE_CONFIG', message: 'Invalid fee configuration' },
  6011: { code: 'ANCHOR_INVALID_TRANSFER_FEE', message: 'Invalid transfer fee' },
  6012: { code: 'ANCHOR_TRANSFER_ALREADY_CLAIMED', message: 'Transfer already claimed' },
  6013: { code: 'ANCHOR_TRANSFER_ALREADY_CANCELLED', message: 'Transfer already cancelled' },
  6014: { code: 'ANCHOR_TRANSFER_ALREADY_REJECTED', message: 'Transfer already rejected' },
  6015: { code: 'ANCHOR_TRANSFER_EXPIRED', message: 'Transfer is expired' },
  6016: { code: 'ANCHOR_ONLY_SENDER_CAN_CANCEL', message: 'Only sender can cancel transfer' },
  6017: { code: 'ANCHOR_ONLY_RECIPIENT_CAN_CLAIM', message: 'Only recipient can claim transfer' },
  6018: { code: 'ANCHOR_ONLY_OPERATOR_CAN_REJECT', message: 'Only operator can reject transfer' },
  6019: { code: 'ANCHOR_INVALID_MEMO_LENGTH', message: 'Invalid memo length' },
  6020: { code: 'ANCHOR_CLAIM_DEADLINE_NOT_PASSED', message: 'Claim deadline has not passed' },
  6021: { code: 'ANCHOR_CALCULATION_ERROR', message: 'Calculation error' },
  6022: { code: 'ANCHOR_MISSING_ACCOUNT', message: 'Missing required account' },
  6023: { code: 'ANCHOR_INVALID_MINT', message: 'Invalid mint' },
  6024: { code: 'ANCHOR_STALE_POOL_VALUE', message: 'Pool value is stale and must be updated' },
  6025: { code: 'ANCHOR_INVALID_OPERATION', message: 'Invalid operation for this pool type' },
  6026: { code: 'ANCHOR_OUTSTANDING_TRANSFERS', message: 'Cannot reset pool with outstanding transfers' },
  6027: { code: 'ANCHOR_INVALID_TRANSFER', message: 'Invalid transfer' },
  6028: { code: 'ANCHOR_TRANSFER_ALREADY_DECLINED', message: 'Transfer already declined' },
  6029: { code: 'ANCHOR_ONLY_RECIPIENT_CAN_DECLINE', message: 'Only recipient can decline transfer' },
};

export const SILKYSIG_ERROR_MAP: Record<number, { code: string; message: string }> = {
  6000: { code: 'POLICY_UNAUTHORIZED', message: 'Unauthorized: signer is not owner or operator' },
  6001: { code: 'POLICY_EXCEEDS_TX_LIMIT', message: 'Transfer exceeds operator per-transaction limit' },
  6002: { code: 'ACCOUNT_PAUSED', message: 'Account is paused' },
  6003: { code: 'MAX_OPERATORS', message: 'Maximum operators reached' },
  6004: { code: 'OPERATOR_NOT_FOUND', message: 'Operator not found' },
  6005: { code: 'OPERATOR_EXISTS', message: 'Operator slot already occupied' },
  6006: { code: 'MATH_OVERFLOW', message: 'Mathematical overflow' },
  6007: { code: 'AMOUNT_MUST_BE_POSITIVE', message: 'Amount must be positive' },
  6008: { code: 'DRIFT_USER_ALREADY_INITIALIZED', message: 'Drift user already initialized' },
  6009: { code: 'DRIFT_DEPOSIT_FAILED', message: 'Drift deposit failed' },
  6010: { code: 'DRIFT_WITHDRAW_FAILED', message: 'Drift withdrawal failed' },
  6011: { code: 'INVALID_DRIFT_USER', message: 'Invalid Drift user account' },
  6012: { code: 'MISSING_DRIFT_ACCOUNTS', message: 'Missing required Drift accounts' },
  6013: { code: 'INVALID_DRIFT_PROGRAM', message: 'Invalid Drift program ID' },
  6014: { code: 'DRIFT_DELETE_USER_FAILED', message: 'Failed to delete Drift user' },
};

export function toSilkysigError(err: unknown): SdkError {
  if (err instanceof SdkError) return err;

  const message = err instanceof Error ? err.message : String(err);

  const hexMatch = message.match(/0x([0-9a-fA-F]+)/);
  if (hexMatch) {
    const errorCode = parseInt(hexMatch[1], 16);
    const mapped = SILKYSIG_ERROR_MAP[errorCode];
    if (mapped) {
      return new SdkError(mapped.code, mapped.message);
    }
  }

  return new SdkError('UNKNOWN_ERROR', message);
}

export function toSdkError(err: unknown): SdkError {
  if (err instanceof SdkError) return err;

  const message = err instanceof Error ? err.message : String(err);

  // Parse Anchor hex error codes from simulation messages (e.g. "0x1770")
  const hexMatch = message.match(/0x([0-9a-fA-F]+)/);
  if (hexMatch) {
    const errorCode = parseInt(hexMatch[1], 16);
    const anchor = ANCHOR_ERROR_MAP[errorCode];
    if (anchor) {
      return new SdkError(anchor.code, anchor.message);
    }
  }

  return new SdkError('UNKNOWN_ERROR', message);
}
