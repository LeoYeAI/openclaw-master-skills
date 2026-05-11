# Convergence Criteria

How Orchestrator assesses when deep discussion has reached natural conclusion.

## Convergence Assessment

Orchestrator evaluates convergence after each round (starting from round 3).

### Criteria (Weighted)

| Criterion | Weight | How to Assess |
|-----------|--------|---------------|
| **Consensus** | 30% | 80%+ key decisions have agreement |
| **Novelty** | 20% | No new major ideas in last 2 rounds |
| **Actionability** | 20% | Action plan has owners + timelines |
| **Dissent** | 30% | All experts agree or minor reservations only |

### Scoring

```python
def assess_convergence(history, responses, round_num):
    # 1. Consensus Score (0-1)
    # Count key decisions with explicit agreement
    consensus_score = count_agreements() / total_decisions()
    
    # 2. Novelty Score (0-1)
    # Compare last 2 rounds for new ideas
    novelty_score = count_new_ideas(last_2_rounds) / threshold
    novelty_score = min(novelty_score, 1.0)  # Cap at 1.0
    
    # 3. Actionability Score (0-1)
    # Check if action plan has: owners, timelines, deliverables
    actionability_score = (
        has_owners() * 0.4 +
        has_timelines() * 0.4 +
        has_deliverables() * 0.2
    )
    
    # 4. Dissent Score (0-1, lower is better)
    # Count unresolved strong objections
    dissent_score = count_strobjections() / max(1, total_experts())
    
    # Weighted total
    total_score = (
        0.3 * consensus_score +
        0.2 * (1 - novelty_score) +  # Lower novelty = more converged
        0.2 * actionability_score +
        0.3 * (1 - dissent_score)    # Lower dissent = more converged
    )
    
    # Require minimum 3 rounds
    if round_num >= 3 and total_score >= 0.75:
        return True  # Converged
    
    return False  # Continue discussion
```

## Convergence Signals

### ✅ Strong Signals (Ready to Conclude)

- "I think we've covered the main points"
- "I agree with the proposed direction"
- "My concerns have been addressed"
- "This action plan looks solid"
- Experts start summarizing each other's points
- Discussion shifts from "what" to "how"
- Last 2 rounds have <3 new major ideas

### ⚠️ Weak Signals (Maybe Continue)

- "I still have some concerns about X"
- "We haven't discussed Y yet"
- "Can we clarify Z?"
- Experts repeating earlier points
- Discussion still in "what" phase
- Last 2 rounds have 5+ new major ideas

### ❌ Stop Signals (Definitely Continue)

- "I strongly disagree with..."
- "This approach won't work because..."
- "We're missing a critical perspective"
- Active conflict between experts
- Key decisions still unresolved
- No action plan yet

## Round Types (Dynamic)

Orchestrator selects round type based on discussion state:

| Round | Typical Focus | Prompt |
|-------|---------------|--------|
| 1 | 问题定义 | "请从各自专业角度分析核心挑战" |
| 2 | 创意生成 | "基于挑战，请提出具体方案" |
| 3 | 批判分析 | "请批判性分析方案，识别风险" |
| 4+ | 动态 | Based on what's needed: |
| | - 分歧解决 | "针对以下分歧，请继续讨论..." |
| | - 方案综合 | "请综合讨论，形成最终方案..." |
| | - 行动计划 | "请制定具体实施计划..." |

## Orchestrator Decision Tree

```
After each round (starting round 3):
│
├─ Has 80%+ consensus on key decisions?
│  ├─ No → Continue (focus:分歧解决)
│  └─ Yes ↓
│
├─ Any strong unresolved objections?
│  ├─ Yes → Continue (focus:分歧解决)
│  └─ No ↓
│
├─ Action plan specific (owners + timelines)?
│  ├─ No → Continue (focus:行动计划)
│  └─ Yes ↓
│
├─ New major ideas in last 2 rounds < 3?
│  ├─ No → Continue (focus:方案综合)
│  └─ Yes ↓
│
└─ CONVERGED → Synthesize final report
```

## Examples

### Example 1: Converged (Round 4)

```
Round 4 Summary:
- Consensus: 90% (8/9 key decisions agreed)
- Novelty: Low (2 new ideas in rounds 3-4)
- Actionability: High (all actions have owners + dates)
- Dissent: None (all experts expressed support)

Decision: CONVERGED → Synthesize final report
```

### Example 2: Not Converged (Round 4)

```
Round 4 Summary:
- Consensus: 60% (5/8 key decisions agreed)
- Novelty: Medium (5 new ideas in rounds 3-4)
- Actionability: Low (no owners or dates yet)
- Dissent: Expert 2 strongly objects to approach

Decision: CONTINUE → Round 5 (focus:分歧解决 + 行动计划)
```

### Example 3: Forced Conclusion (Round 10)

```
Round 10 Summary:
- Still significant disagreement
- But reached max_rounds (10)

Decision: FORCED CONCLUSION
- Synthesize best available consensus
- Document unresolved disagreements
- Note: "Discussion reached maximum rounds without full convergence"
```

## Best Practices

### For Orchestrator

1. **Don't rush convergence** - Let discussion flow naturally
2. **Track disagreements explicitly** - Note who disagrees and why
3. **Summarize frequently** - Help experts see progress
4. **Prompt for specifics** - "Who will do what by when?"
5. **Know when to conclude** - Don't drag out unnecessarily

### For Experts

1. **Be specific about agreement/disagreement** - "I agree with X because..."
2. **Acknowledge when concerns addressed** - "My concern about Y has been resolved"
3. **Help move toward action** - "To make this actionable, we need..."
4. **Distinguish major vs minor issues** - "This is a minor concern, not a blocker"

## Troubleshooting

### Issue: Discussion Stuck in Loop

**Symptom**: Experts repeating same points for 2+ rounds

**Solution**:
- Orchestrator intervenes: "We seem to be cycling on X. Let me summarize the options..."
- Propose specific decision: "Can we agree on Option A with modification B?"
- Move to next topic: "Let's park X for now and discuss Y"

### Issue: One Expert Dominating

**Symptom**: One expert writes 50%+ of content

**Solution**:
- Orchestrator prompts others: "Experts 2,3,4,5 - what are your thoughts?"
- Set turn-taking: "Let's go around and hear from each expert"
- Private message (if possible): "Please ensure balanced participation"

### Issue: No Convergence After 8 Rounds

**Symptom**: Still significant disagreement at round 8

**Solution**:
- Orchestrator assesses: Is this fundamental incompatibility?
- Consider: Should we split into separate recommendations?
- Document: "Experts could not reach consensus on X. Here are the competing views..."
