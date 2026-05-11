#!/bin/bash
# Todoist CLI wrapper for OpenClaw

set -e

TOKEN_FILE="$HOME/.openclaw/workspace/.todoist-token"
IDENTITY_FILE="$HOME/.openclaw/workspace/.agent-identity.json"
API_BASE="https://api.todoist.com/api/v1"

# Load token
if [ ! -f "$TOKEN_FILE" ]; then
    echo "Token not found: $TOKEN_FILE"
    exit 1
fi
TOKEN=$(cat "$TOKEN_FILE")

# Load identity
load_identity() {
    if [ -f "$IDENTITY_FILE" ]; then
        INSTANCE_ID=$(jq -r .instance_id "$IDENTITY_FILE")
        CURRENT_AGENT=$(jq -r .current_agent "$IDENTITY_FILE")
        AGENT_LABEL=$(jq -r ".agents.$CURRENT_AGENT.todoist_label" "$IDENTITY_FILE")
    else
        INSTANCE_ID=$(hostname | shasum -a 256 | cut -c1-8)
        CURRENT_AGENT="main"
        AGENT_LABEL="agent-$INSTANCE_ID-main"
    fi
}

# API helpers
api_get() { curl -s "$API_BASE/$1" -H "Authorization: Bearer $TOKEN"; }
api_post() { curl -s -X POST "$API_BASE/$1" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$2"; }

get_task_id() {
    api_get "tasks" | jq -r ".results[] | select(.content | test(\"$1\"; \"i\")) | .id" | head -1
}

get_project_id() {
    api_get "projects" | jq -r ".results[] | select(.name | contains(\"$1\")) | .id" | head -1
}

# Commands
cmd_list() {
    local filter="${1:-all}"
    load_identity
    echo "Tasks (Instance: $INSTANCE_ID, Agent: $CURRENT_AGENT)"
    echo ""
    
    local tasks=$(api_get "tasks")
    local today=$(date +%Y-%m-%d)
    
    case "$filter" in
        today)
            echo "Today:"
            echo "$tasks" | jq -r ".results[] | select(.due.date == \"$today\") | \"  [ ] \(.content)\""
            ;;
        overdue)
            echo "Overdue:"
            echo "$tasks" | jq -r ".results[] | select(.due.date < \"$today\") | \"  [!] \(.content) (\(.due.date))\""
            ;;
        personal)
            local pid=$(get_project_id "个人事务")
            echo "Personal:"
            echo "$tasks" | jq -r ".results[] | select(.project_id == \"$pid\") | \"  [ ] \(.content)\""
            ;;
        agent)
            echo "Agent ($CURRENT_AGENT):"
            echo "$tasks" | jq -r ".results[] | select(.labels | index(\"$AGENT_LABEL\")) | \"  [ ] \(.content)\""
            ;;
        *)
            local pid=$(get_project_id "个人事务")
            echo "Personal:"
            echo "$tasks" | jq -r ".results[] | select(.project_id == \"$pid\") | \"  [ ] \(.content)\""
            echo ""
            echo "Agent ($CURRENT_AGENT):"
            echo "$tasks" | jq -r ".results[] | select(.labels | index(\"$AGENT_LABEL\")) | \"  [ ] \(.content)\""
            ;;
    esac
}

cmd_add() {
    local content="$1"
    local type="${2:-personal}"
    local due="${3:-}"
    load_identity
    
    local pid
    local labels="[]"
    
    if [ "$type" = "agent" ]; then
        pid=$(get_project_id "Agent 任务")
        labels="[\"$AGENT_LABEL\"]"
        echo "Adding Agent task [$CURRENT_AGENT]: $content"
    else
        pid=$(get_project_id "个人事务")
        echo "Adding personal task: $content"
    fi
    
    local payload="{\"content\":\"$content\",\"project_id\":\"$pid\",\"labels\":$labels"
    [ -n "$due" ] && payload="$payload,\"due_string\":\"$due\""
    payload="$payload}"
    
    api_post "tasks" "$payload" | jq -r '.content // "Added"'
}

cmd_subtask() {
    local parent="$1"
    local content="$2"
    local pid=$(get_task_id "$parent")
    [ -z "$pid" ] && { echo "Parent not found: $parent"; exit 1; }
    echo "Adding subtask to: $parent"
    api_post "tasks" "{\"content\":\"$content\",\"parent_id\":\"$pid\"}" | jq -r '.content // "Added"'
}

cmd_show() {
    local q="$1"
    local id=$(get_task_id "$q")
    [ -z "$id" ] && { echo "Task not found: $q"; exit 1; }
    local t=$(api_get "tasks" | jq -r ".results[] | select(.id == \"$id\")")
    echo "Task: $(echo "$t" | jq -r .content)"
    echo "Due: $(echo "$t" | jq -r '.due.string // "none"')"
    echo "Labels: $(echo "$t" | jq -r '.labels | join(", ") // "none"')"
    echo ""
    echo "Subtasks:"
    api_get "tasks" | jq -r ".results[] | select(.parent_id == \"$id\") | \"  - \(.content)\""
}

cmd_update() {
    local q="$1"
    local field="$2"
    local val="$3"
    local id=$(get_task_id "$q")
    [ -z "$id" ] && { echo "Task not found: $q"; exit 1; }
    
    local payload
    case "$field" in
        date|due) payload="{\"due_string\":\"$val\"}" ;;
        content) payload="{\"content\":\"$val\"}" ;;
        priority) payload="{\"priority\":$val}" ;;
        *) echo "Unknown field: $field"; exit 1 ;;
    esac
    
    curl -s -X POST "$API_BASE/tasks/$id" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$payload" > /dev/null
    echo "Updated: $q ($field = $val)"
}

cmd_claim() {
    local q="$1"
    load_identity
    local id=$(get_task_id "$q")
    [ -z "$id" ] && { echo "Task not found: $q"; exit 1; }
    local t=$(api_get "tasks" | jq -r ".results[] | select(.id == \"$id\")")
    local lbls=$(echo "$t" | jq -r '.labels')
    local new=$(echo "[$lbls, \"$AGENT_LABEL\"]" | jq -s 'add | unique')
    curl -s -X POST "$API_BASE/tasks/$id" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"labels\":$new}" > /dev/null
    echo "Claimed: $(echo "$t" | jq -r .content) -> $CURRENT_AGENT"
}

cmd_complete() {
    local q="$1"
    local id=$(get_task_id "$q")
    [ -z "$id" ] && { echo "Task not found: $q"; exit 1; }
    local name=$(api_get "tasks" | jq -r ".results[] | select(.id == \"$id\") | .content")
    api_post "tasks/$id/close" "{}" > /dev/null
    echo "Completed: $name"
}

cmd_delete() {
    local q="$1"
    local id=$(get_task_id "$q")
    [ -z "$id" ] && { echo "Task not found: $q"; exit 1; }
    local name=$(api_get "tasks" | jq -r ".results[] | select(.id == \"$id\") | .content")
    curl -s -X DELETE "$API_BASE/tasks/$id" -H "Authorization: Bearer $TOKEN" > /dev/null
    echo "Deleted: $name"
}

cmd_projects() { api_get "projects" | jq -r '.results[] | "  \(.name)"'; }
cmd_labels() { api_get "labels" | jq -r '.results[] | "  \(.name)"'; }
cmd_config() { jq -C . "$IDENTITY_FILE"; }

# Main
case "${1:-help}" in
    list|ls) cmd_list "$2" ;;
    add) cmd_add "$2" "$3" "$4" ;;
    subtask) cmd_subtask "$2" "$3" ;;
    show) cmd_show "$2" ;;
    update) cmd_update "$2" "$3" "$4" ;;
    claim) cmd_claim "$2" ;;
    complete|done) cmd_complete "$2" ;;
    delete|rm) cmd_delete "$2" ;;
    projects) cmd_projects ;;
    labels) cmd_labels ;;
    config) cmd_config ;;
    *)
        echo "Todoist CLI"
        echo ""
        echo "Commands:"
        echo "  list [today|personal|agent|overdue]  List tasks"
        echo "  add <content> [type] [due]           Add task"
        echo "  subtask <parent> <content>           Add subtask"
        echo "  show <keyword>                       Show task details"
        echo "  update <task> <field> <value>        Update task"
        echo "  claim <task>                         Claim task for current agent"
        echo "  complete <task>                      Complete task"
        echo "  delete <task>                        Delete task"
        echo "  projects                             List projects"
        echo "  labels                               List labels"
        echo "  config                               Show config"
        ;;
esac