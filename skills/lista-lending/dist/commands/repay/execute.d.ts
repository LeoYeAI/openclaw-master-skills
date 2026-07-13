import type { ParsedArgs } from "../../types.js";
import type { CommandResult } from "../shared/result.js";
import type { RepayRuntime } from "./types.js";
export declare function executeRepayTransaction(runtime: RepayRuntime, args: Pick<ParsedArgs, "amount" | "repayAll">): Promise<CommandResult>;
