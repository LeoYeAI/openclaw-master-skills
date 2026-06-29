# Workout Templates Reference

The v2.0 plan format uses workout templates to dramatically reduce verbosity. Instead of specifying full workout objects with structure, paces, and descriptions, you reference templates that expand automatically.

## How Templates Work

### Basic Syntax

All templates are referenced by ID, and IDs include a sport prefix (e.g., `run.`, `bike.`, `swim.`, `strength.`, `brick.`):

```yaml
# Template reference syntax
workouts:
  Mon: run.rest # No parameter
  Tue: run.easy(40) # Single parameter
  Wed: run.tempo(20, 10, 10) # Multiple parameters
  Thu: swim.threshold(10) # Sport-prefixed template
```

### Template Resolution

You do not need to resolve template files manually. Always discover and validate templates using the CLI commands below.

### Parameter Passing

Parameters are passed in order matching the template's `params` definition:

```yaml
# Template definition (tempo.yaml)
params:
  tempo_mins:
    type: int
    required: true
  warmup_mins:
    type: int
    default: 10
  cooldown_mins:
    type: int
    default: 10

# Usage examples
tempo(20)           # tempo_mins=20, warmup=10, cooldown=10 (defaults)
tempo(25, 15, 10)   # tempo_mins=25, warmup=15, cooldown=10
```

### Variable Interpolation

Templates use `${variable}` syntax for dynamic values:

```yaml
# In template definition
pace: "${paces.tempo}"
duration: "${duration}min"
estimatedDuration: "${warmup_mins + tempo_mins + cooldown_mins}"

# Athlete's paces are injected from the plan
paces:
  tempo: "8:15/mi"
```

---

## Template File Structure

Each template is a YAML file with this structure:

```yaml
id: tempo # Template identifier
name: Tempo Run # Display name
sport: run # Sport type
type: tempo # Workout type
category: tempo # Workout category

params: # Configurable parameters
  tempo_mins:
    type: int
    required: true
    default: 20
    min: 10
    max: 45
    description: Duration of tempo section in minutes
  warmup_mins:
    type: int
    default: 10
    description: Warmup duration in minutes

structure: # Workout structure
  warmup:
    - type: warmup
      name: Easy warmup
      duration: "${warmup_mins}min"
      pace: "${paces.easy}"
  main:
    - type: work
      name: Tempo
      duration: "${tempo_mins}min"
      pace: "${paces.tempo}"
      intensity: Zone 3-4
  cooldown:
    - type: cooldown
      name: Easy cooldown
      duration: "${cooldown_mins}min"
      pace: "${paces.easy}"

humanReadable: | # Coach-friendly text output
  TEMPO RUN

  WARM-UP: ${warmup_mins} min easy @ ${paces.easy}

  MAIN SET:
  ${tempo_mins} min @ tempo pace (${paces.tempo})

  COOL-DOWN: ${cooldown_mins} min easy

estimatedDuration: "${warmup_mins + tempo_mins + cooldown_mins}"
targetZone: Z3-Z4
rpe: "6-7"
notes: Builds lactate threshold and race-pace feel
```

---

## Creating Custom Templates

Custom templates live in `$HOME/.endurance-coach/workout-templates` and can override built-ins with the same ID.

### Recommended (CLI Scaffold)

```bash
npx -y endurance-coach@latest templates create my-tempo --type run --category tempo --example
npx -y endurance-coach@latest templates validate my-tempo
```

### Manual (Advanced)

To add a custom template by hand:

1. Create a YAML file in `$HOME/.endurance-coach/workout-templates/{sport}/`
2. Follow the structure above
3. Define params with types, defaults, and constraints
4. Use `${variable}` interpolation for dynamic values
5. Test with `npx -y endurance-coach@latest templates show your-template`
6. Validate with `npx -y endurance-coach@latest templates validate your-template`

**Available interpolation variables:**

- `${param_name}` - Any defined parameter
- `${paces.X}` - Athlete's pace values
- `${zones.X}` - Athlete's zone values
- Math expressions: `${warmup + main + cooldown}`

---

## CLI Commands for Templates

```bash
# List all templates
npx -y endurance-coach@latest templates

# List templates with usage examples
npx -y endurance-coach@latest templates --verbose

# Filter by sport
npx -y endurance-coach@latest templates list --sport run
npx -y endurance-coach@latest templates list --sport swim
npx -y endurance-coach@latest templates list --sport bike

# Filter by workout category
npx -y endurance-coach@latest templates list --type tempo

# Filter by source
npx -y endurance-coach@latest templates list --source user

# Show template details
npx -y endurance-coach@latest templates show run.intervals.400
npx -y endurance-coach@latest templates show swim.threshold

# Create template scaffold
npx -y endurance-coach@latest templates create newWorkout --type run --category tempo

# Validate a template
npx -y endurance-coach@latest templates validate run.intervals.400
```
