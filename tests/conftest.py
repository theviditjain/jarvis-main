"""
Root pytest conftest.py.

Adds src/ to sys.path so all tests can import from domain/, agent/,
ports/, adapters/, and infrastructure/ without a src. prefix —
mirroring the PYTHONPATH=src runtime convention.
"""

from __future__ import annotations

import sys
import pytest
from pathlib import Path

# Add src/ to sys.path so test imports match production PYTHONPATH=src
_repo_root = Path(__file__).parent
_src = _repo_root / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

# Re-export all fixtures so pytest discovers them automatically
from tests.fixtures.mock_ports import (  # noqa: F401
    mock_llm,
    mock_graph,
    mock_vector,
    mock_streaming,
    base_state,
    read_intent,
    write_intent,
    MockLLMPort,
    MockGraphPort,
    MockVectorSearchPort,
    MockStreamingPort,
)

@pytest.fixture
def runnable_config():
    """Mock RunnableConfig containing a mock DI container for LangGraph nodes."""
    from langchain_core.runnables import RunnableConfig
    from unittest.mock import MagicMock
    
    mock_container = MagicMock()
    mock_container.logging.bind.return_value = MagicMock()
    mock_container.audit = MagicMock()
    
    return RunnableConfig(configurable={"container": mock_container})
