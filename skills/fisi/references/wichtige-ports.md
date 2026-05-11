# Wichtige Ports — Referenz

## Standard-Ports (Prüfungsrelevant)

| Port | Protokoll | Dienst | Transport |
|------|-----------|--------|-----------|
| 20 | FTP-Data | Datentransfer | TCP |
| 21 | FTP | Steuerung | TCP |
| 22 | SSH | Secure Shell | TCP |
| 23 | Telnet | Remote Login (unsicher) | TCP |
| 25 | SMTP | E-Mail Versand | TCP |
| 53 | DNS | Namensauflösung | TCP/UDP |
| 67/68 | DHCP | IP-Vergabe | UDP |
| 80 | HTTP | Webserver | TCP |
| 110 | POP3 | E-Mail Abruf | TCP |
| 143 | IMAP | E-Mail Abruf | TCP |
| 443 | HTTPS | Webserver (verschlüsselt) | TCP |
| 445 | SMB | Dateifreigabe (Windows) | TCP |
| 587 | SMTP | E-Mail Submission | TCP |
| 993 | IMAPS | IMAP verschlüsselt | TCP |
| 995 | POP3S | POP3 verschlüsselt | TCP |
| 3306 | MySQL | Datenbank | TCP |
| 3389 | RDP | Remote Desktop | TCP |
| 5432 | PostgreSQL | Datenbank | TCP |
| 5900 | VNC | Remote Desktop | TCP |
| 8080 | HTTP-Alt | Proxy/Webserver | TCP |

## Port-Bereiche
- **Well-Known Ports**: 0-1023 (System/Root)
- **Registered Ports**: 1024-49151 (Anwendungen)
- **Dynamic/Private Ports**: 49152-65535 (temporär)

## Merkhilfe
- HTTP: 80 (→ HTTPS: 443 = 80 + 363)
- FTP: 20/21 (Data/Control)
- SSH: 22 (der sichere Telnet-Ersatz für 23)
- DNS: 53 (einziger der TCP UND UDP nutzt)
- SMTP: 25 (Versand), POP3: 110 (Abruf), IMAP: 143 (Abruf mit Sync)
