# Knowledge Acquisition Guide

> Replaces the tool-specific `mcp-tools-guide.md`, `tool-scenario-mapping.md`,
> and `latest-knowledge-acquisition.md` with a **platform-agnostic** version.

---

## Core Principle

**LLM training data is the baseline. Fresh research is the supplement and override.**

| Situation | Action |
|-----------|--------|
| Own knowledge + fresh research agree | Use with high confidence |
| Own knowledge + fresh research conflict | **Fresh research wins** |
| Own knowledge exists, no fresh research available | Use own knowledge, mark "unverified" |
| No own knowledge, fresh research found | Use fresh research |

---

## Mandatory Research Flow

```
Step 0: Form baseline from own knowledge
    ↓
Step 1: Research using available tools
    ↓
Step 2: Validate via 4-Layer Gate
    ↓
Step 3: Fuse old + new knowledge (conflicts → new wins)
    ↓
Step 4: Expert self-check
    ↓
Begin writing SKILL.md
```

**Skipping research → Skill is invalid and must be redone.**

---

## Tool Selection (Use What's Available)

### By Research Goal

| Goal | Tool Category | Examples |
|------|--------------|---------|
| **Official library/framework docs** | Documentation lookup | Any docs search tool, official website |
| **Latest best practices** | Web search | Any web search tool, tech blog aggregators |
| **Real code examples** | Code search | Any code search tool, GitHub search |
| **Open source project docs** | Repository docs | GitHub README, wiki pages |
| **Specific page content** | URL fetcher | Any URL/page fetch tool |
| **Latest news/trends** | General search | Any web search tool |

### Decision Flow

```
Need information about...
    │
    ├─ A specific library/framework API?
    │   → Documentation lookup tool (priority 1)
    │
    ├─ Best practices or patterns?
    │   → Web search (priority 1), get 3+ sources
    │
    ├─ Real-world code examples?
    │   → Code search tool or GitHub search (priority 2)
    │
    ├─ Latest version/breaking changes?
    │   → Official docs + web search (priority 1)
    │
    └─ No tools available?
        → Use own knowledge, mark ALL claims as "unverified"
```

### Combination Strategy

| Scenario | Primary | Verification |
|----------|---------|-------------|
| Library API usage | Docs lookup | Web search to confirm |
| Architecture pattern | Web search (3+ sources) | Code examples |
| Open source project | Repository docs | Fetch specific pages |
| Technology trend | Web search | Fetch authoritative articles |

---

## Minimum Research Requirements

| Item | Minimum | How to Verify |
|------|---------|---------------|
| Official source | At least 1 | Record URL + date |
| Current version | Confirmed | Record version number |
| Best practices | At least 3 from credible sources | Record sources |
| Common pitfalls | At least 3 real cases | Record sources |
| Source freshness | All sources < 1 year old | Check dates |

---

## 4-Layer Knowledge Validation Gate

### Layer 1: Freshness Gate

| Check | Pass | Fail Action |
|-------|------|-------------|
| Source date | < 1 year | Re-acquire |
| Version | Current latest | Check breaking changes |
| Freshness tier | A or B | C/D must be re-validated |

**Freshness Tiers:**

| Tier | Age | Status | Action |
|------|-----|--------|--------|
| A | < 3 months | Fresh | Use directly |
| B | 3-6 months | Recent | Check for updates |
| C | 6-12 months | Aging | Must validate before use |
| D | > 12 months | Expired | Must re-acquire |

### Layer 2: Accuracy Gate

| Check | Pass | Fail Action |
|-------|------|-------------|
| Source credibility | S/A/B tier | C/D need cross-validation |
| Multi-source | Official + 2 independent | Add more sources |
| Consistency | > 80% agreement | Flag conflicts, analyze |

**Source Credibility Tiers:**

| Tier | Source Type | Trust |
|------|-----------|-------|
| S | Official docs, official blog | Highest — use directly |
| A | Official GitHub, official examples | High — use directly |
| B | Known tech blogs, high-vote SO answers | Medium — cross-validate |
| C | Personal blogs, forum posts | Low — must multi-source verify |
| D | Unknown origin, AI-generated | Lowest — must verify against official |

### Layer 3: Completeness Gate

| Check | Pass | Fail Action |
|-------|------|-------------|
| Core features | 100% covered | Supplement missing features |
| Usage scenarios | ≥ 80% covered | Supplement scenarios |
| Target version | 100% covered | Supplement version info |
| Target platform | 100% covered | Supplement platform info |

### Layer 4: Fusion Gate

| Check | Pass | Fail Action |
|-------|------|-------------|
| Comparison done | Own vs new knowledge compared | Must compare |
| Conflicts resolved | All conflicts noted and resolved | Resolve before continuing |
| Fusion recorded | Decision rationale documented | Document it |

---

## Research Output Template

```markdown
## Knowledge Acquisition Report

### Date: YYYY-MM-DD
### Domain: [domain name]

### Tools Used
| Tool | Query | Result Summary |
|------|-------|----------------|
| [tool] | [query] | [summary] |

### Key Findings
1. **Latest Version**: [version] (released: YYYY-MM-DD)
2. **Important Changes**: [list]
3. **Best Practices**: [list]
4. **Deprecated Items**: [list]

### Source Verification
| Source | URL | Date | Credibility |
|--------|-----|------|-------------|
| Official docs | [URL] | YYYY-MM-DD | S |
| Tech blog | [URL] | YYYY-MM-DD | B |

### 4-Layer Gate Results
- [ ] Freshness: All sources < 1 year
- [ ] Accuracy: Official + 2 independent sources
- [ ] Completeness: Core 100%, scenarios 80%+
- [ ] Fusion: Own vs new compared, conflicts resolved
```

---

## Fallback Strategy (No Tools Available)

```
Priority 1: Use available search/docs tools
    ↓ (unavailable)
Priority 2: Use own LLM knowledge
    ↓
Priority 3: Mark ALL knowledge as "unverified"
    ↓
Add metadata note: "Knowledge source: LLM baseline, not externally verified"
```

**Never skip the research step entirely.** Even without tools, document what
you know and what you're uncertain about.

---

## Self-Check

```markdown
- [ ] Formed baseline from own knowledge
- [ ] Used available tools for fresh research (or marked as unverified)
- [ ] Compared old vs new knowledge
- [ ] Conflicts resolved (new knowledge wins)
- [ ] Confirmed current latest version
- [ ] Checked for breaking changes
- [ ] All sources < 1 year old (or marked)
- [ ] Key conclusions cross-validated
```
