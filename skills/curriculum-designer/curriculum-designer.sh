#!/bin/bash

# Curriculum Designer Skill
# Staged implementation with checkpointing for better reliability and debuggability

set -e

# Source checkpoint helpers
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../../scripts/checkpoint-helpers.sh"

# Configuration
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GOG_FOLDER_ID="1upJQu-IVmZRJQsNGmJNRzq9IwL67MVL9"
SESSION_ID="${SESSION_ID:-$(uuidgen 2>/dev/null || echo "manual-$(date +%s)")}"

# Initialize checkpoint session
SESSION_DIR=$(checkpoint_init "$SESSION_ID")
echo "🚀 Starting curriculum designer session: $SESSION_ID"
echo "📂 Checkpoint directory: $SESSION_DIR"
echo ""

# =============================================================================
# STAGE 1: Gather Requirements
# =============================================================================
stage_requirements() {
    local session_dir="$1"

    if checkpoint_exists "$session_dir" "requirements"; then
        echo "✓ Stage 1: Requirements already exist, loading..."
        checkpoint_load "$session_dir" "requirements"
        return 0
    fi

    echo "📋 Stage 1: Collecting requirements..."
    echo ""

    # This would normally be interactive with the user
    # For now, we'll collect via questions
    local pod_name
    local target_audience
    local subject_areas
    local duration
    local frequency
    local daily_lab_hours
    local previous_exposure
    local teacher_capability
    local teacher_training_needed
    local learning_area_focus
    local specific_skills
    local assessment_method

    # In a real implementation, these would be collected from user input
    # For now, we'll create a template structure
    cat > "${session_dir}/requirements.json" <<EOF
{
  "pod_name": "Unknown",
  "target_audience": "Unknown",
  "subject_areas": [],
  "duration": "1 month",
  "frequency": "3 days/week",
  "daily_lab_hours": 2,
  "previous_exposure": "None",
  "teacher_capability": "Basic",
  "teacher_training_needed": true,
  "learning_area_focus": ["Digital Literacy", "Academic Empowerment"],
  "specific_skills": [],
  "assessment_method": "Practical exercises and quizzes"
}
EOF

    echo "✓ Requirements template created"
    echo "⚠️  Edit $(basename $session_dir)/requirements.json with actual requirements"

    checkpoint_load "$session_dir" "requirements"
}

# =============================================================================
# STAGE 2: Research Resources
# =============================================================================
stage_research() {
    local session_dir="$1"
    local requirements="$2"

    if checkpoint_exists "$session_dir" "research-results"; then
        echo "✓ Stage 2: Research results already exist, loading..."
        checkpoint_load "$session_dir" "research-results"
        return 0
    fi

    echo "🔍 Stage 2: Researching resources..."
    echo ""

    # Load YouTube API key
    local env_file="$HOME/.openclaw/workspace/skills/curriculum-designer/.env"
    local youtube_api_key=""

    if [ -f "$env_file" ]; then
        youtube_api_key=$(grep YOUTUBE_API_KEY "$env_file" 2>/dev/null | cut -d= -f2)
    fi

    if [ -z "$youtube_api_key" ]; then
        echo "⚠️  YouTube API key not found in .env file"
        echo "⚠️  Skipping YouTube search, returning empty results"
        echo '{"resources": []}' > "${session_dir}/research-results.json"
        return 0
    fi

    # Extract subjects from requirements
    local subjects=$(echo "$requirements" | python3 -c "import sys, json; print(','.join(json.load(sys.stdin).get('subject_areas', [])))" 2>/dev/null || echo "")

    # Search function
    search_youtube() {
        local query="$1"
        local api_key="$2"

        local result=$(curl -s "https://www.googleapis.com/youtube/v3/search?part=snippet&q=${query}+tutorial+hindi+beginners&type=video&maxResults=5&videoDuration=medium&key=${api_key}" 2>/dev/null)

        echo "$result" | python3 <<EOF
import sys, json
try:
    data = json.load(sys.stdin)
    items = data.get('items', [])
    resources = []
    for item in items[:3]:
        video_id = item.get('id', {}).get('videoId')
        title = item.get('snippet', {}).get('title')
        channel = item.get('snippet', {}).get('channelTitle')
        if video_id and title:
            resources.append({
                "title": title,
                "channel": channel,
                "url": f"https://youtube.com/watch?v={video_id}",
                "video_id": video_id
            })
    print(json.dumps({"topic": "${query}", "videos": resources}, indent=2))
except Exception as e:
    print(json.dumps({"error": str(e)}), file=sys.stderr)
    print(json.dumps({"topic": "${query}", "videos": []}))
EOF
    }

    # Search for common topics
    local queries=(
        "computer basics"
        "typing practice"
        "internet browser basics"
        "gmail email tutorial"
        "google docs tutorial"
        "google sheets tutorial"
        "chatgpt tutorial"
        "ai tools for students"
    )

    local all_results='{"resources": []}'

    for query in "${queries[@]}"; do
        echo "  Searching: $query"
        local result=$(search_youtube "$query" "$youtube_api_key")
        echo "$result" >> "${session_dir}/search-results-$(echo $query | tr ' ' '-').json"
    done

    # Combine all results
    python3 <<EOF
import json
import glob
import os

all_resources = []
search_dir = "${session_dir}"

pattern = os.path.join(search_dir, "search-results-*.json")
for file_path in glob.glob(pattern):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            videos = data.get('videos', [])
            all_resources.extend(videos)
    except:
        pass

print(json.dumps({"resources": all_resources}, indent=2))
EOF > "${session_dir}/research-results.json"

    echo "✓ Research complete: $(ls ${session_dir}/search-results-*.json 2>/dev/null | wc -l) searches performed"

    checkpoint_load "$session_dir" "research-results"
}

# =============================================================================
# STAGE 3: Validate Resources
# =============================================================================
stage_validate() {
    local session_dir="$1"
    local research="$2"

    if checkpoint_exists "$session_dir" "validated-resources"; then
        echo "✓ Stage 3: Validated resources already exist, loading..."
        checkpoint_load "$session_dir" "validated-resources"
        return 0
    fi

    echo "✅ Stage 3: Validating resources..."
    echo ""

    # Use oEmbed for validation
    validate_video() {
        local video_url="$1"

        local oembed_url="https://www.youtube.com/oembed?url=${video_url}&format=json"
        local response=$(curl -s -o /dev/null -w "%{http_code}" "$oembed_url")

        if [ "$response" = "200" ]; then
            echo "valid"
        else
            echo "invalid"
        fi
    }

    # Validate all resources
    python3 <<EOF
import json
import subprocess

# Load research results
with open("${session_dir}/research-results.json", 'r') as f:
    research = json.load(f)

resources = research.get('resources', [])
validated = []

for resource in resources:
    url = resource.get('url')
    title = resource.get('title')

    # Validate via oEmbed
    result = subprocess.run(
        ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
         f'https://www.youtube.com/oembed?url={url}&format=json'],
        capture_output=True, text=True
    )

    if result.stdout.strip() == '200':
        resource['status'] = 'valid'
        validated.append(resource)
        print(f"  ✓ Valid: {title}")
    else:
        resource['status'] = 'invalid'
        print(f"  ✗ Invalid: {title}")

print(json.dumps({"resources": validated, "invalid_count": len(resources) - len(validated)}, indent=2))
EOF > "${session_dir}/validated-resources.json"

    echo "✓ Validation complete"

    checkpoint_load "$session_dir" "validated-resources"
}

# =============================================================================
# STAGE 4: Design Curriculum
# =============================================================================
stage_design() {
    local session_dir="$1"
    local validated="$2"
    local requirements="$3"

    if checkpoint_exists "$session_dir" "curriculum-structure"; then
        echo "✓ Stage 4: Curriculum structure already exists, loading..."
        checkpoint_load "$session_dir" "curriculum-structure"
        return 0
    fi

    echo "📚 Stage 4: Designing curriculum structure..."
    echo ""

    # This would normally call an LLM to generate the curriculum structure
    # For now, we'll create a template structure based on the validated resources

    python3 <<EOF
import json

# Load requirements
with open("${session_dir}/requirements.json", 'r') as f:
    requirements = json.load(f)

# Load validated resources
with open("${session_dir}/validated-resources.json", 'r') as f:
    validated = json.load(f)

resources = validated.get('resources', [])
duration = requirements.get('duration', '1 month')
frequency = requirements.get('frequency', '3 days/week')

# Estimate number of sessions (simplified)
sessions = 12

# Create curriculum structure
curriculum = {
    "curriculum_id": f"CUR-{requirements.get('pod_name', 'UNKNOWN')}-{duration.replace(' ', '-').lower()}",
    "pod_name": requirements.get('pod_name', 'Unknown POD'),
    "duration": duration,
    "frequency": frequency,
    "total_sessions": sessions,
    "learning_areas": requirements.get('learning_area_focus', []),
    "sessions": []
}

# Create session entries
for i in range(1, sessions + 1):
    # Distribute resources across sessions
    if resources and i <= len(resources):
        resource = resources[i-1]
        video_url = resource.get('url')
        video_title = resource.get('title')
    else:
        video_url = ""
        video_title = "No video assigned"

    session = {
        "day": i,
        "subject": curriculum['learning_areas'][i % len(curriculum['learning_areas'])] if curriculum['learning_areas'] else "General",
        "module": f"Module {i}: Digital Skills",
        "daily_learning_objectives": "Basic computer operations and digital literacy skills",
        "daily_assessment": "Practical exercises and observation",
        "youtube_link": video_url,
        "youtube_title": video_title,
        "tools_used": "Computer, Internet Browser"
    }

    curriculum['sessions'].append(session)

print(json.dumps(curriculum, indent=2))
EOF > "${session_dir}/curriculum-structure.json"

    echo "✓ Curriculum structure created with $sessions sessions"

    checkpoint_load "$session_dir" "curriculum-structure"
}

# =============================================================================
# STAGE 5: Create Sheet
# =============================================================================
stage_sheet() {
    local session_dir="$1"
    local structure="$2"

    if checkpoint_exists "$session_dir" "final-sheet-url"; then
        echo "✓ Stage 5: Sheet already created, loading URL..."
        checkpoint_load_text "$session_dir" "final-sheet-url"
        return 0
    fi

    echo "📊 Stage 5: Creating Google Sheet..."
    echo ""

    # Load curriculum structure
    python3 <<EOF
import json

with open("${session_dir}/curriculum-structure.json", 'r') as f:
    curriculum = json.load(f)

# Create sheet data
sheet_data = []

# Header row
sheet_data.append([
    "Day",
    "Subject",
    "Module",
    "Daily Learning Objectives",
    "Daily Assessment",
    "YouTube Link",
    "YouTube Title",
    "Tools Used"
])

# Data rows
for session in curriculum.get('sessions', []):
    sheet_data.append([
        session.get('day', ''),
        session.get('subject', ''),
        session.get('module', ''),
        session.get('daily_learning_objectives', ''),
        session.get('daily_assessment', ''),
        session.get('youtube_link', ''),
        session.get('youtube_title', ''),
        session.get('tools_used', '')
    ])

# Save as CSV for easier import
import csv
with open("${session_dir}/curriculum-sheet.csv", 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(sheet_data)

print(f"CSV file created with {len(sheet_data) - 1} data rows")
EOF

    echo "⚠️  Sheet CSV created at: $(basename $session_dir)/curriculum-sheet.csv"
    echo "⚠️  Manual upload to Google Sheets required (gog integration pending)"

    # For now, return placeholder URL
    local placeholder_url="https://docs.google.com/spreadsheets/d/PENDING_MANUAL_UPLOAD"
    echo "$placeholder_url" > "${session_dir}/final-sheet-url.txt"

    checkpoint_load_text "$session_dir" "final-sheet-url"
}

# =============================================================================
# MAIN EXECUTION FLOW
# =============================================================================
main() {
    echo "=========================================="
    echo "   Curriculum Designer - Checkpoint Mode   "
    echo "=========================================="
    echo ""

    # Stage 1: Requirements
    local requirements=$(stage_requirements "$SESSION_DIR")
    echo ""

    # Stage 2: Research
    local research=$(stage_research "$SESSION_DIR" "$requirements")
    echo ""

    # Stage 3: Validation
    local validated=$(stage_validate "$SESSION_DIR" "$research")
    echo ""

    # Stage 4: Design
    local structure=$(stage_design "$SESSION_DIR" "$validated" "$requirements")
    echo ""

    # Stage 5: Sheet
    local sheet_url=$(stage_sheet "$SESSION_DIR" "$structure")
    echo ""

    # Complete the session
    echo "=========================================="
    echo "   ✅ Curriculum Design Complete!         "
    echo "=========================================="
    echo ""
    echo "📊 Sheet URL: $sheet_url"
    echo "📂 Checkpoint directory: $SESSION_DIR"
    echo ""

    # Mark session as completed but keep the checkpoint for review
    checkpoint_complete "$SESSION_DIR" # No --destroy flag - keeps checkpoint

    return 0
}

# Run main function
main "$@"
