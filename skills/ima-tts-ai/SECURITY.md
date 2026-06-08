# Security Disclosure: ima-tts-ai

## Purpose

This document explains endpoint usage, credential flow, and local data behavior for `ima-tts-ai`.

## Network Endpoints

| Domain | Used For | Trigger |
|---|---|---|
| `api.imastudio.com` | Product list, task create, task detail polling | All requests |

This skill does **not** use a secondary upload domain.

## Credential Flow

| Credential | Where Sent | Why |
|---|---|---|
| `IMA_API_KEY` | `api.imastudio.com` | Open API auth (`Authorization: Bearer ...`) |

No credential is sent to other domains in this skill.

## Model Scope

This skill targets TTS with `seed-tts-2.0` default behavior and text-to-speech category only.

## Local Data

| Path | Content | Retention |
|---|---|---|
| `~/.openclaw/memory/ima_prefs.json` | Per-user model preference cache | Until manually removed |
| `~/.openclaw/logs/ima_skills/` | Operational logs | Auto-cleaned by script after 7 days |

No API key is written into repository files.
