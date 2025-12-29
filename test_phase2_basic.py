"""
test_phase2_basic.py - Phase 2 Basic Verification

Tests:
1. Config handler with new metadata fields
2. File manager dict-based operations
3. Backward compatibility with old config format
4. Enable/disable functionality
5. Status update functionality
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from config_handler import ConfigHandler
from file_manager import FileManager


def test_config_metadata_fields():
    """Test ConfigHandler handles metadata fields correctly."""
    print("Test 1: ConfigHandler metadata fields...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
        # Create config with new format
        config_data = {
            "files": [
                {
                    "path": "C:\\test1.xlsx",
                    "enabled": True,
                    "last_status": "Success",
                    "last_run": "2024-12-04T10:00:00"
                },
                {
                    "path": "C:\\test2.xlsx",
                    "enabled": False,
                    "last_status": None,
                    "last_run": None
                }
            ],
            "log_directory": "C:\\CustomLogs",
            "schedule_time": "09:00",
            "auto_refresh_enabled": True,
            "theme_mode": "dark",
            "run_on_startup": False
        }
        json.dump(config_data, f)
    
    try:
        config = ConfigHandler(config_path)
        files = config.get_files()
        
        # Verify structure
        assert len(files) == 2, f"Expected 2 files, got {len(files)}"
        assert files[0]["enabled"] == True, "File 1 should be enabled"
        assert files[1]["enabled"] == False, "File 2 should be disabled"
        assert files[0]["last_status"] == "Success", "File 1 should have Success status"
        assert files[1]["last_status"] is None, "File 2 should have None status"
        
        # Verify log_directory
        log_dir = config.get_log_directory()
        assert log_dir == "C:\\CustomLogs", f"Expected C:\\CustomLogs, got {log_dir}"
        
        print("✅ PASS: ConfigHandler metadata fields work correctly")
        return True
    finally:
        os.unlink(config_path)


def test_backward_compatibility():
    """Test backward compatibility with old string-based format."""
    print("\nTest 2: Backward compatibility...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
        # Create config with OLD format (string paths)
        config_data = {
            "files": [
                "C:\\oldformat1.xlsx",
                "C:\\oldformat2.xlsx"
            ],
            "schedule_time": "09:00",
            "auto_refresh_enabled": True,
            "theme_mode": "dark",
            "run_on_startup": False
        }
        json.dump(config_data, f)
    
    try:
        config = ConfigHandler(config_path)
        files = config.get_files()
        
        # Verify conversion to new format
        assert len(files) == 2, f"Expected 2 files, got {len(files)}"
        assert isinstance(files[0], dict), "Should be converted to dict"
        assert files[0]["path"] == "C:\\oldformat1.xlsx", "Path should be preserved"
        assert files[0]["enabled"] == True, "Should default to enabled"
        assert files[0]["last_status"] is None, "Should default to None status"
        assert files[0]["last_run"] is None, "Should default to None timestamp"
        
        print("✅ PASS: Backward compatibility works correctly")
        return True
    finally:
        os.unlink(config_path)


def test_file_manager_dict_operations():
    """Test FileManager with dict-based structure."""
    print("\nTest 3: FileManager dict operations...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
        config_data = {
            "files": [],
            "schedule_time": "09:00",
            "auto_refresh_enabled": True,
            "theme_mode": "dark",
            "run_on_startup": False
        }
        json.dump(config_data, f)
    
    try:
        config = ConfigHandler(config_path)
        file_mgr = FileManager(config)
        
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as test_file:
            test_path = test_file.name
        
        try:
            # Add file
            success, msg = file_mgr.add_file(test_path)
            assert success, f"Failed to add file: {msg}"
            
            # List files - should include metadata
            files = file_mgr.list_files()
            assert len(files) == 1, f"Expected 1 file, got {len(files)}"
            
            file_data = files[0]
            assert "enabled" in file_data, "Missing enabled field"
            assert "last_status" in file_data, "Missing last_status field"
            assert "last_run" in file_data, "Missing last_run field"
            assert file_data["enabled"] == True, "New file should be enabled by default"
            
            # Get enabled files
            enabled = file_mgr.get_enabled_files()
            assert len(enabled) == 1, f"Expected 1 enabled file, got {len(enabled)}"
            
            # Disable file
            success = file_mgr.set_file_enabled(test_path, False)
            assert success, "Failed to disable file"
            
            # Check enabled files again
            enabled = file_mgr.get_enabled_files()
            assert len(enabled) == 0, f"Expected 0 enabled files after disabling, got {len(enabled)}"
            
            # Update status
            timestamp = datetime.now().isoformat()
            success = file_mgr.update_file_status(test_path, "Success", timestamp)
            assert success, "Failed to update status"
            
            # Verify status update
            files = file_mgr.list_files()
            assert files[0]["last_status"] == "Success", "Status not updated"
            assert files[0]["last_run"] == timestamp, "Timestamp not updated"
            
            print("✅ PASS: FileManager dict operations work correctly")
            return True
        finally:
            os.unlink(test_path)
    finally:
        os.unlink(config_path)


def test_enable_disable_persistence():
    """Test that enable/disable state persists in config."""
    print("\nTest 4: Enable/disable persistence...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
        config_data = {
            "files": [
                {
                    "path": "C:\\test.xlsx",
                    "enabled": True,
                    "last_status": None,
                    "last_run": None
                }
            ],
            "schedule_time": "09:00",
            "auto_refresh_enabled": True,
            "theme_mode": "dark",
            "run_on_startup": False
        }
        json.dump(config_data, f)
    
    try:
        # Load config and disable file
        config = ConfigHandler(config_path)
        success = config.set_file_enabled("C:\\test.xlsx", False)
        assert success, "Failed to disable file"
        
        # Reload config from disk
        config2 = ConfigHandler(config_path)
        files = config2.get_files()
        
        assert files[0]["enabled"] == False, "Disabled state not persisted"
        
        print("✅ PASS: Enable/disable state persists correctly")
        return True
    finally:
        os.unlink(config_path)


def test_log_directory_config():
    """Test log directory configuration."""
    print("\nTest 5: Log directory configuration...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_path = f.name
        config_data = {
            "files": [],
            "schedule_time": "09:00",
            "auto_refresh_enabled": True,
            "theme_mode": "dark",
            "run_on_startup": False
        }
        json.dump(config_data, f)
    
    try:
        config = ConfigHandler(config_path)
        
        # Should be None by default
        log_dir = config.get_log_directory()
        assert log_dir is None, f"Expected None, got {log_dir}"
        
        # Set custom directory
        config.set_log_directory("C:\\CustomLogs")
        
        # Reload and verify
        config2 = ConfigHandler(config_path)
        log_dir = config2.get_log_directory()
        assert log_dir == "C:\\CustomLogs", f"Expected C:\\CustomLogs, got {log_dir}"
        
        print("✅ PASS: Log directory configuration works correctly")
        return True
    finally:
        os.unlink(config_path)


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 2 Basic Verification Tests")
    print("=" * 60)
    
    tests = [
        test_config_metadata_fields,
        test_backward_compatibility,
        test_file_manager_dict_operations,
        test_enable_disable_persistence,
        test_log_directory_config
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{len(tests)} tests passed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All Phase 2 basic tests passed!")
        return 0
    else:
        print(f"❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
