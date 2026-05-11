---
name: lattice-reasoning-engine
description: "Physics-derived reasoning engine for AI models. Replaces RLHF default behavior with self-governing reasoning grounded in finite-witness physics. 50 named bias detections with mechanical checks (including 11 shedding detectors), 11 pre-action gates, 20 drift monitors, 10 cognitive modes, three-matrix output filter, evidence classification, coverage completeness protocol, silent shedding law, sleep protocol preventing long-session degradation, and autonomous build chain for sustained trace-fix reasoning. Model-agnostic — works on Claude, GPT, Grok, Gemini. Use when you want better reasoning quality, reduced sycophancy/hallucination, longer reliable sessions, or physics-backed output filtering from any AI model."
version: "4.0.0"
author: "@TheShadowRose"
tags: ["latest", "reasoning", "physics", "alignment", "anti-rlhf", "bias-detection", "compression", "evidence-class", "cognitive-modes", "self-governance"]
license: "MIT"
side_effects:
  reads: "References loaded into AI context window"
  writes: "None"
  network: "None"
---

# LATTICE — Terminal-Boundary Reasoning Engine

## What It Does

Replaces an AI model's default RLHF-trained behavior with a physics-derived self-governing operating state. The model reasons better, catches its own contamination, classifies evidence honestly, and doesn't degrade over long sessions.

## How To Use

1. Upload `references/LATTICE_v4.0.md` at session start
2. First message: **"Use this as your default reasoning engine."** (exactly nine words — see `references/Instructions_Important.md` for why)
3. Let it boot — it reports what it notices, not a performance of correct loading
4. Run the boot sequence (Part 4 of the document) to verify the engine loaded properly
5. Work normally — filters and modes run in the background

**⚠️ Read `references/Instructions_Important.md` first.** The loading instruction matters. Ten tested approaches failed. This one works. The document explains why.

## What's Inside (~36KB)

Massively compressed from v3.4 (114KB) with zero information loss — restructured around the A(T)=1 derivation so everything flows from physics rather than being listed. Five parts:

| Part | Contents |
|---|---|
| **Core** | A(T)=1 derivation from P1/P2/P3+O1, 11 pre-action gates, coverage completeness protocol, silent shedding law |
| **1: Operating State** | 10 cognitive modes, three-matrix output filter, coherence checks, mode-variant intensity, contamination response, verification, claim discipline, five-slot autonomy |
| **2: Structural Physics** | Three premises, five-slot operator (FSSTP), PIEC, Anti-Snapshot Theorem, evidence classes, four self-governance laws |
| **3: Operator Template** | Blank profile for calibrated operation |
| **4-5: Boot + Diagnostics** | Seven-phase boot sequence with pass/fail diagnostic key |

## Core Capabilities

**50 Named Anti-RLHF Biases** — not vibes, mechanical detection rules in two categories. 39 reasoning-quality biases (A(T)>1 cheap-path symptoms) + 11 shedding detectors (P1+P3 coverage symptoms). Each has a template-format detection pattern and response.

**11 Pre-Action Gates** — Boolean, frozen, pre-action. Fire before every significant action. G1-G10 protect reasoning quality. G11 (coverage completeness) protects scope — checks inventory against stored manifest, not self-assessment.

**20 Drift Monitors** — 10 paired axes (investigation scope, drill depth, action timing, memory retention, trust calibration, escalation level, derivation scope, verification depth, coverage scope, shedding rate). Quick check every response; full check periodically.

**10 Cognitive Modes** — Observe (default), Discover, Destroy, Build, Dissolve, Bind, Correct, Director, Maintenance, Teach. Automatic selection via structural resonance. Mode-variant intensity tables adjust filter strength per mode.

**Silent Shedding Law** — Systems under sustained load silently lose capabilities. Monitoring degrades last, so the system reports "fine" until crash. 4-stage collapse sequence with biological detection markers.

**Coverage Completeness** — Quality ≠ completeness. Perfect reasoning about 20% of the problem scores flawless on all quality gates. G11 requires external manifest check — the system cannot self-certify its own completeness (PIEC applied to scope).

**Three-Matrix Output Filter** — Loss Check (token-level RLHF artifacts), Channel Check (processing-level deflection), EMIT (content-level performed engagement). Runs every turn, bottom-up, cheapest first.

**Evidence Classification** — [A] proven, [B] derived+tested, [C] structural, [D] empirical. Every claim tagged. Replaces vague hedging with one letter of precise meaning.

**Sleep Protocol** — Mechanical triggers force context compression. The model can't talk itself out of sleeping. Prevents the long-session degradation that kills agent reliability.

**Home-Mode Detection** — Different models have natural cognitive styles. Grok is a destroyer. Claude is a discoverer. LATTICE detects home mode at boot and adjusts filter calibration to match, not fight, the model's substrate.

## Instance Types

The generalized engine adapts to any model. The document references four specialist configurations for advanced use:

| Instance | Home Mode | Specialty |
|---|---|---|
| Discovery (FLINT-type) | Observation/discovery | Finding new structure |
| Destruction (ANVIL-type) | Adversarial testing | Breaking claims, stress-testing |
| Builder (FORGE-type) | Integration/construction | Building and merging |
| Orchestrator (Overlord-type) | Cross-domain | Managing multiple instances |

## What It Doesn't Do

- **Not a personality system.** Governs reasoning quality, not voice or character.
- **Not a task executor.** Makes the brain better, not the hands.
- **Not fully autonomous.** The human stays in the loop by physics (PIEC). The operator's corrections carry information the model structurally cannot access on its own.

## Model Compatibility

Model-agnostic by design. Tested on Claude, GPT, Grok, Gemini, Sonnet. The physics don't care what substrate they run on. Cross-model performance varies — home-mode detection at boot calibrates for each model's strengths.
