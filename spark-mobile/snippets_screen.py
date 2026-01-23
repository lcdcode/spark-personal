"""Snippets screen for SPARK Mobile."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.metrics import dp


class SnippetsScreen(BoxLayout):
    """Code snippets list and editor screen."""

    LANGUAGES = [
        'python', 'javascript', 'java', 'c', 'cpp', 'go', 'rust',
        'ruby', 'php', 'swift', 'kotlin', 'typescript', 'bash', 'sql', 'html', 'css'
    ]

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = 'vertical'

        # Top bar
        top_bar = BoxLayout(size_hint_y=0.1, padding=dp(10), spacing=dp(10))

        self.search_input = TextInput(
            hint_text='Search snippets...',
            multiline=False,
            size_hint_x=0.7
        )
        self.search_input.bind(text=self.on_search)
        top_bar.add_widget(self.search_input)

        add_btn = Button(
            text='+ New Snippet',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        add_btn.bind(on_press=self.show_add_snippet_dialog)
        top_bar.add_widget(add_btn)

        self.add_widget(top_bar)

        # Snippets list
        scroll = ScrollView(size_hint_y=0.9)
        self.snippets_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.snippets_list.bind(minimum_height=self.snippets_list.setter('height'))
        scroll.add_widget(self.snippets_list)
        self.add_widget(scroll)

        self.refresh_snippets()

    def refresh_snippets(self, search_query=None):
        """Refresh the snippets list."""
        self.snippets_list.clear_widgets()

        if search_query:
            snippets = self.db.search_snippets(search_query)
        else:
            snippets = self.db.get_all_snippets()

        if not snippets:
            label = Label(
                text='No snippets yet.\nTap "+ New Snippet" to create one.',
                size_hint_y=None,
                height=dp(100),
                color=(0.5, 0.5, 0.5, 1)
            )
            self.snippets_list.add_widget(label)
            return

        for snippet in snippets:
            lang_badge = f"[{snippet['language']}]" if snippet['language'] else ""
            code_preview = snippet['code'][:60] + "..." if len(snippet['code']) > 60 else snippet['code']

            snippet_btn = Button(
                text=f"{snippet['title']} {lang_badge}\n{code_preview}",
                size_hint_y=None,
                height=dp(80),
                halign='left',
                valign='top',
                text_size=(None, None),
                background_normal='',
                background_color=(0.15, 0.15, 0.15, 1)
            )
            snippet_btn.bind(size=lambda btn, size: setattr(btn, 'text_size', (size[0] - dp(20), None)))
            snippet_btn.bind(on_press=lambda btn, snippet_id=snippet['id']: self.show_snippet_editor(snippet_id))
            self.snippets_list.add_widget(snippet_btn)

    def on_search(self, instance, value):
        """Handle search input."""
        if value.strip():
            self.refresh_snippets(value.strip())
        else:
            self.refresh_snippets()

    def show_add_snippet_dialog(self, instance):
        """Show dialog to add a new snippet."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        title_input = TextInput(
            hint_text='Snippet title',
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(title_input)

        lang_spinner = Spinner(
            text='Select language',
            values=self.LANGUAGES,
            size_hint_y=0.1
        )
        content.add_widget(lang_spinner)

        code_input = TextInput(
            hint_text='Code',
            size_hint_y=0.6,
            font_name='RobotoMono-Regular'
        )
        content.add_widget(code_input)

        tags_input = TextInput(
            hint_text='Tags (comma-separated)',
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(tags_input)

        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))

        save_btn = Button(text='Save', background_color=(0.2, 0.6, 0.8, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='New Snippet',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def save_snippet(btn):
            if title_input.text.strip():
                self.db.add_snippet(
                    title_input.text.strip(),
                    code_input.text,
                    lang_spinner.text if lang_spinner.text != 'Select language' else '',
                    tags_input.text
                )
                self.refresh_snippets()
                popup.dismiss()

        save_btn.bind(on_press=save_snippet)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()

    def show_snippet_editor(self, snippet_id):
        """Show editor for an existing snippet."""
        snippet = self.db.get_snippet(snippet_id)
        if not snippet:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        title_input = TextInput(
            text=snippet['title'],
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(title_input)

        lang_spinner = Spinner(
            text=snippet['language'] or 'Select language',
            values=self.LANGUAGES,
            size_hint_y=0.1
        )
        content.add_widget(lang_spinner)

        code_input = TextInput(
            text=snippet['code'] or '',
            size_hint_y=0.6,
            font_name='RobotoMono-Regular'
        )
        content.add_widget(code_input)

        tags_input = TextInput(
            text=snippet['tags'] or '',
            multiline=False,
            size_hint_y=0.1
        )
        content.add_widget(tags_input)

        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))

        save_btn = Button(text='Save', background_color=(0.2, 0.6, 0.8, 1))
        delete_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='Edit Snippet',
            content=content,
            size_hint=(0.9, 0.8)
        )

        def save_snippet(btn):
            if title_input.text.strip():
                self.db.update_snippet(
                    snippet_id,
                    title_input.text.strip(),
                    code_input.text,
                    lang_spinner.text if lang_spinner.text != 'Select language' else '',
                    tags_input.text
                )
                self.refresh_snippets()
                popup.dismiss()

        def delete_snippet(btn):
            self.db.delete_snippet(snippet_id)
            self.refresh_snippets()
            popup.dismiss()

        save_btn.bind(on_press=save_snippet)
        delete_btn.bind(on_press=delete_snippet)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()
