"""Command-line interface for MCP-Grep."""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.markup import escape
from rich.text import Text

from mcp_grep.core import MCPGrep


@click.command()
@click.argument('pattern')
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('-i', '--ignore-case', is_flag=True, help='Ignore case distinctions')
@click.option('-n', '--line-number', is_flag=True, help='Show line numbers', default=True)
@click.option('--color/--no-color', default=True, help='Highlight matches in color')
def main(
    pattern: str,
    files: List[str],
    ignore_case: bool,
    line_number: bool,
    color: bool,
) -> None:
    """Search for PATTERN in each FILE.

    Examples:
        mcp-grep "import" *.py
        mcp-grep -i "error" log.txt
    """
    console = Console(highlight=False, color_system="auto" if color else None)
    
    grep = MCPGrep(pattern, ignore_case=ignore_case)
    
    try:
        for result in grep.search_files(files):
            file_path = result['file']
            line_num = result['line_num']
            line = result['line']
            matches = result['matches']
            
            if color:
                text = Text()
                if line_number:
                    text.append(f"{file_path}:{line_num}:", style="cyan")
                    text.append(" ")
                
                # Add line with highlighted matches
                last_end = 0
                for start, end in matches:
                    text.append(line[last_end:start])
                    text.append(line[start:end], style="bold red")
                    last_end = end
                text.append(line[last_end:])
                
                console.print(text)
            else:
                if line_number:
                    console.print(f"{file_path}:{line_num}: {line}")
                else:
                    console.print(line)
                    
    except KeyboardInterrupt:
        console.print("[yellow]Search interrupted.[/yellow]")
        sys.exit(130)
    
    
if __name__ == "__main__":
    main()
