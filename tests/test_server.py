"""Tests for the MCP server implementation."""

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

    @pytest.mark.asyncio
    async def test_basic_match(self, test_file):
        """Test basic pattern matching."""
        # Arrange
        with open(test_file, 'w') as f:
            f.write("Line one has apple\nLine two has banana\nLine three has orange")
        
        # Act
        result = await grep(pattern="apple", paths=test_file)
        results = json.loads(result)
        
        # Assert
        assert len(results) == 1
        assert results[0]['line_num'] == 1
        assert "apple" in results[0]['line']

    @pytest.mark.asyncio
    