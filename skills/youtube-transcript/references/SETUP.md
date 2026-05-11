# YouTube Transcript - Setup Guide

## Why Residential IP?

YouTube blocks cloud provider IPs (AWS, Hetzner, GCP, Azure, etc.) from accessing transcripts. Requests from these IPs get 403/429 errors or bot detection.

**Solution:** Route requests through a residential IP via WireGuard VPN to a home router.

## Prerequisites

- Python 3.x installed
- WireGuard installed on VPS
- Access to a residential network (home router with WireGuard support)

## 1. Install Python Dependencies

```bash
pip3 install youtube-transcript-api requests
```

## 2. Configure WireGuard VPN

You need a WireGuard server on a residential network (home router, NAS, etc.).

### On Your Home Router (Server)

```bash
# Generate keys
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey

# Configure interface (e.g., /etc/wireguard/wg0.conf or via LuCI/OpenWRT)
[Interface]
PrivateKey = <router_private_key>
Address = 10.100.0.1/24
ListenPort = 51820

[Peer]
PublicKey = <vps_public_key>
AllowedIPs = 10.100.0.2/32
```

Enable masquerading/NAT so the VPS can route traffic through your home IP.

### On Your VPS (Client)

```bash
# Generate keys
wg genkey | tee /etc/wireguard/privatekey | wg pubkey > /etc/wireguard/publickey

# Configure /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <vps_private_key>
Address = 10.100.0.2/24
Table = 51820

[Peer]
PublicKey = <router_public_key>
Endpoint = <your-home-ip-or-ddns>:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

### Bring Up VPN

```bash
wg-quick up wg0
ip rule add from 10.100.0.2 table 51820
```

### Verify

```bash
curl --interface 10.100.0.2 ifconfig.me  # Should show your home IP
```

## 3. Configure Script (If Needed)

Edit `scripts/fetch_transcript.py` and adjust:
```python
VPN_INTERFACE = "wg0"        # Your WireGuard interface name
VPN_SOURCE_IP = "10.100.0.2" # Your VPS's WireGuard IP
```

## Troubleshooting

| Error | Cause | Solution |
|-------|-------|----------|
| VPN not available | WireGuard down | Script auto-retries; check `wg show` |
| Transcripts disabled | Creator disabled captions | No workaround |
| No transcript found | No captions in requested languages | Try different language codes |
| RequestBlocked | VPN not routing properly | Verify `curl --interface <VPN_IP> ifconfig.me` shows residential IP |

## Alternatives to WireGuard

If you can't set up WireGuard:
- **SSH tunnel**: `ssh -D 1080 user@home-server` + configure SOCKS proxy
- **Residential proxy service**: Bright Data, Oxylabs, SmartProxy (paid)
- **Tailscale/ZeroTier**: Easier setup than raw WireGuard
