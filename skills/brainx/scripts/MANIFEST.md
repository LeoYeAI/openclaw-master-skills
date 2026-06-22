# BrainX V5 Scripts Manifest

Este archivo documenta los scripts de mantenimiento en `/home/clawd/.openclaw/skills/brainx-v5/scripts/`.

## Leyenda de Recursos
- **RAM**: Bajo (<100MB), Medio (100-500MB), Alto (>500MB)
- **CPU**: Bajo (segundos), Medio (minutos), Alto (largo proceso)

| Script | Frecuencia | RAM | CPU | Propósito |
| :--- | :--- | :--- | :--- | :--- |
| `session-harvester.js` | Cron (Hourly) | Bajo | Bajo | Recolecta sesiones frescas para ingestión |
| `trajectory-recorder.js` | Cron (Hourly) | Bajo | Bajo | Registra la trayectoria de razonamiento del agente |
| `session-snapshot.js` | Cron (Daily) | **Medio** | Medio | **INCREMENTAL**: Crea snapshots de sesiones nuevas |
| `dedup-supersede.js` | Manual | Medio | Alto | Elimina memorias duplicadas/obsoletas |
| `quality-scorer.js` | Manual | Medio | Medio | Evalúa calidad semántica de memorias |
| `eval-memory-quality.js`| Manual | Alto | Alto | Análisis profundo de dataset (Rag/Eval) |
| `backup-brainx.sh` | Semanal | Bajo | Bajo | Backup SQL de BrainX (vía pg_dump) |

*Nota: Cualquier script que gestione datos de BrainX debe ser ejecutado mediante el agente de mantenimiento único para evitar inconsistencias.*
