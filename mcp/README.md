# MCP Setup Guide

This guide explains how to use the shared MCP Toolbox configuration in this repo so any team member can test and use the current database tools without repeating setup/debugging.

## What this setup covers

Right now the MCP config supports the shared DAB databases currently running on the team server:

- **PostgreSQL** -> `bookreview_db`
- **MongoDB** -> `yelp_db`

This is the current working scope. SQLite and DuckDB are not part of this MCP config yet.

---

## Files

- **Toolbox binary:** `bin/toolbox`
- **Project wrapper:** `./toolbox`
- **MCP config:** `mcp/tools.yaml`

---

## Current database connections

### PostgreSQL
- Host: `team-dab-postgres`
- Port: `5432`
- Database: `bookreview_db`

### MongoDB
- Host: `team-dab-mongo`
- Port: `27017`
- Database: `yelp_db`

---

## Current tools

### PostgreSQL tools
- `list_tables`
- `describe_books_info`
- `preview_books_info`

### MongoDB tools
- `find_yelp_businesses`
- `find_yelp_checkins`

---

## Current config

The working config is stored in `mcp/tools.yaml`.

## How to test in the SSH instance

From the repo root:

```bash
cd ~/data-agent-challenge

./toolbox invoke list_tables
./toolbox invoke describe_books_info
./toolbox invoke preview_books_info
./toolbox invoke find_yelp_businesses
./toolbox invoke find_yelp_checkins
```

To launch the Toolbox UI against the repo MCP config:

```bash
./toolbox serve --enable-api --ui
```

If port `5000` is already in use, launch the UI on `5001` instead:

```bash
TOOLBOX_URL=http://127.0.0.1:5001 ./toolbox --ui --port 5001
```
