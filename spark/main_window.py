"""Main window for SPARK Personal."""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMenuBar, QMenu, QStatusBar,
    QLineEdit, QVBoxLayout, QWidget, QMessageBox, QDialog,
    QLabel, QComboBox, QPushButton, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from pathlib import Path
from spark.notes_widget import NotesWidget
from spark.spreadsheet_widget import SpreadsheetWidget
from spark.snippets_widget import SnippetsWidget
from spark.backup_manager import BackupManager, BackupDialog, AutoBackupTimer
from spark.themes import get_stylesheet, THEMES


class SettingsDialog(QDialog):
    """Settings dialog for application configuration."""

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(list(THEMES.keys()))
        self.theme_combo.setCurrentText(self.config.get('theme', 'Light'))
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font settings
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Family:"))
        self.font_edit = QLineEdit()
        self.font_edit.setText(self.config.get('font_family', 'Consolas'))
        font_layout.addWidget(self.font_edit)
        layout.addLayout(font_layout)

        # Font size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Font Size:"))
        self.size_edit = QLineEdit()
        self.size_edit.setText(str(self.config.get('font_size', 10)))
        size_layout.addWidget(self.size_edit)
        layout.addLayout(size_layout)

        # Autosave interval
        autosave_layout = QHBoxLayout()
        autosave_layout.addWidget(QLabel("Autosave Interval (seconds):"))
        self.autosave_edit = QLineEdit()
        self.autosave_edit.setText(str(self.config.get('autosave_interval_seconds', 300)))
        autosave_layout.addWidget(self.autosave_edit)
        layout.addLayout(autosave_layout)

        # Database location
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Database:"))
        db_label = QLabel(str(self.config.get_database_path()))
        db_label.setWordWrap(True)
        db_layout.addWidget(db_label)
        layout.addLayout(db_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

    def save_settings(self):
        """Save settings to config."""
        self.config.set('theme', self.theme_combo.currentText())
        self.config.set('font_family', self.font_edit.text())
        try:
            self.config.set('font_size', int(self.size_edit.text()))
        except ValueError:
            pass
        try:
            self.config.set('autosave_interval_seconds', int(self.autosave_edit.text()))
        except ValueError:
            pass

        QMessageBox.information(
            self, "Settings Saved",
            "Settings saved successfully!\nPlease restart the application for changes to take effect."
        )
        self.accept()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, database, config):
        super().__init__()
        self.database = database
        self.config = config

        self.setWindowTitle("SPARK Personal - Knowledgebase & Snippet Manager")

        # Set window icon
        icon_path = Path(__file__).parent.parent / "spark.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Set window size from config
        width = self.config.get('window_width', 1200)
        height = self.config.get('window_height', 800)
        self.resize(width, height)

        # Apply theme
        self.apply_theme()

        # Setup backup manager
        self.backup_manager = BackupManager(config, config.get_database_path())
        self.auto_backup_timer = AutoBackupTimer(self.backup_manager, config)

        self.init_ui()
        self.create_menus()

        # Start auto-backup
        self.auto_backup_timer.start()

        # Status bar message
        self.show_notification("SPARK Personal loaded successfully")

    def apply_theme(self):
        """Apply the current theme."""
        theme = self.config.get('theme', 'Light')
        font_family = self.config.get('font_family', 'Consolas')
        font_size = self.config.get('font_size', 10)

        stylesheet = get_stylesheet(theme, font_family, font_size)
        self.setStyleSheet(stylesheet)

    def init_ui(self):
        """Initialize the UI components."""
        # Central widget with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Notes widget
        self.notes_widget = NotesWidget(self.database, self.config)
        self.notes_widget.note_modified.connect(self.on_data_modified)
        self.tabs.addTab(self.notes_widget, "Notes")

        # Spreadsheets widget
        self.spreadsheet_widget = SpreadsheetWidget(self.database, self.config)
        self.spreadsheet_widget.sheet_modified.connect(self.on_data_modified)
        self.tabs.addTab(self.spreadsheet_widget, "Spreadsheets")

        # Snippets widget
        self.snippets_widget = SnippetsWidget(self.database, self.config)
        self.snippets_widget.snippet_modified.connect(self.on_data_modified)
        self.tabs.addTab(self.snippets_widget, "Code Snippets")

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Search bar in status bar
        self.search_widget = QWidget()
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)

        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes or snippets...")
        self.search_input.returnPressed.connect(self.perform_search)
        self.search_input.setMaximumWidth(300)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)

        self.status_bar.addPermanentWidget(self.search_widget)

    def create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        backup_action = QAction("Backup Manager", self)
        backup_action.triggered.connect(self.show_backup_manager)
        file_menu.addAction(backup_action)

        backup_now_action = QAction("Backup Now", self)
        backup_now_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        backup_now_action.triggered.connect(self.backup_now)
        file_menu.addAction(backup_now_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        search_action = QAction("Search", self)
        search_action.setShortcut(QKeySequence("Ctrl+F"))
        search_action.triggered.connect(self.focus_search)
        edit_menu.addAction(search_action)

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        undo_action.triggered.connect(self.undo_action)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        redo_action.triggered.connect(self.redo_action)
        edit_menu.addAction(redo_action)

        recalculate_action = QAction("Recalculate", self)
        recalculate_action.setShortcut(QKeySequence("Ctrl+R"))
        recalculate_action.triggered.connect(self.recalculate_spreadsheet)
        edit_menu.addAction(recalculate_action)

        # View menu
        view_menu = menubar.addMenu("View")

        view_notes_action = QAction("Notes", self)
        view_notes_action.setShortcut(QKeySequence("Ctrl+1"))
        view_notes_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        view_menu.addAction(view_notes_action)

        view_spreadsheets_action = QAction("Spreadsheets", self)
        view_spreadsheets_action.setShortcut(QKeySequence("Ctrl+2"))
        view_spreadsheets_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        view_menu.addAction(view_spreadsheets_action)

        view_snippets_action = QAction("Snippets", self)
        view_snippets_action.setShortcut(QKeySequence("Ctrl+3"))
        view_snippets_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        view_menu.addAction(view_snippets_action)

        view_menu.addSeparator()

        # Themes submenu
        themes_menu = view_menu.addMenu("Themes")
        for theme_name in THEMES.keys():
            theme_action = QAction(theme_name, self)
            theme_action.triggered.connect(
                lambda checked, t=theme_name: self.change_theme(t)
            )
            themes_menu.addAction(theme_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self.config, self)
        dialog.exec()

    def show_backup_manager(self):
        """Show backup manager dialog."""
        dialog = BackupDialog(self.backup_manager, self.config, self)
        dialog.backup_created.connect(self.on_backup_created)
        dialog.exec()

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About SPARK Personal",
            "SPARK Personal v1.0.0\n\n"
            "Personal knowledgebase and snippet manager for programmers.\n\n"
            "Features:\n"
            "- Hierarchical notes with Markdown support\n"
            "- Spreadsheets with formula engine\n"
            "- Code snippets with syntax highlighting\n"
            "- Automatic backups\n"
            "- Multiple themes\n\n"
            "Built with Python and PyQt6"
        )

    def change_theme(self, theme_name: str):
        """Change the application theme."""
        self.config.set('theme', theme_name)
        self.apply_theme()
        self.show_notification(f"Theme changed to {theme_name}")

    def focus_search(self):
        """Focus the search input."""
        self.search_input.setFocus()

    def perform_search(self):
        """Perform search based on current tab."""
        query = self.search_input.text()
        current_index = self.tabs.currentIndex()

        if current_index == 0:  # Notes
            self.notes_widget.search(query)
        elif current_index == 2:  # Snippets
            self.snippets_widget.search(query)

        if query:
            self.show_notification(f"Searching for: {query}")

    def on_data_modified(self):
        """Handle data modification."""
        self.show_notification("Data modified")

    def on_backup_created(self):
        """Handle backup creation."""
        self.show_notification("Backup created successfully")

    def backup_now(self):
        """Create a backup immediately."""
        try:
            backup_path = self.backup_manager.create_backup()
            # Apply cleanup policy after creating backup
            retention_count = self.config.get('backup_retention_count', 10)
            self.backup_manager.cleanup_old_backups(keep_count=retention_count)
            self.show_notification(f"Backup created: {backup_path.name}")
        except Exception as e:
            QMessageBox.warning(
                self, "Backup Failed",
                f"Failed to create backup: {str(e)}"
            )

    def undo_action(self):
        """Handle undo action for the current widget."""
        current_index = self.tabs.currentIndex()

        if current_index == 0:  # Notes
            if hasattr(self.notes_widget, 'undo'):
                self.notes_widget.undo()
        elif current_index == 1:  # Spreadsheets
            if hasattr(self.spreadsheet_widget, 'undo'):
                self.spreadsheet_widget.undo()
        elif current_index == 2:  # Snippets
            if hasattr(self.snippets_widget, 'undo'):
                self.snippets_widget.undo()

    def redo_action(self):
        """Handle redo action for the current widget."""
        current_index = self.tabs.currentIndex()

        if current_index == 0:  # Notes
            if hasattr(self.notes_widget, 'redo'):
                self.notes_widget.redo()
        elif current_index == 1:  # Spreadsheets
            if hasattr(self.spreadsheet_widget, 'redo'):
                self.spreadsheet_widget.redo()
        elif current_index == 2:  # Snippets
            if hasattr(self.snippets_widget, 'redo'):
                self.snippets_widget.redo()

    def recalculate_spreadsheet(self):
        """Recalculate spreadsheet if spreadsheet tab is active."""
        current_index = self.tabs.currentIndex()

        if current_index == 1:  # Spreadsheets tab
            if hasattr(self.spreadsheet_widget, 'recalculate'):
                self.spreadsheet_widget.recalculate()
                self.show_notification("Spreadsheet recalculated")
            else:
                self.show_notification("Recalculate function not available")
        else:
            self.show_notification("Recalculate only works in Spreadsheets tab")

    def show_notification(self, message: str, timeout: int = 3000):
        """Show notification in status bar."""
        self.status_bar.showMessage(message, timeout)

    def closeEvent(self, event):
        """Handle window close event."""
        # Save any unsaved changes
        if hasattr(self.notes_widget, 'is_modified') and self.notes_widget.is_modified:
            self.notes_widget.save_current_note()

        if hasattr(self.spreadsheet_widget, 'is_modified') and self.spreadsheet_widget.is_modified:
            self.spreadsheet_widget.save_current_sheet()

        if hasattr(self.snippets_widget, 'is_modified') and self.snippets_widget.is_modified:
            self.snippets_widget.save_current_snippet()

        # Save window size
        self.config.set('window_width', self.width())
        self.config.set('window_height', self.height())

        # Close database connection
        self.database.close()

        event.accept()
