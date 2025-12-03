"""
integrity_ui.py - Integrity Details Inspection Window

Purpose:
    Professional UI window for displaying detailed integrity verification results.
    Shows a comprehensive table of all monitored files with hash comparison,
    status indicators, and interactive refresh functionality.
    
    Features:
    - Detailed file-by-file integrity table
    - Color-coded status indicators (✓ ✗ ⚠)
    - Real-time refresh button
    - Summary statistics panel
    - Full hash display with truncation
    - Tooltip support for full paths
    - Modern responsive design
    
Author: ENG. Saeed Al-moghrabi
Version: 1.0.0 - Production Ready
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QGroupBox, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import Optional, Callable


class IntegrityDetailsWindow(QDialog):
    """
    Detailed integrity inspection window.
    
    This window displays comprehensive integrity verification results
    including file-by-file hash comparison and status indicators.
    """
    
    def __init__(self, parent=None, integrity_checker=None):
        """
        Initialize the integrity details window.
        
        Args:
            parent: Parent widget (usually MainWindow)
            integrity_checker: IntegrityChecker instance for verification
        """
        super().__init__(parent)
        
        self.integrity_checker = integrity_checker
        self.report = None
        
        self.setup_window()
        self.setup_ui()
        self.load_integrity_data()
    
    def setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Integrity Verification Details")
        self.setGeometry(150, 150, 1000, 600)
        self.setMinimumSize(800, 500)
        
        # Make it modal
        self.setModal(True)
    
    def setup_ui(self):
        """Build the complete UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("🔒 Application Integrity Verification")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        
        # Summary panel
        self.summary_group = self.create_summary_panel()
        main_layout.addWidget(self.summary_group)
        
        # Files table
        table_label = QLabel("Detailed File Integrity Status:")
        table_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        main_layout.addWidget(table_label)
        
        self.files_table = self.create_files_table()
        main_layout.addWidget(self.files_table)
        
        # Button panel
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Auto-generate button (developer mode)
        self.auto_generate_btn = QPushButton("🔧 Auto-Generate Manifest")
        self.auto_generate_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.auto_generate_btn.setMinimumHeight(40)
        self.auto_generate_btn.setStyleSheet("background-color: #FFA500; color: white;")
        self.auto_generate_btn.clicked.connect(self.handle_auto_generate)
        self.auto_generate_btn.setToolTip("Developer only: Auto-generate manifest with current file hashes")
        button_layout.addWidget(self.auto_generate_btn)
        
        button_layout.addStretch()
        
        # Refresh button
        self.refresh_btn = QPushButton("🔄 Re-run Integrity Check")
        self.refresh_btn.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.refresh_btn.setMinimumHeight(40)
        self.refresh_btn.clicked.connect(self.handle_refresh)
        button_layout.addWidget(self.refresh_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFont(QFont("Segoe UI", 10))
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        main_layout.addLayout(button_layout)
    
    def create_summary_panel(self) -> QGroupBox:
        """Create the summary statistics panel."""
        group = QGroupBox("Verification Summary")
        group.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Status label
        self.status_label = QLabel("Status: Unknown")
        self.status_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(QLabel("Overall Status:"), 0, 0)
        layout.addWidget(self.status_label, 0, 1)
        
        # Total files
        self.total_files_label = QLabel("0")
        self.total_files_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(QLabel("Total Files Monitored:"), 1, 0)
        layout.addWidget(self.total_files_label, 1, 1)
        
        # Matched files
        self.matched_label = QLabel("0")
        self.matched_label.setFont(QFont("Segoe UI", 10))
        self.matched_label.setStyleSheet("color: #50C878; font-weight: bold;")
        layout.addWidget(QLabel("✓ Matched:"), 2, 0)
        layout.addWidget(self.matched_label, 2, 1)
        
        # Mismatched files
        self.mismatched_label = QLabel("0")
        self.mismatched_label.setFont(QFont("Segoe UI", 10))
        self.mismatched_label.setStyleSheet("color: #FFA500; font-weight: bold;")
        layout.addWidget(QLabel("✗ Modified:"), 3, 0)
        layout.addWidget(self.mismatched_label, 3, 1)
        
        # Missing files
        self.missing_label = QLabel("0")
        self.missing_label.setFont(QFont("Segoe UI", 10))
        self.missing_label.setStyleSheet("color: #DC3545; font-weight: bold;")
        layout.addWidget(QLabel("⚠ Missing:"), 4, 0)
        layout.addWidget(self.missing_label, 4, 1)
        
        # Verification time
        self.time_label = QLabel("0.0 ms")
        self.time_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(QLabel("Verification Time:"), 5, 0)
        layout.addWidget(self.time_label, 5, 1)
        
        # Last generated timestamp
        self.last_generated_label = QLabel("N/A")
        self.last_generated_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(QLabel("Last Manifest Generation:"), 6, 0)
        layout.addWidget(self.last_generated_label, 6, 1)
        
        # Generation mode
        self.generation_mode_label = QLabel("N/A")
        self.generation_mode_label.setFont(QFont("Segoe UI", 10))
        layout.addWidget(QLabel("Generation Mode:"), 7, 0)
        layout.addWidget(self.generation_mode_label, 7, 1)
        
        return group
    
    def create_files_table(self) -> QTableWidget:
        """Create the files integrity table."""
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Status", "File Name", "Stored Hash", "Current Hash", "Match"
        ])
        
        # Configure table
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Hide vertical header
        v_header = table.verticalHeader()
        if v_header:
            v_header.setVisible(False)
        
        # Set column widths
        header = table.horizontalHeader()
        if header:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Status
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # File Name
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Stored Hash
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Current Hash
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Match
        
        # Set font
        table.setFont(QFont("Consolas", 9))
        
        return table
    
    def load_integrity_data(self):
        """Load and display integrity verification data."""
        if not self.integrity_checker:
            QMessageBox.warning(
                self,
                "No Integrity Checker",
                "Integrity checker is not available."
            )
            return
        
        # Get detailed report
        self.report = self.integrity_checker.get_detailed_report()
        
        # Update summary
        self.update_summary(self.report)
        
        # Update table
        self.update_files_table(self.report)
    
    def update_summary(self, report: dict):
        """Update the summary panel with report data."""
        # Overall status
        status_text = report["overall_status"].upper()
        if report["overall_status"] == "verified":
            self.status_label.setText(f"✓ {status_text}")
            self.status_label.setStyleSheet("color: #50C878; font-weight: bold;")
        elif report["overall_status"] == "tampered":
            self.status_label.setText(f"✗ {status_text}")
            self.status_label.setStyleSheet("color: #DC3545; font-weight: bold;")
        else:
            self.status_label.setText(f"⚠ {status_text}")
            self.status_label.setStyleSheet("color: #FFA500; font-weight: bold;")
        
        # Statistics
        self.total_files_label.setText(str(report["total_files"]))
        self.matched_label.setText(str(report["matched"]))
        self.mismatched_label.setText(str(report["mismatched"]))
        self.missing_label.setText(str(report["missing"]))
        self.time_label.setText(f"{report['verification_time_ms']:.1f} ms")
        
        # Manifest metadata
        self.last_generated_label.setText(report.get("last_generated", "N/A"))
        mode = report.get("generation_mode", "N/A")
        mode_display = {
            "manual": "Manual (Developer Tool)",
            "auto": "Auto (Developer Trigger)",
            "cli": "CLI (--generate-manifest)"
        }.get(mode, mode)
        self.generation_mode_label.setText(mode_display)
    
    def update_files_table(self, report: dict):
        """Update the files table with detailed file data."""
        files = report.get("files", [])
        
        self.files_table.setRowCount(len(files))
        
        for row, file_data in enumerate(files):
            # Status icon
            status = file_data["status"]
            if status == "match":
                status_icon = "✓"
                status_color = QColor(80, 200, 120)  # Green
            elif status == "modified":
                status_icon = "✗"
                status_color = QColor(255, 165, 0)  # Orange
            elif status == "missing":
                status_icon = "⚠"
                status_color = QColor(220, 53, 69)  # Red
            else:
                status_icon = "?"
                status_color = QColor(150, 150, 150)  # Gray
            
            status_item = QTableWidgetItem(status_icon)
            status_item.setForeground(status_color)
            status_item.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.files_table.setItem(row, 0, status_item)
            
            # File name
            name_item = QTableWidgetItem(file_data["name"])
            name_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            name_item.setToolTip(file_data["path"])
            self.files_table.setItem(row, 1, name_item)
            
            # Stored hash (truncated)
            stored_hash = file_data["stored_hash"]
            stored_display = f"{stored_hash[:16]}...{stored_hash[-8:]}" if len(stored_hash) > 32 else stored_hash
            stored_item = QTableWidgetItem(stored_display)
            stored_item.setToolTip(f"Full hash: {stored_hash}")
            stored_item.setFont(QFont("Consolas", 8))
            self.files_table.setItem(row, 2, stored_item)
            
            # Current hash (truncated)
            current_hash = file_data["current_hash"]
            if current_hash in ["N/A", "Error"]:
                current_display = current_hash
            else:
                current_display = f"{current_hash[:16]}...{current_hash[-8:]}" if len(current_hash) > 32 else current_hash
            
            current_item = QTableWidgetItem(current_display)
            current_item.setToolTip(f"Full hash: {current_hash}")
            current_item.setFont(QFont("Consolas", 8))
            
            if status != "match":
                current_item.setForeground(status_color)
            
            self.files_table.setItem(row, 3, current_item)
            
            # Match indicator
            if status == "match":
                match_text = "Yes"
                match_color = QColor(80, 200, 120)
            else:
                match_text = "No"
                match_color = status_color
            
            match_item = QTableWidgetItem(match_text)
            match_item.setForeground(match_color)
            match_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            match_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.files_table.setItem(row, 4, match_item)
    
    def handle_auto_generate(self):
        """Handle auto-generate manifest button click (Developer mode)."""
        if not self.integrity_checker:
            return
        
        # Confirm action
        reply = QMessageBox.warning(
            self,
            "⚠️ Developer Action",
            "This will regenerate the integrity manifest with CURRENT file hashes.\n\n"
            "⚠️ WARNING: Only use if you've intentionally modified code files.\n"
            "⚠️ This will disable detection of any tampering that has occurred.\n\n"
            "🔧 Developer mode - Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable button
        self.auto_generate_btn.setEnabled(False)
        self.auto_generate_btn.setText("⏳ Generating...")
        
        try:
            # Generate manifest
            elapsed_ms = self.integrity_checker.generate_manifest(mode="manual")
            
            # Re-run verification
            self.integrity_checker.verify_integrity()
            
            # Reload data
            self.load_integrity_data()
            
            # Show success
            QMessageBox.information(
                self,
                "✓ Manifest Generated",
                f"Integrity manifest regenerated successfully!\n\n"
                f"Generation time: {elapsed_ms:.1f}ms\n"
                f"Files hashed: {self.report['total_files']}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Generation Failed",
                f"Failed to generate manifest:\n\n{str(e)}"
            )
        
        finally:
            # Re-enable button
            self.auto_generate_btn.setEnabled(True)
            self.auto_generate_btn.setText("🔧 Auto-Generate Manifest")
    
    def handle_refresh(self):
        """Handle refresh button click."""
        if not self.integrity_checker:
            return
        
        # Disable button during refresh
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("⏳ Verifying...")
        
        # Re-run verification
        self.integrity_checker.verify_integrity()
        
        # Reload data
        self.load_integrity_data()
        
        # Re-enable button
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("🔄 Re-run Integrity Check")
        
        # Show message
        if self.report:
            if self.report["overall_status"] == "verified":
                QMessageBox.information(
                    self,
                    "Verification Complete",
                    f"All {self.report['total_files']} files verified successfully!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Integrity Issues Detected",
                    f"Found {self.report['mismatched']} modified and {self.report['missing']} missing files."
                )
