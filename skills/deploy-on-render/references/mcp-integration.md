# Render MCP Server

Render provides an official MCP server at **`https://mcp.render.com/mcp`**. Use it from IDEs that support MCP (e.g. Cursor, Codex) or via **mcporter** when available.

## Available tools (typical)

- **Workspace:** `list_workspaces`, `select_workspace`, `get_selected_workspace`
- **Create:** `create_web_service`, `create_static_site`, `create_cron_job`, `create_postgres`, `create_key_value`
- **Read:** `list_services`, `get_service`, `list_deploys`, `get_deploy`, `list_logs`, `list_log_label_values`, `get_metrics`
- **Data:** `query_render_postgres` (read-only SQL)

**create_web_service** (typical params): name, runtime, buildCommand, startCommand, repo, branch, plan, region, envVars.

**create_static_site**: name, buildCommand, publishPath (e.g. publishPath or staticPublishPath), repo, branch.

**create_cron_job**: name, schedule, runtime, buildCommand, startCommand, repo, branch.

**create_postgres**: name, plan, region, version, diskSizeGb.

**create_key_value**: name, plan, region, maxmemoryPolicy.

Exact parameter names and required fields: see [Render MCP server](https://github.com/render-oss/render-mcp-server) and [Render MCP docs](https://render.com/docs/mcp-server).

## Supported values

- **Runtimes:** node, python, go, rust, ruby, elixir, docker
- **Regions:** oregon, frankfurt, singapore, ohio, virginia
- **Plans (services):** starter, standard, pro, pro_max, pro_plus, pro_ultra
- **Plans (Postgres):** free, basic_256mb, basic_1gb, basic_4gb, pro_*, accelerated_*
- **Plans (Key Value):** free, starter, standard, pro, pro_plus

## OpenClaw and MCP

OpenClaw does **not** load MCP servers from config. You have two options:

1. **REST API** — Use `RENDER_API_KEY` and the Render REST API (curl / exec). See `references/rest-api-deployment.md` and the main skill for endpoints.
2. **mcporter** — If the user has `mcporter` installed and Render configured, the agent can call tools via mcporter, e.g.:
   - `mcporter call render.list_services`
   - `mcporter call render.create_web_service name=my-api runtime=node buildCommand="npm ci" startCommand="npm start" repo=https://github.com/user/repo branch=main`
   - `mcporter list render` or `mcporter list render --schema` to see tools and arguments.

Auth: set `RENDER_API_KEY` in the environment; mcporter config must pass it as Bearer token to `https://mcp.render.com/mcp`.
