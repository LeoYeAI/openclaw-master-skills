# TPN API Code Examples (API Key Authentication)

Working examples for generating a SOCKS5 proxy via `POST /api/v1/proxy/generate` and routing a request through it.

Replace `YOUR_API_KEY` with your actual TPN API key.

---

## curl

```bash
# Generate a proxy (60 min, any country)
RESPONSE=$(curl -s -X POST https://api.taoprivatenetwork.com/api/v1/proxy/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"minutes": 60, "format": "json", "connection_type": "any"}')

# Parse credentials with jq
USERNAME=$(echo "$RESPONSE" | jq -r '.vpnConfig.username')
PASSWORD=$(echo "$RESPONSE" | jq -r '.vpnConfig.password')
HOST=$(echo "$RESPONSE" | jq -r '.vpnConfig.ip_address')
PORT=$(echo "$RESPONSE" | jq -r '.vpnConfig.port')
EXPIRES=$(echo "$RESPONSE" | jq -r '.expiresAt')

echo "Proxy: socks5h://$USERNAME:$PASSWORD@$HOST:$PORT"
echo "Expires: $EXPIRES"

# Route a request through the proxy
curl --proxy "socks5h://$USERNAME:$PASSWORD@$HOST:$PORT" \
  --connect-timeout 10 --max-time 30 \
  https://ipv4.icanhazip.com
```

---

## Browser JavaScript (fetch)

```js
// Generate a SOCKS5 proxy via the TPN API
const response = await fetch( 'https://api.taoprivatenetwork.com/api/v1/proxy/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': 'YOUR_API_KEY'
    },
    body: JSON.stringify( { minutes: 60, format: 'json', connection_type: 'any' } )
} )

const data = await response.json()
const { username, password, ip_address, port } = data.vpnConfig

console.log( `Proxy: socks5h://${ username }:${ password }@${ ip_address }:${ port }` )
console.log( `Expires: ${ data.expiresAt }` )

// Note: browsers cannot use SOCKS5 proxies directly in fetch.
// Use the proxy URI in a backend service, browser extension, or system proxy settings.
```

---

## Node.js (node-fetch + socks-proxy-agent)

```bash
npm install node-fetch socks-proxy-agent
```

```js
import fetch from 'node-fetch'
import { SocksProxyAgent } from 'socks-proxy-agent'

const api_key = 'YOUR_API_KEY'

// Generate a SOCKS5 proxy
const proxy_response = await fetch( 'https://api.taoprivatenetwork.com/api/v1/proxy/generate', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    },
    body: JSON.stringify( { minutes: 60, format: 'json', connection_type: 'any' } )
} )

const proxy_data = await proxy_response.json()
const { username, password, ip_address, port } = proxy_data.vpnConfig

// Build the socks5h URI (h = DNS through proxy)
const proxy_uri = `socks5h://${ username }:${ password }@${ ip_address }:${ port }`
console.log( `Proxy: ${ proxy_uri }` )
console.log( `Expires: ${ proxy_data.expiresAt }` )

// Route a request through the proxy
const agent = new SocksProxyAgent( proxy_uri )
const result = await fetch( 'https://ipv4.icanhazip.com', {
    agent,
    signal: AbortSignal.timeout( 30_000 )
} )

const exit_ip = await result.text()
console.log( `Exit IP: ${ exit_ip.trim() }` )
```

---

## Python (requests + PySocks)

```bash
pip install requests pysocks
```

```python
import requests

api_key = "YOUR_API_KEY"

# Generate a SOCKS5 proxy
proxy_response = requests.post(
    "https://api.taoprivatenetwork.com/api/v1/proxy/generate",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    },
    json={"minutes": 60, "format": "json", "connection_type": "any"},
)

proxy_data = proxy_response.json()
vpn = proxy_data["vpnConfig"]
username = vpn["username"]
password = vpn["password"]
host = vpn["ip_address"]
port = vpn["port"]

proxy_uri = f"socks5h://{username}:{password}@{host}:{port}"
print(f"Proxy: {proxy_uri}")
print(f"Expires: {proxy_data['expiresAt']}")

# Route a request through the proxy
proxies = {
    "http": proxy_uri,
    "https": proxy_uri,
}

result = requests.get(
    "https://ipv4.icanhazip.com",
    proxies=proxies,
    timeout=(10, 30),
)

print(f"Exit IP: {result.text.strip()}")
```
