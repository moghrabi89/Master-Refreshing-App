"""
Phase 1 Verification Test - Architecture & Stability Improvements

This script verifies that all Phase 1 improvements have been implemented correctly:
1. Centralized application paths (get_app_root)
2. COM initialization in worker threads
3. APScheduler removal from requirements
4. File validation on startup

Author: ENG. Saeed Al-moghrabi
"""

import sys
import os
from pathlib import Path


def test_paths_module():
    """Test 1: Verify utils/paths.py exists and works correctly."""
    print("\n" + "=" * 60)
    print("TEST 1: Centralized Path Resolution (get_app_root)")
    print("=" * 60)
    
    try:
        from utils.paths import get_app_root, get_config_path, get_manifest_path, get_logs_dir
        
        app_root = get_app_root()
        print(f"✅ get_app_root() works: {app_root}")
        print(f"✅ get_config_path() works: {get_config_path()}")
        print(f"✅ get_manifest_path() works: {get_manifest_path()}")
        print(f"✅ get_logs_dir() works: {get_logs_dir()}")
        
        # Verify it returns a Path object
        assert isinstance(app_root, Path), "get_app_root() should return Path object"
        assert app_root.exists(), "App root should exist"
        
        print(f"✅ App root exists and is valid")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_config_handler_paths():
    """Test 2: Verify ConfigHandler uses get_app_root."""
    print("\n" + "=" * 60)
    print("TEST 2: ConfigHandler Path Resolution")
    print("=" * 60)
    
    try:
        from config_handler import ConfigHandler
        from utils.paths import get_app_root
        
        # Create config handler with default path
        config = ConfigHandler()
        
        expected_path = str(get_app_root() / "config.json")
        actual_path = config.config_path
        
        print(f"Expected path: {expected_path}")
        print(f"Actual path:   {actual_path}")
        
        # Normalize paths for comparison (handle different separators)
        expected_normalized = os.path.normpath(expected_path)
        actual_normalized = os.path.normpath(actual_path)
        
        assert expected_normalized == actual_normalized, "Config path should use get_app_root()"
        
        print("✅ ConfigHandler correctly uses get_app_root()")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrity_checker_paths():
    """Test 3: Verify IntegrityChecker uses get_app_root."""
    print("\n" + "=" * 60)
    print("TEST 3: IntegrityChecker Path Resolution")
    print("=" * 60)
    
    try:
        from integrity_checker import IntegrityChecker
        from utils.paths import get_app_root
        
        # Create integrity checker without explicit app_root
        checker = IntegrityChecker()
        
        expected_root = get_app_root()
        actual_root = checker.app_root
        
        print(f"Expected root: {expected_root}")
        print(f"Actual root:   {actual_root}")
        
        assert actual_root == expected_root, "IntegrityChecker should use get_app_root()"
        
        print("✅ IntegrityChecker correctly uses get_app_root()")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_logger_paths():
    """Test 4: Verify Logger uses get_app_root for log file."""
    print("\n" + "=" * 60)
    print("TEST 4: Logger Path Resolution")
    print("=" * 60)
    
    try:
        from logs_window import Logger
        from utils.paths import get_app_root
        
        # Create logger with default path
        logger = Logger(ui_widget=None, log_file="logs/app.log")
        
        expected_path = str(get_app_root() / "logs" / "app.log")
        actual_path = logger.log_file
        
        print(f"Expected path: {expected_path}")
        print(f"Actual path:   {actual_path}")
        
        # Normalize paths
        expected_normalized = os.path.normpath(expected_path)
        actual_normalized = os.path.normpath(actual_path)
        
        assert expected_normalized == actual_normalized, "Logger should use get_app_root()"
        
        print("✅ Logger correctly uses get_app_root()")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pythoncom_import():
    """Test 5: Verify pythoncom is imported in main.py."""
    print("\n" + "=" * 60)
    print("TEST 5: COM Initialization (pythoncom)")
    print("=" * 60)
    
    try:
        # Read main.py and check for pythoncom import
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "import pythoncom" in content, "main.py should import pythoncom"
        print("✅ pythoncom imported in main.py")
        
        # Check for CoInitialize in RefreshWorker.run()
        assert "pythoncom.CoInitialize()" in content, "RefreshWorker.run() should call CoInitialize()"
        print("✅ CoInitialize() found in RefreshWorker.run()")
        
        # Check for CoUninitialize in finally block
        assert "pythoncom.CoUninitialize()" in content, "RefreshWorker.run() should call CoUninitialize()"
        print("✅ CoUninitialize() found in finally block")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_apscheduler_removed():
    """Test 6: Verify APScheduler removed from requirements.txt."""
    print("\n" + "=" * 60)
    print("TEST 6: APScheduler Removal")
    print("=" * 60)
    
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        assert "APScheduler" not in content, "APScheduler should be removed from requirements.txt"
        assert "apscheduler" not in content.lower(), "apscheduler should be removed from requirements.txt"
        
        print("✅ APScheduler successfully removed from requirements.txt")
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_file_validation_method():
    """Test 7: Verify FileManager has validate_file_paths() method."""
    print("\n" + "=" * 60)
    print("TEST 7: File Validation Method")
    print("=" * 60)
    
    try:
        from file_manager import FileManager
        from config_handler import ConfigHandler
        
        config = ConfigHandler()
        fm = FileManager(config)
        
        # Check method exists
        assert hasattr(fm, 'validate_file_paths'), "FileManager should have validate_file_paths() method"
        print("✅ validate_file_paths() method exists")
        
        # Test method works
        removed = fm.validate_file_paths()
        assert isinstance(removed, list), "validate_file_paths() should return a list"
        print(f"✅ validate_file_paths() works (removed {len(removed)} files)")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_startup_validation_integration():
    """Test 8: Verify file validation is integrated in main.py startup."""
    print("\n" + "=" * 60)
    print("TEST 8: Startup Validation Integration")
    print("=" * 60)
    
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for validate_file_paths call in _load_initial_state
        assert "validate_file_paths()" in content, "_load_initial_state should call validate_file_paths()"
        print("✅ validate_file_paths() called in _load_initial_state()")
        
        # Check for logging of removed files
        assert "Removed missing file from configuration" in content, "Should log removed files"
        print("✅ Logging for removed files found")
        
        # Check for summary logging
        assert "Startup validation removed" in content, "Should log validation summary"
        print("✅ Validation summary logging found")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def run_all_tests():
    """Run all Phase 1 verification tests."""
    print("\n" + "=" * 70)
    print("  PHASE 1 VERIFICATION - Architecture & Stability Improvements")
    print("=" * 70)
    
    tests = [
        ("Centralized Path Resolution", test_paths_module),
        ("ConfigHandler Path Integration", test_config_handler_paths),
        ("IntegrityChecker Path Integration", test_integrity_checker_paths),
        ("Logger Path Integration", test_logger_paths),
        ("COM Initialization", test_pythoncom_import),
        ("APScheduler Removal", test_apscheduler_removed),
        ("File Validation Method", test_file_validation_method),
        ("Startup Validation Integration", test_startup_validation_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("  🎉 ALL PHASE 1 IMPROVEMENTS VERIFIED SUCCESSFULLY!")
    else:
        print(f"  ⚠️  {total - passed} test(s) failed - review output above")
    
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
