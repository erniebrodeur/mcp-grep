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
    # Convert single path to list
    if isinstance(paths, str):
        paths = [paths]
    
    # Find grep binary
    grep_path = shutil.which("grep")
    if not grep_path:
        return json.dumps({"error": "grep binary not found in PATH"})
    
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
    
    results = []
    
    try:
        # Execute grep
        process = subprocess.run(cmd, text=True, capture_output=True)
        
        # Parse output
        if process.returncode not in [0, 1]:  # 0=match found, 1=no match
            return json.dumps({
                "error": f"grep failed with code {process.returncode}",
                "stderr": process.stderr
            })
        
        # Process stdout if we have results
        if process.stdout:
            output_lines = process.stdout.splitlines()
            
            # Track context lines
            current_file = None
            matches = []
            context_lines = []
            separator_indices = []
            
            # Find separator lines (--) for context
            for i, line in enumerate(output_lines):
                if line == "--":
                    separator_indices.append(i)
            
            # Process each line
            for i, line in enumerate(output_lines):
                # Skip separators
                if i in separator_indices:
                    continue
                
                if ":" in line:  # Normal grep output format is "file:line:content"
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        file_path, line_num_str, content = parts
                        
                        # Check if this is a context line (usually prefixed)
                        is_match = True
                        if content.startswith("-"):
                            is_match = False
                            content = content[1:]
                        
                        # Add to results
                        if is_match:
                            matches.append({
                                "file": file_path,
                                "line_num": int(line_num_str),
                                "line": content,
                                "is_match": True
                            })
                        else:
                            context_lines.append({
                                "file": file_path,
                                "line_num": int(line_num_str),
                                "line": content,
                                "is_match": False
                            })
            
            # Group results by file
            file_results = {}
            for item in matches + context_lines:
                file_path = item["file"]
                if file_path not in file_results:
                    file_results[file_path] = []
                file_results[file_path].append(item)
            
            # Sort and format results
            for file_path, lines in file_results.items():
                # Sort by line number
                lines.sort(key=lambda x: x["line_num"])
                
                # Group by match with its context
                result_with_context = []
                current_match = None
                
                for line in lines:
                    if line["is_match"]:
                        if current_match:
                            result_with_context.append(current_match)
                        current_match = {
                            "file": file_path,
                            "line_num": line["line_num"],
                            "line": line["line"],
                            "context": []
                        }
                    elif current_match:
                        current_match["context"].append({
                            "line_num": line["line_num"],
                            "line": line["line"],
                            "is_match": False
                        })
                
                if current_match:
                    result_with_context.append(current_match)
                
                results.extend(result_with_context)
    
    except Exception as e:
        return json.dumps({"error": str(e)})
    
    return json.dumps(results, indent=2)

if __name__ == "__main__":
    # Run the server with stdio transport for MCP
    mcp.run()
