# 🛡️ BrainX V5 - Guía de Resiliencia y Disaster Recovery

## 📊 Análisis de Componentes Críticos

### 1. Datos Persistentes (IMPORTANTE)

| Componente | Ubicación | Riesgo | Impacto |
|------------|-----------|--------|---------|
| **PostgreSQL Database** | `postgresql://localhost:5432/brainx_v5` | 🔴 ALTO | 🔴 CRÍTICO - Todas las memorias |
| **OpenClaw Config** | `~/.openclaw/openclaw.json` | 🟡 MEDIO | 🟡 Configuración de hooks |
| **Environment Vars** | `~/.openclaw/.env` | 🟡 MEDIO | 🔴 CRÍTICO - Credenciales DB/OpenAI |
| **Skill Files** | `~/.openclaw/skills/brainx-v5/` | 🟢 BAJO | 🟢 Reinstalable desde GitHub |
| **Custom Hooks** | `~/.openclaw/hooks/internal/` | 🟡 MEDIO | 🟡 Funcionalidad auto-inject |
| **Workspace Docs** | `~/.openclaw/workspace-*/brainx.md` | 🟢 BAJO | 🟢 Documentación re-creatable |

### 2. Tablas de Base de Datos

```
brainx_v5/
├── brainx_memories              ← 🔴 CRÍTICO: Todas las memorias (126 registros)
├── brainx_learning_details      ← 🟡 Detalles de aprendizajes
├── brainx_trajectories          ← 🟡 Trayectorias de problemas
├── brainx_context_packs         ← 🟡 Packs de contexto
├── brainx_session_snapshots     ← 🟡 Snapshots de sesiones
├── brainx_pilot_log             ← 🟢 Logs de uso
└── activity, drafts, leads      ← 🟡 Otras tablas
```

---

## 🔥 Escenarios de Desastre

### Escenario 1: Actualización de OpenClaw

**Riesgo:** 🟢 **BAJO**

**Qué pasa:**
- OpenClaw se actualiza (`openclaw update` o `pnpm update -g openclaw`)
- Los hooks internos se preservan
- La skill de brainx-v5 permanece en `~/.openclaw/skills/`

**Protección:**
- ✅ Los datos están en PostgreSQL (independientes de OpenClaw)
- ✅ El hook `brainx-auto-inject` está en `~/.openclaw/hooks/internal/`
- ✅ Configuración en `openclaw.json` persiste

**Acción requerida:** Ninguna

---

### Escenario 2: Reinstalación del Gateway

**Riesgo:** 🟡 **MEDIO**

**Qué pasa:**
```bash
# El usuario ejecuta:
rm -rf ~/.openclaw
# o
openclaw reset --hard
```

**Qué se pierde:**
- ❌ Todo `~/.openclaw/` incluyendo:
  - Configuración de hooks
  - Archivos `brainx.md` de workspaces
  - Hooks personalizados
  - `.env` con credenciales

**Qué se conserva:**
- ✅ Base de datos PostgreSQL (en `/var/lib/postgresql/`)

**Recuperación:**
```bash
# 1. Reinstalar OpenClaw
pnpm install -g openclaw

# 2. Configurar gateway
openclaw onboard

# 3. Restaurar BrainX V5
cd ~/backups/brainx-v5
./restore-brainx.sh brainx-v5_backup_YYYYMMDD.tar.gz --force

# 4. Configurar variables de entorno
# Editar ~/.openclaw/.env y agregar:
# DATABASE_URL=postgresql://brainx:.../brainx_v5
# OPENAI_API_KEY=sk-...
```

---

### Escenario 3: Migración a Nuevo VPS

**Riesgo:** 🔴 **ALTO** (si no hay backup)

**Pre-migración (VPS actual):**
```bash
# Crear backup completo
cd ~/.openclaw/skills/brainx-v5/scripts
./backup-brainx.sh ~/brainx-v5-backup-final

# El archivo ~/brainx-v5-backup-final/brainx-v5_backup_YYYYMMDD.tar.gz
# contiene TODO lo necesario
```

**Migración archivos:**
```bash
# 1. Copiar backup al nuevo VPS
scp ~/brainx-v5-backup-final/brainx-v5_backup_*.tar.gz \
    usuario@nuevo-vps:/home/usuario/

# 2. En el nuevo VPS, instalar dependencias:
# - PostgreSQL + pgvector
# - Node.js 22+
# - pnpm
# - OpenClaw
```

**Post-migración (Nuevo VPS):**
```bash
# 1. Instalar PostgreSQL y pgvector
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# 2. Crear usuario y base de datos
sudo -u postgres psql << EOF
CREATE USER brainx WITH PASSWORD 'tu-password';
CREATE DATABASE brainx_v5 OWNER brainx;
GRANT ALL PRIVILEGES ON DATABASE brainx_v5 TO brainx;
EOF

# 3. Instalar pgvector
sudo apt-get install postgresql-16-pgvector  # Ajustar versión

# 4. Habilitar extensión
sudo -u postgres psql brainx_v5 -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Instalar OpenClaw
pnpm install -g openclaw
openclaw onboard

# 6. Restaurar BrainX V5
tar -xzf brainx-v5_backup_*.tar.gz
cd brainx-v5_backup_*/
../scripts/restore-brainx.sh ../brainx-v5_backup_*.tar.gz --force

# 7. Configurar variables de entorno
nano ~/.openclaw/.env
# Agregar:
# DATABASE_URL=postgresql://brainx:tu-password@localhost:5432/brainx_v5
# OPENAI_API_KEY=sk-...

# 8. Reiniciar
cd ~/.openclaw/skills/brainx-v5
./brainx health
```

---

## 🗄️ Estrategia de Backup

### Backup Automático Diario (recomendado)

Agregar a `crontab -e`:
```bash
# Backup diario de BrainX V5 a las 3 AM
0 3 * * * /home/clawd/.openclaw/skills/brainx-v5/scripts/backup-brainx.sh /home/clawd/backups/brainx-v5 >> /home/clawd/backups/brainx-v5/backup.log 2>&1

# Mantener solo los últimos 7 backups
0 4 * * * find /home/clawd/backups/brainx-v5 -name "brainx-v5_backup_*.tar.gz" -mtime +7 -delete
```

### Backup Manual

```bash
# Crear backup ahora
~/.openclaw/skills/brainx-v5/scripts/backup-brainx.sh ~/mis-backups

# Resultado:
# ~/mis-backups/brainx-v5_backup_20260220_125501.tar.gz
```

### Contenido del Backup

```
brainx-v5_backup_YYYYMMDD_HHMMSS.tar.gz
├── brainx_v5_database.sql          ← 🔴 Datos críticos (dump PostgreSQL)
├── METADATA.json                   ← 📋 Info del backup
├── config/
│   ├── brainx-v5-skill/           ← 📁 Skill completo
│   ├── openclaw.env               ← ⚙️ Variables de entorno
│   └── openclaw.json              ← ⚙️ Configuración (hooks)
├── hooks/
│   └── brainx-auto-inject         ← 🪝 Hook personalizado
├── workspaces/
│   ├── workspace-clawma_brainx.md
│   ├── workspace-coder_brainx.md
│   └── ...                        ← 📝 brainx.md de cada workspace
└── wrappers/
    ├── workspace-clawma_wrapper.sh
    └── ...                        ← 🔧 Wrappers de cada workspace
```

---

## ✅ Checklist de Resiliencia

### Pre-desastre (hacer ahora)

- [ ] Crear backup inicial: `./backup-brainx.sh ~/backups`
- [ ] Verificar backup: `tar -tzf backup.tar.gz | head`
- [ ] Configurar backup automático (cron)
- [ ] Documentar contraseña de PostgreSQL en lugar seguro
- [ ] Sincronizar backups a cloud (opcional):
  ```bash
  # Ejemplo con rclone
  rclone sync ~/backups/brainx-v5 gdrive:backups/brainx-v5
  ```

### Post-desastre

- [ ] PostgreSQL está corriendo: `sudo systemctl status postgresql`
- [ ] Base de datos existe: `psql $DATABASE_URL -c "\l"`
- [ ] pgvector habilitado: `psql $DATABASE_URL -c "CREATE EXTENSION vector;"`
- [ ] Skill funciona: `~/.openclaw/skills/brainx-v5/brainx health`
- [ ] Hook ejecutable: `ls -la ~/.openclaw/hooks/internal/brainx-auto-inject`
- [ ] Configuración en openclaw.json: `cat ~/.openclaw/openclaw.json | grep -A5 hooks`
- [ ] Contexto generado: `cat ~/.openclaw/workspace-clawma/BRAINX_CONTEXT.md`

---

## 🔧 Comandos de Verificación

### Verificar estado de BrainX V5

```bash
# 1. Health check
cd ~/.openclaw/skills/brainx-v5
./brainx health

# 2. Contar memorias
export DATABASE_URL="postgresql://brainx:.../brainx_v5"
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM brainx_memories;"

# 3. Verificar hook
~/.openclaw/hooks/internal/brainx-auto-inject ~/.openclaw/workspace-clawma clawma
cat ~/.openclaw/workspace-clawma/BRAINX_CONTEXT.md

# 4. Verificar variables de entorno
grep -E "DATABASE_URL|OPENAI_API_KEY" ~/.openclaw/.env
```

### Restauración rápida (emergencia)

```bash
# Si todo falla, restaurar solo la base de datos:
pg_dump "postgresql://brainx:...@localhost/brainx_v5" > brainx_v5_emergency.sql

# Y luego en el nuevo servidor:
psql "postgresql://brainx:...@localhost/brainx_v5" < brainx_v5_emergency.sql
```

---

## 📞 Troubleshooting

### Problema: "Database does not exist"

```bash
# Crear base de datos vacía
sudo -u postgres createdb brainx_v5
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE brainx_v5 TO brainx;"
```

### Problema: "Extension 'vector' does not exist"

```bash
# Instalar pgvector
sudo apt-get install postgresql-16-pgvector
sudo -u postgres psql brainx_v5 -c "CREATE EXTENSION vector;"
```

### Problema: Hook no ejecuta

```bash
# Verificar permisos
chmod +x ~/.openclaw/hooks/internal/brainx-auto-inject

# Verificar configuración
cat ~/.openclaw/openclaw.json | jq '.hooks'

# Reiniciar gateway
systemctl --user restart openclaw-gateway
```

---

## 🎯 Conclusión

| Escenario | Riesgo | Esfuerzo de Recuperación |
|-----------|--------|--------------------------|
| Update OpenClaw | 🟢 Bajo | 0 minutos (automático) |
| Reinstalar Gateway | 🟡 Medio | 5-10 minutos (restore script) |
| Migrar VPS | 🔴 Alto | 15-30 minutos (con backup) |
| Sin backup | 🔴 CRÍTICO | ❌ Imposible recuperar memorias |

**Recomendación:**
1. ✅ Crear backup AHORA: `./backup-brainx.sh ~/backups`
2. ✅ Configurar backup automático (cron)
3. ✅ Guardar backup en cloud/secundario
4. ✅ Probar restauración en ambiente de prueba

**Recuerda:** La base de datos PostgreSQL es lo más crítico. Todo lo demás se puede reconstruir, pero las memorias son irremplazables.
