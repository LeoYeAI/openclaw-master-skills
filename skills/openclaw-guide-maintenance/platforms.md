# OpenClaw Platforms Reference

## Table of Contents

- [Overview](#overview)
- [macOS](#macos)
- [iOS](#ios)
- [Android](#android)
- [Windows](#windows)
- [Linux](#linux)
- [VPS & Hosting](#vps--hosting)
- [Gateway Service Install](#gateway-service-install)

## Overview

OpenClaw runs on macOS, Linux, and Windows. Companion apps are available for iOS and Android as nodes.

| Platform | Gateway | Node | CLI |
|---|---|---|---|
| macOS | ✅ | ✅ (menu bar + headless) | ✅ |
| Linux | ✅ | ✅ (headless) | ✅ |
| Windows (WSL2) | ✅ | ✅ (headless) | ✅ |
| iOS | — | ✅ (app) | — |
| Android | — | ✅ (app) | — |

## macOS

- **macOS App**: Menu bar app with built-in Gateway management
- **CLI**: Full command-line interface
- **Node**: Both menu bar app mode and headless node host
- **Service**: LaunchAgent (`ai.openclaw.gateway` or `ai.openclaw.<profile>`)
- Legacy service label: `com.openclaw.*`

See: https://docs.openclaw.ai/platforms/macos

## iOS

iOS node app with:
- Device pairing with Gateway
- Canvas support (A2UI)
- Camera (snap + clip)
- Screen recording
- Location sharing
- Voice features
- Connect tab for session management

See: https://docs.openclaw.ai/platforms/ios

## Android

Android node app with:
- Device pairing + Connect tab
- Chat sessions
- Voice tab
- Canvas / camera / screen
- Device commands (notifications, contacts/calendar, motion, photos, SMS, app updates)

See: https://docs.openclaw.ai/platforms/android

## Windows

- Runs via **WSL2** (Windows Subsystem for Linux)
- Full CLI + Gateway support within WSL2
- Native Windows PowerShell installer available

See: https://docs.openclaw.ai/platforms/windows

## Linux

- Full CLI + Gateway support
- **Service**: systemd user service (`openclaw-gateway[-<profile>].service`)
- Headless node host available

See: https://docs.openclaw.ai/platforms/linux

## VPS & Hosting

| Provider | Description |
|---|---|
| **Fly.io** | Container deployment |
| **Hetzner** | Docker-based deployment |
| **GCP** | Compute Engine deployment |
| **exe.dev** | VM + HTTPS proxy |

See VPS hub: https://docs.openclaw.ai/vps

## Gateway Service Install

### Via CLI

```bash
# Wizard (recommended)
openclaw onboard --install-daemon

# Direct install
openclaw gateway install

# Via configure flow
openclaw configure    # Select "Gateway service"

# Repair / migrate
openclaw doctor       # Offers to install or fix service
```

### Per-Platform Service Details

| Platform | Service Type | Identifier |
|---|---|---|
| macOS | LaunchAgent | `ai.openclaw.gateway` or `ai.openclaw.<profile>` |
| Linux/WSL2 | systemd user service | `openclaw-gateway[-<profile>].service` |

### Service Management

```bash
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
openclaw gateway status
```
