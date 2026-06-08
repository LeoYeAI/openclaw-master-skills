#!/usr/bin/env bash
set -euo pipefail

# Coolify CLI - Pure bash implementation
# Manages Coolify deployments, applications, databases, and services via the Coolify API

# Configuration
COOLIFY_API_URL="${COOLIFY_API_URL:-https://app.coolify.io/api/v1}"
COOLIFY_TOKEN="${COOLIFY_TOKEN:-}"

# Colors for output (optional, falls back to plain)
if [[ -t 1 ]]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' NC=''
fi

# ============================================================================
# Helper Functions
# ============================================================================

check_requirements() {
  local missing=()
  
  command -v curl >/dev/null 2>&1 || missing+=("curl")
  command -v jq >/dev/null 2>&1 || missing+=("jq")
  
  if [[ ${#missing[@]} -gt 0 ]]; then
    error_response "MissingDependency" \
      "Missing required tools: ${missing[*]}" \
      "Install with: apt-get install ${missing[*]} (Debian/Ubuntu) or brew install ${missing[*]} (macOS)"
    exit 1
  fi
  
  if [[ -z "$COOLIFY_TOKEN" ]]; then
    error_response "MissingToken" \
      "COOLIFY_TOKEN environment variable not set" \
      "Set your API token: export COOLIFY_TOKEN='your-token-here'"
    exit 1
  fi
}

api_call() {
  local method="$1"
  local endpoint="$2"
  local data="${3:-}"
  
  local url="${COOLIFY_API_URL}${endpoint}"
  local response
  local http_code
  local temp_file
  
  temp_file=$(mktemp)
  
  if [[ -n "$data" ]]; then
    http_code=$(curl -s -w "%{http_code}" -o "$temp_file" \
      -X "$method" \
      -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$url")
  else
    http_code=$(curl -s -w "%{http_code}" -o "$temp_file" \
      -X "$method" \
      -H "Authorization: Bearer ${COOLIFY_TOKEN}" \
      "$url")
  fi
  
  response=$(cat "$temp_file")
  rm -f "$temp_file"
  
  # Handle HTTP errors
  if [[ "$http_code" -ge 400 ]]; then
    local error_msg
    error_msg=$(echo "$response" | jq -r '.message // .error // "Unknown error"' 2>/dev/null || echo "HTTP $http_code error")
    
    error_response "APIError" \
      "API request failed (HTTP $http_code): $error_msg" \
      "Check your API token and parameters"
    return 1
  fi
  
  echo "$response"
}

success_response() {
  local data="$1"
  local count="${2:-}"
  
  if [[ -n "$count" ]]; then
    echo "$data" | jq --argjson cnt "$count" '{success: true, data: ., count: $cnt}'
  else
    echo "$data" | jq '{success: true, data: .}'
  fi
}

error_response() {
  local type="$1"
  local message="$2"
  local hint="${3:-}"
  
  jq -n \
    --arg type "$type" \
    --arg msg "$message" \
    --arg hint "$hint" \
    '{success: false, error: {type: $type, message: $msg, hint: $hint}}'
}

# ============================================================================
# Applications Commands
# ============================================================================

cmd_applications_list() {
  local tag=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --tag)
        tag="$2"
        shift 2
        ;;
      *)
        error_response "UnknownOption" "Unknown option: $1" "Run: coolify applications list --help"
        return 1
        ;;
    esac
  done
  
  local endpoint="/applications"
  [[ -n "$tag" ]] && endpoint="${endpoint}?tag=${tag}"
  
  local response
  response=$(api_call GET "$endpoint")
  
  local count
  count=$(echo "$response" | jq 'length')
  success_response "$response" "$count"
}

cmd_applications_get() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid)
        uuid="$2"
        shift 2
        ;;
      *)
        error_response "UnknownOption" "Unknown option: $1" "Run: coolify applications get --uuid <uuid>"
        return 1
        ;;
    esac
  done
  
  if [[ -z "$uuid" ]]; then
    error_response "MissingParameter" "Missing required parameter: --uuid" "Usage: coolify applications get --uuid <uuid>"
    return 1
  fi
  
  local response
  response=$(api_call GET "/applications/${uuid}")
  success_response "$response"
}

cmd_applications_start() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid)
        uuid="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call POST "/applications/${uuid}/start")
  success_response "$response"
}

cmd_applications_stop() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid)
        uuid="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call POST "/applications/${uuid}/stop")
  success_response "$response"
}

cmd_applications_restart() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid)
        uuid="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call POST "/applications/${uuid}/restart")
  success_response "$response"
}

cmd_applications_logs() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid)
        uuid="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call GET "/applications/${uuid}/logs")
  success_response "$response"
}

cmd_applications_envs() {
  local subcommand="${1:-}"
  shift || true
  
  case "$subcommand" in
    list)
      cmd_applications_envs_list "$@"
      ;;
    create)
      cmd_applications_envs_create "$@"
      ;;
    update)
      cmd_applications_envs_update "$@"
      ;;
    delete)
      cmd_applications_envs_delete "$@"
      ;;
    bulk-update)
      cmd_applications_envs_bulk_update "$@"
      ;;
    *)
      error_response "UnknownSubcommand" "Unknown envs subcommand: $subcommand" \
        "Available: list, create, update, delete, bulk-update"
      return 1
      ;;
  esac
}

cmd_applications_envs_list() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid)
        uuid="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call GET "/applications/${uuid}/envs")
  success_response "$response"
}

cmd_applications_envs_create() {
  local uuid="" key="" value="" is_runtime="true" is_buildtime="false"
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      --key) key="$2"; shift 2 ;;
      --value) value="$2"; shift 2 ;;
      --is-runtime) is_runtime="$2"; shift 2 ;;
      --is-buildtime) is_buildtime="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  [[ -z "$key" ]] && { error_response "MissingParameter" "Missing --key" ""; return 1; }
  [[ -z "$value" ]] && { error_response "MissingParameter" "Missing --value" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg key "$key" \
    --arg value "$value" \
    --argjson runtime "$is_runtime" \
    --argjson buildtime "$is_buildtime" \
    '{key: $key, value: $value, is_runtime: $runtime, is_buildtime: $buildtime}')
  
  local response
  response=$(api_call POST "/applications/${uuid}/envs" "$data")
  success_response "$response"
}

cmd_applications_envs_update() {
  local uuid="" env_uuid="" value=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      --env-uuid) env_uuid="$2"; shift 2 ;;
      --value) value="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  [[ -z "$env_uuid" ]] && { error_response "MissingParameter" "Missing --env-uuid" ""; return 1; }
  [[ -z "$value" ]] && { error_response "MissingParameter" "Missing --value" ""; return 1; }
  
  local data
  data=$(jq -n --arg value "$value" '{value: $value}')
  
  local response
  response=$(api_call PATCH "/applications/${uuid}/envs/${env_uuid}" "$data")
  success_response "$response"
}

cmd_applications_envs_delete() {
  local uuid="" env_uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      --env-uuid) env_uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  [[ -z "$env_uuid" ]] && { error_response "MissingParameter" "Missing --env-uuid" ""; return 1; }
  
  local response
  response=$(api_call DELETE "/applications/${uuid}/envs/${env_uuid}")
  success_response "$response"
}

cmd_applications_envs_bulk_update() {
  local uuid="" json=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      --json) json="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  [[ -z "$json" ]] && { error_response "MissingParameter" "Missing --json" ""; return 1; }
  
  local response
  response=$(api_call POST "/applications/${uuid}/envs/bulk" "$json")
  success_response "$response"
}

cmd_applications_create_public() {
  local project_uuid="" server_uuid="" git_repository="" git_branch="" name=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --git-repository) git_repository="$2"; shift 2 ;;
      --git-branch) git_branch="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$git_repository" ]] && { error_response "MissingParameter" "Missing --git-repository" ""; return 1; }
  [[ -z "$git_branch" ]] && { error_response "MissingParameter" "Missing --git-branch" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg repo "$git_repository" \
    --arg branch "$git_branch" \
    --arg name "$name" \
    '{project_uuid: $project, server_uuid: $server, git_repository: $repo, git_branch: $branch, name: $name, build_pack: "nixpacks", ports_exposes: "3000"}')
  
  local response
  response=$(api_call POST "/applications/public" "$data")
  success_response "$response"
}

# ============================================================================
# Databases Commands
# ============================================================================

cmd_databases_list() {
  local response
  response=$(api_call GET "/databases")
  
  local count
  count=$(echo "$response" | jq 'length')
  success_response "$response" "$count"
}

cmd_databases_get() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call GET "/databases/${uuid}")
  success_response "$response"
}

cmd_databases_start() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call POST "/databases/${uuid}/start")
  success_response "$response"
}

cmd_databases_stop() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call POST "/databases/${uuid}/stop")
  success_response "$response"
}

cmd_databases_restart() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call POST "/databases/${uuid}/restart")
  success_response "$response"
}

cmd_databases_delete() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call DELETE "/databases/${uuid}")
  success_response "$response"
}

cmd_databases_create_postgresql() {
  local project_uuid="" server_uuid="" name="" postgres_user="postgres" postgres_password="" postgres_db=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --postgres-user) postgres_user="$2"; shift 2 ;;
      --postgres-password) postgres_password="$2"; shift 2 ;;
      --postgres-db) postgres_db="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg user "$postgres_user" \
    --arg password "$postgres_password" \
    --arg db "$postgres_db" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "postgresql", postgres_user: $user, postgres_password: $password, postgres_db: $db}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}


cmd_databases_create_mysql() {
  local project_uuid="" server_uuid="" name="" mysql_root_password="" mysql_database=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --mysql-root-password) mysql_root_password="$2"; shift 2 ;;
      --mysql-database) mysql_database="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg password "$mysql_root_password" \
    --arg database "$mysql_database" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "mysql", mysql_root_password: $password, mysql_database: $database}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}

cmd_databases_create_mariadb() {
  local project_uuid="" server_uuid="" name="" mariadb_root_password="" mariadb_database=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --mariadb-root-password) mariadb_root_password="$2"; shift 2 ;;
      --mariadb-database) mariadb_database="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg password "$mariadb_root_password" \
    --arg database "$mariadb_database" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "mariadb", mariadb_root_password: $password, mariadb_database: $database}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}

cmd_databases_create_mongodb() {
  local project_uuid="" server_uuid="" name="" mongo_initdb_root_username="" mongo_initdb_root_password=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --mongo-initdb-root-username) mongo_initdb_root_username="$2"; shift 2 ;;
      --mongo-initdb-root-password) mongo_initdb_root_password="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg username "$mongo_initdb_root_username" \
    --arg password "$mongo_initdb_root_password" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "mongodb", mongo_initdb_root_username: $username, mongo_initdb_root_password: $password}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}

cmd_databases_create_redis() {
  local project_uuid="" server_uuid="" name="" redis_password=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --redis-password) redis_password="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg password "$redis_password" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "redis", redis_password: $password}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}

cmd_databases_create_keydb() {
  local project_uuid="" server_uuid="" name="" keydb_password=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --keydb-password) keydb_password="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg password "$keydb_password" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "keydb", keydb_password: $password}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}

cmd_databases_create_clickhouse() {
  local project_uuid="" server_uuid="" name="" clickhouse_admin_user="" clickhouse_admin_password=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --clickhouse-admin-user) clickhouse_admin_user="$2"; shift 2 ;;
      --clickhouse-admin-password) clickhouse_admin_password="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg user "$clickhouse_admin_user" \
    --arg password "$clickhouse_admin_password" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "clickhouse", clickhouse_admin_user: $user, clickhouse_admin_password: $password}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}

cmd_databases_create_dragonfly() {
  local project_uuid="" server_uuid="" name="" dragonfly_password=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --project-uuid) project_uuid="$2"; shift 2 ;;
      --server-uuid) server_uuid="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --dragonfly-password) dragonfly_password="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$project_uuid" ]] && { error_response "MissingParameter" "Missing --project-uuid" ""; return 1; }
  [[ -z "$server_uuid" ]] && { error_response "MissingParameter" "Missing --server-uuid" ""; return 1; }
  [[ -z "$name" ]] && { error_response "MissingParameter" "Missing --name" ""; return 1; }
  
  local data
  data=$(jq -n \
    --arg project "$project_uuid" \
    --arg server "$server_uuid" \
    --arg name "$name" \
    --arg password "$dragonfly_password" \
    '{project_uuid: $project, server_uuid: $server, name: $name, type: "dragonfly", dragonfly_password: $password}')
  
  local response
  response=$(api_call POST "/databases" "$data")
  success_response "$response"
}


# ============================================================================
# Deployment Commands
# ============================================================================

cmd_deploy() {
  local uuid="" force="false" tag="" instant_deploy="false"
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      --tag) tag="$2"; shift 2 ;;
      --force) force="true"; shift ;;
      --instant-deploy) instant_deploy="true"; shift ;;
      *) shift ;;
    esac
  done
  
  if [[ -z "$uuid" && -z "$tag" ]]; then
    error_response "MissingParameter" "Missing --uuid or --tag" "Provide either --uuid or --tag"
    return 1
  fi
  
  local data
  data=$(jq -n \
    --argjson force "$force" \
    --argjson instant "$instant_deploy" \
    '{force: $force, instant_deploy: $instant}')
  
  local endpoint
  if [[ -n "$uuid" ]]; then
    endpoint="/applications/${uuid}/deploy"
  else
    endpoint="/deploy?tag=${tag}"
  fi
  
  local response
  response=$(api_call POST "$endpoint" "$data")
  success_response "$response"
}

cmd_deployments_list() {
  local response
  response=$(api_call GET "/deployments")
  success_response "$response"
}

cmd_deployments_get() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call GET "/deployments/${uuid}")
  success_response "$response"
}

# ============================================================================
# Servers Commands
# ============================================================================

cmd_servers_list() {
  local response
  response=$(api_call GET "/servers")
  
  local count
  count=$(echo "$response" | jq 'length')
  success_response "$response" "$count"
}

cmd_servers_get() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call GET "/servers/${uuid}")
  success_response "$response"
}

# ============================================================================
# Projects Commands
# ============================================================================

cmd_projects_list() {
  local response
  response=$(api_call GET "/projects")
  
  local count
  count=$(echo "$response" | jq 'length')
  success_response "$response" "$count"
}

cmd_projects_get() {
  local uuid=""
  
  while [[ $# -gt 0 ]]; do
    case $1 in
      --uuid) uuid="$2"; shift 2 ;;
      *) shift ;;
    esac
  done
  
  [[ -z "$uuid" ]] && { error_response "MissingParameter" "Missing --uuid" ""; return 1; }
  
  local response
  response=$(api_call GET "/projects/${uuid}")
  success_response "$response"
}

# ============================================================================
# Teams Commands
# ============================================================================

cmd_teams_list() {
  local response
  response=$(api_call GET "/teams")
  success_response "$response"
}

cmd_teams_current() {
  local response
  response=$(api_call GET "/teams/current")
  success_response "$response"
}

# ============================================================================
# Main Command Router
# ============================================================================

cmd_applications() {
  local subcommand="${1:-}"
  shift || true
  
  case "$subcommand" in
    list) cmd_applications_list "$@" ;;
    get) cmd_applications_get "$@" ;;
    start) cmd_applications_start "$@" ;;
    stop) cmd_applications_stop "$@" ;;
    restart) cmd_applications_restart "$@" ;;
    logs) cmd_applications_logs "$@" ;;
    envs) cmd_applications_envs "$@" ;;
    create-public) cmd_applications_create_public "$@" ;;
    *)
      error_response "UnknownSubcommand" "Unknown applications subcommand: $subcommand" \
        "Available: list, get, start, stop, restart, logs, envs, create-public"
      return 1
      ;;
  esac
}

cmd_databases() {
  local subcommand="${1:-}"
  shift || true
  
  case "$subcommand" in
    list) cmd_databases_list "$@" ;;
    get) cmd_databases_get "$@" ;;
    start) cmd_databases_start "$@" ;;
    stop) cmd_databases_stop "$@" ;;
    restart) cmd_databases_restart "$@" ;;
    delete) cmd_databases_delete "$@" ;;
    create-postgresql) cmd_databases_create_postgresql "$@" ;;
    create-mysql) cmd_databases_create_mysql "$@" ;;
    create-mariadb) cmd_databases_create_mariadb "$@" ;;
    create-mongodb) cmd_databases_create_mongodb "$@" ;;
    create-redis) cmd_databases_create_redis "$@" ;;
    create-keydb) cmd_databases_create_keydb "$@" ;;
    create-clickhouse) cmd_databases_create_clickhouse "$@" ;;
    create-dragonfly) cmd_databases_create_dragonfly "$@" ;;
    *)
      error_response "UnknownSubcommand" "Unknown databases subcommand: $subcommand" \
        "Available: list, get, start, stop, restart, delete, create-postgresql, create-mysql, create-mariadb, create-mongodb, create-redis, create-keydb, create-clickhouse, create-dragonfly"
      return 1
      ;;
  esac
}

cmd_deployments() {
  local subcommand="${1:-}"
  shift || true
  
  case "$subcommand" in
    list) cmd_deployments_list "$@" ;;
    get) cmd_deployments_get "$@" ;;
    *)
      error_response "UnknownSubcommand" "Unknown deployments subcommand: $subcommand" \
        "Available: list, get"
      return 1
      ;;
  esac
}

cmd_servers() {
  local subcommand="${1:-}"
  shift || true
  
  case "$subcommand" in
    list) cmd_servers_list "$@" ;;
    get) cmd_servers_get "$@" ;;
    *)
      error_response "UnknownSubcommand" "Unknown servers subcommand: $subcommand" \
        "Available: list, get"
      return 1
      ;;
  esac
}

cmd_projects() {
  local subcommand="${1:-}"
  shift || true
  
  case "$subcommand" in
    list) cmd_projects_list "$@" ;;
    get) cmd_projects_get "$@" ;;
    *)
      error_response "UnknownSubcommand" "Unknown projects subcommand: $subcommand" \
        "Available: list, get"
      return 1
      ;;
  esac
}

cmd_teams() {
  local subcommand="${1:-}"
  shift || true
  
  case "$subcommand" in
    list) cmd_teams_list "$@" ;;
    current) cmd_teams_current "$@" ;;
    *)
      error_response "UnknownSubcommand" "Unknown teams subcommand: $subcommand" \
        "Available: list, current"
      return 1
      ;;
  esac
}

show_help() {
  cat <<EOF
Coolify CLI - Manage Coolify deployments via API

Usage: coolify <command> <subcommand> [options]

Commands:
  applications    Manage applications
  databases       Manage databases
  deploy          Deploy an application
  deployments     View deployments
  servers         Manage servers
  projects        Manage projects
  teams           Manage teams

Examples:
  coolify applications list
  coolify applications get --uuid abc-123
  coolify deploy --uuid abc-123 --force
  coolify databases create-postgresql --project-uuid proj-123 --server-uuid srv-456 --name mydb

Environment Variables:
  COOLIFY_TOKEN      API token (required)
  COOLIFY_API_URL    API base URL (default: https://app.coolify.io/api/v1)

For more information, see SKILL.md
EOF
}

# ============================================================================
# Main Entry Point
# ============================================================================

main() {
  # Check requirements first
  check_requirements
  
  local command="${1:-}"
  
  if [[ -z "$command" || "$command" == "--help" || "$command" == "-h" ]]; then
    show_help
    exit 0
  fi
  
  shift
  
  case "$command" in
    applications) cmd_applications "$@" ;;
    databases) cmd_databases "$@" ;;
    deploy) cmd_deploy "$@" ;;
    deployments) cmd_deployments "$@" ;;
    servers) cmd_servers "$@" ;;
    projects) cmd_projects "$@" ;;
    teams) cmd_teams "$@" ;;
    *)
      error_response "UnknownCommand" "Unknown command: $command" "Run: coolify --help"
      exit 1
      ;;
  esac
}

main "$@"
