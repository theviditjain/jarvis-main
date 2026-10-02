"""
GitPort — Abstract Git Operations Interface.

Defines the contract for performing Git operations as part of the WRITE
workflow. This port is the final step before a patch is persisted and
jarvis-parser is signalled to re-index the changed files.

IMPORTANT:
  Git operations are ONLY performed in WRITE and HYBRID execution modes.
  This port is NEVER called in READ mode.
  After a successful write, the changed files are submitted for re-indexing
  by jarvis-parser — this runtime does NOT trigger re-indexing directly.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.models.patch import Patch


class GitPort(ABC):
    """
    Abstract port for Git operations.

    Used exclusively by the Git Operations node in WRITE / HYBRID workflows.
    No other node should call this port.
    """

    @abstractmethod
    async def create_branch(
        self,
        repository_id: str,
        branch_name: str,
        *,
        from_ref: Optional[str] = None,
    ) -> str:
        """
        Create a new branch in the repository.

        Args:
            repository_id: Identifier of the target repository.
            branch_name:   Name for the new branch.
            from_ref:      Starting ref (defaults to default branch).

        Returns:
            The SHA of the commit the branch was created at.
        """
        ...

    @abstractmethod
    async def apply_patch(
        self,
        repository_id: str,
        patch: Patch,
    ) -> str:
        """
        Apply a validated patch to the repository.

        Args:
            repository_id: Identifier of the target repository.
            patch:         Validated Patch object to apply.

        Returns:
            The SHA of the resulting commit.

        Raises:
            GitOperationError: If the patch cannot be applied cleanly.
        """
        ...

    @abstractmethod
    async def create_pull_request(
        self,
        repository_id: str,
        branch: str,
        title: str,
        description: str,
        *,
        base_branch: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> str:
        """
        Create a pull request for a patch branch.

        Args:
            repository_id: Identifier of the target repository.
            branch:        Source branch containing the patch.
            title:         PR title.
            description:   PR body (markdown).
            base_branch:   Target branch for the PR.
            labels:        Optional labels to apply to the PR.

        Returns:
            URL of the created pull request.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify that the Git provider is reachable."""
        ...
