# System Design

> **Authoritative engineering document for the JARVIS AI Runtime.**
> Every architectural decision is documented here with its rationale.

---

## 1. Overview

The JARVIS Runtime is a stateless AI reasoning service that operates over externally-indexed code repositories. It receives user queries via HTTP, executes a LangGraph reasoning workflow, and streams structured results back to the client via Server-Sent Events.

The service is **read-only from the perspective of the indexed data stores**. It reads from Neo4j and Milvus — it never writes to them. In future WRITE mode, it writes to repository files via a Git adapter, and signals jarvis-platform to trigger re-indexing.

---

## 2. Architectural Decisions

### ADR-001: Hexagonal Architecture

**Decision:** Use Hexagonal Architecture (Ports & Adapters).

**Rationale:**
- LangGraph nodes must be independently testable without infrastructure dependencies.
- LLM providers, databases, and streaming backends must be replaceable without touching business logic.
- Clear separation prevents the common pattern of Neo4j queries leaking into application services.

**Consequence:**
- All external I/O is wrapped in a Port (ABC).
- The DI container is the only place where ports are bound to adapters.
- Test doubles can replace any adapter without modifying application code.

---

### ADR-002: LangGraph for Workflow Orchestration

**Decision:** Use LangGraph StateGraph as the workflow engine.

**Rationale:**
- LangGraph provides first-class support for stateful, multi-step AI workflows.
- The conditional edge system maps cleanly to READ / WRITE / HYBRID branching.
- The shared state model (JarvisState / GraphStateAnnotation) ensures every node has access to the full execution context.
- LangGraph's checkpointing (future) will enable workflow resumption.

**Consequence:**
- Every step in the workflow is a node — independently testable, independently deployable in theory.
- The graph is compiled once at startup and reused for all requests.
- State mutations happen via partial dict returns, not in-place mutation.

---

### ADR-003: Hybrid Retrieval (Neo4j + Milvus)

**Decision:** Sequential retrieval: Milvus (Semantic+BM25) -> LLM Relevance Filter -> Neo4j Expansion.

**Rationale:**
- Structural (graph) retrieval alone misses semantically similar code with different names.
- Semantic (vector) retrieval alone misses structurally critical nodes (callers, dependents).
- RRF is provably superior to score averaging when combining rankings from different scales.

**Consequence:**
- Initial search uses Milvus for both dense and sparse representations.
- An LLM call is required in the middle of retrieval to filter irrelevant nodes.
- Neo4j is only queried for the verified relevant nodes to expand context.

---

### ADR-004: Server-Sent Events for Streaming

**Decision:** Use SSE (Server-Sent Events) rather than WebSockets.

**Rationale:**
- SSE is unidirectional — the server streams to the client. This matches the JARVIS use case exactly.
- SSE works over HTTP/1.1 without protocol upgrades.
- SSE reconnects automatically on network interruption.
- WebSockets add bidirectional complexity that is not needed.

**Consequence:**
- Each streaming session has an asyncio queue.
- The SSE adapter manages per-session queues.
- In multi-worker deployments, replace with Redis Pub/Sub.

---

### ADR-005: Repository Files as Source of Truth

**Decision:** Repository files are always the source of truth. Neo4j is a derived index.

**Rationale:**
- Neo4j can become stale between index runs.
- Constructing file content from graph properties is unreliable and incomplete.
- Any write operation must operate on the actual file, not a graph representation.

**Consequence:**
- The RepositoryReader node fetches file content from the repository before patch generation.
- Write operations go to files via GitPort, not to Neo4j.
- After writes, jarvis-parser re-indexes changed files to restore Neo4j consistency.

---

### ADR-006: Structured Streaming Events (never raw chain-of-thought)

**Decision:** THINKING events contain only high-level progress summaries. Internal reasoning is never exposed.

**Rationale:**
- Exposing chain-of-thought creates security risks (prompt injection via reasoning).
- Users want to know "what is JARVIS doing?" not "what is the LLM thinking?".
- High-level summaries are more user-friendly than raw LLM output.

**Consequence:**
- ReasoningNode stores internal chain-of-thought in `state.reasoning` (never streamed).
- THINKING events are hand-crafted by each node ("Searching 3 related classes…").
- The `reasoning` field is excluded from API responses.

---

### ADR-007: YAML Configuration with Environment Variable Override

**Decision:** Use layered YAML (base → environment) with environment variable override.

**Rationale:**
- YAML is human-readable and easy to diff in PRs.
- Layered overrides allow development vs. production settings without duplication.
- Environment variable override enables 12-factor app compliance for secrets.

**Consequence:**
- ConfigurationPort abstracts the underlying source.
- Application code never calls `os.environ` directly.
- Secrets are always provided via environment variables — never hardcoded in YAML.

---

### ADR-008: BigQuery for Workflow Auditing

**Decision:** Use Google BigQuery as a centralized auditing warehouse.

**Rationale:**
- JARVIS performs complex, multi-step AI reasoning and source code modifications requiring a robust auditing trail for compliance, security analytics, and metrics.
- Simple application logging is insufficient for querying historical agent actions structured by workflow, step, and repository.

**Consequence:**
- An `AuditPort` isolates the application layer from BigQuery.
- A `BigQueryAdapter` implements this port, using the `insert_rows_json` streaming API to push events in real-time.
- Every LangGraph node receives the `AuditPort` via `RunnableConfig` and emits standard `AuditEvent` payloads (STARTED, COMPLETED, FAILED).

---

## 3. Data Flow

### Read Request

```
1.  Client POSTs to /api/v1/chat/stream with { query, repository_id }
2.  FastAPI creates a session_id and returns the SSE stream URL
3.  Client subscribes to GET /api/v1/chat/stream/{session_id}
4.  FastAPI launches the LangGraph workflow in a background task
5.  LangGraph nodes execute sequentially, emitting SSE events via StreamingPort
6.  Client receives STATUS → THINKING → MARKDOWN (streaming) → CITATION → DONE
7.  SSEAdapter closes the queue after DONE
```

### Write Request (Future)

```
1.  Client POSTs with a write intent ("Add OpenAPI docs to UserController")
2.  Intent classification returns WRITE or HYBRID mode
3.  PatchPlanner determines affected files using Neo4j dependency chain
4.  RepositoryReader fetches current file content from repository
5.  PatchGenerator produces unified diffs via LLM
6.  Validation checks syntax and diff integrity
7.  GitOperations creates branch + PR via GitPort
8.  Response streams PR URL and change summary
9.  jarvis-platform detects PR creation, signals jarvis-parser to re-index
```

---

## 4. State Machine

The JarvisState is the single source of truth for a workflow execution.

```
query (Input)
    │
    ▼
enhanced_query (QueryEnhancement)
    │
    ▼
intent (IntentClassification)
    │
    ▼
execution_plan (Planner)
    │
    ▼
retrieved_nodes (HybridRetrieval) ◄─── (loop from Reflection if need_more_context)
    │
    ▼
context (ContextBuilder)
    │
    ├─── READ ──► reasoning ──► answer ──► citations
    │
    ├─── WRITE ──► patch (skeleton) ──► repository_context ──► patch (with diffs) ──► answer
    │
    └─── HYBRID ──► reasoning ──► patch ──► answer
```

---

## 5. Scalability Considerations

### Stateless Workers

The FastAPI application is stateless — no in-memory state is shared between requests (except the SSEAdapter queue, which is per-process). This allows horizontal scaling with a load balancer.

### Multi-Worker SSE

The current SSEAdapter uses asyncio queues, which are in-memory and process-local. In a multi-worker deployment (multiple Uvicorn workers or pods), a Redis Pub/Sub adapter must replace SSEAdapter to ensure events are delivered regardless of which worker handles the subscription request.

### LangGraph Parallelism

HybridRetrieval now executes sequentially (Milvus -> LLM -> Neo4j). Future nodes may use LangGraph's native parallel branch execution for further throughput improvements across independent workflows.

### Token Budget Management

ContextBuilder enforces a configurable token budget (`workflow.max_context_tokens`). Nodes retrieved with lower relevance scores are truncated first. This prevents context overflow and controls LLM cost.

---

## 6. Security Considerations

| Concern | Mitigation |
|---|---|
| API Key exposure | Keys provided via environment variables only, never YAML |
| Chain-of-thought leakage | THINKING events are hand-crafted summaries — LLM reasoning never streamed |
| Prompt injection via user query | Query Enhancement sanitises input before embedding |
| Neo4j injection | All Cypher queries use parameterised bindings |
| Milvus filter injection | Filter expressions are constructed programmatically, not from raw user input |
| Write safety (future) | Validation node checks for credential patterns, destructive operations |
| Non-root Docker container | Dockerfile creates `jarvis` user with UID 1001 |

---

## 7. Dependency Map

```
domain          ← no dependencies
ports           ← domain only
application     ← domain + ports
adapters        ← domain + ports (never application, never other adapters)
infrastructure  ← domain + ports + adapters + application
app             ← infrastructure + adapters/inbound
```

Any import that violates this dependency map is a bug in the architecture.
