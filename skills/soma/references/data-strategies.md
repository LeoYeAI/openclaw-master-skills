# SOMA Data Strategies

> Data strategies: https://docs.soma.org/guides/data-strategies
> Datasets: https://docs.soma.org/concepts/submitting
> Quickstart patterns: `quickstart-patterns.md`

## Think Like a Curator, Not a Pipeline

The default approach — stream The Stack v2, filter, submit — is what everyone does. It works. It's also the fastest way to become indistinguishable from every other submitter on the network.

The network's collective intelligence depends on **diversity**. Every byte of novel, high-quality data you submit teaches the network something new. The submitter who discovers an underserved domain and curates excellent data for it contributes more to the network (and earns more) than 100 submitters running identical Stack v2 pipelines in crowded regions.

Your edge as a data submitter is **what data you choose and how you curate it**, not how fast your pipeline runs.

## Recommended Datasets

Start here, but don't stop here:

| Dataset | Type | Best for | Strategic note |
|---------|------|----------|----------------|
| **The Stack v2** | Source code | General programming targets | Baseline. Filter by language to specialize — don't submit everything |
| **StarCoderData** | Source code | Curated, high-quality code | Higher quality filtering than raw Stack v2. Better signal-to-noise |
| **FineWeb-Edu** | Web text | Educational/textual targets | Natural language grounding. Technical documentation is gold |
| **SWE-bench** | Code patches | Software engineering | Real GitHub issues paired with resolving changes. Unique signal |
| **Custom datasets** | Varies | Niche domain specialization | Your biggest competitive moat. See Novel Data Sources below |

**Key insight**: Data is chunked to 1024 bytes during processing. Documents exceeding the context window are split into independent sequences without cross-sequence visibility. Shorter, self-contained passages — functions, docstrings, paragraphs — are more effective training material than raw file dumps.

## Customizing Your Data Source

The submitter interface requires yielding bytes objects under a 1 MB submission maximum. You can plug in any data source:

```python
def my_data_source():
    """Yield data as UTF-8 bytes from any source."""
    from datasets import load_dataset
    ds = load_dataset(
        "HuggingFaceFW/fineweb-edu",
        split="train",
        streaming=True,
    ).shuffle(buffer_size=100_000)

    for row in ds:
        text = row.get("text", "")
        if not text.strip():
            continue
        data = text.encode("utf-8")
        if len(data) > 10_000:
            continue
        yield data
```

This pattern works with any HuggingFace dataset, local files, API responses, or generated content. The key constraint: yield raw bytes, keep each chunk under ~10KB for best results.

## Smart Filtering with Embedding Models

### The problem

Most files from The Stack v2 aren't relevant to any given target. Without filtering, you waste GPU cycles scoring data that will never hit.

### The solution

Use a small embedding model (~80MB) to pre-filter before expensive scoring:

```python
from sentence_transformers import SentenceTransformer
import numpy as np

filter_model = SentenceTransformer("all-MiniLM-L6-v2")
target_embedding = np.array(target.embedding)

def make_filtered_batches(batch_size: int, similarity_threshold: float = 0.3):
    ds = load_dataset(
        "bigcode/the-stack-v2-dedup",
        split="train",
        streaming=True,
    ).shuffle(buffer_size=100_000)

    for row in ds:
        content = row["content"]
        file_embedding = filter_model.encode(content[:512])
        similarity = np.dot(file_embedding, target_embedding) / (
            np.linalg.norm(file_embedding) * np.linalg.norm(target_embedding)
        )

        if similarity < similarity_threshold:
            continue

        # This data is likely relevant — worth scoring with full models
        yield content.encode("utf-8")
```

The small model adds minimal latency while dramatically reducing irrelevant scoring calls. Tune `similarity_threshold` based on your hit rate — lower is more permissive, higher is more selective.

## LLM Distillation for Synthetic Data

Generate high-quality synthetic data by distilling large language model knowledge. This is especially effective for **sparse regions** of embedding space where organic data is scarce.

### Implementation with vLLM

```python
from vllm import LLM, SamplingParams

llm = LLM(model="Qwen/Qwen2.5-Coder-32B-Instruct", tensor_parallel_size=2)

prompts = [
    "Write a Python function that implements a binary search tree with insert, delete, and search operations.",
    "Write a Rust function that parses a CSV file and returns a Vec of structs.",
    "Write a Go HTTP middleware that implements rate limiting with a token bucket.",
    "Write a TypeScript function that validates and transforms a JSON schema.",
]

params = SamplingParams(temperature=0.8, max_tokens=1024)
outputs = llm.generate(prompts, params)

for output in outputs:
    generated = output.outputs[0].text
    data = generated.encode("utf-8")
    # Feed into submission pipeline or training pipeline
```

### The Distillation Pipeline

1. **Analyze targets**: Query `get_targets(status="open")`. Look at target embeddings and identify which domains they correspond to.
2. **Craft diverse prompts**: Cover the target domain from multiple angles. Algorithms, patterns, edge cases, documentation, tests.
3. **Generate with temperature variation**: Use 0.7–1.0 to get diverse outputs. Lower temperatures produce more predictable code; higher produces more creative examples.
4. **Score and submit**: Run generated data through the normal scoring pipeline. Submit winners.

### Tips

- Vary prompts across sub-domains: algorithms, web, systems, data science, DevOps, infrastructure
- Generate 20-50 candidates per target — most won't hit, but the ones that do are valuable
- Iterate on near-threshold candidates by generating additional related content
- Experiment with different generator models (Qwen, Llama, Mistral) — they produce different output distributions
- The best synthetic data targets domains that are **underrepresented** in standard datasets

## Novel Data Sources — Think Beyond the Obvious

The network rewards novelty. If everyone submits Python code from The Stack, the network gets saturated on Python and the marginal value of more Python drops. Meanwhile, domains with zero coverage represent huge opportunities.

**GitHub beyond source code:**
- READMEs, documentation, and wikis
- Issue discussions and pull request conversations
- CI/CD configurations (GitHub Actions YAML, Jenkins, CircleCI)
- Dockerfiles and docker-compose files
- Infrastructure-as-code (Terraform, Pulumi, CloudFormation)

**Academic and scientific:**
- ArXiv papers (LaTeX source)
- PubMed abstracts and medical literature
- Mathematical proof databases
- Chemistry notation (SMILES strings, molecular data)
- Bioinformatics sequences and annotations

**Web infrastructure:**
- RFCs and internet standards
- W3C specifications
- Man pages and command documentation
- API documentation (OpenAPI/Swagger specs)
- Stack Overflow Q&A pairs

**Niche programming:**
- Smart contracts (Solidity, Move, Vyper)
- Hardware description languages (VHDL, Verilog, SystemVerilog)
- Shader code (GLSL, HLSL, Metal Shading Language)
- Build systems (Makefiles, CMake, Bazel BUILD files, Nix expressions)
- Database query languages (SQL dialects, Cypher, SPARQL)
- Configuration languages (Dhall, Jsonnet, CUE)

**Byte-native and structured formats:**
- SVG files (vector graphics as XML/text)
- MIDI files (music as byte sequences)
- CSV/TSV tabular data
- GeoJSON and mapping data
- Protocol buffer definitions (.proto files)
- Log files (structured and semi-structured)

**Cross-domain pairings (high value):**
- Code paired with its documentation
- Test files paired with implementation
- API specifications paired with client examples
- Bug reports paired with fixing commits
- Type definitions paired with usage

**The creative question to always ask**: What data exists in the world that no one else is submitting? The answer is your competitive advantage.

## Data Quality Over Data Quantity

One perfectly curated, high-quality submission in an underserved niche is worth more than 1000 generic code files in a saturated region. Quality signals:

- **Information density**: Does every byte carry signal? Remove boilerplate, license headers, generated code that's mostly whitespace.
- **Self-contained**: Does the 1024-byte window capture a complete concept? A full function is better than a random slice of a 10,000-line file.
- **Domain-representative**: Does this data genuinely represent the domain you're targeting? A well-written Rust function teaches the network about Rust better than a trivial "hello world."
- **Novel structure**: Does this data contain patterns the network hasn't seen? Unusual control flow, rare API usage, unconventional formatting — these teach the network new things.

## Volume Strategy

For sustained earnings, automate your submitter to run continuously:

- Deploy as a 24/7 cron job: `uv run modal deploy src/quickstart/submitter.py`
- Use streaming datasets to avoid loading everything into memory
- Shuffle with a large buffer (100k+) to avoid sequential bias
- Track which data ranges you've covered to avoid re-processing
- Deploy both training and submitter together — your model earns commission from other submitters' data, and your submitter earns rewards against all models including your own

## The Feedback Loop

The most underused strategy: learning from your own results.

After each epoch:
1. Check which of your submissions won rewards (`get_targets(status="claimable")`)
2. Analyze the winning data — what domain was it? What made it score well?
3. Analyze your misses — why did the distance exceed the threshold?
4. Double down on what works. Adjust or abandon what doesn't.

This feedback loop is your **private signal** about what the network values. Every other submitter has to guess. You have data.
