import { fatal } from "./output.js"

// 安全解析 BigInt，给出友好的错误提示
export function parseBigInt(value: string, fieldName: string): bigint {
  try {
    return BigInt(value)
  } catch {
    fatal(`Invalid ${fieldName}: "${value}". Must be a positive integer.`)
  }
}
