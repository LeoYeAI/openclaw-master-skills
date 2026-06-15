#!/bin/bash
# Discord Server Control - CLI Wrapper
# Usage: ./discord-ctrl.sh <command> [options]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Config
BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
GUILD_ID="${DISCORD_GUILD_ID:-}"

# Help
show_help() {
    cat << EOF
Discord Server Control - Full Server Management

Commands:
    channel-list [guildId]              List all channels
    channel-create <guildId> <name> [type]  Create a channel (type: text|voice|category)
    channel-delete <guildId> <channelId>    Delete a channel
    channel-edit <guildId> <channelId> <name>    Edit channel name
    
    role-list <guildId>                  List all roles
    role-create <guildId> <name> [color]     Create a role
    role-delete <guildId> <roleId>           Delete a role
    
    member-kick <guildId> <userId> [reason]  Kick a member
    member-ban <guildId> <userId> [reason]   Ban a member
    member-unban <guildId> <userId>          Unban a user
    
    message-send <guildId> <channelId> <message>   Send a message
    message-delete <guildId> <messageId>           Delete a message
    
    server-info <guildId>                 Get server info
    emoji-list <guildId>                   List server emojis

Options:
    --token <token>       Bot token (or set DISCORD_BOT_TOKEN)
    --help                Show this help

Examples:
    ./discord-ctrl.sh channel-list 123456789
    ./discord-ctrl.sh channel-create 123456789 general text
    ./discord-ctrl.sh member-kick 123456789 987654321 Spam
    ./discord-ctrl.sh message-send 123456789 111222333 "Hello world!"

EOF
}

# API calls
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    curl -s -X "$method" \
        "https://discord.com/api/v10$endpoint" \
        -H "Authorization: Bot $BOT_TOKEN" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"}
}

# Commands
cmd_channel_list() {
    local guild="${1:-$GUILD_ID}"
    api_call "GET" "/guilds/$guild/channels" | jq '.[] | "\(.name) [\(?.type)]"' 2>/dev/null || api_call "GET" "/guilds/$guild/channels"
}

cmd_channel_create() {
    local guild="$1" name="$2" type="${3:-text}"
    local data=$(jq -n --arg n "$name" --arg t "$type" '{name:$n, type:($t | if .=="voice" then 2 elif .=="category" then 4 else 0 end)}')
    api_call "POST" "/guilds/$guild/channels" "$data"
}

cmd_channel_delete() {
    local guild="$1" channel="$2"
    api_call "DELETE" "/channels/$channel"
}

cmd_channel_edit() {
    local guild="$1" channel="$2" name="$3"
    local data=$(jq -n --arg n "$name" '{name:$n}')
    api_call "PATCH" "/channels/$channel" "$data"
}

cmd_role_list() {
    local guild="${1:-$GUILD_ID}"
    api_call "GET" "/guilds/$guild/roles" | jq '.[] | "\(.name) - \(.id)"' 2>/dev/null || api_call "GET" "/guilds/$guild/roles"
}

cmd_role_create() {
    local guild="$1" name="$2" color="${3:-000000}"
    local data=$(jq -n --arg n "$name" --arg c "$color" '{name:$n, color:("0x"+$c | tonumber)}')
    api_call "POST" "/guilds/$guild/roles" "$data"
}

cmd_role_delete() {
    local guild="$1" role="$2"
    api_call "DELETE" "/guilds/$guild/roles/$role"
}

cmd_member_kick() {
    local guild="$1" user="$2" reason="${3:-}"
    local data=$(jq -n ${reason:+--arg r "$reason" '{reason:$r}'})
    api_call "DELETE" "/guilds/$guild/members/$user" "${reason:+$data}"
}

cmd_member_ban() {
    local guild="$1" user="$2" reason="${3:-}"
    local data=$(jq -n ${reason:+--arg r "$reason" '{reason:$r}'})
    api_call "PUT" "/guilds/$guild/bans/$user" "${reason:+$data}"
}

cmd_member_unban() {
    local guild="$1" user="$2"
    api_call "DELETE" "/guilds/$guild/bans/$user"
}

cmd_message_send() {
    local guild="$1" channel="$2" message="$3"
    local data=$(jq -n --arg m "$message" '{content:$m}')
    api_call "POST" "/channels/$channel/messages" "$data"
}

cmd_message_delete() {
    local guild="$1" message="$2"
    api_call "DELETE" "/channels/$guild/messages/$message"
}

cmd_server_info() {
    local guild="${1:-$GUILD_ID}"
    api_call "GET" "/guilds/$guild?with_counts=true"
}

cmd_emoji_list() {
    local guild="${1:-$GUILD_ID}"
    api_call "GET" "/guilds/$guild/emojis"
}

# Main
main() {
    if [[ -z "$BOT_TOKEN" ]]; then
        echo -e "${RED}Error: DISCORD_BOT_TOKEN not set. Use --token or export DISCORD_BOT_TOKEN${NC}"
        exit 1
    fi
    
    local cmd="${1:-}"
    shift || true
    
    case "$cmd" in
        channel-list)  cmd_channel_list "$@" ;;
        channel-create) cmd_channel_create "$@" ;;
        channel-delete) cmd_channel_delete "$@" ;;
        channel-edit)   cmd_channel_edit "$@" ;;
        role-list)      cmd_role_list "$@" ;;
        role-create)    cmd_role_create "$@" ;;
        role-delete)    cmd_role_delete "$@" ;;
        member-kick)    cmd_member_kick "$@" ;;
        member-ban)     cmd_member_ban "$@" ;;
        member-unban)   cmd_member_unban "$@" ;;
        message-send)   cmd_message_send "$@" ;;
        message-delete) cmd_message_delete "$@" ;;
        server-info)    cmd_server_info "$@" ;;
        emoji-list)     cmd_emoji_list "$@" ;;
        --help|-h)      show_help ;;
        "")             show_help ;;
        *)              echo -e "${RED}Unknown command: $cmd${NC}"; show_help; exit 1 ;;
    esac
}

main "$@"
