# Streaming Protocol

> **SSE streaming specification for the JARVIS AI Runtime.**

---

## Overview

JARVIS uses **Server-Sent Events (SSE)** for all streaming communication. SSE is a W3C standard for server-to-client event streaming over HTTP. It is simpler than WebSockets for unidirectional streaming and has native browser support.

---

## Session Lifecycle

```
1. POST /api/v1/chat/stream
   Body: { "query": "...", "repository_id": "...", "stream": true }
   Response: { "session_id": "uuid", "stream_url": "/api/v1/chat/stream/{session_id}" }

2. GET /api/v1/chat/stream/{session_id}
   Headers: Accept: text/event-stream
   Response: text/event-stream (open connection)

3. LangGraph workflow executes in background
   Events are emitted via StreamingPort
   Events are serialised to SSE wire format
   Client receives events incrementally

4. DONE event is received
   Client closes EventSource connection
   Server tears down session queue
```

---

## Wire Format

Each event follows the SSE specification:

```
event: {EVENT_TYPE}\n
data: {JSON_PAYLOAD}\n
\n
```

Example stream:

```
event: STATUS
data: {"event_type":"STATUS","session_id":"550e8400-e29b-41d4-a716-446655440000","message":"Initialising workflow…","sequence":0,"emitted_at":"2024-01-15T10:30:00Z"}

event: THINKING
data: {"event_type":"THINKING","session_id":"550e8400-e29b-41d4-a716-446655440000","message":"Enhancing query for better retrieval…","sequence":1,"emitted_at":"2024-01-15T10:30:00.1Z"}

event: THINKING
data: {"event_type":"THINKING","session_id":"550e8400-e29b-41d4-a716-446655440000","message":"Found 14 related nodes — 6 from graph, 8 from vector store","sequence":4,"emitted_at":"2024-01-15T10:30:01.5Z"}

event: MARKDOWN
data: {"event_type":"MARKDOWN","session_id":"550e8400-e29b-41d4-a716-446655440000","data":{"chunk":"## PaymentService\n\nThe `PaymentService` is responsible for"},"sequence":5,"emitted_at":"2024-01-15T10:30:02.0Z"}

event: MARKDOWN
data: {"event_type":"MARKDOWN","session_id":"550e8400-e29b-41d4-a716-446655440000","data":{"chunk":" orchestrating the full payment lifecycle"},"sequence":6,"emitted_at":"2024-01-15T10:30:02.1Z"}

event: CITATION
data: {"event_type":"CITATION","session_id":"550e8400-e29b-41d4-a716-446655440000","data":{"node_id":"4:abc123","file_path":"src/payment/PaymentService.java","line_start":42,"line_end":180,"element_name":"PaymentService","node_type":"Class","relevance_score":0.94},"sequence":12,"emitted_at":"2024-01-15T10:30:04.0Z"}

event: DONE
data: {"event_type":"DONE","session_id":"550e8400-e29b-41d4-a716-446655440000","sequence":15,"emitted_at":"2024-01-15T10:30:04.5Z"}
```

---

## Event Payload Schemas

### STATUS

```json
{
  "event_type": "STATUS",
  "session_id": "string",
  "message": "Human-readable status update",
  "sequence": 0,
  "emitted_at": "ISO-8601 UTC"
}
```

### THINKING

```json
{
  "event_type": "THINKING",
  "session_id": "string",
  "message": "High-level progress summary — never chain-of-thought",
  "sequence": 1,
  "emitted_at": "ISO-8601 UTC"
}
```

> ⚠️ THINKING events must never contain internal LLM reasoning. Only emit human-friendly progress summaries.

### MARKDOWN

```json
{
  "event_type": "MARKDOWN",
  "session_id": "string",
  "data": {
    "chunk": "Incremental markdown text token"
  },
  "sequence": 5,
  "emitted_at": "ISO-8601 UTC"
}
```

Concatenate all MARKDOWN chunks in sequence order to reconstruct the full response.

### MERMAID

```json
{
  "event_type": "MERMAID",
  "session_id": "string",
  "data": {
    "diagram": "graph TD\n  A --> B\n  B --> C"
  },
  "sequence": 10,
  "emitted_at": "ISO-8601 UTC"
}
```

Pass the `diagram` string to Mermaid.js for rendering. A single response may contain multiple MERMAID events.

### TOOL

```json
{
  "event_type": "TOOL",
  "session_id": "string",
  "data": {
    "tool_name": "neo4j_search",
    "status": "completed",
    "latency_ms": 45.2
  },
  "sequence": 3,
  "emitted_at": "ISO-8601 UTC"
}
```

### CITATION

```json
{
  "event_type": "CITATION",
  "session_id": "string",
  "data": {
    "node_id": "4:abc123:0",
    "repository_id": "repo-456",
    "file_path": "src/payment/PaymentService.java",
    "line_start": 42,
    "line_end": 180,
    "element_name": "PaymentService",
    "node_type": "Class",
    "relevance_score": 0.94,
    "snippet": "public class PaymentService implements PaymentPort {"
  },
  "sequence": 12,
  "emitted_at": "ISO-8601 UTC"
}
```

### ERROR

```json
{
  "event_type": "ERROR",
  "session_id": "string",
  "data": {
    "code": "RETRIEVAL_ERROR",
    "message": "Neo4j connection timed out after 30s"
  },
  "sequence": 8,
  "emitted_at": "ISO-8601 UTC"
}
```

On ERROR, the stream may continue (recoverable) or terminate with DONE (unrecoverable).

### DONE

```json
{
  "event_type": "DONE",
  "session_id": "string",
  "sequence": 15,
  "emitted_at": "ISO-8601 UTC"
}
```

Close the EventSource connection on DONE.

---

## Client Implementation

```javascript
const eventSource = new EventSource(`/api/v1/chat/stream/${sessionId}`);
let markdownBuffer = '';

eventSource.addEventListener('THINKING', (e) => {
  const event = JSON.parse(e.data);
  showThinkingIndicator(event.message);
});

eventSource.addEventListener('MARKDOWN', (e) => {
  const event = JSON.parse(e.data);
  markdownBuffer += event.data.chunk;
  renderMarkdown(markdownBuffer);
});

eventSource.addEventListener('MERMAID', (e) => {
  const event = JSON.parse(e.data);
  renderMermaid(event.data.diagram);
});

eventSource.addEventListener('CITATION', (e) => {
  const event = JSON.parse(e.data);
  addCitation(event.data);
});

eventSource.addEventListener('DONE', (e) => {
  eventSource.close();
  finalizeCitations();
});

eventSource.addEventListener('ERROR', (e) => {
  const event = JSON.parse(e.data);
  showError(event.data.message);
});
```

---

## Heartbeat

The SSEAdapter emits a heartbeat comment every 15 seconds to prevent proxy timeouts:

```
: heartbeat

```

(Lines starting with `:` are SSE comments and are ignored by the client.)
