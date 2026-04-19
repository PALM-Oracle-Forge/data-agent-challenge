# agent — Oracle Forge Runtime

All agent source code. Flat Python modules — no deep package nesting.

## Components

| File | Role |
| --- | --- |
| [oracle_forge_agent.py](oracle_forge_agent.py) | `OracleForgeAgent` — top-level orchestrator (`process_query`, `answer`, session mgmt) |
| [context_manager.py](context_manager.py) | `ContextManager` — three-layer context assembly (schema + KB + corrections) |
| [query_router.py](query_router.py) | `QueryRouter` — entity extraction, multi-DB decomposition, dialect selection |
| [execution_engine.py](execution_engine.py) | `ExecutionEngine` — MCP dispatch + sandbox dispatch + retry wiring |
| [self_correction.py](self_correction.py) | `SelfCorrectionLoop` — 5 failure types, LLM-based fix, max 3 retries |
| [mcp_toolbox.py](mcp_toolbox.py) | `MCPToolbox` — hybrid routing (HTTP toolbox + direct MongoDB/DuckDB) |
| [mcp_client.py](mcp_client.py) | Typed MCP interface adapter (scaffold — not used at runtime) |
| [sandbox_client.py](sandbox_client.py) | `SandboxClient` — HTTP sandbox execution |
| [llm_client.py](llm_client.py) | Anthropic / OpenRouter SDK wrapper |
| [duckdb_mcp_server.py](duckdb_mcp_server.py) | Standalone DuckDB MCP HTTP service |
| [agentic_loop.py](agentic_loop.py) | Agentic-mode loop (LLM-driven tool calling) |
| [config_manager.py](config_manager.py) | KB registry parsing + env-based DB config building |
| [models/models.py](models/models.py) | Shared dataclasses (`QueryResult`, `ContextBundle`, `QueryEvent`, …) |
| [types.py](types.py) | Extra type aliases |

## Runtime context

[AGENT.md](AGENT.md) is loaded **first** at every session start by `ContextManager`. It contains the operating rules, known join-key fixes, and the on-demand file map for KB documents.

## Tests

```bash
uv run pytest agent/tests/ -v
```

See [agent/tests/](tests/) for unit, integration, and property tests (15+ files).

## Conventions

- Shared dataclasses live **only** in `agent/models/models.py` — never redefine them elsewhere.
- All database access goes through `MCPToolbox.call_tool()` — no raw drivers outside `mcp_toolbox.py`.
- LLM temperature is always `0.0`. Max retries = 3.
- The corrections log (`kb/corrections/corrections_log.md`) is **append-only**.
