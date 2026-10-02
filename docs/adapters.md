# Adapters Reference

> **Concrete implementations of every Port in the JARVIS Runtime.**

---

## OpenAIAdapter

**File:** `adapters/outbound/openai/openai_adapter.py`
**Implements:** `LLMPort`

Uses the official OpenAI async Python client. Supports chat completions (gpt-4o), streaming completions, and text embeddings (text-embedding-3-large).

**Configuration:**
```yaml
llm:
  openai:
    api_key: ""           # OPENAI_API_KEY env var
    model: "gpt-4o"
    embedding_model: "text-embedding-3-large"
    timeout: 60.0
    max_retries: 3
```

---

## Neo4jAdapter

**File:** `adapters/outbound/neo4j/neo4j_adapter.py`
**Implements:** `GraphPort`

Uses the official Neo4j async Python driver. All Cypher queries live in this file — they must never appear in application nodes.

**Configuration:**
```yaml
database:
  neo4j:
    uri: "bolt://localhost:7687"
    user: "neo4j"
    password: ""          # DATABASE_NEO4J_PASSWORD env var
    database: "neo4j"
```

---

## MilvusAdapter

**File:** `adapters/outbound/milvus/milvus_adapter.py`
**Implements:** `VectorSearchPort`

Uses pymilvus MilvusClient. Manages collection access, filter expression construction, and RRF reranking.

**Configuration:**
```yaml
database:
  milvus:
    uri: "http://localhost:19530"
    token: ""             # DATABASE_MILVUS_TOKEN env var
    timeout: 30.0
```

---

## SSEAdapter

**File:** `adapters/outbound/sse/sse_adapter.py`
**Implements:** `StreamingPort`

In-memory asyncio queue per session. Thread-safe within a single asyncio event loop. For multi-worker deployments, replace with `RedisStreamingAdapter` (future).

**Configuration:**
```yaml
streaming:
  max_queue_size: 1000
  heartbeat_interval_seconds: 15
```

---

## YamlConfigurationAdapter

**File:** `adapters/outbound/yaml/yaml_configuration_adapter.py`
**Implements:** `ConfigurationPort`

Loads `configs/application.yaml` as base, merges `configs/{environment}.yaml` on top, and allows environment variable override for any key.

**Key naming:** `database.neo4j.uri` → env var `DATABASE_NEO4J_URI`

---

## Adding a New Adapter

1. Create `adapters/outbound/{name}/{name}_adapter.py`
2. Import the target Port from `ports/{port}/__init__.py`
3. Subclass the Port and implement all abstract methods
4. Raise `NotImplementedError` for methods not yet implemented
5. Register the adapter in `infrastructure/dependency_injection/container.py`
6. Add required dependencies to `pyproject.toml`

**Naming convention:** `{Provider}{Port}Adapter` — e.g., `AnthropicLLMAdapter`, `GitHubGitAdapter`.
