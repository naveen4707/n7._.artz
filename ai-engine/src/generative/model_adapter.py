"""Model adapter for optional Loomis AI generative enhancement.

The rest of Loomis AI does not depend on this module. If the API is unavailable,
the deterministic renderer remains the guaranteed fallback.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path
from typing import Optional


class GenerativeEnhancementError(RuntimeError):
    """Raised when generative enhancement cannot be completed."""


class OpenAIImageAdapter:
    """Small replaceable adapter around the OpenAI Images API."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        self.model = model or os.getenv("LOOMIS_IMAGE_MODEL", "gpt-image-2")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise GenerativeEnhancementError(
                "OPENAI_API_KEY is not set. Configure it in the environment."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise GenerativeEnhancementError(
                "The OpenAI Python package is not installed. "
                "Run: pip install openai"
            ) from exc

        self.client = OpenAI(api_key=self.api_key)

    def enhance(
        self,
        image_path: str | Path,
        output_path: str | Path,
        prompt: str,
    ) -> Path:
        """Edit an existing rendered stage and save the returned image."""
        source = Path(image_path)
        target = Path(output_path)

        if not source.exists():
            raise GenerativeEnhancementError(
                f"Input image does not exist: {source}"
            )

        target.parent.mkdir(parents=True, exist_ok=True)

        try:
            with source.open("rb") as image_file:
                result = self.client.images.edit(
                    model=self.model,
                    image=image_file,
                    prompt=prompt,
                )
        except Exception as exc:
            raise GenerativeEnhancementError(
                f"Image generation request failed: {exc}"
            ) from exc

        if not getattr(result, "data", None):
            raise GenerativeEnhancementError(
                "The image API returned no image data."
            )

        item = result.data[0]
        b64_json = getattr(item, "b64_json", None)

        if not b64_json:
            raise GenerativeEnhancementError(
                "The image API response did not contain b64_json."
            )

        try:
            target.write_bytes(base64.b64decode(b64_json))
        except Exception as exc:
            raise GenerativeEnhancementError(
                f"Could not decode generated image: {exc}"
            ) from exc

        return target
