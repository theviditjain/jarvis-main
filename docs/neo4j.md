# Neo4j Graph Model

> **Authoritative documentation for the JARVIS knowledge graph schema.**
> Maintained by the JARVIS team. Node types and relationships are produced by **jarvis-parser**.

---

## Why Neo4j?

Neo4j is used because code is **inherently a graph**. A class extends another class, implements multiple interfaces, calls dozens of methods, and exposes REST endpoints that depend on database tables. Representing these relationships in a relational database requires complex joins. In a graph, they are first-class citizens — queryable in a single traversal.

JARVIS uses Neo4j to:
- **Discover the dependency chain** of a code element (which classes would break if this method changes).
- **Find all callers** of a method, enabling impact analysis for WRITE operations.
- **Traverse service boundaries** — which REST endpoint calls which service calls which repository.
- **Identify cross-module patterns** — all classes implementing a specific interface.

---

## Why Neo4j is NOT the Source of Truth

> **The repository file system is always the source of truth for source code.**

Neo4j stores **relationships and metadata** extracted from source files by jarvis-parser. If the graph becomes inconsistent with the file system (e.g., a file was modified without re-indexing), the file system wins. JARVIS never reconstructs file content from the graph.

This means:
- Write operations modify **files**, not Neo4j nodes.
- After a write, **jarvis-parser re-indexes** the changed files to restore consistency.
- The JARVIS runtime never writes to Neo4j.

---

## Node Types

### Repository

Represents an entire repository known to the JARVIS platform.

```
(:Repository {
    id:             String,   // Unique identifier assigned by jarvis-parser
    name:           String,   // "org/repo" format
    language:       String,   // Primary language
    indexed_at:     DateTime, // Last successful index timestamp
    parser_version: String,   // Version of jarvis-parser that indexed this
    default_branch: String    // Default branch (e.g. "main")
})
```

### Module

A top-level module or package within a repository.

```
(:Module {
    id:            String,
    name:          String,   // Module name
    file_path:     String,   // Repository-relative path
    repository_id: String
})
```

### Package

A package within a module (e.g., Java package, Python package).

```
(:Package {
    id:            String,
    name:          String,   // Fully qualified package name
    repository_id: String
})
```

### Class

A class definition.

```
(:Class {
    id:            String,
    name:          String,   // Simple class name
    qualified_name: String,  // Fully qualified name
    file_path:     String,
    line_start:    Integer,
    line_end:      Integer,
    is_abstract:   Boolean,
    repository_id: String,
    summary:       String    // LLM-generated summary
})
```

### Interface

An interface definition (Java/TypeScript/Go interface).

```
(:Interface {
    id:            String,
    name:          String,
    qualified_name: String,
    file_path:     String,
    line_start:    Integer,
    line_end:      Integer,
    repository_id: String
})
```

### Enum

An enumeration type.

```
(:Enum {
    id:            String,
    name:          String,
    qualified_name: String,
    file_path:     String,
    values:        [String], // Enum constant names
    repository_id: String
})
```

### Method

A method or function definition.

```
(:Method {
    id:             String,
    name:           String,
    qualified_name: String,
    file_path:      String,
    line_start:     Integer,
    line_end:       Integer,
    signature:      String,  // Full method signature
    return_type:    String,
    is_public:      Boolean,
    is_static:      Boolean,
    repository_id:  String,
    summary:        String   // LLM-generated summary
})
```

### RESTEndpoint

An HTTP REST endpoint exposed by the application.

```
(:RESTEndpoint {
    id:            String,
    http_method:   String,   // GET, POST, PUT, DELETE, PATCH
    path:          String,   // URL path (e.g. "/api/v1/users/{id}")
    handler:       String,   // Qualified name of the handler method
    file_path:     String,
    repository_id: String
})
```

### KafkaTopic

A Kafka topic that the application publishes to or consumes from.

```
(:KafkaTopic {
    id:            String,
    name:          String,
    repository_id: String
})
```

### DatabaseTable

A database table the application interacts with.

```
(:DatabaseTable {
    id:            String,
    name:          String,
    schema:        String,
    repository_id: String
})
```

### Configuration

A configuration file or configuration class.

```
(:Configuration {
    id:            String,
    name:          String,
    file_path:     String,
    config_type:   String,   // "yaml", "properties", "class", etc.
    repository_id: String
})
```

### EnvironmentVariable

An environment variable referenced by the application.

```
(:EnvironmentVariable {
    id:            String,
    name:          String,   // Variable name (e.g. "DATABASE_URL")
    default_value: String,
    required:      Boolean,
    repository_id: String
})
```

---

## Relationships

| Relationship | From → To | Meaning |
|---|---|---|
| `CONTAINS` | Repository → Module, Package → Class | Structural containment |
| `CALLS` | Method → Method | Direct method invocation |
| `IMPLEMENTS` | Class → Interface | Interface implementation |
| `EXTENDS` | Class → Class | Inheritance |
| `USES` | Method → Class | Type reference or instantiation |
| `RETURNS` | Method → Class | Return type |
| `THROWS` | Method → Class | Exception type thrown |
| `READS` | Method → DatabaseTable | Database read operation |
| `WRITES` | Method → DatabaseTable | Database write operation |
| `PUBLISHES` | Method → KafkaTopic | Kafka message publication |
| `CONSUMES` | Method → KafkaTopic | Kafka message consumption |
| `DEPENDS_ON` | Class → Class | Dependency injection or import |
| `OWNS` | Class → Method, Class → Field | Class membership |

---

## Example Cypher Queries

### Find all methods called by a specific class

```cypher
MATCH (c:Class {qualified_name: 'com.example.PaymentService'})
-[:OWNS]->(m:Method)
-[:CALLS]->(called:Method)
RETURN c.name, m.name, called.name, called.file_path
```

### Find the dependency chain (impact analysis)

```cypher
MATCH path = (start:Class {id: $node_id})
             <-[:CALLS|DEPENDS_ON*1..5]-(dependent)
RETURN path
ORDER BY length(path) ASC
```

### Find all REST endpoints in a repository

```cypher
MATCH (r:Repository {id: $repository_id})
      -[:CONTAINS*1..4]->(e:RESTEndpoint)
RETURN e.http_method, e.path, e.handler
ORDER BY e.path
```

### Find classes implementing an interface

```cypher
MATCH (i:Interface {qualified_name: $interface_name})
      <-[:IMPLEMENTS]-(c:Class)
RETURN c.name, c.file_path, c.repository_id
```

### Find all Kafka consumers in a repository

```cypher
MATCH (r:Repository {id: $repository_id})
      -[:CONTAINS*1..4]->(m:Method)
      -[:CONSUMES]->(t:KafkaTopic)
RETURN m.qualified_name, t.name
```

### Find what a method depends on (full impact surface)

```cypher
MATCH (m:Method {id: $method_id})
OPTIONAL MATCH (m)-[:CALLS]->(called:Method)
OPTIONAL MATCH (m)-[:READS|WRITES]->(table:DatabaseTable)
OPTIONAL MATCH (m)-[:PUBLISHES|CONSUMES]->(topic:KafkaTopic)
RETURN m, collect(called) as calls, collect(table) as tables, collect(topic) as topics
```

---

## Index Recommendations

```cypher
-- Node lookups by ID (primary key)
CREATE INDEX idx_class_id FOR (c:Class) ON (c.id);
CREATE INDEX idx_method_id FOR (m:Method) ON (m.id);
CREATE INDEX idx_repository_id FOR (r:Repository) ON (r.id);

-- Filtered queries by repository
CREATE INDEX idx_class_repo FOR (c:Class) ON (c.repository_id);
CREATE INDEX idx_method_repo FOR (m:Method) ON (m.repository_id);

-- Name lookups
CREATE INDEX idx_class_name FOR (c:Class) ON (c.qualified_name);
CREATE INDEX idx_method_name FOR (m:Method) ON (m.qualified_name);
CREATE INDEX idx_endpoint_path FOR (e:RESTEndpoint) ON (e.path);
```
