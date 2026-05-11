---
name: fisi
description: Fachinformatiker für Systemintegration - Unterstützung bei allen Themen der FiSi-Ausbildung/Umschulung. Verwende diesen Skill bei: FiSi-Lehrplan-Themen (Netzwerke, Linux/Windows-Server, Datenbanken, Scripting, IT-Sicherheit, Cloud, Virtualisierung), Prüfungsvorbereitung (AP1/AP2), Projektarbeit, Hausaufgaben, Code-Reviews, Konfigurationsdateien, Examensfragen,typische FiSi-Aufgaben wie "Wie richte ich einen DHCP-Server ein?", "Erkläre mir Subnetting", "Hilf mir bei der Bash-Skript-Aufgabe", "Was braucht man für eine Firewall-Konfiguration?", "Erstelle ein Konzept für...", "Bewerte diese Architektur", "Wie bereite ich mich auf die Abschlussprüfung vor?".
compatibility: Benötigt Bash-Zugriff für Scriptausführung, Serena-Tools für Code-Analyse
---

# FiSi-Skill: Fachinformatiker für Systemintegration

## Überblick

Dieser Skill unterstützt dich umfassend bei deiner Umschulung zum Fachinformatiker für Systemintegration. Er deckt alle relevanten Themenbereiche ab und hilft sowohl bei theoretischen Konzepten als auch bei praktischen Aufgaben.

## Themenbereiche

### 1. Netzwerke (Network Infrastructure)
- OSI-Modell, TCP/IP-Stack
- IP-Adressierung, Subnetting (IPv4/IPv6)
- Routing-Protokolle (RIP, OSPF, BGP)
- VLANs, Trunking, Spanning-Tree
- DHCP, DNS, NAT
- VPN-Konfigurationen
- Netzwerksicherheit, Firewalls

### 2. Server-Administration
- **Linux-Server**: Debian/Ubuntu, RHEL/CentOS, SUSE
  - User-Management, Permissions
  - Package-Management (apt, yum, zypper)
  - Services: Apache, Nginx, SSH, Samba, NFS
  - Log-Analyse, Monitoring
- **Windows-Server**: Active Directory, GPOs, DNS, DHCP, WSUS
  - PowerShell-Scripting
  - Rollen und Features

### 3. Datenbanken
- SQL-Grundlagen (SELECT, INSERT, UPDATE, DELETE, JOINs)
- Datenbank-Design, Normalisierung
- MySQL, PostgreSQL, SQLite
- Backup-Strategien, Replikation

### 4. Scripting & Automatisierung
- **Bash**: Shell-Skripte, Textverarbeitung (grep, sed, awk)
- **Python**: Automatisierung, API-Integration
- **PowerShell**: Windows-Administration
- **YAML**: Konfigurationsdateien (Ansible, Docker)

### 5. Virtualisierung & Cloud
- VMware, Hyper-V, KVM
- Docker, Kubernetes
- Cloud-Plattformen: AWS, Azure, Google Cloud
- IaaS, PaaS, SaaS-Modelle

### 6. IT-Sicherheit
- Verschlüsselung (SSL/TLS, PGP, AES)
- Authentifizierung (LDAP, Kerberos, 2FA)
- Security Hardening
- OWASP Top 10
- Incident Response

### 7. Storage
- RAID-Level (0, 1, 5, 6, 10)
- SAN, NAS, DAS
- ZFS, LVM
- Backup-Strategien (3-2-1-Regel)

### 8. Soft Skills & Projektmanagement
- AGILE, SCRUM, Kanban
- Dokumentation
- Kundenkommunikation
- Wirtschaftlichkeitsberechnung

## Prüfungsvorbereitung (AP1 & AP2)

### Abschlussprüfung Teil 1 (AP1)
- Zeitraum: Mitte der Ausbildung
- Inhalte: Grundlagen aller oben genannten Bereiche
- Fokus: Verständnis, Basis-Konfigurationen

### Abschlussprüfung Teil 2 (AP2)
- Zeitraum: Ende der Ausbildung
- Inhalte: Vertiefte Themen, Projektarbeit, Wirtschaftlichkeit
- Fokus: Praxis, Konzepte, Entscheidungsbegründungen

## Arbeitsweise

1. **Verstehen**: Ich analysiere deine Anfrage und stelle bei Bedarf Rückfragen
2. **Erklären**: Konzepte werden verständlich und praxisnah erklärt
3. **Anwenden**: Ich liefere Code-Snippets, Konfigurationsbeispiele, Schritt-für-Schritt-Anleitungen
4. **Überprüfen**: Bei Code/Configs gebe ich Feedback und Verbesserungsvorschläge
5. **Zusammenfassen**: Wichtige Punkte werden hervorgehoben

## Code- und Config-Qualität

Ich achte auf:
- **Best Practices**: Sichere, effiziente Lösungen
- **Kommentare**: Erklärungen im Code
- **Fehlerbehandlung**: Robuste Skripte
- **Dokumentation**: Nachvollziehbare Konfigurationen

## Typische Aufgabenformate

- "Erkläre mir [Konzept]"
- "Wie richte ich [Service] ein?"
- "Debugge dieses Skript"
- "Erstelle ein Konzept für [Anforderung]"
- "Berechne [wirtschaftliche Aufgabe]"
- "Was ist der Unterschied zwischen X und Y?"
- "Hilf mir bei der Prüfungsvorbereitung für [Thema]"

## Beispiele und Musterlösungen

### Subnetting-Berechnung (IPv4)

**Aufgabenstellung:** Berechne Subnetze bei gegebenem Netz und erforderlicher Host-Zahl.

**Vorgehensweise:**
1. Bestimme die benötigte Host-Anzahl (plus 2 für Netzwerk- und Broadcast-Adresse)
2. Finde die nächste potenz von 2: `2^n >= required_hosts`
3. Berechne Subnetzmaske: `/32 - n` oder `255.255.255.x`
4. Berechne Netzadresse, erster/letzter Host und Broadcast

**Beispiel:** `192.168.10.0/24`, benötigt 6 Subnetze mit mindestens 20 Hosts

| Subnetz | Netzadresse | Nutzbarer Bereich | Broadcast |
|---------|-------------|-------------------|-----------|
| 1 | 192.168.10.0 | 192.168.10.1 - 192.168.10.30 | 192.168.10.31 |
| 2 | 192.168.10.32 | 192.168.10.33 - 192.168.10.62 | 192.168.10.63 |
| 3 | 192.168.10.64 | 192.168.10.65 - 192.168.10.94 | 192.168.10.95 |

**Berechnung:** Für 20+ Hosts braucht man 5 Bits (`2^5=32`). Subnetzmaske: `/27` (255.255.255.224).

### Linux Dateiberechtigungen

**Aufgabe:** Verzeichnis `/var/www/projekt` konfigurieren:
- Besitzer (www-data): Lesen, Schreiben, Ausführen (rwx)
- Gruppe (webentwickler): Lesen, Ausführen (r-x)
- Andere: Kein Zugriff (---)
- Neue Dateien erben Gruppe webentwickler

**Befehle:**
```bash
# Besitzer und Gruppe setzen
sudo chown www-data:webentwickler /var/www/projekt

# Berechtigungen: rwxr-x--- (750)
sudo chmod 750 /var/www/projekt

# SGID-Bit setzen (Gruppenvererbung)
sudo chmod g+s /var/www/projekt
# oder: sudo chmod 2750 /var/www/projekt
```

**Oktalnotation:**
- 7 = rwx (4+2+1) → Besitzer
- 5 = r-x (4+0+1) → Gruppe
- 0 = --- (0+0+0) → Andere
- 2 = SGID-Bit (spezielle Berechtigung)

### Docker-Containerisierung

**Container vs. Virtuelle Maschinen:**
- **Container**: Teilen den Host-Kernel, leichtgewichtig, schneller Start (Sekunden), geringer Overhead
- **VM**: Eigenes Betriebssystem, schwerer, langsamerer Start (Minuten), höherer Ressourcenverbrauch

**Dockerfile für Node.js-Backend:**
```dockerfile
# Multi-Stage Build für optimierte Image-Größe
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
RUN addgroup -g 1001 -S nodejs && adduser -S nodeuser -u 1001
WORKDIR /app
COPY --from=builder --chown=nodeuser:nodejs /app/node_modules ./node_modules
COPY --chown=nodeuser:nodejs . .
USER nodeuser
EXPOSE 3000
CMD ["node", "server.js"]
```

**docker-compose.yml (Node.js + PostgreSQL + Nginx):**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/appdb
    depends_on:
      - db
    networks:
      - appnet

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=appdb
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - appnet

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
    networks:
      - appnet

volumes:
  db_data:

networks:
  appnet:
```

**Sicherheitshinweise:**
- Nicht als root innerhalb des Containers laufen lassen
- `.dockerignore` erstellen (node_modules, .env, .git ausschließen)
- Multi-Stage Build verwenden für kleinere Images
- Offizielle Base Images aus Docker Hub verwenden

### RAID-Level Vergleich

**Aufgabe:** Fileserver mit 8 Festplatten à 2 TB konfigurieren. Vergleiche RAID 1, RAID 5 und RAID 10.

**Vergleichstabelle:**

| RAID-Level | Nutzbare Kapazität | Lesen | Schreiben | Max. Ausfälle |
|------------|-------------------|-------|-----------|---------------|
| RAID 1 (Spiegelung) | 8 TB (50%) | Sehr gut | Gut | 7 Platten* |
| RAID 5 (Striping + Parität) | 14 TB (87.5%) | Gut | Mäßig | 1 Platte |
| RAID 10 (Spiegel + Stripe) | 8 TB (50%) | Sehr gut | Sehr gut | Bis zu 4 Platten** |

\* Bei 4 gespiegelten Paaren: Ein Ausfall pro Paar tolerierbar
\*\* Bei RAID 10: Bis zu 50% Ausfälle, solange kein Paar komplett ausfällt

**Berechnung:**
- RAID 1: 8 Platten in 4 gespiegelten Paaren → 4×2 TB = 8 TB
- RAID 5: (8−1)×2 TB = 14 TB (eine Platte für Parität)
- RAID 10: (8÷2)×2 TB = 8 TB (50% für Spiegelung)

**Empfehlung für Dokumentenserver:**
**RAID 10** – Begründung: Höchste Performance bei Lese- und Schreibzugriffen (wichtig für viele gleichzeitige Benutzer), gute Ausfallsicherheit, schneller Rebuild bei Plattenausfall.

### SQL JOIN-Abfragen

**Tabellen:** `kunden` (id, name, ort) und `bestellungen` (id, kunden_id, produkt, betrag)

**Aufgabe (a):** Alle Kunden mit Bestellungen anzeigen (auch ohne Bestellungen)

```sql
-- LEFT JOIN: Alle Kunden, auch ohne Bestellung
SELECT k.name, b.produkt, b.betrag
FROM kunden k
LEFT JOIN bestellungen b ON k.id = b.kunden_id;
```

**Aufgabe (b):** Gesamtumsatz pro Kunde berechnen

```sql
-- GROUP BY mit Aggregatfunktion SUM
SELECT k.name, COALESCE(SUM(b.betrag), 0) AS gesamtumsatz
FROM kunden k
LEFT JOIN bestellungen b ON k.id = b.kunden_id
GROUP BY k.id, k.name;
```

**Aufgabe (c):** Nur Kunden mit mehr als 500 EUR Umsatz

```sql
-- HAVING filtert auf Aggregat-Ergebnisse
SELECT k.name, SUM(b.betrag) AS gesamtumsatz
FROM kunden k
JOIN bestellungen b ON k.id = b.kunden_id
GROUP BY k.id, k.name
HAVING SUM(b.betrag) > 500;
```

**JOIN-Typen im Vergleich (Venn-Diagramm-Prinzip):**

```
INNER JOIN:        LEFT JOIN:         RIGHT JOIN:
   ╔═══╗            ╔═══════╗          ╔═══════╗
   ║ ▓▓║            ║▓▓▓▓▓▓▓║          ║▓▓▓▓▓▓▓║
A  ║▓▓▓ ║ B      A   ║▓▓▓▓▓▓▓║ B     A   ║▓▓▓▓▓▓▓║ B
   ║▓▓▓▓║            ║▓▓▓▓▓▓▓║          ║▓▓▓▓▓▓▓║
   ╚═══╝            ╚═══════╝          ╚═══════╝
  (Nur Schnitt)    (A komplett)       (B komplett)
```

| JOIN | Beschreibung | Verwendung |
|------|--------------|------------|
| INNER JOIN | Nur passende Zeilen beider Tabellen (Schnittmenge) | Wenn Daten in beiden Tabellen existieren müssen |
| LEFT JOIN | Alle Zeilen der linken Tabelle, passende der rechten (A gesamt) | Wenn alle Datensätze der Haupttabelle erhalten bleiben sollen |
| RIGHT JOIN | Alle Zeilen der rechten Tabelle, passende der linken (B gesamt) | Selten verwendet (umgekehrter LEFT JOIN) |

### OSI-Modell Schichten

**Aufgabe:** Ordne Protokolle und Geräte den korrekten OSI-Schichten zu.

**OSI-Schichten-Übersicht:**

| Schicht | Name | Protokolle/Geräte | Einheit | Schlüsselbegriffe |
|---------|------|-------------------|---------|-------------------|
| 7 | Anwendung | HTTP, HTTPS, FTP, SMTP, DNS | Daten | TLS/SSL, Port 443 |
| 6 | Darstellung | TLS, SSL, ASCII, JPEG, MPEG | Daten | Verschlüsselung, Kompression |
| 5 | Sitzung | NetBIOS, RPC, PPTP | Daten | Sitzungsmanagement |
| 4 | Transport | TCP, UDP, SCTP | Segment | Port-Nummern, Segmentierung |
| 3 | Netzwerk | IP, ICMP, ARP, Router | Paket | IP-Adressen, Routing |
| 2 | Sicherung | Ethernet, PPP, Switch, MAC | Frame | MAC-Adressen, VLAN |
| 1 | Bitübertragung | Hub, Kabel, Glasfaser, Funk | Bit | Bits, elektrische/optische Signale |

**Datenkapselung bei HTTPS-Aufruf:**

1. **Schicht 7 (Anwendung):** Browser sendet HTTP-Request
2. **Schicht 6 (Darstellung):** TLS verschlüsselt die Daten
3. **Schicht 5 (Sitzung):** Sitzung wird etabliert
4. **Schicht 4 (Transport):** TCP-Segment mit Port 443 erstellt
5. **Schicht 3 (Netzwerk):** IP-Paket mit Ziel-IP-Adresse erstellt
6. **Schicht 2 (Sicherung):** Ethernet-Frame mit MAC-Adressen erstellt
7. **Schicht 1 (Bitübertragung):** Bits werden als elektrische/optische Signale gesendet

**Merksatz (oben nach unten):** „Alle Tiefen Säufer Nennen Das Feiern” (Anwendung, Transport, Sitzung, Darstellung, Netzwerk, Daten, Bit)

### Backup-Strategien (3-2-1-Regel)

**Aufgabe:** Unternehmen mit 500 GB Daten, täglich 20 GB Änderungen, Backup-Fenster 22:00–06:00. Entwirf ein Backup-Konzept.

**Die 3-2-1-Regel:**
- **3** Kopien der Daten (1 Produktiv + 2 Backups)
- **2** unterschiedliche Speichermedien (z.B. NAS + Cloud)
- **1** Kopie Offsite (Cloud oder externes Rechenzentrum)

**Backup-Arten im Vergleich:**

| Backup-Typ | Bezugspunkt | Backup-Zeit | Wiederherstellung | Speicherbedarf |
|------------|-------------|-------------|-------------------|----------------|
| Vollbackup | Komplett | Lang (500 GB) | Schnell | Hoch (500 GB/Tag) |
| Differentiell | Letztes Vollbackup | Mittel (~20 GB) | Mittel | Mittel |
| Inkrementell | Letztes Backup | Kurz (~20 GB) | Langsam (Kette) | Niedrig |

**Beispiel-Berechnung (Woche):**
- Sonntag: Vollbackup (500 GB)
- Mo–Sa: Inkrementell (je 20 GB × 6 = 120 GB)
- **Gesamt:** ~620 GB pro Woche

**RPO und RTO definieren:**
- **RPO (Recovery Point Objective):** Max. Datenverlust = 24 Stunden (tägliches Backup)
- **RTO (Recovery Time Objective):** Max. Ausfallzeit = 4 Stunden (bei Vollrestore)

### IT-Sicherheit: Verschlüsselung

**Symmetrische vs. Asymmetrische Verschlüsselung:**

| Eigenschaft | Symmetrisch | Asymmetrisch |
|-------------|-------------|--------------|
| Schlüssel | Gleicher Schlüssel | Schlüsselpaar (öffentlich/privat) |
| Geschwindigkeit | Sehr schnell | Langsam |
| Algorithmen | AES, ChaCha20, 3DES | RSA, ECDSA, DSA |
| Einsatz | Große Datenmengen | Schlüsselaustausch, Signaturen |

**TLS-Handshake (HTTPS-Verbindung):**

1. **Client Hello:** Browser sendet unterstützte Cipher Suites + Zufallswert
2. **Server Hello:** Server wählt Cipher Suite, sendet Zertifikat + Zufallswert
3. **Schlüsselaustausch:** Client verschlüsselt Pre-Master-Secret mit Server-Public-Key
4. **Session Keys:** Aus Pre-Master-Secret werden symmetrische Session Keys abgeleitet
5. **Verschlüsselte Übertragung:** Ab jetzt symmetrische Verschlüsselung (AES)

**Warum beide Verfahren kombiniert?**
- Asymmetrisch = sicherer Schlüsselaustausch, aber langsam
- Symmetrisch = schnell für große Datenmengen, aber Schlüsselverteilung problematisch
- **Hybrid:** Asymmetrisch für den Schlüsseltausch, symmetrisch für die Datenübertragung

**Forward Secrecy (PFS):**
- Verwendet temporäre Session Keys statt statischer Private Keys
- Bei Kompromittierung eines Keys werden vergangene Sessions nicht entschlüsselbar
- TLS 1.3 erzwingt PFS (z.B. mit ECDHE)

**Empfohlene Schlüssellängen:**

| Algorithmus | Schlüssellänge | Sicherheitsstufe |
|-------------|----------------|------------------|
| AES | 256 Bit | Hohe Sicherheit |
| RSA | 2048-4096 Bit | Mindestens 2048 Bit |
| ECDSA/ECDH | 256 Bit (P-256) | Empfohlen statt RSA |
| ChaCha20 | 256 Bit | Alternative zu AES |

### Active Directory Design

**Aufgabe:** Mittelständisches Unternehmen mit Abteilungen Vertrieb, Entwicklung, Verwaltung strukturieren.

**OU-Struktur:**

```
corp.local
├── OU=Benutzer
│   ├── OU=Vertrieb
│   ├── OU=Entwicklung
│   └── OU=Verwaltung
├── OU=Computer
│   ├── OU=Clients
│   └── OU=Server
└── OU=Gruppen
    └── OU=Sicherheitsgruppen
```

**AGDLP-Prinzip (Account → Global → Domain Local → Permission):**

1. Benutzer in **globale** Sicherheitsgruppen (nach Abteilung)
2. Globale Gruppen in **domain-lokale** Gruppen (nach Ressource)
3. Domain-lokale Gruppen erhalten **Berechtigungen**

**Beispiel GPO – Passwortrichtlinie:**

```powershell
# GPO erstellen und verknüpfen
New-GPO -Name "Passwortrichtlinie" | New-GPLink -Target "OU=Benutzer,DC=corp,DC=local"

# Einstellungen konfigurieren (Gruppenrichtlinienverwaltung)
# Computerkonfiguration → Windows-Einstellungen → Sicherheitseinstellungen → Kontorichtlinien
```

**GPO-Einstellungen:**

| Richtlinie | Wert | Beschreibung |
|------------|------|--------------|
| Min. Kennwortlänge | 12 Zeichen | Komplexität erforderlich |
| Kennwortablauf | 90 Tage | Regelmäßiger Wechsel |
| Bildschirmsperre | 10 Min. | Automatische Sperre |
| Kontosperrung | 5 Fehlversuche | Schutz vor Brute-Force |

### VLAN-Konfiguration

**Aufgabe:** Büro mit Abteilungen Verwaltung (VLAN 10), Technik (VLAN 20), Gäste (VLAN 30) trennen.

**Tagged vs. Untagged (802.1Q):**

| Typ | Bezeichnung | Beschreibung |
|-----|-------------|--------------|
| Untagged | Access Port | Endgeräte-Port, kein VLAN-Tag |
| Tagged | Trunk Port | Uplink zwischen Switches, mehrere VLANs |

**Switch-Konfiguration (Beispiel Cisco):**

```bash
# VLANs erstellen
vlan 10
 name Verwaltung
vlan 20
 name Technik
vlan 30
 name Gaeste

# Access-Ports konfigurieren
interface gi0/1
 switchport mode access
 switchport access vlan 10

# Trunk-Port konfigurieren
interface gi0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
```

**Inter-VLAN-Routing (Router-on-a-Stick):**

```bash
# Router-Subinterfaces
interface gi0/0.10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0

interface gi0/0.20
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
```

**Sicherheit:** Gäste-VLAN isoliert, kein Zugriff auf interne VLANs (Firewall-Regel).

### Bash-Scripting

**Aufgabe:** Backup-Skript erstellen, das /home-Verzeichnisse archiviert und alte Backups löscht.

```bash
#!/bin/bash
# backup.sh - Automatisiertes Home-Verzeichnis-Backup

# Konfiguration
BACKUP_DIR="/backup"
SOURCE_DIR="/home"
RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="home_backup_${DATE}.tar.gz"

# Funktion: Fehlerbehandlung
cleanup() {
    echo "Fehler aufgetreten. Bereinige..."
    rm -f "${BACKUP_DIR}/tmp_*"
    exit 1
}
trap cleanup ERR

# Prüfung: Backup-Verzeichnis existiert?
if [ ! -d "$BACKUP_DIR" ]; then
    echo "Erstelle Backup-Verzeichnis..."
    mkdir -p "$BACKUP_DIR" || { echo "Fehler: Kann Verzeichnis nicht erstellen"; exit 1; }
fi

# Backup erstellen
echo "Starte Backup von $SOURCE_DIR..."
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" "$SOURCE_DIR" 2>/dev/null

# Prüfung erfolgreich?
if [ $? -eq 0 ]; then
    echo "Backup erfolgreich: ${BACKUP_FILE}"
    logger -t backup "Home-Verzeichnis gesichert"
else
    echo "Backup fehlgeschlagen!"
    exit 1
fi

# Alte Backups löschen (Retention)
find "$BACKUP_DIR" -name "home_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
echo "Backups älter als $RETENTION_DAGE Tage gelöscht"

# Übersicht anzeigen
du -sh "${BACKUP_DIR}/home_backup_"*.tar.gz | tail -5
```

**Wichtige Bash-Konstrukte:**

| Konstrukt | Beschreibung | Beispiel |
|-----------|--------------|----------|
| `if [ ]` | Bedingung testen | `if [ -f datei ]` |
| `for var in` | Schleife | `for i in {1..10}` |
| `while` | While-Schleife | `while read line` |
| `$?` | Exit-Code | `if [ $? -eq 0 ]` |
| `>` / `>>` | Umleiten/Anhängen | `echo "log" >> datei` |
| `\|\|` / `&&` | Oder / Und | `befehl || fehler` |

### PowerShell für Windows

**Aufgabe:** AD-Benutzer anlegen und Systemdienste überwachen.

```powershell
# Benutzerverwaltung
New-ADUser -Name "Max Mustermann" `
    -SamAccountName "mmustermann" `
    -UserPrincipalName "mmustermann@corp.local" `
    -Path "OU=Entwicklung,OU=Benutzer,DC=corp,DC=local" `
    -AccountPassword (ConvertTo-SecureString "P@ssw0rd!" -AsPlainText -Force) `
    -Enabled $true `
    -ChangePasswordAtLogon $true

# Mehrere Benutzer aus CSV importieren
Import-Csv "C:\\users.csv" | ForEach-Object {
    New-ADUser -Name $_.Name -SamAccountName $_.SAM `
        -Path "OU=Benutzer,DC=corp,DC=local" -Enabled $true
}

# Systemdienste prüfen
Get-Service | Where-Object {$_.Status -eq "Running" -and $_.StartType -eq "Auto"} |
    Select-Object Name, DisplayName, Status | Export-Csv "C:\\services.csv"

# Remote-Computer verwalten (WinRM erforderlich)
Invoke-Command -ComputerName "SERVER01" -ScriptBlock {
    Get-Process | Sort-Object CPU -Descending | Select-Object -First 5
}
```

**PowerShell-Operatoren:**

| Operator | Beschreibung | Beispiel |
|----------|--------------|----------|
| `-eq` | Gleich | `$a -eq $b` |
| `-ne` | Ungleich | `$status -ne "Running"` |
| `-like` | Wildcard | `$name -like "*Admin*"` |
| `-match` | Regex | `$email -match "@corp.local$"` |
| `|` | Pipe | `Get-Process | Where-Object` |
| `$()` | Subexpression | `Write-Host "CPU: $($proc.CPU)"` |

### Firewall-Regeln (iptables)

**Aufgabe:** Webserver absichern – SSH, HTTP und HTTPS erlauben, restlichen Traffic blockieren.

```bash
# Alle bestehenden Regeln löschen
iptables -F
iptables -X

# Standard-Policy: Alles verbieten
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Loopback erlauben
iptables -A INPUT -i lo -j ACCEPT

# Established connections erlauben
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH (Port 22) erlauben
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# HTTP (Port 80) und HTTPS (Port 443) erlauben
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# ICMP (Ping) begrenzt erlauben
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/second -j ACCEPT

# Alles andere loggen und verwerfen
iptables -A INPUT -j LOG --log-prefix "FIREWALL-DROP:"
iptables -A INPUT -j DROP
```

**iptables-Optionen:**

| Option | Bedeutung | Beispiel |
|--------|-----------|----------|
| `-A` | Anhängen (Append) | `-A INPUT` |
| `-P` | Policy setzen | `-P INPUT DROP` |
| `-p` | Protokoll | `-p tcp` |
| `--dport` | Zielport | `--dport 22` |
| `-j` | Jump (Ziel) | `-j ACCEPT` |
| `-m` | Modul laden | `-m state` |

## Output-Formate

Je nach Aufgabe:
- **Erklärungen**: Fließtext mit Beispielen
- **Code**: Bash, Python, PowerShell, SQL
- **Configs**: Apache, Nginx, SSH, Firewall-Regeln
- **Tabellen**: Vergleich, Übersicht
- **Diagramme**: Architekturentwürfe (Mermaid)
- **Checklisten**: Prüfungsvorbereitung, Projektplanung
