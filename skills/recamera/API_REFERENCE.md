# reCamera Web API — Endpoint Reference

Complete field-level documentation for every endpoint. Organized by functional module.

---

## 1. Authentication

### GET `/system/key` — Fetch RSA Public Key

**Auth required:** No

**Response:**

```json
{
  "sPublicKey": "-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAzEpEqV..."
}
```

Use the returned public key to encrypt passwords for login and password change operations.

---

### POST `/system/login` — Login

**Auth required:** No  
**IP-based lockout** on repeated failures.

**Request:**

```json
{
  "sUserName": "admin",
  "sPassword": "RSA-encrypted-password"
}
```

**Response:**

| Field | Type | Values |
|-------|------|--------|
| `iStatus` | int | `0` = correct password, `-1` = wrong password, `-3` = rate-limited |
| `iAuth` | int | `1` = login success, `0` = login fail, `2` = must change password |
| `sWaittime` | int | Timeout duration in seconds |

On success, the response header includes `Set-Cookie` with the JWT token. All subsequent requests must include `Cookie: token={jwt_token}`.

---

### PUT `/system/password` — Change Password

**Request:**

```json
{
  "sUserName": "admin",
  "sOldPassword": "RSA-encrypted-old",
  "sNewPassword": "RSA-encrypted-new"
}
```

---

## 2. Device Information

### GET `/system/device-info` — Basic Device Info

**Response:**

```json
{
  "sSerialNumber": "RC1126B-20240101-001",
  "sFirmwareVersion": "V1.0.3_20250915",
  "sSensorModel": "SC850SL",
  "sBasePlateModel": "PoE"
}
```

---

### GET `/system/time` — Get System Time

**Response:**

```json
{
  "sMethod": "ntp/manual",
  "dNtpConfig": {
    "sAddress": "",
    "sPort": "99"
  },
  "iTimestamp": 13256456,
  "sTimezone": "Asia/Shanghai",
  "sTz": "UTC+8"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `sMethod` | string | `"ntp"` or `"manual"` |
| `iTimestamp` | int64 | Unix timestamp (seconds) |
| `sTimezone` | string | Timezone city |
| `sTz` | string | UTC offset |

### PUT `/system/time` — Update System Time

Same schema as GET response. Returns updated time fields.

---

### GET `/system/resource-info` — System Resource Usage

**Response:**

```json
{
  "iCpuUsage": 13,
  "iNpuUsage": 20,
  "iMemUsage": 30,
  "iStorageUsage": 50
}
```

All values: integer, range 0–100.

---

### GET `/network/lan` — Get LAN Network Info

**Response:**

```json
{
  "dIpv4": {
    "sV4Address": "192.168.1.100",
    "sV4Gateway": "192.168.1.1",
    "sV4Method": "manual",
    "sV4Netmask": "255.255.255.0"
  },
  "dLink": {
    "sDNS1": "8.8.8.8",
    "sDNS2": "8.8.4.4",
    "sAddress": "aa:bb:cc:dd:ee:ff",
    "sInterface": "eth0",
    "iPower": 1,
    "sNicSpeed": "100baseT/Full"
  }
}
```

| Field | Description |
|-------|-------------|
| `sV4Method` | `"manual"` or `"dhcp"` |
| `sAddress` | MAC address |

### PUT `/network/lan` — Update LAN Network

**Request:** Send `dIpv4` and/or `dLink` (only `sDNS1`, `sDNS2` writable in dLink).

---

### GET `/network/wifi-status` — WiFi Status

```json
{
  "iPower": 1,
  "iId": 1,
  "sType": "wifi"
}
```

### POST `/network/wifi-status` — WiFi Power Control

**Query param:** `power=on|off`

---

### GET `/network/wifi-list` — Scan Available WiFi

**Response:** Array of:

```json
{
  "sBssid": "9a:bb:99:12:1b:61",
  "sFlags": "[WPA2-PSK-CCMP][ESS]",
  "iFrequency": 2412,
  "iRssi": -21,
  "sSsid": "NetworkName",
  "sConnected": "false",
  "sReserved": "false"
}
```

| Field | Description |
|-------|-------------|
| `sConnected` | `"true"` if currently connected (only one) |
| `sReserved` | `"true"` if password saved (can auto-connect) |

---

### GET `/network/wifi` — Connected WiFi Info

Returns `dIpv4` and `dLink` same structure as LAN.

### POST `/network/wifi` — Connect to WiFi

```json
{
  "sSsid": "WiFi_BSSID",
  "sPassword": "password123"
}
```

- `sSsid` is the BSSID (unique identifier), not the display name
- `sPassword` can be omitted if already saved or open network

**Response:**

```json
{
  "code": 0,
  "message": "",
  "status": 0
}
```

`status`: 0 = success, -1 = timeout, -2 = wrong password

### DELETE `/network/wifi` — Forget WiFi

**Query param:** `Ignore={ssid}`

---

### GET/POST `/web/setting` — HTTP API Settings

```json
{
  "sEnable": true,
  "sApiKey": "adfsfgfvxcvb"
}
```

---

### GET/POST `/ftp/setting` — FTP Service Settings

```json
{
  "sEnabel": true,
  "sFtpPort": "1234",
  "sFtpUser": "username",
  "sFtpPassword": "password"
}
```

POST error codes: `10001` = weak password, `10004` = port out of range, `10005` = port occupied.

---

### GET/POST `/api/v1/device/serial-port` — Serial Port Config

**Note:** This endpoint does NOT go through CGI. Auth via JWT.

```json
{
  "iBaudrate": 115200,
  "sParity": "N",
  "iStopbits": 1,
  "iBytesize": 8
}
```

Baud rate options: 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600.

---

### GET `/config/export` — Export Config

```json
{
  "size": 7812608,
  "url": "/download/config.tar"
}
```

Download via: `http://{device_ip}/download/config.tar`

### POST `/config/upload` — Import Config

Upload the config tar file.

---

### POST `/system/reboot` — Reboot Device

Standard success response.

---

### POST `/system/factory-reset` — Factory Reset (Two-Phase)

**Phase 1** — Initial request (empty body):

```json
{
  "code": 0,
  "sConfirmToken": "adfagghvshf"
}
```

`sConfirmToken` has a time limit (~1–5 minutes).

**Phase 2** — Confirm with token:

```json
{
  "sConfirmToken": "adfagghvshf"
}
```

---

### GET/POST `/system/secure` — HTTPS Settings

```json
{
  "sEnable": true
}
```

---

### GET `/system/battery` — Battery Status

```json
{
  "isAttached": true,
  "displaySteps": 3,
  "totalSteps": 5,
  "isCharging": false
}
```

---

## 3. Firmware Upgrade

### POST `/system/firmware-upgrade` — Firmware Upload/Download

#### Network Upgrade

**Step 1:** `POST ?upload-type=network`

```json
{ "sReleaseURL": "http://github.com" }
```

Response:

```json
{
  "code": 0,
  "iUpdateAvailable": true,
  "sCurrentVersion": "V1.0.0",
  "sLatestVersion": "V1.1.0",
  "sConfirmToken": "xxxxxxxxxx",
  "sUpdating": true
}
```

**Step 2:** `POST ?upload-type=network` (confirm)

```json
{ "sConfirmToken": "xxxxxxxxx" }
```

**Progress:** `GET /system/firmware-upgrade`

```json
{
  "iCurrent": 589431.0,
  "iPercent": 1,
  "sStatus": "downloading",
  "iTotal": 49219701.0
}
```

`sStatus`: `"downloading"`, `"error"`, `"success"`

#### Local Upload (Resumable)

**Step 1: Init** `POST ?upload-type=resumable`
- Content-Type: text/plain, content-length: 0
- Body: `{"iFileSize": 10254}`
- Response header: `File-Id: 123`

**Step 2: Upload chunks** `POST ?id=123`
- Content-Type: text/plain
- content-range: `bytes 0-524288`
- Body: binary firmware data

**Step 3: Finalize** `POST ?start=123&md5sum=<hash>`
- Content-Type: text/plain

---

## 4. Live Video Configuration

### GET/PUT `/video/{stream_id}/encode` — Video Encoding

`stream_id`: `0` = main stream, `1` = sub stream

```json
{
  "id": 0,
  "sStreamType": "mainStream",
  "iEnabled": 1,
  "sResolution": "3840*2160",
  "sOutputDataType": "H.265",
  "sFrameRate": "30",
  "iMaxRate": 8192,
  "iGOP": 60,
  "sRCMode": "VBR",
  "sRCQuality": "highest"
}
```

| Field | Constraints |
|-------|-------------|
| `sStreamType` | `"mainStream"` / `"subStream"` |
| `sResolution` | Max 3840\*2160, min width/height 384, square allowed |
| `sOutputDataType` | `"H.264"` / `"H.265"` |
| `sFrameRate` | 1–120 |
| `iMaxRate` | 3–200000 (kbps) |
| `iGOP` | 1–120 |
| `sRCMode` | `"CBR"` (constant) / `"VBR"` (variable) |
| `sRCQuality` | `"highest"` / `"high"` / `"medium"` / `"low"` (VBR only) |

---

### GET/POST `/video/{stream_id}/stream` — Stream Push Config

```json
{
  "rtsp": {
    "iEnabled": 1,
    "sURL": "",
    "iAuthType": 0,
    "sUserName": "admin",
    "sPassword": "admin"
  },
  "rtmp": {
    "iEnabled": 1,
    "sURL": "rtmp://xxx"
  },
  "onvif": {
    "iEnabled": 1,
    "iAuthType": 0,
    "sUserName": "admin",
    "sPassword": "admin"
  },
  "muticast": {
    "iEnabled": 1,
    "sAddress": "224.1.1.1",
    "sPort": "8868"
  }
}
```

---

### GET/POST `/osd/cfg` — OSD Configuration

```json
{
  "attribute": {
    "iOSDFontSize": 64,
    "sOSDFrontColor": "fff799",
    "sOSDFrontColorMode": 1
  },
  "channelNameOverlay": {
    "iEnabled": 1,
    "iPositionX": 0.528,
    "iPositionY": 0.458,
    "sChannelName": "reCamera 1126B"
  },
  "dateTimeOverlay": {
    "iEnabled": 1,
    "iDisplayWeekEnabled": 1,
    "iPositionX": 0.05,
    "iPositionY": 0.244,
    "sDateStyle": "CHR-YYYY-MM-DD",
    "sTimeStyle": "24hour"
  },
  "SNOverlay": {
    "iEnabled": 1,
    "iPositionX": 0.050,
    "iPositionY": 0.244
  },
  "inferenceOverlay": {
    "iEnabled": 1
  },
  "maskOverlay": {
    "iEnabled": 1,
    "privacyMask": [
      {
        "id": 0,
        "iMaskHeight": 0.77,
        "iMaskWidth": 0.213,
        "iPositionX": 0.53,
        "iPositionY": 0.380
      }
    ]
  }
}
```

| Field | Constraints |
|-------|-------------|
| `iOSDFontSize` | 0 (auto), 16, 32, 48, 64 |
| `sOSDFrontColor` | RGB hex, e.g. `"ff0000"` |
| `sOSDFrontColorMode` | 0 = auto B/W, 1 = custom |
| Position fields | Float 0.0–1.0 (relative to frame) |
| `sDateStyle` | `"CHR-YYYY-MM-DD"`, `"CHR-DD-MM-YYYY"`, `"CHR-MM-DD-YYYY"`, `"NUM-YYYY-MM-DD"`, `"NUM-DD-MM-YYYY"`, `"NUM-MM-DD-YYYY"` |
| `sTimeStyle` | `"12hour"` / `"24hour"` |
| `privacyMask` | Max 6 regions |
| Week display | Always in English |

---

### GET/POST `/audio/{id}` — Stream Audio Encoding

`id`: `0` = main stream audio, `1` = sub stream audio

```json
{
  "iEnable": 1,
  "iBitRate": 64000,
  "sEncodeType": "G711A"
}
```

- G711A/G711U: bitrate fixed at 64000
- `sEncodeType`: `"G711A"` / `"G711U"`

### GET/POST `/audio/storage` — Storage Audio Encoding

```json
{
  "iEnable": 1,
  "iBitRate": "64000",
  "sEncodeType": "MP3"
}
```

Bitrate range: 8000–128000 (GET) / 32000–128000 (POST).

---

## 5. Image (ISP) Settings

### GET `/image/0` — Get All ISP Parameters

Returns complete ISP configuration including `videoAdjustment`, `nightToDay`, and `profile` array (3 profiles: general, day, night).

### POST `/image/0` — Reset to Default Values

Send the full configuration structure. Device calls `rk_param_reload()` internally.

### PUT `/image/0/scene` — Switch Scene Profile

```json
{ "iProfile": 0 }
```

- `-1`: exit live scene config mode
- `0`, `1`, `2`: enter live scene config mode for that profile

### PUT `/image/0/video-adjustment` — Video Adjustment

```json
{
  "iImageRotation": 90,
  "sImageFlip": "close",
  "sPowerLineFrequencyMode": "NTSC(60HZ)"
}
```

| Field | Values |
|-------|--------|
| `iImageRotation` | 0, 90, 180, 270 |
| `sImageFlip` | `"close"`, `"mirror"` (horizontal), `"flip"` (vertical), `"centrosymmetric"` (both) |
| `sPowerLineFrequencyMode` | `"PAL(50HZ)"`, `"NTSC(60HZ)"` |

### PUT `/image/0/night-to-day` — Night-to-Day

```json
{
  "iMode": 0,
  "iNightToDayFilterLevel": 2,
  "iNightToDayFilterTime": 5,
  "iDawnTime": 28800,
  "iDuskTime": 64800,
  "iProfileSelect": 0
}
```

| Field | Description | Range |
|-------|-------------|-------|
| `iMode` | 0=auto, 1=scheduled, 2=fixed | — |
| `iNightToDayFilterLevel` | Sensitivity (auto mode) | 0=high, 1=mid, 2=low |
| `iNightToDayFilterTime` | Debounce (auto mode) | 1–60s |
| `iDawnTime` | Dawn time in seconds (scheduled) | 0–86400 |
| `iDuskTime` | Dusk time in seconds (scheduled, must > dawn) | 0–86400 |
| `iProfileSelect` | Profile for fixed mode | 0=general, 1=day, 2=night |

### PUT `/image/0/{scene_id}/adjustment` — Image Adjustment

```json
{
  "iBrightness": 57,
  "iContrast": 50,
  "iHue": 50,
  "iSaturation": 50,
  "iSharpness": 50
}
```

All values: 0–100.

### PUT `/image/0/{scene_id}/exposure` — Exposure

```json
{
  "iExposureGain": 1,
  "sExposureMode": "auto",
  "sExposureTime": "1/6",
  "sGainMode": "auto"
}
```

| Field | Values |
|-------|--------|
| `sExposureMode` | `"auto"` / `"manual"` |
| `sGainMode` | `"auto"` / `"manual"` |
| `sExposureTime` | Fraction string, must be <= 1/FPS in manual mode |

### PUT `/image/0/{scene_id}/blc` — Backlight

```json
{
  "sBLCRegion": "open",
  "iBLCStrength": 28,
  "sHDR": "close",
  "iHDRLevel": 1,
  "sHLC": "close",
  "iHLCLevel": 1
}
```

**CRITICAL:** `sBLCRegion`, `sHDR`, `sHLC` are mutually exclusive — only ONE can be `"open"`.

| Field | Range |
|-------|-------|
| `iBLCStrength` | 0–100 |
| `iHDRLevel` | Fixed at 1 (ISP3.5) |
| `iHLCLevel` | 1–100 |

### PUT `/image/0/{scene_id}/white-blance` — White Balance

```json
{
  "iWhiteBalanceCT": 2800,
  "sWhiteBlanceStyle": "auto"
}
```

| Field | Values |
|-------|--------|
| `iWhiteBalanceCT` | 2800–7500 (Kelvin) |
| `sWhiteBlanceStyle` | `"auto"`, `"manual"`, `"daylight"`, `"streetlamp"`, `"outdoor"` |

### PUT `/image/0/{scene_id}/enhancement` — Image Enhancement

```json
{
  "iSpatialDenoiseLevel": 50,
  "iTemporalDenoiseLevel": 50,
  "sNoiseReduceMode": 0
}
```

| Field | Description |
|-------|-------------|
| `sNoiseReduceMode` | `0` = off, `1` = on |
| `iSpatialDenoiseLevel` | 0–100 (forced to 50 if mode=off or 3dnr) |
| `iTemporalDenoiseLevel` | 0–100 (forced to 50 if mode=off or 2dnr; high values cause motion blur) |

---

## 6. Recording System

### GET/POST `.../record/rule/config` — Global Rule Config

```json
{
  "bRuleEnabled": true,
  "dWriterConfig": {
    "sFormat": "MP4",
    "iIntervalMs": 0
  }
}
```

| Field | Values |
|-------|--------|
| `sFormat` | `"MP4"`, `"JPG"`, `"RAW"` (case-sensitive) |
| `iIntervalMs` | Minimum capture interval (ms). Default 5000 for images, 0 for video |

---

### GET/POST `.../record/rule/schedule-rule-config` — Schedule Rule

```json
{
  "bEnabled": true,
  "lActiveWeekdays": [
    {
      "sStart": "Mon 09:00:00",
      "sEnd": "Mon 18:00:00"
    }
  ]
}
```

Time format: `"Day HH:MM:SS"` (Day: Sun/Mon/Tue/Wed/Thu/Fri/Sat). Supports `24:00:00`. Full week example: `{"sStart": "Mon 00:00:00", "sEnd": "Sun 24:00:00"}`.

---

### GET/POST `.../record/rule/record-rule-config` — Record Rule (Triggers)

```json
{
  "sCurrentSelected": "INFERENCE_SET",
  "lInferenceSet": [
    {
      "sID": "person_detection",
      "iDebounceTimes": 3,
      "lConfidenceFilter": [0.5, 1.0],
      "lClassFilter": [0, 1],
      "lRegionFilter": [
        {
          "lPolygon": [[0.0, 0.0], [0.5, 0.0], [0.5, 0.5], [0.0, 0.5]]
        }
      ]
    }
  ],
  "dTimer": {
    "iIntervalSeconds": 60
  },
  "dGPIO": {
    "sName": "GPIO_01",
    "sState": "FLOATING",
    "sSignal": "HIGH",
    "iDebounceDurationMs": 100
  },
  "dTTY": {
    "sName": "Console",
    "sCommand": "RECORD"
  }
}
```

| Field | Values |
|-------|--------|
| `sCurrentSelected` | `"INFERENCE_SET"`, `"TIMER"`, `"GPIO"`, `"TTY"`, `"HTTP"` |
| `lConfidenceFilter` | `[min, max]`, range 0.0–1.0 |
| `lRegionFilter` | Array of polygons. Empty for classification models. At least one for detection (default: `[[0,0],[1,0],[1,1],[0,1]]`) |
| `sState` (GPIO) | `"FLOATING"`, `"PULL_UP"`, `"PULL_DOWN"` |
| `sSignal` (GPIO) | `"HIGH"`, `"LOW"`, `"RISING"`, `"FALLING"` |

---

### GET `.../record/rule/info` — Recording System Info

```json
{
  "bReadyForNewEvent": true,
  "dLastRuleEvent": {
    "sStatus": "COMPLETED",
    "iTimestamp": 1735574400
  },
  "dLastRuleEventOwner": {
    "sRuleType": "TIMER",
    "sRuleID": "timer_rule_1",
    "iTimestamp": 1735574400
  },
  "dAvailableGPIOs": {
    "GPIO_01": {
      "iNum": 1,
      "sState": "FLOATING",
      "lCapabilities": ["FLOATING", "PULL_UP", "PULL_DOWN"],
      "sLevel": "HIGH"
    }
  },
  "dAvailableTTYs": {
    "ttyS0": {
      "sSocketPath": "/tmp/ttyS0.sock",
      "iBufferSize": 1024
    }
  },
  "bMediaPaused": false,
  "bVideoClipLengthSeconds": 60
}
```

Event status values: `"PENDING"`, `"WRITING"`, `"COMPLETED"`, `"FAILED"`, `"INTERRUPTED"`, `"UNKNOWN"`

---

### POST `.../record/rule/http-rule-activate` — Trigger HTTP Rule

Returns `{"code": 0}` on success.

Error conditions:
- `30001` (EPERM): rules disabled / schedule inactive / not HTTP rule selected
- `30016` (EBUSY): storage not ready / event in progress / previous recording still writing

Precondition: `bReadyForNewEvent === true` in info endpoint.

---

### GET/POST `.../record/storage/config` — Storage Configuration

```json
{
  "dSelectSlotToEnable": {
    "sByDevPath": "/dev/sda1",
    "sByUUID": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

- Set to `null` to disable all slots
- `sByDevPath` and `sByUUID` cannot both be empty
- Internal devices: prefer `sByDevPath`. External devices: prefer `sByUUID`
- Async operation: check storage status for actual enable state (poll, up to 30s)

---

### GET `.../record/storage/status` — Storage Status

Returns `lSlots` array. Each slot:

```json
{
  "sDevPath": "/dev/sda1",
  "sMountPath": "/mnt/sda1",
  "bRemovable": true,
  "bInternal": false,
  "sLabel": "MyDrive",
  "sUUID": "550e8400-...",
  "sType": "ext4",
  "bSelected": true,
  "bEnabled": true,
  "bSyncing": false,
  "bWriting": false,
  "bRotating": false,
  "eState": 8,
  "sState": "READY",
  "iStatsSizeBytes": 1000000000,
  "iStatsFreeBytes": 500000000,
  "iQuotaMinimumRecommendBytes": 200000000,
  "iQuotaPreservedBytes": 0,
  "iQuotaUsedBytes": 10000000,
  "iQuotaLimitBytes": 100000000,
  "bQuotaRotate": true
}
```

**State hierarchy:**

| eState | sState | Description |
|--------|--------|-------------|
| 1 | ERROR | Device error |
| 2 | NOT_FORMATTED_OR_FORMAT_UNSUPPORTED | Needs formatting |
| 3 | FORMATTING | Format in progress |
| 4 | NOT_MOUNTED | Not mounted |
| 5 | MOUNTED | Mounted |
| 6 | CONFIGURED | Configured (minimum for RELAY) |
| 7 | INDEXING | Building index |
| 8 | READY | Ready for use |

Also returns `sDataDirName` (e.g. `"DCIM"`) — the directory that may be overwritten on enable.

---

### POST `.../record/storage/control` — Storage Control

```json
{
  "sAction": "FORMAT|FREE_UP|EJECT|CONFIG|RELAY|RELAY_STATUS|UNRELAY|REMOVE_FILES_OR_DIRECTORIES",
  "sSlotDevPath": "/dev/sda1",
  "dSlotConfig": {
    "iQuotaLimitBytes": 1073741824,
    "bQuotaRotate": true
  },
  "lFilesOrDirectoriesToRemove": [
    "2025-10-16/2025-10-16 11-23-21 12345.mp4"
  ]
}
```

| Action | Description | Required State |
|--------|-------------|----------------|
| FORMAT | Format the storage device | Any |
| FREE_UP | Free up space | >= CONFIGURED |
| EJECT | Safely eject device | Any |
| CONFIG | Set quota and rotation | >= CONFIGURED |
| RELAY | Create temporary file access symlink | >= CONFIGURED |
| RELAY_STATUS | Query relay status | — |
| UNRELAY | Close relay | — |
| REMOVE_FILES_OR_DIRECTORIES | Delete specific files | >= CONFIGURED |

`dSlotConfig` only for CONFIG action. `iQuotaLimitBytes: -1` = unlimited.

RELAY response includes:

```json
{
  "dRelayStatus": {
    "iRelayTimeoutRemain": 300,
    "iRelayTimeout": 300,
    "sRelayDirectory": "550e8400-..."
  }
}
```

---

## 7. File Access (Relay)

### GET `/storage/relay/{uuid}/` — List Directory

**Note:** Does NOT go through CGI. Served by Nginx autoindex.

Response (JSON array):

```json
[
  {
    "name": "2025-10-16",
    "type": "directory",
    "mtime": "Tue, 02 Dec 2025 03:31:20 GMT"
  }
]
```

`type`: `"directory"`, `"file"`, `"other"`

### GET `/storage/relay/{uuid}/{path}` — Download File

Returns binary stream with appropriate Content-Type (`video/mp4`, `image/jpeg`, etc.).

Supports `Range` header for partial content (HTTP 206).

**Video thumbnails:** `/path/to/.thumb/video.mp4.thumb.jpg` — pre-generated, may not exist (implement fallback).

---

## 8. AI Model & Inference

### GET `/model/list` — List Models

Response array:

```json
[
  {
    "model": "yolov5.rknn",
    "modelInfo": {
      "name": "yolov5",
      "framework": "rknn",
      "version": "1.0.0",
      "category": "Object Detection",
      "algorithm": "YOLOV5",
      "description": "xxx",
      "classes": ["person", "xxx"],
      "metrics": {
        "iou": 60,
        "confidence": 60,
        "topk": 100
      },
      "author": "Seeed Studio",
      "size": 1110,
      "md5sum": "b3312af49a5d59a2533c973695a2267a"
    }
  }
]
```

`modelInfo` is empty `{}` when no info JSON exists.

Model files location: `/userdata/config/model/rknn/` and `/userdata/config/model/rkllm/`

---

### POST `/model/upload` — Upload Model (Resumable)

**Step 1: Init** `POST ?upload-type=resumable`
- Content-Type: text/plain, content-length: 0
- Response header: `File-Id: 123`

**Step 2: Upload chunks** `POST ?id=123`
- Content-Range: `bytes start-end`
- Body: binary model data

**Step 3: Finalize** `POST ?start=123&File-name=yolov5.rknn&md5sum=<hash>`

---

### DELETE `/model/delete` — Delete Model

**Query param:** `File-name=yolov5.rknn`

---

### GET `/model/info` — Get Model Info

**Query param:** `File-name=yolov5.rknn`

Returns the model info JSON structure.

### POST `/model/info` — Set Model Info

**Query param:** `File-name=yolov5.rknn`

Body: full model info JSON. **Must upload model file first, then configure info.**

---

### GET `/model/algorithm` — Supported Algorithms

```json
{
  "lDetection": ["yolov5", "yolov8"],
  "lClassification": ["yolov5", "yolov8"],
  "lSegmentation": [],
  "lTracking": [],
  "lKeypoint": []
}
```

---

### GET `/model/inference?id=0` — Inference Status

```json
{
  "iEnable": 1,
  "sStatus": "running",
  "sModel": "yolov5.rknn",
  "iFPS": 30
}
```

`sStatus`: `"starting"`, `"running"`, `"stopping"`, `"stopped"`, `"error"`

### POST `/model/inference?id=0` — Configure Inference

```json
{
  "iEnable": 1,
  "sModel": "yolov5.rknn",
  "iFPS": 30
}
```

Model must have associated model info JSON to enable.

---

### GET/POST `/notify/cfg` — Inference Output Config

```json
{
  "iMode": 1,
  "dTemplate": {
    "sDetection": "{timestamp}: detected {class} confidence {confidence} at ({x1},{y1},{x2},{y2})",
    "sClassification": "",
    "sSegmentation": "",
    "sTracking": "",
    "sKeypoint": "",
    "sOBB": ""
  },
  "dMqtt": {
    "sURL": "mqtt.example.com",
    "iPort": 1883,
    "sTopic": "results/data",
    "sUsername": "name",
    "sPassword": "root",
    "sClientId": "test"
  },
  "dUart": {
    "sPort": "/dev/ttyS0"
  },
  "dHttp": {
    "sUrl": "http://192.168.1.111/results/data",
    "sToken": "admin xxx"
  }
}
```

`iMode`: 0=off, 1=MQTT, 2=HTTP, 3=UART

---

## 9. WebSocket Endpoints

### `/ws/inference/results` — Inference Results Stream

Real-time inference output. Example message:

```
2024-01-15 14:30:25: 检测到 person 置信度 0.85 位置 (120,80,250,300)
```

### `/ws/system/terminal` — Terminal

Backend: ttyd. Frontend: Xterm.js.

### `/ws/system/logs` — System Logs

Initial connection sends array:

```json
[
  {
    "sTimestamp": "13212146584",
    "sLevel": "INFO",
    "sData": "System started"
  }
]
```

Subsequent updates sent as individual objects.

---

## 10. SenseCraft AI Cloud API

Base URLs:
- **Production:** `https://sensecraft-train-api.seeed.cc`
- **Test:** `https://test-sensecraft-train-api.seeed.cc`

### Authentication Flow

1. Redirect user to:
   ```
   https://sensecraft.seeed.cc/ai/authorize?client_id=seeed_recamera&response_type=token&scop=profile&redirec_url={encoded_callback_url}
   ```
2. Receive `token` and `refresh_token` from callback
3. Backend resolves `user_id`:
   ```
   POST https://sensecraft-hmi-api.seeed.cc/api/v1/user/login_token
   Header: Authorization: {token}
   ```
4. Token lifecycle: `token` expires → use `refresh_token` to renew → `refresh_token` expires → re-login

---

### POST `/v1/api/create_task` — Create ONNX-to-RKNN Conversion

Content-Type: `multipart/form-data`

| Parameter | Type | Required | Value |
|-----------|------|----------|-------|
| `user_id` | string | Yes | From auth flow |
| `framework_type` | int | Yes | Fixed: `9` (RKNN) |
| `device_type` | int | Yes | Fixed: `40` (reCamera) |
| `file` | binary | Yes | `.onnx` file |
| `dataset_file` | binary | No | ZIP of calibration images |
| `prompt` | string | No | Original filename for reference |

If `dataset_file` omitted: default COCO dataset (100 images) used for quantization.

Response:

```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "model_id": "54305aef-...",
    "created_at": "",
    "model_size": null
  }
}
```

---

### GET `/v1/api/get_training_records` — List User Models

| Parameter | Type | Value |
|-----------|------|-------|
| `user_id` | string | Required |
| `framework_type` | int | `9` |
| `device_type` | int | `40` |
| `page` | int | Page number |
| `size` | int | Items per page |

Response includes `total`, `records[]`, and `undone[]`.

Record fields: `model_id`, `status`, `progress` (0–100), `error_message`, `model_size` (bytes string), `started_at`/`finished_at`/`created_at` (Unix ms timestamps).

---

### GET `/v1/api/train_status` — Check Task Status

| Parameter | Type |
|-----------|------|
| `user_id` | string |
| `model_id` | string |

Status values: `"init"` → numeric (in progress) → `"done"` / `"error"`

**Polling:** 2s interval. Download only when `status === "done"`.

---

### GET `/v1/api/get_model` — Download Model (v1)

Returns binary `.rknn` file. Response header: `x-model-md5: {hash}`. Save as `{model_id}.rknn`.

### GET `/v2/api/get_model` — Download Model (v2)

Returns JSON with `download_url`, `md5`, `model_size`, `download_filename`. Use `download_url` to fetch binary.

---

### GET `/v1/api/del_model` — Delete Cloud Model

| Parameter | Type |
|-----------|------|
| `user_id` | string |
| `model_id` | string |

Response: `{"code": 0, "msg": "del ok", "data": {"model_id": "..."}}`
