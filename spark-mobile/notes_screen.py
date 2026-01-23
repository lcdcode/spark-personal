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
        top_bar = BoxLayout(size_hint_y=0.1, padding=dp(10), spacing=dp(10))

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
                    text='No notes yet.\nTap "+ New" to create one.',
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

        # Create indent based on hierarchy level
        indent = "  " * level
        tree_symbol = "└─ " if level > 0 else ""

        # Preview text - shortened for mobile
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

        # Create button in a container to control sizing
        container = BoxLayout(
            size_hint_y=None,
            height=dp(75) if preview else dp(55),
            padding=(dp(5), dp(3))
        )

        note_btn = Button(
            text=f"{indent}{tree_symbol}{note['title']}{preview_text}",
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
        note_btn.bind(on_press=lambda btn, note_id=note['id']: self.show_note_editor(note_id))

        container.add_widget(note_btn)
        self.notes_list.add_widget(container)

    def on_search(self, instance, value):
        """Handle search input."""
        if value.strip():
            self.refresh_notes(value.strip())
        else:
            self.refresh_notes()

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
            text_size=(None, None),
            halign='left',
            valign='top',
            padding=(dp(10), dp(10))
        )
        content_label.bind(size=lambda lbl, size: setattr(lbl, 'text_size', (size[0], None)))
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
            self.db.delete_note(note_id)
            self.refresh_notes()
            popup.dismiss()

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

        # Convert markdown to basic Kivy markup
        text = md_text

        # Bold: **text** or __text__
        text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
        text = re.sub(r'__(.+?)__', r'[b]\1[/b]', text)

        # Italic: *text* or _text_
        text = re.sub(r'\*(.+?)\*', r'[i]\1[/i]', text)
        text = re.sub(r'_(.+?)_', r'[i]\1[/i]', text)

        # Code: `code`
        text = re.sub(r'`(.+?)`', r'[font=RobotoMono-Regular][color=00ff00]\1[/color][/font]', text)

        # Headers: # Header
        text = re.sub(r'^# (.+)$', r'[size=24][b]\1[/b][/size]', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'[size=20][b]\1[/b][/size]', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'[size=18][b]\1[/b][/size]', text, flags=re.MULTILINE)

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
