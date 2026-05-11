# Linux-Befehle — Schnellreferenz

## Dateisystem
```bash
ls -la              # Dateien auflisten (inkl. versteckte)
cd /pfad            # Verzeichnis wechseln
pwd                 # Aktuelles Verzeichnis anzeigen
mkdir -p dir/sub    # Verzeichnis erstellen (inkl. Eltern)
cp -r quelle ziel   # Kopieren (rekursiv)
mv alt neu          # Verschieben/Umbenennen
rm -rf verzeichnis  # Löschen (rekursiv, ohne Nachfrage)
find / -name "*.log" # Dateien suchen
du -sh /var/log     # Verzeichnisgröße anzeigen
df -h               # Festplattenbelegung
```

## Benutzer & Rechte
```bash
useradd -m -s /bin/bash user  # Benutzer erstellen
usermod -aG gruppe user       # Benutzer zu Gruppe hinzufügen
passwd user                    # Passwort setzen
chmod 755 datei               # Berechtigungen setzen
chown user:gruppe datei       # Besitzer ändern
id user                       # Benutzerinfo anzeigen
```

## Netzwerk
```bash
ip addr show             # IP-Adressen anzeigen
ip route show            # Routing-Tabelle
ss -tulnp               # Offene Ports anzeigen
ping -c 4 host           # Erreichbarkeit prüfen
traceroute host          # Route verfolgen
nslookup domain          # DNS-Abfrage
dig domain               # DNS-Abfrage (detailliert)
curl -I https://host     # HTTP-Header abrufen
```

## Services (systemd)
```bash
systemctl start dienst    # Dienst starten
systemctl stop dienst     # Dienst stoppen
systemctl restart dienst  # Dienst neustarten
systemctl enable dienst   # Autostart aktivieren
systemctl status dienst   # Status anzeigen
journalctl -u dienst -f   # Logs live anzeigen
```

## Package-Management
```bash
# Debian/Ubuntu (apt)
apt update && apt upgrade   # Aktualisieren
apt install paket           # Installieren
apt remove paket            # Deinstallieren
apt search suchbegriff      # Suchen

# RHEL/CentOS (dnf/yum)
dnf install paket
dnf remove paket
dnf search suchbegriff
```

## Prozesse & System
```bash
top / htop               # Prozessmonitor
ps aux                   # Alle Prozesse
kill -9 PID              # Prozess beenden
free -h                  # Speicher anzeigen
uptime                   # Betriebszeit
uname -a                 # Systeminfo
```
