"""
LLMPort — Abstract LLM Interface.

Defines the contract that any LLM adapter must satisfy. The application
layer depends exclusively on this port — it has no knowledge of OpenAI,
Anthropic, or any other concrete provider.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Optional


class LLMPort(ABC):
    """
    Abstract port for Large Language Model interactions.

    Concrete implementations live in ``adapters/outbound/``.
    The application layer must NEVER import from adapters directly.

    All methods are async to support non-blocking I/O throughout the
    streaming workflow.
    """

    @abstractmethod
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
        Request a single completion from the LLM.

        Args:
            system_prompt: Instructions defining the LLM's role and constraints.
            user_prompt:   The user's message or assembled context.
            temperature:   Sampling temperature [0.0, 2.0].
            max_tokens:    Maximum tokens in the completion.
            model:         Override the default model for this request.

        Returns:
            The raw completion string from the LLM.

        Raises:
            LLMError: If the LLM call fails or times out.
        """
        ...

    @abstractmethod
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
        Stream a completion from the LLM token by token.

        Args:
            system_prompt: Instructions defining the LLM's role.
            user_prompt:   The user's message or assembled context.
            temperature:   Sampling temperature [0.0, 2.0].
            max_tokens:    Maximum tokens in the completion.
            model:         Override the default model.

        Yields:
            Token strings as they are streamed from the provider.

        Raises:
            LLMError: If the LLM stream fails or is interrupted.
        """
        ...

    @abstractmethod
    async def embed(
        self,
        texts: List[str],
        *,
        model: Optional[str] = None,
    ) -> List[List[float]]:
        """
        Generate vector embeddings for a list of texts.

        Args:
            texts: List of text strings to embed.
            model: Override the default embedding model.

        Returns:
            A list of embedding vectors (one per input text).

        Raises:
            LLMError: If the embedding call fails.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Verify that the LLM provider is reachable and operational.

        Returns:
            True if the provider is healthy, False otherwise.
        """
        ...
