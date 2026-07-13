# Customer-specific 8D format definitions

When one supplier serves multiple customers, each customer may require a different 8D report layout (section titles, table columns, order). This folder stores **format definitions** so the skill can generate reports that match a given customer’s template.

## How it works

- **File name**: Use a short, machine-friendly name, e.g. `customer-a.md`, `automotive-oem.md`, `iso-form.md`. The user (or you) can say “use format Customer A” or “use automotive-oem”; the skill will look for `formats/customer-a.md` or `formats/automotive-oem.md` (lowercase, hyphens).
- **Content**: Each file describes the report structure: **section titles in the order they should appear**, and optionally **table column headers** for that customer. The skill still fills D1–D8 content (team, problem, containment, root cause, permanent actions, implement, prevent recurrence, close); only the headings and layout follow this file.

## File format (optional but recommended)

Use a simple list of section titles. You can add a short comment for the agent.

```markdown
# Format: [Customer or standard name]

## Section order (use these headings in the report)

1. Cover / Basic information
2. D1 – Team (or "8D Team", "Cross-functional team" — use exact customer heading)
3. D2 – Problem description (or "Problem definition", "5W2H")
4. D3 – Interim containment (or "Containment", "Short-term actions")
5. D4 – Root cause analysis
6. D5 – Permanent corrective actions
7. D6 – Implement and validate
8. D7 – Prevent recurrence
9. D8 – Close / Congratulate team

## Optional: table columns for key sections

- **Team table**: Role | Name | Department | Responsibility
- **Containment table**: Action | Owner | Due date | Status
- **Root cause**: Direct cause | Root cause | Verification method
```

If a section is missing, the skill can still map content (e.g. merge D4 and D5 into one section if the customer template does so). Extra sections (e.g. "Cost impact", "RMA number") can be listed here so the skill adds them with placeholders.

## Adding a new customer format

1. Create a new file in `formats/`, e.g. `formats/acme-corp.md`.
2. List the section titles in the order the customer expects.
3. Optionally add table column headers for team, containment, actions, etc.
4. Tell the user: "Format 'acme-corp' is available; say 'use format acme-corp' when creating an 8D for this customer."

The skill will use this file when the user says they are writing the report for that customer or selects that format by name.
