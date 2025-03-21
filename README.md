# MCP-Grep

A grep server implementation that exposes grep functionality through the Model Context Protocol (MCP).

## Installation

```bash
pip install mcp-grep
```

## Usage

MCP-Grep runs as a server that can be used by MCP-compatible clients:

```bash
# Start the MCP-Grep server
mcp-grep-server
```

The server exposes the following MCP functionality:

- **Resource:** `grep://info` - Returns information about the system grep binary
- **Tool:** `grep` - Searches for patterns in files using the system grep binary

## Features

- Information about the system grep binary (path, version, supported features)
- Search for patterns in files using regular expressions
- Support for common grep options:
  - Case-insensitive matching
  - Context lines (before and after matches)
  - Maximum match count
  - Fixed string matching (non-regex)
  - Recursive directory searching

## Example API Usage

Using the MCP Python client:

```python
from mcp.client import MCPClient

# Connect to the MCP-Grep server
client = MCPClient()

# Get information about the grep binary
grep_info = client.get_resource("grep://info")
print(grep_info)

# Search for a pattern in files
result = client.use_tool("grep", {
    "pattern": "search_pattern",
    "paths": ["file.txt", "directory/"],
    "ignore_case": True,
    "recursive": True
})
print(result)
```

## Development

```bash
# Clone the repository
git clone https://github.com/erniebrodeur/mcp-grep.git
cd mcp-grep

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT
