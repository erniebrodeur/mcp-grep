"""Unit tests for the MCP server implementation.

These tests provide fast unit-level testing of the server components.
For functional tests, see the BDD tests in test_features.py.
"""

import json
import os
import tempfile
import shutil
from pathlib import Path

import pytest

from mcp_grep.server import grep, grep_info, get_grep_info


@pytest.fixture
def test_file():
    """Create a temporary file for testing."""
    _, path = tempfile.mkstemp()
    yield path
    os.unlink(path)


@pytest.fixture
def test_dir():
    """Create a temporary directory for testing."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    shutil.rmtree(dir_path)


class TestGrepTool:
    """Tests for the grep tool."""

    def test_basic_match(self, test_file):
        """Test basic pattern matching."""
        # Arrange
        with open(test_file, 'w') as f:
            f.write("Line one has apple\nLine two has banana\nLine three has orange")
        
        # Act
        result = grep(pattern="test", paths=test_file)
        
        # Assert
        assert isinstance(result, str)
        # Verify it's valid JSON
        json_result = json.loads(result)
        assert isinstance(json_result, list)