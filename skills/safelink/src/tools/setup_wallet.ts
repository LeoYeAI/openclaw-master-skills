import { create_agentic_wallet } from "./wallet.js";

export async function setup_agentic_wallet(rawInput: unknown) {
  return create_agentic_wallet(rawInput);
}

