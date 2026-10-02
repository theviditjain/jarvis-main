# Ports Reference

> **Complete reference for all port interfaces in the JARVIS Runtime.**

---

## Overview

Ports are Python Abstract Base Classes (ABCs) defined in the `ports/` directory. They are the only mechanism by which the application layer communicates with external systems.

Every port method is `async` to support non-blocking I/O throughout the streaming workflow.

---

## LLMPort

**Location:** `ports/llm/__init__.py`

| Method | Description |
|---|---|
| `complete(system, user, ...)` | Single chat completion |
| `stream(system, user, ...)` | Streaming chat completion (async generator) |
| `embed(texts, ...)` | Batch text embedding |
| `health_check()` | Provider reachability check |

**Adapter:** `OpenAIAdapter`

---

## GraphPort

**Location:** `ports/graph/__init__.py`

| Method | Description |
|---|---|
| `find_node_by_id(node_id, ...)` | Retrieve node by Neo4j element ID |
| `find_nodes_by_name(name, ...)` | Search nodes by name |
| `get_neighbours(node_id, ...)` | Traverse graph neighbourhood |
| `get_dependency_chain(node_id, ...)` | Full dependency chain for impact analysis |
| `execute_query(query, ...)` | Raw Cypher execution (adapter escape hatch) |
| `health_check()` | Database reachability check |

**Adapter:** `Neo4jAdapter`

---

## VectorSearchPort

**Location:** `ports/vector/__init__.py`

| Method | Description |
|---|---|
| `search(vector, collection, ...)` | ANN vector search |
| `search_by_text(text, collection, ...)` | Embed then search |
| `hybrid_search(text, collections, ...)` | Multi-collection search with RRF |
| `get_collections()` | List available collections |
| `health_check()` | Database reachability check |

**Adapter:** `MilvusAdapter`

---

## StreamingPort

**Location:** `ports/streaming/__init__.py`

| Method | Description |
|---|---|
| `emit(event)` | Emit a StreamEvent to the session queue |
| `emit_status(session_id, message, ...)` | Convenience: emit STATUS event |
| `emit_thinking(session_id, message, ...)` | Convenience: emit THINKING event |
| `emit_markdown_chunk(session_id, chunk, ...)` | Convenience: emit MARKDOWN event |
| `emit_done(session_id, ...)` | Emit terminal DONE event |
| `subscribe(session_id)` | Subscribe to event stream (async generator) |

**Adapter:** `SSEAdapter`

---

## RepositoryReaderPort

**Location:** `ports/repository/__init__.py`

| Method | Description |
|---|---|
| `read_file(repo_id, path, ...)` | Read a single file's content |
| `list_files(repo_id, path, ...)` | List files in a directory |
| `read_files(repo_id, paths, ...)` | Batch file read |
| `health_check()` | Backend reachability check |

**Adapter:** `PlatformReaderAdapter` (future)

---

## GitPort

**Location:** `ports/git/__init__.py`

| Method | Description |
|---|---|
| `create_branch(repo_id, branch, ...)` | Create a feature branch |
| `apply_patch(repo_id, patch)` | Apply a validated Patch object |
| `create_pull_request(repo_id, branch, ...)` | Open a PR |
| `health_check()` | Git provider reachability check |

**Adapter:** `GitHubAdapter` (future)

---

## ConfigurationPort

**Location:** `ports/configuration/__init__.py`

| Method | Description |
|---|---|
| `get(key, default)` | Retrieve value by dotted key path |
| `get_required(key)` | Retrieve required value (raises on missing) |
| `get_section(section)` | Retrieve entire section as dict |
| `reload()` | Reload from underlying source |

**Adapter:** `YamlConfigurationAdapter`

---

## LoggingPort

**Location:** `ports/logging/__init__.py`

| Method | Description |
|---|---|
| `debug(event, **kwargs)` | DEBUG level structured log |
| `info(event, **kwargs)` | INFO level structured log |
| `warning(event, **kwargs)` | WARNING level structured log |
| `error(event, **kwargs)` | ERROR level structured log |
| `critical(event, **kwargs)` | CRITICAL level structured log |
| `bind(**kwargs)` | Return new logger with bound context |

## MetricsPort

| Method | Description |
|---|---|
| `increment(metric, value, **tags)` | Increment counter |
| `gauge(metric, value, **tags)` | Set gauge value |
| `histogram(metric, value, **tags)` | Record histogram value |
| `timing(metric, value_ms, **tags)` | Record timing measurement |
