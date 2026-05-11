# FlowSwarm Template Library

Battle-tested patterns from production runs. Each template includes the exact context that made it succeed.

## Test Generation Templates

### Pure Data Module (Zero-Iteration Pattern)
**Track record: 3/3 zero-iteration, 254 tests total**

Used on: WidgetHotelAssets (2017L → 147 tests), I18n (272L → 41 tests), TravelClick Types (637L → 66 tests)

The key: enumerate ALL public functions and tell the swarm exactly what to validate.

```
SWARM MODE: Initialize hierarchical swarm (maxAgents 4, strategy specialized).
Spawn: architect (analyze module, plan test structure), coder (write tests), reviewer (verify coverage).

TASK: Write comprehensive ExUnit tests for [MODULE_PATH] ([LINE_COUNT] lines, [MODULE_TYPE]).

Public API:
[PASTE: grep -n "^  def " path/to/module.ex]

Key data to validate:
- [SPECIFIC]: e.g., "All 8 hotels return non-empty data for get_rooms"
- [STRUCTURAL]: e.g., "Each room has required keys: :id, :name, :price_per_night, :images"
- [FORMAT]: e.g., "All image URLs start with https://"
- [BUSINESS RULES]: e.g., "Hotels 102949, 98036, 114747 must have adults_only: true"
- [EDGE CASES]: e.g., "Unknown hotel codes return empty map/list"

Requirements:
- File: test/[matching_path]_test.exs
- Use async: true (pure functions, no state)
- Group tests by function (describe blocks)
- Test ALL variants exhaustively (all hotels, all locales, all struct types)
- Include edge cases: nil input, empty string, unknown keys, wrong types
- Do NOT modify any source files

When done, output the test file contents and a summary line with test count.
```

**Why this works zero-iteration:** The swarm gets the complete function list AND specific assertions. No guessing what the module does. No discovering the API mid-test. It writes correct tests on the first pass because the prompt contains everything needed.

### Config Builder Module (Zero-Iteration Pattern)
**Track record: 1/1 zero-iteration, 58 tests**

Used on: SquadBuilder (889L → 58 tests)

```
SWARM MODE: Initialize hierarchical swarm (maxAgents 4, strategy specialized).
Spawn: architect (analyze module, plan test structure), coder (write tests), reviewer (verify coverage).

TASK: Write comprehensive ExUnit tests for [MODULE_PATH] ([LINE_COUNT] lines, config builder).

Public API:
[PASTE: grep -n "^  def " output]

This module builds [WHAT IT BUILDS] from [INPUT TYPE].

Key things to test:
- Output structure: required keys, correct types, valid values
- Input variations: different configs produce different outputs
- Cross-input consistency: related inputs produce compatible outputs
- Edge cases: empty/nil/missing fields in input structs
- Real data: test with actual configs from the system (e.g., HotelRegistry)

Requirements:
- File: test/[matching_path]_test.exs
- Use async: true
- Group by function (describe blocks)
- Test with REAL data where possible (actual hotel configs, not just mocks)
- Do NOT modify source files
```

### GenServer Module (Iteration-Expected Pattern)
**Track record: 1/1 green after 3 iterations, 43 tests, found 2 real bugs**

Used on: AssetHealthCheck (288L → 43 tests)

```
SWARM MODE: Initialize hierarchical swarm (maxAgents 4, strategy specialized).
Spawn: architect (analyze module + GenServer behavior), coder (write tests), reviewer (verify coverage).

TASK: Write comprehensive ExUnit tests for [MODULE_PATH] ([LINE_COUNT] lines, GenServer).

Public API:
[PASTE: grep -n "^  def " output]

GenServer callbacks present:
[PASTE: grep -n "def handle_" output]

CRITICAL TEST ISOLATION:
- This GenServer registers globally as __MODULE__ and is supervised by the app.
- Do NOT use start_supervised! — conflicts with the global instance.
- Options:
  A) If start_link/1 accepts name: option → use unique names per test, async: true
  B) If name is hardcoded → stop global instance in setup, restart after, async: false
  C) Tag tests that can't isolate with @tag :requires_restart

CATCH-ALL AUDIT:
- Check if handle_cast/2 has a catch-all clause. Missing = REAL BUG (crash on unknown cast).
- Check if handle_info/2 has a catch-all clause. Missing = REAL BUG (crash on unknown message).
- If missing, write tests that PROVE the crash, tag as @tag :known_bug.

Requirements:
- Test init/1, all handle_call, handle_cast, handle_info clauses
- Test state transitions and side effects
- Test crash scenarios (unexpected messages)
- Do NOT modify source files
```

**Why this needs iterations:** GenServer test isolation is genuinely tricky. The first pass usually gets the tests right but the setup/teardown wrong. Expect 2-3 rounds of fixing process conflicts.

## Feature Build Templates

### Elixir Adapter (Proven Pattern)
```
SWARM MODE: Initialize hierarchical swarm (maxAgents 6, strategy specialized).
Spawn: architect (plan module structure, map API), coder (implement), tester (ExUnit), reviewer (patterns).
Architect first → coder → tester + reviewer parallel.

TASK: Build a new [ENGINE] booking adapter in Elixir.

Reference: lib/booking_app/adapters/travelclick/ for the proven pattern.

Architecture:
- Adapter module: search/1, book/1, modify/1, cancel/1
- Token service with exponential backoff
- Rate cache for search results
- Tesla HTTP client
- All functions return {:ok, result} | {:error, reason}

Tests:
- Full lifecycle: search → book → modify → cancel
- Token rotation under load
- Error handling: 4xx, 5xx, timeout, malformed response

HARD LIMIT: Maximum 5 iterations.
```

### VAPI Voice Agent
```
SWARM MODE: Initialize hierarchical swarm (maxAgents 5, strategy specialized).
Spawn: architect (webhook flow), coder (implement), tester (controller tests), security (webhook auth).

TASK: [VAPI integration description]

Constraints:
- Webhook secret validated on EVERY request (no SKIP_VAPI_SIGNATURE in production)
- Tool call responses match VAPI's exact expected format
- All tool functions handle timeouts (10s max)
- Test with real VAPI payload shapes from test/fixtures/vapi/
```

## Quality & Audit Templates

### Quality Loop (Ralph-Style)
```
SWARM MODE: Initialize ring swarm (maxAgents 4, strategy adaptive).
Spawn: coder (fix), tester (run), reviewer (score), coordinator (track).
HARD LIMIT: Maximum 10 iterations.

TASK: Iterate on [target] until [score threshold].

Per iteration:
1. Coder applies fixes from reviewer feedback
2. Tester runs full suite: report pass/fail count
3. Reviewer scores against rubric: report X/Y
4. If score >= threshold: STOP
5. If iteration == 10: STOP regardless

Output final: score, pass/fail, remaining gaps.
```

### Security Audit
```
SWARM MODE: Security-focused hierarchical swarm (maxAgents 5).
Spawn: security-architect (threat model), auditor (scan), coder (fix), tester (verify).

TASK: Security audit of [scope].

Checklist:
- [ ] mix audit / npm audit
- [ ] Hardcoded secrets grep
- [ ] SQL injection (Ecto parameterization)
- [ ] Input validation in controllers
- [ ] Auth bypass paths
- [ ] GenServer catch-all handlers (real bugs if missing!)
- [ ] Error message info leaks
- [ ] Rate limiting
- [ ] CORS/CSP

Output: severity | file:line | finding | fix
HARD LIMIT: Maximum 5 iterations.
```

## Anti-Drift Template (Long Tasks)

For anything touching 10+ files or taking 5+ minutes:

```
SWARM MODE: Initialize anti-drift hierarchical swarm (maxAgents 4).
Spawn: architect (plan + checkpoint), coder (execute one step), reviewer (validate before next).

ANTI-DRIFT RULES:
- Architect writes numbered plan BEFORE any code
- Coder does ONE step at a time
- Reviewer validates EACH step before proceeding
- 2 rejections on same step → STOP and report
- Checkpoint after each success

TASK: [long task]
HARD LIMIT: Maximum 8 iterations.
```

## Meta Template (Self-Analysis)

FlowSwarm analyzing and improving itself:

```
SWARM MODE: Initialize meta-analysis hierarchical swarm (maxAgents 4).
Spawn: analyst (review production data + git history), architect (identify improvements), coder (rewrite), reviewer (validate).

TASK: Analyze FlowSwarm skill at ~/clawd/skills/flow-swarm/ and generate the next version.

Data sources:
1. Git log of swarm-generated commits: git log --oneline --grep="swarm"
2. Daemon logs: .claude-flow/logs/daemon.log
3. Current SKILL.md, setup script, templates
4. Test results from production runs

Analyze:
- What patterns produced zero-iteration success?
- What caused iterations? How to prevent?
- What's missing from templates?
- What daemon features are actually useful vs noise?
- What prompt patterns should be added/removed?

Output: complete rewritten SKILL.md with version bump, changelog, updated data.
```

## Target Selection Cheat Sheet

```bash
# Find untested modules sorted by size (best swarm targets)
for f in lib/**/*.ex; do
  base=$(basename "$f" .ex)
  count=$(find test/ -name "${base}_test.exs" 2>/dev/null | wc -l | tr -d ' ')
  [ "$count" = "0" ] && echo "$(wc -l < "$f")L $f"
done | sort -rn | head -15

# Find modules with thin coverage (test LOC < source LOC / 3)
for f in lib/**/*.ex; do
  base=$(basename "$f" .ex)
  test_file=$(find test/ -name "${base}_test.exs" 2>/dev/null | head -1)
  if [ -n "$test_file" ]; then
    src=$(wc -l < "$f")
    tst=$(wc -l < "$test_file")
    ratio=$((tst * 100 / src))
    [ "$ratio" -lt 33 ] && echo "${ratio}% coverage  ${src}L src / ${tst}L test  $f"
  fi
done | sort -n | head -15

# Classify module type for template selection
grep -l "use GenServer\|use Agent" lib/**/*.ex           # → GenServer template
grep -l "defstruct" lib/**/*.ex | grep -v "use GenServer" # → Pure data template
grep -l "Tesla\|HTTPoison\|Req\." lib/**/*.ex             # → External deps template
```

## Lessons Learned (Production)

1. **Context density > agent count.** A 4-agent swarm with rich context beats an 8-agent swarm with vague instructions.
2. **Enumerate everything.** Pasting `grep "^  def "` output into the prompt eliminates the #1 cause of missed coverage.
3. **Pure data modules are free wins.** Zero iteration, high test count, fast execution. Start here.
4. **GenServers need isolation guidance.** Always include the test isolation section or expect 2-3 rounds of fixing.
5. **Daemon workers are unreliable.** 20-50% success rate on audit/optimize. Don't depend on them.
6. **Parallel runs work.** 2 simultaneous swarms on different modules: no conflicts, both succeed.
7. **Always verify.** Run the tests yourself after the swarm finishes. Trust but verify.
8. **`--print` doesn't persist swarm memory.** The memory DB stays empty in batch mode. This is fine; the value is in the output, not the memory.
