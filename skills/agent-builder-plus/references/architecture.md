# Agent Architecture Patterns

Based on "LLM Powered Autonomous Agents" (Weng, 2023) and modern best practices.

## Core Components

An autonomous agent system generally consists of a central LLM controller augmented with three key capabilities:

1.  **Planning** (Brain)
    *   **Subgoal Decomposition**: Breaking complex tasks into manageable steps (e.g., Chain of Thought, Tree of Thoughts).
    *   **Reflection**: Criticizing and refining plans based on past actions (e.g., ReAct, Reflexion).
2.  **Memory** (Context)
    *   **Short-term**: In-context learning (limited by context window).
    *   **Long-term**: Vector stores (RAG) or external databases for efficient retention and retrieval.
3.  **Tool Use** (Action)
    *   Calling external APIs for data (Search, Calendar) or capabilities (Code execution, Math).

## 1. Planning

### Decomposition Techniques
*   **Chain of Thought (CoT)**: "Think step by step."
*   **Tree of Thoughts (ToT)**: Explore multiple reasoning paths at each step.
*   **LLM+P**: Offloading long-horizon planning to classical planners (e.g., PDDL).

### Self-Reflection
*   **ReAct**: Interleaving `Thought`, `Action`, and `Observation`.
*   **Reflexion**: Using a dynamic memory of past failures to induce self-improvement.
*   **Chain of Hindsight**: Fine-tuning on a sequence of outputs with feedback to improve future generations.

## 2. Memory

### Types
*   **Sensory**: Raw input embeddings.
*   **Short-Term (Working)**: The current prompt context.
*   **Long-Term**: External storage (Vector DBs like Pinecone, Weaviate, Milvus).

### Retrieval (MIPS)
Using Maximum Inner Product Search to find relevant long-term memories. Algorithms include LSH, ANNOY, HNSW, and FAISS.

## 3. Tool Use

### Patterns
*   **MRKL**: Modular Reasoning, Knowledge and Language. A router sends queries to expert modules (calculators, weather APIs).
*   **Toolformer**: Fine-tuning LMs to self-supervise API calls.
*   **Function Calling**: Native LLM capabilities to output structured JSON for API execution (e.g., OpenAI functions).

## Common Architectures

*   **Single Agent**: One LLM loop handling all steps.
*   **Multi-Agent**: Specialized agents (Planner, Executor, Critic) working together (e.g., AutoGPT, BabyAGI, Generative Agents).
