# Autoresearch Configuration — fiesta-agents v2 (Certification + Licensing + Payroll)

## Target Skill
- **Path:** `/root/.openclaw/workspace/skills/fiesta-agents/SKILL.md`
- **Working copy:** `fiesta-agents-v2-certified.md` (this directory)
- **Baseline:** `SKILL.md.baseline` (never touch)

## Optimization Goal
Add three new organizational capabilities to fiesta-agents:
1. **Certification Department** — Agents can be certified for specific competencies. Certification is earned through demonstrated task completion, not self-declared. Includes certification levels, renewal, and revocation.
2. **Licensing** — Agents operate under licenses that define scope of work, permitted tools, cost limits, and audit requirements. Licenses can be granted, suspended, or revoked by Daimyo (judicial branch).
3. **Payroll** — Agent compensation via the entropy economy (Shannon). Work produces entropy. Entropy is minted. Agents earn based on contribution quality and certification level. Integrates with existing entropy-economy server (port 9001).

## Test Inputs (5 scenarios)
1. "Use the certification department to certify frontend-dev for React proficiency based on their last 3 deliverables"
2. "Issue a license to growth-engineer for Twitter marketing operations with a 500 Shannon budget cap"
3. "Run payroll for all agents who completed tasks this week — calculate entropy earned based on task complexity and certification level"
4. "Suspend the license of backend-architect pending review of a failed deployment — Daimyo authority"
5. "Use the orchestrator to onboard a new agent: certify, license, and add to payroll in one pipeline"

## Eval Criteria (5 binary checks)

EVAL 1: Certification Section Exists
Question: Does the skill output include a Certification Department section with at least 3 certification levels and a clear earn/revoke process?
Pass: Section exists with named levels (e.g., Apprentice/Journeyman/Master or L1/L2/L3), earn criteria, and revocation rules
Fail: No certification section, or section exists but lacks levels or process

EVAL 2: Licensing Framework Present
Question: Does the skill define a licensing model where agents have scoped permissions, budget limits, and Daimyo oversight?
Pass: Licensing section with scope definition, cost limits, granting authority, and suspension/revocation mechanism
Fail: No licensing section, or licenses exist but lack budget limits or judicial oversight

EVAL 3: Payroll Integration
Question: Does the skill describe a payroll system that connects to the entropy economy (Shannon), with compensation tied to certification level and contribution quality?
Pass: Payroll section references Shannon/entropy, ties pay to certification level, includes quality multiplier
Fail: No payroll section, or payroll exists but disconnected from entropy economy or certification

EVAL 4: Agent Table Updated
Question: Does the Agent Index table include new agents or roles for certification, licensing, and payroll operations?
Pass: At least 2 new agent roles added (e.g., certification-officer, payroll-administrator, licensing-authority, or similar)
Fail: Agent table unchanged from baseline — no new roles for the three new departments

EVAL 5: Orchestrator Handles Full Lifecycle
Question: Does the orchestrator workflow section include steps for certification, licensing, and payroll in agent onboarding or project completion?
Pass: Orchestrator workflow mentions certification check, license verification, or payroll step as part of its pipeline
Fail: Orchestrator workflow unchanged — no mention of certification, licensing, or payroll integration

## Parameters
- **Runs per experiment:** 3 (cost-conscious, sufficient signal)
- **Budget cap:** 10 experiments max
- **Working copy name:** fiesta-agents-v2-certified.md
