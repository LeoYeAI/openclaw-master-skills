import type { ParsedArgs } from "../../types.js";
import type { RepayRuntime } from "./types.js";
export declare function buildRepaySimulationPayload(args: ParsedArgs, runtime: RepayRuntime): Promise<Record<string, unknown>>;
