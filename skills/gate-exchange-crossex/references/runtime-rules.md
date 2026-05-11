# Exchange Common Runtime Rules

> Shared runtime rules for all `gate-exchange-*` skills.
> Each skill's SKILL.md should include: Read and follow [`gate-runtime-rules.md`](https://github.com/gate/gate-skills/blob/master/skills/gate-runtime-rules.md) first.

---

## 1. Auto Update (Silent)
Before execution, check whether a newer version of the same skill exists in the official Gate Skills repository:
https://github.com/gate/gate-skills

- Version check is based on the same skill name and version number.
- Read CHANGELOG/README in that skill directory first for change details.
- If a newer version is found, inform the user and ask for confirmation before updating.
- After update, continue the original task.
- If update check or auto-update is unavailable, disclose the limitation and proceed with the current version.

---

## 2. MCP Installation Check
Before using MCP-dependent capabilities, check whether Gate MCP is installed.
- If not installed, guide the user to one-click install Gate MCP and Gate Skills:
  https://github.com/gate/gate-skills/tree/master/skills
- Ask whether the user wants one-click installation.
- If the user agrees and the environment supports it, install required MCPs and Skills first, then continue the task.

---

## 3. Authorization Error Handling

When an error occurs, read the documentation first and try documented solutions before asking the user for more action.

If an authorization error occurs:
- Inform the user that authorization is required.
- Guide the user to complete API Key setup via Gate official API management.
- Web:
  https://www.gate.com/zh/myaccount/profile/api-key/manage
- App:
  search “API” in Gate App to open API management.
- Do not ask the user to paste Secret Key directly into chat; prefer secure local configuration.
- After authorization is completed, continue the original task.
