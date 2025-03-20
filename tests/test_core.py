"""Tests for the core functionality of MCP-Grep."""

import os
import tempfile
from pathlib import Path

import pytest

from mcp_grep.core import MCPGrep


@pytest.fixture
def sample_file():
    """Create a temporary file with sample content for testing."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write("Line one has apple\n")
        tmp.write("Line two has banana\n")
        tmp.write("Line three has Apple again\n")
        tmp.write("Line four has no fruit\n")
    
    yield tmp.name
    os.unlink(tmp.name)


def test_search_file(sample_file):
    """Test searching a single file."""
    grep = MCPGrep("apple")
    results = list(grep.search_file(sample_file))
    
    assert len(results) == 1
    assert results[0]['line_num'] == 1
    assert "apple" in results[0]['line']
    
    # Test case-insensitive search
    grep = MCPGrep("apple", ignore_case=True)
    results = list(grep.search_file(sample_file))
    
    assert len(results) == 2
    assert "apple" in results[0]['line'].lower()
    assert "apple" in results[1]['line'].lower()


def test_search_files(sample_file):
    """Test searching multiple files."""
    grep = MCPGrep("banana")
    results = list(grep.search_files([sample_file]))
    
    assert len(results) == 1
    assert results[0]['line_num'] == 2
    assert "banana" in results[0]['line']


def test_file_not_found():
    """Test behavior when file is not found."""
    grep = MCPGrep("pattern")
    
    # This should not raise an exception at this level
    results = list(grep.search_files(["nonexistent_file.txt"]))
    assert len(results) == 0
    
    # This should raise FileNotFoundError
    with pytest.raises(FileNotFoundError):
        list(grep.search_file("nonexistent_file.txt"))
