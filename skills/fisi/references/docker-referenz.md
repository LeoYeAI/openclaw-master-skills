# Docker — Schnellreferenz

## Container vs. VM

| Eigenschaft | Container | VM |
|-------------|-----------|-----|
| Kernel | Geteilt (Host) | Eigener |
| Start | Sekunden | Minuten |
| Größe | MBs | GBs |
| Isolation | Prozess-Level | Hardware-Level |
| Performance | Near-Native | Overhead durch Hypervisor |
| Einsatz | Microservices, CI/CD | Legacy, verschiedene OS |

## Dockerfile (Beispiel: Node.js)
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
USER node
CMD ["node", "server.js"]
```

## docker-compose.yml (Beispiel: Web + DB + Proxy)
```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=mydb
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  pgdata:
```

## Wichtige Befehle
```bash
docker build -t name:tag .     # Image bauen
docker run -d -p 8080:80 name  # Container starten
docker ps                       # Laufende Container
docker logs container           # Logs anzeigen
docker exec -it container sh   # Shell im Container
docker compose up -d            # Compose starten
docker compose down             # Compose stoppen
docker system prune -a          # Aufräumen
```
