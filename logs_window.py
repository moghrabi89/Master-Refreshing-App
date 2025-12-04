"""
logs_window.py - Advanced Logging System

Purpose:
    Complete logging system with dual output: real-time UI display and
    persistent file logging. Provides color-coded entries, automatic rotation,
    and thread-safe operations for concurrent logging from multiple modules.
    
    Features:
    - Real-time log display in QTextEdit widget
    - Color-coded log levels (INFO, SUCCESS, WARNING, ERROR, DEBUG)
    - External file logging with rotation (5MB, 3 backups)
    - Thread-safe logging operations
    - Auto-scroll to latest entry
    - Clear logs functionality
    - Timestamp formatting
    - HTML-based formatting for rich text display

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QObject, pyqtSignal, Qt
from PyQt6.QtGui import QTextCursor
from utils.paths import get_app_root


class LogSignals(QObject):
    """
    Qt signals for thread-safe logging to UI.
    
    Since logging can be called from background threads (scheduler, refresher),
    we need signals to safely update the UI from the main thread.
    """
    log_message = pyqtSignal(str, str)  # (message, level)


class Logger:
    """
    Professional logging manager with dual output.
    
    This class provides a centralized logging interface that outputs to:
    1. UI widget (QTextEdit) with color-coded formatting
    2. External file (logs/app.log) with rotation
    
    Features:
        - Thread-safe UI updates via Qt signals
        - Color-coded log levels
        - Automatic timestamp formatting
        - Rotating file handler (prevents huge log files)
        - Lazy UI widget attachment
        - Python logging module integration
    
    Architecture:
        - Wraps Python's logging module
        - Emits Qt signals for UI updates
        - Uses RotatingFileHandler for file output
        - Maintains both UI and file handlers
    """
    
    # Log level colors (HTML format for QTextEdit)
    COLORS = {
        'INFO': '#AAAAAA',      # Light gray
        'SUCCESS': '#50C878',   # Emerald green
        'WARNING': '#FFA500',   # Orange
        'ERROR': '#DC3545',     # Red
        'DEBUG': '#00FFFF'      # Cyan
    }
    
    def __init__(self, ui_widget: Optional[QTextEdit] = None, log_file: str = "logs/app.log", config_handler=None):
        """
        Initialize the logging system.
        
        Args:
            ui_widget: QTextEdit widget for log display (can be set later)
            log_file: Path to log file (default: logs/app.log, resolved from app root)
            config_handler: Optional ConfigHandler instance to read custom log directory
        """
        self.ui_widget = ui_widget
        self.config_handler = config_handler
        
        # Determine log directory
        log_dir = None
        if config_handler:
            try:
                custom_log_dir = config_handler.get_log_directory()
                if custom_log_dir and os.path.isdir(custom_log_dir):
                    log_dir = custom_log_dir
            except:
                pass  # Fall back to default
        
        # Use custom directory or default
        if log_dir:
            self.log_file = os.path.join(log_dir, "app.log")
        else:
            # Resolve log file path from app root if relative
            if not os.path.isabs(log_file):
                self.log_file = str(get_app_root() / log_file)
            else:
                self.log_file = log_file
        
        self.signals = LogSignals()
        
        # Setup Python logging
        self._setup_file_logging()
        
        # Connect signal to UI update method
        if self.ui_widget:
            self.signals.log_message.connect(self._append_to_ui)
    
    def _setup_file_logging(self) -> None:
        """
        Configure Python logging with rotating file handler.
        
        Configuration:
            - Log file: logs/app.log (resolved from app root)
            - Max size: 5MB per file
            - Backup count: 3 files
            - Format: [YYYY-MM-DD HH:MM:SS] [LEVEL] - Message
            - Encoding: UTF-8
        """
        # Ensure logs directory exists (using parent of log file path)
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        
        # Get logger instance
        self.logger = logging.getLogger('MasterRefreshingApp')
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
    
    def set_ui_widget(self, widget: QTextEdit) -> None:
        """
        Set or update the UI log widget.
        
        Args:
            widget: QTextEdit widget for log display
        """
        self.ui_widget = widget
        
        # Connect signal if not already connected
        try:
            self.signals.log_message.disconnect()
        except:
            pass
        
        self.signals.log_message.connect(self._append_to_ui)
    
    def info(self, message: str) -> None:
        """
        Log an informational message.
        
        Args:
            message: Log message text
        """
        self._log(message, 'INFO')
    
    def success(self, message: str) -> None:
        """
        Log a success message (custom level).
        
        Args:
            message: Success message text
        """
        self._log(message, 'SUCCESS')
    
    def warning(self, message: str) -> None:
        """
        Log a warning message.
        
        Args:
            message: Warning message text
        """
        self._log(message, 'WARNING')
    
    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: Error message text
            exception: Optional exception object for detailed logging
        """
        if exception:
            message = f"{message} | Exception: {str(exception)}"
        self._log(message, 'ERROR')
    
    def debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: Debug message text
        """
        self._log(message, 'DEBUG')
    
    def _log(self, message: str, level: str) -> None:
        """
        Internal logging method.
        
        Args:
            message: Log message
            level: Log level (INFO, SUCCESS, WARNING, ERROR, DEBUG)
        """
        # Log to file (map SUCCESS to INFO for standard logging)
        file_level = level if level != 'SUCCESS' else 'INFO'
        log_method = getattr(self.logger, file_level.lower(), self.logger.info)
        log_method(message)
        
        # Emit signal for UI update (thread-safe)
        self.signals.log_message.emit(message, level)
    
    def _append_to_ui(self, message: str, level: str) -> None:
        """
        Append formatted message to UI widget.
        
        Args:
            message: Log message
            level: Log level for color coding
        
        This method runs in the main thread (via Qt signal).
        """
        if not self.ui_widget:
            return
        
        # Get color for level
        color = self.COLORS.get(level, '#FFFFFF')
        
        # Format timestamp
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Create HTML formatted message
        html_message = (
            f'<span style="color: #666666;">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">[{level}]</span> '
            f'<span style="color: {color};">{message}</span>'
        )
        
        # Append to widget
        self.ui_widget.append(html_message)
        
        # Auto-scroll to bottom
        cursor = self.ui_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.ui_widget.setTextCursor(cursor)
    
    def clear_ui_logs(self) -> None:
        """
        Clear logs from UI display only (file logs remain).
        """
        if self.ui_widget:
            self.ui_widget.clear()
            self.info("UI logs cleared")
    
    # ═══════════════════════════════════════════════════════════════
    # Specialized Logging Methods
    # ═══════════════════════════════════════════════════════════════
    
    def log_refresh_start(self, file_path: str) -> None:
        """Log the start of a file refresh operation."""
        filename = os.path.basename(file_path)
        self.info(f"Starting refresh: {filename}")
    
    def log_refresh_success(self, file_path: str, duration: float) -> None:
        """Log successful file refresh."""
        filename = os.path.basename(file_path)
        self.success(f"✓ Refreshed: {filename} ({duration:.1f}s)")
    
    def log_refresh_error(self, file_path: str, error_message: str) -> None:
        """Log file refresh error."""
        filename = os.path.basename(file_path)
        self.error(f"✗ Failed: {filename} - {error_message}")
    
    def log_scheduler_start(self, scheduled_time: str) -> None:
        """Log scheduler start event."""
        self.info(f"Scheduler started - Daily refresh at {scheduled_time}")
    
    def log_scheduler_stop(self) -> None:
        """Log scheduler stop event."""
        self.info("Scheduler stopped")
    
    def log_scheduler_trigger(self) -> None:
        """Log scheduled refresh trigger."""
        self.info("⏰ Scheduled refresh triggered")
    
    def log_file_added(self, file_path: str) -> None:
        """Log file addition."""
        filename = os.path.basename(file_path)
        self.success(f"+ Added file: {filename}")
    
    def log_file_removed(self, file_path: str) -> None:
        """Log file removal."""
        filename = os.path.basename(file_path)
        self.info(f"- Removed file: {filename}")
    
    def log_app_start(self) -> None:
        """Log application start."""
        self.info("=" * 60)
        self.info("Master Refreshing App - Started")
        self.info("=" * 60)
    
    def log_app_exit(self) -> None:
        """Log application exit."""
        self.info("Application shutting down...")
    
    def __repr__(self) -> str:
        """String representation of Logger."""
        return f"Logger(file={self.log_file}, ui_attached={self.ui_widget is not None})"


# Singleton instance for global access
_logger_instance: Optional[Logger] = None


def get_logger() -> Logger:
    """
    Get the global logger instance.
    
    Returns:
        Logger: The singleton logger instance
    """
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance


def init_logger(ui_widget: Optional[QTextEdit] = None, log_file: str = "logs/app.log", config_handler=None) -> Logger:
    """
    Initialize the global logger instance.
    
    Args:
        ui_widget: QTextEdit widget for log display
        log_file: Path to log file
        config_handler: Optional ConfigHandler to read custom log directory
    
    Returns:
        Logger: The initialized logger instance
    """
    global _logger_instance
    _logger_instance = Logger(ui_widget, log_file, config_handler)
    return _logger_instance


# Test code
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
    import sys
    
    app = QApplication(sys.argv)
    
    # Create main window with log display
    window = QMainWindow()
    window.setWindowTitle("Logger Test")
    window.resize(800, 600)
    
    central = QWidget()
    layout = QVBoxLayout(central)
    
    # Log display
    log_widget = QTextEdit()
    log_widget.setReadOnly(True)
    layout.addWidget(log_widget)
    
    # Test buttons
    btn_info = QPushButton("Test INFO")
    btn_success = QPushButton("Test SUCCESS")
    btn_warning = QPushButton("Test WARNING")
    btn_error = QPushButton("Test ERROR")
    btn_clear = QPushButton("Clear Logs")
    
    layout.addWidget(btn_info)
    layout.addWidget(btn_success)
    layout.addWidget(btn_warning)
    layout.addWidget(btn_error)
    layout.addWidget(btn_clear)
    
    window.setCentralWidget(central)
    
    # Initialize logger
    logger = init_logger(log_widget)
    logger.log_app_start()
    
    # Connect buttons
    btn_info.clicked.connect(lambda: logger.info("This is an info message"))
    btn_success.clicked.connect(lambda: logger.success("Operation completed successfully!"))
    btn_warning.clicked.connect(lambda: logger.warning("This is a warning message"))
    btn_error.clicked.connect(lambda: logger.error("This is an error message"))
    btn_clear.clicked.connect(logger.clear_ui_logs)
    
    # Test specialized methods
    logger.log_file_added("C:/test/report.xlsx")
    logger.log_refresh_start("C:/test/report.xlsx")
    logger.log_refresh_success("C:/test/report.xlsx", 5.3)
    logger.log_scheduler_start("06:00")
    
    window.show()
    sys.exit(app.exec())
