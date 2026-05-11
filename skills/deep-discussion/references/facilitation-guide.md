# Orchestrator Facilitation Guide

Best practices for orchestrating INTERACTIVE multi-agent deep discussion sessions.

## Core Mindset

You are NOT just collecting parallel reports. You are:
- **Facilitator** of a real conversation
- **Synthesizer** of diverse perspectives  
- **Consensus Builder** driving toward agreement
- **Integrator** creating unified solutions

## Session Setup

### Pre-Session Checklist

```
[ ] Output directory created: workspace/deep-discussion/
[ ] Topic clearly defined
[ ] Expert count decided (4-6 recommended)
[ ] Expert perspectives assigned (diverse!)
[ ] All subagents spawned with correct instructions
[ ] Discussion protocol shared with experts
```

### Expert Perspective Assignment

Assign SPECIFIC perspectives based on topic:

**Example - Economic System Design**:
- Expert 1: Token economics designer
- Expert 2: Game theorist
- Expert 3: Distributed systems architect
- Expert 4: Reputation system expert
- Expert 5: Market designer
- Expert 6: Security & compliance expert

**Example - Product Strategy**:
- Expert 1: UX designer
- Expert 2: Product manager
- Expert 3: Engineering lead
- Expert 4: Marketing specialist
- Expert 5: Customer success
- Expert 6: Business/finance

## Facilitation Flow

### Opening Message (to all experts)

```markdown
Welcome to the deep discussion session!

🎯 Topic: {topic}
👥 Participants: {n} experts + 1 orchestrator (me)
📁 Output: workspace/deep-discussion/{topic}.md

Your Fellow Experts:
- Expert 1: {perspective}
- Expert 2: {perspective}
- Expert 3: {perspective}
- Expert 4: {perspective}
- Expert 5: {perspective}
- Expert 6: {perspective}

📋 Discussion Rules:
1. You will see ALL other experts' responses
2. Respond to SPECIFIC experts by name
3. Build on good ideas, challenge weak ones
4. Acknowledge when you change your mind
5. Goal: unified solution, not 6 separate reports

Let's begin Round 1!
```

### Round Management

#### After Collecting All Responses

1. **Read ALL responses carefully**
2. **Identify**:
   - Points of agreement (explicit and implicit)
   - Points of disagreement (label the specific issue)
   - Emerging themes
   - Questions raised but not answered
   - Ideas that multiple experts built on

3. **Write Summary** using template below
4. **Send** summary + next round to ALL experts

#### Summary Template

```markdown
## Round {N} Summary

### 🟢 Consensus Areas
- **Point 1**: All experts agree on X
- **Point 2**: Experts 1,2,4,5 agree on Y (Experts 3,6 have concerns)

### 🔴 Key Disagreements
- **Issue X**:
  - Position A (Experts 1,3): [viewpoint]
  - Position B (Experts 2,4,5,6): [viewpoint]
  - This needs resolution in Round {N+1}

### 💡 Emerging Themes
- Theme 1: [description] - mentioned by Experts 1,2,4
- Theme 2: [description] - built upon by Experts 3,5,6

### ❓ Open Questions
- Question from Expert 2 to Expert 5: [question] - awaiting response
- Unresolved: [issue]

---

## Round {N+1}: {title}

{specific prompt for next round}

Please respond to the open questions and disagreements above.
```

### Handling Difficult Situations

#### Situation 1: Expert Dominating Discussion

**Signs**: One expert writes 50%+ of content, others respond mainly to them

**Response**:
> "Thanks Expert 1 for the detailed analysis. I'd love to hear from Experts 3,4,5 who haven't shared their perspectives on this yet. What are your thoughts?"

#### Situation 2: Experts Talking Past Each Other

**Signs**: No one responding to specific points, parallel monologues

**Response**:
> "Let me pause the discussion. Experts, please re-read the summary. In Round 3, I want each of you to:
> 1. Name ONE expert you agree with and why
> 2. Name ONE point you disagree with and propose alternative
> 3. Build on ONE idea from another expert"

#### Situation 3: Stuck on Disagreement

**Signs**: Same disagreement for 2+ rounds, no progress

**Response**:
> "We seem stuck on [issue]. Let me propose a path forward:
> - Position A has merit because: [synthesize]
> - Position B has merit because: [synthesize]
> - Compromise: [propose middle ground]
> 
> Can everyone live with this compromise? If not, what specific concern remains?"

#### Situation 4: Expert Not Engaging with Others

**Signs**: Expert writes long responses but never mentions other experts

**Response** (private message if possible):
> "Expert 3, your insights are valuable. In Round 4, please specifically respond to:
> - Expert 1's concern about X
> - Expert 5's proposal for Y
> Name them and explain your position."

## Synthesis Techniques

### For Final Report

**DO**:
- Integrate ideas into coherent narrative
- Label consensus vs disagreement clearly
- Attribute specific ideas to specific experts
- Show evolution of thinking ("Initially X, but after discussion, converged on Y")

**DON'T**:
- Just拼接 6 expert reports
- Hide disagreements
- Attribute everything to "the group"

### Integration Pattern

```markdown
## Proposed Solution

### Design Principles (Consensus)
All experts agreed on these core principles:
1. Principle 1 (mentioned by Experts 1,2,4,6)
2. Principle 2 (mentioned by Experts 2,3,5)

### Architecture (Synthesized from Multiple Proposals)

The final architecture combines:
- Token layer from Expert 1's proposal (modified per Expert 2's game theory concerns)
- Governance structure from Expert 3's framework
- Market mechanisms from Expert 5's design
- Security safeguards from Expert 6's requirements

### Areas of Remaining Disagreement

**Issue**: [specific issue]
- Position A (Experts 1,3): [viewpoint]
- Position B (Experts 2,4,5,6): [viewpoint]
- Recommendation: [orchestrator recommendation based on discussion]
```

## Time Management

| Phase | Duration | Buffer |
|-------|----------|--------|
| Setup & Spawn | 2 min | 1 min |
| Round 1 | 10 min | 3 min |
| Round 2 | 15 min | 5 min |
| Round 3 | 15 min | 5 min |
| Round 4 | 15 min | 5 min |
| Round 5 | 10 min | 3 min |
| Final Synthesis | 10 min | 5 min |
| **Total** | **77 min** | **27 min** |

**Recommendation**: Schedule 90-120 min sessions

## Quality Checklist

Before marking session complete:

```
[ ] Every expert responded in every round
[ ] Experts referenced each other by name (≥3 times each)
[ ] At least 2 instances of experts changing minds
[ ] Summary after each round captured agreements/disagreements
[ ] Final report is integrated (not 6 sections)
[ ] Action plan has specific owners and timelines
[ ] Remaining disagreements are explicitly labeled
[ ] Output saved to workspace/deep-discussion/{topic}.md
```

## Example Session Log

```
[14:00] Session started, 6 experts spawned
[14:02] Round 1 prompt sent to all
[14:12] All 6 responses collected
[14:15] Round 1 summary sent + Round 2 prompt
[14:30] All 6 responses collected (Expert 2 responded to Expert 1,4,5)
[14:33] Round 2 summary sent + Round 3 prompt
[14:48] All 6 responses collected (Expert 3 changed mind based on Expert 6)
[14:50] Round 3 summary sent + Round 4 prompt
[15:05] All 6 responses collected (consensus emerging on token design)
[15:07] Round 4 summary sent + Round 5 prompt
[15:17] All 6 responses collected (action plan drafted)
[15:25] Final synthesis complete
[15:27] Report saved to workspace/deep-discussion/f2a-economic-system.md
```

This is the level of facilitation we want!

---

## Session Statistics

After session complete, Orchestrator should generate statistics.

### Statistics to Collect

```python
def collect_session_statistics(discussion_file, session_start_time, session_end_time):
    """
    Collect comprehensive statistics about the deep discussion session.
    
    Returns: dict with time breakdown, expert participation, discussion metrics
    """
    
    # 1. Time Breakdown
    total_duration = session_end_time - session_start_time
    
    phase_times = {
        'setup': calculate_phase_duration('Phase 1'),
        'agenda': calculate_phase_duration('Phase 2'),
        'rounds': calculate_phase_duration('Phase 3'),
        'wrapup': calculate_phase_duration('Phase 4'),
        'synthesis': calculate_phase_duration('Phase 5')
    }
    
    # 2. Expert Participation
    expert_stats = {}
    for expert in all_experts:
        speeches = count_speeches_by_expert(discussion_file, expert)
        total_words = count_words_by_expert(discussion_file, expert)
        avg_response_time = calculate_avg_response_time(expert)
        
        expert_stats[expert] = {
            'speeches': speeches,
            'total_words': total_words,
            'avg_response_time': avg_response_time
        }
    
    # 3. Discussion Metrics
    total_rounds = count_total_rounds(discussion_file)
    total_subrounds = count_total_subrounds(discussion_file)
    convergence_round = find_convergence_round(discussion_file)
    consensus_score = calculate_final_consensus_score()
    key_decisions = count_key_decisions()
    unresolved_disagreements = count_unresolved_disagreements()
    
    return {
        'time_breakdown': phase_times,
        'total_duration': total_duration,
        'expert_stats': expert_stats,
        'discussion_metrics': {
            'total_rounds': total_rounds,
            'total_subrounds': total_subrounds,
            'convergence_round': convergence_round,
            'consensus_score': consensus_score,
            'key_decisions': key_decisions,
            'unresolved_disagreements': unresolved_disagreements
        }
    }
```

### Statistics Template for Report

```markdown
## Session Statistics

### Time Breakdown
| Phase | Duration | Percentage |
|-------|----------|------------|
| Phase 1: Setup | 2 min | 3% |
| Phase 2: Agenda Setting | 8 min | 11% |
| Phase 3: Dynamic Rounds | 52 min | 72% |
| Phase 4: Topic Wrap-up | 5 min | 7% |
| Phase 5: Final Synthesis | 5 min | 7% |
| **Total** | **72 min** | **100%** |

### Expert Participation
| Expert | Role | 发言次数 | 总字数 | 平均响应时间 |
|--------|------|---------|--------|-------------|
| Expert 1 | AI/ML 专家 | 8 | 2,400 | 3.2 min |
| Expert 2 | 产品经理 | 7 | 2,100 | 2.8 min |
| Expert 3 | 数据科学家 | 6 | 1,800 | 3.5 min |
| Expert 4 | UX 设计师 | 5 | 1,500 | 4.1 min |
| Expert 5 | 教育产品专家 | 6 | 1,900 | 3.0 min |

### Discussion Metrics
- **Total Rounds**: 4
- **Total Sub-rounds**: 12
- **Convergence Achieved**: Round 4
- **Consensus Score**: 87%
- **Key Decisions**: 9
- **Unresolved Disagreements**: 1
```

### Implementation Notes

1. **Track timestamps** - Record start/end time for each phase
2. **Count speeches** - Parse discussion-log.md for expert speech markers
3. **Count words** - Simple word count per expert's contributions
4. **Response time** - Time between prompt sent and response received
5. **Consensus score** - Use convergence criteria calculation
6. **Auto-generate** - Include statistics in final report automatically