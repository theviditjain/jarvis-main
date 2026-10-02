# LangGraph Workflow

> **Complete documentation for every node in the JARVIS LangGraph workflow.**

---

## Graph Definition

The workflow is compiled once at startup in `application/graph/__init__.py` using `StateGraph(GraphStateAnnotation)`. The graph is **deterministic** — given the same state, it follows the same path. Non-determinism comes from the LLM, not the graph structure.

---

## State

All nodes read from and write to `GraphStateAnnotation`, which is the LangGraph-compatible TypedDict wrapper around `JarvisState`.

Key fields:

| Field | Set By | Used By |
|---|---|---|
| `query` | API layer | QueryEnhancement |
| `enhanced_query` | QueryEnhancement | IntentClassification, Planner, HybridRetrieval |
| `intent` | IntentClassification | Planner, OperationRouter |
| `execution_plan` | Planner | HybridRetrieval, ContextBuilder, PatchPlanner |
| `retrieved_nodes` | HybridRetrieval | ContextBuilder |
| `context` | ContextBuilder | Reasoning |
| `reasoning` | Reasoning | Reflection (internal, never streamed) |
| `need_more_context` | Reflection | Graph conditional edge |
| `answer` | Reasoning, Response | Response, API layer |
| `patch` | PatchPlanner, PatchGenerator | Validation, GitOperations |
| `repository_context` | RepositoryReader | PatchGenerator |

---

## Node Documentation

### QueryEnhancement

**File:** `application/nodes/query_enhancement.py`

**Purpose:** Rewrites the raw user query into a form that improves both vector search recall (more semantic terms) and graph traversal precision (extracts entity names).

**Example input:** `"how does payment work"`
**Example output:** `"PaymentService payment processing flow, PaymentController REST endpoint, payment validation logic"`

**Emits:** `STATUS("Enhancing query…")`, `THINKING("Query expanded to include payment-related terms")`

---

### IntentClassification

**File:** `application/nodes/intent_classification.py`

**Purpose:** Classifies the user's intent into READ, WRITE, or HYBRID and extracts key entities (class names, method names, endpoints) to guide retrieval.

**Decision logic:**
- Questions about how code works → READ
- Requests to add, modify, delete, refactor code → WRITE
- "Understand X and then implement Y" → HYBRID

**Emits:** `THINKING("Classified as READ — understanding query")`

---

### Planner

**File:** `application/nodes/planner.py`

**Purpose:** Produces a structured `ExecutionPlan` that controls all subsequent retrieval and reasoning steps.

**Plan decisions:**
- Graph traversal depth (1–5 hops)
- Milvus collections to search
- Whether file reads are required
- Maximum reflection iterations

**Emits:** `THINKING("Planning: graph depth 2, 3 collections, READ mode")`

---

### HybridRetrieval

**File:** `application/nodes/hybrid_retrieval.py`

**Purpose:** Executes sequential retrieval: Semantic + keyword search on Milvus, LLM relevance filtering of results, and finally structural expansion via Neo4j.

**Algorithm:**
1. Execute Milvus Hybrid (Semantic + BM25) search using `enhanced_query`
2. Retrieve top_k candidates from vector store
3. Pass candidates to LLM for relevance evaluation against user intent
4. For relevant candidates, query Neo4j to expand structural neighbors (e.g. callers, implementations)
5. Merge and return final `RetrievedNode` list

**Emits:** `TOOL("milvus_search", "started")`, `TOOL("llm_filter", "started")`, `TOOL("neo4j_expansion", "started")`, `THINKING("Filtered to 8 relevant nodes; expanded to 14 structurally related nodes")`


---

### ContextBuilder

**File:** `application/nodes/context_builder.py`

**Purpose:** Formats retrieved nodes into a structured context document for the LLM. Applies token budget management — lower-relevance nodes are truncated first.

**Output format:**
```
## Repository Context
### Class: PaymentService (payment/PaymentService.java:L42)
> Handles payment processing including validation, authorization, and settlement.

### Method: processPayment (payment/PaymentService.java:L67)
> Orchestrates the payment flow. Calls PaymentValidator, then AuthorizationService.
...
```

**Emits:** `THINKING("Built context: 12 nodes, ~3,200 tokens")`

---

### OperationRouter

**File:** `application/nodes/operation_router.py`

**Purpose:** Pass-through routing node. Its only role is to be the source of the conditional edge that branches to READ, WRITE, or HYBRID paths. Contains no logic — the routing decision is in `_route_by_mode()`.

---

### Reasoning

**File:** `application/nodes/reasoning.py`

**Purpose:** Core LLM reasoning step. Streams the response token by token using LLMPort.stream().

**Streaming:** Each token chunk is emitted as a MARKDOWN event. Citations are extracted from the response and emitted as CITATION events.

**Internal reasoning:** The LLM may include chain-of-thought internally. This is stored in `state.reasoning` but **never emitted as a stream event**.

**Emits:** `THINKING("Generating response…")`, `MARKDOWN(chunk)`, `CITATION(citation)`

---

### Reflection

**File:** `application/nodes/reflection.py`

**Purpose:** Evaluates whether the reasoning output is sufficient. If the answer contains uncertainty signals or references to unavailable context, sets `need_more_context = True` to trigger another retrieval loop.

**Loop limit:** `execution_plan.max_iterations` prevents infinite loops. On reaching the limit, `need_more_context` is forced to False.

**Emits:** `THINKING("Answer confidence: high — finalising response")`

---

### Response

**File:** `application/nodes/response.py`

**Purpose:** Finalises the answer, emits remaining CITATION events, optionally emits MERMAID for diagram rendering, and emits DONE to close the stream.

**Emits:** `CITATION(…)`, `MERMAID(diagram)` (optional), `DONE`

---

### PatchPlanner

**File:** `application/nodes/patch_planner.py`

**Purpose (WRITE/HYBRID):** Determines which files require modification. Uses Neo4j to discover the dependency chain — which callers and dependents exist for the target code element.

**Output:** A `Patch` skeleton with a list of `PatchFile` objects (each with file_path and operation, but no diff yet).

**Emits:** `THINKING("Planning changes to 3 files: PaymentService.java, PaymentController.java, application.yaml")`

---

### RepositoryReader

**File:** `application/nodes/repository_reader.py`

**Purpose (WRITE/HYBRID):** Reads the current content of every file listed in the patch plan via RepositoryReaderPort. This ensures PatchGenerator works from the exact current state — not from potentially stale graph data.

**Emits:** `TOOL("repository_reader", file_path)` for each file

---

### PatchGenerator

**File:** `application/nodes/patch_generator.py`

**Purpose (WRITE/HYBRID):** Generates unified diffs for each file in the patch plan. For ADD operations, generates the full new file content. For MODIFY, generates a unified diff.

**Emits:** `THINKING("Generating diff for PaymentService.java…")`

---

### Validation

**File:** `application/nodes/validation.py`

**Purpose:** Validates the generated patch before Git application. Checks:
- Syntax validity (code is parseable)
- Diff integrity (hunks apply cleanly)
- Safety (no credentials, no destructive patterns)

If invalid: sets `patch.validated = False` with `validation_errors`. The conditional edge loops back to PatchGenerator.

**Emits:** `THINKING("Validation passed — 3 files, 0 errors")`

---

### GitOperations

**File:** `application/nodes/git_operations.py`

**Purpose (WRITE only):** Applies the validated patch to the repository via GitPort. Creates a feature branch, commits the patch, and opens a pull request.

**After completion:** jarvis-platform (not this runtime) signals jarvis-parser to re-index the changed files.

**Emits:** `TOOL("git_create_branch", …)`, `TOOL("git_apply_patch", …)`, `TOOL("git_create_pr", …)`

---

## Execution Flow Diagrams

### READ

```
START → QueryEnhancement → IntentClassification → Planner
      → HybridRetrieval → ContextBuilder → OperationRouter
      → Reasoning → Reflection
         │
         ├─ need_more_context=True ──► HybridRetrieval (loop)
         └─ need_more_context=False ──► Response → END
```

### WRITE

```
START → QueryEnhancement → IntentClassification → Planner
      → HybridRetrieval → ContextBuilder → OperationRouter
      → PatchPlanner → RepositoryReader → PatchGenerator → Validation
         │
         ├─ invalid ──► PatchGenerator (loop)
         └─ valid ──► GitOperations → Response → END
```

### HYBRID

```
START → QueryEnhancement → IntentClassification → Planner
      → HybridRetrieval → ContextBuilder → OperationRouter
      → Reasoning → Reflection
         │
         └─ done ──► PatchPlanner → RepositoryReader → PatchGenerator
                   → Validation → Response → END
```
