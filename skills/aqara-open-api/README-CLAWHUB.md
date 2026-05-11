# Aqara Open API — ClawHub Deployment Guide

## Overview

Use the Aqara Open Platform API to query and control Aqara/Lumi smart home devices. This variant supports device discovery, state queries, device control, and space management.

## Environment Variables

| Variable | Required | Description |
|--------|----------|-------------|
| `AQARA_OPEN_API_TOKEN` | Yes | Aqara Open Platform Bearer token (JWT) |
| `AQARA_ENDPOINT_URL` | Yes | API endpoint URL, for example `https://aiot-open-3rd.aqara.cn/open/api` |

## Dependencies

- `curl` (system default)
- `python3` (used by the script to parse JSON responses)
- `bash` (used to run the cache refresh script)

## Execution Model

All API calls are sent as direct HTTP POST requests via `curl` to the Aqara Open Platform. Device data is fetched by the `scripts/fetch_all_devices.sh` script and cached into `data/devices.json`. Read from the cache file first and only call the API again when the cache is missing or the user explicitly requests a refresh.

## File Structure

```text
aqara-open-api/
├── SKILL.md
├── README-CLAWHUB.md
├── scripts/
│   └── fetch_all_devices.sh
├── data/
│   └── devices.json
└── references/
    ├── examples.md
    └── trait-codes.md
```

## Quick Verification

There are three common ways to configure environment variables:

1. Configure `openclaw.json`

```jsonc
{
  "env": {
    "AQARA_OPEN_API_TOKEN": "your-token",
    "AQARA_ENDPOINT_URL": "https://xxx.aqara.cn/open/api"
  }
}
```

2. Export global environment variables in bash and refresh the cache

```bash
export AQARA_OPEN_API_TOKEN="your-token"
export AQARA_ENDPOINT_URL="https://xxx.aqara.cn/open/api"

bash scripts/fetch_all_devices.sh
# Output: OK: wrote N devices to data/devices.json
```

3. Configure `Settints -> Skills -> Entries -> aqara-open-api -> Env`

```bash
AQARA_OPEN_API_TOKEN="your-token"
AQARA_ENDPOINT_URL="https://xxx.aqara.cn/open/api"
```

## API Notes

All requests go through the unified `POST {AQARA_ENDPOINT_URL}` entry point and are routed by the `type` field in the JSON body. Authentication uses `Authorization: Bearer <token>`.

This variant supports 7 API operations:
- **Device management**: `GetAllDevicesWithSpaceRequest` / `GetDeviceTypeInfosRequest` / `ExecuteTraitRequest`
- **Space management**: `GetSpacesRequest` / `CreateSpaceRequest` / `UpdateSpaceRequest` / `AssociateDevicesToSpaceRequest`

See `references/examples.md` for invocation examples and `references/trait-codes.md` for trait reference.

## Important Rules

- **File cache first**: run `bash scripts/fetch_all_devices.sh` to write device data into `data/devices.json`; later queries should read from the file to avoid redundant API calls
- **Read cache first, refresh on miss**: if `data/devices.json` exists, use it directly; only refresh when the file is missing or cannot be parsed
- **Single source of truth**: `endpointId`, `functionCode`, and `traitCode` must come from `data/devices.json`; never guess or fabricate them
- **Type-first filtering**: when querying by device type, prefer filtering by `deviceTypesList` from the cache file rather than inferring type from the device name
- **Resolve before control**: before controlling a device, ensure `data/devices.json` exists and use it to obtain the full endpoint/function/trait structure
