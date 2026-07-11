"""Command line interface for the Resume Growth Advisor runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .core import ResumeGrowthAdvisor
from .openai_provider import OpenAIProviderError, OpenAIResponsesClient, load_system_prompt


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
    parser.add_argument(
        "--engine",
        choices=("deterministic", "openai"),
        default="deterministic",
        help="Use the local deterministic runtime or call OpenAI Responses API.",
    )
    parser.add_argument("--model", help="OpenAI model to use when --engine openai is selected.")
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
    deterministic_markdown = advisor.render_markdown(result)

    if args.engine == "openai":
        system_prompt = load_system_prompt(advisor.config["system_prompt"])
        client = OpenAIResponsesClient.from_env(model=args.model)
        try:
            output_text = client.generate_resume_report(system_prompt, payload, deterministic_markdown)
        except OpenAIProviderError as exc:
            raise SystemExit(str(exc)) from exc

        if args.format == "json":
            print(json.dumps({"engine": "openai", "model": client.model, "output_text": output_text}, ensure_ascii=False, indent=2))
        else:
            print(output_text)
        return 0

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(deterministic_markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
