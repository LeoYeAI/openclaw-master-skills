#!/usr/bin/env bash
# Control D API CLI helper
# Usage: controld.sh <resource> <action> [args...]

set -euo pipefail

API_BASE="https://api.controld.com"

if [[ -z "${CONTROLD_API_TOKEN:-}" ]]; then
    echo "Error: CONTROLD_API_TOKEN not set" >&2
    exit 1
fi

api() {
    local method="$1"
    local endpoint="$2"
    shift 2
    curl -s -X "$method" \
        -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
        -H "Content-Type: application/json" \
        "$@" \
        "${API_BASE}${endpoint}"
}

usage() {
    cat <<EOF
Control D API CLI

Usage: controld.sh <resource> <action> [args...]

Resources:
  profiles    Manage DNS profiles
  devices     Manage devices/endpoints  
  filters     Manage blocking filters
  services    Manage service rules
  rules       Manage custom domain rules
  folders     Manage rule folders
  default     Manage default rule
  access      Manage IP access control
  analytics   View analytics settings
  proxies     List proxy locations
  account     View account info
  network     View network status
  ip          View current IP info

Organization Resources (Business Accounts):
  orgs        Manage organizations
  provision   Manage provisioning codes
  billing     View billing info
  mobileconfig Generate Apple DNS profiles

Examples:
  controld.sh profiles list
  controld.sh profiles create "My Profile"
  controld.sh profiles clone "New Profile" EXISTING_PROFILE_ID
  controld.sh profiles delete PROFILE_ID
  controld.sh devices list
  controld.sh devices create "Router" PROFILE_ID router
  controld.sh devices delete DEVICE_ID
  controld.sh filters list PROFILE_ID
  controld.sh filters enable PROFILE_ID FILTER_ID
  controld.sh services list PROFILE_ID
  controld.sh services block PROFILE_ID SERVICE_ID
  controld.sh services spoof PROFILE_ID SERVICE_ID PROXY_ID
  controld.sh rules list PROFILE_ID FOLDER_ID
  controld.sh rules block PROFILE_ID "domain.com"
  controld.sh rules bypass PROFILE_ID "trusted.com"
  controld.sh proxies list
  controld.sh account
  controld.sh network

Organization Examples:
  controld.sh orgs info               # View your organization info
  controld.sh orgs update "name=New Name&twofa_req=1"
  controld.sh orgs suborgs            # List sub-organizations
  controld.sh orgs suborg-create "name=Customer&contact_email=a@b.com&twofa_req=0&stats_endpoint=PK&max_users=10&max_routers=5"
  controld.sh orgs members            # List organization members
  controld.sh provision list
  controld.sh provision create PROFILE_ID windows 7d 100

Billing Examples:
  controld.sh billing payments        # Payment history
  controld.sh billing subscriptions   # Active/canceled subscriptions
  controld.sh billing products        # Currently activated products

Mobile Config Examples:
  controld.sh mobileconfig DEVICE_ID                    # Output to stdout
  controld.sh mobileconfig DEVICE_ID config.mobileconfig # Save to file
  controld.sh mobileconfig DEVICE_ID - "client_id=iphone&dont_sign=1"
EOF
}

# Profiles
profiles_list() {
    api GET /profiles | jq -r '.body.profiles[] | "\(.PK)\t\(.name)"'
}

profiles_get() {
    local id="$1"
    api GET "/profiles/$id" | jq '.body'
}

profiles_create() {
    local name="$1"
    local clone_id="${2:-}"
    if [[ -n "$clone_id" ]]; then
        api POST /profiles -d "{\"name\":\"$name\",\"clone_profile_id\":\"$clone_id\"}"
    else
        api POST /profiles -d "{\"name\":\"$name\"}"
    fi | jq '.body'
}

profiles_clone() {
    local name="$1"
    local clone_id="$2"
    api POST /profiles -d "{\"name\":\"$name\",\"clone_profile_id\":\"$clone_id\"}" | jq '.body'
}

profiles_update() {
    local id="$1"
    local name="$2"
    api PUT "/profiles/$id" -d "{\"name\":\"$name\"}" | jq '.body'
}

profiles_delete() {
    local id="$1"
    api DELETE "/profiles/$id" | jq '.'
}

profiles_options() {
    api GET /profiles/options | jq -r '.body.options[] | "\(.PK)\t\(.title)\t\(.type)"'
}

# Devices
devices_list() {
    api GET /devices | jq -r '.body.devices[] | "\(.device_id)\t\(.name)\t\(.status)\t\(.profile.name // "none")"'
}

devices_get() {
    local id="$1"
    api GET "/devices/$id" | jq '.body'
}

devices_types() {
    api GET /devices/types | jq '.body.types'
}

devices_create() {
    local name="$1"
    local profile_id="$2"
    local icon="${3:-router}"
    api POST /devices -d "{\"name\":\"$name\",\"profile_id\":\"$profile_id\",\"icon\":\"$icon\"}" | jq '.body'
}

devices_update() {
    local id="$1"
    shift
    local json="$*"
    api PUT "/devices/$id" -d "$json" | jq '.body'
}

devices_delete() {
    local id="$1"
    api DELETE "/devices/$id" | jq '.'
}

# Filters
filters_list() {
    local profile_id="$1"
    api GET "/profiles/$profile_id/filters" | jq -r '.body.filters[] | "\(.PK)\t\(.name)\t\(.status)"'
}

filters_external() {
    local profile_id="$1"
    api GET "/profiles/$profile_id/filters/external" | jq -r '.body.filters[] | "\(.PK)\t\(.name)\t\(.status)"'
}

filters_enable() {
    local profile_id="$1"
    local filter_id="$2"
    api PUT "/profiles/$profile_id/filters/filter/$filter_id" -d '{"status":1}' | jq '.body'
}

filters_disable() {
    local profile_id="$1"
    local filter_id="$2"
    api PUT "/profiles/$profile_id/filters/filter/$filter_id" -d '{"status":0}' | jq '.body'
}

# Services
services_categories() {
    api GET /services/categories | jq -r '.body.categories[] | "\(.PK)\t\(.name)\t\(.count)"'
}

services_in_category() {
    local category="$1"
    api GET "/services/categories/$category" | jq -r '.body.services[] | "\(.PK)\t\(.name)"'
}

services_list() {
    local profile_id="$1"
    api GET "/profiles/$profile_id/services" | jq -r '.body.services[] | "\(.PK)\t\(.name)\t\(.action.do)\t\(.action.status)"'
}

services_block() {
    local profile_id="$1"
    local service_id="$2"
    api PUT "/profiles/$profile_id/services/$service_id" -d '{"do":0,"status":1}' | jq '.body'
}

services_bypass() {
    local profile_id="$1"
    local service_id="$2"
    api PUT "/profiles/$profile_id/services/$service_id" -d '{"do":1,"status":1}' | jq '.body'
}

services_spoof() {
    local profile_id="$1"
    local service_id="$2"
    local via="${3:-}"
    if [[ -n "$via" ]]; then
        api PUT "/profiles/$profile_id/services/$service_id" -d "{\"do\":2,\"status\":1,\"via\":\"$via\"}" | jq '.body'
    else
        api PUT "/profiles/$profile_id/services/$service_id" -d '{"do":2,"status":1}' | jq '.body'
    fi
}

services_clear() {
    local profile_id="$1"
    local service_id="$2"
    api PUT "/profiles/$profile_id/services/$service_id" -d '{"status":0}' | jq '.body'
}

# Rule folders
folders_list() {
    local profile_id="$1"
    api GET "/profiles/$profile_id/groups" | jq -r '.body.groups[] | "\(.PK)\t\(.group)\t\(.action.status)"'
}

folders_create() {
    local profile_id="$1"
    local name="$2"
    local do_action="${3:-0}"
    api POST "/profiles/$profile_id/groups" -d "{\"name\":\"$name\",\"do\":$do_action}" | jq '.body'
}

folders_update() {
    local profile_id="$1"
    local folder_id="$2"
    local do_action="$3"
    api PUT "/profiles/$profile_id/groups/$folder_id" -d "{\"do\":$do_action,\"status\":1}" | jq '.body'
}

folders_delete() {
    local profile_id="$1"
    local folder_id="$2"
    api DELETE "/profiles/$profile_id/groups/$folder_id" | jq '.'
}

# Custom rules
rules_list() {
    local profile_id="$1"
    local folder_id="$2"
    api GET "/profiles/$profile_id/rules/$folder_id" | jq -r '.body.rules[] | "\(.PK)\t\(.action.do)\t\(.action.status)"'
}

rules_create() {
    local profile_id="$1"
    local do_action="$2"
    shift 2
    local hostnames
    hostnames=$(printf '"%s",' "$@" | sed 's/,$//')
    api POST "/profiles/$profile_id/rules" -d "{\"hostnames\":[$hostnames],\"do\":$do_action,\"status\":1}" | jq '.body'
}

rules_block() {
    local profile_id="$1"
    shift
    rules_create "$profile_id" 0 "$@"
}

rules_bypass() {
    local profile_id="$1"
    shift
    rules_create "$profile_id" 1 "$@"
}

rules_spoof() {
    local profile_id="$1"
    shift
    rules_create "$profile_id" 2 "$@"
}

rules_redirect() {
    local profile_id="$1"
    shift
    rules_create "$profile_id" 3 "$@"
}

rules_delete() {
    local profile_id="$1"
    local hostname="$2"
    api DELETE "/profiles/$profile_id/rules/$hostname" | jq '.'
}

# Default rule
default_get() {
    local profile_id="$1"
    api GET "/profiles/$profile_id/default" | jq '.body.default'
}

default_set() {
    local profile_id="$1"
    local do_action="$2"
    api PUT "/profiles/$profile_id/default" -d "{\"do\":$do_action,\"status\":1}" | jq '.body'
}

# IP access
access_list() {
    local device_id="$1"
    api GET /access -d "{\"device_id\":\"$device_id\"}" | jq -r '.body.ips[] | "\(.ip)\t\(.country)\t\(.city)"'
}

access_learn() {
    local device_id="$1"
    shift
    local ips
    ips=$(printf '"%s",' "$@" | sed 's/,$//')
    api POST /access -d "{\"device_id\":\"$device_id\",\"ips\":[$ips]}" | jq '.'
}

access_delete() {
    local device_id="$1"
    shift
    local ips
    ips=$(printf '"%s",' "$@" | sed 's/,$//')
    api DELETE /access -d "{\"device_id\":\"$device_id\",\"ips\":[$ips]}" | jq '.'
}

# Analytics
analytics_levels() {
    api GET /analytics/levels | jq -r '.body.levels[] | "\(.PK)\t\(.title)"'
}

analytics_endpoints() {
    api GET /analytics/endpoints | jq -r '.body.endpoints[] | "\(.PK)\t\(.title)\t\(.country_code)"'
}

# Proxies
proxies_list() {
    api GET /proxies | jq -r '.body.proxies[] | "\(.PK)\t\(.country)\t\(.city)\t\(.country_name)"'
}

proxies_list_full() {
    api GET /proxies | jq '.body.proxies'
}

# Account/Network
account() {
    api GET /users | jq '.body'
}

network() {
    api GET /network | jq '.body'
}

ip() {
    api GET /ip | jq '.body'
}

# Organizations (Business Accounts)
# Note: Organization endpoints operate on the org associated with your API token

orgs_info() {
    api GET /organizations/organization | jq '.body'
}

orgs_update() {
    # Uses form-urlencoded data
    local data="$*"
    curl -s -X PUT \
        -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "$data" \
        "${API_BASE}/organizations" | jq '.body'
}

# Members
members_list() {
    api GET /organizations/members | jq -r '.body.members[] | "\(.PK)\t\(.email)\t\(.permission)"'
}

# Sub-Organizations
suborgs_list() {
    api GET /organizations/sub_organizations | jq -r '.body.sub_organizations[] | "\(.PK)\t\(.name)\t\(.endpoint_count)\t\(.profile_count)"'
}

suborgs_create() {
    # Required: name, contact_email, twofa_req, stats_endpoint, max_users, max_routers
    # Uses form-urlencoded data
    local data="$*"
    curl -s -X POST \
        -H "Authorization: Bearer $CONTROLD_API_TOKEN" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "$data" \
        "${API_BASE}/organizations/suborg" | jq '.body'
}

# Billing
billing_payments() {
    api GET /billing/payments | jq '.body'
}

billing_subscriptions() {
    api GET /billing/subscriptions | jq '.body'
}

billing_products() {
    api GET /billing/products | jq '.body'
}

# Mobile Config
mobileconfig_generate() {
    local device_id="$1"
    local output="${2:--}"  # default to stdout
    local extra_params="${3:-}"
    local url="${API_BASE}/mobileconfig/${device_id}"
    [[ -n "$extra_params" ]] && url="${url}?${extra_params}"
    if [[ "$output" == "-" ]]; then
        curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" "$url"
    else
        curl -s -H "Authorization: Bearer $CONTROLD_API_TOKEN" "$url" -o "$output"
        echo "Saved to: $output"
    fi
}

# Provisioning
provision_list() {
    api GET /provision | jq -r '.body.codes[] | "\(.PK)\t\(.device_type)\t\(.status)\t\(.limit)\t\(.used)"'
}

provision_get() {
    local code_id="$1"
    api GET "/provision/$code_id" | jq '.body'
}

provision_create() {
    local profile_id="$1"
    local device_type="${2:-windows}"
    local expires_after="${3:-7d}"
    local limit="${4:-100}"
    local prefix="${5:-}"
    local json="{\"profile_id\":\"$profile_id\",\"device_type\":\"$device_type\",\"expires_after\":\"$expires_after\",\"limit\":$limit"
    [[ -n "$prefix" ]] && json="$json,\"prefix\":\"$prefix\""
    json="$json}"
    api POST /provision -d "$json" | jq '.body'
}

provision_invalidate() {
    local code_id="$1"
    api PUT "/provision/$code_id" -d '{"status":"invalid"}' | jq '.body'
}

provision_delete() {
    local code_id="$1"
    api DELETE "/provision/$code_id" | jq '.'
}

# Main dispatch
resource="${1:-}"
action="${2:-}"
shift 2 2>/dev/null || true

case "$resource" in
    profiles)
        case "$action" in
            list) profiles_list ;;
            get) profiles_get "$@" ;;
            create) profiles_create "$@" ;;
            clone) profiles_clone "$@" ;;
            update) profiles_update "$@" ;;
            delete) profiles_delete "$@" ;;
            options) profiles_options ;;
            *) usage; exit 1 ;;
        esac
        ;;
    devices)
        case "$action" in
            list) devices_list ;;
            get) devices_get "$@" ;;
            types) devices_types ;;
            create) devices_create "$@" ;;
            update) devices_update "$@" ;;
            delete) devices_delete "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    filters)
        case "$action" in
            list) filters_list "$@" ;;
            external) filters_external "$@" ;;
            enable) filters_enable "$@" ;;
            disable) filters_disable "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    services)
        case "$action" in
            categories) services_categories ;;
            in) services_in_category "$@" ;;
            list) services_list "$@" ;;
            block) services_block "$@" ;;
            bypass) services_bypass "$@" ;;
            spoof) services_spoof "$@" ;;
            clear) services_clear "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    folders)
        case "$action" in
            list) folders_list "$@" ;;
            create) folders_create "$@" ;;
            update) folders_update "$@" ;;
            delete) folders_delete "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    rules)
        case "$action" in
            list) rules_list "$@" ;;
            create) rules_create "$@" ;;
            block) rules_block "$@" ;;
            bypass) rules_bypass "$@" ;;
            spoof) rules_spoof "$@" ;;
            redirect) rules_redirect "$@" ;;
            delete) rules_delete "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    default)
        case "$action" in
            get) default_get "$@" ;;
            set) default_set "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    access)
        case "$action" in
            list) access_list "$@" ;;
            learn) access_learn "$@" ;;
            delete) access_delete "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    analytics)
        case "$action" in
            levels) analytics_levels ;;
            endpoints) analytics_endpoints ;;
            *) usage; exit 1 ;;
        esac
        ;;
    proxies)
        case "$action" in
            list) proxies_list ;;
            full) proxies_list_full ;;
            *) usage; exit 1 ;;
        esac
        ;;
    orgs)
        case "$action" in
            info) orgs_info ;;
            update) orgs_update "$@" ;;
            suborgs) suborgs_list ;;
            suborg-create) suborgs_create "$@" ;;
            members) members_list ;;
            *) usage; exit 1 ;;
        esac
        ;;
    billing)
        case "$action" in
            payments) billing_payments ;;
            subscriptions) billing_subscriptions ;;
            products) billing_products ;;
            *) usage; exit 1 ;;
        esac
        ;;
    mobileconfig)
        # mobileconfig is treated specially - action is actually the device_id
        mobileconfig_generate "$action" "${1:-}" "${2:-}"
        ;;
    provision)
        case "$action" in
            list) provision_list ;;
            get) provision_get "$@" ;;
            create) provision_create "$@" ;;
            invalidate) provision_invalidate "$@" ;;
            delete) provision_delete "$@" ;;
            *) usage; exit 1 ;;
        esac
        ;;
    account) account ;;
    network) network ;;
    ip) ip ;;
    help|--help|-h) usage ;;
    *) usage; exit 1 ;;
esac
