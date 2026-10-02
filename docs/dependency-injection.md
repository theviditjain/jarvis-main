# Dependency Injection

> **How the JARVIS Runtime wires ports to adapters.**

---

## Container

`infrastructure/dependency_injection/container.py` is the **single place** in the entire codebase where port interfaces are bound to concrete adapter implementations.

The container uses **lazy initialisation** — adapters are created on first access. This prevents slow startup during testing when only some adapters are needed.

---

## Usage in FastAPI

```python
from infrastructure.dependency_injection.container import get_container, Container
from fastapi import Depends

@router.post("/chat/stream")
async def chat(
    request: ChatRequest,
    container: Container = Depends(get_container),
):
    llm: LLMPort = container.llm           # OpenAIAdapter, typed as LLMPort
    streaming: StreamingPort = container.streaming  # SSEAdapter, typed as StreamingPort
    # ...
```

The route handler receives port-typed objects. It never knows it is talking to OpenAI.

---

## Usage in Tests

```python
def test_reasoning_node():
    container = Container()
    container._llm = MockLLMAdapter()       # Replace adapter before first access
    container._streaming = MockStreamingAdapter()

    # Node receives mock ports — no API calls, no network
    node = ReasoningNode(llm=container.llm, streaming=container.streaming)
    ...
```

---

## Container Properties

| Property | Port | Adapter |
|---|---|---|
| `container.configuration` | `ConfigurationPort` | `YamlConfigurationAdapter` |
| `container.llm` | `LLMPort` | `OpenAIAdapter` |
| `container.graph` | `GraphPort` | `Neo4jAdapter` |
| `container.vector` | `VectorSearchPort` | `MilvusAdapter` |
| `container.streaming` | `StreamingPort` | `SSEAdapter` |

---

## Singleton Behaviour

`get_container()` is decorated with `@lru_cache(maxsize=1)`, making it a process-level singleton. All FastAPI requests share the same container instance, and therefore the same adapter connection pools.

To reset in tests: `get_container.cache_clear()`.
