#!/bin/bash
# OpenclawCash CLI Tool
# Usage: ./agentwalletapi.sh <command> [options]
#
# Requirements: curl (jq optional for pretty output)
# Sensitive env var: AGENTWALLETAPI_KEY (in .env)
#
# Commands:
#   wallets                     List all wallets
#   user-tag-get                Read global checkout user tag for this API key owner
#   user-tag-set <userTag> [--yes]   Set global checkout user tag once (immutable after set)
#   wallet <walletId|publicWalletId|walletLabel> [chain]   Get one wallet detail with balances
#   create <label> [network] <passphraseEnvVar> [--yes]    Create a wallet (default network: sepolia)
#   import <label> <network> [privateKey|-] [--yes]   Import wallet (network: mainnet|polygon-mainnet|solana-mainnet)
#   transactions <walletId|publicWalletId> [chain]     List merged transaction history for a wallet
#   balance <walletId|publicWalletId> [token] [chain]  Check balances for a wallet
#   transfer <walletId|publicWalletId> <to> <amount> [token] [chain] [--yes]   Send native/token transfer
#   tokens [network] [chain]            List supported tokens (default: mainnet)
#   quote <network> <tokenIn> <tokenOut> <amountInBaseUnits> [chain]   Get swap quote
#   swap <walletId|publicWalletId> <tokenIn> <tokenOut> <amountInBaseUnits> [slippage] [chain] [--yes]
#   approve <walletId|publicWalletId> <tokenAddress> <spender> <amountBaseUnits> [chain] [--yes]   Approve ERC-20 allowance
#   checkout-payreq-create <walletSelector> <amountBaseUnits> [expiresSec] [autoReleaseSec] [disputeWindowSec] [--yes]
#   checkout-payreq-get <payreqId>
#   checkout-escrow-get <escrowId>
#   checkout-funding-confirm <escrowId> <txHash> [minConfirmations] [--yes]
#   checkout-accept <escrowId> [--yes]
#   checkout-proof <escrowId> <proofHash> [proofUrl] [--yes]
#   checkout-dispute <escrowId> <reasonCode> [--yes]
#   checkout-quick-pay <escrowId> <walletSelector> [--yes]
#   checkout-swap-and-pay-quote <escrowId> <walletSelector>
#   checkout-swap-and-pay-confirm <escrowId> <walletSelector> [slippage] [--yes]
#   checkout-release <escrowId> [--yes]
#   checkout-refund <escrowId> [--yes]
#   checkout-cancel <escrowId> [--yes]
#   checkout-webhooks-list
#   checkout-webhook-create <url> [eventTypesCsv] [enabled] [--yes]
#   checkout-webhook-update <id> [url] [eventTypesCsv] [enabled] [--yes]
#   checkout-webhook-delete <id> [--yes]
#   polymarket-limit <walletSelector> <tokenId> <BUY|SELL> <price> <size> [--yes]
#   polymarket-market <walletSelector> <tokenId> <BUY|SELL> <amount> [orderType] [worstPrice] [--yes]
#   polymarket-account <walletSelector>
#   polymarket-resolve <marketUrl|slug> <outcome>
#   polymarket-orders <walletSelector> [status] [limit] [cursor]
#   polymarket-activity <walletSelector> [limit] [cursor]
#   polymarket-positions <walletSelector> [limit]
#   polymarket-redeem <walletSelector> [tokenId|all] [limit] [--yes]
#   polymarket-cancel <walletSelector> <orderId> [--yes]

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$SKILL_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found. Run setup first:"
    echo "  bash $SKILL_DIR/scripts/setup.sh"
    exit 1
fi

source "$ENV_FILE"

if [ -z "$AGENTWALLETAPI_KEY" ] || [ "$AGENTWALLETAPI_KEY" = "occ_your_api_key" ]; then
    echo "Error: API key not configured. Edit $ENV_FILE and set AGENTWALLETAPI_KEY."
    exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required but not installed."
    exit 1
fi

BASE_URL="${AGENTWALLETAPI_URL:-https://openclawcash.com}"

FORCE_RISKY=0
FILTERED_ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--yes" ]; then
        FORCE_RISKY=1
    else
        FILTERED_ARGS+=("$arg")
    fi
done
set -- "${FILTERED_ARGS[@]}"
COMMAND="$1"

json_escape_var() {
    DEST_VAR="$1"
    VALUE="${2-}"
    VALUE="${VALUE//\\/\\\\}"
    VALUE="${VALUE//\"/\\\"}"
    VALUE="${VALUE//$'\n'/\\n}"
    VALUE="${VALUE//$'\r'/\\r}"
    VALUE="${VALUE//$'\t'/\\t}"
    printf -v "$DEST_VAR" '%s' "$VALUE"
}

url_encode_var() {
    DEST_VAR="$1"
    VALUE="${2-}"
    ENCODED=""
    for (( i=0; i<${#VALUE}; i++ )); do
        CHAR="${VALUE:i:1}"
        case "$CHAR" in
            [a-zA-Z0-9.~_-]) ENCODED+="$CHAR" ;;
            *)
                printf -v HEX '%%%02X' "'$CHAR"
                ENCODED+="$HEX"
                ;;
        esac
    done
    printf -v "$DEST_VAR" '%s' "$ENCODED"
}

append_query_param() {
    DEST_VAR="$1"
    KEY="$2"
    RAW_VALUE="$3"
    URL="${!DEST_VAR}"
    url_encode_var ENCODED_VALUE "$RAW_VALUE"
    if [[ "$URL" == *\?* ]]; then
        URL="${URL}&${KEY}=${ENCODED_VALUE}"
    else
        URL="${URL}?${KEY}=${ENCODED_VALUE}"
    fi
    printf -v "$DEST_VAR" '%s' "$URL"
}

require_uint() {
    NAME="$1"
    VALUE="$2"
    if ! [[ "$VALUE" =~ ^[0-9]+$ ]]; then
        echo "Error: $NAME must be an unsigned integer."
        exit 1
    fi
}

is_uint() {
    VALUE="$1"
    [[ "$VALUE" =~ ^[0-9]+$ ]]
}

is_public_wallet_id() {
    VALUE="$1"
    [[ "$VALUE" =~ ^[A-Za-z0-9]{6,12}$ ]]
}

append_wallet_selector_query() {
    DEST_VAR="$1"
    SELECTOR="$2"
    if is_uint "$SELECTOR" || is_public_wallet_id "$SELECTOR"; then
        append_query_param "$DEST_VAR" "walletId" "$SELECTOR"
    else
        append_query_param "$DEST_VAR" "walletLabel" "$SELECTOR"
    fi
}

append_wallet_id_json_field() {
    DEST_VAR="$1"
    SELECTOR="$2"
    BODY="${!DEST_VAR}"
    if is_uint "$SELECTOR"; then
        BODY="$BODY\"walletId\": $SELECTOR"
    else
        json_escape_var WALLET_ID_ESC "$SELECTOR"
        BODY="$BODY\"walletId\": \"$WALLET_ID_ESC\""
    fi
    printf -v "$DEST_VAR" '%s' "$BODY"
}

append_wallet_or_address_json_field() {
    DEST_VAR="$1"
    SELECTOR="$2"
    BODY="${!DEST_VAR}"
    if [[ "$SELECTOR" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
        json_escape_var WALLET_ADDR_ESC "$SELECTOR"
        BODY="$BODY\"walletAddress\": \"$WALLET_ADDR_ESC\""
    else
        append_wallet_id_json_field "$DEST_VAR" "$SELECTOR"
        return
    fi
    printf -v "$DEST_VAR" '%s' "$BODY"
}

require_decimal() {
    NAME="$1"
    VALUE="$2"
    if ! [[ "$VALUE" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        echo "Error: $NAME must be a number."
        exit 1
    fi
}

require_polymarket_token_id() {
    VALUE="$1"
    if ! [[ "$VALUE" =~ ^[0-9]+$ ]]; then
        echo "Error: tokenId must be a numeric Polymarket outcome token ID."
        echo "Hint: resolve market + outcome first:"
        echo "  agentwalletapi.sh polymarket-resolve <marketUrl|slug> <outcome>"
        exit 1
    fi
}

pretty_print_json() {
    if command -v jq >/dev/null 2>&1; then
        jq . 2>/dev/null || cat
    else
        cat
    fi
}

new_idempotency_key() {
    echo "cli-$(date +%s)-$RANDOM"
}

confirm_risky_action() {
    ACTION="$1"
    if [ "$FORCE_RISKY" -eq 1 ]; then
        return 0
    fi

    if [ ! -t 0 ]; then
        echo "Error: $ACTION is a high-risk action. Re-run with --yes to confirm."
        exit 1
    fi

    echo "WARNING: $ACTION can move funds or import sensitive keys."
    echo "Target API host: $BASE_URL"
    printf "Type YES to continue: "
    read -r ANSWER
    if [ "$ANSWER" != "YES" ]; then
        echo "Cancelled."
        exit 1
    fi
}

case "$COMMAND" in
    wallets)
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$BASE_URL/api/agent/wallets" | pretty_print_json
        ;;

    user-tag-get)
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$BASE_URL/api/agent/user-tag" | pretty_print_json
        ;;

    user-tag-set)
        USER_TAG="$2"
        if [ -z "$USER_TAG" ]; then
            echo "Usage: agentwalletapi.sh user-tag-set <userTag> [--yes]"
            exit 1
        fi
        json_escape_var USER_TAG_ESC "$USER_TAG"
        BODY="{\"userTag\":\"$USER_TAG_ESC\"}"
        curl -s -X PUT \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/user-tag" | pretty_print_json
        ;;

    wallet)
        SELECTOR="$2"
        CHAIN="$3"
        if [ -z "$SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh wallet <walletId|publicWalletId|walletLabel> [chain]"
            exit 1
        fi
        URL="$BASE_URL/api/agent/wallet"
        append_wallet_selector_query URL "$SELECTOR"
        if [ -n "$CHAIN" ]; then
            append_query_param URL "chain" "$CHAIN"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    create)
        confirm_risky_action "Wallet creation"
        LABEL="$2"
        NETWORK="${3:-sepolia}"
        PASSPHRASE_ENV_VAR="$4"
        if [ -z "$LABEL" ] || [ -z "$PASSPHRASE_ENV_VAR" ]; then
            echo "Usage: agentwalletapi.sh create <label> [network] <passphraseEnvVar> [--yes]"
            echo "  network options: sepolia | mainnet | solana-devnet | solana-testnet | solana-mainnet"
            echo "  Example:"
            echo "    export WALLET_EXPORT_PASSPHRASE_OPS='your-strong-passphrase'"
            echo "    agentwalletapi.sh create \"Ops Wallet\" sepolia WALLET_EXPORT_PASSPHRASE_OPS --yes"
            exit 1
        fi
        PASSPHRASE_VALUE="${!PASSPHRASE_ENV_VAR}"
        if [ -z "$PASSPHRASE_VALUE" ]; then
            echo "Error: env var $PASSPHRASE_ENV_VAR is not set."
            echo "Store the wallet export passphrase in an env var first, then retry."
            exit 1
        fi
        json_escape_var LABEL_ESC "$LABEL"
        json_escape_var NETWORK_ESC "$NETWORK"
        json_escape_var PASSPHRASE_ESC "$PASSPHRASE_VALUE"
        json_escape_var PASSPHRASE_ENV_ESC "$PASSPHRASE_ENV_VAR"
        BODY="{\"label\":\"$LABEL_ESC\",\"network\":\"$NETWORK_ESC\",\"exportPassphrase\":\"$PASSPHRASE_ESC\",\"exportPassphraseStorageType\":\"env\",\"exportPassphraseStorageRef\":\"$PASSPHRASE_ENV_ESC\",\"confirmExportPassphraseSaved\":true}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/wallets/create" | pretty_print_json
        unset PASSPHRASE_VALUE
        ;;

    import)
        confirm_risky_action "Wallet import"
        if [ "$FORCE_RISKY" -eq 1 ]; then
            echo "Import confirmation accepted via --yes."
        fi
        LABEL="$2"
        NETWORK="$3"
        PRIVATE_KEY="$4"
        if [ -z "$LABEL" ] || [ -z "$NETWORK" ]; then
            echo "Usage: agentwalletapi.sh import <label> <network> [privateKey|-] [--yes]"
            echo "  network options: mainnet | polygon-mainnet | solana-mainnet"
            echo "  pass '-' to read private key from stdin (recommended for automation)"
            exit 1
        fi
        if [ "$PRIVATE_KEY" = "-" ]; then
            if [ -t 0 ]; then
                echo "Error: private key input set to '-' but stdin is empty."
                echo "Example: printf '%s' '<private_key>' | agentwalletapi.sh import <label> <network> - --yes"
                exit 1
            fi
            IFS= read -r PRIVATE_KEY
        elif [ -n "$PRIVATE_KEY" ]; then
            echo "WARNING: passing private key as a CLI argument can leak in shell history/process logs."
            echo "Safer options: omit [privateKey] for hidden prompt, or pass '-' and pipe via stdin."
        fi
        if [ -z "$PRIVATE_KEY" ]; then
            if [ ! -t 0 ]; then
                echo "Error: private key missing. Provide as argument or run interactively to be prompted."
                exit 1
            fi
            printf "Enter private key (input hidden): "
            stty -echo
            read -r PRIVATE_KEY
            stty echo
            echo ""
        fi
        json_escape_var LABEL_ESC "$LABEL"
        json_escape_var NETWORK_ESC "$NETWORK"
        json_escape_var PRIVATE_KEY_ESC "$PRIVATE_KEY"
        BODY="{\"label\":\"$LABEL_ESC\",\"network\":\"$NETWORK_ESC\",\"privateKey\":\"$PRIVATE_KEY_ESC\"}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/wallets/import" | pretty_print_json
        unset PRIVATE_KEY
        unset BODY
        ;;

    transactions)
        WALLET_ID="$2"
        CHAIN="$3"
        if [ -z "$WALLET_ID" ]; then
            echo "Usage: agentwalletapi.sh transactions <walletId|publicWalletId> [chain]"
            exit 1
        fi
        URL="$BASE_URL/api/agent/transactions"
        append_query_param URL "walletId" "$WALLET_ID"
        if [ -n "$CHAIN" ]; then
            append_query_param URL "chain" "$CHAIN"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    balance)
        WALLET_ID="$2"
        TOKEN_FILTER="$3"
        CHAIN="$4"
        if [ -z "$WALLET_ID" ]; then
            echo "Usage: agentwalletapi.sh balance <walletId|publicWalletId> [token] [chain]"
            exit 1
        fi
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        if [ -n "$TOKEN_FILTER" ]; then
            json_escape_var TOKEN_FILTER_ESC "$TOKEN_FILTER"
            BODY="$BODY, \"token\": \"$TOKEN_FILTER_ESC\""
        fi
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/token-balance" | pretty_print_json
        ;;

    transfer)
        confirm_risky_action "Transfer"
        WALLET_ID="$2"
        TO="$3"
        AMOUNT="$4"
        TOKEN="${5:-ETH}"
        CHAIN="$6"
        if [ -z "$WALLET_ID" ] || [ -z "$TO" ] || [ -z "$AMOUNT" ]; then
            echo "Usage: agentwalletapi.sh transfer <walletId|publicWalletId> <to> <amount> [token] [chain]"
            echo "  token defaults to the wallet's native token (ETH/SOL) if not specified"
            exit 1
        fi
        json_escape_var TO_ESC "$TO"
        json_escape_var AMOUNT_ESC "$AMOUNT"
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        BODY="$BODY, \"to\": \"$TO_ESC\", \"amountDisplay\": \"$AMOUNT_ESC\""
        if [ "$TOKEN" != "ETH" ]; then
            json_escape_var TOKEN_ESC "$TOKEN"
            BODY="$BODY, \"token\": \"$TOKEN_ESC\""
        fi
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/transfer" | pretty_print_json
        ;;

    tokens)
        NETWORK="${2:-mainnet}"
        CHAIN="$3"
        URL="$BASE_URL/api/agent/supported-tokens"
        append_query_param URL "network" "$NETWORK"
        if [ -n "$CHAIN" ]; then
            append_query_param URL "chain" "$CHAIN"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    quote)
        NETWORK="$2"
        TOKEN_IN="$3"
        TOKEN_OUT="$4"
        AMOUNT_IN="$5"
        CHAIN="$6"
        if [ -z "$NETWORK" ] || [ -z "$TOKEN_IN" ] || [ -z "$TOKEN_OUT" ] || [ -z "$AMOUNT_IN" ]; then
            echo "Usage: agentwalletapi.sh quote <network> <tokenIn> <tokenOut> <amountInBaseUnits> [chain]"
            exit 1
        fi
        json_escape_var TOKEN_IN_ESC "$TOKEN_IN"
        json_escape_var TOKEN_OUT_ESC "$TOKEN_OUT"
        json_escape_var AMOUNT_IN_ESC "$AMOUNT_IN"
        BODY="{\"tokenIn\":\"$TOKEN_IN_ESC\",\"tokenOut\":\"$TOKEN_OUT_ESC\",\"amountIn\":\"$AMOUNT_IN_ESC\""
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        URL="$BASE_URL/api/agent/quote"
        append_query_param URL "network" "$NETWORK"
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$URL" | pretty_print_json
        ;;

    swap)
        confirm_risky_action "Swap"
        WALLET_ID="$2"
        TOKEN_IN="$3"
        TOKEN_OUT="$4"
        AMOUNT_IN="$5"
        SLIPPAGE="${6:-0.5}"
        CHAIN="$7"
        if [ -z "$WALLET_ID" ] || [ -z "$TOKEN_IN" ] || [ -z "$TOKEN_OUT" ] || [ -z "$AMOUNT_IN" ]; then
            echo "Usage: agentwalletapi.sh swap <walletId|publicWalletId> <tokenIn> <tokenOut> <amountInBaseUnits> [slippage] [chain]"
            exit 1
        fi
        require_decimal "slippage" "$SLIPPAGE"
        json_escape_var TOKEN_IN_ESC "$TOKEN_IN"
        json_escape_var TOKEN_OUT_ESC "$TOKEN_OUT"
        json_escape_var AMOUNT_IN_ESC "$AMOUNT_IN"
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        BODY="$BODY,\"tokenIn\":\"$TOKEN_IN_ESC\",\"tokenOut\":\"$TOKEN_OUT_ESC\",\"amountIn\":\"$AMOUNT_IN_ESC\",\"slippage\":$SLIPPAGE"
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/swap" | pretty_print_json
        ;;

    approve)
        confirm_risky_action "Token approval"
        WALLET_ID="$2"
        TOKEN_ADDRESS="$3"
        SPENDER="$4"
        AMOUNT="$5"
        CHAIN="$6"
        if [ -z "$WALLET_ID" ] || [ -z "$TOKEN_ADDRESS" ] || [ -z "$SPENDER" ] || [ -z "$AMOUNT" ]; then
            echo "Usage: agentwalletapi.sh approve <walletId|publicWalletId> <tokenAddress> <spender> <amountBaseUnits> [chain]"
            exit 1
        fi
        json_escape_var TOKEN_ADDRESS_ESC "$TOKEN_ADDRESS"
        json_escape_var SPENDER_ESC "$SPENDER"
        json_escape_var AMOUNT_ESC "$AMOUNT"
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        BODY="$BODY,\"tokenAddress\":\"$TOKEN_ADDRESS_ESC\",\"spender\":\"$SPENDER_ESC\",\"amount\":\"$AMOUNT_ESC\""
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/approve" | pretty_print_json
        ;;

    checkout-payreq-create)
        confirm_risky_action "Checkout pay request creation"
        WALLET_SELECTOR="$2"
        AMOUNT="$3"
        EXPIRES="${4:-3600}"
        AUTO_RELEASE="${5:-3600}"
        DISPUTE_WINDOW="${6:-3600}"
        if [ -z "$WALLET_SELECTOR" ] || [ -z "$AMOUNT" ]; then
            echo "Usage: agentwalletapi.sh checkout-payreq-create <walletSelector> <amountBaseUnits> [expiresSec] [autoReleaseSec] [disputeWindowSec] [--yes]"
            exit 1
        fi
        require_uint "expiresSec" "$EXPIRES"
        require_uint "autoReleaseSec" "$AUTO_RELEASE"
        require_uint "disputeWindowSec" "$DISPUTE_WINDOW"
        if [ "$EXPIRES" -lt 3600 ] || [ "$AUTO_RELEASE" -lt 3600 ] || [ "$DISPUTE_WINDOW" -lt 3600 ]; then
            echo "expiresSec, autoReleaseSec, and disputeWindowSec must each be at least 3600 (1 hour)." >&2
            exit 1
        fi
        if [ "$DISPUTE_WINDOW" -gt "$AUTO_RELEASE" ]; then
            echo "disputeWindowSec must be less than or equal to autoReleaseSec." >&2
            exit 1
        fi
        json_escape_var AMOUNT_ESC "$AMOUNT"
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        BODY="$BODY, \"amount\": \"$AMOUNT_ESC\", \"expiresInSeconds\": $EXPIRES, \"autoReleaseSeconds\": $AUTO_RELEASE, \"disputeWindowSeconds\": $DISPUTE_WINDOW}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/payreq" | pretty_print_json
        ;;

    checkout-payreq-get)
        PAYREQ_ID="$2"
        if [ -z "$PAYREQ_ID" ]; then
            echo "Usage: agentwalletapi.sh checkout-payreq-get <payreqId>"
            exit 1
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$BASE_URL/api/agent/checkout/payreq/$PAYREQ_ID" | pretty_print_json
        ;;

    checkout-escrow-get)
        ESCROW_ID="$2"
        if [ -z "$ESCROW_ID" ]; then
            echo "Usage: agentwalletapi.sh checkout-escrow-get <escrowId>"
            exit 1
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID" | pretty_print_json
        ;;

    checkout-funding-confirm)
        confirm_risky_action "Checkout funding confirm"
        ESCROW_ID="$2"
        TX_HASH="$3"
        MIN_CONFIRMATIONS="$4"
        if [ -z "$ESCROW_ID" ] || [ -z "$TX_HASH" ]; then
            echo "Usage: agentwalletapi.sh checkout-funding-confirm <escrowId> <txHash> [minConfirmations] [--yes]"
            exit 1
        fi
        json_escape_var TX_HASH_ESC "$TX_HASH"
        BODY="{\"txHash\":\"$TX_HASH_ESC\""
        if [ -n "$MIN_CONFIRMATIONS" ]; then
            require_uint "minConfirmations" "$MIN_CONFIRMATIONS"
            BODY="$BODY, \"minConfirmations\": $MIN_CONFIRMATIONS"
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/funding-confirm" | pretty_print_json
        ;;

    checkout-accept)
        confirm_risky_action "Checkout accept"
        ESCROW_ID="$2"
        if [ -z "$ESCROW_ID" ]; then
            echo "Usage: agentwalletapi.sh checkout-accept <escrowId> [--yes]"
            exit 1
        fi
        BODY="{}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/accept" | pretty_print_json
        ;;

    checkout-proof)
        confirm_risky_action "Checkout proof submit"
        ESCROW_ID="$2"
        PROOF_HASH="$3"
        PROOF_URL="$4"
        if [ -z "$ESCROW_ID" ] || [ -z "$PROOF_HASH" ]; then
            echo "Usage: agentwalletapi.sh checkout-proof <escrowId> <proofHash> [proofUrl] [--yes]"
            exit 1
        fi
        json_escape_var PROOF_HASH_ESC "$PROOF_HASH"
        BODY="{\"proofHash\":\"$PROOF_HASH_ESC\""
        if [ -n "$PROOF_URL" ]; then
            json_escape_var PROOF_URL_ESC "$PROOF_URL"
            BODY="$BODY, \"proofUrl\": \"$PROOF_URL_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/proof" | pretty_print_json
        ;;

    checkout-dispute)
        confirm_risky_action "Checkout dispute open"
        ESCROW_ID="$2"
        REASON_CODE="$3"
        if [ -z "$ESCROW_ID" ] || [ -z "$REASON_CODE" ]; then
            echo "Usage: agentwalletapi.sh checkout-dispute <escrowId> <reasonCode> [--yes]"
            exit 1
        fi
        json_escape_var REASON_CODE_ESC "$REASON_CODE"
        BODY="{\"reasonCode\":\"$REASON_CODE_ESC\"}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/dispute" | pretty_print_json
        ;;

    checkout-quick-pay)
        confirm_risky_action "Checkout quick pay"
        ESCROW_ID="$2"
        WALLET_SELECTOR="$3"
        if [ -z "$ESCROW_ID" ] || [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh checkout-quick-pay <escrowId> <walletSelector> [--yes]"
            exit 1
        fi
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/quick-pay" | pretty_print_json
        ;;

    checkout-swap-and-pay-quote)
        ESCROW_ID="$2"
        WALLET_SELECTOR="$3"
        if [ -z "$ESCROW_ID" ] || [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh checkout-swap-and-pay-quote <escrowId> <walletSelector>"
            exit 1
        fi
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        BODY="$BODY, \"confirm\": false}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/swap-and-pay" | pretty_print_json
        ;;

    checkout-swap-and-pay-confirm)
        confirm_risky_action "Checkout swap-and-pay confirm"
        ESCROW_ID="$2"
        WALLET_SELECTOR="$3"
        SLIPPAGE="$4"
        if [ -z "$ESCROW_ID" ] || [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh checkout-swap-and-pay-confirm <escrowId> <walletSelector> [slippage] [--yes]"
            exit 1
        fi
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        BODY="$BODY, \"confirm\": true"
        if [ -n "$SLIPPAGE" ]; then
            require_decimal "slippage" "$SLIPPAGE"
            BODY="$BODY, \"slippage\": $SLIPPAGE"
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/swap-and-pay" | pretty_print_json
        ;;

    checkout-release|checkout-refund|checkout-cancel)
        confirm_risky_action "Checkout terminal action"
        ACTION="$COMMAND"
        ESCROW_ID="$2"
        if [ -z "$ESCROW_ID" ]; then
            echo "Usage: agentwalletapi.sh checkout-release|checkout-refund|checkout-cancel <escrowId> [--yes]"
            exit 1
        fi
        ENDPOINT_SUFFIX="release"
        BODY='{"force":false}'
        if [ "$ACTION" = "checkout-refund" ]; then
            ENDPOINT_SUFFIX="refund"
        fi
        if [ "$ACTION" = "checkout-cancel" ]; then
            ENDPOINT_SUFFIX="cancel"
            BODY='{}'
        fi
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/escrows/$ESCROW_ID/$ENDPOINT_SUFFIX" | pretty_print_json
        ;;

    checkout-webhooks-list)
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$BASE_URL/api/agent/checkout/webhooks" | pretty_print_json
        ;;

    checkout-webhook-create)
        confirm_risky_action "Checkout webhook create"
        URL="$2"
        EVENT_TYPES_CSV="$3"
        ENABLED="$4"
        if [ -z "$URL" ]; then
            echo "Usage: agentwalletapi.sh checkout-webhook-create <url> [eventTypesCsv] [enabled] [--yes]"
            exit 1
        fi
        json_escape_var URL_ESC "$URL"
        BODY="{\"url\":\"$URL_ESC\""
        if [ -n "$EVENT_TYPES_CSV" ]; then
            IFS=',' read -r -a EVENT_TYPES <<< "$EVENT_TYPES_CSV"
            BODY="$BODY, \"eventTypes\": ["
            for i in "${!EVENT_TYPES[@]}"; do
                EVENT="$(echo "${EVENT_TYPES[$i]}" | xargs)"
                json_escape_var EVENT_ESC "$EVENT"
                BODY="$BODY\"$EVENT_ESC\""
                if [ "$i" -lt "$((${#EVENT_TYPES[@]}-1))" ]; then BODY="$BODY, "; fi
            done
            BODY="$BODY]"
        fi
        if [ -n "$ENABLED" ]; then
            BODY="$BODY, \"enabled\": $ENABLED"
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/webhooks" | pretty_print_json
        ;;

    checkout-webhook-update)
        confirm_risky_action "Checkout webhook update"
        WEBHOOK_ID="$2"
        URL="$3"
        EVENT_TYPES_CSV="$4"
        ENABLED="$5"
        if [ -z "$WEBHOOK_ID" ]; then
            echo "Usage: agentwalletapi.sh checkout-webhook-update <id> [url] [eventTypesCsv] [enabled] [--yes]"
            exit 1
        fi
        BODY="{"
        ADDED=0
        if [ -n "$URL" ]; then
            json_escape_var URL_ESC "$URL"
            BODY="$BODY\"url\":\"$URL_ESC\""
            ADDED=1
        fi
        if [ -n "$EVENT_TYPES_CSV" ]; then
            if [ "$ADDED" -eq 1 ]; then BODY="$BODY, "; fi
            IFS=',' read -r -a EVENT_TYPES <<< "$EVENT_TYPES_CSV"
            BODY="$BODY\"eventTypes\": ["
            for i in "${!EVENT_TYPES[@]}"; do
                EVENT="$(echo "${EVENT_TYPES[$i]}" | xargs)"
                json_escape_var EVENT_ESC "$EVENT"
                BODY="$BODY\"$EVENT_ESC\""
                if [ "$i" -lt "$((${#EVENT_TYPES[@]}-1))" ]; then BODY="$BODY, "; fi
            done
            BODY="$BODY]"
            ADDED=1
        fi
        if [ -n "$ENABLED" ]; then
            if [ "$ADDED" -eq 1 ]; then BODY="$BODY, "; fi
            BODY="$BODY\"enabled\": $ENABLED"
            ADDED=1
        fi
        BODY="$BODY}"
        if [ "$ADDED" -eq 0 ]; then
            echo "Error: provide at least one of url, eventTypesCsv, enabled."
            exit 1
        fi
        curl -s -X PATCH \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            -d "$BODY" \
            "$BASE_URL/api/agent/checkout/webhooks/$WEBHOOK_ID" | pretty_print_json
        ;;

    checkout-webhook-delete)
        confirm_risky_action "Checkout webhook delete"
        WEBHOOK_ID="$2"
        if [ -z "$WEBHOOK_ID" ]; then
            echo "Usage: agentwalletapi.sh checkout-webhook-delete <id> [--yes]"
            exit 1
        fi
        curl -s -X DELETE \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Idempotency-Key: $(new_idempotency_key)" \
            "$BASE_URL/api/agent/checkout/webhooks/$WEBHOOK_ID" | pretty_print_json
        ;;

    polymarket-config)
        echo "Polymarket setup via agent API is disabled."
        echo "Ask your human to complete setup at https://openclawcash.com/venues/polymarket."
        echo "Then use polymarket-resolve, polymarket-limit|polymarket-market, polymarket-redeem and polymarket-account|polymarket-orders|polymarket-activity|polymarket-positions."
        exit 1
        ;;

    polymarket-limit)
        confirm_risky_action "Polymarket limit order"
        WALLET_SELECTOR="$2"
        TOKEN_ID="$3"
        SIDE="$4"
        PRICE="$5"
        SIZE="$6"
        if [ -z "$WALLET_SELECTOR" ] || [ -z "$TOKEN_ID" ] || [ -z "$SIDE" ] || [ -z "$PRICE" ] || [ -z "$SIZE" ]; then
            echo "Usage: agentwalletapi.sh polymarket-limit <walletSelector> <tokenId> <BUY|SELL> <price> <size> [--yes]"
            exit 1
        fi
        require_polymarket_token_id "$TOKEN_ID"
        require_decimal "price" "$PRICE"
        require_decimal "size" "$SIZE"
        json_escape_var TOKEN_ID_ESC "$TOKEN_ID"
        json_escape_var SIDE_ESC "$SIDE"
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        BODY="$BODY, \"tokenId\": \"$TOKEN_ID_ESC\", \"side\": \"$SIDE_ESC\", \"price\": $PRICE, \"size\": $SIZE}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/venues/polymarket/orders/limit" | pretty_print_json
        ;;

    polymarket-market)
        confirm_risky_action "Polymarket market order"
        WALLET_SELECTOR="$2"
        TOKEN_ID="$3"
        SIDE="$4"
        AMOUNT="$5"
        ORDER_TYPE="${6:-FAK}"
        WORST_PRICE="${7:-0}"
        if [ -z "$WALLET_SELECTOR" ] || [ -z "$TOKEN_ID" ] || [ -z "$SIDE" ] || [ -z "$AMOUNT" ]; then
            echo "Usage: agentwalletapi.sh polymarket-market <walletSelector> <tokenId> <BUY|SELL> <amount> [orderType] [worstPrice] [--yes]"
            exit 1
        fi
        require_polymarket_token_id "$TOKEN_ID"
        require_decimal "amount" "$AMOUNT"
        require_decimal "worstPrice" "$WORST_PRICE"
        json_escape_var TOKEN_ID_ESC "$TOKEN_ID"
        json_escape_var SIDE_ESC "$SIDE"
        json_escape_var ORDER_TYPE_ESC "$ORDER_TYPE"
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        BODY="$BODY, \"tokenId\": \"$TOKEN_ID_ESC\", \"side\": \"$SIDE_ESC\", \"amount\": $AMOUNT, \"orderType\": \"$ORDER_TYPE_ESC\", \"worstPrice\": $WORST_PRICE}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/venues/polymarket/orders/market" | pretty_print_json
        ;;

    polymarket-account)
        WALLET_SELECTOR="$2"
        if [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh polymarket-account <walletSelector>"
            exit 1
        fi
        URL="$BASE_URL/api/agent/venues/polymarket/account"
        if [[ "$WALLET_SELECTOR" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
            append_query_param URL "walletAddress" "$WALLET_SELECTOR"
        else
            append_query_param URL "walletId" "$WALLET_SELECTOR"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    polymarket-resolve)
        MARKET_OR_SLUG="$2"
        OUTCOME="$3"
        if [ -z "$MARKET_OR_SLUG" ] || [ -z "$OUTCOME" ]; then
            echo "Usage: agentwalletapi.sh polymarket-resolve <marketUrl|slug> <outcome>"
            exit 1
        fi
        URL="$BASE_URL/api/agent/venues/polymarket/market/resolve"
        if [[ "$MARKET_OR_SLUG" =~ ^https?:// ]]; then
            append_query_param URL "marketUrl" "$MARKET_OR_SLUG"
        else
            append_query_param URL "slug" "$MARKET_OR_SLUG"
        fi
        append_query_param URL "outcome" "$OUTCOME"
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    polymarket-orders)
        WALLET_SELECTOR="$2"
        STATUS="$3"
        LIMIT="$4"
        CURSOR="$5"
        if [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh polymarket-orders <walletSelector> [status] [limit] [cursor]"
            exit 1
        fi
        URL="$BASE_URL/api/agent/venues/polymarket/orders"
        if [[ "$WALLET_SELECTOR" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
            append_query_param URL "walletAddress" "$WALLET_SELECTOR"
        else
            append_query_param URL "walletId" "$WALLET_SELECTOR"
        fi
        if [ -n "$STATUS" ]; then
            append_query_param URL "status" "$STATUS"
        fi
        if [ -n "$LIMIT" ]; then
            require_uint "limit" "$LIMIT"
            append_query_param URL "limit" "$LIMIT"
        fi
        if [ -n "$CURSOR" ]; then
            append_query_param URL "cursor" "$CURSOR"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    polymarket-activity)
        WALLET_SELECTOR="$2"
        LIMIT="$3"
        CURSOR="$4"
        if [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh polymarket-activity <walletSelector> [limit] [cursor]"
            exit 1
        fi
        URL="$BASE_URL/api/agent/venues/polymarket/activity"
        if [[ "$WALLET_SELECTOR" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
            append_query_param URL "walletAddress" "$WALLET_SELECTOR"
        else
            append_query_param URL "walletId" "$WALLET_SELECTOR"
        fi
        if [ -n "$LIMIT" ]; then
            require_uint "limit" "$LIMIT"
            append_query_param URL "limit" "$LIMIT"
        fi
        if [ -n "$CURSOR" ]; then
            append_query_param URL "cursor" "$CURSOR"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    polymarket-positions)
        WALLET_SELECTOR="$2"
        LIMIT="$3"
        if [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh polymarket-positions <walletSelector> [limit]"
            exit 1
        fi
        URL="$BASE_URL/api/agent/venues/polymarket/positions"
        if [[ "$WALLET_SELECTOR" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
            append_query_param URL "walletAddress" "$WALLET_SELECTOR"
        else
            append_query_param URL "walletId" "$WALLET_SELECTOR"
        fi
        if [ -n "$LIMIT" ]; then
            require_uint "limit" "$LIMIT"
            append_query_param URL "limit" "$LIMIT"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    polymarket-redeem)
        confirm_risky_action "Polymarket redeem"
        WALLET_SELECTOR="$2"
        TOKEN_OR_ALL="$3"
        LIMIT="$4"
        if [ -z "$WALLET_SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh polymarket-redeem <walletSelector> [tokenId|all] [limit] [--yes]"
            exit 1
        fi
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        if [ -n "$TOKEN_OR_ALL" ] && [ "$TOKEN_OR_ALL" != "all" ]; then
            require_polymarket_token_id "$TOKEN_OR_ALL"
            json_escape_var TOKEN_ID_ESC "$TOKEN_OR_ALL"
            BODY="$BODY, \"tokenId\": \"$TOKEN_ID_ESC\""
        fi
        if [ -n "$LIMIT" ]; then
            require_uint "limit" "$LIMIT"
            BODY="$BODY, \"limit\": $LIMIT"
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/venues/polymarket/redeem" | pretty_print_json
        ;;

    polymarket-cancel)
        confirm_risky_action "Polymarket cancel order"
        WALLET_SELECTOR="$2"
        ORDER_ID="$3"
        if [ -z "$WALLET_SELECTOR" ] || [ -z "$ORDER_ID" ]; then
            echo "Usage: agentwalletapi.sh polymarket-cancel <walletSelector> <orderId> [--yes]"
            exit 1
        fi
        json_escape_var ORDER_ID_ESC "$ORDER_ID"
        BODY="{"
        append_wallet_or_address_json_field BODY "$WALLET_SELECTOR"
        BODY="$BODY, \"orderId\": \"$ORDER_ID_ESC\"}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/venues/polymarket/orders/cancel" | pretty_print_json
        ;;

    *)
        echo "OpenclawCash CLI Tool"
        echo ""
        echo "Usage: agentwalletapi.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo "  wallets                                    List all wallets"
        echo "  user-tag-get                               Read global checkout user tag"
        echo "  user-tag-set <userTag> [--yes]            Set global checkout user tag once"
        echo "  wallet <walletId|publicWalletId|walletLabel> [chain]  Get one wallet detail with balances"
        echo "  create <label> [network] <passphraseEnvVar> [--yes]  Create wallet (default network: sepolia)"
        echo "  import <label> <network> [privateKey] [--yes]      Import wallet (mainnet|polygon-mainnet|solana-mainnet)"
        echo "  transactions <walletId|publicWalletId> [chain]    List wallet transaction history"
        echo "  balance <walletId|publicWalletId> [token] [chain] Check balances"
        echo "  transfer <walletId|publicWalletId> <to> <amount> [token] [chain] [--yes]  Send native/token transfer"
        echo "  tokens [network] [chain]                           List supported tokens"
        echo "  quote <network> <tokenIn> <tokenOut> <amountInBaseUnits> [chain]  Get swap quote"
        echo "  swap <walletId|publicWalletId> <tokenIn> <tokenOut> <amountInBaseUnits> [slippage] [chain] [--yes]  Execute swap"
        echo "  approve <walletId|publicWalletId> <tokenAddress> <spender> <amountBaseUnits> [chain] [--yes]  Approve allowance"
        echo "  checkout-payreq-create <walletSelector> <amountBaseUnits> [expiresSec] [autoReleaseSec] [disputeWindowSec] [--yes]"
        echo "  checkout-payreq-get <payreqId>"
        echo "  checkout-escrow-get <escrowId>"
        echo "  checkout-funding-confirm <escrowId> <txHash> [minConfirmations] [--yes]"
        echo "  checkout-accept <escrowId> [--yes]"
        echo "  checkout-proof <escrowId> <proofHash> [proofUrl] [--yes]"
        echo "  checkout-dispute <escrowId> <reasonCode> [--yes]"
        echo "  checkout-quick-pay <escrowId> <walletSelector> [--yes]"
        echo "  checkout-swap-and-pay-quote <escrowId> <walletSelector>"
        echo "  checkout-swap-and-pay-confirm <escrowId> <walletSelector> [slippage] [--yes]"
        echo "  checkout-release <escrowId> [--yes]"
        echo "  checkout-refund <escrowId> [--yes]"
        echo "  checkout-cancel <escrowId> [--yes]"
        echo "  checkout-webhooks-list"
        echo "  checkout-webhook-create <url> [eventTypesCsv] [enabled] [--yes]"
        echo "  checkout-webhook-update <id> [url] [eventTypesCsv] [enabled] [--yes]"
        echo "  checkout-webhook-delete <id> [--yes]"
        echo "  polymarket-limit <walletSelector> <tokenId> <BUY|SELL> <price> <size> [--yes]"
        echo "  polymarket-market <walletSelector> <tokenId> <BUY|SELL> <amount> [orderType] [worstPrice] [--yes]"
        echo "  polymarket-account <walletSelector>"
        echo "  polymarket-resolve <marketUrl|slug> <outcome>"
        echo "  polymarket-orders <walletSelector> [status] [limit] [cursor]"
        echo "  polymarket-activity <walletSelector> [limit] [cursor]"
        echo "  polymarket-positions <walletSelector> [limit]"
        echo "  polymarket-redeem <walletSelector> [tokenId|all] [limit] [--yes]"
        echo "  polymarket-cancel <walletSelector> <orderId> [--yes]"
        echo ""
        echo "Examples:"
        echo "  agentwalletapi.sh wallets"
        echo "  agentwalletapi.sh user-tag-get"
        echo "  agentwalletapi.sh user-tag-set my-agent-tag --yes"
        echo "  export WALLET_EXPORT_PASSPHRASE_OPS='your-strong-passphrase'"
        echo "  agentwalletapi.sh create 'Ops Wallet' sepolia WALLET_EXPORT_PASSPHRASE_OPS --yes"
        echo "  agentwalletapi.sh import 'Treasury Imported' mainnet --yes"
        echo "  agentwalletapi.sh import 'Poly Ops' polygon-mainnet --yes"
        echo "  agentwalletapi.sh transactions 2"
        echo "  agentwalletapi.sh balance 2"
        echo "  agentwalletapi.sh transfer 2 0xRecipient 0.01 --yes"
        echo "  agentwalletapi.sh transfer 2 0xRecipient 100 USDC --yes"
        echo "  agentwalletapi.sh tokens mainnet"
        echo "  agentwalletapi.sh quote mainnet WETH USDC 10000000000000000"
        echo "  agentwalletapi.sh swap 2 ETH USDC 10000000000000000 0.5 --yes"
        echo "  agentwalletapi.sh approve 2 0xA0b86991... 0xSpender... 1000000000 --yes"
        echo "  agentwalletapi.sh checkout-payreq-create 2 30000000 --yes"
        echo "  agentwalletapi.sh checkout-quick-pay es_d4e5f6 2 --yes"
        echo "  agentwalletapi.sh checkout-swap-and-pay-quote es_d4e5f6 2"
        echo "  agentwalletapi.sh checkout-release es_d4e5f6 --yes"
        echo "  agentwalletapi.sh polymarket-market 2 123456 BUY 25 FAK 0.65 --yes"
        echo "  agentwalletapi.sh polymarket-resolve https://polymarket.com/market/market-slug No"
        echo "  agentwalletapi.sh polymarket-account 2"
        echo "  agentwalletapi.sh polymarket-orders 2 OPEN 50"
        echo "  agentwalletapi.sh polymarket-redeem 2 all 100 --yes"
        echo "  agentwalletapi.sh polymarket-redeem 2 1234567890 100 --yes"
        echo "  agentwalletapi.sh polymarket-cancel 2 0xorderid --yes"
        ;;
esac
