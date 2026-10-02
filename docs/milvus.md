# Milvus Vector Store

> **Semantic knowledge layer for the JARVIS AI Runtime.**
> All collections are populated exclusively by **jarvis-parser**.

---

## Why Milvus?

Neo4j captures *structural* relationships — which class calls which method. Milvus captures *semantic* similarity — which methods do similar things, regardless of their names or structural location.

This distinction is critical for code reasoning:
- A developer searching for "payment validation logic" may not know the exact class name.
- Vector search finds semantically similar implementations even across different modules or naming conventions.
- Combined with graph traversal, this produces dramatically better retrieval than either alone.

---

## Collections

JARVIS uses five Milvus collections. All are populated by jarvis-parser at index time.

### `jarvis_methods`

Embeddings of individual method signatures and their LLM-generated summaries.

**Use case:** Find methods that do similar things to the query (e.g., "rate limiting", "token validation").

| Field | Type | Description |
|---|---|---|
| `id` | INT64 | Primary key (auto-generated) |
| `node_id` | VARCHAR(256) | Neo4j element ID |
| `repository_id` | VARCHAR(256) | Repository identifier |
| `package` | VARCHAR(512) | Package name |
| `class` | VARCHAR(512) | Class qualified name |
| `method` | VARCHAR(512) | Method signature |
| `language` | VARCHAR(64) | Programming language |
| `file_path` | VARCHAR(1024) | Repository-relative file path |
| `hash` | VARCHAR(64) | SHA-256 of method content |
| `parser_version` | VARCHAR(32) | jarvis-parser version |
| `embedding_model` | VARCHAR(128) | Embedding model identifier |
| `vector` | FLOAT_VECTOR(3072) | text-embedding-3-large vector |

### `jarvis_classes`

Embeddings of class-level summaries including all method signatures and docstrings.

**Use case:** Find classes responsible for a specific business domain (e.g., "authentication", "order management").

| Field | Type | Description |
|---|---|---|
| `id` | INT64 | Primary key |
| `node_id` | VARCHAR(256) | Neo4j element ID |
| `repository_id` | VARCHAR(256) | Repository identifier |
| `package` | VARCHAR(512) | Package name |
| `class` | VARCHAR(512) | Class qualified name |
| `language` | VARCHAR(64) | Programming language |
| `file_path` | VARCHAR(1024) | Repository-relative file path |
| `hash` | VARCHAR(64) | SHA-256 of class content |
| `parser_version` | VARCHAR(32) | jarvis-parser version |
| `embedding_model` | VARCHAR(128) | Embedding model identifier |
| `vector` | FLOAT_VECTOR(3072) | Embedding vector |

### `jarvis_capabilities`

Embeddings of high-level business capability descriptions extracted from class clusters and module summaries.

**Use case:** Answer high-level questions like "how does this service handle authentication?" without needing to specify exact class names.

| Field | Type | Description |
|---|---|---|
| `id` | INT64 | Primary key |
| `node_id` | VARCHAR(256) | Associated Neo4j module/package node ID |
| `repository_id` | VARCHAR(256) | Repository identifier |
| `capability` | VARCHAR(1024) | Capability description |
| `language` | VARCHAR(64) | Programming language |
| `file_path` | VARCHAR(1024) | Representative file path |
| `hash` | VARCHAR(64) | Content hash |
| `parser_version` | VARCHAR(32) | jarvis-parser version |
| `embedding_model` | VARCHAR(128) | Embedding model identifier |
| `vector` | FLOAT_VECTOR(3072) | Embedding vector |

### `jarvis_readmes`

Embeddings of repository README sections and documentation files.

**Use case:** Answer architectural overview questions using the repository's own documentation as context.

| Field | Type | Description |
|---|---|---|
| `id` | INT64 | Primary key |
| `repository_id` | VARCHAR(256) | Repository identifier |
| `section` | VARCHAR(512) | README section heading |
| `file_path` | VARCHAR(1024) | Path to the README file |
| `hash` | VARCHAR(64) | Content hash |
| `parser_version` | VARCHAR(32) | jarvis-parser version |
| `embedding_model` | VARCHAR(128) | Embedding model identifier |
| `vector` | FLOAT_VECTOR(3072) | Embedding vector |

### `jarvis_configs`

Embeddings of configuration files (YAML, properties, JSON configs).

**Use case:** Answer infrastructure and configuration questions (e.g., "what database connection pool settings are used?").

| Field | Type | Description |
|---|---|---|
| `id` | INT64 | Primary key |
| `node_id` | VARCHAR(256) | Neo4j Configuration node ID |
| `repository_id` | VARCHAR(256) | Repository identifier |
| `config_type` | VARCHAR(64) | yaml, properties, json, etc. |
| `file_path` | VARCHAR(1024) | Repository-relative file path |
| `hash` | VARCHAR(64) | Content hash |
| `parser_version` | VARCHAR(32) | jarvis-parser version |
| `embedding_model` | VARCHAR(128) | Embedding model identifier |
| `vector` | FLOAT_VECTOR(3072) | Embedding vector |

---

## Hybrid Retrieval

JARVIS uses a **multi-stage hybrid retrieval** strategy:

### Stage 1 — Milvus Search (Semantic + BM25)

```
Query (Text)
      │
      ▼
Milvus Hybrid Search
 (Dense Embeddings + Sparse BM25 Keyword Search)
      │
      ▼
Top-K Results Merged Internally by Milvus
```

### Stage 2 — LLM Relevance Filtering

```
Top-K Results
      │
      ▼
LLM Evaluation (Relevance vs Intent)
      │
      ▼
Filtered Set of Highly Relevant Nodes
```

### Stage 3 — Neo4j Neighbor Expansion

```
For each relevant node:
  Neo4j: fetch structural neighbors (CALLS, IMPLEMENTS, DEPENDS_ON)
  Append neighbors to context list
  De-duplicate by node_id

Final result: Comprehensive and structurally sound context graph.
```


This sequential approach ensures high-recall semantic extraction followed by precise, intent-driven filtering, and finally structural completeness.

### Stage 4 — Repository Scope Filter

If `repository_id` is provided, results are filtered to a single repository using Milvus filter expressions:

```python
filter_expr = f'repository_id == "{repository_id}"'
```

---

## Index Configuration

```python
index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}

search_params = {
    "metric_type": "COSINE",
    "params": {"nprobe": 10}
}
```

For production at scale (>10M vectors), consider switching to `HNSW` for lower latency:

```python
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 500}
}
```

---

## Metadata Filtering

All collections support Milvus scalar filtering for pre-search filtering:

```python
# Filter by repository and language
filter_expr = 'repository_id == "repo-123" and language == "java"'

# Filter by package prefix
filter_expr = 'package like "com.example.payment%"'

# Filter by parser version (useful during migrations)
filter_expr = 'parser_version >= "2.0.0"'
```

---

## Embedding Model

All vectors use **OpenAI text-embedding-3-large** (3072 dimensions) by default.

| Property | Value |
|---|---|
| Model | `text-embedding-3-large` |
| Dimensions | 3072 |
| Distance Metric | Cosine similarity |
| Max Input Tokens | 8191 |

Content longer than 8191 tokens is chunked before embedding. The `hash` field enables deduplication — chunks with identical content hashes skip re-embedding.
