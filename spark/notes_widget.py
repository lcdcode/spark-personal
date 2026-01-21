"""Notes widget with hierarchical tree and Markdown editor."""

import html
import os
import re
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QTextEdit, QTabWidget, QSplitter, QLineEdit,
    QMessageBox, QInputDialog, QFileDialog, QMenu, QTextBrowser
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl
from PyQt6.QtGui import QTextCursor, QImage, QAction, QDesktopServices
import markdown
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


class ChecklistPreprocessor(Preprocessor):
    """Convert GitHub-style checklists to HTML."""

    CHECKLIST_PATTERN = re.compile(r'^(\s*)- \[([ xX])\] (.+)$', re.MULTILINE)

    def run(self, lines):
        new_lines = []
        for line in lines:
            # Check for checklist items
            match = self.CHECKLIST_PATTERN.match(line)
            if match:
                indent, checked, text = match.groups()
                checkbox = '☑' if checked.lower() == 'x' else '☐'
                # Keep it as a list item by preserving the "- " prefix
                new_lines.append(f'{indent}- {checkbox} {text}')
            else:
                new_lines.append(line)
        return new_lines


class ChecklistExtension(Extension):
    """Markdown extension for GitHub-style checklists."""

    def extendMarkdown(self, md):
        md.preprocessors.register(ChecklistPreprocessor(md), 'checklist', 100)


class BlockquotePreprocessor(Preprocessor):
    """Fix blockquote line handling - add line breaks only between consecutive text lines."""

    def run(self, lines):
        new_lines = []
        prev_was_text_blockquote = False

        for line in lines:
            is_blockquote = line.strip().startswith('>')
            is_blank_blockquote = line.strip() == '>'
            is_text_blockquote = is_blockquote and not is_blank_blockquote

            # Add hard line break (two spaces) if this is a text blockquote
            # and the previous line was also a text blockquote
            if is_text_blockquote and prev_was_text_blockquote and new_lines:
                last_line = new_lines.pop()
                new_lines.append(last_line.rstrip() + '  ')

            new_lines.append(line)
            prev_was_text_blockquote = is_text_blockquote

        return new_lines


class BlockquoteExtension(Extension):
    """Markdown extension for better blockquote handling."""

    def extendMarkdown(self, md):
        md.preprocessors.register(BlockquotePreprocessor(md), 'blockquote_fix', 95)


class CodeBlockPreprocessor(Preprocessor):
    """Syntax highlight fenced code blocks using Pygments."""

    FENCED_BLOCK_PATTERN = re.compile(
        r'^```(\w*)\n(.*?)^```',
        re.MULTILINE | re.DOTALL
    )

    def run(self, lines):
        text = '\n'.join(lines)

        def replace_code_block(match):
            lang = match.group(1) or 'text'
            code = match.group(2)

            try:
                lexer = get_lexer_by_name(lang, stripall=True)
            except ClassNotFound:
                try:
                    lexer = guess_lexer(code)
                except ClassNotFound:
                    lexer = get_lexer_by_name('text', stripall=True)

            # Use Pygments for syntax highlighting with inline styles
            formatter = HtmlFormatter(
                style='monokai',
                noclasses=True,  # Use inline styles instead of CSS classes
                nowrap=True,     # Don't wrap - we'll do it ourselves
            )
            highlighted = highlight(code, lexer, formatter)

            # Remove any <br> tags that Pygments might add
            highlighted = re.sub(r'<br\s*/?>', '', highlighted)

            # Wrap in table for reliable background color in QTextBrowser
            wrapper = (
                '<table cellpadding="0" cellspacing="0" border="0" width="100%">'
                '<tr><td style="background-color: #272822; color: #f8f8f2; '
                'padding: 12px; '
                'font-family: Consolas, Monaco, monospace; font-size: 0.9em;">'
                f'<pre style="margin: 0; background-color: #272822; color: #f8f8f2;">{highlighted}</pre>'
                '</td></tr></table>'
            )
            return f'\n\n{wrapper}\n\n'

        text = self.FENCED_BLOCK_PATTERN.sub(replace_code_block, text)
        return text.split('\n')


class CodeHighlightExtension(Extension):
    """Markdown extension for syntax-highlighted code blocks."""

    def extendMarkdown(self, md):
        md.preprocessors.register(CodeBlockPreprocessor(md), 'codehighlight', 90)


class NotesWidget(QWidget):
    """Widget for managing hierarchical notes with Markdown support."""

    note_modified = pyqtSignal()

    def __init__(self, database, config, parent=None):
        super().__init__(parent)
        self.database = database
        self.config = config
        self.current_note_id = None
        self.is_modified = False
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)

        self.init_ui()
        self.load_notes()

        # Start autosave timer
        if self.config.get('autosave_enabled', True):
            interval = self.config.get('autosave_interval_seconds', 300) * 1000
            self.autosave_timer.start(interval)

    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)

        # Left panel: Tree and buttons
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Notes")
        self.tree.itemClicked.connect(self.on_note_selected)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.tree)

        # Buttons
        button_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Note")
        self.btn_add.clicked.connect(self.add_note)
        self.btn_add_child = QPushButton("Add Child")
        self.btn_add_child.clicked.connect(self.add_child_note)
        self.btn_add_child.setEnabled(False)  # Disabled until a note is selected
        self.btn_delete = QPushButton("Delete")
        self.btn_delete.clicked.connect(self.delete_note)
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_add_child)
        button_layout.addWidget(self.btn_delete)
        left_layout.addLayout(button_layout)

        # Connect tree selection change to update button states
        self.tree.itemSelectionChanged.connect(self.update_button_states)

        # Right panel: Editor and preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Title editor
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Note Title")
        self.title_edit.textChanged.connect(self.mark_modified)
        right_layout.addWidget(self.title_edit)

        # Tab widget for editor and preview
        self.tabs = QTabWidget()

        # Editor tab
        self.editor = QTextEdit()
        self.editor.setAcceptDrops(True)
        self.editor.textChanged.connect(self.mark_modified)
        self.editor.setTabStopDistance(
            self.config.get('editor_tab_width', 4) *
            self.editor.fontMetrics().horizontalAdvance(' ')
        )
        self.tabs.addTab(self.editor, "Editor")

        # Preview tab (using QTextBrowser for clickable links)
        self.preview = QTextBrowser()
        self.preview.setReadOnly(True)
        self.preview.setOpenExternalLinks(False)  # Handle links ourselves
        self.preview.anchorClicked.connect(self.on_link_clicked)
        self.tabs.addTab(self.preview, "Preview")

        self.tabs.currentChanged.connect(self.on_tab_changed)
        right_layout.addWidget(self.tabs)

        # Action buttons
        action_button_layout = QHBoxLayout()
        self.btn_insert_image = QPushButton("Insert Image")
        self.btn_insert_image.clicked.connect(self.insert_image)
        self.btn_save = QPushButton("Save (Ctrl+S)")
        self.btn_save.clicked.connect(self.save_current_note)
        action_button_layout.addWidget(self.btn_insert_image)
        action_button_layout.addWidget(self.btn_save)
        right_layout.addLayout(action_button_layout)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        layout.addWidget(splitter)

    def load_notes(self):
        """Load notes into the tree widget."""
        self.tree.clear()
        root_notes = self.database.get_root_notes()
        for note in root_notes:
            self.add_tree_item(None, note)

    def add_tree_item(self, parent_item, note):
        """Add a note to the tree widget."""
        if parent_item is None:
            item = QTreeWidgetItem(self.tree)
        else:
            item = QTreeWidgetItem(parent_item)

        item.setText(0, note['title'])
        item.setData(0, Qt.ItemDataRole.UserRole, note['id'])

        # Add children
        children = self.database.get_child_notes(note['id'])
        for child in children:
            self.add_tree_item(item, child)

        item.setExpanded(True)
        return item

    def on_note_selected(self, item, column):
        """Handle note selection."""
        if self.is_modified:
            self.save_current_note()

        note_id = item.data(0, Qt.ItemDataRole.UserRole)
        note = self.database.get_note(note_id)

        if note:
            self.current_note_id = note_id
            self.title_edit.setText(note['title'])
            self.editor.setPlainText(note['content'] or "")
            self.is_modified = False

            # Always update the preview with current content
            self.update_preview()

            # Default to preview tab unless it's a new note (empty content)
            if note['content']:
                self.tabs.setCurrentIndex(1)  # Preview tab
            else:
                self.tabs.setCurrentIndex(0)  # Editor tab

    def add_note(self):
        """Add a new root note."""
        title, ok = QInputDialog.getText(self, "New Note", "Enter note title:")
        if ok and title:
            note_id = self.database.add_note(title)
            self.load_notes()
            self.note_modified.emit()

    def add_child_note(self):
        """Add a child note to the selected note."""
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a parent note first.")
            return

        parent_id = current_item.data(0, Qt.ItemDataRole.UserRole)
        title, ok = QInputDialog.getText(self, "New Child Note", "Enter note title:")
        if ok and title:
            note_id = self.database.add_note(title, parent_id=parent_id)
            self.load_notes()
            self.note_modified.emit()

    def delete_note(self):
        """Delete the selected note."""
        current_item = self.tree.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a note to delete.")
            return

        reply = QMessageBox.question(
            self, "Delete Note",
            "Are you sure you want to delete this note and all its children?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            note_id = current_item.data(0, Qt.ItemDataRole.UserRole)
            self.database.delete_note(note_id)
            self.load_notes()
            self.clear_editor()
            self.note_modified.emit()

    def save_current_note(self):
        """Save the current note."""
        if self.current_note_id and self.is_modified:
            title = self.title_edit.text()
            content = self.editor.toPlainText()
            self.database.update_note(self.current_note_id, title, content)
            self.is_modified = False
            self.load_notes()
            self.note_modified.emit()

    def autosave(self):
        """Autosave the current note if modified."""
        if self.is_modified and self.current_note_id:
            self.save_current_note()

    def mark_modified(self):
        """Mark the current note as modified."""
        self.is_modified = True

    def update_button_states(self):
        """Update button enabled states based on selection."""
        has_selection = self.tree.currentItem() is not None
        self.btn_add_child.setEnabled(has_selection)

    def on_tab_changed(self, index):
        """Handle tab change between editor and preview."""
        if index == 1:  # Preview tab
            self.update_preview()

    def insert_image(self):
        """Insert an image into the note."""
        # Open file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;All Files (*)"
        )

        if not file_path:
            return

        try:
            source_path = Path(file_path)

            # Validate file size (10MB limit for security)
            MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
            file_size = source_path.stat().st_size
            if file_size > MAX_IMAGE_SIZE:
                QMessageBox.warning(
                    self,
                    "File Too Large",
                    f"Image must be less than 10MB. Selected file is {file_size / (1024*1024):.1f}MB."
                )
                return

            # Get the images directory from config
            images_dir = self.config.get_images_dir()

            # Generate a unique filename to avoid conflicts
            destination_filename = source_path.name
            destination_path = images_dir / destination_filename

            # Handle duplicate filenames
            counter = 1
            while destination_path.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                destination_filename = f"{stem}_{counter}{suffix}"
                destination_path = images_dir / destination_filename
                counter += 1

            # Copy the image to the images directory
            shutil.copy2(source_path, destination_path)

            # Insert markdown image syntax with relative path
            # The path is just the filename, which will be resolved relative to images/
            image_markdown = f"![{destination_filename}]({destination_filename})"

            # Insert at cursor position
            cursor = self.editor.textCursor()
            cursor.insertText(image_markdown)

            # Mark as modified
            self.mark_modified()

            QMessageBox.information(
                self,
                "Image Inserted",
                f"Image copied to images folder and inserted as:\n{image_markdown}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to insert image: {str(e)}"
            )

    def update_preview(self):
        """Update the preview pane with rendered Markdown."""
        content = self.editor.toPlainText()

        # Process image paths: block remote images and resolve local paths
        content = self._process_image_paths(content)

        # Use custom extensions for better rendering
        # Note: nl2br removed as it adds <br> inside code blocks causing stripy appearance
        extensions = [
            'tables',
            BlockquoteExtension(),
            ChecklistExtension(),
            CodeHighlightExtension(),
        ]

        html_content = markdown.markdown(content, extensions=extensions)

        # Apply strikethrough manually (~~text~~) with HTML escaping for security
        html_content = re.sub(
            r'~~(.+?)~~',
            lambda m: f'<del>{html.escape(m.group(1))}</del>',
            html_content
        )

        # CSS for proper styling
        css = '''
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                line-height: 1.6;
                padding: 10px;
            }
            h1, h2, h3, h4, h5, h6 {
                margin-top: 1em;
                margin-bottom: 0.5em;
                font-weight: 600;
            }
            h1 { font-size: 2em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
            h2 { font-size: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 0.3em; }
            h3 { font-size: 1.25em; }
            h4 { font-size: 1em; }
            h5 { font-size: 0.875em; }
            h6 { font-size: 0.85em; color: #666; }
            code {
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                font-size: 0.9em;
            }
            pre {
                background-color: #272822;
                color: #f8f8f2;
                padding: 12px;
                border-radius: 6px;
                overflow-x: auto;
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                font-size: 0.9em;
                line-height: 1.3;
                margin: 1em 0;
                white-space: pre;
            }
            pre code {
                background-color: transparent;
                padding: 0;
                color: inherit;
            }
            pre span {
                line-height: 1.3;
            }
            /* Remove any br tags inside pre blocks via display */
            pre br {
                display: none;
            }
            blockquote {
                border-left: 4px solid #0066cc;
                margin: 1em 0;
                padding: 0.5em 1em;
                background-color: #f8f9fa;
                color: #555;
            }
            blockquote blockquote {
                border-left-color: #999;
                margin-left: 1.5em;
                margin-top: 0.5em;
                margin-bottom: 0.5em;
                background-color: #f0f1f3;
            }
            blockquote blockquote blockquote {
                border-left-color: #666;
                margin-left: 1.5em;
                background-color: #e8e9eb;
            }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px 12px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
                font-weight: 600;
            }
            tr:nth-child(even) {
                background-color: #fafafa;
            }
            hr {
                border: none;
                border-top: 1px solid #ddd;
                margin: 1.5em 0;
            }
            a {
                color: #0066cc;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            del {
                color: #999;
                text-decoration: line-through;
            }
            ul, ol {
                padding-left: 2em;
            }
            li {
                margin: 0.25em 0;
            }
            .codehilite {
                background-color: #272822;
                border-radius: 6px;
                padding: 12px;
                margin: 1em 0;
                overflow-x: auto;
                line-height: 1.3;
            }
            .codehilite pre {
                margin: 0;
                padding: 0;
                background-color: transparent;
            }
            .codehilite br {
                display: none;
            }
        </style>
        '''

        full_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            {css}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        '''

        self.preview.setHtml(full_html)

    def _process_image_paths(self, content: str) -> str:
        """Process image paths in markdown content.

        - Blocks remote images (http/https) for security
        - Resolves relative paths to the images/ folder
        """
        # Pattern to match markdown images: ![alt](path)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)

            # Block remote images for user protection
            if image_path.startswith(('http://', 'https://', 'ftp://', '//')):
                # Replace with a warning message
                return f'![Remote images are blocked for security: {alt_text}]()'

            # Resolve local paths relative to images directory
            images_dir = self.config.get_images_dir()
            resolved_path = images_dir / image_path

            # Validate path stays within images_dir (prevent path traversal)
            try:
                if not resolved_path.resolve().is_relative_to(images_dir.resolve()):
                    return f'![Invalid path: {alt_text}]()'
            except (ValueError, OSError):
                return f'![Invalid path: {alt_text}]()'

            # Convert to file:// URL for QTextBrowser
            if resolved_path.exists():
                file_url = resolved_path.as_uri()
                return f'![{alt_text}]({file_url})'
            else:
                # Image not found
                return f'![Image not found: {image_path}]()'

        return re.sub(image_pattern, replace_image, content)

    def on_link_clicked(self, url: QUrl):
        """Handle link clicks in the preview."""
        if url.scheme() in ('http', 'https', 'mailto'):
            QDesktopServices.openUrl(url)

    def clear_editor(self):
        """Clear the editor."""
        self.current_note_id = None
        self.title_edit.clear()
        self.editor.clear()
        self.preview.clear()
        self.is_modified = False

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts."""
        if event.key() == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.save_current_note()
        else:
            super().keyPressEvent(event)

    def search(self, query: str):
        """Search notes and highlight results."""
        if not query:
            self.load_notes()
            return

        self.tree.clear()
        results = self.database.search_notes(query)
        for note in results:
            item = QTreeWidgetItem(self.tree)
            item.setText(0, note['title'])
            item.setData(0, Qt.ItemDataRole.UserRole, note['id'])

    def show_context_menu(self, position):
        """Show context menu for the notes tree."""
        menu = QMenu()

        # Add Note action (always available)
        add_action = QAction("Add Note", self)
        add_action.triggered.connect(self.add_note)
        menu.addAction(add_action)

        # Actions that require a selection
        current_item = self.tree.currentItem()
        if current_item:
            add_child_action = QAction("Add Child Note", self)
            add_child_action.triggered.connect(self.add_child_note)
            menu.addAction(add_child_action)

            menu.addSeparator()

            delete_action = QAction("Delete Note", self)
            delete_action.triggered.connect(self.delete_note)
            menu.addAction(delete_action)

            menu.addSeparator()

            save_action = QAction("Save Note", self)
            save_action.triggered.connect(self.save_current_note)
            menu.addAction(save_action)

        menu.exec(self.tree.viewport().mapToGlobal(position))
