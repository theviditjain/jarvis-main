"""
RepositoryReaderPort — Abstract Repository Reader Interface.

Defines the contract for reading source files from a repository.
This port is used exclusively by WRITE and HYBRID workflows to fetch
the current content of files that will be modified.

Repository files are the source of truth. This port provides read-only
access to those files. Write operations go through GitPort.

IMPORTANT:
  This runtime does NOT clone, manage, or store repositories.
  The adapter resolves file content from an external source
  (e.g. a remote API provided by jarvis-platform) or a locally
  available workspace managed by another service.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional


class RepositoryReaderPort(ABC):
    """
    Abstract port for reading source files from a repository.

    Used by the Repository Reader node in WRITE / HYBRID workflows.
    The application layer never reads files directly — it always goes
    through this port.
    """

    @abstractmethod
    async def read_file(
        self,
        repository_id: str,
        file_path: str,
        *,
        ref: Optional[str] = None,
    ) -> str:
        """
        Read the content of a single file from a repository.

        Args:
            repository_id: Identifier of the target repository.
            file_path:     Repository-relative path to the file.
            ref:           Git ref (branch, tag, commit) to read from.
                           Defaults to the repository's default branch.

        Returns:
            The raw file content as a UTF-8 string.

        Raises:
            FileNotFoundError: If the file does not exist at the given ref.
            RepositoryReaderError: If the read operation fails.
        """
        ...

    @abstractmethod
    async def list_files(
        self,
        repository_id: str,
        path: str = "",
        *,
        ref: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> List[str]:
        """
        List files within a directory of a repository.

        Args:
            repository_id: Identifier of the target repository.
            path:          Directory path to list (empty = root).
            ref:           Git ref to list at.
            pattern:       Glob pattern to filter results.

        Returns:
            List of repository-relative file paths.
        """
        ...

    @abstractmethod
    async def read_files(
        self,
        repository_id: str,
        file_paths: List[str],
        *,
        ref: Optional[str] = None,
    ) -> dict[str, str]:
        """
        Read multiple files in a single batch operation.

        Args:
            repository_id: Identifier of the target repository.
            file_paths:    List of repository-relative file paths.
            ref:           Git ref to read from.

        Returns:
            Dictionary mapping file_path → file_content.
        """
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify that the repository reader backend is reachable."""
        ...
