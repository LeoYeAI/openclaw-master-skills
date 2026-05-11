# Aqara Open API — curl Examples

All examples assume environment variables are set:

```bash
export AQARA_OPEN_API_TOKEN="your-bearer-token"
export AQARA_ENDPOINT_URL="https://aiot-open-3rd.aqara.cn/open/api"
```

---

## Device Management

### Load All Devices (with space info, full detail — cached to file)

This is the primary data source. Run the cache script once; subsequent device, space, and status queries read from the local file `data/devices.json`. Only re-run when the cache is missing or the user explicitly asks to refresh.

```bash
# Preferred: use the cache script (fetches API + writes data/devices.json)
bash scripts/fetch_all_devices.sh

# Manual curl (for reference only — prefer the script):
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"GetAllDevicesWithSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'"}'
```

`data/devices.json` contains all devices with full `endpoints[]`, current trait values, and `space` info. Filter locally by `deviceTypesList`, `name`, `state`, and `space.name`.

### Get All Device Types

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"GetDeviceTypeInfosRequest","version":"v1","msgId":"msg-'$(date +%s)'"}'
```

### Device Status / Trait Values

**No separate API call needed.** Current trait values are included in `data/devices.json` under each device's `endpoints[].functions[].traits[].value`.

### Control Device — Turn On

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"ExecuteTraitRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":[{"deviceId":"lumi.device.abc123","endpointId":1,"functionCode":"Output","traitCode":"OnOff","value":true}]}'
```

### Control Device — Turn Off

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"ExecuteTraitRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":[{"deviceId":"lumi.device.abc123","endpointId":1,"functionCode":"Output","traitCode":"OnOff","value":false}]}'
```

### Control Device — Set Brightness

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"ExecuteTraitRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":[{"deviceId":"lumi.device.abc123","endpointId":1,"functionCode":"LevelControl","traitCode":"CurrentLevel","value":80}]}'
```

---

## Space Management

### List Spaces

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"GetSpacesRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":null}'
```

### Create a Top-Level Space

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"CreateSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"name":"My Home"}}'
```

### Create a Sub-Space

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"CreateSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"name":"Living Room","parentSpaceId":"space_id_123","spatialMarking":"living_room"}}'
```

### Update Space

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"UpdateSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"spaceId":"space_id_123","name":"New Room Name"}}'
```

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"UpdateSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"spaceId":"space_id_123","spatialMarking":"bedroom"}}'
```

### Assign Devices to Space

```bash
curl -s -X POST "$AQARA_ENDPOINT_URL" \
  -H "Authorization: Bearer $AQARA_OPEN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"type":"AssociateDevicesToSpaceRequest","version":"v1","msgId":"msg-'$(date +%s)'","data":{"spaceId":"space_id_123","deviceIds":["lumi.device.abc123","lumi.device.def456"]}}'
```

---