# JARVIS AI Runtime — Technical Documentation

> **Project:** JARVIS (Java/AI Repository Intelligence System)
> **Author:** Vidit Jain
> **Architecture:** Hexagonal (Ports & Adapters) + LangGraph agentic workflow
> **Stack:** Python · FastAPI · LangGraph · OpenAI · Milvus · Neo4j · BigQuery

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Hexagonal Architecture](#2-hexagonal-architecture)
3. [Hybrid Search RAG Pipeline](#3-hybrid-search-rag-pipeline)
4. [BigQuery Auditing](#4-bigquery-auditing)
5. [Milvus — Ports & Adapters Implementation](#5-milvus--ports--adapters-implementation)
6. [Dependency Injection Container](#6-dependency-injection-container)
7. [LangGraph Workflow Graph](#7-langgraph-workflow-graph)
8. [Data Flow Diagrams](#8-data-flow-diagrams)

---

## 1. System Overview

JARVIS is an AI-powered code reasoning and code modification runtime. It allows developers to query a codebase in natural language and receive structured, grounded answers — with full traceability back to the source code.

The system is built around three pillars:

| Pillar | Technology | Role |
|---|---|---|
| **Semantic Knowledge** | Milvus (vector store) | Stores dense embeddings of code elements for semantic search |
| **Structural Knowledge** | Neo4j (graph database) | Stores code relationships (CALLS, IMPLEMENTS, DEPENDS_ON) |
| **LLM Reasoning** | OpenAI GPT-4o | Query enhancement, intent classification, reasoning, and relevance filtering |

### Top-Level Directory Structure

```
src/
├── adapters/           # Concrete port implementations (infrastructure)
│   ├── inbound/        # API endpoints, CLI
│   └── outbound/       # BigQuery, Milvus, Neo4j, OpenAI, SSE, YAML
├── agent/              # LangGraph agentic workflow
│   ├── graph/          # StateGraph definition and edge conditions
│   ├── nodes/          # Individual LangGraph node implementations
│   ├── prompts/        # Prompt templates (separated from logic)
│   └── use_cases/      # Orchestration use cases
├── domain/             # Pure domain layer — zero external dependencies
│   ├── entities/       # Core domain entities
│   ├── events/         # Domain events (AuditEvent, StreamEvent)
│   ├── models/         # Pydantic models (ExecutionPlan, Answer, etc.)
│   ├── state/          # LangGraph state annotations
│   └── value_objects/  # Immutable value types
├── infrastructure/     # DI container, middleware, telemetry
│   └── dependency_injection/container.py
└── ports/              # Abstract interfaces (ABCs)
    ├── audit/          # AuditPort
    ├── configuration/  # ConfigurationPort
    ├── graph/          # GraphPort (Neo4j)
    ├── llm/            # LLMPort (OpenAI)
    ├── repository/     # RepositoryReaderPort
    ├── streaming/      # StreamingPort (SSE)
    └── vector/         # VectorSearchPort (Milvus)
```

---

## 2. Hexagonal Architecture

JARVIS strictly enforces **Hexagonal Architecture** (Ports & Adapters pattern, coined by Alistair Cockburn). The fundamental rule is: **dependencies always point inward**.

### Layer Boundaries

```
╔══════════════════════════════════════════════════════════╗
║                      Domain                              ║
║  No external dependencies. Pure Python + Pydantic.       ║
║  entities/, events/, models/, state/, value_objects/     ║
╚════════════════════════╤═════════════════════════════════╝
                         │ imports from
╔════════════════════════▼═════════════════════════════════╗
║                    Application                           ║
║  LangGraph nodes, use cases, services, prompts.          ║
║  Imports: domain + ports. NEVER adapters directly.       ║
╚════════════════════════╤═════════════════════════════════╝
                         │ implements
╔════════════════════════▼═════════════════════════════════╗
║                      Ports                               ║
║  Abstract interfaces (ABCs). No implementation code.     ║
║  VectorSearchPort, AuditPort, LLMPort, GraphPort…        ║
╚════════════════════════╤═════════════════════════════════╝
                         │ satisfied by
╔════════════════════════▼═════════════════════════════════╗
║                     Adapters                             ║
║  Concrete implementations. OpenAI, Neo4j, Milvus, BQ.   ║
║  Imports: domain + ports. NEVER application layer.       ║
╚════════════════════════╤═════════════════════════════════╝
                         │ wired by
╔════════════════════════▼═════════════════════════════════╗
║                  Infrastructure                          ║
║  DI Container, Middleware, Telemetry.                    ║
║  The ONLY layer that knows all other layers.             ║
╚══════════════════════════════════════════════════════════╝
```

### Import Rules (Enforced by Convention)

**Allowed:**
```python
# Inside any agent/nodes/*.py file
from domain.state.graph_state import GraphStateAnnotation   # ✅ domain
from domain.events.audit_event import AuditEvent           # ✅ domain event
from ports.vector import VectorSearchPort                   # ✅ port
from ports.audit import AuditPort                           # ✅ port
```

**Forbidden:**
```python
# Inside any agent/nodes/*.py file
from adapters.outbound.milvus.milvus_adapter import MilvusAdapter  # ❌ adapter in app
from pymilvus import MilvusClient                                   # ❌ external lib in app
from google.cloud import bigquery                                   # ❌ infra in app
```

### Key Design Benefits

| Benefit | How JARVIS Achieves It |
|---|---|
| **Testability** | Node tests inject mock ports — zero real I/O needed |
| **Swappable backends** | Switch from Milvus → Pinecone by writing one new adapter |
| **Swappable LLMs** | Replace OpenAI with Anthropic without touching any node code |
| **Clean domain** | `domain/` has zero third-party imports — forever stable |

---

## 3. Hybrid Search RAG Pipeline

The hybrid search RAG (Retrieval-Augmented Generation) is the core intelligence mechanism of JARVIS. It uses a **4-stage sequential retrieval process** to achieve both high recall and high precision.

### 3.1 Pipeline Overview

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│  Stage 0 — Query Enhancement        │
│  LLM enriches the raw query with    │
│  technical synonyms, context, and   │
│  domain-specific terminology.       │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Stage 1 — Milvus Hybrid Search     │
│  Dense (semantic) + Sparse (BM25)   │
│  Searches across 5 collections      │
│  simultaneously. Returns Top-K      │
│  merged and internally reranked.    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Stage 2 — LLM Relevance Filtering  │
│  GPT-4o evaluates each candidate    │
│  against the intent and enhanced    │
│  query. Discards low-confidence     │
│  results.                           │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Stage 3 — Neo4j Graph Expansion    │
│  For each surviving node, fetch     │
│  structural neighbors from Neo4j    │
│  (CALLS, IMPLEMENTS, DEPENDS_ON).   │
│  De-duplicates by node_id.          │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│  Stage 4 — Context Assembly         │
│  ContextBuilderNode formats all     │
│  retrieved nodes into a structured  │
│  context document for the LLM       │
│  reasoning step. Applies token      │
│  budget management.                 │
└─────────────────────────────────────┘
```

### 3.2 Stage 1 — Milvus Hybrid Search (Dense + BM25)

Milvus natively supports **hybrid retrieval** by combining:

- **Dense embeddings** (semantic similarity) — uses OpenAI `text-embedding-3-large` (3072-dimensional FLOAT_VECTOR).
- **Sparse BM25 embeddings** (keyword/lexical similarity) — captures exact terminology matches for technical identifiers.

These are merged **inside Milvus** using internal reranking before returning results to JARVIS.

#### Searched Collections

| Collection | What It Contains | Use Case |
|---|---|---|
| `jarvis_methods` | Method-level embeddings (signature + LLM summary) | "Find methods that do rate limiting" |
| `jarvis_classes` | Class-level embeddings (all methods + docstrings) | "Find authentication-related classes" |
| `jarvis_capabilities` | Business capability descriptions from module clusters | "How does this service handle payments?" |
| `jarvis_readmes` | README sections and documentation files | "What does this repository do?" |
| `jarvis_configs` | Configuration file embeddings (YAML, JSON, properties) | "What are the database pool settings?" |

#### Repository Scoping

If `repository_id` is provided in the state, all Milvus queries are pre-filtered using scalar metadata filtering:

```python
filter_expr = f'repository_id == "{repository_id}"'
```

This ensures retrieved results are always from the correct repository and prevents cross-repository contamination.

#### Index Configuration

```python
# Default: IVF_FLAT for balanced performance
index_params = {
    "metric_type": "COSINE",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}

search_params = {
    "metric_type": "COSINE",
    "params": {"nprobe": 10}
}

# Production at scale (>10M vectors): switch to HNSW
index_params = {
    "metric_type": "COSINE",
    "index_type": "HNSW",
    "params": {"M": 16, "efConstruction": 500}
}
```

### 3.3 Stage 2 — LLM Relevance Filtering

After Milvus returns top-K results, the raw candidates are passed to `GPT-4o` with the original intent and enhanced query. The LLM evaluates each candidate and selects only those that are **genuinely relevant** to the user's intent.

This is the precision layer of the pipeline — Milvus provides high recall, the LLM provides high precision.

### 3.4 Stage 3 — Neo4j Structural Expansion

For each LLM-confirmed relevant node, JARVIS queries **Neo4j** to retrieve its immediate structural neighbors:

- `CALLS` — methods or functions this node invokes
- `IMPLEMENTS` — interfaces or abstract classes this node satisfies
- `DEPENDS_ON` — packages, classes, or modules this node depends on

Results are de-duplicated by `node_id` to prevent context explosion. This ensures the LLM gets not just the directly relevant code, but the **full structural context** needed to reason accurately.

### 3.5 Reflection Loop

After the initial Reasoning step, the **ReflectionNode** evaluates whether the generated answer is sufficiently grounded. If `need_more_context = True`, the workflow re-enters `HybridRetrieval` with:

- A deeper retrieval depth
- Expanded collection scope
- Increased hop count for Neo4j traversal

```
reasoning → reflection → (need_more_context?) → hybrid_retrieval → context_builder → reasoning
                       → (done?) → response
```

### 3.6 Metadata Filtering Examples

```python
# Filter by repository and language
filter_expr = 'repository_id == "repo-123" and language == "java"'

# Filter by package prefix
filter_expr = 'package like "com.example.payment%"'

# Filter by parser version (useful during migrations)
filter_expr = 'parser_version >= "2.0.0"'
```

### 3.7 HybridRetrievalNode — Implementation Detail

**File:** [`src/agent/nodes/hybrid_retrieval.py`](file:///Users/viditjain/Downloads/jarvis-main/src/agent/nodes/hybrid_retrieval.py)

**Position in Workflow:** `Planner → [HybridRetrieval] → ContextBuilder`

**State Inputs:**
| Field | Type | Description |
|---|---|---|
| `enhanced_query` | `str` | Enriched query text from QueryEnhancementNode |
| `execution_plan` | `dict` | Plan with retrieval parameters (collections, top_k, hops) |
| `repository_id` | `Optional[str]` | Scope restriction for Milvus and Neo4j |
| `iteration` | `int` | Reflection iteration count (affects retrieval depth) |

**State Outputs:**
| Field | Type | Description |
|---|---|---|
| `retrieved_nodes` | `List[dict]` | Final de-duplicated and expanded node set |
| `tool_results` | `List[dict]` | ToolResult records for observability |

**Design Principles:**
- Contains **no Cypher queries** — those live exclusively in `Neo4jAdapter`
- Contains **no Milvus filter expressions** — those live exclusively in `MilvusAdapter`
- Contains **no prompt text** — prompts live in `agent/prompts/`
- Emits an `AuditEvent` at the start of every execution for BigQuery tracing

---

## 4. BigQuery Auditing

JARVIS implements a **fire-and-forget structured audit trail** for every workflow step. Every LangGraph node emits an `AuditEvent` at execution start. The `BigQueryAdapter` streams these events to Google BigQuery using the streaming insert API.

### 4.1 The AuditEvent Domain Model

**File:** [`src/domain/events/audit_event.py`](file:///Users/viditjain/Downloads/jarvis-main/src/domain/events/audit_event.py)

```python
class AuditEvent(BaseModel):
    workflow_id: str        # Unique ID for the full user request / session
    step_name:   str        # LangGraph node name (e.g. "HybridRetrieval")
    status:      str        # STARTED | COMPLETED | FAILED
    timestamp:   str        # ISO 8601 UTC (auto-generated)
    repository_id: Optional[str]     # Repository scope, if any
    metadata:    Dict[str, Any]      # Arbitrary structured context
    error:       Optional[str]       # Error message if FAILED
```

`AuditEvent` is a pure Pydantic model in the domain layer — zero infrastructure dependencies.

### 4.2 The AuditPort Interface

**File:** [`src/ports/audit/__init__.py`](file:///Users/viditjain/Downloads/jarvis-main/src/ports/audit/__init__.py)

```python
class AuditPort(ABC):
    @abstractmethod
    def log_event(self, event: AuditEvent) -> None:
        """Record a single structured audit event."""
        ...
```

The port is intentionally **synchronous** (`log_event` not `async`) — audit logging must never block the critical request path. The concrete adapter handles async concerns internally.

### 4.3 The BigQueryAdapter

**File:** [`src/adapters/outbound/bigquery/bigquery_adapter.py`](file:///Users/viditjain/Downloads/jarvis-main/src/adapters/outbound/bigquery/bigquery_adapter.py)

**Implements:** `AuditPort`

```python
class BigQueryAdapter(AuditPort):
    def __init__(self, project_id, dataset_id, table_id):
        self._table_ref = f"{project_id}.{dataset_id}.{table_id}"
        self._client = bigquery.Client(project=project_id)

    def log_event(self, event: AuditEvent) -> None:
        row_to_insert = event.model_dump()
        errors = self._client.insert_rows_json(self._table_ref, [row_to_insert])
        if errors:
            logger.error(f"Failed to insert: {errors}")
```

#### Key Design Decisions

| Decision | Rationale |
|---|---|
| **`insert_rows_json` streaming API** | Events are immediately queryable in BigQuery — no batch delay |
| **Graceful degradation on init failure** | If BQ credentials are unavailable, `_client = None` and auditing is silently disabled — the application continues |
| **Exception swallowing** | Audit failures are logged but never propagated — auditing must never break the user-facing request path |
| **`model_dump()` serialization** | Pydantic's `model_dump()` produces a BigQuery-compatible dict directly from the domain event |

#### BigQuery Table Schema

```sql
CREATE TABLE `{project}.{dataset}.{table}` (
  workflow_id    STRING    NOT NULL,
  step_name      STRING    NOT NULL,
  status         STRING    NOT NULL,
  timestamp      TIMESTAMP NOT NULL,
  repository_id  STRING,
  metadata       JSON,
  error          STRING
);
```

#### Configuration (YAML)

```yaml
database:
  bigquery:
    project_id: "my-gcp-project"
    dataset_id: "jarvis_audit"
    table_id:   "workflow_events"
```

#### Environment Variable Override

Following the convention `DATABASE_BIGQUERY_PROJECT_ID`, etc., these can be overridden via environment variables for production deployments.

### 4.4 Audit Pattern in Every Node

Every LangGraph node follows this consistent auditing pattern:

```python
class HybridRetrievalNode:
    @staticmethod
    async def run(state: GraphStateAnnotation, config: RunnableConfig) -> Dict[str, Any]:
        container = config["configurable"]["container"]
        audit = container.audit   # ← AuditPort (resolved to BigQueryAdapter by DI)

        # 1. Emit STARTED event at the top of every node
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="HybridRetrieval",
            status="STARTED",
            repository_id=state.get("repository_id"),
        ))

        # 2. ... execute node logic ...

        # 3. Emit COMPLETED (or FAILED with error= field)
        audit.log_event(AuditEvent(
            workflow_id=state.get("session_id", "unknown"),
            step_name="HybridRetrieval",
            status="COMPLETED",
            metadata={"nodes_retrieved": len(retrieved_nodes)},
        ))
```

### 4.5 Complete List of Audited Steps

| Node | Audit Step Name | When Emitted |
|---|---|---|
| `RelevanceNode` | `Relevance` | Start of relevance check |
| `QueryEnhancementNode` | `QueryEnhancement` | Start of query enrichment |
| `IntentClassificationNode` | `IntentClassification` | Start of intent classification |
| `PlannerNode` | `Planner` | Start of execution planning |
| `HybridRetrievalNode` | `HybridRetrieval` | Start of retrieval |
| `ContextBuilderNode` | `ContextBuilder` | Start of context assembly |
| `OperationRouterNode` | `OperationRouter` | Start of routing decision |
| `ReasoningNode` | `Reasoning` | Start of LLM reasoning |
| `ReflectionNode` | `Reflection` | Start of self-reflection |
| `ResponseNode` | `Response` | Start of answer generation |
| `PatchPlannerNode` | `PatchPlanner` | Start of patch planning |
| `PatchGeneratorNode` | `PatchGenerator` | Start of code generation |
| `ValidationNode` | `Validation` | Start of patch validation |
| `GitOperationsNode` | `GitOperations` | Start of git commit/PR |

### 4.6 Querying Audit Logs in BigQuery

```sql
-- Full trace for a single workflow request
SELECT step_name, status, timestamp, metadata
FROM `project.jarvis_audit.workflow_events`
WHERE workflow_id = 'session-abc-123'
ORDER BY timestamp;

-- Find all failed steps in the last 24 hours
SELECT workflow_id, step_name, error, timestamp
FROM `project.jarvis_audit.workflow_events`
WHERE status = 'FAILED'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR);

-- Average time per step (requires COMPLETED events with timestamps)
SELECT step_name, COUNT(*) as executions
FROM `project.jarvis_audit.workflow_events`
WHERE status = 'STARTED'
GROUP BY step_name
ORDER BY executions DESC;
```

---

## 5. Milvus — Ports & Adapters Implementation

### 5.1 The VectorSearchPort (Abstract Contract)

**File:** [`src/ports/vector/__init__.py`](file:///Users/viditjain/Downloads/jarvis-main/src/ports/vector/__init__.py)

`VectorSearchPort` is the **sole interface** through which the application layer accesses Milvus. Application nodes never import `pymilvus` — they depend only on this abstract contract.

```python
class VectorSearchPort(ABC):

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        collection: str,
        *,
        top_k: int = 10,
        filter_expr: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Approximate nearest-neighbor vector search on a pre-computed embedding."""
        ...

    @abstractmethod
    async def search_by_text(
        self,
        query_text: str,
        collection: str,
        *,
        top_k: int = 10,
        filter_expr: Optional[str] = None,
        repository_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Convenience: embed the query text, then search. Delegates embedding to LLMPort."""
        ...

    @abstractmethod
    async def hybrid_search(
        self,
        query_text: str,
        collections: List[str],
        *,
        top_k: int = 10,
        repository_id: Optional[str] = None,
        rerank: bool = True,
    ) -> List[Dict[str, Any]]:
        """Semantic (dense) + keyword (BM25 sparse) hybrid search across multiple collections."""
        ...

    @abstractmethod
    async def get_collections(self) -> List[str]:
        """List all available Milvus collections."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify Milvus connectivity."""
        ...
```

#### Method Contracts Summary

| Method | Primary Use | Note |
|---|---|---|
| `search()` | When embedding is pre-computed | Direct ANN lookup — fastest |
| `search_by_text()` | Single-collection semantic search | Internally calls `LLMPort.embed()` |
| `hybrid_search()` | Multi-collection dense+BM25 | Used by `HybridRetrievalNode` |
| `get_collections()` | Health checks, discovery | Returns `List[str]` |
| `health_check()` | Startup readiness probes | Returns `True` if reachable |

### 5.2 The MilvusAdapter (Concrete Implementation)

**File:** [`src/adapters/outbound/milvus/milvus_adapter.py`](file:///Users/viditjain/Downloads/jarvis-main/src/adapters/outbound/milvus/milvus_adapter.py)

**Implements:** `VectorSearchPort`

The adapter uses the **high-level `MilvusClient`** API from `pymilvus`. This is a deliberate choice over the low-level `Collection` API — it reduces boilerplate and manages connection lifecycle automatically.

```python
class MilvusAdapter(VectorSearchPort):
    def __init__(
        self,
        uri: str,
        token: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        self._client = MilvusClient(uri=uri, token=token)
        self._timeout = timeout
```

#### Adapter Responsibilities (Infrastructure Only)

The adapter handles **exclusively** infrastructure concerns:

| Responsibility | Where It Lives |
|---|---|
| Milvus connection management | `MilvusAdapter.__init__()` |
| Filter expression construction | `MilvusAdapter.hybrid_search()` |
| RRF (Reciprocal Rank Fusion) reranking | `MilvusAdapter.hybrid_search()` |
| Collection schema knowledge | `MilvusAdapter` docstring |
| `pymilvus` API invocation | All `MilvusAdapter` methods |

The adapter does **NOT** handle:

| NOT Here | Where It Actually Lives |
|---|---|
| Embedding generation | `OpenAIAdapter` (via `LLMPort`) |
| Retrieval strategy decisions | `PlannerNode` |
| Result interpretation | `HybridRetrievalNode`, `ReasoningNode` |
| Domain model construction | Kept as plain dicts — no domain objects |

#### Supported Collections (Documented in Adapter)

```
jarvis_methods       → Method-level embeddings
jarvis_classes       → Class-level embeddings
jarvis_capabilities  → Business capability embeddings
jarvis_readmes       → Repository README embeddings
jarvis_configs       → Configuration file embeddings
```

### 5.3 Collection Schemas

#### `jarvis_methods`

| Field | Type | Description |
|---|---|---|
| `id` | `INT64` | Primary key (auto-generated) |
| `node_id` | `VARCHAR(256)` | Neo4j element ID (cross-reference key) |
| `repository_id` | `VARCHAR(256)` | Repository identifier |
| `package` | `VARCHAR(512)` | Package/module name |
| `class` | `VARCHAR(512)` | Fully qualified class name |
| `method` | `VARCHAR(512)` | Method signature |
| `language` | `VARCHAR(64)` | Programming language |
| `file_path` | `VARCHAR(1024)` | Repository-relative file path |
| `hash` | `VARCHAR(64)` | SHA-256 of method content (dedup key) |
| `parser_version` | `VARCHAR(32)` | jarvis-parser version tag |
| `embedding_model` | `VARCHAR(128)` | Embedding model identifier |
| `vector` | `FLOAT_VECTOR(3072)` | `text-embedding-3-large` vector |

#### `jarvis_classes`

Same as `jarvis_methods` but without `method` field — represents the full class with all methods and docstrings collapsed into the embedding.

#### `jarvis_capabilities`

| Field | Type | Description |
|---|---|---|
| `id` | `INT64` | Primary key |
| `node_id` | `VARCHAR(256)` | Neo4j module/package node ID |
| `repository_id` | `VARCHAR(256)` | Repository identifier |
| `capability` | `VARCHAR(1024)` | Natural language capability description |
| `language` | `VARCHAR(64)` | Programming language |
| `file_path` | `VARCHAR(1024)` | Representative file path |
| `vector` | `FLOAT_VECTOR(3072)` | Embedding vector |

#### `jarvis_readmes` and `jarvis_configs`

Both follow the base schema (`id`, `repository_id`, `file_path`, `hash`, `parser_version`, `embedding_model`, `vector`) with minor additions (`section` for readmes, `config_type` for configs).

### 5.4 Embedding Model

All vectors use **OpenAI `text-embedding-3-large`**:

| Property | Value |
|---|---|
| Model | `text-embedding-3-large` |
| Dimensions | **3072** |
| Distance Metric | **Cosine similarity** |
| Max Input Tokens | 8,191 |

Content exceeding 8,191 tokens is **chunked** before embedding. The `hash` field enables deduplication — chunks with identical content hashes skip re-embedding at index time.

### 5.5 Port → Adapter Binding Rules

```
VectorSearchPort  (ports/vector/__init__.py)
        │
        └── MilvusAdapter  (adapters/outbound/milvus/milvus_adapter.py)

AuditPort         (ports/audit/__init__.py)
        │
        └── BigQueryAdapter  (adapters/outbound/bigquery/bigquery_adapter.py)

LLMPort           (ports/llm/__init__.py)
        │
        └── OpenAIAdapter  (adapters/outbound/openai/openai_adapter.py)

GraphPort         (ports/graph/__init__.py)
        │
        └── Neo4jAdapter  (adapters/outbound/neo4j/neo4j_adapter.py)
```

---

## 6. Dependency Injection Container

**File:** [`src/infrastructure/dependency_injection/container.py`](file:///Users/viditjain/Downloads/jarvis-main/src/infrastructure/dependency_injection/container.py)

The `Container` class is the **only place** in the codebase where Ports are bound to their concrete Adapters. No other file performs this binding.

### 6.1 Container Design

```python
class Container:
    """
    Lazy initialization — adapters are created on first access.
    Prevents slow startup during testing.
    """

    @property
    def vector(self) -> VectorSearchPort:
        if self._vector is None:
            cfg = self.configuration
            self._vector = MilvusAdapter(
                uri=cfg.get_required("database.milvus.uri"),
                token=cfg.get("database.milvus.token"),
                timeout=float(cfg.get("database.milvus.timeout", 30.0)),
            )
        return self._vector

    @property
    def audit(self) -> AuditPort:
        if self._audit is None:
            db_config = self.configuration.get_config("database.bigquery")
            self._audit = BigQueryAdapter(
                project_id=db_config.get("project_id", ""),
                dataset_id=db_config.get("dataset_id", ""),
                table_id=db_config.get("table_id", ""),
            )
        return self._audit
```

**Return types are always the Port interface, not the Adapter class.** This is enforced by the type annotations — callers receive `VectorSearchPort`, `AuditPort`, etc.

### 6.2 FastAPI Integration

```python
@lru_cache(maxsize=1)
def get_container() -> Container:
    """Singleton container — one instance per process lifetime."""
    return Container()
```

The `@lru_cache` ensures only one container instance exists. FastAPI routes use `Depends(get_container)`.

### 6.3 LangGraph Integration

The container is injected into the LangGraph `RunnableConfig.configurable` dict:

```python
config = {
    "configurable": {
        "container": get_container()
    }
}
graph.invoke(state, config=config)
```

Inside every node:
```python
container = config["configurable"]["container"]
vector: VectorSearchPort = container.vector   # Returns MilvusAdapter typed as VectorSearchPort
audit: AuditPort = container.audit            # Returns BigQueryAdapter typed as AuditPort
```

---

## 7. LangGraph Workflow Graph

**File:** [`src/agent/graph/__init__.py`](file:///Users/viditjain/Downloads/jarvis-main/src/agent/graph/__init__.py)

### 7.1 Execution Modes

| Mode | Trigger | Workflow Path |
|---|---|---|
| **READ** | Explain, answer, analyze queries | Enhancement → Intent → Plan → Retrieval → Context → Reasoning → Reflection → Response |
| **WRITE** | Code modification, generation queries | Enhancement → Intent → Plan → Retrieval → Context → PatchPlanner → RepoReader → PatchGen → Validation → Git → Response |
| **HYBRID** | Mixed understand-then-modify queries | Enhancement → Intent → Plan → Retrieval → Context → Reasoning → PatchPlanner → PatchGen → Validation → Response |

### 7.2 Graph Topology

```
START
  │
  ▼
[Relevance] ──── irrelevant ──────────────────────────► [Response] → END
  │
  │ relevant
  ▼
[QueryEnhancement]
  │
  ▼
[IntentClassification]
  │
  ▼
[Planner]
  │
  ▼
[HybridRetrieval] ◄─────────────────────────────────────────────────┐
  │                                                                  │
  ▼                                                                  │
[ContextBuilder]                                                     │
  │                                                                  │
  ▼                                                                  │
[OperationRouter]                                                    │
  │                                                                  │
  ├── READ ──►  [Reasoning] → [Reflection] ── need_more_context ────┘
  │                               │
  │                               └── done ──► [Response] → END
  │
  └── WRITE ─► [PatchPlanner] → [RepoReader] → [PatchGenerator]
                                                      │
                                               [Validation]
                                                      │
                                    ┌── invalid ──────┘
                                    │
                                    └── valid ──► [GitOperations] → [Response] → END
```

### 7.3 Node Toggle System

Every node is wrapped in `_make_toggleable()`, which checks configuration before executing:

```python
enabled = container.config.get(f"workflow.nodes_enabled.{node_name}", True)
if not enabled:
    return {}  # pass-through (skip this node)
```

This allows disabling specific nodes for:
- A/B testing
- Debugging (disable reflection to reduce LLM calls)
- Cost control (disable query enhancement in batch mode)

---

## 8. Data Flow Diagrams

### 8.1 Hybrid Search RAG — Full Data Flow

```
User HTTP Request
    │
    │ query_text, repository_id, session_id
    ▼
FastAPI Inbound Adapter
    │
    │ Injects Container via Depends()
    ▼
LangGraph Graph.invoke(state, config)
    │
    ├──[Relevance]──────────────────── AuditPort.log_event(STARTED)
    │                                  LLMPort.complete() [guardrail]
    │
    ├──[QueryEnhancement]────────────── AuditPort.log_event(STARTED)
    │                                   LLMPort.complete() → enhanced_query
    │
    ├──[IntentClassification]─────────── AuditPort.log_event(STARTED)
    │                                    LLMPort.complete() → intent {execution_mode}
    │
    ├──[Planner]─────────────────────── AuditPort.log_event(STARTED)
    │                                   LLMPort.complete() → execution_plan
    │
    ├──[HybridRetrieval]─────────────── AuditPort.log_event(STARTED)
    │   │
    │   ├── VectorSearchPort.hybrid_search(enhanced_query, collections=[...])
    │   │       └── MilvusAdapter → pymilvus (Dense ANN + BM25 Sparse) → Top-K
    │   │
    │   ├── LLMPort.complete() → filter candidates → relevant_nodes
    │   │
    │   └── GraphPort.get_neighbours(node_id) for each relevant_node
    │           └── Neo4jAdapter → Cypher traversal → expanded neighbors
    │
    ├──[ContextBuilder]──────────────── AuditPort.log_event(STARTED)
    │                                   Format nodes → context string
    │
    ├──[Reasoning]───────────────────── AuditPort.log_event(STARTED)
    │                                   LLMPort.complete(context) → reasoning
    │
    ├──[Reflection]─────────────────────AuditPort.log_event(STARTED)
    │                                   Evaluate → need_more_context?
    │
    └──[Response]────────────────────── AuditPort.log_event(STARTED)
                                        StreamingPort.emit(answer)
                                        SSEAdapter → SSE stream → User
```

### 8.2 BigQuery Audit Event Flow

```
[Any LangGraph Node]
        │
        │ container.audit.log_event(AuditEvent(...))
        ▼
    AuditPort.log_event()
        │
        │ (resolved by DI Container)
        ▼
    BigQueryAdapter.log_event()
        │
        │ event.model_dump() → dict
        ▼
    bigquery.Client.insert_rows_json()
        │
        │ streaming insert (immediately queryable)
        ▼
    BigQuery Table: project.dataset.table
```

### 8.3 Milvus Adapter Initialization Flow

```
[Application Startup]
        │
        │ get_container() → Container()
        ▼
    Container._vector = None  (lazy)
        │
        │ First access: container.vector
        ▼
    YamlConfigurationAdapter.get_required("database.milvus.uri")
        │
        ▼
    MilvusAdapter(uri=..., token=..., timeout=...)
        │
        │ pymilvus.MilvusClient(uri=uri, token=token)
        ▼
    VectorSearchPort instance ready
        │
        │ Returned typed as VectorSearchPort (not MilvusAdapter)
        ▼
    [HybridRetrievalNode uses VectorSearchPort interface only]
```

---

---

You were assigned a task to implement **incremental Milvus vector store updates** for the `jarvis-mind-agent` Python service. The core problem was: when the Java parser (`jarvis-mind-parser`) performs an incremental Neo4j graph refresh — creating, updating, or deleting code nodes — the Milvus vector store was never updated to reflect those changes, causing stale or ghost embeddings. The solution required two sides: the **Python agent** needed a new endpoint to receive the diff and re-embed accordingly, and the **Java parser** needed to call that endpoint after every graph refresh.

On the **Python agent side**, you created a brand new service `UpdateCodeService` in `agent/src/jarvis_mind_agent/services/updation/update_code_service.py`. This service accepts four lists of Neo4j node UUIDs — `nodes_created`, `nodes_updated`, `nodes_deleted`, and `deleted_parent_ids` — and runs a full cascading re-embedding pipeline. The pipeline first deletes stale rows from **all five Milvus collections** (`code_body`, `code_description`, `packages_description`, `modules_description`, `services_description`) upfront for all updated and deleted IDs — this fixed "Gap 1" where deleted package/module/service rows were left as ghost entries. Then it re-embeds surviving code nodes at the CODE level, and cascades upward: for each affected parent package, it fetches **all sibling children** (not just the changed ones) via a new `_fetch_all_children()` method, aggregates their descriptions into the package body using `UpdateParentNodesStep`, generates a fresh LLM description, writes it back to Neo4j via `UpdateNodesStep` (so the next cascade level reads fresh data — fixing the staleness bug), generates embeddings, and upserts into Milvus. This same cascade pattern repeats for modules and then services. Each cascade level is **independent** — modules and services run even if no packages were affected — fixing a bug where nested `if` guards were blocking higher-level cascades. A `_categorize_by_label()` method fetches each UUID in `deleted_parent_ids` from Neo4j, checks its label, and routes it to the correct cascade level (package, module, or service), because `deleted_parent_ids` are the **first surviving ancestors** of deleted nodes (computed by the parser before deletion), not the deleted nodes themselves.

You also added an abstract `delete_rows()` method to the `VectorStore` port interface, and implemented it in both `milvus_store.py` and `hsr_milvus_store.py` using element ID filter expressions. You added the `deleted_parent_ids` field to `IngestionUpdateModel` in `server/schemas.py`, registered the `UpdateCodeService` in `server/builder.py`, and wired up the new `POST /updation/update` route. You also fixed a pre-existing bug in `generate_embeddings_nodes.py` and `generate_embeddings_pages.py` where old field names (`content_embeddings`, `qualified_name_embeddings`) were still being used after the schema renamed them to `content_dense_embeddings`, `content_sparse_embeddings`, `qualified_name_dense_embeddings`, and `qualified_name_sparse_embeddings`.

On the **Java parser side** (in the `jarvis-mind-parser` repo on branch `dev/refresh_graph`), you modified `Neo4JService.java` to introduce a `NodeRecord` inner record holding both hash and UUID, changed `loadExistingNodeHashes` to return `Map<String, NodeRecord>` by including `n.id` in the Cypher query, made `refreshGraph()` return an `AgentUpdatePayload` containing the four UUID lists, and added logic to build a `childToParent` map from CONTAINS relations to compute `deletedParentIds` before deletion. You added a new `CallbackService.java` that POSTs a JSON payload to `{agentEndpoint}/updation/update`. In `PipelineService.java`, you injected `CallbackService` and wired it to call `sendAgentUpdate()` after every `refreshGraph()`, conditionally only when `agentEndpoint` is configured. You also added `agentEndpoint` to `AppConfig.java` reading from `app.agent_endpoint`.

For testing, you wrote **69 unit tests** in `agent/tests/databases/vector/test_update_code_service_cascade.py` covering: `UpdateCodeConfig` construction, the `run()` method lock/no-op behavior, upfront deletion from all 5 collections, CODE-level insert logic, package/module/service cascade flows, `_categorize_by_label()` routing, `_fetch_all_children()` deduplication, `_update_collection()` with and without description generation, and edge cases like empty inputs and no surviving children. You used `model_construct()` to bypass Pydantic validation (since `GraphStore`, `VectorStore` are TYPE_CHECKING-only imports), and built an `async_step_class()` helper so mocked pipeline steps could be properly awaited. Total test suite reached **200 passing tests**.

All of this was committed on a new branch `feature/milvus-updation-cascading`, derived from the `hybrid-search-rag` branch, and pushed to GitHub with `git push --set-upstream origin feature/milvus-updation-cascading`.






Here's the full picture of everything built in this session:

You started by understanding the Cosmos DB → BigQuery pipeline in depth — how pipeline/run.py orchestrates a change-feed replication from Azure Cosmos (jarvis-conversations) into five flattened BigQuery tables (conversations, messages, summaries, feedback, feedback_v2) using a staging-table + MERGE pattern in pipeline/bq_sink.py that is fully idempotent (safe to replay), ordered by cosmos_ts (Cosmos's server-side _ts timestamp), and partitioned by ingested_at with clustering on id for query efficiency. You learned what CSAT, p50/p95 latency, KPIs, idempotent upserts, staging tables, and the BigQuery schema shapes all mean.

From there, you commissioned a full Jarvis Intelligence leadership dashboard — an immersive admin analytics page built as a single FastAPI route (GET /dashboard) serving a self-contained ECharts HTML page (app/static/dashboard.html), backed by a JSON API (GET /dashboard/api/analytics), with no separate build toolchain. The analytics layer lives in app/analytics/ — config.py (soft BigQuery config loaded from .env via pydantic-settings, never crashes boot), queries.py (all BigQuery queries, reusing pipeline/auth.py's three-tier credential resolution), demo.py (deterministic synthetic data for demos/local dev), and pricing.py (token-count × rate → USD cost). The page was wired into the existing FastAPI app in app/main.py alongside the /v1 conversation API, with the Cosmos startup made fault-tolerant (logs a loud warning but keeps serving so the dashboard works locally without Cosmos creds). The dashboard serves eight KPI cards (conversations, messages, active users, cost, CSAT, TTFT p95, tool calls, tokens), a daily usage trend (messages/conversations/users area chart), cost by model (donut), spend + adoption by tenant (dual-axis bar+line), model mix by tenant (stacked bar), latency by model (p50 vs p95 bar), CSAT by tenant (colour-graded bar), and agent activity + tool calls (grouped bar) — all interactive ECharts with tooltips, legends, zoom.

You then added full three-level filtering: tenant (dropdown), LLM model (dropdown), workflow mode (agentConfig.mode — code, debug, data, feature — discovered via live data inspection and requiring a double-encoding unwrap since the pipeline serialises JSON columns as json.dumps of an already-serialised value), and a header user typeahead search (250ms debounced, server-side BigQuery LIKE search, scales to thousands of users, shows a suggestion dropdown with tenant/msgs/cost/top-model per result). The user-dropdown was removed and replaced with the search, and a 👥 Users button opens a slide-in drawer with a live searchable leaderboard table (userId, tenant, messages, conversations, cost, top model, last active) → click any row → user detail drill-down (mini KPIs, mode usage pie, daily activity bar chart, recent conversations table, "Filter dashboard by this user" button that scopes all charts to that user). All filters stack and apply to every chart and the users list simultaneously.

You discovered the real Cosmos and BigQuery creds — service account svc-atlas-intl-genai-dev@wmt-atlas-genai-dev — wrote them to .gitignore-protected files (.env and secrets/bq-sa.json), corrected the dataset from the default guess to the real conversation_service_dev, and ran python3 -m pipeline.run --reset (capped to 5000 docs/container) to pull real jarvis-conversations data into BigQuery, landing 334 conversations, 1089 messages, 79 feedback rows etc. — confirming live data (real users like n0p0aup, s0s1ea0, real models claude-opus-4-5-20251101, gpt-5.1, real agents mind, debugger, assist, real modes code, debug, data, feature). The user count discrepancy (KPI showed 11, list showed 9) was fixed by removing the role='assistant' restriction from the user-list query so both count all distinct users consistently. A Cache-Control: no-store header was added to the dashboard page response so browser caching never hides code changes again.

The pricing module was overhauled to use prefix/family matching (_rate_for()) so versioned model IDs like claude-opus-4-5-20251101 automatically inherit the claude-opus family rate without needing explicit entries — and DEFAULT_PRICE was corrected from (2.00, 8.00) (per-1K, ~1000× too high) to (0.003, 0.015) (same scale as your real rates), which previously inflated the total cost to a fake $2.9M — now correctly $601 against real token data. Zero calls fall to default; all 485 assistant calls map to real rates.

Finally, the entire dashboard was converted to light mode — white/grey panels (#f4f6fb background, #ffffff cards), dark-slate text (#1f2a3d), blue/purple accents at reduced opacity glows, light chart axis/gridline/tooltip colours, and a light drawer — with JS verified via node --check (0 syntax errors) throughout.
