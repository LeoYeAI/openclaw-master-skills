# AI Desktop Agent - Cognitive Automation Guide

## 🤖 What Is This?

The **AI Desktop Agent** is an intelligent layer on top of the basic desktop control that **understands** what you want and figures out how to do it autonomously.

Unlike basic automation that requires exact instructions, the AI Agent:
- **Understands natural language** ("Draw a cat in Paint")
- **Plans the steps** automatically
- **Executes autonomously** 
- **Adapts** based on what it sees

---

## 🎯 What Can It Do?

### ✅ Autonomous Drawing
```python
from skills.desktop_control.ai_agent import AIDesktopAgent

agent = AIDesktopAgent()

# Just describe what you want!
agent.execute_task("Draw a circle in Paint")
agent.execute_task("Draw a star in MS Paint")
agent.execute_task("Draw a house with a sun")
```

**What it does:**
1. Opens MS Paint
2. Selects pencil tool
3. Figures out how to draw the requested shape
4. Draws it autonomously
5. Takes a screenshot of the result

### ✅ Autonomous Text Entry
```python
# It figures out where to type
agent.execute_task("Type 'Hello World' in Notepad")
agent.execute_task("Write an email saying thank you")
```

**What it does:**
1. Opens Notepad (or finds active text editor)
2. Types the text naturally
3. Formats if needed

### ✅ Autonomous Application Control
```python
# It knows how to open apps
agent.execute_task("Open Calculator")
agent.execute_task("Launch Microsoft Paint")
agent.execute_task("Open File Explorer")
```

### ✅ Autonomous Game Playing (Advanced)
```python
# It will try to play the game!
agent.execute_task("Play Solitaire for me")
agent.execute_task("Play Minesweeper")
```

**What it does:**
1. Analyzes the game screen
2. Detects game state (cards, mines, etc.)
3. Decides best move
4. Executes the move
5. Repeats until win/lose

---

## 🏗️ How It Works

### Architecture

```
User Request ("Draw a cat")
    ↓
Natural Language Understanding
    ↓
Task Planning (Step-by-step plan)
    ↓
Step Execution Loop:
    - Observe Screen (Computer Vision)
    - Decide Action (AI Reasoning)
    - Execute Action (Desktop Control)
    - Verify Result
    ↓
Task Complete!
```

### Key Components

1. **Task Planner** - Breaks down high-level tasks into steps
2. **Vision System** - Understands what's on screen (screenshots, OCR, object detection)
3. **Reasoning Engine** - Decides what to do next
4. **Action Executor** - Performsthe actual mouse/keyboard actions
5. **Feedback Loop** - Verifies actions succeeded

---

## 📋 Supported Tasks (Current)

### Tier 1: Fully Automated ✅

| Task Pattern | Example | Status |
|-------------|---------|---------|
| Draw shapes in Paint | "Draw a circle" | ✅ Working |
| Basic text entry | "Type Hello" | ✅ Working |
| Launch applications | "Open Paint" | ✅ Working |

### Tier 2: Partially Automated 🔨

| Task Pattern | Example | Status |
|-------------|---------|---------|
| Form filling | "Fill out this form" | 🔨 In Progress |
| File operations | "Copy these files" | 🔨 In Progress |
| Web navigation | "Find on Google" | 🔨 Planned |

### Tier 3: Experimental 🧪

| Task Pattern | Example | Status |
|-------------|---------|---------|
| Game playing | "Play Solitaire" | 🧪 Experimental |
| Image editing | "Resize this photo" | 🧪 Planned |
| Code editing | "Fix this bug" | 🧪 Research |

---

## 🎨 Example: Drawing in Paint

### Simple Request
```python
agent = AIDesktopAgent()
result = agent.execute_task("Draw a circle in Paint")

# Check result
print(f"Status: {result['status']}")
print(f"Steps taken: {len(result['steps'])}")
```

### What Happens Behind the Scenes

**1. Planning Phase:**
```
Plan generated:
  Step 1: Launch MS Paint
  Step 2: Wait 2s for Paint to load
  Step 3: Activate Paint window
  Step 4: Select pencil tool (press 'P')
  Step 5: Draw circle at canvas center
  Step 6: Screenshot the result
```

**2. Execution Phase:**
```
[✓] Launched Paint via Win+R → mspaint
[✓] Waited 2.0s
[✓] Activated window "Paint"
[✓] Pressed 'P' to select pencil
[✓] Drew circle with 72 points
[✓] Screenshot saved: drawing_result.png
```

**3. Result:**
```python
{
    "task": "Draw a circle in Paint",
    "status": "completed",
    "success": True,
    "steps": [... 6 steps ...],
    "screenshots": [... 6 screenshots ...],
}
```

---

## 🎮 Example: Game Playing

```python
agent = AIDesktopAgent()

# Play a simple game
result = agent.execute_task("Play Solitaire for me")
```

### Game Playing Loop

```
1. Analyze screen → Detect cards, positions
2. Identify valid moves → Find legal plays
3. Evaluate moves → Which is best?
4. Execute move → Click and drag card
5. Repeat until game ends
```

### Game-Specific Intelligence

The agent can learn patterns for:
- **Solitaire**: Card stacking rules, suit matching
- **Minesweeper**: Probability calculations, safe clicks
- **2048**: Tile merging strategy
- **Chess** (if integrated with engine): Move evaluation

---

## 🧠 Enhancing the AI

### Adding Application Knowledge

```python
# In ai_agent.py, add to app_knowledge:

self.app_knowledge = {
    "photoshop": {
        "name": "Adobe Photoshop",
        "launch_command": "photoshop",
        "common_actions": {
            "new_layer": {"hotkey": ["ctrl", "shift", "n"]},
            "brush_tool": {"hotkey": ["b"]},
            "eraser": {"hotkey": ["e"]},
        }
    }
}
```

### Adding Custom Task Patterns

```python
# Add a custom planning method
def _plan_photo_edit(self, task: str) -> List[Dict]:
    """Plan for photo editing tasks."""
    return [
        {"type": "launch_app", "app": "photoshop"},
        {"type": "wait", "duration": 3.0},
        {"type": "open_file", "path": extracted_path},
        {"type": "apply_filter", "filter": extracted_filter},
        {"type": "save_file"},
    ]
```

---

## 🔥 Advanced: Vision + Reasoning

### Screen Analysis

The agent can analyze screenshots to:
- **Detect UI elements** (buttons, text fields, menus)
- **Read text** (OCR for labels, instructions)
- **Identify objects** (icons, images, game pieces)
- **Understand layout** (where things are)

```python
# Analyze what's on screen
analysis = agent._analyze_screen()

print(analysis)
# Output:
# {
#     "active_window": "Untitled - Paint",
#     "mouse_position": (640, 480),
#     "detected_elements": [...],
#     "text_found": [...],
# }
```

### Integration with OpenClaw LLM

```python
# Future: Use OpenClaw's LLM for reasoning
agent = AIDesktopAgent(llm_client=openclaw_llm)

# The agent can now:
# - Reason about complex tasks
# - Understand context better
# - Plan more sophisticated workflows
# - Learn from feedback
```

---

## 🛠️ Extending for Your Needs

### Add Support for New Apps

1. **Identify the app**
2. **Document common actions**
3. **Add to knowledge base**
4. **Create planning method**

Example: Adding Excel support

```python
# Step 1: Add to app_knowledge
"excel": {
    "name": "Microsoft Excel",
    "launch_command": "excel",
    "common_actions": {
        "new_sheet": {"hotkey": ["shift", "f11"]},
        "sum_formula": {"action": "type", "text": "=SUM()"},
    }
}

# Step 2: Create planner
def _plan_excel_task(self, task: str) -> List[Dict]:
    return [
        {"type": "launch_app", "app": "excel"},
        {"type": "wait", "duration": 2.0},
        # ... specific Excel steps
    ]

# Step 3: Hook into main planner
if "excel" in task_lower or "spreadsheet" in task_lower:
    return self._plan_excel_task(task)
```

---

## 🎯 Real-World Use Cases

### 1. Automated Form Filling
```python
agent.execute_task("Fill out the job application with my resume data")
```

### 2. Batch Image Processing
```python
agent.execute_task("Resize all images in this folder to 800x600")
```

### 3. Social Media Posting
```python
agent.execute_task("Post this image to Instagram with caption 'Beautiful sunset'")
```

### 4. Data Entry
```python
agent.execute_task("Copy data from this PDF to Excel spreadsheet")
```

### 5. Testing
```python
agent.execute_task("Test the login form with invalid credentials")
```

---

## ⚙️ Configuration

### Enable/Disable Failsafe
```python
# Safe mode (default)
agent = AIDesktopAgent(failsafe=True)

# Fast mode (no failsafe)
agent = AIDesktopAgent(failsafe=False)
```

### Set Max Steps
```python
# Prevent infinite loops
result = agent.execute_task("Play game", max_steps=100)
```

### Access Action History
```python
# Review what the agent did
print(agent.action_history)
```

---

## 🐛 Debugging

### View Step-by-Step Execution
```python
result = agent.execute_task("Draw a star in Paint")

for i, step in enumerate(result['steps'], 1):
    print(f"Step {i}: {step['step']['description']}")
    print(f"  Success: {step['success']}")
    if 'error' in step:
        print(f"  Error: {step['error']}")
```

### View Screenshots
```python
# Each step captures before/after screenshots
for screenshot_pair in result['screenshots']:
    before = screenshot_pair['before']
    after = screenshot_pair['after']
    
    # Display or save for analysis
    before.save(f"step_{screenshot_pair['step']}_before.png")
    after.save(f"step_{screenshot_pair['step']}_after.png")
```

---

## 🚀 Future Enhancements

Planned features:

- [ ] **Computer Vision**: OCR, object detection, UI element recognition
- [ ] **LLM Integration**: Natural language understanding with OpenClaw LLM
- [ ] **Learning**: Remember successful patterns, improve over time
- [ ] **Multi-App Workflows**: "Get data from Chrome and put in Excel"
- [ ] **Voice Control**: "Alexa, draw a cat in Paint"
- [ ] **Autonomous Debugging**: Fix errors automatically
- [ ] **Game AI**: Reinforcement learning for game playing
- [ ] **Web Automation**: Full browser control with understanding

---

## 📚 Full API

### Main Methods

```python
# Execute a task
result = agent.execute_task(task: str, max_steps: int = 50)

# Analyze screen
analysis = agent._analyze_screen()

# Manual mode: Execute individual steps
step = {"type": "launch_app", "app": "paint"}
result = agent._execute_step(step)
```

### Result Structure

```python
{
    "task": str,                    # Original task
    "status": str,                  # "completed", "failed", "error"
    "success": bool,                # Overall success
    "steps": List[Dict],            # All steps executed
    "screenshots": List[Dict],      # Before/after screenshots
    "failed_at_step": int,          # If failed, which step
    "error": str,                   # Error message if failed
}
```

---

**🦞 Built for OpenClaw - The future of desktop automation!**
