"""Google Vertex AI client for Gemini backfill / regeneration.

Uses Application Default Credentials or GOOGLE_APPLICATION_CREDENTIALS.
Never hardcodes secrets. Set GOOGLE_CLOUD_PROJECT (defaults to automatic-summer-16f3p).
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from poem_annotator.config import VERTEX_PROJECT_ID, VERTEX_LOCATION, VERTEX_GEMINI_MODEL


class VertexAIError(RuntimeError):
    pass


def _model_id() -> str:
    raw = VERTEX_GEMINI_MODEL.strip()
    if "/models/" in raw:
        return raw.rsplit("/models/", 1)[-1]
    if raw.startswith("publishers/google/models/"):
        return raw.split("/")[-1]
    return raw


def generate_text(
    system_prompt: str,
    user_prompt: str,
    *,
    max_output_tokens: int = 2048,
    temperature: float = 0.1,
    json_mode: bool = True,
) -> str:
    """Call Vertex Gemini via google-genai; return response text."""
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise VertexAIError(
            "google-genai is required for Vertex AI. Install with: pip install google-genai"
        ) from exc

    project = os.getenv("GOOGLE_CLOUD_PROJECT", VERTEX_PROJECT_ID).strip()
    location = os.getenv("GOOGLE_CLOUD_LOCATION", VERTEX_LOCATION).strip()
    model = _model_id()

    client = genai.Client(vertexai=True, project=project, location=location)

    cfg_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
    }
    if system_prompt:
        cfg_kwargs["system_instruction"] = system_prompt
    if json_mode:
        cfg_kwargs["response_mime_type"] = "application/json"

    try:
        response = client.models.generate_content(
            model=model,
            contents=user_prompt,
            config=types.GenerateContentConfig(**cfg_kwargs),
        )
    except Exception as exc:
        raise VertexAIError(str(exc)) from exc

    text = getattr(response, "text", None) or ""
    if not text.strip():
        raise VertexAIError("Vertex Gemini returned empty content")
    return text.strip()


def generate_json(system_prompt: str, user_prompt: str, **kwargs: Any) -> Any:
    raw = generate_text(system_prompt, user_prompt, json_mode=True, **kwargs)
    stripped = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", stripped, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        stripped = fence.group(1).strip()
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        start, end = stripped.find("{"), stripped.rfind("}")
        if start != -1 and end > start:
            return json.loads(stripped[start : end + 1])
        raise VertexAIError(f"Vertex response was not valid JSON: {raw[:200]}") from None
