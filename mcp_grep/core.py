"""Core functionality for MCP-Grep."""

import re
from pathlib import Path
from typing import Dict, Generator, List, Pattern, Union


class MCPGrep:
    """MCP-Grep main class."""

    def __init__(self, pattern: str, ignore_case: bool = False):
        """Initialize with search pattern.

        Args:
            pattern: Regular expression pattern to search for
            ignore_case: Whether to perform case-insensitive matching
        """
        flags = re.IGNORECASE if ignore_case else 0
        self.pattern = re.compile(pattern, flags)
    
    def search_file(self, file_path: Union[str, Path]) -> Generator[Dict, None, None]:
        """Search for pattern in a file.

        Args:
            file_path: Path to the file to search in

        Yields:
            Dict containing line number, matched line, and match spans
        """
        path = Path(file_path)
        
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                matches = list(self.pattern.finditer(line))
                if matches:
                    yield {
                        'file': str(path),
                        'line_num': line_num,
                        'line': line.rstrip('\n'),
                        'matches': [(m.start(), m.end()) for m in matches]
                    }
    
    def search_files(self, file_paths: List[Union[str, Path]]) -> Generator[Dict, None, None]:
        """Search for pattern in multiple files.

        Args:
            file_paths: List of file paths to search in

        Yields:
            Dict containing file path, line number, matched line, and match spans
        """
        for file_path in file_paths:
            try:
                yield from self.search_file(file_path)
            except FileNotFoundError as e:
                # Just log the error and continue with next file
                print(f"Error: {e}")
