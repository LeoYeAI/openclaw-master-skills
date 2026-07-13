import { parseArgs } from "util";
function parseCsv(value) {
    if (!value)
        return undefined;
    const items = value
        .split(",")
        .map((v) => v.trim())
        .filter(Boolean);
    return items.length > 0 ? items : undefined;
}
export function parseCliInput() {
    const { positionals, values } = parseArgs({
        allowPositionals: true,
        options: {
            vault: { type: "string" },
            market: { type: "string" },
            amount: { type: "string" },
            chain: { type: "string" },
            address: { type: "string" },
            page: { type: "string" },
            "page-size": { type: "string" },
            sort: { type: "string" },
            order: { type: "string" },
            scope: { type: "string" },
            zone: { type: "string" },
            keyword: { type: "string" },
            assets: { type: "string" },
            curators: { type: "string" },
            loans: { type: "string" },
            collaterals: { type: "string" },
            "wallet-topic": { type: "string" },
            "wallet-address": { type: "string" },
            "withdraw-all": { type: "boolean" },
            "repay-all": { type: "boolean" },
            simulate: { type: "boolean" },
            "simulate-supply": { type: "string" },
            show: { type: "boolean" },
            clear: { type: "boolean" },
            "set-rpc": { type: "boolean" },
            "clear-rpc": { type: "boolean" },
            url: { type: "string" },
            "debug-log-file": { type: "string" },
            help: { type: "boolean", short: "h" },
        },
    });
    const command = positionals[0];
    const page = typeof values.page === "string" && values.page.trim() !== ""
        ? Number(values.page)
        : undefined;
    const pageSize = typeof values["page-size"] === "string" && values["page-size"].trim() !== ""
        ? Number(values["page-size"])
        : undefined;
    return {
        command,
        help: Boolean(values.help),
        debugLogFile: values["debug-log-file"],
        args: {
            vault: values.vault,
            market: values.market,
            amount: values.amount,
            chain: values.chain,
            walletTopic: values["wallet-topic"],
            walletAddress: values["wallet-address"],
            withdrawAll: values["withdraw-all"],
            repayAll: values["repay-all"],
            simulate: values.simulate,
            simulateSupply: values["simulate-supply"],
            help: values.help,
        },
        configArgs: {
            show: values.show,
            setRpc: values["set-rpc"],
            clearRpc: values["clear-rpc"],
            chain: values.chain,
            url: values.url,
        },
        vaultsArgs: {
            chain: values.chain,
            page,
            pageSize,
            sort: values.sort,
            order: values.order,
            zone: values.zone,
            keyword: values.keyword,
            assets: parseCsv(values.assets),
            curators: parseCsv(values.curators),
        },
        marketsArgs: {
            chain: values.chain,
            page,
            pageSize,
            sort: values.sort,
            order: values.order,
            zone: values.zone,
            keyword: values.keyword,
            loans: parseCsv(values.loans),
            collaterals: parseCsv(values.collaterals),
        },
        holdingsArgs: {
            address: values.address || values["wallet-address"],
            scope: values.scope,
        },
        selectArgs: {
            vault: values.vault,
            market: values.market,
            chain: values.chain,
            walletTopic: values["wallet-topic"],
            walletAddress: values["wallet-address"],
            clear: values.clear,
            show: values.show,
        },
    };
}
