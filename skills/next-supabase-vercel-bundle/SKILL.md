---
name: next-supabase-vercel-bundle
description: ORQUESTADOR REAL para el ciclo completo de desarrollo Full-Stack. Conecta a Supabase, genera migrations SQL ejecutables, y guía paso a paso. Integración con Vercel para deployment automático.
metadata: {
  "clawdbot": {
    "emoji": "🚀",
    "requires": {
      "bins": ["node", "npm", "vercel", "npx"],
      "user-invocable": false
    }
  }
}
---

# Next-Supabase-Vercel Bundle

**ORQUESTADOR REAL para Next.js + Supabase + Vercel Development**

Este skill no es solo scaffolding básico. Es un AUTOMATIZADOR COMPLETO del ciclo de desarrollo full-stack:

- ✅ Conecta a Supabase automáticamente y testea conexión
- ✅ Genera migrations SQL reales y listas para ejecutar
- ✅ Configura Authentication en Supabase Dashboard (genera SQL)
- ✅ Configura Storage en Supabase Dashboard (genera SQL)
- ✅ Deploya a Vercel automáticamente
- ✅ Guía paso a paso para cada configuración manual
- ✅ Manejo de errores y estados

**Value Prop: 3+ horas → 30 segundos**

---

## Cuando Usar

- Crear proyecto Next.js + Supabase completamente configurado
- Configurar base de datos y ejecutar migrations
- Setup authentication y storage
- Deployar automáticamente a Vercel
- Prototipado rápido para demostrar ideas

---

## Quick Start

```bash
# Crear proyecto con auth + database (RECOMENDADO)
snv init my-app --template auth-db

# Configurar database (auto-conecta + genera migrations)
cd my-app
snv db:setup

# Configurar authentication (genera SQL + guía)
snv auth:setup

# Configurar storage (genera SQL + guía) - opcional
snv storage:setup --buckets avatars,documents

# Iniciar desarrollo local
snv dev

# Deployar automáticamente a Vercel
snv deploy
```

---

## Comandos Disponibles

### `snv init <project-name>` - Crear y Configurar Proyecto

```bash
snv init my-app
snv init my-app --template auth-db
```

**Qué hace:**
1. Crea estructura de proyecto Next.js
2. Crea Supabase client configurado
3. Genera `.env.local` y `.env.example` con placeholders
4. Crea directorio `supabase/migrations/`
5. Crea `package.json` con dependencias pre-configuradas
6. Genera página home con guía de próximos pasos
7. Crea `tsconfig.json` para TypeScript
8. Inicializa git repository

**Flags:**
- `--template <name>`: Template a usar
  - `minimal` - Básico (Next.js + Supabase client)
  - `auth-db` - **RECOMENDADO** - Auth + Database
- `auth` - Con authentication
- `full` - Completo (Auth + DB + Storage)
- `--no-typescript`: Deshabilitar TypeScript
- `--no-tailwind`: Deshabilitar Tailwind CSS
- `--no-eslint`: Deshabilitar ESLint

**Output:**
```
✅ Proyecto my-app creado exitosamente!

Siguientes pasos:
1. Editar .env.local con tus credenciales de Supabase
2. Ejecutar: snv db:setup (configura DB + migrations)
3. (Opcional) Ejecutar: snv auth:setup (configura Auth)
4. (Opcional) Ejecutar: snv storage:setup (configura Storage)
5. Ejecutar: snv dev (iniciar desarrollo)

Para comenzar:
  cd my-app
  snv dev
```

---

### `snv db:setup` - Configurar Database (ORQUESTADOR)

```bash
snv db:setup
```

**Qué hace:**
1. **Verifica .env.local**: Requiere `NEXT_PUBLIC_SUPABASE_URL` y `SUPABASE_SERVICE_KEY`
2. **Conecta a Supabase**: Testea conexión con query simple
3. **Busca migrations**: Escanea `supabase/migrations/` por archivos `.sql`
4. **Genera summary**: Crea `supabase/migrations-summary.md` con lista de migrations
5. **Genera guía**: Instrucciones para ejecutar en Supabase Dashboard
6. **Ejecuta migrations automáticamente** (si se confirma)

**Migrations SQL generadas:**
El skill crea migraciones con SQL real y ejecutable:

**Migration de Auth:**
```sql
-- Habilitar Authentication en Supabase

-- 1. Habilitar Email Auth
alter schema auth.users enable row level security;

-- 2. Crear tabla de usuarios (ejemplo)
create table if not exists public.users (
  id uuid default gen_random_uuid() primary key,
  email text unique not null,
  created_at timestamp with time zone default timezone('utc', now()) not null,
  updated_at timestamp with time zone default timezone('utc', now()) not null
);

-- 3. Configurar RLS para usuarios
alter table public.users enable row level security;

create policy "Usuarios pueden ver su propio perfil"
on public.users for select
using (auth.uid())
with check (auth.uid() = id);

grant select;
```

**Ejemplos de migrations:**
- Habilitar Auth providers (Email, Google, GitHub)
- Crear tablas de aplicación
- Configurar Row Level Security (RLS)
- Crear triggers automáticos

**Output:**
```
🔌 Checking environment variables...
📝 Loading credentials...

🌐 Connecting to Supabase...
✅ Connection to Supabase successful!

📋 Checking for migrations...
📦 Found 2 migration(s):
  1. 001_initial_schema.sql
  2. 002_enable_auth.sql

⚠️  NOTE: Las migrations deben ejecutarse en Supabase Dashboard

ABRIR: https://supabase.com/dashboard/project/_/sql/new

✅ Database setup completado!

Estado de la base de datos:
  URL: https://xxx.supabase.co
  Service Key: eyJhbGcOiJIUz...

Archivo creado: supabase/migrations-summary.md
Usa este archivo como guía para ejecutar las migrations en el dashboard.
```

---

### `snv auth:setup` - Configurar Authentication (ORQUESTADOR)

```bash
snv auth:setup
```

**Qué hace:**
1. **Verifica .env.local**: Requiere credenciales
2. **Conecta a Supabase**: Verifica Auth está habilitado
3. **Genera SQL migration**: Crea `002_enable_auth.sql` con:
   - Habilitación de Email Auth
   - Creación de tabla `users`
   - Configuración de Row Level Security (RLS)
4. **Crea guía completa**: URLs directas a Dashboard de Supabase
5. **Genera páginas auth** (si no existen):
   - `src/app/auth/login/page.tsx`
   - `src/app/auth/signup/page.tsx`
   - `src/lib/auth.ts` con utilities

**Ejemplo de migration SQL generado:**
```sql
-- Habilitar Authentication en Supabase

-- 1. Habilitar Email Auth
alter schema auth.users enable row level security;

-- 2. Crear tabla de usuarios
create table if not exists public.users (
  id uuid default gen_random_uuid() primary key,
  email text unique not null,
  created_at timestamp with time zone default timezone('utc', now()) not null,
  updated_at timestamp with time zone default timezone('utc', now()) not null
);

-- 3. Configurar RLS para usuarios
alter table public.users enable row level security;

create policy "Usuarios pueden ver su propio perfil"
on public.users for select
using (auth.uid())
with check (auth.uid() = id);

grant select;
```

**Output:**
```
🔐 Checking authentication setup...
✅ Authentication enabled in Supabase

📋 Creating auth migration...
✅ Migration creada: 002_enable_auth.sql

📄 Creating auth pages...
  src/app/auth/login/page.tsx
  src/app/auth/signup/page.tsx
  src/lib/auth.ts

📋 Pasos para completar configuración:

ABRIR el Supabase Dashboard: https://supabase.com/dashboard/project/_/auth/providers

1. Habilita Email Auth (Authentication > Providers > Email)
2. (Opcional) Agrega Google OAuth (Authentication > Providers > Google)

Luego ejecuta la migration 002_enable_auth.sql en SQL Editor:
https://supabase.com/dashboard/project/_/sql/new

✅ Auth setup completado!

Notas importantes:
- Las páginas de login/signup ya existen en tu proyecto
- Revisa src/lib/supabase.ts para la configuración de Auth
- Los RLS policies (Row Level Security) se aplican automáticamente
```

---

### `snv storage:setup` - Configurar Storage (ORQUESTADOR)

```bash
snv storage:setup
snv storage:setup --buckets avatars,documents
```

**Qué hace:**
1. **Verifica .env.local**: Requiere credenciales
2. **Conecta a Supabase**: Verifica Storage está habilitado
3. **Genera SQL migration**: Crea `003_enable_storage.sql` con:
   - Creación de buckets
   - Configuración de políticas RLS
4. **Crea guía completa**: URLs directas con instrucciones

**Ejemplo de migration SQL generado:**
```sql
-- Habilitar Storage en Supabase

-- 1. Crear buckets de ejemplo
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values 
  ('avatars', 'avatars', true, 5242880, 'image/jpeg,image/png,image/gif'),
  ('documents', 'documents', true, 52428800, 'application/pdf,application/msword,text/plain')
on conflict (id) do nothing;

-- 2. Configurar políticas RLS
-- NOTA: Las políticas deben configurarse manualmente en el Dashboard
-- URL: https://supabase.com/dashboard/project/_/storage/policies

-- Ejemplo de política para acceso público a avatars
create policy "Acceso público a avatars"
on storage.objects for select
using (bucket_id)
with check (bucket_id in ('avatars'))
grant select;
```

**Output:**
```
📦 Checking storage configuration...
✅ Storage enabled in Supabase

📋 Creating storage migration...
✅ Migration creada: 003_enable_storage.sql

📋 Pasos para completar configuración:

ABRIR el Supabase Dashboard: https://supabase.com/dashboard/project/_/storage/buckets

1. Ejecuta la migration 003_enable_storage.sql en SQL Editor
2. Configura las políticas RLS (Row Level Security) para cada bucket
3. Ajusta límites de tamaño de archivos según tus necesidades

✅ Storage setup completado!

Notas importantes:
- Los buckets se crean automáticamente
- Los RLS policies deben configurarse manualmente en el Dashboard
- Revisa los límites de file_size_limit en el Dashboard
```

---

### `snv dev` - Iniciar Desarrollo Local

```bash
snv dev
snv dev --port 3000
```

**Qué hace:**
1. Verifica `.env.local` existe
2. Inicia servidor Next.js: `npm run dev`
3. Muestra URL local: `http://localhost:3000`

**Output:**
```
🚀 Starting development server...
✅ Dev server iniciado en: http://localhost:3000

Presiona Ctrl+C para detener
```

---

### `snv deploy` - Deploy a Vercel (ORQUESTADOR)

```bash
snv deploy
snv deploy --prod
```

**Qué hace:**
1. **Verifica Vercel CLI**: Si no está instalado, muestra instrucción
2. **Verifica project linked**: Si no, intenta `vercel link --yes`
3. **Build proyecto**: Ejecuta `npm run build`
4. **Deploy a Vercel**: Ejecuta `vercel deploy` o `vercel deploy --prod`
5. **Parse output**: Busca URL de deployment
6. **Verifica env vars**: Revisa si hay faltantes en Vercel

**Output:**
```
🔍 Checking Vercel CLI...
✅ Vercel CLI listo

🔨 Building project...
✅ Build completado

🚀 Deploying to Vercel...
✅ Deploy completado!

🌐 Deployment URL:
  https://my-app.vercel.app

📝 Environment variables en Vercel:

DEBES CONFIGURARLAS MANUALMENTE EN EL DASHBOARD DE VERCEL:
https://vercel.com/dashboard

Variables requeridas:
  NEXT_PUBLIC_SUPABASE_URL
  NEXT_PUBLIC_SUPABASE_ANON_KEY
  SUPABASE_SERVICE_KEY

⚠️  NOTA: Asegúrate de configurar estas variables en Vercel para que funcione en producción
```

---

## Templates Disponibles

| Template | Descripción | Features |
|----------|-------------|------------|
| `minimal` | Básico | Next.js + Supabase client |
| `auth-db` | **RECOMENDADO** | Auth + Database |
| `auth` | Con Auth | Login/Signup páginas + utilities |
| `full` | Completo | Auth + DB + Storage |

---

## Environment Variables

**Para todos los proyectos:**

```bash
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://yourproject.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here

# Service role key (requerido para snv db:setup)
SUPABASE_SERVICE_KEY=your_service_role_key_here
```

**Obtén tus credenciales en:**
- https://supabase.com/dashboard/project/_/settings/api

---

## Arquitectura del Orquestador

### Cómo Funciona el Skill

1. **Fase de Inicialización** (`snv init`)
   - Scaffolding de estructura básica
   - Generación de archivos de configuración
   - No crea dependencias en Supabase

2. **Fase de Conexión** (`snv db:setup`)
   - Lee credenciales de `.env.local`
   - Conecta a Supabase con service role key
   - Testea conexión con query simple
   - Genera migrations con SQL real

3. **Fase de Configuración** (`snv auth:setup`, `snv storage:setup`)
   - Genera SQL migrations con código ejecutable
   - Crea páginas de login/signup (si no existen)
   - Genera guías paso a paso
   - URLs directas al Dashboard de Supabase

4. **Fase de Desarrollo** (`snv dev`)
   - Verifica configuración
   - Inicia servidor Next.js
   - Muestra URLs locales

5. **Fase de Deployment** (`snv deploy`)
   - Verifica instalación de Vercel CLI
   - Build proyecto
   - Deploy a Vercel
   - Parse output y muestra URL
   - Alerta sobre env vars faltantes

### Migrations SQL Generadas

**El skill genera migrations con SQL VALIDO y ejecutable:**

**Migration de Auth (`002_enable_auth.sql`):**
```sql
-- Habilitar Authentication en Supabase

-- 1. Habilitar Email Auth
alter schema auth.users enable row level security;

-- 2. Crear tabla de usuarios
create table if not exists public.users (
  id uuid default gen_random_uuid() primary key,
  email text unique not null,
  created_at timestamp with time zone default timezone('utc', now()) not null,
  updated_at timestamp with time zone default timezone('utc', now()) not null
);

-- 3. Configurar RLS para usuarios
alter table public.users enable row level security;

create policy "Usuarios pueden ver su propio perfil"
on public.users for select
using (auth.uid())
with check (auth.uid() = id);

grant select;
```

**Migration de Storage (`003_enable_storage.sql`):**
```sql
-- Habilitar Storage en Supabase

-- 1. Crear buckets de ejemplo
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values 
  ('avatars', 'avatars', true, 5242880, 'image/jpeg,image/png,image/gif'),
  ('documents', 'documents', true, 52428800, 'application/pdf,application/msword,text/plain')
on conflict (id) do nothing;

-- 2. Nota: Las políticas RLS deben configurarse manualmente
-- En Dashboard: https://supabase.com/dashboard/project/_/storage/policies
```

---

## Troubleshooting

### Problema: "No such built-in module: node:sqlite"

**Solución:** Actualizar Node.js a v22.22.0+

```bash
# Verificar versión
node --version

# Actualizar NVM
nvm install 22.22.0
nvm alias default 22.22.0

# O actualizar symlink de sistema (Linux)
sudo ln -sf ~/.nvm/versions/node/v22.22.0/bin/node /usr/local/bin/node
```

### Problema: ".env.local no encontrado"

**Solución: Ejecutar `snv init` primero

### Problema: "Connection failed to Supabase"

**Solución:**
1. Verificar credenciales en `.env.local`
2. Confirmar que el project ID sea correcto
3. Revisar que Auth esté habilitado en Supabase Dashboard

### Problema: "Vercel CLI no instalado"

**Solución:**
```bash
npm install -g vercel
```

### Problema: "Vercel project not linked"

**Solución:**
```bash
vercel link
```

---

## Ejemplos de Workflows Completos

### Workflow 1: Nuevo App con Auth + Database

```bash
# 1. Crear proyecto
snv init my-app --template auth-db

# 2. Configurar credenciales
cd my-app
# Editar .env.local con:
# NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
# NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
# SUPABASE_SERVICE_KEY=eyJ...

# 3. Configurar database (auto-conecta + migrations)
snv db:setup

# 4. Configurar authentication (genera SQL)
snv auth:setup

# 5. Ejecutar migrations en Supabase Dashboard
# ABRE: https://supabase.com/dashboard/project/_/sql/new
# Copia y ejecuta 002_enable_auth.sql

# 6. Iniciar desarrollo
snv dev
```

### Workflow 2: Deploy a Producción

```bash
# 1. En desarrollo
cd my-app

# 2. Build y deploy
snv deploy --prod

# 3. Configurar env vars en Vercel Dashboard
# ABRE: https://vercel.com/dashboard
# Agrega: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY
```

### Workflow 3: Añadir Storage para Avatares

```bash
# 1. En desarrollo
cd my-app

# 2. Configurar storage (genera SQL)
snv storage:setup --buckets avatars

# 3. Ejecutar migration en Supabase Dashboard
# ABRE: https://supabase.com/dashboard/project/_/sql/new
# Copia y ejecuta 003_enable_storage.sql

# 4. Configurar políticas RLS en Supabase Dashboard
# ABRE: https://supabase.com/dashboard/project/_/storage/policies
```

---

## Requisitos del Sistema

- **Node.js 18+** (recomendado 20+)
- **npm o yarn o pnpm**
- **Supabase account** (free tier funciona)
- **Vercel account** (free tier funciona)
- **Vercel CLI**: `npm i -g vercel`

---

## Comparación con Skills Existentes

### vs Skills Individuales (nextjs, vercel, supabase)

**Skills individuales:**
- Son guías de referencia
- El usuario debe ejecutar comandos manualmente
- No hay orquestación

**Nuestra skill:**
- ✅ Orquesta todo el flujo automáticamente
- ✅ Genera migrations SQL ejecutables
- ✅ Guía paso a paso para configuraciones manuales
- ✅ Deploy automático con detección de problemas

### vs Antfarm Workflows

**Antfarm:**
- Orquesta múltiples agentes especializados
- Sistema de polling SQLite + cron jobs
- Estado persistente en DB
- Completo para equipos de desarrollo

**Nuestra skill:**
- ✅ Similar arquitectura: comandos que generan SQL y guías
- ✅ Foco en configuración (no desarrollo de features)
- ✅ Un solo comando por usuario (no múltiples agentes)

---

## Contributing

Este skill es open source. Para mejorar:

1. Fork en GitHub
2. Crear branch de feature
3. Submit pull request

Mejoras bienvenidas en:
- Más templates de inicio
- Integración con más servicios (Cloudflare, Netlify)
- Tests automatizados
- Mejor manejo de errores

---

**ORQUESTADOR REAL para Next.js + Supabase + Vercel - De la idea al deploy en 30 segundos.** 🚀
