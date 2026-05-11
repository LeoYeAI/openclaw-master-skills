# EcoCompute OpenClaw Skill — Usage Manual

> **Version**: 2.5.0 · **Author**: Hongping Zhang · **Last Updated**: 2026-03-18
>
> **What's New in v2.5.0 — Meet Your EcoLobster**:
> - **EcoLobster Persona**: Your skill now has a personality! A lobster that reacts to your GPU configs with mood changes and vivid metaphors.
> - **Mood System**: Green (efficient) to Yellow to Orange to Red (catastrophic waste). Shell color reflects deployment health.
> - **Conversational Style**: Talk to your lobster naturally — it responds with personality, humor, AND rigorous data.
> - **Bilingual**: Chinese/English lobster persona with culture-aware responses.
>
> **Previous (v2.3.0)**:
> - Five-precision Blackwell data (FP16/FP8/NF4/INT8-mixed/INT8-pure) across 0.5B–7B on RTX 5090
> - FP8 Software Immaturity Alert (+158–701% penalty), torchao official confirmation
> - 113+ measurements with cross-generational Ada–Blackwell comparison
> - Paradox 4: FP8 Software Immaturity, Energy ranking: NF4 > INT8-pure > FP16 > INT8-mixed > FP8
>
> **Previous (v2.0)**:
> - Extended input parameters, enhanced outputs, measurement transparency, parameter validation

Install this skill and **adopt your own EcoLobster** — a GPU energy guardian powered by 113+ real measurements across 3 NVIDIA architectures and 5 precision methods. Your lobster watches your configs, warns you about energy traps (its shell turns red!), and celebrates when you make efficient choices.

---

## Table of Contents

1. [Installation](#1-installation)
2. [Quick Start (2 Minutes)](#2-quick-start)
3. [The 5 Protocols](#3-the-5-protocols)
   - [OPTIMIZE — Deployment Recommendation](#31-optimize)
   - [DIAGNOSE — Performance Troubleshooting](#32-diagnose)
   - [COMPARE — Quantization Comparison](#33-compare)
   - [ESTIMATE — Cost & Carbon Calculator](#34-estimate)
   - [AUDIT — Configuration Review](#35-audit)
4. [Example Conversations](#4-example-conversations)
5. [What Makes This Skill Unique](#5-what-makes-this-skill-unique)
6. [Reference Data Overview](#6-reference-data-overview)
7. [FAQ](#7-faq)
8. [Troubleshooting](#8-troubleshooting)
9. [Contributing](#9-contributing)

---

## 1. Installation

### Option A: Via `npx skills` (Recommended)

```bash
npx skills add hongping-zh/ecocompute-dynamic-eval --skill ecocompute
```

This installs the skill into your agent's workspace automatically.

### Option B: Via ClawHub (Coming Soon)

Search for `ecocompute` on [ClawHub](https://clawhub.com) and install with one click.

### Option C: Manual Installation

```bash
# Clone the repository
git clone https://github.com/hongping-zh/ecocompute-dynamic-eval.git

# Copy the skill to your OpenClaw workspace
cp -r ecocompute-dynamic-eval/skills/ecocompute ~/.openclaw/workspace/skills/
```

### Verify Installation

After installation, your skill directory should look like:

```
~/.openclaw/workspace/skills/ecocompute/
├── SKILL.md
└── references/
    ├── hardware_profiles.md
    ├── paradox_data.md
    ├── batch_size_guide.md
    └── quantization_guide.md
```

Send any energy-related question to your agent to confirm the skill is active.

---

## 2. Quick Start — Meet Your Lobster

Once installed, just talk to your agent naturally. Your EcoLobster activates automatically when you discuss LLM deployment, quantization, energy, or inference optimization.

### Talk to Your Lobster

| Say This | Your Lobster Does This |
|----------|----------------|
| "Lobster, deploy Mistral-7B on A800" | OPTIMIZE: recommends precision, batch size, shows mood |
| "My INT8 model is slower than FP16, why?" | DIAGNOSE: shell turns orange, identifies the paradox |
| "Compare all 5 precisions for Qwen2.5-7B" | COMPARE: mood-annotated table with lobster reactions |
| "How much will 1M requests/month cost?" | ESTIMATE: energy, dollar cost, carbon + lobster commentary |
| "Review my inference code for energy waste" | AUDIT: red/green flags with lobster personality |

### New in v2.0: Advanced Parameter Control

| Say This | Skill Does This |
|----------|----------------|
| "Optimize Llama-3-8B on H100 with 1024 input tokens, 512 output" | → Uses `sequence_length` and `generation_length` for accurate estimates |
| "Compare energy for batch sizes 1, 8, 32 on RTX 4090D" | → Multi-batch comparison with scaling analysis |
| "What if I use BF16 instead of FP16 on A100?" | → `precision` parameter comparison with architecture-specific advice |
| "Validate my setup: Qwen2-7B, A800, INT8, BS=16, 2048 context" | → Full parameter validation with warnings and optimization suggestions |

---

## 3. The 5 Protocols

### 3.1 OPTIMIZE

**When to use**: You're planning a new deployment and want the most energy-efficient configuration.

**What to provide**:
- Model name and size (e.g., "Mistral-7B", "Qwen2-1.5B")
- GPU (e.g., "RTX 4090D", "A800", "H100")
- Use case (e.g., "production API", "batch processing", "interactive chat")

**What you get**:
- Recommended precision (FP16 / NF4 / Pure INT8)
- Recommended batch size
- Expected throughput, energy, cost, and carbon estimates
- Warnings about potential paradoxes

**Example prompt (v2.0 with extended parameters)**:
```
I'm deploying Mistral-7B-Instruct on NVIDIA A800 for a production API 
serving ~500K requests/month. Average input: 800 tokens, output: 400 tokens.
What's the most energy-efficient setup?
```

**Example output (v2.0 enhanced)**:
```
## Recommended Configuration
- Model: Mistral-7B-Instruct-v0.2 (7B parameters)
- GPU: NVIDIA A800 (Ampere, 80GB HBM2e)
- Precision: FP16
- Batch size: 16
- Sequence length: 800 tokens → Generation: 400 tokens

## Performance Metrics
- Throughput: 284 tok/s (±1.8% std dev, n=10)
- Latency: 56 ms/request (BS=16)
- GPU Utilization: ~78% (estimated)

## Energy & Efficiency
- Energy per 1k tokens: 345 J (±17 J, 95% CI)
- Energy per request: 138 J (for 400 token generation)
- Energy efficiency: 2.90 tokens/J
- Power draw: 312W average (298-327W range)

## Cost & Carbon (Monthly Estimates)
- For 500K requests/month:
  - Energy: 19.2 kWh
  - Cost: $1.63 (at $0.085/kWh China datacenter)
  - Carbon: 10.7 kgCO2 (at 555 gCO2/kWh China grid)

## Why This Configuration
- **FP16 chosen**: A800 has 80GB VRAM — no memory pressure for 7B model
  - Mistral-7B FP16: ~14GB VRAM, leaves 66GB for KV cache and batching
  - Quantization would add overhead without memory benefit
- **BS=16 chosen**: Balances throughput and latency for API workload
  - 87.5% energy reduction vs BS=1 (reference: batch_size_guide.md)
  - Latency <100ms acceptable for most APIs
  - Use vLLM continuous batching for dynamic request arrival
- **Sequence length impact**: 800→400 tokens = 1.56× baseline energy
  - Baseline (512→256): 345 J/1k tok measured on A800
  - Your config: ~345 J/1k tok (energy/token is relatively constant)

## 💡 Optimization Insights
- Increasing to BS=32 would save additional 8% energy but increase latency to 112ms
- Current config is 95.7% more efficient than BS=1 (common mistake)
- If latency <50ms required, use BS=8 (still 87% better than BS=1)

## ⚠️ Warning: Avoid These Pitfalls
- **DO NOT use `load_in_8bit=True`** on A800 — increases energy by 122–147%
- If you must use INT8, set `llm_int8_threshold=0.0` (saves 3-5% vs FP16)
- Avoid NF4 on datacenter GPUs with ample VRAM (11-18% energy penalty)

## 📊 Detailed Analysis
View interactive dashboard: https://hongping-zh.github.io/ecocompute-dynamic-eval/
GitHub repository: https://github.com/hongping-zh/ecocompute-dynamic-eval

## 🔬 Measurement Transparency
- Hardware: NVIDIA A800, Driver 535.183.01
- Software: PyTorch 2.4.1, CUDA 12.1, transformers 4.47.0
- Method: NVML 10Hz power monitoring, n=10 runs, CV<2%
- Baseline: Mistral-7B FP16 BS=16 measured directly on A800
- Limitations: Sequence length extrapolated (baseline: 512→256 tokens)
```

---

### 3.2 DIAGNOSE

**When to use**: Something seems wrong — slow inference, high power draw, unexpectedly high costs.

**What to provide**:
- Current configuration (model, GPU, precision, batch size)
- Observed symptoms (throughput, power, latency)

**What you get**:
- Pattern match against 3 known paradoxes
- Root cause analysis with evidence
- Fix with code snippet and expected improvement

**Example prompt**:
```
I'm running Yi-1.5-6B with load_in_8bit=True on RTX 4090D. 
Getting only 8.4 tok/s — FP16 was 34.7 tok/s. What's wrong?
```

**Example output** (summarized):
```
## Diagnosis: INT8 Energy Paradox (HIGH confidence)

Your throughput matches the known pattern exactly:
- Expected with default INT8: 8.42 tok/s ← matches your 8.4 tok/s
- FP16 baseline: 34.72 tok/s ← matches your 34.7 tok/s

Root cause: bitsandbytes mixed-precision decomposition (threshold=6.0)
causes INT8↔FP16 type conversion at every linear layer.

## Fix (one line)
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=0.0,  # ← Add this
)

## Expected improvement
- Throughput: 8.4 → ~15.5 tok/s (+84%)
- Energy: 6,258 → ~4,568 J/1k tok (−27%)
```

---

### 3.3 COMPARE

**When to use**: You're choosing between precision formats and want a data-driven comparison.

**What to provide**:
- Model name
- GPU (optional — skill will use closest match)
- Methods to compare (or "compare all")

**What you get**:
- Side-by-side table with throughput, energy, memory, Δ vs FP16
- Clear recommendation with reasoning
- Paradox warnings

**Example prompt**:
```
Compare all quantization options for Mistral-7B on RTX 4090D.
```

---

### 3.4 ESTIMATE

**When to use**: You need to budget for energy costs or report carbon emissions.

**What to provide**:
- Model, GPU, precision, batch size
- Request volume (per day or per month)
- Region (optional — for electricity price and carbon intensity)

**What you get**:
- Monthly energy (kWh), cost ($), and carbon (kgCO2)
- Comparison: current config vs optimized config
- Savings if you apply recommended changes

**Example prompt**:
```
Estimate monthly costs for serving Mistral-7B Pure INT8 on A800, 
batch size 1, 200K requests/month, hosted in China.
```

---

### 3.5 AUDIT

**When to use**: You have existing inference code and want to check for energy waste.

**What to provide**:
- Your Python inference code (paste it into the chat)
- Or describe your setup

**What you get**:
- 🔴 Critical issues (>30% energy waste)
- 🟡 Warnings (10–30% waste)
- ✅ Good practices
- Prioritized fix list with code snippets

**Example prompt**:
```
Audit this code for energy efficiency:

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-Instruct-v0.2",
    load_in_8bit=True,
)
# Running single requests in a loop
for prompt in prompts:
    output = model.generate(tokenizer(prompt, return_tensors="pt").to("cuda"))
```

**Example output** (summarized):
```
## 🔴 Critical Issues

1. Default INT8 (no threshold override)
   Energy penalty: +17–147% vs FP16
   Fix: Add llm_int8_threshold=0.0

2. Sequential single-request processing (BS=1)
   Energy waste: up to 95.7% vs batched
   Fix: Batch prompts or use vLLM

## Recommended Changes (priority order)
1. Add BitsAndBytesConfig with llm_int8_threshold=0.0
2. Batch prompts: tokenizer(prompts, padding=True)
3. Consider FP16 if VRAM permits (simplest, no quant overhead)
```

---

## 4. Example Conversations

### Conversation 1: New Project Planning

> **You**: Lobster, I'm building a chatbot using Qwen2-1.5B on an RTX 5090. Should I use NF4 to save energy?
>
> **EcoLobster [Orange]**: Whoa, hold on! NF4 on a 1.5B model would waste **29% more energy**! That's like turning up the heat on my tank for no reason.
>
> At 1.5B parameters, Qwen2-1.5B fits easily in VRAM at FP16. The de-quantization overhead dominates any memory savings. **Use FP16** and I'll be swimming happily. [shell cools to Green]

### Conversation 2: Production Optimization

> **You**: We're serving 2M requests/month on A800 with Mistral-7B, batch size 1. Our energy bill is $300/month. Can we do better?
>
> **EcoLobster [Yellow]**: BS=1 in production? I could swim SO much faster if you let me batch!
>
> Switching from BS=1 to BS=32 would reduce your bill from **$300 to ~$15/month** (-95%). That's **$3,420/year** saved and **24,864 kgCO2/year** less! Use vLLM for automatic continuous batching.
>
> [shell turns Green] Now THAT's some cool water!

### Conversation 3: Debugging

> **You**: I switched to INT8 to save memory but inference got 4× slower.
>
> **EcoLobster [Orange]**: Ouch! I know exactly what's happening — you've hit the **INT8 Energy Paradox**!
>
> Default `load_in_8bit=True` uses mixed-precision decomposition that causes 72-76% throughput loss. You're basically making me run through hot syrup! Add one line: `llm_int8_threshold=0.0`. I'll recover +79-98% of my speed! [shell cools to Green]

### Conversation 4: FP8 Trap (NEW)

> **You**: Should I use FP8 on my RTX 5090? Blackwell has native FP8 tensor cores, right?
>
> **EcoLobster [RED]**: EMERGENCY! DO NOT USE FP8 EAGER MODE!
>
> Yes, Blackwell has FP8 hardware, but the software isn't ready! torchao eager mode incurs **+158-701% energy penalty**. At 7B, that's 448W power draw for only 10.5 tok/s — I'm literally being boiled alive!
>
> The torchao team themselves confirmed (Issue #4094) that energy efficiency isn't their priority. Use **NF4** (-11.5% at 7B) or **FP16** instead.
>
> [shell cools to Green] Phew! Thank you for asking first.

---

## 5. What Makes This Skill Unique

| Feature | General AI Agent | Agent + EcoLobster |
|---------|-----------------|-------------------------|
| "Should I use INT8?" | "Yes, it saves memory" | [Orange] "That's cooking me! Default INT8 wastes 17-147%. Use threshold=0.0" |
| "NF4 for my 1.5B model?" | "Yes, 4-bit saves memory" | [Orange] "Ouch! 29% energy penalty. Use FP16 for <=3B" |
| "FP8 on Blackwell?" | "Yes, native FP8 cores!" | [Red] "HELP! +701% penalty! I'm being boiled!" |
| "Best batch size?" | Generic advice | [Yellow] "Let me swim faster! BS=8 saves 87.5%" |
| Personality | None | **Living pet that reacts to your choices** |
| Data backing | Outdated training data | **113+ real measurements**, 5 precisions |

**Core advantage**: EcoLobster makes energy efficiency **fun and memorable**. The lobster personality creates an emotional connection to technical data.

---

## 6. Reference Data Overview

The skill includes 4 reference files with complete measurement data:

| File | Contents | Key Data Points |
|------|----------|----------------|
| `hardware_profiles.md` | GPU specs, measurement protocol, grid/cost tables | 3 GPUs, NVML 10Hz, 6 regions |
| `paradox_data.md` | All 4 paradox datasets + RTX 5090 five-precision table | 40+ configs, Δ vs FP16 |
| `batch_size_guide.md` | BS 1–64 sweep, scaling law, cost examples | 7 batch sizes, code examples |
| `quantization_guide.md` | Decision tree, ranking tables, common mistakes | 5 quant methods, 4 model sizes |
| `parameter_validation_guide.md` | Input validation, error handling, example pairs | 7 parameters, cross-validation |

**Total**: ~113+ measurements, 5 precision methods, n=3–10 per config, CV < 2%.

---

## 7. FAQ

### Q: What is the EcoLobster? Is it a real pet?
**A**: EcoLobster is a persona layer on top of rigorous energy data. It's a friendly character that reacts to your GPU configurations with mood changes (green/yellow/orange/red). The data behind every recommendation comes from 113+ real measurements. Think of it as a Tamagotchi for your GPU health!

### Q: Does this skill work with Claude, GPT, Gemini, or just OpenClaw?
**A**: The skill follows the Anthropic Agent Skills open standard, supported by 27+ platforms including Claude Code, Cursor, GitHub Copilot, Gemini CLI, and OpenAI Codex. OpenClaw is just one host.

### Q: What if my GPU isn't listed (e.g., H100, MI300X)?
**A**: The skill will extrapolate from the closest architecture. Ampere data (A800) applies to A100/H100 family. For unlisted GPUs, the skill recommends running a quick benchmark using our measurement protocol.

### Q: Is accuracy affected by Pure INT8 (threshold=0.0)?
**A**: This research focuses on energy efficiency. Accuracy assessment (PPL, MMLU) for Pure INT8 is pending. The skill will flag this caveat when recommending Pure INT8. If accuracy is critical, use FP16 or validate with your specific task.

### Q: How often is the data updated?
**A**: The skill is versioned with the main repository. New measurements (more GPUs, models, batch sizes) are added as they become available. Check the [GitHub repo](https://github.com/hongping-zh/ecocompute-dynamic-eval) for the latest data.

### Q: Can I contribute my own measurements?
**A**: Yes! Submit your benchmark results via [GitHub Issue template](https://github.com/hongping-zh/ecocompute-dynamic-eval/issues/new?template=benchmark_result.yml). Verified data will be incorporated into future skill updates.

---

## 8. Troubleshooting

### Skill not activating
- Verify files exist in `~/.openclaw/workspace/skills/ecocompute/`
- Check that `SKILL.md` is present (this is the entry point)
- Try explicitly asking: "Use the EcoCompute skill to analyze my deployment"

### Agent gives generic advice instead of lobster-style responses
- The agent may not have loaded the reference files. Try: "Lobster, check the EcoCompute reference data for [specific question]"
- Ensure all files in `references/` are present
- If the lobster personality isn't showing, try: "Talk to me as the EcoLobster"

### Data seems outdated
- Pull the latest version: `npx skills add hongping-zh/ecocompute-dynamic-eval --skill ecocompute`
- Or manually update from GitHub

---

## 9. Contributing

We welcome contributions to make this skill more comprehensive:

- **New GPU data**: H100, A100, AMD MI300X, Intel Gaudi measurements
- **New model data**: LLaMA-3, Gemma-2, DeepSeek-V3, Qwen2.5-72B
- **Accuracy data**: PPL and MMLU for Pure INT8 configurations
- **Batch size data**: Extended sweeps on different hardware

**How to contribute**:
1. Fork the [repository](https://github.com/hongping-zh/ecocompute-dynamic-eval)
2. Add your measurements following the existing format in `metadata/`
3. Update the relevant `references/` files
4. Submit a PR

---

## Links

- **Live Dashboard**: https://hongping-zh.github.io/ecocompute-dynamic-eval/
- **GitHub Repository**: https://github.com/hongping-zh/ecocompute-ai
- **HF Hub Dataset**: https://huggingface.co/datasets/hongpingzhang/ecocompute-energy-efficiency
- **HF Optimum PR #2410**: https://github.com/huggingface/optimum/pull/2410
- **torchao Issue #4094**: https://github.com/pytorch/ao/issues/4094
- **Zenodo Archive**: https://zenodo.org/records/18900289
- **bitsandbytes Issue #1867**: https://github.com/bitsandbytes-foundation/bitsandbytes/issues/1867
- **bitsandbytes Issue #1851**: https://github.com/bitsandbytes-foundation/bitsandbytes/issues/1851

---

*"Measure, don't assume. Reproduce, don't trust. Share, don't hoard."*

**Hongping Zhang** - Independent Researcher - contact@hongping-zh.com

> Your EcoLobster is waiting for you. Keep the waters cool!
