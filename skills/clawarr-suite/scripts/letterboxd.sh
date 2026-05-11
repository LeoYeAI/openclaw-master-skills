#!/usr/bin/env bash
# letterboxd.sh - Letterboxd integration (export/import focus)
# Usage: letterboxd.sh <command> [options]
#
# Commands:
#   export [file]                - Export from Plex/Radarr as Letterboxd CSV
#   export-from-trakt <in> <out> - Convert Trakt JSON to Letterboxd CSV
#   import <file>                - Import Letterboxd CSV to local tracking
#   profile <username>           - Scrape public profile stats
#   diary <username> [year]      - View public diary

set -euo pipefail

HOST="${CLAWARR_HOST:-}"
TAUTULLI_KEY="${TAUTULLI_KEY:-}"
RADARR_KEY="${RADARR_KEY:-}"

if ! command -v jq &> /dev/null; then
  echo "❌ Error: jq is required"
  exit 1
fi

if ! command -v curl &> /dev/null; then
  echo "❌ Error: curl is required"
  exit 1
fi

show_help() {
  head -n 12 "$0" | grep "^#" | sed 's/^# \?//'
  exit 0
}

# Command: export (from Plex/Radarr)
cmd_export() {
  local output_file="${1:-letterboxd_import_$(date +%Y%m%d_%H%M%S).csv}"
  
  echo "📤 Exporting to Letterboxd CSV: $output_file"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # CSV header (Letterboxd format)
  echo "Date,Letterboxd URI,Name,Year,Directors,Rating,Rewatch,Tags,Watched Date" > "$output_file"
  
  if [[ -n "$TAUTULLI_KEY" ]] && [[ -n "$HOST" ]]; then
    echo "Fetching watch history from Tautulli..."
    
    local history
    history=$(curl -sf "http://${HOST}:8181/api/v2?apikey=${TAUTULLI_KEY}&cmd=get_history&length=10000&media_type=movie")
    
    if [[ -z "$history" ]]; then
      echo "❌ Failed to fetch Tautulli history"
      exit 1
    fi
    
    local count
    count=$(echo "$history" | jq -r '.response.data.recordsFiltered')
    
    echo "Processing $count movies..."
    echo ""
    
    # Transform to Letterboxd CSV format
    echo "$history" | jq -r '.response.data.data[] | 
      select(.watched_status == 1) | 
      [
        (.date | tonumber | strftime("%Y-%m-%d")),
        "",
        .title,
        .year,
        "",
        "",
        "No",
        "",
        (.date | tonumber | strftime("%Y-%m-%d"))
      ] | @csv' >> "$output_file"
    
    local exported
    exported=$(wc -l < "$output_file")
    exported=$((exported - 1))  # Subtract header
    
    echo "✅ Exported $exported movies to: $output_file"
    echo ""
    echo "Upload at: https://letterboxd.com/import/"
    echo ""
    
  elif [[ -n "$RADARR_KEY" ]] && [[ -n "$HOST" ]]; then
    echo "Fetching movie library from Radarr..."
    
    local movies
    movies=$(curl -sf -H "X-Api-Key: $RADARR_KEY" "http://${HOST}:7878/api/v3/movie")
    
    if [[ -z "$movies" ]]; then
      echo "❌ Failed to fetch Radarr library"
      exit 1
    fi
    
    echo "Processing movies..."
    echo ""
    
    # Transform to Letterboxd CSV format (only movies with files)
    echo "$movies" | jq -r '.[] | 
      select(.hasFile == true) | 
      [
        (.added | split("T")[0]),
        "",
        .title,
        .year,
        "",
        "",
        "No",
        "",
        (.added | split("T")[0])
      ] | @csv' >> "$output_file"
    
    local exported
    exported=$(wc -l < "$output_file")
    exported=$((exported - 1))  # Subtract header
    
    echo "✅ Exported $exported movies to: $output_file"
    echo ""
    echo "Upload at: https://letterboxd.com/import/"
    echo ""
    
  else
    echo "❌ Neither Tautulli nor Radarr configured"
    echo ""
    echo "Set one of:"
    echo "  • TAUTULLI_KEY + CLAWARR_HOST (for watch history)"
    echo "  • RADARR_KEY + CLAWARR_HOST (for library)"
    exit 1
  fi
}

# Command: export-from-trakt
cmd_export_from_trakt() {
  local input_file="${1:-}"
  local output_file="${2:-letterboxd_from_trakt_$(date +%Y%m%d_%H%M%S).csv}"
  
  if [[ -z "$input_file" ]]; then
    echo "Usage: letterboxd.sh export-from-trakt <trakt_json> [output_csv]"
    exit 1
  fi
  
  if [[ ! -f "$input_file" ]]; then
    echo "❌ File not found: $input_file"
    exit 1
  fi
  
  echo "📤 Converting Trakt history to Letterboxd CSV"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # CSV header
  echo "Date,Letterboxd URI,Name,Year,Directors,Rating,Rewatch,Tags,Watched Date" > "$output_file"
  
  # Convert Trakt JSON to Letterboxd CSV (movies only)
  jq -r '.[] | 
    select(.type == "movie") | 
    [
      (.watched_at | split("T")[0]),
      "",
      .movie.title,
      .movie.year,
      "",
      "",
      "No",
      "",
      (.watched_at | split("T")[0])
    ] | @csv' "$input_file" >> "$output_file"
  
  local count
  count=$(wc -l < "$output_file")
  count=$((count - 1))  # Subtract header
  
  echo "✅ Converted $count movies to: $output_file"
  echo ""
  echo "Upload at: https://letterboxd.com/import/"
  echo ""
}

# Command: import
cmd_import() {
  local file="${1:-}"
  
  if [[ -z "$file" ]]; then
    echo "Usage: letterboxd.sh import <letterboxd_csv>"
    exit 1
  fi
  
  if [[ ! -f "$file" ]]; then
    echo "❌ File not found: $file"
    exit 1
  fi
  
  echo "📥 Importing Letterboxd diary"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  local local_db="$HOME/.config/clawarr/letterboxd_import.json"
  mkdir -p "$(dirname "$local_db")"
  
  # Parse CSV and convert to JSON
  local entries='[]'
  local line_num=0
  
  while IFS=, read -r date uri name year directors rating rewatch tags watched_date; do
    line_num=$((line_num + 1))
    
    # Skip header
    if [[ $line_num -eq 1 ]]; then
      continue
    fi
    
    # Clean quotes from CSV parsing
    name=$(echo "$name" | sed 's/^"//;s/"$//')
    year=$(echo "$year" | sed 's/^"//;s/"$//')
    date=$(echo "$date" | sed 's/^"//;s/"$//')
    rating=$(echo "$rating" | sed 's/^"//;s/"$//')
    
    # Create entry
    local entry
    entry=$(jq -n \
      --arg name "$name" \
      --arg year "$year" \
      --arg date "$date" \
      --arg rating "$rating" \
      '{title: $name, year: $year, watched_date: $date, rating: $rating}')
    
    entries=$(echo "$entries" | jq --argjson entry "$entry" '. + [$entry]')
  done < "$file"
  
  # Save to local DB
  echo "$entries" > "$local_db"
  
  local count
  count=$(echo "$entries" | jq 'length')
  
  echo "✅ Imported $count movies to local database"
  echo "   Saved to: $local_db"
  echo ""
}

# Command: profile
cmd_profile() {
  local username="${1:-}"
  
  if [[ -z "$username" ]]; then
    echo "Usage: letterboxd.sh profile <username>"
    exit 1
  fi
  
  echo "👤 Letterboxd Profile: $username"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  echo "Fetching public profile..."
  
  # Scrape public profile stats
  local profile_html
  profile_html=$(curl -sf "https://letterboxd.com/$username/" || echo "")
  
  if [[ -z "$profile_html" ]]; then
    echo "❌ Could not fetch profile (user may not exist or be private)"
    exit 1
  fi
  
  # Extract basic stats using grep/sed
  local films
  films=$(echo "$profile_html" | grep -o 'Films[^<]*<span[^>]*>[^<]*' | sed 's/.*<span[^>]*>//' | head -1)
  
  local this_year
  this_year=$(echo "$profile_html" | grep -o 'This year[^<]*<span[^>]*>[^<]*' | sed 's/.*<span[^>]*>//' | head -1)
  
  local lists
  lists=$(echo "$profile_html" | grep -o 'Lists[^<]*<span[^>]*>[^<]*' | sed 's/.*<span[^>]*>//' | head -1)
  
  echo "Profile: https://letterboxd.com/$username/"
  echo ""
  
  if [[ -n "$films" ]]; then
    echo "Films watched: $films"
  fi
  
  if [[ -n "$this_year" ]]; then
    echo "This year: $this_year"
  fi
  
  if [[ -n "$lists" ]]; then
    echo "Lists: $lists"
  fi
  
  echo ""
  echo "Note: Limited data available via web scraping"
  echo "      For full integration, apply for Letterboxd API access"
  echo ""
}

# Command: diary
cmd_diary() {
  local username="${1:-}"
  local year="${2:-$(date +%Y)}"
  
  if [[ -z "$username" ]]; then
    echo "Usage: letterboxd.sh diary <username> [year]"
    exit 1
  fi
  
  echo "📖 Letterboxd Diary: $username ($year)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  echo "Fetching diary..."
  
  # Scrape public diary
  local diary_html
  diary_html=$(curl -sf "https://letterboxd.com/$username/films/diary/for/$year/" || echo "")
  
  if [[ -z "$diary_html" ]]; then
    echo "❌ Could not fetch diary (user may not exist or be private)"
    exit 1
  fi
  
  # Extract diary entries (basic parsing)
  # This is very simplified - full parsing would need more robust HTML handling
  echo "Recent entries:"
  echo ""
  
  echo "$diary_html" | grep -o 'data-film-name="[^"]*"' | sed 's/data-film-name="//;s/"$//' | head -20 | while read -r film; do
    echo "  • $film"
  done
  
  echo ""
  echo "View full diary: https://letterboxd.com/$username/films/diary/for/$year/"
  echo ""
  echo "Note: Limited data available via web scraping"
  echo ""
}

# Main command router
COMMAND="${1:-help}"

case "$COMMAND" in
  export)              cmd_export "${2:-}" ;;
  export-from-trakt)   cmd_export_from_trakt "${2:-}" "${3:-}" ;;
  import)              cmd_import "${2:-}" ;;
  profile)             cmd_profile "${2:-}" ;;
  diary)               cmd_diary "${2:-}" "${3:-}" ;;
  help|--help|-h)      show_help ;;
  *)
    echo "❌ Unknown command: $COMMAND"
    echo "Run '$0 help' for usage"
    exit 1
    ;;
esac
