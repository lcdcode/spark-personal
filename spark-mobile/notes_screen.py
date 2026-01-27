"""Notes screen for SPARK Mobile."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp


class NotesScreen(BoxLayout):
    """Notes list and editor screen."""

    def __init__(self, db, db_path=None, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.db_path = db_path
        self.orientation = 'vertical'
        self.current_note_id = None

        # Top bar with add button
        top_bar = BoxLayout(size_hint_y=0.05, padding=dp(10), spacing=dp(10))

        self.search_input = TextInput(
            hint_text='Search notes...',
            multiline=False,
            size_hint_x=0.7
        )
        self.search_input.bind(text=self.on_search)
        top_bar.add_widget(self.search_input)

        add_btn = Button(
            text='+ New Note',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        add_btn.bind(on_press=self.show_add_note_dialog)
        top_bar.add_widget(add_btn)

        self.add_widget(top_bar)

        # Notes list
        scroll = ScrollView(size_hint_y=0.9)
        self.notes_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.notes_list.bind(minimum_height=self.notes_list.setter('height'))
        scroll.add_widget(self.notes_list)
        self.add_widget(scroll)

        # Load initial notes
        self.refresh_notes()

    def refresh_notes(self, search_query=None):
        """Refresh the notes list with hierarchical display."""
        self.notes_list.clear_widgets()

        if search_query:
            # For search, show flat list
            notes = self.db.search_notes(search_query)
            if not notes:
                label = Label(
                    text=f'No notes found for "{search_query}"',
                    size_hint_y=None,
                    height=dp(100),
                    color=(0.5, 0.5, 0.5, 1)
                )
                self.notes_list.add_widget(label)
                return

            for note in notes:
                self._add_note_widget(note, level=0)
        else:
            # Show hierarchical tree view
            root_notes = self.db.get_root_notes()

            if not root_notes:
                label = Label(
                    text='No notes yet.\nTap "+ New Note" to create one.',
                    size_hint_y=None,
                    height=dp(100),
                    color=(0.5, 0.5, 0.5, 1)
                )
                self.notes_list.add_widget(label)
                return

            for note in root_notes:
                self._add_note_with_children(note, level=0)

    def _add_note_with_children(self, note, level=0):
        """Recursively add note and its children."""
        # Add the note
        self._add_note_widget(note, level)

        # Add children
        children = self.db.get_child_notes(note['id'])
        for child in children:
            self._add_note_with_children(child, level + 1)

    def _add_note_widget(self, note, level=0):
        """Create and add a note button widget with proper styling."""
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.clock import Clock

        # Preview text - shortened for mobile
        # We don't actually show the preview anymore (it was ugly) but it's here to guide the 
        # height of the button
        preview = note['content'][:35] + "..." if len(note['content']) > 35 else note['content']
        preview = preview.replace('\n', ' ')  # Replace newlines with spaces
        preview_text = f"\n{preview}" if preview else ""

        # Color coding by level
        if level == 0:
            bg_color = (0.2, 0.3, 0.4, 1)  # Blue-ish for root
        elif level == 1:
            bg_color = (0.25, 0.25, 0.35, 1)  # Purple-ish for level 1
        else:
            bg_color = (0.2, 0.2, 0.3, 1)  # Darker for deeper levels

        # Create button in a container with left padding based on level
        left_indent = dp(20) * level  # 20dp indent per level
        container = BoxLayout(
            size_hint_y=None,
            height=dp(75) if preview else dp(55),
            padding=(dp(5) + left_indent, dp(3), dp(5), dp(3))
        )

        note_btn = Button(
            text=f"{note['title']}", # removed preview_text - it looked ugly
            halign='left',
            valign='middle',
            background_normal='',
            background_color=bg_color,
            padding=(dp(15), dp(8)),
            shorten=True,
            shorten_from='right',
            text_size=(None, None)
        )

        # Set text_size based on button width to enable text wrapping
        def update_text_size(btn, size):
            btn.text_size = (size[0] - dp(30), None)

        note_btn.bind(size=update_text_size)

        # Store state for long press detection
        note_btn._long_press_event = None
        note_btn._is_long_press = False

        def on_button_down(instance):
            """Handle button press start - schedule long press detection."""
            note_btn._is_long_press = False
            note_btn._long_press_event = Clock.schedule_once(
                lambda dt: on_long_press(),
                0.8
            )

        def on_long_press():
            """Triggered when long press threshold is reached."""
            note_btn._is_long_press = True
            if note_btn._long_press_event:
                note_btn._long_press_event.cancel()
                note_btn._long_press_event = None
            self.show_child_note_menu(note['id'], note['title'])

        def on_button_release(instance):
            """Handle button release - cancel long press and trigger normal press if needed."""
            if note_btn._long_press_event:
                note_btn._long_press_event.cancel()
                note_btn._long_press_event = None

            # Only open editor if it wasn't a long press
            if not note_btn._is_long_press:
                self.show_note_editor(note['id'])

            note_btn._is_long_press = False

        # Bind to button's on_press/on_release instead of touch events
        note_btn.bind(on_press=on_button_down)
        note_btn.bind(on_release=on_button_release)

        container.add_widget(note_btn)
        self.notes_list.add_widget(container)

    def on_search(self, instance, value):
        """Handle search input."""
        if value.strip():
            self.refresh_notes(value.strip())
        else:
            self.refresh_notes()

    def show_child_note_menu(self, parent_id, parent_title):
        """Show menu to create a child note."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        message = Label(
            text=f'Create a child note under:\n"{parent_title}"',
            size_hint_y=0.2
        )
        content.add_widget(message)

        title_input = TextInput(
            hint_text='Child note title',
            multiline=False,
            size_hint_y=0.15
        )
        content.add_widget(title_input)

        content_input = TextInput(
            hint_text='Note content',
            size_hint_y=0.5
        )
        content.add_widget(content_input)

        btn_layout = BoxLayout(size_hint_y=0.15, spacing=dp(10))

        save_btn = Button(text='Create', background_color=(0.2, 0.6, 0.8, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='New Child Note',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def save_child_note(btn):
            if title_input.text.strip():
                self.db.add_note(title_input.text.strip(), content_input.text, parent_id=parent_id)
                self.refresh_notes()
                popup.dismiss()

        save_btn.bind(on_press=save_child_note)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()

    def show_add_note_dialog(self, instance):
        """Show dialog to add a new note."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        title_input = TextInput(
            hint_text='Note title',
            multiline=False,
            size_hint_y=0.15
        )
        content.add_widget(title_input)

        content_input = TextInput(
            hint_text='Note content',
            size_hint_y=0.7
        )
        content.add_widget(content_input)

        btn_layout = BoxLayout(size_hint_y=0.15, spacing=dp(10))

        save_btn = Button(text='Save', background_color=(0.2, 0.6, 0.8, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='New Note',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def save_note(btn):
            if title_input.text.strip():
                self.db.add_note(title_input.text.strip(), content_input.text)
                self.refresh_notes()
                popup.dismiss()

        save_btn.bind(on_press=save_note)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()

    def show_note_editor(self, note_id):
        """Show editor for an existing note with markdown rendering."""
        note = self.db.get_note(note_id)
        if not note:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Title
        title_label = Label(
            text=note['title'],
            size_hint_y=0.1,
            font_size='20sp',
            bold=True,
            color=(1, 1, 1, 1)
        )
        content.add_widget(title_label)

        # Render markdown content
        from markdown import markdown
        html_content = markdown(note['content'] or 'No content')

        # For now, show simplified markdown in a label
        # (Full HTML rendering would need kivy-garden.webview which is complex on Android)
        rendered_text = self._markdown_to_simple_text(note['content'] or 'No content')

        content_scroll = ScrollView(size_hint_y=0.65)
        content_label = Label(
            text=rendered_text,
            markup=True,
            size_hint_y=None,
            text_size=(None, None),
            halign='left',
            valign='top',
            padding=(dp(10), dp(10))
        )
        # Allow label to expand vertically based on text
        content_label.bind(texture_size=lambda instance, value: setattr(instance, 'height', value[1]))
        content_label.bind(size=lambda lbl, size: setattr(lbl, 'text_size', (size[0] - dp(20), None)))

        # Handle link clicks
        def on_ref_press(instance, ref):
            """Handle clicks on links in the markdown."""
            import webbrowser

            try:
                # Only handle http/https URLs, not file:// URIs
                if ref.startswith('http://') or ref.startswith('https://'):
                    webbrowser.open(ref)
            except Exception as e:
                print(f"Failed to open link {ref}: {e}")
                import traceback
                traceback.print_exc()

        content_label.bind(on_ref_press=on_ref_press)
        content_scroll.add_widget(content_label)
        content.add_widget(content_scroll)

        btn_layout = BoxLayout(size_hint_y=0.15, spacing=dp(10))

        edit_btn = Button(text='Edit', background_color=(0.2, 0.6, 0.8, 1))
        delete_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        close_btn = Button(text='Close')

        popup = Popup(
            title='View Note',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def edit_note(btn):
            popup.dismiss()
            self.show_note_edit_dialog(note_id)

        def delete_note(btn):
            popup.dismiss()
            self.show_delete_confirmation(note_id, note['title'])

        edit_btn.bind(on_press=edit_note)
        delete_btn.bind(on_press=delete_note)
        close_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(edit_btn)
        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        popup.open()

    def _markdown_to_simple_text(self, md_text):
        """Convert markdown to Kivy markup for basic rendering."""
        import re
        import os
        from pathlib import Path

        # Convert markdown to basic Kivy markup
        text = md_text

        # Handle escaped characters first (before any markdown processing)
        # Replace escaped markdown characters with placeholders that won't be processed
        escape_map = {
            r'\*': '{{ESCAPEDASTERISK}}',
            r'\_': '{{ESCAPEDUNDERSCORE}}',
            r'\`': '{{ESCAPEDBACKTICK}}',
            r'\[': '{{ESCAPEDLBRACKET}}',
            r'\]': '{{ESCAPEDRBRACKET}}',
            r'\#': '{{ESCAPEDHASH}}',
            r'\!': '{{ESCAPEDEXCLAMATION}}',
            r'\|': '{{ESCAPEDPIPE}}',
            r'\-': '{{ESCAPEDDASH}}',
            r'\>': '{{ESCAPEDGT}}',
        }

        for escaped, placeholder in escape_map.items():
            text = text.replace(escaped, placeholder)

        # Tables: Process before code blocks to avoid conflicts
        def process_tables(text):
            lines = text.split('\n')
            result = []
            i = 0

            while i < len(lines):
                line = lines[i]

                # Check if this line might be a table (contains |)
                if '|' in line and i + 1 < len(lines):
                    # Check if next line is a separator
                    next_line = lines[i + 1]
                    if re.match(r'^\s*\|?[\s\-:|]+\|?\s*$', next_line):
                        # Found a table! Collect all table rows
                        table_lines = [line, next_line]
                        j = i + 2
                        while j < len(lines) and '|' in lines[j]:
                            table_lines.append(lines[j])
                            j += 1

                        # Format the table
                        formatted = ['[color=666666]' + '-' * 40 + '[/color]']

                        for idx, tline in enumerate(table_lines):
                            if idx == 1:  # Skip separator
                                continue

                            # Split by | and clean up
                            cells = [c.strip() for c in tline.split('|')]
                            if cells and not cells[0]:
                                cells = cells[1:]
                            if cells and not cells[-1]:
                                cells = cells[:-1]

                            if idx == 0:  # Header
                                formatted.append(' [color=888888]|[/color] '.join([f'[b]{c}[/b]' for c in cells]))
                            else:  # Data rows
                                formatted.append(' [color=888888]|[/color] '.join(cells))

                        formatted.append('[color=666666]' + '-' * 40 + '[/color]')
                        result.append('\n'.join(formatted))
                        i = j
                        continue

                result.append(line)
                i += 1

            return '\n'.join(result)

        text = process_tables(text)

        # Code blocks: ```code``` (must be processed before inline code)
        def replace_code_block(match):
            code = match.group(1)
            # Use a monospace font and background color simulation via color
            lines = code.strip().split('\n')
            formatted_lines = [f'[font=RobotoMono-Regular][color=cccccc]{line}[/color][/font]' for line in lines]
            return '\n[color=444444]' + '-' * 40 + '[/color]\n' + '\n'.join(formatted_lines) + '\n[color=444444]' + '-' * 40 + '[/color]\n'
        text = re.sub(r'```(?:\w+)?\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

        # Images: ![alt](path) - Show placeholder text (inline images not supported in Kivy Label)
        # Process BEFORE links since both use bracket syntax
        def replace_image(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            return f'{{{{IMAGE:{alt_text or img_path}}}}}'  # Use placeholder that won't match link regex

        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, text)

        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[color=4488ff][ref=\2][u]\1[/u][/ref][/color]', text)

        # Now replace image placeholders with final markup
        def replace_image_placeholder(match):
            content = match.group(1)
            return f'[color=4488ff][i][Image: {content}][/i] [color=888888](viewable on desktop)[/color][/color]'

        text = re.sub(r'\{\{IMAGE:([^}]+)\}\}', replace_image_placeholder, text)

        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
        text = re.sub(r'__(.+?)__', r'[b]\1[/b]', text)

        # Italic: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'[i]\1[/i]', text)
        text = re.sub(r'_(.+?)_', r'[i]\1[/i]', text)

        # Inline code: `code`
        text = re.sub(r'`(.+?)`', r'[font=RobotoMono-Regular][color=cccccc]\1[/color][/font]', text)

        # Block quotes: > text
        def replace_blockquote(match):
            quote_text = match.group(1)
            return f'[color=888888]|[/color] [i][color=aaaaaa]{quote_text}[/color][/i]'
        text = re.sub(r'^>\s*(.+)$', replace_blockquote, text, flags=re.MULTILINE)

        # Horizontal rules: --- or ***
        text = re.sub(r'^(?:---|\*\*\*|___)\s*$', '[color=666666]' + '-' * 40 + '[/color]', text, flags=re.MULTILINE)

        # Headers: # Header (use larger sizes - default is ~15sp)
        text = re.sub(r'^# (.+)$', r'[size=32sp][b]\1[/b][/size]', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'[size=28sp][b]\1[/b][/size]', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'[size=24sp][b]\1[/b][/size]', text, flags=re.MULTILINE)
        text = re.sub(r'^#### (.+)$', r'[size=20sp][b]\1[/b][/size]', text, flags=re.MULTILINE)
        text = re.sub(r'^##### (.+)$', r'[size=18sp][b]\1[/b][/size]', text, flags=re.MULTILINE)
        text = re.sub(r'^###### (.+)$', r'[size=16sp][b]\1[/b][/size]', text, flags=re.MULTILINE)

        # Restore escaped characters (after all markdown processing)
        unescape_map = {
            '{{ESCAPEDASTERISK}}': '*',
            '{{ESCAPEDUNDERSCORE}}': '_',
            '{{ESCAPEDBACKTICK}}': '`',
            '{{ESCAPEDLBRACKET}}': '[',
            '{{ESCAPEDRBRACKET}}': ']',
            '{{ESCAPEDHASH}}': '#',
            '{{ESCAPEDEXCLAMATION}}': '!',
            '{{ESCAPEDPIPE}}': '|',
            '{{ESCAPEDDASH}}': '-',
            '{{ESCAPEDGT}}': '>',
        }

        for placeholder, char in unescape_map.items():
            text = text.replace(placeholder, char)

        return text

    def show_note_edit_dialog(self, note_id):
        """Show edit dialog for a note."""
        note = self.db.get_note(note_id)
        if not note:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        title_input = TextInput(
            text=note['title'],
            multiline=False,
            size_hint_y=0.15,
            hint_text='Title'
        )
        content.add_widget(title_input)

        content_input = TextInput(
            text=note['content'] or '',
            size_hint_y=0.7,
            hint_text='Content (markdown supported)'
        )
        content.add_widget(content_input)

        btn_layout = BoxLayout(size_hint_y=0.15, spacing=dp(10))

        save_btn = Button(text='Save', background_color=(0.2, 0.6, 0.8, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='Edit Note',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def save_note(btn):
            if title_input.text.strip():
                self.db.update_note(note_id, title_input.text.strip(), content_input.text)
                self.refresh_notes()
                popup.dismiss()

        save_btn.bind(on_press=save_note)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()

    def show_db_info(self, instance):
        """Show database location information with verification."""
        from pathlib import Path

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Check if file actually exists
        db_path = Path(self.db_path)
        db_exists = db_path.exists()
        db_size = db_path.stat().st_size if db_exists else 0

        # Try to list directory contents
        db_dir = db_path.parent
        try:
            dir_contents = list(db_dir.iterdir()) if db_dir.exists() else []
            dir_list = "\n".join([f"  {f.name} ({f.stat().st_size} bytes)" for f in dir_contents[:10]])
            if not dir_list:
                dir_list = "(empty)"
        except Exception as e:
            dir_list = f"Error: {e}"

        info_text = f"Database: {self.db_path}\n\n"
        info_text += f"Exists: {'YES' if db_exists else 'NO'}\n"
        info_text += f"Size: {db_size} bytes\n\n"
        info_text += f"Folder: {db_dir}\n"
        info_text += f"Folder exists: {'YES' if db_dir.exists() else 'NO'}\n\n"
        info_text += f"Folder contents:\n{dir_list}"

        info_label = Label(
            text=info_text,
            size_hint_y=0.9,
            text_size=(dp(300), None),
            halign='left',
            valign='top'
        )
        content.add_widget(info_label)

        close_btn = Button(text='Close', size_hint_y=0.1)

        popup = Popup(
            title='Database Info',
            content=content,
            size_hint=(0.9, 0.7)
        )

        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()

    def export_database(self, instance):
        """Export database to Downloads folder using MediaStore."""
        import sys
        from kivy.utils import platform as kivy_platform

        print("SPARK: Export button pressed!")
        print(f"SPARK: sys.platform = {sys.platform}")
        print(f"SPARK: kivy.utils.platform = {kivy_platform}")

        try:
            if kivy_platform == 'android':
                from jnius import autoclass
                import shutil
                from pathlib import Path

                print(f"SPARK: Source DB path: {self.db_path}")

                # Simple direct file copy approach
                Environment = autoclass('android.os.Environment')

                # Get Downloads directory
                downloads_dir = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS
                )
                downloads_path = Path(str(downloads_dir.getAbsolutePath()))

                print(f"SPARK: Downloads path: {downloads_path}")

                # Create SPARK subfolder
                spark_dir = downloads_path / 'SPARK'
                print(f"SPARK: Creating directory: {spark_dir}")
                spark_dir.mkdir(exist_ok=True, parents=True)

                # Copy database
                export_path = spark_dir / 'spark.db'
                print(f"SPARK: Copying to: {export_path}")

                shutil.copy2(self.db_path, export_path)

                # Get file size
                file_size = export_path.stat().st_size
                print(f"SPARK: Export successful! {file_size} bytes written")

                # Show success message
                content = BoxLayout(orientation='vertical', padding=dp(10))
                message = Label(
                    text=f'Database exported!\n\nLocation:\n{export_path}\n\n({file_size} bytes)\n\nCheck Downloads/SPARK folder',
                    size_hint_y=0.8
                )
                content.add_widget(message)

                close_btn = Button(text='OK', size_hint_y=0.2)
                popup = Popup(
                    title='Export Successful!',
                    content=content,
                    size_hint=(0.8, 0.4)
                )
                close_btn.bind(on_press=popup.dismiss)
                content.add_widget(close_btn)
                popup.open()
            else:
                print("Export only available on Android")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"SPARK: Export error: {e}")
            print(error_details)

            # Show detailed error message
            content = BoxLayout(orientation='vertical', padding=dp(10))
            message = Label(
                text=f'Export failed:\n\n{str(e)}\n\nCheck console for details',
                size_hint_y=0.8
            )
            content.add_widget(message)

            close_btn = Button(text='OK', size_hint_y=0.2)
            popup = Popup(
                title='Export Error',
                content=content,
                size_hint=(0.8, 0.4)
            )
            close_btn.bind(on_press=popup.dismiss)
            content.add_widget(close_btn)
            popup.open()

    def show_delete_confirmation(self, note_id, note_title):
        """Show confirmation dialog before deleting a note."""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        message = Label(
            text=f'Are you sure you want to delete this note?\n\n"{note_title}"\n\nThis action cannot be undone.',
            size_hint_y=0.7
        )
        content.add_widget(message)

        btn_layout = BoxLayout(size_hint_y=0.3, spacing=dp(10))

        delete_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='Confirm Delete',
            content=content,
            size_hint=(0.8, 0.4)
        )

        def confirm_delete(btn):
            self.db.delete_note(note_id)
            self.refresh_notes()
            popup.dismiss()

        delete_btn.bind(on_press=confirm_delete)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)

        popup.open()
