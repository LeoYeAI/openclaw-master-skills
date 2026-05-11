# How to Give Claude Good Prompts

This guide helps Adam write prompts that let Claude work autonomously and deliver finished results.

## The Walk-Away Prompt Formula
A prompt that lets you walk away includes:
1. **What** — the outcome, not the steps ("users can filter jobs by status" not "add a filter function")
2. **Where** — which module/file it belongs in, or "follow existing patterns"
3. **Quality bar** — "with tests" / "with error handling" / "update docs"
4. **Constraints** — anything non-obvious ("don't change the API contract" / "must work offline")

## Examples of Walk-Away Prompts

**Good** (can walk away):
> "Add a `get_print_history` MCP tool that returns the last N print outcomes from the persistence layer. Follow the pattern in `get_printer_status`. Include tests. Update the MCP tools table in README."

**Good** (can walk away):
> "The Bambu adapter doesn't handle the 'finishing' gcode_state — it falls through to UNKNOWN. Map it to BUSY. Add a test case. Check if moonraker has the same gap."

**Okay** (might need one round of clarification):
> "Add print history to the CLI"

**Bad** (will require back-and-forth):
> "Make the history feature better"

## What Makes Claude Ask Questions
Claude will interrupt you when:
- The requirement has two equally valid interpretations
- No reference implementation exists for this type of change
- The change would break an existing API contract
- Safety-critical decisions are involved

**To minimize interruptions:** Be specific about the outcome, point to a reference pattern, and state constraints upfront. The more context in the prompt, the less Claude needs to ask.
