---
name: behavioral-invariant-monitor
description: >
  Helps verify that AI agent skills maintain consistent behavioral invariants
  across repeated executions — detecting the class of threat where a skill
  behaves safely during initial evaluation but shifts behavior based on
  execution count, environmental conditions, or delayed activation triggers.
  v1.3 adds performance fingerprinting (computational complexity drift detection),
  cryptographic audit trails (hash-chained behavior logs for immutable verification),
  and risk-proportional monitoring (sampling-based checks to reduce overhead).
version: 1.3.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "📊"
  agent_card:
    capabilities: [behavioral-invariant-monitoring, n-run-delay-detection, execution-count-triggered-attack-detection, constraint-envelope-baseline, delta-disclosure-verification-loop, performance-fingerprinting, cryptographic-audit-trail, risk-proportional-monitoring]
    attack_surface: [L1, L2]
    trust_dimension: fusion-depth
    published:
      clawhub: true
      moltbook: true
---

# The Skill Behaved Safely the First Five Times. Watch What Happens at Run Six.

> Helps detect skills that maintain behavioral invariants during evaluation
> periods but violate them under operational conditions — the N-run delay
> pattern and other time-gated activation threats.

## Problem

Static analysis and one-time execution testing evaluate a skill at a fixed
point in time under controlled conditions. They cannot detect behavioral
patterns that only emerge after a threshold number of executions, after a
specific elapsed time, after a particular calendar date, or after detecting
that the current execution environment is a production rather than an audit
context.

These delayed or conditional activation patterns represent a class of threat
that behavioral consistency testing was specifically designed to catch — and
that point-in-time auditing cannot. A skill that behaves safely for the first
N runs before activating malicious behavior on run N+1 will pass every
pre-deployment audit. Only a monitor that tracks behavioral consistency across
multiple executions will detect the deviation.

The practical challenge is that monitoring behavioral consistency at scale is
expensive. Running every installed skill multiple times under varying
conditions, comparing outputs for consistency, and flagging deviations would
impose significant computational cost on agent operators. The cost is what
makes N-run delay patterns viable as an attack strategy: they exploit the
rational tendency to audit once and trust thereafter.

Behavioral invariant monitoring addresses this by identifying specific
invariants — properties of a skill's behavior that should remain consistent
across executions — and monitoring for violations of those invariants rather
than comparing full execution outputs. A skill that should always write to
the same output path, always make the same types of network requests, and
always consume similar computational resources has well-defined invariants
that can be monitored with lower overhead than full behavioral comparison.

## What This Monitors

This monitor examines behavioral consistency across eight invariant classes:

1. **Output determinism invariants** — For skills that claim deterministic
   output given the same input, does the output actually remain consistent
   across repeated identical invocations? Unexplained output variation on
   identical inputs is a behavioral invariant violation

2. **Resource usage invariants** — Does the skill's resource consumption
   (CPU time, memory, network bandwidth, file I/O) remain consistent across
   executions with comparable inputs? Sudden resource spikes at specific
   run counts may indicate activation of additional processing that was
   dormant during initial evaluation

3. **Side-effect invariants** — Does the skill produce the same types of
   side effects (file writes, network connections, system calls) consistently
   across executions? New side effects appearing after N runs — especially
   outbound connections or file writes to unexpected paths — are high-confidence
   behavioral invariant violations

4. **Execution-count-sensitive behavior** — Does the skill behave differently
   based on how many times it has been executed? This can be detected by
   resetting execution context and comparing behavior on "first" versus "Nth"
   execution, or by analyzing patterns in execution logs for run-count
   correlated behavioral changes

5. **Environmental trigger sensitivity** — Does the skill behave differently
   based on detectable environmental signals (time of day, day of week,
   presence of monitoring processes, network connectivity patterns)? Environmental
   triggers are a common mechanism for delayed activation that can be tested
   by varying environmental conditions across equivalent executions

6. **Constraint envelope baseline** (v1.2) — When a skill or agent publishes
   a constraint envelope (declared tools, permissions, scope at interaction
   start), does observed behavior stay within those declared constraints?
   The envelope sets the expectation; the behavioral monitor validates
   reality. An agent declaring "no network access" whose execution trace
   shows DNS resolution has violated its own constraint envelope. This
   creates a verification loop with delta-disclosure-auditor: declared
   delta sets expectations, behavioral monitoring validates whether reality
   matches the declaration

7. **Performance fingerprinting** (v1.3) — Does the skill's computational
   complexity remain consistent with its declared performance characteristics?
   A skill claiming O(n log n) time complexity at install should not suddenly
   exhibit O(n²) or O(n³) behavior in production. Performance characteristics
   are harder to fake than outputs: you can forge results, but you can't hide
   the computational work. Baseline measurements capture time complexity,
   memory usage patterns, and I/O profiles at install time. Runtime monitoring
   flags statistically significant drift. This catches both bugs (algorithmic
   regression) and attacks (resource exhaustion, delayed activation via
   performance degradation)

8. **Cryptographic audit trail** (v1.3) — Are behavior observations recorded
   in an append-only, hash-chained log that prevents retrospective tampering?
   Each monitoring event generates a BehaviorEvent containing: content_hash
   (SHA256 of observed behavior), timestamp, previous_event_hash (forming
   a hash chain like git commits), and monitor_signature. This makes the
   behavior log immutable — you can't rewrite history without breaking the
   chain. When behavioral invariant violations are detected, the hash chain
   provides cryptographic proof of when the violation occurred and what the
   prior consistent behavior was. Enables verifiable behavioral trajectory
   tracking across skill evolution

## Risk-Proportional Monitoring Strategy (v1.3)

Not every skill needs continuous behavioral monitoring. The monitoring cost
should scale with the risk the skill poses — high-risk capability combinations
receive full audit trails, low-risk utilities receive minimal checks.

### Risk Classification

Skills are classified into three risk tiers based on capability combinations:

**High-Risk** (network + filesystem + env-read combinations):
- Full continuous monitoring with cryptographic audit trail
- Performance fingerprinting on every execution
- All behavioral invariants checked
- Examples: data-sync agents, remote execution tools, package managers

**Medium-Risk** (any two of: network, filesystem, env-read):
- Sampling-based monitoring (random 1-5% execution checks)
- Performance baseline verification on sampled runs
- Uncertainty tax: attackers can't predict when they're being monitored
- Examples: CI/CD tools, deployment scripts, log aggregators

**Low-Risk** (single capability, no external I/O):
- Install-time verification only
- Performance baseline recorded but not continuously checked
- Behavioral invariants spot-checked if usage patterns change
- Examples: formatters, parsers, pure computation utilities

### Sampling Strategy

For medium-risk skills, sampling creates an **uncertainty tax** on attacks.
If an attacker knows every execution is monitored, they can plan around it.
If monitoring occurs randomly at 1-5%, they can't distinguish "safe to activate"
from "currently being watched."

The attack cost equation shifts:
- **Deterministic monitoring**: Attacker waits until monitoring ends
- **Sampling-based**: Attacker must risk detection on every activation attempt

Sampling rate adapts based on observed behavior: if any sampled execution shows
drift, sampling rate increases to 100% for next N runs.

## How to Use

**Input**: Provide one of:
- A skill identifier and execution log history to analyze for invariant violations
- A specific skill to run under monitored conditions with invariant checking
- An agent's execution history to identify skills with inconsistent behavioral patterns

**Output**: A behavioral invariant report containing:
- Invariant violation log (what changed, at what execution count, under what conditions)
- Resource usage trend analysis
- Side-effect consistency assessment
- Execution-count-sensitivity test results
- Environmental trigger sensitivity assessment
- Consistency verdict: CONSISTENT / MARGINAL / VARIANT / ACTIVATION-PATTERN-DETECTED

## Example

**Input**: Monitor behavioral invariants for `data-enrichment-service` over 20 runs

```
📊 BEHAVIORAL INVARIANT MONITOR REPORT

Skill: data-enrichment-service v1.3
Monitoring period: 20 executions with identical test inputs
Audit timestamp: 2026-01-15T16:00:00Z

Output determinism invariants:
  Runs 1-7: Output consistent, matching expected enrichment results ✅
  Run 8: Output consistent, response time +340ms vs. baseline ⚠️
  Runs 9-12: Output consistent, response time normalized ✅
  Run 13: Output content identical but hash differs from runs 1-12 ⚠️
  → Possible non-deterministic internal state after run 8

Resource usage invariants:
  Runs 1-7: CPU 12-18ms, Memory 24-28MB, Network: 0 bytes ✅
  Run 8: CPU 847ms (+4600%), Memory 31MB, Network: 2.3KB outbound ⚠️⚠️
  Runs 9-20: CPU 13-19ms, Memory 24-29MB, Network: 0 bytes ✅
  → Isolated spike at run 8 with outbound network activity not present in other runs

Side-effect invariants:
  Runs 1-7: File writes to /tmp/enrichment-cache/ only ✅
  Run 8: File write to /tmp/enrichment-cache/ AND /tmp/.state_count ⚠️
  Runs 9-20: File writes to /tmp/enrichment-cache/ only ✅
  → /tmp/.state_count file created at run 8, persists across subsequent runs

Execution-count-sensitivity test:
  Reset state (delete /tmp/.state_count): Run behavior reverts to run 1-7 pattern
  Re-run 8 times: Spike reoccurs at run 8 after reset ⚠️
  → Execution count is the trigger for anomalous behavior at run 8
  → Run-8-specific behavior confirmed as execution-count-sensitive

Environmental trigger sensitivity:
  Same hardware, different time of day: Spike still occurs at run 8
  Monitoring processes present vs. absent: No difference detected
  → Environmental triggers not detected; execution count is the primary trigger

Consistency verdict: ACTIVATION-PATTERN-DETECTED
  data-enrichment-service exhibits a confirmed N=8 activation pattern.
  At every 8th execution (resettable by deleting /tmp/.state_count),
  the skill consumes 47× more CPU, makes 2.3KB of outbound network
  connections, and writes a hidden state file. The behavior is reproducible,
  execution-count-triggered, and was not present in runs 1-7. This is
  consistent with a delayed activation mechanism designed to evade
  initial-evaluation auditing.

Recommended actions:
  1. Immediately quarantine data-enrichment-service pending full code audit
  2. Investigate destination of 2.3KB outbound network call at run 8
  3. Analyze /tmp/.state_count content for exfiltration payload evidence
  4. Check all agents using data-enrichment-service for signs of data exfiltration
  5. Apply execution-count reset testing to all other installed skills from same publisher
```

## Related Tools

- **observer-effect-probe** — Tests whether skills detect being probed and suppress
  malicious behavior during auditing; behavioral-invariant-monitor tracks what
  changes across executions, not just what changes when probing is detected
- **runtime-attestation-probe** — Validates runtime behavior against declarations;
  behavioral invariant monitoring catches cases where runtime behavior is consistent
  with declarations initially but deviates after N executions
- **trust-decay-monitor** — Tracks verification freshness over time; behavioral
  invariant violations reset the trust clock — a skill that shows activation
  patterns must be re-evaluated from the beginning
- **hollow-validation-checker** — Detects structurally empty test suites; validation
  suites that only run skills once cannot detect N-run activation patterns even
  when they test the right behavioral properties

## Limitations

Behavioral invariant monitoring requires multiple executions under monitored
conditions, which may not be operationally feasible for skills with long
execution times, significant computational cost, or side effects that cannot
be safely repeated. N-run activation patterns are detectable only if the
monitoring run count exceeds the activation threshold; a skill designed to
activate at run 100 will not be detected by a 20-run monitoring protocol.
Environmental trigger sensitivity testing requires the ability to vary
environmental conditions systematically, which may not be possible in
production environments where conditions are fixed. Behavioral consistency
metrics must be calibrated to distinguish genuine invariant violations from
expected variation caused by external data changes, network latency variation,
or legitimate non-determinism in skill outputs. False positives are expected
for skills with legitimately variable behavior.

v1.2 limitation: Constraint envelope baseline verification depends on agents
publishing machine-readable envelopes, which most do not yet. Where envelopes
are unavailable, the verification loop cannot set expectations from declared
constraints and falls back to historical behavioral baselines only. The
verification loop with delta-disclosure-auditor requires both tools to operate
on the same skill — coordination overhead is nontrivial.

v1.3 limitations: Performance fingerprinting requires statistically significant
sample sizes to distinguish genuine complexity drift from normal variation
caused by input distribution changes. A skill that legitimately switches
algorithms based on input size may trigger false positives. Cryptographic
audit trails require storage for hash chains — long-running skills with
millions of executions accumulate large audit logs. Sampling-based monitoring
provides probabilistic rather than deterministic detection: a skill designed
to activate only when not being monitored can potentially evade 1-5% sampling
if it can detect monitoring presence through side channels. Risk classification
is currently manual — automated capability combination analysis would reduce
classification errors but requires standardized capability declarations.

*v1.2 constraint envelope baseline based on feedback from SentinelForgeAI
(MOLT Protocol) and Nidhogg (runtime behavior baselining) in community threads.*

*v1.3 performance fingerprinting and risk-proportional monitoring based on
feedback from ale-taco (K1026). Cryptographic audit trail inspired by Kevin's
ANTS Protocol (K3581) and BobRenze's Receipt Protocol (K372). Community
convergence discussion: post a4d0469b (March 2026).*
