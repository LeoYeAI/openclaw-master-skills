# OSI-Modell — Referenz

| Nr | Schicht | Englisch | PDU | Protokolle | Geräte |
|----|---------|----------|-----|------------|--------|
| 7 | Anwendung | Application | Daten | HTTP, FTP, SMTP, DNS, DHCP, SSH | Gateway, Proxy |
| 6 | Darstellung | Presentation | Daten | SSL/TLS, JPEG, ASCII, MIME | - |
| 5 | Sitzung | Session | Daten | NetBIOS, RPC, SMB | - |
| 4 | Transport | Transport | Segment | TCP, UDP | - |
| 3 | Vermittlung | Network | Paket | IP, ICMP, ARP, OSPF, BGP | Router, L3-Switch |
| 2 | Sicherung | Data Link | Frame | Ethernet, WLAN (802.11), PPP | Switch, Bridge |
| 1 | Bitübertragung | Physical | Bits | Ethernet (physisch), DSL, ISDN | Hub, Repeater, Kabel |

## Datenkapselung (HTTPS-Aufruf)

1. **Schicht 7**: HTTP-Request (GET /index.html)
2. **Schicht 6**: TLS-Verschlüsselung
3. **Schicht 5**: TLS-Session aufbauen
4. **Schicht 4**: TCP-Segment (Quell-Port, Ziel-Port 443)
5. **Schicht 3**: IP-Paket (Quell-IP, Ziel-IP)
6. **Schicht 2**: Ethernet-Frame (Quell-MAC, Ziel-MAC)
7. **Schicht 1**: Elektrische Signale / Licht über Kabel

## TCP vs. UDP

| Eigenschaft | TCP | UDP |
|-------------|-----|-----|
| Verbindung | Verbindungsorientiert (3-Way-Handshake) | Verbindungslos |
| Zuverlässigkeit | Ja (Bestätigung, Retransmission) | Nein |
| Reihenfolge | Garantiert (Sequenznummern) | Nicht garantiert |
| Overhead | Höher (20+ Byte Header) | Niedriger (8 Byte Header) |
| Einsatz | HTTP, FTP, SSH, E-Mail | DNS, VoIP, Streaming, Gaming |
