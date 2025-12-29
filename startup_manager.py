"""
startup_manager.py - Windows Startup Auto-Run Manager

Purpose:
    Manages Windows startup integration for Master Refreshing App.
    Enables/disables automatic application launch on Windows boot using
    industry-standard methods: Startup folder shortcuts and Registry entries.
    
    Features:
    - Startup folder shortcut creation/removal
    - Windows Registry integration
    - Dual-method support for reliability
    - Safe error handling
    - No duplicate entries
    - Clean removal

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0
"""

import os
import sys
import winreg
from pathlib import Path
from typing import Optional, Tuple, Callable, Dict, Any
import win32com.client


class StartupManager:
    """
    Windows startup integration manager.
    
    This class provides methods to register/unregister the application
    for automatic startup on Windows boot using both:
    1. Startup folder shortcut (.lnk)
    2. Windows Registry (HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run)
    
    Architecture:
        - Dual-method approach for reliability
        - No duplicate entries
        - Clean error handling
        - Logging support via callback
    """
    
    # Constants
    APP_NAME = "MasterRefreshingApp"
    REGISTRY_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def __init__(self, log_callback: Optional[Callable[[str, str], None]] = None):
        """
        Initialize the startup manager.
        
        Args:
            log_callback: Optional callback function(message, level) for logging
        """
        self.log_callback = log_callback
        
        # Get application executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_path = sys.executable
        else:
            # Running as Python script
            self.app_path = os.path.abspath(sys.argv[0])
        
        # Get startup folder path
        self.startup_folder = self._get_startup_folder()
        self.shortcut_path = os.path.join(self.startup_folder, f"{self.APP_NAME}.lnk")
    
    def _get_startup_folder(self) -> str:
        """
        Get the Windows startup folder path.
        
        Returns:
            str: Path to user's startup folder
        """
        startup_folder = os.path.join(
            os.environ.get('APPDATA', ''),
            'Microsoft',
            'Windows',
            'Start Menu',
            'Programs',
            'Startup'
        )
        
        # Create folder if it doesn't exist
        if not os.path.exists(startup_folder):
            try:
                os.makedirs(startup_folder, exist_ok=True)
            except Exception as e:
                self._log(f"Warning: Could not create startup folder: {e}", "WARNING")
        
        return startup_folder
    
    def enable(self) -> Tuple[bool, str]:
        """
        Enable application auto-run on Windows startup.
        
        Uses both methods:
        1. Creates startup folder shortcut
        2. Adds Windows Registry entry
        
        Returns:
            Tuple[bool, str]: (Success status, message)
        """
        success_count = 0
        messages = []
        
        # Method 1: Startup folder shortcut
        shortcut_success, shortcut_msg = self._create_startup_shortcut()
        if shortcut_success:
            success_count += 1
            messages.append(f"✓ Shortcut: {shortcut_msg}")
            self._log(f"Startup shortcut created: {self.shortcut_path}", "INFO")
        else:
            messages.append(f"✗ Shortcut: {shortcut_msg}")
            self._log(f"Startup shortcut failed: {shortcut_msg}", "WARNING")
        
        # Method 2: Windows Registry
        registry_success, registry_msg = self._add_registry_entry()
        if registry_success:
            success_count += 1
            messages.append(f"✓ Registry: {registry_msg}")
            self._log(f"Startup registry entry added", "INFO")
        else:
            messages.append(f"✗ Registry: {registry_msg}")
            self._log(f"Startup registry failed: {registry_msg}", "WARNING")
        
        # Evaluate overall success
        if success_count == 2:
            return True, "Startup enabled successfully (both methods)"
        elif success_count == 1:
            return True, f"Startup enabled (1/2 methods) - {'; '.join(messages)}"
        else:
            return False, f"Startup enable failed - {'; '.join(messages)}"
    
    def disable(self) -> Tuple[bool, str]:
        """
        Disable application auto-run on Windows startup.
        
        Removes both:
        1. Startup folder shortcut
        2. Windows Registry entry
        
        Returns:
            Tuple[bool, str]: (Success status, message)
        """
        success_count = 0
        messages = []
        
        # Method 1: Remove startup folder shortcut
        shortcut_success, shortcut_msg = self._remove_startup_shortcut()
        if shortcut_success:
            success_count += 1
            messages.append(f"✓ Shortcut: {shortcut_msg}")
            self._log(f"Startup shortcut removed", "INFO")
        else:
            messages.append(f"✗ Shortcut: {shortcut_msg}")
            self._log(f"Startup shortcut removal failed: {shortcut_msg}", "WARNING")
        
        # Method 2: Remove Windows Registry entry
        registry_success, registry_msg = self._remove_registry_entry()
        if registry_success:
            success_count += 1
            messages.append(f"✓ Registry: {registry_msg}")
            self._log(f"Startup registry entry removed", "INFO")
        else:
            messages.append(f"✗ Registry: {registry_msg}")
            self._log(f"Startup registry removal failed: {registry_msg}", "WARNING")
        
        # Evaluate overall success
        if success_count == 2:
            return True, "Startup disabled successfully (both methods)"
        elif success_count == 1:
            return True, f"Startup disabled (1/2 methods) - {'; '.join(messages)}"
        else:
            return False, f"Startup disable failed - {'; '.join(messages)}"
    
    def is_enabled(self) -> bool:
        """
        Check if application is configured to run on startup.
        
        Returns:
            bool: True if either method is active, False otherwise
        """
        shortcut_exists = os.path.exists(self.shortcut_path)
        registry_exists = self._check_registry_entry()
        
        return shortcut_exists or registry_exists
    
    # ═══════════════════════════════════════════════════════════════
    # Method 1: Startup Folder Shortcut
    # ═══════════════════════════════════════════════════════════════
    
    def _create_startup_shortcut(self) -> Tuple[bool, str]:
        """
        Create a shortcut in the Windows startup folder.
        
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        try:
            # Check if shortcut already exists
            if os.path.exists(self.shortcut_path):
                # Verify it points to correct path
                try:
                    shell = win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(self.shortcut_path)
                    if shortcut.TargetPath == self.app_path:
                        return True, "Already exists (valid)"
                except Exception:
                    pass  # Will recreate below
            
            # Create new shortcut
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(self.shortcut_path)
            shortcut.TargetPath = self.app_path
            shortcut.WorkingDirectory = os.path.dirname(self.app_path)
            shortcut.IconLocation = self.app_path
            shortcut.Description = "Master Refreshing App - Auto Refresh Excel Files"
            shortcut.save()
            
            return True, "Created successfully"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _remove_startup_shortcut(self) -> Tuple[bool, str]:
        """
        Remove the startup folder shortcut.
        
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        try:
            if os.path.exists(self.shortcut_path):
                os.remove(self.shortcut_path)
                return True, "Removed successfully"
            else:
                return True, "Not present (already removed)"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    # ═══════════════════════════════════════════════════════════════
    # Method 2: Windows Registry
    # ═══════════════════════════════════════════════════════════════
    
    def _add_registry_entry(self) -> Tuple[bool, str]:
        """
        Add application to Windows Registry Run key.
        
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        try:
            # Open registry key (create if doesn't exist)
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE
            )
            
            # Check if entry already exists with correct path
            try:
                existing_value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                if existing_value == self.app_path:
                    winreg.CloseKey(key)
                    return True, "Already exists (valid)"
            except FileNotFoundError:
                pass  # Entry doesn't exist, will create below
            
            # Set registry value
            winreg.SetValueEx(
                key,
                self.APP_NAME,
                0,
                winreg.REG_SZ,
                self.app_path
            )
            
            winreg.CloseKey(key)
            return True, "Added successfully"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _remove_registry_entry(self) -> Tuple[bool, str]:
        """
        Remove application from Windows Registry Run key.
        
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Try to delete the value
            try:
                winreg.DeleteValue(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True, "Removed successfully"
            except FileNotFoundError:
                winreg.CloseKey(key)
                return True, "Not present (already removed)"
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _check_registry_entry(self) -> bool:
        """
        Check if registry entry exists.
        
        Returns:
            bool: True if entry exists, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_KEY,
                0,
                winreg.KEY_QUERY_VALUE
            )
            
            try:
                winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        
        except Exception:
            return False
    
    # ═══════════════════════════════════════════════════════════════
    # Utility Methods
    # ═══════════════════════════════════════════════════════════════
    
    def get_status_details(self) -> Dict[str, Any]:
        """
        Get detailed status of startup configuration.
        
        Returns:
            Dictionary with status details
        """
        return {
            "enabled": self.is_enabled(),
            "shortcut_exists": os.path.exists(self.shortcut_path),
            "registry_exists": self._check_registry_entry(),
            "app_path": self.app_path,
            "shortcut_path": self.shortcut_path
        }
    
    def _log(self, message: str, level: str = "INFO") -> None:
        """
        Log a message using the callback or stdout.
        
        Args:
            message: Log message
            level: Log level (INFO, WARNING, ERROR, DEBUG)
        """
        if self.log_callback:
            try:
                self.log_callback(message, level)
            except Exception:
                print(f"[{level}] {message}")
        else:
            print(f"[{level}] {message}")
    
    def __repr__(self) -> str:
        """String representation of StartupManager."""
        status = "enabled" if self.is_enabled() else "disabled"
        return f"StartupManager(status={status})"


# Test code
if __name__ == "__main__":
    print("=== StartupManager Test ===\n")
    
    # Create manager
    manager = StartupManager(lambda msg, level: print(f"[{level}] {msg}"))
    
    print(f"Manager: {manager}")
    print(f"\nCurrent status: {manager.is_enabled()}")
    print(f"Details: {manager.get_status_details()}\n")
    
    # Test enable
    print("Testing enable...")
    success, message = manager.enable()
    print(f"Result: {success} - {message}\n")
    
    # Check status
    print(f"Status after enable: {manager.is_enabled()}")
    print(f"Details: {manager.get_status_details()}\n")
    
    # Test disable
    print("Testing disable...")
    success, message = manager.disable()
    print(f"Result: {success} - {message}\n")
    
    # Final status
    print(f"Final status: {manager.is_enabled()}")
    print("\n=== Test Complete ===")
