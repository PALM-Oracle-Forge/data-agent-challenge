#!/usr/bin/env python3
"""Run Oracle Forge against our local DAB mirror under `runs/<dataset>/<query>/`.

Folder layout (DAB-compatible):

    runs/<dataset>/<query_name>/
        query.json           (scaffolded from DAB)
        ground_truth.csv
        validate.py
        logs/data_agent/<root_name>/
            final_agent.json
            llm_calls.jsonl
            tool_calls.jsonl

Usage:
    # Run one query
    python run_agent.py --dataset agnews --query query1 --root_name run_0

    # Run every query in a dataset
    python run_agent.py --dataset agnews --all --root_name run_0

    # Override databases
    python run_agent.py --dataset bookreview --query query1 --root_name run_0 \\
        --databases books_database review_database
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv

load_dotenv()

from agent.config_manager import ConfigManager
from agent.oracle_forge_agent import OracleForgeAgent

KB_DATASET_OVERVIEW = ROOT_DIR / "kb" / "domain" / "dataset_overview.md"
MCP_TOOLS_YAML = ROOT_DIR / "mcp" / "tools.yaml"
RUNS_ROOT = ROOT_DIR / "runs"


def _load_question(query_dir: Path) -> str:
    raw = (query_dir / "query.json").read_text(encoding="utf-8").strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(payload, str):
        return payload
    if isinstance(payload, dict) and "query" in payload:
        return payload["query"]
    return raw


def _select_query_dirs(dataset_root: Path, query: str | None, all_queries: bool) -> List[Path]:
    if all_queries:
        dirs = sorted(p for p in dataset_root.iterdir() if p.is_dir() and p.name.startswith("query"))
        if not dirs:
            raise SystemExit(f"No query directories under {dataset_root}")
        return dirs
    if not query:
        raise SystemExit("Specify either --query <query_name> or --all.")
    qdir = dataset_root / query
    if not qdir.is_dir():
        raise SystemExit(f"Query dir not found: {qdir}")
    return [qdir]


def _write_final_agent(
    *,
    log_dir: Path,
    query_dir: Path,
    question: str,
    result: Dict[str, Any],
    messages: List[Dict[str, Any]],
    model: str,
    max_iterations: int,
    run_start: float,
    run_end: float,
) -> Path:
    """Write a DAB-shaped final_agent.json into log_dir."""
    final_payload = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "start_time": run_start,
        "end_time": run_end,
        "duration": run_end - run_start,
        "final_result": result.get("answer", ""),
        "terminate_reason": result.get("terminate_reason"),
        "messages": messages,
        "result_storage": {},
        "llm_call_count": result.get("iterations"),
        "tools": {},
        "query_dir": str(query_dir),
        "question": question,
        "max_iterations": max_iterations,
        "deployment_name": model,
        "llm_log_path": str(log_dir / "llm_calls.jsonl"),
        "tool_log_path": str(log_dir / "tool_calls.jsonl"),
        "total_usage": result.get("usage", {}),
        "confidence": result.get("confidence"),
    }
    path = log_dir / "final_agent.json"
    path.write_text(json.dumps(final_payload, indent=2, default=str), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--dataset", required=True, help="DAB dataset name (e.g. agnews).")
    parser.add_argument("--query", help="Query name under runs/<dataset>/ (e.g. query1).")
    parser.add_argument("--all", action="store_true", help="Run all queries in the dataset.")
    parser.add_argument("--root_name", default="run_0", help="Run directory name (default: run_0).")
    parser.add_argument("--iterations", type=int, default=30, help="Max LLM iterations (default: 30).")
    parser.add_argument("--databases", nargs="+", metavar="DB_ID", default=None, help="Override KB-derived DB list.")
    parser.add_argument("--use_hints", action="store_true", help="Inject db_description_with_hint.txt if present.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing logs/data_agent/<root_name>/ dir.")
    args = parser.parse_args()

    dataset_root = RUNS_ROOT / args.dataset
    if not dataset_root.is_dir():
        raise SystemExit(
            f"Dataset not scaffolded: {dataset_root}\n"
            f"Run: python scripts/scaffold_bench.py --dataset {args.dataset}"
        )

    query_dirs = _select_query_dirs(dataset_root, args.query, args.all)

    config_mgr = ConfigManager(KB_DATASET_OVERVIEW, MCP_TOOLS_YAML)
    if args.databases:
        databases_info = [{"db_id": db_id, "db_type": ""} for db_id in args.databases]
        db_ids = args.databases
    else:
        registry = config_mgr.parse_kb_dataset_registry()
        key = args.dataset.lower()
        if key not in registry:
            raise SystemExit(
                f"Dataset '{args.dataset}' not in KB registry.\n"
                f"Known: {sorted(registry.keys())}\nUse --databases to override."
            )
        databases_info = registry[key]
        db_ids = [d["db_id"] for d in databases_info]

    db_configs = config_mgr.build_db_configs_from_env(
        databases_info, dataset_name=args.dataset.lower()
    )

    print(f"Dataset      : {args.dataset}")
    print(f"Databases    : {db_ids}")
    print(f"Queries      : {[q.name for q in query_dirs]}")
    print(f"Max iters    : {args.iterations}")
    print(f"Root name    : {args.root_name}")
    print()

    agent = OracleForgeAgent(db_configs=db_configs or None, max_iterations=args.iterations)
    model = getattr(agent._client, "_openrouter_model", "unknown")

    try:
        for idx, qdir in enumerate(query_dirs, 1):
            print(f"--- ({idx}/{len(query_dirs)}) {args.dataset}/{qdir.name}")
            question = _load_question(qdir)

            log_dir = qdir / "logs" / "data_agent" / args.root_name
            if log_dir.exists():
                if not args.force:
                    print(f"  SKIP: {log_dir} already exists (use --force to overwrite)\n")
                    continue
                # Remove old logs; mirrors DAB's assert-not-exists contract once cleared
                for f in ("final_agent.json", "llm_calls.jsonl", "tool_calls.jsonl"):
                    (log_dir / f).unlink(missing_ok=True)
            log_dir.mkdir(parents=True, exist_ok=True)

            hints_text = ""
            if args.use_hints:
                for fname in ("db_description_with_hint.txt", "db_description_withhint.txt"):
                    hint_file = qdir / fname
                    if hint_file.exists():
                        hints_text = hint_file.read_text(encoding="utf-8")
                        break

            print(f"  question: {question!r}")
            run_start = time.time()
            result = agent.answer(
                {
                    "question": question,
                    "available_databases": db_ids,
                    "schema_info": {},
                    "hints": hints_text,
                    "log_dir": log_dir,
                }
            )
            run_end = time.time()

            messages = getattr(agent, "_last_messages", [])
            _write_final_agent(
                log_dir=log_dir,
                query_dir=qdir,
                question=question,
                result=result,
                messages=messages,
                model=model,
                max_iterations=args.iterations,
                run_start=run_start,
                run_end=run_end,
            )

            print(f"  answer  : {result.get('answer')}")
            print(f"  stopped : {result.get('terminate_reason')} after {result.get('iterations')} iter")
            print(f"  logs    : {log_dir}\n")
    finally:
        print("cleanup...")
        agent.end_session()


if __name__ == "__main__":
    main()
