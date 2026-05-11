# Batch Size Optimization Guide — EcoCompute Reference Data

## Key Finding

Batch size is the **single largest energy optimization lever** for LLM inference. Going from BS=1 to BS=64 reduces energy per request by **95.7%** on NVIDIA A800 with Mistral-7B Pure INT8.

## Complete Batch Size Data (A800 + Mistral-7B Pure INT8)

| Batch Size | Throughput (tok/s) | Energy/Request (J) | Energy/1k tok (J) | GPU Util (%) | Δ Energy vs BS=1 | Throughput Scaling |
|-----------|-------------------|-------------------|-------------------|-------------|-----------------|-------------------|
| 1 | 18.09 | 14.16 | 5,781 | ~45% | — | 1.0× |
| 2 | 36.48 | 7.57 | 3,091 | ~58% | **−46.5%** | 2.0× |
| 4 | 72.96 | 3.79 | 1,580 | ~72% | **−73.3%** | 4.0× |
| 8 | 144.32 | 1.77 | 827 | ~85% | **−87.5%** | 8.0× |
| 16 | 283.71 | 0.98 | 452 | ~92% | **−93.1%** | 15.7× |
| 32 | 548.20 | 0.72 | 295 | ~95% | **−94.9%** | 30.3× |
| 64 | 1,003.50 | 0.61 | 248 | ~97% | **−95.7%** | 55.5× |

## Why Batch Size Matters So Much

### At BS=1 (Latency-Bound)
- GPU Tensor Cores are **mostly idle** (~45% utilization)
- Kernel launch overhead dominates each operation
- Memory latency (not bandwidth) is the bottleneck
- Fixed overhead per request is NOT amortized
- Result: **14.16 J per request** — massive waste

### At BS≥8 (Compute-Bound)
- GPU Tensor Cores are **fully utilized** (85%+ utilization)
- Fixed overhead amortized across N requests
- Memory access patterns become bandwidth-efficient (coalesced)
- Near-linear throughput scaling up to BS=16
- Result: **1.77 J per request** at BS=8 — 87.5% reduction

### Diminishing Returns Above BS=32
- Throughput still scales but sub-linearly
- Energy savings plateau: BS=32 (−94.9%) vs BS=64 (−95.7%) — only 0.8% difference
- VRAM becomes the constraint at very large batch sizes
- Recommendation: **BS=8–32 is the sweet spot** for most deployments

## Scaling Law

Energy per request approximately follows an inverse relationship:

```
Energy/request ≈ C / BS^α

Where:
  C ≈ 14.16 J (BS=1 baseline)
  α ≈ 0.78 (empirically fitted)
```

This holds well from BS=1 to BS=32, with slight flattening at BS=64.

## Practical Recommendations

### Production API Server
- **Minimum**: BS=8 (−87.5% energy, 8× throughput)
- **Optimal**: BS=16–32 (−93 to −95% energy)
- **Implementation**: Use vLLM, TGI, or similar continuous batching framework
- **Trade-off**: Slight increase in per-request latency at higher BS

### Interactive Chat Application
- BS=1 is acceptable for real-time response
- **Optimization**: Batch concurrent users (even 2–4 users batched saves 46–73%)
- Consider request queuing with 50–100ms window to accumulate batch

### Batch Processing / Offline Jobs
- **Always use BS=32–64** (−95% energy)
- No latency constraint → maximize throughput
- Example: Summarizing 10,000 documents → use BS=64

### VRAM Budget Calculator

Approximate VRAM usage for Mistral-7B Pure INT8:
```
VRAM ≈ Model Weights + KV Cache × BS + Activation Memory × BS

Model weights (INT8): ~7 GB
KV cache per request: ~0.5 GB (at 256 tokens)
Activation memory: ~0.2 GB per request

BS=1:  ~7.7 GB
BS=8:  ~12.6 GB
BS=16: ~18.2 GB
BS=32: ~29.4 GB
BS=64: ~51.8 GB  (requires ≥80 GB VRAM → A800/H100 only)
```

## Cost Impact Example

**Scenario**: 1 million requests/month, Mistral-7B Pure INT8, A800

| Batch Size | Energy/month (kWh) | Cost (@ $0.04/kWh) | Carbon (kgCO2, China grid) | Δ vs BS=1 |
|-----------|-------------------|--------------------|--------------------------|---------| 
| 1 | 3,933 | $157 | 2,183 | — |
| 8 | 492 | $20 | 273 | **−87.5%** |
| 32 | 200 | $8 | 111 | **−94.9%** |
| 64 | 169 | $7 | 94 | **−95.7%** |

**BS=1 → BS=32 saves $149/month and 2,072 kgCO2/month** for just one model on one GPU.

## Code Examples

### vLLM (Recommended for Production)
```python
from vllm import LLM, SamplingParams

# vLLM handles continuous batching automatically
llm = LLM(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    quantization="bitsandbytes",
    load_format="bitsandbytes",
    max_num_batched_tokens=8192,  # allows up to ~32 concurrent requests
)

# Submit multiple requests — vLLM batches them automatically
sampling_params = SamplingParams(max_tokens=256)
outputs = llm.generate(prompts, sampling_params)
```

### Manual Batching (HuggingFace)
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=0.0,  # Pure INT8 — critical for energy efficiency
)

model = AutoModelForCausalLM.from_pretrained(model_name, quantization_config=config)
tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
tokenizer.pad_token = tokenizer.eos_token

# Batch multiple prompts
prompts = ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4"]
inputs = tokenizer(prompts, return_tensors="pt", padding=True).to("cuda")
outputs = model.generate(**inputs, max_new_tokens=256)
```
