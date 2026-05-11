# Webhooks — HA → Agent Communication

This guide covers setting up bidirectional communication where Home Assistant sends
events to your AI agent via webhooks.

## Overview

While the REST API enables **Agent → HA** communication (controlling devices), webhooks
enable **HA → Agent** communication (reacting to events). This allows your agent to:

- Receive motion alerts and respond
- Get notified when doors/windows open
- React to automation triggers
- Process sensor threshold alerts

## Setup

### 1. Define REST Commands in HA

Add to your `configuration.yaml`:

```yaml
rest_command:
  notify_agent:
    url: "https://your-agent-url/webhook/home-assistant"
    method: POST
    headers:
      Authorization: "Bearer YOUR_WEBHOOK_SECRET"
      Content-Type: "application/json"
    payload: >-
      {
        "event": "{{ event }}",
        "entity": "{{ entity }}",
        "area": "{{ area }}",
        "state": "{{ state }}",
        "timestamp": "{{ now().isoformat() }}"
      }
```

### 2. Create Automations That Trigger Webhooks

```yaml
# Motion detected
- alias: "Agent: Motion Alert"
  trigger:
    - platform: state
      entity_id: binary_sensor.motion_hallway
      to: "on"
  action:
    - service: rest_command.notify_agent
      data:
        event: motion_detected
        entity: binary_sensor.motion_hallway
        area: hallway
        state: "on"

# Door opened
- alias: "Agent: Door Alert"
  trigger:
    - platform: state
      entity_id: binary_sensor.front_door
      to: "on"
  action:
    - service: rest_command.notify_agent
      data:
        event: door_opened
        entity: binary_sensor.front_door
        area: entrance
        state: "open"

# Temperature threshold
- alias: "Agent: Temperature Alert"
  trigger:
    - platform: numeric_state
      entity_id: sensor.living_room_temperature
      above: 30
  action:
    - service: rest_command.notify_agent
      data:
        event: temperature_high
        entity: sensor.living_room_temperature
        area: living_room
        state: "{{ states('sensor.living_room_temperature') }}"
```

### 3. Webhook Payload Format

The agent receives a JSON payload like:

```json
{
  "event": "motion_detected",
  "entity": "binary_sensor.motion_hallway",
  "area": "hallway",
  "state": "on",
  "timestamp": "2025-01-15T10:30:00+00:00"
}
```

## Security

- Use HTTPS for the webhook URL
- Include an Authorization header with a secret token
- Validate the token on the agent side before processing
- Consider IP whitelisting if your HA instance has a static IP

## Troubleshooting

- **Webhook not firing**: Check HA automations log for errors
- **Connection refused**: Ensure the agent URL is reachable from HA's network
- **Timeout**: HA has a 10-second timeout for REST commands by default
- **SSL errors**: Add `verify_ssl: false` to rest_command if using self-signed certs
