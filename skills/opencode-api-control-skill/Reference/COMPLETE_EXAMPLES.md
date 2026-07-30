# Complete Workflow Examples

## Example 1: Create Simple Project

**Goal**: Create a todo app from scratch
```bash
#!/bin/bash

# Get skill directory
cd /path/to/opencode-skill

# Read config
PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)

# 1. Update providers
echo "Updating providers..."
bash ./scripts/update_providers.sh

# 2. Create project directory
PROJECT_NAME="todo-app"
PROJECT_PATH="$PROJECTS_DIR/$PROJECT_NAME"
mkdir -p "$PROJECT_PATH"
echo "Created: $PROJECT_PATH"

# 3. Create session
echo "Creating session..."
SESSION_ID=$(bash ./scripts/create_session.sh "$PROJECT_PATH" "Todo App")
echo "Session: $SESSION_ID"

# 4. Send task
echo "Starting development..."
bash ./scripts/send_message.sh "Create a Todo app with React and TypeScript. Include add, delete, and complete functions with local storage."

# 5. Show changes
echo -e "\n=== Files Created ==="
bash ./scripts/get_diff.sh
```

**Output**:
```
Updating providers...
✓ Updated providers cache: 3 providers available
Created: /home/user/projects/todo-app
Creating session...
Session: ses_abc123
Starting development...
[AI response with code]

=== Files Created ===
added: src/App.tsx (+45/-0)
added: src/components/TodoList.tsx (+67/-0)
added: src/types/todo.ts (+8/-0)
added: package.json (+25/-0)
```

---

## Example 2: Continue Existing Project

**Goal**: Add authentication to existing app
```bash
#!/bin/bash

cd /path/to/opencode-skill

# 1. Load existing project
echo "Loading project..."
bash ./scripts/load_project.sh "todo-app"

# 2. Continue work
bash ./scripts/send_message.sh "Add user authentication with login and registration forms. Use JWT tokens."

# 3. Monitor progress
bash ./scripts/monitor_session.sh
```

**Output**:
```
Loading project...
✓ Loaded project: todo-app
[AI implementing authentication]
⟳ Processing...
Creating auth components...
Adding JWT handling...
✓ Task completed
📊 Tokens: 2150, Cost: $0.035
```

---

## Example 3: Use Specific Provider

**Goal**: Build dashboard with Claude Sonnet
```bash
#!/bin/bash

cd /path/to/opencode-skill

PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)

# 1. Update providers
bash ./scripts/update_providers.sh

# 2. Select provider (user requested "Claude Sonnet")
echo "Selecting Claude Sonnet..."
RESULT=$(bash ./scripts/select_provider.sh "claude" "sonnet")
PROVIDER_ID=$(echo "$RESULT" | cut -d' ' -f1)
MODEL_ID=$(echo "$RESULT" | cut -d' ' -f2)
echo "Using: $PROVIDER_ID/$MODEL_ID"

# 3. Create project
PROJECT_PATH="$PROJECTS_DIR/dashboard"
mkdir -p "$PROJECT_PATH"

# 4. Create session
SESSION_ID=$(bash ./scripts/create_session.sh "$PROJECT_PATH" "Dashboard with Claude")

# 5. Send with selected provider
bash ./scripts/send_message.sh \
  "Create a modern dashboard with React, TypeScript, Tailwind CSS, and Chart.js" \
  "$PROVIDER_ID" \
  "$MODEL_ID"
```

**Output**:
```
✓ Updated providers cache: 3 providers available
Selecting Claude Sonnet...
Using: anthropic/claude-sonnet-4-5
✓ Saved state: ses_xyz789
[AI building dashboard with Claude]
```

---

## Example 4: Multi-Phase Development

**Goal**: Plan then implement e-commerce platform
```bash
#!/bin/bash

cd /path/to/opencode-skill

PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)
PROJECT_PATH="$PROJECTS_DIR/ecommerce"
mkdir -p "$PROJECT_PATH"

# Phase 1: Planning
echo "=== PHASE 1: Planning ==="
SESSION_ID=$(bash ./scripts/create_session.sh "$PROJECT_PATH" "E-commerce Platform")

bash ./scripts/send_message.sh \
  "Analyze and plan an e-commerce platform with: product catalog, shopping cart, checkout, user accounts, admin panel. Suggest architecture and tech stack." \
  "" "" "plan"  # Use plan agent

echo -e "\n[Reviewing plan...]\n"
sleep 2

# Phase 2: Implementation
echo "=== PHASE 2: Implementation ==="

bash ./scripts/send_message.sh \
  "Implement the planned e-commerce platform. Start with project structure and core features." \
  "" "" "build"  # Use build agent

# Phase 3: Monitor
echo "=== PHASE 3: Monitoring ==="
bash ./scripts/monitor_session.sh

# Phase 4: Review
echo -e "\n=== PHASE 4: Review ==="
bash ./scripts/get_diff.sh

# Save this important project
bash ./scripts/save_project.sh "ecommerce"
echo "✓ Project saved"
```

---

## Example 5: Manage Multiple Projects

**Goal**: Work on frontend and backend simultaneously
```bash
#!/bin/bash

cd /path/to/opencode-skill

PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)

# === Frontend Project ===
echo "=== Starting Frontend ==="
mkdir -p "$PROJECTS_DIR/frontend"
SESSION_FRONTEND=$(bash ./scripts/create_session.sh "$PROJECTS_DIR/frontend" "Frontend")
bash ./scripts/save_project.sh "frontend"

bash ./scripts/send_message.sh "Create React frontend with TypeScript, Tailwind, and React Router"

# === Backend Project ===
echo -e "\n=== Starting Backend ==="
mkdir -p "$PROJECTS_DIR/backend"
SESSION_BACKEND=$(bash ./scripts/create_session.sh "$PROJECTS_DIR/backend" "Backend")
bash ./scripts/save_project.sh "backend"

bash ./scripts/send_message.sh "Create Node.js API with Express, TypeScript, and MongoDB"

# === Switch Between Projects ===

echo -e "\n=== Working on Frontend ==="
bash ./scripts/load_project.sh "frontend"
bash ./scripts/send_message.sh "Add authentication pages"

echo -e "\n=== Working on Backend ==="
bash ./scripts/load_project.sh "backend"
bash ./scripts/send_message.sh "Add JWT authentication endpoints"

# === Review Both ===

echo -e "\n=== Frontend Changes ==="
bash ./scripts/load_project.sh "frontend"
bash ./scripts/get_diff.sh

echo -e "\n=== Backend Changes ==="
bash ./scripts/load_project.sh "backend"
bash ./scripts/get_diff.sh
```

---

## Example 6: Provider Not Available Fallback

**Goal**: Try specific provider, fall back to default
```bash
#!/bin/bash

cd /path/to/opencode-skill

PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)

# User requested "Gemini Pro"
REQUESTED_PROVIDER="gemini"
REQUESTED_MODEL="pro"

# Try to select
if RESULT=$(bash ./scripts/select_provider.sh "$REQUESTED_PROVIDER" "$REQUESTED_MODEL" 2>/dev/null); then
  PROVIDER_ID=$(echo "$RESULT" | cut -d' ' -f1)
  MODEL_ID=$(echo "$RESULT" | cut -d' ' -f2)
  echo "✓ Using requested: $PROVIDER_ID/$MODEL_ID"
else
  echo "⚠ $REQUESTED_PROVIDER not available, using default"
  PROVIDER_ID=$(jq -r '.default_provider' ./config.json)
  MODEL_ID=$(jq -r '.default_model' ./config.json)
  echo "✓ Using default: $PROVIDER_ID/$MODEL_ID"
fi

# Create project
mkdir -p "$PROJECTS_DIR/my-app"
SESSION_ID=$(bash ./scripts/create_session.sh "$PROJECTS_DIR/my-app" "App")

# Send with selected/default provider
bash ./scripts/send_message.sh \
  "Create application" \
  "$PROVIDER_ID" \
  "$MODEL_ID"
```

---

## Example 7: Long Task with Monitoring

**Goal**: Build complex app and monitor progress
```bash
#!/bin/bash

cd /path/to/opencode-skill

PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)
mkdir -p "$PROJECTS_DIR/complex-app"

# Create session
SESSION_ID=$(bash ./scripts/create_session.sh "$PROJECTS_DIR/complex-app" "Complex App")

# Start task in background
bash ./scripts/send_message.sh \
  "Create a full-stack application with: React frontend, Node.js backend, PostgreSQL database, user authentication, real-time features with WebSockets, and comprehensive testing." &

# Monitor with logging
bash ./scripts/monitor_session.sh | tee build.log

# After completion, review
echo -e "\n=== Summary ==="
bash ./scripts/get_diff.sh | wc -l
echo "files modified"

echo -e "\nSaved log to: build.log"
```

---

## Example 8: Batch Project Creation

**Goal**: Create multiple related microservices
```bash
#!/bin/bash

cd /path/to/opencode-skill

PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)

SERVICES=("auth-service" "user-service" "product-service" "order-service")

for SERVICE in "${SERVICES[@]}"; do
  echo "=== Creating $SERVICE ==="
  
  # Create directory
  mkdir -p "$PROJECTS_DIR/$SERVICE"
  
  # Create session
  SESSION_ID=$(bash ./scripts/create_session.sh \
    "$PROJECTS_DIR/$SERVICE" \
    "${SERVICE^}")
  
  # Generate service
  bash ./scripts/send_message.sh \
    "Create a Node.js microservice for $SERVICE with Express, TypeScript, and Docker support"
  
  # Save project
  bash ./scripts/save_project.sh "$SERVICE"
  
  echo "✓ $SERVICE complete"
  echo "---"
done

echo -e "\n✓ All microservices created"

# List all projects
echo -e "\nProjects:"
ls -1 ./state/*.json | grep -v 'current\|init' | xargs -n1 basename -s .json
```

---

## Example 9: Review and Iterate

**Goal**: Get AI to review and improve code
```bash
#!/bin/bash

cd /path/to/opencode-skill

# Load existing project
bash ./scripts/load_project.sh "my-app"

# Round 1: Review
echo "=== Review Round 1 ==="
bash ./scripts/send_message.sh \
  "Review the current codebase for: code quality, best practices, security issues, and performance. List specific improvements needed."

# Round 2: Apply improvements
echo -e "\n=== Applying Improvements ==="
bash ./scripts/send_message.sh \
  "Apply the improvements you identified. Focus on security and performance first."

# Round 3: Add tests
echo -e "\n=== Adding Tests ==="
bash ./scripts/send_message.sh \
  "Add comprehensive tests for all components and functions using Jest and React Testing Library."

# Final review
echo -e "\n=== Final Changes ==="
bash ./scripts/get_diff.sh
```

---

## Example 10: Emergency Recovery

**Goal**: Recover from failed session
```bash
#!/bin/bash

cd /path/to/opencode-skill

PROJECTS_DIR=$(jq -r '.projects_base_dir' ./config.json)

# Check if current session is stuck
if bash ./scripts/check_status.sh | grep -q "error"; then
  echo "⚠ Current session has error"
  
  # Create new session in same project
  source ./scripts/load_state.sh
  
  echo "Creating recovery session..."
  NEW_SESSION=$(bash ./scripts/create_session.sh \
    "$PROJECT_PATH" \
    "Recovery Session")
  
  echo "✓ New session: $NEW_SESSION"
  
  # Continue work
  bash ./scripts/send_message.sh "Continue the previous task"
else
  echo "✓ Session is healthy"
fi
```

---

## Quick Command Reference
```bash
# Setup (ensure server is running)
bash ./scripts/start_server.sh
bash ./scripts/update_providers.sh

# Create
mkdir -p "$PROJECT_PATH"
bash ./scripts/create_session.sh "$PROJECT_PATH" "Title"

# Work
bash ./scripts/send_message.sh "prompt"
bash ./scripts/send_message.sh "prompt" "provider" "model"
bash ./scripts/send_message.sh "prompt" "" "" "agent"

# Monitor
bash ./scripts/monitor_session.sh
bash ./scripts/check_status.sh
bash ./scripts/get_diff.sh

# Manage
bash ./scripts/save_project.sh "name"
bash ./scripts/load_project.sh "name"
source ./scripts/load_state.sh
```
---
**Author:** [Malek RSH](https://github.com/malek262) | **Repository:** [OpenCode-CLI-Controller](https://github.com/malek262/opencode-api-control-skill)
