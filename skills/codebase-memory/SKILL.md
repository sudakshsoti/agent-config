---
name: codebase-memory
description: "Use to query a codebase knowledge graph for architecture, callers, dependencies, dead code, impact analysis, and structural refactoring evidence. Not for agent-config harness changes (harness-config-maintenance) or skill install and retirement (skill-lifecycle)."
disable-model-invocation: true
---

# Codebase Memory — Knowledge Graph Tools

Graph tools return precise structural results in ~500 tokens vs ~80K for grep.

## Quick Decision Matrix

| Question                | Tool call                                               | Caveat                                                                                                |
| ----------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Who calls X?            | `trace_path(direction="inbound")`                       | Misses cross-service callers; use `direction="both"`. Needs the exact name: `search_graph` first.      |
| What does X call?       | `trace_path(direction="outbound")`                      | Misses cross-service callees; use `direction="both"`. Needs the exact name: `search_graph` first.      |
| Full call context       | `trace_path(direction="both")`                          | Needs the exact name: `search_graph(name_pattern=...)` first.                                         |
| Find by name pattern    | `search_graph(name_pattern="...")`                      | 10 results per page; check `has_more` and use `offset`.                                               |
| Dead code               | `search_graph(max_degree=0, exclude_entry_points=true)` | Degree filters also count rows; `query_graph` is capped at 200 rows.                                  |
| Cross-service edges     | `query_graph` with Cypher                               | `search_graph(relationship="HTTP_CALLS")` filters nodes by degree, not edges; Cypher shows real edges. |
| Impact of local changes | `detect_changes()`                                      | Maps the git diff to affected symbols.                                                                |
| Risk-classified trace   | `trace_path(risk_labels=true)`                          | Adds a risk label to each hop so high-blast-radius callers sort first.                                |
| Text search             | `search_code` or Grep                                   |                                                                                                       |

## Exploration Workflow

1. `list_projects` — check if project is indexed
2. `get_graph_schema` — understand node/edge types
3. `search_graph(label="Function", name_pattern=".*Pattern.*")` — find code
4. `get_code_snippet(qualified_name="project.path.FuncName")` — read source

## Tracing Workflow

1. `search_graph(name_pattern=".*FuncName.*")` — discover exact name
2. `trace_path(function_name="FuncName", direction="both", depth=3)` — trace
3. `detect_changes()` — map git diff to affected symbols

## Quality Analysis

- Dead code: `search_graph(max_degree=0, exclude_entry_points=true)`
- High fan-out: `search_graph(min_degree=10, relationship="CALLS", direction="outbound")`
- High fan-in: `search_graph(min_degree=10, relationship="CALLS", direction="inbound")`

## 14 MCP Tools

`index_repository`, `index_status`, `list_projects`, `delete_project`,
`search_graph`, `search_code`, `trace_path`, `detect_changes`,
`query_graph`, `get_graph_schema`, `get_code_snippet`, `get_architecture`,
`manage_adr`, `ingest_traces`

## Edge Types

CALLS, HTTP_CALLS, ASYNC_CALLS, IMPORTS, DEFINES, DEFINES_METHOD,
HANDLES, IMPLEMENTS, OVERRIDE, USAGE, FILE_CHANGES_WITH,
CONTAINS_FILE, CONTAINS_FOLDER, CONTAINS_PACKAGE

## Cypher Examples (for query_graph)

Property names below (`url_path`, `confidence`, `file_path`) are examples: confirm them with `get_graph_schema` first.

```
MATCH (a)-[r:HTTP_CALLS]->(b) RETURN a.name, b.name, r.url_path, r.confidence LIMIT 20
MATCH (f:Function) WHERE f.name =~ '.*Handler.*' RETURN f.name, f.file_path
MATCH (a)-[r:CALLS]->(b) WHERE a.name = 'main' RETURN b.name
```
