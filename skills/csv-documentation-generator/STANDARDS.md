# Code Annotation Standards

This document describes the code annotation standards used by the csv-documentation-generator skill for GxP compliance traceability.

## Overview

The annotation standards provide a unified way for AI agents to add traceability markers to code. These markers allow the csv-documentation-generator skill to:
- Parse requirements from source code
- Link code to test cases
- Assess risk levels
- Generate compliance documentation

## Standards File Location

The central standards file is located at:
```
{skill_root}/standards/code-annotations.json
```

This file is **skill-agnostic** - any AI agent or skill can read it to understand the annotation conventions.

## Quick Start for AI Agents

When generating code, AI agents SHOULD use these annotation markers:

### Requirement Markers

```python
# @REQ URS-001 - System shall support role-based access control (RBAC)
# @REQ URS-002 - User passwords must meet complexity requirements (min 8 chars)
```

### Test Case Markers

```python
# @TEST[OQ-UM-001] - Verify user role assignment
# @TEST[IQ-AT-001] - Verify audit trail recording
```

### Risk Markers

```python
# @RISK H  # High risk - security/compliance related
# @RISK M  # Medium risk - standard requirements
# @RISK L  # Low risk - simple features/reports
```

### Design Specification Markers

```python
# @FS FS-001  # References Functional Specification
# @TS TS-001  # References Technical Specification
```

## System Prompt Integration (Manual Configuration Required)

> ⛔ This step is **NOT automatic**. You must manually add these rules to your agent's system prompt (AGENTS.md) if you want @REQ/@TEST annotations to apply across ALL skills.

To enable cross-skill annotation enforcement, add the following to your AGENTS.md or agent system prompt:

```
Code Annotation Rules (for GxP traceability):
- When writing code that implements requirements, add @REQ markers: # @REQ URS-xxx - description
- When writing test cases, add @TEST markers: # @TEST[OQ-UM-xxx] - description
- Mark high-risk code sections with @RISK H (security, compliance, audit trail related)
- Mark medium-risk code with @RISK M
- Mark low-risk code with @RISK L
```

### How to Add to Your System Prompt

1. Find your AI agent's system prompt configuration (e.g., AGENTS.md)
2. Append the rules above to the existing system prompt
3. The rules will apply to ALL code generation, not just this skill

### Why This Is Needed

**OpenClaw skills only execute when active.** There is no mechanism to make instructions persist across skill switches except via the system prompt.

| Without System Prompt | With System Prompt |
|---------------------|-------------------|
| Only applies when csv-documentation-generator is active | Applies to ALL code generation |
| Relies on AI remembering to add markers | AI automatically adds markers |
| Only this skill benefits | All skills can benefit |

## Supported Languages

| Language | Requirement Pattern | Test Pattern |
|----------|-------------------|--------------|
| Python | `# @REQ URS-xxx` | `# @TEST[OQ-UM-xxx]` |
| JavaScript/TypeScript | `// @REQ URS-xxx` | `// @TEST[OQ-UM-xxx]` |
| Java | `// @REQ URS-xxx` | `// @TEST[OQ-UM-xxx]` |
| C/C++/C# | `// @REQ URS-xxx` | `// @TEST[OQ-UM-xxx]` |
| Go | `// @REQ URS-xxx` | `// @TEST[OQ-UM-xxx]` |
| Rust | `// @REQ URS-xxx` | `// @TEST[OQ-UM-xxx]` |
| SQL | `-- @REQ URS-xxx` | `-- @TEST[OQ-UM-xxx]` |
| Shell | `# @REQ URS-xxx` | `# @TEST[OQ-UM-xxx]` |
| Ruby | `# @REQ URS-xxx` | `# @TEST[OQ-UM-xxx]` |
| PHP | `// @REQ URS-xxx` | `// @TEST[OQ-UM-xxx]` |
| YAML | `# @REQ URS-xxx` | `# @TEST[OQ-UM-xxx]` |

## Standard Modules

| Module ID | Name | Test Prefix |
|-----------|------|-------------|
| `user_mgmt` | User Management | UM |
| `audit_trail` | Audit Trail | AT |
| `data_mgmt` | Data Management | DM |
| `business_func` | Business Functions | BF |
| `reporting` | Reporting | RP |
| `integration` | Integration | INT |
| `security` | Security | SEC |
| `compliance` | Compliance | CMP |

## Risk Levels

| Level | Description | Requires Validation |
|-------|-------------|-------------------|
| H | High Risk - Security, compliance, electronic signature, audit trail | Yes |
| M | Medium Risk - Default for most requirements | Yes |
| L | Low Risk - Simple features, documentation, reports | No |

## Example Code

```python
# @REQ URS-001 - System shall support role-based access control (RBAC)
# @RISK H  # Security related
def assign_role(user_id: str, role: str) -> bool:
    """
    Assign a role to a user.
    @TEST[OQ-UM-001] - Verify role assignment
    """
    # Implementation...
    return True

# @REQ URS-002 - User passwords must meet complexity requirements
# @RISK H  # Security related
def validate_password(password: str) -> bool:
    """
    Validate password complexity.
    @TEST[OQ-UM-002] - Verify password complexity
    """
    return len(password) >= 8

# @REQ URS-010 - System shall record all user actions in audit trail
# @FS FS-003
# @RISK H  # Compliance related
def record_audit_event(event_type: str, user_id: str, details: dict):
    """
    Record an event to the audit trail.
    @TEST[OQ-AT-001] - Verify audit trail recording
    """
    # Implementation...
    pass
```

## For Other Skills

This standards file is **skill-agnostic**. Other skills can read it to provide consistent annotation:

```python
from csv_documentation_generator.standards_reader import StandardsReader

reader = StandardsReader()
patterns = reader.get_requirement_patterns()
rules = reader.get_system_prompt_rules()
```

No cross-skill dependency required - standards are opt-in.

## Customization

The standards file at `{skill_root}/standards/code-annotations.json` can be customized:

- Add new language patterns
- Modify marker formats
- Adjust risk levels
- Enable/disable specific marker types

Set `"enforcement": "strict"` in the JSON file to require strict adherence.
