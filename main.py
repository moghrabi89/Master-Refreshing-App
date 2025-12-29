"""
main.py - Application Entry Point and Main Controller

Purpose:
    Complete application orchestrator for Master Refreshing App.
    Integrates all modules (UI, file manager, scheduler, refresher, tray, logging)
    into a fully functional desktop application with proper signal/slot wiring,
    worker threads for heavy operations, and comprehensive error handling.
    
    Features:
    - Full module integration and initialization
    - Worker threads for Excel refresh operations
    - Signal/slot wiring between all components
    - System tray integration
    - Configuration persistence
    - Global error handling
    - Graceful shutdown
    - Thread-safe operations
    - Integrity verification and detailed inspection UI
    - Auto manifest generation with command-line support

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0 - Production Ready
"""

import sys
import os
import traceback
import pythoncom
from datetime import datetime
from typing import Optional, List
from PyQt6.QtWidgets import (
    QApplication, QMessageBox, QFileDialog, QTableWidgetItem, QMenuBar, QMenu, QCheckBox, QWidget, QHBoxLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QTime, pyqtSlot
from PyQt6.QtGui import QCursor, QAction, QColor

# Import application modules
from ui_main import MainWindow
from config_handler import ConfigHandler
from file_manager import FileManager
from refresher import ExcelRefresher
from scheduler import RefreshScheduler
from tray import SystemTrayManager
from logs_window import init_logger, get_logger, Logger
from theme import get_theme, ThemeManager
from startup_manager import StartupManager
from integrity_checker import IntegrityChecker
from integrity_ui import IntegrityDetailsWindow
from settings_dialog import SettingsDialog
from single_instance import SingleInstanceManager


class RefreshWorker(QObject):
    """
    Worker thread for Excel refresh operations with progress tracking.
    
    Runs Excel refresh in a separate thread to prevent UI freezing.
    Emits signals to update UI with progress, logs, and results.
    Processes files sequentially with real-time progress updates.
    """
    
    # Signals
    started = pyqtSignal()
    progress = pyqtSignal(str, str)  # (message, level) - for logs
    progress_update = pyqtSignal(int)  # percentage (0-100)
    progress_text = pyqtSignal(str)  # "Refreshing file X of Y"
    wait_progress = pyqtSignal(int)  # 2-minute wait progress (0-100)
    wait_time_remaining = pyqtSignal(str)  # Time remaining (MM:SS)
    file_started = pyqtSignal(str)  # file path being processed
    file_completed = pyqtSignal(str, str)  # (file path, status: success/error/skipped)
    finished = pyqtSignal(dict)  # results dictionary
    error = pyqtSignal(str)  # error message
    
    def __init__(self, file_paths: List[str], timeout: int = 3600):
        super().__init__()
        self.file_paths = file_paths
        self.refresher = None
        self.total_files = len(file_paths)
        self.current_index = 0
        self.timeout = timeout
        self.stop_requested = False  # Flag to stop operation
    
    def run(self):
        """Execute refresh operation in background thread with progress tracking."""
        # Initialize COM for this thread
        pythoncom.CoInitialize()
        
        try:
            self.started.emit()
            
            # Create refresher with callbacks and custom timeout
            self.refresher = ExcelRefresher(
                file_paths=self.file_paths,
                log_callback=self._log_callback,
                progress_callback=self._progress_callback,
                wait_progress_callback=self._wait_progress_callback,
                timeout=self.timeout,
                stop_check_callback=lambda: self.stop_requested  # Pass stop check
            )
            
            # Execute sequential refresh
            results = self.refresher.refresh_all_files()
            
            # Check if stopped by user
            if self.stop_requested:
                self.progress_text.emit("Refresh stopped by user")
            else:
                # Emit 100% completion
                self.progress_update.emit(100)
                self.progress_text.emit(f"Completed all {self.total_files} files")
            
            # Emit results
            self.finished.emit(results)
            
        except Exception as e:
            error_msg = f"Refresh worker error: {str(e)}\n{traceback.format_exc()}"
            self.error.emit(error_msg)
        finally:
            # Uninitialize COM for this thread
            pythoncom.CoUninitialize()
    
    def _log_callback(self, message: str, level: str):
        """Callback for refresher logs."""
        self.progress.emit(message, level)
    
    def _wait_progress_callback(self, percentage: int, time_remaining: str):
        """Callback for 2-minute wait progress."""
        self.wait_progress.emit(percentage)
        self.wait_time_remaining.emit(time_remaining)
    
    def _progress_callback(self, current: int, total: int, file_path: str, status: str):
        """
        Callback for progress updates during sequential refresh.
        
        Args:
            current: Current file index (1-based)
            total: Total number of files
            file_path: Path of current file
            status: 'started', 'completed', 'error', 'skipped'
        """
        # Calculate percentage
        percentage = int((current / total) * 100) if total > 0 else 0
        
        file_name = os.path.basename(file_path)
        
        # Emit progress signals
        if status == 'started':
            self.file_started.emit(file_path)
            self.progress_update.emit(percentage)
            self.progress_text.emit(f"File {current}/{total}: {file_name}")
        elif status in ['completed', 'success', 'error', 'skipped']:
            # Map 'success' to 'completed' for consistency
            emit_status = 'completed' if status == 'success' else status
            self.file_completed.emit(file_path, emit_status)
            self.progress_update.emit(percentage)
            self.progress_text.emit(f"Completed {current}/{total} files")


class Application(QObject):
    """
    Main application controller.
    
    This class orchestrates the entire application lifecycle including:
    - Component initialization
    - Signal/slot wiring
    - Configuration management
    - Thread management
    - System tray integration
    - Graceful shutdown
    
    Architecture:
        - Composition over inheritance
        - Event-driven design
        - Thread-safe operations
        - Clean separation of concerns
    """
    
    def __init__(self):
        super().__init__()
        
        # Core components (will be initialized in initialize())
        self.main_window: MainWindow = None  # type: ignore
        self.config: ConfigHandler = None  # type: ignore
        self.file_manager: FileManager = None  # type: ignore
        self.scheduler: RefreshScheduler = None  # type: ignore
        self.tray_manager: SystemTrayManager = None  # type: ignore
        self.startup_manager: StartupManager = None  # type: ignore
        self.integrity_checker: IntegrityChecker = None  # type: ignore
        self.logger: Logger = None  # type: ignore
        self.theme: ThemeManager = None  # type: ignore
        
        # Worker thread management
        self.refresh_thread: Optional[QThread] = None
        self.refresh_worker: Optional[RefreshWorker] = None
        
        # State tracking
        self.is_refreshing = False
        self.is_stopping = False  # Flag to track if user requested to stop operations
        self.scheduler_running = False
        
        # Single instance manager (set by main())
        self.single_instance_manager: Optional[SingleInstanceManager] = None
    
    def initialize(self) -> bool:
        """
        Initialize all application components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # 1. Initialize configuration first (needed for theme)
            self.config = ConfigHandler("config.json")
            
            # 2. Initialize theme with saved mode
            theme_mode = self.config.get_theme_mode()
            self.theme = get_theme()
            self.theme.set_theme_mode(theme_mode)
            
            # 3. Initialize logger (create logs directory first)
            if not os.path.exists("logs"):
                os.makedirs("logs")
            
            # Logger will be fully initialized after UI is created
            self.logger = init_logger(log_file="logs/app.log", config_handler=self.config)
            self.logger.log_app_start()
            
            # 4. Initialize file manager
            self.file_manager = FileManager(self.config)
            
            # 5. Create main window
            self.main_window = MainWindow()
            
            # 6. Apply theme to main window
            self.theme.apply_to_widget(self.main_window)
            
            # 7. Add menu bar
            self._create_menu_bar()
            
            # 8. Connect logger to UI
            self.logger.set_ui_widget(self.main_window.logs_display)
            
            # 9. Wire signals and slots
            self._wire_ui_signals()
            
            # 9. Initialize scheduler
            self._initialize_scheduler()
            
            # 10. Initialize system tray
            self._initialize_system_tray()
            
            # 11. Initialize Windows startup manager
            self._initialize_startup_manager()
            
            # 12. Run integrity verification
            self._run_integrity_check()
            
            # 13. Load initial state from configuration
            self._load_initial_state()
            
            # 14. Log successful initialization
            self.logger.success("Application initialized successfully")
            
            return True
            
        except Exception as e:
            error_msg = f"Initialization failed: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            QMessageBox.critical(
                None,
                "Initialization Error",
                f"Failed to initialize application:\n\n{str(e)}"
            )
            return False
    
    def _wire_ui_signals(self):
        """Connect UI signals to handler methods."""
        # File management buttons
        self.main_window.add_files_btn.clicked.connect(self.handle_add_files)
        self.main_window.remove_files_btn.clicked.connect(self.handle_remove_files)
        
        # Refresh buttons
        self.main_window.refresh_now_btn.clicked.connect(self.handle_manual_refresh)
        self.main_window.stop_refresh_btn.clicked.connect(self.handle_stop_refresh)
        
        # Stop All Operations button
        self.main_window.stop_all_btn.clicked.connect(self.handle_stop_all_operations)
        
        # Scheduler buttons
        self.main_window.start_scheduler_btn.clicked.connect(self.handle_start_scheduler)
        self.main_window.stop_scheduler_btn.clicked.connect(self.handle_stop_scheduler)
        
        # Time edit changes
        self.main_window.time_edit_1.timeChanged.connect(self.handle_time_changed)
        self.main_window.time_edit_2.timeChanged.connect(self.handle_time_changed)
        self.main_window.time_edit_3.timeChanged.connect(self.handle_time_changed)
        
        # Windows Startup checkbox
        self.main_window.startup_checkbox.stateChanged.connect(self.handle_startup_toggle)
        
        # Create Startup Setting button
        self.main_window.create_startup_btn.clicked.connect(self.handle_create_startup_setting)
        
        self.logger.debug("UI signals wired successfully")
    
    def _create_menu_bar(self):
        """Create application menu bar."""
        # Ensure a QMenuBar exists on the main window
        menubar: Optional[QMenuBar] = self.main_window.menuBar()
        if menubar is None:
            menubar = QMenuBar(self.main_window)
            self.main_window.setMenuBar(menubar)
        
        # File menu
        file_menu: Optional[QMenu] = menubar.addMenu("&File") if menubar is not None else None
        if file_menu is None:
            self.logger.error("Failed to create File menu: menubar is None")
            return
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self.main_window)
        settings_action.setStatusTip("Configure application settings")
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # Theme toggle action
        current_theme = self.config.get_theme_mode()
        theme_icon = "🌙" if current_theme == "dark" else "☀️"
        self.theme_toggle_action = QAction(f"{theme_icon} Toggle Theme ({current_theme.capitalize()} Mode)", self.main_window)
        self.theme_toggle_action.setStatusTip("Switch between Dark and Light mode")
        self.theme_toggle_action.triggered.connect(self.handle_toggle_theme)
        file_menu.addAction(self.theme_toggle_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("❌ Exit", self.main_window)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.handle_exit)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu: Optional[QMenu] = menubar.addMenu("&Tools") if menubar is not None else None
        if tools_menu is None:
            # Safety guard for type checkers; in practice this should never happen
            self.logger.error("Failed to create Tools menu: menubar is None")
            return
        
        # Integrity Details action
        integrity_action = QAction("🔒 Integrity Details", self.main_window)
        integrity_action.setStatusTip("View detailed integrity verification status")
        integrity_action.triggered.connect(self.show_integrity_details)
        tools_menu.addAction(integrity_action)
        
        tools_menu.addSeparator()
        
        # Generate Manifest action (Developer mode)
        manifest_action = QAction("⚙️ Generate Integrity Manifest", self.main_window)
        manifest_action.setStatusTip("Regenerate integrity manifest (Developer only)")
        manifest_action.triggered.connect(self.generate_manifest)
        tools_menu.addAction(manifest_action)
        
        self.logger.debug("Menu bar created")
    
    def _initialize_scheduler(self):
        """Initialize the refresh scheduler."""
        scheduled_times = self.config.get_schedule_times()
        
        self.scheduler = RefreshScheduler(
            scheduled_times=scheduled_times,
            refresh_callback=self.handle_scheduled_refresh,
            log_callback=self._scheduler_log_callback
        )
        
        # Auto-start scheduler if enabled in config
        # Also auto-start if Windows startup is enabled (to ensure continuous operation)
        if self.config.is_auto_refresh_enabled():
            self.handle_start_scheduler()
        elif self.config.is_run_on_startup_enabled():
            # If Windows startup is enabled, also enable scheduler for continuous operation
            self.config.set_auto_refresh_enabled(True)
            self.handle_start_scheduler()
            self.logger.info("Scheduler auto-started (Windows startup is enabled)")
        
        times_str = ", ".join([t for t in scheduled_times if t])
        self.logger.debug(f"Scheduler initialized: {times_str}")
    
    def _initialize_system_tray(self):
        """Initialize system tray integration."""
        self.tray_manager = SystemTrayManager(
            main_window=self.main_window,
            on_refresh_now=self.handle_manual_refresh,
            on_start_scheduler=self.handle_start_scheduler,
            on_stop_scheduler=self.handle_stop_scheduler,
            on_exit_app=self.handle_exit
        )
        
        self.tray_manager.show()
        self.logger.debug("System tray initialized")
    
    def _initialize_startup_manager(self):
        """Initialize Windows startup manager."""
        def startup_log_callback(message: str, level: str):
            """Callback for startup manager logs."""
            if self.logger:
                if level == "INFO":
                    self.logger.info(message)
                elif level == "WARNING":
                    self.logger.warning(message)
                elif level == "ERROR":
                    self.logger.error(message)
                else:
                    self.logger.debug(message)
        
        self.startup_manager = StartupManager(log_callback=startup_log_callback)
        self.logger.debug("Startup manager initialized")
        
        # Sync config with actual state if Windows startup is already enabled
        if self.startup_manager.is_enabled() and not self.config.is_run_on_startup_enabled():
            # Sync config with actual state (Windows startup is enabled but config says disabled)
            self.config.set_run_on_startup_enabled(True)
            self.logger.info("Windows startup state synced with registry")
        
        # Ensure checkbox reflects the actual state
        if self.startup_manager.is_enabled():
            self.main_window.startup_checkbox.setChecked(True)
    
    def _run_integrity_check(self):
        """Run integrity verification check on startup with auto-manifest support."""
        def integrity_log_callback(message: str, level: str):
            """Callback for integrity checker logs."""
            if self.logger:
                if level == "INFO":
                    self.logger.info(message)
                elif level == "WARNING":
                    self.logger.warning(message)
                elif level == "ERROR":
                    self.logger.error(message)
                else:
                    self.logger.debug(message)
        
        self.integrity_checker = IntegrityChecker(log_callback=integrity_log_callback)
        
        # Check for auto-manifest triggers (SAFE: only runs with developer flags)
        was_generated, elapsed_ms = self.integrity_checker.auto_generate_if_triggered()
        
        if was_generated:
            self.logger.info(f"🔧 Auto-manifest generated successfully ({elapsed_ms:.1f}ms)")
        
        # Run verification (non-blocking, fast)
        self.integrity_checker.verify_integrity()
        
        # Update UI status indicator
        status_text = self.integrity_checker.get_status_text()
        status_color = self.integrity_checker.get_status_color()
        
        # Update integrity label in status bar
        if hasattr(self.main_window, 'integrity_label'):
            self.main_window.integrity_label.setText(f"Integrity: {status_text}")
            
            # Apply color styling
            color_map = {
                "green": "#50C878",
                "orange": "#FFA500",
                "red": "#DC3545",
                "gray": "#666666"
            }
            color_code = color_map.get(status_color, "#666666")
            self.main_window.integrity_label.setStyleSheet(
                f"color: {color_code}; font-weight: bold;"
            )
        
        self.logger.debug(f"Integrity check completed in {self.integrity_checker.verification_time_ms:.1f}ms")
    
    def _load_initial_state(self):
        """Load initial state from configuration and validate files."""
        # Validate file paths and remove missing files
        missing_files = self.file_manager.validate_file_paths()
        
        if missing_files:
            # Log each removed file
            for file_path in missing_files:
                self.logger.warning(f"Removed missing file from configuration: {file_path}")
            
            # Log summary
            self.logger.warning(f"Startup validation removed {len(missing_files)} missing file(s) from configuration")
        
        # Load files into table
        files = self.file_manager.list_files()
        self._update_file_table(files)
        
        # Update file count
        self._update_file_count()
        
        # Set scheduled times in UI
        times = self.config.get_schedule_times()
        if times[0]:
            hour, minute = map(int, times[0].split(':'))
            self.main_window.time_edit_1.setTime(QTime(hour, minute))
        if times[1]:
            hour, minute = map(int, times[1].split(':'))
            self.main_window.time_edit_2.setTime(QTime(hour, minute))
        if times[2]:
            hour, minute = map(int, times[2].split(':'))
            self.main_window.time_edit_3.setTime(QTime(hour, minute))
        
        # Set Windows startup checkbox state
        startup_enabled = self.config.is_run_on_startup_enabled()
        self.main_window.startup_checkbox.setChecked(startup_enabled)
        
        self.logger.info(f"Loaded {len(files)} files from configuration")
    
    # ═══════════════════════════════════════════════════════════════
    # FILE MANAGEMENT HANDLERS
    # ═══════════════════════════════════════════════════════════════
    
    def handle_add_files(self):
        """Handle add files button click."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self.main_window,
            "Select Excel Files",
            "",
            "Excel Files (*.xlsx *.xlsm *.xlsb *.xls);;All Files (*.*)"
        )
        
        if not file_paths:
            return
        
        # Add files using file manager
        result = self.file_manager.add_files(file_paths)
        
        # Log results
        for added_file in result['added']:
            self.logger.log_file_added(added_file)
        
        for skipped in result['skipped']:
            self.logger.warning(f"Skipped: {os.path.basename(skipped['path'])} - {skipped['reason']}")
        
        # Update UI
        files = self.file_manager.list_files()
        self._update_file_table(files)
        self._update_file_count()
        
        # Show summary message
        if result['total_added'] > 0:
            QMessageBox.information(
                self.main_window,
                "Files Added",
                f"Successfully added {result['total_added']} file(s).\n"
                f"Skipped: {result['total_skipped']}"
            )
    
    def handle_remove_files(self):
        """Handle remove files button click."""
        selected_rows = self.main_window.file_table.selectionModel().selectedRows()  # type: ignore
        
        if not selected_rows:
            QMessageBox.warning(
                self.main_window,
                "No Selection",
                "Please select files to remove."
            )
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self.main_window,
            "Confirm Removal",
            f"Remove {len(selected_rows)} selected file(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Get file paths to remove
        files_to_remove = []
        for row in selected_rows:
            # Column 2 now contains the full path (was column 1 before)
            item = self.main_window.file_table.item(row.row(), 2)
            if item is None:
                continue
            file_path = item.text()
            files_to_remove.append(file_path)
        
        # Remove files
        result = self.file_manager.remove_files(files_to_remove)
        
        # Log removals
        for removed_file in result['removed']:
            self.logger.log_file_removed(removed_file)
        
        # Update UI
        files = self.file_manager.list_files()
        self._update_file_table(files)
        self._update_file_count()
    
    # ═══════════════════════════════════════════════════════════════
    # REFRESH HANDLERS
    # ═══════════════════════════════════════════════════════════════
    
    def handle_manual_refresh(self):
        """Handle manual refresh button click."""
        # Check if already refreshing
        if self.is_refreshing:
            QMessageBox.warning(
                self.main_window,
                "Refresh In Progress",
                "A refresh operation is already running. Please wait for it to complete."
            )
            return
        
        # Get only enabled files
        enabled_files = self.file_manager.get_enabled_files()
        
        if not enabled_files:
            QMessageBox.warning(
                self.main_window,
                "No Files",
                "Please add enabled Excel files before refreshing."
            )
            return
        
        # Start refresh in worker thread
        self._start_refresh_worker(enabled_files)
    
    def handle_stop_refresh(self):
        """Handle stop refresh button click."""
        if not self.is_refreshing:
            return
        
        # Confirm stop action
        reply = QMessageBox.question(
            self.main_window,
            "Stop Refresh",
            "Are you sure you want to stop the refresh operation?\n\nThe current file will be saved before stopping.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.is_stopping = True
            self.logger.warning("⚠️ User requested to stop refresh operation")
            self.main_window.status_message.setText("Stopping refresh operation...")
            self.main_window.stop_refresh_btn.setEnabled(False)
            
            # Signal worker to stop
            if self.refresh_worker:
                self.refresh_worker.stop_requested = True
    
    def handle_stop_all_operations(self):
        """
        Handle Stop All Operations button click.
        
        Stops all running operations (refresh) but does NOT stop the scheduler.
        The scheduler continues to run and will trigger at scheduled times.
        """
        # Check if there are any operations to stop
        if not self.is_refreshing:
            QMessageBox.information(
                self.main_window,
                "No Operations Running",
                "There are no operations currently running to stop."
            )
            return
        
        # Confirm stop action
        reply = QMessageBox.question(
            self.main_window,
            "Stop All Operations",
            "Are you sure you want to stop all running operations?\n\n"
            "This will stop the current refresh operation.\n"
            "The current file will be saved before stopping.\n\n"
            "Note: The scheduler will continue running and will trigger at scheduled times.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Stop refresh operation
            self.is_stopping = True
            self.logger.warning("⚠️ User requested to stop all operations")
            self.main_window.status_message.setText("Stopping all operations...")
            
            # Disable stop button to prevent multiple clicks
            self.main_window.stop_all_btn.setEnabled(False)
            self.main_window.stop_refresh_btn.setEnabled(False)
            
            # Signal worker to stop
            if self.refresh_worker:
                self.refresh_worker.stop_requested = True
            
            # Note: We do NOT stop the scheduler - it continues running
            self.logger.info("Operations stopped. Scheduler continues running.")
    
    def handle_scheduled_refresh(self):
        """Handle scheduled refresh trigger from scheduler."""
        try:
            self.logger.log_scheduler_trigger()
            
            # Get only enabled files
            enabled_files = self.file_manager.get_enabled_files()
            
            if enabled_files:
                self._start_refresh_worker(enabled_files)
            else:
                self.logger.warning("Scheduled refresh aborted: No enabled files to refresh")
        except Exception as e:
            # Catch any exception to prevent application shutdown
            error_msg = f"Error in scheduled refresh handler: {str(e)}\n{traceback.format_exc()}"
            self.logger.error(error_msg)
            # Don't re-raise - keep the application running
    
    def _start_refresh_worker(self, file_paths: List[str]):
        """Start refresh operation in worker thread with progress tracking."""
        self.is_refreshing = True
        self.is_stopping = False
        
        # Disable/Enable buttons
        self.main_window.refresh_now_btn.setVisible(False)
        self.main_window.stop_refresh_btn.setVisible(True)
        self.main_window.stop_refresh_btn.setEnabled(True)
        self.main_window.stop_all_btn.setEnabled(True)  # Enable Stop All button
        self.main_window.add_files_btn.setEnabled(False)
        self.main_window.remove_files_btn.setEnabled(False)
        self.main_window.start_scheduler_btn.setEnabled(False)
        self.main_window.time_edit_1.setEnabled(False)
        self.main_window.time_edit_2.setEnabled(False)
        self.main_window.time_edit_3.setEnabled(False)
        
        # Show and reset progress bar
        self.main_window.progress_container.setVisible(True)
        self.main_window.progress_bar.setValue(0)
        self.main_window.progress_label.setText("Initializing refresh...")
        
        # Change cursor to waiting
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))
        
        # Update status
        self.main_window.status_message.setText(f"Refreshing {len(file_paths)} file(s)...")
        
        # Get timeout from config
        timeout = self.config.get_refresh_timeout()
        timeout_minutes = timeout // 60
        self.logger.info(f"Using refresh timeout: {timeout}s ({timeout_minutes} minutes)")
        
        # Create worker thread with custom timeout
        self.refresh_thread = QThread()
        self.refresh_worker = RefreshWorker(file_paths, timeout=timeout)
        self.refresh_worker.moveToThread(self.refresh_thread)
        
        # Connect signals
        self.refresh_thread.started.connect(self.refresh_worker.run)
        self.refresh_worker.progress.connect(self._on_refresh_progress)
        self.refresh_worker.progress_update.connect(self._on_progress_update)
        self.refresh_worker.progress_text.connect(self._on_progress_text)
        self.refresh_worker.wait_progress.connect(self._on_wait_progress)
        self.refresh_worker.wait_time_remaining.connect(self._on_wait_time_remaining)
        self.refresh_worker.file_started.connect(self._on_file_started)
        self.refresh_worker.file_completed.connect(self._on_file_completed)
        self.refresh_worker.finished.connect(self._on_refresh_finished)
        self.refresh_worker.error.connect(self._on_refresh_error)
        self.refresh_worker.finished.connect(self.refresh_thread.quit)
        self.refresh_worker.finished.connect(self.refresh_worker.deleteLater)
        self.refresh_thread.finished.connect(self.refresh_thread.deleteLater)
        
        # Start thread
        self.refresh_thread.start()
        
        self.logger.info(f"Background refresh started: {len(file_paths)} file(s)")
    
    def _on_refresh_progress(self, message: str, level: str):
        """Handle refresh progress log updates (already logged by worker)."""
        pass
    
    @pyqtSlot(int)
    def _on_progress_update(self, percentage: int):
        """Handle progress bar percentage update."""
        self.main_window.progress_bar.setValue(percentage)
        QApplication.processEvents()  # Keep UI responsive
    
    @pyqtSlot(int)
    def _on_wait_progress(self, percentage: int):
        """Handle 2-minute wait progress bar update."""
        self.main_window.progress_bar.setValue(percentage)
        QApplication.processEvents()  # Keep UI responsive
    
    @pyqtSlot(str)
    def _on_wait_time_remaining(self, time_str: str):
        """Handle countdown timer update."""
        self.main_window.progress_label.setText(f"Time remaining: {time_str}")
        QApplication.processEvents()  # Keep UI responsive
    
    @pyqtSlot(str)
    def _on_progress_text(self, text: str):
        """Handle progress label text update."""
        self.main_window.progress_label.setText(text)
        QApplication.processEvents()  # Keep UI responsive
    
    @pyqtSlot(str)
    def _on_file_started(self, file_path: str):
        """Handle file processing start."""
        file_name = os.path.basename(file_path)
        self.main_window.status_message.setText(f"Processing: {file_name}")
        
        # Highlight the current file being processed in the table
        self._highlight_current_file(file_path, highlight=True)
        
        QApplication.processEvents()  # Keep UI responsive
    
    @pyqtSlot(str, str)
    def _on_file_completed(self, file_path: str, status: str):
        """Handle file processing completion and update status."""
        # Remove highlight from the completed file
        self._highlight_current_file(file_path, highlight=False)
        
        # Map worker status to display status
        status_map = {
            'completed': 'Success',
            'success': 'Success',
            'error': 'Error',
            'skipped': 'Skipped'
        }
        display_status = status_map.get(status, status.capitalize())
        
        # Get current timestamp in ISO format
        timestamp = datetime.now().isoformat()
        
        # Update file status in config and file manager
        self.file_manager.update_file_status(file_path, display_status, timestamp)
        
        # Update only the specific row in the table (fast, no UI freeze)
        self._update_file_row_status(file_path, display_status, timestamp)
    
    @pyqtSlot(dict)
    def _on_refresh_finished(self, results: dict):
        """Handle refresh completion."""
        self.is_refreshing = False
        self.is_stopping = False
        
        # Hide progress bar
        self.main_window.progress_container.setVisible(False)
        
        # Restore UI
        QApplication.restoreOverrideCursor()
        self.main_window.refresh_now_btn.setVisible(True)
        self.main_window.stop_refresh_btn.setVisible(False)
        self.main_window.stop_all_btn.setEnabled(False)  # Disable Stop All button
        self.main_window.add_files_btn.setEnabled(True)
        self.main_window.remove_files_btn.setEnabled(True)
        self.main_window.start_scheduler_btn.setEnabled(True)
        self.main_window.time_edit_1.setEnabled(True)
        self.main_window.time_edit_2.setEnabled(True)
        self.main_window.time_edit_3.setEnabled(True)
        
        # Update status
        self.main_window.status_message.setText("Ready")
        
        # Show summary
        succeeded = results['succeeded']
        failed = results['failed']
        skipped = results.get('skipped', 0)
        elapsed = results['elapsed_time']
        
        # Log detailed results including row changes
        if skipped > 0:
            self.logger.info(
                f"Refresh completed: {succeeded} succeeded, {failed} failed, {skipped} skipped ({elapsed:.1f}s)"
            )
        else:
            self.logger.info(
                f"Refresh completed: {succeeded} succeeded, {failed} failed ({elapsed:.1f}s)"
            )
        
        # Log detailed row information for each successfully refreshed file
        for file_result in results.get('results', []):
            if file_result.get('status') == 'success' and 'added_rows' in file_result:
                file_name = os.path.basename(file_result['file'])
                rows_before = file_result.get('rows_before', 0)
                rows_after = file_result.get('rows_after', 0)
                added_rows = file_result.get('added_rows', 0)
                
                self.logger.info(f"Refresh completed for: {file_name}")
                self.logger.info(f"Rows before: {rows_before}")
                self.logger.info(f"Rows after:  {rows_after}")
                self.logger.info(f"Added rows:  {added_rows}")
        
        # Show notification
        if self.tray_manager:
            if failed == 0 and skipped == 0:
                self.tray_manager.show_notification(
                    "Refresh Complete",
                    f"Successfully refreshed {succeeded} file(s).",
                    self.tray_manager.tray_icon.MessageIcon.Information
                )
            elif skipped > 0:
                self.tray_manager.show_notification(
                    "Refresh Complete",
                    f"Refreshed {succeeded} file(s), {failed} failed, {skipped} skipped.",
                    self.tray_manager.tray_icon.MessageIcon.Information if failed == 0 else self.tray_manager.tray_icon.MessageIcon.Warning
                )
            else:
                self.tray_manager.show_notification(
                    "Refresh Complete",
                    f"Refreshed {succeeded} file(s), {failed} failed.",
                    self.tray_manager.tray_icon.MessageIcon.Warning
                )
    
    @pyqtSlot(str)
    def _on_refresh_error(self, error_msg: str):
        """Handle refresh error."""
        self.is_refreshing = False
        self.is_stopping = False
        
        # Hide progress bar
        self.main_window.progress_container.setVisible(False)
        
        # Restore UI
        QApplication.restoreOverrideCursor()
        self.main_window.refresh_now_btn.setVisible(True)
        self.main_window.stop_refresh_btn.setVisible(False)
        self.main_window.stop_all_btn.setEnabled(False)  # Disable Stop All button
        self.main_window.add_files_btn.setEnabled(True)
        self.main_window.remove_files_btn.setEnabled(True)
        self.main_window.start_scheduler_btn.setEnabled(True)
        self.main_window.time_edit_1.setEnabled(True)
        self.main_window.time_edit_2.setEnabled(True)
        self.main_window.time_edit_3.setEnabled(True)
        
        self.main_window.status_message.setText("Error")
        
        self.logger.error(f"Refresh error: {error_msg}")
        
        QMessageBox.critical(
            self.main_window,
            "Refresh Error",
            "An error occurred during refresh. Check logs for details."
        )
    
    # ═══════════════════════════════════════════════════════════════
    # SCHEDULER HANDLERS
    # ═══════════════════════════════════════════════════════════════
    
    def handle_start_scheduler(self):
        """Handle start scheduler button click."""
        if self.scheduler_running:
            return
        
        success = self.scheduler.start()
        
        if success:
            self.scheduler_running = True
            
            # Update UI
            self.main_window.start_scheduler_btn.setEnabled(False)
            self.main_window.stop_scheduler_btn.setEnabled(True)
            self.main_window.scheduler_status_label.setText("● Scheduler: Running")
            self.main_window.scheduler_status_label.setStyleSheet("color: #50C878; font-weight: bold;")
            
            # Update tray
            if self.tray_manager:
                self.tray_manager.update_scheduler_state(True)
            
            # Save state
            self.config.set_auto_refresh_enabled(True)
            
            # Log
            scheduled_time = self.scheduler.get_scheduled_time()
            self.logger.log_scheduler_start(scheduled_time)
    
    def handle_stop_scheduler(self):
        """Handle stop scheduler button click."""
        if not self.scheduler_running:
            return
        
        success = self.scheduler.stop()
        
        if success:
            self.scheduler_running = False
            
            # Update UI
            self.main_window.start_scheduler_btn.setEnabled(True)
            self.main_window.stop_scheduler_btn.setEnabled(False)
            self.main_window.scheduler_status_label.setText("● Scheduler: Stopped")
            self.main_window.scheduler_status_label.setStyleSheet("color: #DC3545; font-weight: bold;")
            
            # Update tray
            if self.tray_manager:
                self.tray_manager.update_scheduler_state(False)
            
            # Save state
            self.config.set_auto_refresh_enabled(False)
            
            # Log
            self.logger.log_scheduler_stop()
    
    def handle_time_changed(self, time):
        """Handle schedule time change for any of the 3 time fields."""
        # Get all 3 times from UI
        time1_str = self.main_window.time_edit_1.time().toString("HH:mm")
        time2_str = self.main_window.time_edit_2.time().toString("HH:mm")
        time3_str = self.main_window.time_edit_3.time().toString("HH:mm")
        
        # Filter out 00:00 (considered as empty)
        times = []
        if time1_str and time1_str != "00:00":
            times.append(time1_str)
        if time2_str and time2_str != "00:00":
            times.append(time2_str)
        if time3_str and time3_str != "00:00":
            times.append(time3_str)
        
        # Ensure at least one time
        if not times:
            times = [time1_str]  # Always keep first time
        
        # Pad to 3 slots
        while len(times) < 3:
            times.append("")
        
        # Update scheduler
        if self.scheduler:
            self.scheduler.set_times([t for t in times if t])
        
        # Save to config
        self.config.set_schedule_times(times)
        
        times_display = ", ".join([t for t in times if t])
        self.logger.info(f"Schedule times updated: {times_display}")
    
    def _scheduler_log_callback(self, message: str, level: str):
        """Callback for scheduler logs."""
        # Map level to logger method
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "SUCCESS":
            self.logger.success(message)
        elif level == "DEBUG":
            self.logger.debug(message)
    
    # ═══════════════════════════════════════════════════════════════
    # WINDOWS STARTUP HANDLER
    # ═══════════════════════════════════════════════════════════════
    
    def handle_create_startup_setting(self):
        """Handle Create Startup Setting button click."""
        # Check if already enabled
        if self.startup_manager.is_enabled():
            QMessageBox.information(
                self.main_window,
                "Startup Already Enabled",
                "Windows Startup is already configured.\n\nThe application will start automatically with Windows."
            )
            return
        
        # Enable Windows startup
        success, message = self.startup_manager.enable()
        
        if success:
            # Update config
            self.config.set_run_on_startup_enabled(True)
            
            # Update checkbox
            self.main_window.startup_checkbox.setChecked(True)
            
            # Log success
            self.logger.success(f"Windows startup setting created: {message}")
            
            # Show success message
            QMessageBox.information(
                self.main_window,
                "Startup Setting Created",
                f"Windows Startup setting has been created successfully!\n\n{message}\n\n"
                "The application will now start automatically when Windows boots.\n"
                "It will appear in the system tray (next to the clock)."
            )
            
            # Auto-start scheduler if not already running (to ensure continuous operation)
            if not self.scheduler_running:
                self.config.set_auto_refresh_enabled(True)
                self.handle_start_scheduler()
                self.logger.info("Scheduler auto-started after creating startup setting")
        else:
            # Log error
            self.logger.error(f"Failed to create startup setting: {message}")
            
            # Show error message
            QMessageBox.critical(
                self.main_window,
                "Startup Setting Failed",
                f"Could not create Windows Startup setting:\n\n{message}\n\n"
                "Please try again or check your system permissions."
            )
    
    def handle_startup_toggle(self, state):
        """Handle Windows startup checkbox toggle."""
        enabled = (state == 2)  # Qt.CheckState.Checked = 2
        
        if enabled:
            # Enable startup
            success, message = self.startup_manager.enable()
            if success:
                self.config.set_run_on_startup_enabled(True)
                self.logger.success(f"Windows startup enabled: {message}")
            else:
                self.logger.error(f"Failed to enable startup: {message}")
                # Revert checkbox
                self.main_window.startup_checkbox.setChecked(False)
                QMessageBox.warning(
                    self.main_window,
                    "Startup Enable Failed",
                    f"Could not enable Windows startup:\n\n{message}"
                )
        else:
            # Disable startup
            success, message = self.startup_manager.disable()
            if success:
                self.config.set_run_on_startup_enabled(False)
                self.logger.info(f"Windows startup disabled: {message}")
            else:
                self.logger.error(f"Failed to disable startup: {message}")
                # Revert checkbox
                self.main_window.startup_checkbox.setChecked(True)
                QMessageBox.warning(
                    self.main_window,
                    "Startup Disable Failed",
                    f"Could not disable Windows startup:\n\n{message}"
                )
    
    # ═══════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ═══════════════════════════════════════════════════════════════
    
    def handle_toggle_theme(self):
        """Handle theme toggle button click."""
        # Get current theme mode
        current_mode = self.theme.current_theme
        
        # Toggle between dark and light
        new_mode = "light" if current_mode == "dark" else "dark"
        
        # Update theme
        self.theme.set_theme_mode(new_mode)
        
        # Save to config
        self.config.set_theme_mode(new_mode)
        
        # Reapply theme to main window
        self.theme.apply_to_widget(self.main_window)
        
        # Update button text
        theme_icon = "🌙" if new_mode == "dark" else "☀️"
        self.theme_toggle_action.setText(f"{theme_icon} Toggle Theme ({new_mode.capitalize()} Mode)")
        
        # Log
        self.logger.info(f"Theme switched to {new_mode} mode")
        
        # Show notification
        if self.tray_manager:
            self.tray_manager.show_notification(
                "Theme Changed",
                f"Switched to {new_mode.capitalize()} Mode",
                self.tray_manager.tray_icon.MessageIcon.Information
            )
    
    def show_settings_dialog(self):
        """Show settings configuration dialog."""
        try:
            dialog = SettingsDialog(self.config, self.main_window)
            dialog.exec()
        except Exception as e:
            self.logger.error(f"Failed to show settings dialog: {e}")
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to open settings dialog:\n\n{str(e)}"
            )
    
    def show_integrity_details(self):
        """Show detailed integrity verification window."""
        try:
            dialog = IntegrityDetailsWindow(self.main_window, self.integrity_checker)
            dialog.exec()
        except Exception as e:
            self.logger.error(f"Failed to show integrity details: {e}")
            QMessageBox.critical(
                self.main_window,
                "Error",
                f"Failed to open integrity details window:\n\n{str(e)}"
            )
    
    def generate_manifest(self):
        """Regenerate integrity manifest (Developer mode)."""
        # Confirm action
        reply = QMessageBox.question(
            self.main_window,
            "Confirm Manifest Generation",
            "This will regenerate the integrity manifest with current file hashes.\n\n"
            "⚠️ Only use this if you've intentionally modified code files.\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Generate manifest
            elapsed_ms = self.integrity_checker.generate_manifest()
            
            # Show success message
            QMessageBox.information(
                self.main_window,
                "Manifest Generated",
                f"Integrity manifest regenerated successfully!\n\n"
                f"Generation time: {elapsed_ms:.1f}ms"
            )
            
            # Re-run integrity check and update UI
            self._run_integrity_check()
            
            self.logger.info(f"Integrity manifest regenerated in {elapsed_ms:.1f}ms")
            
        except Exception as e:
            self.logger.error(f"Failed to generate manifest: {e}")
            QMessageBox.critical(
                self.main_window,
                "Generation Failed",
                f"Failed to generate integrity manifest:\n\n{str(e)}"
            )
    
    def _update_file_row_status(self, file_path: str, status: str, timestamp: str):
        """Update a specific file row's status and timestamp (fast update)."""
        table = self.main_window.file_table
        
        # Normalize the file path for comparison (handles different path formats)
        normalized_target = os.path.normpath(file_path)
        
        # Find the row for this file
        row_found = False
        for row in range(table.rowCount()):
            path_item = table.item(row, 2)  # Column 2 is Full Path
            if path_item:
                # Normalize both paths for comparison
                table_path = os.path.normpath(path_item.text())
                if table_path == normalized_target:
                    row_found = True
                    
                    # Update Column 4: Last Status
                    status_item = QTableWidgetItem(status)
                    table.setItem(row, 4, status_item)
                    
                    # Update Column 5: Last Refresh
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        formatted_time = timestamp
                    
                    time_item = QTableWidgetItem(formatted_time)
                    table.setItem(row, 5, time_item)
                    
                    # Force UI update
                    QApplication.processEvents()
                    
                    self.logger.debug(f"Updated table row for {os.path.basename(file_path)}: Status={status}, Time={formatted_time}")
                    break
        
        if not row_found:
            self.logger.warning(f"Could not find table row for: {file_path} (searched {table.rowCount()} rows)")
    
    def _highlight_current_file(self, file_path: str, highlight: bool = True):
        """Highlight or unhighlight the current file being processed."""
        table = self.main_window.file_table
        
        # Normalize the file path for comparison
        normalized_target = os.path.normpath(file_path)
        
        for row in range(table.rowCount()):
            path_item = table.item(row, 2)  # Column 2 is Full Path
            if path_item:
                # Normalize both paths for comparison
                table_path = os.path.normpath(path_item.text())
                if table_path == normalized_target:
                    # Apply highlight to all columns in the row
                    if highlight:
                        # Yellow background for current file
                        bg_color = QColor(255, 255, 200)  # Light yellow
                        fg_color = QColor(0, 0, 0)  # Black text
                    else:
                        # Reset to default (white/transparent)
                        bg_color = QColor(255, 255, 255)  # White
                        fg_color = QColor(0, 0, 0)  # Black text
                    
                    for col in range(1, table.columnCount()):  # Skip column 0 (checkbox)
                        item = table.item(row, col)
                        if item:
                            item.setBackground(bg_color)
                            item.setForeground(fg_color)
                    
                    # Force UI update
                    QApplication.processEvents()
                    break
    
    def _update_file_table(self, files: List[dict]):
        """Update the file table with file list."""
        table = self.main_window.file_table
        table.setRowCount(0)
        
        for file_data in files:
            row = table.rowCount()
            table.insertRow(row)
            
            # Column 0: Enabled (checkbox)
            enabled = file_data.get('enabled', True)
            checkbox = QCheckBox()
            checkbox.setChecked(enabled)
            checkbox.setProperty("file_path", file_data['path'])  # Store path for reference
            checkbox.stateChanged.connect(self._handle_checkbox_toggle)
            
            # Center the checkbox
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            table.setCellWidget(row, 0, checkbox_widget)
            
            # Column 1: File Name
            table.setItem(row, 1, QTableWidgetItem(file_data['name']))
            
            # Column 2: Full Path
            table.setItem(row, 2, QTableWidgetItem(file_data['path']))
            
            # Column 3: Extension
            extension = file_data.get('extension', '')
            ext_item = QTableWidgetItem(extension)
            table.setItem(row, 3, ext_item)
            
            # Column 4: Last Status
            last_status = file_data.get('last_status') or 'Never Run'
            status_item = QTableWidgetItem(last_status)
            table.setItem(row, 4, status_item)
            
            # Column 5: Last Refresh
            last_run = file_data.get('last_run')
            if last_run:
                # Format ISO timestamp to human-readable
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_run)
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_time = last_run
            else:
                formatted_time = 'Never'
            table.setItem(row, 5, QTableWidgetItem(formatted_time))
    
    def _handle_checkbox_toggle(self, state):
        """Handle enable/disable checkbox toggle."""
        sender = self.sender()
        if isinstance(sender, QCheckBox):
            file_path = sender.property("file_path")
            enabled = (state == Qt.CheckState.Checked.value)
            
            # Update file manager
            success = self.file_manager.set_file_enabled(file_path, enabled)
            
            status_bar = self.main_window.statusBar()
            if status_bar is not None:
                if success:
                    status = "enabled" if enabled else "disabled"
                    status_bar.showMessage(f"File {status}: {os.path.basename(file_path)}", 3000)
                else:
                    status_bar.showMessage("Failed to update file status", 3000)
    
    def _update_file_count(self):
        """Update the file count in status bar."""
        count = self.file_manager.get_file_count()
        self.main_window.file_count_label.setText(f"Files: {count}")
    
    # ═══════════════════════════════════════════════════════════════
    # APPLICATION LIFECYCLE
    # ═══════════════════════════════════════════════════════════════
    
    def run(self) -> int:
        """
        Show main window and start application event loop.
        
        If Windows startup is enabled, start minimized to system tray.
        
        Returns:
            int: Application exit code
        """
        # Check if Windows startup is enabled (check actual state, not just config)
        # This ensures the app starts in tray even if started from Windows startup
        startup_enabled = self.startup_manager.is_enabled() or self.config.is_run_on_startup_enabled()
        
        if startup_enabled:
            # Start minimized to system tray (hidden)
            self.main_window.hide()
            self.logger.info("Application started minimized to system tray (Windows startup enabled)")
            
            # Show notification
            if self.tray_manager:
                self.tray_manager.show_notification(
                    "Master Refreshing App",
                    "Application is running in the background. Double-click the tray icon to open.",
                    self.tray_manager.tray_icon.MessageIcon.Information
                )
        else:
            # Normal startup - show window
            self.main_window.show()
        
        return QApplication.instance().exec()  # type: ignore
    
    def bring_to_front(self):
        """
        Bring the main window to front and activate it.
        Called when a secondary instance requests activation.
        """
        # If window is minimized or hidden, restore it
        if self.main_window.isMinimized():
            self.main_window.showNormal()
        elif not self.main_window.isVisible():
            self.main_window.show()
        
        # Raise window above others and activate
        self.main_window.raise_()
        self.main_window.activateWindow()
        
        # Log the activation
        self.logger.info("Main window activated by secondary instance request")
    
    def handle_exit(self):
        """Handle application exit."""
        # Confirm exit if scheduler is running
        if self.scheduler_running:
            reply = QMessageBox.question(
                self.main_window,
                "Confirm Exit",
                "Scheduler is running. Do you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # Shutdown gracefully
        self.shutdown()
        
        # Quit application
        QApplication.instance().quit()  # type: ignore
    
    def shutdown(self):
        """Clean shutdown of all components."""
        self.logger.log_app_exit()
        
        # Stop scheduler
        if self.scheduler and self.scheduler_running:
            self.scheduler.stop()
        
        # Hide tray icon
        if self.tray_manager:
            self.tray_manager.hide()
        
        # Cleanup single instance server
        if self.single_instance_manager:
            self.single_instance_manager.cleanup()
        
        # Save configuration
        if self.config:
            self.config.save_config()
        
        self.logger.info("Application shutdown complete")


def setup_exception_handler():
    """Setup global exception handler."""
    def exception_hook(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Uncaught exception:\n{error_msg}")
        
        # Try to log if logger is available
        try:
            logger = get_logger()
            logger.error(f"Uncaught exception: {error_msg}")
        except:
            pass
        
        # Show error dialog
        QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n\n{exc_value}\n\nThe application will continue running."
        )
    
    sys.excepthook = exception_hook


def main():
    """
    Application entry point with command-line support.
    
    Supports flags:
        --generate-manifest: Generate integrity manifest and exit
        --auto-manifest: Auto-generate manifest during startup if needed
    
    Initializes QApplication, creates Application controller,
    and starts the event loop.
    """
    # Check for command-line flags
    if len(sys.argv) > 1:
        if "--generate-manifest" in sys.argv:
            print("Generating integrity manifest...")
            try:
                from integrity_checker import IntegrityChecker
                checker = IntegrityChecker()
                elapsed_ms = checker.generate_manifest(mode="cli")
                print(f"✓ Manifest generated successfully in {elapsed_ms:.1f}ms")
                print(f"  Location: {os.path.join(os.path.dirname(__file__), 'integrity_manifest.json')}")
                return 0
            except Exception as e:
                print(f"✗ Failed to generate manifest: {e}")
                traceback.print_exc()
                return 1
        
        if "--auto-manifest" in sys.argv:
            # Set environment variable to trigger auto-manifest
            os.environ["APP_DEV_MODE"] = "1"
            print("Developer mode enabled - Auto-manifest will be generated if needed")
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Master Refreshing App")
    app.setOrganizationName("ENG. Saeed Al-moghrabi")
    app.setApplicationVersion("1.0.0")
    
    # Setup global exception handler
    setup_exception_handler()
    
    # ═══════════════════════════════════════════════════════════════
    # SINGLE INSTANCE CHECK
    # ═══════════════════════════════════════════════════════════════
    
    single_instance = SingleInstanceManager()
    
    if not single_instance.try_start_as_primary():
        # Another instance is already running
        print("Another instance is already running. Activating existing window...")
        
        # Try to signal the existing instance to show its window
        if single_instance.signal_existing_instance():
            print("Successfully signaled existing instance.")
            return 0
        else:
            print("Warning: Failed to signal existing instance, but it appears to be running.")
            return 1
    
    # We are the primary instance - continue startup
    print("Starting as primary instance...")
    
    # Create application controller
    application = Application()
    application.single_instance_manager = single_instance
    
    # Connect single instance activation signal to bring_to_front
    single_instance.activate_window.connect(application.bring_to_front)
    
    # Initialize application
    if not application.initialize():
        single_instance.cleanup()
        return 1
    
    # Run application
    exit_code = application.run()
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
