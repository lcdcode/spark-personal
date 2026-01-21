"""Theme definitions for SPARK Personal."""

THEMES = {
    "Light": {
        "background": "#ffffff",
        "foreground": "#000000",
        "accent": "#0078d4",
        "border": "#cccccc",
        "hover": "#e5e5e5",
        "selected": "#cce8ff",
        "editor_bg": "#ffffff",
        "editor_fg": "#000000",
        "tree_bg": "#f5f5f5",
    },
    "Dark": {
        "background": "#1e1e1e",
        "foreground": "#d4d4d4",
        "accent": "#0e639c",
        "border": "#3e3e3e",
        "hover": "#2a2a2a",
        "selected": "#264f78",
        "editor_bg": "#1e1e1e",
        "editor_fg": "#d4d4d4",
        "tree_bg": "#252526",
    },
    "Solarized Light": {
        "background": "#fdf6e3",
        "foreground": "#657b83",
        "accent": "#268bd2",
        "border": "#eee8d5",
        "hover": "#eee8d5",
        "selected": "#93a1a1",
        "editor_bg": "#fdf6e3",
        "editor_fg": "#657b83",
        "tree_bg": "#eee8d5",
    },
    "Solarized Dark": {
        "background": "#002b36",
        "foreground": "#839496",
        "accent": "#268bd2",
        "border": "#073642",
        "hover": "#073642",
        "selected": "#586e75",
        "editor_bg": "#002b36",
        "editor_fg": "#839496",
        "tree_bg": "#073642",
    },
    "Gruvbox": {
        "background": "#282828",
        "foreground": "#ebdbb2",
        "accent": "#fe8019",
        "border": "#3c3836",
        "hover": "#3c3836",
        "selected": "#504945",
        "editor_bg": "#282828",
        "editor_fg": "#ebdbb2",
        "tree_bg": "#3c3836",
    },
}


def get_stylesheet(theme_name: str, font_family: str, font_size: int) -> str:
    """Generate Qt stylesheet for the given theme."""
    theme = THEMES.get(theme_name, THEMES["Light"])

    return f"""
    QMainWindow, QWidget {{
        background-color: {theme['background']};
        color: {theme['foreground']};
        font-family: {font_family};
        font-size: {font_size}pt;
    }}

    QTreeWidget {{
        background-color: {theme['tree_bg']};
        color: {theme['foreground']};
        border: 1px solid {theme['border']};
        outline: none;
    }}

    QTreeWidget::item:hover {{
        background-color: {theme['hover']};
    }}

    QTreeWidget::item:selected {{
        background-color: {theme['selected']};
    }}

    QListWidget {{
        background-color: {theme['tree_bg']};
        color: {theme['foreground']};
        border: 1px solid {theme['border']};
        outline: none;
    }}

    QListWidget::item:hover {{
        background-color: {theme['hover']};
    }}

    QListWidget::item:selected {{
        background-color: {theme['selected']};
    }}

    QTextEdit, QPlainTextEdit {{
        background-color: {theme['editor_bg']};
        color: {theme['editor_fg']};
        border: 1px solid {theme['border']};
        selection-background-color: {theme['selected']};
    }}

    QLineEdit {{
        background-color: {theme['editor_bg']};
        color: {theme['editor_fg']};
        border: 1px solid {theme['border']};
        padding: 4px;
    }}

    QPushButton {{
        background-color: {theme['accent']};
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 3px;
    }}

    QPushButton:hover {{
        background-color: {theme['foreground']};
    }}

    QPushButton:pressed {{
        background-color: {theme['border']};
    }}

    QTabWidget::pane {{
        border: 1px solid {theme['border']};
        background-color: {theme['background']};
    }}

    QTabBar::tab {{
        background-color: {theme['tree_bg']};
        color: {theme['foreground']};
        padding: 8px 16px;
        border: 1px solid {theme['border']};
        border-bottom: none;
    }}

    QTabBar::tab:selected {{
        background-color: {theme['background']};
    }}

    QTabBar::tab:hover {{
        background-color: {theme['hover']};
    }}

    QMenuBar {{
        background-color: {theme['background']};
        color: {theme['foreground']};
    }}

    QMenuBar::item:selected {{
        background-color: {theme['hover']};
    }}

    QMenu {{
        background-color: {theme['background']};
        color: {theme['foreground']};
        border: 1px solid {theme['border']};
    }}

    QMenu::item:selected {{
        background-color: {theme['selected']};
    }}

    QTableWidget {{
        background-color: {theme['editor_bg']};
        color: {theme['editor_fg']};
        gridline-color: {theme['border']};
        border: 1px solid {theme['border']};
    }}

    QHeaderView::section {{
        background-color: {theme['tree_bg']};
        color: {theme['foreground']};
        border: 1px solid {theme['border']};
        padding: 4px;
    }}

    QComboBox {{
        background-color: {theme['editor_bg']};
        color: {theme['editor_fg']};
        border: 1px solid {theme['border']};
        padding: 4px;
    }}

    QComboBox::drop-down {{
        border: none;
    }}

    QComboBox QAbstractItemView {{
        background-color: {theme['background']};
        color: {theme['foreground']};
        selection-background-color: {theme['selected']};
    }}

    QStatusBar {{
        background-color: {theme['tree_bg']};
        color: {theme['foreground']};
    }}

    QScrollBar:vertical {{
        background-color: {theme['background']};
        width: 12px;
    }}

    QScrollBar::handle:vertical {{
        background-color: {theme['border']};
        border-radius: 6px;
    }}

    QScrollBar:horizontal {{
        background-color: {theme['background']};
        height: 12px;
    }}

    QScrollBar::handle:horizontal {{
        background-color: {theme['border']};
        border-radius: 6px;
    }}
    """
