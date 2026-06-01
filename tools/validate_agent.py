#!/usr/bin/env python3
"""Validate the Resume Growth Advisor agent package without external dependencies."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "agent" / "resume_interview_agent.json"


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def require_path(relative_path: str) -> None:
    path = ROOT / relative_path
    if not path.exists():
        raise SystemExit(f"Missing referenced file: {relative_path}")
    if path.is_file() and path.stat().st_size == 0:
        raise SystemExit(f"Referenced file is empty: {relative_path}")


def validate_config(config: dict) -> None:
    required_top_level = [
        "agent_id",
        "name",
        "version",
        "entry_prompt",
        "principles",
        "workflow",
        "schemas",
        "system_prompt",
    ]
    missing = [key for key in required_top_level if key not in config]
    if missing:
        raise SystemExit(f"Missing top-level config keys: {', '.join(missing)}")

    require_path(config["system_prompt"])

    workflow = config["workflow"]
    if not isinstance(workflow, list) or not workflow:
        raise SystemExit("workflow must be a non-empty list")

    seen_ids: set[str] = set()
    for node in workflow:
        for key in ["id", "name", "prompt", "outputs"]:
            if key not in node:
                raise SystemExit(f"Workflow node missing {key}: {node}")
        if node["id"] in seen_ids:
            raise SystemExit(f"Duplicate workflow node id: {node['id']}")
        seen_ids.add(node["id"])
        require_path(node["prompt"])
        if not isinstance(node["outputs"], list) or not node["outputs"]:
            raise SystemExit(f"Workflow node outputs must be non-empty: {node['id']}")

    schemas = config["schemas"]
    for schema_name in ["input", "output"]:
        if schema_name not in schemas:
            raise SystemExit(f"Missing schema reference: {schema_name}")
        require_path(schemas[schema_name])
        load_json(ROOT / schemas[schema_name])


def main() -> int:
    config = load_json(CONFIG_PATH)
    validate_config(config)
    print("Agent package validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
