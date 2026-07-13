import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));

export const WALLET_CONNECT_CLI = resolve(
  __dirname,
  "../../../lista-wallet-connect/dist/cli/cli.bundle.mjs"
);

const EXPLORER_URLS: Record<string, string> = {
  "eip155:56": "https://bscscan.com/tx/",
  "eip155:1": "https://etherscan.io/tx/",
};

export function getExplorerUrl(chain: string, txHash: string): string {
  const baseUrl = EXPLORER_URLS[chain] || EXPLORER_URLS["eip155:56"];
  return `${baseUrl}${txHash}`;
}
