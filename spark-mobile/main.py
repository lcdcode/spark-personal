"""SPARK Mobile - Touch-first knowledgebase for Android/iOS."""

import os
import sys
import logging
from pathlib import Path

# Configure logging FIRST - before any other imports
logging.basicConfig(
    level=logging.DEBUG,
    format='SPARK: %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

print("="*60)
print("SPARK MOBILE STARTUP - INITIAL LOGGING TEST")
print(f"Python version: {sys.version}")
print(f"Platform: {sys.platform}")
print(f"Working directory: {os.getcwd()}")
print("="*60)
sys.stdout.flush()

try:
    from kivy.app import App
    print("✓ Kivy imported successfully")
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
    from kivy.core.window import Window
    from kivy.config import Config
    print("✓ Kivy UI components imported")

    # Import database and screens
    from database import Database
    print("✓ Database module imported")
    from notes_screen import NotesScreen
    print("✓ NotesScreen imported")
    from snippets_screen import SnippetsScreen
    print("✓ SnippetsScreen imported")
    from spreadsheets_screen import SpreadsheetsScreen
    print("✓ SpreadsheetsScreen imported")

    # Configure Kivy
    Config.set('kivy', 'exit_on_escape', '0')
    Config.set('graphics', 'resizable', False)
    print("✓ Kivy configured")

except Exception as e:
    import traceback
    print("="*60)
    print("CRITICAL ERROR DURING IMPORTS:")
    print(str(e))
    print("-"*60)
    traceback.print_exc()
    print("="*60)
    sys.stdout.flush()
    raise


class SparkMobile(App):
    """Main application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = None
        self.db_path = None
        self.db_last_modified = None
        self.check_interval = 5  # Check every 5 seconds

    def build(self):
        """Build the UI."""
        # Set app title
        self.title = "SPARK Mobile"

        # Set icon
        self.icon = 'icon.png'

        # Request storage permissions on Android
        if sys.platform == 'android':
            self.request_android_permissions()

        # Initialize database
        self.db_path = self.get_db_path()
        print(f"Database path: {self.db_path}")
        self.db = Database(self.db_path)
        self.update_db_timestamp()

        # Create main layout with dark theme
        Window.clearcolor = (0.1, 0.1, 0.1, 1)

        # Schedule database change check
        from kivy.clock import Clock
        Clock.schedule_interval(self.check_database_changes, self.check_interval)

        # Create tabbed interface
        tabs = TabbedPanel(
            do_default_tab=False,
            tab_pos='top_mid',
            tab_width=Window.width / 3
        )

        # Notes tab
        notes_tab = TabbedPanelItem(text='Notes')
        self.notes_screen = NotesScreen(self.db, db_path=str(self.db_path))
        notes_tab.add_widget(self.notes_screen)
        tabs.add_widget(notes_tab)

        # Snippets tab
        snippets_tab = TabbedPanelItem(text='Snippets')
        self.snippets_screen = SnippetsScreen(self.db)
        snippets_tab.add_widget(self.snippets_screen)
        tabs.add_widget(snippets_tab)

        # Spreadsheets tab
        sheets_tab = TabbedPanelItem(text='Sheets')
        self.sheets_screen = SpreadsheetsScreen(self.db)
        sheets_tab.add_widget(self.sheets_screen)
        tabs.add_widget(sheets_tab)

        return tabs

    def get_db_path(self) -> Path:
        """Get platform-appropriate database path."""
        from kivy.utils import platform as kivy_platform

        if kivy_platform == 'android':
            print("SPARK: ===== DATABASE PATH DETECTION =====")

            # Try Documents directory first, then Downloads
            try:
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')

                # Try Documents first (more appropriate for app data)
                locations = [
                    ('Documents', Environment.DIRECTORY_DOCUMENTS),
                    ('Downloads', Environment.DIRECTORY_DOWNLOADS)
                ]

                for location_name, location_type in locations:
                    try:
                        public_dir = Environment.getExternalStoragePublicDirectory(location_type)
                        base_path = Path(str(public_dir.getAbsolutePath()))

                        print(f"SPARK: Trying {location_name} path: {base_path}")

                        # Try to create SPARK subfolder
                        spark_dir = base_path / 'SPARK'
                        spark_dir.mkdir(exist_ok=True, parents=True)

                        # Test if we can actually write here
                        test_file = spark_dir / '.test'
                        test_file.touch()
                        test_file.unlink()

                        db_path = spark_dir / 'spark.db'
                        print(f"SPARK: ✓ SUCCESS! Database at: {db_path}")
                        print(f"SPARK: This location is accessible by Syncthing!")
                        print(f"SPARK: Configure Syncthing to sync: {location_name}/SPARK/")
                        print(f"SPARK: ==========================================")
                        return db_path

                    except (PermissionError, OSError) as e:
                        print(f"SPARK: Cannot create SPARK folder in {location_name}: {e}")
                        continue

                print(f"SPARK: Could not access Documents or Downloads folders")

            except Exception as e:
                import traceback
                print(f"SPARK: Error accessing external storage: {e}")
                traceback.print_exc()

            # Fallback to internal storage
            print("SPARK: ==========================================")
            print(f"SPARK: Using internal storage (not accessible to Syncthing)")
            print(f"SPARK: Use the 📤 export button to copy DB to Downloads")
            print(f"SPARK: ==========================================")
            from android.storage import app_storage_path
            return Path(app_storage_path()) / 'spark.db'
        else:
            # On desktop, use current directory for testing
            data_dir = Path.cwd() / 'data'
            data_dir.mkdir(exist_ok=True)
            return data_dir / 'spark.db'

    def on_pause(self):
        """Handle app pause (required for Android)."""
        # Save any pending changes
        if self.db:
            self.db.close()
        return True

    def on_resume(self):
        """Handle app resume (required for Android)."""
        # Reconnect to database
        if self.db:
            self.db.connect()

    def on_stop(self):
        """Handle app stop."""
        if self.db:
            self.db.close()

    def request_android_permissions(self):
        """Request storage permissions on Android."""
        from kivy.utils import platform as kivy_platform

        if kivy_platform == 'android':
            try:
                from android.permissions import request_permissions, Permission, check_permission

                # Request all storage permissions
                permissions = [
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                ]

                print("SPARK: Requesting storage permissions...")
                request_permissions(permissions)

                # Check if permissions were granted
                write_granted = check_permission(Permission.WRITE_EXTERNAL_STORAGE)
                read_granted = check_permission(Permission.READ_EXTERNAL_STORAGE)

                print(f"SPARK: WRITE_EXTERNAL_STORAGE: {'✓ Granted' if write_granted else '✗ Denied'}")
                print(f"SPARK: READ_EXTERNAL_STORAGE: {'✓ Granted' if read_granted else '✗ Denied'}")

                if not write_granted or not read_granted:
                    print("SPARK: ⚠ WARNING: Storage permissions not granted!")
                    print("SPARK: Please enable storage permissions in Android Settings")

            except Exception as e:
                print(f"SPARK: Error requesting permissions: {e}")

    def update_db_timestamp(self):
        """Update the stored database modification timestamp."""
        import os
        try:
            if os.path.exists(self.db_path):
                self.db_last_modified = os.path.getmtime(self.db_path)
        except Exception as e:
            print(f"SPARK: Error getting db timestamp: {e}")

    def check_database_changes(self, dt):
        """Check if database has been externally modified."""
        import os
        try:
            if not os.path.exists(self.db_path):
                return

            current_mtime = os.path.getmtime(self.db_path)

            if self.db_last_modified and current_mtime > self.db_last_modified:
                print(f"SPARK: Database changed externally! {self.db_last_modified} -> {current_mtime}")
                self.show_reload_prompt()

        except Exception as e:
            print(f"SPARK: Error checking database changes: {e}")

    def show_reload_prompt(self):
        """Show prompt to reload database."""
        from kivy.uix.popup import Popup
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.metrics import dp

        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        message = Label(
            text='The database has been modified externally\n(possibly by Syncthing).\n\nWould you like to reload the data?',
            size_hint_y=0.7
        )
        content.add_widget(message)

        btn_layout = BoxLayout(size_hint_y=0.3, spacing=dp(10))

        reload_btn = Button(text='Reload', background_color=(0.2, 0.6, 0.8, 1))
        later_btn = Button(text='Later')

        popup = Popup(
            title='Database Updated',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        def reload_database(btn):
            self.reload_database()
            popup.dismiss()

        def dismiss_popup(btn):
            # Update timestamp to avoid repeated prompts
            self.update_db_timestamp()
            popup.dismiss()

        reload_btn.bind(on_press=reload_database)
        later_btn.bind(on_press=dismiss_popup)

        btn_layout.add_widget(later_btn)
        btn_layout.add_widget(reload_btn)
        content.add_widget(btn_layout)

        popup.open()

    def reload_database(self):
        """Reload database and refresh all screens."""
        print("SPARK: Reloading database...")
        try:
            # Close and reopen database connection
            if self.db:
                self.db.close()

            self.db = Database(self.db_path)
            self.update_db_timestamp()

            # Refresh all screens
            if hasattr(self, 'notes_screen'):
                self.notes_screen.db = self.db
                self.notes_screen.refresh_notes()

            if hasattr(self, 'snippets_screen'):
                self.snippets_screen.db = self.db
                self.snippets_screen.refresh_snippets()

            if hasattr(self, 'sheets_screen'):
                self.sheets_screen.db = self.db
                self.sheets_screen.refresh_sheets()

            print("SPARK: Database reloaded successfully")

        except Exception as e:
            print(f"SPARK: Error reloading database: {e}")


if __name__ == '__main__':
    SparkMobile().run()
