"""
ConfigurationPort — Abstract Configuration Interface.

Defines the contract for reading application configuration. All
configuration values flow into the application layer exclusively
through this port — never through os.environ or direct file access.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class ConfigurationPort(ABC):
    """
    Abstract port for reading application configuration.

    Adapters may read from YAML files, environment variables, or remote
    configuration services (e.g. Vault). The application layer must not
    know where configuration comes from.
    """

    @abstractmethod
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve a configuration value by dotted key path.

        Args:
            key:     Dotted key path (e.g. ``database.neo4j.uri``).
            default: Value to return if the key is not found.

        Returns:
            The configuration value, or ``default`` if not found.
        """
        ...

    @abstractmethod
    def get_required(self, key: str) -> Any:
        """
        Retrieve a required configuration value.

        Args:
            key: Dotted key path.

        Returns:
            The configuration value.

        Raises:
            ConfigurationError: If the key is not present.
        """
        ...

    @abstractmethod
    def get_section(self, section: str) -> dict:
        """
        Retrieve an entire configuration section as a dictionary.

        Args:
            section: Top-level section name.

        Returns:
            Dictionary of key-value pairs in the section.
        """
        ...

    @abstractmethod
    def reload(self) -> None:
        """Reload configuration from the underlying source."""
        ...
