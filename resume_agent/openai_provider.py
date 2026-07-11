"""OpenAI Responses API integration for the Resume Growth Advisor agent.

ChatGPT Plus is a ChatGPT web subscription, not an API credential. This module
uses the OpenAI API with an API key from OPENAI_API_KEY and can be paired with a
Plus account only if the same user also has API billing configured.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

DEFAULT_OPENAI_MODEL = "gpt-5.2"
DEFAULT_RESPONSES_URL = "https://api.openai.com/v1/responses"


class OpenAIProviderError(RuntimeError):
    """Raised when the OpenAI provider cannot complete a request."""


@dataclass(frozen=True)
class OpenAIResponsesClient:
    """Minimal dependency-free client for OpenAI's Responses API."""

    api_key: str | None = None
    model: str = DEFAULT_OPENAI_MODEL
    endpoint: str = DEFAULT_RESPONSES_URL
    timeout: int = 60

    @classmethod
    def from_env(cls, model: str | None = None) -> "OpenAIResponsesClient":
        return cls(api_key=os.getenv("OPENAI_API_KEY"), model=model or os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL))

    def generate_resume_report(self, system_prompt: str, user_payload: dict[str, Any], baseline_report: str) -> str:
        """Generate a GPT-backed resume report using the deterministic report as grounding."""

        if not self.api_key:
            raise OpenAIProviderError(
                "OPENAI_API_KEY is not set. ChatGPT Plus alone cannot authenticate API calls; "
                "create an API key on platform.openai.com and export it first."
            )

        prompt = _build_user_prompt(user_payload, baseline_report)
        response_payload = {
            "model": self.model,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(response_payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OpenAIProviderError(f"OpenAI API request failed with HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise OpenAIProviderError(f"OpenAI API request failed: {exc.reason}") from exc

        output_text = _extract_output_text(data)
        if not output_text:
            raise OpenAIProviderError("OpenAI API response did not contain output text.")
        return output_text


def load_system_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


def _build_user_prompt(user_payload: dict[str, Any], baseline_report: str) -> str:
    return (
        "请基于以下用户输入和确定性基线报告，生成一份更自然、更完整、可直接交付用户的中文简历与面试辅导报告。\n"
        "要求：不得编造用户未提供的信息；缺少数据时先提示补充或使用保守表达；保留诊断、重写、面试辅导和风险提醒结构。\n\n"
        "## 用户输入 JSON\n"
        f"{json.dumps(user_payload, ensure_ascii=False, indent=2)}\n\n"
        "## 确定性基线报告\n"
        f"{baseline_report}"
    )


def _extract_output_text(data: dict[str, Any]) -> str:
    if isinstance(data.get("output_text"), str):
        return data["output_text"]

    chunks: list[str] = []
    for output_item in data.get("output", []) or []:
        for content_item in output_item.get("content", []) or []:
            text = content_item.get("text")
            if isinstance(text, str):
                chunks.append(text)
    return "\n".join(chunks).strip()
