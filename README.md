# Oracle Forge - Data Agent Benchmark

Oracle Forge is Team PaLM's multi-database data analytics agent for the UC Berkeley DataAgentBench (DAB) benchmark. It answers natural-language questions across PostgreSQL, MongoDB, SQLite, and DuckDB, keeps traceable execution logs, and uses a sandbox for post-retrieval work such as extraction, merge, and validation.

## Team

Team: `PaLM`

| Member | Role | Responsibilities |
| --- | --- | --- |
| Bethel Yohannes | Lead Architect | Agent integration, MCP setup, repository structure |
| Yosef Zewdu | Infrastructure Engineer | Database setup, environment configuration |
| Estifanos Teklay | Knowledge Engineer | Knowledge base and context layers |
| Melkam Berhane | Knowledge Engineer | Domain knowledge and validation |

## Architecture Overview

```
Oracle Forge Agent
    |
    |-- Context Manager (KB layers, schema, domain knowledge)
    |-- Agentic Loop (LLM + Tool execution)
    |-- MCP Toolbox (Database connectors)
    |   |-- PostgreSQL (bookreview_db)
    |   |-- MongoDB (yelp_db)
    |   |-- SQLite (review_database)
    |   |-- DuckDB (user_database)
    |-- Evaluation Harness (Scoring, tracing, validation)
    |-- Self-Correction Loop (Error recovery)
```

## Quick Start (5 Minutes)

**For Complete Beginners - No Prior Knowledge Required**

### Prerequisites
- Python 3.10+ installed
- Docker installed and running
- Git installed

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd data-agent-challenge
```

### Step 2: Install Dependencies
```bash
# Install uv (fast Python package installer)
pip install uv

# Install project dependencies
uv sync
```

### Step 3: Start Required Services
```bash
# Start PostgreSQL container
docker run -d --name team-dab-postgres -e POSTGRES_DB=bookreview_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=teampalm -p 5432:5432 postgres:15

# Start MongoDB container
docker run -d --name team-dab-mongo -p 27017:27017 mongo:6.0

# Start MCP Toolbox (PostgreSQL/MongoDB/SQLite)
uv run python toolbox/mcp_server.py &

# Start DuckDB MCP Server
uv run python agent/duckdb_mcp_server.py &
```

### Step 4: Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API key
# Add your LLM API key (OPENROUTER_API_KEY or ANTHROPIC_API_KEY)
```

### Step 5: Run Your First Query
```bash
# Test with BookReview dataset
uv run python run_agent.py \
  --dataset bookreview \
  --query query_bookreview_benchmark/query1/query.json \
  --iterations 10 \
  --root_name run_0
```

### Step 6: Evaluate Results
```bash
# Score your agent's performance
uv run python eval/run_evaluation.py \
  --dataset bookreview \
  --run run_0 \
  --note "first_run"

# View score progression
uv run python eval/run_evaluation.py --progress
```

## Directory Structure

```
data-agent-challenge/
|-- README.md                    # This file
|-- .env.example                 # Environment variables template
|-- run_agent.py                 # Main agent runner
|-- agent/                       # Agent core logic
|   |-- oracle_forge_agent.py   # Main agent class
|   |-- agentic_loop.py          # LLM + tool execution loop
|   |-- mcp_toolbox.py           # Database connector toolbox
|   |-- llm_client.py            # LLM API client
|   |-- loop_detector.py         # Loop detection for repetitive queries
|   |-- planner_fallback.py      # Error recovery and safe execution
|   |-- duckdb_mcp_server.py     # DuckDB MCP server
|   `-- tests/                   # Agent unit tests
|-- kb/                          # Knowledge base
|   |-- domain/                  # Domain knowledge (datasets, schemas)
|   |-- architecture/            # System architecture docs
|   |-- evaluation/              # Evaluation methodology
|   `-- agent/                   # Agent behavior guidelines
|-- eval/                        # Evaluation harness
|   |-- run_evaluation.py        # Scoring system
|   |-- score_log.json           # Historical scores
|   `-- trace_log.jsonl          # Detailed execution traces
|-- utils/                       # Utility functions
|   |-- dab_output.py            # DAB format output handling
|   `-- ...
|-- mcp/                         # MCP configuration
|   |-- tools.yaml               # Database tool definitions
|   |-- MANUAL.md                # MCP setup guide
|   `-- servers/                 # MCP server implementations
|-- query_bookreview_benchmark/  # BookReview test queries
|-- query_yelp/                  # Yelp test queries
|-- results/                     # Agent execution results
|   |-- query_bookreview/        # BookReview run results
|   `-- query_yelp/              # Yelp run results
`-- toolbox/                     # MCP toolbox server
```

## Supported Databases

| Database | Dataset | Tables/Collections | Access Method |
|----------|----------|-------------------|---------------|
| PostgreSQL | bookreview | books_info | MCP Tool: `run_query` |
| MongoDB | yelp | business, checkin | MCP Tool: `find_yelp_businesses` |
| SQLite | bookreview | review | MCP Tool: `sqlite_bookreview_query` |
| DuckDB | yelp | review, tip, user | MCP Tool: `duckdb_yelp_query` |

## Common Issues & Solutions

### Issue: "Database connection refused"
**Solution**: Check Docker containers are running
```bash
docker ps  # Should show postgres and mongo containers
```

### Issue: "LoopDetector initialization error"
**Solution**: Clear Python cache
```bash
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Issue: "DuckDB server not starting"
**Solution**: Check for module conflicts
```bash
# The agent/types.py conflicts with standard library
# This is a known issue, use uv run to avoid it
```

## Evaluation Results

Current performance across datasets:

```bash
# View latest scores
uv run python eval/run_evaluation.py --progress

# Expected output:
# bookreview: 100.0% pass@1
# yelp: 28.6% pass@1
```

## Contributing

1. **Add new queries**: Place in appropriate `query_*/` directory
2. **Improve knowledge**: Update `kb/domain/` files
3. **Fix bugs**: Add tests in `agent/tests/`
4. **Update docs**: Keep README files current

## Live Agent

The agent can be run interactively or through batch evaluation. See `run_agent.py --help` for all options.

## Support

For issues:
1. Check this README first
2. Look in `kb/evaluation/` for methodology
3. Check `agent/tests/` for example usage
4. Review `mcp/MANUAL.md` for database setup

## What We Built

Oracle Forge is organized around four runtime layers:

1. `OracleForgeAgent` handles the user question and assembles context.
2. `AgenticLoop` executes the LLM + tool interaction.
3. `MCPToolbox` provides database access across PostgreSQL, MongoDB, SQLite, and DuckDB.
4. `Evaluation Harness` scores performance and tracks progress.

## Live Agent Demo

The agent can be run interactively or through batch evaluation. See `run_agent.py --help` for all options.

## Technology Stack

- **PostgreSQL, MongoDB, SQLite**: Google MCP Toolbox
- **DuckDB**: Custom MCP service  
- **Sandbox**: Python execution environment
- **Evaluation**: DAB-style query packaging and scoring
