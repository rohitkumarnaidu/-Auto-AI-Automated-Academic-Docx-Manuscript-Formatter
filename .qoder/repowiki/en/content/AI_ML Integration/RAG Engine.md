# RAG Engine

<cite>
**Referenced Files in This Document**
- [rag_engine.py](file://backend/app/pipeline/intelligence/rag_engine.py)
- [default_guidelines.json](file://backend/app/pipeline/intelligence/default_guidelines.json)
- [semantic_parser.py](file://backend/app/pipeline/intelligence/semantic_parser.py)
- [session_vector_store.py](file://backend/app/services/session_vector_store.py)
- [crossref_client.py](file://backend/app/services/crossref_client.py)
- [model_store.py](file://backend/app/services/model_store.py)
- [settings.py](file://backend/app/config/settings.py)
- [quality_scorer.py](file://backend/app/pipeline/generation/quality_scorer.py)
- [verify_rag_interface.py](file://backend/manual_tests/rag/verify_rag_interface.py)
- [test_rag_engine.py](file://backend/tests/test_rag_engine.py)
</cite>

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Core Components](#core-components)
4. [Architecture Overview](#architecture-overview)
5. [Detailed Component Analysis](#detailed-component-analysis)
6. [Dependency Analysis](#dependency-analysis)
7. [Performance Considerations](#performance-considerations)
8. [Troubleshooting Guide](#troubleshooting-guide)
9. [Conclusion](#conclusion)
10. [Appendices](#appendices)

## Introduction
This document describes the Retrieval-Augmented Generation (RAG) engine used for academic formatting guidelines. It explains the retrieval system architecture, embedding strategies, and integration points with the broader pipeline. It covers document indexing, similarity search, relevance ranking, and the optional integration with Crossref for academic paper metadata validation. It also documents configuration options for embedding models, retrieval parameters, and performance tuning, along with the generation pipeline that combines retrieved context with LLM responses, error handling, and quality assessment of retrieved results.

## Project Structure
The RAG engine resides in the intelligence pipeline and integrates with services for embeddings, session storage, and external metadata validation. Key modules include:
- Retrieval engine: local embedding store with ChromaDB-backed vector store and a native fallback
- Embedding model lifecycle: priority loading with fallbacks and a deterministic hash-based model
- Indexing and querying: publisher-aware filtering and configurable top-k retrieval
- Crossref integration: citation validation and metadata confidence scoring
- Quality scoring: post-generation evaluation of generated content against required sections and citation counts

```mermaid
graph TB
subgraph "Intelligence Pipeline"
RE["RagEngine<br/>Indexing + Query"]
SP["SemanticParser<br/>SciBERT-based classification"]
QS["QualityScorer<br/>Content quality metrics"]
end
subgraph "Services"
MS["ModelStore<br/>Global model registry"]
SV["SessionVectorStore<br/>Per-session embeddings"]
CR["CrossRefClient<br/>Citation validation"]
end
subgraph "External"
ST["SentenceTransformers<br/>Embedding models"]
CH["ChromaDB<br/>Vector store"]
RD["Redis<br/>Caching"]
end
RE --> MS
RE --> ST
RE --> CH
SP --> MS
SP --> ST
SV --> MS
SV --> ST
SV --> CH
CR --> RD
QS -. "evaluates generated output" .-> RE
```

**Diagram sources**
- [rag_engine.py:106-528](file://backend/app/pipeline/intelligence/rag_engine.py#L106-L528)
- [semantic_parser.py:32-306](file://backend/app/pipeline/intelligence/semantic_parser.py#L32-L306)
- [session_vector_store.py:53-204](file://backend/app/services/session_vector_store.py#L53-L204)
- [crossref_client.py:32-164](file://backend/app/services/crossref_client.py#L32-L164)
- [model_store.py:4-33](file://backend/app/services/model_store.py#L4-L33)

**Section sources**
- [rag_engine.py:106-528](file://backend/app/pipeline/intelligence/rag_engine.py#L106-L528)
- [semantic_parser.py:32-306](file://backend/app/pipeline/intelligence/semantic_parser.py#L32-L306)
- [session_vector_store.py:53-204](file://backend/app/services/session_vector_store.py#L53-L204)
- [crossref_client.py:32-164](file://backend/app/services/crossref_client.py#L32-L164)
- [model_store.py:4-33](file://backend/app/services/model_store.py#L4-L33)

## Core Components
- RagEngine: Manages embedding model loading, persistent storage (ChromaDB or native JSON), indexing guidelines, and similarity-based retrieval with publisher filters.
- DeterministicEmbeddingModel: Provides a lightweight fallback embedding using token hashing to maintain semantic-like retrieval when ML libraries are unavailable.
- ModelStore: Global registry for pre-loaded models to avoid repeated initialization overhead.
- SessionVectorStore: Per-session vector store for dynamic document chunks with TTL deletion and optional ChromaDB backend.
- SemanticParser: Optional SciBERT-based classification for manuscript block types with heuristic fallback and language detection.
- CrossRefClient: Validates citations and retrieves metadata with Redis caching and rate-limit handling.
- QualityScorer: Computes quality metrics for generated content (compliance, completeness, citation count, section balance).

**Section sources**
- [rag_engine.py:68-104](file://backend/app/pipeline/intelligence/rag_engine.py#L68-L104)
- [rag_engine.py:106-528](file://backend/app/pipeline/intelligence/rag_engine.py#L106-L528)
- [model_store.py:4-33](file://backend/app/services/model_store.py#L4-L33)
- [session_vector_store.py:53-204](file://backend/app/services/session_vector_store.py#L53-L204)
- [semantic_parser.py:32-306](file://backend/app/pipeline/intelligence/semantic_parser.py#L32-L306)
- [crossref_client.py:32-164](file://backend/app/services/crossref_client.py#L32-L164)
- [quality_scorer.py:15-123](file://backend/app/pipeline/generation/quality_scorer.py#L15-L123)

## Architecture Overview
The RAG engine supports a tiered retrieval strategy:
- Tier 1: BAAI/bge-m3 (1024d) with ChromaDB persistent collection
- Tier 2: BAAI/bge-small-en-v1.5 (384d) with ChromaDB
- Tier 3: Any SentenceTransformer with native JSON cosine similarity
- Tier 4: Deterministic hash vector (256d) with native JSON

Initialization attempts ChromaDB; if unavailable, it falls back to a native JSON store. The engine auto-seeds default guidelines from a bundled JSON file when the store is empty.

```mermaid
sequenceDiagram
participant Client as "Pipeline Orchestrator"
participant Engine as "RagEngine"
participant Store as "ChromaDB/PersistentClient"
participant Native as "Native JSON Store"
Client->>Engine : query_rules(template_name, section_name, top_k)
Engine->>Engine : normalize publisher + intent
alt ChromaDB available
Engine->>Store : query(query_texts=[intent], n_results=top_k, where=publisher)
Store-->>Engine : documents[]
Engine-->>Client : [text,...]
else Fallback to native
Engine->>Engine : encode(intent)
Engine->>Native : iterate kb entries with matching publisher
Engine->>Engine : compute cosine similarity
Engine-->>Client : ranked [text,...]
end
```

**Diagram sources**
- [rag_engine.py:423-467](file://backend/app/pipeline/intelligence/rag_engine.py#L423-L467)

**Section sources**
- [rag_engine.py:117-201](file://backend/app/pipeline/intelligence/rag_engine.py#L117-L201)
- [rag_engine.py:423-467](file://backend/app/pipeline/intelligence/rag_engine.py#L423-L467)
- [default_guidelines.json:1-59](file://backend/app/pipeline/intelligence/default_guidelines.json#L1-L59)

## Detailed Component Analysis

### Retrieval Engine (RagEngine)
- Embedding model loading priority:
  - Reuse from ModelStore if available
  - Load BAAI/bge-m3 (1024d) or fallback to BAAI/bge-small-en-v1.5 (384d)
  - If transformers unavailable, activate DeterministicEmbeddingModel (256d)
- Storage backends:
  - ChromaDB persistent collection named by active model
  - Native JSON store (kb.json) for fallback and persistence
- Indexing:
  - add_guideline writes to both ChromaDB and native store
  - Metadata includes normalized publisher and lowercased section
- Querying:
  - query_guidelines supports publisher filtering and top-k selection
  - query_rules adapts template/section names to publisher/intent and returns rule dicts
- Auto-seeding:
  - _seed_if_empty loads default guidelines from default_guidelines.json when store is empty
- Persistence:
  - reset deletes collection and clears native store
  - native store persists to kb.json

```mermaid
classDiagram
class RagEngine {
+add_guideline(publisher, section, text, metadata)
+query_guidelines(publisher, intent, top_k) str[]
+query_rules(template_name, section_name, top_k) Dict[]
+reset() void
-_seed_if_empty() void
-_load_embedding_model() void
-_load_native() void
-_save_native() void
}
class DeterministicEmbeddingModel {
+get_sentence_embedding_dimension() int
+encode(texts) float[]
-_encode_one(text) float[]
-_token_index(token) int
}
RagEngine --> DeterministicEmbeddingModel : "fallback"
```

**Diagram sources**
- [rag_engine.py:68-104](file://backend/app/pipeline/intelligence/rag_engine.py#L68-L104)
- [rag_engine.py:106-528](file://backend/app/pipeline/intelligence/rag_engine.py#L106-L528)

**Section sources**
- [rag_engine.py:117-201](file://backend/app/pipeline/intelligence/rag_engine.py#L117-L201)
- [rag_engine.py:202-244](file://backend/app/pipeline/intelligence/rag_engine.py#L202-L244)
- [rag_engine.py:400-422](file://backend/app/pipeline/intelligence/rag_engine.py#L400-L422)
- [rag_engine.py:423-467](file://backend/app/pipeline/intelligence/rag_engine.py#L423-L467)
- [rag_engine.py:503-516](file://backend/app/pipeline/intelligence/rag_engine.py#L503-L516)
- [default_guidelines.json:1-59](file://backend/app/pipeline/intelligence/default_guidelines.json#L1-L59)

### Embedding Strategies and Fallbacks
- Primary model: BAAI/bge-m3 (1024d)
- Fallback model: BAAI/bge-small-en-v1.5 (384d)
- Deterministic fallback: token hashing into 256-d vectors
- ModelStore reuse avoids repeated loading; settings toggle low-memory or transformer usage

```mermaid
flowchart TD
Start(["Initialize RagEngine"]) --> CheckMS["Check ModelStore"]
CheckMS --> |Found| UseMS["Reuse model from ModelStore"]
CheckMS --> |Not Found| LowMem{"LOW_MEMORY_MODE or RAG_USE_TRANSFORMERS?"}
LowMem --> |Yes| Det["Activate DeterministicEmbeddingModel"]
LowMem --> |No| TryBGE["Try BGE-M3"]
TryBGE --> |Success| UseBGE["Use BGE-M3"]
TryBGE --> |Fail| TrySmall["Try BGE-Small"]
TrySmall --> |Success| UseSmall["Use BGE-Small"]
TrySmall --> |Fail| Det
Det --> End(["Ready"])
UseMS --> End
UseBGE --> End
UseSmall --> End
```

**Diagram sources**
- [rag_engine.py:314-395](file://backend/app/pipeline/intelligence/rag_engine.py#L314-L395)
- [model_store.py:4-33](file://backend/app/services/model_store.py#L4-L33)
- [settings.py:185-190](file://backend/app/config/settings.py#L185-L190)

**Section sources**
- [rag_engine.py:52-66](file://backend/app/pipeline/intelligence/rag_engine.py#L52-L66)
- [rag_engine.py:314-395](file://backend/app/pipeline/intelligence/rag_engine.py#L314-L395)
- [model_store.py:4-33](file://backend/app/services/model_store.py#L4-L33)
- [settings.py:185-190](file://backend/app/config/settings.py#L185-L190)

### Document Indexing and Similarity Search
- Indexing:
  - Documents are added with metadata (publisher, section)
  - Embeddings are computed and stored alongside text
- Querying:
  - ChromaDB query with publisher filter and top_k
  - Native fallback computes cosine similarity across matching publisher entries
- Ranking:
  - Cosine similarity used for native ranking
  - ChromaDB returns nearest neighbors based on distance

```mermaid
flowchart TD
A["add_guideline(text, metadata)"] --> B{"ChromaDB enabled?"}
B --> |Yes| C["Compute embedding"]
C --> D["collection.add(ids, documents, metadatas)"]
B --> |No| E["Skip ChromaDB add"]
D --> F["Append to knowledge_base with embedding"]
E --> F
F --> G["Persist native store"]
H["query_guidelines(publisher, intent, top_k)"] --> I{"ChromaDB enabled?"}
I --> |Yes| J["collection.query(where=publisher)"]
J --> K{"Results found?"}
K --> |Yes| L["Return documents"]
K --> |No| M["Log warning and continue"]
I --> |No| N["Encode intent"]
M --> N
N --> O["Iterate knowledge_base (publisher match)"]
O --> P["Compute cosine similarity"]
P --> Q["Sort descending and return top_k"]
```

**Diagram sources**
- [rag_engine.py:400-467](file://backend/app/pipeline/intelligence/rag_engine.py#L400-L467)

**Section sources**
- [rag_engine.py:400-467](file://backend/app/pipeline/intelligence/rag_engine.py#L400-L467)

### Crossref Integration for Academic Paper Retrieval
- Validates citations and retrieves metadata with confidence scoring
- Distributed caching via Redis with in-memory fallback
- Rate limiting handled with retries and backoff
- Confidence derived from TF-IDF relevance score provided by Crossref

```mermaid
sequenceDiagram
participant Client as "Caller"
participant CR as "CrossRefClient"
participant Redis as "Redis Cache"
participant API as "CrossRef API"
Client->>CR : validate_citation(raw_text)
CR->>Redis : GET crossref : {query}
alt Cache hit
Redis-->>CR : cached result
CR-->>Client : result
else Cache miss
CR->>API : GET works?query.bibliographic={query}&rows=1
API-->>CR : JSON message.items[0]
CR->>Redis : SETEX crossref : {query} result (7d)
CR-->>Client : result
end
```

**Diagram sources**
- [crossref_client.py:132-154](file://backend/app/services/crossref_client.py#L132-L154)

**Section sources**
- [crossref_client.py:32-164](file://backend/app/services/crossref_client.py#L32-L164)

### Semantic Search Capabilities
- Optional SciBERT-based classification for manuscript blocks with heuristic fallback
- Language detection to gate transformer usage
- Batch inference with robust error handling and fallback to heuristics

```mermaid
classDiagram
class SemanticParser {
+analyze_blocks(blocks) Dict[]
+classify_block(text, use_transformer) Dict
+predict_blocks_batch(texts) Dict[]
-_predict_block_types_batch(texts) Dict[]
-_heuristic_classify(text) Dict
-_repair_fragmented_headings(blocks) Block[]
}
```

**Diagram sources**
- [semantic_parser.py:32-306](file://backend/app/pipeline/intelligence/semantic_parser.py#L32-L306)

**Section sources**
- [semantic_parser.py:32-306](file://backend/app/pipeline/intelligence/semantic_parser.py#L32-L306)

### Session Vector Store
- Per-session ChromaDB collections with TTL-based deletion
- Embedding model reuse via ModelStore
- Adds chunks with embeddings and metadata; queries with similarity scoring

```mermaid
flowchart TD
S["create_collection(session_id)"] --> T["get_or_create_collection(session_{id})"]
U["add_chunks(session_id, chunks)"] --> V["encode(text)"]
V --> W["collection.add(documents, metadatas, ids, embeddings)"]
X["query(session_id, question, top_k)"] --> Y["encode(question)"]
Y --> Z["collection.query(query_embeddings, n_results)"]
Z --> AA["Map distances to scores and return chunks"]
```

**Diagram sources**
- [session_vector_store.py:53-204](file://backend/app/services/session_vector_store.py#L53-L204)

**Section sources**
- [session_vector_store.py:53-204](file://backend/app/services/session_vector_store.py#L53-L204)

### Generation Pipeline and Quality Assessment
- The retrieval results are consumed by the generation pipeline to augment prompts
- QualityScorer evaluates generated content against required sections and citation counts, computing weighted scores for compliance, completeness, citations, and section balance

```mermaid
flowchart TD
B1["Generated Content"] --> B2["Normalize sections"]
B2 --> B3["Compute template_compliance"]
B2 --> B4["Compute completeness (>=100 words)"]
B2 --> B5["Count citations"]
B2 --> B6["Compute section_balance (CV)"]
B3 --> B7["Weighted aggregation"]
B4 --> B7
B5 --> B7
B6 --> B7
B7 --> B8["Overall score"]
```

**Diagram sources**
- [quality_scorer.py:15-123](file://backend/app/pipeline/generation/quality_scorer.py#L15-L123)

**Section sources**
- [quality_scorer.py:15-123](file://backend/app/pipeline/generation/quality_scorer.py#L15-L123)

## Dependency Analysis
- RagEngine depends on:
  - ModelStore for embedding model reuse
  - ChromaDB client for vector operations (optional)
  - SentenceTransformers for embeddings (optional)
  - DeterministicEmbeddingModel as fallback
- SemanticParser depends on:
  - SciBERT tokenizer/model via Transformers
  - ModelStore for pre-loading
- SessionVectorStore depends on:
  - ChromaDB client and SentenceTransformers
  - ModelStore for embedding model reuse
- CrossRefClient depends on:
  - Redis for distributed caching
  - Requests for HTTP calls

```mermaid
graph LR
RE["RagEngine"] --> MS["ModelStore"]
RE --> ST["SentenceTransformers"]
RE --> CH["ChromaDB"]
RE --> DET["DeterministicEmbeddingModel"]
SP["SemanticParser"] --> MS
SP --> ST
SV["SessionVectorStore"] --> MS
SV --> ST
SV --> CH
CR["CrossRefClient"] --> RD["Redis"]
CR --> REQ["Requests"]
```

**Diagram sources**
- [rag_engine.py:106-528](file://backend/app/pipeline/intelligence/rag_engine.py#L106-L528)
- [semantic_parser.py:32-306](file://backend/app/pipeline/intelligence/semantic_parser.py#L32-L306)
- [session_vector_store.py:53-204](file://backend/app/services/session_vector_store.py#L53-L204)
- [crossref_client.py:32-164](file://backend/app/services/crossref_client.py#L32-L164)
- [model_store.py:4-33](file://backend/app/services/model_store.py#L4-L33)

**Section sources**
- [rag_engine.py:106-528](file://backend/app/pipeline/intelligence/rag_engine.py#L106-L528)
- [semantic_parser.py:32-306](file://backend/app/pipeline/intelligence/semantic_parser.py#L32-L306)
- [session_vector_store.py:53-204](file://backend/app/services/session_vector_store.py#L53-L204)
- [crossref_client.py:32-164](file://backend/app/services/crossref_client.py#L32-L164)
- [model_store.py:4-33](file://backend/app/services/model_store.py#L4-L33)

## Performance Considerations
- Prefer ChromaDB for scalable vector operations; native fallback ensures resilience.
- Use ModelStore to preload and reuse embedding models across requests.
- Tune top_k to balance recall and latency; higher values increase computation cost.
- Enable LOW_MEMORY_MODE or disable RAG_USE_TRANSFORMERS to activate deterministic embeddings when resources are constrained.
- For Crossref, leverage Redis caching to reduce API calls and improve latency.

[No sources needed since this section provides general guidance]

## Troubleshooting Guide
- ChromaDB import or compatibility errors:
  - The engine detects known compatibility issues and falls back to native storage automatically.
- Empty knowledge base:
  - Auto-seeding from default_guidelines.json occurs when the store is empty.
- Query failures:
  - ChromaDB query failures trigger fallback to native cosine similarity.
- Transformer import failures:
  - DeterministicEmbeddingModel is activated and registered in ModelStore.
- Crossref rate limits:
  - Built-in retries with backoff; consider enabling Redis for caching to minimize repeated calls.

**Section sources**
- [rag_engine.py:172-196](file://backend/app/pipeline/intelligence/rag_engine.py#L172-L196)
- [rag_engine.py:202-244](file://backend/app/pipeline/intelligence/rag_engine.py#L202-L244)
- [rag_engine.py:436-438](file://backend/app/pipeline/intelligence/rag_engine.py#L436-L438)
- [rag_engine.py:320-395](file://backend/app/pipeline/intelligence/rag_engine.py#L320-L395)
- [crossref_client.py:73-118](file://backend/app/services/crossref_client.py#L73-L118)

## Conclusion
The RAG engine provides a robust, layered retrieval system for academic formatting guidelines. It prioritizes high-quality embeddings with graceful fallbacks, supports both ChromaDB and native storage, and integrates optional semantic classification and citation validation. The design emphasizes reliability, performance tuning, and ease of operation across diverse environments.

[No sources needed since this section summarizes without analyzing specific files]

## Appendices

### Configuration Options
- Feature toggles and memory modes:
  - USE_SCIBERT_CLASSIFICATION: Enable/disable SciBERT-based classification
  - LOW_MEMORY_MODE: Activate deterministic embeddings
  - RAG_USE_TRANSFORMERS: Control transformer-based embeddings
  - PRELOAD_AI_MODELS: Preload models into ModelStore
- Crossref:
  - CROSSREF_MAILTO: Contact email header for API
  - REDIS_ENABLED/REDIS_URL: Enable distributed caching
- Retrieval:
  - top_k: Number of results to return from query
  - Publisher filtering: enforced by metadata and query adapters

**Section sources**
- [settings.py:185-190](file://backend/app/config/settings.py#L185-L190)
- [settings.py:358-362](file://backend/app/config/settings.py#L358-L362)
- [rag_engine.py:423-467](file://backend/app/pipeline/intelligence/rag_engine.py#L423-L467)
- [crossref_client.py:37-39](file://backend/app/services/crossref_client.py#L37-L39)

### Interface Verification
- Manual verification script confirms presence of required methods and basic behavior.

**Section sources**
- [verify_rag_interface.py:1-42](file://backend/manual_tests/rag/verify_rag_interface.py#L1-L42)

### Tests
- Comprehensive unit tests cover initialization, persistence, fallback behavior, and ranking correctness.

**Section sources**
- [test_rag_engine.py:1-355](file://backend/tests/test_rag_engine.py#L1-L355)