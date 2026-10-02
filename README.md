# JARVIS Runtime

> **AI Reasoning Engine for Indexed Code Repositories**
> Enterprise-grade · Hexagonal Architecture · LangGraph · Streaming
> **Author:** Vidit Jain

---

## Table of Contents

1. [Vision](#vision)
2. [Responsibilities](#responsibilities)
3. [System Boundaries](#system-boundaries)
4. [High-Level Architecture](#high-level-architecture)
5. [Hexagonal Architecture](#hexagonal-architecture)
6. [Folder Structure](#folder-structure)
7. [Dependency Rules](#dependency-rules)
8. [Ports & Adapters](#ports--adapters)
9. [Unified Agent Architecture](#unified-agent-architecture)
10. [Read Workflow](#read-workflow)
11. [Write Workflow (Future)](#write-workflow-future)
12. [Hybrid Workflow](#hybrid-workflow)
13. [Streaming Protocol](#streaming-protocol)
14. [Dependency Injection](#dependency-injection)
15. [Configuration](#configuration)
16. [Testing Strategy](#testing-strategy)
17. [Getting Started](#getting-started)
18. [API Reference](#api-reference)
19. [Design Principles](#design-principles)
20. [Future Features](#future-features)
21. [Authors & Maintainers](#authors--maintainers)
22. [Contributing](#contributing)
23. [License](#license)

---

## Vision

JARVIS Runtime is the **AI brain** of the JARVIS platform — a pure reasoning engine that operates over already-indexed code repositories. It answers questions about code, discovers relationships between components, and (in future releases) proposes and applies code modifications.

The runtime is designed from day one for **enterprise-scale, production use**. It uses Hexagonal Architecture to ensure every infrastructure concern is replaceable, every application node is independently testable, and the domain model is always kept free of framework pollution.

---

## Responsibilities

### This Repository IS Responsible For

| Responsibility | Details |
|---|---|
| **AI Reasoning** | LangGraph-based multi-step reasoning over code graphs |
| **Hybrid Retrieval** | Parallel Neo4j (structural) + Milvus (semantic) search with RRF reranking |
| **Streaming** | Server-Sent Events (SSE) for real-time response streaming |
| **Intent Classification** | Routing user queries to READ / WRITE / HYBRID workflows |
| **Context Assembly** | Building token-budgeted LLM contexts from retrieved nodes |
| **Patch Generation** | (Future) Generating validated code diffs for WRITE operations |
| **Citation** | Tracing every AI claim back to a specific source code location |
| **Audit Logging** | Fire-and-forget structured audit event streaming to BigQuery |
| **Chat API** | FastAPI endpoints for chat initiation and SSE subscription |
| **Retrieval API** | Direct access to hybrid retrieval without LLM reasoning |

### This Repository is NOT Responsible For

| Responsibility | Belongs To |
|---|---|
| Parsing source repositories | **jarvis-parser** |
| Cloning / managing Git repositories | **jarvis-parser** |
| Repository indexing into Neo4j / Milvus | **jarvis-parser** |
| Authentication / Authorization | **jarvis-platform** |
| User management | **jarvis-platform** |
| Repository UI | **jarvis-platform** |
| Re-indexing after write operations | **jarvis-parser** (triggered by jarvis-platform) |

---

## System Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                         JARVIS Platform                              │
│  ┌──────────────┐    ┌─────────────────┐    ┌────────────────────┐ │
│  │   Frontend   │    │  jarvis-platform │    │   jarvis-parser    │ │
│  │  (Next.js)   │◄──►│  (API Gateway)  │◄──►│  (Code Indexer)    │ │
│  └──────────────┘    └────────┬────────┘    └────────┬───────────┘ │
│                               │                       │             │
│                               ▼                       ▼             │
│                    ┌──────────────────┐    ┌─────────────────────┐ │
│                    │  JARVIS Runtime  │    │   Neo4j + Milvus    │ │
│                    │  (this repo)     │◄──►│   (Shared stores)   │ │
│                    └──────────────────┘    └─────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

**jarvis** (this repo) consumes Neo4j and Milvus. It never writes to Neo4j — that is exclusively the domain of jarvis-parser.

---

## High-Level Architecture

```
                         HTTP / SSE
                             │
                    ┌────────▼────────┐
                    │   FastAPI App   │  ← Inbound Adapter
                    └────────┬────────┘
                             │ Depends()
                    ┌────────▼────────┐
                    │   Use Cases     │  ← Application Layer
                    └────────┬────────┘
                             │ via Ports
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │LangGraph │  │LangGraph │  │LangGraph │  ← Application Nodes
        │ Node 1   │  │ Node 2   │  │ Node N   │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
      ┌──────▼──────────────▼──────────────▼──────┐
      │               Port Interfaces              │  ← Ports Layer
      │  LLMPort  GraphPort  VectorPort  SSEPort   │
      └──────┬──────────────┬──────────────┬───────┘
             │              │              │
      ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐
      │ OpenAI      │ │  Neo4j    │ │  Milvus    │  ← Outbound Adapters
      │ Adapter     │ │  Adapter  │ │  Adapter   │
      └─────────────┘ └───────────┘ └────────────┘
             │              │              │
          OpenAI          Neo4j         Milvus
```

---

## Hexagonal Architecture

The JARVIS Runtime is built on the Ports & Adapters (Hexagonal) pattern. This architecture was chosen to:

1. **Decouple business logic from infrastructure** — LangGraph nodes know nothing about Neo4j, OpenAI, or HTTP.
2. **Enable independent testing** — every node can be unit-tested with mock ports.
3. **Support adapter replacement** — swap OpenAI for Anthropic without touching a single application file.
4. **Enforce clear boundaries** — circular dependencies become impossible by design.

```
         ╔═══════════════════════════════════════════╗
         ║              Domain Layer                  ║
         ║  JarvisState, Entities, Value Objects,    ║
         ║  Domain Events, Exceptions                ║
         ╚══════════════════╤════════════════════════╝
                            │ (no outward dependencies)
         ╔══════════════════▼════════════════════════╗
         ║            Application Layer              ║
         ║  LangGraph Nodes, Use Cases, Services,   ║
         ║  Prompts, Planner, Reasoning              ║
         ╚══════════════════╤════════════════════════╝
                            │ (speaks through Ports only)
         ╔══════════════════▼════════════════════════╗
         ║              Ports Layer                   ║
         ║  LLMPort, GraphPort, VectorSearchPort,    ║
         ║  StreamingPort, ConfigurationPort, …      ║
         ╚══════════════════╤════════════════════════╝
                            │ (adapters implement Ports)
         ╔══════════════════▼════════════════════════╗
         ║            Adapters Layer                  ║
         ║  OpenAIAdapter, Neo4jAdapter,             ║
         ║  MilvusAdapter, SSEAdapter, …             ║
         ╚══════════════════╤════════════════════════╝
                            │
         ╔══════════════════▼════════════════════════╗
         ║           Infrastructure Layer            ║
         ║  DI Container, Middleware, Telemetry      ║
         ╚═══════════════════════════════════════════╝
```

**The dependency arrow always points inward.** Domain has zero dependencies. Application depends only on Domain and Ports. Adapters depend on Ports. Infrastructure wires them together.

---

## Folder Structure

```
jarvis/
├── src/                        # All Python source code
│   ├── app/                    # Application entry point (FastAPI factory)
│   │
│   ├── domain/                 # Pure domain — zero external dependencies
│   │   ├── entities/           # Objects with identity (RepositoryReference, RetrievedNode, Citation)
│   │   ├── models/             # Composite models (JarvisState, ExecutionPlan, Patch, Answer)
│   │   ├── state/              # LangGraph state annotation (GraphStateAnnotation)
│   │   ├── value_objects/      # Immutable values (Intent, Query, RelevanceScore)
│   │   ├── events/             # Domain events (StreamEvent, StreamEventType, AuditEvent)
│   │   └── exceptions/         # Typed domain exceptions
│   │
│   ├── agent/                  # LangGraph single-agent orchestration and nodes
│   │   ├── graph/              # LangGraph StateGraph definition and compilation
│   │   ├── nodes/              # One file per LangGraph node
│   │   │   ├── relevance.py
│   │   │   ├── query_enhancement.py
│   │   │   ├── intent_classification.py
│   │   │   ├── planner.py
│   │   │   ├── hybrid_retrieval.py
│   │   │   ├── context_builder.py
│   │   │   ├── operation_router.py
│   │   │   ├── reasoning.py
│   │   │   ├── reflection.py
│   │   │   ├── response.py
│   │   │   ├── patch_planner.py
│   │   │   ├── repository_reader.py
│   │   │   ├── patch_generator.py
│   │   │   ├── validation.py
│   │   │   └── git_operations.py
│   │   ├── workflows/          # High-level workflow orchestrators
│   │   ├── use_cases/          # Application use cases (ChatUseCase)
│   │   ├── services/           # Cross-cutting application services
│   │   ├── prompts/            # All LLM prompt templates (no prompts in nodes)
│   │   ├── planner/            # Planner strategy implementations
│   │   └── reasoning/          # Reasoning strategy implementations
│   │
│   ├── ports/                  # Abstract interfaces (Python ABCs)
│   │   ├── audit/              # AuditPort — structured audit logging to BigQuery
│   │   ├── llm/                # LLMPort — chat completions, streaming, embeddings
│   │   ├── graph/              # GraphPort — Neo4j graph traversal
│   │   ├── vector/             # VectorSearchPort — Milvus similarity search
│   │   ├── repository/         # RepositoryReaderPort — file content access
│   │   ├── git/                # GitPort — branch creation, patch application, PRs
│   │   ├── streaming/          # StreamingPort — SSE event emission
│   │   ├── configuration/      # ConfigurationPort — configuration access
│   │   └── logging/            # LoggingPort, MetricsPort — observability
│   │
│   ├── adapters/               # Concrete port implementations
│   │   ├── inbound/            # FastAPI routers (chat, retrieval, health), CLI
│   │   └── outbound/           # BigQuery, OpenAI, Neo4j, Milvus, SSE, YAML adapters
│   │
│   └── infrastructure/         # Cross-cutting infrastructure concerns
│       ├── dependency_injection/ # DI Container
│       ├── middleware/         # FastAPI middleware (logging, correlation)
│       └── telemetry/          # Structlog configuration
│
├── configs/                    # Environment-specific YAML configuration
├── docs/                       # Engineering documentation and ADRs
│   ├── architecture.md
│   ├── hexagonal.md
│   ├── langgraph.md
│   ├── neo4j.md
│   ├── milvus.md
│   ├── streaming.md
│   ├── ports.md
│   ├── adapters.md
│   ├── dependency-injection.md
│   └── system-design.md
│
└── tests/
    ├── unit/                   # Pure unit tests (no I/O, mock ports)
    │   ├── domain/
    │   ├── agent/
    │   ├── ports/
    │   └── adapters/
    ├── integration/            # Tests against real databases
    │   ├── neo4j/
    │   ├── milvus/
    │   └── openai/
    ├── e2e/                    # Full workflow end-to-end tests
    └── fixtures/               # Shared pytest fixtures
```

---

## Dependency Rules

These rules are enforced by the architecture and must never be violated:

| Rule | Description |
|---|---|
| **Domain has no imports from application, ports, or adapters** | Domain is the innermost layer |
| **Application imports only from domain and ports** | Never from adapters or infrastructure |
| **Ports contain only ABCs** | No implementation code |
| **Adapters implement exactly one Port** | One adapter → one port |
| **No adapter may call another adapter** | Adapters communicate through ports only |
| **Infrastructure wires everything** | The DI container is the only place where ports are bound to adapters |
| **LangGraph nodes receive ports via injection** | No `import` of concrete adapters in nodes |

---

## Ports & Adapters

Every external dependency is hidden behind a Port (Abstract Base Class). The application layer calls port methods — it never knows which adapter is backing them.

| Port | Adapter | External System |
|---|---|---|
| `LLMPort` | `OpenAIAdapter` | OpenAI API |
| `GraphPort` | `Neo4jAdapter` | Neo4j Database |
| `VectorSearchPort` | `MilvusAdapter` | Milvus Vector Store |
| `AuditPort` | `BigQueryAdapter` | Google BigQuery |
| `StreamingPort` | `SSEAdapter` | In-memory asyncio queues |
| `ConfigurationPort` | `YamlConfigurationAdapter` | YAML + env vars |
| `LoggingPort` | `StructlogAdapter` (future) | Structlog |
| `RepositoryReaderPort` | `PlatformReaderAdapter` (future) | jarvis-platform API |
| `GitPort` | `GitHubAdapter` (future) | GitHub / GitLab API |

---

## Unified Agent Architecture

JARVIS does **not** use separate agents for reading and writing. It uses **one orchestration graph with two execution branches**.

Why? Because both read and write workflows share 70–80% of their logic. Imagine these two requests:
1. *"Explain how refunds work."*
2. *"Add logging to the refund flow."*

Both require the exact same foundational pipeline: query enhancement, repository selection, graph traversal, dependency analysis, and context retrieval. Duplicating this across two agents would result in immense code duplication and state desynchronization. Instead, a single agent decides which workflow to execute and branches accordingly.

### The Unified LangGraph

The workflow is compiled once at startup via `build_graph()` in `src/agent/graph/__init__.py`. Here is the complete LangGraph structure representing the unified agent:

```
                            START
                              │
                              ▼
                          Relevance ──────► (irrelevant) ──► Response ──► END
                              │ (relevant)
                              ▼
                      QueryEnhancement
                              │
                              ▼
                     IntentClassification
                              │
                              ▼
                           Planner
                              │
                              ▼
                       HybridRetrieval
                              │
                              ▼
                       ContextBuilder
                              │
                              ▼
                       OperationRouter
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
     [READ BRANCH]      [WRITE BRANCH]    [HYBRID BRANCH]
           │                  │                  │
       Reasoning         PatchPlanner        Reasoning
           │                  │                  │
           ▼                  ▼                  ▼
      Reflection      RepositoryReader      Reflection
           │                  │                  │
           ▼                  ▼                  ▼
      (if needed)      PatchGenerator       (if needed)
     ──► Loop ──►             │            ──► Loop ──►
           │                  ▼                  │
           ▼              Validation             ▼
        Response              │               Response
           │                  ▼                  │
           │            GitOperations            │
           │                  │                  │
           ▼                  ▼                  ▼
          END                END                END
```

### Node Reference

| Node | Purpose | Ports Used |
|---|---|---|
| `Relevance` | Fast-path guardrail checking if query pertains to the repository | LLMPort |
| `QueryEnhancement` | Rewrite raw query for retrieval precision | LLMPort, StreamingPort |
| `IntentClassification` | Classify READ / WRITE / HYBRID intent | LLMPort |
| `Planner` | Produce structured ExecutionPlan | LLMPort, GraphPort |
| `HybridRetrieval` | Parallel graph + vector retrieval | GraphPort, VectorSearchPort |
| `ContextBuilder` | Assemble token-budgeted context | StreamingPort |
| `OperationRouter` | Activate correct execution branch | — |
| `Reasoning` | LLM reasoning over assembled context | LLMPort, StreamingPort |
| `Reflection` | Self-evaluate and gate retrieval loop | LLMPort |
| `Response` | Finalise answer and close stream | StreamingPort |
| `PatchPlanner` | Plan file-level code modifications | LLMPort, GraphPort |
| `RepositoryReader` | Read current source file content | RepositoryReaderPort |
| `PatchGenerator` | Generate unified diffs | LLMPort |
| `Validation` | Validate generated patch | LLMPort |
| `GitOperations` | Apply patch and create PR | GitPort |

---

## Read Workflow

```
User Query
    │
    ▼  POST /api/v1/chat/stream
FastAPI (inbound adapter)
    │
    ▼  builds JarvisState
LangGraph
    │
    ├─► Relevance          (filters off-topic queries early)
    │
    ├─► QueryEnhancement   (enriches query)
    │
    ├─► IntentClassification  (mode = READ)
    │
    ├─► Planner            (decides graph depth, collections)
    │
    ├─► HybridRetrieval    (Neo4j subgraph + Milvus embeddings)
    │
    ├─► ContextBuilder     (formats context, applies token budget)
    │
    ├─► OperationRouter    (READ branch)
    │
    ├─► Reasoning          (LLM streams markdown tokens)
    │
    ├─► Reflection         ──► (if need_more_context) ──► HybridRetrieval
    │                      └─► (done)
    ▼
Response (emits DONE event)

SSE Stream → Client
  STATUS   → "Starting retrieval…"
  THINKING → "Searching 3 related classes…"
  MARKDOWN → "## Overview\nThe `PaymentService`…"  (streamed tokens)
  CITATION → { node_id, file_path, line_start, … }
  DONE     → end of stream
```

**Neo4j** is used to discover structural relationships — which classes a method calls, which interfaces a class implements, which services a REST endpoint depends on.

**Milvus** is used to find semantically similar implementations — methods with similar embedding vectors to the query, regardless of naming conventions.

---

## Write Workflow (Future)

```
User Request ("Add rate limiting to PaymentController")
    │
    ▼
Relevance → QueryEnhancement → IntentClassification (mode = WRITE) → Planner
    │
    ▼
HybridRetrieval
    │  Neo4j: find PaymentController, its dependencies, callers
    │  Milvus: find similar rate-limiting implementations in codebase
    ▼
ContextBuilder
    │
    ▼
PatchPlanner
    │  Determines which files to modify:
    │    - PaymentController.java
    │    - RateLimitConfig.java (new file)
    │    - application.yaml (config update)
    ▼
RepositoryReader
    │  Reads CURRENT content of each affected file from source
    │  (Repository files are ALWAYS the source of truth)
    │  (Neo4j is used only for dependency discovery — not file content)
    ▼
PatchGenerator
    │  Generates unified diffs for each file
    ▼
Validation
    │  Validates syntax, diff integrity, safety
    │  If invalid → loops back to PatchGenerator
    ▼
GitOperations
    │  Creates branch jarvis/patch-{id}
    │  Applies patch
    │  Creates Pull Request
    ▼
Response (streams PR URL and change summary)

POST-WRITE:
    jarvis-platform signals jarvis-parser
    jarvis-parser re-indexes changed files
    Neo4j is updated with new relationships
    (JARVIS runtime is NOT involved in re-indexing)
```

> **Design Note:** Neo4j is used to determine the *impact* of a change — which callers, implementors, and dependents exist. But the *actual file content* is always read from the repository, never reconstructed from Neo4j. After a write, jarvis-parser re-indexes the changed files to keep Neo4j consistent.

---

## Hybrid Workflow

The HYBRID mode combines READ and WRITE:

```
Relevance → QueryEnhancement → IntentClassification (HYBRID) → Planner
    │
    ▼
HybridRetrieval + ContextBuilder + OperationRouter
    │
    ▼ (HYBRID → Reasoning first)
Reasoning          ← "Understand the codebase before modifying"
    │
    ▼
Reflection         ← "Do I have enough context to generate a safe patch?"
    │
    ▼
PatchPlanner → RepositoryReader → PatchGenerator → Validation → Response
    │
    (No Git operations in HYBRID — patch is returned for human review)
```

HYBRID is the recommended mode for complex modifications where understanding existing patterns before generating code is critical for quality.

---

## Streaming Protocol

All streaming uses **Server-Sent Events (SSE)** over HTTP/1.1.

### Event Types

| Event Type | Purpose | Payload |
|---|---|---|
| `STATUS` | Workflow lifecycle updates | `{ message: string }` |
| `THINKING` | High-level progress (never chain-of-thought) | `{ message: string }` |
| `MARKDOWN` | Incremental response content | `{ chunk: string }` |
| `MERMAID` | Diagram for visual rendering | `{ diagram: string }` |
| `TOOL` | Tool invocation notification | `{ tool_name, status, latency_ms }` |
| `CITATION` | Source attribution | `{ node_id, file_path, line_start, element_name }` |
| `ERROR` | Error during processing | `{ code, message }` |
| `DONE` | Stream termination signal | `{}` |

### Wire Format

```
event: THINKING
data: {"event_type":"THINKING","session_id":"uuid","message":"Searching graph for related classes…","sequence":2}

event: MARKDOWN
data: {"event_type":"MARKDOWN","session_id":"uuid","data":{"chunk":"## PaymentService\n"},"sequence":3}

event: CITATION
data: {"event_type":"CITATION","session_id":"uuid","data":{"node_id":"4:abc","file_path":"src/PaymentService.java","line_start":42},"sequence":4}

event: DONE
data: {"event_type":"DONE","session_id":"uuid","sequence":99}
```

### Rendering Guidelines

- **MARKDOWN** events should be concatenated and rendered progressively with a Markdown renderer.
- **MERMAID** events should be passed to a Mermaid.js renderer.
- **CITATION** events should be displayed inline as clickable links to source files.
- **THINKING** events should be displayed as transient progress indicators (not persisted in chat history).
- **DONE** terminates the connection — the client should call `eventSource.close()`.

---

## Dependency Injection

The `Container` class in `infrastructure/dependency_injection/container.py` is the **single place** where ports are bound to adapters.

```python
# In routes:
container: Container = Depends(get_container)
llm: LLMPort = container.llm          # Returns OpenAIAdapter, typed as LLMPort

# In tests:
container = Container()
container._llm = MockLLMAdapter()      # Inject mock without changing application code
```

**Why this matters:** A LangGraph node that receives `LLMPort` can be tested without an OpenAI API key. A Validation node can be tested without a real patch. Every node is independently verifiable.

---

## Configuration

Configuration is layered:

```
configs/application.yaml      ← Base defaults
configs/development.yaml      ← Development overrides
configs/production.yaml       ← Production overrides
Environment variables         ← Highest precedence (12-factor app)
```

Access configuration through `ConfigurationPort.get("dotted.key.path")`. Never read `os.environ` directly in application code.

---

## Testing Strategy

```
tests/
├── unit/           # Fast, no I/O, mock all ports
│   ├── domain/     # Pydantic model validation, value objects, stream events
│   ├── agent/      # LangGraph node logic with mock ports
│   ├── ports/      # Port contract definitions
│   └── adapters/   # Adapter serialization logic
├── integration/    # Against real databases (requires Docker Compose)
│   ├── neo4j/      # Graph queries, schema validation
│   ├── milvus/     # Vector search, collection setup
│   └── openai/     # LLM integration tests
├── e2e/            # Full workflow from API call to stream completion
└── fixtures/       # Shared pytest fixtures (mock ports, test state)
```

**Coverage target:** 80% minimum, enforced in CI via `pytest --cov-fail-under=80`.

**Node testability example:**
```python
async def test_intent_classification_defaults_to_read(base_state, runnable_config):
    result = await IntentClassificationNode.run(base_state, runnable_config)
    assert result["intent"]["execution_mode"] == "READ"
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Poetry 1.8+
- Docker & Docker Compose

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-org/jarvis.git
cd jarvis

# 2. Install dependencies
make install

# 3. Copy and configure environment
cp .env.example .env
# Edit .env with your OpenAI API key and database credentials

# 4. Start infrastructure services
make docker-up

# 5. Start the development server
make dev

# 6. Open API documentation
open http://localhost:8000/docs
```

### Running Tests

```bash
make test              # All tests
make test-unit         # Unit tests only (no Docker required)
make test-integration  # Integration tests (requires Docker Compose)
make test-cov          # With HTML coverage report
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/chat/stream` | Initiate streaming chat session |
| `GET` | `/api/v1/chat/stream/{session_id}` | Subscribe to SSE event stream |
| `POST` | `/api/v1/chat/complete` | Blocking (non-streaming) chat |
| `POST` | `/api/v1/retrieval/search` | Hybrid retrieval without LLM |
| `GET` | `/api/v1/retrieval/node/{node_id}` | Fetch graph node by ID |
| `GET` | `/api/v1/health/live` | Liveness probe |
| `GET` | `/api/v1/health/ready` | Readiness probe |
| `GET` | `/api/v1/health/status` | Detailed health status |

Interactive docs: `http://localhost:8000/docs`

---

## Design Principles

| # | Principle |
|---|---|
| 1 | Repository source code is always the source of truth |
| 2 | Neo4j stores relationships — not file content |
| 3 | Milvus stores semantic knowledge — not structure |
| 4 | Repository files are read only when modifications are required |
| 5 | Neo4j is used to determine impact and dependencies |
| 6 | Milvus is used to retrieve semantically similar implementations |
| 7 | Write operations modify repository files — never Neo4j directly |
| 8 | After successful writes, jarvis-parser re-indexes changed files |
| 9 | Application communicates only through Ports |
| 10 | Adapters contain infrastructure concerns only |
| 11 | LangGraph nodes are independently testable units |
| 12 | Everything must support future autonomous coding |

---

## Future Features

| Feature | Status | Description |
|---|---|---|
| Write Workflow | Planned | Full autonomous code modification via patch generation |
| Redis Streaming | Planned | Replace in-memory SSE queues for multi-worker support |
| Git Integration | Planned | GitHub / GitLab adapter for PR creation |
| Multi-Repo Reasoning | Planned | Cross-repository dependency analysis |
| OpenTelemetry | Planned | Distributed tracing with OTLP export |
| Evaluation Framework | Planned | Automated retrieval and reasoning quality metrics |
| Anthropic Adapter | Future | Alternative LLM provider adapter |
| Local LLM Adapter | Future | Ollama / vLLM for on-premise deployments |
| Autonomous Agent Loop | Future | Unsupervised multi-step code evolution |

## Authors & Maintainers

- **Vidit Jain** — Lead Developer & Maintainer

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, branch naming conventions, and code review requirements.

---

## License

MIT License — see [LICENSE](LICENSE).
