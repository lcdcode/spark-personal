"""Code snippets widget with syntax highlighting."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QPushButton, QLineEdit, QComboBox, QSplitter, QInputDialog,
    QMessageBox, QLabel, QApplication, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QAction
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


# Common programming languages
LANGUAGES = sorted([
    "Python", "JavaScript", "Java", "C", "C++", "C#", "Ruby", "Go", "Rust",
    "PHP", "Swift", "Kotlin", "TypeScript", "SQL", "HTML", "CSS", "Shell",
    "Bash", "PowerShell", "R", "Perl", "Scala", "Haskell", "Lua", "YAML",
    "JSON", "XML", "Markdown", "Plain Text"
])


class SnippetsWidget(QWidget):
    """Widget for managing code snippets."""

    snippet_modified = pyqtSignal()

    def __init__(self, database, config, parent=None):
        super().__init__(parent)
        self.database = database
        self.config = config
        self.current_snippet_id = None
        self.is_modified = False

        self.init_ui()
        self.load_snippets()

    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)

        # Left panel: Snippet list and filters
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Language filter
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("Language:"))
        self.lang_filter = QComboBox()
        self.lang_filter.addItem("All Languages")
        self.lang_filter.addItems(LANGUAGES)
        self.lang_filter.currentTextChanged.connect(self.filter_snippets)
        lang_layout.addWidget(self.lang_filter)
        left_layout.addLayout(lang_layout)

        # Snippet list with context menu
        self.snippet_list = QListWidget()
        self.snippet_list.itemClicked.connect(self.on_snippet_selected)
        self.snippet_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.snippet_list.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.snippet_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Snippet")
        self.btn_add.clicked.connect(self.add_snippet)
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_snippet)
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_delete)
        left_layout.addLayout(button_layout)

        # Right panel: Editor
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Snippet Title")
        self.title_edit.textChanged.connect(self.mark_modified)
        right_layout.addWidget(self.title_edit)

        # Language selector
        lang_select_layout = QHBoxLayout()
        lang_select_layout.addWidget(QLabel("Language:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(LANGUAGES)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        lang_select_layout.addWidget(self.language_combo)
        lang_select_layout.addStretch()
        right_layout.addLayout(lang_select_layout)

        # Tags
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (comma-separated)")
        self.tags_edit.textChanged.connect(self.mark_modified)
        right_layout.addWidget(self.tags_edit)

        # Code editor with syntax highlighting
        self.code_editor = QTextEdit()
        self.code_editor.setFontFamily("Consolas")
        self.code_editor.setFontPointSize(10)
        # Set document margins to 0
        self.code_editor.document().setDocumentMargin(0)
        self.code_editor.textChanged.connect(self.mark_modified)
        self.code_editor.textChanged.connect(self.update_syntax_highlighting)
        right_layout.addWidget(self.code_editor)

        # Action buttons
        action_layout = QHBoxLayout()
        self.btn_copy = QPushButton("Copy to Clipboard")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save_current_snippet)
        action_layout.addWidget(self.btn_copy)
        action_layout.addWidget(self.btn_save)
        right_layout.addLayout(action_layout)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter)

    def load_snippets(self):
        """Load all snippets into the list."""
        self.snippet_list.clear()
        snippets = self.database.get_all_snippets()

        for snippet in snippets:
            item = self.snippet_list.addItem(
                f"[{snippet['language']}] {snippet['title']}"
            )
            self.snippet_list.item(self.snippet_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole, snippet['id']
            )

    def filter_snippets(self, language: str):
        """Filter snippets by language."""
        self.snippet_list.clear()

        if language == "All Languages":
            snippets = self.database.get_all_snippets()
        else:
            snippets = self.database.get_snippets_by_language(language)

        for snippet in snippets:
            item = self.snippet_list.addItem(
                f"[{snippet['language']}] {snippet['title']}"
            )
            self.snippet_list.item(self.snippet_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole, snippet['id']
            )

    def on_snippet_selected(self, item):
        """Handle snippet selection."""
        if self.is_modified:
            self.save_current_snippet()

        snippet_id = item.data(Qt.ItemDataRole.UserRole)
        snippet = self.database.get_snippet(snippet_id)

        if snippet:
            self.current_snippet_id = snippet_id
            self.title_edit.setText(snippet['title'])
            self.code_editor.setPlainText(snippet['code'] or "")
            self.language_combo.setCurrentText(snippet['language'] or "Plain Text")
            self.tags_edit.setText(snippet['tags'] or "")
            self.is_modified = False
            self.update_syntax_highlighting()

    def on_language_changed(self, language: str):
        """Handle language change."""
        self.mark_modified()
        self.update_syntax_highlighting()

    def update_syntax_highlighting(self):
        """Update syntax highlighting in the editor."""
        # Save cursor position and scroll position
        cursor = self.code_editor.textCursor()
        cursor_position = cursor.position()
        scrollbar = self.code_editor.verticalScrollBar()
        scroll_position = scrollbar.value()

        code = self.code_editor.toPlainText()
        language = self.language_combo.currentText()

        if not code:
            return

        try:
            # Map language names to Pygments lexer names
            lang_map = {
                "C++": "cpp",
                "C#": "csharp",
                "Plain Text": "text",
                "Shell": "bash",
            }
            lexer_name = lang_map.get(language, language.lower())
            lexer = get_lexer_by_name(lexer_name)
            # Use nowrap=True to get just the span-wrapped tokens without pre wrapper
            formatter = HtmlFormatter(style='monokai', noclasses=True, nowrap=True)
            highlighted = highlight(code, lexer, formatter)

            # Create HTML with inline styles to avoid block spacing
            styled_html = f"""<!DOCTYPE html>
<html>
<head>
<style>
html, body {{
    margin: 0;
    padding: 8px;
    background-color: #272822;
    font-family: "Consolas", "Monaco", "Courier New", monospace;
    font-size: 10pt;
    color: #f8f8f2;
    line-height: 1.3;
}}
p {{
    margin: 0;
    padding: 0;
    line-height: 1.3;
    white-space: pre;
}}
</style>
</head>
<body>
<p>{highlighted}</p>
</body>
</html>"""

            # Block signals to prevent triggering textChanged
            self.code_editor.blockSignals(True)
            self.code_editor.setHtml(styled_html)
            self.code_editor.blockSignals(False)

            # Restore cursor position and scroll position
            cursor = self.code_editor.textCursor()
            cursor.setPosition(min(cursor_position, len(self.code_editor.toPlainText())))
            self.code_editor.setTextCursor(cursor)
            scrollbar.setValue(scroll_position)

        except ClassNotFound:
            # If lexer not found, just use plain text
            pass

    def add_snippet(self):
        """Add a new snippet."""
        title, ok = QInputDialog.getText(self, "New Snippet", "Enter snippet title:")
        if ok and title:
            snippet_id = self.database.add_snippet(title)
            self.load_snippets()
            self.snippet_modified.emit()

    def delete_snippet(self):
        """Delete the selected snippet."""
        current_item = self.snippet_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Sele![Alt text](image-url.png)ction", "Please select a snippet to delete.")
            return

        reply = QMessageBox.question(
            self, "Delete Snippet",
            "Are you sure you want to delete this snippet?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            snippet_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.database.delete_snippet(snippet_id)
            self.load_snippets()
            self.clear_editor()
            self.snippet_modified.emit()

    def save_current_snippet(self):
        """Save the current snippet."""
        if self.current_snippet_id and self.is_modified:
            title = self.title_edit.text()
            code = self.code_editor.toPlainText()
            language = self.language_combo.currentText()
            tags = self.tags_edit.text()

            self.database.update_snippet(
                self.current_snippet_id, title, code, language, tags
            )
            self.is_modified = False
            self.load_snippets()
            self.snippet_modified.emit()

    def copy_to_clipboard(self):
        """Copy snippet code to clipboard."""
        code = self.code_editor.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(code)
        QMessageBox.information(self, "Copied", "Code copied to clipboard!")

    def mark_modified(self):
        """Mark the current snippet as modified."""
        self.is_modified = True

    def clear_editor(self):
        """Clear the editor."""
        self.current_snippet_id = None
        self.title_edit.clear()
        self.code_editor.clear()
        self.tags_edit.clear()
        self.is_modified = False

    def search(self, query: str):
        """Search snippets."""
        if not query:
            self.load_snippets()
            return

        self.snippet_list.clear()
        results = self.database.search_snippets(query)
        for snippet in results:
            item = self.snippet_list.addItem(
                f"[{snippet['language']}] {snippet['title']}"
            )
            self.snippet_list.item(self.snippet_list.count() - 1).setData(
                Qt.ItemDataRole.UserRole, snippet['id']
            )

    def show_context_menu(self, position):
        """Show context menu for the snippet list."""
        menu = QMenu()

        # Add Snippet action (always available)
        add_action = QAction("Add Snippet", self)
        add_action.triggered.connect(self.add_snippet)
        menu.addAction(add_action)

        # Actions that require a selection
        current_item = self.snippet_list.currentItem()
        if current_item:
            menu.addSeparator()

            copy_action = QAction("Copy to Clipboard", self)
            copy_action.triggered.connect(self.copy_to_clipboard)
            menu.addAction(copy_action)

            save_action = QAction("Save Snippet", self)
            save_action.triggered.connect(self.save_current_snippet)
            menu.addAction(save_action)

            menu.addSeparator()

            delete_action = QAction("Delete Snippet", self)
            delete_action.triggered.connect(self.delete_snippet)
            menu.addAction(delete_action)

        menu.exec(self.snippet_list.viewport().mapToGlobal(position))
