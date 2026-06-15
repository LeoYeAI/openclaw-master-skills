# Hierarchical Task Management

Linear context accumulation doesn't scale. For complex tasks, you need structured working memory that persists across iterations.

## The Problem

Without task hierarchy:
- LLM must re-derive progress from raw message history every turn
- No clear prioritization when steering messages arrive
- Completed subtask details clutter active context
- No graceful handling of interruptions

## Task Stack/Tree Structure

```typescript
interface TaskStack {
  tasks: Task[];
  activeTaskId: string | null;
}

interface Task {
  id: string;
  parentId: string | null;
  title: string;
  description: string;
  status: TaskStatus;
  priority: number;  // Higher = more urgent
  createdAt: number;
  updatedAt: number;
  subtasks: Task[];
  result?: TaskResult;
  metadata: Record<string, unknown>;
}

type TaskStatus = 
  | 'pending'      // Not started
  | 'in_progress'  // Currently executing
  | 'blocked'      // Waiting on dependency or human
  | 'complete'     // Successfully finished
  | 'failed'       // Failed with error
  | 'abandoned';   // Intentionally stopped

interface TaskResult {
  success: boolean;
  summary: string;
  artifacts?: string[];  // File paths, URLs, etc.
  error?: string;
}
```

## Example Task Tree

```json
{
  "tasks": [{
    "id": "deploy-app",
    "title": "Deploy application to staging",
    "status": "in_progress",
    "priority": 1,
    "subtasks": [
      {
        "id": "check-dockerfile",
        "title": "Verify Dockerfile exists",
        "status": "complete",
        "result": { "success": true, "summary": "Dockerfile found at ./Dockerfile" }
      },
      {
        "id": "build-image",
        "title": "Build Docker image",
        "status": "in_progress",
        "subtasks": [
          { "id": "npm-install", "status": "complete" },
          { "id": "npm-build", "status": "in_progress" },
          { "id": "docker-build", "status": "pending" }
        ]
      },
      {
        "id": "push-registry",
        "title": "Push to container registry",
        "status": "pending"
      },
      {
        "id": "verify-deployment",
        "title": "Verify deployment health",
        "status": "pending"
      }
    ]
  }],
  "activeTaskId": "npm-build"
}
```

## Operations

### Create Task

```typescript
function createTask(stack: TaskStack, task: Partial<Task>): Task {
  const newTask: Task = {
    id: generateId(),
    parentId: task.parentId ?? null,
    title: task.title ?? 'Untitled',
    description: task.description ?? '',
    status: 'pending',
    priority: task.priority ?? 0,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    subtasks: [],
    metadata: task.metadata ?? {},
  };
  
  if (newTask.parentId) {
    const parent = findTask(stack, newTask.parentId);
    parent?.subtasks.push(newTask);
  } else {
    stack.tasks.push(newTask);
  }
  
  return newTask;
}
```

### Update Task Status

```typescript
function updateTaskStatus(
  stack: TaskStack, 
  taskId: string, 
  status: TaskStatus,
  result?: TaskResult
): void {
  const task = findTask(stack, taskId);
  if (!task) return;
  
  task.status = status;
  task.updatedAt = Date.now();
  if (result) task.result = result;
  
  // Propagate status to parent if all siblings complete
  if (status === 'complete' && task.parentId) {
    const parent = findTask(stack, task.parentId);
    if (parent && parent.subtasks.every(t => t.status === 'complete')) {
      updateTaskStatus(stack, parent.id, 'complete', {
        success: true,
        summary: `All ${parent.subtasks.length} subtasks completed`,
      });
    }
  }
}
```

### Get Next Task

```typescript
function getNextTask(stack: TaskStack): Task | null {
  // Find highest-priority pending task with no pending dependencies
  const candidates = flattenTasks(stack)
    .filter(t => t.status === 'pending')
    .filter(t => !hasPendingDependencies(stack, t))
    .sort((a, b) => b.priority - a.priority);
  
  return candidates[0] ?? null;
}
```

## Handling Interruptions

When a steering message arrives mid-task:

```typescript
function handleInterruption(
  stack: TaskStack,
  steeringMessage: string,
  urgency: 'low' | 'medium' | 'high' | 'critical'
): InterruptionDecision {
  const activeTask = stack.activeTaskId 
    ? findTask(stack, stack.activeTaskId) 
    : null;
  
  if (urgency === 'critical') {
    // Pause everything, handle immediately
    if (activeTask) {
      activeTask.status = 'blocked';
      activeTask.metadata.pausedAt = Date.now();
      activeTask.metadata.pausedBy = 'steering';
    }
    return { action: 'handle_now', pausedTask: activeTask?.id };
  }
  
  if (urgency === 'high') {
    // Complete current step, then switch
    return { action: 'finish_step_then_handle' };
  }
  
  // Queue for after current task branch
  const interruptTask = createTask(stack, {
    title: 'Handle steering message',
    description: steeringMessage,
    priority: urgency === 'medium' ? 5 : 1,
  });
  
  return { action: 'queued', taskId: interruptTask.id };
}
```

## Persistence

Store task stack in session file alongside messages:

```typescript
interface EnhancedSession {
  messages: AgentMessage[];
  taskStack: TaskStack;
  workingMemory: WorkingMemory;
}
```

On session load:
```typescript
const session = await loadSession(sessionFile);
const taskStack = session.taskStack ?? { tasks: [], activeTaskId: null };
```

On save:
```typescript
await saveSession(sessionFile, {
  messages: sessionManager.messages,
  taskStack: currentTaskStack,
  workingMemory: currentWorkingMemory,
});
```

## Context Injection

Inject task context into system prompt:

```typescript
function buildTaskContextPrompt(stack: TaskStack): string {
  const active = stack.activeTaskId 
    ? findTask(stack, stack.activeTaskId) 
    : null;
  
  if (!active) return '';
  
  const completed = flattenTasks(stack)
    .filter(t => t.status === 'complete')
    .map(t => `- ✓ ${t.title}`);
  
  const pending = flattenTasks(stack)
    .filter(t => t.status === 'pending')
    .map(t => `- ○ ${t.title}`);
  
  return `
## Current Task
**${active.title}**
${active.description}

## Progress
### Completed
${completed.join('\n') || '(none)'}

### Remaining
${pending.join('\n') || '(none)'}
`.trim();
}
```

## Integration with OpenClaw

### Storage Location

```
~/.openclaw/sessions/
  {sessionKey}/
    transcript.json    # Message history
    task-stack.json    # Task hierarchy
    working-memory.json # Summarized context
```

### System Prompt Extension

Add to `src/agents/system-prompt.ts`:

```typescript
if (taskStack && taskStack.tasks.length > 0) {
  sections.push({
    label: '## Current Work',
    content: buildTaskContextPrompt(taskStack),
  });
}
```

## Benefits

1. **Structured progress tracking**: Know exactly where you are
2. **Efficient context**: Only active task in prompt, completed summarized
3. **Graceful interruptions**: Can pause/resume without losing state
4. **Priority management**: Important tasks bubble up automatically
5. **Debuggability**: Clear audit trail of what happened
