"""SPARK Mobile - Touch-first knowledgebase for Android/iOS."""

import os
import sys
from pathlib import Path

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.core.window import Window

# Import database (will copy from desktop app)
from database import Database


class SparkMobile(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None

    def build(self):
        """Build the UI."""
        # Set app title
        self.title = "SPARK Mobile"

        # Initialize database
        db_path = self.get_db_path()
        self.db = Database(db_path)

        # Create main layout
        root = BoxLayout(orientation='vertical')

        # Create tabbed interface
        tabs = TabbedPanel(do_default_tab=False)

        # Notes tab
        notes_tab = TabbedPanelItem(text='Notes')
        notes_tab.add_widget(Label(text='Notes view coming soon'))
        tabs.add_widget(notes_tab)

        # Snippets tab
        snippets_tab = TabbedPanelItem(text='Snippets')
        snippets_tab.add_widget(Label(text='Snippets view coming soon'))
        tabs.add_widget(snippets_tab)

        # Spreadsheets tab
        sheets_tab = TabbedPanelItem(text='Sheets')
        sheets_tab.add_widget(Label(text='Spreadsheets view coming soon'))
        tabs.add_widget(sheets_tab)

        root.add_widget(tabs)
        return root

    def get_db_path(self) -> Path:
        """Get platform-appropriate database path."""
        if sys.platform == 'android':
            # On Android, use app's internal storage
            from android.storage import app_storage_path
            data_dir = Path(app_storage_path())
        else:
            # On desktop, use current directory for testing
            data_dir = Path.cwd() / 'data'
            data_dir.mkdir(exist_ok=True)

        return data_dir / 'spark.db'

    def on_pause(self):
        """Handle app pause (required for Android)."""
        return True

    def on_resume(self):
        """Handle app resume (required for Android)."""
        pass


if __name__ == '__main__':
    SparkMobile().run()
