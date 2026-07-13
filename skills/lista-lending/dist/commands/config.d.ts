/**
 * Config command - manage RPC URLs and other settings
 */
export interface ConfigArgs {
    show?: boolean;
    setRpc?: boolean;
    clearRpc?: boolean;
    chain?: string;
    url?: string;
}
export declare function cmdConfig(args: ConfigArgs): Promise<void>;
