# EngramClaw 🧠

[![Skill para OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/gentleman-programming/openclaw)
[![Engram](https://img.shields.io/badge/Engram-MCP-green)](https://github.com/Gentleman-Programming/engram)

Skill de OpenClaw que integra **Engram** - sistema de memoria persistente para agentes IA.

## ¿Qué hace?

Permite que los agentes recuerden entre sesiones:
- Bugfixes y cómo se resolvieron
- Decisiones de arquitectura
- Patrones descubiertos y gotchas
- Configuraciones importantes

## Instalación

### Prerrequisitos

Este skill requiere dos binarios:

| Herramienta | Propósito | Repo |
|-------------|-----------|------|
| **MCPorter** | Cliente MCP | [steipete/mcporter](https://github.com/steipete/mcporter) |
| **Engram** | Backend de memoria | [Gentleman-Programming/engram](https://github.com/Gentleman-Programming/engram) |

### Paso 1: Instalar MCPorter

**macOS / Linux:**
```bash
brew tap steipete/tap
brew install steipete/tap/mcporter
```

**Todas las plataformas (npm):**
```bash
npm install -g mcporter
```

**Windows (binario):** Descargar de [GitHub Releases](https://github.com/steipete/mcporter/releases)

### Paso 2: Instalar Engram

**macOS / Linux:**
```bash
brew install gentleman-programming/tap/engram
```

**Windows:** Descargar de [GitHub Releases](https://github.com/Gentleman-Programming/engram/releases) y agregar al PATH

### Paso 3: Conectar

```bash
mcporter config add engram --stdio "engram mcp"
mcporter list engram  # Debe mostrar 13 herramientas
```

## Quick Start

```bash
# Inicio de sesión - recuperar contexto
mcporter call engram.mem_context project="mi-proyecto"

# Guardar un bugfix
mcporter call engram.mem_save \
  title="Query N+1 corregido" \
  type="bugfix" \
  project="mi-proyecto" \
  content='**Qué**: Agregué eager loading
**Por qué**: Performance degradado con 100+ registros
**Dónde**: src/services/users.ts
**Aprendido**: ORM requiere Preload() explícito'

# Buscar en memoria
mcporter call engram.mem_search query="auth"

# Fin de sesión - guardar resumen
mcporter call engram.mem_session_summary \
  project="mi-proyecto" \
  content='## Objetivo
Implementar autenticación JWT
...'
```

## Características

| Característica | Descripción |
|----------------|-------------|
| **Multiplataforma** | macOS, Linux, Windows |
| **Memoria curada** | El agente decide qué guardar, no captura automática |
| **Revelación progresiva** | Search → Timeline → Full content (eficiente en tokens) |
| **Búsqueda FTS5** | Full-text search en SQLite |
| **13 herramientas MCP** | CRUD + session lifecycle + stats |
| **Integración OpenClaw** | Complementa MEMORY.md y memory/YYYY-MM-DD.md |

## Cuándo Usar

| Disparador | Herramienta |
|------------|-------------|
| Inicio de sesión | `mem_context` |
| Después de bugfix/decisión | `mem_save` |
| Usuario dice "recuerda" | `mem_search` |
| Fin de sesión | `mem_session_summary` |

## Estructura

```
EngramClaw/
├── SKILL.md          # Instrucciones completas del skill
├── references/
│   └── tools.md      # Referencia de las 13 herramientas MCP
└── README.md         # Este archivo
```

## Documentación

- **[SKILL.md](./SKILL.md)** - Guía completa: protocolo de memoria, anti-patrones, troubleshooting
- **[references/tools.md](./references/tools.md)** - Referencia de todas las herramientas MCP

## Ecosistema OpenClaw

```
MEMORY.md (estático) → memory/YYYY-MM-DD.md (diario) → Engram (técnico) → self-improving (comportamiento)
```

| Tipo de info | Dónde guardar |
|--------------|---------------|
| Info permanente del usuario | MEMORY.md |
| Notas del día | memory/YYYY-MM-DD.md |
| Bugfix técnico | Engram |
| Correcciones de comportamiento | self-improving |

## Licencia

MIT

## Links

- [Engram](https://github.com/Gentleman-Programming/engram) - Backend de memoria
- [OpenClaw](https://github.com/gentleman-programming/openclaw) - Framework de agentes
