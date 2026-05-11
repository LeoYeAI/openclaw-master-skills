# Meeting Notes Preferences

Optional customization file. If this exists in your workspace, the AI will follow these preferences.

---

## Output Format

Choose your default output format:

```
default: plain
```

Options: `plain`, `markdown`, `json`, `slack`, `email`

---

## Sections to Include

Check the sections you want in every extraction:

- [x] Summary
- [x] Action Items
- [x] Decisions
- [ ] Open Questions
- [ ] Attendees
- [ ] Next Steps

---

## Action Item Format

How should action items be formatted?

```
style: "[ ] @{owner}: {task} — {deadline}"
```

Alternative styles:
- `"- {task} ({owner}, due {deadline})"`
- `"• {owner} → {task} [{deadline}]"`
- `"TODO: {task} // @{owner} // {deadline}"`

---

## Owner Defaults

When no owner is specified:

```
default_owner: Team
```

Options: `Team`, `TBD`, `Unassigned`, or a specific name

---

## Deadline Handling

When no deadline is mentioned:

```
no_deadline_text: TBD
```

Options: `TBD`, `No deadline`, `ASAP`, `Unscheduled`

---

## Grouping

For meetings with many action items:

```
group_by: none
```

Options: `none`, `owner`, `deadline`, `priority`

---

## Additional Instructions

Add any specific instructions for your workflow:

```
- Bold owner names in markdown output
- Always include meeting date if mentioned
- Flag any items marked "urgent" or "ASAP"
- Use emoji indicators for Slack output
```

---

## Project-Specific Tags

If you want action items tagged for specific projects:

```
auto_tag: false
tag_format: "[{project}]"
```

---

*Delete any sections you don't need. The AI uses smart defaults for anything not specified.*
