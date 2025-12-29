"""
settings_dialog.py - Application Settings Dialog

Purpose:
    Settings dialog for configuring application parameters.
    Currently supports log directory configuration only.
    
    Features:
    - Log directory path selection
    - Browse button with folder picker
    - Validation for directory existence
    - Save/Cancel buttons
    - Clean, user-friendly interface

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
from typing import Optional
from config_handler import ConfigHandler


class SettingsDialog(QDialog):
    """
    Settings configuration dialog.
    
    Provides interface for configuring:
    - Log directory path (with browse button)
    
    Features:
        - Directory validation
        - Browse dialog integration
        - Save/Cancel buttons
        - Automatic config persistence
    """
    
    def __init__(self, config: ConfigHandler, parent=None):
        """
        Initialize settings dialog.
        
        Args:
            config: ConfigHandler instance for reading/writing settings
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Application Settings")
        self.setModal(True)
        self.resize(500, 200)
        
        self._setup_ui()
        self._load_current_settings()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Application Settings")
        title_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Log Directory Group
        log_group = QGroupBox("Log Directory")
        log_layout = QVBoxLayout(log_group)
        log_layout.setSpacing(10)
        
        # Description
        desc = QLabel("Specify where application logs should be saved:")
        desc.setWordWrap(True)
        log_layout.addWidget(desc)
        
        # Path input with browse button
        path_layout = QHBoxLayout()
        path_layout.setSpacing(5)
        
        self.log_path_edit = QLineEdit()
        self.log_path_edit.setPlaceholderText("Leave empty for default location (logs/ folder)")
        path_layout.addWidget(self.log_path_edit)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.setFixedWidth(100)
        self.browse_btn.clicked.connect(self._browse_log_directory)
        path_layout.addWidget(self.browse_btn)
        
        log_layout.addLayout(path_layout)
        
        # Note
        note = QLabel("Note: Changes will take effect after application restart.")
        note.setStyleSheet("color: #888888; font-style: italic;")
        note.setWordWrap(True)
        log_layout.addWidget(note)
        
        layout.addWidget(log_group)
        
        # Spacer
        layout.addStretch()
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setFixedWidth(100)
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._save_settings)
        buttons_layout.addWidget(self.save_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_current_settings(self):
        """Load current settings from config."""
        log_dir = self.config.get_log_directory()
        if log_dir:
            self.log_path_edit.setText(log_dir)
    
    def _browse_log_directory(self):
        """Open folder picker dialog."""
        current_path = self.log_path_edit.text().strip()
        
        # Use current path as starting directory if valid
        start_dir = current_path if current_path and os.path.isdir(current_path) else ""
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Log Directory",
            start_dir,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if directory:
            self.log_path_edit.setText(directory)
    
    def _save_settings(self):
        """Validate and save settings."""
        log_path = self.log_path_edit.text().strip()
        
        # Validate log directory if provided
        if log_path:
            if not os.path.isdir(log_path):
                QMessageBox.warning(
                    self,
                    "Invalid Directory",
                    f"The specified directory does not exist:\n{log_path}\n\n"
                    "Please select a valid directory or leave empty for default."
                )
                return
        
        # Save to config (empty string becomes None)
        self.config.set_log_directory(log_path if log_path else None)
        
        # Show success message
        QMessageBox.information(
            self,
            "Settings Saved",
            "Settings have been saved successfully.\n"
            "Please restart the application for changes to take effect."
        )
        
        self.accept()
