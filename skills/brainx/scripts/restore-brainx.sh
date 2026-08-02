#!/bin/bash
# BrainX V5 - Restore Completo
# Uso: ./restore-brainx.sh [backup_tar.gz] [opciones]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRAINX_DIR="$(dirname "$SCRIPT_DIR")"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de ayuda
print_error() { echo -e "${RED}❌ $1${NC}" >&2; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Help flag
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "🧠 BrainX V5 - Sistema de Restauración"
    echo "========================================"
    echo ""
    echo "Uso: $0 <backup_tar.gz> [--force] [--skip-db]"
    echo ""
    echo "Opciones:"
    echo "  --force    Sobrescribir archivos existentes sin preguntar"
    echo "  --skip-db  No restaurar la base de datos (solo archivos)"
    echo "  --help     Mostrar esta ayuda"
    echo ""
    echo "Ejemplo:"
    echo "  $0 brainx_v5_backup_20260309.tar.gz"
    echo "  $0 brainx_v5_backup_20260309.tar.gz --force --skip-db"
    exit 0
fi

# Verificar argumentos
if [ $# -lt 1 ]; then
    echo "Uso: $0 <backup_tar.gz> [--force] [--skip-db]"
    echo ""
    echo "Opciones:"
    echo "  --force    Sobrescribir archivos existentes sin preguntar"
    echo "  --skip-db  No restaurar la base de datos (solo archivos)"
    exit 1
fi

BACKUP_FILE="$1"
FORCE=false
SKIP_DB=false

# Parsear opciones
for arg in "${@:2}"; do
    case "$arg" in
        --force) FORCE=true ;;
        --skip-db) SKIP_DB=true ;;
    esac
done

echo "🧠 BrainX V5 - Sistema de Restauración"
echo "======================================"
echo ""

# Verificar que el archivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Archivo de backup no encontrado: $BACKUP_FILE"
    exit 1
fi

# Verificar que es un archivo tar.gz
if [[ ! "$BACKUP_FILE" =~ \.tar\.gz$ ]]; then
    print_error "El archivo debe ser un .tar.gz"
    exit 1
fi

# Extraer backup
BACKUP_DIR=$(mktemp -d)
print_info "Extrayendo backup a directorio temporal..."
tar -xzf "$BACKUP_FILE" -C "$BACKUP_DIR"

# Encontrar el directorio extraído
EXTRACTED_DIR=$(find "$BACKUP_DIR" -maxdepth 1 -type d | tail -n 1)
METADATA_FILE="$EXTRACTED_DIR/METADATA.json"

if [ ! -f "$METADATA_FILE" ]; then
    print_error "METADATA.json no encontrado en el backup"
    rm -rf "$BACKUP_DIR"
    exit 1
fi

print_success "Backup extraído"
echo ""

# Mostrar información del backup
echo "📋 Información del Backup:"
echo "   Creado: $(grep '"created_at"' "$METADATA_FILE" | cut -d'"' -f4)"
echo "   Host: $(grep '"hostname"' "$METADATA_FILE" | cut -d'"' -f4)"
echo "   Usuario: $(grep '"user"' "$METADATA_FILE" | cut -d'"' -f4)"
echo ""

# Confirmación
if [ "$FORCE" = false ]; then
    echo -n "¿Deseas continuar con la restauración? [s/N]: "
    read -r response
    if [[ ! "$response" =~ ^[Ss]$ ]]; then
        print_info "Restauración cancelada"
        rm -rf "$BACKUP_DIR"
        exit 0
    fi
fi

echo ""
echo "🔄 Iniciando restauración..."
echo ""

# 1. Restaurar base de datos
if [ "$SKIP_DB" = false ]; then
    echo "📦 1/6 Restaurando base de datos PostgreSQL..."
    
    if command -v psql >/dev/null 2>&1; then
        DB_FILE="$EXTRACTED_DIR/brainx_v5_database.sql"
        
        if [ -f "$DB_FILE" ]; then
            print_info "Archivo SQL encontrado ($(stat -c%s "$DB_FILE" | numfmt --to=iec))"
            
            # Verificar si DATABASE_URL está configurado
            if [ -f "${HOME}/.openclaw/.env" ]; then
                export $(grep -v '^#' "${HOME}/.openclaw/.env" | grep DATABASE_URL | xargs) 2>/dev/null || true
            fi
            
            if [ -z "${DATABASE_URL:-}" ]; then
                print_warning "DATABASE_URL no configurado"
                echo "   Por favor, configura DATABASE_URL en ~/.openclaw/.env antes de continuar"
                echo "   Formato: postgresql://user:pass@host:5432/brainx_v5"
                rm -rf "$BACKUP_DIR"
                exit 1
            fi
            
            # Verificar conexión
            if psql "$DATABASE_URL" -c "SELECT 1;" >/dev/null 2>&1; then
                print_info "Conexión a PostgreSQL exitosa"
                
                # Verificar si la base de datos existe
                DB_EXISTS=$(psql "$DATABASE_URL" -t -c "SELECT 1 FROM pg_database WHERE datname='brainx_v5';" 2>/dev/null | tr -d '[:space:]')
                
                if [ "$DB_EXISTS" = "1" ]; then
                    if [ "$FORCE" = false ]; then
                        print_warning "La base de datos brainx_v5 ya existe"
                        echo -n "   ¿Deseas sobrescribirla? [s/N]: "
                        read -r db_response
                        if [[ ! "$db_response" =~ ^[Ss]$ ]]; then
                            print_info "Saltando restauración de base de datos"
                        else
                            print_info "Restaurando base de datos..."
                            psql "$DATABASE_URL" < "$DB_FILE" 2>/dev/null || {
                                print_error "Error al restaurar la base de datos"
                                rm -rf "$BACKUP_DIR"
                                exit 1
                            }
                            print_success "Base de datos restaurada"
                        fi
                    else
                        print_info "Restaurando base de datos (modo force)..."
                        psql "$DATABASE_URL" < "$DB_FILE" 2>/dev/null
                        print_success "Base de datos restaurada"
                    fi
                else
                    print_info "Creando base de datos brainx_v5..."
                    psql "$DATABASE_URL" < "$DB_FILE" 2>/dev/null
                    print_success "Base de datos creada y restaurada"
                fi
            else
                print_error "No se puede conectar a PostgreSQL con DATABASE_URL"
                rm -rf "$BACKUP_DIR"
                exit 1
            fi
        else
            print_warning "Archivo SQL no encontrado en el backup"
        fi
    else
        print_warning "PostgreSQL client (psql) no disponible"
    fi
else
    print_info "Saltando restauración de base de datos (--skip-db)"
fi

echo ""

# 2. Restaurar skill de BrainX V5
echo "📄 2/6 Restaurando skill BrainX V5..."
SKILL_BACKUP="$EXTRACTED_DIR/config/brainx-v5-skill"
if [ -d "$SKILL_BACKUP" ]; then
    if [ -d "${HOME}/.openclaw/skills/brainx-v5" ]; then
        if [ "$FORCE" = true ]; then
            rm -rf "${HOME}/.openclaw/skills/brainx-v5"
            cp -r "$SKILL_BACKUP" "${HOME}/.openclaw/skills/brainx-v5"
            print_success "Skill reemplazado"
        else
            print_warning "El skill ya existe"
            echo "   Usa --force para reemplazarlo"
        fi
    else
        cp -r "$SKILL_BACKUP" "${HOME}/.openclaw/skills/brainx-v5"
        print_success "Skill restaurado"
    fi
else
    print_warning "Backup del skill no encontrado"
fi

echo ""

# 3. Restaurar hooks
echo "🪝 3/6 Restaurando hooks personalizados..."
HOOKS_BACKUP="$EXTRACTED_DIR/hooks"
if [ -d "$HOOKS_BACKUP" ]; then
    mkdir -p "${HOME}/.openclaw/hooks/internal"
    cp -r "$HOOKS_BACKUP/"* "${HOME}/.openclaw/hooks/internal/" 2>/dev/null || true
    chmod +x "${HOME}/.openclaw/hooks/internal/"* 2>/dev/null || true
    print_success "Hooks restaurados"
else
    print_info "No hay hooks en el backup"
fi

echo ""

# 4. Restaurar archivos de configuración
echo "⚙️  4/6 Restaurando configuración de OpenClaw..."

# openclaw.json (solo sección de hooks)
OPENCLAW_CONFIG="$EXTRACTED_DIR/config/openclaw.json"
if [ -f "$OPENCLAW_CONFIG" ]; then
    # Extraer configuración de hooks
    if command -v jq >/dev/null 2>&1; then
        HOOKS_CONFIG=$(jq '.hooks' "$OPENCLAW_CONFIG" 2>/dev/null)
        if [ -n "$HOOKS_CONFIG" ] && [ "$HOOKS_CONFIG" != "null" ]; then
            # Merge con configuración existente
            if [ -f "${HOME}/.openclaw/openclaw.json" ]; then
                jq --argjson hooks "$HOOKS_CONFIG" '.hooks = $hooks' \
                    "${HOME}/.openclaw/openclaw.json" > "${HOME}/.openclaw/openclaw.json.tmp"
                mv "${HOME}/.openclaw/openclaw.json.tmp" "${HOME}/.openclaw/openclaw.json"
                print_success "Configuración de hooks restaurada"
            fi
        fi
    else
        print_warning "jq no disponible, configuración de hooks no restaurada"
        echo "   Instala jq para restaurar automáticamente: sudo apt-get install jq"
    fi
else
    print_warning "Configuración de openclaw no encontrada en backup"
fi

echo ""

# 5. Restaurar brainx.md en workspaces
echo "📝 5/6 Restaurando brainx.md en workspaces..."
WORKSPACES_BACKUP="$EXTRACTED_DIR/workspaces"
if [ -d "$WORKSPACES_BACKUP" ]; then
    for file in "$WORKSPACES_BACKUP"/*_brainx.md; do
        if [ -f "$file" ]; then
            # Extraer nombre del workspace
            filename=$(basename "$file")
            ws_name=${filename%_brainx.md}
            ws_dir="${HOME}/.openclaw/${ws_name}"
            
            if [ -d "$ws_dir" ]; then
                cp "$file" "$ws_dir/brainx.md"
                echo "   ✅ Restaurado: $ws_name/brainx.md"
            else
                echo "   ⚠️  Workspace no existe: $ws_name"
            fi
        fi
    done
else
    print_info "No hay archivos brainx.md en el backup"
fi

echo ""

# 6. Restaurar wrappers
echo "🔧 6/6 Restaurando wrappers..."
WRAPPERS_BACKUP="$EXTRACTED_DIR/wrappers"
if [ -d "$WRAPPERS_BACKUP" ]; then
    for file in "$WRAPPERS_BACKUP"/*_wrapper.sh; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            ws_name=${filename%_wrapper.sh}
            ws_hooks_dir="${HOME}/.openclaw/${ws_name}/hooks"
            
            if [ -d "$ws_hooks_dir" ]; then
                cp "$file" "$ws_hooks_dir/brainx-v5-wrapper.sh"
                chmod +x "$ws_hooks_dir/brainx-v5-wrapper.sh"
                echo "   ✅ Restaurado: $ws_name/hooks/brainx-v5-wrapper.sh"
            else
                mkdir -p "$ws_hooks_dir" 2>/dev/null || true
                cp "$file" "$ws_hooks_dir/brainx-v5-wrapper.sh" 2>/dev/null || true
                chmod +x "$ws_hooks_dir/brainx-v5-wrapper.sh" 2>/dev/null || true
            fi
        fi
    done
else
    print_info "No hay wrappers en el backup"
fi

echo ""

# Limpiar
rm -rf "$BACKUP_DIR"

# Resumen final
echo "======================================"
print_success "Restauración completada!"
echo "======================================"
echo ""
echo "Pasos finales:"
echo ""
echo "1. Verifica que PostgreSQL esté corriendo:"
echo "   sudo systemctl status postgresql"
echo ""
echo "2. Verifica que las variables de entorno estén configuradas:"
echo "   cat ~/.openclaw/.env | grep -E 'DATABASE_URL|OPENAI_API_KEY'"
echo ""
echo "3. Reinicia el gateway de OpenClaw:"
echo "   openclaw restart"
echo "   # o: systemctl --user restart openclaw-gateway"
echo ""
echo "4. Verifica que BrainX V5 funciona:"
echo "   cd ~/.openclaw/skills/brainx-v5"
echo "   ./brainx health"
echo ""
echo "5. Prueba el hook de auto-inyección:"
echo "   cat ~/.openclaw/workspace-clawma/BRAINX_CONTEXT.md"
echo ""
