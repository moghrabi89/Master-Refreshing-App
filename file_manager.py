"""
file_manager.py - File List Management Module

Purpose:
    Backend file management system for Excel file handling.
    Provides functionality to add, remove, validate, and list Excel files
    with automatic configuration persistence.
    
    Features:
    - Add/remove Excel files with validation
    - Support multiple Excel formats (.xlsx, .xlsm, .xlsb, .xls)
    - Extract file metadata (name, path, extension)
    - Prevent duplicate entries
    - Automatic configuration updates
    - File existence validation
    - Comprehensive error handling

Author: ENG. Saeed Al-moghrabi
"""

import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from config_handler import ConfigHandler


class FileManager:
    """
    Excel file list manager with configuration integration.
    
    This class manages the list of Excel files to be refreshed,
    providing validation, metadata extraction, and automatic
    persistence through the ConfigHandler.
    """
    
    # Supported Excel file extensions
    SUPPORTED_EXTENSIONS = {'.xlsx', '.xlsm', '.xlsb', '.xls'}
    
    def __init__(self, config_handler: ConfigHandler):
        """
        Initialize the file manager.
        
        Args:
            config_handler: ConfigHandler instance for persistence
        """
        self.config = config_handler
        self._files: List[str] = []
        
        # Load initial file list from configuration
        self.refresh_file_list()
    
    def refresh_file_list(self) -> None:
        """
        Reload file list from configuration.
        
        Synchronizes the internal file list with the configuration file.
        This should be called if the config is modified externally.
        """
        self._files = self.config.get_files()
        
        # Log: File list refreshed from configuration
        # logging.debug(f"File list refreshed: {len(self._files)} files loaded")
    
    def list_files(self) -> List[Dict[str, str]]:
        """
        Get list of all registered files with metadata.
        
        Returns:
            List of dictionaries, each containing:
                - name: File name (basename)
                - path: Full absolute path
                - extension: File extension (e.g., '.xlsx')
        
        Example:
            [
                {
                    "name": "report.xlsx",
                    "path": "C:/Documents/report.xlsx",
                    "extension": ".xlsx"
                }
            ]
        """
        files_metadata = []
        
        for file_path in self._files:
            metadata = self.get_metadata(file_path)
            files_metadata.append(metadata)
        
        return files_metadata
    
    def add_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Add an Excel file to the managed list.
        
        Validates the file and adds it to the configuration if valid.
        
        Args:
            file_path: Absolute or relative path to Excel file
        
        Returns:
            Tuple of (success: bool, message: str)
            - success: True if file was added, False otherwise
            - message: Descriptive message explaining the result
        
        Example:
            success, msg = file_manager.add_file("C:/data/report.xlsx")
            if success:
                print(f"Success: {msg}")
        """
        # Convert to absolute path
        abs_path = os.path.abspath(file_path)
        
        # Validate file exists
        if not self.file_exists(abs_path):
            return False, f"File does not exist: {abs_path}"
        
        # Validate extension
        if not self.is_supported_extension(abs_path):
            ext = os.path.splitext(abs_path)[1]
            return False, f"Unsupported file extension: {ext}. Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
        
        # Check for duplicates (case-insensitive on Windows)
        normalized_path = os.path.normpath(abs_path).lower()
        for existing_file in self._files:
            if os.path.normpath(existing_file).lower() == normalized_path:
                return False, f"File already in list: {os.path.basename(abs_path)}"
        
        # Add to configuration
        if self.config.add_file(abs_path):
            # Update internal list
            self._files.append(abs_path)
            
            # Log: File added successfully
            # logging.info(f"Added file: {abs_path}")
            
            # Placeholder: Signal for UI update
            # signal_file_added.emit(self.get_metadata(abs_path))
            
            return True, f"Successfully added: {os.path.basename(abs_path)}"
        else:
            return False, "Failed to add file to configuration"
    
    def add_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Add multiple files at once.
        
        Args:
            file_paths: List of file paths to add
        
        Returns:
            Dictionary containing:
                - added: List of successfully added file paths
                - skipped: List of skipped file paths with reasons
                - total_added: Count of successfully added files
                - total_skipped: Count of skipped files
        """
        result = {
            "added": [],
            "skipped": [],
            "total_added": 0,
            "total_skipped": 0
        }
        
        for file_path in file_paths:
            success, message = self.add_file(file_path)
            
            if success:
                result["added"].append(file_path)
                result["total_added"] += 1
            else:
                result["skipped"].append({
                    "path": file_path,
                    "reason": message
                })
                result["total_skipped"] += 1
        
        # Log: Batch add operation completed
        # logging.info(f"Batch add: {result['total_added']} added, {result['total_skipped']} skipped")
        
        return result
    
    def remove_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Remove a file from the managed list.
        
        Args:
            file_path: Path to file to remove (exact match or basename)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Try to find the file (support both full path and basename matching)
        file_to_remove = None
        normalized_input = os.path.normpath(file_path).lower()
        
        for existing_file in self._files:
            normalized_existing = os.path.normpath(existing_file).lower()
            
            # Match by full path or basename
            if (normalized_existing == normalized_input or 
                os.path.basename(normalized_existing) == os.path.basename(normalized_input)):
                file_to_remove = existing_file
                break
        
        if file_to_remove is None:
            return False, f"File not found in list: {os.path.basename(file_path)}"
        
        # Remove from configuration
        if self.config.remove_file(file_to_remove):
            # Update internal list
            self._files.remove(file_to_remove)
            
            # Log: File removed successfully
            # logging.info(f"Removed file: {file_to_remove}")
            
            # Placeholder: Signal for UI update
            # signal_file_removed.emit(file_to_remove)
            
            return True, f"Successfully removed: {os.path.basename(file_to_remove)}"
        else:
            return False, "Failed to remove file from configuration"
    
    def remove_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Remove multiple files at once.
        
        Args:
            file_paths: List of file paths to remove
        
        Returns:
            Dictionary with removal statistics
        """
        result = {
            "removed": [],
            "not_found": [],
            "total_removed": 0,
            "total_not_found": 0
        }
        
        for file_path in file_paths:
            success, message = self.remove_file(file_path)
            
            if success:
                result["removed"].append(file_path)
                result["total_removed"] += 1
            else:
                result["not_found"].append(file_path)
                result["total_not_found"] += 1
        
        return result
    
    def clear_all(self) -> int:
        """
        Remove all files from the list.
        
        Returns:
            Number of files that were removed
        """
        count = len(self._files)
        
        self.config.clear_files()
        self._files = []
        
        # Log: All files cleared
        # logging.info(f"Cleared all files ({count} removed)")
        
        # Placeholder: Signal for UI update
        # signal_files_cleared.emit()
        
        return count
    
    def get_metadata(self, file_path: str) -> Dict[str, str]:
        """
        Extract metadata for a specific file.
        
        Args:
            file_path: Path to the file
        
        Returns:
            Dictionary containing:
                - name: File name (basename)
                - path: Full absolute path
                - extension: File extension
                - exists: Whether file exists on filesystem (bool as string)
                - size: File size in bytes (if exists)
        """
        abs_path = os.path.abspath(file_path)
        name = os.path.basename(abs_path)
        extension = os.path.splitext(abs_path)[1]
        
        metadata = {
            "name": name,
            "path": abs_path,
            "extension": extension,
            "exists": str(os.path.exists(abs_path))
        }
        
        # Add file size if file exists
        if os.path.exists(abs_path):
            try:
                size_bytes = os.path.getsize(abs_path)
                metadata["size"] = self._format_file_size(size_bytes)
                metadata["size_bytes"] = str(size_bytes)
            except OSError:
                metadata["size"] = "Unknown"
                metadata["size_bytes"] = "0"
        else:
            metadata["size"] = "N/A"
            metadata["size_bytes"] = "0"
        
        return metadata
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: File size in bytes
        
        Returns:
            Formatted string (e.g., "2.5 MB")
        """
        size = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists on the filesystem.
        
        Args:
            file_path: Path to check
        
        Returns:
            True if file exists and is a file, False otherwise
        """
        return os.path.isfile(file_path)
    
    def is_supported_extension(self, file_path: str) -> bool:
        """
        Check if file has a supported Excel extension.
        
        Args:
            file_path: Path to check
        
        Returns:
            True if extension is supported, False otherwise
        """
        extension = os.path.splitext(file_path)[1].lower()
        return extension in self.SUPPORTED_EXTENSIONS
    
    def validate_all_files(self) -> Dict[str, Any]:
        """
        Validate all files in the list.
        
        Checks if all registered files still exist on the filesystem.
        Removes files that no longer exist.
        
        Returns:
            Dictionary containing:
                - valid: List of valid file paths
                - invalid: List of invalid/missing file paths
                - removed_count: Number of files removed
        """
        valid_files = []
        invalid_files = []
        
        for file_path in self._files[:]:  # Copy list to avoid modification during iteration
            if self.file_exists(file_path):
                valid_files.append(file_path)
            else:
                invalid_files.append(file_path)
        
        # Remove invalid files from configuration
        if invalid_files:
            removed = self.config.validate_file_paths()
            self._files = self.config.get_files()
            
            # Log: Invalid files removed
            # logging.warning(f"Removed {len(removed)} invalid files from configuration")
            
            # Placeholder: Signal for UI update
            # signal_invalid_files_removed.emit(removed)
        
        return {
            "valid": valid_files,
            "invalid": invalid_files,
            "removed_count": len(invalid_files)
        }
    
    def get_file_count(self) -> int:
        """
        Get the total number of files in the list.
        
        Returns:
            Count of files
        """
        return len(self._files)
    
    def get_files_by_extension(self, extension: str) -> List[str]:
        """
        Get all files with a specific extension.
        
        Args:
            extension: Extension to filter by (e.g., '.xlsx')
        
        Returns:
            List of file paths with matching extension
        """
        ext_lower = extension.lower()
        if not ext_lower.startswith('.'):
            ext_lower = '.' + ext_lower
        
        return [
            f for f in self._files 
            if os.path.splitext(f)[1].lower() == ext_lower
        ]
    
    def search_files(self, search_term: str) -> List[Dict[str, str]]:
        """
        Search for files by name (case-insensitive).
        
        Args:
            search_term: Search string to match against file names
        
        Returns:
            List of metadata dictionaries for matching files
        """
        search_lower = search_term.lower()
        results = []
        
        for file_path in self._files:
            if search_lower in os.path.basename(file_path).lower():
                results.append(self.get_metadata(file_path))
        
        return results
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported Excel file extensions.
        
        Returns:
            List of extension strings
        """
        return sorted(list(self.SUPPORTED_EXTENSIONS))
    
    def __len__(self) -> int:
        """Return the number of files in the list."""
        return len(self._files)
    
    def __repr__(self) -> str:
        """String representation of FileManager."""
        return f"FileManager(files={len(self._files)}, supported={self.SUPPORTED_EXTENSIONS})"


# Test/Demo code (for standalone testing)
if __name__ == "__main__":
    import json
    
    print("=== FileManager Test ===\n")
    
    # Initialize with config handler
    from config_handler import ConfigHandler
    config = ConfigHandler("test_file_manager_config.json")
    file_manager = FileManager(config)
    
    print(f"FileManager initialized: {file_manager}")
    print(f"Supported extensions: {file_manager.get_supported_extensions()}\n")
    
    # Test adding files (these won't exist, but we can test the logic)
    print("Testing add_file()...")
    
    # Create a test file for demonstration
    test_file = "test_workbook.xlsx"
    with open(test_file, 'w') as f:
        f.write("test")
    
    success, msg = file_manager.add_file(test_file)
    print(f"Add result: {success} - {msg}")
    
    # Try adding duplicate
    success, msg = file_manager.add_file(test_file)
    print(f"Duplicate add: {success} - {msg}\n")
    
    # Test listing files
    print("Current file list:")
    files = file_manager.list_files()
    print(json.dumps(files, indent=2))
    print(f"File count: {file_manager.get_file_count()}\n")
    
    # Test metadata
    if files:
        print("Metadata for first file:")
        metadata = file_manager.get_metadata(files[0]["path"])
        print(json.dumps(metadata, indent=2))
        print()
    
    # Test validation
    print("Validating all files...")
    validation = file_manager.validate_all_files()
    print(f"Valid: {len(validation['valid'])}, Invalid: {len(validation['invalid'])}\n")
    
    # Test removal
    print("Testing remove_file()...")
    if files:
        success, msg = file_manager.remove_file(files[0]["path"])
        print(f"Remove result: {success} - {msg}")
        print(f"File count after removal: {file_manager.get_file_count()}\n")
    
    # Test unsupported extension
    print("Testing unsupported extension...")
    success, msg = file_manager.add_file("test.txt")
    print(f"Result: {success} - {msg}\n")
    
    # Clean up test files
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists("test_file_manager_config.json"):
        os.remove("test_file_manager_config.json")
    
    print("=== Test Complete ===")
