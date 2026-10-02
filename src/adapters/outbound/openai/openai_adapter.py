"""
OpenAIAdapter — LLM Port Implementation.

Concrete implementation of LLMPort using the OpenAI Python SDK.
This adapter handles all communication with the OpenAI API.

IMPORTANT:
  - This adapter contains ONLY infrastructure concerns.
  - No business logic, no prompts, no domain concepts.
  - Prompts are built by the application layer and passed in.
  - All retry, rate-limiting, and error-handling logic lives here.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator, List, Optional

from openai import AsyncOpenAI

from ports.llm import LLMPort


class OpenAIAdapter(LLMPort):
    """
    OpenAI implementation of LLMPort.

    Wraps the official OpenAI async Python client. Supports both
    chat completions and embeddings. Streams tokens using the
    official streaming API.

    Configuration keys (via ConfigurationPort):
        llm.openai.api_key:         OpenAI API key.
        llm.openai.model:           Default chat model (e.g. gpt-4o).
        llm.openai.embedding_model: Default embedding model.
        llm.openai.timeout:         Request timeout in seconds.
        llm.openai.max_retries:     Number of automatic retries.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        embedding_model: str = "text-embedding-3-large",
        timeout: float = 60.0,
        max_retries: int = 3,
    ) -> None:
        """
        Initialise the OpenAI adapter.

        Args:
            api_key:         OpenAI API key.
            model:           Default chat completion model.
            embedding_model: Default embedding model.
            timeout:         HTTP request timeout in seconds.
            max_retries:     Number of automatic retries on transient errors.
        """
        self._client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._model = model
        self._embedding_model = embedding_model

    async def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        model: Optional[str] = None,
    ) -> str:
        """
        Request a single chat completion from OpenAI.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("OpenAIAdapter.complete is not yet implemented.")

    async def stream(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        model: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion from OpenAI token by token.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("OpenAIAdapter.stream is not yet implemented.")
        # Required by mypy for async generator type; never reached.
        yield ""  # type: ignore[misc]

    async def embed(
        self,
        texts: List[str],
        *,
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("OpenAIAdapter.embed is not yet implemented.")

    async def health_check(self) -> bool:
        """
        Verify that the OpenAI API is reachable.

        Placeholder — implementation pending.
        """
        raise NotImplementedError("OpenAIAdapter.health_check is not yet implemented.")
