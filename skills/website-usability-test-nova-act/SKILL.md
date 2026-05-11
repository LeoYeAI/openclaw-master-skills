---
name: nova-act-usability
version: 1.0.2
description: AI-orchestrated usability testing using Amazon Nova Act. The agent generates personas, runs tests to collect raw data, interprets responses to determine goal achievement, and generates HTML reports. Tests real user workflows (booking, checkout, posting) with safety guardrails. Use when asked to "test website usability", "run usability test", "generate usability report", "evaluate user experience", "test checkout flow", "test booking process", or "analyze website UX".
metadata:
  openclaw:
    requires:
      config:
        - ~/.openclaw/config/nova-act.json
      bins:
        - python3
---

# Nova Act Usability Testing v1.0.2

**AI-orchestrated** usability testing with digital twin personas powered by Amazon Nova Act.

## ⚠️ Prerequisites & Credentials

**This skill requires an Amazon Nova Act API key.**

| Requirement | Details |
|-------------|---------|
| **API Key** | Nova Act API key from [AWS Console](https://console.aws.amazon.com/) |
| **Config Location** | `~/.openclaw/config/nova-act.json` |
| **Format** | `{"apiKey": "your-nova-act-api-key-here"}` |
| **Dependencies** | `pip3 install nova-act pydantic playwright` |
| **Browser** | `playwright install chromium` (~300MB download) |

## 🔒 Data & Privacy Notice

**What this skill accesses:**
- **Reads:** `~/.openclaw/config/nova-act.json` (your API key)
- **Writes:** `./nova_act_logs/` (trace files with screenshots), `./test_results_adaptive.json`, `./nova_act_usability_report.html`

**What trace files contain:**
- Screenshots of every page visited
- Full page content (HTML, text)
- Browser actions and AI decisions

**Recommendations:**
- Run tests only on **non-production** or **test environments**
- Be aware traces may capture **PII or sensitive data** visible on tested pages
- Review/delete trace files after use if they contain sensitive content
- Consider running in a **sandboxed environment** (container/VM) for untrusted sites

---

## Features

**Agent-Driven Interpretation**: The script no longer interprets responses. YOU (the agent) must:
1. Run the test script → collect raw data
2. Read JSON → interpret each `raw_response` 
3. Set `goal_achieved` and `overall_success`
4. Generate the report

No hardcoded regex. No extra API calls. The agent doing the work is already running.

## Quick Start (For AI Agents)

**When a user asks to test a website, YOU (the AI agent) must complete ALL 4 phases:**

| Phase | What Happens | Who Does It |
|-------|--------------|-------------|
| 1. Setup | Generate personas, run test script | Agent + Script |
| 2. Collect | Script captures raw Nova Act responses | Script |
| 3. Interpret | Read JSON, determine goal_achieved for each step | **Agent** |
| 4. Report | Generate HTML report with interpreted results | Agent |

**⚠️ The script does NOT interpret responses or generate the final report. You must do phases 3-4.**

### 🎯 Recommended: AI Agent Generates Personas

**You're already an AI (Claude) - use your intelligence to generate contextual personas!**

```python
import subprocess
import os
import sys
import json
import tempfile

# Step 1: Check dependencies
try:
    import nova_act
    print("✅ Dependencies ready")
except ImportError:
    print("📦 Dependencies not installed. Please run:")
    print("   pip3 install nova-act pydantic playwright")
    print("   playwright install chromium")
    sys.exit(1)

# Step 2: Verify Nova Act API key
config_file = os.path.expanduser("~/.openclaw/config/nova-act.json")
with open(config_file, 'r') as f:
    config = json.load(f)
    if config.get('apiKey') == 'your-nova-act-api-key-here':
        print(f"⚠️  Please add your Nova Act API key to {config_file}")
        sys.exit(1)

# Step 3: YOU (the AI agent) generate personas
# Example for https://www.pgatour.com/ (golf tournament site)
website_url = "https://www.pgatour.com/"

personas = [
    {
        "name": "Marcus Chen",
        "archetype": "tournament_follower",
        "age": 42,
        "tech_proficiency": "high",
        "description": "Avid golf fan who follows multiple tours and tracks player stats",
        "goals": [
            "Check current tournament leaderboard",
            "View recent tournament results",
            "Track favorite player performance"
        ]
    },
    {
        "name": "Dorothy Williams",
        "archetype": "casual_viewer",
        "age": 68,
        "tech_proficiency": "low",
        "description": "Occasional golf viewer who watches major tournaments",
        "goals": [
            "Find when the next tournament is",
            "See who won recently",
            "Understand how to watch online"
        ]
    }
]

# Step 4: Save personas and run test
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(personas, f, indent=2)
    personas_file = f.name

skill_dir = os.path.expanduser("~/.openclaw/skills/nova-act-usability")
test_script = os.path.join(skill_dir, "scripts", "run_adaptive_test.py")

# Run with AI-generated personas
subprocess.run([sys.executable, test_script, website_url, personas_file])

# Clean up temp file
os.unlink(personas_file)
```

**Persona Template:**
```json
{
  "name": "FirstName LastName",
  "archetype": "descriptive_identifier",
  "age": 30,
  "tech_proficiency": "low|medium|high",
  "description": "One sentence about who they are",
  "goals": [
    "First goal relevant to this website",
    "Second goal relevant to this website",
    "Third goal relevant to this website"
  ]
}
```

### 📝 Alternative: Simple Custom Persona

If user specifies a persona description, pass it as a string:

```python
# User: "Test PGA Tour site as a golf enthusiast"
website_url = "https://www.pgatour.com/"
user_persona = "golf enthusiast who follows tournaments closely"

subprocess.run([sys.executable, test_script, website_url, user_persona])
# Script will parse this and create personas automatically
```

### ⚠️ Fallback: Auto-Generation (Not Recommended)

Let the script guess personas based on basic category keywords:

```python
# Generic, less contextual personas
subprocess.run([sys.executable, test_script, website_url])
```

### Why YOU Should Generate Personas

**✅ Advantages:**
- **Better context:** You have full conversation history and domain knowledge
- **Smarter inference:** You can analyze the URL, industry, and user intent
- **No duplicate API calls:** You're already Claude - don't call yourself again!
- **User preferences:** You can adapt based on stated preferences
- **Clarifying questions:** You can ask the user about target demographics

**❌ What to avoid:**
- Don't let Python script make its own Claude API call (wasteful)
- Don't rely on generic fallback personas (less accurate)
- Don't skip persona generation (hurts test quality)

### 💡 Tips for Persona Generation

**Analyze the website:**
- **URL domain:** `.gov` → citizens, `.edu` → students/faculty
- **Keywords:** "shop" → shoppers, "book" → travelers, "play" → gamers
- **Industry:** Golf → fans/players, Banking → customers/businesses

**Create diverse personas:**
- Mix experience levels (beginner, intermediate, expert)
- Mix tech proficiency (low, medium, high)  
- Mix age ranges (young, middle-aged, senior)
- Mix motivations (casual, professional, enthusiastic)

**Generate realistic goals:**
- Specific to the website's purpose
- Actionable and measurable
- Match the persona's characteristics

**Examples by industry:**
- **E-commerce:** bargain_hunter, comparison_shopper, impulse_buyer
- **News:** daily_reader, topic_follower, casual_browser
- **Sports:** die_hard_fan, casual_viewer, stats_tracker
- **Travel:** business_traveler, vacation_planner, deal_seeker
- **SaaS:** power_user, evaluator, beginner
## User Invocation

Users can trigger this skill by saying:
- "Test the usability of [website URL]"
- "Run a usability test on [website URL]"
- "Generate a usability report for [website URL]"
- "Evaluate the UX of [website URL]"
- "Analyze [website URL] for usability issues"
- **NEW:** "Test the booking flow on [website]"
- **NEW:** "Test the checkout process on [e-commerce site]"
- **NEW:** "Test posting workflow on [social media site]"

**The AI will automatically:**
1. Load the Nova Act cookbook for guidance
2. Analyze the page to understand it
3. Detect if it's a workflow-based site (booking, e-commerce, social, etc.)
4. **Generate contextual personas:**
   - If custom persona specified → Create persona matching that description
   - If no custom persona → Use Claude AI to infer the 3 most plausible real-world user types
   - Fallback to category-based personas if AI unavailable
5. Create realistic test cases (including full workflows when appropriate)
6. Run adaptive, iterative tests with Nova Act
7. **NEW:** Apply safety stops before material impact actions (payment, posting, account creation)
8. Generate comprehensive HTML report with trace links
9. Provide viewing instructions

## Workflow Testing

**NEW in this version:** The skill now tests complete user journeys, not just information-finding!

### Supported Workflows

**E-Commerce:**
- Product search → Add to cart → Checkout → **STOP before payment**

**Flight/Hotel Booking:**
- Search → Select → Fill details → **STOP before booking**

**Social Media:**
- Create post → Add content → **STOP before publishing**

**Account Signup:**
- Fill registration → **STOP before final submission**

**Form Submission:**
- Fill form → **STOP before submit**

### Safety Guarantees

The skill will **NEVER:**
- Complete actual purchases
- Create real accounts
- Post publicly
- Send emails/messages
- Subscribe to newsletters
- Make any action with monetary/legal/reputational impact

The skill will **ALWAYS:**
- Test up to (but not including) the final action
- Verify the final button exists and is accessible
- Document the safety stop in observations

## 🧠 Agent Analysis (CRITICAL)

**You (the AI agent) must analyze test results!** The script collects raw responses but does NOT interpret them.

### Why Agent Analysis?

The script returns raw Nova Act responses like:
- `"No"` - Is there a pricing link?
- `"I don't see any documentation"` - Is there docs?
- `"Amazon Nova Act"` - What is the headline?

**You must determine if each response means the goal was achieved:**

| Response | Goal Achieved? |
|----------|---------------|
| `"No"` | ❌ NOT achieved |
| `"I don't see..."` | ❌ NOT achieved |
| `"Not found"` | ❌ NOT achieved |
| `"Yes, I found..."` | ✅ Achieved |
| `"Amazon Nova Act"` (content) | ✅ Achieved |
| `"The pricing is $29/mo"` | ✅ Achieved |

### Result Data Structure

After the test script runs, read the JSON results. Each step contains:

```json
{
    "step_name": "check_nav_for_pricing",
    "prompt": "Is there a pricing link in the navigation?",
    "expected_outcome": "Find pricing in navigation",
    "raw_response": "No",
    "api_success": true,
    "needs_agent_analysis": true,
    "attempts": [
        {
            "prompt": "Is there a pricing link in the navigation?",
            "response": "No",
            "approach": "original"
        }
    ]
}
```

**Key fields you analyze:**
- `raw_response`: The actual Nova Act response - YOU determine what it means
- `api_success`: Did the API call work? (script handles this)
- `needs_agent_analysis`: Always `true` - your cue to interpret
- `attempts`: All attempts made (script tries up to 3 alternative approaches)

### How to Analyze

**For each step, determine:**
1. `goal_achieved`: Did the response indicate success or failure?
2. `friction_level`: How hard was it? (attempts.length > 1 = friction)
3. `observations`: UX insights from the response

**Analysis example:**

```
Step 1: "Is there a pricing link?" 
  → Response: "No" (1 attempt)
  → Goal achieved: NO (explicit negative)
  → Friction: HIGH (not discoverable)

Step 2: "What is the headline?" 
  → Response: "Amazon Nova Act" (1 attempt)
  → Goal achieved: YES (actual content)
  → Friction: LOW (immediately visible)

Step 3: "Find documentation" 
  → Response: "I found a docs link in the footer" (3 attempts)
  → Goal achieved: YES (found eventually)
  → Friction: MEDIUM (required multiple approaches)
```

### Helper Functions (For Script Integration)

The `response_interpreter.py` provides helpers if you want structured prompts:

```python
from scripts.response_interpreter import (
    format_for_agent_analysis,
    create_agent_prompt_for_interpretation,
    create_agent_prompt_for_alternative
)

# Format all results for analysis
formatted = format_for_agent_analysis(results)

# Get interpretation prompt for one step
prompt = create_agent_prompt_for_interpretation(step_result)

# Get retry prompt when goal not achieved  
retry_prompt = create_agent_prompt_for_alternative(
    original_prompt="Is there a pricing link?",
    failed_response="No",
    attempt_number=2
)
```

### Complete Analysis Workflow (MANDATORY)

**The script does NOT generate the final report automatically.** You (the agent) must:

1. **Run the test script** → outputs `test_results_adaptive.json` with raw data
2. **Read the JSON** into your context
3. **Interpret each step** → set `goal_achieved: true/false` based on `raw_response`
4. **Set overall success** → set `overall_success: true/false` on each test
5. **Save updated JSON**
6. **Call report generator** with interpreted results

**Step-by-step code for the agent to execute:**

```python
import json
import os
import sys

# Add skill scripts to path
sys.path.insert(0, os.path.expanduser("~/.openclaw/skills/nova-act-usability/scripts"))
from enhanced_report_generator import generate_enhanced_report

# 1. Read raw results
with open('test_results_adaptive.json', 'r') as f:
    results = json.load(f)

# 2. YOU (the agent) interpret each step
for test in results:
    goals_achieved = 0
    for step in test.get('steps', []):
        raw = step.get('raw_response', '')
        
        # AGENT INTERPRETS: Does this response indicate goal was achieved?
        # You decide based on the response content and expected outcome
        # Example interpretations:
        #   "No" → goal_achieved = False
        #   "Leaderboard, News, Schedule, Players" → goal_achieved = True (content found)
        #   "Yes" → goal_achieved = True
        #   "I don't see any..." → goal_achieved = False
        
        step['goal_achieved'] = ???  # YOU set this based on your interpretation
        if step['goal_achieved']:
            goals_achieved += 1
    
    # 3. Set overall success (e.g., >= 50% goals achieved)
    total = len(test.get('steps', []))
    test['goals_achieved'] = goals_achieved
    test['overall_success'] = (goals_achieved / total >= 0.5) if total > 0 else False

# 4. Save interpreted results
with open('test_results_adaptive.json', 'w') as f:
    json.dump(results, f, indent=2)

# 5. Generate report with interpreted data
page_analysis = {
    'title': '...',  # From your earlier analysis
    'purpose': '...',
    'navigation': [...]
}
all_traces = []
for r in results:
    all_traces.extend(r.get('trace_files', []))

report_path = generate_enhanced_report(page_analysis, results, all_traces)
print(f"Report: {report_path}")
```

**Why the agent must interpret:**
- No hardcoded regex or pattern matching
- You understand context (what "Yes" means for this specific question)
- You can reason about partial success, edge cases
- No duplicate Claude API calls - you're already running!

## ⚠️ Critical: Keep Nova Act Prompts Simple

**Nova Act is a browser automation tool, NOT a reasoning engine.**

The Claude agent (you) does all reasoning about:
- What to test based on the persona
- Whether results are good or bad
- What the UX implications are

Nova Act just:
- Clicks, types, scrolls
- Reports what it sees

### ❌ WRONG: Asking Nova Act to reason

```python
# DON'T ask Nova Act to think about personas
nova.act("As a beginner user, can you easily find the documentation?")
nova.act("Would a business professional find the pricing clear?")
nova.act("Is this task accomplishable for someone with low technical skills?")
```

### ✅ RIGHT: Simple, direct browser commands

```python
# Simple browser actions
nova.act("Click the Documentation link in the navigation")
nova.act("Find and click a link containing 'Pricing'")
nova.act_get("What text is displayed in the main heading?")
nova.act_get("List the navigation menu items visible on this page")
```

### The Correct Workflow

1. **Agent** (you) decides what to test based on persona: "Dorothy is 68 with low tech skills - she wants to know how to watch golf online"
2. **Agent** generates simple Nova Act prompts: "Click 'Watch & Listen' in the navigation"
3. **Nova Act** executes browser task and returns raw results: "Clicked Watch & Listen, now on video page"
4. **Agent** interprets results: "Dorothy would find this confusing because the options are unclear..."

## How This Works

**You (the AI) are the orchestrator.** This skill provides:
1. **Nova Act cookbook** (`references/nova-act-cookbook.md`) - Best practices, workflow patterns, and safety guidelines (automatically loaded at test start)
2. **Adaptive test orchestrator** (`run_adaptive_test.py`) - Main execution script with workflow detection
3. **Dynamic strategy generator** (`scripts/dynamic_exploration.py`) - Generates workflow-appropriate test strategies
4. **Session management** (`scripts/nova_session.py`) - Nova Act wrapper
5. **Report generator** (`enhanced_report_generator.py`) - Auto-generated HTML reports

**Execution Flow:**

### CRITICAL: Check Dependencies First

**Before running ANY test, check if dependencies are installed:**

```bash
# Check if nova-act is installed
python3 -c "import nova_act" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Dependencies not installed. Please run:"
    echo "  pip3 install nova-act pydantic playwright"
    echo "  playwright install chromium"
    exit 1
fi

# Check API key
if ! grep -q '"apiKey":.*[^"]' ~/.openclaw/config/nova-act.json; then
    echo "⚠️  Please add your Nova Act API key to ~/.openclaw/config/nova-act.json"
    exit 1
fi
```

**Or use Python to check:**

```python
import sys

# Check if nova-act is installed
try:
    import nova_act
    print("✅ Dependencies already installed")
except ImportError:
    print("📦 Dependencies not installed. Please run:")
    print("   pip3 install nova-act pydantic playwright")
    print("   playwright install chromium")
    sys.exit(1)
```

### Running Tests (After Dependencies Confirmed)

When a user asks for usability testing:

```bash
# Find the skill directory
SKILL_DIR=~/.openclaw/skills/nova-act-usability

# Run the adaptive test script
python3 "$SKILL_DIR/scripts/run_adaptive_test.py" "https://example.com"

# This will:
# - Create nova_act_logs/ in current directory
# - Create test_results_adaptive.json in current directory
# - Create nova_act_usability_report.html in current directory
# - Provide 60-second status updates during test
```

### ⏱️ Timeout Guidance

**Recommended timeout: 30 minutes (1800 seconds)**

Full usability tests with 3 personas × 3 goals = 9 tests can take 10-20+ minutes depending on:
- Website load times (slow sites like media-heavy sports sites take longer)
- Nova Act API response times (each act() call takes 5-60 seconds)
- Network conditions

**Graceful shutdown:** If the test is interrupted (timeout, SIGTERM, SIGINT), it will:
1. Save all completed test results to `test_results_adaptive.json`
2. Generate a **partial report** clearly marked as incomplete
3. Show how many tests completed vs planned

**For shorter tests:** Use fewer personas or goals:
```python
# Quick test with 1 persona
personas = [{"name": "Test User", "archetype": "casual", ...}]
```

### What You (the AI) Need to Do:

1. **Check dependencies** (run the check above)
2. **If missing**: Tell user to run `pip3 install nova-act pydantic playwright && playwright install chromium`
3. **If present**: Extract the website URL from user's request
4. **Run the test** with the URL as argument
5. **Monitor progress** (status updates every 60 seconds)
6. **Share the report** viewing instructions with user

## Quick Start

**When user requests usability testing:**

```python
import subprocess
import os

# Get skill directory
skill_dir = os.path.expanduser("~/.openclaw/skills/nova-act-usability")
if not os.path.exists(skill_dir):
    # Try workspace location
    skill_dir = os.path.join(os.getcwd(), "nova-act-usability")

script_path = os.path.join(skill_dir, "scripts", "run_adaptive_test.py")

# Run test
result = subprocess.run(
    ["python3", script_path, "https://example.com"],
    env={**os.environ, "NOVA_ACT_SKIP_PLAYWRIGHT_INSTALL": "1"},
    capture_output=True,
    text=True
)

print(result.stdout)
```

## Detailed Workflow (Internal)

The adaptive test script (`run_adaptive_test.py`) handles:

### Step 1: Page Analysis
- Loads the page with Nova Act
- Extracts title, navigation, purpose
- Identifies key elements (docs, demo, pricing)

### Step 2: Contextual Persona Generation
- Creates personas based on what the page offers
- Developer persona if API/code focused
- Business persona for evaluation
- Beginner persona if demo available

### Step 3: Realistic Test Case Generation
- Top 3 use cases per persona
- Based on actual page content
- Matched to persona goals

### Step 4: Iterative Test Execution

For each persona + task combination:

```python
from scripts.nova_session import nova_session
from nova_act import BOOL_SCHEMA
import time

observations = []

with nova_session(website_url) as nova:
    start_time = time.time()
    
    # Initial navigation
    observations.append({
        "step": "navigate",
        "action": f"Loaded {website_url}",
        "success": True,
        "notes": "Initial page load"
    })
    
    # Execute task step-by-step (AI-orchestrated)
    # Break into small act() calls based on cookbook guidance
    
    # Example: "Find pricing information" task
    
    # Step 1: Look for pricing link
    nova.act("Look for a link or button for pricing, plans, or subscription")
    found = nova.act_get(
        "Is there a visible pricing or plans link?",
        schema=BOOL_SCHEMA
    )
    
    observations.append({
        "step": "find_pricing_link",
        "action": "Search for pricing navigation",
        "success": found.parsed_response,
        "notes": "Easy to find" if found.parsed_response else "Not immediately visible - UX friction"
    })
    
    if found.parsed_response:
        # Step 2: Navigate to pricing
        nova.act("Click on the pricing or plans link")
        
        # Step 3: Analyze pricing page
        is_clear = nova.act_get(
            "Is the pricing information clearly displayed with prices and features?",
            schema=BOOL_SCHEMA
        )
        
        observations.append({
            "step": "view_pricing",
            "action": "Accessed pricing page",
            "success": is_clear.parsed_response,
            "notes": "Clear pricing display" if is_clear.parsed_response else "Pricing unclear or confusing"
        })
    else:
        # Alternative path - try search
        nova.act("Look for a search function")
        # ... continue orchestrating
    
    duration = time.time() - start_time
    
    # Document overall task result
    task_success = all(obs["success"] for obs in observations if obs["success"] is not None)
    
    results.append({
        "persona": persona_name,
        "task": task_description,
        "success": task_success,
        "duration": duration,
        "observations": observations,
        "friction_points": [obs for obs in observations if not obs.get("success")]
    })
```

### Step 5: Pool and Analyze Results

After all tests:
1. Identify common friction points across personas
2. Note accessibility issues for low-tech personas
3. Flag efficiency problems (too many steps)
4. Document task failures (major UX issues)

### Step 6: Generate Report

```python
import json
from scripts.enhanced_report_generator import generate_enhanced_report

# Save results
with open("test_results_adaptive.json", "w") as f:
    json.dump(results, f, indent=2)

# Generate HTML report
report_path = generate_enhanced_report(
    page_analysis=page_analysis,
    results=test_results
)

print(f"Report: {report_path}")
```

## Key Principles

### Dynamic Task Decomposition

The AI should decide how to break down each task based on:
- Website complexity
- Persona's technical level
- Task nature (navigation vs data entry vs search)

**Low-tech persona example:**
```python
# More explicit, step-by-step
nova.act("Look for a button labeled 'Contact' or 'Contact Us'")
nova.act("Click on the Contact button")
result = nova.act_get("Is there a phone number or email address visible?")
```

**High-tech persona example:**
```python
# Test efficiency features
nova.act("Look for keyboard shortcuts or quick access features")
nova.act("Try to use search (Ctrl+K or Cmd+K)")
```

### Real-Time Observation

After EVERY `act()` call, analyze:
- Did it succeed?
- Was the UI element easy to find?
- Was the label clear?
- How many attempts needed?
- Any error messages?

Document friction immediately in observations.

### Persona-Aware Prompting

Adapt `act()` prompts to persona characteristics:
- **Elderly/low-tech:** Look for obvious, labeled buttons; read everything
- **Power users:** Try keyboard shortcuts, advanced features
- **Mobile users:** Test mobile responsiveness, touch targets
- **Screen reader users:** Test keyboard navigation, ARIA labels

## Resources

### `references/nova-act-cookbook.md`
**MUST READ before starting any test.** Contains best practices for:
- Effective act() prompting
- Task decomposition strategies
- Data extraction patterns
- Error handling
- Persona adaptation

### `references/persona-examples.md`
Template personas with detailed profiles:
- Tech-savvy millennial
- Elderly first-timer
- Busy professional
- Student/budget-conscious
- Accessibility-focused
- International/non-native speaker

### `scripts/nova_session.py`
Thin wrapper providing Nova Act session primitive:
```python
with nova_session(url, headless=True, logs_dir="./logs") as nova:
    nova.act("action")
    result = nova.act_get("query", schema=Schema)
```

### `scripts/enhanced_report_generator.py`
Compiles observations into HTML usability report with trace file links.

### `assets/report-template.html`
Professional HTML template for usability reports.

## ⚠️ IMPORTANT: First-Time Setup Required

**This skill requires dependencies that must be installed before use.**

### For AI Agents: Dependency Check

**ALWAYS check if dependencies are installed before running tests:**

```python
# Quick dependency check
try:
    import nova_act
    print("✅ Dependencies installed")
except ImportError:
    print("📦 Dependencies not installed. Please run:")
    print("   pip3 install nova-act pydantic playwright")
    print("   playwright install chromium")
    print("")
    print("This will take 2-3 minutes to download browsers (~300MB)")
```

### For Users: One-Time Setup

**Step 1: Install Python packages**
```bash
pip3 install nova-act pydantic playwright
```

**Step 2: Install Playwright browser**
```bash
playwright install chromium
```

**Step 3: Configure API key**
1. Get your Nova Act API key from [AWS Console](https://console.aws.amazon.com/)
2. Create config file:
```bash
mkdir -p ~/.openclaw/config
echo '{"apiKey": "your-key-here"}' > ~/.openclaw/config/nova-act.json
```
3. Replace `your-key-here` with your actual Nova Act API key

## Example: AI-Orchestrated Test

**User request:** "Test example.com for elderly users"

**AI orchestration:**

1. Read `references/nova-act-cookbook.md`
2. Read `references/persona-examples.md`
3. Generate elderly persona (Dorothy, 72, low tech proficiency)
4. Generate tasks:
   - "Find contact information"
   - "Read about services"
   - "Navigate to FAQ"
5. For each task, dynamically orchestrate Nova Act:
   - Start session
   - Execute small act() steps
   - Observe and analyze each result
   - Take notes on friction (small text, unclear labels, etc.)
   - Continue or adapt based on observations
6. Pool observations
7. Generate HTML report with findings and recommendations

**The AI decides every step.** The skill just provides tools and guidance.

## File Structure

```
nova-act-usability/
├── SKILL.md                          # This file
├── README.md                         # User documentation
├── skill.json                        # Skill manifest
├── scripts/
│   ├── run_adaptive_test.py          # Main orchestrator (accepts URL arg)
│   ├── nova_session.py               # Session wrapper
│   ├── enhanced_report_generator.py  # HTML report generator
│   └── trace_finder.py               # Extract trace file paths
├── references/
│   ├── nova-act-cookbook.md          # Best practices
│   └── persona-examples.md           # Template personas
└── assets/
    └── report-template.html          # HTML template

```

## Output Files (Created in Working Directory)

When you run a test, these files are created in your current working directory:

```
./
├── nova_act_logs/                    # Nova Act trace files
│   ├── act_<id>_output.html         # Session recordings
│   └── ...
├── test_results_adaptive.json        # Raw test results
└── nova_act_usability_report.html   # Final report
```

All paths are relative - works from any installation location!
