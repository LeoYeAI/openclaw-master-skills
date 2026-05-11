# 📜 Art of War Agents

> 兵者，国之大事，死生之地，存亡之道，不可不察也
>
> "War is a matter of vital importance to the State; the province of life or death; the road to survival or ruin. It is mandatory that it be thoroughly studied."

**Sun Tzu's Art of War applied to AI agent organization and task orchestration.**

This skill maps all **13 chapters** of the Art of War to practical patterns for deploying, managing, and optimizing AI agents.

---

## Install

### ClawdHub
```bash
clawdhub install art-of-war-agents
```

### Manual
Copy this repo into your ClawdHub skills directory.

---

## Quick Start

Once installed, the skill activates when you discuss:
- Agent deployment decisions
- Multi-agent orchestration
- Task assessment
- Token/cost optimization
- Agent collaboration strategies

### Example Usage

```
User: Should I use an agent for competitor research?

Agent: [Applies 始计篇 — Five Constants assessment]
- 道: Aligns with business goals ✓
- 天: Launch in 3 weeks, timing good ✓
- 地: Need market data, competitor info ✓
- 将: Research + synthesis agents available ✓
- 法: Clear workflow defined ✓

Recommendation: Deploy. Start with existing reports (因间) 
before new searches (死间). Budget: ~5k tokens.
```

---

## The Thirteen Chapters → Agent Patterns

| Chapter | Agent Application |
|---------|------------------|
| 1. 始计篇 | Task assessment (五事七计) |
| 2. 作战篇 | Cost awareness, speed |
| 3. 谋攻篇 | Planning hierarchy, avoid force |
| 4. 军形篇 | Defense first, risk management |
| 5. 兵势篇 | Momentum, 奇正 combinations |
| 6. 虚实篇 | Strategic targeting, avoid waste |
| 7. 军争篇 | Indirect approaches |
| 8. 九变篇 | Adaptability, fault detection |
| 9. 行军篇 | Signal reading, intervention timing |
| 10. 地形篇 | Task classification |
| 11. 九地篇 | Resource allocation by importance |
| 12. 火攻篇 | Tool usage (API, code, search) |
| 13. 用间篇 | Information gathering, verification |

---

## Core Principles

### 知彼知己 (Know Enemy, Know Yourself)
- Understand the task deeply
- Know your agents' capabilities and limits
- Every deployment is calculated, not hopeful

### 上兵伐谋 (Best Strategy Attacks Plans)
- Planning > Execution
- A well-planned single agent beats three confused agents
- Win before fighting

### 奇正相生 (Orthodox + Unorthodox)
- **正**: Standard workflows, reliable agents
- **奇**: Creative approaches, experiments
- Use both; never rely on 奇 alone

### 速战速决 (Speed is Essential)
- Prolonged runs waste tokens and drift
- Set clear termination conditions
- 2-3 iterations with no progress → reassess

### 先胜后战 (Victory Before Battle)
- Ensure conditions favor success before deploying
- If you can't define "winning", don't start
- Retreat > waste resources on unwinnable tasks

---

## Decision Tree

```
Task arrives
    ↓
Can I do this myself in <5 min?
    ├─ Yes → Do it (don't deploy agent)
    └─ No → Continue
    ↓
Is the task clearly defined?
    ├─ No → Plan first (始计篇)
    └─ Yes → Continue
    ↓
What's the token budget?
    ├─ Low (<10k) → Single focused agent (谋攻篇)
    └─ High → Multi-agent OK (兵势篇)
    ↓
What's the risk if wrong?
    ├─ High → Defense first (军形篇)
    └─ Low → Speed优先 (作战篇)
    ↓
Deploy with clear success criteria
    ↓
Monitor for drift (行军篇)
    ↓
Validate output (用间篇)
```

---

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Core principles, quick reference, troubleshooting, examples |
| `references/thirteen-chapters.md` | Deep dive: each chapter's full agent mapping with tables |
| `scripts/assess-task.py` | Interactive 五事七计 scoring tool |
| `scripts/quick-decision.py` | Quick decision card — yes/no deployment guidance |

---

## License

MIT

---

## Related

- [thinking-skills](https://github.com/wanikua/thinking-skills) — 20 thinking framework commands
- [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills) — Curated skill collection
