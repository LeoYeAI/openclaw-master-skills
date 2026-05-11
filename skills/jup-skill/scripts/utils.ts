/**
 * utils.ts - Shared utility functions for Jupiter API scripts
 */

/**
 * Gets the Jupiter API key from provided value or environment variable
 */
export function getApiKey(providedKey?: string): string | null {
  if (providedKey) return providedKey;
  if (process.env.JUP_API_KEY) return process.env.JUP_API_KEY;
  return null;
}

/**
 * Prints an error message about missing API key with instructions
 */
export function printApiKeyError(): void {
  console.error(`
Error: Jupiter API key is required.

To get an API key:
  1. Visit https://portal.jup.ag
  2. Create an account and generate an API key
  3. Use it via:
     - --api-key flag: pnpm fetch-api --api-key YOUR_KEY ...
     - Environment variable: export JUP_API_KEY=YOUR_KEY

Rate limits:
  - Free tier: 60 requests/minute
  - Pro tier: Up to 30,000 requests/minute
  - Ultra tier: Dynamic scaling with swap volume
`);
}

/**
 * Validates if a string is valid base64
 */
export function isValidBase64(str: string): boolean {
  if (!str || str.length === 0) return false;

  // Base64 regex: allows A-Z, a-z, 0-9, +, /, and = for padding
  const base64Regex = /^[A-Za-z0-9+/]*={0,2}$/;

  // Check regex and length (must be multiple of 4)
  if (!base64Regex.test(str) || str.length % 4 !== 0) {
    return false;
  }

  // Try to decode to verify
  try {
    Buffer.from(str, "base64");
    return true;
  } catch {
    return false;
  }
}

/**
 * Validates if a string is a valid UUID format
 * Accepts any version of UUID (1-5), not just v4
 */
export function isValidUUID(str: string): boolean {
  if (!str) return false;

  // General UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(str);
}
