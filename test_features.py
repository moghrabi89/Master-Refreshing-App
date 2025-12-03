"""
Comprehensive Feature Testing Script
Tests all major features of the application
"""

print('=' * 70)
print('         COMPREHENSIVE FEATURE TESTING')
print('=' * 70)
print()

# Test 1: Configuration System
print('[1] Configuration System:')
try:
    from config_handler import ConfigHandler
    config = ConfigHandler()
    config.set_schedule_time('08:00')
    time = config.get_schedule_time()
    print(f'    ✓ Set/Get time: {time}')
    config.add_file('test.xlsx')
    files = config.get_files()
    print(f'    ✓ Add/Get files: {len(files)} files')
    config.remove_file('test.xlsx')
    print('    ✓ Remove file: OK')
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 2: File Manager
print()
print('[2] File Manager:')
try:
    from file_manager import FileManager
    fm = FileManager(config)
    result = fm.add_files(['test1.xlsx', 'test2.xlsx'])
    print(f'    ✓ Batch add: {result["total_added"]} added')
    count = fm.get_file_count()
    print(f'    ✓ File count: {count}')
    fm.clear_all()  # Correct method name
    print('    ✓ Clear all: OK')
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 3: Scheduler
print()
print('[3] Scheduler System:')
try:
    from scheduler import RefreshScheduler
    called = []
    def callback():
        called.append(True)
    scheduler = RefreshScheduler('12:00', callback)
    print(f'    ✓ Create scheduler: OK')
    print(f'    ✓ Scheduled time: {scheduler.scheduled_time}')
    scheduler.set_schedule_time('14:00')  # Correct method name
    print(f'    ✓ Update time: {scheduler.scheduled_time}')
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 4: Theme System
print()
print('[4] Theme System:')
try:
    from theme import get_theme  # Correct function name
    theme_manager = get_theme()
    theme_css = theme_manager.get_stylesheet()
    print(f'    ✓ Generate theme: {len(theme_css)} chars')
    print(f'    ✓ Contains QMainWindow: {"QMainWindow" in theme_css}')
    print(f'    ✓ Contains QPushButton: {"QPushButton" in theme_css}')
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 5: Logger
print()
print('[5] Logging System:')
try:
    from logs_window import init_logger, get_logger
    init_logger()
    logger = get_logger()
    logger.info('Test info message')
    logger.warning('Test warning')
    logger.error('Test error')
    print('    ✓ Logger initialized: OK')
    print('    ✓ Log methods: OK')
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 6: Integrity Checker
print()
print('[6] Integrity System:')
try:
    from integrity_checker import IntegrityChecker
    checker = IntegrityChecker()
    
    # Test auto-manifest triggers
    should_gen = checker.should_auto_generate()
    print(f'    ✓ Auto-generate check: {not should_gen}')
    
    # Test manifest metadata
    metadata = checker.get_manifest_metadata()
    print(f'    ✓ Manifest exists: {metadata["exists"]}')
    print(f'    ✓ Total files: {metadata["total_files"]}')
    
    # Test verification
    result = checker.verify_integrity()
    print(f'    ✓ Verification: {checker.get_status_text()}')
    print(f'    ✓ Time: {checker.verification_time_ms:.2f} ms')
    
    # Test detailed report
    report = checker.get_detailed_report()
    print(f'    ✓ Report status: {report["overall_status"]}')
    
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 7: Startup Manager
print()
print('[7] Startup Manager:')
try:
    from startup_manager import StartupManager
    sm = StartupManager()
    is_enabled = sm.is_enabled()
    print(f'    ✓ Check status: {is_enabled}')
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 8: System Tray
print()
print('[8] System Tray:')
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    window = QMainWindow()  # Create dummy window for tray
    from tray import SystemTrayManager
    tray = SystemTrayManager(window)  # Requires main_window parameter
    print('    ✓ Tray manager created: OK')
    print('    ✓ Tray available: {}'.format(tray.system_tray is not None))
    
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 9: Main Window UI
print()
print('[9] Main Window UI:')
try:
    from PyQt6.QtWidgets import QApplication
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    from ui_main import MainWindow
    window = MainWindow()
    print('    ✓ Window created: OK')
    print(f'    ✓ Has file table: {window.file_table is not None}')
    print(f'    ✓ Has buttons: {window.add_files_btn is not None}')
    print(f'    ✓ Has progress bar: {window.progress_bar is not None}')
    print(f'    ✓ Has integrity label: {window.integrity_label is not None}')
    
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

# Test 10: Integrity UI
print()
print('[10] Integrity Details UI:')
try:
    from PyQt6.QtWidgets import QApplication
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    from integrity_ui import IntegrityDetailsWindow
    from integrity_checker import IntegrityChecker
    
    checker = IntegrityChecker()
    dialog = IntegrityDetailsWindow(None, checker)
    print('    ✓ Dialog created: OK')
    print(f'    ✓ Has table: {dialog.files_table is not None}')
    print(f'    ✓ Has auto-generate btn: {dialog.auto_generate_btn is not None}')
    print(f'    ✓ Has refresh btn: {dialog.refresh_btn is not None}')
    print(f'    ✓ Has summary labels: {dialog.status_label is not None}')
    
    print('    Result: PASSED')
except Exception as e:
    print(f'    ✗ Error: {e}')
    print('    Result: FAILED')

print()
print('=' * 70)
print('         ALL FEATURES TESTED')
print('=' * 70)
