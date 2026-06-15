# Confidence-Gated Autonomy

Not all decisions should be made autonomously. State-of-the-art agents assess their own confidence and escalate when appropriate.

## Why It Matters

Without confidence gates:
- Agent makes high-risk decisions without human oversight
- No differentiation between safe and dangerous operations
- Trust is binary (full autonomy or none)
- Errors on irreversible actions are catastrophic

With confidence gates:
- Risky actions get human review
- Checkpoints before destructive operations
- Configurable autonomy levels per client/context
- Graceful degradation when uncertain

## Confidence Assessment

### Assessment Prompt

```typescript
const CONFIDENCE_ASSESSMENT_PROMPT = `
Assess your confidence in the proposed action.

Proposed action: {action}
Context: {context}
Potential impact: {impact}

Consider:
1. How certain are you this is the right approach?
2. What could go wrong?
3. Is this reversible?
4. Do you have enough information?

Rate your confidence (0.0-1.0) and explain briefly.

Format:
Confidence: [0.0-1.0]
Reversible: [yes/no/partial]
Reasoning: [brief explanation]
Question for human (if low confidence): [optional question]
`;
```

### Confidence Levels

```typescript
interface ConfidenceAssessment {
  confidence: number;  // 0.0 - 1.0
  reversible: boolean | 'partial';
  reasoning: string;
  suggestedQuestion?: string;
}

const THRESHOLDS = {
  PROCEED_FREELY: 0.9,      // High confidence, just do it
  PROCEED_CAUTIOUSLY: 0.7,  // Create checkpoint, then proceed
  ASK_HUMAN: 0.5,           // Need human input
  REFUSE: 0.3,              // Don't do this without explicit approval
};
```

### Decision Logic

```typescript
async function gateAction(
  action: ToolCall,
  context: Context,
  config: AutonomyConfig
): Promise<GateDecision> {
  // Skip assessment for low-risk actions
  if (isLowRisk(action)) {
    return { proceed: true, checkpoint: false };
  }
  
  const assessment = await assessConfidence(action, context);
  const threshold = config.confidenceThreshold ?? THRESHOLDS;
  
  if (assessment.confidence >= threshold.PROCEED_FREELY) {
    return { proceed: true, checkpoint: false };
  }
  
  if (assessment.confidence >= threshold.PROCEED_CAUTIOUSLY) {
    return { 
      proceed: true, 
      checkpoint: true,
      reason: assessment.reasoning,
    };
  }
  
  if (assessment.confidence >= threshold.ASK_HUMAN) {
    return {
      proceed: false,
      waitForHuman: true,
      question: assessment.suggestedQuestion ?? 
        `Should I proceed with: ${describeAction(action)}?`,
      options: ['Yes, proceed', 'No, cancel', 'Modify approach'],
    };
  }
  
  return {
    proceed: false,
    refused: true,
    reason: `Confidence too low (${assessment.confidence}): ${assessment.reasoning}`,
  };
}
```

## Risk Classification

### Action Risk Levels

```typescript
type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

const TOOL_RISK_MAP: Record<string, RiskLevel> = {
  // Low risk - read-only, reversible
  'Read': 'low',
  'web_search': 'low',
  'web_fetch': 'low',
  'sessions_list': 'low',
  
  // Medium risk - reversible side effects
  'Write': 'medium',  // Can overwrite
  'Edit': 'medium',
  'exec': 'medium',   // Depends on command
  
  // High risk - may be irreversible
  'message': 'high',   // Sends external comms
  'browser': 'high',   // Can click things
  
  // Critical - definitely irreversible
  // (custom tools like delete, deploy, etc.)
};

function classifyRisk(action: ToolCall): RiskLevel {
  const baseRisk = TOOL_RISK_MAP[action.name] ?? 'medium';
  
  // Elevate risk for certain patterns
  if (action.name === 'exec') {
    const cmd = action.arguments.command as string;
    if (/rm\s+-rf|drop\s+table|delete\s+from/i.test(cmd)) {
      return 'critical';
    }
    if (/git\s+push|npm\s+publish|docker\s+push/i.test(cmd)) {
      return 'high';
    }
  }
  
  if (action.name === 'message') {
    // Sending to external channels is higher risk
    return 'high';
  }
  
  return baseRisk;
}
```

### Context-Aware Risk

```typescript
function adjustRiskForContext(
  baseRisk: RiskLevel,
  context: Context
): RiskLevel {
  // Elevate risk in production environments
  if (context.environment === 'production') {
    return elevateRisk(baseRisk);
  }
  
  // Reduce risk for test/sandbox
  if (context.environment === 'sandbox') {
    return reduceRisk(baseRisk);
  }
  
  // Elevate for first-time actions
  if (!context.hasPerformedBefore(action.name)) {
    return elevateRisk(baseRisk);
  }
  
  return baseRisk;
}
```

## Human Escalation

### Escalation Interface

```typescript
interface EscalationRequest {
  id: string;
  action: ToolCall;
  question: string;
  options: string[];
  context: string;
  urgency: 'low' | 'normal' | 'high';
  timeout?: number;  // Auto-decline after X seconds
}

async function requestHumanInput(
  request: EscalationRequest
): Promise<HumanResponse> {
  // Pause the agent loop
  pauseExecution();
  
  // Send notification to human
  await notify(request);
  
  // Wait for response (or timeout)
  const response = await waitForResponse(request.id, request.timeout);
  
  // Resume with decision
  resumeExecution();
  
  return response;
}
```

### Notification Channels

```typescript
async function notify(request: EscalationRequest): Promise<void> {
  const channels = getNotificationChannels();
  
  const message = formatEscalationMessage(request);
  
  // Send to all configured channels
  for (const channel of channels) {
    await channel.send(message, {
      priority: request.urgency,
      buttons: request.options.map(opt => ({
        label: opt,
        action: `respond:${request.id}:${opt}`,
      })),
    });
  }
}
```

## Checkpointing

Before high-risk actions, save state:

```typescript
interface Checkpoint {
  id: string;
  timestamp: number;
  context: Context;
  taskStack: TaskStack;
  pendingAction: ToolCall;
  files?: FileSnapshot[];  // For file operations
}

async function createCheckpoint(
  context: Context,
  action: ToolCall
): Promise<Checkpoint> {
  const checkpoint: Checkpoint = {
    id: generateId(),
    timestamp: Date.now(),
    context: cloneContext(context),
    taskStack: cloneTaskStack(context.taskStack),
    pendingAction: action,
  };
  
  // For file operations, snapshot the file
  if (action.name === 'Write' || action.name === 'Edit') {
    const path = action.arguments.path as string;
    if (await exists(path)) {
      checkpoint.files = [{
        path,
        content: await readFile(path),
      }];
    }
  }
  
  await saveCheckpoint(checkpoint);
  return checkpoint;
}

async function rollback(checkpointId: string): Promise<void> {
  const checkpoint = await loadCheckpoint(checkpointId);
  
  // Restore files
  for (const file of checkpoint.files ?? []) {
    await writeFile(file.path, file.content);
  }
  
  // Restore context (handled by caller)
  return checkpoint.context;
}
```

## Configuration

### Per-Client Autonomy Levels

```typescript
interface AutonomyConfig {
  level: 'minimal' | 'standard' | 'full';
  
  // Override thresholds
  confidenceThreshold?: typeof THRESHOLDS;
  
  // Always require approval for these
  alwaysAsk?: string[];  // Tool names
  
  // Never require approval for these
  neverAsk?: string[];
  
  // Auto-decline after timeout (ms)
  escalationTimeout?: number;
  
  // Create checkpoints before these
  checkpointBefore?: string[];
}

// Presets
const AUTONOMY_PRESETS: Record<string, AutonomyConfig> = {
  minimal: {
    level: 'minimal',
    confidenceThreshold: {
      PROCEED_FREELY: 0.99,
      PROCEED_CAUTIOUSLY: 0.95,
      ASK_HUMAN: 0.8,
      REFUSE: 0.5,
    },
    alwaysAsk: ['exec', 'message', 'Write'],
  },
  standard: {
    level: 'standard',
    // Uses default thresholds
    checkpointBefore: ['exec', 'Write'],
  },
  full: {
    level: 'full',
    confidenceThreshold: {
      PROCEED_FREELY: 0.7,
      PROCEED_CAUTIOUSLY: 0.5,
      ASK_HUMAN: 0.3,
      REFUSE: 0.1,
    },
    neverAsk: ['Read', 'web_search', 'Write', 'Edit'],
  },
};
```

## OpenClaw Integration

### Config Extension

Add to agent config:

```yaml
agents:
  defaults:
    autonomy:
      level: standard
      escalationTimeout: 300000  # 5 minutes
      checkpointBefore:
        - exec
        - Write
```

### Tool Execution Hook

In `pi-embedded-subscribe.handlers.tools.ts`:

```typescript
async function executeToolWithGate(
  toolCall: ToolCall,
  context: Context,
  config: AgentConfig
): Promise<ToolResult> {
  const gateResult = await gateAction(toolCall, context, config.autonomy);
  
  if (gateResult.checkpoint) {
    await createCheckpoint(context, toolCall);
  }
  
  if (gateResult.waitForHuman) {
    const response = await requestHumanInput({
      action: toolCall,
      question: gateResult.question,
      options: gateResult.options,
    });
    
    if (response.decision === 'cancel') {
      return { skipped: true, reason: 'Cancelled by user' };
    }
    // Continue with execution
  }
  
  if (gateResult.refused) {
    return { error: true, reason: gateResult.reason };
  }
  
  return executeTool(toolCall);
}
```
