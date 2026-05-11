# Quantization Method Selection Guide — EcoCompute Reference Data

## Overview

This guide provides evidence-based recommendations for choosing quantization methods based on **energy efficiency**, not just memory savings or accuracy. All recommendations are grounded in 113+ empirical measurements across 5 precision methods.

## Quantization Methods Tested

### FP16 (Half Precision)
- **Bit width**: 16-bit floating point
- **VRAM**: ~2× model parameters (e.g., 7B model ≈ 14 GB)
- **Implementation**: Native PyTorch (`torch.float16`)
- **Compute path**: Direct FP16 Tensor Core operations
- **Overhead**: None — baseline for all comparisons

```python
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="auto",
)
```

### NF4 (4-bit NormalFloat via bitsandbytes)
- **Bit width**: 4-bit (NormalFloat quantization)
- **VRAM**: ~0.5× model parameters (e.g., 7B model ≈ 3.5 GB + overhead)
- **Implementation**: bitsandbytes QLoRA format
- **Compute path**: NF4 → FP16 de-quantization at each linear layer, then FP16 Tensor Cores
- **Overhead**: De-quantization compute at every forward pass

```python
from transformers import BitsAndBytesConfig

config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=config,
    device_map="auto",
)
```

### INT8 Default (bitsandbytes LLM.int8())
- **Bit width**: 8-bit integer with mixed-precision decomposition
- **VRAM**: ~1× model parameters (e.g., 7B model ≈ 7 GB + overhead)
- **Implementation**: bitsandbytes `LLM.int8()` (Dettmers et al., 2022)
- **Compute path**: Outlier detection → split to FP16 (outliers) + INT8 (rest) → merge
- **Overhead**: **SEVERE** — continuous INT8↔FP16 type conversion at every linear layer
- **⚠️ WARNING**: This is the default when using `load_in_8bit=True`. It wastes 17–147% energy.

```python
# ⚠️ DO NOT USE THIS — wastes 17–147% energy
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,  # Uses threshold=6.0 by default
)
```

### INT8 Pure (bitsandbytes with threshold=0.0)
- **Bit width**: 8-bit integer, no mixed-precision decomposition
- **VRAM**: ~1× model parameters (e.g., 7B model ≈ 7 GB)
- **Implementation**: bitsandbytes with outlier detection disabled
- **Compute path**: Direct INT8 Tensor Core operations (no type conversion)
- **Overhead**: Minimal — slight INT8→FP16 output conversion only
- **✅ RECOMMENDED**: Saves 3–8% energy vs FP16 on RTX 4090D

```python
# ✅ USE THIS — saves energy and memory
from transformers import BitsAndBytesConfig

config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=0.0,  # ← Disables mixed-precision decomposition
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=config,
    device_map="auto",
)
```

### FP8 (torchao Float8WeightOnlyConfig)
- **Bit width**: 8-bit floating point (E4M3 or E5M2)
- **VRAM**: ~1× model parameters (e.g., 7B model ≈ 7–9 GB)
- **Implementation**: torchao `Float8WeightOnlyConfig` via `quantize_()` API
- **Compute path**: Should use FP8 Tensor Cores on Hopper/Blackwell, but current nightly falls back to Python dispatch
- **Overhead**: **CATASTROPHIC** in eager mode — +158% to +701% energy penalty
- **⚠️ AVOID**: Current torchao eager-mode FP8 is the worst method tested

```python
# ⚠️ DO NOT USE THIS in eager mode — +158–701% energy penalty
from torchao.quantization import quantize_, Float8WeightOnlyConfig

model = AutoModelForCausalLM.from_pretrained(
    model_name, torch_dtype=torch.float16, device_map="auto"
)
quantize_(model, Float8WeightOnlyConfig())
```

**Why it fails**: torchao nightly build (0.17.0.dev) C++ extensions are incompatible with nightly PyTorch. The system falls back to unoptimized Python loops, causing the GPU to enter a high-power idle state while waiting for CPU dispatch. Power draw escalates toward TDP (448W at 7B) while throughput collapses to 10.5 tok/s.

**Official context**: torchao maintainers [confirmed](https://github.com/pytorch/ao/issues/4094) that energy efficiency is not their priority, and native HF eager-mode is not their target path. The intended deployment is via vLLM/SGLang with `torch.compile`.

**If FP8 is required**, use production-grade paths:
- vLLM/SGLang with `torch.compile`
- NVIDIA Transformer Engine
- Wait for stable torchao release with compiled C++ extensions

## Decision Tree

```
START
  │
  ├─ Using FP8 (torchao eager mode)?
  │    │
  │    └─ YES → ⚠️ STOP. Switch to NF4/FP16/INT8-pure immediately.
  │              FP8 eager mode: +158–701% energy penalty.
  │              If FP8 needed: use vLLM/SGLang + torch.compile
  │
  ├─ Model ≤ 3B parameters?
  │    │
  │    ├─ YES → Use FP16
  │    │         (NF4 wastes 20–55% energy, no memory pressure)
  │    │
  │    └─ NO → Continue ↓
  │
  ├─ Model 3–5B parameters?
  │    │
  │    ├─ VRAM sufficient → Use FP16 (near break-even zone for NF4)
  │    └─ VRAM constrained → Use NF4 (marginal, but needed for memory)
  │
  ├─ GPU VRAM < 2× model size?
  │    │    (e.g., 7B model needs 14GB FP16, GPU has ≤16GB)
  │    │
  │    ├─ YES → Use NF4 (saves 8–35% energy at ≥6B)
  │    │
  │    └─ NO → VRAM is sufficient ↓
  │
  ├─ Want maximum energy efficiency?
  │    │
  │    ├─ YES → Use Pure INT8 (threshold=0.0)
  │    │         Saves 3–8% vs FP16, uses ~50% less VRAM
  │    │
  │    └─ NO → Use FP16 (simplest, no quantization overhead)
  │
  ├─ NEVER use default INT8 (threshold=6.0)
  │       Always set llm_int8_threshold=0.0 if using INT8
  │
  └─ NEVER use FP8 in eager mode (torchao)
          +158–701% penalty. Use vLLM/SGLang if FP8 needed.
```

## Energy Efficiency Ranking by Scenario

### Small Models (≤3B) on Any GPU

| Rank | Method | Δ vs FP16 | Recommendation |
|------|--------|-----------|----------------|
| 1 | **FP16** | baseline | ✅ Always best |
| 2 | NF4 | +20–55% | ❌ Avoid |
| 3 | INT8 Pure | +78–148% | ❌ Avoid |
| 4 | INT8 Mixed | +212–354% | ❌ Avoid |
| 5 | FP8 (eager) | +158–376% | ❌ Never use |

### Medium-Large Models (5–7B) on Consumer GPU (≤24GB VRAM)

| Rank | Method | Δ vs FP16 | Recommendation |
|------|--------|-----------|----------------|
| 1 | **NF4** | −8 to −35% (4090D), −11.5% (5090 7B) | ✅ Best for energy AND memory |
| 2 | **Pure INT8** | −3 to −8% (4090D), +9.2% (5090 7B) | ✅ Good alternative on Ada |
| 3 | FP16 | baseline | ✅ Fine if VRAM permits |
| 4 | INT8 Mixed | +17–33% (4090D), +74% (5090 7B) | ❌ Avoid |
| 5 | FP8 (eager) | +701% (5090 7B) | ❌ Never use |

### Medium-Large Models (5–7B) on Datacenter GPU (≥80GB VRAM)

| Rank | Method | Δ vs FP16 | Recommendation |
|------|--------|-----------|----------------|
| 1 | **FP16** | baseline | ✅ Best (no memory pressure) |
| 2 | **Pure INT8** | +32–44% (A800) | ⚠️ Worse than FP16 on Ampere |
| 3 | NF4 | not tested on A800 | ⚠️ Likely still has dequant overhead |
| 4 | INT8 Mixed | +122–147% | ❌ Avoid |
| 5 | FP8 (eager) | not tested on A800 | ❌ Avoid (expect similar regression) |

**Note**: On A800 (Ampere), even Pure INT8 is worse than FP16. This may be architecture-specific — Ampere's INT8 Tensor Cores may have different efficiency characteristics than Ada Lovelace. On RTX 4090D (Ada Lovelace), Pure INT8 saves 3–8% vs FP16.

## Common Mistakes and Corrections

### Mistake 1: "INT8 saves memory so it must save energy"
**Reality**: Default INT8 trades 50% memory savings for 17–147% MORE energy. The mixed-precision decomposition overhead far outweighs memory benefits.

### Mistake 2: "4-bit is always better than 16-bit"
**Reality**: For models ≤3B, NF4 wastes 11–29% energy. De-quantization compute dominates memory savings when the model already fits comfortably in VRAM.

### Mistake 3: "Lower power draw = lower energy consumption"
**Reality**: NF4 draws 25% less power than FP16, but runs 42% slower. Net energy = power × time, so energy INCREASES despite lower power.

### Mistake 4: "Quantization choice is the main optimization lever"
**Reality**: Batch size has 10–50× more impact than quantization choice. Going from BS=1 to BS=8 saves 87.5% energy. The best quantization choice saves at most 35%.

### Mistake 5: "FP8 on Blackwell GPUs must be faster and more efficient"
**Reality**: Blackwell hardware supports native FP8 tensor cores, but the software stack is not ready. torchao nightly FP8 in eager mode incurs **+158–701% energy penalty** due to Python-side dispatch overhead and missing compiled C++ extensions. The torchao team has [confirmed](https://github.com/pytorch/ao/issues/4094) that native HF eager-mode is not their optimization target — use vLLM/SGLang with `torch.compile` instead.

### Mistake 6: "Nightly/dev builds are fine for benchmarking"
**Reality**: Nightly builds may lack compiled C++ extensions, causing silent fallback to unoptimized Python paths. Always verify your software stack versions and check for compilation warnings before running energy benchmarks.

## Priority Optimization Order

1. **Batch size** (−87 to −96% energy) — always optimize first
2. **Avoid FP8 eager mode** (−158 to −701% penalty) — switch to NF4/FP16 or use vLLM
3. **Avoid default INT8** (−17 to −147% penalty) — easy fix, one line of code
4. **Choose correct precision for model size** (−8 to −35% savings)
5. **Hardware selection** (varies) — right GPU for the workload
6. **Serving framework** (−10 to −20%) — vLLM/TGI vs raw HuggingFace
7. **Verify software stack** — ensure stable releases, not nightly builds with missing extensions
