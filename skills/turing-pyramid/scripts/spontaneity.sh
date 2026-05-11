#!/bin/bash
# Turing Pyramid — Spontaneity Layer A: Surplus Energy System
# Sourced by run-cycle.sh — provides surplus accumulation and matrix shifting
#
# When all needs are satisfied (homeostasis), agents tend to always pick
# low-impact actions. This layer allows high-impact actions to "leak through"
# by accumulating surplus energy over time and shifting the impact matrix
# toward bigger actions when enough surplus builds up.
#
# Design: global gate (all needs >= 1.5) + per-need surplus pools
# Integration: modifies roll_impact_range() output, not a separate module

# ─── Configuration defaults ───
SPONT_BASELINE="${SPONT_BASELINE:-2.0}"
SPONT_GATE_MIN="${SPONT_GATE_MIN:-1.5}"
SPONT_DEFAULT_THRESHOLD="${SPONT_DEFAULT_THRESHOLD:-10}"
SPONT_DEFAULT_CAP="${SPONT_DEFAULT_CAP:-48}"
SPONT_MAX_SPEND_RATIO="${SPONT_MAX_SPEND_RATIO:-0.8}"
SPONT_MISS_RATIO="${SPONT_MISS_RATIO:-0.3}"

# ─── Gate Check ───
# Returns 0 (true) if spontaneity is possible, 1 (false) otherwise
# Gate requires: all needs >= gate_min AND starvation guard not active
check_spontaneity_gate() {
    local state_file=$1
    local config_file=$2
    local starvation_active=${3:-false}

    if [[ "$starvation_active" == "true" ]]; then
        return 1
    fi

    # Read gate_min from config, fallback to default
    local gate_min
    gate_min=$(jq -r '.settings.spontaneity.gate_min_satisfaction // empty' "$config_file" 2>/dev/null)
    gate_min="${gate_min:-$SPONT_GATE_MIN}"

    # Check all needs
    local needs
    needs=$(jq -r '.needs | keys[]' "$config_file")
    
    while IFS= read -r need; do
        local sat
        sat=$(jq -r --arg n "$need" '.[$n].satisfaction // 2.0' "$state_file")
        if (( $(echo "$sat < $gate_min" | bc -l) )); then
            return 1
        fi
    done <<< "$needs"

    return 0
}

# ─── Surplus Accumulation ───
# Called once per cycle, AFTER decay/tension calc, BEFORE action selection
# Accumulates surplus for each need with spontaneity enabled
accumulate_surplus() {
    local state_file=$1
    local config_file=$2
    local starvation_active=${3:-false}

    # Check global gate
    if ! check_spontaneity_gate "$state_file" "$config_file" "$starvation_active"; then
        # Gate closed: surplus freezes (does NOT reset)
        return 0
    fi

    # Check if spontaneity is enabled globally
    local spont_enabled
    spont_enabled=$(jq -r '.settings.spontaneity.enabled // false' "$config_file" 2>/dev/null)
    if [[ "$spont_enabled" != "true" ]]; then
        return 0
    fi

    local baseline
    baseline=$(jq -r '.settings.spontaneity.baseline // empty' "$config_file" 2>/dev/null)
    baseline="${baseline:-$SPONT_BASELINE}"

    local now_epoch
    now_epoch=$(date +%s)
    local now_iso
    now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    local needs
    needs=$(jq -r '.needs | keys[]' "$config_file")

    while IFS= read -r need; do
        # Check if this need has spontaneity config
        local spont_cfg
        spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")
        
        if [[ "$spont_cfg" == "null" ]]; then
            continue
        fi

        local spont_enabled_need
        spont_enabled_need=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
        if [[ "$spont_enabled_need" != "true" ]]; then
            continue
        fi

        local cap
        cap=$(jq -r ".needs.\"$need\".spontaneous.cap // $SPONT_DEFAULT_CAP" "$config_file")

        # Get current satisfaction and surplus
        local sat
        sat=$(jq -r --arg n "$need" '.[$n].satisfaction // 2.0' "$state_file")
        
        local current_surplus
        current_surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")

        # Calculate hours since last surplus check
        local last_check
        last_check=$(jq -r --arg n "$need" '.[$n].last_surplus_check // "1970-01-01T00:00:00Z"' "$state_file")
        local last_epoch
        last_epoch=$(date -d "$last_check" +%s 2>/dev/null || echo 0)
        local seconds_since=$((now_epoch - last_epoch))
        local hours_since
        hours_since=$(echo "scale=4; $seconds_since / 3600" | bc -l)

        # Skip if less than 1 minute since last check (avoid micro-accumulation)
        if (( seconds_since < 60 )); then
            continue
        fi

        # Delta = (satisfaction - baseline) * hours
        # Can be negative if sat < baseline (surplus drains)
        local delta
        delta=$(echo "scale=4; ($sat - $baseline) * $hours_since" | bc -l)

        # Apply delta and clamp
        local new_surplus
        new_surplus=$(echo "scale=4; $current_surplus + $delta" | bc -l)
        
        # Clamp to [0, cap]
        if (( $(echo "$new_surplus < 0" | bc -l) )); then
            new_surplus="0"
        fi
        if (( $(echo "$new_surplus > $cap" | bc -l) )); then
            new_surplus="$cap"
        fi

        # Round to 1 decimal for cleanliness
        new_surplus=$(printf "%.1f" "$new_surplus")

        # Update state
        jq --arg n "$need" \
           --argjson s "$new_surplus" \
           --arg t "$now_iso" \
           '.[$n].surplus = $s | .[$n].last_surplus_check = $t' \
           "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"

        # Debug log (only if delta is meaningful)
        if (( $(echo "${delta#-} > 0.01" | bc -l) )); then
            echo "  [SURPLUS:ACCUM] $need: sat=$sat, delta=$(printf "%+.2f" "$delta"), surplus=$new_surplus/$cap"
        fi

    done <<< "$needs"
}

# ─── Random float in range ───
# Returns random float between min and max (inclusive)
random_float() {
    local min=$1
    local max=$2
    # Use $RANDOM (0-32767) for randomness
    local rand=$RANDOM
    local range
    range=$(echo "scale=4; $max - $min" | bc -l)
    local result
    result=$(echo "scale=4; $min + ($rand / 32767) * $range" | bc -l)
    printf "%.2f" "$result"
}

# ─── Get Shifted Matrix ───
# If surplus is eligible, interpolate impact matrix toward spontaneous target
# Outputs: "shifted_low shifted_mid shifted_high spend_amount t_value" or "none"
get_shifted_matrix() {
    local need=$1
    local normal_low=$2
    local normal_mid=$3
    local normal_high=$4
    local state_file=$5
    local config_file=$6

    # Check if spontaneity configured for this need
    local spont_cfg
    spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")
    if [[ "$spont_cfg" == "null" ]]; then
        echo "none"
        return
    fi

    local spont_enabled
    spont_enabled=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
    if [[ "$spont_enabled" != "true" ]]; then
        echo "none"
        return
    fi

    # Get surplus and config
    local surplus
    surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")
    
    local threshold
    threshold=$(jq -r ".needs.\"$need\".spontaneous.threshold // $SPONT_DEFAULT_THRESHOLD" "$config_file")
    
    local cap
    cap=$(jq -r ".needs.\"$need\".spontaneous.cap // $SPONT_DEFAULT_CAP" "$config_file")

    local max_spend_ratio
    max_spend_ratio=$(jq -r '.settings.spontaneity.max_spend_ratio // empty' "$config_file" 2>/dev/null)
    max_spend_ratio="${max_spend_ratio:-$SPONT_MAX_SPEND_RATIO}"

    # Calculate max_spend
    local max_spend
    max_spend=$(echo "scale=4; $surplus * $max_spend_ratio" | bc -l)

    # Both conditions: surplus >= threshold AND max_spend >= threshold
    if (( $(echo "$surplus < $threshold" | bc -l) )) || \
       (( $(echo "$max_spend < $threshold" | bc -l) )); then
        echo "none"
        return
    fi

    # Get target matrix
    local target_low target_mid target_high
    target_low=$(jq -r ".needs.\"$need\".spontaneous.target_matrix.low // 10" "$config_file")
    target_mid=$(jq -r ".needs.\"$need\".spontaneous.target_matrix.mid // 30" "$config_file")
    target_high=$(jq -r ".needs.\"$need\".spontaneous.target_matrix.high // 60" "$config_file")

    # Roll: how much surplus to risk
    local min_spend="$threshold"
    local rolled_spend
    rolled_spend=$(random_float "$min_spend" "$max_spend")

    # Interpolation factor t = rolled / cap, clamped to [0, 1]
    local t
    t=$(echo "scale=4; $rolled_spend / $cap" | bc -l)
    if (( $(echo "$t > 1.0" | bc -l) )); then t="1.0"; fi

    # Interpolate: normal + (target - normal) * t
    local shifted_low shifted_mid shifted_high
    shifted_low=$(echo "scale=1; $normal_low + ($target_low - $normal_low) * $t" | bc -l)
    shifted_mid=$(echo "scale=1; $normal_mid + ($target_mid - $normal_mid) * $t" | bc -l)
    shifted_high=$(echo "scale=1; $normal_high + ($target_high - $normal_high) * $t" | bc -l)

    # Round to integers
    shifted_low=$(printf "%.0f" "$shifted_low")
    shifted_mid=$(printf "%.0f" "$shifted_mid")
    shifted_high=$(printf "%.0f" "$shifted_high")

    # Normalize to sum=100
    local total=$((shifted_low + shifted_mid + shifted_high))
    if [[ $total -ne 100 ]] && [[ $total -gt 0 ]]; then
        # Adjust the largest bucket
        local diff=$((100 - total))
        if [[ $shifted_high -ge $shifted_low ]] && [[ $shifted_high -ge $shifted_mid ]]; then
            shifted_high=$((shifted_high + diff))
        elif [[ $shifted_mid -ge $shifted_low ]]; then
            shifted_mid=$((shifted_mid + diff))
        else
            shifted_low=$((shifted_low + diff))
        fi
    fi

    echo "$shifted_low $shifted_mid $shifted_high $rolled_spend $t"
}

# ─── Spend Surplus ───
# Called after action selection to deduct surplus
spend_surplus() {
    local need=$1
    local impact_range=$2     # "low", "mid", "high"
    local rolled_spend=$3
    local state_file=$4
    local config_file=$5

    local miss_ratio
    miss_ratio=$(jq -r '.settings.spontaneity.spend_on_miss_ratio // empty' "$config_file" 2>/dev/null)
    miss_ratio="${miss_ratio:-$SPONT_MISS_RATIO}"

    local current_surplus
    current_surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")

    local spend_amount
    if [[ "$impact_range" == "high" ]]; then
        # Full spend
        spend_amount="$rolled_spend"
        echo "  [SURPLUS] $need: → HIGH → surplus -= $spend_amount → $(echo "scale=1; $current_surplus - $spend_amount" | bc -l) [SPONTANEOUS]" >&2
    else
        # Partial spend (cost of attempt)
        spend_amount=$(echo "scale=2; $rolled_spend * $miss_ratio" | bc -l)
        echo "  [SURPLUS] $need: → $impact_range → surplus -= $spend_amount (miss) → $(echo "scale=1; $current_surplus - $spend_amount" | bc -l)" >&2
    fi

    # Apply deduction, clamp to 0
    local new_surplus
    new_surplus=$(echo "scale=1; $current_surplus - $spend_amount" | bc -l)
    if (( $(echo "$new_surplus < 0" | bc -l) )); then
        new_surplus="0"
    fi

    jq --arg n "$need" \
       --argjson s "$new_surplus" \
       '.[$n].surplus = $s' \
       "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"
}

# ─── Show Surplus Status ───
# For show-status.sh integration
show_surplus_status() {
    local state_file=$1
    local config_file=$2
    local starvation_active=${3:-false}

    local spont_enabled
    spont_enabled=$(jq -r '.settings.spontaneity.enabled // false' "$config_file" 2>/dev/null)
    if [[ "$spont_enabled" != "true" ]]; then
        return
    fi

    # Gate status
    local gate_status="CLOSED"
    if check_spontaneity_gate "$state_file" "$config_file" "$starvation_active"; then
        gate_status="OPEN"
    fi

    echo ""
    echo "Surplus pools (gate: $gate_status):"

    local needs
    needs=$(jq -r '.needs | keys[]' "$config_file")

    while IFS= read -r need; do
        local spont_cfg
        spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")

        if [[ "$spont_cfg" == "null" ]]; then
            printf "  %-16s — (spontaneity disabled)\n" "$need:"
            continue
        fi

        local spont_enabled_need
        spont_enabled_need=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
        if [[ "$spont_enabled_need" != "true" ]]; then
            printf "  %-16s — (spontaneity disabled)\n" "$need:"
            continue
        fi

        local surplus cap threshold
        surplus=$(jq -r --arg n "$need" '.[$n].surplus // 0' "$state_file")
        cap=$(jq -r ".needs.\"$need\".spontaneous.cap // $SPONT_DEFAULT_CAP" "$config_file")
        threshold=$(jq -r ".needs.\"$need\".spontaneous.threshold // $SPONT_DEFAULT_THRESHOLD" "$config_file")

        # Progress bar (12 chars)
        local filled
        filled=$(echo "scale=0; $surplus / $cap * 12" | bc -l 2>/dev/null)
        filled=${filled:-0}
        if [[ $filled -gt 12 ]]; then filled=12; fi
        local empty=$((12 - filled))
        local bar=""
        for ((i=0; i<filled; i++)); do bar+="█"; done
        for ((i=0; i<empty; i++)); do bar+="░"; done

        # Status label
        local max_spend
        max_spend=$(echo "scale=2; $surplus * $SPONT_MAX_SPEND_RATIO" | bc -l)
        local status_label
        if (( $(echo "$surplus >= $threshold" | bc -l) )) && \
           (( $(echo "$max_spend >= $threshold" | bc -l) )); then
            status_label="eligible ✓"
        elif (( $(echo "$surplus > 0" | bc -l) )); then
            status_label="accumulating..."
        else
            local sat
            sat=$(jq -r --arg n "$need" '.[$n].satisfaction // 2.0' "$state_file")
            if (( $(echo "$sat < $SPONT_BASELINE" | bc -l) )); then
                status_label="sat < baseline"
            else
                status_label="starting..."
            fi
        fi

        printf "  %-16s %s  %5.1f/%s  (%s)\n" "$need:" "$bar" "$surplus" "$cap" "$status_label"

    done <<< "$needs"
}

# ═══════════════════════════════════════════════════════════════
# Layer C — Context-Driven Spontaneity: Delta Triggers
# ═══════════════════════════════════════════════════════════════

# Associative array to hold context boosts per need (populated by run_context_scan)
declare -A CONTEXT_BOOSTS
declare -A CONTEXT_LABELS

# ─── Run Context Scan ───
# Calls context-scan.sh, parses fired triggers, accumulates boosts per need
run_context_scan() {
    local scripts_dir=$1

    # Reset boosts
    CONTEXT_BOOSTS=()
    CONTEXT_LABELS=()

    local context_script="$scripts_dir/context-scan.sh"
    if [[ ! -x "$context_script" ]]; then
        return 0
    fi

    # Run context scan, capture stdout (trigger JSON lines) and let stderr pass through
    local triggers_file
    triggers_file=$(mktemp /tmp/tp_context_XXXXXX)
    trap "rm -f '$triggers_file'" RETURN 2>/dev/null || true
    
    local log_output
    log_output=$("$context_script" 2>&1 1>"$triggers_file" || true)
    
    # Print stderr (logs)
    if [[ -n "$log_output" ]]; then
        echo "$log_output"
    fi
    
    # Parse trigger JSON lines from stdout
    if [[ -s "$triggers_file" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            
            local amount label
            amount=$(echo "$line" | jq -r '.amount // 0')
            label=$(echo "$line" | jq -r '.label // "[CONTEXT]"')
            
            # Apply boost to each need
            local needs_count
            needs_count=$(echo "$line" | jq '.needs | length')
            for ((j=0; j<needs_count; j++)); do
                local need_name
                need_name=$(echo "$line" | jq -r ".needs[$j]")
                
                # Accumulate boost (multiple triggers can boost same need)
                local current=${CONTEXT_BOOSTS[$need_name]:-0}
                CONTEXT_BOOSTS[$need_name]=$(echo "scale=4; $current + $amount" | bc -l)
                
                # Accumulate labels
                local current_label=${CONTEXT_LABELS[$need_name]:-}
                if [[ -z "$current_label" ]]; then
                    CONTEXT_LABELS[$need_name]="$label"
                else
                    CONTEXT_LABELS[$need_name]="$current_label $label"
                fi
            done
        done < "$triggers_file"
    fi
    rm -f "$triggers_file"
}

# ─── Get Context Boost for Need ───
# Returns accumulated boost amount for a specific need
get_context_boost() {
    local need=$1
    echo "${CONTEXT_BOOSTS[$need]:-0}"
}

# ─── Get Context Label for Need ───
get_context_label() {
    local need=$1
    echo "${CONTEXT_LABELS[$need]:-}"
}

# ═══════════════════════════════════════════════════════════════
# Layer B — Stochastic Spontaneity: Boredom Noise + Momentum Echo
# ═══════════════════════════════════════════════════════════════

# ─── B2: Boredom Noise ───
# Monotony-driven noise. Grows with time since last high-impact action.
# Returns noise chance as float [0..noise_cap]
calc_boredom_noise() {
    local need=$1
    local state_file=$2
    local config_file=$3

    # Check global noise enabled
    local noise_enabled
    noise_enabled=$(jq -r '.settings.spontaneity.noise.enabled // false' "$config_file" 2>/dev/null)
    if [[ "$noise_enabled" != "true" ]]; then
        echo "0"
        return
    fi

    # Check if this need has spontaneity
    local spont_cfg
    spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")
    if [[ "$spont_cfg" == "null" ]]; then
        echo "0"
        return
    fi
    local spont_enabled
    spont_enabled=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
    if [[ "$spont_enabled" != "true" ]]; then
        echo "0"
        return
    fi

    # Get params
    local base_noise norm_hours max_mult noise_cap high_threshold
    base_noise=$(jq -r '.settings.spontaneity.noise.base_noise // 0.03' "$config_file")
    norm_hours=$(jq -r '.settings.spontaneity.noise.norm_hours // 24' "$config_file")
    max_mult=$(jq -r '.settings.spontaneity.noise.max_multiplier // 3' "$config_file")
    noise_cap=$(jq -r '.settings.spontaneity.noise.noise_cap // 0.12' "$config_file")

    # Per-need override for high_impact_threshold
    high_threshold=$(jq -r ".needs.\"$need\".spontaneous.noise_override.high_impact_threshold // empty" "$config_file" 2>/dev/null)
    if [[ -z "$high_threshold" ]]; then
        high_threshold=$(jq -r '.settings.spontaneity.noise.high_impact_threshold // 2.0' "$config_file")
    fi

    # Hours since last high-impact action
    # Migration: if field missing, set to now (prevents spike on first run after upgrade)
    local last_high
    last_high=$(jq -r --arg n "$need" '.[$n].last_high_action_at // empty' "$state_file")
    if [[ -z "$last_high" ]]; then
        local now_iso
        now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        jq --arg n "$need" --arg t "$now_iso" '.[$n].last_high_action_at = $t' \
           "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"
        last_high="$now_iso"
    fi
    local last_high_epoch
    last_high_epoch=$(date -d "$last_high" +%s 2>/dev/null || echo 0)
    local now_epoch
    now_epoch=$(date +%s)
    local hours_since
    hours_since=$(echo "scale=4; ($now_epoch - $last_high_epoch) / 3600" | bc -l)

    # Monotony multiplier: linear ramp, capped at max_mult
    local multiplier
    multiplier=$(echo "scale=4; $hours_since / $norm_hours" | bc -l)
    if (( $(echo "$multiplier > $max_mult" | bc -l) )); then
        multiplier="$max_mult"
    fi

    # Boredom = base × multiplier, capped at noise_cap
    local boredom
    boredom=$(echo "scale=4; $base_noise * $multiplier" | bc -l)
    if (( $(echo "$boredom > $noise_cap" | bc -l) )); then
        boredom="$noise_cap"
    fi

    printf "%.4f" "$boredom"
}

# ─── B3: Momentum Echo ───
# Post-spontaneous creative inertia. Decays linearly over echo_duration.
# Returns echo boost as float [0..echo_base]
calc_echo_boost() {
    local need=$1
    local state_file=$2
    local config_file=$3

    # Check global echo enabled
    local echo_enabled
    echo_enabled=$(jq -r '.settings.spontaneity.echo.enabled // false' "$config_file" 2>/dev/null)
    if [[ "$echo_enabled" != "true" ]]; then
        echo "0"
        return
    fi

    # Check if this need has spontaneity
    local spont_cfg
    spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")
    if [[ "$spont_cfg" == "null" ]]; then
        echo "0"
        return
    fi
    local spont_enabled
    spont_enabled=$(jq -r ".needs.\"$need\".spontaneous.enabled // false" "$config_file")
    if [[ "$spont_enabled" != "true" ]]; then
        echo "0"
        return
    fi

    # Get params
    local echo_base echo_duration
    echo_base=$(jq -r '.settings.spontaneity.echo.echo_base // 0.08' "$config_file")
    echo_duration=$(jq -r '.settings.spontaneity.echo.echo_duration_hours // 24' "$config_file")

    # Hours since last spontaneous HIGH action
    # Migration: if field missing, treat as expired (no echo on first run)
    local last_spont
    last_spont=$(jq -r --arg n "$need" '.[$n].last_spontaneous_at // empty' "$state_file")
    if [[ -z "$last_spont" ]]; then
        last_spont="1970-01-01T00:00:00Z"  # expired → echo=0
    fi
    local last_spont_epoch
    last_spont_epoch=$(date -d "$last_spont" +%s 2>/dev/null || echo 0)
    local now_epoch
    now_epoch=$(date +%s)
    local hours_since
    hours_since=$(echo "scale=4; ($now_epoch - $last_spont_epoch) / 3600" | bc -l)

    # Expired?
    if (( $(echo "$hours_since >= $echo_duration" | bc -l) )); then
        echo "0"
        return
    fi

    # Linear decay: 1.0 at t=0, 0.0 at t=echo_duration
    local echo_strength
    echo_strength=$(echo "scale=4; 1.0 - ($hours_since / $echo_duration)" | bc -l)
    if (( $(echo "$echo_strength < 0" | bc -l) )); then
        echo_strength="0"
    fi

    local boost
    boost=$(echo "scale=4; $echo_base * $echo_strength" | bc -l)
    printf "%.4f" "$boost"
}

# ─── Combined Noise Upgrade ───
# After normal impact roll (possibly shifted by Layer A),
# try to upgrade the range by one step via noise.
# Outputs to stderr for logging, returns "range label" on stdout
try_noise_upgrade() {
    local need=$1
    local current_range=$2
    local state_file=$3
    local config_file=$4

    # Skip if already high or skip
    if [[ "$current_range" == "high" || "$current_range" == "skip" ]]; then
        echo "$current_range"
        return
    fi

    local boredom echo_boost context_boost
    boredom=$(calc_boredom_noise "$need" "$state_file" "$config_file")
    echo_boost=$(calc_echo_boost "$need" "$state_file" "$config_file")
    context_boost=$(get_context_boost "$need")

    local noise_cap
    noise_cap=$(jq -r '.settings.spontaneity.noise.noise_cap // 0.12' "$config_file" 2>/dev/null)

    local total_noise
    total_noise=$(echo "scale=4; $boredom + $echo_boost + $context_boost" | bc -l)
    if (( $(echo "$total_noise > $noise_cap" | bc -l) )); then
        total_noise="$noise_cap"
    fi

    # Nothing to do
    if (( $(echo "$total_noise <= 0" | bc -l) )); then
        echo "$current_range"
        return
    fi

    # Roll
    local roll_pct=$((RANDOM % 10000))
    local threshold_pct
    threshold_pct=$(echo "scale=0; $total_noise * 10000 / 1" | bc -l)

    if [[ $roll_pct -lt ${threshold_pct%.*} ]]; then
        # Upgrade by one step
        local upgraded
        if [[ "$current_range" == "low" ]]; then
            upgraded="mid"
        elif [[ "$current_range" == "mid" ]]; then
            upgraded="high"
        else
            echo "$current_range"
            return
        fi

        # Determine label — show which sources contributed
        local label_parts=""
        if (( $(echo "$boredom > 0" | bc -l) )); then label_parts="NOISE"; fi
        if (( $(echo "$echo_boost > 0" | bc -l) )); then
            [[ -n "$label_parts" ]] && label_parts="$label_parts+" || true
            label_parts="${label_parts}ECHO"
        fi
        if (( $(echo "$context_boost > 0" | bc -l) )); then
            [[ -n "$label_parts" ]] && label_parts="$label_parts+" || true
            label_parts="${label_parts}CONTEXT"
        fi
        local label="[${label_parts:-NOISE}]"
        
        # Add context-specific label if present
        local ctx_label
        ctx_label=$(get_context_label "$need")
        if [[ -n "$ctx_label" ]]; then
            label="$label $ctx_label"
        fi

        echo "  [NOISE] $need: boredom=$(printf "%.3f" "$boredom"), echo=$(printf "%.3f" "$echo_boost"), context=$(printf "%.3f" "$context_boost"), total=$(printf "%.3f" "$total_noise"), roll=$(printf "%.4f" "$(echo "scale=4; $roll_pct / 10000" | bc -l)") → ${current_range}→${upgraded} $label" >&2

        echo "$upgraded $label"
    else
        echo "$current_range"
    fi
}

# ─── Record Spontaneous Action ───
# Called when Layer A fires [SPONTANEOUS] HIGH — sets last_spontaneous_at for echo
record_spontaneous() {
    local need=$1
    local state_file=$2

    local now_iso
    now_iso=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    jq --arg n "$need" --arg t "$now_iso" \
       '.[$n].last_spontaneous_at = $t' \
       "$state_file" > "$state_file.tmp" && mv "$state_file.tmp" "$state_file"
}

# ─── Show Noise Status ───
show_noise_status() {
    local state_file=$1
    local config_file=$2

    local noise_enabled echo_enabled
    noise_enabled=$(jq -r '.settings.spontaneity.noise.enabled // false' "$config_file" 2>/dev/null)
    echo_enabled=$(jq -r '.settings.spontaneity.echo.enabled // false' "$config_file" 2>/dev/null)

    if [[ "$noise_enabled" != "true" && "$echo_enabled" != "true" ]]; then
        return
    fi

    echo ""
    echo "Noise status:"

    local needs
    needs=$(jq -r '.needs | keys[]' "$config_file")

    while IFS= read -r need; do
        local spont_cfg
        spont_cfg=$(jq -r ".needs.\"$need\".spontaneous // \"null\"" "$config_file")

        if [[ "$spont_cfg" == "null" ]]; then
            printf "  %-16s — (spontaneity disabled)\n" "$need:"
            continue
        fi

        local boredom echo_boost
        boredom=$(calc_boredom_noise "$need" "$state_file" "$config_file")
        echo_boost=$(calc_echo_boost "$need" "$state_file" "$config_file")

        local total
        total=$(echo "scale=4; $boredom + $echo_boost" | bc -l)
        local noise_cap
        noise_cap=$(jq -r '.settings.spontaneity.noise.noise_cap // 0.12' "$config_file" 2>/dev/null)
        if (( $(echo "$total > $noise_cap" | bc -l) )); then
            total="$noise_cap"
        fi

        local boredom_pct echo_pct total_pct
        boredom_pct=$(printf "%.1f" "$(echo "scale=1; $boredom * 100" | bc -l)")
        echo_pct=$(printf "%.1f" "$(echo "scale=1; $echo_boost * 100" | bc -l)")
        total_pct=$(printf "%.1f" "$(echo "scale=1; $total * 100" | bc -l)")

        # Hours since last high action
        local last_high hours_label
        last_high=$(jq -r --arg n "$need" '.[$n].last_high_action_at // "1970-01-01T00:00:00Z"' "$state_file")
        local last_high_epoch
        last_high_epoch=$(date -d "$last_high" +%s 2>/dev/null || echo 0)
        local now_epoch
        now_epoch=$(date +%s)
        local hours_since_high
        hours_since_high=$(echo "scale=0; ($now_epoch - $last_high_epoch) / 3600" | bc -l)
        hours_label="${hours_since_high}h no high"

        # Echo info
        local echo_info=""
        if (( $(echo "$echo_boost > 0" | bc -l) )); then
            local last_spont
            last_spont=$(jq -r --arg n "$need" '.[$n].last_spontaneous_at // "1970-01-01T00:00:00Z"' "$state_file")
            local last_spont_epoch
            last_spont_epoch=$(date -d "$last_spont" +%s 2>/dev/null || echo 0)
            local hours_since_spont
            hours_since_spont=$(echo "scale=0; ($now_epoch - $last_spont_epoch) / 3600" | bc -l)
            echo_info=" echo=${echo_pct}% (SPONT ${hours_since_spont}h ago)"
        fi

        printf "  %-16s boredom=%s%% (%s)%s → total=%s%%\n" "$need:" "$boredom_pct" "$hours_label" "$echo_info" "$total_pct"

    done <<< "$needs"
}
