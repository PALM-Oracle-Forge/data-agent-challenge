# kb — Knowledge Base

The Knowledge Base feeds the ContextManager's three layers. Each subdirectory has a distinct role.

| Directory | Role | Loaded at runtime? |
| --- | --- | --- |
| [domain/](domain/) | **KB v2** — dataset overview, join-key glossary, schema, domain terms, SQL conventions, unstructured field inventory | Yes (Layer 2) |
| [evaluation/](evaluation/) | DAB format, scoring method, failure categories | Yes (Layer 2) |
| [corrections/](corrections/) | **KB v3** — append-only `corrections_log.md` — the self-learning loop | Yes (Layer 3) |
| [architecture/](architecture/) | Team reference: context layers, memory system, self-correcting execution, tool scoping | **No** — team reference only |

## Versioning

- **v1** — schema introspection (Layer 1, generated at runtime by `utils/schema_introspector.py`)
- **v2** — domain knowledge (this directory, `kb/domain/` and `kb/evaluation/`)
- **v3** — corrections memory (`kb/corrections/corrections_log.md`)

See [CHANGELOG.md](CHANGELOG.md) for per-version changes.

## Rules

- **corrections_log.md is append-only.** Never edit existing entries.
- **SQL dialect and DB behavioral rules go in `domain/`, not in the corrections log.** The corrections log is reserved for specific runtime failures and their fixes.
- **Every new document in `domain/` must pass the injection probe** before merging — see [probes/README.md](../probes/README.md) and `kb/CHANGELOG.md`.
- `architecture/` is **not** loaded at runtime — edit freely without invalidating the agent's context.
