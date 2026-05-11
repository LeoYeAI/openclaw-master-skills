# SKILL.md template

Copy this template when creating a new skill. Fill in the placeholders, delete sections you don't need.

```markdown
---
name: {skill-name}
description: |
  {Product/tool name} guide for {primary use case}. Covers {feature-1},
  {feature-2}, {feature-3}. Use this skill for any {trigger-1}, {trigger-2},
  or {trigger-3} question.
---

# {Skill Title}

This skill provides instructions for {what it does}. Follow these patterns exactly when generating code.

## Core rules

1. {Most important rule — the one that prevents the worst mistakes}
2. {Second most important rule}
3. {Third rule}
4. {Fourth rule — keep to 3-5 max}

When unsure about a pattern, reference the detailed guides:
- {Topic 1}: [references/{topic-1}.md](references/{topic-1}.md)
- {Topic 2}: [references/{topic-2}.md](references/{topic-2}.md)

## Quick setup

```bash
{minimal setup commands — 3-5 lines max}
```

## {Primary feature}

```{language}
{canonical code example — the pattern users need most often}
```

For {variations/advanced usage}, see [references/{detail}.md](references/{detail}.md).

## {Secondary feature}

{Brief description}. For the complete workflow, see [references/{detail}.md](references/{detail}.md).

## {Quick reference}

| Command/Method | Description |
|----------------|-------------|
| `{cmd-1}` | {what it does} |
| `{cmd-2}` | {what it does} |
| `{cmd-3}` | {what it does} |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| {common problem 1} | {fix} |
| {common problem 2} | {fix} |
| {common problem 3} | {fix} |

## Resources

- [{Resource 1}]({url})
- [{Resource 2}]({url})
```

## Template checklist

After filling in the template, verify:

- [ ] Name is lowercase with hyphens, 1-64 chars, no leading/trailing/consecutive hyphens
- [ ] Name matches parent directory name
- [ ] Description under 1024 chars (spec limit); ideally under 300 for best matching
- [ ] Description includes trigger phrases
- [ ] Body is under 500 lines
- [ ] Core rules section has 3-5 items max
- [ ] One canonical code example in SKILL.md (detailed examples in references/)
- [ ] Routing table points to reference files
- [ ] Tables used for structured data (not bullet lists)
- [ ] No emoji in headings
- [ ] All code blocks have language tags
- [ ] No persona-based framing
- [ ] Troubleshooting section present
