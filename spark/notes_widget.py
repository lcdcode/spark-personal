"""Notes widget with hierarchical tree and Markdown editor."""

import html
import os
import re
import shutil
import secrets
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QTextEdit, QTabWidget, QSplitter, QLineEdit,
    QMessageBox, QInputDialog, QFileDialog, QMenu, QTextBrowser
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QUrl, QMimeData
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


class ImageTextEdit(QTextEdit):
    """Custom QTextEdit with drag-and-drop and paste support for images."""

    image_inserted = pyqtSignal(str)  # Emits the image path when an image is inserted

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def canInsertFromMimeData(self, source: QMimeData) -> bool:
        """Check if the mime data contains an image or file."""
        return source.hasImage() or source.hasUrls() or source.hasText()

    def insertFromMimeData(self, source: QMimeData):
        """Handle pasted or dropped content."""
        # Handle image data directly from clipboard
        if source.hasImage():
            image = source.imageData()
            if isinstance(image, QImage) and not image.isNull():
                self.image_inserted.emit(image)
                return

        # Handle file URLs (drag and drop)
        if source.hasUrls():
            urls = source.urls()
            if urls:
                for url in urls:
                    if url.isLocalFile():
                        file_path = url.toLocalFile()
                        # Check if it's an image file
                        if self._is_image_file(file_path):
                            self.image_inserted.emit(file_path)
                            return

        # Fall back to default text insertion
        super().insertFromMimeData(source)

    def _is_image_file(self, file_path: str) -> bool:
        """Check if a file is an image based on extension."""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
        return Path(file_path).suffix.lower() in image_extensions


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

        # Editor tab (using ImageTextEdit for drag-and-drop support)
        self.editor = ImageTextEdit()
        self.editor.textChanged.connect(self.mark_modified)
        self.editor.image_inserted.connect(self.handle_image_insert)
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

    def _extract_image_filenames(self, content: str) -> list:
        """Extract image filenames from markdown content.

        Args:
            content: Markdown content to parse

        Returns:
            List of image filenames found in the content
        """
        if not content:
            return []

        # Match markdown image syntax: ![alt text](filename)
        # This matches both local filenames and paths
        pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)

        filenames = []
        for alt_text, path in matches:
            # Skip remote URLs
            if path.startswith(('http://', 'https://', 'ftp://', '//')):
                continue
            # Skip file:// URLs (these are already resolved paths)
            if path.startswith('file://'):
                continue
            # Extract just the filename (remove any path components)
            filename = Path(path).name
            filenames.append(filename)

        return filenames

    def _collect_note_images(self, note_id: int, collected_ids=None) -> list:
        """Recursively collect all image filenames from a note and its children.

        Args:
            note_id: ID of the note to process
            collected_ids: Set of already processed note IDs (to avoid duplicates)

        Returns:
            List of image filenames (may contain duplicates)
        """
        if collected_ids is None:
            collected_ids = set()

        # Avoid processing the same note twice
        if note_id in collected_ids:
            return []

        collected_ids.add(note_id)
        images = []

        # Get the note content
        note = self.database.get_note(note_id)
        if note and note['content']:
            note_images = self._extract_image_filenames(note['content'])
            images.extend(note_images)
            if note_images:
                print(f"Found {len(note_images)} image(s) in note '{note['title']}': {note_images}")

        # Recursively process children
        children = self.database.get_child_notes(note_id)
        for child in children:
            images.extend(self._collect_note_images(child['id'], collected_ids))

        return images

    def _delete_note_images(self, note_id: int):
        """Delete all images associated with a note and its children.

        Args:
            note_id: ID of the note whose images should be deleted
        """
        # Collect all image filenames
        image_filenames = self._collect_note_images(note_id)

        if not image_filenames:
            print("No images found to delete")
            return

        # Remove duplicates while preserving order
        unique_images = list(dict.fromkeys(image_filenames))
        print(f"Collected {len(unique_images)} unique image(s) to delete: {unique_images}")

        images_dir = self.config.get_images_dir()
        deleted_count = 0
        not_found_count = 0

        for filename in unique_images:
            image_path = images_dir / filename
            try:
                if image_path.exists():
                    image_path.unlink()
                    deleted_count += 1
                    print(f"  ✓ Deleted: {filename}")
                else:
                    not_found_count += 1
                    print(f"  ⚠ Not found: {filename}")
            except Exception as e:
                # Log error but continue deleting other images
                print(f"  ✗ Failed to delete {filename}: {e}")

        print(f"Summary: Deleted {deleted_count} image(s), {not_found_count} not found")

    def delete_note(self):
        """Delete the selected note and its associated images."""
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

            # Delete associated images first
            self._delete_note_images(note_id)

            # Then delete the note from database
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

    def _generate_unique_filename(self, original_name: str, images_dir: Path) -> str:
        """Generate a unique filename with random suffix."""
        original_path = Path(original_name)
        stem = original_path.stem
        suffix = original_path.suffix

        # Generate a random 8-character hex string
        random_suffix = secrets.token_hex(4)  # 4 bytes = 8 hex characters

        # Create filename with random suffix
        filename = f"{stem}_{random_suffix}{suffix}"
        destination_path = images_dir / filename

        # In the unlikely event of a collision, keep trying
        while destination_path.exists():
            random_suffix = secrets.token_hex(4)
            filename = f"{stem}_{random_suffix}{suffix}"
            destination_path = images_dir / filename

        return filename

    def _copy_image_to_storage(self, source_path: Path) -> str:
        """Copy an image to the images directory and return the filename.

        Returns:
            str: The filename (not full path) of the copied image

        Raises:
            Exception: If the image is too large or copying fails
        """
        # Validate file size (10MB limit for security)
        MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
        file_size = source_path.stat().st_size
        if file_size > MAX_IMAGE_SIZE:
            raise Exception(
                f"Image must be less than 10MB. Selected file is {file_size / (1024*1024):.1f}MB."
            )

        # Get the images directory from config
        images_dir = self.config.get_images_dir()

        # Generate a unique filename with random suffix
        destination_filename = self._generate_unique_filename(source_path.name, images_dir)
        destination_path = images_dir / destination_filename

        # Copy the image to the images directory
        shutil.copy2(source_path, destination_path)

        return destination_filename

    def _save_qimage_to_storage(self, image: QImage) -> str:
        """Save a QImage to the images directory and return the filename.

        Returns:
            str: The filename (not full path) of the saved image

        Raises:
            Exception: If saving fails
        """
        # Get the images directory from config
        images_dir = self.config.get_images_dir()

        # Generate a unique filename with timestamp and random suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = secrets.token_hex(4)
        filename = f"pasted_image_{timestamp}_{random_suffix}.png"
        destination_path = images_dir / filename

        # Save the image
        if not image.save(str(destination_path), "PNG"):
            raise Exception("Failed to save image")

        return filename

    def handle_image_insert(self, image_data):
        """Handle image insertion from drag-and-drop or paste.

        Args:
            image_data: Either a file path (str) or a QImage object
        """
        try:
            if isinstance(image_data, QImage):
                # Handle pasted image from clipboard
                filename = self._save_qimage_to_storage(image_data)
            else:
                # Handle dropped file path
                source_path = Path(image_data)
                filename = self._copy_image_to_storage(source_path)

            # Insert markdown image syntax
            image_markdown = f"![{filename}]({filename})"

            # Insert at cursor position
            cursor = self.editor.textCursor()
            cursor.insertText(image_markdown)

            # Mark as modified
            self.mark_modified()

        except Exception as e:
            QMessageBox.warning(
                self,
                "Image Insert Failed",
                f"Failed to insert image: {str(e)}"
            )

    def insert_image(self):
        """Insert an image into the note via file dialog."""
        # Open file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg);;All Files (*)"
        )

        if not file_path:
            return

        # Use the common handler
        self.handle_image_insert(file_path)

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
