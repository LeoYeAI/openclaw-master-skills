---
name: mikrotik-api
description: "Manages MikroTik routers via the RouterOS API (port 8728/8729). Use when the user wants to configure, monitor, or troubleshoot a MikroTik router — including interfaces, firewall, DHCP, DNS, routing, queues, VPN, and system management."
---

# MikroTik API Management

Communicate with MikroTik RouterOS devices using the Python `routeros-api` library over the API port (8728 plain, 8729 SSL).

## Prerequisites

Install the library if not present:
```bash
pip3 install --break-system-packages routeros-api
```

## Connection

It is highly recommended to use environment variables for credentials to avoid hardcoding.

### Environment Variables
Set these in your environment or `.env` file:
- `MIKROTIK_HOST`: Router IP or hostname
- `MIKROTIK_USERNAME`: Router username
- `MIKROTIK_PASSWORD`: Router password

### Python Connection Pattern
```python
import routeros_api
import os

# Get credentials from environment variables
host = os.getenv('MIKROTIK_HOST')
username = os.getenv('MIKROTIK_USERNAME')
password = os.getenv('MIKROTIK_PASSWORD')

# Fallback to manual input if env vars are missing
if not all([host, username, password]):
    print("Environment variables MIKROTIK_HOST, MIKROTIK_USERNAME, or MIKROTIK_PASSWORD are not set.")
    # host = input("Enter Host: ") ...

conn = routeros_api.RouterOsApiPool(
    host=host,
    username=username,
    password=password,
    plaintext_login=True,   # Required for RouterOS 6.43+
    port=8728               # Use 8729 for SSL
)
api = conn.get_api()
# ... do work ...
conn.disconnect()
```

### Connection Rules
- **Prefer Environment Variables**: Instruct the user to set `MIKROTIK_HOST`, `MIKROTIK_USERNAME`, and `MIKROTIK_PASSWORD`.
- Ask the user for these details only if not found in the environment.
- Default API port is **8728** (plain) or **8729** (SSL).
- Always call `conn.disconnect()` when done.
- Use `plaintext_login=True` for RouterOS v6.43+ and v7.x.

### SSL Connection
```python
conn = routeros_api.RouterOsApiPool(
    host=host,
    username=username,
    password=password,
    plaintext_login=True,
    use_ssl=True,
    ssl_verify=False,       # Set True with proper certs
    ssl_verify_hostname=False,
    port=8729
)
```

## Core API Operations

### Reading resources (GET / print)
```python
resource = api.get_resource('/ip/address')
items = resource.get()                          # Get all
items = resource.get(interface='ether1')         # Filter by param
items = resource.get(disabled='false')           # Filter by status
```

### Adding entries (ADD)
```python
resource = api.get_resource('/ip/address')
resource.add(address='192.168.1.1/24', interface='ether1')
# With comment
resource.add(address='192.168.1.1/24', interface='ether1', comment='Management')
```

### Updating entries (SET)
```python
resource = api.get_resource('/ip/address')
resource.set(id='*1', address='192.168.2.1/24')
resource.set(id='*1', comment='Updated via API')
resource.set(id='*1', disabled='yes')           # Disable entry
resource.set(id='*1', disabled='no')            # Enable entry
```

### Removing entries (REMOVE)
```python\nresource = api.get_resource('/ip/address')
resource.remove(id='*1')
```

### Calling commands (CALL)
```python
resource = api.get_resource('/system')
resource.call('reboot')

# Call with parameters
resource = api.get_resource('/ip/firewall/filter')
resource.call('move', {'numbers': '*1', 'destination': '*5'})
```

### Enabling / Disabling entries
```python
resource = api.get_resource('/interface')
resource.set(id='*1', disabled='yes')   # Disable
resource.set(id='*1', disabled='no')    # Enable
```

## Complete Resource Path Reference

### System
| Task | Resource Path |
|------|--------------|
| System info (CPU, RAM, uptime) | `/system/resource` |
| Router identity | `/system/identity` |
| System clock | `/system/clock` |
| NTP client | `/system/ntp/client` |
| NTP server | `/system/ntp/server` |
| Scheduler | `/system/scheduler` |
| Scripts | `/system/script` |
| Logging rules | `/system/logging` |
| Log entries | `/log` |
| Packages | `/system/package` |
| Package update | `/system/package/update` |
| Router board info | `/system/routerboard` |
| License | `/system/license` |
| Health (voltage, temp) | `/system/health` |
| History | `/system/history` |
| Users | `/user` |
| User groups | `/user/group` |
| Active users | `/user/active` |
| SSH keys | `/user/ssh-keys` |
| Files | `/file` |
| Backup | `/system/backup` |
| SNMP | `/snmp` |
| SNMP community | `/snmp/community` |
| Certificates | `/certificate` |
| Console | `/system/console` |
| LEDs | `/system/leds` |

### Interfaces
| Task | Resource Path |
|------|--------------|
| All interfaces | `/interface` |
| Ethernet | `/interface/ethernet` |
| Bridge | `/interface/bridge` |
| Bridge ports | `/interface/bridge/port` |
| Bridge VLANs | `/interface/bridge/vlan` |
| Bridge hosts (MAC table) | `/interface/bridge/host` |
| Bridge MSTi | `/interface/bridge/msti` |
| Bridge settings | `/interface/bridge/settings` |
| VLAN | `/interface/vlan` |
| Bonding (LACP/bonding) | `/interface/bonding` |
| EoIP tunnel | `/interface/eoip` |
| GRE tunnel | `/interface/gre` |
| IPIP tunnel | `/interface/ipip` |
| VXLAN | `/interface/vxlan` |
| VXLAN VTEP | `/interface/vxlan/vtep` |
| WireGuard | `/interface/wireguard` |
| WireGuard peers | `/interface/wireguard/peers` |
| L2TP client | `/interface/l2tp-client` |
| L2TP server | `/interface/l2tp-server/server` |
| SSTP client | `/interface/sstp-client` |
| SSTP server | `/interface/sstp-server/server` |
| OVPN client | `/interface/ovpn-client` |
| OVPN server | `/interface/ovpn-server/server` |
| PPPoE client | `/interface/pppoe-client` |
| PPPoE server | `/interface/pppoe-server/server` |
| PPTP client | `/interface/pptp-client` |
| PPTP server | `/interface/pptp-server/server` |
| LTE | `/interface/lte` |
| LTE APN | `/interface/lte/apn` |
| Wireless (WiFi legacy) | `/interface/wireless` |
| WiFi (new, ROS 7) | `/interface/wifi` |
| WiFi channels | `/interface/wifi/channel` |
| WiFi datapath | `/interface/wifi/datapath` |
| WiFi security | `/interface/wifi/security` |
| WiFi configuration | `/interface/wifi/configuration` |
| WiFi provisioning | `/interface/wifi/provisioning` |
| WiFi registration table | `/interface/wifi/registration-table` |
| WiFi access list | `/interface/wifi/access-list` |
| WiFi interworking | `/interface/wifi/interworking` |
| Interface lists | `/interface/list` |
| Interface list members | `/interface/list/member` |
| Ethernet switch | `/interface/ethernet/switch` |
| Ethernet switch port | `/interface/ethernet/switch/port` |
| Traffic monitor | `/interface/monitor-traffic` |

### IP
| Task | Resource Path |
|------|--------------|
| IP addresses | `/ip/address` |
| ARP table | `/ip/arp` |
| Routes | `/ip/route` |
| Route rules | `/ip/route/rule` |
| DNS settings | `/ip/dns` |
| DNS static entries | `/ip/dns/static` |
| DNS cache | `/ip/dns/cache` |
| DHCP client | `/ip/dhcp-client` |
| DHCP server | `/ip/dhcp-server` |
| DHCP server network | `/ip/dhcp-server/network` |
| DHCP server leases | `/ip/dhcp-server/lease` |
| DHCP server option | `/ip/dhcp-server/option` |
| DHCP server option sets | `/ip/dhcp-server/option/sets` |
| DHCP relay | `/ip/dhcp-relay` |
| IP pool | `/ip/pool` |
| IP neighbors | `/ip/neighbor` |
| IP neighbor discovery | `/ip/neighbor/discovery-settings` |
| IP services | `/ip/service` |
| IP settings (forwarding) | `/ip/settings` |
| IP proxy | `/ip/proxy` |
| IP proxy access list | `/ip/proxy/access` |
| IP SOCKS | `/ip/socks` |
| IP SSH | `/ip/ssh` |
| IP cloud | `/ip/cloud` |
| IP UPnP | `/ip/upnp` |
| IP UPnP interfaces | `/ip/upnp/interfaces` |
| IP SMB | `/ip/smb` |
| IP traffic flow | `/ip/traffic-flow` |
| IP traffic flow target | `/ip/traffic-flow/target` |
| IP accounting | `/ip/accounting` |
| IP Kid Control | `/ip/kid-control` |
| IP Kid Control devices | `/ip/kid-control/device` |
| IP Hotspot | `/ip/hotspot` |
| IP Hotspot profile | `/ip/hotspot/profile` |
| IP Hotspot user | `/ip/hotspot/user` |
| IP Hotspot user profile | `/ip/hotspot/user/profile` |
| IP Hotspot active | `/ip/hotspot/active` |
| IP Hotspot host | `/ip/hotspot/host` |
| IP Hotspot cookie | `/ip/hotspot/cookie` |
| IP Hotspot IP binding | `/ip/hotspot/ip-binding` |
| IP Hotspot walled garden | `/ip/hotspot/walled-garden` |
| IP Hotspot walled garden IP | `/ip/hotspot/walled-garden/ip` |

### Firewall
| Task | Resource Path |
|------|--------------|
| Filter rules | `/ip/firewall/filter` |
| NAT rules | `/ip/firewall/nat` |
| Mangle rules | `/ip/firewall/mangle` |
| RAW rules | `/ip/firewall/raw` |
| Address lists | `/ip/firewall/address-list` |
| Connections (conntrack) | `/ip/firewall/connection` |
| Connection tracking | `/ip/firewall/connection/tracking` |
| Service ports (ALGs) | `/ip/firewall/service-port` |
| Layer 7 protocols | `/ip/firewall/layer7-protocol` |

### IPv6
| Task | Resource Path |
|------|--------------|
| IPv6 addresses | `/ipv6/address` |
| IPv6 routes | `/ipv6/route` |
| IPv6 firewall filter | `/ipv6/firewall/filter` |
| IPv6 firewall mangle | `/ipv6/firewall/mangle` |
| IPv6 firewall RAW | `/ipv6/firewall/raw` |
| IPv6 firewall address list | `/ipv6/firewall/address-list` |
| IPv6 ND (Neighbor Disc.) | `/ipv6/nd` |
| IPv6 ND prefix | `/ipv6/nd/prefix` |
| IPv6 DHCP client | `/ipv6/dhcp-client` |
| IPv6 DHCP server | `/ipv6/dhcp-server` |
| IPv6 pool | `/ipv6/pool` |
| IPv6 settings | `/ipv6/settings` |

### Routing (RouterOS 7)
| Task | Resource Path |
|------|--------------|
| Routing tables | `/routing/table` |
| Routing rules | `/routing/rule` |
| OSPF instance | `/routing/ospf/instance` |
| OSPF area | `/routing/ospf/area` |
| OSPF interface template | `/routing/ospf/interface-template` |
| OSPF neighbors | `/routing/ospf/neighbor` |
| OSPF LSA | `/routing/ospf/lsa` |
| BGP connection | `/routing/bgp/connection` |
| BGP template | `/routing/bgp/template` |
| BGP session | `/routing/bgp/session` |
| BGP advertisements | `/routing/bgp/advertisements` |
| BGP networks | `/routing/bgp/network` |
| RIP instance | `/routing/rip/instance` |
| RIP interface template | `/routing/rip/interface-template` |
| Route filter rules | `/routing/filter/rule` |
| Route filter select rules | `/routing/filter/select-rule` |
| Prefix lists | `/routing/filter/community-list` |
| BFD session | `/routing/bfd/session` |
| BFD configuration | `/routing/bfd/configuration` |
| Routing ID | `/routing/id` |
| RPKI | `/routing/rpki` |
| IGMP Proxy | `/routing/igmp-proxy` |
| PIM | `/routing/pimsm` |

### PPP
| Task | Resource Path |
|------|--------------|
| PPP secrets | `/ppp/secret` |
| PPP profiles | `/ppp/profile` |
| PPP active connections | `/ppp/active` |
| PPP AAA settings | `/ppp/aaa` |
| PPP L2TP secret | `/ppp/l2tp-secret` |

### Queues (QoS)
| Task | Resource Path |
|------|--------------|
| Simple queues | `/queue/simple` |
| Queue tree | `/queue/tree` |
| Queue types | `/queue/type` |
| Interface queues | `/queue/interface` |

### CAPsMAN / WiFi Controller (ROS 7)
| Task | Resource Path |
|------|--------------|
| CAPsMAN manager | `/caps-man/manager` |
| CAPsMAN configuration | `/caps-man/configuration` |
| CAPsMAN channel | `/caps-man/channel` |
| CAPsMAN datapath | `/caps-man/datapath` |
| CAPsMAN security | `/caps-man/security` |
| CAPsMAN provisioning | `/caps-man/provisioning` |
| CAPsMAN interface | `/caps-man/interface` |
| CAPsMAN registration table | `/caps-man/registration-table` |
| CAPsMAN access list | `/caps-man/access-list` |
| CAPsMAN remote-cap | `/caps-man/remote-cap` |

### MPLS
| Task | Resource Path |
|------|--------------|
| MPLS settings | `/mpls` |
| MPLS interface | `/mpls/interface` |
| MPLS forwarding table | `/mpls/forwarding-table` |
| MPLS LDP | `/mpls/ldp` |
| MPLS LDP interface | `/mpls/ldp/interface` |
| MPLS LDP neighbor | `/mpls/ldp/neighbor` |
| VPLS | `/interface/vpls` |
| Traffic engineering | `/mpls/traffic-eng` |

### Tools
| Task | Resource Path |
|------|--------------|
| Ping | `/tool/ping` (use `call`) |
| Traceroute | `/tool/traceroute` (use `call`) |
| Bandwidth test | `/tool/bandwidth-test` (use `call`) |
| Torch (traffic by IP) | `/tool/torch` (use `call`) |
| Profile (CPU profile) | `/tool/profile` |
| Netwatch | `/tool/netwatch` |
| E-mail settings | `/tool/e-mail` |
| Fetch (HTTP client) | `/tool/fetch` |
| Graphing interface | `/tool/graphing/interface` |
| Graphing resource | `/tool/graphing/resource` |
| Graphing queue | `/tool/graphing/queue` |
| Sniffer | `/tool/sniffer` |
| SNMP | `/snmp` |
| MAC server | `/tool/mac-server` |
| MAC Winbox | `/tool/mac-server/mac-winbox` |
| MAC Ping | `/tool/mac-server/ping` |
| Bandwidth server | `/tool/bandwidth-server` |
| IP Scan | `/tool/ip-scan` |
| SMS | `/tool/sms` |
| Romon | `/tool/romon` |

### Container (ROS 7.4+)
| Task | Resource Path |
|------|--------------|
| Container config | `/container/config` |
| Containers | `/container` |
| Container mounts | `/container/mounts` |
| Container envs | `/container/envs` |

### IoT
| Task | Resource Path |
|------|--------------|
| IoT Bluetooth | `/iot/bluetooth` |
| IoT Bluetooth scanners | `/iot/bluetooth/scanners` |
| IoT GPIO | `/iot/gpio` |
| IoT MQTT broker | `/iot/mqtt/brokers` |

### ZeroTier
| Task | Resource Path |
|------|--------------|
| ZeroTier | `/zerotier` |
| ZeroTier interface | `/zerotier/interface` |

## Advanced Operations

### Filtering with multiple parameters
```python
resource = api.get_resource('/ip/firewall/filter')
rules = resource.get(chain='forward', action='drop')
```

### Ordering firewall rules (place-before)
```python
resource = api.get_resource('/ip/firewall/filter')
resource.add(
    chain='forward',
    action='accept',
    src_address='10.0.0.0/8',
    place_before='*5'       # Insert before rule *5
)
```
Note: Use underscores in Python for hyphenated attributes (e.g., `src-address` → `src_address`, `place-before` → `place_before`).

### Moving firewall rules
```python
resource = api.get_resource('/ip/firewall/filter')
resource.call('move', {'numbers': '*A', 'destination': '*1'})
```

### Batch operations
```python
resource = api.get_resource('/ip/firewall/address-list')
ips = ['1.2.3.4', '5.6.7.8', '9.10.11.12']
for ip in ips:
    resource.add(list='blocklist', address=ip, comment='Blocked via API')
```

### Enable/disable by name
```python
resource = api.get_resource('/interface')
ifaces = resource.get(name='ether5')
if ifaces:
    resource.set(id=ifaces[0]['id'], disabled='yes')
```

### Get specific properties only
```python
# The library always returns all properties; filter in Python:
resource = api.get_resource('/interface')
for iface in resource.get():
    print(iface.get('name'), iface.get('type'), iface.get('running'))
```

### Run system tools (ping, traceroute)
```python
# Tools that produce output need call() with parameters
resource = api.get_resource('/tool')
# Note: Some tools (ping, traceroute) run indefinitely.
# Use count parameter to limit.
result = resource.call('ping', {'address': '8.8.8.8', 'count': '4'})
for r in result:
    print(r)
```

### Backup & Export
```python
# Create a backup file
resource = api.get_resource('/system/backup')
resource.call('save', {'name': 'api-backup'})

# Export config to file
resource = api.get_resource('/')
resource.call('export', {'file': 'api-export'})
```

### System reboot / shutdown
```python
resource = api.get_resource('/system')
resource.call('reboot')
# resource.call('shutdown')
```

### Firmware / Package update
```python
resource = api.get_resource('/system/package/update')
resource.call('check-for-updates')
result = resource.get()
print(result)
# resource.call('install')   # Install and reboot
```

## REST API (RouterOS 7.1+)

RouterOS 7.1+ also supports a REST API over HTTP/HTTPS. Use when the Python library is unavailable.

### REST via curl
```bash
# GET - Read resources
curl -k -u user:pass https://<IP>/rest/ip/address

# PUT - Create new entry
curl -k -u user:pass -X PUT https://<IP>/rest/ip/address \
  --data '{"address":"192.168.1.1/24","interface":"ether1"}' \
  -H "content-type: application/json"

# PATCH - Update entry
curl -k -u user:pass -X PATCH https://<IP>/rest/ip/address/*1 \
  --data '{"comment":"updated"}' -H "content-type: application/json"

# DELETE - Remove entry
curl -k -u user:pass -X DELETE https://<IP>/rest/ip/address/*1

# POST - Run any command
curl -k -u user:pass -X POST https://<IP>/rest/ip/address/print \
  --data '{"_proplist":["address","interface"]}' \
  -H "content-type: application/json"
```

### REST with query filters
```bash
curl -k -u user:pass -X POST https://<IP>/rest/interface/print \
  --data '{".query":["type=ether"],"_proplist":["name","type","running"]}' \
  -H "content-type: application/json"
```

### REST via Python requests
```python
import requests
from requests.auth import HTTPBasicAuth

base = 'https://<IP>/rest'
auth = HTTPBasicAuth('<USER>', '<PASS>')

# GET all interfaces
r = requests.get(f'{base}/interface', auth=auth, verify=False)
print(r.json())

# POST (run commands with parameters)
r = requests.post(f'{base}/ip/address/print',
    auth=auth, verify=False,
    json={'_proplist': ['address', 'interface']})
print(r.json())
```

## Error Handling

```python
import routeros_api
from routeros_api.exceptions import RouterOsApiCommunicationError

try:
    conn = routeros_api.RouterOsApiPool(host, username=user, password=pw, plaintext_login=True)
    api = conn.get_api()
    resource = api.get_resource('/ip/address')
    resource.add(address='invalid', interface='nonexistent')
except RouterOsApiCommunicationError as e:
    print(f"API Error: {e}")
except ConnectionError:
    print("Cannot reach router")
finally:
    try:
        conn.disconnect()
    except:
        pass
```

### API Error Categories
| Code | Meaning |
|------|---------|
| 0 | Missing item or command |
| 1 | Argument value failure |
| 2 | Command interrupted |
| 3 | Scripting related failure |
| 4 | General failure |
| 5 | API related failure |
| 6 | TTY related failure |
| 7 | Value from :return command |

## Workflow

1. **Connect** to the router using credentials from environment variables or the user.
2. **Read first** — always fetch current state before making changes.
3. **Confirm** destructive operations (delete, disable, reboot, firewall changes) with the user.
4. **Apply changes** using add/set/remove.
5. **Verify** by reading back the resource after changes.
6. **Disconnect** when done.

## Important Notes

- The `id` field in responses (e.g., `*1`, `*A`) is the internal MikroTik ID used for set/remove.
- Use underscore in Python kwargs for hyphenated RouterOS attributes: `src-address` → `src_address`.
- Filter and NAT rules are **order-sensitive** — use `place_before` when adding to control position.
- Always show the user what currently exists before modifying firewall rules.
- For bulk operations, iterate over results and apply changes one by one.
- RouterOS 7.x uses different paths for routing (e.g., `/routing/ospf/instance` not `/routing/ospf`).
- If the API port is closed, advise the user to enable it: `/ip/service enable api`.
- Tools like ping/traceroute run indefinitely — always pass `count` or `duration` parameter.
- REST API requires `www` or `www-ssl` service enabled on the router.
- REST API has a **60-second timeout** for commands; use limiting params (`count`, `duration`, `once`).
