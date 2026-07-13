import { TargetType } from "../../context.js";
export interface SdkErrorMappingOptions {
    targetType: TargetType;
    targetId?: string;
    insufficientReason?: string;
    insufficientMessage?: string;
    insufficientKeywords?: string[];
}
export declare function buildSdkErrorOutput(message: string, options: SdkErrorMappingOptions): Record<string, unknown>;
