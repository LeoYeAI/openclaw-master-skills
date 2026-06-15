#!/bin/bash
# Discord Server Admin Pro - Complete CLI
# Full A-Z Discord server management

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Config
BOT_TOKEN="${DISCORD_BOT_TOKEN:-}"
GUILD_ID="${DISCORD_GUILD_ID:-}"
API_BASE="https://discord.com/api/v10"

log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; exit 1; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*" >&2; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }

# Check deps
check_deps() {
    command -v curl &> /dev/null || { log_error "curl required"; }
    command -v jq &> /dev/null || { log_error "jq required (sudo apt install jq)"; }
}

validate_token() { [[ -z "$BOT_TOKEN" ]] && log_error "DISCORD_BOT_TOKEN not set"; }

# API wrapper
api() {
    local method=$1 endpoint=$2 data=$3
    local response=$(curl -s -w "\n%{http_code}" -X "$method" \
        "$API_BASE$endpoint" \
        -H "Authorization: Bot $BOT_TOKEN" \
        -H "Content-Type: application/json" \
        ${data:+-d "$data"})
    
    local code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    case $code in
        200|201|204) echo "$body" ;;
        401) log_error "Unauthorized - check bot token" ;;
        403) log_error "Forbidden - bot lacks permissions" ;;
        404) log_error "Not found - check IDs" ;;
        429) local retry=$(echo "$body" | jq -r '.retry_after // 1'); log_warn "Rate limited, waiting ${retry}s"; sleep $retry; api $method $endpoint "$data" ;;
        *) log_error "API error $code: $body" ;;
    esac
}

api_get() { api GET "$1" ""; }
api_post() { api POST "$1" "$2"; }
api_patch() { api PATCH "$1" "$2"; }
api_delete() { api DELETE "$1" ""; }
api_put() { api PUT "$1" "${2:-}"; }

# JSON helpers
json_obj() { jq -n "$1" 2>/dev/null; }
kv_json() { local o="{}"; for a in "$@"; do [[ "$a" =~ ^([^:]+):(.+)$ ]] && o=$(echo "$o" | jq --arg k "${BASH_REMATCH[1]}" --arg v "${BASH_REMATCH[2]}" '. + {($k):$v}'); done; echo "$o"; }

# Duration parser (1h, 1d, etc)
parse_dur() {
    local d=$1 s=0
    [[ $d =~ ^([0-9]+)s$ ]] && s=${BASH_REMATCH[1]}
    [[ $d =~ ^([0-9]+)m$ ]] && s=$((${BASH_REMATCH[1]}*60))
    [[ $d =~ ^([0-9]+)h$ ]] && s=$((${BASH_REMATCH[1]}*3600))
    [[ $d =~ ^([0-9]+)d$ ]] && s=$((${BASH_REMATCH[1]}*86400))
    echo $s
}

# ============================================================================
# COMMANDS
# ============================================================================

show_help() {
    cat << 'EOF'
Discord Server Admin Pro - Full Server Management

USAGE: ./discord-admin.sh <command> [options]

SERVER INTELLIGENCE:
  server-info <guild>              Full server overview
  vanity-get <guild>              Get vanity URL
  vanity-set <guild> <code>       Set vanity URL
  widget-get <guild>              Get widget settings
  widget-edit <guild> <json>      Edit widget

CHANNELS:
  channel-list <guild>           List all channels
  channel-create <guild> <name> [type]  Create channel (text|voice|category|forum|stage)
  channel-edit <guild> <channelId> <json>  Edit channel
  channel-delete <guild> <channelId>     Delete channel
  channel-perms <guild> <channelId>       List permissions

ROLES:
  role-list <guild>              List all roles
  role-create <guild> <name> [json]  Create role with permissions
  role-edit <guild> <roleId> <json>   Edit role
  role-delete <guild> <roleId>   Delete role
  role-position <guild> <roleId> <pos>  Change position
  role-assign <guild> <roleId> <userId>  Assign role
  role-remove <guild> <roleId> <userId>  Remove role
  role-bulk <guild> <roleId> <userIds>   Bulk assign role

MEMBERS:
  member-info <guild> <userId>   Member details
  member-nick <guild> <userId> <nick>  Set nickname
  member-nick-reset <guild> <userId>   Reset nickname
  member-timeout <guild> <userId> <dur>  Timeout (1s,1m,1h,1d)
  member-untimeout <guild> <userId>  Remove timeout
  member-kick <guild> <userId> [reason]  Kick member
  member-ban <guild> <userId> [reason] [days]  Ban member
  member-unban <guild> <userId> [reason]  Unban member
  ban-list <guild>                List all bans
  prune <guild> [days]            Prune inactive members

MESSAGES:
  msg-send <channel> <content>   Send message
  msg-embed <channel> <json>     Send embed
  msg-edit <channel> <msgId> <content>  Edit message
  msg-delete <channel> <msgId>   Delete message
  msg-bulk-delete <channel> <msgIds>  Bulk delete (comma-sep)
  msg-history <channel> [limit]  Get message history
  msg-pin <channel> <msgId>       Pin message
  msg-unpin <channel> <msgId>     Unpin message
  msg-pins <channel>              List pins
  msg-search <guild> <query> [channel]  Search messages

AUTOMOD:
  automod-list <guild>           List AutoMod rules
  automod-create <guild> <name> <json>  Create rule
  automod-edit <guild> <ruleId> <json>   Edit rule
  automod-delete <guild> <ruleId> Delete rule

WEBHOOKS:
  webhook-list <guild> [channel]  List webhooks
  webhook-create <channel> <name> [avatar]  Create webhook
  webhook-info <webhookId>        Get webhook
  webhook-edit <webhookId> <json>  Edit webhook
  webhook-delete <webhookId>      Delete webhook
  webhook-exec <webhookId> <content> [json]  Execute webhook

EMOJIS & STICKERS:
  emoji-list <guild>              List emojis
  emoji-create <guild> <name> <imageUrl>  Add emoji
  emoji-delete <guild> <emojiId>   Delete emoji
  sticker-list <guild>            List stickers
  sticker-create <guild> <name> <tags> <imageUrl>  Add sticker
  sticker-edit <guild> <stickerId> <json>  Edit sticker
  sticker-delete <guild> <stickerId>  Delete sticker

EVENTS:
  event-list <guild>              List scheduled events
  event-create <guild> <json>     Create event
  event-edit <guild> <eventId> <json>  Edit event
  event-delete <guild> <eventId>   Delete event

INVITES:
  invite-list <guild>              List invites
  invite-create <channel> [json]   Create invite
  invite-info <code>              Get invite info
  invite-delete <guild> <code>    Delete invite

THREADS:
  thread-list <guild> [channel]   List threads
  thread-create <channel> <name> [msgId]  Create thread
  thread-edit <threadId> <json>     Edit thread
  thread-delete <threadId>          Delete thread
  thread-archive <threadId>         Archive thread
  thread-join <threadId>            Join thread
  thread-leave <threadId>           Leave thread

AUDIT LOGS:
  audit-logs <guild> [limit] [user] [action]  Get audit logs

STAGE:
  stage-create <channel> [topic]    Create stage instance
  stage-edit <channel> <json>       Edit stage
  stage-close <channel>             Close stage

INTEGRATIONS:
  integration-list <guild>          List integrations
  integration-sync <guild> <id>    Sync integration
  integration-delete <guild> <id>  Delete integration

TEMPLATES:
  template-list <guild>             List templates
  template-create <guild> <name> [desc]  Create template
  template-sync <guild> <code>      Sync template
  template-delete <guild> <id>      Delete template
  template-use <code> <name>        Create server from template

GUILD:
  guild-edit <guild> <json>        Edit server settings
  guild-leave <guild>              Leave server

MOD LOG:
  modlog-set <guild> <channel>      Set mod log channel
  modlog-get <guild>               Get mod log channel
  modlog-disable <guild>           Disable mod log

OPTIONS:
  --token <token>                   Set bot token
  --format <json|pretty|minimal>   Output format
  --help, -h                       Show this help

EXAMPLES:
  ./discord-admin.sh channel-list 123456789
  ./discord-admin.sh role-create 123456789 Moderator '{"color":16711680,"permissions":"268435456"}'
  ./discord-admin.sh member-ban 123456789 987654321 Spamming 7
  ./discord-admin.sh webhook-create 123456789 "Alerts" --token MYTOKEN

JSON FORMAT NOTES:
  - Use single quotes around JSON: '{"key":"value"}'
  - Permission values are integers (not names)
  - Colors are hex (e.g., "#FF0000" or "0xFF0000")
  - Timestamps: ISO 8601 format

PERMISSION VALUES:
  ADMINISTRATOR: 8
  VIEW_AUDIT_LOG: 128
  MANAGE_GUILD: 32
  MANAGE_ROLES: 268435456
  MANAGE_CHANNELS: 4
  KICK_MEMBERS: 2
  BAN_MEMBERS: 4
  MANAGE_MESSAGES: 8192
  MANAGE_WEBHOOKS: 536870912
  MANAGE_EMOJIS: 1073741824
  MANAGE_EVENTS: 8589934592
  MODERATE_MEMBERS: 274877906944

EOF
}

# ============================================================================
# MAIN
# ============================================================================

check_deps

# Parse global options
while [[ "$1" =~ ^-- ]]; do
    case "$1" in
        --token) BOT_TOKEN="$2"; shift 2 ;;
        --format) OUTPUT_FORMAT="$2"; shift 2 ;;
        --debug) DEBUG_MODE="true"; shift ;;
        *) shift ;;
    esac
done

cmd="${1:-}"
shift 2>/dev/null || true

case "$cmd" in
    --help|-h|"") show_help ;;
    
    # Server
    server-info) validate_token; api_get "/guilds/${1:-$GUILD_ID}?with_counts=true" ;;
    vanity-get) validate_token; api_get "/guilds/${1:-$GUILD_ID}/vanity-url" ;;
    vanity-set) validate_token; api_patch "/guilds/$1/vanity-url" "{\"code\":\"$2\"}" ;;
    widget-get) validate_token; api_get "/guilds/${1:-$GUILD_ID}/widget" ;;
    widget-edit) validate_token; api_patch "/guilds/$1/widget" "$2" ;;
    guild-edit) validate_token; api_patch "/guilds/$1" "$2" ;;
    guild-leave) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/members/@me" ;;
    
    # Channels
    channel-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/channels" ;;
    channel-create) validate_token; 
        type=${3:-text}; t=0; [[ "$type" == "voice" ]] && t=2; [[ "$type" == "category" ]] && t=4; [[ "$type" == "forum" ]] && t=15; [[ "$type" == "stage" ]] && t=13
        api_post "/guilds/$1/channels" "{\"name\":\"$2\",\"type\":$t}" ;;
    channel-edit) validate_token; api_patch "/channels/$1" "$2" ;;
    channel-delete) validate_token; api_delete "/channels/$1" ;;
    channel-perms) validate_token; api_get "/channels/$1/permissions" ;;
    channel-sync) validate_token; api_patch "/channels/$2" "{\"permissions_sync\":true}" ;;
    
    # Roles
    role-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/roles" ;;
    role-create) validate_token; api_post "/guilds/${1:-$GUILD_ID}/roles" "{\"name\":\"$2\"${3:+,\"$3}}\"" ;;
    role-edit) validate_token; api_patch "/guilds/$1/roles/$2" "$3" ;;
    role-delete) validate_token; api_delete "/guilds/$1/roles/$2" ;;
    role-position) validate_token; api_patch "/guilds/$1/roles" "[{\"id\":\"$2\",\"position\":$3}]" ;;
    role-assign) validate_token; api_put "/guilds/$1/members/$3/roles/$2" ;;
    role-remove) validate_token; api_delete "/guilds/$1/members/$3/roles/$2" ;;
    role-bulk) 
        validate_token; IFS=',' read -ra users <<< "$3"
        for u in "${users[@]}"; do api_put "/guilds/$1/members/$u/roles/$2" 2>/dev/null || true; done
        log_success "Role assigned to ${#users[@]} users" ;;
    
    # Members
    member-info) validate_token; api_get "/guilds/${1:-$GUILD_ID}/members/$2" ;;
    member-nick) validate_token; api_patch "/guilds/${1:-$GUILD_ID}/members/$2" "{\"nick\":\"$3\"}" ;;
    member-nick-reset) validate_token; api_patch "/guilds/${1:-$GUILD_ID}/members/$2" "{\"nick\":null}" ;;
    member-timeout)
        validate_token; s=$(parse_dur "$3")
        t=$(date -d "+$s sec" -Iseconds 2>/dev/null || date -u -v+"${s}S" -Iseconds 2>/dev/null || echo "")
        [[ -z "$t" ]] && t=$(date -u +%Y-%m-%dT%H:%M:%SZ)
        api_patch "/guilds/${1:-$GUILD_ID}/members/$2" "{\"communication_disabled_until\":\"$t\"}" ;;
    member-untimeout) validate_token; api_patch "/guilds/${1:-$GUILD_ID}/members/$2" "{\"communication_disabled_until\":null}" ;;
    member-kick) validate_token; [[ -n "$3" ]] && api_delete "/guilds/${1:-$GUILD_ID}/members/$2" "{\"reason\":\"$3\"}" || api_delete "/guilds/${1:-$GUILD_ID}/members/$2" ;;
    member-ban) validate_token; d=${4:-0}; api_put "/guilds/${1:-$GUILD_ID}/bans/$2" "{\"delete_message_days\":$d${3:+,\"reason\":\"$3\"}}" ;;
    member-unban) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/bans/$2" ;;
    ban-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/bans" ;;
    prune) validate_token; api_post "/guilds/${1:-$GUILD_ID}/prune" "{\"days\":${2:-30}}" ;;
    
    # Messages
    msg-send) validate_token; api_post "/channels/$1/messages" "{\"content\":\"$2\"}" ;;
    msg-embed) validate_token; api_post "/channels/$1/messages" "{\"embeds\":[$2]}" ;;
    msg-edit) validate_token; api_patch "/channels/$1/messages/$2" "{\"content\":\"$3\"}" ;;
    msg-delete) validate_token; api_delete "/channels/$1/messages/$2" ;;
    msg-bulk-delete) 
        validate_token; IFS=',' read -ra msgs <<< "$2"
        ids=$(printf '"%s",' "${msgs[@]}"); ids="${ids%,}"
        api_post "/channels/$1/messages/bulk-delete" "{\"messages\":[$ids]}" ;;
    msg-history) validate_token; api_get "/channels/$1/messages?limit=${2:-100}" ;;
    msg-pin) validate_token; api_put "/channels/$1/pins/$2" ;;
    msg-unpin) validate_token; api_delete "/channels/$1/pins/$2" ;;
    msg-pins) validate_token; api_get "/channels/$1/pins" ;;
    msg-search) validate_token; api_get "/guilds/${1:-$GUILD_ID}/messages/search?content=$2${3:+&channel_id=$3}" ;;
    
    # AutoMod
    automod-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/auto-moderation/rules" ;;
    automod-create) validate_token; api_post "/guilds/${1:-$GUILD_ID}/auto-moderation/rules" "$2" ;;
    automod-edit) validate_token; api_patch "/guilds/$1/auto-moderation/rules/$2" "$3" ;;
    automod-delete) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/auto-moderation/rules/$2" ;;
    
    # Webhooks
    webhook-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/webhooks${2:+/$2}" ;;
    webhook-create) validate_token; api_post "/channels/${1:-$GUILD_ID}/webhooks" "{\"name\":\"$2\"}" ;;
    webhook-info) validate_token; api_get "/webhooks/$1" ;;
    webhook-edit) validate_token; api_patch "/webhooks/$1" "$2" ;;
    webhook-delete) validate_token; api_delete "/webhooks/$1" ;;
    webhook-exec) 
        validate_token; shift
        id=$1; shift; content=$1; shift
        data="{\"content\":\"$content\"}"
        for a in "$@"; do data=$(echo "$data" | jq --argjson v "$a" '. + $v'); done
        api_post "/webhooks/$id" "$data" ;;
    
    # Emojis & Stickers
    emoji-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/emojis" ;;
    emoji-create) validate_token; api_post "/guilds/${1:-$GUILD_ID}/emojis" "{\"name\":\"$2\",\"image\":\"$3\"}" ;;
    emoji-delete) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/emojis/$2" ;;
    sticker-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/stickers" ;;
    sticker-create) validate_token; api_post "/guilds/${1:-$GUILD_ID}/stickers" "{\"name\":\"$2\",\"tags\":\"$3\"}" ;;
    sticker-edit) validate_token; api_patch "/guilds/${1:-$GUILD_ID}/stickers/$2" "$3" ;;
    sticker-delete) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/stickers/$2" ;;
    
    # Events
    event-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/scheduled-events" ;;
    event-create) validate_token; api_post "/guilds/${1:-$GUILD_ID}/scheduled-events" "$2" ;;
    event-edit) validate_token; api_patch "/guilds/$1/scheduled-events/$2" "$3" ;;
    event-delete) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/scheduled-events/$2" ;;
    
    # Invites
    invite-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/invites" ;;
    invite-create) 
        validate_token; c=$1; shift
        data="{}"; for a in "$@"; do data=$(echo "$data" | jq --argjson v "$a" '. + $v'); done
        api_post "/channels/$c/invites" "$data" ;;
    invite-info) validate_token; api_get "/invites/$1" ;;
    invite-delete) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/invites/$2" ;;
    
    # Threads
    thread-list) validate_token; [[ -n "$2" ]] && api_get "/channels/$2/threads" || api_get "/guilds/${1:-$GUILD_ID}/threads" ;;
    thread-create) 
        validate_token; [[ -n "$3" ]] && api_post "/channels/$1/messages/$3/threads" "{\"name\":\"$2\"}" \
        || api_post "/channels/$1/threads" "{\"name\":\"$2\"}" ;;
    thread-edit) validate_token; api_patch "/channels/$1" "$2" ;;
    thread-delete) validate_token; api_delete "/channels/$1" ;;
    thread-archive) validate_token; api_patch "/channels/$1" "{\"archived\":true}" ;;
    thread-join) validate_token; api_post "/channels/$1/thread-members/@me" ;;
    thread-leave) validate_token; api_delete "/channels/$1/thread-members/@me" ;;
    
    # Audit Logs
    audit-logs) 
        validate_token; e="/guilds/${1:-$GUILD_ID}/audit-logs?limit=${2:-50}"
        [[ -n "$3" ]] && e+="&user_id=$3"; [[ -n "$4" ]] && e+="&action_type=$4"
        api_get "$e" ;;
    
    # Stage
    stage-create) validate_token; api_post "/channels/$1/threads" "{\"name\":\"${2:-Stage}\",\"type\":13}" ;;
    stage-edit) validate_token; api_patch "/channels/$1" "$2" ;;
    stage-close) validate_token; api_patch "/channels/$1" "{\"archived\":true}" ;;
    
    # Integrations
    integration-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/integrations" ;;
    integration-sync) validate_token; api_post "/guilds/${1:-$GUILD_ID}/integrations/$2" ;;
    integration-delete) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/integrations/$2" ;;
    
    # Templates
    template-list) validate_token; api_get "/guilds/${1:-$GUILD_ID}/templates" ;;
    template-create) validate_token; api_post "/guilds/${1:-$GUILD_ID}/templates" "{\"name\":\"$2\"${3:+,\"description\":\"$3\"}}" ;;
    template-sync) validate_token; api_put "/guilds/${1:-$GUILD_ID}/templates/$2" ;;
    template-delete) validate_token; api_delete "/guilds/${1:-$GUILD_ID}/templates/$2" ;;
    template-use) validate_token; api_post "/guilds/$1/templates" "{\"name\":\"$2\"}" ;;
    
    # Mod Log
    modlog-set) validate_token; api_patch "/guilds/$1" "{\"system_channel_id\":\"$2\"}" ;;
    modlog-get) validate_token; api_get "/guilds/${1:-$GUILD_ID}" | jq '.system_channel_id' ;;
    modlog-disable) validate_token; api_patch "/guilds/${1:-$GUILD_ID}" "{\"system_channel_id\":null}" ;;
    
    *)
        log_error "Unknown command: $cmd"
        echo "Use --help for available commands"
        exit 1
        ;;
esac

# Output format
if [[ -t 1 ]]; then
    if [[ "$OUTPUT_FORMAT" == "pretty" ]] || [[ -z "$OUTPUT_FORMAT" && "$cmd" != "msg-send" && "$cmd" != "member-kick" ]]; then
        if command -v jq &> /dev/null; then
            while IFS= read -r line; do echo "$line"; done | jq '.' 2>/dev/null || true
        fi
    fi
fi
