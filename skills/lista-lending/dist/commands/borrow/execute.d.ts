import type { CommandResult } from "../shared/result.js";
import type { BorrowRuntime } from "./types.js";
export declare function executeBorrowTransaction(runtime: BorrowRuntime, amount: string): Promise<CommandResult>;
