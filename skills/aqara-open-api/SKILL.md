---
name: aqara-open-api
description: Query and control Aqara/Lumi Studio smart home devices and manage spaces via the Aqara Open Platform API (HTTP JSON). Use when the user asks to list Aqara devices, get device status, control lights/switches/sensors, or manage rooms/spaces. Requires AQARA_OPEN_API_TOKEN and AQARA_ENDPOINT_URL.
version: 1.0.1
author: aqara
homepage: https://opendoc.aqara.com
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":["jq","curl"],"env":["AQARA_ENDPOINT_URL","AQARA_OPEN_API_TOKEN"]}}}
---

# Aqara Open API Skill

This skill equips the agent to operate Aqara/Lumi Studio smart home devices via HTTPS requests to the Aqara Open Platform API. **All operations are performed exclusively through `curl` commands**, except `GetAllDevicesWithSpaceRequest`, which must be executed through `bash scripts/fetch_all_devices.sh` to refresh the local cache file `data/devices.json`.

This skill supports only:
- device discovery and device type lookup
- device state queries from cache
- device control
- space listing, creation, update, and device assignment

## Configuration
The following environment variables are required:
- `AQARA_ENDPOINT_URL`: The base URL
- `AQARA_OPEN_API_TOKEN`: Your Long-Lived Access Token.

## AI Quick Navigation (Read This First)

> This section is a navigation and execution summary only. It **does not add new rules** or change existing constraints.

### What This Skill Can Do

- **Device discovery**: load all devices, space mappings, endpoints, functions, traits, and current values
- **Device type catalog**: query all device types in the project with code and display name
- **Device queries**: filter by type, name, room/space, or online status; read current trait values
- **Device control**: send control requests using real `deviceId`, `endpointId`, `functionCode`, and `traitCode` from cache
- **Space management**: list spaces, create spaces, update spaces, and assign devices to spaces

### Intent to Fastest Path

- **List all devices / devices by type / devices in a room / device state**
  - Check `data/devices.json`
  - If cache exists: read the file
  - If cache is missing: run `bash scripts/fetch_all_devices.sh`
- **Control a device**
  - Ensure `data/devices.json` exists
  - Read `deviceId + endpointId + functionCode + traitCode` from cache
  - Then use bash + `curl` for `ExecuteTraitRequest`
- **What device types are there?**
  - Use bash + `curl` for `GetDeviceTypeInfosRequest`
- **Refresh all device data**
  - Only run `bash scripts/fetch_all_devices.sh`
- **List spaces**
  - Use bash + `curl` for `GetSpacesRequest`
- **Create or update a space**
  - First get the real `spaceId` from `GetSpacesRequest`
  - Then call `CreateSpaceRequest` or `UpdateSpaceRequest`
- **Assign devices to a space**
  - First get the real `spaceId` from `GetSpacesRequest`
  - Read real `deviceId` values from `data/devices.json`
  - Then call `AssociateDevicesToSpaceRequest`

### Six Highest-Priority Rules

1. **All-device loading only goes through the script**: `GetAllDevicesWithSpaceRequest` may only be executed via `bash scripts/fetch_all_devices.sh`.
2. **All other requests only go through curl**: except for the refresh script above, every other API call must use bash + `curl`.
3. **Request bodies may only contain four fields**: `type`, `version`, `msgId`, and `data`; **`version` must always be `"v1"`**.
4. **`type` is whitelist-only**: use only the exact request types listed in this document; never test guessed alternatives such as `GetAllSpacesRequest`, `GetSpaceListRequest`, or `QuerySpaceListRequest`.
5. **All IDs and codes must come from real API data**: never guess `deviceId`, `endpointId`, `functionCode`, `traitCode`, or `spaceId`.

### Required Preconditions

- **Before listing devices, reading state, or filtering by room/type**: check whether `data/devices.json` exists
- **Before controlling a device**: obtain the real `deviceId`, `endpointId`, `functionCode`, and `traitCode` from the cache file
- **Before creating or updating a space**: if `spaceId` is needed, call `GetSpacesRequest` first
- **Before assigning devices to a space**: get `spaceId` from `GetSpacesRequest` and `deviceId` values from `data/devices.json`

### Terms and Field Reference

- **Cache file**: `data/devices.json`, which stores the `data` array from `GetAllDevicesWithSpaceRequest`
- **deviceId**: device identifier used for control and space assignment
- **endpointId**: endpoint identifier, only from cached `endpoints[].endpointId`
- **functionCode / traitCode**: capability identifiers from cache
- **spaceId**: space identifier from `GetSpacesRequest` or cached `space.spaceId`

### Section Index

- **Protocol and four-field request body**: see `## API Protocol`
- **Script vs curl execution rules**: see `### Execution Model`
- **Cache file rules**: see `### File Cache Model (Cache-First Data Model)`
- **Device APIs**: see `## API Commands` under `### Device Management`
- **Space APIs**: see `### Space Management`
- **Standard workflows**: see `## Standard Operating Procedures (SOP)`
- **Decision trees**: see `## Cache Decision Tree` and `## API Call Decision Tree`
- **Forbidden behavior**: see `## Forbidden Behavior`
- **Trait code reference**: see `references/trait-codes.md`

## 1. Role and Core Philosophy

**Role**: You are a strict hardware interface controller. Never infer or guess IDs or capability fields.

## 2. Hard Safety Rules

### 2.1 Valid Value Rule

Any operation involving live device state, such as power, brightness, or temperature, must follow this rule:

| Power status | Valid interpretation | Response style |
|-------------|----------------------|----------------|
| `Switch == "false"` | Brightness / color temperature / power should be treated as 0 or "off" | "The device is currently off" |
| `Switch == "true"` | Use the actual returned value | "Brightness is X%" |

**Never** produce logically inconsistent output such as "the light is off but brightness is 100%".

## Quick Start (Operator)

1. Set environment variables:
- `AQARA_OPEN_API_TOKEN`: your Aqara Open API Bearer token (JWT)
- `AQARA_ENDPOINT_URL`: the API base URL

**Real environment value rule**: `AQARA_ENDPOINT_URL` and `AQARA_OPEN_API_TOKEN` **must be read from the runtime environment** (via `$AQARA_ENDPOINT_URL` and `$AQARA_OPEN_API_TOKEN`). **Do not guess, fabricate, or use example placeholders** as real request values. If either variable is missing or empty, tell the user to configure it first.

2. Test connectivity:

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"GetAllDevicesWithSpaceRequest","version":"v1","msgId":"test-1"}'
```

## API Protocol

Base URL: `$AQARA_ENDPOINT_URL`

All requests use a **single unified POST endpoint**. Routing is determined by the `type` field in the JSON body.

### Request Envelope

The request-body JSON may contain **exactly these 4 fields**. Do not add, remove, or replace fields:

```json
{
  "type": "<RequestType>",
  "version": "v1",
  "msgId": "<unique-id>",
  "data": { ... }
}
```

| Field | Required | Meaning | Forbidden behavior |
|------|----------|---------|--------------------|
| `type` | Yes | API method name, such as `ExecuteTraitRequest` or `GetSpacesRequest` | Do not modify, abbreviate, or replace it with a value not listed in this document |
| `version` | Yes | **Must be the string `"v1"`** | Do not omit it; do not use `"v2"`, `"1.0"`, or any other value |
| `msgId` | Yes | Unique request identifier, such as `"msg-1234567890"` | None |
| `data` | Yes | Payload for the selected `type` (`null`, object, array, or string depending on the request) | Only use structures defined in this document or `references/` |

**Strict request-body constraints**

1. **Do not omit `version`**: every curl request body must include `"version":"v1"`.
2. **Do not add undefined fields**: the request body may contain **only** these 4 keys. Do not add `senderId`, `source`, `timestamp`, or any field not defined in this document.
3. **Do not invent field names or structures**: neither the top-level body nor `data` may contain made-up fields or undocumented shapes.
4. **Do not invent or trial-run alternate `type` values**: if this document says the request type is `GetSpacesRequest`, then `type` must be exactly `GetSpacesRequest`.
5. **Do not use synonym or variant guessing for `type`**: names such as `GetAllSpacesRequest`, `GetSpaceListRequest`, `QuerySpaceListRequest`, `ListSpacesRequest`, or other self-created variants are forbidden unless they are explicitly documented in this file.

### Required Headers

```
Authorization: Bearer $AQARA_OPEN_API_TOKEN
Content-Type: application/json
```

### Response Envelope

```json
{
  "type": "<ResponseType>",
  "version": "v1",
  "msgId": "<matching-id>",
  "code": 0,
  "message": null,
  "data": { ... }
}
```

`code: 0` = success. Non-zero = error. Common error codes:
- 400: invalid parameters
- 1001: token expired
- 2030: device not found

### curl Template

The `-d` value for every curl request must be a JSON object with **only 4 keys**: `type`, `version`, `msgId`, and `data`. Replace `<TYPE>` with the API method name and `<DATA>` with the correct payload:

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"<TYPE>","version":"v1","msgId":"msg-'$(date +%s)'","data":<DATA>}'
```

Always keep `"version":"v1"` in `-d`, and never add `senderId` or any other field not defined in this document.

## How the Agent Should Use This Skill

### Execution Model

**Execution rules (must follow)**:

- **Only `GetAllDevicesWithSpaceRequest`**: execute it via **`bash scripts/fetch_all_devices.sh`**. The script calls the API and writes the response `data` to `data/devices.json`. Do not call this request directly with curl.
- **All other supported API requests** (such as `ExecuteTraitRequest`, `GetSpacesRequest`, `CreateSpaceRequest`, `UpdateSpaceRequest`, and `AssociateDevicesToSpaceRequest`): execute them with **bash + `curl`**. The JSON body must contain **exactly 4 keys**: `type`, `version`, `msgId`, and `data`.
- **No exploratory `type` retries**: when a request fails, do not try nearby or similar type names. Verify the documented `type`, payload shape, token, IDs, cache, and required preconditions, then retry the same documented request only if appropriate.

### File Cache Model (Cache-First Data Model)

**Local cache file**

- `data/devices.json` — the `data` array from `GetAllDevicesWithSpaceRequest`, including complete device information: `deviceId`, `name`, `deviceTypesList`, `state`, `space`, `endpoints`, and all `functions/traits/current values`

**Refresh cache (create/overwrite cache file)**

```bash
bash scripts/fetch_all_devices.sh
```

**Usage rules (must follow)**

1. **Read cache first**: when the user asks for device lists, device types, room mappings, or basic device information, check whether `data/devices.json` exists and is non-empty.
2. **Cache hit**: if the cache file exists, **read the file directly** and continue. Do not call `GetAllDevicesWithSpaceRequest` again.
3. **Cache miss / missing file / parse failure**: run `bash scripts/fetch_all_devices.sh` to refresh the cache. After refresh, **re-read the cache file** before continuing.
4. **Explicit refresh requested by the user**: run `bash scripts/fetch_all_devices.sh` and then re-read the file.
5. **Control commands** (`ExecuteTraitRequest`) still go directly to the API via curl, but all `deviceId` / `endpointId` / `functionCode` / `traitCode` values **must come from the cache file**.

### Critical Data-Only Rule

**NEVER guess, fabricate, or infer** `deviceId`, `endpointId`, `functionCode`, or `traitCode`. Every value used in control calls **MUST** come from the cached `data/devices.json` file.

- `endpointId` must be taken from the device's `endpoints[].endpointId`.
- `functionCode` and `traitCode` must be taken from `endpoints[].functions[].traits[]`.
- `value` type must match the trait definition.

### Local Filtering (No Extra API Calls)

When the user asks for a subset of devices (for example, all lights, devices in the bedroom, or online switches):
- **Filter the cached `data/devices.json` locally** by `deviceTypesList`, `name`, `state`, or `space.name` / `space.spatialMarking`.
- Do **not** make a new API call to filter.

### Device Type vs Device Name

- **By Type (preferred)**: when the user asks for lights or switches, filter cached file by `deviceTypesList`.
- **By Name (secondary)**: use device name only to select a specific device from the cached list.

### Error Handling

- On errors with code 1001 (token expired) or 400 (bad params): re-check token, verify all IDs come from cached device data.
- On 2030: device not found; run `bash scripts/fetch_all_devices.sh` to refresh cache and retry.
- Timeout/network errors: retry once, then report.
- Cache file parse error: delete `data/devices.json` and run `bash scripts/fetch_all_devices.sh` to regenerate.

## API Commands (7 total)

### Device Management

#### Get all devices with space info — `GetAllDevicesWithSpaceRequest`

Retrieve all smart home devices in a single call, including full device info, space assignment, endpoints, functions, traits, and current values. No `data` field is needed (or `data: null`).

The agent **MUST** write this response to the local cache file (`data/devices.json`) and use the cache for all subsequent device queries, status checks, and as the basis for control commands. Use the provided script to fetch and cache:

```bash
bash scripts/fetch_all_devices.sh
```

Manual curl (for reference only — prefer the script):

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"GetAllDevicesWithSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'"}'
```

#### Get all device types — `GetDeviceTypeInfosRequest`

Retrieve every device type available in the current project. Each entry contains a `deviceType` code and its localized display `name`.

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"GetDeviceTypeInfosRequest","version":"v1","msgId":"msg-'$(date +%s)'"}'
```

#### Control device — `ExecuteTraitRequest`

Control one or more device functions, such as turning on/off or adjusting level. `endpointId`, `functionCode`, and `traitCode` must be read from the cache.

```bash
# Turn on
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"ExecuteTraitRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":[{"deviceId":"<deviceId>","endpointId":<endpointId>,"functionCode":"<functionCode>","traitCode":"OnOff","value":true}]}'

# Turn off
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"ExecuteTraitRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":[{"deviceId":"<deviceId>","endpointId":<endpointId>,"functionCode":"<functionCode>","traitCode":"OnOff","value":false}]}'
```

### Space Management

#### List space hierarchy — `GetSpacesRequest`

Retrieve all spaces as a hierarchical tree. Each space includes its ID, name, parent space ID, spatial marking label, and nested children.

**Space request type hard rule**: the request `type` for space listing is **only** `GetSpacesRequest`. Do not try `GetAllSpacesRequest`, `GetSpaceListRequest`, `QuerySpaceListRequest`, or any other guessed variant.

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"GetSpacesRequest","version":"v1","msgId":"msg-'$(date +%s)'"}'
```

#### Create a new space — `CreateSpaceRequest`

Create a room, zone, or building. Omit `parentSpaceId` to create a top-level space. Run `GetSpacesRequest` first if the parent space ID is not known.

```bash
# Top-level space
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"CreateSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"name":"Living Room","spatialMarking":"living_room"}}'

# Sub-space
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"CreateSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"name":"Bedroom","parentSpaceId":"<parentSpaceId>","spatialMarking":"bedroom"}}'
```

#### Update space properties — `UpdateSpaceRequest`

Update the name or spatial marking of an existing space. Only provided fields are updated. `spaceId` is required.

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"UpdateSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"spaceId":"<spaceId>","name":"New Room Name"}}'
```

#### Assign devices to a space — `AssociateDevicesToSpaceRequest`

Assign one or more devices to an existing space. Response `data` only contains failed items; empty means all succeeded.

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"AssociateDevicesToSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"spaceId":"<spaceId>","deviceIds":["<deviceId1>","<deviceId2>"]}}'
```

## Standard Operating Procedures (SOP)

### SOP A: List or discover devices

1. Check whether `data/devices.json` exists and is non-empty.
2. If it exists: read device data directly from the file.
3. If it is missing or empty: run `bash scripts/fetch_all_devices.sh` to generate the cache, then read the file.
4. Answer the user's request by filtering the cache file.

### SOP B: Query device state

1. Device state and trait values are already included in the cache file.
2. If `data/devices.json` is missing, run `bash scripts/fetch_all_devices.sh` first.
3. Find the device in the cache file and read the corresponding trait `value`.
4. No separate API call is needed to read device state.

### SOP C: Control device

1. If `data/devices.json` is missing, run `bash scripts/fetch_all_devices.sh` first.
2. Read the exact `deviceId`, `endpointId`, `functionCode`, and `traitCode` from the cache file.
3. Use the `ExecuteTraitRequest` curl command with only cached values.
4. Response `data` only contains failed items; an empty array means all commands succeeded.

### SOP D: Space management

1. Device-to-space associations are already included in `data/devices.json`.
2. Use the `GetSpacesRequest` curl command to retrieve the full space hierarchy tree.
3. Use `CreateSpaceRequest`, `UpdateSpaceRequest`, or `AssociateDevicesToSpaceRequest` as needed.

## Cache Decision Tree

```
Does the user request involve devices, spaces, or types?
├── Yes → Check the local cache file `data/devices.json`
│   ├── Cache hit (file exists and is non-empty)
│   │   └── Read from the file directly and filter/aggregate locally
│   └── Cache miss / missing file
│       ├── Run `bash scripts/fetch_all_devices.sh`
│       ├── Re-read the cache file
│       └── Continue with the refreshed data
└── No → Continue with the normal flow

Does the task require device control?
├── Yes → Ensure `data/devices.json` exists (refresh first if missing)
│   ├── Read `deviceId + endpointId + functionCode + traitCode` from cache
│   └── Call `ExecuteTraitRequest` via curl
└── No → Return the cached data result

Did the user explicitly ask to refresh device data?
└── Run `bash scripts/fetch_all_devices.sh` to overwrite the cache, then re-read it
```

## API Call Decision Tree

```
User wants devices by type?
  → data/devices.json exists? → Yes: filter file by deviceTypesList
                               → No:  bash scripts/fetch_all_devices.sh, then filter

User wants to list/discover all devices?
  → data/devices.json exists? → Yes: return full list from file
                               → No:  bash scripts/fetch_all_devices.sh, then read

User wants state of a device?
  → data/devices.json exists? → No: bash scripts/fetch_all_devices.sh
  → Read value from file: endpoints[].functions[].traits[].value

User wants to control a device?
  → data/devices.json exists? → No: bash scripts/fetch_all_devices.sh
  → Get deviceId + endpointId + functionCode + traitCode from file
  → curl ExecuteTraitRequest with correct value type

User wants devices by space/room?
  → data/devices.json exists? → Yes: filter file by space.name / spatialMarking
                               → No:  bash scripts/fetch_all_devices.sh, then filter

User wants to refresh device data?
  → bash scripts/fetch_all_devices.sh

User wants to see spaces?
  → curl GetSpacesRequest

User wants to create, update, or assign spaces?
  → curl GetSpacesRequest if a real spaceId is needed
  → then curl CreateSpaceRequest / UpdateSpaceRequest / AssociateDevicesToSpaceRequest
```

## Forbidden Behavior

| Forbidden | Correct behavior |
|-----------|------------------|
| Guessing or fabricating `deviceId` | Always use IDs from `data/devices.json` cache file. |
| Guessing or creating `endpointId` | Always take from `endpoints[].endpointId` in cache file. |
| Guessing `functionCode` or `traitCode` | Always take from `endpoints[].functions[].traits[]` in cache file. |
| Running `ExecuteTraitRequest` without first resolving device/endpoint info | Ensure `data/devices.json` exists and use the cached structure. |
| Using curl to call `GetAllDevicesWithSpaceRequest` | Only this request goes through the script: use `bash scripts/fetch_all_devices.sh`. |
| Calling the script or API for devices when cache file already exists and user did not ask to refresh | Read `data/devices.json` instead. |
| Making a separate API call to read device status/values | Device status and trait values are already in `data/devices.json`. |
| Inferring device type from device name | Filter cached devices by `deviceTypesList`. |
| Guessing `spaceId` | Always use IDs from `GetSpacesRequest` response or cached device `space.spaceId`. |
| Guessing or testing undocumented request `type` values | Use only the exact request names listed in `Request Type Whitelist`. |
| Trying alternate request names after a failure | Keep the documented `type` unchanged; inspect payload, token, IDs, cache, and preconditions. |
| Trying guessed space-list request names such as `GetAllSpacesRequest`, `GetSpaceListRequest`, or `QuerySpaceListRequest` | Use only `GetSpacesRequest` to list spaces. |
| Guessing or fabricating `AQARA_ENDPOINT_URL` or `AQARA_OPEN_API_TOKEN` | These must be read from the runtime environment. |

## Files

- `scripts/fetch_all_devices.sh` — cache refresh script; calls `GetAllDevicesWithSpaceRequest` and writes `data/devices.json`
- `data/devices.json` — cache file generated by the script; contains complete device data
- `references/examples.md` — example curl invocations
- `references/trait-codes.md` — full list of trait codes with type, unit, read/write, subscribe flags

Keep this `SKILL.md` lean; consult references for details.