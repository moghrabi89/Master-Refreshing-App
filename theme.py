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
    
    # Background Colors (Dark Mode)
    BG_DARKEST = '#1A1A1A'
    BG_DARK = '#1E1E1E'
    BG_MEDIUM = '#252525'
    BG_LIGHT = '#2D2D2D'
    BG_LIGHTER = '#3A3A3A'
    
    # Background Colors (Light Mode)
    BG_LIGHT_WHITE = '#FFFFFF'
    BG_LIGHT_LIGHT = '#F5F5F5'
    BG_LIGHT_MEDIUM = '#E8E8E8'
    BG_LIGHT_DARK = '#D0D0D0'
    BG_LIGHT_DARKER = '#B0B0B0'
    
    # Text Colors (Dark Mode)
    TEXT_WHITE = '#FFFFFF'
    TEXT_LIGHT = '#E0E0E0'
    TEXT_GRAY = '#AAAAAA'
    TEXT_DARK_GRAY = '#666666'
    
    # Text Colors (Light Mode)
    TEXT_DARK = '#1A1A1A'
    TEXT_DARK_LIGHT = '#333333'
    TEXT_DARK_MEDIUM = '#555555'
    TEXT_DARK_GRAY_LIGHT = '#777777'
    
    # Status Colors
    SUCCESS_GREEN = '#50C878'
    ERROR_RED = '#DC3545'
    WARNING_ORANGE = '#FFA500'
    INFO_BLUE = '#4169E1'
    
    # Accent Colors
    ACCENT_PRIMARY = ROYAL_BLUE
    ACCENT_SECONDARY = TEAL
    ACCENT_TERTIARY = EMERALD
    
    def __init__(self, theme_mode: str = "dark"):
        """
        Initialize the theme manager.
        
        Args:
            theme_mode: Theme mode - "dark" or "light" (default: "dark")
        """
        self.current_theme = theme_mode
        self.set_theme_mode(theme_mode)
    
    def set_theme_mode(self, mode: str) -> None:
        """
        Set the theme mode (dark or light).
        
        Args:
            mode: "dark" or "light"
        """
        if mode.lower() in ["dark", "light"]:
            self.current_theme = mode.lower()
        else:
            self.current_theme = "dark"  # Default to dark
    
    def get_current_colors(self) -> Dict[str, str]:
        """
        Get current color palette based on theme mode.
        
        Returns:
            Dictionary of color values for current theme
        """
        if self.current_theme == "light":
            return {
                "bg_main": self.BG_LIGHT_WHITE,
                "bg_secondary": self.BG_LIGHT_LIGHT,
                "bg_tertiary": self.BG_LIGHT_MEDIUM,
                "bg_quaternary": self.BG_LIGHT_DARK,
                "bg_quinary": self.BG_LIGHT_DARKER,
                "text_primary": self.TEXT_DARK,
                "text_secondary": self.TEXT_DARK_LIGHT,
                "text_tertiary": self.TEXT_DARK_MEDIUM,
                "text_quaternary": self.TEXT_DARK_GRAY_LIGHT,
            }
        else:  # dark mode (default)
            return {
                "bg_main": self.BG_DARK,
                "bg_secondary": self.BG_LIGHT,
                "bg_tertiary": self.BG_MEDIUM,
                "bg_quaternary": self.BG_LIGHTER,
                "bg_quinary": self.BG_DARKEST,
                "text_primary": self.TEXT_WHITE,
                "text_secondary": self.TEXT_LIGHT,
                "text_tertiary": self.TEXT_GRAY,
                "text_quaternary": self.TEXT_DARK_GRAY,
            }
    
    def get_complete_stylesheet(self) -> str:
        """
        Generate the complete application stylesheet based on current theme mode.
        
        Returns:
            str: Complete QSS stylesheet
        """
        colors = self.get_current_colors()
        theme_name = "DARK" if self.current_theme == "dark" else "LIGHT"
        
        return f"""
            /* ═══════════════════════════════════════════════════════════════ */
            /* MASTER REFRESHING APP - MODERN {theme_name} THEME                         */
            /* ═══════════════════════════════════════════════════════════════ */
            
            /* ===== GLOBAL STYLES ===== */
            QMainWindow {{
                background-color: {colors['bg_main']};
            }}
            
            QWidget {{
                background-color: {colors['bg_main']};
                color: {colors['text_primary']};
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
                background-color: {colors['bg_secondary']};
                border-radius: 12px;
                border: 1px solid {colors['bg_quaternary']};
            }}
            
            QFrame#schedulerFrame,
            QFrame#refreshFrame {{
                background-color: {colors['bg_tertiary']};
                border-radius: 10px;
                border: 1px solid {colors['bg_quaternary']};
            }}
            
            QLabel#panelTitle {{
                color: {colors['text_primary']};
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
                background: {colors['bg_quaternary']};
                color: {colors['text_quaternary']};
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
                background: {colors['bg_quaternary']};
                color: {colors['text_quaternary']};
            }}
            
            QPushButton#stopRefreshBtn {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.ERROR_RED},
                    stop:1 #C82333
                );
                font-size: 13pt;
                min-height: 55px;
                color: white;
            }}
            
            QPushButton#stopRefreshBtn:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E63946,
                    stop:1 #DC143C
                );
            }}
            
            QPushButton#stopRefreshBtn:disabled {{
                background: {colors['bg_quaternary']};
                color: {colors['text_quaternary']};
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
                background-color: {colors['bg_tertiary']};
                alternate-background-color: {colors['bg_secondary']};
                border: 1px solid {colors['bg_quaternary']};
                border-radius: 8px;
                gridline-color: {colors['bg_quaternary']};
                color: {colors['text_primary']};
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
                background-color: {colors['bg_quaternary']};
            }}
            
            QHeaderView::section {{
                background-color: {colors['bg_main']};
                color: {colors['text_primary']};
                padding: 8px;
                border: none;
                border-bottom: 2px solid {self.ROYAL_BLUE};
                font-weight: bold;
                font-size: 10pt;
            }}
            
            QHeaderView::section:hover {{
                background-color: {colors['bg_secondary']};
            }}
            
            /* ===== TIME EDIT WIDGET ===== */
            QTimeEdit {{
                background-color: {colors['bg_tertiary']};
                border: 2px solid {colors['bg_quaternary']};
                border-radius: 8px;
                padding: 8px;
                color: {colors['text_primary']};
                font-size: 12pt;
                min-height: 35px;
            }}
            
            QTimeEdit:focus {{
                border: 2px solid {self.ROYAL_BLUE};
            }}
            
            QTimeEdit::up-button, QTimeEdit::down-button {{
                background-color: {colors['bg_quaternary']};
                border: none;
                width: 20px;
                border-radius: 4px;
            }}
            
            QTimeEdit::up-button:hover, QTimeEdit::down-button:hover {{
                background-color: {colors['bg_quinary']};
            }}
            
            QTimeEdit::up-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-bottom: 5px solid {colors['text_primary']};
                width: 0px;
                height: 0px;
            }}
            
            QTimeEdit::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['text_primary']};
                width: 0px;
                height: 0px;
            }}
            
            /* ===== CHECKBOX WIDGET ===== */
            QCheckBox {{
                background: transparent;
                color: {colors['text_primary']};
                font-size: 11pt;
                spacing: 8px;
                padding: 5px;
            }}
            
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 6px;
                border: 2px solid {colors['bg_quaternary']};
                background-color: {colors['bg_tertiary']};
            }}
            
            QCheckBox::indicator:hover {{
                border: 2px solid {self.ROYAL_BLUE};
                background-color: {colors['bg_secondary']};
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
                background-color: {colors['bg_quinary']};
                border: 2px solid {colors['text_quaternary']};
            }}
            
            QCheckBox:disabled {{
                color: {colors['text_quaternary']};
            }}
            
            /* ===== PROGRESS BAR ===== */
            QProgressBar {{
                background-color: {colors['bg_tertiary']};
                border: 2px solid {colors['bg_quaternary']};
                border-radius: 10px;
                text-align: center;
                color: {colors['text_primary']};
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
                color: {colors['text_secondary']};
                background: transparent;
                font-size: 9pt;
                padding: 2px;
            }}
            
            /* ===== TEXT EDIT (LOGS DISPLAY) ===== */
            QTextEdit {{
                background-color: {colors['bg_quinary']};
                border: 1px solid {colors['bg_quaternary']};
                border-radius: 8px;
                padding: 10px;
                color: {colors['text_tertiary']};
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
                line-height: 1.4;
            }}
            
            QTextEdit#logsDisplay {{
                background-color: {colors['bg_quinary']};
            }}
            
            /* ===== STATUS BAR ===== */
            QStatusBar {{
                background-color: {colors['bg_quinary']};
                color: {colors['text_tertiary']};
                border-top: 1px solid {colors['bg_quaternary']};
                font-size: 9pt;
            }}
            
            QStatusBar QLabel {{
                background: transparent;
                color: {colors['text_tertiary']};
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
                color: {colors['text_primary']};
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
                background-color: {colors['bg_tertiary']};
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {colors['bg_quaternary']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['bg_quinary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background-color: {colors['bg_tertiary']};
                height: 12px;
                border-radius: 6px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {colors['bg_quaternary']};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background-color: {colors['bg_quinary']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* ===== MESSAGE BOX ===== */
            QMessageBox {{
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
            }}
            
            QMessageBox QLabel {{
                color: {colors['text_primary']};
            }}
            
            QMessageBox QPushButton {{
                min-width: 80px;
            }}
            
            /* ===== FILE DIALOG ===== */
            QFileDialog {{
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
            }}
            
            /* ===== TOOLTIPS ===== */
            QToolTip {{
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
                border: 1px solid {self.ROYAL_BLUE};
                border-radius: 4px;
                padding: 5px;
                font-size: 9pt;
            }}
            
            /* ===== MENU (Context Menu for Tray) ===== */
            QMenu {{
                background-color: {colors['bg_secondary']};
                color: {colors['text_primary']};
                border: 1px solid {colors['bg_quaternary']};
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
                color: {colors['text_quaternary']};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {colors['bg_quaternary']};
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


def get_theme(theme_mode: Optional[str] = None) -> ThemeManager:
    """
    Get the global theme manager instance.
    
    Args:
        theme_mode: Optional theme mode ("dark" or "light"). If provided,
                   will update the theme mode of the existing instance.
    
    Returns:
        ThemeManager: The singleton theme instance
    """
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = ThemeManager(theme_mode or "dark")
    elif theme_mode is not None:
        _theme_instance.set_theme_mode(theme_mode)
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
