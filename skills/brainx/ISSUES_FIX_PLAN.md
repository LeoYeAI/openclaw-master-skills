# Plan de Fixes para BrainX V5

## Issues a resolver:

### 1. Unificar carga de dotenv (ESM vs CommonJS)
Algunos scripts usan `require('dotenv')` en archivos que podrían ser ESM. Revisa todos los archivos en `scripts/` y `lib/` y unifica el patrón de carga de variables de entorno.

Patrón correcto a usar:
```javascript
// Para CommonJS
require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

// Para ESM (hook/)
import 'dotenv/config';
// o
import dotenv from 'dotenv';
dotenv.config({ path: new URL('../.env', import.meta.url).pathname });
```

### 2. Hardcodeo de modelo en memory-distiller.js
El script `scripts/memory-distiller.js` tiene hardcodeado `gpt-4.1-mini`. Cambiar para usar env var `BRAINX_DISTILLER_MODEL` con fallback al valor actual.

Línea a cambiar:
```javascript
const DEFAULT_MODEL = process.env.BRAINX_DISTILLER_MODEL || 'gpt-4.1-mini';
```

### 3. Agregar rate limiting en llamadas OpenAI
En `lib/openai-rag.js`, la función `embed()` hace llamadas directas sin rate limiting. Agregar:
- Exponential backoff para errores 429
- Retry con máximo 3 intentos
- Delay entre llamadas si es necesario

### 4. Agregar tests unitarios
Crear `tests/unit/` con tests básicos para:
- `lib/db.js` - mock de PostgreSQL
- `lib/openai-rag.js` - mock de fetch
- `lib/brainx-phase2.js` - test de funciones puras

Usar el test runner nativo de Node.js (`node --test`) si es posible, o Jest si ya está configurado.

### 5. Agregar reintentos en hook/handler.js
El hook de auto-inyección no maneja fallos de conexión a DB. Agregar:
- Retry con backoff para queries PostgreSQL
- Fallback graceful si BrainX no está disponible
- Logging de errores sin romper el bootstrap del agente

## Entregables:
1. Archivos modificados con los fixes
2. Nuevos archivos de tests creados
3. Resumen de cambios realizados

Verifica cada cambio ejecutando los comandos relevantes para asegurar que funcionan correctamente.
