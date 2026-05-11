#!/usr/bin/env bash
# trackers.sh - Unified multi-tracker interface
# Usage: trackers.sh <command> [options]
#
# Commands:
#   setup                           - Interactive setup wizard
#   status                          - Show configured trackers
#   sync <source> <target>          - Sync between trackers
#   export <tracker> [format]       - Export data (json, csv)
#   import <tracker> <file>         - Import from file
#   compare <tracker1> <tracker2>   - Compare watch histories
#   profile <tracker> [username]    - Show profile on any tracker
#
# Supported trackers: trakt, letterboxd, simkl, plex

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

show_help() {
  head -n 18 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Command: setup
cmd_setup() {
  echo "🔧 Media Tracker Setup Wizard"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "This wizard will help you configure media tracking services."
  echo ""
  
  # Check which trackers are available
  echo "Available trackers:"
  echo "  1. Trakt.tv (full integration)"
  echo "  2. Simkl (full integration)"
  echo "  3. Letterboxd (export/import only)"
  echo "  4. TV Time (export/import only)"
  echo "  5. Traktarr (Trakt → Radarr/Sonarr automation)"
  echo "  6. Retraktarr (Radarr/Sonarr → Trakt sync)"
  echo ""
  
  echo "Which tracker would you like to configure?"
  echo -n "Enter number (1-6): "
  read -r choice
  
  case "$choice" in
    1)
      echo ""
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "Configuring Trakt.tv"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo ""
      
      if [[ -f "$SCRIPT_DIR/trakt.sh" ]]; then
        bash "$SCRIPT_DIR/trakt.sh" auth
        
        echo ""
        echo "Testing connection..."
        bash "$SCRIPT_DIR/trakt.sh" auth-status
        
        echo "✅ Trakt.tv setup complete!"
      else
        echo "❌ trakt.sh not found"
        exit 1
      fi
      ;;
      
    2)
      echo ""
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "Configuring Simkl"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo ""
      
      if [[ -f "$SCRIPT_DIR/simkl.sh" ]]; then
        bash "$SCRIPT_DIR/simkl.sh" auth
        echo "✅ Simkl setup complete!"
      else
        echo "❌ simkl.sh not found"
        exit 1
      fi
      ;;
      
    3)
      echo ""
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "Letterboxd Configuration"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo ""
      echo "Letterboxd requires API approval for direct integration."
      echo "For now, you can use export/import functionality:"
      echo ""
      echo "  Export from Plex:"
      echo "    trackers.sh export letterboxd"
      echo ""
      echo "  Import to Letterboxd:"
      echo "    1. Go to letterboxd.com/settings/import"
      echo "    2. Upload the generated CSV file"
      echo ""
      echo "✅ Letterboxd info displayed"
      ;;
      
    4)
      echo ""
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "TV Time Configuration"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo ""
      echo "TV Time does not have a public API."
      echo ""
      echo "To export from TV Time:"
      echo "  1. Go to tvtime.com/export"
      echo "  2. Download your CSV export"
      echo "  3. Use: trackers.sh import tvtime <file.csv>"
      echo ""
      echo "✅ TV Time info displayed"
      ;;
      
    5)
      echo ""
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "Traktarr Setup (Trakt → Radarr/Sonarr)"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo ""
      
      # Check if traktarr is installed
      if command -v traktarr &> /dev/null || [[ -f "$HOME/.local/bin/traktarr" ]]; then
        echo "✅ Traktarr found"
        echo ""
        bash "$SCRIPT_DIR/trakt.sh" traktarr-status
        echo ""
        echo "Configure traktarr? (y/n)"
        read -r configure
        
        if [[ "$configure" == "y" ]]; then
          bash "$SCRIPT_DIR/trakt.sh" traktarr-config
        fi
      else
        echo "⚠️  Traktarr not found"
        echo ""
        echo "Traktarr automatically adds content from Trakt lists to Radarr/Sonarr."
        echo ""
        echo "Install traktarr? (y/n)"
        read -r install
        
        if [[ "$install" == "y" ]]; then
          echo ""
          echo "Installing traktarr via pip..."
          
          if command -v pip3 &> /dev/null; then
            pip3 install --user traktarr
          elif command -v pip &> /dev/null; then
            pip install --user traktarr
          else
            echo "❌ pip not found. Install Python first."
            exit 1
          fi
          
          echo ""
          echo "✅ Traktarr installed"
          echo ""
          echo "Now configuring..."
          bash "$SCRIPT_DIR/trakt.sh" traktarr-config
        else
          echo ""
          echo "Manual installation:"
          echo "  pip install traktarr"
          echo ""
          echo "Then run: trackers.sh setup (option 5)"
        fi
      fi
      
      echo ""
      echo "✅ Traktarr setup complete"
      ;;
      
    6)
      echo ""
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo "Retraktarr Setup (Radarr/Sonarr → Trakt)"
      echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      echo ""
      
      # Check if retraktarr is installed
      if command -v retraktarr &> /dev/null || [[ -f "$HOME/.local/bin/retraktarr" ]]; then
        echo "✅ Retraktarr found"
        echo ""
        bash "$SCRIPT_DIR/trakt.sh" retraktarr-status
        echo ""
        echo "Configure retraktarr? (y/n)"
        read -r configure
        
        if [[ "$configure" == "y" ]]; then
          bash "$SCRIPT_DIR/trakt.sh" retraktarr-config
        fi
      else
        echo "⚠️  Retraktarr not found"
        echo ""
        echo "Retraktarr syncs your Radarr/Sonarr library to Trakt lists."
        echo ""
        echo "Install retraktarr? (y/n)"
        read -r install
        
        if [[ "$install" == "y" ]]; then
          echo ""
          echo "Installing retraktarr via pip..."
          
          if command -v pip3 &> /dev/null; then
            pip3 install --user retraktarr
          elif command -v pip &> /dev/null; then
            pip install --user retraktarr
          else
            echo "❌ pip not found. Install Python first."
            exit 1
          fi
          
          echo ""
          echo "✅ Retraktarr installed"
          echo ""
          echo "Now configuring..."
          bash "$SCRIPT_DIR/trakt.sh" retraktarr-config
        else
          echo ""
          echo "Manual installation:"
          echo "  pip install retraktarr"
          echo ""
          echo "Then run: trackers.sh setup (option 6)"
        fi
      fi
      
      echo ""
      echo "✅ Retraktarr setup complete"
      ;;
      
    *)
      echo "❌ Invalid choice"
      exit 1
      ;;
  esac
  
  echo ""
}

# Command: status
cmd_status() {
  echo "📊 Tracker Configuration Status"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Check Trakt
  echo -n "Trakt.tv:      "
  if [[ -f "$HOME/.config/clawarr/trakt_tokens.json" ]]; then
    if bash "$SCRIPT_DIR/trakt.sh" auth-status > /dev/null 2>&1; then
      echo "✅ Authenticated"
    else
      echo "⚠️  Configured but expired"
    fi
  else
    echo "❌ Not configured"
  fi
  
  # Check Simkl
  echo -n "Simkl:         "
  if [[ -f "$HOME/.config/clawarr/simkl_tokens.json" ]]; then
    echo "✅ Authenticated"
  else
    echo "❌ Not configured"
  fi
  
  # Check Letterboxd
  echo -n "Letterboxd:    "
  if [[ -n "${LETTERBOXD_API_KEY:-}" ]]; then
    echo "✅ API key configured"
  else
    echo "⚠️  Export/import only (no API key)"
  fi
  
  # Check TV Time
  echo "TV Time:       ⚠️  Export/import only (no API)"
  
  echo ""
  
  # Check Plex/Tautulli for syncing
  echo -n "Plex:          "
  if [[ -n "${PLEX_TOKEN:-}" ]]; then
    echo "✅ Token configured"
  else
    echo "❌ Not configured"
  fi
  
  echo -n "Tautulli:      "
  if [[ -n "${TAUTULLI_KEY:-}" ]]; then
    echo "✅ API key configured"
  else
    echo "❌ Not configured"
  fi
  
  echo ""
  
  # Check Traktarr
  echo -n "Traktarr:      "
  if command -v traktarr &> /dev/null || [[ -f "$HOME/.local/bin/traktarr" ]]; then
    if [[ -f "$HOME/.config/traktarr/config.json" ]]; then
      echo "✅ Installed and configured"
    else
      echo "⚠️  Installed but not configured"
    fi
  else
    echo "❌ Not installed"
  fi
  
  echo -n "Retraktarr:    "
  if command -v retraktarr &> /dev/null || [[ -f "$HOME/.local/bin/retraktarr" ]]; then
    if [[ -f "$HOME/.config/retraktarr/config.json" ]]; then
      echo "✅ Installed and configured"
    else
      echo "⚠️  Installed but not configured"
    fi
  else
    echo "❌ Not installed"
  fi
  
  echo ""
}

# Command: sync
cmd_sync() {
  local source="${1:-}"
  local target="${2:-}"
  
  if [[ -z "$source" ]] || [[ -z "$target" ]]; then
    echo "Usage: trackers.sh sync <source> <target>"
    echo ""
    echo "Examples:"
    echo "  trackers.sh sync plex trakt"
    echo "  trackers.sh sync trakt letterboxd"
    echo "  trackers.sh sync trakt simkl"
    exit 1
  fi
  
  echo "🔄 Syncing: $source → $target"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  case "$source-$target" in
    plex-trakt)
      if [[ -f "$SCRIPT_DIR/trakt.sh" ]]; then
        bash "$SCRIPT_DIR/trakt.sh" sync-plex
      else
        echo "❌ trakt.sh not found"
        exit 1
      fi
      ;;
      
    trakt-letterboxd)
      echo "Exporting Trakt history for Letterboxd..."
      
      # Export from Trakt
      local temp_file
      temp_file=$(mktemp)
      bash "$SCRIPT_DIR/trakt.sh" sync-history export "$temp_file"
      
      # Convert to Letterboxd CSV
      local output_file="letterboxd_import_$(date +%Y%m%d_%H%M%S).csv"
      bash "$SCRIPT_DIR/letterboxd.sh" export-from-trakt "$temp_file" "$output_file"
      
      rm -f "$temp_file"
      
      echo ""
      echo "✅ Export ready: $output_file"
      echo "   Upload at: letterboxd.com/settings/import"
      ;;
      
    trakt-simkl)
      echo "❌ Trakt → Simkl sync not yet implemented"
      echo "   (Requires custom matching logic)"
      exit 1
      ;;
      
    *)
      echo "❌ Unsupported sync path: $source → $target"
      echo ""
      echo "Supported paths:"
      echo "  • plex → trakt"
      echo "  • trakt → letterboxd"
      exit 1
      ;;
  esac
}

# Command: export
cmd_export() {
  local tracker="${1:-}"
  local format="${2:-json}"
  
  if [[ -z "$tracker" ]]; then
    echo "Usage: trackers.sh export <tracker> [format]"
    echo "Trackers: trakt, letterboxd, plex"
    echo "Formats: json, csv (default: json)"
    exit 1
  fi
  
  local output_file="${tracker}_export_$(date +%Y%m%d_%H%M%S).$format"
  
  echo "📤 Exporting from $tracker"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  case "$tracker" in
    trakt)
      if [[ "$format" == "json" ]]; then
        bash "$SCRIPT_DIR/trakt.sh" sync-history export "$output_file"
      else
        echo "❌ Trakt only supports JSON export"
        exit 1
      fi
      ;;
      
    letterboxd)
      if [[ "$format" == "csv" ]]; then
        bash "$SCRIPT_DIR/letterboxd.sh" export "$output_file"
      else
        echo "❌ Letterboxd only supports CSV export"
        exit 1
      fi
      ;;
      
    plex)
      echo "❌ Direct Plex export not implemented"
      echo "   Use: trackers.sh sync plex trakt"
      exit 1
      ;;
      
    *)
      echo "❌ Unknown tracker: $tracker"
      exit 1
      ;;
  esac
}

# Command: import
cmd_import() {
  local tracker="${1:-}"
  local file="${2:-}"
  
  if [[ -z "$tracker" ]] || [[ -z "$file" ]]; then
    echo "Usage: trackers.sh import <tracker> <file>"
    exit 1
  fi
  
  if [[ ! -f "$file" ]]; then
    echo "❌ File not found: $file"
    exit 1
  fi
  
  echo "📥 Importing to $tracker"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  case "$tracker" in
    trakt)
      bash "$SCRIPT_DIR/trakt.sh" sync-history import "$file"
      ;;
      
    letterboxd)
      bash "$SCRIPT_DIR/letterboxd.sh" import "$file"
      ;;
      
    tvtime)
      echo "❌ TV Time import not yet implemented"
      exit 1
      ;;
      
    *)
      echo "❌ Unknown tracker: $tracker"
      exit 1
      ;;
  esac
}

# Command: compare
cmd_compare() {
  local tracker1="${1:-}"
  local tracker2="${2:-}"
  
  if [[ -z "$tracker1" ]] || [[ -z "$tracker2" ]]; then
    echo "Usage: trackers.sh compare <tracker1> <tracker2>"
    exit 1
  fi
  
  echo "🔍 Comparing: $tracker1 vs $tracker2"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Export both to temp files
  local temp1
  temp1=$(mktemp)
  local temp2
  temp2=$(mktemp)
  
  echo "Fetching data from $tracker1..."
  case "$tracker1" in
    trakt)
      bash "$SCRIPT_DIR/trakt.sh" sync-history export "$temp1" > /dev/null 2>&1
      ;;
    *)
      echo "❌ Tracker not supported for comparison: $tracker1"
      rm -f "$temp1" "$temp2"
      exit 1
      ;;
  esac
  
  echo "Fetching data from $tracker2..."
  case "$tracker2" in
    trakt)
      bash "$SCRIPT_DIR/trakt.sh" sync-history export "$temp2" > /dev/null 2>&1
      ;;
    *)
      echo "❌ Tracker not supported for comparison: $tracker2"
      rm -f "$temp1" "$temp2"
      exit 1
      ;;
  esac
  
  echo ""
  echo "Analyzing differences..."
  echo ""
  
  # Compare item counts
  local count1
  count1=$(jq 'length' "$temp1")
  local count2
  count2=$(jq 'length' "$temp2")
  
  echo "Total items:"
  echo "  $tracker1: $count1"
  echo "  $tracker2: $count2"
  echo ""
  
  # Compare movie counts
  local movies1
  movies1=$(jq '[.[] | select(.type == "movie")] | length' "$temp1")
  local movies2
  movies2=$(jq '[.[] | select(.type == "movie")] | length' "$temp2")
  
  echo "Movies:"
  echo "  $tracker1: $movies1"
  echo "  $tracker2: $movies2"
  echo ""
  
  # Compare episode counts
  local episodes1
  episodes1=$(jq '[.[] | select(.type == "episode")] | length' "$temp1")
  local episodes2
  episodes2=$(jq '[.[] | select(.type == "episode")] | length' "$temp2")
  
  echo "Episodes:"
  echo "  $tracker1: $episodes1"
  echo "  $tracker2: $episodes2"
  echo ""
  
  # Find items in tracker1 but not tracker2
  echo "Items in $tracker1 but not $tracker2:"
  local diff_count
  diff_count=$(jq -s --argjson data1 "$(cat "$temp1")" --argjson data2 "$(cat "$temp2")" '
    ($data1 | map(.movie.title // .show.title) | unique) - ($data2 | map(.movie.title // .show.title) | unique) | length
  ' <<< '[]')
  
  echo "  Approximately $diff_count unique titles"
  echo ""
  
  rm -f "$temp1" "$temp2"
}

# Command: profile
cmd_profile() {
  local tracker="${1:-}"
  local username="${2:-}"
  
  if [[ -z "$tracker" ]]; then
    echo "Usage: trackers.sh profile <tracker> [username]"
    exit 1
  fi
  
  case "$tracker" in
    trakt)
      bash "$SCRIPT_DIR/trakt.sh" profile "$username"
      ;;
      
    letterboxd)
      if [[ -z "$username" ]]; then
        echo "Usage: trackers.sh profile letterboxd <username>"
        exit 1
      fi
      bash "$SCRIPT_DIR/letterboxd.sh" profile "$username"
      ;;
      
    simkl)
      bash "$SCRIPT_DIR/simkl.sh" profile "$username"
      ;;
      
    *)
      echo "❌ Unknown tracker: $tracker"
      exit 1
      ;;
  esac
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  setup)       cmd_setup ;;
  status)      cmd_status ;;
  sync)        cmd_sync "${2:-}" "${3:-}" ;;
  export)      cmd_export "${2:-}" "${3:-json}" ;;
  import)      cmd_import "${2:-}" "${3:-}" ;;
  compare)     cmd_compare "${2:-}" "${3:-}" ;;
  profile)     cmd_profile "${2:-}" "${3:-}" ;;
  help|--help|-h) show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
