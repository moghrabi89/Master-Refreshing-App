"""
theme.py - UI Theme and Stylesheet Manager

Purpose:
    Centralized theming system for Master Refreshing App.
    Provides complete QSS (Qt Style Sheets) for modern, professional UI design
    with gradient backgrounds, smooth animations, and consistent styling.
    
    Features:
    - Centralized color palette
    - Complete QSS stylesheet generation
    - Component-specific styling
    - Modern design elements (gradients, rounded corners, shadows)
    - Smooth hover effects and transitions
    - Dark theme with high contrast
    - Consistent visual language

Author: ENG. Saeed Al-moghrabi
Version: 1.0.0
"""

from typing import Dict, Optional


class ThemeManager:
    """
    Professional theme manager for Master Refreshing App.
    
    This class centralizes all UI styling and theming, providing:
    - Color palette management
    - Complete QSS stylesheet generation
    - Component-specific styling methods
    - Modern design patterns
    
    Design Philosophy:
        - Dark theme for reduced eye strain
        - High contrast for readability
        - Gradient accents for modern feel
        - Smooth transitions for polish
        - Consistent spacing and sizing
    """
    
    # ═══════════════════════════════════════════════════════════════
    # Color Palette
    # ═══════════════════════════════════════════════════════════════
    
    # Primary Colors
    ROYAL_BLUE = '#4169E1'
    TEAL = '#008080'
    EMERALD = '#50C878'
    NEON_BLUE = '#00FFFF'
    
    # Background Colors
    BG_DARKEST = '#1A1A1A'
    BG_DARK = '#1E1E1E'
    BG_MEDIUM = '#252525'
    BG_LIGHT = '#2D2D2D'
    BG_LIGHTER = '#3A3A3A'
    
    # Text Colors
    TEXT_WHITE = '#FFFFFF'
    TEXT_LIGHT = '#E0E0E0'
    TEXT_GRAY = '#AAAAAA'
    TEXT_DARK_GRAY = '#666666'
    
    # Status Colors
    SUCCESS_GREEN = '#50C878'
    ERROR_RED = '#DC3545'
    WARNING_ORANGE = '#FFA500'
    INFO_BLUE = '#4169E1'
    
    # Accent Colors
    ACCENT_PRIMARY = ROYAL_BLUE
    ACCENT_SECONDARY = TEAL
    ACCENT_TERTIARY = EMERALD
    
    def __init__(self):
        """Initialize the theme manager."""
        self.current_theme = "modern_dark"
    
    def get_complete_stylesheet(self) -> str:
        """
        Generate the complete application stylesheet.
        
        Returns:
            str: Complete QSS stylesheet
        """
        return f"""
            /* ═══════════════════════════════════════════════════════════════ */
            /* MASTER REFRESHING APP - MODERN DARK THEME                         */
            /* ═══════════════════════════════════════════════════════════════ */
            
            /* ===== GLOBAL STYLES ===== */
            QMainWindow {{
                background-color: {self.BG_DARK};
            }}
            
            QWidget {{
                background-color: {self.BG_DARK};
                color: {self.TEXT_WHITE};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }}
            
            /* ===== HEADER BANNER ===== */
            QFrame#headerFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ROYAL_BLUE},
                    stop:0.5 {self.TEAL},
                    stop:1 {self.EMERALD}
                );
                border: none;
                border-radius: 0px;
            }}
            
            QLabel#titleLabel {{
                color: {self.TEXT_WHITE};
                background: transparent;
                font-size: 24pt;
                font-weight: bold;
            }}
            
            QLabel#subtitleLabel {{
                color: {self.TEXT_LIGHT};
                background: transparent;
                font-size: 11pt;
            }}
            
            /* ===== PANELS AND FRAMES ===== */
            QFrame#fileManagerPanel,
            QFrame#controlsPanel,
            QFrame#logsPanel {{
                background-color: {self.BG_LIGHT};
                border-radius: 12px;
                border: 1px solid {self.BG_LIGHTER};
            }}
            
            QFrame#schedulerFrame,
            QFrame#refreshFrame {{
                background-color: {self.BG_MEDIUM};
                border-radius: 10px;
                border: 1px solid {self.BG_LIGHTER};
            }}
            
            QLabel#panelTitle {{
                color: {self.TEXT_WHITE};
                background: transparent;
                font-size: 14pt;
                font-weight: bold;
            }}
            
            /* ===== BUTTONS ===== */
            QPushButton {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ROYAL_BLUE},
                    stop:1 {self.TEAL}
                );
                color: {self.TEXT_WHITE};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 11pt;
                font-weight: bold;
                min-height: 35px;
            }}
            
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5179F1,
                    stop:1 #009090
                );
            }}
            
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3159D1,
                    stop:1 #007070
                );
            }}
            
            QPushButton:disabled {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_DARK_GRAY};
            }}
            
            QPushButton#refreshNowBtn {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.EMERALD},
                    stop:1 {self.NEON_BLUE}
                );
                font-size: 13pt;
                min-height: 55px;
            }}
            
            QPushButton#refreshNowBtn:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D888,
                    stop:1 #10FFFF
                );
            }}
            
            QPushButton#refreshNowBtn:disabled {{
                background: {self.BG_LIGHTER};
                color: {self.TEXT_DARK_GRAY};
            }}
            
            QPushButton#removeFilesBtn {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ERROR_RED},
                    stop:1 #C82333
                );
            }}
            
            QPushButton#removeFilesBtn:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EC4555,
                    stop:1 #D83343
                );
            }}
            
            /* ===== TABLE WIDGET ===== */
            QTableWidget {{
                background-color: {self.BG_MEDIUM};
                alternate-background-color: #2A2A2A;
                border: 1px solid {self.BG_LIGHTER};
                border-radius: 8px;
                gridline-color: {self.BG_LIGHTER};
                color: {self.TEXT_WHITE};
                selection-background-color: {self.ROYAL_BLUE};
                selection-color: {self.TEXT_WHITE};
            }}
            
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
            
            QTableWidget::item:selected {{
                background-color: {self.ROYAL_BLUE};
                color: {self.TEXT_WHITE};
            }}
            
            QTableWidget::item:hover {{
                background-color: {self.BG_LIGHTER};
            }}
            
            QHeaderView::section {{
                background-color: {self.BG_DARK};
                color: {self.TEXT_WHITE};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {self.ROYAL_BLUE};
                font-weight: bold;
                font-size: 10pt;
            }}
            
            QHeaderView::section:hover {{
                background-color: {self.BG_LIGHT};
            }}
            
            /* ===== TIME EDIT WIDGET ===== */
            QTimeEdit {{
                background-color: {self.BG_MEDIUM};
                border: 2px solid {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 8px;
                color: {self.TEXT_WHITE};
                font-size: 12pt;
                min-height: 35px;
            }}
            
            QTimeEdit:focus {{
                border: 2px solid {self.ROYAL_BLUE};
            }}
            
            QTimeEdit::up-button, QTimeEdit::down-button {{
                background-color: {self.BG_LIGHTER};
                border: none;
                width: 20px;
                border-radius: 4px;
            }}
            
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
                background-color: #4A4A4A;
            }}
            
            QTimeEdit::up-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 5px solid {self.TEXT_WHITE};
                width: 0px;
                height: 0px;
            }}
            
            QTimeEdit::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {self.TEXT_WHITE};
                width: 0px;
                height: 0px;
            }}
            
            /* ===== CHECKBOX WIDGET ===== */
            QCheckBox {{
                background: transparent;
                color: {self.TEXT_WHITE};
                font-size: 11pt;
                spacing: 8px;
                padding: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid {self.BG_LIGHTER};
                background-color: {self.BG_MEDIUM};
            }}
            
            QCheckBox::indicator:hover {{
                border: 2px solid {self.ROYAL_BLUE};
                background-color: {self.BG_LIGHT};
            }}
            
            QCheckBox::indicator:checked {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ROYAL_BLUE},
                    stop:1 {self.TEAL}
                );
                border: 2px solid {self.ROYAL_BLUE};
            }}
            
            QCheckBox::indicator:checked:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5179F1,
                    stop:1 #009090
                );
            }}
            
            QCheckBox::indicator:disabled {{
                background-color: {self.BG_DARKEST};
                border: 2px solid {self.TEXT_DARK_GRAY};
            }}
            
            QCheckBox:disabled {{
                color: {self.TEXT_DARK_GRAY};
            }}
            
            /* ===== PROGRESS BAR ===== */
            QProgressBar {{
                background-color: {self.BG_MEDIUM};
                border: 2px solid {self.BG_LIGHTER};
                border-radius: 10px;
                text-align: center;
                color: {self.TEXT_WHITE};
                font-size: 10pt;
                font-weight: bold;
                min-height: 28px;
            }}
            
            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ROYAL_BLUE},
                    stop:0.5 {self.TEAL},
                    stop:1 {self.EMERALD}
                );
                border-radius: 8px;
                margin: 2px;
            }}
            
            QLabel#progressLabel {{
                color: {self.TEXT_LIGHT};
                background: transparent;
                font-size: 9pt;
                padding: 2px;
            }}
            
            /* ===== TEXT EDIT (LOGS DISPLAY) ===== */
            QTextEdit {{
                background-color: {self.BG_DARKEST};
                border: 1px solid {self.BG_LIGHTER};
                border-radius: 8px;
                padding: 10px;
                color: {self.TEXT_GRAY};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                line-height: 1.4;
            }}
            
            QTextEdit#logsDisplay {{
                background-color: {self.BG_DARKEST};
            }}
            
            /* ===== STATUS BAR ===== */
            QStatusBar {{
                background-color: {self.BG_DARKEST};
                color: {self.TEXT_GRAY};
                border-top: 1px solid {self.BG_LIGHTER};
                font-size: 9pt;
            }}
            
            QStatusBar QLabel {{
                background: transparent;
                color: {self.TEXT_GRAY};
                padding: 4px 8px;
            }}
            
            QLabel#integrityLabel {{
                background: transparent;
                font-weight: bold;
                padding: 4px 10px;
                border-radius: 4px;
            }}
            
            /* ===== LABELS ===== */
            QLabel {{
                background: transparent;
                color: {self.TEXT_WHITE};
            }}
            
            QLabel#schedulerStatus {{
                color: {self.ERROR_RED};
                font-weight: bold;
            }}
            
            QLabel#schedulerStatusRunning {{
                color: {self.SUCCESS_GREEN};
                font-weight: bold;
            }}
            
            /* ===== SCROLLBARS ===== */
            QScrollBar:vertical {{
                background-color: {self.BG_MEDIUM};
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: #4A4A4A;
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: #5A5A5A;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {self.BG_MEDIUM};
                height: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: #4A4A4A;
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: #5A5A5A;
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* ===== MESSAGE BOX ===== */
            QMessageBox {{
                background-color: {self.BG_LIGHT};
                color: {self.TEXT_WHITE};
            }}
            
            QMessageBox QLabel {{
                color: {self.TEXT_WHITE};
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
            }}
            
            /* ===== FILE DIALOG ===== */
            QFileDialog {{
                background-color: {self.BG_LIGHT};
                color: {self.TEXT_WHITE};
            }}
            
            /* ===== TOOLTIPS ===== */
            QToolTip {{
                background-color: {self.BG_LIGHT};
                color: {self.TEXT_WHITE};
                border: 1px solid {self.ROYAL_BLUE};
                border-radius: 4px;
                padding: 5px;
                font-size: 9pt;
            }}
            
            /* ===== MENU (Context Menu for Tray) ===== */
            QMenu {{
                background-color: {self.BG_LIGHT};
                color: {self.TEXT_WHITE};
                border: 1px solid {self.BG_LIGHTER};
                border-radius: 6px;
                padding: 5px;
            }}
            
            QMenu::item {{
                padding: 8px 25px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {self.ROYAL_BLUE};
                color: {self.TEXT_WHITE};
            }}
            
            QMenu::item:disabled {{
                color: {self.TEXT_DARK_GRAY};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {self.BG_LIGHTER};
                margin: 5px 0px;
            }}
        """
    
    def get_color(self, color_name: str) -> str:
        """
        Get a color value by name.
        
        Args:
            color_name: Name of the color constant
        
        Returns:
            str: Hex color value
        """
        return getattr(self, color_name.upper(), self.TEXT_WHITE)
    
    def apply_to_widget(self, widget) -> None:
        """
        Apply the theme stylesheet to a widget.
        
        Args:
            widget: QWidget to apply stylesheet to
        """
        widget.setStyleSheet(self.get_complete_stylesheet())
    
    def __repr__(self) -> str:
        """String representation of ThemeManager."""
        return f"ThemeManager(theme='{self.current_theme}')"


# Global theme instance
_theme_instance: Optional[ThemeManager] = None


def get_theme() -> ThemeManager:
    """
    Get the global theme manager instance.
    
    Returns:
        ThemeManager: The singleton theme instance
    """
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = ThemeManager()
    return _theme_instance


# Test code
if __name__ == "__main__":
    theme = get_theme()
    print(theme)
    print("\n=== Color Palette ===")
    print(f"Royal Blue: {theme.ROYAL_BLUE}")
    print(f"Teal: {theme.TEAL}")
    print(f"Emerald: {theme.EMERALD}")
    print(f"Success Green: {theme.SUCCESS_GREEN}")
    print(f"Error Red: {theme.ERROR_RED}")
    print("\n=== Stylesheet Generated ===")
    stylesheet = theme.get_complete_stylesheet()
    print(f"Stylesheet length: {len(stylesheet)} characters")
    print("\nTheme ready for application!")
