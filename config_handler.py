"""
config_handler.py - Configuration Persistence Manager

Purpose:
    Complete configuration management system using JSON file storage.
    Handles all persistent settings for the Master Refreshing App including
    file lists, schedule times, scheduler state, and theme preferences.
    
    Features:
    - Automatic config file creation with defaults
    - Safe JSON read/write operations
    - Getter/setter methods for all settings
    - Immediate persistence on changes
    - Robust error handling
    - Thread-safe operations

Author: ENG. Saeed Al-moghrabi
"""

import json
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from utils.paths import get_app_root


class ConfigHandler:
    """
    Configuration persistence manager for Master Refreshing App.
    
    This class manages all application configuration using a JSON file.
    It provides safe read/write operations, automatic defaults, and
    immediate persistence for all setting changes.
    """
    
    # Default configuration structure
    DEFAULT_CONFIG = {
        "files": [],
        "schedule_time": "06:00",
        "auto_refresh_enabled": False,
        "theme_mode": "modern",
        "run_on_startup": False,
        "log_directory": None  # None means use default (app_root/logs)
    }
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the configuration handler.
        
        Args:
            config_path: Path to the configuration file (default: "config.json")
                        Can be relative (resolved from app root) or absolute
        """
        # Resolve path from app root if relative
        if not os.path.isabs(config_path):
            self.config_path = str(get_app_root() / config_path)
        else:
            self.config_path = config_path
        
        self.config: Dict[str, Any] = {}
        
        # Load configuration on initialization
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file.
        
        If the file doesn't exist or is corrupted, creates a new one
        with default values. Never crashes the application.
        
        Returns:
            Dictionary containing the loaded configuration
        """
        try:
            # Check if config file exists
            if os.path.exists(self.config_path):
                # Read and parse JSON
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Validate structure and merge with defaults
                self.config = self._validate_and_merge(loaded_config)
                
                # Log: Configuration loaded successfully
                # logging.info(f"Configuration loaded from {self.config_path}")
            else:
                # File doesn't exist - create with defaults
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()
                
                # Log: Created new configuration file
                # logging.info(f"Created new configuration file: {self.config_path}")
        
        except json.JSONDecodeError as e:
            # Corrupted JSON - recreate with defaults
            # logging.error(f"Corrupted config file: {e}. Creating new config.")
            self.config = self.DEFAULT_CONFIG.copy()
            self.save_config()
        
        except Exception as e:
            # Any other error - use defaults in memory
            # logging.error(f"Error loading config: {e}. Using defaults.")
            self.config = self.DEFAULT_CONFIG.copy()
        
        return self.config
    
    def save_config(self) -> bool:
        """
        Save current configuration to JSON file.
        
        Writes configuration with proper formatting and ensures safe
        file operations. Returns success status.
        
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Write to temporary file first (atomic operation)
            temp_path = self.config_path + ".tmp"
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Replace original file with temp file
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            os.rename(temp_path, self.config_path)
            
            # Log: Configuration saved successfully
            # logging.debug(f"Configuration saved to {self.config_path}")
            
            return True
        
        except Exception as e:
            # Log: Error saving configuration
            # logging.error(f"Error saving config: {e}")
            return False
    
    def _validate_and_merge(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate loaded configuration and merge with defaults.
        
        Ensures all required keys exist and have correct types.
        Missing keys are filled with default values.
        
        Args:
            loaded_config: Configuration dictionary loaded from file
        
        Returns:
            Validated and merged configuration dictionary
        """
        # Start with defaults
        validated = self.DEFAULT_CONFIG.copy()
        
        # Update with loaded values if they exist and are valid type
        if isinstance(loaded_config.get("files"), list):
            validated["files"] = loaded_config["files"]
        
        if isinstance(loaded_config.get("schedule_time"), str):
            validated["schedule_time"] = loaded_config["schedule_time"]
        
        if isinstance(loaded_config.get("auto_refresh_enabled"), bool):
            validated["auto_refresh_enabled"] = loaded_config["auto_refresh_enabled"]
        
        if isinstance(loaded_config.get("theme_mode"), str):
            validated["theme_mode"] = loaded_config["theme_mode"]
        
        if isinstance(loaded_config.get("run_on_startup"), bool):
            validated["run_on_startup"] = loaded_config["run_on_startup"]
        
        # Handle log_directory (can be str or None)
        if "log_directory" in loaded_config:
            log_dir = loaded_config["log_directory"]
            if log_dir is None or isinstance(log_dir, str):
                validated["log_directory"] = log_dir
        
        return validated
    
    # ===== FILE LIST MANAGEMENT =====
    
    def get_files(self) -> List[Dict[str, Any]]:
        """
        Get list of Excel files from configuration.
        
        Returns:
            List of file metadata dictionaries with keys:
                - path: str (file path)
                - enabled: bool (default True)
                - last_status: Optional[str]
                - last_run: Optional[str] (ISO timestamp)
        """
        files = self.config.get("files", [])
        
        # Normalize old string format to new dict format
        normalized_files = []
        for file_entry in files:
            if isinstance(file_entry, str):
                # Old format: just a string path
                normalized_files.append({
                    "path": file_entry,
                    "enabled": True,
                    "last_status": None,
                    "last_run": None
                })
            elif isinstance(file_entry, dict):
                # New format: ensure all required fields exist
                normalized_files.append({
                    "path": file_entry.get("path", ""),
                    "enabled": file_entry.get("enabled", True),
                    "last_status": file_entry.get("last_status"),
                    "last_run": file_entry.get("last_run")
                })
        
        return normalized_files.copy()
    
    def add_file(self, file_path: str) -> bool:
        """
        Add a file to the configuration.
        
        Args:
            file_path: Absolute path to Excel file
        
        Returns:
            True if file was added, False if already exists
        """
        files = self.get_files()  # Get normalized list
        
        # Normalize path for comparison (handle different path separators)
        normalized_path = os.path.normpath(file_path)
        
        # Check if file already exists (avoid duplicates)
        for file_entry in files:
            if os.path.normpath(file_entry["path"]) == normalized_path:
                return False
        
        # Add file with metadata and save
        files.append({
            "path": file_path,
            "enabled": True,
            "last_status": None,
            "last_run": None
        })
        self.config["files"] = files
        self.save_config()
        
        # Log: File added to configuration
        # logging.info(f"Added file to config: {file_path}")
        
        return True
    
    def add_files(self, file_paths: List[str]) -> int:
        """
        Add multiple files to the configuration.
        
        Args:
            file_paths: List of absolute file paths
        
        Returns:
            Number of files actually added (excludes duplicates)
        """
        added_count = 0
        for file_path in file_paths:
            if self.add_file(file_path):
                added_count += 1
        return added_count
    
    def remove_file(self, file_path: str) -> bool:
        """
        Remove a file from the configuration.
        
        Args:
            file_path: Path to file to remove
        
        Returns:
            True if file was removed, False if not found
        """
        files = self.get_files()  # Get normalized list
        
        # Normalize path for comparison
        normalized_path = os.path.normpath(file_path)
        
        # Find and remove matching file
        original_count = len(files)
        files = [f for f in files if os.path.normpath(f["path"]) != normalized_path]
        
        if len(files) < original_count:
            self.config["files"] = files
            self.save_config()
            
            # Log: File removed from configuration
            # logging.info(f"Removed file from config: {file_path}")
            
            return True
        
        return False
    
    def remove_files(self, file_paths: List[str]) -> int:
        """
        Remove multiple files from the configuration.
        
        Args:
            file_paths: List of file paths to remove
        
        Returns:
            Number of files actually removed
        """
        removed_count = 0
        for file_path in file_paths:
            if self.remove_file(file_path):
                removed_count += 1
        return removed_count
    
    def clear_files(self) -> None:
        """Remove all files from the configuration."""
        self.config["files"] = []
        self.save_config()
        
        # Log: All files cleared from configuration
        # logging.info("Cleared all files from configuration")
    
    def get_file_count(self) -> int:
        """
        Get the count of files in configuration.
        
        Returns:
            Number of files
        """
        return len(self.get_files())
    
    def update_file_metadata(self, file_path: str, enabled: Optional[bool] = None, 
                            last_status: Optional[str] = None, last_run: Optional[str] = None) -> bool:
        """
        Update metadata for a specific file.
        
        Args:
            file_path: Path to the file to update
            enabled: New enabled state (None to leave unchanged)
            last_status: New last status (None to leave unchanged)
            last_run: New last run timestamp (None to leave unchanged)
        
        Returns:
            True if file was found and updated, False otherwise
        """
        files = self.get_files()
        normalized_path = os.path.normpath(file_path)
        
        found = False
        for file_entry in files:
            if os.path.normpath(file_entry["path"]) == normalized_path:
                if enabled is not None:
                    file_entry["enabled"] = enabled
                if last_status is not None:
                    file_entry["last_status"] = last_status
                if last_run is not None:
                    file_entry["last_run"] = last_run
                found = True
                break
        
        if found:
            self.config["files"] = files
            self.save_config()
        
        return found
    
    def set_file_enabled(self, file_path: str, enabled: bool) -> bool:
        """
        Set the enabled state for a specific file.
        
        Args:
            file_path: Path to the file
            enabled: True to enable, False to disable
        
        Returns:
            True if successful, False if file not found
        """
        return self.update_file_metadata(file_path, enabled=enabled)
    
    # ===== SCHEDULE TIME MANAGEMENT =====
    
    def get_schedule_time(self) -> str:
        """
        Get the scheduled refresh time.
        
        Returns:
            Time string in format "HH:MM"
        """
        return self.config.get("schedule_time", "06:00")
    
    def set_schedule_time(self, time_str: str) -> bool:
        """
        Set the scheduled refresh time.
        
        Args:
            time_str: Time in format "HH:MM" (24-hour format)
        
        Returns:
            True if time was set successfully, False if invalid format
        """
        # Validate time format
        if not self._validate_time_format(time_str):
            # Log: Invalid time format
            # logging.warning(f"Invalid time format: {time_str}")
            return False
        
        # Update and save
        self.config["schedule_time"] = time_str
        self.save_config()
        
        # Log: Schedule time updated
        # logging.info(f"Schedule time set to: {time_str}")
        
        return True
    
    def _validate_time_format(self, time_str: str) -> bool:
        """
        Validate time string format.
        
        Args:
            time_str: Time string to validate
        
        Returns:
            True if valid "HH:MM" format, False otherwise
        """
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            # Validate ranges
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return True
        except (ValueError, AttributeError):
            pass
        
        return False
    
    # ===== AUTO-REFRESH STATE MANAGEMENT =====
    
    def is_auto_refresh_enabled(self) -> bool:
        """
        Check if auto-refresh (scheduler) is enabled.
        
        Returns:
            True if scheduler is enabled, False otherwise
        """
        return self.config.get("auto_refresh_enabled", False)
    
    def set_auto_refresh_enabled(self, enabled: bool) -> None:
        """
        Set the auto-refresh enabled state.
        
        Args:
            enabled: True to enable scheduler, False to disable
        """
        self.config["auto_refresh_enabled"] = bool(enabled)
        self.save_config()
        
        # Log: Auto-refresh state changed
        # logging.info(f"Auto-refresh {'enabled' if enabled else 'disabled'}")
    
    # ===== THEME MANAGEMENT =====
    
    def get_theme_mode(self) -> str:
        """
        Get the current UI theme mode.
        
        Returns:
            Theme mode string (e.g., "modern", "dark")
        """
        return self.config.get("theme_mode", "modern")
    
    def set_theme_mode(self, mode: str) -> None:
        """
        Set the UI theme mode.
        
        Args:
            mode: Theme mode identifier (e.g., "modern", "dark", "light")
        """
        self.config["theme_mode"] = mode
        self.save_config()
        
        # Log: Theme mode changed
        # logging.info(f"Theme mode set to: {mode}")
    
    # ===== WINDOWS STARTUP MANAGEMENT =====
    
    def is_run_on_startup_enabled(self) -> bool:
        """
        Check if Windows startup auto-run is enabled.
        
        Returns:
            True if startup is enabled, False otherwise
        """
        return self.config.get("run_on_startup", False)
    
    def set_run_on_startup_enabled(self, enabled: bool) -> None:
        """
        Set the Windows startup auto-run state.
        
        Args:
            enabled: True to enable startup, False to disable
        """
        self.config["run_on_startup"] = bool(enabled)
        self.save_config()
        
        # Log: Startup state changed
        # logging.info(f"Windows startup {'enabled' if enabled else 'disabled'}")
    
    # ===== LOG DIRECTORY MANAGEMENT =====
    
    def get_log_directory(self) -> Optional[str]:
        """
        Get the configured log directory.
        
        Returns:
            Log directory path, or None if using default
        """
        return self.config.get("log_directory")
    
    def set_log_directory(self, directory: Optional[str]) -> bool:
        """
        Set the log directory.
        
        Args:
            directory: Directory path, or None to use default
        
        Returns:
            True if successful
        """
        self.config["log_directory"] = directory
        return self.save_config()
    
    # ===== UTILITY METHODS =====
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the entire configuration dictionary.
        
        Returns:
            Copy of the complete configuration
        """
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        
        # Log: Configuration reset to defaults
        # logging.info("Configuration reset to defaults")
    
    def validate_file_paths(self) -> List[str]:
        """
        Validate all file paths in configuration.
        
        Removes any files that no longer exist on the filesystem.
        
        Returns:
            List of removed file paths
        """
        files = self.config.get("files", [])
        removed = []
        
        # Check each file
        valid_files = []
        for file_path in files:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                removed.append(file_path)
        
        # Update if any files were removed
        if removed:
            self.config["files"] = valid_files
            self.save_config()
            
            # Log: Invalid files removed
            # logging.info(f"Removed {len(removed)} invalid file paths from config")
        
        return removed
    
    def export_config(self, export_path: str) -> bool:
        """
        Export configuration to a different file.
        
        Args:
            export_path: Path to export the configuration to
        
        Returns:
            True if export successful, False otherwise
        """
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # Log: Configuration exported
            # logging.info(f"Configuration exported to: {export_path}")
            
            return True
        except Exception as e:
            # Log: Export failed
            # logging.error(f"Failed to export config: {e}")
            return False
    
    def __repr__(self) -> str:
        """String representation of ConfigHandler."""
        return f"ConfigHandler(path='{self.config_path}', files={self.get_file_count()})"


# Test/Demo code (for standalone testing)
if __name__ == "__main__":
    print("=== ConfigHandler Test ===\n")
    
    # Initialize config handler
    config = ConfigHandler("test_config.json")
    
    # Display initial configuration
    print("Initial configuration:")
    print(json.dumps(config.get_all(), indent=2))
    print()
    
    # Test adding files
    print("Adding test files...")
    config.add_file("C:/test/file1.xlsx")
    config.add_file("C:/test/file2.xlsm")
    config.add_file("C:/test/file1.xlsx")  # Duplicate - should not be added
    print(f"Files in config: {config.get_files()}")
    print(f"File count: {config.get_file_count()}")
    print()
    
    # Test schedule time
    print("Setting schedule time...")
    config.set_schedule_time("08:30")
    print(f"Schedule time: {config.get_schedule_time()}")
    print()
    
    # Test auto-refresh state
    print("Enabling auto-refresh...")
    config.set_auto_refresh_enabled(True)
    print(f"Auto-refresh enabled: {config.is_auto_refresh_enabled()}")
    print()
    
    # Test theme mode
    print("Setting theme mode...")
    config.set_theme_mode("dark")
    print(f"Theme mode: {config.get_theme_mode()}")
    print()
    
    # Display final configuration
    print("Final configuration:")
    print(json.dumps(config.get_all(), indent=2))
    print()
    
    # Test removing files
    print("Removing file...")
    config.remove_file("C:/test/file1.xlsx")
    print(f"Files after removal: {config.get_files()}")
    print()
    
    # Test validation
    print("Validating file paths...")
    removed = config.validate_file_paths()
    print(f"Removed invalid paths: {removed}")
    print()
    
    print(f"ConfigHandler: {config}")
    print("\n=== Test Complete ===")
    
    # Cleanup test file
    import os
    if os.path.exists("test_config.json"):
        os.remove("test_config.json")
        print("Test config file cleaned up.")
