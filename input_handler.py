import os
import ctypes
from typing import List, Optional, Tuple
import magic


class InputHandler:
    def __init__(self, base_path: str, max_depth: Optional[int] = None, include_hidden: bool = False):
        self.base_path = base_path
        self.max_depth = max_depth
        self.include_hidden = include_hidden
        self.mime_detector = magic.Magic(mime=True)

        # Windows hidden file attribute constant
        self.FILE_ATTRIBUTE_HIDDEN = 0x02  # Windows API constant for hidden files

        # Valid file types for PII detection
        self.valid_mime_prefixes = [
            "text/",
            "application/pdf",
            "application/vnd.openxmlformats-officedocument",
            "application/msword",
            "image/jpeg",
            "image/png",
            "image/tiff",
        ]

    def collect_files(self) -> List[Tuple[str, str]]:
        """Traverse the directory and collect (file_path, mime_type) tuples."""
        return self._traverse(self.base_path, current_depth=0)

    def _traverse(self, path: str, current_depth: int) -> List[Tuple[str, str]]:
        if self.max_depth is not None and current_depth > self.max_depth:
            return []

        collected_files = []

        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    # Skip hidden files/folders (Windows + Linux/macOS compatible)
                    if not self.include_hidden and self._is_hidden(entry):
                        continue

                    if entry.is_dir(follow_symlinks=False):
                        collected_files.extend(self._traverse(entry.path, current_depth + 1))

                    elif entry.is_file():
                        mime_type = self._get_mime_type(entry.path)
                        if self._is_valid_pii_type(mime_type):
                            collected_files.append((entry.path, mime_type))

        except PermissionError:
            pass  # Skip directories without access

        return collected_files

    def _is_hidden(self, entry: os.DirEntry) -> bool:
        """Detect if a file is hidden (Works on Windows, Linux, macOS)."""
        # Linux/macOS: Hidden if filename starts with `.`
        if entry.name.startswith("."):
            return True

        # Windows: Check file attributes using ctypes
        try:
            attrs = ctypes.windll.kernel32.GetFileAttributesW(str(entry.path))
            return bool(attrs & self.FILE_ATTRIBUTE_HIDDEN)
        except Exception:
            return False  # Default to not hidden if detection fails

    def _get_mime_type(self, filepath: str) -> str:
        """Detect file type using magic numbers."""
        try:
            return self.mime_detector.from_file(filepath)
        except Exception:
            return "unknown"

    def _is_valid_pii_type(self, mime_type: str) -> bool:
        """Check if file is a valid type for PII extraction."""
        if mime_type == "inode/x-empty":
            return False
        return any(mime_type.startswith(prefix) for prefix in self.valid_mime_prefixes)
