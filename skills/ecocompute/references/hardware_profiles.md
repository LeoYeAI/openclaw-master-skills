# Hardware Profiles — EcoCompute Reference Data

## GPU Specifications

### NVIDIA RTX 5090 (Blackwell)
- **Architecture**: Blackwell (SM 100/120)
- **VRAM**: 32 GB GDDR7
- **Memory Bandwidth**: 1,792 GB/s
- **Tensor Cores**: 5th Generation (native FP8 support)
- **TDP**: 575W
- **Idle Power**: ~22W
- **Use Case**: Consumer flagship, single-GPU inference
- **Software (five-precision study)**: PyTorch 2.12.0.dev20260315+cu128, CUDA 12.8, transformers 4.50.0, bitsandbytes 0.45.3, torchao 0.17.0.dev20260316+cu128, Driver 580.105.08
- **Software (earlier NF4/FP16 study)**: PyTorch 2.6.0, CUDA 12.6, transformers 4.48.0, bitsandbytes 0.45.3, Driver 570.86.15

**Tested Models (five-precision)**: Qwen2.5-0.5B, Qwen2.5-1.5B, Qwen2.5-3B, Qwen2.5-7B (FP16, FP8, NF4, INT8-mixed, INT8-pure)
**Tested Models (earlier)**: Qwen2-1.5B, Phi-3-mini-3.8B (FP16, NF4)

**Key Findings**:
- NF4 wastes 20–55% energy on models ≤3B; saves 11.5% at 7B (crossover confirmed at ~5B)
- FP8 (torchao eager) is worst method: +158% to +701% penalty (escalating with model size)
- Energy ranking: NF4 > INT8-pure > FP16 > INT8-mixed > FP8
- torchao FP8 C++ extensions disabled in nightly build → Python fallback causes high-power idle state

### NVIDIA RTX 4090D (Ada Lovelace)
- **Architecture**: Ada Lovelace (SM 89)
- **VRAM**: 24 GB GDDR6X
- **Memory Bandwidth**: 1,008 GB/s
- **Tensor Cores**: 4th Generation
- **TDP**: 425W
- **Idle Power**: ~17W
- **Use Case**: Consumer high-end, most common enthusiast GPU
- **Software**: PyTorch 2.4.1, CUDA 12.1, transformers 4.47.0, bitsandbytes 0.45.0, Driver 560.35.03

**Tested Models**: TinyLlama-1.1B, Yi-1.5-6B, Mistral-7B, Phi-3-mini, Qwen2.5-3B, Qwen2.5-7B (FP16, NF4, INT8 default, INT8 pure)

**Key Finding**: Default INT8 increases energy by 17–33%. Pure INT8 (threshold=0.0) saves 3–8% vs FP16.

### NVIDIA A800 (Ampere)
- **Architecture**: Ampere (SM 80)
- **VRAM**: 80 GB HBM2e
- **Memory Bandwidth**: 2,039 GB/s
- **Tensor Cores**: 3rd Generation
- **TDP**: 400W
- **Idle Power**: ~65W
- **Use Case**: Datacenter, batch processing, production inference
- **Software**: PyTorch 2.4.1, CUDA 12.1, transformers 4.47.0, bitsandbytes 0.45.0, Driver 535.183.01

**Tested Models**: Mistral-7B (FP16, INT8 default, INT8 pure, batch sizes 1–64)

**Key Finding**: Default INT8 has 122–147% energy penalty. Batch size 64 reduces energy per request by 95.7% vs BS=1.

## Energy Measurement Protocol

```
Tool:           NVIDIA Management Library (NVML) via pynvml
Sampling:       10 Hz (100ms polling interval)
Metric:         GPU board power (watts), excluding CPU/DRAM
Idle baseline:  Subtracted per-GPU (measured before each experiment)
Warmup:         3 runs discarded before measurement
Stabilization:  30 seconds between model loads
Measured runs:  10 per configuration
Generation:     Greedy decoding (do_sample=False), max_new_tokens=256
Quality gate:   CV < 2% (throughput), CV < 5% (power)
```

## Energy Calculation

```
Energy per token (J/tok) = Average Power (W) × Generation Time (s) / Tokens Generated
Energy per 1k tokens (J) = Energy per token × 1000
Carbon per 1k tokens (gCO2) = Energy (kWh) × Grid Intensity (gCO2/kWh)
```

## Grid Carbon Intensity Reference

| Region | gCO2/kWh | Source |
|--------|----------|--------|
| US Average | 390 | EPA eGRID 2024 |
| China Average | 555 | IEA 2024 |
| EU Average | 230 | EEA 2024 |
| France | 56 | Low carbon (nuclear) |
| Norway | 8 | Nearly 100% hydro |
| India | 632 | IEA 2024 |

## Electricity Cost Reference

| Region | $/kWh | Note |
|--------|-------|------|
| US Average | 0.12 | EIA residential 2024 |
| US Cloud (spot) | 0.03–0.06 | AWS/GCP/Azure |
| China | 0.085 | Industrial rate |
| EU Average | 0.22 | Eurostat 2024 |
| AutoDL (China) | ~0.04 | Cloud GPU rental |
