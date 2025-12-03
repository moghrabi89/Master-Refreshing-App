"""
ui_main.py - Main Window UI Implementation

Purpose:
    Complete PyQt6 graphical interface for Master Refreshing App.
    Features modern, clean design with:
    - Header banner with title and developer credit
    - File manager panel with table and add/remove buttons
    - Scheduler control panel with time picker and start/stop functionality
    - Manual refresh button
    - Real-time logs display panel
    - Status bar
    
    UI ONLY - No backend logic implemented.

Author: ENG. Saeed Al-moghrabi
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QTextEdit,
    QTimeEdit, QFrame, QStatusBar, QHeaderView, QFileDialog
)
from PyQt6.QtCore import Qt, QTime
from PyQt6.QtGui import QFont, QColor


class MainWindow(QMainWindow):
    """
    Main application window with complete UI layout.
    
    This class builds the entire user interface including all panels,
    controls, and styling. No backend logic is implemented here.
    """
    
    def __init__(self):
        """Initialize the main window and build the UI."""
        super().__init__()
        self.setup_window()
        self.setup_ui()
        self.setup_styles()
    
    def setup_window(self):
        """Configure main window properties."""
        self.setWindowTitle("Master Refreshing App")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
    
    def setup_ui(self):
        """Build the complete user interface layout."""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Header Section
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # 2. Content Area (File Manager + Controls)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # 2.1 Left Side: File Manager Panel
        file_panel = self.create_file_manager_panel()
        content_layout.addWidget(file_panel, stretch=3)
        
        # 2.2 Right Side: Controls Panel (Scheduler + Refresh)
        controls_panel = self.create_controls_panel()
        content_layout.addWidget(controls_panel, stretch=2)
        
        main_layout.addLayout(content_layout)
        
        # 3. Logs Panel
        logs_panel = self.create_logs_panel()
        main_layout.addWidget(logs_panel)
        
        # 4. Status Bar
        self.create_status_bar()
    
    def create_header(self):
        """
        Create the application header banner.
        
        Returns:
            QFrame: Header widget with title and subtitle
        """
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(100)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(5)
        
        # Main title
        title_label = QLabel("Master Refreshing App")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        
        # Subtitle (developer credit)
        subtitle_label = QLabel("Developed by ENG. Saeed Al-moghrabi")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 11)
        subtitle_label.setFont(subtitle_font)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        return header_frame
    
    def create_file_manager_panel(self):
        """
        Create the file management panel.
        
        Returns:
            QFrame: File manager panel with table and buttons
        """
        panel = QFrame()
        panel.setObjectName("fileManagerPanel")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Panel title
        title_label = QLabel("📁 Excel Files Manager")
        title_label.setObjectName("panelTitle")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # File table widget
        self.file_table = QTableWidget()
        self.file_table.setObjectName("fileTable")
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["File Name", "Full Path", "Extension"])
        
        # Configure table
        self.file_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.file_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.horizontalHeader().setStretchLastSection(False)
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        layout.addWidget(self.file_table)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Add Files button
        self.add_files_btn = QPushButton("➕ Add Files")
        self.add_files_btn.setObjectName("addFilesBtn")
        self.add_files_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_files_btn.setMinimumHeight(40)
        
        # Remove Selected button
        self.remove_files_btn = QPushButton("🗑️ Remove Selected")
        self.remove_files_btn.setObjectName("removeFilesBtn")
        self.remove_files_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_files_btn.setMinimumHeight(40)
        
        buttons_layout.addWidget(self.add_files_btn)
        buttons_layout.addWidget(self.remove_files_btn)
        
        layout.addLayout(buttons_layout)
        
        return panel
    
    def create_controls_panel(self):
        """
        Create the scheduler and refresh controls panel.
        
        Returns:
            QFrame: Controls panel with scheduler and refresh button
        """
        panel = QFrame()
        panel.setObjectName("controlsPanel")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Scheduler Section
        scheduler_frame = self.create_scheduler_section()
        layout.addWidget(scheduler_frame)
        
        # Spacer
        layout.addStretch()
        
        # Manual Refresh Button
        refresh_frame = self.create_refresh_section()
        layout.addWidget(refresh_frame)
        
        # Spacer at bottom
        layout.addStretch()
        
        return panel
    
    def create_scheduler_section(self):
        """
        Create the scheduler control section.
        
        Returns:
            QFrame: Scheduler controls frame
        """
        frame = QFrame()
        frame.setObjectName("schedulerFrame")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title_label = QLabel("⏰ Daily Scheduler")
        title_label.setObjectName("panelTitle")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Time selection label
        time_label = QLabel("Refresh Time:")
        time_label.setFont(QFont("Segoe UI", 11))
        layout.addWidget(time_label)
        
        # Time picker
        self.time_edit = QTimeEdit()
        self.time_edit.setObjectName("timeEdit")
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime(6, 0))  # Default: 06:00 AM
        self.time_edit.setMinimumHeight(40)
        self.time_edit.setFont(QFont("Segoe UI", 12))
        layout.addWidget(self.time_edit)
        
        # Scheduler status indicator
        self.scheduler_status_label = QLabel("● Scheduler: Stopped")
        self.scheduler_status_label.setObjectName("schedulerStatus")
        self.scheduler_status_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self.scheduler_status_label)
        
        # Start Scheduler button
        self.start_scheduler_btn = QPushButton("▶️ Start Scheduler")
        self.start_scheduler_btn.setObjectName("startSchedulerBtn")
        self.start_scheduler_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_scheduler_btn.setMinimumHeight(45)
        layout.addWidget(self.start_scheduler_btn)
        
        # Stop Scheduler button
        self.stop_scheduler_btn = QPushButton("⏸️ Stop Scheduler")
        self.stop_scheduler_btn.setObjectName("stopSchedulerBtn")
        self.stop_scheduler_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_scheduler_btn.setMinimumHeight(45)
        self.stop_scheduler_btn.setEnabled(False)  # Initially disabled
        layout.addWidget(self.stop_scheduler_btn)
        
        return frame
    
    def create_refresh_section(self):
        """
        Create the manual refresh section.
        
        Returns:
            QFrame: Manual refresh button frame
        """
        frame = QFrame()
        frame.setObjectName("refreshFrame")
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Section title
        title_label = QLabel("🔄 Manual Actions")
        title_label.setObjectName("panelTitle")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Refresh Now button (prominent)
        self.refresh_now_btn = QPushButton("⚡ Refresh Now")
        self.refresh_now_btn.setObjectName("refreshNowBtn")
        self.refresh_now_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_now_btn.setMinimumHeight(60)
        refresh_font = QFont("Segoe UI", 13, QFont.Weight.Bold)
        self.refresh_now_btn.setFont(refresh_font)
        layout.addWidget(self.refresh_now_btn)
        
        return frame
    
    def create_logs_panel(self):
        """
        Create the activity logs display panel.
        
        Returns:
            QFrame: Logs panel with text display
        """
        panel = QFrame()
        panel.setObjectName("logsPanel")
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 10, 15, 15)
        
        # Panel title
        title_label = QLabel("📋 Activity Logs")
        title_label.setObjectName("panelTitle")
        title_font = QFont("Segoe UI", 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Logs text display
        self.logs_display = QTextEdit()
        self.logs_display.setObjectName("logsDisplay")
        self.logs_display.setReadOnly(True)
        self.logs_display.setMinimumHeight(200)
        self.logs_display.setMaximumHeight(250)
        self.logs_display.setFont(QFont("Consolas", 9))
        
        # Add placeholder text
        self.logs_display.setPlaceholderText("Application logs will appear here...")
        
        layout.addWidget(self.logs_display)
        
        return panel
    
    def create_status_bar(self):
        """Create and configure the status bar."""
        status_bar = QStatusBar()
        status_bar.setObjectName("statusBar")
        
        # Add status message
        self.status_message = QLabel("Ready")
        self.status_message.setFont(QFont("Segoe UI", 9))
        status_bar.addWidget(self.status_message)
        
        # Add file count indicator
        self.file_count_label = QLabel("Files: 0")
        self.file_count_label.setFont(QFont("Segoe UI", 9))
        status_bar.addPermanentWidget(self.file_count_label)
        
        self.setStatusBar(status_bar)
    
    def setup_styles(self):
        """Apply modern stylesheet to the entire application."""
        stylesheet = """
            /* ===== GENERAL ===== */
            QMainWindow {
                background-color: #1E1E1E;
            }
            
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            
            /* ===== HEADER ===== */
            QFrame#headerFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4169E1,
                    stop:0.5 #008080,
                    stop:1 #50C878
                );
                border: none;
                border-radius: 0px;
            }
            
            QLabel#titleLabel {
                color: #FFFFFF;
                background: transparent;
            }
            
            QLabel#subtitleLabel {
                color: #E0E0E0;
                background: transparent;
            }
            
            /* ===== PANELS ===== */
            QFrame#fileManagerPanel,
            QFrame#controlsPanel,
            QFrame#logsPanel {
                background-color: #2D2D2D;
                border-radius: 12px;
                border: 1px solid #3A3A3A;
            }
            
            QFrame#schedulerFrame,
            QFrame#refreshFrame {
                background-color: #252525;
                border-radius: 10px;
                border: 1px solid #3A3A3A;
            }
            
            QLabel#panelTitle {
                color: #FFFFFF;
                background: transparent;
            }
            
            /* ===== BUTTONS ===== */
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4169E1,
                    stop:1 #008080
                );
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5179F1,
                    stop:1 #009090
                );
            }
            
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3159D1,
                    stop:1 #007070
                );
            }
            
            QPushButton:disabled {
                background: #3A3A3A;
                color: #666666;
            }
            
            QPushButton#refreshNowBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #50C878,
                    stop:1 #00FFFF
                );
                font-size: 14px;
            }
            
            QPushButton#refreshNowBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D888,
                    stop:1 #10FFFF
                );
            }
            
            QPushButton#removeFilesBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #DC3545,
                    stop:1 #C82333
                );
            }
            
            QPushButton#removeFilesBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EC4555,
                    stop:1 #D83343
                );
            }
            
            /* ===== TABLE ===== */
            QTableWidget {
                background-color: #252525;
                alternate-background-color: #2A2A2A;
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                gridline-color: #3A3A3A;
                color: #FFFFFF;
            }
            
            QTableWidget::item {
                padding: 8px;
            }
            
            QTableWidget::item:selected {
                background-color: #4169E1;
                color: #FFFFFF;
            }
            
            QHeaderView::section {
                background-color: #1E1E1E;
                color: #FFFFFF;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #4169E1;
                font-weight: bold;
            }
            
            /* ===== TIME EDIT ===== */
            QTimeEdit {
                background-color: #252525;
                border: 2px solid #3A3A3A;
                border-radius: 8px;
                padding: 8px;
                color: #FFFFFF;
            }
            
            QTimeEdit:focus {
                border: 2px solid #4169E1;
            }
            
            QTimeEdit::up-button, QTimeEdit::down-button {
                background-color: #3A3A3A;
                border: none;
                width: 20px;
                border-radius: 4px;
            }
            
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {
                background-color: #4A4A4A;
            }
            
            /* ===== LOGS DISPLAY ===== */
            QTextEdit#logsDisplay {
                background-color: #1A1A1A;
                border: 1px solid #3A3A3A;
                border-radius: 8px;
                padding: 10px;
                color: #CCCCCC;
            }
            
            /* ===== STATUS BAR ===== */
            QStatusBar {
                background-color: #1A1A1A;
                color: #AAAAAA;
                border-top: 1px solid #3A3A3A;
            }
            
            QStatusBar QLabel {
                background: transparent;
                color: #AAAAAA;
                padding: 4px 8px;
            }
            
            /* ===== SCHEDULER STATUS ===== */
            QLabel#schedulerStatus {
                background: transparent;
                color: #DC3545;
                font-weight: bold;
            }
            
            /* ===== SCROLLBARS ===== */
            QScrollBar:vertical {
                background-color: #252525;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4A4A4A;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #5A5A5A;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                background-color: #252525;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #4A4A4A;
                border-radius: 6px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #5A5A5A;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """
        
        self.setStyleSheet(stylesheet)
    
    def closeEvent(self, event):
        """
        Override close event (future: minimize to tray instead of close).
        
        For now, this is a placeholder for future system tray integration.
        """
        # Future implementation: minimize to tray
        event.accept()


# Test/Preview function (for development only)
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
