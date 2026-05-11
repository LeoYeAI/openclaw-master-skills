---
name: engram
description: Sistema de memoria persistente para agentes IA. Usa mem_save después de bugfixes, decisiones, descubrimientos, cambios de config. Usa mem_search cuando el usuario menciona "remember"/"recordar" o al empezar trabajo que se solapa con sesiones previas. Usa mem_session_summary antes de terminar sesiones para preservar contexto.
homepage: https://github.com/Gentleman-Programming/engram
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["mcporter", "engram"]
      env: []
    platforms:
      - macOS
      - Linux
      - Windows
    install:
      - id: mcporter-npm
        kind: npm
        package: mcporter
        bins: ["mcporter"]
        label: Install MCPorter via npm (all platforms)
        platforms: ["macOS", "Linux", "Windows"]
      - id: mcporter-brew
        kind: brew
        formula: steipete/tap/mcporter
        bins: ["mcporter"]
        label: Install MCPorter via Homebrew (macOS/Linux)
        platforms: ["macOS", "Linux"]
      - id: engram-brew
        kind: brew
        formula: gentleman-programming/tap/engram
        bins: ["engram"]
        label: Install Engram via Homebrew (macOS/Linux)
        platforms: ["macOS", "Linux"]
      - id: engram-binary
        kind: manual
        label: Download Engram binary from GitHub Releases
        url: https://github.com/Gentleman-Programming/engram/releases
        platforms: ["macOS", "Linux", "Windows"]
---

# Engram - Memoria Persistente para Agentes IA

Engram te da memoria persistente entre sesiones. Recuerdas bugfixes, decisiones de arquitectura, patrones y descubrimientos de conversaciones previas.

## ⚠️ IMPORTANTE: Mecanismo de Activación

**NO es automático como cron job** → Requiere decisión ACTIVA del agente.

### ✅ Cuándo el agente LLAMA a Engram:

| Momento | Herramienta | Razón |
|---------|-------------|-------|
| **INICIO de sesión** | `mem_context` | Recuperar trabajo previo |
| **Después de trabajo significativo** | `mem_save` | Guardar descubrimientos |
| **Usuario dice "recuerda"/"recordar"** | `mem_search` | Buscar en memoria |
| **Empezando trabajo similar** | `mem_search` | Verificar si ya se hizo |
| **FIN de sesión** | `mem_session_summary` | Preservar contexto |
| **Después de compactación de contexto** | `mem_context` | Recuperar estado |

### ❌ Cuándo el agente NO llama a Engram:

- Cada mensaje del usuario (ruido)
- Heartbeats (gasta tokens innecesariamente)
- Crons en background (no es el propósito)
- Tool calls triviales (no vale la pena guardarlo)

### 🤖 Decisión del Agente:

El agente evalúa el contexto y decide:
- **¿Fue trabajo significativo?** → Guardar
- **¿Aprendí algo importante?** → Guardar
- **¿Cambio de configuración crítico?** → Guardar
- **¿Fue trivial?** → No guardar

**NO esperes a que te pidan guardar** → Decide proactivamente.

---

## ⚙️ Prerrequisitos

Este skill requiere dos binarios instalados:

| Herramienta | Propósito | Repositorio |
|-------------|-----------|-------------|
| **MCPorter** | Cliente MCP para ejecutar herramientas | [steipete/mcporter](https://github.com/steipete/mcporter) |
| **Engram** | Backend de memoria persistente | [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram) |

### Instalar MCPorter

**macOS / Linux (Homebrew):**
```bash
brew tap steipete/tap
brew install steipete/tap/mcporter
```

**Todas las plataformas (npm):**
```bash
# Sin instalación (para probar)
npx mcporter --version

# Instalación global
npm install -g mcporter
```

**Windows (binario):**
1. Descargar `mcporter-<version>.exe` desde [GitHub Releases](https://github.com/steipete/mcporter/releases)
2. Renombrar a `mcporter.exe`
3. Agregar al PATH del sistema

**Verificar:**
```bash
mcporter --version
```

### Instalar Engram

**macOS / Linux (Homebrew):**
```bash
brew install gentleman-programming/tap/engram
```

**Todas las plataformas (binario):**
1. Descargar desde [GitHub Releases](https://github.com/Gentleman-Programming/engram/releases)
2. **Windows**: Renombrar a `engram.exe` y agregar al PATH
3. **macOS/Linux**: `chmod +x engram && sudo mv engram /usr/local/bin/`

**Verificar:**
```bash
engram version
```

---

## Setup (Conectar MCPorter con Engram)

Una vez instalados ambos binarios, registrar Engram como servidor MCP:

```bash
# Registrar servidor MCP de Engram
mcporter config add engram --stdio "engram mcp"

# Verificar conexión (debe mostrar 13 herramientas)
mcporter list engram
```

**Resultado esperado:**
```
engram - Sistema de memoria persistente para agentes IA
  13 tools · HTTP/stdio
```

## Conceptos Core

- **Memoria curada por el agente**: TÚ decides qué vale la pena recordar, no captura automática
- **Revelación progresiva**: Search → Timeline → Full observation (eficiente en tokens)
- **Ciclo de vida de sesión**: Contexto al inicio, guardados durante trabajo, resumen al final

---

## 🌐 Integración con Ecosistema OpenClaw

### Ecosistema de Memoria Completo

```
┌──────────────────────────────────────┐
│      MEMORY.md (Estático/Permanente) │
│  - Info del usuario (no cambia)      │
│  - Reglas de seguridad (permanentes) │
│  - Directrices (permanentes)         │
└──────────────────────────────────────┘
              ↓ complementa
┌──────────────────────────────────────┐
│   memory/YYYY-MM-DD.md (Diario/Raw)  │
│  - Notas del día                     │
│  - Proyectos trabajados              │
│  - Contexto inmediato                │
│  - Se archiva automáticamente        │
└──────────────────────────────────────┘
              ↓ complementa
┌──────────────────────────────────────┐
│      Engram (Memoria Técnica)        │
│  - Bugfixes                          │
│  - Decisiones de código              │
│  - Patrones descubiertos             │
│  - Configuraciones técnicas          │
│  - Búsqueda rápida                   │
└──────────────────────────────────────┘
              ↓ complementa
┌──────────────────────────────────────┐
│  self-improving (Comportamiento)     │
│  - Correcciones del usuario          │
│  - Preferencias aprendidas           │
│  - Patrones de comportamiento        │
│  - Sistema HOT/WARM/COLD             │
└──────────────────────────────────────┘
```

### Cuándo Usar Cada Sistema

| Tipo de Información | Dónde Guardar | Por Qué |
|---------------------|---------------|---------|
| Info permanente del usuario | MEMORY.md | No cambia, referencia rápida |
| Notas del día | memory/YYYY-MM-DD.md | Contexto inmediato, raw |
| Bugfix técnico | Engram | Búsqueda rápida, técnico |
| Corrección del usuario | self-improving | Comportamiento futuro |
| Decisión de arquitectura | Engram | Técnico, referenciable |
| Preferencia de comunicación | MEMORY.md + self-improving | Ambos |
| Proyecto activo | memory/YYYY-MM-DD.md | Contexto inmediato |
| Patrón de código | Engram | Reutilizable |

### Relación con Heartbeats

**❌ NO llamar Engram desde heartbeats** → Gasta tokens innecesariamente.

**✅ Heartbeats son para**:
- Chequeos proactivos (emails, calendario, etc.)
- Tareas recurrentes
- Notificaciones

**✅ Engram es para**:
- Memoria entre sesiones
- Contexto técnico
- Búsqueda de trabajo previo

### Relación con self-improving

**Pueden solaparse** en tipo "learning":
- **self-improving**: Preferencias de comportamiento del usuario
- **Engram**: Aprendizajes técnicos de código

**Regla**: Si es sobre cómo el usuario quiere que te comportes → self-improving. Si es técnico → Engram.

---

## Cuándo Usar Cada Herramienta

| Disparador | Herramienta | Propósito |
|------------|-------------|-----------|
| Empezando trabajo en un proyecto | `mem_context` | Cargar contexto de sesión previa |
| Después de arreglar un bug | `mem_save` | Documentar qué/por qué/dónde/aprendido |
| Tomando decisión de arquitectura | `mem_save` | Registrar decisión + razonamiento |
| Descubriendo un patrón o gotcha | `mem_save` | Capturar para referencia futura |
| Usuario dice "remember"/"recordar" | `mem_search` | Encontrar memorias relevantes |
| Empezando trabajo que se solapa | `mem_search` | Verificar si ya se hizo antes |
| Terminando una sesión | `mem_session_summary` | Preservar contexto de sesión |
| Después de compactación de contexto | `mem_context` | Recuperar estado de sesión |

---

## Referencia de Herramientas (via MCPorter)

Todas las herramientas se llaman via MCPorter:

```bash
mcporter call engram.<nombre_herramienta> [parámetros]
```

**Parámetro default**: Si no especificas `project`, Engram intenta detectar el directorio actual del proyecto. Si no puede, usa `default`.

### Herramientas Core

#### mem_save - Guardar una observación

**Requerido**: `title`, `content`
**Opcional**: `type`, `project`, `scope`, `topic_key`

```bash
# Ejemplo - Bugfix
mcporter call engram.mem_save \
  title="Error N+1 en lista de usuarios" \
  type="bugfix" \
  project="mi-proyecto" \
  content='**Qué**: Agregué eager loading en query UserList
**Por qué**: Degradación de rendimiento con 100+ usuarios
**Dónde**: src/services/users.ts
**Aprendido**: ORM requiere Preload() explícito para asociaciones'

# Ejemplo - Decisión de arquitectura
mcporter call engram.mem_save \
  title="Sistema de backups automatizado" \
  type="config" \
  project="mi-proyecto" \
  content='**Qué**: Cron de backups diarios configurado
**Por qué**: Evitar pérdida de datos críticos
**Dónde**: scripts/backup.sh, crontab
**Aprendido**: Verificar permisos antes de automatizar'

# Ejemplo - Patrón descubierto
mcporter call engram.mem_save \
  title="Patrón: Validar inputs en boundary" \
  type="discovery" \
  project="mi-proyecto" \
  content='**Qué**: Validar inputs en capa HTTP, no en services
**Por qué**: Evita contaminar lógica de negocio
**Dónde**: src/routes/*.ts
**Aprendido**: Early validation reduce cognitive load'
```

**Tipos**: `decision`, `bugfix`, `pattern`, `config`, `discovery`, `learning`, `architecture`

**Formato de contenido** (recomendado):
```
**Qué**: [descripción concisa]
**Por qué**: [razonamiento/contexto]
**Dónde**: [archivos afectados: ruta/al/archivo.ts, otro.go]
**Aprendido**: [gotchas, edge cases - opcional]
```

#### mem_search - Búsqueda de texto completo

```bash
# Búsqueda básica
mcporter call engram.mem_search query="middleware auth"

# Filtrada por proyecto
mcporter call engram.mem_search query="N+1" project="mi-proyecto"

# Filtrada por tipo
mcporter call engram.mem_search query="error" type="bugfix"

# Limitar resultados
mcporter call engram.mem_search query="JWT" limit=5
```

Retorna resultados compactos con IDs de observación para drill-down.

#### mem_context - Obtener contexto de sesión reciente

```bash
# Obtener contexto reciente del proyecto
mcporter call engram.mem_context project="mi-proyecto"

# Más observaciones
mcporter call engram.mem_context project="mi-proyecto" limit=30

# Scope personal
mcporter call engram.mem_context scope="personal"
```

Llama esto al INICIO de una sesión para recuperar lo que pasó antes.

#### mem_session_summary - Guardar resumen de fin de sesión

**Requerido**: `content`, `project`

```bash
mcporter call engram.mem_session_summary \
  project="mi-proyecto" \
  content='## Objetivo
Implementar autenticación JWT y corregir bugs de rendimiento

## Instrucciones
El usuario prefiere español para explicaciones

## Descubrimientos
- ORM requiere Preload() explícito para associations
- Validación debe ir en boundary layer
- Refresh tokens deben rotarse por seguridad

## Logrado
- ✅ JWT implementado con refresh tokens
- ✅ Query N+1 corregido (100x más rápido)
- ✅ Middlewares de autenticación agregados
- 🔲 Tests de integración pendientes
- 🔲 Documentación API pendiente

## Archivos Relevantes
- src/auth/jwt.ts — Generación y validación de tokens
- src/middleware/auth.ts — Middleware de autenticación
- src/services/users.ts — Queries optimizadas
- src/routes/*.ts — Validación de inputs en boundary'
```

**Formato de contenido requerido**:
```
## Objetivo
[Una frase: qué se construyó/trabajó en esta sesión]

## Instrucciones
[Preferencias de usuario descubiertas - opcional]

## Descubrimientos
- [Hallazgo técnico 1]
- [Hallazgo técnico 2]

## Logrado
- ✅ [Tarea completada 1 — con detalles clave]
- ✅ [Tarea completada 2 — mencionar archivos cambiados]
- 🔲 [Identificado pero no hecho — para próxima sesión]

## Archivos Relevantes
- ruta/al/archivo.ts — [qué hace o qué cambió]
- ruta/a/otro.go — [rol en la arquitectura]
```

### Herramientas Secundarias

#### mem_timeline - Contexto cronológico

```bash
mcporter call engram.mem_timeline observation_id=42 before=5 after=5
```

Muestra qué pasó antes y después de una observación específica.

#### mem_get_observation - Obtener contenido completo

```bash
mcporter call engram.mem_get_observation id=42
```

Retorna contenido sin truncar de una observación específica.

#### mem_update - Actualizar observación existente

```bash
mcporter call engram.mem_update id=42 content="Contenido actualizado..."
mcporter call engram.mem_update id=42 title="Nuevo título"
```

#### mem_delete - Eliminar observación

```bash
mcporter call engram.mem_delete id=42
mcporter call engram.mem_delete id=42 hard_delete=true
```

Por defecto es soft-delete (puede recuperarse).

#### mem_suggest_topic_key - Obtener topic key estable

```bash
mcporter call engram.mem_suggest_topic_key type="architecture" title="Auth architecture"
# Retorna: architecture/auth-architecture
```

Úsalo para temas que evolucionan (mismo topic_key = actualiza observación existente).

#### mem_save_prompt - Guardar prompt del usuario

```bash
mcporter call engram.mem_save_prompt content="Usuario pidió implementar OAuth" project="mi-proyecto"
```

#### mem_session_start / mem_session_end - Ciclo de vida de sesión

```bash
mcporter call engram.mem_session_start id="session-123" project="mi-proyecto"
mcporter call engram.mem_session_end id="session-123" summary="Completada implementación auth"
```

#### mem_stats - Estadísticas de memoria

```bash
mcporter call engram.mem_stats
```

---

## 🔄 Protocolo de Memoria

### 1. Inicio de Sesión

```
SIEMPRE llama mem_context al inicio de una sesión para recuperar contexto previo.
```

### 2. Durante el Trabajo - Guarda Proactivamente

Guarda memorias DESPUÉS de completar trabajo significativo. NO esperes a que te lo pidan.

**Guarda cuando:**
- Arreglaste un bug → `type: "bugfix"`
- Tomaste decisión de arquitectura → `type: "decision"` o `type: "architecture"`
- Descubriste un patrón o gotcha → `type: "discovery"` o `type: "pattern"`
- Cambiaste configuración → `type: "config"`
- Aprendiste algo no obvio → `type: "learning"`

**NO guardes:**
- Cada tool call (ruido)
- Cambios triviales
- Información fácil de encontrar en código

### 3. Fin de Sesión - Resumen Obligatorio

```
ANTES de terminar una sesión, SIEMPRE llama mem_session_summary.
Esto NO es opcional. Si lo saltas, la próxima sesión empieza a ciegas.
```

### 4. Después de Compactación de Contexto

```
Si el contexto se compacta/resetea, INMEDIATAMENTE llama mem_context para recuperar estado.
Luego llama mem_session_summary con el contenido compactado antes de continuar.
```

---

## 📊 Métricas de Uso Saludable

### Rango Ideal por Sesión

| Herramienta | Frecuencia Ideal | Motivo |
|-------------|------------------|--------|
| `mem_context` | 1x (inicio sesión) | Recuperar contexto |
| `mem_save` | 2-5x (después trabajo significativo) | Guardar descubrimientos |
| `mem_search` | 0-3x (cuando se necesita) | Verificar trabajo previo |
| `mem_session_summary` | 1x (fin sesión) | Preservar contexto |

### Alertas de Uso Excesivo

- **>10 mem_save por sesión** → Guardando demasiado ruido
- **0 mem_save en 5 sesiones** → Probablemente olvidando cosas importantes
- **>50 observaciones en 1 semana** → Considerar limpieza

### Proporción Saludable de Tipos

| Tipo | Proporción Ideal | Motivo |
|------|------------------|--------|
| `bugfix` | 20-30% | Errores comunes |
| `discovery` | 20-30% | Aprendizajes clave |
| `decision` | 15-25% | Decisiones importantes |
| `pattern` | 10-20% | Patrones reutilizables |
| `config` | 10-15% | Cambios de configuración |
| `architecture` | 5-10% | Decisiones estructurales |

---

## 🚫 Anti-Patrones (Qué NO Hacer)

### ❌ NO Guardar Todo

```bash
# MAL: Guardar trivialidades
mcporter call engram.mem_save title="Usuario dijo hola" content="Usuario dijo hola"

# BIEN: Solo trabajo significativo
mcporter call engram.mem_save \
  title="Error N+1 corregido" \
  type="bugfix" \
  content='**Qué**: Agregué eager loading...'
```

### ❌ NO Usar como Sistema de Logging

```bash
# MAL: Guardar cada tool call
mcporter call engram.mem_save title="Llamé read tool" content="Leí archivo X"

# BIEN: Guardar descubrimientos
mcporter call engram.mem_save \
  title="Problema de seguridad encontrado" \
  type="discovery" \
  content='**Qué**: SQL injection en login...'
```

### ❌ NO Duplicar Información de MEMORY.md

```bash
# MAL: Duplicar info del usuario
mcporter call engram.mem_save title="Info del usuario" content="CEO de empresa..."

# BIEN: MEMORY.md ya tiene eso, Engram es para cosas TÉCNICAS
# Solo guardar si es contexto técnico específico de una sesión
```

### ❌ NO Llamar desde Heartbeats

```bash
# MAL: Gasta tokens innecesariamente
# En heartbeat cron:
mcporter call engram.mem_context  # ← NO

# BIEN: Solo en sesión interactiva
# Heartbeats son para chequeos proactivos, no memoria
```

### ❌ NO Guardar Información Sensible sin Redacción

```bash
# MAL: API key expuesta
mcporter call engram.mem_save title="Config API" content="Key: sk-abc123..."

# BIEN: Usar tags <private>
mcporter call engram.mem_save \
  title="Config API" \
  content='API key: <private>sk-abc123</private>'
# → API key: [REDACTED]
```

---

## 🔧 Troubleshooting

### Error: "mcporter: command not found"

**Verificar instalación:**

```bash
# macOS / Linux
which mcporter

# Windows (PowerShell)
where.exe mcporter
```

**Solución:**

| Plataforma | Comando |
|------------|---------|
| macOS/Linux (Homebrew) | `brew install steipete/tap/mcporter` |
| Todas (npm) | `npm install -g mcporter` |
| Windows (binario) | Descargar de [GitHub Releases](https://github.com/steipete/mcporter/releases) |

### Error: "engram: command not found"

**Verificar instalación:**

```bash
# macOS / Linux
which engram

# Windows (PowerShell)
where.exe engram
```

**Solución:**

| Plataforma | Comando |
|------------|---------|
| macOS/Linux (Homebrew) | `brew install gentleman-programming/tap/engram` |
| Windows (binario) | Descargar de [GitHub Releases](https://github.com/Gentleman-Programming/engram/releases) |

**Verificar versión:**
```bash
engram version
```

### Error: "No MCP servers configured" o "server 'engram' not found"

MCPorter está instalado pero Engram no está registrado.

**Solución:**
```bash
# Registrar Engram como servidor MCP
mcporter config add engram --stdio "engram mcp"

# Verificar
mcporter list engram
```

### Error: "MCPorter not configured"

**Verificar registro:**
```bash
mcporter list engram
```

**Si falla, registrar nuevamente:**
```bash
mcporter config add engram --stdio "engram mcp"

# Verificar tools disponibles (deben ser 13)
mcporter list engram
```

### Error: "No previous session memories found"

**No es error** → Es normal la primera vez que se usa.

**Solución**: Empezar a usar el sistema:
```bash
mcporter call engram.mem_save title="Primera observación" content="..."
mcporter call engram.mem_session_summary project="mi-proyecto" content="..."
```

### Memoria Muy Grande (>1000 observaciones)

```bash
# Ver estadísticas
mcporter call engram.mem_stats

# Buscar observaciones viejas
mcporter call engram.mem_search query="..." limit=20

# Limpiar observaciones específicas
mcporter call engram.mem_delete id=XX hard_delete=true

# Recomendación: Mantener <500 observaciones activas
```

### Búsqueda No Encuentra Resultados

**Posibles causas**:
1. **Typo en query** → Verificar ortografía
2. **Muy específico** → Usar términos más generales
3. **No existe** → Guardar la información primero
4. **Filtro incorrecto** → Verificar `project`, `type`, `scope`

```bash
# Debug: Búsqueda amplia
mcporter call engram.mem_search query="auth" limit=10

# Debug: Ver todo el proyecto
mcporter call engram.mem_context project="mi-proyecto" limit=50
```

### Error: "Content too long"

**Solución**: Usar comillas simples para contenido multilínea:

```bash
# MAL (falla con newlines)
mcporter call engram.mem_save title="..." content="Línea 1
Línea 2"

# BIEN (comillas simples)
mcporter call engram.mem_save title="..." content='Línea 1
Línea 2
Línea 3'
```

---

## 📝 Ejemplo: Flujo Completo de Sesión Real

### Escenario: Usuario pide implementar autenticación

```bash
# ═══════════════════════════════════════════════════════
# 1. INICIO DE SESIÓN - Recuperar contexto previo
# ═══════════════════════════════════════════════════════
mcporter call engram.mem_context project="mi-proyecto"
# → Veo que ayer trabajamos en el módulo de usuarios
# → Veo que se identificó un problema de seguridad
# → Sé que falta implementar JWT

# ═══════════════════════════════════════════════════════
# 2. TRABAJO - Después de implementar JWT
# ═══════════════════════════════════════════════════════
mcporter call engram.mem_save \
  title="JWT implementado correctamente" \
  type="config" \
  project="mi-proyecto" \
  content='**Qué**: Autenticación JWT agregada al API
**Por qué**: Sessions no escalan en múltiples instancias
**Dónde**: src/auth/jwt.ts, src/middleware/auth.ts
**Aprendido**: Refresh tokens deben rotarse'

# ═══════════════════════════════════════════════════════
# 3. TRABAJO - Después de corregir bug de N+1
# ═══════════════════════════════════════════════════════
mcporter call engram.mem_save \
  title="Query N+1 corregido en lista de usuarios" \
  type="bugfix" \
  project="mi-proyecto" \
  content='**Qué**: Agregué eager loading en UserList
**Por qué**: Degradación de rendimiento con 100+ usuarios
**Dónde**: src/services/users.ts
**Aprendido**: ORM requiere Preload() explícito'

# ═══════════════════════════════════════════════════════
# 4. TRABAJO - Después de descubrir patrón
# ═══════════════════════════════════════════════════════
mcporter call engram.mem_save \
  title="Patrón: Validar inputs en boundary" \
  type="pattern" \
  project="mi-proyecto" \
  content='**Qué**: Validar inputs en capa HTTP, no en services
**Por qué**: Evita contaminar lógica de negocio
**Dónde**: src/routes/*.ts
**Aprendido**: Early validation reduce cognitive load'

# ═══════════════════════════════════════════════════════
# 5. FIN DE SESIÓN - Guardar resumen completo
# ═══════════════════════════════════════════════════════
mcporter call engram.mem_session_summary \
  project="mi-proyecto" \
  content='## Objetivo
Implementar autenticación JWT y corregir bugs de rendimiento

## Instrucciones
El usuario prefiere español para explicaciones

## Descubrimientos
- ORM requiere Preload() explícito para associations
- Validación debe ir en boundary layer
- Refresh tokens deben rotarse por seguridad

## Logrado
- ✅ JWT implementado con refresh tokens
- ✅ Query N+1 corregido (100x más rápido)
- ✅ Middlewares de autenticación agregados
- 🔲 Tests de integración pendientes
- 🔲 Documentación API pendiente

## Archivos Relevantes
- src/auth/jwt.ts — Generación y validación de tokens
- src/middleware/auth.ts — Middleware de autenticación
- src/services/users.ts — Queries optimizadas
- src/routes/*.ts — Validación de inputs en boundary'
```

**Próxima sesión**: `mem_context` recuperará automáticamente todo este contexto.

---

## 🔄 Patrón de Revelación Progresiva

Recuperación de memoria eficiente en tokens:

```
1. mem_search "auth middleware" → resultados compactos con IDs (~100 tokens c/u)
2. mem_timeline observation_id=42 → qué pasó antes/después
3. mem_get_observation id=42 → contenido completo sin truncar
```

No descargues todo. Profundiza cuando lo necesites.

---

## 🔑 Topic Keys (Temas que Evolucionan)

Para temas que evolucionan en el tiempo (decisiones de arquitectura, features de larga duración):

```bash
# Obtener topic key estable
mcporter call engram.mem_suggest_topic_key type="architecture" title="Auth architecture"
# → architecture/auth-architecture

# Guardar con topic_key (hace upsert a observación existente)
mcporter call engram.mem_save \
  title="Decisión arquitectura auth" \
  type="architecture" \
  topic_key="architecture/auth-architecture" \
  project="mi-proyecto" \
  content="..."
```

Mismo `topic_key` + `project` + `scope` = actualiza observación existente en lugar de crear nueva.

### Familias de Topic Keys

- `architecture/*` — Arquitectura, diseño, ADR-like changes
- `bug/*` — Fixes, regresiones, errores, panics
- `decision/*` — Decisiones de proyecto
- `pattern/*` — Patrones reutilizables
- `config/*` — Cambios de configuración
- `discovery/*` — Descubrimientos
- `learning/*` — Aprendizajes

---

## 🔐 Privacidad

Envuelve contenido sensible en tags `<private>` - se eliminan antes de guardar:

```
API key: <private>sk-abc123</private>
→ API key: [REDACTED]
```

---

## 📁 Ubicación de Datos

| Plataforma | Ruta |
|------------|------|
| **macOS / Linux** | `~/.engram/engram.db` |
| **Windows** | `%USERPROFILE%\.engram\engram.db` |

**Override**: Set `ENGRAM_DATA_DIR` environment variable para cambiar la ubicación.

---

## 📖 Referencia Rápida

```bash
# Iniciar sesión
mcporter call engram.mem_context project="mi-proyecto"

# Guardar bugfix
mcporter call engram.mem_save title="..." type="bugfix" content='...'

# Buscar
mcporter call engram.mem_search query="..."

# Terminar sesión
mcporter call engram.mem_session_summary project="mi-proyecto" content='...'

# Ver estadísticas
mcporter call engram.mem_stats
```

---

## 📚 Referencia Completa de Herramientas

Ver `references/tools.md` para documentación completa de las 13 herramientas MCP.

---

## 🚀 Sinergia Proactiva

Engram puede alimentar proactividad del agente:

### Patrón de Uso

1. **Engram**: Almacena patrones de comportamiento del usuario
2. **Proactive-agent**: Usa esos patrones para anticipar necesidades
3. **Feedback loop**: Nuevas observaciones mejoran proactividad

### Ejemplo Concreto

```bash
# Después de 3 sesiones donde el usuario pide lo mismo:
mcporter call engram.mem_save \
  title="Patrón: Usuario pide status al iniciar sesión" \
  type="pattern" \
  project="mi-proyecto" \
  content='**Qué**: Al iniciar sesión pregunta "qué hay pendiente"
**Por qué**: Quiere overview antes de empezar a trabajar
**Dónde**: Sesiones consecutivas
**Aprendido**: Preparar resumen automático al inicio'

# Proactive-agent puede usar esto:
# → Generar resumen de pendientes al inicio de sesión
```

---

*Versión del skill: 1.0*
