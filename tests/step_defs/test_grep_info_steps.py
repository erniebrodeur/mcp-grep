"""Test steps for grep info resource functionality."""

import json

import pytest
from pytest_bdd import given, when, then, parsers

from mcp.server.fastmcp import FastMCP
from mcp_grep.server import grep_info


@pytest.fixture
def mcp_server():
    """Create a mock MCP server."""
    return FastMCP("grep-test-server")


@given("I'm connected to the MCP grep server")
def connected_to_server(mcp_server):
    """Mock connection to MCP server."""
    return mcp_server


@when('I request the "grep://info" resource')
def request_grep_info():
    """Request the grep info resource."""
    result = grep_info()
    return json.loads(result)


@pytest.fixture
def request_grep_info():
    """Fixture for grep info resource."""
    result = grep_info()
    return json.loads(result)


@then('I should receive grep binary metadata as JSON')
def check_json_metadata(request_grep_info):
    """Check that the result is valid JSON metadata."""
    assert isinstance(request_grep_info, dict)


@then('the metadata should include the binary path')
def check_binary_path(request_grep_info):
    """Check that the metadata includes the binary path."""
    assert 'path' in request_grep_info
    # Path might be None if grep isn't installed, but key should exist
    if request_grep_info['path'] is not None:
        assert isinstance(request_grep_info['path'], str)


@then('the metadata should include version information')
def check_version_info(request_grep_info):
    """Check that the metadata includes version information."""
    assert 'version' in request_grep_info
    # Version might be None if grep isn't installed, but key should exist


@then('the metadata should include PCRE support status')
def check_pcre_support(request_grep_info):
    """Check that the metadata includes PCRE support status."""
    assert 'supports_pcre' in request_grep_info
    assert isinstance(request_grep_info['supports_pcre'], bool)


@then('the metadata should include color support status')
def check_color_support(request_grep_info):
    """Check that the metadata includes color support status."""
    assert 'supports_color' in request_grep_info
    assert isinstance(request_grep_info['supports_color'], bool)
