---
name: recamera-web-api
description: reCamera (RV1126B) device full-stack Web API reference covering authentication, device management, video/audio/image configuration, recording rules & storage, AI model inference, terminal/logs, and SenseCraft cloud model conversion. Use when developing or debugging reCamera frontend/backend features, calling device HTTP/WebSocket APIs, or integrating with SenseCraft AI services.
---

# reCamera Web API

Complete API reference for the reCamera (RV1126B) embedded camera platform. This skill enables agents to correctly construct HTTP requests, handle responses, and follow the interaction protocols required by the device.

## Conventions

### Base URL

All CGI endpoints are prefixed with:

```
/cgi-bin/entry.cgi/{api_category}/{resource}/{sub_resource}
```

Exceptions clearly noted per-endpoint (e.g. serial port uses `/api/v1/...`, file relay uses `/storage/relay/...`).

### Authentication (CRITICAL — Token Must Be Captured and Reused)

**Login flow (mandatory for all authenticated operations):**

1. Fetch RSA public key: `GET /system/key` (no auth required)
2. Login: `POST /system/login` with `{sUserName, sPassword}` (password RSA-encrypted)
3. **Extract token from response:** On success (`iStatus: 0, iAuth: 1`), the HTTP response contains a `Set-Cookie` header like `Set-Cookie: token=<jwt_value>; Path=/; ...`. You **MUST** capture the `token` value from this header.
4. **Persist token for session:** Store the extracted token value. All subsequent HTTP requests for this session must include the header: `Cookie: token=<jwt_value>`

**For curl / shell scripts:**
```bash
# Login and capture token from Set-Cookie header
RESPONSE=$(curl -s -D - -X POST http://{ip}/cgi-bin/entry.cgi/system/login \
  -H "Content-Type: application/json" \
  -d '{"sUserName":"admin","sPassword":"<RSA-encrypted>"}')
TOKEN=$(echo "$RESPONSE" | grep -oP 'Set-Cookie:.*token=\K[^;]+')

# ALL subsequent requests must carry the token cookie
curl -s -X GET http://{ip}/cgi-bin/entry.cgi/system/device-info \
  -H "Cookie: token=$TOKEN"
```

**For browser automation (browser-use agent):**
After navigating to the login page and submitting credentials, the browser automatically stores the `token` cookie from the `Set-Cookie` header. However, you should **verify** the cookie exists by checking `document.cookie` for a `token=` entry after login succeeds. All subsequent same-origin XHR/fetch requests will include the cookie automatically (the app uses `withCredentials: true`).

**IMPORTANT:** If you receive an HTTP 401 response or a response body with `"code": 401`, the token has expired or is missing. You must re-login to obtain a fresh token.

## Agent Playbooks (Mandatory Execution)

When user intent matches one of the following tasks, execute the corresponding workflow directly.

### Playbook A: Discover reCamera Devices in a Subnet

**Trigger intent examples:** "scan subnet", "find recamera on 192.168.x.0/24", "discover devices in LAN"

**Mandatory workflow:**
1. Enumerate active IPs in the target subnet (e.g. ARP table / ping sweep / nmap host discovery).
2. For each active IP, send `GET http://{ip}/cgi-bin/entry.cgi/system/key` (no auth).
3. Classify as reCamera only if:
   - HTTP status is `200`, and
   - response contains field `sPublicKey`.
4. Return a structured result with:
   - `reachable_ips`
   - `recamera_ips`
   - `non_recamera_ips`
   - `unreachable_or_timeout_ips`

**Do not** treat "TCP port open" alone as reCamera confirmation. `/system/key` verification is required.

### Playbook B: Login and Persist Token for Follow-up Calls

**Trigger intent examples:** "login device", "call authenticated API", "configure after login"

**Mandatory workflow:**
1. `GET /system/key` to fetch RSA public key.
2. `POST /system/login` with `{sUserName, sPassword}` (RSA-encrypted password).
3. On successful login (`iStatus: 0`, `iAuth: 1`), parse `Set-Cookie` response header and extract `token`.
4. Persist token in session context.
5. For all subsequent HTTP requests in the same session, include:
   - `Cookie: token=<jwt_value>`
6. If any request returns 401 / auth failure, re-login and refresh token, then retry once.

**Do not** continue authenticated calls without a captured token.

### Configuration Update Pattern (Read-Before-Write)

**CRITICAL:** For any endpoint that supports both GET and POST/PUT:
1. First `GET` the current full configuration
2. Modify only the fields you need to change on the returned data
3. `POST`/`PUT` the complete modified configuration back

Never send a partial configuration constructed from scratch. The device expects the full config object and omitted fields may revert to defaults or cause unexpected behavior.

### Field Naming

JSON keys use a **type-prefix + camelCase** convention:

| Prefix | Type | Example |
|--------|------|---------|
| `i` | Integer | `iCpuUsage` |
| `f` | Float | `fConfidence` |
| `s` | String | `sSerialNumber` |
| `l` | List/Array | `lActiveWeekdays` |
| `d` | Dict/Object | `dNtpConfig` |
| `b` | Boolean | `bRuleEnabled` |

### Standard Response

Operation endpoints (POST/PUT/DELETE) return:

```json
{
  "code": 0,
  "message": "success"
}
```

`code: 0` = success. Non-zero = error (see error code ranges below).

### Error Code Ranges

| Range | Module |
|-------|--------|
| `10xxx` | Device Info |
| `20xxx` | Live Video |
| `30xxx` | Recording & Storage |
| `40xxx` | AI Inference |
| `50xxx` | Terminal & Logs |

## API Quick Reference

### 1. Authentication

| Action | Method | Path | Notes |
|--------|--------|------|-------|
| Get RSA public key | GET | `/system/key` | No auth. Encrypt passwords with returned key |
| Login | POST | `/system/login` | Body: `{sUserName, sPassword}`. IP-based lockout on failures |
| Change password | PUT | `/system/password` | Body: `{sUserName, sOldPassword, sNewPassword}` (RSA-encrypted) |

Login response key fields:
- `iStatus`: 0=correct, -1=wrong password, -3=rate limited
- `iAuth`: 1=success, 0=fail, 2=must change password

### 2. Device Info

| Action | Method | Path |
|--------|--------|------|
| Device info | GET | `/system/device-info` |
| Get system time | GET | `/system/time` |
| Set system time | PUT | `/system/time` |
| System resources (CPU/NPU/Mem/Storage) | GET | `/system/resource-info` |
| Get network (LAN) | GET | `/network/lan` |
| Set network (LAN) | PUT | `/network/lan` |
| WiFi status | GET | `/network/wifi-status` |
| WiFi power on/off | POST | `/network/wifi-status?power=on\|off` |
| Scan WiFi list | GET | `/network/wifi-list` |
| Connected WiFi info | GET | `/network/wifi` |
| Connect WiFi | POST | `/network/wifi` |
| Forget WiFi | DELETE | `/network/wifi?Ignore={ssid}` |
| Get HTTP API settings | GET | `/web/setting` |
| Set HTTP API settings | POST | `/web/setting` |
| Get FTP settings | GET | `/ftp/setting` |
| Set FTP settings | POST | `/ftp/setting` |
| Get serial port config | GET | `/api/v1/device/serial-port` |
| Set serial port config | POST | `/api/v1/device/serial-port` |
| Export device config | GET | `/config/export` |
| Import device config | POST | `/config/upload` |
| Reboot | POST | `/system/reboot` |
| Factory reset (two-phase) | POST | `/system/factory-reset` |
| Get HTTPS status | GET | `/system/secure` |
| Set HTTPS | POST | `/system/secure` |
| Battery status | GET | `/system/battery` |

### 3. Live Video

| Action | Method | Path |
|--------|--------|------|
| Get video encode config | GET | `/video/{stream_id}/encode` |
| Set video encode config | PUT | `/video/{stream_id}/encode` |
| Get stream push config | GET | `/video/{stream_id}/stream` |
| Set stream push config | POST | `/video/{stream_id}/stream` |
| Get OSD config | GET | `/osd/cfg` |
| Set OSD config | POST | `/osd/cfg` |
| Get audio encode (stream) | GET | `/audio/{id}` |
| Set audio encode (stream) | POST | `/audio/{id}` |
| Get audio encode (storage) | GET | `/audio/storage` |
| Set audio encode (storage) | POST | `/audio/storage` |

`stream_id`: 0=main stream, 1=sub stream

### 4. Image (ISP) Settings

| Action | Method | Path |
|--------|--------|------|
| Get all ISP params | GET | `/image/0` |
| Reset to defaults | POST | `/image/0` |
| Switch scene profile | PUT | `/image/0/scene` |
| Video adjustment (rotation/flip) | PUT | `/image/0/video-adjustment` |
| Night-to-day params | PUT | `/image/0/night-to-day` |
| Image adjustment (brightness etc.) | PUT | `/image/0/{scene_id}/adjustment` |
| Exposure | PUT | `/image/0/{scene_id}/exposure` |
| Backlight (BLC/HDR/HLC) | PUT | `/image/0/{scene_id}/blc` |
| White balance | PUT | `/image/0/{scene_id}/white-blance` |
| Image enhancement (denoise) | PUT | `/image/0/{scene_id}/enhancement` |

`scene_id`: 0=general, 1=day, 2=night

**ISP Configuration Workflow:**
1. `GET /image/0` — fetch all params and determine current scene/profile in use
2. Select target scene profile (`scene_id` / `iProfile`: `0|1|2`) based on current mode or user-specified mode
3. `PUT /image/0/scene` with `{iProfile: 0|1|2}` — enter that profile's live edit mode (5min timeout)
4. Adjust parameters (brightness/contrast/hue/saturation/sharpness etc.) via `PUT /image/0/{scene_id}/{specific}`
5. Send save/commit command: `PUT /image/0/scene` with `{iProfile: -1}` to exit edit mode and finalize changes

**Mandatory sequence for image tuning tasks:** "select mode -> enter mode edit state -> adjust params -> send save command". Do not skip the final save/commit step.

### 5. Recording

| Action | Method | Path |
|--------|--------|------|
| Get/Set global rule config | GET/POST | `.../record/rule/config` |
| Get/Set schedule rule | GET/POST | `.../record/rule/schedule-rule-config` |
| Get/Set record rule (triggers) | GET/POST | `.../record/rule/record-rule-config` |
| Recording system info | GET | `.../record/rule/info` |
| HTTP rule trigger | POST | `.../record/rule/http-rule-activate` |
| Get/Set storage config | GET/POST | `.../record/storage/config` |
| Storage status | GET | `.../record/storage/status` |
| Storage control | POST | `.../record/storage/control` |

Trigger types: `INFERENCE_SET`, `TIMER`, `GPIO`, `TTY`, `HTTP`

Storage control actions: `FORMAT`, `FREE_UP`, `EJECT`, `CONFIG`, `RELAY`, `RELAY_STATUS`, `UNRELAY`, `REMOVE_FILES_OR_DIRECTORIES`

### 6. File Access (via Relay)

File access requires a relay session:
1. `POST .../record/storage/control` with `sAction: "RELAY"` — returns `dRelayStatus.sRelayDirectory` (UUID)
2. `GET /storage/relay/{uuid}/` — list directories (Nginx autoindex JSON)
3. `GET /storage/relay/{uuid}/{path}` — download file
4. Relay auto-expires after 300s; re-request refreshes timeout
5. Video thumbnails: `/path/to/.thumb/video.mp4.thumb.jpg` (may not exist, implement fallback)

### 7. AI Model & Inference

| Action | Method | Path |
|--------|--------|------|
| List models | GET | `/model/list` |
| Upload model (resumable) | POST | `/model/upload` |
| Delete model | DELETE | `/model/delete?File-name={name}` |
| Get model info | GET | `/model/info?File-name={name}` |
| Set model info | POST | `/model/info?File-name={name}` |
| Supported algorithms | GET | `/model/algorithm` |
| Get inference status | GET | `/model/inference?id=0` |
| Configure inference | POST | `/model/inference?id=0` |
| Get notification config | GET | `/notify/cfg` |
| Set notification config | POST | `/notify/cfg` |

Notification output modes: 0=off, 1=MQTT, 2=HTTP, 3=UART

### 8. WebSocket Endpoints

| Function | URL | Protocol |
|----------|-----|----------|
| Inference results stream | `/ws/inference/results` | WebSocket |
| Terminal (ttyd + xterm.js) | `/ws/system/terminal` | WebSocket |
| System logs | `/ws/system/logs` | WebSocket |

### 9. SenseCraft AI Cloud (ONNX to RKNN)

Base URL: `https://sensecraft-train-api.seeed.cc` (prod) / `https://test-sensecraft-train-api.seeed.cc` (test)

| Action | Method | Path | Key Params |
|--------|--------|------|------------|
| Create conversion task | POST | `/v1/api/create_task` | `user_id`, `framework_type=9`, `device_type=40`, `file` (.onnx) |
| List user models | GET | `/v1/api/get_training_records` | `user_id`, `framework_type=9`, `device_type=40`, `page`, `size` |
| Check task status | GET | `/v1/api/train_status` | `user_id`, `model_id` |
| Download model (v1) | GET | `/v1/api/get_model` | `user_id`, `model_id` — returns binary .rknn |
| Download model (v2) | GET | `/v2/api/get_model` | `user_id`, `model_id` — returns JSON with `download_url` |
| Delete cloud model | GET | `/v1/api/del_model` | `user_id`, `model_id` |

**SenseCraft Auth Flow:**
1. Redirect user to: `https://sensecraft.seeed.cc/ai/authorize?client_id=seeed_recamera&response_type=token&scop=profile&redirec_url={your_url}`
2. Receive token via callback
3. Backend resolves `user_id`: POST `https://sensecraft-hmi-api.seeed.cc/api/v1/user/login_token` with `Authorization: {token}` header

**Conversion polling:** 2s interval on `/train_status`; download only when `status === "done"`

## Firmware Upgrade Flow

Two modes: **local upload** (resumable) and **network download**.

**Network upgrade:**
1. `POST /system/firmware-upgrade?upload-type=network` with `{sReleaseURL}` — returns version info + `sConfirmToken`
2. `POST /system/firmware-upgrade?upload-type=network` with `{sConfirmToken}` — confirm upgrade
3. `GET /system/firmware-upgrade` — poll download progress

**Local upload (resumable):**
1. `POST /system/firmware-upgrade?upload-type=resumable` with `{iFileSize}` — returns `File-Id` header
2. `POST /system/firmware-upgrade?id={file_id}` with binary chunks (Content-Range headers)
3. `POST /system/firmware-upgrade?start={file_id}&md5sum={hash}` — finalize upload

## Factory Reset (Two-Phase Confirmation)

1. First `POST /system/factory-reset` — returns `sConfirmToken` (time-limited, ~1-5 min)
2. Second `POST /system/factory-reset` with `{sConfirmToken}` — executes reset

## Key Constraints & Gotchas

- **Read-before-write (GET-then-POST/PUT)**: When updating any configuration endpoint that has a corresponding GET method, ALWAYS fetch the current configuration first via GET, then modify only the needed fields on the fetched data, and POST/PUT the complete object back. Never construct a partial config payload from scratch — the device expects the full configuration structure and missing fields may be reset to defaults or cause errors
- **JWT token expiration**: The token obtained from login has a ~10-hour TTL. For long-running scripts or sessions, monitor for 401/auth errors and re-login to refresh the token
- **RTSP capture with OpenCV**: When using `cv2.VideoCapture` to grab frames from an RTSP stream, the first ~120 frames are stale buffered data. ALWAYS discard at least 120 frames before capturing a usable image (e.g. loop `cap.read()` 120 times, then take the next frame)
- **BLC/HDR/HLC are mutually exclusive** — only one can be `"open"` at a time in backlight settings
- **Privacy masks**: max 6 regions in OSD mask overlay
- **ISP scene config**: 5-minute inactivity timeout auto-exits live config mode
- **Storage RELAY**: requires slot state >= `CONFIGURED`; relay expires in 300s
- **Model inference**: model must have associated model info (JSON) before enabling
- **InferenceSet + classification model**: `RegionFilter` must be empty
- **InferenceSet + detection model**: at least one polygon required (default to full-frame `[[0,0],[1,0],[1,1],[0,1]]`)
- **Serial port** endpoint does NOT go through CGI: `/api/v1/device/serial-port`
- **File relay** endpoint does NOT go through CGI: `/storage/relay/...`
- **Device discovery**: To detect whether a reCamera device is reachable at a given IP, send `GET http://{ip}/cgi-bin/entry.cgi/system/key`. This endpoint requires no authentication and returns immediately. A successful response (HTTP 200 with `sPublicKey` field) confirms the target is a reCamera device

## Large Reference Reading Policy (Token-Efficient)

`API_REFERENCE.md` is intentionally large. Use it **on demand** instead of reading the whole file by default.

1. **Default behavior:** Do NOT read `API_REFERENCE.md` in full.
2. **First-pass routing:** Determine target module from user intent (auth/device/network/video/image/recording/storage/inference/websocket/cloud).
3. **Section-first lookup:** Read only the relevant section(s) for the current task.
4. **Progressive expansion:** If a field or constraint is still unclear, expand to adjacent subsection(s) only.
5. **Full-file exception:** Read the entire `API_REFERENCE.md` only when the user explicitly asks for a full audit/review/export, or when cross-module validation is strictly required.

Practical rule: prefer "minimum sufficient context" and keep reads scoped to the exact endpoint(s) being implemented or debugged.

## Additional Resources

- For complete endpoint schemas with all fields and value ranges, see [API_REFERENCE.md](API_REFERENCE.md)
