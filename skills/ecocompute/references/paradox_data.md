# Paradox Data — EcoCompute Complete Measurements

> **Updated**: 2026-03-18 · **Version**: 2.3.0 · **Total measurements**: 113+

## RTX 5090 Five-Precision Benchmark (0.5B–7B)

Complete energy data across all five tested precisions on Blackwell (n=3, 10 iterations each).

| Model | Params | Precision | Throughput (tok/s) | Power (W) | Energy (J/1k tok) | ΔE vs FP16 | GPU Mem (GB) |
|-------|--------|-----------|-------------------|-----------|-------------------|------------|-------------|
| Qwen2.5-0.5B | 0.5B | FP16 | 83.01 | 122.5 | 1,472 | — | 1.62 |
| | | FP8† | 44.14 | 168.5 | 3,799 | **+158%** ⚠️ | 1.14 |
| | | NF4 | 47.32 | 108.2 | 2,283 | **+55%** ⚠️ | 0.92 |
| | | INT8-mix | 16.37 | 109.4 | 6,680 | **+354%** ⚠️ | 1.62 |
| | | INT8-pure | 29.68 | 108.4 | 3,654 | **+148%** ⚠️ | 1.62 |
| Qwen2.5-1.5B | 1.5B | FP16 | 68.91 | 160.5 | 2,310 | — | 3.53 |
| | | FP8† | 35.43 | 293.7 | 8,284 | **+259%** ⚠️ | 2.32 |
| | | NF4 | 41.92 | 130.5 | 3,121 | **+35%** ⚠️ | 1.68 |
| | | INT8-mix | 14.45 | 121.5 | 8,409 | **+264%** ⚠️ | 3.53 |
| | | INT8-pure | 25.35 | 120.3 | 4,753 | **+106%** ⚠️ | 3.53 |
| Qwen2.5-3B | 3.0B | FP16 | 54.80 | 193.6 | 3,504 | — | 6.53 |
| | | FP8† | 23.35 | 390.4 | 16,666 | **+376%** ⚠️ | 4.08 |
| | | NF4 | 36.42 | 153.2 | 4,204 | **+20%** ⚠️ | 2.89 |
| | | INT8-mix | 11.52 | 125.8 | 10,921 | **+212%** ⚠️ | 6.53 |
| | | INT8-pure | 20.95 | 130.7 | 6,235 | **+78%** ⚠️ | 6.53 |
| Qwen2.5-7B | 7.0B | FP16 | 69.97 | 374.9 | 5,331 | — | 15.22 |
| | | FP8† | 10.48 | 448.3 | 42,711 | **+701%** ⚠️ | 8.89 |
| | | NF4 | 39.92 | 189.0 | 4,718 | **−11.5%** ✅ | 6.19 |
| | | INT8-mix | 12.91 | 120.0 | 9,280 | **+74%** ⚠️ | 8.12 |
| | | INT8-pure | 23.56 | 137.4 | 5,822 | **+9.2%** ⚠️ | 8.12 |

{\scriptsize †Reflects unoptimized Python fallback in torchao nightly build; not indicative of peak hardware potential.}

### Energy Efficiency Ranking (RTX 5090, all sizes)

**Best to worst**: NF4 > INT8-pure > FP16 baseline > INT8-mixed > FP8

---

## Paradox 1: NF4 Small-Model Energy Penalty (RTX 5090 Blackwell)

NF4 quantization **increases** energy consumption for models ≤3B parameters.

### RTX 5090 — FP16 vs NF4 (earlier study)

| Model | Params | Precision | Throughput (tok/s) | Power (W) | Energy (J/1k tok) | Δ vs FP16 |
|-------|--------|-----------|-------------------|-----------|-------------------|----------|
| Qwen2-1.5B | 1.5B | FP16 | 71.45 ± 0.80 | 172.30 | 2,411 | — |
| Qwen2-1.5B | 1.5B | NF4 | 41.57 ± 0.29 | 129.83 | 3,123 | **+29.4%** ⚠️ |
| Phi-3-mini | 3.8B | FP16 | 43.47 ± 0.11 | 213.35 | 4,908 | — |
| Phi-3-mini | 3.8B | NF4 | 32.08 ± 0.13 | 175.85 | 5,483 | **+11.7%** ⚠️ |

**Root Cause — De-quantization Tax:**
- Small models fit in VRAM at FP16 → memory bandwidth is NOT the bottleneck
- NF4 adds de-quantization (NF4→FP16) at every linear layer
- Extra compute overhead DOMINATES the small memory savings
- Formula: E_ratio = (T_NF4/T_FP16) × (P_NF4/P_FP16) ≈ 1.72 × 0.75 ≈ 1.29 (matches +29.4%)

**Crossover Point:** ~4–5B parameters (confirmed at 7B on RTX 5090: NF4 saves 11.5%). Below ~5B, FP16 is always more efficient.

### RTX 4090D — NF4 Saves Energy for Larger Models

| Model | Params | Precision | Throughput (tok/s) | Energy (J/1k tok) | Δ vs FP16 |
|-------|--------|-----------|-------------------|-------------------|-----------|
| Yi-1.5-6B | 6B | FP16 | 34.72 ± 0.18 | 4,716 ± 119 | — |
| Yi-1.5-6B | 6B | NF4 | 36.42 ± 0.27 | 3,333 ± 25 | **−29.3%** ✅ |
| Mistral-7B | 7B | FP16 | 29.06 ± 0.10 | 5,661 ± 143 | — |
| Mistral-7B | 7B | NF4 | 32.29 ± 0.02 | 3,707 ± 15 | **−34.5%** ✅ |
| Phi-3-mini | 3.8B | FP16 | 57.62 ± 0.48 | 2,775 ± 48 | — |
| Phi-3-mini | 3.8B | NF4 | 42.16 ± 0.25 | 3,076 ± 20 | **+10.8%** ⚠️ |
| Qwen2.5-7B | 7B | FP16 | 28.37 ± 0.39 | 5,649 ± 83 | — |
| Qwen2.5-7B | 7B | NF4 | 34.29 ± 0.24 | 5,191 ± 37 | **−8.1%** ✅ |

---

## Paradox 2: bitsandbytes INT8 Energy Overhead

Default `LLM.int8()` (threshold=6.0) **increases** energy consumption by 17–147%.

### RTX 4090D — Default INT8 vs FP16 vs Pure INT8

| Model | Precision | Throughput (tok/s) | Energy (J/1k tok) | Δ vs FP16 | Δ vs Default INT8 |
|-------|-----------|-------------------|-------------------|-----------|-------------------|
| **Yi-1.5-6B** | FP16 | 34.72 ± 0.18 | 4,716 ± 119 | — | — |
| Yi-1.5-6B | INT8 Default | 8.42 ± 0.03 | 6,258 ± 78 | **+32.7%** ⚠️ | — |
| Yi-1.5-6B | INT8 Pure (t=0.0) | 15.47 ± 0.08 | 4,568 | **−3.1%** ✅ | **−34.2%** ✅ |
| **Mistral-7B** | FP16 | 29.06 ± 0.10 | 5,661 ± 143 | — | — |
| Mistral-7B | INT8 Default | 7.88 ± 0.03 | 7,401 ± 115 | **+30.7%** ⚠️ | — |
| Mistral-7B | INT8 Pure (t=0.0) | 14.15 ± 0.23 | 5,212 | **−7.9%** ✅ | **−36.9%** ✅ |
| **Average** | — | — | — | **+31.7%** ⚠️ | — |
| **Average (Pure)** | — | — | — | **−5.5%** ✅ | **−35.6%** ✅ |

### A800 — INT8 Overhead Is Even Worse on Datacenter GPUs

| Model | BS | Precision | Throughput (tok/s) | Energy (J/1k tok) | Δ vs FP16 |
|-------|---|-----------|-------------------|-------------------|-----------|
| Mistral-7B | 1 | FP16 | 36.18 | 4,334 | — |
| Mistral-7B | 1 | INT8 Default | 9.87 | 9,608 | **+122%** ⚠️ |
| Mistral-7B | 1 | INT8 Pure | 18.09 | 5,781 | +33% |
| Mistral-7B | 4 | FP16 | 145.35 | 1,100 | — |
| Mistral-7B | 4 | INT8 Default | 35.91 | 2,718 | **+147%** ⚠️ |
| Mistral-7B | 4 | INT8 Pure | 72.96 | 1,580 | +44% |
| Mistral-7B | 8 | FP16 | 290.59 | 628 | — |
| Mistral-7B | 8 | INT8 Default | 69.88 | 1,417 | **+126%** ⚠️ |
| Mistral-7B | 8 | INT8 Pure | 144.32 | 827 | +32% |

**Root Cause — Mixed-Precision Decomposition:**
1. `LLM.int8()` with `threshold=6.0` detects "outlier" features (magnitude > 6.0)
2. Outlier features are extracted and computed in FP16
3. Remaining features computed in INT8
4. Results merged back → continuous INT8↔FP16 type conversion at every linear layer
5. This causes 72–76% throughput loss, which dominates the 25% power reduction

**Ablation Proof:**
Setting `llm_int8_threshold=0.0` disables the decomposition entirely:
- All features processed in INT8 (no outlier extraction)
- Throughput recovery: **+79–98%** vs default INT8
- Energy reduction: **−34–42%** vs default INT8
- Net vs FP16: **−3% to −8%** energy savings (RTX 4090D), **+32–44%** penalty still on A800

**Code to reproduce:**
```python
# Default INT8 (ENERGY WASTEFUL — avoid this)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,
    # llm_int8_threshold defaults to 6.0
)

# Pure INT8 (ENERGY EFFICIENT — use this instead)
from transformers import BitsAndBytesConfig
quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=0.0,  # ← This one line saves 34–42% energy
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=quantization_config,
)
```

---

## Paradox 3: BS=1 Waste (A800)

Single-request inference wastes up to 95.7% of available energy efficiency.

See `batch_size_guide.md` for complete data.

---

---

## Paradox 4: FP8 Software Immaturity (RTX 5090 Blackwell)

FP8 (torchao `Float8WeightOnlyConfig`) is the **worst method tested** across all model sizes on Blackwell.

### FP8 Energy Penalty Escalation

| Model | Params | FP8 Energy (J/1k) | FP16 Energy (J/1k) | ΔE% | FP8 Power (W) | FP8 Throughput (tok/s) |
|-------|--------|-------------------|--------------------|----|---------------|----------------------|
| Qwen2.5-0.5B | 0.5B | 3,799 | 1,472 | **+158%** | 168.5 | 44.14 |
| Qwen2.5-1.5B | 1.5B | 8,284 | 2,310 | **+259%** | 293.7 | 35.43 |
| Qwen2.5-3B | 3.0B | 16,666 | 3,504 | **+376%** | 390.4 | 23.35 |
| Qwen2.5-7B | 7.0B | 42,711 | 5,331 | **+701%** | 448.3 | 10.48 |

**Root Cause — Python-Side Dispatch Overhead:**
1. torchao nightly build (0.17.0.dev) C++ extensions are incompatible with nightly PyTorch, forcing unoptimized Python fallback
2. Weight-only FP8 quantization lacks fused inference kernels
3. GPU enters **high-power idle state** waiting for Python dispatch → massive energy waste
4. Power draw escalates toward TDP (448W at 7B vs 575W TDP) while throughput collapses

**Official Context:**
torchao maintainers have confirmed ([Issue #4094](https://github.com/pytorch/ao/issues/4094)):
- "TorchAO does not aim to make models more power efficient"
- "Accelerating native HF checkpoints is not a priority"
- Intended path: vLLM/SGLang with `torch.compile`

**Recommendation:** NEVER use FP8 via torchao eager mode. If FP8 is required, use:
- vLLM/SGLang with `torch.compile`
- NVIDIA Transformer Engine
- Wait for stable torchao release with compiled C++ extensions

---

## Summary Decision Matrix

| Model Size | GPU VRAM | Best Precision | Avoid | Notes |
|-----------|----------|---------------|-------|-------|
| ≤3B | Any | **FP16** | NF4 (+11–55%), FP8 (+158–376%) | No memory pressure, all quantization adds overhead |
| 3–5B | Any | **FP16 preferred** | FP8 (always), INT8-mixed | Near break-even zone for NF4 |
| ≥5B | ≤24GB | **NF4** | FP8, INT8-mixed | NF4 saves 11.5% at 7B, memory savings dominate |
| ≥5B | ≥80GB | **FP16 or Pure INT8** | FP8, INT8-mixed | No memory pressure |
| Any | Any | — | FP8 eager mode (always) | +158–701% penalty in current software |
| Any | Any | — | INT8 default (always) | Always set threshold=0.0 if using INT8 |

## Quality Metrics

- RTX 4090D / A800: n=10 runs per configuration
- RTX 5090 five-precision: n=3 runs (quick validation), 10 iterations each → 113+ total iterations
- Coefficient of Variation: 0.3–1.7% (throughput), <5% (power)
- Cross-model consistency: ±3.5%
- Thermal stabilization: 30s between model loads
- Warmup: 3 runs discarded
- Cross-generational: Ada Lovelace N_crit ≈ 4.2B (extrapolated), Blackwell N_crit ≈ 4–5B (confirmed at 7B)
