# Advanced RAG Techniques

## Overview

Advanced RAG techniques to improve accuracy when basic RAG (chunk → embed → retrieve → generate) isn't good enough.

---

## 1. Late Chunking

### Concept

Thay vì chunk trước rồi embed từng chunk (mất context), Late Chunking embed **toàn bộ document** trước, sau đó mới chia thành chunks từ embedding output.

```
Traditional: Document → Chunk → Embed each chunk (mỗi chunk mất context)
Late Chunking: Document → Embed full doc → Pool embeddings theo chunk boundaries
```

### Why Is It Better?

- Mỗi token "nhìn thấy" toàn bộ document khi encode (full attention)
- Chunk embedding giữ được context từ surrounding text
- Đặc biệt hiệu quả với pronoun resolution ("nó", "điều này")

### Code Example

```python
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

def late_chunking_embed(
    document: str,
    chunk_boundaries: list[tuple[int, int]],  # [(start_char, end_char), ...]
    model_name: str = "BAAI/bge-m3"
) -> list[np.ndarray]:
    """
    Late Chunking: embed full document, then pool by chunk boundaries.
    
    Args:
        document: Full document text
        chunk_boundaries: List of (start_char, end_char) for each chunk
        model_name: HuggingFace model name
    
    Returns:
        List of chunk embeddings
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    
    # Tokenize full document (keep offset mapping)
    encoded = tokenizer(
        document,
        return_tensors="pt",
        return_offsets_mapping=True,
        max_length=8192,
        truncation=True
    )
    offsets = encoded.pop("offset_mapping")[0]  # (seq_len, 2)
    
    # Encode full document — each token sees the full context
    with torch.no_grad():
        outputs = model(**encoded)
    token_embeddings = outputs.last_hidden_state[0]  # (seq_len, dim)
    
    # Map chunk boundaries → token indices
    chunk_embeddings = []
    for char_start, char_end in chunk_boundaries:
        # Find tokens belonging to this chunk
        token_mask = []
        for i, (tok_start, tok_end) in enumerate(offsets):
            if tok_end > char_start and tok_start < char_end:
                token_mask.append(i)
        
        if token_mask:
            # Mean pooling token embeddings within chunk
            chunk_tokens = token_embeddings[token_mask]
            chunk_emb = chunk_tokens.mean(dim=0).numpy()
            chunk_embeddings.append(chunk_emb)
    
    return chunk_embeddings


# Sử dụng
document = """
Bảo hiểm nhân thọ Manulife cung cấp nhiều gói sản phẩm.
Gói An Tâm Hưng Thịnh có thời hạn 20 năm.
Nó chi trả 100% số tiền bảo hiểm khi người được bảo hiểm tử vong.
Gói này cũng bao gồm quyền lợi nằm viện.
"""

# Define chunk boundaries
chunks = [
    (0, 60),    # "Bảo hiểm nhân thọ Manulife..."
    (61, 110),  # "Gói An Tâm Hưng Thịnh..."
    (111, 185), # "Nó chi trả 100%..."  ← "Nó" sẽ hiểu = gói ATHT
    (186, 230), # "Gói này cũng bao gồm..."
]

embeddings = late_chunking_embed(document, chunks)
# Each chunk embedding retains context from the full document
```

### Limitations

- Cần model hỗ trợ long context (>4K tokens)
- Chậm hơn khi encode (full document mỗi lần)
- Không phù hợp cho document quá dài (>8K tokens) — cần chia thành sections trước

---

## 2. RAPTOR (Recursive Abstractive Processing for Tree-Organized Retrieval)

### Concept

RAPTOR xây dựng cây tóm tắt đa tầng từ documents. Search ở nhiều mức abstraction:

```
Level 0: Original chunks (chi tiết nhất)
Level 1: Summary of 5-10 chunks (trung bình)
Level 2: Summary of summaries (tổng quan)
Level 3: Document-level summary (cao nhất)
```

### Why Is It Better?

- Câu hỏi tổng quan ("So sánh các gói bảo hiểm") match level 1-2
- Câu hỏi chi tiết ("Điều khoản loại trừ gói X") match level 0
- Cải thiện retrieval cho cả broad và narrow queries

### Code Example

```python
from openai import OpenAI
import numpy as np
from dataclasses import dataclass

client = OpenAI()


@dataclass
class RaptorNode:
    text: str
    embedding: np.ndarray
    level: int
    children: list["RaptorNode"]
    metadata: dict


def get_embedding(text: str) -> np.ndarray:
    """Get embedding from OpenAI."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding)


def summarize_texts(texts: list[str], context: str = "") -> str:
    """Summarize a group of texts using LLM."""
    combined = "\n\n---\n\n".join(texts)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": "Summarize the following passages into one concise paragraph, keeping important information."
        }, {
            "role": "user",
            "content": combined
        }],
        max_tokens=500
    )
    return response.choices[0].message.content


def cluster_chunks(embeddings: list[np.ndarray], n_clusters: int) -> list[list[int]]:
    """Cluster embeddings using K-means."""
    from sklearn.cluster import KMeans
    
    X = np.array(embeddings)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(X)
    
    clusters = [[] for _ in range(n_clusters)]
    for idx, label in enumerate(labels):
        clusters[label].append(idx)
    return clusters


def build_raptor_tree(
    chunks: list[str],
    max_levels: int = 3,
    cluster_size: int = 5
) -> list[RaptorNode]:
    """
    Build RAPTOR tree from chunks.
    
    Args:
        chunks: List of text chunks (level 0)
        max_levels: Maximum tree depth
        cluster_size: Target chunks per cluster
    
    Returns:
        All nodes (all levels) for indexing
    """
    all_nodes = []
    
    # Level 0: Original chunks
    current_level_nodes = []
    for i, chunk in enumerate(chunks):
        node = RaptorNode(
            text=chunk,
            embedding=get_embedding(chunk),
            level=0,
            children=[],
            metadata={"chunk_index": i}
        )
        current_level_nodes.append(node)
        all_nodes.append(node)
    
    # Build higher levels
    for level in range(1, max_levels + 1):
        if len(current_level_nodes) <= 1:
            break
        
        # Cluster current level
        embeddings = [n.embedding for n in current_level_nodes]
        n_clusters = max(1, len(current_level_nodes) // cluster_size)
        clusters = cluster_chunks(embeddings, n_clusters)
        
        next_level_nodes = []
        for cluster_indices in clusters:
            # Summarize cluster
            cluster_texts = [current_level_nodes[i].text for i in cluster_indices]
            summary = summarize_texts(cluster_texts)
            
            children = [current_level_nodes[i] for i in cluster_indices]
            node = RaptorNode(
                text=summary,
                embedding=get_embedding(summary),
                level=level,
                children=children,
                metadata={"num_children": len(children)}
            )
            next_level_nodes.append(node)
            all_nodes.append(node)
        
        current_level_nodes = next_level_nodes
    
    return all_nodes


def raptor_retrieve(
    query: str,
    all_nodes: list[RaptorNode],
    top_k: int = 5
) -> list[RaptorNode]:
    """Retrieve from all levels of RAPTOR tree."""
    query_embedding = get_embedding(query)
    
    # Score all nodes across all levels
    scored = []
    for node in all_nodes:
        similarity = np.dot(query_embedding, node.embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(node.embedding)
        )
        scored.append((similarity, node))
    
    # Sort by similarity, return top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    return [node for _, node in scored[:top_k]]


# === Usage ===
chunks = [
    "Gói An Tâm Hưng Thịnh có phí đóng 10 triệu/năm...",
    "Quyền lợi tử vong: chi trả 100% STBH...",
    "Điều khoản loại trừ: tự tử trong 2 năm đầu...",
    "Gói An Tâm Sống Khỏe bao gồm quyền lợi nằm viện...",
    # ... more chunks
]

# Build tree (one-time)
all_nodes = build_raptor_tree(chunks, max_levels=2, cluster_size=3)

# Retrieve
results = raptor_retrieve("So sánh các gói bảo hiểm Manulife", all_nodes, top_k=5)
# → Sẽ match summary nodes (level 1-2) thay vì chỉ chi tiết level 0
```

---

## 3. GraphRAG (Microsoft)

### Concept

GraphRAG xây dựng **knowledge graph** từ documents, sau đó dùng graph structure + community summaries để trả lời câu hỏi.

```
Documents → Extract Entities & Relations → Build Knowledge Graph
         → Detect Communities (Leiden algorithm)
         → Summarize each community
         → Query: map question to communities → reduce answers
```

### Why Is It Better?

- Trả lời câu hỏi tổng hợp ("Những yếu tố nào ảnh hưởng đến quyết định bồi thường?")
- Hiểu relationships giữa entities
- Community summaries cung cấp multi-hop reasoning

### Code Example

```python
"""
GraphRAG simplified implementation.
For production, use Microsoft's graphrag package: pip install graphrag
"""
from openai import OpenAI
from dataclasses import dataclass, field
import json
import networkx as nx

client = OpenAI()


@dataclass
class Entity:
    name: str
    type: str  # PERSON, ORG, PRODUCT, CONCEPT, ...
    description: str


@dataclass
class Relation:
    source: str
    target: str
    relation: str
    description: str


@dataclass
class Community:
    id: int
    entities: list[str]
    summary: str


def extract_entities_and_relations(text: str) -> tuple[list[Entity], list[Relation]]:
    """Extract entities and relations from text using LLM."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": """Extract entities and relations from the text.
Return JSON:
{
    "entities": [{"name": "...", "type": "PERSON|ORG|PRODUCT|CONCEPT|EVENT", "description": "..."}],
    "relations": [{"source": "entity_name", "target": "entity_name", "relation": "...", "description": "..."}]
}"""
        }, {
            "role": "user",
            "content": text
        }],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    entities = [Entity(**e) for e in data.get("entities", [])]
    relations = [Relation(**r) for r in data.get("relations", [])]
    return entities, relations


def build_knowledge_graph(chunks: list[str]) -> nx.Graph:
    """Build knowledge graph from document chunks."""
    G = nx.Graph()
    
    for chunk in chunks:
        entities, relations = extract_entities_and_relations(chunk)
        
        for entity in entities:
            if G.has_node(entity.name):
                # Merge descriptions
                existing = G.nodes[entity.name].get("description", "")
                G.nodes[entity.name]["description"] = f"{existing} | {entity.description}"
            else:
                G.add_node(entity.name, type=entity.type, description=entity.description)
        
        for rel in relations:
            G.add_edge(
                rel.source, rel.target,
                relation=rel.relation,
                description=rel.description
            )
    
    return G


def detect_communities(G: nx.Graph) -> list[set]:
    """Detect communities using Louvain (approximation of Leiden)."""
    from community import community_louvain
    
    partition = community_louvain.best_partition(G)
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = set()
        communities[comm_id].add(node)
    
    return list(communities.values())


def summarize_community(G: nx.Graph, community_nodes: set) -> str:
    """Summarize a community's entities and relations."""
    subgraph = G.subgraph(community_nodes)
    
    # Collect entity descriptions
    entity_info = []
    for node in subgraph.nodes():
        data = G.nodes[node]
        entity_info.append(f"- {node} ({data.get('type', 'UNKNOWN')}): {data.get('description', '')}")
    
    # Collect relations
    relation_info = []
    for u, v, data in subgraph.edges(data=True):
        relation_info.append(f"- {u} --[{data.get('relation', '')}]--> {v}: {data.get('description', '')}")
    
    context = f"Entities:\n" + "\n".join(entity_info) + f"\n\nRelations:\n" + "\n".join(relation_info)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "system",
            "content": "Summarize the following group of entities and relations into one coherent description."
        }, {
            "role": "user",
            "content": context
        }],
        max_tokens=300
    )
    return response.choices[0].message.content


def graphrag_query(
    question: str,
    communities: list[Community],
    top_k: int = 3
) -> str:
    """
    GraphRAG query: Map question to communities, then reduce.
    
    Map phase: Ask each community if it can answer
    Reduce phase: Combine relevant answers
    """
    # MAP: Score each community's relevance
    community_answers = []
    for comm in communities:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": f"Community summary:\n{comm.summary}"
            }, {
                "role": "user",
                "content": f"Based on this community, answer the question (if relevant): {question}\nIf not relevant, respond 'NOT_RELEVANT'."
            }],
            max_tokens=200
        )
        answer = response.choices[0].message.content
        if "NOT_RELEVANT" not in answer:
            community_answers.append(answer)
    
    if not community_answers:
        return "No relevant information found."
    
    # REDUCE: Combine answers
    combined = "\n\n".join(community_answers[:top_k])
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": "Synthesize the following answers into one complete answer, removing duplicates."
        }, {
            "role": "user",
            "content": f"Question: {question}\n\nPartial answers:\n{combined}"
        }],
        max_tokens=500
    )
    return response.choices[0].message.content


# === Usage ===
# 1. Build graph
chunks = ["...", "...", "..."]  # Document chunks
G = build_knowledge_graph(chunks)

# 2. Detect communities
community_sets = detect_communities(G)

# 3. Summarize communities
communities = []
for i, comm_nodes in enumerate(community_sets):
    summary = summarize_community(G, comm_nodes)
    communities.append(Community(id=i, entities=list(comm_nodes), summary=summary))

# 4. Query
answer = graphrag_query("Những yếu tố nào ảnh hưởng đến quyết định bồi thường?", communities)
```

### Microsoft GraphRAG Package

Cho production, dùng package chính thức:

```bash
pip install graphrag

# Init project
graphrag init --root ./ragtest

# Index documents
graphrag index --root ./ragtest

# Query (global — dùng community summaries)
graphrag query --root ./ragtest --method global --query "..."

# Query (local — dùng entity + relationship context)
graphrag query --root ./ragtest --method local --query "..."
```

---

## When to Use Which Technique

| Technique | Best For | Overhead | Quality Gain |
|---|---|---|---|
| **Late Chunking** | Documents có nhiều co-reference (nó, điều này) | Thấp | +5-10% retrieval |
| **RAPTOR** | Mix broad + narrow queries | Trung bình (LLM calls) | +10-15% cho broad queries |
| **GraphRAG** | Multi-hop reasoning, synthesize across docs | Cao (build graph) | +15-25% cho synthesis queries |
| **Basic RAG** | Simple factual Q&A | Thấp | Baseline |

### Combining Techniques

```
Recommended Stack (Production):
1. Late Chunking cho embedding quality
2. RAPTOR cho multi-level retrieval
3. Hybrid search (BM25 + vector)
4. Reranking (Cohere/Cross-encoder)
5. GraphRAG cho synthesis queries (optional, high cost)
```
