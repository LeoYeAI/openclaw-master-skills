# Render Blueprint (render.yaml) – Quick Reference

Full spec: [Blueprint YAML Reference](https://render.com/docs/blueprint-spec).  
JSON Schema for IDE validation: https://render.com/schema/render.yaml.json

## Root-level keys

- `services` – web, worker, cron, pserv, keyvalue
- `databases` – PostgreSQL
- `envVarGroups` – shared env vars (no fromDatabase/fromService/sync:false)
- `projects` / `ungrouped` – project/environment grouping
- `previews` – preview environment generation and expiry

## Service types

| type       | Purpose |
|-----------|---------|
| `web`     | Public HTTP app or static site (`runtime: static` for static) |
| `pserv`   | Private service (internal only) |
| `worker`  | Background worker |
| `cron`    | Scheduled job (cron expression) |
| `keyvalue`| Redis/Valkey-compatible Key Value (in `services`; use `fromService` to reference) |

## Runtimes

`runtime`: `node`, `python`, `elixir`, `go`, `ruby`, `rust`, `docker`, `image`, `static`.

## Env vars

- Literal: `key` + `value`
- From Postgres: `fromDatabase.name` + `fromDatabase.property` (e.g. `connectionString`)
- From service (e.g. Key Value): `fromService.type` + `fromService.name` + `fromService.property`
- Secret (user fills in Dashboard): `sync: false` (service-level only, not in env groups)
- Generated: `generateValue: true`

## Validation

- CLI: `render blueprints validate render.yaml` (Render CLI v2.7.0+)
- API: [Validate Blueprint](https://api-docs.render.com/reference/validate-blueprint)
