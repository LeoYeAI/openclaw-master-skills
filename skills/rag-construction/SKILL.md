---
name: "rag-construction"
description: "Build RAG systems for construction knowledge bases. Create searchable AI-powered construction document systems"
homepage: "https://datadrivenconstruction.io"
metadata: {"openclaw": {"emoji": "🐼", "os": ["darwin", "linux", "win32"], "homepage": "https://datadrivenconstruction.io", "requires": {"bins": ["python3"]}}}
---
# RAG Construction

## Overview

Based on DDC methodology (Chapter 2.3), this skill builds Retrieval-Augmented Generation (RAG) systems for construction knowledge bases, enabling semantic search and AI-powered question answering over construction documents.

**Book Reference:** "Pandas DataFrame и LLM ChatGPT" / "Pandas DataFrame and LLM ChatGPT"

## Quick Start

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime
import json
import hashlib
import re

class DocumentType(Enum):
    """Types of construction documents"""
    SPECIFICATION = "specification"
    DRAWING = "drawing"
    CONTRACT = "contract"
    RFI = "rfi"
    SUBMITTAL = "submittal"
    CHANGE_ORDER = "change_order"
    MEETING_MINUTES = "meeting_minutes"
    DAILY_REPORT = "daily_report"
    SAFETY_REPORT = "safety_report"
    INSPECTION = "inspection"
    MANUAL = "manual"
    STANDARD = "standard"

class ChunkingStrategy(Enum):
    """Text chunking strategies"""
    FIXED_SIZE = "fixed_size"
    PARAGRAPH = "paragraph"
    SECTION = "section"
    SEMANTIC = "semantic"
    SENTENCE = "sentence"

@dataclass
class DocumentChunk:
    """A chunk of document text"""
    id: str
    document_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    token_count: int = 0
    position: int = 0

@dataclass
class Document:
    """Construction document"""
    id: str
    title: str
    doc_type: DocumentType
    content: str
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    chunks: List[DocumentChunk] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SearchResult:
    """Search result from vector store"""
    chunk: DocumentChunk
    score: float
    document_title: str
    doc_type: DocumentType

@dataclass
class RAGResponse:
    """Response from RAG system"""
    query: str
    answer: str
    sources: List[SearchResult]
    confidence: float
    tokens_used: int


class TextChunker:
    """Split documents into chunks for embedding"""

    def __init__(
        self,
        strategy: ChunkingStrategy = ChunkingStrategy.PARAGRAPH,
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split document into chunks"""
        if self.strategy == ChunkingStrategy.FIXED_SIZE:
            return self._chunk_fixed_size(document)
        elif self.strategy == ChunkingStrategy.PARAGRAPH:
            return self._chunk_by_paragraph(document)
        elif self.strategy == ChunkingStrategy.SECTION:
            return self._chunk_by_section(document)
        elif self.strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_by_sentence(document)
        else:
            return self._chunk_fixed_size(document)

    def _chunk_fixed_size(self, document: Document) -> List[DocumentChunk]:
        """Chunk by fixed character size with overlap"""
        chunks = []
        text = document.content
        start = 0
        position = 0

        while start < len(text):
            end = start + self.chunk_size

            # Find word boundary
            if end < len(text):
                while end > start and text[end] not in ' \n\t':
                    end -= 1

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_id = self._generate_chunk_id(document.id, position)
                chunks.append(DocumentChunk(
                    id=chunk_id,
                    document_id=document.id,
                    content=chunk_text,
                    metadata={
                        "doc_type": document.doc_type.value,
                        "title": document.title,
                        **document.metadata
                    },
                    token_count=len(chunk_text.split()),
                    position=position
                ))
                position += 1

            start = end - self.chunk_overlap
            if start >= len(text):
                break

        return chunks

    def _chunk_by_paragraph(self, document: Document) -> List[DocumentChunk]:
        """Chunk by paragraphs"""
        chunks = []
        paragraphs = document.content.split('\n\n')
        current_chunk = ""
        position = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) < self.chunk_size:
                current_chunk += "\n\n" + para if current_chunk else para
            else:
                if current_chunk:
                    chunk_id = self._generate_chunk_id(document.id, position)
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        document_id=document.id,
                        content=current_chunk,
                        metadata={
                            "doc_type": document.doc_type.value,
                            "title": document.title,
                            **document.metadata
                        },
                        token_count=len(current_chunk.split()),
                        position=position
                    ))
                    position += 1
                current_chunk = para

        # Add remaining content
        if current_chunk:
            chunk_id = self._generate_chunk_id(document.id, position)
            chunks.append(DocumentChunk(
                id=chunk_id,
                document_id=document.id,
                content=current_chunk,
                metadata={
                    "doc_type": document.doc_type.value,
                    "title": document.title,
                    **document.metadata
                },
                token_count=len(current_chunk.split()),
                position=position
            ))

        return chunks

    def _chunk_by_section(self, document: Document) -> List[DocumentChunk]:
        """Chunk by document sections (headers)"""
        # Split by common section patterns
        section_pattern = r'\n(?=(?:\d+\.|\d+\s|SECTION|ARTICLE|PART)\s+[A-Z])'
        sections = re.split(section_pattern, document.content)

        chunks = []
        for position, section in enumerate(sections):
            section = section.strip()
            if section:
                # If section is too large, further split it
                if len(section) > self.chunk_size * 2:
                    sub_chunker = TextChunker(ChunkingStrategy.PARAGRAPH, self.chunk_size)
                    sub_doc = Document(
                        id=f"{document.id}_sec{position}",
                        title=document.title,
                        doc_type=document.doc_type,
                        content=section,
                        source=document.source,
                        metadata=document.metadata
                    )
                    sub_chunks = sub_chunker.chunk_document(sub_doc)
                    for i, chunk in enumerate(sub_chunks):
                        chunk.id = self._generate_chunk_id(document.id, position * 100 + i)
                        chunk.position = position * 100 + i
                    chunks.extend(sub_chunks)
                else:
                    chunk_id = self._generate_chunk_id(document.id, position)
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        document_id=document.id,
                        content=section,
                        metadata={
                            "doc_type": document.doc_type.value,
                            "title": document.title,
                            **document.metadata
                        },
                        token_count=len(section.split()),
                        position=position
                    ))

        return chunks

    def _chunk_by_sentence(self, document: Document) -> List[DocumentChunk]:
        """Chunk by sentences, grouping to meet size requirements"""
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', document.content)

        chunks = []
        current_chunk = ""
        position = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunk_id = self._generate_chunk_id(document.id, position)
                    chunks.append(DocumentChunk(
                        id=chunk_id,
                        document_id=document.id,
                        content=current_chunk.strip(),
                        metadata={
                            "doc_type": document.doc_type.value,
                            "title": document.title,
                            **document.metadata
                        },
                        token_count=len(current_chunk.split()),
                        position=position
                    ))
                    position += 1
                current_chunk = sentence

        if current_chunk:
            chunk_id = self._generate_chunk_id(document.id, position)
            chunks.append(DocumentChunk(
                id=chunk_id,
                document_id=document.id,
                content=current_chunk.strip(),
                metadata={
                    "doc_type": document.doc_type.value,
                    "title": document.title,
                    **document.metadata
                },
                token_count=len(current_chunk.split()),
                position=position
            ))

        return chunks

    def _generate_chunk_id(self, doc_id: str, position: int) -> str:
        """Generate unique chunk ID"""
        return hashlib.md5(f"{doc_id}_{position}".encode()).hexdigest()[:12]


class VectorStore:
    """Simple in-memory vector store for RAG"""

    def __init__(self):
        self.chunks: Dict[str, DocumentChunk] = {}
        self.embeddings: Dict[str, List[float]] = {}

    def add_chunks(self, chunks: List[DocumentChunk]):
        """Add chunks to the store"""
        for chunk in chunks:
            self.chunks[chunk.id] = chunk
            if chunk.embedding:
                self.embeddings[chunk.id] = chunk.embedding

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        """Search for similar chunks"""
        results = []

        for chunk_id, chunk in self.chunks.items():
            # Apply metadata filter
            if filter_metadata:
                match = all(
                    chunk.metadata.get(k) == v
                    for k, v in filter_metadata.items()
                )
                if not match:
                    continue

            # Calculate similarity (cosine similarity simulation)
            if chunk_id in self.embeddings:
                score = self._cosine_similarity(query_embedding, self.embeddings[chunk_id])
                results.append((chunk, score))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def get_stats(self) -> Dict:
        """Get store statistics"""
        doc_types = {}
        for chunk in self.chunks.values():
            doc_type = chunk.metadata.get("doc_type", "unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1

        return {
            "total_chunks": len(self.chunks),
            "chunks_with_embeddings": len(self.embeddings),
            "chunks_by_type": doc_types
        }


class EmbeddingModel:
    """Simulated embedding model (replace with actual model in production)"""

    def __init__(self, model_name: str = "text-embedding-ada-002"):
        self.model_name = model_name
        self.dimension = 1536

    def embed(self, text: str) -> List[float]:
        """Generate embedding for text"""
        # Simulation: generate deterministic embedding based on text hash
        text_hash = hashlib.sha256(text.encode()).digest()
        embedding = []
        for i in range(self.dimension):
            byte_idx = i % len(text_hash)
            embedding.append((text_hash[byte_idx] - 128) / 128.0)
        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [self.embed(text) for text in texts]


class ConstructionRAG:
    """
    RAG system for construction knowledge bases.
    Based on DDC methodology Chapter 2.3.
    """

    def __init__(
        self,
        embedding_model: Optional[EmbeddingModel] = None,
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.PARAGRAPH,
        chunk_size: int = 500
    ):
        self.embedding_model = embedding_model or EmbeddingModel()
        self.chunker = TextChunker(chunking_strategy, chunk_size)
        self.vector_store = VectorStore()
        self.documents: Dict[str, Document] = {}

    def add_document(self, document: Document) -> int:
        """
        Add a document to the knowledge base.

        Args:
            document: Document to add

        Returns:
            Number of chunks created
        """
        # Store document
        self.documents[document.id] = document

        # Chunk document
        chunks = self.chunker.chunk_document(document)

        # Generate embeddings
        for chunk in chunks:
            chunk.embedding = self.embedding_model.embed(chunk.content)

        # Add to vector store
        self.vector_store.add_chunks(chunks)

        # Update document with chunks
        document.chunks = chunks

        return len(chunks)

    def add_documents(self, documents: List[Document]) -> Dict[str, int]:
        """Add multiple documents"""
        results = {}
        for doc in documents:
            results[doc.id] = self.add_document(doc)
        return results

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_type: Optional[DocumentType] = None
    ) -> List[SearchResult]:
        """
        Search the knowledge base.

        Args:
            query: Search query
            top_k: Number of results to return
            doc_type: Filter by document type

        Returns:
            List of search results
        """
        # Generate query embedding
        query_embedding = self.embedding_model.embed(query)

        # Build filter
        filter_metadata = None
        if doc_type:
            filter_metadata = {"doc_type": doc_type.value}

        # Search vector store
        results = self.vector_store.search(
            query_embedding,
            top_k=top_k,
            filter_metadata=filter_metadata
        )

        # Build search results
        search_results = []
        for chunk, score in results:
            doc = self.documents.get(chunk.document_id)
            search_results.append(SearchResult(
                chunk=chunk,
                score=score,
                document_title=doc.title if doc else "Unknown",
                doc_type=doc.doc_type if doc else DocumentType.MANUAL
            ))

        return search_results

    def query(
        self,
        question: str,
        top_k: int = 5,
        doc_type: Optional[DocumentType] = None
    ) -> RAGResponse:
        """
        Answer a question using RAG.

        Args:
            question: Question to answer
            top_k: Number of context chunks to use
            doc_type: Filter by document type

        Returns:
            RAG response with answer and sources
        """
        # Search for relevant context
        search_results = self.search(question, top_k=top_k, doc_type=doc_type)

        if not search_results:
            return RAGResponse(
                query=question,
                answer="I couldn't find relevant information to answer this question.",
                sources=[],
                confidence=0.0,
                tokens_used=0
            )

        # Build context from search results
        context_parts = []
        for i, result in enumerate(search_results):
            context_parts.append(
                f"[Source {i+1}: {result.document_title}]\n{result.chunk.content}"
            )

        context = "\n\n".join(context_parts)

        # Generate answer (simulated - in production, call LLM)
        answer = self._generate_answer(question, context, search_results)

        # Calculate confidence
        avg_score = sum(r.score for r in search_results) / len(search_results)

        return RAGResponse(
            query=question,
            answer=answer,
            sources=search_results,
            confidence=avg_score,
            tokens_used=len(context.split()) + len(question.split())
        )

    def _generate_answer(
        self,
        question: str,
        context: str,
        sources: List[SearchResult]
    ) -> str:
        """
        Generate answer from context.
        In production, this would call an LLM API.
        """
        # Simulated answer generation
        answer_parts = [
            f"Based on the available construction documentation:\n"
        ]

        # Extract key information from sources
        for source in sources[:3]:
            # Take first sentence of each relevant chunk
            first_sentence = source.chunk.content.split('.')[0] + '.'
            answer_parts.append(f"- {first_sentence}")

        answer_parts.append(
            f"\n\nThis information comes from {len(sources)} source documents "
            f"including: {', '.join(set(s.document_title for s in sources[:3]))}."
        )

        return "\n".join(answer_parts)

    def get_document_summary(self, document_id: str) -> Optional[Dict]:
        """Get summary of a document"""
        doc = self.documents.get(document_id)
        if not doc:
            return None

        return {
            "id": doc.id,
            "title": doc.title,
            "type": doc.doc_type.value,
            "chunks": len(doc.chunks),
            "total_tokens": sum(c.token_count for c in doc.chunks),
            "source": doc.source,
            "created_at": doc.created_at.isoformat()
        }

    def get_stats(self) -> Dict:
        """Get system statistics"""
        return {
            "total_documents": len(self.documents),
            "vector_store": self.vector_store.get_stats(),
            "embedding_model": self.embedding_model.model_name,
            "chunking_strategy": self.chunker.strategy.value
        }

    def export_knowledge_base(self) -> Dict:
        """Export knowledge base for backup/transfer"""
        return {
            "documents": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "type": doc.doc_type.value,
                    "content": doc.content,
                    "source": doc.source,
                    "metadata": doc.metadata
                }
                for doc in self.documents.values()
            ],
            "stats": self.get_stats(),
            "exported_at": datetime.now().isoformat()
        }
```

## Common Use Cases

### Build Construction Knowledge Base

```python
rag = ConstructionRAG(
    chunking_strategy=ChunkingStrategy.SECTION,
    chunk_size=500
)

# Add specifications
spec_doc = Document(
    id="spec-03300",
    title="Cast-in-Place Concrete Specification",
    doc_type=DocumentType.SPECIFICATION,
    content="""
    SECTION 03 30 00 - CAST-IN-PLACE CONCRETE

    PART 1 - GENERAL
    1.1 SUMMARY
    A. Section includes cast-in-place concrete for foundations,
       slabs, walls, and other structural elements.

    1.2 RELATED SECTIONS
    A. Section 03 10 00 - Concrete Forming
    B. Section 03 20 00 - Concrete Reinforcing

    PART 2 - PRODUCTS
    2.1 CONCRETE MATERIALS
    A. Portland Cement: ASTM C150, Type I or II
    B. Aggregates: ASTM C33, graded
    C. Water: Clean, potable
    """,
    source="project_specs.pdf",
    metadata={"division": "03", "project": "Building A"}
)

chunks_created = rag.add_document(spec_doc)
print(f"Created {chunks_created} chunks")
```

### Search Knowledge Base

```python
# Search for concrete requirements
results = rag.search(
    query="concrete strength requirements",
    top_k=5,
    doc_type=DocumentType.SPECIFICATION
)

for result in results:
    print(f"Score: {result.score:.3f}")
    print(f"Document: {result.document_title}")
    print(f"Content: {result.chunk.content[:200]}...")
    print()
```

### Answer Questions with RAG

```python
response = rag.query(
    question="What type of cement should be used for foundations?",
    top_k=3
)

print(f"Answer: {response.answer}")
print(f"Confidence: {response.confidence:.0%}")
print(f"Sources: {len(response.sources)}")
```

## Quick Reference

| Component | Purpose |
|-----------|---------|
| `ConstructionRAG` | Main RAG system |
| `TextChunker` | Document chunking |
| `VectorStore` | Embedding storage |
| `EmbeddingModel` | Text embeddings |
| `DocumentChunk` | Chunk with metadata |
| `RAGResponse` | Query response |

## Resources

- **Book**: "Data-Driven Construction" by Artem Boiko, Chapter 2.3
- **Website**: https://datadrivenconstruction.io

## Next Steps

- Use [llm-data-automation](../llm-data-automation/SKILL.md) for automation
- Use [vector-search](../../Chapter-4.4/vector-search/SKILL.md) for advanced search
- Use [document-classification-nlp](../../../DDC_Innovative/document-classification-nlp/SKILL.md) for classification
