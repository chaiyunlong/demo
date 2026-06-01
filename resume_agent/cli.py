"""Command line interface for the Resume Growth Advisor runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .core import ResumeGrowthAdvisor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Resume Growth Advisor agent locally.")
    parser.add_argument("--input", "-i", type=Path, help="Path to a JSON request file. Reads stdin if omitted.")
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format. Defaults to markdown.",
    )
    parser.add_argument("--config", type=Path, help="Optional agent config path.")
    return parser


def load_payload(path: Path | None) -> dict[str, Any]:
    if path:
        raw = path.read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        raise SystemExit("No input provided. Pass --input or pipe a JSON request to stdin.")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Input must be valid JSON: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = load_payload(args.input)
    advisor = ResumeGrowthAdvisor(args.config) if args.config else ResumeGrowthAdvisor()
    result = advisor.analyze(payload)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(advisor.render_markdown(result), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
