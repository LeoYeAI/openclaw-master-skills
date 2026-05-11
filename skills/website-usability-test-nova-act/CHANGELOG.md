# Changelog

All notable changes to the Nova Act Usability Testing skill will be documented in this file.

## [2.0.0] - 2026-02-06

### 🎯 Major: Agent-Driven Interpretation (Breaking Change)

**Problem:** The script was setting `overall_success: false` always and attempting hardcoded regex-based interpretation of responses. This was wrong because:
1. Hardcoded patterns can't understand context
2. Extra Claude API calls from Python are wasteful (agent is already running)
3. Reports showed incorrect pass/fail status

**Solution:** Complete separation of concerns:
- **Script** collects raw data only → outputs JSON with `needs_agent_analysis: true`
- **Agent** (Claude) interprets responses → sets `goal_achieved` and `overall_success`
- **Agent** calls report generator → produces accurate HTML report

### Architecture: Three-Phase Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase 1: DATA COLLECTION (run_adaptive_test.py)                 │
│ - Runs Nova Act browser automation                              │
│ - Captures raw_response from each step                          │
│ - Sets api_success (did API call work?)                         │
│ - Sets needs_agent_analysis: true                               │
│ - Outputs: test_results_adaptive.json                           │
│ - Does NOT interpret success/failure                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 2: AGENT INTERPRETATION (orchestrating AI agent)          │
│ - Reads JSON results                                            │
│ - For each step: interprets raw_response contextually           │
│ - Sets goal_achieved: true/false based on meaning               │
│ - Sets overall_success based on goals achieved                  │
│ - Saves updated JSON                                            │
│ - NO regex, NO hardcoded patterns, NO extra API calls           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ Phase 3: REPORT GENERATION (enhanced_report_generator.py)       │
│ - Reads interpreted JSON                                        │
│ - Shows ✅ PASSED / ❌ FAILED based on goal_achieved            │
│ - Shows ⏳ PENDING if agent hasn't interpreted yet              │
│ - Global recording numbering (1→N across all tests)             │
└─────────────────────────────────────────────────────────────────┘
```

### Changed

#### run_adaptive_test.py
- **Removed** `interpret_step_success()` function (hardcoded interpretation)
- **Removed** automatic `overall_success` calculation
- Script now outputs raw data with `needs_agent_analysis: true`
- Completion status based on API success only, not goal achievement
- Agent must interpret and set final values

#### enhanced_report_generator.py
- **Added** `goal_achieved` field support (agent-set interpretation)
- **Added** "⏳ PENDING" status for un-interpreted tests
- **Added** "Awaiting agent interpretation" warnings on steps
- **Fixed** recording numbering: now globally sequential (1, 2, 3... not restarting per test)
- **Added** CSS for `.pending` status styling
- Smart status detection: error states show FAILED, interpreted show PASSED/FAILED, uninterpreted show PENDING

#### SKILL.md
- **Added** complete agent workflow documentation with code examples
- **Updated** "Complete Analysis Workflow" section with mandatory interpretation steps
- **Added** interpretation code template for agents to use
- Clarified that agent MUST interpret before generating final report

### Key Data Fields

| Field | Set By | Meaning |
|-------|--------|---------|
| `raw_response` | Script | Actual text Nova Act returned |
| `api_success` | Script | Did the API call complete? |
| `needs_agent_analysis` | Script | Always `true` - agent must interpret |
| `goal_achieved` | Agent | Did the response indicate success? |
| `goals_achieved` | Agent | Count of steps where goal was achieved |
| `overall_success` | Agent | Test passed (≥50% goals achieved) |

### Why This Matters

1. **No hardcoded interpretation** - Agent understands "Leaderboard, News, Stats" is useful content
2. **No wasted API calls** - Agent doing the work is already running
3. **Correct reports** - Tests that found content show ✅, tests with "No" show ❌
4. **Transparency** - PENDING status shows when interpretation is needed

---

## [2.0.0-beta] - 2026-02-05

### 🎯 Simplified Nova Act Prompts

**Problem:** Prompts were asking Nova Act to reason about personas and usability, e.g.:
- "As a tournament_follower with high technical skills, can you easily accomplish this task?"

This is wrong - Nova Act is a browser automation tool, not a reasoning engine.

**Solution:** Nova Act now gets simple, direct browser commands. The Claude agent handles all reasoning.

### Changed
- **Cookbook updated**: Added "Nova Act is NOT a Reasoning Engine" as Principle #0
  - ❌ "As a beginner user, can you easily find the docs?"
  - ✅ "Click the Documentation link in the navigation"
- **dynamic_exploration.py**: Generic fallback now generates direct browser commands
  - Removed persona-specific prompt generation
  - `adapt_prompt_for_persona()` now returns prompts unchanged
- **response_interpreter.py**: `generate_alternative_approach()` now strips persona prefixes
  - Alternative prompts are simple: "Check the navigation menu for: {task}"
- **SKILL.md**: Added "Keep Nova Act Prompts Simple" section
  - Clear examples of wrong vs right prompts
  - Explains correct workflow: Agent reasons → Nova Act executes → Agent interprets

### Key Principle
- **Agent decides** what to test (based on persona goals)
- **Nova Act executes** simple browser tasks
- **Agent interprets** results in persona context

---

## [1.3.1] - 2026-02-05

### 🛡️ Graceful Shutdown & Partial Reports

**Problem:** Tests could be killed (timeout/signal) mid-run with no report generated.

**Solution:** Added signal handlers and atexit hooks to generate partial reports on interruption.

### Added
- **Signal handling**: Catches SIGTERM/SIGINT and generates report before exit
- **Partial report indicator**: HTML report clearly shows when incomplete
  - Yellow warning banner at top
  - Shows "X of Y planned tests completed"
- **Progress tracking**: Global state tracks completed vs planned tests
- **Intermediate saves**: Results saved after each test completion

### Changed
- Recommended timeout updated to **30 minutes** (was 15 min)
- SKILL.md now includes timeout guidance section
- Report generator accepts `_partial_report` flag in page_analysis

### Fixed
- **Simplified page analysis**: Nova Act now just reports what's visible
  - Extracts: title, navigation, purpose, visible sections
  - Removed hardcoded key_elements checks (pricing/docs/demo)
  - Orchestrating AI agent interprets the data and decides what matters
  - Nova Act does what it's good at (browser interaction), agent does reasoning

---

## [1.3.0] - 2026-02-05

### 🎯 Major: Semantic Response Interpretation

**Critical Fix:** Nova Act returning "No" was being treated as success because the API call worked.
Now we interpret responses semantically to determine if the **goal was actually achieved**.

### Added
- **Agent-Analyzed Results**: The orchestrating AI agent (OpenClaw/Claude) now interprets test results
  - Script returns raw responses with `needs_agent_analysis: true`
  - Agent determines `goal_achieved` based on response content
  - No external API calls needed - uses the agent that's already running!
  
- **Response Interpreter** (`response_interpreter.py`): Structures data for agent analysis
  - Captures raw Nova Act responses
  - Detects obvious negatives for automatic retries ("No", "not found")
  - Provides prompts/templates for agent analysis
  - Returns `api_success` (API worked) vs `goal_achieved` (agent determines)

- **Adaptive Exploration**: Up to 3 different approaches per test step
  - If first approach fails, tries alternative strategies automatically
  - Strategy 1: Look in navigation vs content (or vice versa)
  - Strategy 2: Scroll and look again
  - Strategy 3: Broaden the search terms
  - `generate_alternative_approach()` creates context-aware retries

- **New Result Fields**:
  - `goal_achieved`: Boolean - did we find what we were looking for?
  - `goals_achieved`: Count of steps where goal was achieved
  - `api_successes`: Count of steps where API call succeeded
  - `attempts`: List of all attempts per step with prompts and responses

### Changed
- `execute_exploration_step()` → `execute_exploration_step_adaptive()`
  - Uses `safe_act_get` for queries (captures actual response text)
  - Interprets responses before marking success
  - Retries with alternative approaches when goal not achieved
  
- **Success Calculation**: Now based on `goal_achieved`, not just API success
  - "No" response → `success=True, goal_achieved=False` → Test step FAILED
  - "Yes, I found X" → `success=True, goal_achieved=True` → Test step PASSED

- **Test Output**: Shows "goals achieved" instead of "steps successful"

### Fixed
- **CRITICAL**: Tests no longer pass when Nova Act returns negative answers
- Steps that return "No" or "not found" are now correctly marked as failed
- Overall test success now reflects whether the user's goal was accomplished

---

## [1.2.0] - 2026-02-05

### 🎯 Major Features

#### AI Agent-Orchestrated Persona Generation
- **AI agent (Claude) generates personas** and passes them as JSON to the test script
- Removes duplicate API calls (agent is already Claude)
- Better context (agent has conversation history, domain knowledge)
- Script accepts 3 argument types:
  1. **JSON file**: `personas.json` (recommended)
  2. **JSON string**: `'[{"name": "...", ...}]'` (recommended)
  3. **Simple description**: `"golf enthusiast"` (fallback)

#### Workflow Testing with Safety Guardrails
- Complete user journey testing: booking, checkout, posting, signup, form submission
- **Automatic safety stops** before material impact (payment, publishing, account creation)
- 6 workflow types detected and tested appropriately
- Observes but doesn't execute final actions with material impact

#### Enhanced Report Generation
- Per-test trace file links (not just global)
- WSL-compatible file paths (`file://wsl$/Ubuntu/...`)
- Dynamic page analysis based on site type
- Session recordings section with clickable trace links

### 🔧 Bug Fixes

#### Critical Fixes
- **safe_act returns observations**: Added `ActResult`/`QueryResult` dataclasses with observation tracking
- **Trace files filtered by run**: Only includes traces from current test run (not old sessions)
- **Executive Summary rendering**: Fixed f-string evaluation in report templates
- **Error message handling**: Fixed type mismatch in safe_act error handling

#### Code Quality Improvements
- **Consistent error handling**: Standardized on Result dataclass types
- **Safe JSON extraction**: Replaced regex with multi-strategy `extract_json_safely()`
- **Cookbook integration**: Prompts now use cookbook guidance for better Nova Act interactions
- **Configurable defaults**: Timeouts and thresholds now centralized as constants
- **URL parameter passing**: Removed global variable mutation

### 📦 Installation & Setup
- Manual installation via `pip3 install nova-act pydantic playwright`
- Playwright browser: `playwright install chromium`
- Config file at `~/.openclaw/config/nova-act.json`
- 60-second status updates during test execution

### 📝 Documentation
- Complete SKILL.md rewrite with AI agent guidance
- Persona generation examples by industry
- Workflow testing patterns and safety guidelines
- Technical overview document

### Technical Details

#### New Files/Functions
- `extract_json_safely()`: Multi-strategy JSON extraction
- `parse_cookbook_hints()`: Extract guidance from cookbook
- `apply_cookbook_guidance()`: Apply best practices to prompts
- `ActResult`/`QueryResult`: Dataclasses for consistent returns
- Legacy tuple compatibility functions for backwards compat

#### Key Parameters
- `DEFAULT_TIMEOUT = 20` seconds
- `DEFAULT_MAX_RETRIES = 1`
- `SLOW_OPERATION_THRESHOLD = 15` seconds
- Test start time filtering for traces

---

## [1.1.0] - 2026-02-04

### Added
- Initial release with adaptive usability testing
- Dynamic persona generation
- Contextual test case generation
- Fully dynamic exploration strategies
- Robust error handling
- HTML report generation with trace links

## [1.0.0] - 2026-02-03

### Added
- Basic Nova Act usability testing framework
- Manual persona configuration
- Hardcoded test strategies
- Basic reporting
