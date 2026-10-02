"""
YamlConfigurationAdapter — Configuration Port Implementation.

Reads application configuration from layered YAML files.
Supports environment variable interpolation and environment-specific
overrides (development.yaml, production.yaml layered over application.yaml).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from ports.configuration import ConfigurationPort


class YamlConfigurationAdapter(ConfigurationPort):
    """
    YAML file-based implementation of ConfigurationPort.

    Loads configuration from:
      1. ``configs/application.yaml``       (base defaults)
      2. ``configs/{environment}.yaml``     (environment overrides)
      3. Environment variables              (highest precedence)

    Dotted key access (e.g. ``database.neo4j.uri``) traverses
    the nested YAML structure.

    Args:
        config_dir:   Path to the ``configs/`` directory.
        environment:  Active environment (``development`` or ``production``).
    """

    def __init__(
        self,
        config_dir: Path,
        environment: str = "development",
    ) -> None:
        self._config_dir = config_dir
        self._environment = environment
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load and merge configuration from YAML files."""
        base_path = self._config_dir / "application.yaml"
        env_path = self._config_dir / f"{self._environment}.yaml"

        config: Dict[str, Any] = {}

        if base_path.exists():
            with open(base_path) as f:
                base = yaml.safe_load(f) or {}
            config = self._deep_merge(config, base)

        if env_path.exists():
            with open(env_path) as f:
                env_config = yaml.safe_load(f) or {}
            config = self._deep_merge(config, env_config)

        self._config = config

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge override into base, returning a new dict."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _resolve(self, key: str) -> Any:
        """Resolve a dotted key path against the loaded config."""
        parts = key.split(".")
        current: Any = self._config
        for part in parts:
            if not isinstance(current, dict):
                return None
            current = current.get(part)
        return current

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve a configuration value, falling back to environment variables.

        Placeholder — environment variable interpolation pending.
        """
        value = self._resolve(key)
        if value is None:
            # Fall back to environment variable (uppercased, dots → underscores)
            env_key = key.upper().replace(".", "_")
            return os.environ.get(env_key, default)
        return value

    def get_required(self, key: str) -> Any:
        """Retrieve a required value or raise ConfigurationError."""
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required configuration key not found: {key!r}")
        return value

    def get_section(self, section: str) -> dict:
        """Retrieve an entire section as a dictionary."""
        value = self._config.get(section, {})
        return value if isinstance(value, dict) else {}

    def reload(self) -> None:
        """Reload configuration from disk."""
        self._load()
