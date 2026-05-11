# Subnetting-Referenztabelle (IPv4)

## CIDR → Subnetzmaske → Hosts

| CIDR | Subnetzmaske | Hosts (nutzbar) | Netze bei /24 |
|------|-------------|-----------------|---------------|
| /24 | 255.255.255.0 | 254 | 1 |
| /25 | 255.255.255.128 | 126 | 2 |
| /26 | 255.255.255.192 | 62 | 4 |
| /27 | 255.255.255.224 | 30 | 8 |
| /28 | 255.255.255.240 | 14 | 16 |
| /29 | 255.255.255.248 | 6 | 32 |
| /30 | 255.255.255.252 | 2 | 64 |
| /31 | 255.255.255.254 | 0 (P2P) | 128 |
| /32 | 255.255.255.255 | 1 (Host) | 256 |

## Berechnungsformel

- Hosts pro Subnetz: `2^(32-CIDR) - 2`
- Anzahl Subnetze: `2^(CIDR - Original-CIDR)`
- Subnetzgröße (Sprung): `256 - letztes Oktett der Maske`

## Private IP-Bereiche (RFC 1918)

| Klasse | Bereich | CIDR | Hosts |
|--------|---------|------|-------|
| A | 10.0.0.0 - 10.255.255.255 | 10.0.0.0/8 | 16.777.214 |
| B | 172.16.0.0 - 172.31.255.255 | 172.16.0.0/12 | 1.048.574 |
| C | 192.168.0.0 - 192.168.255.255 | 192.168.0.0/16 | 65.534 |
