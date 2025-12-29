"""
paths.py - Application Path Management

Purpose:
    Centralized path resolution for the Master Refreshing App.
    Provides a single source of truth for locating the application root directory,
    ensuring consistent path resolution in both development and packaged/frozen builds.
    
    This module eliminates the need for Path.cwd() or ad-hoc relative paths
    throughout the codebase, making the application more robust and portable.

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0
"""

from pathlib import Path
import sys


def get_app_root() -> Path:
    """
    Return the root directory of the application.
    
    This function provides consistent path resolution in two environments:
    
    1. Frozen/Packaged Build (PyInstaller, Nuitka, etc.):
       Returns the directory containing the executable.
       Example: C:\\Program Files\\MasterRefreshingApp\\
    
    2. Development Mode (running from source):
       Returns the project root directory (where main.py, config.json, etc. live).
       Example: F:\\Master Refreshing App\\
    
    Returns:
        Path: Absolute path to the application root directory
    
    Usage:
        from utils.paths import get_app_root
        
        config_path = get_app_root() / "config.json"
        manifest_path = get_app_root() / "integrity_manifest.json"
        logs_dir = get_app_root() / "logs"
    
    Technical Details:
        - Uses sys.frozen to detect packaged executables
        - Uses sys.executable for frozen builds
        - Uses __file__ resolution for development mode
        - Returns resolved absolute paths (no symlinks)
    """
    if getattr(sys, "frozen", False):
        # Running as a bundled executable (PyInstaller/Nuitka)
        # sys.executable points to the .exe file
        # We return its parent directory
        app_root = Path(sys.executable).resolve().parent
    else:
        # Running from source code
        # __file__ is utils/paths.py
        # We go up two levels: utils/ -> project_root/
        app_root = Path(__file__).resolve().parent.parent
    
    return app_root


# Convenience function for common paths
def get_config_path() -> Path:
    """Get the path to config.json."""
    return get_app_root() / "config.json"


def get_manifest_path() -> Path:
    """Get the path to integrity_manifest.json."""
    return get_app_root() / "integrity_manifest.json"


def get_logs_dir() -> Path:
    """Get the logs directory path."""
    return get_app_root() / "logs"


def get_resources_dir() -> Path:
    """Get the resources directory path."""
    return get_app_root() / "resources"


# For debugging purposes
if __name__ == "__main__":
    print("=" * 60)
    print("Application Path Resolution Test")
    print("=" * 60)
    print(f"\nFrozen build: {getattr(sys, 'frozen', False)}")
    print(f"App root: {get_app_root()}")
    print(f"Config: {get_config_path()}")
    print(f"Manifest: {get_manifest_path()}")
    print(f"Logs dir: {get_logs_dir()}")
    print(f"Resources: {get_resources_dir()}")
    print("\n" + "=" * 60)
