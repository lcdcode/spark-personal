"""Spreadsheets screen for SPARK Mobile."""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
import json


class SpreadsheetsScreen(BoxLayout):
    """Spreadsheets list and simple viewer screen."""

    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self.db = db
        self.orientation = 'vertical'

        # Top bar
        top_bar = BoxLayout(size_hint_y=0.1, padding=dp(10), spacing=dp(10))

        title = Label(text='Spreadsheets', size_hint_x=0.7, font_size='20sp')
        top_bar.add_widget(title)

        add_btn = Button(
            text='+ New Sheet',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        add_btn.bind(on_press=self.show_add_sheet_dialog)
        top_bar.add_widget(add_btn)

        self.add_widget(top_bar)

        # Sheets list
        scroll = ScrollView(size_hint_y=0.9)
        self.sheets_list = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.sheets_list.bind(minimum_height=self.sheets_list.setter('height'))
        scroll.add_widget(self.sheets_list)
        self.add_widget(scroll)

        self.refresh_sheets()

    def refresh_sheets(self):
        """Refresh the spreadsheets list."""
        self.sheets_list.clear_widgets()

        sheets = self.db.get_all_spreadsheets()

        if not sheets:
            label = Label(
                text='No spreadsheets yet.\nTap "+ New Sheet" to create one.',
                size_hint_y=None,
                height=dp(100),
                color=(0.5, 0.5, 0.5, 1)
            )
            self.sheets_list.add_widget(label)
            return

        for sheet in sheets:
            # Parse data to show preview
            try:
                data = json.loads(sheet['data']) if sheet['data'] else {}
                cell_count = len(data)
                preview = f"{cell_count} cells"
            except:
                preview = "No data"

            sheet_btn = Button(
                text=f"{sheet['name']}\n{preview}",
                size_hint_y=None,
                height=dp(80),
                halign='left',
                valign='top',
                text_size=(None, None),
                background_normal='',
                background_color=(0.15, 0.15, 0.15, 1)
            )
            sheet_btn.bind(size=lambda btn, size: setattr(btn, 'text_size', (size[0] - dp(20), None)))
            sheet_btn.bind(on_press=lambda btn, sheet_id=sheet['id']: self.show_sheet_viewer(sheet_id))
            self.sheets_list.add_widget(sheet_btn)

    def show_add_sheet_dialog(self, instance):
        """Show dialog to add a new spreadsheet."""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        name_input = TextInput(
            hint_text='Spreadsheet name',
            multiline=False,
            size_hint_y=0.2
        )
        content.add_widget(name_input)

        info_label = Label(
            text='A basic spreadsheet will be created.\nYou can add data after creation.',
            size_hint_y=0.6,
            color=(0.7, 0.7, 0.7, 1)
        )
        content.add_widget(info_label)

        btn_layout = BoxLayout(size_hint_y=0.2, spacing=dp(10))

        save_btn = Button(text='Create', background_color=(0.2, 0.6, 0.8, 1))
        cancel_btn = Button(text='Cancel')

        popup = Popup(
            title='New Spreadsheet',
            content=content,
            size_hint=(0.9, 0.5)
        )

        def save_sheet(btn):
            if name_input.text.strip():
                # Create with empty data structure
                initial_data = json.dumps({"A1": ""})
                self.db.add_spreadsheet(name_input.text.strip(), initial_data)
                self.refresh_sheets()
                popup.dismiss()

        save_btn.bind(on_press=save_sheet)
        cancel_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(save_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup.open()

    def show_sheet_viewer(self, sheet_id):
        """Show viewer for a spreadsheet."""
        sheet = self.db.get_spreadsheet(sheet_id)
        if not sheet:
            return

        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))

        # Parse and display data
        try:
            data = json.loads(sheet['data']) if sheet['data'] else {}
        except:
            data = {}

        # Create a simple grid view of cells
        scroll = ScrollView(size_hint_y=0.7)
        cells_grid = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None,
            padding=dp(5)
        )
        cells_grid.bind(minimum_height=cells_grid.setter('height'))

        if data:
            for cell, value in sorted(data.items()):
                cell_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
                cell_layout.add_widget(Label(text=cell, size_hint_x=0.3, color=(0.5, 0.8, 1, 1)))
                cell_layout.add_widget(Label(text=str(value), size_hint_x=0.7, halign='left'))
                cells_grid.add_widget(cell_layout)
        else:
            cells_grid.add_widget(Label(
                text='No data in this spreadsheet',
                size_hint_y=None,
                height=dp(50),
                color=(0.5, 0.5, 0.5, 1)
            ))

        scroll.add_widget(cells_grid)
        content.add_widget(scroll)

        # Info label
        info_label = Label(
            text='Note: Full spreadsheet editing is available in the desktop app.',
            size_hint_y=0.2,
            color=(0.7, 0.7, 0.7, 1)
        )
        content.add_widget(info_label)

        # Buttons
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))

        delete_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        close_btn = Button(text='Close')

        popup = Popup(
            title=sheet['name'],
            content=content,
            size_hint=(0.9, 0.8)
        )

        def delete_sheet(btn):
            self.db.delete_spreadsheet(sheet_id)
            self.refresh_sheets()
            popup.dismiss()

        delete_btn.bind(on_press=delete_sheet)
        close_btn.bind(on_press=popup.dismiss)

        btn_layout.add_widget(delete_btn)
        btn_layout.add_widget(close_btn)
        content.add_widget(btn_layout)

        popup.open()
