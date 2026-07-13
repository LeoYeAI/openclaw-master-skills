import { TargetType } from "../../context.js";

export interface SdkErrorMappingOptions {
  targetType: TargetType;
  targetId?: string;
  insufficientReason?: string;
  insufficientMessage?: string;
  insufficientKeywords?: string[];
}

const DEFAULT_INSUFFICIENT_KEYWORDS = ["insufficient", "exceeds", "balance"];

export function buildSdkErrorOutput(
  message: string,
  options: SdkErrorMappingOptions
): Record<string, unknown> {
  const targetLabel = options.targetType === TargetType.Vault ? "Vault" : "Market";
  const invalidPhrase =
    options.targetType === TargetType.Vault
      ? message.includes("vault not found") || message.includes("invalid vault")
      : message.includes("market not found") || message.includes("invalid market");

  if (invalidPhrase) {
    return {
      status: "error",
      reason:
        options.targetType === TargetType.Vault ? "invalid_vault" : "invalid_market",
      message: options.targetId
        ? `${targetLabel} ${options.targetId} not found or invalid`
        : `${targetLabel} not found or invalid`,
    };
  }

  const insufficientKeywords = options.insufficientKeywords || DEFAULT_INSUFFICIENT_KEYWORDS;
  const isInsufficient = insufficientKeywords.some((keyword) =>
    message.toLowerCase().includes(keyword.toLowerCase())
  );
  if (isInsufficient && options.insufficientReason && options.insufficientMessage) {
    return {
      status: "error",
      reason: options.insufficientReason,
      message: options.insufficientMessage,
    };
  }

  if (message.includes("RPC") || message.includes("fetch")) {
    return {
      status: "error",
      reason: "rpc_error",
      message,
      hint: "Try setting a custom RPC with: config --set-rpc --chain <chain> --url <url>",
    };
  }

  return {
    status: "error",
    reason: "sdk_error",
    message,
  };
}
