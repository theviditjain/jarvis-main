# Architecture Overview

> **Top-level architectural documentation for the JARVIS AI Runtime.**
> See `system-design.md` for the authoritative ADR-level document.

---

## Components

| Component | Language | Role |
|---|---|---|
| **FastAPI** | Python | HTTP server, SSE endpoint, OpenAPI docs |
| **LangGraph** | Python | Multi-step AI workflow orchestration |
| **LangChain** | Python | LLM abstraction utilities |
| **Neo4j** | Graph DB | Structural code relationships |
| **Milvus** | Vector DB | Semantic code embeddings |
| **OpenAI** | External API | LLM completions and embeddings |
| **Structlog** | Python | Structured JSON logging |
| **Pydantic** | Python | Data validation and serialisation |
| **Poetry** | Python | Dependency management |

---

## Request Lifecycle

```
Client
  │
  │ POST /api/v1/chat/stream
  ▼
FastAPI Router (inbound adapter)
  │
  │ Builds JarvisState
  │ Launches background LangGraph task
  │
  ▼
GET /api/v1/chat/stream/{session_id}
  │
  │ Returns SSE stream
  ▼
Client receives events as workflow executes
  STATUS → THINKING → MARKDOWN → CITATION → DONE
```

---

## Key Design Decisions

1. **Hexagonal Architecture** — all external I/O behind Ports.
2. **LangGraph StateGraph** — shared JarvisState flows through every node.
3. **SSE Streaming** — unidirectional, HTTP-native, reconnection-safe.
4. **Hybrid Retrieval** — Milvus (Semantic+BM25) → LLM Filter → Neo4j Expansion.
5. **Repository Files as Source of Truth** — Neo4j is derived, never authoritative for content.

See `docs/system-design.md` for detailed ADRs.
