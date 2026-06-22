# plume-infographic Skill Intent Classification Adjustment Plan

## 1. Background

The current `plume-infographic` skill uses two approaches for text-based infographic requests:

- **Single image** requests like "make an infographic about XX" are typically mapped directly to `topic`
- **Batch** requests like "make 5 infographics about XX series" require content planning first, then passing the organized complete content via `article` mode

This creates two problems:

1. **Inconsistent mental model between single and batch**: For the same information-incomplete topic requests, single image tends to create directly, while batch plans first
2. **Topic input is too sparse**: Users often give only a one-line topic, creating directly leads to insufficient content density and unclear information structure, resulting in unstable output

Therefore, this adjustment aims to unify the skill's text-based infographic processing path.

---

## 2. Adjustment Goals

### 2.1 Core Goals

1. **Stop using `topic` as the primary path in the skill**
2. **Unify on `article` for carrying text infographic content**
3. **When user has only a one-line infographic request, also adopt the same "proactive content suggestion" flow as batch infographics**
4. **Emphasize suggestive guidance, not passively waiting for user to supplement**

### 2.2 Non-Goals

This adjustment does not change:

- `reference` mode parameter structure
- `retry` mode parameter structure
- Backend executor's compatibility with `topic`
- `poll_cron.py` / `plume_api.py` workflow

---

## 3. New Unified Strategy

## 3.1 All Text Requests Go Through Article

For all **non-reference, non-retry** text infographic requests, handle uniformly as follows:

- Skill layer no longer recommends using `topic`
- Unified usage:

```bash
--mode article --article "...complete content..."
```

Here `article` no longer means only "long text pasted by user", but extends to:

- Long-form text directly provided by user
- Complete content proactively supplemented by Agent based on user's one-line topic
- Planned paginated content for batch scenarios

In other words, `article` becomes the skill layer's unified **text carrier structure**.

---

## 3.2 Single and Batch Share the Same Decision Principles

### Cases Where Direct Creation Is Allowed

Tasks can be created directly when:

1. User has provided sufficiently detailed text content
2. User has given structured content or clear paragraph information
3. User is retrying or doing reference image rewrite based on existing results

### Cases Requiring Guided Supplementation First

Do not create tasks directly in these cases; guide content first:

1. User gave only a topic word
2. User gave only a one-line description
3. User expressed wanting an infographic but didn't specify core content layers
4. User made a batch request but didn't specify quantity, split method, or direction for each page

---

## 4. New Handling for Single-Sentence Single-Image Requests

## 4.1 Applicable Scenarios

For example:

- "Make an infographic about the history of gold"
- "Create an infographic about AI in healthcare"
- "Help me make a quantum computing diagram"

These requests are **single image**, but essentially share the same problem as "batch infographics lacking planning": **incomplete input information**.

Therefore, these should no longer be treated as `topic` and created immediately, but should go through lightweight planning first.

## 4.2 Guidance Principles

### Principle 1: Proactively Suggest, Don't Passively Wait

Don't just reply with:

- "Please provide more content"
- "What style do you want?"
- "Please provide more detailed information"

Instead, proactively propose an initial content plan, letting the user just confirm or fine-tune.

### Principle 2: Consolidate Questions, Complete in One Turn

Try to accomplish in a single message:

- Content direction suggestions
- Key missing information confirmation
- Optional style preference confirmation

Avoid splitting into multiple turns of mechanical follow-up questions.

### Principle 3: Only Supplement What's Necessary

Single image requests usually don't need planning to "each page" level like batch, but still need to expand the topic into an actionable information structure.

Suggest at minimum:

- Topic background / origins
- Core stages / key points
- Modern significance / applications / conclusions

## 4.3 Recommended Phrasing

### Example 1: Historical Topic

User:

> Make an infographic about the history of gold

Recommended guidance:

> Let me plan this into a more complete infographic. I suggest at least 3 sections: the origin and discovery of gold, ancient currency and civilization applications, and modern financial and industrial value. If you don't have a particular preference, I can generate based on this structure; also let me know if you prefer minimalist, classical, or tech-style design.

### Example 2: Knowledge/Science Topic

User:

> Help me make a quantum computing diagram

Recommended guidance:

> Sure, I suggest this infographic covers 3 layers: what quantum computing is, how it differs from traditional computing, and current typical applications and challenges. If you agree, I'll organize this into complete content for generation; style-wise, do you prefer minimalist educational or more tech-oriented?

## 4.4 Creation Principles

After user confirms, Agent should organize the complete content into `article` for submission, not continue passing just a topic word.

For example:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --mode article \
  --article "Gold History Infographic. Part 1: The cosmic origins and natural formation of gold. Part 2: Gold currency and power symbolism in ancient civilizations. Part 3: The role of modern gold in financial reserves, jewelry industry, and electronics manufacturing." \
  --style-hint "classical hand-drawn"
```

---

## 5. Batch Requests Continue Proactive Planning, Unified as Article Delivery

Batch infographics originally required content planning first; this adjustment doesn't change that principle, only unifies two points:

1. Messaging clarifies: batch and single image are the same type of "plan first when information is incomplete" problem
2. After planning, unified submission via `--mode article --article`

### Core Items Still Requiring Confirmation for Batch Planning

- Quantity (suggest 3-5)
- Content relationship (independent topics or coherent pages)
- Style consistency (`style_transfer` vs `content_rewrite`)
- Outline content for each page

### Batch Creation Format Remains

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/create_infographic.py create \
  --mode article \
  --article "...planned complete paginated content..." \
  --count 5 \
  --child-reference-type content_rewrite
```

---

## 6. Relationship with Script Layer

## 6.1 Skill Layer Strategy Adjustment

This adjustment first occurs at the **skill routing and documentation layer**:

- No longer directing Agent to use `topic`
- All text requests unified through `article`
- Single image one-line requests also adopt proactive content planning

## 6.2 Script Layer Compatibility Strategy

`scripts/create_infographic.py` does not remove `topic` support yet, instead:

- **Retain compatibility**: Old calls passing `--mode topic --topic ...` still work
- **No longer recommended**: New `SKILL.md`, examples, and flows no longer use `topic`

This reduces change risk while completing upper-layer strategy convergence.

---

## 7. Files Requiring Synchronized Updates

After this plan is confirmed, the following files should be updated:

### 7.1 Skill Main Document

- `plume-infographic/SKILL.md`

Changes:

- Remove `topic` as primary path in user intent mapping
- Add rule for "proactive guidance for single image when information is incomplete"
- Expand content planning section to cover both single and batch

### 7.2 Parameter Documentation

- `plume-infographic/references/modes.md`

Changes:

- No longer recommend `topic` as a mode
- Clarify that `article` can carry "complete content after topic expansion"

### 7.3 Workflow Documentation

- `plume-infographic/references/workflows.md`

Changes:

- Topic infographic examples changed to `article`
- Simple batch examples also changed to `article`
- Add proactive guidance notes for single-sentence requests

### 7.4 Script Files

- `plume-infographic/scripts/create_infographic.py`

Changes:

- Retain `topic` compatibility
- Optimize title generation logic for `article` path, avoid batch titles degrading to "conversion-Npcs"

### 7.5 Repository-Level Design Document

- `docs/plume-infographic-skill-design-plan.md`

Changes:

- Update design notes related to `topic/article` to keep repository-level docs consistent with skill-internal docs

---

## 8. Validation Criteria

After implementation, the following criteria should be met:

1. **Skill documentation no longer uses `topic` as the primary text path**
2. **Single image one-line requests trigger suggestive supplementation first, not direct creation**
3. **Batch requests maintain proactive planning, described with the same approach as single image**
4. **All text-based creation unified using `--mode article --article`**
5. **Script layer still supports old `topic` calls, not affecting existing potential callers**

---

## 9. Suggested Implementation Order

1. Update project-internal design documents first
2. Then update `SKILL.md`
3. Then update `references/modes.md` and `references/workflows.md`
4. Finally fine-tune `create_infographic.py` compatibility and title logic
5. Verify compatibility through script commands

---

## 10. Conclusion

The essence of this adjustment is not simply renaming `topic` to `article`, but unifying `plume-infographic`'s decision model for text-based infographics:

- **When input is incomplete, plan proactively first**
- **After planning, unified delivery via article with complete content**
- **Single and batch follow the same principles, only differing in planning granularity**

This significantly reduces the "topic too short leading to sparse information" problem and makes the skill's interaction experience more stable and consistent.
