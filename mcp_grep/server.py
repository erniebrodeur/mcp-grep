"""MCP Server implementation for grep functionality using system grep binary."""

from pathlib import Path
import json
import subprocess
import shutil
import os
from typing import Dict, List, Optional, Union

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("grep-server")

def get_grep_info() -> Dict[str, Optional[str]]:
    """Get information about the system grep binary."""
    info = {
        "path": None,
        "version": None,
        "supports_pcre": False,
        "supports_color": False
    }
    
    # Find grep path
    grep_path = shutil.which("grep")
    if grep_path:
        info["path"] = grep_path
        
        # Get version
        try:
            version_output = subprocess.check_output([grep_path, "--version"], text=True)
            info["version"] = version_output.split("\n")[0].strip()
            
            # Check for PCRE support
            try:
                subprocess.check_output([grep_path, "--perl-regexp", "test", "-"], 
                                      input="test", text=True, stderr=subprocess.DEVNULL)
                info["supports_pcre"] = True
            except subprocess.CalledProcessError:
                pass
                
            # Check for color support
            try:
                subprocess.check_output([grep_path, "--color=auto", "test", "-"], 
                                      input="test", text=True)
                info["supports_color"] = True
            except subprocess.CalledProcessError:
                pass
        except subprocess.CalledProcessError:
            pass
    
    return info

# Register grep info as a resource
@mcp.resource("grep://info")
def grep_info() -> str:
    """Resource providing information about the grep binary."""
    return json.dumps(get_grep_info(), indent=2)

@mcp.tool()
def grep(
    pattern: str,
    paths: Union[str, List[str]],
    ignore_case: bool = False,
    before_context: int = 0,
    after_context: int = 0,
    max_count: int = 0,
    fixed_strings: bool = False,
    recursive: bool = False
) -> str:
    """Search for pattern in files using system grep.
    
    Args:
        pattern: Pattern to search for
        paths: File or directory paths to search in (string or list of strings)
        ignore_case: Case-insensitive matching (-i)
        before_context: Number of lines before match (-B)
        after_context: Number of lines after match (-A)
        max_count: Stop after N matches (-m)
        fixed_strings: Treat pattern as literal text, not regex (-F)
        recursive: Search directories recursively (-r)
        
    Returns:
        JSON string with search results
    """
    # Convert single path to list and expand user paths
    if isinstance(paths, str):
        paths = [os.path.expanduser(paths)]
    else:
        paths = [os.path.expanduser(p) for p in paths]
        
    # Let grep handle directories according to the recursive flag
    
    # Find grep binary
    grep_path = shutil.which("grep")
    if not grep_path:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "grep binary not found in PATH"
                }
            ],
            "isError": True
        }
    
    # Build command
    cmd = [grep_path]
    
    # Add options
    if ignore_case:
        cmd.append("-i")
    if before_context > 0:
        cmd.extend(["-B", str(before_context)])
    if after_context > 0:
        cmd.extend(["-A", str(after_context)])
    if max_count > 0:
        cmd.extend(["-m", str(max_count)])
    if fixed_strings:
        cmd.append("-F")
    if recursive:
        cmd.append("-r")
    
    # Common options we always want
    cmd.extend(["--line-number", "--color=never"])
    
    # Add pattern and paths
    cmd.append(pattern)
    cmd.extend(paths)
    
    try:
        # Execute grep
        process = subprocess.run(cmd, text=True, capture_output=True)
        
        # Parse output
        if process.returncode not in [0, 1]:  # 0=match found, 1=no match
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"grep failed with code {process.returncode}\n{process.stderr}"
                    }
                ],
                "isError": True
            }
        
        # Parse results into clean JSON
        results = []
        if process.stdout:
            for line in process.stdout.splitlines():
                # Handle normal grep output (not context lines or separators)
                if line != "--" and ":" in line:  # Skip separators and ensure we have a match
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        file_path, line_num, content = parts
                        results.append({
                            "file": file_path,
                            "line_num": int(line_num),
                            "line": content
                        })
        
        # No results case
        if not results and process.returncode == 1:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "No matches found"
                    }
                ],
                "isError": False
            }
    
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing grep: {str(e)}"
                }
            ],
            "isError": True
        }
    
    results_json = json.dumps(results, indent=2)
    return {
        "content": [
            {
                "type": "text",
                "text": results_json
            }
        ],
        "isError": False
    }

if __name__ == "__main__":
    # Run the server with stdio transport for MCP
    mcp.run()