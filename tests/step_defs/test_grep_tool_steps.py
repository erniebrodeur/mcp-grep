"""Test steps for grep tool functionality."""

import json
import os
import tempfile
import shutil
from pathlib import Path

import pytest
from pytest_bdd import given, when, then, parsers

from mcp.server.fastmcp import FastMCP
from mcp_grep.server import grep


@pytest.fixture
def mcp_server():
    """Create a mock MCP server."""
    return FastMCP("grep-test-server")


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


@given("I'm connected to the MCP grep server")
def connected_to_server(mcp_server):
    """Mock connection to MCP server."""
    return mcp_server


@given(parsers.parse('a file with content "{content}"'))
def file_with_content(test_file, content):
    """Create a test file with the given content."""
    with open(test_file, 'w') as f:
        f.write(content)
    return test_file


@given("a directory with multiple files containing the word \"secret\"")
def directory_with_files(test_dir):
    """Create a directory with multiple files containing 'secret'."""
    # Create main dir files
    with open(os.path.join(test_dir, "file1.txt"), 'w') as f:
        f.write("This file has the secret word\n")
    
    with open(os.path.join(test_dir, "file2.txt"), 'w') as f:
        f.write("This file doesn't have the word\n")
    
    # Create subdirectory
    subdir = os.path.join(test_dir, "subdir")
    os.mkdir(subdir)
    
    with open(os.path.join(subdir, "file3.txt"), 'w') as f:
        f.write("This subdir file has the secret\n")
    
    return test_dir


@when(parsers.parse('I invoke the grep tool with pattern "{pattern}" and the file path'))
async def invoke_grep_with_pattern(pattern, test_file):
    """Invoke grep with pattern and path."""
    result = await grep(pattern=pattern, paths=test_file)
    return json.loads(result)


@when(parsers.parse('I invoke the grep tool with pattern "{pattern}" and ignore_case={ignore_case:Boolean}'))
async def invoke_grep_with_ignore_case(pattern, ignore_case, test_file):
    """Invoke grep with pattern and ignore_case option."""
    result = await grep(pattern=pattern, paths=test_file, ignore_case=ignore_case)
    return json.loads(result)


@when(parsers.parse('I invoke the grep tool with pattern "{pattern}" and before_context={before:d} and after_context={after:d}'))
async def invoke_grep_with_context(pattern, before, after, test_file):
    """Invoke grep with pattern and context options."""
    result = await grep(pattern=pattern, paths=test_file, before_context=before, after_context=after)
    return json.loads(result)


@when(parsers.parse('I invoke the grep tool with pattern "{pattern}" and fixed_strings={fixed:Boolean}'))
async def invoke_grep_with_fixed_strings(pattern, fixed, test_file):
    """Invoke grep with pattern and fixed_strings option."""
    result = await grep(pattern=pattern, paths=test_file, fixed_strings=fixed)
    return json.loads(result)


@when(parsers.parse('I invoke the grep tool with pattern "{pattern}" and recursive={recursive:Boolean}'))
async def invoke_grep_with_recursive(pattern, recursive, test_dir):
    """Invoke grep with pattern and recursive option."""
    result = await grep(pattern=pattern, paths=test_dir, recursive=recursive)
    return json.loads(result)


@when(parsers.parse('I invoke the grep tool with pattern "{pattern}" and max_count={max_count:d}'))
async def invoke_grep_with_max_count(pattern, max_count, test_file):
    """Invoke grep with pattern and max_count option."""
    result = await grep(pattern=pattern, paths=test_file, max_count=max_count)
    return json.loads(result)


@then(parsers.parse('I should receive results with {count:d} matching line'))
@then(parsers.parse('I should receive results with {count:d} matching lines'))
def check_result_count(count, invoke_grep_with_pattern):
    """Check that results contain expected number of matches."""
    assert len(invoke_grep_with_pattern) == count


@then(parsers.parse('the result should include line number {line_num:d}'))
def check_line_number(line_num, invoke_grep_with_pattern):
    """Check that the result includes the expected line number."""
    assert invoke_grep_with_pattern[0]['line_num'] == line_num


@then(parsers.parse('the result should contain "{text}"'))
def check_result_content(text, invoke_grep_with_pattern):
    """Check that the result contains the expected text."""
    assert text in invoke_grep_with_pattern[0]['line']


@then('each match should include context lines')
def check_context_lines(invoke_grep_with_context):
    """Check that each match includes context lines."""
    for match in invoke_grep_with_context:
        assert 'context' in match
        assert len(match['context']) > 0


@then('I should receive results from multiple files')
def check_multiple_files(invoke_grep_with_recursive):
    """Check that results come from multiple files."""
    files = set(result['file'] for result in invoke_grep_with_recursive)
    assert len(files) > 1


@then('I should receive results with no more than {count:d} matching lines')
def check_max_results(count, invoke_grep_with_max_count):
    """Check that results contain no more than the specified number of matches."""
    assert len(invoke_grep_with_max_count) <= count
