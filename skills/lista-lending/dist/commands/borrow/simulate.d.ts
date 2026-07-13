import type { ParsedArgs } from "../../types.js";
import type { BorrowRuntime } from "./types.js";
export declare function buildBorrowSimulationPayload(args: ParsedArgs, runtime: BorrowRuntime): Promise<Record<string, unknown>>;
