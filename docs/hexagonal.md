# Hexagonal Architecture

> **Implementation guide for the hexagonal pattern in the JARVIS Runtime.**

---

## Concept

Hexagonal Architecture (also called Ports & Adapters) was introduced by Alistair Cockburn. The key insight is that the *application* should not know about the *infrastructure* that surrounds it. Instead:

- The application defines abstract **Ports** (interfaces).
- External systems are accessed through **Adapters** that implement those Ports.
- Dependencies always point **inward** — from adapters toward the domain.

---

## Layer Boundaries

```
╔══════════════════════════════════════════════════════════╗
║                      Domain                              ║
║  No external dependencies. Pure Python + Pydantic.       ║
╚════════════════════════╤═════════════════════════════════╝
                         │ imports from
╔════════════════════════▼═════════════════════════════════╗
║                    Application                           ║
║  LangGraph nodes, use cases, services, prompts.          ║
║  Imports: domain + ports. Never adapters.                ║
╚════════════════════════╤═════════════════════════════════╝
                         │ implements
╔════════════════════════▼═════════════════════════════════╗
║                      Ports                               ║
║  Abstract interfaces (ABCs). No implementation code.     ║
╚════════════════════════╤═════════════════════════════════╝
                         │ satisfied by
╔════════════════════════▼═════════════════════════════════╗
║                     Adapters                             ║
║  Concrete implementations. OpenAI, Neo4j, Milvus, SSE.  ║
║  Imports: domain + ports. Never application.             ║
╚════════════════════════╤═════════════════════════════════╝
                         │ wired by
╔════════════════════════▼═════════════════════════════════╗
║                  Infrastructure                          ║
║  DI Container, Middleware, Telemetry.                    ║
║  The only layer that knows all layers.                   ║
╚══════════════════════════════════════════════════════════╝
```

---

## Rule Enforcement

### ✅ Allowed imports

```python
# In application/nodes/reasoning.py
from domain.models.jarvis_state import JarvisState      # ✅ domain
from ports.llm import LLMPort                            # ✅ port
from ports.streaming import StreamingPort                # ✅ port
```

### ❌ Forbidden imports

```python
# In application/nodes/reasoning.py
from adapters.outbound.openai import OpenAIAdapter       # ❌ adapter in application
from neo4j import AsyncGraphDatabase                     # ❌ infrastructure in application
import openai                                            # ❌ external lib in application
```

```python
# In adapters/outbound/neo4j/neo4j_adapter.py
from adapters.outbound.milvus import MilvusAdapter       # ❌ adapter calling adapter
from application.nodes import ReasoningNode              # ❌ adapter calling application
```

---

## Testing Advantage

Because application nodes depend only on ports (interfaces), tests can inject mock adapters with zero real I/O:

```python
class MockLLMPort(LLMPort):
    async def complete(self, system_prompt, user_prompt, **kwargs) -> str:
        return '{"execution_mode": "READ", "category": "explain"}'

async def test_intent_classification():
    node = IntentClassificationNode(llm=MockLLMPort())
    result = await node.run({"enhanced_query": "How does PaymentService work?"})
    assert result["intent"]["execution_mode"] == "READ"
```

No OpenAI API key. No network call. Instant execution.

---

## Adding a New Adapter

To add a new LLM provider (e.g., Anthropic):

1. Create `adapters/outbound/anthropic/anthropic_adapter.py`
2. Implement `LLMPort` (all abstract methods)
3. Update `Container` to conditionally use it based on configuration
4. Add `anthropic` to `pyproject.toml`

**Zero changes to the application layer.** The nodes never knew it was OpenAI — they only know `LLMPort`.
