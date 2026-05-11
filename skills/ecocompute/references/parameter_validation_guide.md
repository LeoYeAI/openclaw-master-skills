# Parameter Validation & Error Handling Guide — EcoCompute v2.0

## Overview

This guide provides comprehensive parameter validation rules, error handling patterns, and example request/response pairs for the EcoCompute Skill v2.0.

---

## Input Parameter Specifications

### 1. model_id (Required)

**Type**: String  
**Format**: Model name or Hugging Face Hub ID  
**Examples**: 
- `"mistralai/Mistral-7B-Instruct-v0.2"`
- `"Qwen/Qwen2-7B"`
- `"Mistral-7B"` (informal, will be normalized)

**Validation Rules**:
1. Must be non-empty string
2. Extract parameter count if present (e.g., "7B" → 7 billion)
3. If parameter count not explicit, look up from known models
4. Warn if model not in tested dataset (extrapolation required)

**Error Handling**:
```
❌ Invalid: model_id = ""
Response: "Error: model_id is required. Please specify a model name (e.g., 'Mistral-7B') or Hugging Face ID (e.g., 'mistralai/Mistral-7B-Instruct-v0.2')."

⚠️ Warning: model_id = "Llama-3-70B"
Response: "Warning: Llama-3-70B (70B params) not directly measured. Extrapolating from 7B model data. For accurate results, consider benchmarking with our measurement protocol."

✅ Valid: model_id = "mistralai/Mistral-7B-Instruct-v0.2"
```

---

### 2. hardware_platform (Required, with Default)

**Type**: String (enum)  
**Supported Values**: 
- Direct measurements: `rtx5090`, `rtx4090d`, `a800`
- Extrapolated: `a100`, `h100`, `rtx3090`, `v100`
- Aliases: `4090` → `rtx4090d`, `5090` → `rtx5090`

**Default**: `rtx4090d` (most common consumer GPU)

**Validation Rules**:
1. Normalize to lowercase
2. Map aliases to canonical names
3. Check if GPU is in direct measurement set
4. If extrapolated, note architecture similarity

**Error Handling**:
```
❌ Invalid: hardware_platform = "gtx1080"
Response: "Error: GPU 'gtx1080' not supported. Supported GPUs: RTX 5090, RTX 4090D, A800, A100 (extrapolated), H100 (extrapolated), RTX 3090 (extrapolated), V100 (extrapolated). For other GPUs, use our measurement protocol: [link]"

⚠️ Warning: hardware_platform = "h100"
Response: "Note: H100 data extrapolated from A800 (both Ampere/Hopper architecture). Expect ±10-15% variance. For production deployments, consider validation benchmarking."

✅ Valid: hardware_platform = "a800"
Response: "Using NVIDIA A800 (Ampere, 80GB HBM2e) — direct measurements available."
```

---

### 3. quantization (Optional)

**Type**: String (enum)  
**Options**: `fp16`, `bf16`, `fp32`, `nf4`, `int8_default`, `int8_pure`  
**Default**: `fp16` (safest baseline)

**Validation Rules**:
1. Must be from supported list
2. Check GPU compatibility (e.g., BF16 requires Ampere+)
3. Cross-validate with model size (warn if NF4 on ≤3B model)

**Error Handling**:
```
❌ Invalid: quantization = "int4"
Response: "Error: 'int4' not supported. Did you mean 'nf4' (4-bit NormalFloat)? Supported: fp16, bf16, fp32, nf4, int8_default, int8_pure."

⚠️ Warning: quantization = "bf16", hardware_platform = "rtx3090"
Response: "Warning: BF16 requires Ampere or newer (RTX 30-series uses GA102 which supports BF16, but with lower efficiency than Ampere). Consider FP16 for RTX 3090."

⚠️ Warning: quantization = "nf4", model_id = "Qwen2-1.5B"
Response: "Warning: NF4 on small models (≤3B) wastes 11-29% energy vs FP16. Recommendation: Use FP16 for Qwen2-1.5B (1.5B params) on this GPU."

✅ Valid: quantization = "int8_pure", model_id = "Mistral-7B", hardware_platform = "a800"
Response: "Using Pure INT8 (threshold=0.0) — saves ~5% energy vs FP16 on A800 for 7B models."
```

---

### 4. batch_size (Optional)

**Type**: Integer  
**Range**: 1-64  
**Preferred**: Powers of 2 (1, 2, 4, 8, 16, 32, 64)  
**Default**: 1 (conservative, but flagged for optimization)

**Validation Rules**:
1. Must be positive integer
2. Must be ≤64 (hardware/memory limits)
3. Warn if not power of 2 (suboptimal GPU utilization)
4. Flag BS=1 in production scenarios

**Error Handling**:
```
❌ Invalid: batch_size = 0
Response: "Error: batch_size must be ≥1. Did you mean batch_size=1?"

❌ Invalid: batch_size = 128
Response: "Error: batch_size=128 exceeds maximum supported (64). For larger batches, use vLLM with continuous batching."

⚠️ Warning: batch_size = 5
Response: "Warning: batch_size=5 is not a power of 2. GPU kernels are optimized for powers of 2. Consider BS=4 or BS=8 for better performance."

⚠️ Warning: batch_size = 1, use_case = "production API"
Response: "⚠️ Critical optimization opportunity: BS=1 in production wastes up to 95.7% energy. Recommendation: Use BS≥8 with request batching (vLLM continuous batching)."

✅ Valid: batch_size = 16
Response: "Using BS=16 — reduces energy by 87.5% vs BS=1."
```

---

### 5. sequence_length (Optional, v2.0)

**Type**: Integer  
**Range**: 128-4096 tokens  
**Default**: 512 (typical chat/API scenario)

**Validation Rules**:
1. Must be positive integer
2. Warn if exceeds model's context window
3. Note impact on memory and energy

**Error Handling**:
```
❌ Invalid: sequence_length = 0
Response: "Error: sequence_length must be ≥1. Typical values: 512 (chat), 1024 (documents), 2048 (long context)."

⚠️ Warning: sequence_length = 8192, model_id = "Mistral-7B"
Response: "Warning: sequence_length=8192 exceeds Mistral-7B's context window (8192 max with sliding window). Ensure your use case fits within model limits."

⚠️ Note: sequence_length = 2048
Response: "Note: 2048 tokens = 4× baseline (512). Energy per request will scale approximately linearly. Estimated energy: [X] J (vs [Y] J at 512 tokens)."

✅ Valid: sequence_length = 1024
Response: "Using 1024 input tokens (2× baseline). Energy estimates adjusted accordingly."
```

---

### 6. generation_length (Optional, v2.0)

**Type**: Integer  
**Range**: 1-2048 tokens  
**Default**: 256 (used in benchmark data)

**Validation Rules**:
1. Must be positive integer
2. Reasonable upper limit (2048 for most use cases)
3. Note direct proportionality to energy

**Error Handling**:
```
❌ Invalid: generation_length = -1
Response: "Error: generation_length must be ≥1. Typical values: 128 (short answers), 256 (default), 512 (detailed responses)."

⚠️ Warning: generation_length = 2048
Response: "Warning: Generating 2048 tokens = 8× baseline (256). Energy per request: [X] J (vs [Y] J at 256 tokens). Consider if this length is necessary for your use case."

✅ Valid: generation_length = 512
Response: "Generating 512 tokens (2× baseline). Energy per request: ~2× baseline measurement."
```

---

### 7. precision (Optional, v2.0)

**Type**: String (enum)  
**Options**: `fp32`, `bf16`, `fp16`, `tf32`  
**Default**: Inferred from `quantization` parameter

**Validation Rules**:
1. Check GPU architecture compatibility
2. Cross-validate with `quantization` (avoid conflicts)
3. Note if precision differs from quantization

**Error Handling**:
```
❌ Invalid: precision = "int8"
Response: "Error: 'int8' is a quantization method, not a precision. Use quantization='int8_pure' instead. Precision options: fp32, bf16, fp16, tf32."

⚠️ Warning: precision = "bf16", hardware_platform = "rtx4090d"
Response: "Note: RTX 4090D (Ada Lovelace) supports BF16, but FP16 may be faster for inference. BF16 is primarily beneficial for training."

⚠️ Conflict: precision = "fp32", quantization = "nf4"
Response: "Warning: Conflicting parameters. NF4 quantization uses FP16/BF16 for dequantization, not FP32. Using FP16 compute with NF4 weights."

✅ Valid: precision = "fp16"
Response: "Using FP16 precision (default for inference)."
```

---

## Cross-Parameter Validation

### Memory Capacity Check

**Rule**: Ensure model + KV cache + batch size fits in GPU VRAM

**Example**:
```python
model_size_gb = {
    "fp16": params_billions * 2,
    "nf4": params_billions * 0.5,
    "int8": params_billions * 1,
}

kv_cache_gb = batch_size * sequence_length * 0.0001  # Rough estimate

total_vram_needed = model_size_gb + kv_cache_gb

if total_vram_needed > gpu_vram_capacity:
    return "⚠️ Warning: Estimated VRAM usage ({total_vram_needed}GB) may exceed GPU capacity ({gpu_vram_capacity}GB). Consider: (1) reducing batch_size, (2) using quantization, or (3) reducing sequence_length."
```

**Error Example**:
```
⚠️ Warning: Mistral-7B FP16 (14GB) + BS=32 + seq_len=2048 (~18GB total) may exceed RTX 4090D capacity (24GB). Recommendation: Use BS=16 or NF4 quantization.
```

---

## Complete Example Request/Response Pairs

### Example 1: Minimal Input (Use Defaults)

**Request**:
```json
{
  "model_id": "Qwen/Qwen2-7B"
}
```

**Response**:
```
## Configuration (with defaults applied)
- Model: Qwen2-7B (7B parameters)
- GPU: RTX 4090D (default, Ada Lovelace, 24GB)
- Precision: FP16 (default)
- Batch size: 1 (default, ⚠️ consider increasing for production)
- Sequence length: 512 tokens → Generation: 256 tokens (defaults)

## ⚠️ Optimization Recommendations
1. **Increase batch_size**: BS=1 wastes 87-95% energy. Use BS≥8 for production.
2. **Specify hardware_platform**: Defaulting to RTX 4090D. Specify your actual GPU for accurate estimates.

## Performance Metrics (RTX 4090D, FP16, BS=1)
- Throughput: 42.3 tok/s (±1.2% std dev)
- Energy per 1k tokens: 892 J (±38 J)
- Energy per request: 228 J (for 256 token generation)

[... rest of standard output ...]
```

---

### Example 2: Full Parameter Specification

**Request**:
```json
{
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "hardware_platform": "a800",
  "quantization": "int8_pure",
  "batch_size": 32,
  "sequence_length": 1024,
  "generation_length": 512
}
```

**Response**:
```
## Validated Configuration
- Model: Mistral-7B-Instruct-v0.2 (7B parameters) ✅
- GPU: NVIDIA A800 (Ampere, 80GB HBM2e) ✅
- Precision: Pure INT8 (threshold=0.0) ✅
- Batch size: 32 ✅
- Sequence length: 1024 tokens → Generation: 512 tokens ✅

## Validation Notes
✅ All parameters valid
✅ VRAM check: ~8GB model + ~3GB KV cache = 11GB total (well within 80GB capacity)
✅ Pure INT8 on A800 saves ~5% energy vs FP16 (no paradox with threshold=0.0)
✅ BS=32 provides 93% energy reduction vs BS=1
⚠️ Sequence length 2× baseline (1024 vs 512) — energy estimates scaled accordingly
⚠️ Generation length 2× baseline (512 vs 256) — energy per request doubled

## Performance Metrics (Measured + Extrapolated)
- Throughput: 312 tok/s (±2.1% std dev, n=10)
  - Baseline (BS=16, 512→256): 284 tok/s measured
  - Scaling: BS=32 gives ~10% throughput increase
- Latency: 164 ms/request (BS=32, 512 tokens)
- GPU Utilization: ~85% (estimated)

## Energy & Efficiency
- Energy per 1k tokens: 327 J (±16 J, 95% CI)
  - Baseline (FP16, BS=16): 345 J measured
  - Pure INT8: -5% energy
  - BS=32: -8% energy vs BS=16
- Energy per request: 167 J (for 512 token generation)
  - 2× baseline due to 2× generation length
- Energy efficiency: 3.06 tokens/J
- Power draw: 298W average (285-312W range)

[... rest of output ...]

## 🔬 Measurement Transparency
- Hardware: NVIDIA A800, Driver 535.183.01
- Software: PyTorch 2.4.1, CUDA 12.1, transformers 4.47.0
- Method: NVML 10Hz power monitoring, n=10 runs, CV<2%
- Baseline: Mistral-7B Pure INT8 BS=16 measured directly on A800
- Extrapolations:
  - BS=32: Scaled from BS=16 data using batch_size_guide.md
  - Sequence length 1024: Linear scaling from 512 baseline
  - Generation length 512: Linear scaling from 256 baseline
- Confidence: HIGH (direct measurement with validated scaling laws)
```

---

### Example 3: Invalid Parameters (Error Handling)

**Request**:
```json
{
  "model_id": "",
  "hardware_platform": "gtx1080",
  "quantization": "int4",
  "batch_size": 128,
  "sequence_length": -1
}
```

**Response**:
```
## ❌ Parameter Validation Errors

1. **model_id**: Required parameter missing
   - Error: model_id cannot be empty
   - Fix: Specify a model name (e.g., "Mistral-7B") or Hugging Face ID

2. **hardware_platform**: Unsupported GPU
   - Error: 'gtx1080' not supported
   - Supported: RTX 5090, RTX 4090D, A800, A100, H100, RTX 3090, V100
   - Fix: Use a supported GPU or follow our measurement protocol for GTX 1080

3. **quantization**: Invalid value
   - Error: 'int4' not recognized
   - Did you mean: 'nf4' (4-bit NormalFloat)?
   - Supported: fp16, bf16, fp32, nf4, int8_default, int8_pure

4. **batch_size**: Out of range
   - Error: batch_size=128 exceeds maximum (64)
   - Fix: Use batch_size≤64, or use vLLM for larger batches

5. **sequence_length**: Invalid value
   - Error: sequence_length must be ≥1
   - Typical values: 512 (chat), 1024 (documents), 2048 (long context)

## 🔧 Suggested Corrected Request
```json
{
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "hardware_platform": "rtx4090d",
  "quantization": "nf4",
  "batch_size": 64,
  "sequence_length": 512
}
```

Please correct the errors and try again.
```

---

### Example 4: Warnings (Suboptimal but Valid)

**Request**:
```json
{
  "model_id": "Qwen/Qwen2-1.5B",
  "hardware_platform": "a800",
  "quantization": "nf4",
  "batch_size": 1
}
```

**Response**:
```
## Configuration (with warnings)
- Model: Qwen2-1.5B (1.5B parameters) ✅
- GPU: NVIDIA A800 (Ampere, 80GB HBM2e) ✅
- Precision: NF4 ⚠️
- Batch size: 1 ⚠️
- Sequence length: 512 tokens → Generation: 256 tokens (defaults)

## ⚠️ Critical Warnings

### 1. NF4 on Small Model (Energy Waste: +29%)
**Issue**: NF4 quantization on 1.5B model wastes 29% more energy than FP16
- Qwen2-1.5B FP16: 3GB VRAM (fits easily in 80GB A800)
- NF4 dequantization overhead: 29% energy penalty
- **Recommendation**: Use FP16 instead

**Impact**:
- Current (NF4): ~1,150 J/1k tokens
- Optimized (FP16): ~892 J/1k tokens
- Savings: 258 J/1k tokens (22% reduction)

### 2. Batch Size = 1 in Production (Energy Waste: up to 95.7%)
**Issue**: BS=1 has massive energy waste vs batching
- **Recommendation**: Use BS≥8 for production workloads

**Impact**:
- Current (BS=1): ~1,150 J/1k tokens
- Optimized (BS=16): ~143 J/1k tokens
- Savings: 1,007 J/1k tokens (87.5% reduction)

## 💡 Optimized Configuration
```json
{
  "model_id": "Qwen/Qwen2-1.5B",
  "hardware_platform": "a800",
  "quantization": "fp16",  // Changed from nf4
  "batch_size": 16         // Changed from 1
}
```

**Expected improvement**:
- Energy: 1,150 → 111 J/1k tokens (-90.3%)
- Monthly cost (500K requests): $48 → $4.60 (-90.4%)
- Carbon: 267 kgCO2 → 26 kgCO2 (-90.3%)

Would you like me to provide the optimized configuration analysis?
```

---

## Error Message Templates

### Template 1: Missing Required Parameter
```
❌ Error: {parameter_name} is required.
Fix: {suggestion}
Example: {example_value}
```

### Template 2: Invalid Value
```
❌ Error: '{value}' is not a valid {parameter_name}.
Supported values: {valid_options}
Did you mean: {closest_match}?
```

### Template 3: Out of Range
```
❌ Error: {parameter_name}={value} is out of valid range [{min}, {max}].
Fix: {suggestion}
Typical values: {examples}
```

### Template 4: Suboptimal Configuration
```
⚠️ Warning: {parameter_name}={value} may cause {issue}.
Impact: {quantified_impact}
Recommendation: {alternative}
Expected improvement: {benefit}
```

### Template 5: Extrapolation Notice
```
ℹ️ Note: {parameter} data extrapolated from {baseline}.
Method: {extrapolation_method}
Confidence: {confidence_level}
Recommendation: {validation_suggestion if confidence < HIGH}
```

---

## Best Practices for Parameter Handling

1. **Always validate before processing**: Check all parameters before running analysis
2. **Provide helpful error messages**: Include fix suggestions and examples
3. **Use warnings, not errors, for suboptimal choices**: Let users proceed but inform them
4. **Quantify impact**: Always show the cost of suboptimal choices in energy/cost/carbon
5. **Suggest alternatives**: Provide corrected configuration with expected improvements
6. **Be transparent about extrapolation**: Clearly state when data is measured vs extrapolated
7. **Link to documentation**: Point users to measurement protocol for unsupported configs

---

## Validation Checklist

Before providing recommendations, verify:

- [ ] model_id is valid and parameter count extracted
- [ ] hardware_platform is supported (or closest match identified)
- [ ] quantization is compatible with GPU architecture
- [ ] batch_size is within valid range and power of 2
- [ ] sequence_length and generation_length are reasonable
- [ ] VRAM capacity check passed
- [ ] Cross-parameter conflicts resolved
- [ ] Warnings issued for suboptimal choices
- [ ] Extrapolations clearly noted
- [ ] Measurement transparency provided

---

**Last Updated**: 2026-02-16  
**Version**: 2.0  
**Author**: Hongping Zhang
