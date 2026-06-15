/**
 * Lightweight LLM Caller
 *
 * Makes API calls to Anthropic for plan generation and reflection.
 * Uses fetch directly to avoid heavy SDK dependencies.
 */
export interface LLMMessage {
    role: "user" | "assistant" | "system";
    content: string;
}
export interface LLMCallOptions {
    messages: LLMMessage[];
    maxTokens?: number;
    temperature?: number;
    model?: string;
}
export interface LLMResponse {
    content: string;
    usage?: {
        inputTokens: number;
        outputTokens: number;
    };
}
export interface LLMCallerConfig {
    apiKey?: string;
    model?: string;
    maxTokens?: number;
    baseUrl?: string;
}
export declare class LLMCaller {
    private apiKey;
    private model;
    private maxTokens;
    private baseUrl;
    constructor(config?: LLMCallerConfig);
    /**
     * Check if the caller is configured with an API key
     */
    isConfigured(): boolean;
    /**
     * Make an LLM call
     */
    call(options: LLMCallOptions): Promise<LLMResponse>;
    /**
     * Convenience method matching the LLMCaller type expected by orchestrator
     */
    invoke(options: {
        messages: Array<{
            role: string;
            content: string | unknown[];
        }>;
        maxTokens?: number;
    }): Promise<{
        content: string;
    }>;
}
export declare function getLLMCaller(config?: LLMCallerConfig): LLMCaller;
export declare function createLLMCaller(config?: LLMCallerConfig): LLMCaller;
export declare function resetLLMCaller(): void;
export declare function createOrchestratorLLMCaller(config?: LLMCallerConfig): (options: {
    messages: Array<{
        role: string;
        content: string | unknown[];
    }>;
    maxTokens?: number;
}) => Promise<{
    content: string;
}>;
//# sourceMappingURL=caller.d.ts.map