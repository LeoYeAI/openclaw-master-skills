# Observable State Machine

For production multi-tenant deployment, wrapping the loop in an explicit state machine makes it debuggable, auditable, and trustworthy.

## Why State Machines

Without explicit states:
- Hard to know what the agent is doing
- No clear audit trail
- Debugging requires reading logs
- Client dashboards are guesswork

With state machines:
- Clear visibility into agent status
- Every transition is logged
- Easy to build dashboards
- Clients can track progress in real-time

## State Definitions

```typescript
type AgentState =
  | 'idle'           // Waiting for input
  | 'planning'       // Generating/revising plan
  | 'executing'      // Running tool calls
  | 'reflecting'     // Assessing progress
  | 'waiting_human'  // Paused for human input
  | 'replanning'     // Revising plan based on reflection
  | 'recovering'     // Handling error
  | 'completing'     // Finalizing response
  | 'error'          // Unrecoverable error
  | 'complete';      // Task finished

interface StateContext {
  state: AgentState;
  previousState: AgentState | null;
  enteredAt: number;
  metadata: Record<string, unknown>;
  history: StateTransition[];
}

interface StateTransition {
  from: AgentState;
  to: AgentState;
  trigger: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}
```

## State Diagram

```
                    ┌──────────────────────────────────────────────────────────────┐
                    │                                                              │
                    ▼                                                              │
┌──────┐  user_input   ┌──────────┐  plan_ready   ┌───────────┐                   │
│ IDLE │──────────────▶│ PLANNING │──────────────▶│ EXECUTING │                   │
└──────┘               └──────────┘               └───────────┘                   │
   ▲                        │                          │                          │
   │                        │ complex_task             │ tool_complete            │
   │                        ▼                          ▼                          │
   │                   ┌──────────┐              ┌────────────┐                   │
   │                   │REPLANNING│◀─────────────│ REFLECTING │                   │
   │                   └──────────┘  need_replan └────────────┘                   │
   │                        │                          │                          │
   │                        │ plan_revised             │ on_track                 │
   │                        │                          │                          │
   │                        └──────────────────────────┼──────────────────────────┘
   │                                                   │                          
   │                                                   │ all_done                 
   │                        ┌─────────────┐            │                          
   │    response_sent       │ COMPLETING  │◀───────────┘                          
   └────────────────────────┤             │                                       
                            └─────────────┘                                       
                                                                                  
                    ┌───────────────┐                                             
   From any state:  │ WAITING_HUMAN │  (on low confidence or escalation)         
                    └───────────────┘                                             
                            │                                                     
                            │ human_responded                                     
                            ▼                                                     
                    (returns to previous state)                                   
                                                                                  
                    ┌───────────────┐                                             
   From any state:  │  RECOVERING   │  (on tool error)                           
                    └───────────────┘                                             
                            │                                                     
                            ├── recovered ──▶ (previous state)                   
                            │                                                     
                            └── unrecoverable ──▶ ERROR                          
```

## State Machine Implementation

```typescript
class AgentStateMachine {
  private context: StateContext;
  private observers: StateObserver[] = [];
  
  constructor() {
    this.context = {
      state: 'idle',
      previousState: null,
      enteredAt: Date.now(),
      metadata: {},
      history: [],
    };
  }
  
  // Valid transitions
  private readonly transitions: Record<AgentState, AgentState[]> = {
    idle: ['planning'],
    planning: ['executing', 'error'],
    executing: ['reflecting', 'waiting_human', 'recovering', 'completing'],
    reflecting: ['executing', 'replanning', 'completing'],
    replanning: ['executing', 'error'],
    waiting_human: ['executing', 'planning', 'completing', 'idle'],
    recovering: ['executing', 'replanning', 'error'],
    completing: ['idle'],
    error: ['idle'],
    complete: ['idle'],
  };
  
  transition(to: AgentState, trigger: string, metadata?: Record<string, unknown>): void {
    const from = this.context.state;
    
    // Validate transition
    if (!this.transitions[from].includes(to)) {
      throw new Error(`Invalid transition: ${from} -> ${to}`);
    }
    
    // Record transition
    const transition: StateTransition = {
      from,
      to,
      trigger,
      timestamp: Date.now(),
      metadata,
    };
    
    this.context.history.push(transition);
    this.context.previousState = from;
    this.context.state = to;
    this.context.enteredAt = Date.now();
    this.context.metadata = metadata ?? {};
    
    // Notify observers
    for (const observer of this.observers) {
      observer.onTransition(transition);
    }
  }
  
  getState(): AgentState {
    return this.context.state;
  }
  
  getHistory(): StateTransition[] {
    return [...this.context.history];
  }
  
  subscribe(observer: StateObserver): () => void {
    this.observers.push(observer);
    return () => {
      this.observers = this.observers.filter(o => o !== observer);
    };
  }
}
```

## State-Specific Logic

```typescript
async function runStateMachine(
  machine: AgentStateMachine,
  input: UserInput
): Promise<AgentOutput> {
  machine.transition('planning', 'user_input', { input: input.text });
  
  while (true) {
    const state = machine.getState();
    
    switch (state) {
      case 'planning': {
        const plan = await generatePlan(input);
        if (plan.needsMoreInfo) {
          machine.transition('waiting_human', 'need_clarification', {
            question: plan.clarificationQuestion,
          });
        } else {
          machine.transition('executing', 'plan_ready', { plan });
        }
        break;
      }
      
      case 'executing': {
        const result = await executeNextTool();
        if (result.error) {
          machine.transition('recovering', 'tool_error', { error: result.error });
        } else if (result.needsHuman) {
          machine.transition('waiting_human', 'low_confidence', {
            question: result.question,
          });
        } else {
          machine.transition('reflecting', 'tool_complete', { result });
        }
        break;
      }
      
      case 'reflecting': {
        const reflection = await reflect();
        if (reflection.allDone) {
          machine.transition('completing', 'all_done');
        } else if (reflection.needsReplan) {
          machine.transition('replanning', 'need_replan', {
            reason: reflection.reason,
          });
        } else {
          machine.transition('executing', 'on_track');
        }
        break;
      }
      
      case 'replanning': {
        const newPlan = await replan();
        machine.transition('executing', 'plan_revised', { plan: newPlan });
        break;
      }
      
      case 'waiting_human': {
        const response = await waitForHumanInput();
        if (response.action === 'proceed') {
          machine.transition('executing', 'human_responded', { response });
        } else if (response.action === 'cancel') {
          machine.transition('completing', 'human_cancelled');
        } else {
          machine.transition('planning', 'human_redirected', { newGoal: response.newGoal });
        }
        break;
      }
      
      case 'recovering': {
        const recovery = await attemptRecovery();
        if (recovery.succeeded) {
          machine.transition('executing', 'recovered', { strategy: recovery.strategy });
        } else {
          machine.transition('error', 'unrecoverable', { reason: recovery.reason });
        }
        break;
      }
      
      case 'completing': {
        const output = await formatFinalResponse();
        machine.transition('idle', 'response_sent');
        return output;
      }
      
      case 'error': {
        const output = formatErrorResponse(machine.context.metadata);
        machine.transition('idle', 'error_reported');
        return output;
      }
      
      case 'idle':
        // Shouldn't reach here during execution
        throw new Error('Unexpected idle state during execution');
    }
  }
}
```

## Observability

### Logging Observer

```typescript
class LoggingObserver implements StateObserver {
  onTransition(transition: StateTransition): void {
    const duration = transition.timestamp - (this.lastTransition?.timestamp ?? transition.timestamp);
    console.log(
      `[${new Date(transition.timestamp).toISOString()}] ` +
      `${transition.from} -> ${transition.to} ` +
      `(${transition.trigger}) ` +
      `[${duration}ms]`
    );
    if (transition.metadata) {
      console.log(`  metadata: ${JSON.stringify(transition.metadata)}`);
    }
  }
}
```

### Metrics Observer

```typescript
class MetricsObserver implements StateObserver {
  private stateTimers = new Map<AgentState, number>();
  
  onTransition(transition: StateTransition): void {
    // Track time spent in each state
    const timeInState = transition.timestamp - this.getStateEntryTime(transition.from);
    metrics.histogram('agent.state.duration', timeInState, {
      state: transition.from,
    });
    
    // Count transitions
    metrics.increment('agent.transitions', {
      from: transition.from,
      to: transition.to,
      trigger: transition.trigger,
    });
    
    // Track state entry
    this.stateTimers.set(transition.to, transition.timestamp);
  }
}
```

### Real-time Dashboard Observer

```typescript
class DashboardObserver implements StateObserver {
  constructor(private sessionKey: string, private broadcast: BroadcastFn) {}
  
  onTransition(transition: StateTransition): void {
    this.broadcast({
      type: 'agent_state_change',
      sessionKey: this.sessionKey,
      data: {
        state: transition.to,
        previousState: transition.from,
        trigger: transition.trigger,
        metadata: transition.metadata,
        timestamp: transition.timestamp,
      },
    });
  }
}
```

## Client Dashboard Integration

### State Display Component

```typescript
interface AgentStatusDisplay {
  state: AgentState;
  stateLabel: string;
  progress: number;  // 0-100
  currentAction?: string;
  history: {
    state: AgentState;
    duration: number;
  }[];
}

const STATE_LABELS: Record<AgentState, string> = {
  idle: 'Ready',
  planning: 'Creating plan...',
  executing: 'Working...',
  reflecting: 'Checking progress...',
  replanning: 'Adjusting approach...',
  waiting_human: 'Waiting for input',
  recovering: 'Handling issue...',
  completing: 'Finishing up...',
  error: 'Error occurred',
  complete: 'Done',
};

function calculateProgress(history: StateTransition[]): number {
  // Estimate progress based on state history
  const executingCount = history.filter(t => t.to === 'executing').length;
  const reflectingCount = history.filter(t => t.to === 'reflecting').length;
  
  // Assume average task has 3-5 execution cycles
  const estimatedCycles = 4;
  return Math.min(100, (reflectingCount / estimatedCycles) * 100);
}
```

## Persistence

Store state for session recovery:

```typescript
interface PersistedStateContext {
  state: AgentState;
  enteredAt: number;
  metadata: Record<string, unknown>;
  history: StateTransition[];
  // Additional context for resumption
  pendingToolCalls?: ToolCall[];
  currentPlan?: TaskPlan;
  pendingHumanQuestion?: string;
}

async function persistState(
  sessionKey: string,
  context: StateContext
): Promise<void> {
  await writeFile(
    `~/.openclaw/sessions/${sessionKey}/state.json`,
    JSON.stringify(context, null, 2)
  );
}

async function resumeFromState(
  sessionKey: string
): Promise<AgentStateMachine | null> {
  const statePath = `~/.openclaw/sessions/${sessionKey}/state.json`;
  if (!await exists(statePath)) return null;
  
  const persisted = JSON.parse(await readFile(statePath));
  const machine = new AgentStateMachine();
  machine.loadContext(persisted);
  
  return machine;
}
```

## OpenClaw Integration

### Wrap Existing Loop

In `src/agents/pi-embedded-runner/run.ts`:

```typescript
export async function runEmbeddedPiAgent(
  params: RunEmbeddedPiAgentParams
): Promise<EmbeddedPiRunResult> {
  const machine = new AgentStateMachine();
  
  // Add observers
  machine.subscribe(new LoggingObserver());
  if (params.config?.agents?.metrics?.enabled) {
    machine.subscribe(new MetricsObserver());
  }
  if (params.onStateChange) {
    machine.subscribe({
      onTransition: params.onStateChange,
    });
  }
  
  // Run with state machine
  return runStateMachine(machine, params);
}
```

### Event Emission

Expose state changes via existing event system:

```typescript
// In onAgentEvent callback
if (params.onAgentEvent) {
  machine.subscribe({
    onTransition: (t) => {
      params.onAgentEvent({
        type: 'state_change',
        state: t.to,
        previousState: t.from,
        trigger: t.trigger,
      });
    },
  });
}
```
