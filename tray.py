"""
tray.py - System Tray Integration Module

Purpose:
    Complete system tray management for Master Refreshing App.
    Provides full tray icon functionality, context menu, hide-to-tray behavior,
    and window restoration. This module handles UI behavior only and delegates
    business logic to provided callbacks.
    
    Features:
    - System tray icon with custom/fallback icon support
    - Rich context menu with 5 core actions
    - Minimize/hide to tray behavior
    - Double-click to restore window
    - Tray notifications (with placeholders for future use)
    - Callback-based architecture for clean separation
    - No business logic - pure UI behavior

    Integration Example:
        # In main window's __init__:
        # tray = SystemTrayManager(
        #     main_window=self,
        #     on_refresh_now=self.handle_manual_refresh,
        #     on_start_scheduler=self.handle_start_scheduler,
        #     on_stop_scheduler=self.handle_stop_scheduler,
        #     on_exit_app=self.handle_exit
        # )
        # tray.show()

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0
"""

import os
from typing import Callable, Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSlot


class SystemTrayManager:
    """
    Professional System Tray Manager for Master Refreshing App.
    
    This class manages all system tray interactions including:
    - Tray icon lifecycle
    - Context menu creation and management
    - Window hide/show behavior
    - Tray notifications
    - Double-click restoration
    
    The class uses a callback-based architecture to maintain clean separation
    between UI behavior and business logic. All actual operations (refresh,
    scheduling, etc.) are delegated to the provided callback functions.
    
    Architecture:
        - Composition over inheritance (wraps QSystemTrayIcon)
        - Callback pattern for action handling
        - Event-driven design
        - No business logic coupling
    
    Attributes:
        main_window: Reference to the main QMainWindow
        tray_icon: The QSystemTrayIcon instance
        tray_menu: The context menu (QMenu)
        callbacks: Dictionary of registered callback functions
        _scheduler_running: Internal state for menu updates
    """
    
    def __init__(self,
                 main_window,
                 on_refresh_now: Optional[Callable[[], None]] = None,
                 on_start_scheduler: Optional[Callable[[], None]] = None,
                 on_stop_scheduler: Optional[Callable[[], None]] = None,
                 on_exit_app: Optional[Callable[[], None]] = None):
        """
        Initialize the System Tray Manager.
        
        Args:
            main_window: Reference to the main QMainWindow instance
            on_refresh_now: Callback for manual refresh action
            on_start_scheduler: Callback for starting scheduler
            on_stop_scheduler: Callback for stopping scheduler
            on_exit_app: Callback for application exit
        
        Note:
            All callbacks are optional. If not provided, the actions
            will log warnings instead of executing.
        """
        self.main_window = main_window
        
        # Store callbacks
        self.callbacks = {
            'refresh_now': on_refresh_now,
            'start_scheduler': on_start_scheduler,
            'stop_scheduler': on_stop_scheduler,
            'exit_app': on_exit_app
        }
        
        # Internal state
        self._scheduler_running = False
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self.main_window)
        
        # Load icon (with fallback)
        self._load_icon()
        
        # Create context menu
        self.tray_menu = self._create_menu()
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Connect tray icon activation (double-click) with explicit type
        self.tray_icon.activated[QSystemTrayIcon.ActivationReason].connect(self._on_icon_activated)
        
        # Set tooltip
        self.tray_icon.setToolTip("Master Refreshing App")
        
        # Install event filter on main window to intercept close events
        self._setup_close_behavior()
    
    def _load_icon(self) -> None:
        """
        Load the tray icon from resources with fallback support.
        
        Attempts to load from:
        1. resources/icon.png
        2. Built-in Qt icon as fallback
        
        The icon is also set as the window icon for consistency.
        """
        icon_path = "resources/icon.png"
        
        if os.path.exists(icon_path):
            # Load custom icon
            icon = QIcon(icon_path)
            self.tray_icon.setIcon(icon)
            self.main_window.setWindowIcon(icon)
        else:
            # Fallback: Use a built-in style icon
            # QSystemTrayIcon requires an icon, so we create a simple one
            from PyQt6.QtGui import QPixmap, QPainter, QColor
            from PyQt6.QtCore import QSize
            
            # Create a simple colored square as fallback
            pixmap = QPixmap(QSize(64, 64))
            pixmap.fill(QColor(65, 105, 225))  # Royal Blue
            
            painter = QPainter(pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(painter.font())
            font = painter.font()
            font.setPointSize(32)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "M")
            painter.end()
            
            icon = QIcon(pixmap)
            self.tray_icon.setIcon(icon)
            self.main_window.setWindowIcon(icon)
    
    def _create_menu(self) -> QMenu:
        """
        Create the system tray context menu with all actions.
        
        Menu Structure:
            - Open App
            - Refresh Now
            - ───────────────
            - Start Scheduler
            - Stop Scheduler
            - ───────────────
            - Exit
        
        Returns:
            QMenu: The configured context menu
        """
        menu = QMenu()
        
        # Action 1: Open App
        self.action_open = QAction("🔓 Open App", self.main_window)
        self.action_open.triggered.connect(self._handle_open_app)
        menu.addAction(self.action_open)
        
        # Action 2: Refresh Now
        self.action_refresh = QAction("⚡ Refresh Now", self.main_window)
        self.action_refresh.triggered.connect(self._handle_refresh_now)
        menu.addAction(self.action_refresh)
        
        # Separator
        menu.addSeparator()
        
        # Action 3: Start Scheduler
        self.action_start_scheduler = QAction("▶️ Start Scheduler", self.main_window)
        self.action_start_scheduler.triggered.connect(self._handle_start_scheduler)
        menu.addAction(self.action_start_scheduler)
        
        # Action 4: Stop Scheduler
        self.action_stop_scheduler = QAction("⏸️ Stop Scheduler", self.main_window)
        self.action_stop_scheduler.triggered.connect(self._handle_stop_scheduler)
        self.action_stop_scheduler.setEnabled(False)  # Initially disabled
        menu.addAction(self.action_stop_scheduler)
        
        # Separator
        menu.addSeparator()
        
        # Action 5: Exit
        self.action_exit = QAction("❌ Exit", self.main_window)
        self.action_exit.triggered.connect(self._handle_exit)
        menu.addAction(self.action_exit)
        
        return menu
    
    def _setup_close_behavior(self) -> None:
        """
        Setup minimize-to-tray behavior by overriding the main window's close event.
        
        This method patches the main window's closeEvent to intercept
        the close action and hide to tray instead of exiting.
        
        Implementation:
            - Save original closeEvent
            - Replace with custom handler
            - Delegate to original when needed
        """
        # Store original closeEvent
        original_close_event = self.main_window.closeEvent
        
        def custom_close_event(event):
            """
            Custom close event handler that minimizes to tray.
            
            Args:
                event: QCloseEvent instance
            """
            # Hide window instead of closing
            event.ignore()
            self.main_window.hide()
            
            # Show notification
            self.show_notification(
                "Master Refreshing App",
                "Application minimized to system tray. Double-click the tray icon to restore.",
                QSystemTrayIcon.MessageIcon.Information
            )
        
        # Replace closeEvent with our custom handler
        self.main_window.closeEvent = custom_close_event
        
        # Store original for potential future use
        self.main_window._original_close_event = original_close_event
    
    def _on_icon_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """
        Handle system tray icon activation (clicks).
        
        Args:
            reason: QSystemTrayIcon.ActivationReason enum value
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.restore_window()
    
    def restore_window(self) -> None:
        """
        Restore the main window from tray.
        
        Operations:
            1. Show the window
            2. Restore from minimized state if needed
            3. Bring to front
            4. Activate (give focus)
            5. Raise above other windows
        
        This ensures consistent behavior across multiple hide/restore cycles.
        """
        # Show window
        self.main_window.show()
        
        # Restore from minimized state
        if self.main_window.isMinimized():
            self.main_window.showNormal()
        
        # Bring to front and activate
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    # ═══════════════════════════════════════════════════════════════
    # Action Handlers (delegate to callbacks)
    # ═══════════════════════════════════════════════════════════════
    
    def _handle_open_app(self) -> None:
        """
        Handle "Open App" action.
        
        Simply restores the main window to visible state.
        """
        self.restore_window()
    
    def _handle_refresh_now(self) -> None:
        """
        Handle "Refresh Now" action.
        
        Delegates to the provided callback. If no callback is registered,
        logs a warning.
        """
        if self.callbacks['refresh_now']:
            self.callbacks['refresh_now']()
        else:
            print("[WARNING] Tray: No callback registered for 'refresh_now'")
    
    def _handle_start_scheduler(self) -> None:
        """
        Handle "Start Scheduler" action.
        
        Delegates to the provided callback and updates menu state.
        """
        if self.callbacks['start_scheduler']:
            self.callbacks['start_scheduler']()
            # Update menu state (will be called back by main window)
        else:
            print("[WARNING] Tray: No callback registered for 'start_scheduler'")
    
    def _handle_stop_scheduler(self) -> None:
        """
        Handle "Stop Scheduler" action.
        
        Delegates to the provided callback and updates menu state.
        """
        if self.callbacks['stop_scheduler']:
            self.callbacks['stop_scheduler']()
            # Update menu state (will be called back by main window)
        else:
            print("[WARNING] Tray: No callback registered for 'stop_scheduler'")
    
    def _handle_exit(self) -> None:
        """
        Handle "Exit" action.
        
        This is the proper way to exit the application (not minimize to tray).
        Delegates to the provided callback for cleanup operations.
        """
        if self.callbacks['exit_app']:
            self.callbacks['exit_app']()
        else:
            # Fallback: direct quit
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app is not None:
                app.quit()
    
    # ═══════════════════════════════════════════════════════════════
    # Public API Methods
    # ═══════════════════════════════════════════════════════════════
    
    def show(self) -> None:
        """
        Show the system tray icon.
        
        Must be called after initialization to make the tray icon visible.
        """
        self.tray_icon.show()
    
    def hide(self) -> None:
        """
        Hide the system tray icon.
        
        Use this if you want to temporarily remove the tray icon
        without destroying the object.
        """
        self.tray_icon.hide()
    
    def show_notification(self, 
                         title: str, 
                         message: str, 
                         icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information,
                         duration: int = 3000) -> None:
        """
        Display a system tray notification (balloon tip).
        
        Args:
            title: Notification title
            message: Notification message body
            icon: Icon type (Information, Warning, Critical, NoIcon)
            duration: Display duration in milliseconds (default: 3000ms = 3s)
        
        Note:
            Notification appearance and behavior depends on the operating system.
            Windows 10/11 shows notifications in the Action Center.
        
        Example:
            tray.show_notification(
                "Refresh Complete",
                "All Excel files have been refreshed successfully.",
                QSystemTrayIcon.MessageIcon.Information
            )
        """
        if self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, duration)
    
    def update_scheduler_state(self, is_running: bool) -> None:
        """
        Update the menu actions based on scheduler state.
        
        This method should be called by the main window whenever
        the scheduler state changes.
        
        Args:
            is_running: True if scheduler is running, False otherwise
        
        Behavior:
            - If running: Enable "Stop", Disable "Start"
            - If stopped: Enable "Start", Disable "Stop"
        """
        self._scheduler_running = is_running
        
        # Update menu item states
        self.action_start_scheduler.setEnabled(not is_running)
        self.action_stop_scheduler.setEnabled(is_running)
        
        # Update action text to show current state
        if is_running:
            self.action_stop_scheduler.setText("⏸️ Stop Scheduler (Running)")
        else:
            self.action_start_scheduler.setText("▶️ Start Scheduler (Stopped)")
    
    def set_tooltip(self, tooltip: str) -> None:
        """
        Update the tray icon tooltip text.
        
        Args:
            tooltip: New tooltip text
        
        Example:
            tray.set_tooltip("Master Refreshing App - Next refresh: 06:00 AM")
        """
        self.tray_icon.setToolTip(tooltip)
    
    def is_visible(self) -> bool:
        """
        Check if the tray icon is currently visible.
        
        Returns:
            True if visible, False otherwise
        """
        return self.tray_icon.isVisible()
    
    # ═══════════════════════════════════════════════════════════════
    # Future Enhancement Placeholders
    # ═══════════════════════════════════════════════════════════════
    
    def notify_refresh_started(self, file_count: int) -> None:
        """
        Placeholder: Notify that refresh has started.
        
        Args:
            file_count: Number of files being refreshed
        
        Future Implementation:
            Show notification with progress indication
        """
        # self.show_notification(
        #     "Refresh Started",
        #     f"Refreshing {file_count} Excel file(s)...",
        #     QSystemTrayIcon.MessageIcon.Information
        # )
        pass
    
    def notify_refresh_completed(self, succeeded: int, failed: int) -> None:
        """
        Placeholder: Notify that refresh has completed.
        
        Args:
            succeeded: Number of files refreshed successfully
            failed: Number of files that failed
        
        Future Implementation:
            Show notification with results summary
        """
        # if failed == 0:
        #     self.show_notification(
        #         "Refresh Complete",
        #         f"Successfully refreshed {succeeded} file(s).",
        #         QSystemTrayIcon.MessageIcon.Information
        #     )
        # else:
        #     self.show_notification(
        #         "Refresh Complete",
        #         f"Refreshed {succeeded} file(s), {failed} failed.",
        #         QSystemTrayIcon.MessageIcon.Warning
        #     )
        pass
    
    def notify_scheduler_triggered(self) -> None:
        """
        Placeholder: Notify that scheduled refresh was triggered.
        
        Future Implementation:
            Show notification when scheduler executes
        """
        # self.show_notification(
        #     "Scheduled Refresh",
        #     "Daily refresh is now running...",
        #     QSystemTrayIcon.MessageIcon.Information
        # )
        pass
    
    def __repr__(self) -> str:
        """String representation of SystemTrayManager."""
        status = "visible" if self.is_visible() else "hidden"
        scheduler_status = "running" if self._scheduler_running else "stopped"
        return f"SystemTrayManager(status={status}, scheduler={scheduler_status})"


# ═══════════════════════════════════════════════════════════════════
# Integration Documentation and Usage Examples
# ═══════════════════════════════════════════════════════════════════

"""
INTEGRATION GUIDE
═════════════════

1. Basic Integration in MainWindow
───────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Initialize system tray
        self.tray_manager = SystemTrayManager(
            main_window=self,
            on_refresh_now=self.handle_manual_refresh,
            on_start_scheduler=self.handle_start_scheduler,
            on_stop_scheduler=self.handle_stop_scheduler,
            on_exit_app=self.handle_exit
        )
        self.tray_manager.show()
    
    def handle_manual_refresh(self):
        # Trigger your refresh logic here
        print("Manual refresh triggered from tray")
        # self.refresh_engine.refresh_all_files()
    
    def handle_start_scheduler(self):
        # Start your scheduler
        print("Starting scheduler from tray")
        # self.scheduler.start()
        self.tray_manager.update_scheduler_state(True)
    
    def handle_stop_scheduler(self):
        # Stop your scheduler
        print("Stopping scheduler from tray")
        # self.scheduler.stop()
        self.tray_manager.update_scheduler_state(False)
    
    def handle_exit(self):
        # Cleanup and exit
        print("Exiting application")
        # self.scheduler.stop()
        # self.config.save()
        QApplication.instance().quit()


2. Updating Tray State
───────────────────────

# After scheduler state changes:
self.tray_manager.update_scheduler_state(is_running=True)

# Update tooltip dynamically:
next_run = scheduler.get_next_run_time()
self.tray_manager.set_tooltip(f"Next refresh: {next_run}")


3. Showing Notifications
─────────────────────────

# Manual notification:
self.tray_manager.show_notification(
    "Operation Complete",
    "All files processed successfully.",
    QSystemTrayIcon.MessageIcon.Information
)

# Future: Use built-in notification methods:
# self.tray_manager.notify_refresh_completed(succeeded=5, failed=0)


4. Icon File Setup
──────────────────

Create a 64x64 PNG icon and place it at:
    resources/icon.png

If the file doesn't exist, a fallback icon will be generated automatically.


5. Testing Without Main Window
───────────────────────────────

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow
    import sys
    
    app = QApplication(sys.argv)
    
    # Create a dummy window
    window = QMainWindow()
    window.setWindowTitle("Tray Test")
    window.resize(400, 300)
    
    # Initialize tray
    tray = SystemTrayManager(
        main_window=window,
        on_refresh_now=lambda: print("Refresh triggered"),
        on_start_scheduler=lambda: print("Scheduler started"),
        on_stop_scheduler=lambda: print("Scheduler stopped"),
        on_exit_app=lambda: app.quit()
    )
    tray.show()
    
    window.show()
    sys.exit(app.exec())


NOTES
═════

- The tray icon will remain active even when the window is hidden
- Double-click the tray icon to restore the window
- Close button (X) will minimize to tray, not exit
- Use the "Exit" menu item to actually quit the application
- All business logic is delegated through callbacks
- No imports of other application modules (clean separation)

"""
